---
task_id: TASK-PROC-032-25
type: impl
parent_requirement: REQ-PROC-032-03
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-05-31
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T23:11:49Z
after: [TASK-PROC-044-02-01, TASK-PROC-044-01-04, TASK-PROC-044-01-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-17]
  sections: []
scope_description: "On approval, ui-scribble-approve-handoff emits an APPROVAL_TRAIL.md aggregating the decision history across all versions (rejected alternatives, key trade-offs, rationale behind locked decisions), synthesized from per-version feedback.md, auto-review briefs, and inter-version diffs."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
session_id: 0527a287-6bb3-466a-be81-4cf25b232212
session_account: gmail2
---
# Goal: Approval trail aggregated across versions (APPROVAL_TRAIL.md)

## Objective

On approval, `ui-scribble-approve-handoff` emits an `APPROVAL_TRAIL.md` for the scribble that
aggregates the decision history across all versions — the alternatives that were rejected, the
key trade-offs, and the rationale behind the locked decisions — synthesized from the per-version
`feedback.md`, the auto-review briefs, and the inter-version diffs. The "why" behind the final
design survives beyond the version folders. [AC-40]

This is a STANDALONE task (developer decision O3).

## Requirements Summary

Covers AC-40: an approval-time `APPROVAL_TRAIL.md` aggregating cross-version decision history
(rejected alternatives, trade-offs, locked-decision rationale), synthesized from per-version
`feedback.md` + auto-review briefs + inter-version diffs; emitted by `ui-scribble-approve-handoff`.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `ui-scribble-approve-handoff` emits `APPROVAL_TRAIL.md` as an approval-time artifact.
- Aggregation logic synthesizing per-version `feedback.md`, auto-review briefs, and
  inter-version diffs into the decision history (rejected alternatives, key trade-offs,
  rationale behind locked decisions).

### Out of Scope
- Per-flow navigation (AC-38), walk validation (AC-39), storage mirror (AC-37),
  discovery (AC-41) — sibling tasks.

## Acceptance Criteria

- [x] AC-40: On approval, `ui-scribble-approve-handoff` emits an `APPROVAL_TRAIL.md` that aggregates the cross-version decision history (rejected alternatives, key trade-offs, rationale behind locked decisions), synthesized from the per-version `feedback.md`, the auto-review briefs, and the inter-version diffs.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| (orchestrator-wired) | — | If this edits the `ui-scribble-approve-handoff` agent, the orchestrator will add `after: claude-modify-agent`. |

## Notes

STANDALONE per developer decision O3. If `ui-scribble-approve-handoff` is implemented as an
agent, the orchestrator will add `after: claude-modify-agent`. Use `claude-modify-agent` /
`claude-modify-skill` as appropriate. Keep the edited agent/skill `contract.yaml` in sync
(REQ-PROC-044 mechanism).
