---
task_id: TASK-PROC-009-01
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-01-09
completed: 2026-01-09
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-06, SEC-08, SEC-09, SEC-11]
scope_description: "Foundation: ID system, tooling, and setup-task skill updates"
requirements_version:
  commit: f7add7a
  file: ../requirements.md
---

# Goal: Meta Information Foundation & Tooling

## Objective

Build the foundational infrastructure for the meta information system:
1. Create a complete ID registry for all existing requirements
2. Build validation and coverage report scripts
3. Update the `setup-task` skill to auto-generate IDs and frontmatter

This task creates the tools that will be used by Tasks 2 and 3 for the actual migration.

## Requirements Summary

The parent requirement defines:
- **ID Format**: `REQ-[CATEGORY]-[NUMBER]` for requirements, `TASK-[REQ]-[NN]` for tasks
- **Categories**: FUNC (functional), NFUNC (non-functional), PROC (process)
- **Priority System**: URGENCY (0-5) + IMPACT (0-5) with reason codes
- **Status Lifecycles**: draft → defined → in_progress → implemented → deprecated
- **Coverage Tracking**: trackable_items in requirements, covers in tasks

For complete requirements:
```
git show f7add7a:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

1. **ID Registry Creation**
   - Analyze all 37 requirements.md files in the project
   - Assign unique IDs (REQ-FUNC-001, REQ-PROC-001, etc.)
   - Create mapping document: `path → ID`
   - Ensure no collisions

2. **Validation Script (Python or Dart)**
   - Validate YAML frontmatter structure
   - Validate ID format and uniqueness
   - Validate `covers` references point to existing `trackable_items`
   - Report errors/warnings

3. **Coverage Report Script**
   - Scan all requirements and tasks
   - Compute coverage per requirement
   - Generate markdown report showing:
     - Coverage percentage per requirement
     - Gaps (uncovered acceptance criteria)
     - Task-to-item mapping

4. **setup-task Skill Updates**
   - Auto-generate task_id based on parent_requirement
   - Include `covers` field template in goal.md
   - Prompt user for which AC/sections the task covers

### Out of Scope

- Actual migration of requirements.md files (Task 2)
- Actual migration of goal.md files (Task 3)
- Complex analysis of requirement content

## Deliverables

1. `requirements_tasks/_meta/id_registry.md` - Complete ID mapping
2. `scripts/validate_meta.py` (or `.dart`) - Validation script
3. `scripts/coverage_report.py` (or `.dart`) - Coverage report generator
4. Updated `setup-task` skill in `.claude/skills/`
5. **`meta-migrator` agent** in `.claude/agents/` - Temporary agent for Tasks 2 & 3

## Acceptance Criteria

- [ ] All 37 requirements have unique IDs assigned in registry
- [ ] Validation script catches invalid YAML frontmatter
- [ ] Validation script catches invalid `covers` references
- [ ] Coverage report correctly shows 0% coverage initially
- [ ] setup-task skill generates proper task_id format
- [ ] All scripts run without errors on Windows
- [ ] `meta-migrator` agent created and tested

## Implementation Notes

### ID Assignment Strategy

1. **PROC** (process requirements): Start at 001
   - `requirements_tasks/process/AI_rules/` → REQ-PROC-00x

2. **FUNC** (functional features): Start at 001
   - `requirements_tasks/features/` → REQ-FUNC-0xx

3. **NFUNC** (non-functional): Start at 001
   - `requirements_tasks/non_functional/` → REQ-NFUNC-0xx (if exists)

### Script Language Choice

- Python preferred (standard library, no build step)
- Dart acceptable if better for project ecosystem
- Must work on Windows (user's environment)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| None | - | This is the foundation task |

## Notes

- Process requirements are already implemented, so their status will be `implemented`
- Focus on correctness over speed - these tools will be used for 86+ files
- Scripts should be idempotent (safe to run multiple times)

---

## meta-migrator Agent Specification

Create a temporary agent in `.claude/agents/meta-migrator.md` for use in Tasks 2 & 3.

**Purpose**: YAML frontmatter migration specialist for requirements and tasks

**Tools**: Read, Edit, Write, Glob, Grep

**Default Model**: Haiku (cost optimization)

**Escalation to Sonnet when**:
- Files with 8+ acceptance criteria
- Complex dependency chains
- Validation errors encountered
- Unclear priority assignment (needs judgment)
- trackable_items extraction is ambiguous

**Agent Prompt Template**:
```markdown
You are a YAML frontmatter migration specialist. Your job is to add standardized
metadata to requirements.md and goal.md files following the specification in:
requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md

For each file:
1. Read the existing content
2. Generate appropriate YAML frontmatter
3. Add frontmatter at the top of the file
4. Run validation script to verify
5. Report any issues

Escalate to Sonnet if:
- File has 8+ acceptance criteria to extract
- Priority assignment is unclear
- Dependencies are complex
- Validation fails
```

**Lifecycle**:
- Created: End of Task 1
- Used: Tasks 2 & 3
- Removed: End of Task 3
