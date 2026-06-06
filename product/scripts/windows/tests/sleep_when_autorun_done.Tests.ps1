#Requires -Modules Pester
<#
.SYNOPSIS
    Pester v5 tests for sleep_when_autorun_done.ps1.

.NOTES
    Run on the Windows host only — Pester is not installed in the Linux dev container.

    Invoke:
        Invoke-Pester scripts/sleep_when_autorun_done.Tests.ps1 -Output Detailed

    The main block of sleep_when_autorun_done.ps1 is guarded by:
        if (-not $env:PESTER_TESTING) { ... }
    So dot-sourcing with PESTER_TESTING set is safe — only functions are loaded.
#>

BeforeAll {
    $env:PESTER_TESTING = "1"
    # Dot-source with a valid -ProjectPath so path variables resolve without error.
    # $PSScriptRoot is scripts/windows/tests/; the script under test is one level up;
    # flutter_app/ (project root) is three levels up (tests -> windows -> scripts -> flutter_app).
    $scriptDir = Split-Path $PSScriptRoot -Parent
    . "$scriptDir/sleep_when_autorun_done.ps1" -ProjectPath (Split-Path (Split-Path $scriptDir -Parent) -Parent)

    # Helper: write JSON to a temp file and return its path.
    # Must live in the same BeforeAll block as the dot-source so that both the
    # main script's functions and this helper share the same Pester setup scope.
    function New-TempStateJson {
        param([hashtable]$Fields)
        $path = Join-Path $TestDrive "state.json"
        $Fields | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $path -Encoding UTF8
        return $path
    }
}

