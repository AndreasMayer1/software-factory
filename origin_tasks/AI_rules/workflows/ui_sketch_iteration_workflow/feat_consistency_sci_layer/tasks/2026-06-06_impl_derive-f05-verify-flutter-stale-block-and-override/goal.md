---
task_id: TASK-PROC-032-05-04
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
  acceptance_criteria: [AC-13]
  sections: []
scope_description: "Implement ui-verify-flutter stale-scribble hard-block for generative readers, explicit advisory override with stale-target label, and referential-reader flag-only mode."
release_description: "Blocks Flutter verification when scribble is stale; labels override runs as stale-target."
opus_recommended: false
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Implement ui-verify-flutter Stale-Block and Override (T-C9)

## Objective

Extend `ui-verify-flutter` to enforce the SCI stale-scribble gate:

1. **Generative reader hard-block**: `ui-verify-flutter` hard-blocks when the scribble of the covered requirement is stale (stale_since is set). The run must be explicitly overridden to proceed.
2. **Advisory override with stale-target label**: When the override is provided, the run proceeds and labels its verdict as made against a stale target (the label must be visible in the output and stored in the run record).
3. **Referential reader flag-only**: For referential readers (read-only, non-generative), staleness results in a flag/warning only — no hard block.

Skills: `claude-modify-skill` (ui-verify-flutter). Requires SCI machinery from T-C8 (TASK-PROC-032-05-01).

## Requirements Summary

Covers AC-13 (generative-block / referential-flag / stale-target label) of REQ-PROC-032-05.

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `ui-verify-flutter` hard-block logic for generative readers on stale scribble
- Explicit advisory override flag + stale-target label in output and run record
- Referential-reader flag-only (warning, no block)

### Out of Scope
- SCI machinery itself (delivered by T-C8 / TASK-PROC-032-05-01)
- Other SCI detectors (rot-graph, loopback, cascade, entry-context, coverage)

## Acceptance Criteria

- [ ] `ui-verify-flutter` hard-blocks generative readers when scribble `stale_since` is set
- [ ] Override flag allows run to proceed; output and run record carry "stale-target" label
- [ ] Referential readers emit a warning/flag only (no hard block) when scribble is stale
- [ ] All existing tests pass; no quality gate regressions

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-05-01 | pending | SCI machinery (stale_since, rot-graph) must exist before this stale-block can read staleness state |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-05-01](../2026-06-06_impl_derive-f05-sci-invariant-audit-and-rot-graph/goal.md) | Predecessor — executor should read SCI machinery deliverables before implementing the stale-block |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_impl_derive-f05-verify-flutter-stale-block-and-override/

Coverage auto-set from plan: [AC-13]

target_package omitted: process task, no release package.
