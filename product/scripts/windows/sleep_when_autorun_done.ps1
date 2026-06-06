<#
.SYNOPSIS
    Puts the PC to sleep once the autorun orchestrator finishes.

.DESCRIPTION
    Watches the orchestrator (scripts/automation/orchestrate.py) from Windows and
    suspends the host once it stops. Optionally schedules a Windows wake-up task
    so the PC comes back at a chosen time (e.g. for the next nightly run).

    Detection strategy (cross-platform  -  works for WSL2 and Docker devcontainers):

      1. state.json is_running flag (PRIMARY)
         - The orchestrator writes is_running=true at startup, false in finally.
         - Single source of truth; no time-based heuristic needed.
      2. state.json rate_limit_reached flag (early-exit)
         - When true, the orchestrator is just waiting for a rate-limit reset.
         - The script proceeds to suspend immediately and schedules wake from
           state.json next_wake_time.
      3. Sentinel + log-mtime fallback (legacy)
         - Used when state.json is missing/unreadable or is_running absent
           (older orchestrator). LogStaleMinutes still applies in this path.
      4. Final log line "[orchestrator] Stopped. Reason: ..."
         - Used to surface the stop reason to the user.

    The script never reads container PIDs from the host (PID namespaces make that
    unreliable across WSL/Docker), so it works regardless of the dev container backend.

.PARAMETER ProjectPath
    Windows path to the flutter_app folder.
    Default: parent of the script's own directory (resolved via $PSScriptRoot or $MyInvocation.MyCommand.Path).

.PARAMETER WakeBeforeResetMinutes
    Wake the PC this many minutes BEFORE the earliest rate-limit reset
    (read from automation/state.json -> rate_limited_until). Default 5.

    Wake-up is only scheduled when the orchestrator is actively waiting for a
    rate-limit reset (state.json rate_limit_reached=true). Any other stop reason
    (manual stop, max-tasks reached, error, SIGKILL) leaves the PC asleep with
    no wake task, even if stale rate_limited_until entries remain in state.json.

    Behaviour when orchestrator is rate-limited:
      - state.json next_wake_time is set   -> wake = next_wake_time - N min
      - else active rate_limited_until     -> wake = (earliest reset) - N min
      - else                               -> no wake task (just sleep)
      - earliest reset already in the past -> no wake task (would fire immediately)

.PARAMETER MinSleepMinutes
    Minimum sleep duration worth a suspend/resume cycle. Default 2.

    If the computed wake time is less than this many minutes away (or already in
    the past), the script does NOT suspend — it logs and re-polls instead. This
    guards against a pointless and risky near-zero sleep: when the earliest reset
    is so close that "wake N min before reset" lands at (or before) now, the 15s
    suspend countdown can push the real suspend PAST the trigger time, so the RTC
    wake alarm never fires and the host stays asleep. The host instead stays awake
    (held by SetThreadExecutionState) for the short remaining window until the
    orchestrator clears rate_limit_reached.

.PARAMETER NoWake
    Disable the wake-up logic entirely; always sleep without scheduling a wake task.

.PARAMETER PollSeconds
    Poll interval. Default 60.

.PARAMETER LogStaleMinutes
    Treat the orchestrator as "no longer active" if orchestrate.log has not been
    written for this many minutes (covers SIGKILL where the sentinel persists).
    Default 30. Only applies in the legacy fallback path.

.PARAMETER WakeTaskName
    Name of the scheduled task that wakes the PC. Default "AutorunWakePC".

.PARAMETER Hibernate
    Hibernate (S4) instead of sleep (S3). Slower wake but zero power draw.

.PARAMETER DryRun
    Print what would happen, then exit instead of actually suspending.

.PARAMETER Quiet
    Suppress per-poll status lines (still prints start/stop summaries).

.PARAMETER LogFile
    Append all output to this log file (in addition to console).

.PARAMETER TestMode
    Skip orchestrator monitoring and instead run a self-contained two-cycle
    sleep/wake test to verify the suspend + wake-task plumbing on this host:
      Cycle 1: sleep after 5s,  wake ~30s later (scheduled task)
      Cycle 2: sleep after 10s, wake ~30s later (scheduled task)
      Then unregister the wake task and exit.
    Requires Administrator (registers a SYSTEM scheduled task). Incompatible
    with -NoWake (the whole point is to test wake-from-sleep).

.EXAMPLE
    # Default: sleep when done, auto-wake 5 min before earliest rate-limit reset
    .\scripts\sleep_when_autorun_done.ps1

.EXAMPLE
    # Verify sleep + wake on this PC (no orchestrator needed)
    .\scripts\sleep_when_autorun_done.ps1 -TestMode

.EXAMPLE
    # Wake 10 min before the earliest reset (more buffer for orchestrator restart)
    .\scripts\sleep_when_autorun_done.ps1 -WakeBeforeResetMinutes 10

.EXAMPLE
    # Just sleep, never wake automatically
    .\scripts\sleep_when_autorun_done.ps1 -NoWake

.EXAMPLE
    # Hibernate + dry-run to verify behaviour before committing
    .\scripts\sleep_when_autorun_done.ps1 -Hibernate -DryRun

.NOTES
    Wake-up requires:
      - Administrator rights to register the scheduled task
      - "Allow wake timers" enabled in Power Options (powercfg /waketimers to inspect)
      - Hardware support for wake from sleep (most modern PCs)
#>