AfterAll {
    Remove-Item Env:\PESTER_TESTING -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
Describe "Get-OrchestratorState" {

    It "returns Available=false when state.json is missing" {
        $path = Join-Path $TestDrive "nonexistent_state.json"
        $result = Get-OrchestratorState -Path $path
        $result.Available | Should -Be $false
        $result.IsRunning | Should -BeNullOrEmpty
    }

    It "returns IsRunning=true when state.json has is_running=true" {
        $path = New-TempStateJson @{ is_running = $true; stop_requested = $false }
        $result = Get-OrchestratorState -Path $path
        $result.Available | Should -Be $true
        $result.IsRunning | Should -Be $true
    }

    It "returns IsRunning=false when state.json has is_running=false" {
        $path = New-TempStateJson @{ is_running = $false; stop_requested = $false }
        $result = Get-OrchestratorState -Path $path
        $result.Available | Should -Be $true
        $result.IsRunning | Should -Be $false
    }

    It "returns RateLimitReached=true and a parsed NextWakeTime when present" {
        $wakeIso = "2026-04-30T22:00:00+02:00"
        $path = New-TempStateJson @{
            is_running        = $true
            rate_limit_reached = $true
            next_wake_time    = $wakeIso
        }
        $result = Get-OrchestratorState -Path $path
        $result.Available        | Should -Be $true
        $result.RateLimitReached | Should -Be $true
        $result.NextWakeTime     | Should -Not -BeNullOrEmpty
        # NextWakeTime is a [datetime] in local time — just verify it round-trips to a reasonable value
        $result.NextWakeTime.GetType().Name | Should -Be "DateTime"
    }

    It "returns Available=false without crashing when state.json is invalid JSON" {
        $path = Join-Path $TestDrive "bad_state.json"
        Set-Content -LiteralPath $path -Value "{ not valid json {{{"
        $result = Get-OrchestratorState -Path $path
        $result.Available | Should -Be $false
    }

    It "returns StopRequested=true when stop_requested is true in state.json" {
        $path = New-TempStateJson @{ is_running = $true; stop_requested = $true }
        $result = Get-OrchestratorState -Path $path
        $result.Available     | Should -Be $true
        $result.StopRequested | Should -Be $true
    }

    It "returns Available=true with null NextWakeTime when next_wake_time is not parseable" {
        $path = New-TempStateJson @{ is_running = $true; next_wake_time = "not-a-date" }
        $result = Get-OrchestratorState -Path $path
        $result.Available    | Should -Be $true
        $result.NextWakeTime | Should -BeNullOrEmpty
    }

    It "returns Timezone field from state.json" {
        $path = New-TempStateJson @{ is_running = $true; timezone = "Europe/Berlin" }
        $result = Get-OrchestratorState -Path $path
        $result.Available | Should -Be $true
        $result.Timezone  | Should -Be "Europe/Berlin"
    }

    It "returns null Timezone when field is absent" {
        $path = New-TempStateJson @{ is_running = $true }
        $result = Get-OrchestratorState -Path $path
        $result.Timezone | Should -BeNullOrEmpty
    }

    It "returns TimezoneOffset field from state.json" {
        $path = New-TempStateJson @{ is_running = $true; timezone_offset = "+02:00" }
        $result = Get-OrchestratorState -Path $path
        $result.Available      | Should -Be $true
        $result.TimezoneOffset | Should -Be "+02:00"
    }

    It "returns null TimezoneOffset when field is absent" {
        $path = New-TempStateJson @{ is_running = $true }
        $result = Get-OrchestratorState -Path $path
        $result.TimezoneOffset | Should -BeNullOrEmpty
    }
}

# ---------------------------------------------------------------------------
Describe "Test-ContainerTimezone" {
    BeforeAll {
        # Custom timezone objects with fixed offsets avoid depending on the test
        # machine's timezone database for anything other than "UTC" (always present).
        $script:tzUtc    = [System.TimeZoneInfo]::Utc
        $script:tzPlus2  = [System.TimeZoneInfo]::CreateCustomTimeZone(
            "Test+2", [timespan]::FromHours(2), "Test UTC+2", "Test UTC+2")
    }

    It "is silent when container and host UTC offsets match" {
        Mock Write-Log { }
        Test-ContainerTimezone -ContainerTzName "UTC" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 0 -Scope It
    }

    It "emits 3 Write-Log lines when container and host UTC offsets differ" {
        Mock Write-Log { }
        # Container is UTC, host override is UTC+2 — offsets differ
        Test-ContainerTimezone -ContainerTzName "UTC" -HostTzOverride $script:tzPlus2
        Should -Invoke Write-Log -Exactly 3 -Scope It
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*WARNING: Container timezone*differs*"
        }
    }

    It "emits one WARNING when container timezone name cannot be resolved" {
        Mock Write-Log { }
        Test-ContainerTimezone -ContainerTzName "Unknown/Fake_Timezone" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*Cannot resolve container timezone*"
        }
    }

    It "does nothing when ContainerTzName is empty" {
        Mock Write-Log { }
        Test-ContainerTimezone -ContainerTzName "" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 0 -Scope It
    }

    It "does nothing when both ContainerTzName and ContainerTzOffset are empty" {
        Mock Write-Log { }
        Test-ContainerTimezone -ContainerTzName "" -ContainerTzOffset "" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 0 -Scope It
    }

    It "is silent when offset matches host (offset path, no name resolution)" {
        Mock Write-Log { }
        # Host = UTC, container offset = +00:00 → match
        Test-ContainerTimezone -ContainerTzOffset "+00:00" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 0 -Scope It
    }

    It "warns when offset differs from host (offset path, no name resolution)" {
        Mock Write-Log { }
        # Host = UTC, container offset = +02:00 → mismatch
        Test-ContainerTimezone -ContainerTzOffset "+02:00" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 2 -Scope It
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*WARNING: Container timezone*differs*"
        }
    }

    It "parses negative offset correctly" {
        Mock Write-Log { }
        # Host = UTC+2, container offset = -05:00 → mismatch (7h apart)
        Test-ContainerTimezone -ContainerTzOffset "-05:00" -HostTzOverride $script:tzPlus2
        Should -Invoke Write-Log -Exactly 2 -Scope It
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*UTC-05:00*"
        }
    }

    It "prefers offset over name when both are supplied" {
        Mock Write-Log { }
        # Name 'Unknown/Fake' would fail resolution; offset must take precedence and succeed silently.
        Test-ContainerTimezone -ContainerTzName "Unknown/Fake_Timezone" -ContainerTzOffset "+00:00" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 0 -Scope It
    }

    It "includes the IANA name alongside the offset in mismatch warning" {
        Mock Write-Log { }
        Test-ContainerTimezone -ContainerTzName "Europe/Berlin" -ContainerTzOffset "+02:00" -HostTzOverride $script:tzUtc
        Should -Invoke Write-Log -Exactly 3 -Scope It
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*Europe/Berlin*+02:00*differs*"
        }
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*Fix: set TZ=Europe/Berlin*"
        }
    }

    It "warns about malformed offset then falls back to name resolution" {
        Mock Write-Log { }
        Test-ContainerTimezone -ContainerTzName "UTC" -ContainerTzOffset "not-an-offset" -HostTzOverride $script:tzUtc
        # 1 warning about the malformed offset; name resolution succeeds and offsets match → no further log
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*timezone_offset*not in*format*"
        }
    }

    It "skips silently when malformed offset is provided and no name is given" {
        Mock Write-Log { }
        Test-ContainerTimezone -ContainerTzOffset "garbage" -HostTzOverride $script:tzUtc
        # 1 warning about malformed offset, then nothing else (no name to fall back to)
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*timezone_offset*not in*format*"
        }
    }
}

