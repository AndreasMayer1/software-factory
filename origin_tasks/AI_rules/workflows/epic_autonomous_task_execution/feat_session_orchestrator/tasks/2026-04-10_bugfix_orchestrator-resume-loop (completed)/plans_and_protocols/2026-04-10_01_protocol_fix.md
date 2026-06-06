# Protocol: TASK-PROC-041-01-06

**Date**: 2026-04-10  
**Status**: Fixed, tests passing

---

## Root Cause Analysis

### Bug 1 — Infinite loop (AC-21)

**Location**: `process_answered_feedback()` in `orchestrate.py` (~line 1142)

**Root cause**: `find_answered_feedback()` does not accept `exhausted_resume_ids` as a parameter. After 3 failed resume attempts, the session_id is added to `exhausted_resume_ids`, but the next loop iteration calls `find_answered_feedback()` again with no filter — returning the same exhausted item. The `attempt > 3` branch fires again immediately, prints the warning, and returns "continue" → infinite loop.

**Fix**: Filter the result of `find_answered_feedback` by `exhausted_resume_ids` before picking the first item:
```python
answered = [
    a for a in find_answered_feedback(FEEDBACK_DIR, self.deps)
    if a["session_id"] not in run_data.exhausted_resume_ids
]
```
When all answered items are exhausted, this returns an empty list → "next" → loop proceeds to next step (or stops if nothing else to do).

### Bug 2 — Git commit failure (AC-23)

**Location**: `git_commit_best_effort()` (~line 388)

**Root cause**: After `git add`, the code ran `git commit` unconditionally. If the files were already tracked and unchanged (already committed in a prior run), `git add` is a no-op but `git commit` exits 1 with "nothing to commit" → `CalledProcessError` → WARNING logged.

**Fix**: Check staged diff before committing:
```python
staged = deps.run_subprocess(["git", "diff", "--cached", "--quiet"], check=False, ...)
if staged.returncode == 0:
    return  # nothing staged, skip commit silently
```
`git diff --cached --quiet` exits 0 = no staged changes, exits 1 = staged changes exist.

---

## Changes Made

| File | Change |
|------|--------|
| `scripts/automation/orchestrate.py` | Filter exhausted sessions in `process_answered_feedback` |
| `scripts/automation/orchestrate.py` | Add staged-changes check in `git_commit_best_effort` |
| `scripts/automation/tests/test_orchestrate.py` | Update 2 tests + add `test_no_commit_when_nothing_staged` |

## Test Results

157/157 tests passing after fix.
