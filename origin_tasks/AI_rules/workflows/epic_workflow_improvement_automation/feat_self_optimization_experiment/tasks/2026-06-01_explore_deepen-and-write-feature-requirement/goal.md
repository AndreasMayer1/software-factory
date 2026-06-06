---
task_id: TASK-PROC-006-07-01
type: explore
parent_requirement: REQ-PROC-006-07
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
scope_description: "Deepen feature feat_self_optimization_experiment per the approved epic plan, then fill its feature requirement (REQ-PROC-006-07) via requ-explore."
release_description: ""
effort: L
created: 2026-06-01
opus_recommended: true   # reason: cross-cutting explore that writes a feature requirement; experiment design + kill-switch safety
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 74dfea86
  file: ../requirements.md
---

# Goal: Deepen & Write the Self-Optimization-Experiment Feature Requirement

## Objective

Deepen this feature per the approved epic plan, then fill the feature requirement
(REQ-PROC-006-07, currently a `placeholder`) via `requ-explore`. Do for *this feature*
what TASK-PROC-006-20 did for the whole system.

Open questions: how are the two staged, developer-witnessed runs designed (drain &
baseline, then optimizer-on-itself); what is the OEC (Overall Evaluation Criterion) and
the auto-abort conditions; and how does the hard token kill-switch guarantee the
experiment cannot blow the weekly budget?

## Background

This is a bounded, time-boxed activity — distinct from the standing guardrails in
feat_guardrails_and_budgets. It is meant to demonstrate the optimizer can *measurably*
improve toward its targets by running on itself at higher cadence while it is young. It
depends on the target metrics (feat_targets_metrics_audit) for its baseline and OEC, and
on the weekly budget / kill-switch infrastructure (feat_guardrails_and_budgets).

Current requirements: ../requirements.md

For complete requirements at task creation time:
```
git show 74dfea86:requirements_tasks/process/AI_rules/workflows/epic_workflow_improvement_automation/feat_self_optimization_experiment/requirements.md
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

1. **Stage 1 — drain & baseline.** Drain the event backlog; establish a baseline reading
   of the target metrics (feat_targets_metrics_audit) before any self-tuning.
2. **Stage 2 — optimizer-on-itself.** Higher cadence against itself, measured by
   `claude-optimize-audit` + the new target metrics, with explicit success/failure
   criteria.
3. **OEC + auto-abort.** Define the composite metric the experiment optimizes and the
   auto-abort conditions (regression, drift, budget burn).
4. **Hard token kill-switch.** Deterministic; must not blow the weekly byte budget
   (G-INV-4, feat_guardrails_and_budgets). Developer-witnessed; subordinate to delivery.

## Execution Model

Gather raw material — read the optimizer implementation, the audit skill,
`.factory/optimize/`, the placeholder requirement — then synthesize iteratively. The
session model is fixed at launch (Opus). End by running `requ-explore` to write
REQ-PROC-006-07.

**Web research**: delegate to a spawned `general-purpose` agent with a focused question
(e.g. *"how do online controlled experiments define an OEC and safe auto-abort
guardrails?"*); never run WebSearch inline.

## Output

A synthesis in `plans_and_protocols/` and a filled feature requirement
(REQ-PROC-006-07) with testable acceptance criteria, honest about residual uncertainty.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The feature requirement REQ-PROC-006-07 is written via requ-explore (no longer a placeholder)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. Subordinate to product delivery (G-INV-5). |
</content>
