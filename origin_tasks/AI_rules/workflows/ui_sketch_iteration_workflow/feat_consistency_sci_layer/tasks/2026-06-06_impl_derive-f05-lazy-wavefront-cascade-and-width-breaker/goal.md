---
task_id: TASK-PROC-032-05-06
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
synthesis_justification: "Must hold lazy-wavefront cascade detector (live flow_positions + visited set), two-stage width breaker (configurable soft/hard defaults), and PROP-10 entry-reference integrity in one coherent design."
after: [TASK-PROC-032-05-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05, AC-06]
  sections: []
scope_description: "Implement lazy-wavefront depth-1 cascade detector (live flow_positions, per-cascade visited set), two-stage width breaker (soft 3 / hard 7 defaults, configurable, hard escalates via back-pressure), PROP-10 mode-independent entry-reference integrity check and bounded recovery, cascade log (E2 probe)."
release_description: "Adds lazy cascade detection and width breaker to prevent unbounded scribble refresh cascades."
opus_recommended: true  # reason: cross-cutting invariant — cascade detector + width breaker + entry-reference integrity check span agent + skill edits with inter-dependent state
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Implement Lazy-Wavefront Cascade Detector and Width Breaker (T-C11)

## Objective

Implement the lazy-wavefront cascade detection and width-breaker machinery:

1. **Lazy-wavefront cascade detector**: Depth-1 cascade detector using live `flow_positions` and a per-cascade visited set to avoid re-visiting nodes. Detects when a scribble refresh triggers further downstream refresh cascades.
2. **Two-stage width breaker**:
   - Soft threshold (default 3, configurable): emits a warning when the cascade width exceeds the soft limit.
   - Hard threshold (default 7, configurable): escalates via the back-pressure protocol (measured-on-fixture defaults) when the cascade width exceeds the hard limit.
3. **PROP-10 mode-independent entry-reference integrity**: Checks entry-reference integrity regardless of sketch mode; bounded recovery (does not loop indefinitely).
4. **Cascade log (E2 probe)**: Emits a structured cascade log for audit/inspection.

Skills/agents: `claude-modify-agent` (ui-scribble-cross-feature-checker) + `claude-modify-skill` (ui-scribble-auto-review). Requires SCI machinery from T-C8 (TASK-PROC-032-05-01).

## Requirements Summary

Covers AC-05 (lazy-wavefront cascade detector + width breaker) and AC-06 (PROP-10 entry-reference integrity + bounded recovery) of REQ-PROC-032-05.

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Lazy-wavefront depth-1 cascade detector (live flow_positions, per-cascade visited set)
- Two-stage width breaker (soft 3 / hard 7 measured-on-fixture defaults, configurable, hard escalates via back-pressure)
- PROP-10 mode-independent entry-reference integrity check + bounded recovery
- Cascade log (E2 probe) output format

### Out of Scope
- SCI machinery itself (delivered by T-C8 / TASK-PROC-032-05-01)
- Entry-context spine (T-C12)
- Coverage ordering / L3 assertion (T-C13)
- Loopback-as-task (T-C10)

## Acceptance Criteria

- [ ] Lazy-wavefront cascade detector fires on depth-1 cascade using live flow_positions + per-cascade visited set
- [ ] Soft width threshold (default 3) emits warning; hard threshold (default 7) escalates via back-pressure
- [ ] Both thresholds are configurable
- [ ] PROP-10 entry-reference integrity check runs mode-independently with bounded recovery
- [ ] Cascade log (E2 probe) is emitted with structured output
- [ ] All existing tests pass; no quality gate regressions

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-05-01 | pending | SCI machinery must exist before cascade detector can read scribble staleness/rot-graph state |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-05-01](../2026-06-06_impl_derive-f05-sci-invariant-audit-and-rot-graph/goal.md) | Predecessor — executor should read SCI machinery deliverables before implementing cascade detector |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_impl_derive-f05-lazy-wavefront-cascade-and-width-breaker/

Coverage auto-set from plan: [AC-05, AC-06]

target_package omitted: process task, no release package.