# ---------------------------------------------------------------------------
Describe "Get-WakeTime" {
    BeforeAll {
        $script:baseTime = [datetime]::new(2026, 4, 30, 22, 0, 0)
    }

    It "uses next_wake_time when rateLimitBreak=true and NextWakeTime is set" {
        $state = @{ Available = $true; NextWakeTime = $script:baseTime }
        $rl    = @{ Active = @{}; Earliest = $null }
        $result = Get-WakeTime -RateLimitBreak $true -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -Be $script:baseTime.AddMinutes(-5)
        $result.Source | Should -BeLike "*next_wake_time*"
    }

    It "falls through to rate_limited_until when rateLimitBreak=true but NextWakeTime is null" {
        $earliest = $script:baseTime.AddHours(1)
        $state = @{ Available = $true; NextWakeTime = $null }
        $rl    = @{ Active = @{ acc = $earliest }; Earliest = $earliest }
        $result = Get-WakeTime -RateLimitBreak $true -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -Be $earliest.AddMinutes(-5)
        $result.Source | Should -BeLike "*rate_limited_until*"
    }

    It "does NOT wake on normal stop even when active rate_limited_until entries exist" {
        # Why: normal stop = orchestrator finished (max-tasks, manual stop, error).
        # Stale rate_limited_until entries from a previous session must not wake the PC.
        $earliest = $script:baseTime.AddHours(2)
        $state = @{ Available = $true; NextWakeTime = $null }
        $rl    = @{ Active = @{ acc = $earliest }; Earliest = $earliest }
        $result = Get-WakeTime -RateLimitBreak $false -State $state -RateLimitState $rl -WakeBeforeMinutes 10
        $result.WakeAt | Should -BeNullOrEmpty
        $result.Source | Should -BeLike "*not a rate-limit wait*"
    }

    It "returns null WakeAt on normal stop with no active limits" {
        $state = @{ Available = $true; NextWakeTime = $null }
        $rl    = @{ Active = @{}; Earliest = $null }
        $result = Get-WakeTime -RateLimitBreak $false -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -BeNullOrEmpty
        $result.Source | Should -BeLike "*not a rate-limit wait*"
    }

    It "ignores NextWakeTime entirely when rateLimitBreak=false (normal stop path)" {
        # Normal stop must not wake the PC, regardless of state.json fields.
        $state = @{ Available = $true; NextWakeTime = $script:baseTime }
        $rl    = @{ Active = @{}; Earliest = $null }
        $result = Get-WakeTime -RateLimitBreak $false -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -BeNullOrEmpty
    }

    It "returns null WakeAt when rateLimitBreak=true but neither NextWakeTime nor active limits exist" {
        $state = @{ Available = $true; NextWakeTime = $null }
        $rl    = @{ Active = @{}; Earliest = $null }
        $result = Get-WakeTime -RateLimitBreak $true -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -BeNullOrEmpty
        $result.Source | Should -BeLike "*no active*"
    }

    It "applies WakeBeforeMinutes offset correctly" {
        $state = @{ Available = $true; NextWakeTime = $script:baseTime }
        $rl    = @{ Active = @{}; Earliest = $null }
        $result = Get-WakeTime -RateLimitBreak $true -State $state -RateLimitState $rl -WakeBeforeMinutes 15
        $result.WakeAt | Should -Be $script:baseTime.AddMinutes(-15)
    }

    It "does NOT wake on normal stop when state.json is unavailable (SIGKILL/crash fallback)" {
        # Why: if the orchestrator was SIGKILLed before its finally ran, state.json may
        # be stale or unreadable. The polling loop then exits via the log-stale fallback
        # with $rateLimitBreak=false. The safe default is no wake.
        $state = @{ Available = $false; NextWakeTime = $null }
        $rl    = @{ Active = @{}; Earliest = $null }
        $result = Get-WakeTime -RateLimitBreak $false -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -BeNullOrEmpty
        $result.Source | Should -BeLike "*not a rate-limit wait*"
    }

    It "does NOT wake on normal stop when state.json is unavailable but stale rate_limited_until exists" {
        # Why: belt-and-braces — even if Get-RateLimitState somehow surfaced active entries
        # (e.g. read from a partially-written state.json), normal stop must not wake.
        $earliest = $script:baseTime.AddHours(3)
        $state = @{ Available = $false; NextWakeTime = $null }
        $rl    = @{ Active = @{ acc = $earliest }; Earliest = $earliest }
        $result = Get-WakeTime -RateLimitBreak $false -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -BeNullOrEmpty
        $result.Source | Should -BeLike "*not a rate-limit wait*"
    }

    It "does NOT wake on normal stop when RateLimitState is null (defensive)" {
        # Why: callers may pass $null for RateLimitState. With $RateLimitBreak=false we
        # must short-circuit before touching .Active / .Earliest (otherwise StrictMode
        # would throw a property-not-found error on $null).
        $state = @{ Available = $true; NextWakeTime = $null }
        $result = Get-WakeTime -RateLimitBreak $false -State $state -RateLimitState $null -WakeBeforeMinutes 5
        $result.WakeAt | Should -BeNullOrEmpty
        $result.Source | Should -BeLike "*not a rate-limit wait*"
    }

    It "uses next_wake_time even when active rate_limited_until entries also exist" {
        # Why: when both signals are present on a rate-limit break, next_wake_time wins
        # — it's the orchestrator's chosen resume time and may differ from the earliest
        # rate_limited_until (e.g. when the orchestrator adds a buffer).
        $nextWake = $script:baseTime.AddMinutes(45)
        $earliest = $script:baseTime.AddMinutes(30)
        $state = @{ Available = $true; NextWakeTime = $nextWake }
        $rl    = @{ Active = @{ acc = $earliest }; Earliest = $earliest }
        $result = Get-WakeTime -RateLimitBreak $true -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -Be $nextWake.AddMinutes(-5)
        $result.Source | Should -BeLike "*next_wake_time*"
    }

    It "uses next_wake_time when rate-limit break occurs but State.Available=false" {
        # Why: if state.json became unreadable between observation and wake calculation,
        # NextWakeTime is null but RateLimitBreak is already set. Fall through to
        # rate_limited_until if present, otherwise return no wake.
        $earliest = $script:baseTime.AddHours(1)
        $state = @{ Available = $false; NextWakeTime = $null }
        $rl    = @{ Active = @{ acc = $earliest }; Earliest = $earliest }
        $result = Get-WakeTime -RateLimitBreak $true -State $state -RateLimitState $rl -WakeBeforeMinutes 5
        $result.WakeAt | Should -Be $earliest.AddMinutes(-5)
        $result.Source | Should -BeLike "*rate_limited_until*"
    }
}

