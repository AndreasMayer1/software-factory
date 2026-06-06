---
task_id: TASK-PROC-032-05-07
type: impl
parent_requirement: REQ-PROC-032-05
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: pending
effort: L
created: 2026-06-06
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold entry-surface type, entry-point multiplicity, back/close destination, container dimension, resolvable 3-tier entry reference, and bounded reconciliation logic across generator + reviewer agents in one coherent design."
after: [TASK-PROC-032-05-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Implement entry-context spine (PROP-8): generator emits entry-surface type, entry-point multiplicity, back/close destination, container dimension + rationale, and 3-tier entry reference; reviewers assert presence/consistency/size-appropriateness; bounded reconciliation against router/screenshot for already-built openers (greenfield skips)."
release_description: "Embeds entry-context metadata in scribble generator and reviewers for launch-path consistency."
opus_recommended: true  # reason: cross-cutting invariant — entry-context spine spans generator + reviewer agent edits + skill edits with interdependent assertion logic
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Implement Entry-Context Spine (T-C12)

## Objective

Implement the entry-context spine (PROP-8) so that every generated scribble carries complete entry-context metadata and reviewers assert its correctness:

1. **Generator emits entry-context**: `ui-scribble-generator` emits:
   - Entry-surface type (e.g. bottom-sheet, full-screen, dialog)
   - Entry-point multiplicity (how many callers open this surface)
   - Back/close destination
   - Container dimension + rationale
   - Resolvable 3-tier entry reference (unique identifier linking to the app-shell launch map)

2. **Reviewers assert entry-context**: `ui-scribble-auto-review` (and relevant reviewer agents) assert:
   - Presence: all fields are present
   - Consistency: fields are internally consistent (e.g. dimension matches surface type)
   - Size-appropriateness: container dimension is appropriate for the content

3. **Bounded reconciliation**: For already-built openers (existing router + screenshot available), reviewers reconcile entry-context against the router/screenshot. Greenfield surfaces skip reconciliation.

Skills/agents: `claude-modify-agent` (ui-scribble-generator + reviewer agents) + `claude-modify-skill` (ui-scribble-auto-review). Requires SCI machinery from T-C8 (TASK-PROC-032-05-01).

## Requirements Summary

Covers AC-08 (entry-context spine PROP-8) of REQ-PROC-032-05.

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `ui-scribble-generator` entry-context emission (5 fields: surface type, multiplicity, back/close destination, container dimension + rationale, 3-tier entry reference)
- `ui-scribble-auto-review` and reviewer agents: presence/consistency/size-appropriateness assertions
- Bounded reconciliation against router/screenshot for already-built openers
- Greenfield surfaces: skip reconciliation

### Out of Scope
- SCI machinery itself (delivered by T-C8 / TASK-PROC-032-05-01)
- Cascade detection and width breaker (T-C11)
- Coverage ordering / L3 assertion (T-C13)
- App-shell launch-map requirement authoring (T-C17)

## Acceptance Criteria

- [ ] `ui-scribble-generator` emits all 5 entry-context fields in generated scribble output
- [ ] Reviewer agents assert presence of all 5 fields
- [ ] Reviewer agents assert internal consistency (dimension matches surface type, etc.)
- [ ] Reviewer agents assert size-appropriateness of container dimension
- [ ] Reconciliation runs against router/screenshot for already-built openers and is bounded (no infinite loop)
- [ ] Greenfield surfaces pass review without reconciliation
- [ ] All existing tests pass; no quality gate regressions

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-05-01 | pending | SCI machinery must exist before entry-context spine can integrate with scribble staleness state |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-05-01](../2026-06-06_impl_derive-f05-sci-invariant-audit-and-rot-graph/goal.md) | Predecessor — executor should read SCI machinery deliverables before implementing entry-context spine |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_impl_derive-f05-entry-context-spine/

Coverage auto-set from plan: [AC-08]

target_package omitted: process task, no release package.
