---
task_id: TASK-PROC-032-06-01
type: impl
parent_requirement: REQ-PROC-032-06
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: in_progress
effort: M
created: 2026-06-06
started: 2026-06-06
expected_tool_calls: 20
skill_chain_depth: 2
after: [TASK-PROC-032-31, TASK-PROC-032-32]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Derive the impl tasks for feature REQ-PROC-032-06 (carrier + auto-review) in a single task-derive-from-requ run, covering the genuinely-uncovered new ACs authored by TASK-PROC-032-31 (carrier/review layer) and -32 (auto-review control)."
release_description: ""
opus_recommended: true
writes_requirements: false
requirements_version:
  commit: 9a73678c
  file: ../requirements.md
session_id: d33f08f6-c35a-4caf-b3d4-e7d18379f071
session_account: gmail
---
# Goal: Derive impl tasks for F06 (Carrier + Auto-Review)

## Objective

Run `task-derive-from-requ` **once** on `feat_carrier_and_auto_review/requirements.md`
(REQ-PROC-032-06) to decompose the feature into impl tasks. This single derivation
replaces what would otherwise be two colliding derivations: TASK-PROC-032-31 (carrier /
human-review layer) and TASK-PROC-032-32 (auto-review control model) both authored into
this one fused feature, so the feature is derived once here rather than by each authoring
task.

## Background

REQ-PROC-032 was restructured into an epic + 7 features (zero spec change, verified). The
fused F06 owns 12 ACs: the auto-review control ACs (AC-01, AC-09…12 — old AC-31, AC-63…66)
and the carrier/human-review-layer ACs (AC-02…08 — old AC-56…62). Because
`task-derive-from-requ` only derives tasks for **uncovered** ACs, and the genuinely-new
carrier/auto-review ACs have no completed-task coverage, this run produces exactly the new
impl work (no duplication of already-implemented ACs).

For the full restructure record + crosswalk:
`../../tasks/2026-06-06_impl_restructure-req-proc-032-into-epic/plans_and_protocols/`

Current requirements: ../requirements.md

## Scope

### In Scope
- One `task-derive-from-requ` run on REQ-PROC-032-06.
- **Append every derived impl task ID to `.claude/task_ordering_priority_override.txt`**
  (developer directive — process tasks carry no `target_package` and won't surface in
  `next_tasks.py` otherwise).

### Out of Scope
- Re-deriving already-implemented (covered) ACs.
- F05 (derived by TASK-PROC-032-30) and F07 (by TASK-PROC-032-33).

## Acceptance Criteria

- [ ] `task-derive-from-requ` run once on REQ-PROC-032-06; impl tasks created for its uncovered ACs.
- [ ] Each derived task ID appended to `.claude/task_ordering_priority_override.txt`.
- [ ] No duplicate derivation of F06 by TASK-PROC-032-31 or -32.
- [ ] For new tasks "after" is set to the other tasks that derive tasks from requ for the features below REQ-PROC-032.   

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-31 | pending | Authors carrier/review-layer ACs into F06 |
| TASK-PROC-032-32 | pending | Authors auto-review-control ACs into F06 |

## Notes

Created by the REQ-PROC-032 restructure (TASK-PROC-032-34) to resolve the two-authoring-tasks→one-fused-feature
derivation collision. Race-safe alternative to designating one of -31/-32 as the deriver.
