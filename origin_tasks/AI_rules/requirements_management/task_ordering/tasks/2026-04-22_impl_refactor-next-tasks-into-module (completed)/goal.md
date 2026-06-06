---
task_id: TASK-PROC-042-03
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-22
session_completed_at: 2026-04-22T17:20:21Z
started: 2026-04-22
session_id: 0013b3e0-d772-4060-bcca-3a6a4f3bd971
session_account: gmail
effort: M
created: 2026-04-22
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-04]
  sections: []
scope_description: "Refactor scripts/next_tasks.py into a scripts/task_ordering/ Python module with hardcoded defaults that reproduce current behavior exactly; next_tasks.py becomes a thin CLI wrapper; all existing CLI flags and output format preserved"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Refactor next_tasks.py into task_ordering Module

## Objective

Refactor `scripts/next_tasks.py` into a `scripts/task_ordering/` Python module. This is Phase A of the incremental migration: extract the logic into a project-agnostic module while keeping all behavior identical. No functional change — only structural reorganization.

## Requirements Summary

REQ-PROC-042 requires the ordering mechanism to be portable and automatic (AC-01, AC-04). Extracting the logic into a module is the prerequisite for adding a rules loader in TASK-PROC-042-04.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Create `scripts/task_ordering/` package with: `__init__.py`, `defaults.py`, `ranker.py`, `dependencies.py`, `classifier.py` (stub), `rules.py` (stub)
- `defaults.py` encodes the current hardcoded sort key as Python functions
- `ranker.py` implements the sort_key_factory using defaults
- `dependencies.py` contains the is_blocked / filter logic currently in next_tasks.py
- `next_tasks.py` becomes a thin CLI wrapper delegating to `scripts/task_ordering/`
- All existing CLI flags (`--release`, `--package`, `--count`, `--type`) preserved
- Output format byte-identical to current output

### Out of Scope
- Loading `.claude/task_ordering_rules.yaml` (TASK-PROC-042-04)
- Implementing `classify_layer()` (TASK-PROC-042-05)
- Any behavior change

## Acceptance Criteria

- [ ] `scripts/task_ordering/` package exists with all listed modules
- [ ] `python3 scripts/next_tasks.py` produces identical output to current behavior
- [ ] All CLI flags still work
- [ ] `scripts/task_ordering/defaults.py` contains all current sort-key logic
- [ ] No behavior change on the current backlog (regression check)

## Dependencies

None — this task can run in parallel with TASK-PROC-042-02.

## Notes

Full design reference: `tasks/2026-04-22_explore_intelligent-task-ordering/plans_and_protocols/2026-04-22_02_opus_design.md`
- Part 3.1: Minimal-change refactor (recommended)
- Part 3.2: Engine skeleton pseudocode
