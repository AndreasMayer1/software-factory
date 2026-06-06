---
task_id: TASK-PROC-009-12
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-02-07
completed: 2026-02-07
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-06, SEC-08]
scope_description: "Create auto-update scripts for ID registries and integrate into skills"
requirements_version:
  commit: 9f3bd21
  file: ../requirements.md
---

# Goal: Auto-Update ID Registry Scripts

## Objective

Replace manual ID registry maintenance with automatic generation scripts that scan YAML frontmatter and regenerate registries on-demand before use.

## Requirements Summary

From REQ-PROC-009 (Requirements and Tasks Structure):
- SEC-06: Meta Information Standards - Defines ID format and frontmatter structure
- SEC-08: ID Generation Rules - Specifies how IDs are assigned and validated

The current `id_registry.md` is manually maintained, which is error-prone and defeats the purpose of having a single source of truth. This task creates scripts that automatically generate registries by scanning existing YAML frontmatter.

For complete requirements at task creation time:
```
git show 9f3bd21:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
1. **Script Creation**:
   - Script(s) to generate `requirements_tasks/_meta/id_registry.md` (REQ-* IDs)
   - Script(s) to generate `requirements_user_needs/_meta/id_registry.md` (PERSONA-*, SCEN-*, FLOW-* IDs)
   - Scan YAML frontmatter from respective folders
   - Extract IDs, names, paths
   - Generate registry tables (similar to current format)
   - Detect next available IDs per category
   - Overwrite mode (git tracks history, no changelog needed)

2. **Skill Integration** (just-in-time trigger):
   - Update `setup-task` skill to call script before reading registry
   - Update `create-persona` skill to call script before reading registry
   - Update `create-scenario` skill to call script before reading registry
   - Update `create-user-flow` skill to call script before reading registry

3. **Script Approach**: Either one unified script or two separate scripts (architect's choice)

### Out of Scope
- Migration of existing manual registry (keep current data as reference)
- Validation logic (already exists in validate_meta.py)
- Coverage tracking (separate concern)

## Acceptance Criteria

- [x] Script generates accurate `requirements_tasks/_meta/id_registry.md` from existing requirements.md frontmatter
- [x] Script generates accurate `requirements_user_needs/_meta/id_registry.md` from personas/scenarios/flows frontmatter
- [x] Registry shows next available IDs per category (PROC, NFUNC, FUNC for requirements; PERSONA, SCEN, FLOW for user needs)
- [x] Skills call script before reading registry (just-in-time update)
- [x] No manual updates needed - registry is always current
- [x] Script runs successfully on Windows
- [x] Documentation updated (comments in script explain logic)

## Dependencies

None - this task is independent.

## Notes

**Design Decisions**:
- **Trigger**: Just-in-time (Option A) - regenerate before every read for maximum reliability
- **Behavior**: Overwrite mode - no changelog preservation (git history is sufficient)
- **Two Registries**: Separate files for requirements vs. user needs (different folder structures)

**Reference Files**:
- Current manual registry: `requirements_tasks/_meta/id_registry.md`
- Validation script: `scripts/validate_meta.py` (shows how to parse YAML frontmatter)
- Status script: `scripts/generate_status_overview.py` (shows how to scan folders)
