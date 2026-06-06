---
task_id: TASK-PROC-009-02
type: impl
parent_requirement: REQ-PROC-009
urgency: 4
urgency_reason: U4-DEP
impact: 4
impact_reason: I4-DEBT
status: completed
effort: L
created: 2026-01-09
after: [TASK-PROC-009-01]
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-12, SEC-14]
scope_description: "Migrate all 37 requirements.md files with YAML frontmatter and trackable_items"
requirements_version:
  commit: f7add7a
  file: ../requirements.md
---

# Goal: Requirements.md Migration

## Objective

Add standardized YAML frontmatter to all 37 requirements.md files in the project, including:
- Unique ID from registry (Task 1)
- Priority scores (urgency/impact with reason codes)
- Status values
- trackable_items (acceptance_criteria and/or sections)

## Requirements Summary

Each requirements.md must have frontmatter following this template:

```yaml
---
id: REQ-[CATEGORY]-[NUMBER]
urgency: 0-5
urgency_reason: U[0-5]-[CODE]
impact: 0-5
impact_reason: I[0-5]-[CODE]
status: draft | defined | in_progress | implemented | deprecated
effort: XS | S | M | L | XL
stakeholder: client | therapist | developer | shared
created: YYYY-MM-DD
after: []
blocks: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Description"
  sections:
    - id: SEC-01
      name: "Section Name"
      heading: "## X. Section Heading"
---
```

For complete requirements:
```
git show f7add7a:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

## Scope

### In Scope

1. **All 37 requirements.md files**
   - Add YAML frontmatter from ID registry
   - Set appropriate status (implemented for process, defined/in_progress for features)
   - Estimate effort
   - Identify stakeholder

2. **trackable_items Extraction**
   - Extract acceptance criteria from markdown checkboxes where present (~60% of files)
   - Identify major sections for requirements without AC
   - Assign stable IDs (AC-01, SEC-01, etc.)

3. **Priority Assignment**
   - Assign urgency/impact based on requirement content
   - Include reason codes explaining the rating
   - Process requirements: typically U5-PROC, I5-ENAB (already implemented)
   - Feature requirements: assess based on current project state

4. **Validation**
   - Run validation script (from Task 1) after each file
   - Fix any errors before proceeding

### Out of Scope

- Modifying requirement content (only adding frontmatter)
- Creating new requirements
- Task migration (Task 3)

## Execution Strategy

### Use meta-migrator Agent

This task uses the `meta-migrator` agent created in Task 1.

**Model Selection**:
- **Haiku** (default): Simple requirements with few AC, clear structure
- **Sonnet** (escalate): 8+ acceptance criteria, complex dependencies, unclear priority

**Workflow**:
1. Spawn meta-migrator agent for batch of files
2. Agent reads file, generates frontmatter, validates
3. If escalation needed, agent reports back
4. Review and approve changes
5. Run validation script on batch

---

## Migration Strategy

### Process Requirements (status: implemented)

These are already done, so:
- status: `implemented`
- Just add bookkeeping metadata
- Link to existing completed tasks

### Feature Requirements (various statuses)

Based on task presence:
- No tasks: `defined`
- Has active tasks: `in_progress`
- All tasks completed: `implemented`

### Batch Processing

Migrate in groups by category:
1. `process/AI_rules/` (process requirements)
2. `features/responsive_layout/` (large feature area)
3. `features/questionnaire/` (questionnaire features)
4. `features/` (remaining features)
5. Any remaining categories

## Acceptance Criteria

- [ ] All 37 requirements.md have valid YAML frontmatter
- [ ] All IDs match the registry from Task 1
- [ ] All files have appropriate trackable_items (AC or sections)
- [ ] Validation script passes on all files
- [ ] No duplicate IDs
- [ ] Coverage report shows 0% correctly (before Task 3)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-xxx-01 | pending | Need ID registry and validation script |

## Notes

- Expect ~30 minutes per file on average (less with agent assistance)
- Can be done incrementally
- Some requirements have 12+ acceptance criteria (e.g., plan_evaluation_view) → escalate to Sonnet
- Some have table-based requirements (need section-based tracking)
- Use meta-migrator agent from Task 1 for bulk processing
