---
task_id: TASK-PROC-032-05-03
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
synthesis_justification: "Must hold design-unit map emission, two-tier entry-seam detection logic, and the app-shell launch-map requirement authoring in a single coherent design."
after: [TASK-PROC-032-06-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10]
  sections: []
scope_description: "Implement design-unit map emission, two-tier entry-seam foundation_gap detection (Tier A local provisional + Tier B global authoritative), and author the app-shell / feature-launch-map requirement (PROP-11 R4 / F12-F14)."
release_description: "Adds app-shell launch-map requirement and entry-seam gap detection for design-unit coverage."
opus_recommended: true  # reason: synthesis + cross-cutting — map emission + two-tier seam detection + authoring a new requirement span multiple skills; cross-slice after T-C1 (REQ-PROC-035) not yet derived
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Implement App-Shell Launch-Map and Entry-Seam Detection (T-C17)

## Objective

Implement the design-unit map emission and two-tier entry-seam foundation_gap detection, and author the app-shell / feature-launch-map requirement. Specifically:

1. **Design-unit map emission**: `requ-derive-from-flow` emits a design-unit map (flow→scribble→requirement coverage) as part of its output.
2. **Two-tier entry-seam detection**:
   - Tier A (local provisional): `requ-derive-from-flow` local pass — detect entry-seam gaps provisionally; pass without blocking on first run.
   - Tier B (global authoritative): `requ-verify-flow-coverage --all` global pass — dedup and confirm entry-seam gaps across the full flow set; emit `foundation_gap` markers.
3. **App-shell / feature-launch-map requirement**: Author the canonical Tier-1 requirement (PROP-11 R4 / F12–F14) as part of scope. This is a new requirement file to be created by this task.

Skills/scripts: `claude-modify-skill` (requ-derive-from-flow, requ-verify-flow-coverage).

**CROSS-SLICE dependency**: this task logically depends on the REQ-PROC-035 spine task implementing T-C1 (--scope mode). That task is not yet derived; this dependency is unresolved. Reconcile via `task-repair-meta` once REQ-PROC-035 is decomposed. Do NOT add the spine task to `after:` now — it does not exist yet.

## Requirements Summary

Covers AC-10 (design-unit map, entry-seam seam detection, app-shell launch-map requirement) of REQ-PROC-032-05.

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Design-unit map emission in `requ-derive-from-flow`
- Tier A (local provisional) entry-seam gap detection in `requ-derive-from-flow`
- Tier B (global authoritative) entry-seam dedup + `foundation_gap` marker emission in `requ-verify-flow-coverage --all`
- Authoring the app-shell / feature-launch-map requirement (PROP-11 R4 / F12–F14) as part of this task's deliverables

### Out of Scope
- Cross-slice spine (T-C1, REQ-PROC-035) — reconcile via task-repair-meta
- Coverage ordering and L3 assertion (T-C13)
- Domain→design edge and facet tagging (T-C14)

## Acceptance Criteria

- [ ] `requ-derive-from-flow` emits a design-unit map in its output
- [ ] `requ-derive-from-flow` detects entry-seam gaps provisionally (Tier A, does not block first run)
- [ ] `requ-verify-flow-coverage --all` deduplicates and confirms entry-seam gaps, emits `foundation_gap` markers (Tier B)
- [ ] App-shell / feature-launch-map requirement (PROP-11 R4 / F12–F14) authored and committed
- [ ] All existing tests pass; no quality gate regressions

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No within-slice blocking dependencies; CROSS-SLICE after: T-C1 (REQ-PROC-035, not yet derived) — reconcile via task-repair-meta |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_impl_derive-f05-app-shell-launch-map-and-seam-detection/

Coverage auto-set from plan: [AC-10]

target_package omitted: process task, no release package.

CROSS-SLICE note: The REQ-PROC-035 spine task T-C1 (--scope mode) is a logical predecessor but is not yet derived. Record in implementation_notes and reconcile via task-repair-meta once REQ-PROC-035 is decomposed.

NOTE: Authoring the launch-map requirement is part of scope (not a separate task).
