---
task_id: TASK-PROC-032-24
type: impl
parent_requirement: REQ-PROC-032-03
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-31
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T19:35:17Z
after: [TASK-PROC-044-01-01, TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-16]
  sections: []
scope_description: "Before approval, ui-scribble-auto-review walks the scribble's screens in each participating flow's step order and verifies each step's intent is supported by a screen and its elements; a flow-flaw step is routed upstream via the revision channel; the auto-review brief carries one-line human walk instructions per participating flow."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
session_id: 9371354b-ec67-4a9c-9864-230ebc1ba7e2
session_account: web

---
# Goal: Per-flow walk validation before approval

## Objective

Before a scribble version is approved, `ui-scribble-auto-review` walks the scribble's screens in
each participating flow's step order and verifies that each step's intent is supported by a screen
and its elements. A step whose intent is unsupported because the flow itself is flawed (a missing
or contradictory step) is routed UPSTREAM through the revision channel rather than patched in the
scribble. The auto-review brief carries, per participating flow, one-line human walk instructions
(which file to open and which screens to view in which order) so a reviewer can repeat the walk. [AC-39]

This is a STANDALONE task (developer decision O3) — it does not fold into the review-doctrine task.

## Requirements Summary

Covers AC-39: pre-approval per-flow walk validation in `ui-scribble-auto-review`; flow-flaw steps
routed upstream via the revision channel; per-flow one-line human walk instructions in the brief.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `ui-scribble-auto-review` walks scribble screens in each participating flow's step order and
  verifies each step's intent is supported by a screen and its elements.
- Route a step unsupported due to a flow flaw upstream via the revision channel (create a
  revision-attached task per the `task-create` revision protocol) rather than patching the scribble.
- The auto-review brief carries, per participating flow, one-line human walk instructions
  (which file to open, which screens in which order).

### Out of Scope
- Per-flow navigation capture (AC-38), approval trail (AC-40), storage mirror (AC-37),
  discovery (AC-41) — sibling tasks.

## Acceptance Criteria

- [x] AC-39: `ui-scribble-auto-review` walks the scribble's screens in each participating flow's step order before approval and verifies each step's intent is supported; a flow-flaw step is routed upstream via the revision channel; the auto-review brief carries per-flow one-line human walk instructions.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| (orchestrator-wired) | — | `after: claude-modify-agent` to be added by the orchestrator (this task edits the `ui-scribble-auto-review` agent). |

## Notes

STANDALONE per developer decision O3. Edits the `ui-scribble-auto-review` AGENT, so the
orchestrator will add `after: claude-modify-agent`. Use `claude-modify-agent` /
`claude-modify-skill` as appropriate. Keep the edited agent/skill `contract.yaml` in sync
(REQ-PROC-044 mechanism). The revision channel was built under REQ-PROC-044 (044-06).
