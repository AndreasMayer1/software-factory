---
task_id: TASK-PROC-006-05-01
type: explore
parent_requirement: REQ-PROC-006-05
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
scope_description: "Deepen feature feat_guardrails_and_budgets per the approved epic plan, then fill its feature requirement (REQ-PROC-006-05) via requ-explore."
release_description: ""
effort: L
created: 2026-06-01
opus_recommended: true   # reason: cross-cutting explore that writes a feature requirement; safety/anti-reward-hacking judgment
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 74dfea86
  file: ../requirements.md
---

# Goal: Deepen & Write the Guardrails / Budgets Feature Requirement

## Objective

Deepen this feature per the approved epic plan, then fill the feature requirement
(REQ-PROC-006-05, currently a `placeholder`) via `requ-explore`. Do for *this feature*
what TASK-PROC-006-20 did for the whole system.

Open questions: how is the weekly session-byte budget made deterministic and
shared-CCS-authoritative (G-INV-4); how is meta-work subordination enforced (G-INV-5);
what is the complete deny-list (incl. scenario-set protection); and where exactly is the
meta-recursion boundary — the optimizer tunes dials, never the ruler?

## Background

This feature holds the standing constraints that keep the loop honest and subordinate.
G-INV-1/2/3 are *stated* in the epic as cross-feature invariants; their enforcement
detail lives here, and this feature defines the proposed G-INV-4/5. The weekly byte
budget here must compose with the per-skill simulation sub-budget owned by
feat_evaluation_simulation_harness.

Current requirements: ../requirements.md

For complete requirements at task creation time:
```
git show 74dfea86:requirements_tasks/process/AI_rules/workflows/epic_workflow_improvement_automation/feat_guardrails_and_budgets/requirements.md
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

1. **G-INV-4 — session-byte weekly budget (soft start-gate).** The developer named
   ~4 MB/week; the authoritative counter is shared-CCS. Make it deterministic. How does
   a *soft* start-gate behave when the budget is exhausted?
2. **G-INV-5 — meta-work subordination.** Bugfix/product tasks always precede
   optimization; optimizer-produced tasks enter the queue subordinate to delivery.
3. **Budget composition (round-4).** The weekly byte budget (this feature) and the
   per-skill simulation sub-budget (feat_evaluation_simulation_harness) must compose.
4. **Deny-list.** Complete it (incl. scenario-set protection); define the periodic
   human-review cadence. G-INV-1 makes a stale deny-list tolerable.
5. **Meta-recursion boundary.** Optimizer tunes dials (thresholds, cadences), never the
   ruler (audit rubric, quality gates, evaluation surface) — the system-level G-INV-3.

## Execution Model

Gather raw material — read the optimizer implementation, the deny-list, the CCS budget
sources, the placeholder requirement — then synthesize iteratively. The session model is
fixed at launch (Opus). End by running `requ-explore` to write REQ-PROC-006-05.

**Web research**: delegate to a spawned `general-purpose` agent with a focused question
(e.g. *"how do self-improving agent loops bound meta-work so it cannot starve primary
work?"*); never run WebSearch inline.

## Output

A synthesis in `plans_and_protocols/` and a filled feature requirement
(REQ-PROC-006-05) with testable acceptance criteria, honest about residual uncertainty.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The feature requirement REQ-PROC-006-05 is written via requ-explore (no longer a placeholder)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. Subordinate to product delivery (G-INV-5). |
</content>