[CmdletBinding()]
param(
    [string] $ProjectPath             = "",
    [int]    $WakeBeforeResetMinutes  = 5,
    [int]    $MinSleepMinutes         = 2,
    [switch] $NoWake,
    [int]    $PollSeconds             = 60,
    [int]    $LogStaleMinutes         = 30,
    [string] $WakeTaskName            = "AutorunWakePC",
    [switch] $Hibernate,
    [switch] $DryRun,
    [switch] $Quiet,
    [string] $LogFile                 = "",
    [switch] $TestMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Resolve ProjectPath via the shared helper (3-level precedence: explicit param →
# windows_scripts.config.json → auto-derive from script location).
. "$PSScriptRoot\find_project_root.ps1"
if (-not $ProjectPath) {
    $ProjectPath = Find-ProjectRoot
}

# -- Paths ---------------------------------------------------------------------

$automationDir   = Join-Path $ProjectPath "automation"
$sentinelPath    = Join-Path $automationDir ".automated_mode"
$orchestrateLog  = Join-Path $automationDir "orchestrate.log"
$reportsDir      = Join-Path $automationDir "reports"
$statePath       = Join-Path $automationDir "state.json"

# -- Logging -------------------------------------------------------------------

function Write-Log {
    param([string]$Message, [switch]$Status)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    if (-not ($Status -and $Quiet)) {
        Write-Host $line
    }
    if ($LogFile) {
        # Why: the log file may live inside the Mutagen-synced NTFS mirror (when the
        # project root resolves to the beta endpoint). Mutagen's periodic scan briefly
        # opens it and collides with this append, surfacing as "stream not readable"
        # (GetContentWriterArgumentError). With the script-level $ErrorActionPreference
        # = "Stop", that transient error would abort the watcher BEFORE it suspends the
        # host — defeating its entire purpose. So retry a few times, then degrade to
        # console-only: logging must never be fatal. -Encoding UTF8 matches the wrapper's
        # Set-Content truncation so the file stays single-encoding (em-dashes write clean).
        for ($attempt = 1; $attempt -le 5; $attempt++) {
            try {
                Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8 -ErrorAction Stop
                break
            } catch {
                if ($attempt -eq 5) {
                    Write-Host ("[WARN] log write failed after {0} attempts (continuing console-only): {1}" -f $attempt, $_.Exception.Message) -ForegroundColor Yellow
                } else {
                    Start-Sleep -Milliseconds 200
                }
            }
        }
    }
}

# -- Detection -----------------------------------------------------------------

function Test-SentinelPresent {
    return (Test-Path -LiteralPath $sentinelPath)
}

function Get-LogMTime {
    if (-not (Test-Path -LiteralPath $orchestrateLog)) { return $null }
    return (Get-Item -LiteralPath $orchestrateLog).LastWriteTime
}

function Test-LogActive {
    $mtime = Get-LogMTime
    if ($null -eq $mtime) { return $false }
    $ageMinutes = ((Get-Date) - $mtime).TotalMinutes
    return ($ageMinutes -lt $LogStaleMinutes)
}

function Get-LastLogLine {
    if (-not (Test-Path -LiteralPath $orchestrateLog)) { return "" }
    try { return (Get-Content -LiteralPath $orchestrateLog -Tail 1 -Encoding UTF8 -ErrorAction Stop) }
    catch { return "" }
}

function Invoke-TimezoneCheck {
    param(
        [string]   $LogLine,   # last line of orchestrate.log
        [datetime] $HostNow    # host clock snapshot (passed in, not re-read, for consistency)
    )
    # Parse [orchestrator HH:MM:SS] from the log line
    if (-not ($LogLine -match '^\[orchestrator (\d{2}):(\d{2}):(\d{2})\]')) { return }

    $h = [int]$Matches[1]; $m = [int]$Matches[2]; $s = [int]$Matches[3]
    # Reconstruct on today's date so we can diff against host time
    $logTime = Get-Date -Year $HostNow.Year -Month $HostNow.Month -Day $HostNow.Day `
                        -Hour $h -Minute $m -Second $s -Millisecond 0

    $diffMin = ($HostNow - $logTime).TotalMinutes
    # Clamp into [-720, +720] to handle entries that straddle midnight
    if ($diffMin -gt  720) { $diffMin -= 1440 }
    if ($diffMin -lt -720) { $diffMin += 1440 }

    if ([math]::Abs($diffMin) -gt 30) {
        Write-Log "ERROR: Container timezone does not match host OS timezone!"
        Write-Log ("  Container log time : {0:D2}:{1:D2}:{2:D2}" -f $h, $m, $s)
        Write-Log ("  Host OS time       : {0}" -f $HostNow.ToString("HH:mm:ss"))
        $sign = if ($diffMin -ge 0) { "+" } else { "" }
        Write-Log ("  Difference         : {0}{1:N0} min" -f $sign, $diffMin)
        Write-Log "  Fix: set the TZ env-var in the dev container to match the host (e.g. TZ=Europe/Berlin)."
    }
}

function Format-UtcOffset {
    param([timespan]$Offset)
    $sign = if ($Offset.TotalHours -ge 0) { "+" } else { "-" }
    return ("{0}{1:D2}:{2:D2}" -f $sign, [math]::Abs([int]$Offset.Hours), [math]::Abs([int]$Offset.Minutes))
}

# Why: state.json exposes both 'timezone' (IANA name) and 'timezone_offset' (raw
# '+HH:MM' / '-HH:MM' string) so we can detect container/host timezone mismatch
# at startup. The offset is preferred because Windows PowerShell 5.1 cannot
# resolve IANA names like 'Europe/Berlin' via TimeZoneInfo.FindSystemTimeZoneById
# (only Windows zone IDs); PowerShell 7 / .NET 6+ can resolve both. When this
# check fires, $tzCheckDone is set so the log-timestamp heuristic is skipped to
# avoid double-warning. The $HostTzOverride parameter is injected by unit tests
# to avoid a real local-tz lookup.
function Test-ContainerTimezone {
    param(
        [string]              $ContainerTzName   = "",
        [string]              $ContainerTzOffset = "",
        [System.TimeZoneInfo] $HostTzOverride    = $null
    )
    if (-not $ContainerTzName -and -not $ContainerTzOffset) { return }

    $hostTz  = if ($HostTzOverride) { $HostTzOverride } else { [System.TimeZoneInfo]::Local }
    $nowUtc  = [datetime]::UtcNow
    $hOffset = $hostTz.GetUtcOffset($nowUtc)
    $cOffset = $null
    $cLabel  = ""

    # Prefer the raw offset — works on every PowerShell version, no zone-name database needed.
    if ($ContainerTzOffset) {
        if ($ContainerTzOffset -match '^([+-])(\d{2}):(\d{2})$') {
            $signMul = if ($Matches[1] -eq '-') { -1 } else { 1 }
            $cOffset = [TimeSpan]::FromMinutes($signMul * ([int]$Matches[2] * 60 + [int]$Matches[3]))
            $cLabel  = if ($ContainerTzName) { "{0} ({1})" -f $ContainerTzName, $ContainerTzOffset } else { $ContainerTzOffset }
        } else {
            Write-Log "WARNING: timezone_offset '$ContainerTzOffset' is not in '+HH:MM' / '-HH:MM' format; falling back to name resolution."
        }
    }

    # Fallback: resolve IANA name. Only works on PowerShell 7 / .NET 6+ (or when the
    # name happens to be a Windows zone ID).
    if ($null -eq $cOffset -and $ContainerTzName) {
        try {
            $containerTzInfo = [System.TimeZoneInfo]::FindSystemTimeZoneById($ContainerTzName)
            $cOffset = $containerTzInfo.GetUtcOffset($nowUtc)
            $cLabel  = $ContainerTzName
        } catch {
            Write-Log "WARNING: Cannot resolve container timezone '$ContainerTzName' on this Windows host ($($_.Exception.Message)). Upgrade orchestrator to emit timezone_offset in state.json, or run this script under PowerShell 7."
            return
        }
    }

    if ($null -eq $cOffset) { return }

    if ($cOffset -ne $hOffset) {
        Write-Log ("WARNING: Container timezone {0} (UTC{1}) differs from host timezone '{2}' (UTC{3})." -f `
            $cLabel, (Format-UtcOffset $cOffset), $hostTz.Id, (Format-UtcOffset $hOffset))
        Write-Log "  Container timestamps may appear offset vs. host time."
        if ($ContainerTzName) {
            Write-Log ("  Fix: set TZ={0} in the dev-container (or adjust the host timezone to match)." -f $ContainerTzName)
        }
    }
}

