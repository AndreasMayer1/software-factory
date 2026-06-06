---
task_id: TASK-PROC-006-01-01
type: explore
parent_requirement: REQ-PROC-006-01
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: pending
effort: L
created: 2026-06-01
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Deepen feature feat_detection_event_pipeline per the approved epic plan, then fill its feature requirement (REQ-PROC-006-01) via requ-explore."
release_description: ""
opus_recommended: true   # reason: cross-cutting explore that writes a feature requirement; holds the whole-system model
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 74dfea86
  file: ../requirements.md
---

# Goal: Deepen & Write the Detection / Event-Pipeline Feature Requirement

## Objective

Deepen this feature per the approved epic plan, then fill the feature requirement
(REQ-PROC-006-01, currently a `placeholder`) via `requ-explore`. Do for *this feature*
what TASK-PROC-006-20 did for the whole system: enter the problem space, iterate, and
converge on a testable feature requirement with explicit acceptance criteria.

Open questions this exploration should resolve: what is the exact event schema and
idempotency contract; how does the consolidation combiner collapse related events; what
is the right queue ceiling and pruning policy; and what must trajectory logging capture
so the evaluation features (statistical contract, simulation harness) can replay real
tasks?

## Background

The detection layer is the source of every candidate the optimizer acts on. The epic
restructure (2026-06-01) split the old single REQ-PROC-006 into seven features; this
feature owns detection. The placeholder requirement already carries the monitor
taxonomy and aggregator detail moved down from the old epic — start from there.

A known gap to reconcile: the Stage-2 `skills_used:` trigger in `task-complete`
step 3.4b only fires on `*_protocol.md`, silently skipping other
`plans_and_protocols/` filenames.

Current requirements: ../requirements.md

For complete requirements at task creation time:
```
git show 74dfea86:requirements_tasks/process/AI_rules/workflows/epic_workflow_improvement_automation/feat_detection_event_pipeline/requirements.md
```

## How to Approach This

Use design thinking — empathize before defining, diverge before converging, let
questions lead, iterate. One pass will not be enough.

**Read the full iteration history first so you have the whole picture** (the developer's
explicit instruction):
- This feature's lineage — the holistic re-alignment task TASK-PROC-006-20:
  `../../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `2026-05-30_02_synthesis_round1.md`, `2026-05-30_04_synthesis_round2.md`,
  `2026-05-31_06_synthesis_round3.md`; feedback `2026-05-30_03_feedback.md`,
  `2026-05-31_05_feedback.md`, `2026-06-01_feedback.md`; restructure plan
  `2026-06-01_07_plan_epic-restructure.md`.
- The original optimizer redesign:
  `../../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).

## Seeds

1. **Event schema & idempotency.** What fields make an event self-describing for both
   selection and later replay? What is the cooldown/dedup-by-target contract per monitor?
2. **Consolidation combiner (R2 D-3).** How are related events collapsed before the
   selector sees them, so a backlog cannot explode (the 247-event symptom)?
3. **Queue ceiling & pruning.** What is the ceiling, and what is the right
   consume-then-delete + stale-prune policy?
4. **Trajectory logging (R3 §5.2).** What must be logged so real tasks can be replayed
   by the simulation harness and statistical contract?
5. **The `skills_used:` Stage-2 gap.** Reconcile the `*_protocol.md`-only trigger.

## Execution Model

Gather raw material — read `scripts/optimize/`, the monitors, `.factory/optimize/`, the
placeholder requirement — then synthesize iteratively. The session model is fixed at
launch (Opus, since `opus_recommended: true`). End by running `requ-explore` to write
REQ-PROC-006-01 (lift it out of `placeholder`).

**Web research**: delegate to a spawned `general-purpose` agent with a focused question;
never run WebSearch inline. Frame queries as questions.

## Output

A synthesis in `plans_and_protocols/` and a filled feature requirement
(REQ-PROC-006-01) with testable acceptance criteria, honest about residual uncertainty.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The feature requirement REQ-PROC-006-01 is written via requ-explore (no longer a placeholder)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. Subordinate to product delivery (G-INV-5). |
</content>
