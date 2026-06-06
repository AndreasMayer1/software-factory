---
task_id: TASK-PROC-032-20
type: verify
parent_requirement: REQ-PROC-032-03
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-31
started: 2026-06-02
completed: 2026-06-02
session_completed_at: 2026-06-02T04:10:08Z
after: [TASK-PROC-032-11, TASK-PROC-032-18, TASK-PROC-032-12, TASK-PROC-032-13, TASK-PROC-032-14, TASK-PROC-032-15, TASK-PROC-032-17, TASK-PROC-032-19, TASK-PROC-032-22, TASK-PROC-032-23, TASK-PROC-032-24, TASK-PROC-032-25, TASK-PROC-032-26]
awaiting: []
awaiting_note: ""
verification_task: true
covers:
  acceptance_criteria: [AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17]
  sections: []
scope_description: "Audit each of AC-21..AC-41 against the shipped edits; file fix tasks for any gaps. Hardened final guard: also assert no stale duplicate scribble docs remain after the storage migration, that the parity + contributing-requirements consistency lints run and pass, and that flow_navigation.yaml / APPROVAL_TRAIL / CONTRACT BLOCK / design_decisions block are actually present."
release_description: ""
opus_recommended: true  # reason: cross-cutting verification across 16 ACs and multiple producers/consumers
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
session_id: cfe593ff-f7e1-40c1-9083-145b478784ce
session_account: web
---
# Goal: Verify REQ-PROC-032 scribble-content ACs (AC-21..AC-41)

## Objective

Audit each of AC-21..AC-41 against the shipped edits (audit-only; file fix tasks for gaps).
This is the **final guard** for the whole scribble-content + recovered-strand programme — make the
verification as potent as possible; do not assume implementers were correct.

Process-requirement verification: run/read the producers and confirm each AC's end-state holds —
- AC-21..27 (contract): CONTRACT BLOCK present (dual framing), flutter_handoff `contract:` +
  `design_decisions:` + `verification_seeds:` blocks validate against the schema, named-token sizing
  + a11y-intent + rule-application audit trace present, Sketch-Gate + verifier anchored to the contract.
- AC-28..31 (review): heuristics corpus de-provisionalized + reconciled, auto-review brief + inter-version
  diff (with HTML toggle), persona-conflict/DDR surfacing, iteration-fatigue rail.
- AC-32..36 (content extensions): multi-breakpoint, structured inspiration inputs, reviewer pre-brief,
  cross-feature consistency, automated visual validation.
- **AC-37..41 (recovered strand)**: scribbles physically live at `requirements_tasks/scribbles/<feature_path>`
  mirroring `lib/features/` with **no stale duplicate docs at the old path**; the parity lint runs and passes;
  `flow_navigation.yaml` exists per participating flow and is referenced by `flutter_handoff.yaml`; per-flow
  walk validation + human walk instructions are present; `APPROVAL_TRAIL.md` is emitted on approval; the
  contributing-requirements/participating-flows discovery script + consistency lint run and pass.

## Requirements Summary

Verifies the full AC-21..AC-41 content set delivered by TASK-PROC-032-11 through -19 and -22 through -26.

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Audit-only verification of AC-21..AC-36 against the shipped producer/consumer/doc edits.
- File fix tasks for any gaps found.

### Out of Scope
- Implementing the ACs (done by the predecessor impl tasks).

## Acceptance Criteria

- [x] Each of AC-21..AC-36 audited against the shipped edits with end-state confirmed. (also AC-37..AC-41; all 21 COVERED)
- [x] CONTRACT BLOCK + flutter_handoff contract/verification_seeds blocks validated.
- [x] Sketch Gate + ui-verify-flutter contract anchoring confirmed.
- [x] Heuristics corpus de-provisionalization confirmed.
- [x] Breakpoint / inspiration / pre-brief / cross-feature / visual-validate behaviors confirmed present.
- [x] Fix tasks filed for any uncovered or incompletely-implemented AC. (none uncovered — no fix tasks required; see coverage_report_2026-06-02.md)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-11 | pending | Contract doctrine + producer surfacing |
| TASK-PROC-032-12 | pending | Review doctrine reconcile + cycle aids |
| TASK-PROC-032-13 | pending | Multi-breakpoint from persona device classes |
| TASK-PROC-032-14 | pending | Structured inspiration inputs |
| TASK-PROC-032-15 | pending | Reviewer pre-brief (Phase 0.5) |
| TASK-PROC-032-17 | pending | Cross-feature consistency check |
| TASK-PROC-032-18 | pending | Contract consumers — Sketch Gate + verifier |
| TASK-PROC-032-19 | pending | ui-visual-validate skill |

## Notes

Verification task — left unpackaged so it ranks alongside the impl tasks it verifies in next_tasks.py.
