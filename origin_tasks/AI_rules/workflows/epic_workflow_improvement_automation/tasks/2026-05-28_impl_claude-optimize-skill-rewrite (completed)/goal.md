---
task_id: TASK-PROC-006-10
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-28
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-28T08:58:52Z
after: [TASK-PROC-006-08, TASK-PROC-006-09]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-07, AC-08, AC-09]
  sections: [SEC-02, SEC-03]
scope_description: "Rewrite .claude/skills/claude-optimize/SKILL.md as a thin event consumer: read .factory/optimize/events/, pick highest-priority candidate (bugfix strictly before optimization), emit one improvement task via create_optimize_task.py with the two-field taxonomy and optimization_approach block per SEC-03 heuristics, OR exit as documented no-op. Every run commits runs.tsv and state.json."
release_description: ""
opus_recommended: true   # reason: cross-cutting skill body redesign — 4 ACs, 2 sections
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-E
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: c09e24d5-e933-4353-8fe3-1ee046df839e
session_account: web
---
# Goal: Rewrite claude-optimize Skill Body (IMPL-E)

## Objective

Make claude-optimize a thin event-consumer: one event → one task (or one
documented no-op) → one commit. The LLM step is deliberately minimal. All
detection (IMPL-C) and the writing chokepoint (IMPL-D) live outside the skill.

## Requirements Summary

Reference: REQ-PROC-006 §"Producer Paradigm", §"Candidate Selection Priority",
§"Saturation and Exit", §"Commit Behavior", §"Two-Field Taxonomy" (SEC-02),
§"Web Research Heuristics" (SEC-03), §"Developer Guidelines" key decisions
(commit eabdeaf0).

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- `.claude/skills/claude-optimize/SKILL.md` rewritten as a token-efficient event consumer.
- Selection logic: bugfix candidates strictly first (no fairness rule); within each class, ordering: repeated-question > skill-change-reverted > skill-change-first-used > periodic.
- Produces exactly one of: (a) one improvement task via `scripts/optimize/create_optimize_task.py`, OR (b) a documented no-op entry in runs.tsv.
- Emits the two-field taxonomy on every produced task (SEC-02): `optimization_target` ∈ {skill_body, skill_description, doc_guideline, ordering_rule, hook, script}; `optimization_dimension` ∈ {bugfix, alignment, latency, token_cost, safety, clarity, trigger_accuracy, trigger_precision, layer_order, priority_signal, dependency}.
- Emits the `optimization_approach` block (SEC-03) using the heuristic table (first-match-wins) — heuristic table lives in the skill body (single source of truth).
- Every produced task's AC field uses ground-truth verification (test pass/fail, static analysis clean, script exit code). Single-LLM "is this better?" judgment is forbidden as the sole verification method (AC-08).
- Every run commits `.factory/optimize/history/runs.tsv` and `.factory/optimize/state.json`. Commit message: `chore(optimize): run <id> [created|no-op] [<dimension>]`.
- A no-op run still commits (audit trail).

### Out of Scope

- Monitor scripts (IMPL-C / TASK-PROC-006-08).
- The deny-list and auto-block enforcement (IMPL-D / TASK-PROC-006-09) — invoked via create_optimize_task.py.
- The audit skill (IMPL-G / TASK-PROC-006-12).
- task-complete wiring (IMPL-F / TASK-PROC-006-11).

## Acceptance Criteria

- [x] Skill exits with at most one downstream task per invocation (AC-01); a no-op run produces zero tasks AND commits runs.tsv + state.json (AC-09).
- [x] When both a bugfix and an optimization candidate exist in `events/`, the bugfix is always selected (AC-07) — covered by a fixture-driven test.
- [x] Every produced task carries a verifiable AC using ground-truth signals OR a structural scoring rubric — single-LLM judgment is never the sole verification method (AC-08); the skill body explicitly lists the allowed verification modes.
- [x] Every produced task includes the SEC-02 two-field taxonomy and the SEC-03 `optimization_approach` block.
- [x] Every run results in a git commit containing the updated runs.tsv and state.json (AC-09); commit message follows the named format.
- [x] Skill body is short (token-efficient per requirement §"Developer Guidelines") — soft cap: under ~300 LOC including the heuristics table.

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-08 (IMPL-C) | pending | Needs monitor scripts producing events to consume |
| TASK-PROC-006-09 (IMPL-D) | pending | Needs create_optimize_task.py for the writing chokepoint |

## Notes

Concept docs: round-4 §6 IMPL-E; round-3 §2.3 for heuristics; decisions log
N-D-4 (heuristics table location), N-D-5 (auto-block tag string), N-D-6 (commit
audit reports).
