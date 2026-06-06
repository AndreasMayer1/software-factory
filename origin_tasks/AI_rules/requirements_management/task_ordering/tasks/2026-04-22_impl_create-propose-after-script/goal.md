---
task_id: TASK-PROC-042-08
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-04-22
completed: 2026-04-22
session_completed_at: 2026-04-22T18:37:16Z
session_id: d6935e3d-4585-48eb-a273-1750a4ff3279
session_account: gmail
effort: M
created: 2026-04-22
after: [TASK-PROC-042-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06]
  sections: []
scope_description: "Create scripts/propose_after.py CLI implementing heuristic dependency detection at task-creation time: classifies new task layer from path, applies dependency_heuristics rules from rule file, outputs (task_id, reason) pairs to stdout; never writes to any file; O(N) runtime, no LLM required"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Create propose_after.py Script

## Objective

Create `scripts/propose_after.py` — a creation-time heuristic that suggests `after:` entries for a new task based on its folder path and frontmatter. Runs at task-creation time, outputs proposals to stdout, never writes any files.

## Requirements Summary

AC-06 requires dependencies between task types to be detected heuristically at task creation time (not ordering time), without LLM involvement.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- CLI: `python3 scripts/propose_after.py --path <task-folder-path> --metadata <json-string>`
- `propose_after(new_task_path, new_task_metadata, rules)` function
- Applies all `dependency_heuristics` from rule file in order
- Output format (one line per proposal): `TASK-PROC-042-03   upstream layer dependency, same scope`
- `extract_scope_key()` helper: handles `path_segment[N]` and frontmatter field references
- Edge case handling: completed upstream tasks excluded, blocked tasks included, circular proposals deduplicated (see Part 4.2 of design)
- O(N) runtime — no LLM calls

### Out of Scope
- Reverse direction (finding existing tasks that should wait for the new task) — intentionally deferred per §10.2 of design
- Auto-applying proposals to goal.md (proposals are suggestions only)
- Wiring into task-create skills (TASK-PROC-042-09)

## Acceptance Criteria

- [ ] `propose_after.py --path <path> --metadata '{}'` runs on any existing task path without error
- [ ] Correctly proposes upstream tasks for a new implementation task with same `parent_requirement`
- [ ] Completed tasks are excluded from proposals
- [ ] Each proposal line has format: `TASK-ID   reason`
- [ ] Empty output (no proposals) exits 0 with no output (not an error)
- [ ] No LLM calls, no file writes

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-05 | classifier.py must exist; rules loader must exist |

## Notes

Full design reference:
- Part 4.1: Algorithm pseudocode
- Part 4.2: Edge case table
- §10.2: Decision to not implement reverse direction