function Get-StopReason {
    if (-not (Test-Path -LiteralPath $orchestrateLog)) { return $null }
    try {
        $tail = Get-Content -LiteralPath $orchestrateLog -Tail 50 -Encoding UTF8 -ErrorAction Stop
        $stopLine = $tail | Where-Object { $_ -match 'Stopped\. Reason:' } | Select-Object -Last 1
        if ($stopLine) { return $stopLine }
        $maxLine  = $tail | Where-Object { $_ -match 'Reached --max-tasks' } | Select-Object -Last 1
        if ($maxLine)  { return $maxLine  }
        return $null
    } catch { return $null }
}

function Get-LatestReportName {
    if (-not (Test-Path -LiteralPath $reportsDir)) { return $null }
    $latest = Get-ChildItem -LiteralPath $reportsDir -Filter "*.md" -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) { return $latest.Name }
    return $null
}

# Why: state.json -> rate_limited_until is the orchestrator's source of truth for
# when each account becomes usable again. Disabled (no-access) accounts live only
# in the orchestrator's in-memory state, so they never appear here  -  meaning we
# automatically pick the earliest reset across only the *working but limited*
# accounts. Stale entries (reset already in the past) are filtered: the orchestrator
# only purges them on the next attempt to use that account, so they linger in
# state.json and would otherwise mask a still-active limit on another account.
#
# Returns hashtable @{
#   Earliest    = [datetime?]                  # earliest *future* reset
#   Active      = @{ name = [datetime] }       # accounts still rate-limited (future)
#   Stale       = @{ name = [datetime] }       # entries whose reset is already past
# }
function Get-RateLimitState {
    param([string]$Path = $statePath)
    if (-not (Test-Path -LiteralPath $Path)) {
        return @{ Earliest = $null; Active = @{}; Stale = @{} }
    }
    try {
        $json = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        Write-Log "WARNING: state.json could not be parsed: $($_.Exception.Message)"
        return @{ Earliest = $null; Active = @{}; Stale = @{} }
    }

    if (-not ($json.PSObject.Properties['rate_limited_until'])) {
        return @{ Earliest = $null; Active = @{}; Stale = @{} }
    }

    $now      = Get-Date
    $active   = @{}
    $stale    = @{}
    $earliest = $null

    foreach ($prop in $json.rate_limited_until.PSObject.Properties) {
        $accountName = $prop.Name
        $isoStr      = [string]$prop.Value
        try {
            # RoundtripKind preserves the UTC offset from the ISO string (state.json stores UTC).
            # .ToLocalTime() converts to local so that comparisons against Get-Date (local Kind)
            # and the wake-up arithmetic on $earliest are all in the same timezone.
            $dt = ([datetime]::Parse(
                $isoStr,
                [System.Globalization.CultureInfo]::InvariantCulture,
                [System.Globalization.DateTimeStyles]::RoundtripKind
            )).ToLocalTime()
        } catch {
            Write-Log "WARNING: rate_limited_until[$accountName] not parseable: $isoStr"
            continue
        }

        if ($dt -le $now) {
            # Already past  -  orchestrator hasn't purged it yet but the account is usable
            $stale[$accountName] = $dt
            continue
        }

        $active[$accountName] = $dt
        if ($null -eq $earliest -or $dt -lt $earliest) { $earliest = $dt }
    }

    return @{ Earliest = $earliest; Active = $active; Stale = $stale }
}

