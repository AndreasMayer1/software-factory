---
task_id: TASK-PROC-036-05
type: impl
parent_requirement: REQ-PROC-036
urgency: 4
urgency_reason: U4-BLOCK
impact: 3
impact_reason: I3-ENAB
status: completed
completed: 2026-03-10
effort: S
created: 2026-03-10
after: []
awaiting: []
awaiting_note: ""
release_description: "Add release_description field to task templates and creation skills"
covers:
  acceptance_criteria: []
  sections: [SEC-05]
target_package: "Transfer Data Model"
scope_description: "Add release_description to goal.md template and update task-create + task-create-impl skills to prompt for it on impl tasks."
requirements_version:
  commit: 8aeefd9
  file: ../requirements.md
---

# Goal: Task Metadata Extension (release_description)

## Objective

Add a `release_description` field to the goal.md YAML frontmatter template and update the two task-creation skills to prompt the user to fill it in for `impl`-type tasks.

## Requirements Summary

Covers SEC-05 (Task Metadata Extension) of REQ-PROC-036.

Field spec:
- `release_description: "..."` — max 15 words, English, user-benefit perspective
- Required for `impl` tasks; optional for all other types

Current requirements: ../requirements.md

## Scope

### In Scope
- Update goal.md template in `task-create` skill: add `release_description` field after `scope_description`
- Update `task-create` skill: prompt user to fill `release_description` when task type is `impl`
- Update `task-create-impl` skill: same
- Add field to the task-create skill's template with inline comment explaining the 15-word rule

### Out of Scope
- Backfilling existing completed tasks (not needed — they are already done)
- Backfilling pending/in-progress tasks for 0.0.1 (separate concern; do manually if needed before release)

## Acceptance Criteria

- [ ] `task-create` skill's goal.md template includes `release_description` field
- [ ] `task-create` skill prompts user to provide `release_description` when type is `impl`
- [ ] `task-create-impl` skill has the same prompt
- [ ] Field is listed as optional (with note "leave blank for non-impl tasks")
- [ ] Updated skills tested by creating one example task and verifying the field appears

## Dependencies

None — this is a prerequisite for other tasks, not dependent on them.

## Notes

- This task is a blocker for TASK-PROC-036-02 (scripts) and TASK-PROC-036-03 (technical notes). Implement first.
- Urgency raised to 4 (U4-BLOCK) because other tasks depend on it.
