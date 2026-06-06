---
task_id: TASK-PROC-006-03-01
type: explore
parent_requirement: REQ-PROC-006-03
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: pending
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Deepen feature feat_evaluation_statistical_contract per the approved epic plan, then fill its feature requirement (REQ-PROC-006-03) via requ-explore."
release_description: ""
effort: L
created: 2026-06-01
opus_recommended: true   # reason: cross-cutting explore that writes a feature requirement; statistical-design judgment
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 74dfea86
  file: ../requirements.md
---

# Goal: Deepen & Write the Statistical-Contract Feature Requirement

## Objective

Deepen this feature per the approved epic plan, then fill the feature requirement
(REQ-PROC-006-03, currently a `placeholder`) via `requ-explore`. Do for *this feature*
what TASK-PROC-006-20 did for the whole system.

Open questions: what is the exact slow real-signal evaluation contract — the
events-not-tasks `min_evidence` threshold, the anytime-valid stopping rule (mSPRT /
e-values), CUSUM drift detection, the pending→verdict lifecycle, and how attribution +
holdback give a defensible counterfactual?

## Background

This is the slow, real-signal half of evaluation; its fast counterpart is the
simulation harness (feat_evaluation_simulation_harness). The two must compose into one
verdict story. The placeholder requirement carries the seam definition.

Current requirements: ../requirements.md

For complete requirements at task creation time:
```
git show 74dfea86:requirements_tasks/process/AI_rules/workflows/epic_workflow_improvement_automation/feat_evaluation_statistical_contract/requirements.md
```

## How to Approach This

Use design thinking — empathize before defining, diverge before converging, let
questions lead, iterate. One pass will not be enough.

**Read the full iteration history first so you have the whole picture** (the developer's
explicit instruction):
- TASK-PROC-006-20:
  `../../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `2026-05-30_02_synthesis_round1.md`, `2026-05-30_04_synthesis_round2.md`,
  `2026-05-31_06_synthesis_round3.md`; feedback `2026-05-30_03_feedback.md`,
  `2026-05-31_05_feedback.md`, `2026-06-01_feedback.md`; restructure plan
  `2026-06-01_07_plan_epic-restructure.md`.
- Original redesign:
  `../../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).

## Seeds

1. **Events, not tasks.** What is the `min_evidence` threshold before a verdict is valid?
2. **Anytime-valid stopping.** mSPRT / e-values so the loop can peek without inflating
   false positives — concretely parameterized.
3. **Drift detection.** CUSUM to catch post-verdict regressions.
4. **Lifecycle.** The pending→verdict state machine for each landed change.
5. **Attribution + holdback.** Which change caused the movement; a counterfactual
   fraction that bypasses the change.
6. **Composition with simulation.** How the slow verdict and the fast offline verdict
   (feat_evaluation_simulation_harness) combine.

## Execution Model

Gather raw material — read the optimizer implementation, `.factory/optimize/`, the
placeholder requirement — then synthesize iteratively. The session model is fixed at
launch (Opus). End by running `requ-explore` to write REQ-PROC-006-03.

**Web research**: delegate to a spawned `general-purpose` agent with a focused question
(e.g. *"how do online experimentation systems use anytime-valid e-values to stop early
without inflating error?"*); never run WebSearch inline.

## Output

A synthesis in `plans_and_protocols/` and a filled feature requirement
(REQ-PROC-006-03) with testable acceptance criteria, honest about residual uncertainty.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The feature requirement REQ-PROC-006-03 is written via requ-explore (no longer a placeholder)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. Subordinate to product delivery (G-INV-5). |
</content>