# Why: state.json is the single source of truth for orchestrator runtime state (AC-34..AC-38).
# This helper reads is_running, stop_requested, rate_limit_reached, next_wake_time and
# active_session in one pass and returns a typed hashtable. Returning Available=$false (rather
# than throwing) lets callers fall back to the sentinel + log-mtime heuristic without try/catch
# at every call site. The inner _getProp helper avoids PowerShell's property-not-found
# exception that occurs when reading a missing property on a PSCustomObject in StrictMode.
# Source: requirements_tasks/.../plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md#phase-2b-step-2
function Get-OrchestratorState {
    param([string]$Path = $statePath)
    $defaultMissing = @{
        Available        = $false
        IsRunning        = $null
        StopRequested    = $null
        RateLimitReached = $null
        NextWakeTime     = $null
        ActiveSession    = $null
        Timezone         = $null
        TimezoneOffset   = $null
    }
    if (-not (Test-Path -LiteralPath $Path)) { return $defaultMissing }
    try {
        $json = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        Write-Log "WARNING: state.json could not be parsed: $($_.Exception.Message)"
        return $defaultMissing
    }

    function _getProp($obj, $name) {
        if ($obj.PSObject.Properties[$name]) { return $obj.$name }
        return $null
    }

    $nextWakeRaw = _getProp $json 'next_wake_time'
    $nextWake = $null
    if ($nextWakeRaw) {
        try {
            $nextWake = ([datetime]::Parse(
                [string]$nextWakeRaw,
                [System.Globalization.CultureInfo]::InvariantCulture,
                [System.Globalization.DateTimeStyles]::RoundtripKind
            )).ToLocalTime()
        } catch {
            Write-Log "WARNING: next_wake_time not parseable: $nextWakeRaw"
        }
    }

    return @{
        Available        = $true
        IsRunning        = _getProp $json 'is_running'
        StopRequested    = _getProp $json 'stop_requested'
        RateLimitReached = _getProp $json 'rate_limit_reached'
        NextWakeTime     = $nextWake
        ActiveSession    = _getProp $json 'active_session'
        Timezone         = _getProp $json 'timezone'
        TimezoneOffset   = _getProp $json 'timezone_offset'
    }
}

# Why: state.json["is_running"] is the authoritative signal (AC-36). The sentinel
# + log-mtime fallback is retained for older orchestrators that don't yet write
# is_running, and for cases where state.json itself is unreadable.
# Source: requirements_tasks/.../plans_and_protocols/2026-04-30_01_plan_state-json-consolidation.md#phase-2b-step-3
function Test-OrchestratorActive {
    $st = Get-OrchestratorState
    if ($st.Available -and $null -ne $st.IsRunning) {
        return [bool]$st.IsRunning
    }
    # Fallback path: sentinel + log-mtime heuristic (covers older orchestrators and SIGKILL)
    if (-not (Test-SentinelPresent)) { return $false }
    return (Test-LogActive)
}

# -- Privileges + wake-task ----------------------------------------------------

# Why: extracting wake-time computation into a pure function enables unit tests
# without filesystem access, clock dependency, or admin rights.
# Returns @{ WakeAt = [datetime?]; Source = [string] }
function Get-WakeTime {
    param(
        [bool] $RateLimitBreak,
        $State,
        $RateLimitState,
        [int]  $WakeBeforeMinutes
    )
    # Why: only schedule a wake when the orchestrator is actively waiting for a
    # rate-limit reset. Normal stops (max-tasks, manual stop, error, SIGKILL) must
    # leave the PC asleep — otherwise stale rate_limited_until entries from a
    # previous session would wake the PC pointlessly.
    if (-not $RateLimitBreak) {
        return @{ WakeAt = $null; Source = "orchestrator stopped (not a rate-limit wait)" }
    }
    if ($State.Available -and $null -ne $State.NextWakeTime) {
        return @{ WakeAt = $State.NextWakeTime.AddMinutes(-$WakeBeforeMinutes); Source = "state.json next_wake_time" }
    }
    if ($null -eq $RateLimitState -or $RateLimitState.Active.Count -eq 0) {
        return @{ WakeAt = $null; Source = "no active rate limits" }
    }
    return @{ WakeAt = $RateLimitState.Earliest.AddMinutes(-$WakeBeforeMinutes); Source = "rate_limited_until earliest" }
}

