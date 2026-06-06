# Protocol: Hung Session Detection Implementation

**Date**: 2026-04-24
**Task**: TASK-PROC-041-01-08
**Status**: COMPLETE

## Summary

Implemented hung-session detection and recovery in `scripts/automation/orchestrate.py`
and added 4 new tests in `scripts/automation/tests/test_orchestrate.py`.

## Changes Made

### `scripts/automation/orchestrate.py`

1. **`OrchestratorDeps`** (line ~789): Added `popen_subprocess: Callable` and `get_mtime: Callable` fields.

2. **New constant `JSONL_BASE`**: Added before `run_session_with_hung_detection`.

3. **New function `run_session_with_hung_detection()`**: Inserted after `run_fresh_session_with_answer`.
   - Uses `deps.popen_subprocess` (non-blocking) instead of `deps.run_subprocess`
   - Polls every `hung_check_interval` seconds
   - Kill conditions: stop_requested, session_timeout, hung (stale JSONL + no children)
   - Returns `CompletedProcess` with custom `.kill_reason` and `.elapsed_secs` attributes
   - Child process check via `ps --ppid` — key safety mechanism from 13-hour incident

4. **Refactored `run_normal_session`, `run_resume_session`, `run_fresh_session_with_answer`**:
   - Each builds a `cmd` list locally and delegates to `run_session_with_hung_detection`
   - New parameters: `hung_check_interval`, `hung_timeout_secs`, `session_timeout_secs`, `stop_flag`

5. **`run_normal_session_step`**: Added `stop_flag` parameter; passes new args to `run_normal_session`; checks `kill_reason` and records `hung_killed`, `kill_reason`, `elapsed_secs` in session record.

6. **`process_answered_feedback`**: Updated `run_fresh_session_with_answer` and `run_resume_session` calls to pass new params; added hung-kill logging.

7. **`process_in_progress_resume`**: Updated `run_resume_session` call; added hung-kill logging and session record fields.

8. **`write_report()`**: Added "### Hung / Timed-Out Sessions" section after Pending Feedback.

9. **`parse_args()`**: Added `--hung-check-interval` (default 60 s), `--hung-timeout` (default 30 min), `--session-timeout` (default 14400 s = 4 h).

10. **`main()`**: Added `popen_subprocess=subprocess.Popen` and `get_mtime=os.path.getmtime` to deps wiring.

11. **`run_loop()`**: Updated call to `run_normal_session_step` to pass `stop_flag`.

### `scripts/automation/tests/test_orchestrate.py`

1. Added `run_session_with_hung_detection` to imports.
2. Added `_make_immediately_exiting_proc()` helper.
3. Added `make_popen_from_subprocess_fn()` bridge helper.
4. Updated `make_deps()`: added `popen_subprocess` (default: immediately-exiting mock proc) and `get_mtime` defaults.
5. Updated `make_args()`: added `hung_check_interval=60`, `hung_timeout=30`, `session_timeout=14400`.
6. Updated `TestRunLoopIntegration._make_loop_deps()`: wires `popen_subprocess` from same `subprocess_fn`.
7. Updated `TestRunNormalSessionStep` tests: added `popen_subprocess` and `stop_flag` argument.
8. Updated `TestProcessInProgressResumeFullPath` tests: added `popen_subprocess`.
9. Updated 3 standalone `make_deps(...)` calls in loop integration tests: added `popen_subprocess`.
10. Added `TestRunSessionWithHungDetection` class with 4 tests:
    - `test_hung_detection_no_children_stale_jsonl`
    - `test_hung_detection_children_present_not_hung`
    - `test_session_timeout`
    - `test_kill_sequence_sigterm_then_sigkill`

## Test Results

- 179 passed, 1 pre-existing unrelated failure
  (`TestFindAnsweredFeedback::test_empty_answer_skipped` — was failing before this task)
- All 4 new tests pass

## Key Design Decisions

- `get_mtime` added to `OrchestratorDeps` (not called directly as `os.path.getmtime`)
  for testability — consistent with the existing DI pattern
- `popen_subprocess` default in tests returns immediately-exiting mock so existing tests
  need minimal changes
- `make_popen_from_subprocess_fn()` bridges old fake_subprocess style to new popen API
  so integration tests that test rate-limit/perm-error behavior still work unchanged
- Goal.md is NOT modified on hung kill — AC-15 resume logic handles recovery naturally
