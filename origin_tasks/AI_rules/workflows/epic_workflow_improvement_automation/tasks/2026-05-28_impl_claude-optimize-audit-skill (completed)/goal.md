---
task_id: TASK-PROC-006-12
type: impl
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-05-28
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-28T09:22:06Z
after: [TASK-PROC-006-10]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06, AC-11, AC-12]
  sections: []
scope_description: "Build .claude/skills/claude-optimize-audit/ as a separate skill from claude-optimize (G-INV-3). Computes user-unblock-rate (primary, fast-cadence) and revert-rate (secondary, slow-cadence) from runs.tsv + goal.md awaiting: history + git log. Computes a deterministic N-point health score with trend delta, written to audit_history.tsv. Supports --monitor=<name> sub-audits."
release_description: ""
opus_recommended: true   # reason: new skill design with deterministic rubric + two metrics + sub-audits
writes_requirements: false
worktree_path: ""
target_package: "claude-optimize"
backlog_id: IMPL-G
requirements_version:
  commit: eabdeaf0
  file: ../requirements.md
session_id: d7995fff-38e5-49e1-bd0f-9d740a8675e7
session_account: gmail
---
# Goal: Build `claude-optimize-audit` Skill (IMPL-G)

## Objective

Score the optimizer loop's effectiveness with a deterministic, reproducible
N-point rubric and two named metrics. The audit skill is structurally separate
from the producer skill (G-INV-3) — the same agent never both produces and
scores within a run.

## Requirements Summary

Reference: REQ-PROC-006 §"Effectiveness Metrics and Audit", §"Hard Constraints"
G-INV-3, AC-06/AC-11/AC-12 (commit eabdeaf0). Round-4 Part 2 (deterministic
scoring rubric — kaizen-style 10-point with trend delta + targeted sub-audits)
and Part 4 (revert-rate as secondary metric).

For complete requirements at task creation time:
```
git show eabdeaf0:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- `.claude/skills/claude-optimize-audit/SKILL.md` — separate skill from `.claude/skills/claude-optimize/` (G-INV-3).
- Invoked on user demand (not on a trigger).
- Computes two metrics:
  1. **user-unblock-rate** (primary, fast-cadence): fraction of produced tasks the developer unblocked. Computed from runs.tsv + goal.md `awaiting:` history. Target band 50–80%.
  2. **revert-rate** (secondary, slow-cadence): fraction of unblocked-and-completed improvement tasks reverted or substantially rewritten within N weeks. Computed from `git log`. Quarterly cadence (slow due to maturation window).
- Deterministic N-point health score: starting rubric = 10 criteria, each computed from runs.tsv + git history (NEVER from LLM judgment).
- Score + delta-vs-previous written to `.factory/optimize/history/audit_history.tsv` (append-only) on every audit run.
- Audit report written to `.factory/optimize/reports/<date>_audit.md` (committed per audit run).
- Sub-audits via `claude-optimize-audit --monitor=<name>` — scopes the rubric to one monitor's events.
- Static separation enforced: the producer skill SKILL.md must not import / reference / dispatch to the audit skill within the same run.

### Out of Scope

- DuckDB query layer — that is IMPL-M / TASK-PROC-006-16 (optional v1.5).
- Consuming TASK-PROC-044 observability data (IMPL-I / TASK-PROC-006-14).
- Refining the 10 rubric criteria from real data (intentional follow-up once runs.tsv has accumulated data, per round-4 §9; this task ships the starting criteria).

## Acceptance Criteria

- [x] Skill exists at `.claude/skills/claude-optimize-audit/SKILL.md` and is registered in `.claude/skills/INDEX.md` as a separate skill from `claude-optimize` (AC-06 / G-INV-3).
- [x] Computes user-unblock-rate and revert-rate as specified (AC-11); both metric definitions appear in the skill body with their cadence labels.
- [x] Computes a deterministic N-point health score (rubric definition lives in the skill) with delta-vs-previous, appended to audit_history.tsv on every run (AC-12).
- [x] Score is computed ONLY from runs.tsv + git history; no code path uses LLM judgment for the score (AC-12) — verified by inspection.
- [x] `--monitor=<name>` flag scopes the rubric to a single monitor's events (per round-4 Part 2.2).
- [x] Producer skill (claude-optimize) does NOT invoke claude-optimize-audit within the same run (G-INV-3) — verified by grep against the producer SKILL.md.

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| TASK-PROC-006-10 (IMPL-E) | pending | Needs the producer skill (and a populated runs.tsv) to audit |

## Notes

Concept docs: round-4 Part 2 (steal kaizen's deterministic rubric + targeted
sub-audits); Part 4 (revert-rate as a quality lag-indicator); decisions log
N-D-2 (skill name) and N-D-6 (commit audit reports).

The 10 rubric criteria are the starting point — round-4 §9 explicitly flags
that the criteria "will need a pass once real runs.tsv data exists." Ship the
criteria as a script-owned constant so refinement is a normal edit.