# Why: a wake computed at/near "now" is not worth an S3 suspend/resume cycle, and is
# risky — the 15s suspend countdown can push the real suspend PAST the trigger time,
# so the RTC wake alarm never fires and the host stays asleep. This pure predicate
# (clock injected as $Now, not read) lets the suspend decision be unit-tested without
# a real clock or admin rights. Returns $true when the host should suspend; $false
# means "wake is too soon (or already past) — re-poll instead of sleeping".
function Test-WakeWorthSuspend {
    param(
        [datetime] $WakeAt,
        [datetime] $Now,
        [int]      $MinSleepMinutes
    )
    return (($WakeAt - $Now).TotalMinutes -ge $MinSleepMinutes)
}

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($id)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Register-WakeTask {
    param([datetime]$WakeAt)

    if (-not (Test-IsAdmin)) {
        throw "Wake-up requires admin rights to register a SYSTEM scheduled task. Re-run PowerShell as Administrator, or pass -NoWake."
    }

    $action   = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c rem autorun-wake"
    $trigger  = New-ScheduledTaskTrigger -Once -At $WakeAt
    $settings = New-ScheduledTaskSettingsSet `
                    -WakeToRun `
                    -StartWhenAvailable `
                    -AllowStartIfOnBatteries `
                    -DontStopIfGoingOnBatteries
    # Why: SYSTEM/ServiceAccount fires even when no interactive session exists (required
    # for wake-from-sleep); Interactive logon is silently skipped while the PC sleeps.
    $principal = New-ScheduledTaskPrincipal `
                    -UserId "SYSTEM" `
                    -LogonType ServiceAccount `
                    -RunLevel Highest

    Register-ScheduledTask `
        -TaskName  $WakeTaskName `
        -Action    $action `
        -Trigger   $trigger `
        -Settings  $settings `
        -Principal $principal `
        -Force | Out-Null

    Write-Log ("Wake task '{0}' registered for {1}." -f $WakeTaskName, $WakeAt.ToString("yyyy-MM-dd HH:mm:ss"))
}

# -- Stay-awake (power request) -----------------------------------------------

# Why: hold a system-required power request while the watcher is awake. Windows'
# "Unattended Sleep Timeout" (default ~2 min on AC) fires shortly after a
# scheduled-task wake and idle-resleeps the system unless some process is holding
# a SetThreadExecutionState request. CPU activity — including WSL2 work — does
# NOT count toward "non-idle"; only explicit power requests do. Without this,
# the orchestrator's first post-wake window gets cut short before any account
# unlock can actually be used.
#
# Per-thread state: SetThreadExecutionState is per-calling-thread. PowerShell
# scripts run on a single STA thread, so one call at startup holds across the
# rest of the script (including across explicit suspend transitions — the
# request resumes with the thread). The 'if -as [type]' guard prevents
# Add-Type duplicate-type errors when the script is dot-sourced by Pester.
if (-not ('WinSleepWatcher.PowerApi' -as [type])) {
    Add-Type -MemberDefinition @'
[DllImport("kernel32.dll", SetLastError=true)]
public static extern uint SetThreadExecutionState(uint esFlags);
'@ -Name "PowerApi" -Namespace "WinSleepWatcher" | Out-Null
}
# Why: Windows PowerShell 5.1 parses hex literals as Int32, so 0x80000000 overflows
# to -2147483648 and the [uint32] cast then throws "Wert für UInt32 war zu groß/klein".
# Decimal literal 2147483648 is auto-promoted to Int64 (it doesn't fit in Int32) and
# casts to uint32 cleanly on both PS 5.1 and PS 7. The hex form is kept in a trailing
# comment so the Win32 flag value remains readable.
$ES_CONTINUOUS      = [uint32]2147483648  # 0x80000000
$ES_SYSTEM_REQUIRED = [uint32]1           # 0x00000001

function Set-StayAwake {
    $flags = [uint32]($ES_CONTINUOUS -bor $ES_SYSTEM_REQUIRED)
    [void][WinSleepWatcher.PowerApi]::SetThreadExecutionState($flags)
}

function Clear-StayAwake {
    [void][WinSleepWatcher.PowerApi]::SetThreadExecutionState($ES_CONTINUOUS)
}

# -- Suspend -------------------------------------------------------------------

# Why: Win32 API via System.Windows.Forms is reliable; rundll32 powrprof
# silently ignores its parameters in many Windows builds.
function Invoke-SystemSleep {
    param([switch]$UseHibernate)

    Add-Type -AssemblyName System.Windows.Forms
    $state = if ($UseHibernate) {
        [System.Windows.Forms.PowerState]::Hibernate
    } else {
        [System.Windows.Forms.PowerState]::Suspend
    }
    # SetSuspendState(state, force=false, disableWakeEvent=false)
    # disableWakeEvent MUST be false for scheduled wake tasks to fire.
    [void][System.Windows.Forms.Application]::SetSuspendState($state, $false, $false)
}

# -- Main ----------------------------------------------------------------------

if (-not $env:PESTER_TESTING) {

# -- TestMode short-circuit ----------------------------------------------------
# Self-contained sleep/wake verification — does not touch the orchestrator.
if ($TestMode) {
    if ($NoWake) {
        throw "-TestMode is incompatible with -NoWake (the test verifies wake-from-sleep)."
    }
    if (-not (Test-IsAdmin)) {
        throw "-TestMode needs Administrator to register the wake task. Re-run elevated."
    }

    Write-Log "--- sleep_when_autorun_done [TEST MODE] -----------------------"
    Write-Log ("Suspend mode  : {0}" -f $(if ($Hibernate) { "Hibernate (S4)" } else { "Sleep (S3)" }))
    Write-Log "Cycle 1       : suspend in 5s,   wake ~30s later"
    Write-Log "Cycle 2       : stay awake 180s (Unattended-Sleep-Timeout check), then suspend, wake ~30s later"
    if ($DryRun) { Write-Log "Mode          : DRY RUN (no actual suspend, wake task still registered)" }
    Write-Log ""

    # Hold the same power request the babysitter loop uses, so TestMode exercises
    # the actual fix end-to-end. Without this, Cycle 2's 180s pre-suspend wait
    # would idle-resleep after ~2 min (Windows Unattended Sleep Timeout), the
    # already-scheduled wake task would bring it back ~2 min late, and Start-Sleep
    # would resume to a delayed completion — exactly the bug we want to detect.
    Set-StayAwake

    try {

    # Windows arms the RTC wake alarm ~30s BEFORE the task trigger time (system warmup
    # margin so the OS can boot and run the task on schedule). We need the alarm to fire
    # WHILE the PC is suspended, not before. So the task itself must be scheduled at
    # (desired_wake_time + WAKE_MARGIN). Concretely: with WAKE_MARGIN=30s, scheduling the
    # task 65s out means the alarm fires at +35s — exactly when we want to wake.
    $WAKE_MARGIN_SEC = 30

    # Why Cycle 2 WaitBeforeSleep=180s: the failure mode is "system idle-resleeps after
    # an unattended wake because no process is holding ES_SYSTEM_REQUIRED". The default
    # Unattended Sleep Timeout on AC is ~2 min, so the awake window must exceed that
    # to be a real test. 180s gives a 60s margin over the typical default. The wake
    # task is still pre-registered at WaitBeforeSleep + SleepDuration + WAKE_MARGIN, so
    # even if the stay-awake mechanism fails, the system is rescued by the scheduled
    # wake — Start-Sleep just takes longer than expected, which the elapsed check below
    # detects and reports as FAIL.
    $cycles = @(
        @{ Label = "1/2"; WaitBeforeSleep = 5;   SleepDuration = 30 },
        @{ Label = "2/2"; WaitBeforeSleep = 180; SleepDuration = 30 }
    )
    foreach ($c in $cycles) {
        $desiredWakeOffset = $c.WaitBeforeSleep + $c.SleepDuration
        $taskOffset        = $desiredWakeOffset + $WAKE_MARGIN_SEC
        $wakeAt            = (Get-Date).AddSeconds($taskOffset)
        Write-Log ("[Cycle {0}] Scheduling task at {1} ({2}s from now; expected RTC wake {3}s from now after {4}s OS warmup margin)" -f `
                   $c.Label, $wakeAt.ToString("yyyy-MM-dd HH:mm:ss"), `
                   $taskOffset, $desiredWakeOffset, $WAKE_MARGIN_SEC)
        Register-WakeTask -WakeAt $wakeAt

        # Diagnostic: confirm task is registered with WakeToRun, and that the OS has armed
        # an RTC wake timer. If powercfg /waketimers does not list AutorunWakePC right here,
        # the BIOS/chipset will never wake the PC — root cause is OS-level, not our script.
        Write-Log ("[Cycle {0}] -- Diagnostic: scheduled task settings --" -f $c.Label)
        function _safeProp($obj, $name) {
            if ($null -eq $obj) { return "<null>" }
            if ($obj.PSObject.Properties[$name]) { return [string]$obj.$name }
            return "<missing>"
        }
        try {
            $task = Get-ScheduledTask -TaskName $WakeTaskName -ErrorAction Stop
            $s    = $task.Settings
            Write-Log ("  WakeToRun={0}  AllowStartIfOnBatteries={1}  StartWhenAvailable={2}  Enabled={3}" -f `
                       (_safeProp $s 'WakeToRun'), (_safeProp $s 'AllowStartIfOnBatteries'), `
                       (_safeProp $s 'StartWhenAvailable'), (_safeProp $task 'State'))
            $info = Get-ScheduledTaskInfo -TaskName $WakeTaskName
            Write-Log ("  NextRunTime={0}  LastRunTime={1}  LastTaskResult={2}" -f `
                       (_safeProp $info 'NextRunTime'), (_safeProp $info 'LastRunTime'), `
                       (_safeProp $info 'LastTaskResult'))
        } catch {
            Write-Log ("  Could not read task info: {0}" -f $_.Exception.Message)
        }
        Write-Log ("[Cycle {0}] -- Diagnostic: powercfg /waketimers --" -f $c.Label)
        $wt = (powercfg /waketimers 2>&1 | Out-String).TrimEnd()
        foreach ($line in ($wt -split "`r?`n")) {
            if ($line.Trim()) { Write-Log ("  {0}" -f $line) }
        }
        if ($wt -notmatch [regex]::Escape($WakeTaskName)) {
            Write-Log ("  WARNING: '{0}' NOT listed in /waketimers — OS did not arm a wake alarm." -f $WakeTaskName)
            Write-Log "           Likely causes: 'Allow wake timers' disabled on current power source,"
            Write-Log "           Group Policy override, or BIOS does not honor RTC wake from S3."
        }

        Write-Log ("[Cycle {0}] Awake window: {1}s before suspend (Ctrl+C to abort)" -f $c.Label, $c.WaitBeforeSleep)
        $waitStart = Get-Date
        Start-Sleep -Seconds $c.WaitBeforeSleep
        $waitElapsed = ((Get-Date) - $waitStart).TotalSeconds

        # Stay-awake assertion: Start-Sleep should complete in ~WaitBeforeSleep
        # wall-clock seconds. If the OS idle-resleeps during the awake window,
        # Start-Sleep is paused for the duration of the system sleep, so elapsed
        # wall-clock exceeds expected by that much. 30s tolerance absorbs normal
        # scheduler jitter / clock drift.
        $waitDelta = $waitElapsed - [double]$c.WaitBeforeSleep
        Write-Log ("[Cycle {0}] Awake-window elapsed: {1:N1}s (expected {2}s, delta {3:+0.0;-0.0;0.0}s)" -f `
                   $c.Label, $waitElapsed, $c.WaitBeforeSleep, $waitDelta)
        if ($c.WaitBeforeSleep -ge 60 -and $waitDelta -gt 30) {
            Write-Log ("[Cycle {0}] STAY-AWAKE FAIL: system idle-resleep during the awake window — SetThreadExecutionState is not holding. Inspect powercfg /requests + Kernel-Power 42 events." -f $c.Label)
        } elseif ($c.WaitBeforeSleep -ge 60) {
            Write-Log ("[Cycle {0}] STAY-AWAKE PASS: system stayed awake the full {1}s window." -f $c.Label, $c.WaitBeforeSleep)
        }

        if ($DryRun) {
            Write-Log ("[Cycle {0}] DRY RUN — would suspend now. Sleeping {1}s instead to let wake task fire harmlessly." -f $c.Label, $c.SleepDuration)
            Start-Sleep -Seconds $c.SleepDuration
        } else {
            $beforeSleep = Get-Date
            Invoke-SystemSleep -UseHibernate:$Hibernate
            $afterSleep  = Get-Date
            $sleptSec    = [int]($afterSleep - $beforeSleep).TotalSeconds
            Write-Log ("[Cycle {0}] Resumed from suspend at {1} (slept {2}s)" -f $c.Label, $afterSleep.ToString("yyyy-MM-dd HH:mm:ss"), $sleptSec)

            # Re-assert defensively; SetThreadExecutionState should survive suspend
            # but driver edge-cases on some hardware may clear it.
            Set-StayAwake

            Write-Log ("[Cycle {0}] -- Diagnostic: powercfg /lastwake --" -f $c.Label)
            $lw = (powercfg /lastwake 2>&1 | Out-String).TrimEnd()
            foreach ($line in ($lw -split "`r?`n")) {
                if ($line.Trim()) { Write-Log ("  {0}" -f $line) }
            }
        }
    }

    try {
        Unregister-ScheduledTask -TaskName $WakeTaskName -Confirm:$false -ErrorAction Stop
        Write-Log ("Wake task '{0}' unregistered." -f $WakeTaskName)
    } catch {
        Write-Log ("Wake task cleanup skipped: {0}" -f $_.Exception.Message)
    }

    Write-Log "Test mode completed successfully."
    } finally {
        Clear-StayAwake
    }
    return
}

