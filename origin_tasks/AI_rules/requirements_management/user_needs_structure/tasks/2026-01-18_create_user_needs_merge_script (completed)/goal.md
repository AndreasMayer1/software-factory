---
task_id: TASK-PROC-010-01
type: impl
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-01-19
effort: S
created: 2026-01-18
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Create merge script for user_needs/ folder to generate consolidated user_needs.md"
requirements_version:
  commit: 09027a3
  file: ../requirements.md
---

# Goal: Create User Needs Merge Script

## Objective

Create a PowerShell script `scripts/merge_user_needs.ps1` that consolidates all user needs files (personas, scenarios, user flows) into a single `user_needs.md` file in the project root, similar to how `merge_requirements.ps1` works.

**Use Case**: The script's output enables copy-pasting the entire user needs documentation to another AI in the browser all at once.

## Requirements Summary

Based on the existing `merge_requirements.ps1` script, create a similar script that:

1. **Merges content from**: `requirements_user_needs/` folder
2. **Output file**: `user_needs.md` in project root
3. **Exclusions**:
   - Skip `README.md` (too large)
   - Skip `change_propagation.md`
   - Skip `STATUS.md` (if it exists)
4. **Custom header**: Add explanatory text describing what personas, scenarios, and user flows mean in this project
5. **Auto-commit**: Commit the generated file to git (like the existing script does)

For complete requirements at task creation time:
```
git show 09027a3:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Create `scripts/merge_user_needs.ps1` PowerShell script
- Merge all `.md` files from `requirements_user_needs/` (except excluded files)
- Add custom header explaining personas/scenarios/user flows
- Include folder structure tree
- Auto-commit generated file
- Support `--NoCommit` flag for testing

### Out of Scope
- Modifying existing `merge_requirements.ps1`
- Creating validation scripts
- Adding status tracking features

## Acceptance Criteria

- [x] Script creates `user_needs.md` in project root
- [x] All `.md` files from `requirements_user_needs/` are included (except README files, change_propagation.md, STATUS.md)
- [x] Header includes explanation of personas, scenarios, and user flows
- [x] Folder structure tree is included
- [x] Script auto-commits the generated file
- [x] `--NoCommit` flag works for testing
- [x] Output is suitable for copy-pasting to another AI

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| scripts/merge_requirements.ps1 | exists | Template for this script |
| requirements_user_needs/ | exists | Source folder to merge |

## Notes

The script should follow the same structure as `merge_requirements.ps1`:
- Use UTF-8 encoding without BOM
- Generate directory tree
- Include file paths as headers
- Count and report merged files
- Stage and commit only the generated file
