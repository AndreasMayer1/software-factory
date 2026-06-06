---
id: REQ-PROC-006-01
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

# Feature: Detection & Event Pipeline

> **Status: placeholder.** This requirement was created during the REQ-PROC-006
> epic restructure (2026-06-01). Its detailed design and testable acceptance
> criteria are filled by its exploration task (see References) per the approved
> epic plan. The content below is the seam definition plus the detection-level
> detail moved down from the old single-requirement REQ-PROC-006.

## Overview

The detection layer of the optimizer loop: the cheap structural monitors and the
on-demand aggregator that feed candidate events, the event schema and
idempotency, a consolidation combiner, the queue ceiling, and trajectory logging
so real tasks can be replayed by the evaluation features.

## Scope

Owns: the 4 monitors + aggregator, event schema/idempotency, the **consolidation
combiner script** (R2 D-3), per-file granularity, queue ceiling, and **trajectory
logging** so real tasks can be replayed (R3 §5.2).

## Detection Detail (moved from epic)

Detection and selection are separated. Cheap pure-Python monitor scripts run after
every `task-complete` invocation (target: <2 seconds total). Each monitor checks one
structural signal and, on hit, writes a candidate event file to
`.factory/optimize/events/`. The LLM-driven skill runs only when at least one event
exists. Monitors never read session JSONL — they consume committed, project-local
sources: `runs.tsv`, git history, protocol files, question fingerprints. Aggregators
read project-local session logs on demand and are rate-limited to stay outside the
critical post-task-complete path.

### Class 1: Monitors (post-task-complete, cheap)

Invoked automatically by `run_monitors.py` after every `task-complete`. Read only
committed, project-local sources. Never read session JSONL. Target: <2 seconds total.

| Monitor | Signal | Confidence | Event Type |
|---|---|---|---|
| `monitor_repeated_question.py` | Same pending-question fingerprint repeated ≥3 times | High | `repeated_question` |
| `monitor_skill_change_reverted.py` | Skill file edited then substantially undone within 48 hours | High | `skill_change_reverted` |
| `monitor_skill_change_first_use.py` | Skill file edited AND subsequently used in a session (Stage 2); skill file edited alone (Stage 1) | Medium / Low | `skill_changed_and_used` |
| `monitor_periodic_counter.py` | N completed tasks since last optimize run (default N=10, configurable in `state.json`) | Low | `periodic` |

All monitors are idempotent: they refuse to write a duplicate event for the same
trigger within a cooldown window (14 days for repeated-question, configurable for
others). The skill-change-first-use monitor operates in two stages: Stage 1 fires on
skill-file commits alone (higher false-positive rate); Stage 2 fires only after
protocol-level `skills_used:` evidence confirms the changed skill was exercised. Both
stages are valid operational modes.

> Known gap to reconcile (R3 / TASK-PROC-006-20 Seed 3): the Stage-2 `skills_used:`
> trigger in `task-complete` step 3.4b only fires on `*_protocol.md`, silently
> skipping other `plans_and_protocols/` filenames.

### Class 2: Aggregators (on-demand, expensive)

Invoked periodically from `run_monitors.py` when `completions_since_last_run` reaches
a configured threshold (default: 5). Read `.factory/session_logs/` (project-local
session JSONL). Must implement AC-07 pruning (REQ-PROC-044) before emitting events.
Not invoked on every task-complete — rate-limiting is mandatory to keep the
post-task-complete path fast.

| Aggregator | Signal | Confidence | Event Type |
|---|---|---|---|
| `scripts/factory/aggregate_read_metrics.py` | File read-frequency across sessions exceeds threshold (default: 5 reads); candidates include `cache`, `section`, `reference` actions in payload | Medium | `high_read_file` |

Aggregator events include an `optimization_candidates` field in the payload listing
suggested action types. `select_candidate.py` maps `high_read_file` events to
`token_cost` dimension when `cache` is in candidates, and `clarity` otherwise.

### Event Lifecycle

The `events/` folder uses a consume-then-delete lifecycle to bound storage. Stale
events older than 30 days are pruned at run start. The design must add a queue ceiling
and consolidation combiner to prevent the unbounded accumulation seen in production
(247 queued events).

## References

- Epic: [`../requirements.md`](../requirements.md) (REQ-PROC-006).
- Iteration history (read for the whole picture): the holistic re-alignment task
  `../../tasks/2026-05-30_explore_holistic-optimizer-analysis-and-target-realignment/plans_and_protocols/`
  — syntheses `_02`/`_04`/`_06`, feedback `_03`/`_05`/`_06-01`, restructure plan `_07`.
- Original design exploration:
  `../../tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
  (rounds 1–4 + decisions log).
</content>