# Validate paths early
if (-not (Test-Path -LiteralPath $automationDir)) {
    throw "Automation directory not found: $automationDir (check -ProjectPath)"
}

# Validate admin up-front when wake-up is possible (we don't yet know if state.json
# will have rate limits, but failing early is better than after the orchestrator stops)
if (-not $NoWake -and -not (Test-IsAdmin)) {
    throw "Wake-up is enabled by default and needs Administrator. Re-run elevated, or pass -NoWake."
}

Write-Log "--- sleep_when_autorun_done --------------------------"
Write-Log "Project       : $ProjectPath"
Write-Log "Poll interval : ${PollSeconds}s"
Write-Log "Log-stale     : ${LogStaleMinutes} min (treats no log activity as 'done', fallback path only)"
Write-Log ("Suspend mode  : {0}" -f $(if ($Hibernate) { "Hibernate (S4)" } else { "Sleep (S3)" }))
if ($NoWake) {
    Write-Log "Wake-up       : disabled (-NoWake)"
} else {
    Write-Log "Wake-up       : auto, ${WakeBeforeResetMinutes} min before earliest rate-limit reset"
    Write-Log "Min sleep     : ${MinSleepMinutes} min (shorter computed sleeps re-poll instead of suspending)"
}
if ($DryRun) { Write-Log "Mode          : DRY RUN (no actual suspend)" }
Write-Log ""

