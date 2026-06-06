---
task_id: TASK-PROC-006-14
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-30T12:29:49Z
effort: M
created: 2026-05-28
after: [TASK-PROC-006-17]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02]
  sections: []
scope_description: "Integrate high_read_file events into the optimizer pipeline: (1) implement AC-07 pruning in aggregate_read_metrics.py, (2) add rate-limited aggregator invocation to run_monitors.py (trigger: completions_since_last_run >= 5), (3) update select_candidate.py to classify high_read_file correctly (token_cost for cache candidates, clarity otherwise), (4) patch REQ-PROC-006 Monitor Taxonomy, AC-02, and Common Pitfalls for aggregator producer class. REQ-PROC-006 requirement patches already applied by TASK-PROC-006-17."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-I
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: 98156cc6-e61f-414b-9d11-5c5baa5e0414
session_account: web

---
# Goal: Integrate high_read_file Events into Optimizer Pipeline (IMPL-I)

## Objective

TASK-PROC-006-17 (explore) resolved the architectural questions blocking this task.
`aggregate_read_metrics.py` is fully implemented; the gaps are invocation, correct
dimension classification, and pruning. This task closes those gaps.

## Requirements Summary

Reference: REQ-PROC-006 AC-02 (two-class producer model, patched by TASK-PROC-006-17).
REQ-PROC-044 AC-07 (session log retention/pruning — not yet implemented).

For requirements at task creation time (original):
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md (patched by TASK-PROC-006-17)

## Design Reference

Full synthesis and rationale: `TASK-PROC-006-17/plans_and_protocols/2026-05-30_01_synthesis_round1.md`

Key design decisions from the exploration:
- **Invocation**: add rate-limited aggregator call to `run_monitors.py`; trigger when `state.json`'s `completions_since_last_run >= 5`
- **Dimension mapping**: `high_read_file` → `token_cost` if payload `optimization_candidates` contains `"cache"`, else `clarity`
- **Pruning**: implement per REQ-PROC-044 §6 Developer Guidelines (prune whole session dirs keyed on most-recent JSONL timestamp, configurable `--prune-days`, default 30)
- Open decision D1 in synthesis: `run_monitors.py` vs. separate hook — default to `run_monitors.py` unless developer overrides

## Scope

### In Scope

1. **Pruning** (`scripts/factory/aggregate_read_metrics.py`): implement `prune_old_sessions()` called at `aggregate_logs()` start; expose `--prune-days N` flag (default 30); follow REQ-PROC-044 §6 Developer Guidelines exactly.
2. **Invocation** (`scripts/optimize/run_monitors.py`): add rate-limited call to `aggregate_read_metrics.py --emit-events` when `completions_since_last_run >= 5` from `state.json`. Add event fingerprint deduplication check (consistent with `monitor_common.py` pattern).
3. **Classification** (`scripts/optimize/select_candidate.py`): add `high_read_file` case to `classify()` before the catch-all; map to `(optimization, token_cost)` if `"cache"` in payload candidates, else `(optimization, clarity)`.
4. **Skill sync** (`.claude/skills/claude-optimize/SKILL.md`): update Step 2 classification table to add `high_read_file` row, matching the new `select_candidate.py` code.

### Out of Scope

- Changing the `aggregate_read_metrics.py` aggregation logic beyond pruning.
- Changing the event schema (payload structure, confidence, event_type string).
- Any REQ-PROC-006 requirement text changes (already applied by TASK-PROC-006-17).

## Acceptance Criteria

- [ ] `aggregate_read_metrics.py --emit-events` no longer emits events for session directories whose most-recent JSONL timestamp is older than `--prune-days` (default 30).
- [ ] `run_monitors.py` invokes `aggregate_read_metrics.py --emit-events` when and only when `state.json`'s `completions_since_last_run >= 5`.
- [ ] A `high_read_file` event with `"cache"` in `optimization_candidates` is classified as `(optimization, token_cost)` by `select_candidate.py`.
- [ ] A `high_read_file` event without `"cache"` is classified as `(optimization, clarity)`.
- [ ] G-INV-2 holds: the aggregator is not a callable tool for any agent.
- [ ] No regression: existing four monitors and `run_monitors.py` continue to work unchanged.
- [ ] `aggregate_read_metrics.py` emits no events for duplicate files within a single run (fingerprint deduplication).

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-044-09 | completed | Shipped aggregate_read_metrics.py, session log hooks, high_read_file events |
| TASK-PROC-006-17 | in_progress | Exploration — completes before this task; REQ-PROC-006 patches and design decisions done |

## Notes

Concept docs: round-4 §6 IMPL-I. All architectural questions resolved by TASK-PROC-006-17:
AC-02 contradiction explained (aggregator is not a monitor), producer taxonomy documented,
high_read_file classification defined, invocation strategy confirmed (run_monitors.py with
rate-limiting). This task implements the four concrete changes listed in Scope.
