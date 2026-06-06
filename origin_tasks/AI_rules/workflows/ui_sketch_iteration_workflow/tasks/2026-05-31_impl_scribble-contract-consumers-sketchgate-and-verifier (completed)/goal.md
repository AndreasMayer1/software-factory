---
task_id: TASK-PROC-032-18
type: impl
parent_requirement: REQ-PROC-032-03
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T09:20:14Z
effort: M
created: 2026-05-31
after: [TASK-PROC-032-11]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08, AC-09]
  sections: []
scope_description: "Make downstream consumers honor the scribble contract: rewrite the Sketch Gate in code-simple/code-complex and anchor ui-verify-flutter's finding taxonomy to the contract."
release_description: ""
opus_recommended: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: 62ee8f20-baa8-4fdb-b1b8-cd48ac31b845
session_account: gmail2
---
# Goal: Scribble contract consumers — Sketch Gate and verifier

## Objective

Make the downstream consumers honor the contract that task 1 establishes.

- code-simple + code-complex (claude-modify-skill): rewrite the Sketch Gate step so the
  implementer reads flutter_handoff.yaml's `contract:` block, implements locked-in items as
  shown, and re-derives the re_derive items from doc/presentation/ + tokens.json regardless
  of whether the scribble depicts them. [AC-24]
- ui-verify-flutter (claude-modify-skill): anchor the finding taxonomy to the contract —
  a locked-in divergence is a coder defect; a re-derive item is classified out_of_contract
  (not opined on against the scribble). Every finding states which side of the contract it
  is on. [AC-25]

Depends on task 1 because the contract doctrine + handoff `contract:` block must exist first.

## Requirements Summary

Covers AC-24 (Sketch Gate honors the contract block) and AC-25 (ui-verify-flutter finding
taxonomy anchored to the contract).

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- code-simple + code-complex Sketch Gate rewrite (read contract block; implement locked-in; re-derive re_derive items).
- ui-verify-flutter finding-taxonomy anchoring to the contract.

### Out of Scope
- The contract doctrine + producer emission (TASK-PROC-032-11) — prerequisite, not part of this task.

## Acceptance Criteria

- [x] AC-24: Sketch Gate (code-simple/code-complex) reads the contract block, implements locked-in items as shown, re-derives re_derive items from doc/presentation + tokens regardless of scribble depiction.
- [x] AC-25: ui-verify-flutter finding taxonomy anchored to the contract — locked-in divergence = coder defect; re-derive item = out_of_contract; every finding states its contract side.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-11 | pending | Contract doctrine + handoff `contract:` block must exist first |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-11](../2026-05-31_impl_scribble-contract-doctrine-and-producer-surfacing/goal.md) | Predecessor — establishes the contract doctrine + handoff `contract:` block this task consumes |

## Notes

Skill edits through `claude-modify-skill`.
