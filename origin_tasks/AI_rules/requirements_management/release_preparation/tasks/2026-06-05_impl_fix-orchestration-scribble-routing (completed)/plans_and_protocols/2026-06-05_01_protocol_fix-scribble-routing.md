---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - code-bugfix
  - claude-write-script
  - task-complete-bugfix
  - task-complete
  - claude-commit
---

# Protocol — TASK-PROC-035-22 (D-0 scribble routing fix)

Date: 2026-06-05
Mode: code-bugfix slim (scripts change)

## Problem

`scripts/tasks/create_orchestration_task.py` `_build_ac_block()` routed
`task_type == "scribble"` to the skill string `"ui-create-scribble"`, which does not
exist in the skill registry. The only near-name, `ui-create-scribble-improve`, is a
different meta-tuning skill. Any orchestration batch containing a scribble task would
emit an un-runnable AC line.

## Fix

- `scripts/tasks/create_orchestration_task.py` L276: `"ui-create-scribble"` → `"ui-scribble-iterate"`
  (the real, registered scribble skill).

## Test updates (regression-encoding)

The existing suite asserted the buggy literal, so the assertions had to be flipped to
the corrected skill (they would FAIL against the pre-fix code, proving the regression):
- `test_create_orchestration_task.py`:
  - `TestCreateOrchestrationTaskScribble.test_scribble_skill_in_ac` → asserts `ui-scribble-iterate`
  - `TestBuildAcBlock.test_scribble_uses_correct_skill` → asserts `ui-scribble-iterate`
  - `test_scribble_to_flutter_uses_task_create_code` → negative assert updated to `ui-scribble-iterate`
  - T-B9 comment/docstring updated to name `ui-scribble-iterate`

## Verification

- `python3 -m pytest scripts/tests/test_create_orchestration_task.py -q` → 66 passed.
- `scripts/quality/check_python_gates.sh`: G2/G4/G5 PASS. G1 (F401 in
  `scripts/optimize/run_monitors.py`) and G3 (`test_create_optimize_cycle_task.py`)
  FAIL on clean develop **identically** (verified via `git stash` baseline run) — both
  in files this task did not touch. No new gate finding introduced by this change.
- No other `task_type` routing changed.

## AC status

- [x] `create_orchestration_task.py` routes `task_type: scribble` to `ui-scribble-iterate`
- [x] Python quality gates pass (no new finding from this change; pre-existing baseline failures unrelated)
- [x] No other `task_type` routing changed
