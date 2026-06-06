# Protocol — Phase 2b Implementation: sleep_when_autorun_done.ps1

**Task**: TASK-PROC-041-01-09
**Agent**: implementation-engineer (Claude Sonnet 4.6)
**Date**: 2026-04-30
**Phase**: 2b — PS1 changes

---

## Changes Made

### 1. Removed `$stopRequestPath` variable (plan Step 1)

Deleted the line:
```powershell
$stopRequestPath = Join-Path $automationDir ".stop-requested"
```
from the `# -- Paths` section (was line 120). The variable is no longer referenced anywhere in the file.

Also removed its use in the polling loop: the former `Test-Path -LiteralPath $stopRequestPath` stop-pending check is replaced by the `Get-OrchestratorState` call (see Step 4 below).

**Verification**: `grep -n "stop-requested\|stopRequestPath" scripts/sleep_when_autorun_done.ps1` returns 0 hits.

### 2. Updated `.DESCRIPTION` help-text (plan Step 6)

The `.DESCRIPTION` block now documents the new four-step detection strategy:
1. state.json `is_running` flag (PRIMARY)
2. state.json `rate_limit_reached` flag (early-exit, AC-37)
3. Sentinel + log-mtime fallback (legacy, AC-36)
4. Final log line for stop reason display

The `.PARAMETER LogStaleMinutes` doc was updated to note it applies to the fallback path only.

### 3. Added `Get-OrchestratorState` function (plan Step 2)

Inserted after `Get-RateLimitState` (~line 230 in original). The function:
- Returns `Available=$false` (not throws) when state.json is missing or invalid JSON — callers can fall back without try/catch.
- Uses an inner `_getProp` helper to avoid `StrictMode` property-not-found exceptions on PSCustomObjects.
- Parses `next_wake_time` with `RoundtripKind` + `.ToLocalTime()` (same pattern as `Get-RateLimitState`).
- Returns a hashtable with keys: `Available`, `IsRunning`, `StopRequested`, `RateLimitReached`, `NextWakeTime`, `ActiveSession`.
- WHY comment and Source reference added.

### 4. Updated `Test-OrchestratorActive` (plan Step 3)

Replaced the sentinel-only implementation with:
- PRIMARY: call `Get-OrchestratorState`; if `Available=true` and `IsRunning` is not null, return `[bool]$st.IsRunning`.
- FALLBACK: sentinel + `Test-LogActive` (original behaviour, for older orchestrators and SIGKILL).
- WHY comment with AC-36 reference added.

### 5. Updated polling loop (plan Step 4)

The `while (Test-OrchestratorActive)` loop now:
- Declares `$rateLimitBreak = $false` before the loop.
- Calls `Get-OrchestratorState` each iteration (stored in `$st`).
- Replaces the former `Test-Path -LiteralPath $stopRequestPath` check with `$st.Available -and $true -eq $st.StopRequested`.
- Adds rate-limit early-exit: when `$st.Available -and $true -eq $st.RateLimitReached`, logs the situation, sets `$rateLimitBreak = $true`, and breaks.
- WHY comment on `$rateLimitBreak` explains the distinction between normal stop and rate-limit break.
- The existing TZ-check block is preserved verbatim.

### 6. Updated wake-up scheduling (plan Step 5)

The wake-up section after the polling loop now:
- Re-reads `Get-OrchestratorState` for the final state values.
- When `$rateLimitBreak -and $st.Available -and $null -ne $st.NextWakeTime`: uses `$st.NextWakeTime.AddMinutes(-$WakeBeforeResetMinutes)` with `$wakeSource = "state.json next_wake_time"`.
- Otherwise: falls back to the original `Get-RateLimitState` path with `$wakeSource = "rate_limited_until earliest"`.
- Both paths converge into a single `if ($null -ne $wakeAt)` block that logs source, sleep minutes, and calls `Register-WakeTask`.
- The "earliest reset too close, skipping suspend" guard is retained (but unified for both paths).

### 7. Added `stop_reason` read from state.json (schema analysis recommendation)

In the "Done" section, the script now:
- Calls `Get-OrchestratorState` (stored as `$stFinal`).
- Attempts to read `stop_reason` directly from state.json JSON (the field is recommended by the Opus schema analysis but not yet part of `Get-OrchestratorState`'s typed return).
- Falls back to `Get-StopReason` (log-tail grep) when state.json doesn't have it.

---

## Deviations from Plan

| Plan Step | Deviation | Reason |
|-----------|-----------|--------|
| Step 5 wake-up | Merged the "stale entries" log loop into the `else` branch (only runs in the `rate_limited_until` path), keeping it out of the rate-limit-break path where it is not relevant. | Cleaner output — stale entries are irrelevant when waking from `next_wake_time`. |
| Step 6 `stop_reason` | Added `stop_reason` read from state.json even though the plan only mentions it in the schema analysis recommendation, not in the PS1 plan steps. | Low-risk addition, directly called out in `2026-04-30_02_opus_schema_analysis.md` as a recommendation; does not affect existing behaviour when the field is absent. |
| `Get-OrchestratorState` inner function `_getProp` | Defined as a nested function inside `Get-OrchestratorState` rather than a script-level helper. | Keeps it scoped to its single caller; avoids polluting the script's function namespace. |

---

## Syntax Check Result

`pwsh` is not installed in the Linux dev container (`pwsh: command not found`; `pwsh-preview` also absent). The syntax check could not be run automatically.

**Manual action required**: Run the following on the Windows host to verify parse-cleanliness:

```powershell
$errors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile(
    'C:\path\to\flutter_app\scripts\sleep_when_autorun_done.ps1',
    [ref]$null, [ref]$errors
)
if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }
Write-Host 'Parse OK'
```

The script was reviewed manually and follows the same PowerShell patterns used throughout the original file. No syntax issues are expected.

---

## Pester Tests

Created `scripts/sleep_when_autorun_done.Tests.ps1` — Pester v5 format.

**Note**: Pester tests require manual execution on the Windows host. They cannot run in this Linux dev container.

To run:
```powershell
Invoke-Pester scripts/sleep_when_autorun_done.Tests.ps1 -Output Detailed
```

Test coverage:
- `Get-OrchestratorState`: 6 tests covering missing file, `is_running=true/false`, `rate_limit_reached+next_wake_time`, invalid JSON, `stop_requested=true`.
- `Test-OrchestratorActive`: 4 tests covering state.json primary (true/false), sentinel fallback (absent/present+log-active).

---

## Files Modified

- `scripts/sleep_when_autorun_done.ps1` — ~497 → ~520 lines (net additions after removal of `$stopRequestPath`; new `Get-OrchestratorState` function + updated logic in polling loop and wake-up section)

## Files Created

- `scripts/sleep_when_autorun_done.Tests.ps1` — Pester v5 test file (manual Windows execution required)
