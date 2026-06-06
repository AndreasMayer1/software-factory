---
date: 2026-05-30
type: synthesis
round: 1
agent_id: 503d573f-8993-4be1-b861-478671205182
skills_used:
  - claude-automated-mode
  - claude-route
  - requ-explore
  - task-complete
  - claude-commit
---

# Synthesis Round 1: Optimizer Improvement from Factory-Quality Instrumentation

## Problem Space (refined from task creation)

At task creation, the problem was framed as an apparent contradiction: `aggregate_read_metrics.py` reads session JSONL, yet REQ-PROC-006 AC-02 forbids monitors from doing so. This framing turned out to be the wrong unit of analysis. The actual problem is a **producer taxonomy gap** — the optimizer's event model knows only one producer class (monitors), but a second class now exists (`aggregate_read_metrics.py`) with different invocation semantics, different data access patterns, and no formal classification in the requirement.

This synthesis identifies six concrete findings, makes authoritative recommendations for all of them, and flags the one decision that genuinely requires user input.

---

## Key Findings

### F1 — aggregate_read_metrics.py is not a monitor

**Monitors** (the existing class in REQ-PROC-006's taxonomy):
- Invoked automatically after every `task-complete` via `run_monitors.py`
- Read committed, project-local sources only (git history, runs.tsv, question fingerprints)
- Never read session JSONL

**aggregate_read_metrics.py** (new class, no name yet):
- CLI tool, requires explicit invocation with `--emit-events` flag
- Reads `.factory/session_logs/*/read_events.jsonl`
- Produces events to the same `.factory/optimize/events/` queue
- Designed for periodic on-demand use, not after-every-completion

This is a fundamentally different class. REQ-PROC-006 has no name for it, no taxonomy entry, and no invocation spec. The requirement needs a new producer class defined.

**Proposed name**: "aggregator" (distinct from monitor; aggregates cross-session signals on demand).

### F2 — Session logs are project-local, not account-local

The old rationale in REQ-PROC-006 Common Pitfalls ("account-local; defeats the project-local-state principle") was written before TASK-PROC-044-09 shipped. The PreToolUse/PostToolUse Read hooks now write to `.factory/session_logs/${CLAUDE_SESSION_ID}/read_events.jsonl` — inside the project tree, committed alongside other factory state. The `account-local` concern is **obsolete**.

This has two consequences:
1. The Common Pitfalls entry is now misleading — it characterizes session JSONL reads as inherently problematic, but the problem was always fragility and account-locality, both of which are resolved.
2. AC-02's "no monitor reads session JSONL" is technically accurate (the aggregator is not a monitor), but the surrounding text creates confusion.

### F3 — high_read_file is absent from the Monitor Taxonomy (SEC-01)

The Monitor Taxonomy table in REQ-PROC-006 lists four event types:
`repeated_question`, `skill_change_reverted`, `skill_changed_and_used`, `periodic`.

`high_read_file` is not in the table. An operator reading the taxonomy would not know this event type exists or where it comes from.

### F4 — high_read_file falls through to "alignment" in select_candidate.py

`scripts/optimize/select_candidate.py` `classify()` (line 155) maps unknown event types to `("optimization", DIMENSION_ALIGNMENT)`. `high_read_file` events silently get `dimension=alignment`.

`alignment` means "skill is out of alignment with its documented behavior." For a frequently-read skill file the correct interpretation is that **caching would reduce token cost** — not that the skill is behaviorally misaligned. For large files or multi-session references, the right dimension is restructuring for read efficiency.

The catch-all behavior does not crash the optimizer, but it produces misleading produced tasks: the improvement goal says "alignment" but the event payload suggests "cache this skill" or "split this doc." An implementer following the task as produced would work on the wrong thing.

### F5 — AC-07 pruning is not yet implemented in aggregate_read_metrics.py

REQ-PROC-044 AC-07 (text and Developer Guidelines) specifies in detail how pruning must work:
- Prune at aggregator run start, before aggregation
- Remove entire session directory (not individual records)
- Key on most recent `timestamp` across all JSONL records in the session
- Default: 30 days; configurable via `--prune-days N`
- Fail-safe: retain sessions with no parseable timestamps

Inspecting `aggregate_read_metrics.py`: no pruning code exists. The script reads all session logs unconditionally. This means:
1. Stale optimizer signals (dead file paths) can trigger `high_read_file` events
2. Inflated session counts from old sessions produce spurious "reference" candidates
3. Already-restructured files continue appearing as candidates

AC-07 is a defined, non-controversial requirement. Implementation is clear and fully spec'd. No user decision needed.

### F6 — TASK-PROC-006-14 scope was a placeholder

TASK-PROC-006-14's objective ("extend monitors or add tier-0 source") was written as a placeholder before the upstream schema was known. Now that `aggregate_read_metrics.py` exists and is fully implemented (modulo pruning), the task scope needs to be rewritten to target the specific integration gaps:

1. Add `high_read_file` to `select_candidate.py` classify()
2. Add aggregator invocation to `run_monitors.py` (rate-limited)
3. Patch REQ-PROC-006 (taxonomy, AC-02, Common Pitfalls)
4. Implement AC-07 pruning in `aggregate_read_metrics.py`

The current scope covers item 3 via "AC-02" in `covers.acceptance_criteria`. Items 1, 2, and 4 are not covered. TASK-PROC-006-14 should be re-scoped to include all four.

---

## Recommendations

### R1 — Add "Aggregator" producer class to REQ-PROC-006

Extend the Monitor Taxonomy section (or create a new "Event Producer Taxonomy" section) to include:

| Producer | Type | Signal | Confidence | Event Type |
|---|---|---|---|---|
| `aggregate_read_metrics.py` | aggregator | File read-frequency across sessions | Medium | `high_read_file` |

Aggregator characteristics to document:
- Invoked on demand (not post-task-complete)
- Reads `.factory/session_logs/` (project-local)
- Rate: configurable; recommended every N task completions (see R3)
- Must implement AC-07 pruning before emitting events

### R2 — Patch AC-02 and Common Pitfalls in REQ-PROC-006

**AC-02 proposed revision** (minimal, backward-compatible):

Current:
> Candidate events are detected by pure-Python monitor scripts that execute after every task-complete invocation; no monitor reads session JSONL in routine operation

Proposed:
> Candidate events are produced by two classes of producer: (1) monitor scripts that execute after every task-complete invocation and read only committed, project-local sources — no monitor reads session JSONL; (2) aggregator scripts invoked on demand that may read project-local session logs under `.factory/session_logs/` to derive cross-session signals. Aggregators are not invoked in the post-task-complete critical path.

**Common Pitfalls proposed revision**:

Current pitfall:
> Letting the optimizer read session JSONL in routine operation (expensive, fragile, account-local; defeats the project-local-state principle)

Proposed replacement:
> Running session JSONL aggregation synchronously in the post-task-complete critical path — the aggregator is on-demand and rate-limited, not a real-time hook. Session logs under `.factory/session_logs/` are project-local; reading them is safe but expensive. The rate-limiting rule exists to keep post-task-complete hooks fast (<2 s total).

### R3 — Add rate-limited aggregator invocation to run_monitors.py

The simplest integration that preserves G-INV-2 (detection outside agents): add a conditional call to `aggregate_read_metrics.py --emit-events` at the end of `run_monitors.py`.

Rate-limit rule: invoke the aggregator only when `state.json`'s `completions_since_last_run` >= configurable threshold (suggested default: 5). Read `state.json` at run_monitors.py start; if threshold is met, call the aggregator.

Why `completions_since_last_run` (not a separate counter): `completions_since_last_run` is already maintained by the task-complete hook and reset by claude-optimize on each run. Using it avoids adding another counter.

Why 5 (not 10 which is the periodic monitor threshold): High-read events are less time-sensitive than the periodic trigger; 5 completions gives a reasonable signal window without over-sampling.

This is a design decision, but the rationale is self-contained. TASK-PROC-006-14 implementer can proceed with this unless the user overrides.

### R4 — Implement AC-07 pruning in aggregate_read_metrics.py

The spec in REQ-PROC-044 §6 Developer Guidelines is fully prescriptive. No design decisions needed. Add a `prune_old_sessions(logs_root, prune_days)` function that:
1. Iterates session directories in `logs_root`
2. Parses all JSONL records to find the most recent `timestamp`
3. Removes the entire session directory if `most_recent_timestamp < now - prune_days`
4. Retains sessions with no parseable timestamps (fail-safe)

Call it at the start of `aggregate_logs()`, before any reads. Expose `--prune-days N` CLI flag (default: 30).

### R5 — Update select_candidate.py classify() for high_read_file

Add `high_read_file` case before the catch-all. Map based on optimization_candidates in the payload:

```python
if et == "high_read_file":
    candidates = event.payload.get("optimization_candidates", [])
    if "cache" in candidates:
        return ("optimization", "token_cost")
    return ("optimization", DIMENSION_CLARITY)
```

Rationale:
- "cache" → `token_cost`: the suggested action is to restructure for prompt caching; the metric is token savings
- "section" or "reference" → `clarity`: the suggested action is to split large docs or use schema references; the metric is read efficiency/clarity
- Falling through to `alignment` is wrong for this event type

`token_cost` is already in SEC-02's dimension set. No new vocabulary needed.

### R6 — TASK-PROC-006-14 re-scope

Re-scope TASK-PROC-006-14 `scope_description` to:
> "Integrate high_read_file events into the optimizer pipeline: (1) implement AC-07 pruning in aggregate_read_metrics.py, (2) add rate-limited aggregator invocation to run_monitors.py, (3) update select_candidate.py to classify high_read_file correctly, (4) patch REQ-PROC-006 Monitor Taxonomy, AC-02, and Common Pitfalls to document the aggregator producer class."

Update `covers.acceptance_criteria` to include: AC-02 (already there), AC-01 (aggregator produces verifiable events), AC-09 (pruning ensures state is bounded).

---

## One Open Decision (D1)

### D1 — Aggregator invocation trigger: run_monitors.py vs. separate hook

R3 above recommends adding the aggregator call to `run_monitors.py` with rate-limiting. An alternative is to invoke it via a separate post-task-complete hook entry.

**Option A (recommended): In run_monitors.py** — simple, no new hook, reuses existing state.json counter, rate-limit logic is auditable Python.

**Option B: Separate hook entry** — cleaner separation of concerns; aggregator invocation is visible in settings.json alongside other hooks; but requires a new invocation mechanism and adds hook complexity.

The recommendation is Option A. If the user prefers Option B for architectural cleanliness, that's a valid override; document the decision in the task plan for TASK-PROC-006-14.

---

## What Remains Uncertain

1. **select_candidate.py edge case**: The `high_read_file` payload can contain all of `["cache", "section", "reference"]` simultaneously. R5 checks `"cache" in candidates` first. Whether this priority (cache > section > reference) is correct depends on how much the user values token savings vs. structural clarity. Low-confidence choice; easy to override by an implementer.

2. **AC-07 threshold**: REQ-PROC-044 specifies 30 days as default. The optimizer's event prune window is also 30 days. These being equal is correct per the requirement, but it means a session from day 29 gets aggregated once and then pruned. No ambiguity, but worth noting for future tuning.

3. **Idempotency of aggregator events**: Unlike monitors (which have explicit cooldown windows), the aggregator currently has no deduplication. If called N times before claude-optimize runs, it writes N events for the same file. TASK-PROC-006-14 implementer should add a fingerprint-based deduplication check consistent with the monitor pattern (see `monitor_common.py`).

---

## Summary

| Item | Type | Definitive? | Owner |
|---|---|---|---|
| Add aggregator producer class to REQ-PROC-006 taxonomy | Requirement patch | Yes | TASK-PROC-006-14 |
| Patch AC-02 text | Requirement patch | Yes (text above) | TASK-PROC-006-14 |
| Patch Common Pitfalls | Requirement patch | Yes (text above) | TASK-PROC-006-14 |
| Add high_read_file row to Monitor Taxonomy | Requirement patch | Yes | TASK-PROC-006-14 |
| Implement AC-07 pruning in aggregate_read_metrics.py | Code impl | Yes | TASK-PROC-006-14 |
| Add rate-limited aggregator to run_monitors.py | Code impl | Yes (R3) | TASK-PROC-006-14 |
| Update select_candidate.py classify() | Code impl | Yes (R5) | TASK-PROC-006-14 |
| Re-scope TASK-PROC-006-14 | Task metadata | Yes | This task output |
| Aggregator invocation: run_monitors.py vs. separate hook | Architecture decision | D1 — user input welcome | Developer |
