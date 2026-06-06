---
task_id: TASK-PROC-041-01-09
type: impl
parent_requirement: REQ-PROC-041-01
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-04-30
effort: M
created: 2026-04-30
started: 2026-04-30
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-34, AC-35, AC-36, AC-37, AC-38]
  sections: []
target_package: ""
scope_description: "Consolidate orchestrator runtime signals into state.json properties; update PS1 sleep script to read state.json for stop/wake decisions"
release_description: "Orchestrator state is fully observable via state.json; Windows sleep script reacts immediately to rate-limit pauses."
opus_recommended: true   # reason: cross-cutting change (Python orchestrator + PowerShell script + tests); timezone handling and fallback logic require careful design; high impact on unattended operation
requirements_version:
  commit: 516e3cd3
  file: ../requirements.md
---

# Goal: Orchestrator State JSON Consolidation

## Objective

Expand `automation/state.json` to be the single source of truth for all orchestrator runtime state, replacing ad-hoc sentinel files for signalling. Update `scripts/sleep_when_autorun_done.ps1` to use the new state.json fields for immediate, accurate sleep/wake decisions.

## Requirements Summary

This task implements AC-34 through AC-38 of REQ-PROC-041-01 (Session Orchestrator).

For complete requirements at task creation time:
```
git show 516e3cd3:requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/feat_session_orchestrator/requirements.md
```

Current requirements: ../requirements.md

## Context

### Current state.json structure

```json
{
  "account_index": 0,
  "run_count": 86,
  "start_time": "2026-04-29T21:19:36.107854",   // UTC, no timezone info
  "paused_tasks": [],
  "rate_limited_until": { "gmail": "...", ... },  // UTC ISO strings
  "question_fingerprints": { ... }
}
```

### Current stop-detection (PS1 script)

The Windows script (`scripts/sleep_when_autorun_done.ps1`) currently detects orchestrator stop via:
1. Sentinel file `automation/.automated_mode` (absent = gracefully stopped)
2. Log activity on `automation/orchestrate.log` (stale = SIGKILL case)

It reads `state.json` only for `rate_limited_until` (to schedule PC wake-up) and only AFTER detecting a stop.

### Pain points

- The PS1 script must wait up to `LogStaleMinutes` (default 30 min) to detect SIGKILL-killed orchestrators
- External tools (e.g. the user, monitoring scripts) cannot easily tell whether the orchestrator is rate-limited/waiting vs. truly done without reading log files
- Timestamps in state.json are UTC with no timezone label, making them hard to correlate with local system logs
- `stopRequested` can only be detected by checking for a filesystem sentinel, not by reading state.json

## Scope

### In Scope

1. **`scripts/automation/orchestrate.py`** — add/update state.json fields:
   - `isRunning` (bool): `true` at startup, `false` in `finally`
   - `activeSession` (string | null): UUID of the running session; set before Popen, cleared after exit
   - `stopRequested` (bool): written `false` at startup; set `true` on SIGTERM or when a stop is needed — replaces the `.stop-requested` sentinel file
   - `rateLimitReached` (bool): `true` while sleeping for rate-limit reset
   - `nextWakeTime` (ISO string | null): planned resume time when `rateLimitReached` is `true`
   - `timezone` (string): IANA name of OS local timezone, written at startup and on every state save
   - All timestamps converted to OS local timezone (not UTC)
   - Remove all reads/writes of `automation/.stop-requested` sentinel file

2. **`scripts/sleep_when_autorun_done.ps1`** — updated detection logic:
   - Primary: read `state.json["isRunning"]`; if `false` → orchestrator stopped
   - Fallback: existing sentinel + log-mtime heuristic (when state.json unreadable)
   - Rate-limit aware: when `rateLimitReached` is `true`, sleep PC immediately and schedule wake from `nextWakeTime`

3. **`.claude/skills/claude-autorun.skill.md`** — `stop` action writes `stopRequested: true` to state.json; no longer creates `.stop-requested` file

4. **Tests** — new/updated tests covering all changed behaviours:
   - Python: in `scripts/automation/tests/test_orchestrate.py`
   - PowerShell: Pester tests or document skip rationale in protocol.md

### Out of Scope

- Parallel session execution or other orchestrator features
- Changing `.automated_mode` sentinel (still used for PID-based liveness in `claude-autorun status`)

### Design principle

`state.json` is the **single source of truth** for all runtime signals. No `.xyz` sidecar sentinel files for stop-request signalling. External tools (PS1 script, monitoring) read only state.json.

## Acceptance Criteria

- [ ] AC-34: state.json includes `isRunning`, `activeSession`, `stopRequested`, `rateLimitReached`, `nextWakeTime` fields maintained by orchestrate.py
- [ ] AC-35: All timestamps in state.json use OS local timezone; `timezone` field (IANA name) is written at startup and on every state save
- [ ] AC-36: sleep_when_autorun_done.ps1 uses `state.json["isRunning"]` as primary stop signal; falls back to sentinel+log-mtime when absent/unreadable
- [ ] AC-37: When `rateLimitReached` is `true`, PS1 script sleeps PC immediately and schedules wake from `nextWakeTime` (does not wait for `isRunning` to flip)
- [ ] AC-38: `claude-autorun stop` writes `stopRequested: true` to state.json; no `.stop-requested` sentinel file is created or read anywhere
- [ ] Tests for all Python changes pass (`python3 -m pytest scripts/automation/tests/`)
- [ ] PS1 logic is tested or test-skip rationale is documented in protocol.md

## Dependencies

No blocking task dependencies.

## Notes

- The orchestrator's `PersistentState` dataclass (see `orchestrate.py` around line 305) is where new fields should be added
- `save_state()` is called at every state-change point — timezone and isRunning fields should be set there
- The PS1 fallback must not regress the SIGKILL detection behaviour that existing users rely on
- Use `zoneinfo.ZoneInfo` (Python 3.9+) or `pytz` (already in use) for timezone name lookup
