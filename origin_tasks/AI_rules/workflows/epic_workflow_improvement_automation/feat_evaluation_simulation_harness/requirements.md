---
id: REQ-PROC-006-04
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

# Feature: Evaluation — Simulation Harness

> **Status: placeholder.** Created during the REQ-PROC-006 epic restructure
> (2026-06-01); detailed design and testable ACs are filled by its exploration
> task (see References).

## Overview

The fast, offline evaluation modality: rerun a candidate skill change against
recorded/derived test data to get a verdict before any real-signal accumulation,
using paired old-vs-new comparison over managed scenario sets.

## Scope

Owns: the **fast offline verdict**: skill-creator paired old-vs-new, scenario sets,
**Git-branch test-data management + cleanup + naming** (R4 seed), **held-out 60/40
split**, **synthetic-only-from-real** (R4 seed), the **dynamic per-skill simulation
budget** (R4 seed), scenario-set deny-list + add/deprecate lifecycle (R4 seed).

## Seeds (round-4 developer inputs — carry into the exploration)

- **Git-branch test-data sets.** Real logged tasks become test datasets pointed to by
  dedicated **git branches**, so any commit/dataset can be checked out and re-run.
  Needs: a **cleanup mechanism** and a **naming convention** that makes clear which
  branches are disposable vs must-keep. Same mechanism for synthetic datasets.
- **Synthetic-only-from-real.** Never synthesize test data "from nothing." First
  collect a **real** dataset; derive synthetic data *from* it. (Bounds R3 §5.3 / the
  web research's "replay-first, synthesize-for-gaps" — the developer is stricter:
  synthetic must be *derived from* real, not invented.)
- **Simulation cost is dynamic, per-skill.** Iterative/feedback skills → simulate
  **one iteration**. Token-heavy skills (e.g. scribble generation emitting many HTML
  files) cost far more. Approach: **first simulation of a skill runs UN-budgeted and
  is measured** to establish a per-skill baseline; thereafter allow ~**3 iterations**
  as a starting cap, adapt up/down from the measured baseline. This is a **separate
  simulation budget**, distinct from the 4 MB weekly meta-work budget (owned by
  feat_guardrails_and_budgets); the two must compose.
- **Scenario deny-list lifecycle.** Once created, a scenario is **deny-listed** (can't
  be edited). But there must be a **tamper-resistant** mechanism to *add* new
  scenarios and *deprecate/delete* old ones — "a mechanism that cannot be tricked
  easily." (Open design problem — flagged, not solved.)
- **Held-out 60/40 split** of the scenario/test data so the loop is not scored on data
  it tuned against.

## References

- Epic: [`../requirements.md`](../requirements.md) (REQ-PROC-006).
- Iteration history (read for the whole picture): the holistic re-alignment task
  `../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`.
- Original design exploration:
  `../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).
</content>
