---
id: REQ-PROC-006-05
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

# Feature: Guardrails & Budgets

> **Status: placeholder.** Created during the REQ-PROC-006 epic restructure
> (2026-06-01); detailed design and testable ACs are filled by its exploration
> task (see References). Content below is the seam definition plus the
> guardrail/deny-list detail moved down from the old single-requirement REQ-PROC-006.

## Overview

The standing constraints that keep the loop honest and subordinate: the weekly
session-byte budget start-gate, meta-work subordination, the write-surface
deny-list, and the meta-recursion boundary. The cross-feature invariants
G-INV-1/2/3 are *stated* in the epic; their enforcement detail lives here, and
this feature defines the proposed G-INV-4/5.

## Scope

Owns: the **session-byte budget start-gate** (G-INV-4, soft, shared-CCS-authoritative),
**meta-work subordination** (G-INV-5), the **deny-list** (incl. scenario-set
protection), and the **meta-recursion boundary** (optimizer tunes dials, never the
ruler). G-INV-1/2/3 are stated in the epic but their enforcement detail lives here.

## G-INV-4 / G-INV-5 (proposed — for the exploration to make measurable)

- **G-INV-4 — Session-byte weekly budget, soft start-gate.** Meta-work draws on a
  weekly byte budget (the developer named ~4 MB/week); the authoritative counter is
  shared-CCS. When the budget is exhausted, the optimizer's *start* is soft-gated.
  Must be made deterministic (G-INV-3 spirit). Composes with the **per-skill
  simulation budget** owned by feat_evaluation_simulation_harness.
- **G-INV-5 — Meta-work subordination.** The optimizer must never starve product
  delivery. Bugfix/product tasks always precede optimization work; optimizer-produced
  tasks enter the normal queue subordinate to product delivery.

## Write-Surface Deny-List (moved from epic)

Defense-in-depth measure preventing claude-optimize from producing tasks that target
the factory's evaluation surface. Enforced programmatically at task-creation time.
Auto-block (G-INV-1) is the primary control; the deny-list prevents obviously invalid
proposals from reaching the user's review queue.

Minimum deny-list:
- `.claude/skills/claude-optimize/skill.md` (self-modification)
- `.claude/skills/verify-quality/skill.md` (quality gate enforcer)
- `.claude/skills/task-complete/skill.md` (loop closer)
- `.claude/skills/claude-modify-skill/skill.md` (immediate enforcer)
- `scripts/quality/**` (quality gate scripts)
- `analysis_options.yaml` (analyzer configuration)
- `.claude/factory_flows.md` (system manifest)
- `.claude/skills/INDEX.md` (skill registry)

The deny-list requires periodic human review as the factory evolves. G-INV-1 makes a
stale deny-list tolerable — even proposals targeting unlisted sensitive paths require
manual unblocking. This feature also protects the **scenario sets** (see
feat_evaluation_simulation_harness): once created, scenarios are deny-listed against
editing.

## Meta-Recursion Boundary

The optimizer may tune **dials** (thresholds, cadences, cooldowns) but must never
modify the **ruler** — the audit rubric, the quality gates, or anything on the
evaluation surface. This is the structural expression of G-INV-3 at the system level.

## References

- Epic: [`../requirements.md`](../requirements.md) (REQ-PROC-006).
- Iteration history (read for the whole picture): the holistic re-alignment task
  `../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`.
- Original design exploration:
  `../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).
</content>
