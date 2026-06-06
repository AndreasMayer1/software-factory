---
task_id: TASK-PROC-009-12
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-01-25
completed: 2026-01-25
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add partial mode to merge_requirements.ps1 script to filter output by category (functional/non-functional/process)"
requirements_version:
  commit: 9f3bd21
  file: ../requirements.md
---

# Goal: Add Partial Mode to Requirements Merge Script

## Objective

Add a "partial mode" to the `scripts/merge_requirements.ps1` script that allows filtering the merged output to include only specific requirement categories (functional, non-functional, or process requirements).

## Requirements Summary

The requirement REQ-PROC-009 defines the requirements and tasks structure. This task enhances the merge script (referenced in the requirement) to support filtered output, enabling users to generate category-specific documentation.

For complete requirements at task creation time:
```
git show 9f3bd21:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Add optional parameter(s) to filter by requirement category
- Support filtering for: functional, non-functional, process requirements
- Maintain backward compatibility (no parameter = full merge as before)
- Update output header to indicate when partial mode is active

### Out of Scope
- Changes to file structure or naming conventions
- Additional filtering dimensions (stakeholder, status, etc.)
- GUI or interactive selection

## Acceptance Criteria

- [ ] Script accepts optional parameter to specify category filter
- [ ] When filtered, output includes only markdown files from specified category path
- [ ] Output header clearly indicates partial mode is active and which category
- [ ] Full merge still works when no filter parameter provided
- [ ] No breaking changes to existing script behavior

## Implementation Steps

1. Read current merge_requirements.ps1 script
2. Add parameter for category filtering (e.g., `-Category functional|non-functional|process`)
3. Update folder collection logic to filter based on parameter
4. Update output header to show active filter
5. Test with each category and without parameter

## Dependencies

None

## Notes

The script currently merges from both `requirements_general_overview/` and `requirements_tasks/` folders. Filtering should apply to the appropriate subfolders within `requirements_tasks/` (functional/, non-functional/, process/).
