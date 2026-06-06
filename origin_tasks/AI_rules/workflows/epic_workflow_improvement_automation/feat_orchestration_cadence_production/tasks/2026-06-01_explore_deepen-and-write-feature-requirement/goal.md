---
task_id: TASK-PROC-006-06-01
type: explore
parent_requirement: REQ-PROC-006-06
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
scope_description: "Deepen feature feat_orchestration_cadence_production per the approved epic plan, then fill its feature requirement (REQ-PROC-006-06) via requ-explore."
release_description: ""
effort: L
created: 2026-06-01
opus_recommended: true   # reason: cross-cutting explore that writes a feature requirement; orchestration redesign judgment
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 74dfea86
  file: ../requirements.md
---

# Goal: Deepen & Write the Orchestration / Cadence / Production Feature Requirement

## Objective

Deepen this feature per the approved epic plan, then fill the feature requirement
(REQ-PROC-006-06, currently a `placeholder`) via `requ-explore`. Do for *this feature*
what TASK-PROC-006-20 did for the whole system.

Open questions: how does the subordinate autonomous trigger work (the reversed F-1, not
preempt-all); how is the activity-gated weekly cadence implemented
(`last_self_run_iso_week`); what is the producer skill's contract; and how does
ranked-batch consumption with a proposal cap/digest replace one-event-per-cycle so a
backlog cannot dominate the queue?

## Background

This feature owns how and when the loop runs. The placeholder requirement carries the
producer paradigm, candidate-selection priority, the two-field taxonomy, the web-research
heuristics, and commit behavior — all moved down from the old epic. F-1's first
implementation is held in `git stash` and documented in TASK-PROC-006-18's protocol —
treat it as a starting artifact for the reversed (subordinate) trigger, not a settled
answer.

Current requirements: ../requirements.md

For complete requirements at task creation time:
```
git show 74dfea86:requirements_tasks/process/AI_rules/workflows/epic_workflow_improvement_automation/feat_orchestration_cadence_production/requirements.md
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

1. **Subordinate autonomous trigger (reversed F-1).** Not preempt-all — it respects
   G-INV-5 (meta-work subordination). How does it queue rather than preempt?
2. **Activity-gated weekly cadence (round-4 developer input).** The developer accepted
   the `last_self_run_iso_week` recommendation — *"let's not over-engineer it."* The
   date-aware `awaits` field is dropped for now.
3. **Producer skill.** The `claude-optimize` contract: consume → pick → produce one →
   commit; never executes the improvement itself.
4. **Ranked-batch consumption + proposal cap/digest.** Replace one-event-per-cycle so a
   backlog cannot dominate the queue (the 247-event symptom).

## Execution Model

Gather raw material — read `scripts/optimize/`, the `claude-optimize` skill, the F-1
stash + TASK-PROC-006-18 protocol, `.factory/optimize/`, the placeholder requirement —
then synthesize iteratively. The session model is fixed at launch (Opus). End by running
`requ-explore` to write REQ-PROC-006-06.

**Web research**: delegate to a spawned `general-purpose` agent with a focused question
(e.g. *"how do autonomous task queues schedule low-priority background work without
starving foreground work?"*); never run WebSearch inline.

## Output

A synthesis in `plans_and_protocols/` and a filled feature requirement
(REQ-PROC-006-06) with testable acceptance criteria, honest about residual uncertainty.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The feature requirement REQ-PROC-006-06 is written via requ-explore (no longer a placeholder)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. Subordinate to product delivery (G-INV-5). |
</content>
