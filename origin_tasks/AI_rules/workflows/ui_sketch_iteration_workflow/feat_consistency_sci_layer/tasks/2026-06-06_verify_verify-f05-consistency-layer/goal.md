---
task_id: TASK-PROC-032-05-09
type: verify
parent_requirement: REQ-PROC-032-05
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: pending
effort: M
created: 2026-06-06
skill_chain_depth: 3
after: [TASK-PROC-032-05-01, TASK-PROC-032-05-02, TASK-PROC-032-05-03, TASK-PROC-032-05-04, TASK-PROC-032-05-05, TASK-PROC-032-05-06, TASK-PROC-032-05-07, TASK-PROC-032-05-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14]
  sections: [SEC-18]
scope_description: "Process verification: run check_scribble_currency.py + SCI audit + flow→scribble coverage report against fixture; confirm each AC-01…AC-14 is observable in scripts/skills/agents outputs."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 85ed6d20
  file: ../requirements.md
---

# Goal: Verify F05 Consistency Layer (verify-f05)

## Objective

Audit task (process verification): confirm that all 14 acceptance criteria of REQ-PROC-032-05 are observable in the delivered scripts, skills, and agents. This is distinct from the global fixture gate (T-CV).

Run against a fixture:
1. `check_scribble_currency.py` — confirm it detects SCI violations (AC-02)
2. SCI audit blocking gate — confirm it blocks a stale-scribble coding task (AC-01, AC-03)
3. Flow→scribble coverage report — confirm coverage ordering and L3 assertion surface (AC-07, AC-09)

Confirm each AC is observable:
- **AC-01**: SCI blocks a stale-scribble coding task at the invariant boundary
- **AC-02**: Standing SCI audit detects every violation
- **AC-03**: `check_scribble_currency.py` runs as blocking gate at release finalization
- **AC-04**: Loopback-as-task: normative-upstream loopback creates blocking task, not inline edit
- **AC-05**: Lazy-wavefront cascade detector fires on depth-1 cascade
- **AC-06**: Width breaker: soft threshold warns, hard threshold escalates via back-pressure; PROP-10 integrity check + bounded recovery
- **AC-07**: Flow→scribble coverage report runs; task_type:scribble auto-set for presentation/both ACs; ordering soft-pref emitted
- **AC-08**: Entry-context spine: generator emits all 5 fields; reviewers assert presence/consistency/size-appropriateness; reconciliation bounded
- **AC-09**: L3 coverage assertion detects missing L3 entries; chain-length alert emitted above threshold
- **AC-10**: Design-unit map emitted; Tier A + Tier B entry-seam detection work; launch-map requirement exists
- **AC-11**: Domain→design edge emitted for data-bound ACs; hardens to blocking for code-first units
- **AC-12**: AC facet-tagging (auto-heuristic + human confirm + presentation fail-safe); facet-tag audit (E5 probe) emitted
- **AC-13**: `ui-verify-flutter` hard-blocks generative readers; override labels run as stale-target; referential readers flag-only
- **AC-14**: Soft-SCI mode is gated (sign-off required) and defaults to OFF

## Requirements Summary

Covers all 14 ACs of REQ-PROC-032-05 (verification pass).

For complete requirements at task creation time:
```
git show 85ed6d20:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Fixture-based verification of all 14 ACs
- Running `check_scribble_currency.py`, SCI audit, flow→scribble coverage report
- Observability checks for each skill/agent/script behavior

### Out of Scope
- Global fixture gate (T-CV — separate task)
- Implementation of any AC (all impl tasks must be completed before this runs)

## Acceptance Criteria

- [ ] AC-01: SCI blocks a stale-scribble coding task at the invariant boundary (observed against fixture)
- [ ] AC-02: Standing SCI audit detects every violation (observed against fixture)
- [ ] AC-03: `check_scribble_currency.py` runs as blocking gate at release finalization (observed)
- [ ] AC-04: Loopback-as-task: normative-upstream loopback creates blocking task (observed)
- [ ] AC-05: Lazy-wavefront cascade detector fires on depth-1 cascade (observed)
- [ ] AC-06: Width breaker: soft warns, hard escalates; PROP-10 integrity check + bounded recovery (observed)
- [ ] AC-07: Coverage report runs; task_type:scribble auto-set; ordering soft-pref emitted (observed)
- [ ] AC-08: Entry-context spine: generator emits all 5 fields; reviewers assert; bounded reconciliation (observed)
- [ ] AC-09: L3 assertion fires; chain-length alert emitted (observed)
- [ ] AC-10: Design-unit map emitted; Tier A + B seam detection work; launch-map requirement exists (observed)
- [ ] AC-11: Domain→design edge emitted; hardens to blocking for code-first units (observed)
- [ ] AC-12: AC facet-tagging + audit (E5 probe) emitted (observed)
- [ ] AC-13: `ui-verify-flutter` generative block + stale-target label + referential flag-only (observed)
- [ ] AC-14: Soft-SCI mode gated/off by default (observed)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-05-01 | pending | SCI machinery (T-C8) |
| TASK-PROC-032-05-02 | pending | Coverage ordering + L3 assertion (T-C13) |
| TASK-PROC-032-05-03 | pending | App-shell launch-map + seam detection (T-C17) |
| TASK-PROC-032-05-04 | pending | Stale-block + override (T-C9) |
| TASK-PROC-032-05-05 | pending | Loopback-as-task (T-C10) |
| TASK-PROC-032-05-06 | pending | Cascade detector + width breaker (T-C11) |
| TASK-PROC-032-05-07 | pending | Entry-context spine (T-C12) |
| TASK-PROC-032-05-08 | pending | Domain→design edge + facet tagging (T-C14) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-05-01](../2026-06-06_impl_derive-f05-sci-invariant-audit-and-rot-graph/goal.md) | Predecessor — SCI machinery |
| [TASK-PROC-032-05-02](../2026-06-06_impl_derive-f05-coverage-ordering-and-l3-assertion/goal.md) | Predecessor — coverage ordering + L3 assertion |
| [TASK-PROC-032-05-03](../2026-06-06_impl_derive-f05-app-shell-launch-map-and-seam-detection/goal.md) | Predecessor — launch-map + seam detection |
| [TASK-PROC-032-05-04](../2026-06-06_impl_derive-f05-verify-flutter-stale-block-and-override/goal.md) | Predecessor — stale-block + override |
| [TASK-PROC-032-05-05](../2026-06-06_impl_derive-f05-loopback-as-task/goal.md) | Predecessor — loopback-as-task |
| [TASK-PROC-032-05-06](../2026-06-06_impl_derive-f05-lazy-wavefront-cascade-and-width-breaker/goal.md) | Predecessor — cascade detector + width breaker |
| [TASK-PROC-032-05-07](../2026-06-06_impl_derive-f05-entry-context-spine/goal.md) | Predecessor — entry-context spine |
| [TASK-PROC-032-05-08](../2026-06-06_impl_derive-f05-domain-design-edge-and-facet-tagging/goal.md) | Predecessor — domain→design edge + facet tagging |

## Notes

Location auto-accepted (plan-driven mode): requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/feat_consistency_sci_layer/tasks/2026-06-06_verify_verify-f05-consistency-layer/

Coverage auto-set from plan: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14]

target_package omitted: verification task, no release package.

Distinct from global fixture gate T-CV. After all 8 impl tasks (032-05-01 through 032-05-08).
