---
task_id: TASK-PROC-009-03
type: impl
parent_requirement: REQ-PROC-009
urgency: 4
urgency_reason: U4-DEP
impact: 4
impact_reason: I4-DEBT
status: completed
effort: L
created: 2026-01-09
completed: 2026-01-10
after: [TASK-PROC-009-02]
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-12, SEC-11]
scope_description: "Migrate all 49 goal.md files with YAML frontmatter and covers references"
requirements_version:
  commit: f7add7a
  file: ../requirements.md
---

# Goal: Goal.md (Tasks) Migration

## Objective

Add standardized YAML frontmatter to all 49 goal.md files in the project, including:
- Unique task_id based on parent requirement
- Priority scores (inherited or overridden from parent requirement)
- Status values
- `covers` field linking to parent requirement's trackable_items

## Requirements Summary

Each goal.md must have frontmatter following this template:

```yaml
---
task_id: TASK-[REQ-ID]-[NUMBER]
type: impl | explore
parent_requirement: REQ-xxx
urgency: 0-5
urgency_reason: U[0-5]-[CODE]
impact: 0-5
impact_reason: I[0-5]-[CODE]
status: pending | ready | in_progress | blocked | review | completed | cancelled
effort: XS | S | M | L | XL
created: YYYY-MM-DD
completed: YYYY-MM-DD (when applicable)
after: []
awaiting: []
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: [SEC-01]
scope_description: "Brief summary"
requirements_version:
  commit: xxxxxxx
  file: ../requirements.md
---
```

For complete requirements:
```
git show f7add7a:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

## Scope

### In Scope

1. **All 49 goal.md files**
   - Add/update YAML frontmatter
   - Generate task_id based on parent requirement ID
   - Set appropriate status (completed for `_(completed)` folders)

2. **covers Field Population**
   - Link to parent requirement's trackable_items (from Task 2)
   - Map task scope to specific AC or sections
   - For completed tasks: mark which items they implemented

3. **Priority Inheritance**
   - Copy urgency/impact from parent requirement by default
   - Override only if task has different priority (with justification)

4. **Validation**
   - Run validation script after each file
   - Ensure all `covers` references point to existing trackable_items
   - Fix any broken links

### Out of Scope

- Modifying task content (only adding frontmatter)
- Creating new tasks
- Changing requirements.md files (Task 2)

## Execution Strategy

### Use meta-migrator Agent

This task uses the `meta-migrator` agent created in Task 1.

**Model Selection**:
- **Haiku** (default): Simple tasks with clear scope
- **Sonnet** (escalate): Unclear covers mapping, complex dependencies, validation errors

**Workflow**:
1. Spawn meta-migrator agent per requirement (all tasks for one requirement)
2. Agent reads parent requirement's trackable_items
3. Agent reads each task's goal.md, determines covers mapping
4. Agent adds frontmatter and validates
5. If escalation needed, agent reports back
6. Review and approve changes

---

## Migration Strategy

### Task ID Generation

Based on parent requirement ID:
- `REQ-FUNC-042` + first task → `TASK-FUNC-042-01`
- Sequential numbering within each requirement

### Status Mapping

Based on folder naming:
- Folder ends with `_(completed)` → status: `completed`
- Active folder with recent protocol → status: `in_progress`
- Old folder, no recent activity → status: `completed` or `cancelled` (manual check)

### covers Mapping

For each task:
1. Read parent requirement's trackable_items
2. Analyze task scope (from existing goal content)
3. Map to relevant AC/section IDs
4. Validate references exist

### Batch Processing

Process by requirement (all tasks for one requirement together):
1. Load requirement's trackable_items
2. Migrate all tasks for that requirement
3. Validate coverage
4. Move to next requirement

## Acceptance Criteria

- [ ] All 49 goal.md have valid YAML frontmatter
- [ ] All task_ids follow correct format (TASK-[REQ-ID]-[NN])
- [ ] All `covers` references point to existing trackable_items
- [ ] Validation script passes on all files
- [ ] Coverage report correctly shows coverage percentages
- [ ] Completed tasks have `completed` status and date
- [ ] **meta-migrator agent removed** (cleanup after migration complete)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-xxx-02 | pending | Need requirements with trackable_items first |

## Notes

- Expect ~10 minutes per file on average (less with agent assistance)
- Some tasks may cover multiple AC (e.g., implementation phases)
- Explore tasks may not cover any AC (just investigation)
- 27 goal.md files are still missing git reference metadata (from previous migration)
- This task will complete that migration as well
- Use meta-migrator agent from Task 1 for bulk processing

---

## Agent Cleanup

After all 49 goal.md files are migrated and validated:

1. **Verify migration complete**:
   - Run validation script on all files
   - Generate final coverage report
   - Confirm no errors

2. **Remove meta-migrator agent**:
   - Delete `.claude/agents/meta-migrator.md`
   - The agent was temporary for this migration only
   - Future migrations can recreate if needed

3. **Document removal**:
   - Note in protocol that agent was removed
   - Include final migration statistics
