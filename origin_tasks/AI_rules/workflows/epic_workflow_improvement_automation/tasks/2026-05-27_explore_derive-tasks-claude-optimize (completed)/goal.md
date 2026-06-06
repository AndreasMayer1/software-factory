---
task_id: TASK-PROC-006-04
type: explore
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-27T23:44:59Z
after: [TASK-PROC-006-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Derive the implementation task set for the redesigned claude-optimize from the rewritten REQ-PROC-006, using task-derive-from-requ. Add every created task to the priority override file and wire the validation task."
release_description: ""
opus_recommended: true   # reason: holistic decomposition of a large multi-component design into a correctly-ordered task graph
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
session_id: 0cdeaf76-f2e7-4a65-b0e6-98a692968152
session_account: web
---
# Goal: Derive Implementation Tasks from REQ-PROC-006 (claude-optimize)

## Objective

Once REQ-PROC-006 has been rewritten (TASK-PROC-006-03), decompose it into the
implementation task set using the **`task-derive-from-requ`** skill. The target task
set is already sketched in the concept's round-4 §6 impl backlog (IMPL-A is the
requirement-writing task and is already done by -03; this task creates IMPL-B
through IMPL-J, plus optional IMPL-M).

## MANDATORY READING — the concept (read before any work)

`requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-05-01_explore_redesign-claude-optimize-skill/plans_and_protocols/`

- `2026-05-16_08_opus_synthesis_round4.md` — **the consolidated final design, incl. §6 impl backlog. Start here.**
- `2026-05-16_05_opus_synthesis_round3.md` — detailed architecture
- `2026-05-16_07_decisions_applied.md` — user decisions + §5 impl backlog table

You must fully understand the concept; the derived tasks must faithfully implement it.

## The expected task set (round-4 §6 — confirm/adjust against the rewritten requirement)

| Backlog ID | Task | Depends on |
|---|---|---|
| IMPL-B | `.factory/optimize/` scaffolding (state.json, events/, README, history/runs.tsv, audit_history.tsv, web_searches.tsv, reports/) | IMPL-A (=‑03) |
| IMPL-C | monitor scripts `scripts/optimize/monitor_*.py` + `run_monitors.py` | IMPL-B |
| IMPL-D | `scripts/optimize/create_optimize_task.py` with auto-block `awaiting: ["user-unblock"]` default | IMPL-B |
| IMPL-E | rewrite the `claude-optimize` skill body (event consumer → one task → commit) | IMPL-C, IMPL-D |
| IMPL-F | wire `run_monitors.py` into `task-complete` tail | IMPL-C |
| IMPL-G | build `claude-optimize-audit` skill (rubric score + delta, two metrics, `--monitor=` sub-audits) | IMPL-E |
| IMPL-H | instrument protocol logging with `skills_used:` (enables Stage-2 first-use detection) | IMPL-C |
| IMPL-I | (blocked) consume TASK-PROC-044 observability source | external: TASK-PROC-044 |
| IMPL-J | instrument executor/`claude-log` to write `web_searches.tsv` | IMPL-B |
| IMPL-M (optional) | v1.5 optional DuckDB query layer for the audit skill | IMPL-G |

Treat this as the design intent; the authoritative source is the **ACs of the
rewritten REQ-PROC-006**. `task-derive-from-requ` computes the coverage matrix and a
verification task; reconcile any difference in favor of full AC coverage.

## Post-creation obligations (MANDATORY)

1. **Add every created task ID to** `.claude/task_ordering_priority_override.txt`
   under a clearly-labelled `# --- REQ-PROC-006 claude-optimize impl ---` section,
   in dependency order, each with a one-line comment.
2. **Wire the validation task**: append every created impl task ID to the `after:`
   list of **TASK-PROC-006-06** (`.../2026-05-27_review_validate-claude-optimize-implementation/goal.md`)
   so validation only runs once all impl tasks are complete.
3. Set IMPL-I's `awaiting:` to the external TASK-PROC-044 dependency (it stays
   blocked until that lands).

## Acceptance Criteria

- [x] Every AC of the rewritten REQ-PROC-006 is covered by at least one created task
- [x] A verification task exists (per task-derive-from-requ)
- [x] Dependency order (`after:`) matches the round-4 §6 graph
- [x] All created tasks reference the concept docs in their goal.md (so each implementer understands the design)
- [x] Every created task ID added to `.claude/task_ordering_priority_override.txt`
- [x] Created impl task IDs appended to TASK-PROC-006-06's `after:` list
- [x] IMPL-I left blocked on TASK-PROC-044

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-006-03 | pending | Must rewrite REQ-PROC-006 first |
