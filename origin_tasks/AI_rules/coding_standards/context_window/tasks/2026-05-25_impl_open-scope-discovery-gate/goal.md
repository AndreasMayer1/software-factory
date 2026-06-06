---
task_id: TASK-PROC-001-10
type: impl
parent_requirement: REQ-PROC-001
urgency: 4
urgency_reason: U4-PROC
impact: 4
impact_reason: I4-ENAB
status: pending
effort: S
created: 2026-05-25
after: [TASK-PROC-001-02, TASK-PROC-001-04, TASK-PROC-001-06, TASK-PROC-001-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04]
  sections: []
scope_description: "Add a runtime discovery gate to task-resolve and code-bugfix: when goal.md declares a discovery_command, run it at execution start, count items, and decide inline / agent-assisted / propose-split before touching any files."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 226171b7
  file: ../../requirements.md
---
# Goal: Runtime open-scope discovery gate

## Objective

Tasks with open scope — "fix all flutter analyze issues", "fix all validation failures" — don't know how many work items exist until execution time. The count can range from 1 to 300+, making inline vs. fan-out decisions at creation time unreliable (the project changes between creation and execution). This task adds a runtime discovery gate to execution skills: a `discovery_command` declared in goal.md is run as the first action, the item count determines the approach, and no files are touched before that decision is made.

## Requirements Summary

REQ-PROC-001 AC-04 requires that no open-scope task lacks a documented fan-out plan. The `discovery_command` field (added to the `task-create` skill by TASK-PROC-001-06) is the mechanism that makes that plan adaptive: the plan's shape is decided at runtime from the actual item count, not guessed at creation time.

For complete requirements at task creation time:
```
git show 226171b7:requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

- Add a discovery gate to **`task-resolve`** and **`code-bugfix`** skills:
  - At execution start, check if goal.md frontmatter contains `discovery_command`.
  - If present: run the command, capture stdout as item count (integer), apply thresholds:
    - ≤ 10 items → inline mode (unchanged from today)
    - 11–50 items → agent-assisted mode
    - > 50 items → present count to user and propose splitting before any work begins
  - Thresholds calibrated against the per-task budget values established by TASK-PROC-001-04.
  - If absent: fall through to the existing closed-scope check (no behaviour change).
- The discovery gate in `task-resolve` is inserted as the **first check in Step 2**, before TASK-PROC-001-08's closed-scope file-set check (which handles the S2=closed branch). Both checks live in Step 2; open-scope runs first, closed-scope is the fallback.

### Out of Scope

- `code-complex`: its architecture-advisor planning phase already serves as discovery for architectural tasks.
- `task-create` frontmatter field `discovery_command`: defined and documented by TASK-PROC-001-06 — do not re-define it here.
- Changes to inline or agent-assisted execution paths themselves — only the trigger decision changes.
- Automatic splitting without user confirmation when count > 50.

## Acceptance Criteria

- [ ] **AC-04** — `task-resolve` and `code-bugfix` run the `discovery_command` (when present) before any read/edit work. The resulting item count drives the inline / agent-assisted / propose-split decision. Tasks with no `discovery_command` are unaffected.
- [ ] Thresholds are documented inline in both skills and reference TASK-PROC-001-04's calibration values as their source.
- [ ] A task with `discovery_command` returning 0 items skips the work gracefully (logs "nothing to do" and completes).
- [ ] The discovery gate in `task-resolve` Step 2 is ordered before the closed-scope file-set check so both branches coexist cleanly.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed | Synthesis that identified the S2 open-scope gap |
| TASK-PROC-001-04 | pending | Establishes per-task budget thresholds — needed for calibration values |
| TASK-PROC-001-06 | pending | Adds `discovery_command` frontmatter field to `task-create` skill |
| TASK-PROC-001-08 | pending | Reworks `task-resolve` Step 2 closed-scope check — this task adds the open-scope branch on top |