# Wait for orchestrator to start (covers "I started this script first")
$waitedForStart = $false
while (-not (Test-OrchestratorActive)) {
    if (-not $waitedForStart) {
        Write-Log "Orchestrator not active yet  -  waiting for it to start..."
        $waitedForStart = $true
    }
    Start-Sleep -Seconds $PollSeconds
}

Write-Log "Orchestrator is active. Polling..."

# One-time timezone check: prefer state.json 'timezone_offset' (raw UTC offset,
# works on PowerShell 5.1) and fall back to 'timezone' (IANA name, needs pwsh 7+
# or a Windows zone ID). Immediate and exact — no need to wait for the 2nd log write.
$stForTz = Get-OrchestratorState
if ($stForTz.Available -and ($stForTz.Timezone -or $stForTz.TimezoneOffset)) {
    Test-ContainerTimezone -ContainerTzName $stForTz.Timezone -ContainerTzOffset $stForTz.TimezoneOffset
}

# Track when stop is requested so we can show it during polling
$stopRequestedAnnounced = $false

# Timezone-mismatch check state (log-timestamp heuristic — fallback for older orchestrators).
# Strategy: watch for the 2nd new log write after startup. On the 2nd write, compare the
# log timestamp against the host clock. We use the 2nd write (not the 1st) so that a
# wake-from-sleep event — where the script sees an old pre-sleep entry as "new" — does
# not trigger a false alarm. Between entry-1 and entry-2 observations we check whether
# the host clock jumped by more than 3x the poll interval; if it did, the laptop slept
# and we reset the state to treat the current entry as the new entry-1.
$tzBaselineMTime  = Get-LogMTime   # mtime at monitoring start — only writes AFTER this count
$tzEntry1MTime    = $null          # mtime at first new write
$tzEntry1HostTime = $null          # host clock when entry-1 was observed
# Skip log-timestamp heuristic when state.json already provided timezone info (new orchestrator)
$tzCheckDone      = ($stForTz.Available -and ($null -ne $stForTz.Timezone -or $null -ne $stForTz.TimezoneOffset))
$tzSleepThreshold = [math]::Max(3 * $PollSeconds, 180)   # seconds; at least 3 min

# Babysitter loop: poll → on rate-limit, suspend with scheduled wake → resume →
# re-enter polling. Exits only on normal orchestrator stop (or DryRun / no-wake
# stop / user abort). Why: a single orchestrator run may traverse multiple
# rate-limit cycles as accounts unlock sequentially (e.g. account A resets at
# 02:25, account B at 03:05, account C at 05:00). The old single-cycle design
# would suspend once, wake once, then exit — leaving the PC awake (and burning
# power) through any subsequent rate-limit waits with no auto-resleep.
#
# $rateLimitBreak distinguishes a normal stop (is_running flipped false) from
# an early exit triggered by rate_limit_reached=true. The two cases need
# different wake scheduling: rate-limit break uses next_wake_time directly;
# normal stop uses rate_limited_until. Source: AC-37 in plan Phase 2b Step 4.
#
# Set-StayAwake holds ES_SYSTEM_REQUIRED so Windows does not idle-resleep the
# host during the post-wake polling window (Unattended Sleep Timeout, default
# ~2 min on AC, fires after scheduled-task wakes). Released in finally on any
# exit path.
Set-StayAwake

