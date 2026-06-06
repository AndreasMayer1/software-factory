---
task_id: TASK-PROC-006-15
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-05-28
after: [TASK-PROC-006-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03, AC-11]
  sections: [SEC-03]
scope_description: "Instrument the downstream executor surface (claude-log or executor skills themselves) to append one row per performed web search to .factory/optimize/history/web_searches.tsv. Append-only, never pruned."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-J
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-28T18:51:45Z
session_id: 25b37fd7-e29f-4ee7-9d2c-7ceb73976241
session_account: gmail2
---
# Goal: `web_searches.tsv` Instrumentation (IMPL-J)

## Objective

Log every web search performed by downstream executor tasks so the audit skill
(IMPL-G) can evaluate the SEC-03 web-research heuristics empirically over time.
The instrumentation lives at the call site of the search (claude-log or the
executor skills) — not inside claude-optimize itself.

## Requirements Summary

Reference: REQ-PROC-006 §"Web Research Heuristics" (SEC-03) — "Downstream
executor skills log performed searches to `.factory/optimize/history/web_searches.tsv`"
(commit eabdeaf0). The audit skill (IMPL-G / TASK-PROC-006-12) consumes this
file.

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Append one row per performed web search to `.factory/optimize/history/web_searches.tsv`.
- Row format (TSV columns): `timestamp\ttask_id\tquery\trecommended_by_optimization_approach`.
  - `recommended_by_optimization_approach` is `true` if the produced task's `optimization_approach.web_research_recommended` was `true`; `false` otherwise.
- Instrumentation lives in the downstream executor surface — pick the surface that already sees every search (claude-log or the executor skills' WebSearch/WebFetch wrappers).
- File is append-only, never pruned (matches the requirement's lifecycle table).

### Out of Scope

- Search execution itself.
- Audit consumption of web_searches.tsv (IMPL-G / TASK-PROC-006-12).
- Filtering or analytics over the file (audit's job).

## Acceptance Criteria

- [x] Every web search by a downstream executor task appends exactly one row to web_searches.tsv (verified by a smoke test invoking an executor with a search).
- [x] Row format matches the four-column spec above; the file lifecycle is append-only (no pruning code path).
- [x] `recommended_by_optimization_approach` column reflects the produced task's `optimization_approach.web_research_recommended` value when one exists; defaults to `false` for searches outside an optimize-produced task.
- [x] No instrumentation lives in claude-optimize itself — the call site is the executor surface (verified by grep).

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-07 (IMPL-B) | pending | Needs the web_searches.tsv stub created by the scaffolding task |

## Notes

Concept docs: round-4 §6 IMPL-J; decisions log N-D-4 (web-research heuristics
table location — also informs why the recommendation flag belongs in this row).
