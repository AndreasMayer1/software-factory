---
id: REQ-PROC-006-07
status: draft
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
effort: L
stakeholder: developer
created: 2026-06-01
updated: 2026-06-01
parent: REQ-PROC-006
after: []
blocks: []
market_research_refs: [] # No relevant findings identified — internal process tool
trackable_items:
  acceptance_criteria: []
  sections: []
---

# Feature: Self-Optimization Experiment

> **Status: placeholder.** Created during the REQ-PROC-006 epic restructure
> (2026-06-01); detailed design and testable ACs are filled by its exploration
> task (see References).

## Overview

A bounded, developer-witnessed experiment to demonstrate that the optimizer can
*measurably* improve toward its targets — by running on itself at higher cadence
while it is young — under a hard kill-switch. Distinct from the standing
guardrails (those are permanent; this is a time-boxed activity).

## Scope

Owns: the **two staged, developer-witnessed test runs** (drain&baseline, then
optimizer-on-itself), **OEC + auto-abort guardrails**, the experiment's
kill-switch. A bounded activity, distinct from the standing guardrails in
feat_guardrails_and_budgets.

## Notes for the exploration task

- **Stage 1 — drain & baseline.** Drain the event backlog and establish a baseline
  reading of the target metrics (feat_targets_metrics_audit) before any self-tuning.
- **Stage 2 — optimizer-on-itself.** Run the loop at higher cadence against itself,
  measured by `claude-optimize-audit` plus the new target metrics, with explicit
  success/failure criteria.
- **OEC (Overall Evaluation Criterion) + auto-abort.** Define the composite metric the
  experiment optimizes and the auto-abort conditions (regression, drift, budget burn).
- **Hard token kill-switch.** The experiment must not blow the weekly byte budget
  (G-INV-4, feat_guardrails_and_budgets); a deterministic kill-switch terminates it.
- Witnessed by the developer; subordinate to product delivery (G-INV-5).

## References

- Epic: [`../requirements.md`](../requirements.md) (REQ-PROC-006).
- Iteration history (read for the whole picture): the holistic re-alignment task
  `../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`.
- Original design exploration:
  `../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).
</content>
