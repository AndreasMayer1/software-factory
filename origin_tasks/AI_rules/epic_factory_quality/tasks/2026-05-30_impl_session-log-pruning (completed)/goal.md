---
task_id: TASK-PROC-044-14
type: impl
parent_requirement: REQ-PROC-044
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-30T14:08:25Z
effort: S
created: 2026-05-30
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Add --prune-days N flag (default 30) to aggregate_read_metrics.py; prune session dirs whose most recent JSONL timestamp predates the retention window at script start before aggregation"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 2c998857
  file: ../requirements.md
session_id: c5896da0-0d64-4b1a-bf64-7d7f8bc6fe68
session_account: web

---
# Goal: Session Log Pruning (AC-07)

## Objective

Add a `--prune-days N` flag (default: 30) to `scripts/factory/aggregate_read_metrics.py`
that deletes session directories under `.factory/session_logs/` whose most recent JSONL
record timestamp predates the retention window. Pruning runs at script start, before
aggregation, so only in-window sessions contribute to the heat overlay and optimizer events.

## Requirements Summary

REQ-PROC-044 AC-07: session read-event logs are bounded in age; logs older than the
configured retention window (default: 30 days) are pruned at each aggregator run.

For complete requirements at task creation time:
```
git show 2c998857:requirements_tasks/process/AI_rules/factory_quality/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- `--prune-days N` CLI flag on `aggregate_read_metrics.py` (default: 30)
- Prune entire session directory (all files under `.factory/session_logs/<uuid>/`) when the
  most recent `timestamp` field across all JSONL records in that session predates the window
- Pruning runs before aggregation (at script start)
- Fail-safe: sessions with no parseable timestamps are retained, not deleted
- Silent no-op when no sessions fall outside the window (no warning, no output)
- Update `scripts/tests/test_aggregate_read_metrics.py` with pruning tests

### Out of Scope

- Pruning individual records within a session (prune whole dir or nothing)
- Keying on filesystem `mtime` (unreliable in WSL2/container — use JSONL timestamps only)
- Pruning from hooks (PreToolUse/PostToolUse) — only the aggregator script may prune
- Any change to the session log hooks in `.claude/settings.json`

## Acceptance Criteria

- [x] `--prune-days N` flag exists; default is 30; `--help` documents it
- [x] Running the aggregator with `--prune-days 30` deletes session dirs whose newest timestamp is > 30 days old, and leaves all others intact
- [x] Session dirs with no parseable `timestamp` field in any JSONL record are retained (fail-safe)
- [x] No output or warning is produced when no sessions need pruning
- [x] Pruning occurs before aggregation (a pruned session does not appear in the aggregate output)
- [x] Existing tests pass; new tests cover: prune-eligible sessions removed, in-window sessions kept, no-timestamp fail-safe, prune-before-aggregate ordering
- [x] Python quality gates pass (`scripts/quality/check_python_gates.sh`)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-09 | completed | aggregate_read_metrics.py exists; this task extends it |

## Notes

Standalone override applied: AC-07 is the only uncovered AC in REQ-PROC-044 (AC-01–06 are
all covered by existing tasks). Redirect to task-derive-from-requ would produce only this
single task, so override is appropriate.

Key design decisions from REQ-PROC-044 §6 Developer Guidelines:
- Timestamp key: most recent `timestamp` field across all JSONL records in the session
- Granularity: whole session directory, not individual records
- Fail-safe: no-parseable-timestamp → retain
- Silent no-op: no output when nothing to prune
- Do NOT use filesystem mtime