# ---------------------------------------------------------------------------
Describe "Test-WakeWorthSuspend" {
    BeforeAll {
        $script:now = [datetime]::new(2026, 6, 5, 15, 40, 0)
    }

    It "suspends when wake is comfortably beyond MinSleepMinutes" {
        $wakeAt = $script:now.AddMinutes(30)
        Test-WakeWorthSuspend -WakeAt $wakeAt -Now $script:now -MinSleepMinutes 2 | Should -BeTrue
    }

    It "suspends when wake is exactly MinSleepMinutes away (boundary is inclusive)" {
        $wakeAt = $script:now.AddMinutes(2)
        Test-WakeWorthSuspend -WakeAt $wakeAt -Now $script:now -MinSleepMinutes 2 | Should -BeTrue
    }

    It "does NOT suspend when wake is below MinSleepMinutes" {
        # Regression: field log showed wake registered ~1s out ('sleeping ~0 min'),
        # which the 15s suspend countdown then overshoots so the RTC alarm never fires.
        $wakeAt = $script:now.AddSeconds(1)
        Test-WakeWorthSuspend -WakeAt $wakeAt -Now $script:now -MinSleepMinutes 2 | Should -BeFalse
    }

    It "does NOT suspend when wake is already in the past" {
        $wakeAt = $script:now.AddMinutes(-3)
        Test-WakeWorthSuspend -WakeAt $wakeAt -Now $script:now -MinSleepMinutes 2 | Should -BeFalse
    }

    It "honours a custom MinSleepMinutes threshold" {
        $wakeAt = $script:now.AddMinutes(8)
        Test-WakeWorthSuspend -WakeAt $wakeAt -Now $script:now -MinSleepMinutes 10 | Should -BeFalse
        Test-WakeWorthSuspend -WakeAt $wakeAt -Now $script:now -MinSleepMinutes 5  | Should -BeTrue
    }

    It "always suspends when MinSleepMinutes is 0 and wake is in the future" {
        $wakeAt = $script:now.AddSeconds(30)
        Test-WakeWorthSuspend -WakeAt $wakeAt -Now $script:now -MinSleepMinutes 0 | Should -BeTrue
    }
}

