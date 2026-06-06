---
task_id: TASK-PROC-035-22
type: bugfix
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-BLOCKING
impact: 4
impact_reason: I4-QUALITY
status: completed
effort: XS
created: 2026-06-05
started: 2026-06-05
completed: 2026-06-05
session_completed_at: 2026-06-05T12:36:07Z
expected_tool_calls: 8
skill_chain_depth: 1
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Fix the D-0 latent bug: the orchestration chain routes task_type 'scribble' to a non-existent skill string 'ui-create-scribble' (create_orchestration_task.py L276). Map it to the real skill ui-scribble-iterate."
release_description: ""
opus_recommended: false   #
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: a57fca07
  file: ../requirements.md
session_id: 7ad77f7a-5257-4396-9e51-7cb8d6a97b17
session_account: web
---
# Goal: Fix the orchestration chain routing scribble tasks to a non-existent skill (D-0)

## Objective

`scripts/tasks/create_orchestration_task.py` L275–276 routes `task_type == "scribble"` to the skill string
`"ui-create-scribble"`, which **does not exist** (the real skill is `ui-scribble-iterate`; the only near-name,
`ui-create-scribble-improve`, is a different meta-tuning skill). So the orchestration chain would fail to run
any scribble task. Map the routing to `ui-scribble-iterate`. This is the prerequisite "T-C0" of the
scribble-gate redesign manifest — fix first, as nothing else in the chain can run a scribble task otherwise.

This is a **scripts** change → use `code-bugfix` (slim mode) and the `claude-write-script` skill (mandatory
for any `scripts/**` edit), which runs the Python quality gates.

## Bug Report

**Steps to reproduce:**
1. Have an orchestration plan entry with `task_type: scribble`.
2. Run the orchestration chain (`create_orchestration_task.py`).

**Expected behavior:**
The scribble task is materialised routed to the real scribble skill (`ui-scribble-iterate`).

**Actual behavior:**
It is routed to `skill = "ui-create-scribble"` (L276) — a skill that does not exist — so the scribble task
cannot be executed.

**Environment:** factory tooling (devcontainer).

**Logs:** grounded — `create_orchestration_task.py:275-276`:
```
275:        if task_type == "scribble":
276:            skill = "ui-create-scribble"
```

## Requirements Summary

REQ-PROC-035 (release preparation / orchestration chain). The routing table must name only registered skills —
this fix also motivates the registry routing-contract (authored in T-A1 / TASK-PROC-035-21) that prevents the
whole bug class.

Current requirements: ../requirements.md

## Scope

### In Scope
- Correct the `task_type: scribble` → skill mapping to `ui-scribble-iterate` in `create_orchestration_task.py`.

### Out of Scope
- The registry routing-contract check (that is T-A1 / a derived task). This is the point fix only.

## Acceptance Criteria

- [x] `create_orchestration_task.py` routes `task_type: scribble` to `ui-scribble-iterate`
- [x] Python quality gates pass (via `claude-write-script`)
- [x] No other `task_type` routing changed

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | None. Independent prerequisite; can be done immediately. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../../../../workflows/ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — D-0 in the redesign synthesis / manifest T-C0. |

## Notes

Grounded D-0 finding verified 2026-06-05 at `create_orchestration_task.py:276`.
