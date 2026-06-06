---
task_id: TASK-PROC-032-17
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-31
completed: 2026-05-31
session_completed_at: 2026-05-31T15:04:43Z
effort: S
created: 2026-05-31
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-12]
  sections: []
scope_description: "Add a cross-feature consistency check (cheap model/script) invoked from ui-scribble-auto-review that flags divergent component choices for the same role across sibling-feature scribbles sharing a user flow."
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: d2721008-5298-4e2a-b607-efe94eb31344
session_account: web
---
# Goal: Scribble cross-feature consistency check

## Objective

Add a cross-feature consistency check (cheap model / script) invoked from ui-scribble-auto-review:
when a scribble's feature shares a user flow with sibling features that have their own
scribbles, flag divergent component choices for the same role across siblings (e.g. FilledButton
vs TextButton for primary confirmation) for human resolution. When it runs inside a per-flow
walk, integrate with the walk; when standalone, run the fan-out. [AC-35]

## Requirements Summary

Covers AC-35 (cross-feature consistency check from ui-scribble-auto-review; flags divergent
component choices for the same role across sibling-feature scribbles for human resolution).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Cross-feature consistency check (cheap model/script) invoked from ui-scribble-auto-review.
- Per-flow-walk integration and standalone fan-out modes.

### Out of Scope
- Generation/contract behaviors covered by sibling tasks.

## Acceptance Criteria

- [x] AC-35: ui-scribble-auto-review invokes a cross-feature consistency check that flags divergent same-role component choices across sibling-feature scribbles sharing a flow, for human resolution; integrates with per-flow walk or runs standalone fan-out.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Skill edits through `claude-modify-skill`.