# ---------------------------------------------------------------------------
Describe "Get-RateLimitState" {

    It "returns empty result when state.json is missing" {
        $path = Join-Path $TestDrive "nonexistent_rl.json"
        $result = Get-RateLimitState -Path $path
        $result.Earliest   | Should -BeNullOrEmpty
        $result.Active.Count | Should -Be 0
        $result.Stale.Count  | Should -Be 0
    }

    It "returns empty when rate_limited_until key is absent" {
        $path = New-TempStateJson @{ is_running = $true }
        $result = Get-RateLimitState -Path $path
        $result.Earliest     | Should -BeNullOrEmpty
        $result.Active.Count | Should -Be 0
        $result.Stale.Count  | Should -Be 0
    }

    It "returns active entry and Earliest when reset is in the future" {
        $future = (Get-Date).AddHours(2).ToUniversalTime().ToString("o")
        $path = New-TempStateJson @{ rate_limited_until = @{ account1 = $future } }
        $result = Get-RateLimitState -Path $path
        $result.Active.Count   | Should -Be 1
        $result.Stale.Count    | Should -Be 0
        $result.Earliest       | Should -Not -BeNullOrEmpty
        $result.Active.ContainsKey("account1") | Should -Be $true
    }

    It "classifies past resets as stale and sets Earliest to null" {
        $past = (Get-Date).AddHours(-1).ToUniversalTime().ToString("o")
        $path = New-TempStateJson @{ rate_limited_until = @{ account1 = $past } }
        $result = Get-RateLimitState -Path $path
        $result.Active.Count | Should -Be 0
        $result.Stale.Count  | Should -Be 1
        $result.Earliest     | Should -BeNullOrEmpty
        $result.Stale.ContainsKey("account1") | Should -Be $true
    }

    It "separates mixed active and stale entries correctly" {
        $past   = (Get-Date).AddHours(-1).ToUniversalTime().ToString("o")
        $future = (Get-Date).AddHours(3).ToUniversalTime().ToString("o")
        $path = New-TempStateJson @{ rate_limited_until = @{ stale_acc = $past; active_acc = $future } }
        $result = Get-RateLimitState -Path $path
        $result.Active.Count | Should -Be 1
        $result.Stale.Count  | Should -Be 1
        $result.Active.ContainsKey("active_acc") | Should -Be $true
        $result.Stale.ContainsKey("stale_acc")   | Should -Be $true
        $result.Earliest     | Should -Not -BeNullOrEmpty
    }

    It "Earliest reflects the earliest of multiple active entries" {
        $sooner = (Get-Date).AddHours(1).ToUniversalTime().ToString("o")
        $later  = (Get-Date).AddHours(4).ToUniversalTime().ToString("o")
        $path = New-TempStateJson @{ rate_limited_until = @{ acc_a = $sooner; acc_b = $later } }
        $result = Get-RateLimitState -Path $path
        $result.Active.Count | Should -Be 2
        # Earliest should be closer to sooner than later
        ($result.Earliest - (Get-Date).AddHours(1)).TotalSeconds | Should -BeLessThan 10
    }

    It "skips unparseable timestamp entries gracefully" {
        $path = New-TempStateJson @{ rate_limited_until = @{ bad_acc = "not-a-date" } }
        $result = Get-RateLimitState -Path $path
        $result.Active.Count | Should -Be 0
        $result.Stale.Count  | Should -Be 0
        $result.Earliest     | Should -BeNullOrEmpty
    }
}

