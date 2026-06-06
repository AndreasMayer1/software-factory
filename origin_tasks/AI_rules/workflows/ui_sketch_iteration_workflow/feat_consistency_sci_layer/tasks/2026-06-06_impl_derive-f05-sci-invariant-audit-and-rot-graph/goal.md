---
task_id: TASK-PROC-032-05-01
type: impl
parent_requirement: REQ-PROC-032-05
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: in_progress
effort: L
created: 2026-06-06
started: 2026-06-06
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold staleness-rot-graph invariant, SCI audit logic, skill edits, and new script in one coherent design."
after: [TASK-PROC-032-06-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-14]
  sections: []
scope_description: "Implement SCI machinery: stale_since marker, rot-graph detectors, standing currency audit script, soft-SCI mode, stall report (E1 probe)."
release_description: "Enforces scribble currency invariant — blocks coding tasks when scribbles are stale."
opus_recommended: true  # reason: cross-cutting invariant — SCI machinery spans skill edits + new script + rot-graph; must be held in synthesis
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
session_id: 36c6db87-1495-4183-aa0f-5a8607a3898b
session_account: gmail
---
# Goal: Implement SCI Invariant Machinery, Rot-Graph Detectors, and Standing Audit (T-C8)

## Objective

Implement the core Scribble-Currency Invariant (SCI) enforcement machinery that makes AC-01 a standing property of the system. This includes:

1. **`stale_since` marker**: Set on a scribble when a LOCKED-IN requirement edit occurs, making dependent coding tasks non-runnable.
2. **Auto-create scribble-refresh tasks**: When a requirement edit invalidates a scribble, automatically create a blocking task to refresh it.
3. **Five-edge staleness rot-graph + detectors**: Implement all five named staleness edges (req→scribble, scribble→coding task, domain-code→data-bound scribble, scribble→dependent scribble, scribble→verification verdict) with a detector for each.
4. **Standing script-driven SCI audit** (`check_scribble_currency.py`, new): Resolves every coding task's covered scribble, asserts it is approved and its `contributing_requirements` commit is at/ahead of the requirement's current committed version. Runs as a blocking gate at release finalization; additive to the storage-mirror parity check.
5. **Soft-SCI mode**: Configurable, sign-off-gated mode (default OFF) for exceptional overrides.
6. **E1 stall report probe**: Emit the stall report showing coding tasks blocked by stale scribbles.

## Requirements Summary

AC-01: No coding task is runnable while its covered scribble is missing, unapproved, or stale.
AC-02: Standing SCI audit script detects every violation; runs standalone and at release finalization.
AC-03: Five-edge staleness rot-graph, each edge with a named detector.
AC-14: (cross-referenced — see requirements.md for full text)

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `stale_since` marker protocol in requ-explore (set on scribble at LOCKED-IN requirement edit time)
- Auto-creation of a blocking scribble-refresh task when `stale_since` is set
- All five rot-graph edge detectors (named, per AC-03)
- New script `scripts/quality/check_scribble_currency.py`: resolves coding task → scribble coverage → currency check; reports SCI violations; integrates as a blocking gate at release finalization
- Integration of currency gate into release finalization (additive to storage-mirror parity check)
- Soft-SCI mode (configurable, sign-off-gated, default OFF) in requ-explore / task-derive-from-requ
- E1 stall report: list of coding tasks blocked by stale scribbles
- Skill edits: `claude-modify-skill` on requ-explore and task-derive-from-requ; `claude-write-script` for new currency script

### Out of Scope
- T-C9 (verify-flutter stale-block/override) — handled by a separate task
- T-C11 (lazy-wavefront cascade detector) — separate task, though edge (4) is documented here
- T-C12 (entry-context spine) — separate task
- T-C13/C14/C17 (coverage/ordering, domain→design edge, app-shell map) — separate tasks
- REQ-PROC-035 spine tasks (Wave-1 split) — cross-slice dependency, not yet derived

## Acceptance Criteria

- [ ] `stale_since` is set on a scribble when a LOCKED-IN requirement edit occurs in requ-explore
- [ ] A blocking scribble-refresh task is auto-created when `stale_since` is set
- [ ] All five rot-graph edges are implemented with named detectors (AC-03)
- [ ] `check_scribble_currency.py` exists under `scripts/quality/`, resolves coding task → scribble → currency, and reports SCI violations
- [ ] The currency script runs standalone and as a blocking gate at release finalization
- [ ] Soft-SCI mode is implemented (configurable, sign-off-gated, default OFF)
- [ ] E1 stall report is emitted by the currency script
- [ ] Skill edits (requ-explore, task-derive-from-requ) reflect the new SCI machinery
- [ ] No existing tests broken; new script passes Python quality gates (G1–G5)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-035 spine T-C2 (release-begin-impl Wave-1 split) | not yet derived | CROSS-SLICE: record in notes; reconcile via task-repair-meta once REQ-PROC-035 is decomposed |

## Notes

**CROSS-SLICE dependency**: This task depends on the REQ-PROC-035 spine task implementing T-C2 (the release-begin-impl Wave-1 split that gates coding-task creation). That task is not yet derived. The `after:` field above omits it; reconcile via `task-repair-meta` once REQ-PROC-035 decomposition is complete.

**Implementation guide** (from plan):
SCI machinery: set `stale_since` on a LOCKED-IN requirement edit; auto-create scribble-refresh tasks; the five-edge staleness rot-graph + detectors; the standing script-driven SCI audit (`check_scribble_currency.py`, new) blocking at release finalization, additive to the storage-mirror parity check; soft-SCI configurable sign-off-gated mode default OFF; emit the stall report (E1 probe). Skills/scripts: claude-modify-skill (requ-explore / task-derive-from-requ) + claude-write-script (new currency script). CROSS-SLICE after: the REQ-PROC-035 spine task implementing T-C2 (release-begin-impl Wave-1 split) — not yet derived; reconcile via task-repair-meta.
