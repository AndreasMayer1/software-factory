---
task_id: TASK-PROC-032-05-05
type: impl
parent_requirement: REQ-PROC-032-05
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: pending
effort: M
created: 2026-06-06
skill_chain_depth: 2
after: [TASK-PROC-032-05-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04]
  sections: []
scope_description: "Implement loopback-as-task (L1-L6): stop inline loopbacks in requ-explore, create blocking scribble-refresh tasks for normative-upstream loopbacks, handle un-approved scribble as new task version."
release_description: "Turns scribble-consistency loopbacks into blocking tasks instead of inline requirement edits."
opus_recommended: false
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Implement Loopback-as-Task (T-C10)

## Objective

Implement the loopback-as-task model (L1–L6) so that normative-upstream loopbacks no longer happen inline:

1. **Stop inline loopbacks**: `requ-explore` must not silently edit requirements when a scribble loopback is needed.
2. **Create blocking tasks for normative-upstream loopbacks**: When a scribble loopback is detected (L1–L6 condition met), `requ-explore` creates a blocking scribble-refresh task instead of editing inline.
3. **Un-approved scribble → new task version**: If the scribble for the current task is not approved (e.g. revised scribble still in review), the current task is versioned as a new task instance rather than restarting in-place.

Skills: `claude-modify-skill` (ui-scribble-feedback-classify). Requires SCI machinery from T-C8 (TASK-PROC-032-05-01).

## Requirements Summary

Covers AC-04 (loopback-as-task L1–L6) of REQ-PROC-032-05.

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `ui-scribble-feedback-classify` loopback-as-task logic (L1–L6)
- Blocking scribble-refresh task creation on normative-upstream loopback detection
- Un-approved scribble versioning (new task instance vs. restart)

### Out of Scope
- SCI machinery itself (delivered by T-C8 / TASK-PROC-032-05-01)
- Cascade detection and width breaker (T-C11)
- Entry-context spine (T-C12)

## Acceptance Criteria

- [ ] `requ-explore` does not inline-edit when a normative-upstream loopback is detected
- [ ] A blocking scribble-refresh task is created for each L1–L6 loopback condition
- [ ] Un-approved scribble results in a new task version, not an in-place restart
- [ ] All existing tests pass; no quality gate regressions

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-05-01 | pending | SCI machinery must exist so loopback detection can read scribble staleness state |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-05-01](../2026-06-06_impl_derive-f05-sci-invariant-audit-and-rot-graph/goal.md) | Predecessor — executor should read SCI machinery deliverables before implementing loopback logic |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_impl_derive-f05-loopback-as-task/

Coverage auto-set from plan: [AC-04]

target_package omitted: process task, no release package.