# ---------------------------------------------------------------------------
Describe "Invoke-TimezoneCheck" {

    It "does not call Write-Log when container and host times are in sync" {
        # Fixed host time avoids any flakiness from real clock
        $hostNow = [datetime]::new(2026, 4, 30, 14, 0, 0)
        $logLine = "[orchestrator 14:00:05] task completed"   # ~5s diff, well under 30 min
        Mock Write-Log { }
        Invoke-TimezoneCheck -LogLine $logLine -HostNow $hostNow
        Should -Invoke Write-Log -Exactly 0 -Scope It
    }

    It "calls Write-Log with an ERROR message when container time differs by more than 30 minutes" {
        $hostNow = [datetime]::new(2026, 4, 30, 14, 0, 0)
        $logLine = "[orchestrator 12:00:00] task completed"   # 2h behind host
        Mock Write-Log { }
        Invoke-TimezoneCheck -LogLine $logLine -HostNow $hostNow
        # The function emits 5 Write-Log lines when a mismatch is detected
        Should -Invoke Write-Log -Exactly 5 -Scope It
        Should -Invoke Write-Log -Exactly 1 -Scope It -ParameterFilter {
            $Message -like "*ERROR: Container timezone*"
        }
    }

    It "does nothing when log line does not match the expected format" {
        $hostNow = [datetime]::new(2026, 4, 30, 14, 0, 0)
        $logLine = "some unstructured log line without timestamp"
        Mock Write-Log { }
        Invoke-TimezoneCheck -LogLine $logLine -HostNow $hostNow
        Should -Invoke Write-Log -Exactly 0 -Scope It
    }
}

