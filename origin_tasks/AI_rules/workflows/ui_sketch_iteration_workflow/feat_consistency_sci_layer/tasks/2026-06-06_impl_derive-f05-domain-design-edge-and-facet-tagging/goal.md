---
task_id: TASK-PROC-032-05-08
type: impl
parent_requirement: REQ-PROC-032-05
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: pending
effort: M
created: 2026-06-06
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "Must hold domain→design conditional edge, data-bound detector, AC facet-tagging (auto-heuristic + human confirm), and facet-tag audit in one coherent design across two skills."
after: [TASK-PROC-032-05-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11, AC-12]
  sections: []
scope_description: "Implement domain→design conditional edge + data-bound detector, AC facet-tagging {presentation|behaviour|both} (auto-heuristic + human confirm, fail-safe to presentation), and facet-tag audit (E5 probe)."
release_description: "Adds domain-to-design ordering edge and AC facet tagging to route presentation ACs through scribble first."
opus_recommended: true  # reason: explicit decision task — AC facet-tagging requires evaluation of heuristic options and human-confirm gate design across two skills
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Implement Domain→Design Edge and AC Facet Tagging (T-C14)

## Objective

Implement the domain→design conditional ordering edge and AC facet tagging:

1. **Domain→design conditional edge**: When a presentation/both AC references a domain value-object with behaviour criteria in the same design-unit, a soft ordering preference is emitted (design before domain). For code-first units, this hardens to a blocking edge; human override is available at the gate.
2. **Data-bound detector**: Detects when a presentation AC is bound to domain state (value-object with behaviour criteria in the same design-unit).
3. **AC facet tagging** (`{presentation | behaviour | both}`):
   - Auto-heuristic: infer facet from AC content (keyword/pattern matching)
   - Human confirm: present auto-tag for developer confirmation
   - Fail-safe: default to `presentation` if heuristic is inconclusive
4. **Facet-tag audit (E5 probe)**: Emit a structured audit of all AC facet tags for inspection.

Skills: `claude-modify-skill` (task-derive-from-requ, requ-explore). After T-C13 (TASK-PROC-032-05-02 — coverage ordering must be in place before facet-tag-driven ordering can compose with it).

## Requirements Summary

Covers AC-11 (domain→design conditional edge + data-bound detector) and AC-12 (AC facet-tagging + audit) of REQ-PROC-032-05.

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Domain→design conditional edge (soft for greenfield, hard-blocking for code-first units; human override at gate)
- Data-bound detector (presentation AC referencing domain value-object with behaviour criteria in same design-unit)
- AC facet-tagging (auto-heuristic + human confirm + presentation fail-safe)
- Facet-tag audit (E5 probe) output format

### Out of Scope
- Coverage ordering / L3 assertion (T-C13, predecessor)
- SCI machinery (T-C8, predecessor)
- Entry-context spine (T-C12)
- App-shell launch-map (T-C17)

## Acceptance Criteria

- [ ] Domain→design soft ordering edge emitted for presentation/both ACs referencing domain value-objects with behaviour criteria in same design-unit
- [ ] Soft edge hardens to blocking for code-first units; human override available at gate
- [ ] Data-bound detector correctly identifies the triggering condition
- [ ] Auto-heuristic infers AC facet tag (`presentation | behaviour | both`) from AC content
- [ ] Human confirm gate presents auto-tag before persisting
- [ ] Facet-tag fails safe to `presentation` when heuristic is inconclusive
- [ ] Facet-tag audit (E5 probe) emits structured output covering all AC facet tags
- [ ] All existing tests pass; no quality gate regressions

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-05-02 | pending | Coverage ordering (T-C13) must be in place before facet-tag-driven ordering composes with it |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-05-02](../2026-06-06_impl_derive-f05-coverage-ordering-and-l3-assertion/goal.md) | Predecessor — executor should read coverage/ordering deliverables before implementing domain→design edge |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_impl_derive-f05-domain-design-edge-and-facet-tagging/

Coverage auto-set from plan: [AC-11, AC-12]

target_package omitted: process task, no release package.
