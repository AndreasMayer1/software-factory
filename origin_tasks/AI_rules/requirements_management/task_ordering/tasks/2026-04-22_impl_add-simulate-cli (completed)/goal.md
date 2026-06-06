---
task_id: TASK-PROC-042-07
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-04-22
started: 2026-04-23
completed: 2026-04-23
session_completed_at: 2026-04-22T18:20:51Z
session_id: e39d819b-2467-440c-bdb5-b7682c9bd202
session_account: web
after: [TASK-PROC-042-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Add scripts/task_ordering/simulate.py CLI: loads a proposed rule file, ranks the current backlog with both old and new rules, outputs old vs new top-20 tasks and flags any task whose position shifts by 5 or more"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Add simulate.py CLI

## Objective

Create `scripts/task_ordering/simulate.py` — a dry-run CLI that shows how a proposed rule file change would affect the current backlog ranking. This is the safety gate that the `claude-modify-ordering-rules` skill will always run before committing any rule change.

## Requirements Summary

AC-08 requires rule changes to be dry-runnable against the current backlog before committing.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- CLI: `python3 scripts/task_ordering/simulate.py --proposed-rules <path>`
- Loads current rule file and proposed rule file
- Ranks all open tasks with both rule sets
- Outputs: old top-20 vs new top-20 side-by-side
- Flags any task whose position shifts by ≥5 places (with a clear marker)
- Flags any task that becomes unclassified under the new rules
- Exits 0 always (simulation is informational, not a pass/fail gate)
- `--verbose` flag: also show tasks that shift by 1-4 places

### Out of Scope
- Writing to rule file (simulate.py is read-only)
- The modify skill itself (TASK-PROC-042-10)

## Acceptance Criteria

- [ ] `simulate.py --proposed-rules <path>` runs without error on a valid proposed rule file
- [ ] Output clearly shows old position vs new position for each task in top-20
- [ ] Tasks shifting ≥5 places are visually flagged
- [ ] Tasks becoming unclassified are visually flagged
- [ ] `--verbose` flag works

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-05 | classifier.py and ranker must exist |

## Notes

Full design reference: Part 3.1 Phase C, Part 5.3 Step 4 (skill uses simulate.py)
