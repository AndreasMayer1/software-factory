---
task_id: TASK-PROC-009-13
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-02-22
completed: 2026-03-03
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-06, SEC-13]
scope_description: "Run improve-requ-task-meta-info skill to audit and repair dependency metadata and non-standard frontmatter across all requirements_tasks files"
requirements_version:
  commit: 070c693
  file: ../requirements.md
---

# Goal: Improve Requirements & Task Meta Info

## Objective

Run the `improve-requ-task-meta-info` skill to audit and repair dependency metadata AND non-standard frontmatter across all `requirements_tasks/` files.

## Requirements Summary

REQ-PROC-009 defines the meta information standards for requirements and tasks (SEC-06) and the lifecycle rules for maintaining them (SEC-13). This task applies those standards by running the automated audit-and-repair skill.

For complete requirements at task creation time:
```
git show 070c693:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Audit all `requirements.md` and `goal.md` files for non-standard or missing frontmatter fields
- Repair dependency metadata (`depends_on`, `blocks`, `blocked_by`) to use correct IDs
- Fix any non-standard field names or values (e.g., `requirement_id` → `id`)
- Cross-category dependency relationships captured by the dependency oracle

### Out of Scope
- Changes to requirement content (descriptions, acceptance criteria text)
- Creating new requirements or tasks
- Modifying the `improve-requ-task-meta-info` skill itself

## Acceptance Criteria

- [ ] All `requirements.md` files have valid YAML frontmatter with required fields
- [ ] All `goal.md` files have valid YAML frontmatter with required fields
- [ ] All dependency references (`depends_on`, `blocks`, `blocked_by`) use correct IDs
- [ ] No non-standard field names remain (e.g., `requirement_id` instead of `id`)
- [ ] `requirements_tasks/_meta/id_registry.md` is up to date after repairs

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

- Skill: `improve-requ-task-meta-info`
- The skill dynamically determines agent count and uses a dependency oracle to capture cross-category relationships before parallel detail agents apply repairs.
- Run via: `Use improve-requ-task-meta-info skill`
