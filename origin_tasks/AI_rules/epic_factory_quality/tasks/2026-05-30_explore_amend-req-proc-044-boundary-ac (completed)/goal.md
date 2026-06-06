---
task_id: TASK-PROC-044-11
type: explore
parent_requirement: REQ-PROC-044
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-05-30
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-30T21:46:55Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-04, AC-08]
  sections: []
scope_description: "Amend REQ-PROC-044 to add a boundary AC (draft AC-07) making external factory-boundary contracts explicit, referencing the external-state postcondition vocabulary. Source: TASK-PROC-044-10 synthesis §4."
release_description: ""
writes_requirements: true
opus_recommended: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-10
session_id: 218b5799-4cb5-46d5-afd2-87b72745462e
session_account: web

---
# Goal: Amend REQ-PROC-044 with an External-Boundary Contract AC

## Objective

The exploration TASK-PROC-044-10 (FU-8) concluded that external factory-boundary
interfaces (E1–E9) reuse the *same* contract format as internal skill contracts, with one
additive field (`input_modality:`) and a controlled external-state postcondition vocabulary
(now implemented at `scripts/factory/external_state/`). It recommended **folding** external
contracts under REQ-PROC-044 rather than spawning a sibling requirement.

This task makes that fold real: add an acceptance criterion to REQ-PROC-044 that makes the
boundary explicit. FU-8 itself was `writes_requirements: false` and therefore could not edit
the requirement — this task is the requirement-modifying step.

## Background

The full rationale, the draft AC-07 wording, and the "why requ-explore not product-intake"
argument are in:
`requirements_tasks/process/AI_rules/factory_quality/tasks/2026-05-29_explore_external-interface-contracts/plans_and_protocols/2026-05-30_03_synthesis.md` (§4).

Read it as the spec for this amendment. The draft AC-07 there is illustrative — the final
end-state wording lands under requ-explore's quality gate.

Current requirements: ../../requirements.md

## How to Approach This

This is an `exists_needs_update` extension of an active living requirement (REQ-PROC-044,
`status: active`). Use `requ-explore` in Scenario E (extending an existing requirement):
add one AC to `trackable_items.acceptance_criteria` + a short Dimension note; do not
restructure the existing AC-01..AC-06. Keep the AC in end-state language (no transition
verbs). Leave `status: active`.

## Output

REQ-PROC-044 carries a new boundary AC (AC-07) referencing the external-state vocabulary,
so that FU-8b (the rollout impl task) has a requirement to cover.

## Acceptance Criteria

- [x] REQ-PROC-044 has a new AC making external-boundary contracts explicit, in end-state language
- [x] The AC references the external-state postcondition vocabulary (scripts/factory/external_state/)
- [x] AC-01..AC-06 are unchanged; requirement stays status: active
- [x] The synthesis §4 rationale is honored (fold, not sibling); decision recorded if it deviates

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-10 | in_progress | Source exploration; provides the draft AC + vocabulary |
