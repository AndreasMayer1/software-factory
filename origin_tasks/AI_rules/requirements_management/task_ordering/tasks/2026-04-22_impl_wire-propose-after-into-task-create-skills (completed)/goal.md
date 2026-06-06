---
task_id: TASK-PROC-042-09
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-04-22
started: 2026-04-23
completed: 2026-04-23
session_completed_at: 2026-04-23T06:15:41Z
session_id: 72467124-8b67-4013-a67f-ca97405ef855
session_account: gmail
after: [TASK-PROC-042-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06]
  sections: []
scope_description: "Add propose_after.py invocation step to task-create, task-create-impl, and requ-derive-from-flow skills: after target folder path is determined and before goal.md is written, run the script and present proposals to the user for review"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Wire propose_after.py into Task-Create Skills

## Objective

Add a `propose_after.py` invocation step to the three task-creation skills (`task-create`, `task-create-impl`, `requ-derive-from-flow`). The step runs after the target folder path is known and before `goal.md` is written, then presents dependency proposals to the user for confirmation.

## Requirements Summary

AC-06 requires heuristic dependency detection at task creation time. This task connects the script (TASK-PROC-042-08) to the actual skill workflows.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Add step to `task-create` skill: after folder path determined, run `propose_after.py`, present proposals, ask user to confirm which to include in `after:`
- Same addition to `task-create-impl` skill
- Same addition to `requ-derive-from-flow` skill
- In automated mode: auto-accept only "same-package continuation" proposals; all other proposals require user confirmation
- If `propose_after.py` produces no proposals: skip the step silently (do not prompt)
- If `propose_after.py` fails: warn user, continue without proposals (non-blocking)

### Out of Scope
- Changes to other skills
- The propose_after.py script itself (TASK-PROC-042-08)

## Acceptance Criteria

- [ ] `task-create` skill shows dependency proposals before writing goal.md
- [ ] `task-create-impl` skill shows dependency proposals before writing goal.md
- [ ] `requ-derive-from-flow` skill shows dependency proposals before writing goal.md
- [ ] No proposals → step is skipped silently
- [ ] Script failure → warning shown, task creation continues
- [ ] In automated mode: same-package proposals auto-accepted, others skipped

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-08 | propose_after.py must exist and work correctly |

## Notes

Full design reference: Part 4.3 (Integration with task-create skills)
