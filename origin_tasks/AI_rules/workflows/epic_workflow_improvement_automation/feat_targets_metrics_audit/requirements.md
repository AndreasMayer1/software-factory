---
id: REQ-PROC-006-02
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

# Feature: Targets, Metrics & Audit

> **Status: placeholder.** Created during the REQ-PROC-006 epic restructure
> (2026-06-01); detailed design and testable ACs are filled by its exploration
> task (see References). Content below is the seam definition plus the
> targets/audit detail moved down from the old single-requirement REQ-PROC-006.

## Overview

"What the loop aims at" and "how the loop is scored" as one measurement concern:
the three-layer target model (north-star + leading indicators + guardrail
pointers) and the audit skill that scores effectiveness with a deterministic
rubric.

## Scope

Owns: the **three-layer target model** (north-star + GQM leading indicators +
guardrail pointers), AND the **audit skill** + effectiveness metrics + deterministic
rubric (loop-hygiene *and* north-star-laddered halves). Merged because "what to aim
at" and "how the loop is scored" are one measurement concern. Absorbs pending
**TASK-PROC-006-16** (DuckDB optional query layer).

## Effectiveness Metrics and Audit (moved from epic)

The `claude-optimize-audit` skill reports on the optimizer's effectiveness. It is
invoked on user demand, not on a trigger. It is a different skill from `claude-optimize`
(G-INV-3): the producer is never scored within its own run.

**Two metrics:**

1. **User-unblock-rate** (primary, fast-cadence): fraction of produced tasks the
   developer unblocked. Measures engagement and calibration. Target band: 50–80%.
   Computed from `runs.tsv` and `goal.md` `awaiting:` history.
2. **Revert-rate** (secondary, slow-cadence): fraction of unblocked-and-completed
   improvement tasks that were reverted or substantially rewritten within N weeks.
   Measures whether improvements stick. Computed from `git log`. Evaluated on a slower
   cadence (quarterly) due to maturation window.

> Re-alignment note (TASK-PROC-006-20): these two are loop *process-health* metrics.
> This feature must define the three-layer model that ladders **scope-local leading
> indicators** up to the **app-quality** north-star, and split the rubric into a
> loop-hygiene half and a north-star-laddered half.

**Deterministic scoring rubric:** the audit skill computes a reproducible N-point
health score (starting rubric: 10 criteria, refinable from real data). Each criterion
is computed from `runs.tsv` and git history — never from LLM judgment. The score and
its delta vs. the previous run are recorded in `audit_history.tsv`. Sub-audits are
available via `claude-optimize-audit --monitor=<name>`.

> Bug to reconcile (Seed 3, F-3): the audit `--monitor` exit-code behavior.

**Database deferral (v1.5):** Cross-session analytics that require joins over session
JSONL may optionally use DuckDB as a query-time dependency in a future version. DuckDB
reads raw JSONL directly (no ETL, no schema migration, no daemon). JSONL queries are
account-local and best-effort; `runs.tsv` remains the canonical record. DuckDB is
introduced only after the audit skill is built, and only for queries — never as the
canonical store. (Pending TASK-PROC-006-16 implements this layer.)

## References

- Epic: [`../requirements.md`](../requirements.md) (REQ-PROC-006).
- Iteration history (read for the whole picture): the holistic re-alignment task
  `../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`.
- Original design exploration:
  `../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).
- Absorbed task: `tasks/2026-05-28_impl_duckdb-optional-query-layer/` (TASK-PROC-006-16).
</content>