try {
    $cycleNum = 0
    while ($true) {
        $cycleNum++
        $rateLimitBreak = $false

        # -- Inner poll: wait until orchestrator stops or enters rate-limit wait --
        while (Test-OrchestratorActive) {
            $lastLine = Get-LastLogLine
            $mtime    = Get-LogMTime
            $ageSec   = if ($mtime) { [int]((Get-Date) - $mtime).TotalSeconds } else { -1 }

            $st = Get-OrchestratorState

            if ($st.Available -and $true -eq $st.StopRequested -and -not $stopRequestedAnnounced) {
                Write-Log "Stop already requested  -  orchestrator will exit after current session."
                $stopRequestedAnnounced = $true
            }

            # AC-37: when orchestrator is just waiting for rate-limit reset, sleep PC immediately
            # rather than waiting for is_running to flip false (which could be hours away).
            if ($st.Available -and $true -eq $st.RateLimitReached) {
                Write-Log "Orchestrator is waiting for rate-limit reset (state.json rate_limit_reached=true)."
                $rateLimitBreak = $true
                break
            }

            # -- Timezone check (runs at most once per invocation) --
            if (-not $tzCheckDone -and $null -ne $mtime -and $mtime -ne $tzBaselineMTime) {
                if ($null -eq $tzEntry1MTime) {
                    # First new write observed — store it, wait for the next one
                    $tzEntry1MTime    = $mtime
                    $tzEntry1HostTime = Get-Date
                } elseif ($mtime -ne $tzEntry1MTime) {
                    $hostNow = Get-Date
                    $gapSec  = ($hostNow - $tzEntry1HostTime).TotalSeconds
                    if ($gapSec -gt $tzSleepThreshold) {
                        # Host clock jumped too much — laptop probably slept between the two
                        # observations. Reset so this write becomes the new entry-1.
                        Write-Log ("TZ-check: host gap {0:N0}s since entry-1 — likely woke from sleep, resetting observation." -f $gapSec)
                        $tzEntry1MTime    = $mtime
                        $tzEntry1HostTime = $hostNow
                    } else {
                        Invoke-TimezoneCheck -LogLine $lastLine -HostNow $hostNow
                        $tzCheckDone = $true
                    }
                }
            }

            Write-Log -Status ("running (log age {0}s)  -  {1}" -f $ageSec, $lastLine)
            Start-Sleep -Seconds $PollSeconds
        }

        # -- Stop reporting --
        Write-Log ""
        if ($rateLimitBreak) {
            Write-Log ("Cycle {0}: orchestrator hit rate-limit. Checking wake schedule." -f $cycleNum)
        } else {
            Write-Log "Orchestrator stopped."

            # Prefer stop_reason from state.json (AC-34) over log-grepping.
            $stFinal = Get-OrchestratorState
            $stopReason = $null
            if ($stFinal.Available) {
                try {
                    $rawJson = Get-Content -LiteralPath $statePath -Raw -ErrorAction Stop | ConvertFrom-Json
                    if ($rawJson.PSObject.Properties['stop_reason'] -and $null -ne $rawJson.stop_reason) {
                        $stopReason = "state.json: $($rawJson.stop_reason)"
                    }
                } catch { }
            }
            if (-not $stopReason) {
                $logReason = Get-StopReason
                if ($logReason) { $stopReason = $logReason }
            }
            if ($stopReason) { Write-Log ("Stop reason   : {0}" -f $stopReason) }

            $report = Get-LatestReportName
            if ($report) { Write-Log ("Latest report : {0}" -f $report) }
        }

        # -- Wake scheduling (only schedules when in rate-limit break; on normal
        # stop Get-WakeTime returns null and we suspend without a wake task).
        $wakeRegistered = $false
        if (-not $NoWake) {
            $st = Get-OrchestratorState
            $rl = Get-RateLimitState

            foreach ($name in ($rl.Stale.Keys | Sort-Object)) {
                $resetAt = $rl.Stale[$name].ToLocalTime()
                Write-Log ("Rate-limit    : {0} -> stale (reset {1} already past, account usable)" -f `
                           $name, $resetAt.ToString("yyyy-MM-dd HH:mm:ss"))
            }
            foreach ($name in ($rl.Active.Keys | Sort-Object)) {
                $resetAt = $rl.Active[$name].ToLocalTime()
                Write-Log ("Rate-limited  : {0} -> resets {1}" -f $name, $resetAt.ToString("yyyy-MM-dd HH:mm:ss"))
            }

            $wake = Get-WakeTime -RateLimitBreak $rateLimitBreak -State $st -RateLimitState $rl `
                                  -WakeBeforeMinutes $WakeBeforeResetMinutes

            if ($null -eq $wake.WakeAt) {
                Write-Log ("Wake-up       : skipped  -  {0}" -f $wake.Source)
            } else {
                $now = Get-Date
                if (-not (Test-WakeWorthSuspend -WakeAt $wake.WakeAt -Now $now -MinSleepMinutes $MinSleepMinutes)) {
                    # Why: wake is too soon (or already past) to be worth an S3 suspend cycle.
                    # Already-past means the rate-limit window has elapsed (orchestrator should
                    # clear rate_limit_reached soon); a near-future wake below MinSleepMinutes
                    # would be defeated by the 15s suspend countdown overshooting the trigger.
                    # Either way: stay awake and wait one full poll interval before re-checking,
                    # so we do not busy-spin (a missing sleep here once caused ~13 000 log lines
                    # across 2 621 tight cycles over 6 min in the field).
                    if ($wake.WakeAt -le $now) {
                        Write-Log ("Wake-up       : computed wake {0:N0} sec ago — account(s) likely unlocked; re-polling after {1}s" -f `
                                   (($now - $wake.WakeAt).TotalSeconds), $PollSeconds)
                    } else {
                        Write-Log ("Wake-up       : computed wake only {0:N1} min away (< MinSleep {1} min) — too short to suspend; re-polling after {2}s" -f `
                                   (($wake.WakeAt - $now).TotalMinutes), $MinSleepMinutes, $PollSeconds)
                    }
                    Start-Sleep -Seconds $PollSeconds
                    continue
                }
                $sleepMinutes = [int]([math]::Round(($wake.WakeAt - $now).TotalMinutes))
                Write-Log ("Wake-up       : source={0}, waking at {1} (sleeping ~{2} min)" -f `
                           $wake.Source, $wake.WakeAt.ToString("yyyy-MM-dd HH:mm:ss"), $sleepMinutes)
                Register-WakeTask -WakeAt $wake.WakeAt
                $wakeRegistered = $true
            }
        }

        # -- Suspend --
        if ($DryRun) {
            Write-Log "DRY RUN  -  would suspend now. Exiting."
            break
        }

        Write-Log "Suspending in 15s... (Ctrl+C to abort)"
        Start-Sleep -Seconds 15

        Invoke-SystemSleep -UseHibernate:$Hibernate

        # Execution resumes here when the PC wakes up
        Write-Log "Resumed from suspend."

        # Re-assert power request defensively. SetThreadExecutionState is per-thread
        # and should survive a Windows suspend transition, but re-asserting after
        # each resume costs nothing and protects against driver edge-cases that
        # might clear the flag on some hardware.
        Set-StayAwake

        # If no wake task was registered (normal stop, NoWake flag, or no rate
        # limits to wake from), the PC was suspended only because the user wants
        # it to sleep when the orchestrator finishes. They'll wake it manually;
        # we exit cleanly. Otherwise this is a rate-limit cycle: re-enter polling.
        if (-not $wakeRegistered) {
            break
        }
    }
} finally {
    Clear-StayAwake
}

} # end if (-not $env:PESTER_TESTING)
