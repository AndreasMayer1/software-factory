<#
.SYNOPSIS
    Shortcut-friendly wrapper for sleep_when_autorun_done.ps1.

.DESCRIPTION
    Invoked from a Windows desktop shortcut. Performs three steps:

      1. Disables QuickEdit and MouseInput on the current console via Win32
         SetConsoleMode. Without this, any click in the console buffer enters
         Mark/Select mode and freezes the script until Enter/Esc is pressed.
         That stall blocks the polling loop in sleep_when_autorun_done.ps1,
         which means the host is never suspended when the orchestrator stops.

      2. Truncates automation\win_sleep_script.log. The main script uses
         Add-Content for every poll line, so without truncation the file
         would grow unbounded across runs.

      3. Forwards execution to sleep_when_autorun_done.ps1 with -LogFile
         pointing to that log.

    No parameters - keeps the shortcut Target field short. The project root
    is resolved relative to this script's own location ($PSScriptRoot ->
    ..\.. = flutter_app root).

    Assumes the shortcut is configured to run as Administrator. The main
    script throws a clear error if elevation is missing.

.EXAMPLE
    # Shortcut Target:
    # powershell.exe -ExecutionPolicy Bypass -File "C:\...\scripts\windows\win_sleep_script_wrapper.ps1"
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Paths ---------------------------------------------------------------------

. "$PSScriptRoot\find_project_root.ps1"
$projectRoot = Find-ProjectRoot
$logFile     = Join-Path $projectRoot "automation\win_sleep_script.log"
$mainScript  = Join-Path $PSScriptRoot "sleep_when_autorun_done.ps1"

if (-not (Test-Path -LiteralPath $mainScript)) {
    throw "Main script not found: $mainScript"
}

# -- Step 1: Disable QuickEdit + MouseInput on the current console -------------
# Why: SetConsoleMode requires ENABLE_EXTENDED_FLAGS to be set in the same call
# when modifying the QuickEdit / Insert bits, otherwise the change is ignored
# (documented MSDN behaviour). We OR in the extended flag, then mask out
# QuickEdit and MouseInput so clicks can no longer pause the script.

$signature = @'
[DllImport("kernel32.dll", SetLastError=true)]
public static extern IntPtr GetStdHandle(int nStdHandle);
[DllImport("kernel32.dll", SetLastError=true)]
public static extern bool GetConsoleMode(IntPtr hConsoleHandle, out uint lpMode);
[DllImport("kernel32.dll", SetLastError=true)]
public static extern bool SetConsoleMode(IntPtr hConsoleHandle, uint dwMode);
'@

$consoleApi = Add-Type -MemberDefinition $signature `
                       -Name      "ConsoleApi" `
                       -Namespace "WinSleepWrapper" `
                       -PassThru

$STD_INPUT_HANDLE       = -10
$ENABLE_MOUSE_INPUT     = 0x0010
$ENABLE_QUICK_EDIT_MODE = 0x0040
$ENABLE_EXTENDED_FLAGS  = 0x0080

$stdin = $consoleApi::GetStdHandle($STD_INPUT_HANDLE)
$mode  = 0
if ($consoleApi::GetConsoleMode($stdin, [ref]$mode)) {
    $newMode = ($mode -bor $ENABLE_EXTENDED_FLAGS) `
               -band (-bnot $ENABLE_QUICK_EDIT_MODE) `
               -band (-bnot $ENABLE_MOUSE_INPUT)
    [void]$consoleApi::SetConsoleMode($stdin, $newMode)
}

# -- Step 2: Truncate the log --------------------------------------------------

$logDir = Split-Path $logFile -Parent
if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
Set-Content -LiteralPath $logFile -Value "" -Encoding UTF8

# -- Step 3: Forward to the main script ---------------------------------------

& $mainScript -LogFile $logFile
