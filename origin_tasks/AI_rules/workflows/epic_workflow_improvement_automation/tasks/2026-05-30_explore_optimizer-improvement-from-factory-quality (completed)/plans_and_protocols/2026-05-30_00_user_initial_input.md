---
date: 2026-05-30
type: user_initial_input
---

# User Initial Input

> "create an exploration task with the goal to check how the optimizer can be improved based on the implementation for factory_quality"

Additional context from conversation:

- REQ-PROC-044 TASK-PROC-044-09 shipped `aggregate_read_metrics.py` + PreToolUse/PostToolUse Read hooks writing to `.factory/session_logs/`
- The aggregator reads session JSONL and emits `high_read_file` events to `.factory/optimize/events/`
- REQ-PROC-006 AC-02 says "no monitor reads session JSONL in routine operation" — apparent contradiction
- `high_read_file` event type is absent from REQ-PROC-006's Monitor Taxonomy
- `aggregate_read_metrics.py` is not listed as an event producer in REQ-PROC-006
- TASK-PROC-006-14 (impl, awaiting) exists to "consume TASK-PROC-044 observability data once it lands" — that condition is now met (AC-07 added to REQ-PROC-044, aggregator implemented)
- `.factory/session_logs/` was gitignored as ephemeral local telemetry; REQ-PROC-044 AC-07 added a 30-day retention/pruning policy for the aggregator

Read as a seed bed, not a spec.
