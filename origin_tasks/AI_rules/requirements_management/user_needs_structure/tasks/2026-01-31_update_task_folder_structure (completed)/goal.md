---
task_id: TASK-PROC-010-10
type: impl
parent_requirement: REQ-PROC-010
urgency: 3
urgency_reason: U3-QUAL
impact: 3
impact_reason: I3-PROC
status: completed
completed: 2026-02-02
effort: M
created: 2026-01-31
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Mark approved personas and create task folder structure for each persona"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
---

# Goal: Update Task Folder Structure for Personas

## Objective

Two tasks to complete:

1. **Mark personas as approved**: Mark the following 12 personas as `approved`:
   - dr med turan
   - prof dr weber
   - david structure seeker
   - elias
   - hanna sleepless
   - Jana
   - Lisa
   - max client
   - michael
   - Nina
   - Sophie
   - system_maintenance

2. **Create task folder structure**: Update the files and folders in `requirements_tasks/process/AI_rules/requirements_management/user_needs_content/` so that there is one folder for each persona (all currently existing ones, approved or not approved).

## Requirements Summary

Per README_16_TASK_PLACEMENT.md, tasks that create or modify content in `requirements_user_needs/` are placed in the `requirements_tasks/` structure, organized by content type and persona for better organization and traceability.

**Task Location Strategy**:
```
requirements_tasks/process/AI_rules/requirements_management/user_needs_content/
├── [persona_name]/           # Persona-specific modifications
│   └── tasks/
│       └── YYYY-MM-DD_[type]_[description]/
│           ├── goal.md
│           └── plans_and_protocols/
└── tasks/                    # Cross-persona or structural tasks
    └── YYYY-MM-DD_[type]_[description]/
        ├── goal.md
        └── plans_and_protocols/
```

For complete requirements at task creation time:
```
git show 08f8e76:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Mark 12 specified personas as approved (update review_status in YAML frontmatter)
- Create folder structure for all existing personas in user_needs_content

### Out of Scope
- Creating actual task content within persona folders
- Modifying persona content beyond approval status

## Acceptance Criteria

- [ ] All 12 listed personas have review_status: approved
- [ ] Each persona has a corresponding folder in user_needs_content/
- [ ] Each persona folder has a tasks/ subfolder ready for future use

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| None | - | - |

## Notes

User has reviewed and approved the personas. This is a structural/organizational task.