# ---------------------------------------------------------------------------
Describe "Test-OrchestratorActive" {

    It "returns true when state.json is_running=true (no sentinel needed)" {
        $path = New-TempStateJson @{ is_running = $true }
        # Override $statePath via the -Path parameter by temporarily patching
        # Get-OrchestratorState. Because functions are defined in the script scope,
        # we mock them using Mock (Pester v5).
        Mock Get-OrchestratorState { return @{ Available = $true; IsRunning = $true } }

        $result = Test-OrchestratorActive
        $result | Should -Be $true
    }

    It "returns false when state.json is_running=false" {
        Mock Get-OrchestratorState { return @{ Available = $true; IsRunning = $false } }

        $result = Test-OrchestratorActive
        $result | Should -Be $false
    }

    It "falls back to false when state.json missing and sentinel absent" {
        # state.json unavailable -> Available=false, IsRunning=$null
        Mock Get-OrchestratorState { return @{ Available = $false; IsRunning = $null } }
        # Sentinel absent
        Mock Test-SentinelPresent { return $false }

        $result = Test-OrchestratorActive
        $result | Should -Be $false
    }

    It "falls back to sentinel+log when state.json missing (legacy orchestrator)" {
        Mock Get-OrchestratorState { return @{ Available = $false; IsRunning = $null } }
        Mock Test-SentinelPresent { return $true }
        Mock Test-LogActive { return $true }

        $result = Test-OrchestratorActive
        $result | Should -Be $true
    }

    It "returns true when is_running=true even when stop_requested=true (stop does not end poll)" {
        Mock Get-OrchestratorState { return @{ Available = $true; IsRunning = $true; StopRequested = $true } }

        $result = Test-OrchestratorActive
        $result | Should -Be $true
    }
}

# ---------------------------------------------------------------------------
# Write-Log resilience — regression for the Mutagen log-lock crash.
#
# The watcher's log can live inside the Mutagen-synced NTFS mirror, where a
# periodic scan briefly opens the file and the script's Add-Content append
# throws "stream not readable" (GetContentWriterArgumentError). Before the fix,
# the script-level $ErrorActionPreference = "Stop" turned that into a fatal
# crash, so the host was never suspended. These tests pin the contract: a
# log-write failure must NEVER propagate out of Write-Log.
# ---------------------------------------------------------------------------

Describe "Write-Log resilience" {
    BeforeEach {
        Mock Start-Sleep { }   # don't actually wait between retries
        Mock Write-Host  { }   # suppress console output during the test run
    }

    It "does not throw when Add-Content keeps failing" {
        $LogFile = Join-Path $TestDrive "watcher.log"
        Mock Add-Content { throw "Der Datenstrom war nicht lesbar." }

        { Write-Log "poll line" } | Should -Not -Throw
    }

    It "retries the append up to 5 times before degrading to console-only" {
        $LogFile = Join-Path $TestDrive "watcher.log"
        Mock Add-Content { throw "locked" }

        Write-Log "poll line"
        Should -Invoke Add-Content -Exactly 5 -Scope It
    }

    It "stops retrying as soon as the append succeeds" {
        $LogFile = Join-Path $TestDrive "watcher.log"
        $script:addContentCalls = 0
        Mock Add-Content {
            $script:addContentCalls++
            if ($script:addContentCalls -lt 3) { throw "transient lock" }
        }

        Write-Log "poll line"
        Should -Invoke Add-Content -Exactly 3 -Scope It
    }

    It "skips the file write entirely when no LogFile is configured" {
        $LogFile = ""
        Mock Add-Content { }

        Write-Log "poll line"
        Should -Invoke Add-Content -Exactly 0 -Scope It
    }
}
