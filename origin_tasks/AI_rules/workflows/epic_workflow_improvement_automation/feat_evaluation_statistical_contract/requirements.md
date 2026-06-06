---
id: REQ-PROC-006-03
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

# Feature: Evaluation — Statistical Contract

> **Status: placeholder.** Created during the REQ-PROC-006 epic restructure
> (2026-06-01); detailed design and testable ACs are filled by its exploration
> task (see References).

## Overview

The slow, real-signal evaluation modality: how the factory decides — from real
accumulated evidence rather than tasks — whether a landed improvement actually
helped, using anytime-valid statistics and drift detection.

## Scope

Owns: the **slow real-signal evaluation contract**: events-not-tasks
(`min_evidence`), mSPRT/e-value anytime-valid stopping, CUSUM drift, the
pending→verdict lifecycle, attribution + holdback.

## Notes for the exploration task

- The unit of evidence is **events, not tasks** (`min_evidence` threshold before a
  verdict can be reached).
- Use **anytime-valid** stopping (mSPRT / e-values) so the loop can peek at
  accumulating evidence without inflating false-positive rates.
- **CUSUM** drift detection to catch a regression that creeps in after a verdict.
- A **pending → verdict** lifecycle for each landed change, with **attribution**
  (which change caused the measured movement) and a **holdback** so a fraction of
  work bypasses the change to provide a counterfactual.
- This is the slow counterpart to the fast offline simulation harness
  (feat_evaluation_simulation_harness); the two must compose into one verdict story.

## References

- Epic: [`../requirements.md`](../requirements.md) (REQ-PROC-006).
- Iteration history (read for the whole picture): the holistic re-alignment task
  `../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`.
- Original design exploration:
  `../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).
</content>
