---
id: REQ-PROC-006-06
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

# Feature: Orchestration, Cadence & Production

> **Status: placeholder.** Created during the REQ-PROC-006 epic restructure
> (2026-06-01); detailed design and testable ACs are filled by its exploration
> task (see References). Content below is the seam definition plus the
> production/selection detail moved down from the old single-requirement REQ-PROC-006.

## Overview

How and when the loop actually runs: the subordinate autonomous trigger (the
reversed F-1 — not preempt-all), the activity-gated weekly cadence, the
task-producer skill, and ranked-batch consumption with a proposal cap/digest.

## Scope

Owns: the **subordinate autonomous trigger** (reversed F-1, not preempt-all), the
**activity-gated weekly cadence** (`last_self_run_iso_week`), the **producer skill**
(`claude-optimize`), **ranked-batch consumption + proposal cap/digest**.

## Producer Paradigm (moved from epic)

claude-optimize consumes candidate events from `.factory/optimize/events/`, selects
the highest-priority candidate (bugfix strictly before optimization), and produces
exactly one of: (1) **an improvement task** — a `goal.md` with
`awaiting: ["user-unblock"]` (G-INV-1), a verifiable acceptance criterion, and an
`optimization_approach` block; or (2) **a no-op** documented in `runs.tsv`. No run
produces more than one downstream task. The skill never executes the improvement —
that is the downstream executor's job (`claude-modify-skill`, `code-bugfix`, …).

### Candidate Selection Priority

1. Bugfix candidates (strictly first; no fairness rule).
2. Optimization candidates (only when no bugfix candidate exists).

Within each class, priority follows trigger confidence: repeated-question (S9) >
skill-change-reverted > skill-change-first-used > periodic.

> Re-alignment note (TASK-PROC-006-20): replace one-event-per-cycle consumption with
> **ranked-batch** consumption plus a **proposal cap / digest**, so a backlog cannot
> dominate the queue (the 247-event symptom). The autonomous trigger is **subordinate**
> (reversed F-1), not preempt-all — it respects G-INV-5.

### Commit Behavior

Every run results in a git commit containing at minimum the updated `runs.tsv` and
`state.json` (no-op runs included). Message: `chore(optimize): run <id> [created|no-op] [<dimension>]`.

### Two-Field Taxonomy (moved from epic)

Each produced task declares two classification fields:

```yaml
optimization_target: skill_body | skill_description | doc_guideline | ordering_rule | hook | script
optimization_dimension: bugfix | alignment | latency | token_cost | safety | clarity | trigger_accuracy | trigger_precision | layer_order | priority_signal | dependency
```

The combination determines the downstream executor skill and the verification
strategy (e.g. `skill_body`+`bugfix` → `claude-modify-skill` with binary verification;
`ordering_rule`+any → `claude-modify-ordering-rules`).

### Web Research Heuristics (moved from epic)

claude-optimize does not perform web research itself. Each produced task carries an
`optimization_approach` block (`web_research_recommended`, `web_research_query`,
`reason`). Heuristic (first match wins):

| Candidate Type | Recommended | Reason |
|---|---|---|
| Internal bugfix (code/skill mismatch, fully in-repo) | No | Answer is in the repo |
| Bugfix involving external dependency (CLI, library, API) | Yes | May be a known upstream issue |
| Skill-description trigger-accuracy improvement | Yes | Anthropic publishes guidance on skill descriptions |
| Skill-body workflow/orchestration redesign | Yes | Rich prior art in agent orchestration |
| Doc guideline rewrite | No | Internal style, no external authority |
| Ordering-rule change | No | Project-specific |

Downstream executors log searches to `.factory/optimize/history/web_searches.tsv`.

## Seeds (round-4 developer input)

- **Weekly trigger:** the developer accepted the activity-gated `last_self_run_iso_week`
  recommendation — *"let's not over-engineer it."* The date-aware `awaits` field is
  dropped for now.

## References

- Epic: [`../requirements.md`](../requirements.md) (REQ-PROC-006).
- Iteration history (read for the whole picture): the holistic re-alignment task
  `../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`.
- Original design exploration:
  `../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).
</content>
