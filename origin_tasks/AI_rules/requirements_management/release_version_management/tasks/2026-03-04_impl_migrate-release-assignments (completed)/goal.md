---
task_id: TASK-PROC-034-07
type: impl
parent_requirement: REQ-PROC-034
urgency: 3
urgency_reason: U3-NEAR
impact: 4
impact_reason: I4-USP
status: completed
completed: 2026-03-05
effort: L
created: 2026-03-04
after: [TASK-PROC-034-05, TASK-PROC-034-06]
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Interactively assign target_release to existing high-priority requirements and their tasks, working top-down from the highest urgency items."
requirements_version:
  commit: c8c9ac7
  file: ../requirements.md
---

# Goal: Migrate Existing Requirements — Assign target_release

## What

Interactively assign `target_release` to the ~69 existing requirements (per-trackable-item) and propagate to child tasks, starting with the highest-priority items.

## Scope

### Approach

This is a collaborative AI + user task. The AI proposes assignments based on context (requirement description, existing dependencies, release scope boundaries from RELEASES.md); the user confirms or overrides.

### Priority Order

Process requirements in this order:
1. **urgency >= 4** (U4 or U5) — most time-sensitive, likely in near-term releases
2. **`status: in_progress`** — active work; critical to assign correctly
3. **urgency 2–3** — lower priority, may target later releases
4. **urgency <= 1 / purely internal** — may remain unassigned indefinitely

### Per-Requirement Steps

For each requirement:
1. Show: requirement ID, name, urgency, status, trackable item list
2. For each trackable item (AC or section): propose a `target_release` based on context
3. User confirms, adjusts, or skips
4. Write `target_release` to each item in the requirement's `requirements.md`
5. Compute and write top-level `target_release` (earliest among assigned items)
6. For each completed or active task under this requirement: propagate `target_release` from covered items (same inheritance logic as task-create)

### Dependency Validation After Each Assignment

After assigning each requirement, check: does any `depends_on` item have a *later* release? If so, warn the user and suggest adjusting either the requirement or the dependency.

### Skipping

Requirements covering purely internal tooling (e.g., process/AI_rules/) may be skipped or left unassigned if the user chooses.

## Dependencies

- Must run after TASK-PROC-034-05 (requ-explore updated) and TASK-PROC-034-06 (task-create updated) so the skills enforce the new convention going forward
- Ideally run after TASK-PROC-034-03 (validate_meta updated) so validation catches errors during migration

## Out of Scope

- New requirements created after this task (handled by updated skills)
- Changelog or release notes generation
