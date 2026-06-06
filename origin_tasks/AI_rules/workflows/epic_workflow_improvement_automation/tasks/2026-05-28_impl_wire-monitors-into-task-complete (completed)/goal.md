---
task_id: TASK-PROC-006-11
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-05-28
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-28T09:10:17Z
after: [TASK-PROC-006-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02]
  sections: []
scope_description: "Append run_monitors.py invocation to the tail of the task-complete skill / completion path so monitors execute after every successful task completion. Best-effort: monitor failure must not abort task-complete."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-F
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: 13c9f023-be5c-4488-8550-0463a2000ad4
session_account: gmail2
---
# Goal: Wire `run_monitors.py` into `task-complete` (IMPL-F)

## Objective

Trigger the monitor sweep at the canonical end-of-task moment. Without this,
the monitor scripts from IMPL-C never run in production. The wiring is a small,
specific edit to the task-complete skill or its terminating script.

## Requirements Summary

Reference: REQ-PROC-006 AC-02 ("monitor scripts execute after every
task-complete invocation"), §"Monitor-Based Detection" (commit eabdeaf0).

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Append a single `scripts/optimize/run_monitors.py` invocation to the tail of `task-complete` (skill or completion script) so it runs after a successful task close-out.
- Failure mode: capture run_monitors.py exit code and stderr, log, continue. A monitor crash must not abort task-complete or fail the commit.
- Do not invoke monitors on dry-runs, on back-out paths, or during `task-complete --force` (the latter is debatable — choose: skip monitors on --force to avoid feeding events from incomplete tasks; document the choice in the wiring location).
- Update the task-complete skill body documentation to name the wiring step.

### Out of Scope

- The monitor scripts themselves (IMPL-C / TASK-PROC-006-08).
- The producer skill that consumes events (IMPL-E / TASK-PROC-006-10).
- A pre-task-complete hook variant.

## Acceptance Criteria

- [x] `run_monitors.py` is invoked exactly once at the tail of every successful task-complete (covered by a smoke test running task-complete on a fixture task).
- [x] A simulated monitor crash (e.g. mocking exit code 1) does NOT abort task-complete and does NOT fail the commit.
- [x] task-complete documentation (skill.md or completion script docstring) names the wiring step.
- [x] No regression: an existing successful task-complete run still completes and commits as before.

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-08 (IMPL-C) | pending | Needs run_monitors.py to invoke |

## Notes

Concept docs: round-4 §6 IMPL-F. Best-effort failure handling is consistent
with the requirement principle: "Monitors are idempotent" — re-runs are safe,
so dropping one tick is acceptable.
