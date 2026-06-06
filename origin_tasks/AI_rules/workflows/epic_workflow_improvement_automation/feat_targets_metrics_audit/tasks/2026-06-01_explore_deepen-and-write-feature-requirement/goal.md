---
task_id: TASK-PROC-006-02-01
type: explore
parent_requirement: REQ-PROC-006-02
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
scope_description: "Deepen feature feat_targets_metrics_audit per the approved epic plan, then fill its feature requirement (REQ-PROC-006-02) via requ-explore."
release_description: ""
effort: L
created: 2026-06-01
opus_recommended: true   # reason: cross-cutting explore that writes a feature requirement; defines the north-star/target model
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 74dfea86
  file: ../requirements.md
---

# Goal: Deepen & Write the Targets / Metrics / Audit Feature Requirement

## Objective

Deepen this feature per the approved epic plan, then fill the feature requirement
(REQ-PROC-006-02, currently a `placeholder`) via `requ-explore`. Do for *this feature*
what TASK-PROC-006-20 did for the whole system.

Open questions: what is the three-layer target model concretely (app-quality north-star
+ GQM scope-local leading indicators + guardrail pointers); how does each leading
indicator ladder up to the north-star; and how is the audit rubric split into a
loop-hygiene half and a north-star-laddered half, computed deterministically?

## Background

This feature merges "what to aim at" (targets) with "how the loop is scored" (audit)
because they are one measurement concern. The placeholder requirement already carries
the effectiveness-metrics and audit detail moved down from the old epic, plus the
DuckDB v1.5 deferral. It absorbs the pending impl task TASK-PROC-006-16 (DuckDB optional
query layer), now living in this feature's `tasks/`.

A bug to reconcile: the audit `--monitor` exit-code behavior (F-3).

Current requirements: ../requirements.md

For complete requirements at task creation time:
```
git show 74dfea86:requirements_tasks/process/AI_rules/workflows/epic_workflow_improvement_automation/feat_targets_metrics_audit/requirements.md
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

1. **Three-layer target model.** North-star = app quality (distal); per-stage leading
   indicators that ladder up; guardrail pointers to feat_guardrails_and_budgets. Which
   become requirement-level vs tuning constants?
2. **Deterministic rubric, two halves.** Loop-hygiene criteria AND north-star-laddered
   criteria — all computed from `runs.tsv` + git, never from LLM judgment.
3. **Metric maturation.** user-unblock-rate (fast) vs revert-rate (slow, quarterly) —
   are these the right leading indicators, or proxies that need replacing?
4. **DuckDB layer.** When does the audit accumulate enough data to justify joins (the
   absorbed TASK-PROC-006-16)?
5. **The `--monitor` exit-code bug (F-3).** Fold into the requirement.

## Execution Model

Gather raw material — read `scripts/optimize/`, `claude-optimize-audit`,
`.factory/optimize/history/`, the placeholder requirement — then synthesize iteratively.
The session model is fixed at launch (Opus). End by running `requ-explore` to write
REQ-PROC-006-02 (lift it out of `placeholder`).

**Web research**: delegate to a spawned `general-purpose` agent with a focused question
(e.g. *"how to choose leading-indicator proxy metrics that ladder up to a distal quality
goal?"*); never run WebSearch inline.

## Output

A synthesis in `plans_and_protocols/` and a filled feature requirement
(REQ-PROC-006-02) with testable acceptance criteria, honest about residual uncertainty.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The feature requirement REQ-PROC-006-02 is written via requ-explore (no longer a placeholder)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. Subordinate to product delivery (G-INV-5). |
</content>
