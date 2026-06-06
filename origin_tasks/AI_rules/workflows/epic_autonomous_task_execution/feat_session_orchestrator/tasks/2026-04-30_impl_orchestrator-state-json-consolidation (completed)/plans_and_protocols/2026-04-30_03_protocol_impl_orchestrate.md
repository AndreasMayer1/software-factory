# Protocol — Phase 2a Implementation: orchestrate.py + tests

**Date**: 2026-04-30
**Agent**: implementation-engineer (Claude Sonnet 4.6)
**Task**: TASK-PROC-041-01-09, Phase 2a

---

## Summary

Implemented all changes to `scripts/automation/orchestrate.py` and
`scripts/automation/tests/test_orchestrate.py` per the Opus plan
(`2026-04-30_01_plan_state-json-consolidation.md`) and schema analysis
(`2026-04-30_02_opus_schema_analysis.md`).

---

## Changes Made

### orchestrate.py

1. **Module docstring updated** — removed reference to `.stop-requested` sentinel.

2. **`SENTINEL_STOP` constant removed** (was line 54) — replaced with a comment
   explaining AC-38. No code references remain; verified with grep.

3. **`_get_local_timezone_name()` helper added** (after `rate_limit_sleep`, before
   `strip_hook_footer`) — returns IANA timezone name with fallback chain:
   `zoneinfo.key` → `$TZ` env var → `time.tzname` → `"UTC"`.

4. **`PersistentState` dataclass updated** — 7 new fields added:
   `is_running`, `active_session`, `stop_requested`, `rate_limit_reached`,
   `next_wake_time`, `timezone`, `stop_reason`.
   `stop_reason` was recommended by the schema analysis (Opus) beyond the original plan —
   included as justified (one line in finally, `run_data.stop_reason` already tracked).

5. **`load_state()` updated** — all 7 new fields loaded with `.get()` and defaults.

6. **`save_state()` updated** — refreshes `state.timezone = _get_local_timezone_name()`
   on every call before serialising. WHY comment added.

7. **`get_now_local` default changed** — from `datetime.now` (naive) to
   `lambda: datetime.now().astimezone()` (aware local datetime with offset).
   Fixes latent bug where PS1 `RoundtripKind` parser mis-treated naive times as UTC.

8. **`_read_external_stop_request()` method added** on `Orchestrator` — re-reads
   `state.json["stop_requested"]` from disk on each poll iteration. Safe on disk
   error (returns False).

9. **`check_stop_conditions()` updated** — sentinel file check replaced with
   `self._read_external_stop_request()`. Both stop paths (stop_flag and external)
   now mirror `state.stop_requested = True` to in-memory state.

10. **`rate_limit_sleep` call sites wrapped** — both call sites (resume path in
    `process_in_progress_resume`, normal path in `wait_for_account_if_needed`) now
    set `state.rate_limit_reached = True` + `state.next_wake_time` before sleeping,
    then clear after. `save_state` called around each.

11. **`active_session` set/cleared around all 3 session launch call sites**:
    - `process_answered_feedback`: fresh-session and resume branches
    - `process_in_progress_resume`: resume branch
    - `run_normal_session_step`: normal session

12. **Startup initialization** (in `main()`) — before first `save_state`:
    `is_running=True`, `active_session=None`, `stop_requested=False`,
    `stop_reason=None`, `rate_limit_reached=False`, `next_wake_time=None`.

13. **`finally` block updated** — `unlink_if_exists(SENTINEL_STOP)` removed.
    Added: `is_running=False`, `active_session=None`, `rate_limit_reached=False`,
    `next_wake_time=None`, `state.stop_reason = run_data.stop_reason`, then `save_state`.

### test_orchestrate.py

14. **`TestLoadState.test_missing_file_returns_default`** — extended with assertions
    for all 7 new fields.

15. **`TestLoadState.test_observability_fields_loaded_from_json`** — new test verifying
    all observability fields are loaded correctly from JSON.

16. **`TestSaveState.test_writes_observability_fields`** — new test verifying fields
    are serialised to JSON.

17. **`TestSaveState.test_save_state_writes_timezone_field`** — new test using
    `monkeypatch` to verify `_get_local_timezone_name` is called and result written.

18. **`TestCheckStopConditions.test_stop_file_exists_returns_manual`** — renamed and
    updated to `test_stop_requested_in_state_json_returns_manual` (old test exercised
    the removed sentinel, now tests the new state.json approach).

19. **New `TestExternalStopRequest` class** (5 tests):
    - stop via state.json sets reason and mirrors state
    - SENTINEL_STOP absent from module
    - stop_flag also mirrors to state
    - no stop when state.json missing
    - no stop when stop_requested=false

20. **New `TestTimezoneField` class** (2 tests):
    - `_get_local_timezone_name` returns non-empty string
    - fallback behavior with TZ env var

21. **New `TestActiveSessionLifecycle` class** (1 test):
    - `active_session` set before run_normal_session, cleared after (spy on save_state)

22. **New `TestRateLimitObservability` class** (1 test):
    - `rate_limit_reached=True` saved before rate_limit_sleep, False after

---

## Deviations from Plan

- **`stop_reason` field added** — schema analysis (Opus) recommended this beyond
  the original plan. Included as cost is one line in finally and value is clear
  (developer can read last stop reason from state.json without log grep).

- **`test_stop_file_exists_returns_manual` renamed** — existing test tested the
  removed sentinel. Updated to test the new state.json-based stop mechanism.
  The plan did not explicitly mention this existing test needed updating.

---

## Test Results

```
194 passed in 6.21s
```

Zero failures, zero errors. All new test classes have real implementations (no `...`
placeholders). Coverage includes all 6 observability behaviors (AC-34..AC-38) plus
`stop_reason`.

---

## Verification

```
grep -n "SENTINEL_STOP\|\.stop-requested" scripts/automation/orchestrate.py
```
Returns only comment lines (lines 54 and 2543) — no executable code references.
