---
task_id: TASK-PROC-001-11
type: impl
parent_requirement: REQ-PROC-001
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-06-02
session_completed_at: 2026-06-02T17:46:30Z
started: 2026-06-02
effort: S
created: 2026-05-26
after: [TASK-PROC-001-06, TASK-PROC-001-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Extend task-create-code so that code tasks driving a verify-quality iteration loop on lib/ are automatically flagged opus_recommended: true unless ≤ 3 lib/ files are named in goal.md (AC-07)."
release_description: ""
opus_recommended: false
writes_requirements: false
expected_tool_calls: 12
synthesis_dependent: false
requirements_version:
  commit: 8c0eaa33
  file: ../../requirements.md
plan_source: requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/tasks/2026-05-24_impl_test-case-req-proc-001-decomposition/plans_and_protocols/2026-05-26_task_creation_plan.md
session_id: a0bb80b7-429d-4ed6-a134-4de1ad685509
session_account: web
---
# Goal: task-create-code AC-07 iterative-fix opus escalation

## Objective

Close the REQ-PROC-001 AC-07 zero-coverage gap. AC-07 reads:

> Tasks that drive a `verify-quality` iteration loop on changes under `lib/`
> have `opus_recommended: true` in `goal.md` unless the changed file set is
> named in `goal.md` and contains ≤ 3 files. (Prefer splitting the task
> first; escalation applies only when the iterative-fix loop is inherent to
> the work, not merely large.)

Extend the `task-create-code` skill so this rule is enforced at code-task
creation time. Sits alongside TASK-PROC-001-06 (broader sizing gate, covers
AC-01/02/03) and TASK-PROC-001-07 (automated structural check, covers AC-01/03);
neither of those covers AC-07.

## Requirements Summary

REQ-PROC-001 AC-07 prevents iterative-fix tasks from quietly running on Sonnet
when the file set is wide or unnamed — a class of work that historically blew
the context budget across the verify → fix → re-verify cycle.

For complete requirements at task creation time:
```
git show 8c0eaa33:requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

1. Edit `.claude/skills/task-create-code/SKILL.md` to add an AC-07 check at
   the Opus-recommendation step:
   - Detect S4 (iterative-fix loop) — task's scope includes `lib/`, `test/`,
     `integration_test/` AND the task will exercise `verify-quality`.
   - Detect closed vs open scope — if goal.md lists ≤ 3 specific `lib/` files
     in In Scope, treat as closed (≤ 3 named files).
   - If closed scope (≤ 3 named files): no AC-07 escalation.
   - If open scope OR > 3 files: apply the splitting-first principle per
     REQ-PROC-001 — prompt the user (interactive) or log (automated) that
     splitting the task is the preferred and required first response. Set
     `opus_recommended: true` with the AC-07 reason only when splitting is
     not feasible because the iterative-fix loop is inherent to the work.
2. Document the rule in the skill's Opus Recommendation Check section
   alongside the existing signals.

### Out of Scope

- Retroactively re-evaluating existing tasks. AC-07 applies at creation time
  for new tasks; an audit of existing tasks happens via TASK-PROC-001-12
  (the verification task).
- Changing how `verify-quality` itself runs.
- Touching `task-create` (non-code-task skill) — AC-07 explicitly governs
  changes under `lib/`, the domain of `task-create-code`.

## Acceptance Criteria

- [x] `task-create-code` SKILL.md contains an AC-07 check at the Opus
      recommendation step, referencing REQ-PROC-001 AC-07.
- [x] A code task created with > 3 lib/ files in scope OR open scope
      (pattern-defined) AND a verify-quality loop triggers a splitting-first
      prompt (interactive) or log entry (automated) before any opus escalation.
- [x] `opus_recommended: true` is set with the AC-07 reason only when
      splitting is confirmed infeasible because the iterative-fix loop is
      inherent; auto-escalation without a splitting-first step is absent.
- [x] A code task with ≤ 3 named lib/ files and a verify-quality loop
      remains at `opus_recommended: false` (no override).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-06 | pending | Broader sizing gate — must land first so AC-07 builds on its frontmatter fields. |
| TASK-PROC-001-07 | pending | Automated structural check on task-create-code — shares the same skill file. |

## Notes

Derived by `task-derive-from-requ` (TASK-PROC-058-07 validation run) on
2026-05-26 from `plan_source` listed in frontmatter. AC-04 was already covered
by TASK-PROC-001-10 (created 2026-05-25); AC-07 was the sole remaining
uncovered AC of REQ-PROC-001.
