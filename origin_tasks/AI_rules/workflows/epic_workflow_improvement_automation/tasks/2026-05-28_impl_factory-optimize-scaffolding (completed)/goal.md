---
task_id: TASK-PROC-006-07
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-27T23:56:21Z
effort: S
created: 2026-05-28
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Create .factory/optimize/ scaffolding: state.json (schema + initial values), events/ directory, history/runs.tsv header, history/audit_history.tsv header, history/web_searches.tsv header, reports/ directory, README.md describing layout and lifecycle rules."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-B
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: 31c35f0f-8004-4689-954f-7099ef8bf178
session_account: web

---
# Goal: Build `.factory/optimize/` Scaffolding (IMPL-B)

## Objective

Lay down the project-local state folder claude-optimize will own. Every file
declared in the requirement's "Project-Local State" table must exist with the
correct lifecycle semantics. No script in this task; later tasks (IMPL-C..G)
read and write into this layout.

## Requirements Summary

Reference: REQ-PROC-006 §"Project-Local State" (commit eabdeaf0) for the
canonical file list and lifecycle rules. Reference: round-4 §6 IMPL-B (also
adds `history/audit_history.tsv`, `history/web_searches.tsv` to the v1
scaffold).

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- `.factory/optimize/state.json` — counters, last-run timestamp, no-op streak, periodic counter (default N=10). Schema documented inline at the top of `.factory/optimize/README.md`. Lifecycle: overwritten each run.
- `.factory/optimize/events/` — empty directory (with `.gitkeep`). Lifecycle: consume-then-delete; stale events older than 30 days pruned at run start.
- `.factory/optimize/history/runs.tsv` — header-only stub. Lifecycle: append-only, never pruned; canonical cross-session record.
- `.factory/optimize/history/audit_history.tsv` — header-only stub. Lifecycle: append-only.
- `.factory/optimize/history/web_searches.tsv` — header-only stub. Lifecycle: append-only.
- `.factory/optimize/reports/` — empty directory (with `.gitkeep`). Lifecycle: committed per audit run.
- `.factory/optimize/README.md` — describes layout, lifecycle rules, and the consume-then-delete invariant for events/.

### Out of Scope

- Any script that reads or writes these files (IMPL-C, IMPL-D, IMPL-E, IMPL-G).
- task-complete wiring (IMPL-F).
- Web-search instrumentation that populates web_searches.tsv (IMPL-J).

## Acceptance Criteria

- [x] All paths above exist, committed to git, visible to all accounts (no entries in any per-account ignore list).
- [x] state.json contains valid JSON with the four named counters initialised to neutral values; schema documented in README.md.
- [x] All TSV stubs have a column header line matching the format the consuming scripts (IMPL-C, IMPL-G, IMPL-J) will write.
- [x] README.md describes the consume-then-delete rule for events/ and the 30-day pruning rule for stale events.
- [x] No optimizer state lives in per-account OS memory (verified by inspection — no writes to `/home/vscode/.ccs/instances/.../session-env/` or analogous account paths from this scaffold).

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| (none) | — | First task in the IMPL chain |

## Notes

The README is the single place that documents lifecycle. Downstream tasks
(IMPL-C runs.tsv writes; IMPL-G audit_history.tsv writes; IMPL-J
web_searches.tsv writes) reference this README rather than restating the rules.

Concept docs (for context):
- `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/2026-05-16_08_opus_synthesis_round4.md` (round-4 final design)
- `…/2026-05-16_05_opus_synthesis_round3.md` (detailed architecture)
- `…/2026-05-16_07_decisions_applied.md` (decisions log §5 impl backlog)
