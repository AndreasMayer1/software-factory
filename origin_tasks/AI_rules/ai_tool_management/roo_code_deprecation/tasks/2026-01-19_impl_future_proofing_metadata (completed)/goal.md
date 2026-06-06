---
task_id: TASK-PROC-011-04
type: impl
parent_requirement: REQ-PROC-011
urgency: 3
urgency_reason: U3-TECH
impact: 2
impact_reason: I2-TECH
status: completed
effort: S
created: 2026-01-19
completed: 2026-01-23
after:
  - TASK-PROC-011-01
  - TASK-PROC-011-02
  - TASK-PROC-011-03
awaiting: []
covers:
  sections: []
scope_description: "Add tool_dependency metadata field to requirement standards and document the deprecation pattern established by REQ-PROC-011"
---

# Implementation Task: Add Tool Migration Metadata Standards

## Requirement Reference
- **Requirement**: `requirements_tasks/process/AI_rules/ai_tool_management/roo_code_deprecation/requirements.md`
- **Section**: Future-Proofing
- **Status**: Pending

## Goal

Establish metadata standards that enable future tool migrations by adding `tool_dependency` field to requirement metadata and documenting the deprecation pattern established by this Roo Code migration.

## Context

**Why This Matters**: AI coding tools are still evolving. The project has already migrated from Roo Code to Claude Code, and may migrate again in the future. Proper metadata and documented patterns make future transitions smoother.

**Current Gap**:
- No standard way to identify which requirements are tool-specific vs. tool-agnostic
- No documented pattern for how to deprecate a tool properly

**Solution**: Add metadata standards + document the pattern we just followed

## Scope Overview

**Task Type**: Documentation updates (metadata standards + pattern documentation)

**Operations**:
1. Add `tool_dependency` field to requirement metadata standards
2. Document the deprecation pattern established by REQ-PROC-011

**Affected Files**:
- Documentation about requirement metadata (likely in `doc/` or requirements documentation)
- Possibly create new documentation file if no standards exist

**Estimated Effort**: Small (straightforward documentation additions)

## Tool Dependency Metadata Field

### Purpose

Identify requirements that are tool-specific vs. tool-agnostic to quickly filter what needs updating during tool migrations.

### Field Specification

Add to requirement YAML frontmatter:

```yaml
tool_dependency: [value]
```

**Allowed Values**:
- `tool_agnostic`: Requirement applies regardless of AI tool used
- `claude_code`: Specific to Claude Code
- `roo_code`: Specific to Roo Code (now deprecated)
- `[tool_name]`: For future tools

### Example

```yaml
---
id: REQ-PROC-011
tool_dependency: tool_agnostic
urgency: 3
impact: 2
status: pending
---
```

### Usage

When switching tools in the future:
1. Filter requirements by `tool_dependency: [old_tool]`
2. Review filtered list for deprecation/update needs
3. Update or deprecate as appropriate

## Deprecation Pattern Documentation

Document the pattern established by REQ-PROC-011 for future use:

### Pattern: Tool Deprecation and Archival

**When to Use**: Switching from one AI coding tool to another

**Steps**:
1. **Create Deprecation Requirement**: Document the deprecation strategy (like REQ-PROC-011)
2. **Archive Files**: Move tool-specific files to `.[tool]_archive/` folder
3. **Add Documentation**: Create `DEPRECATED_README.md` and `KNOWLEDGE_TRANSFER.md`
4. **Cancel Affected Tasks**: Update YAML and rename folders with `(cancelled)` suffix
5. **Update Main Docs**: Add deprecation notice to main documentation files
6. **Preserve Knowledge**: Document what patterns should carry forward

**DO**:
- Preserve all archived files (history is valuable)
- Document why deprecated (future context is critical)
- Extract tool-agnostic patterns for reuse
- Maintain cross-references between tasks and requirements

**DON'T**:
- Delete archived files (lose historical knowledge)
- Leave deprecated files in active locations (causes confusion)
- Forget to update parent requirements (breaks traceability)
- Skip knowledge transfer documentation (lose process insights)

### Reference Implementation

REQ-PROC-011 (Roo Code deprecation) serves as the reference implementation:
- SEC-01: Archival strategy
- SEC-02: Knowledge preservation
- SEC-03: Task cancellation
- Future-Proofing: Metadata standards (this task)

## Acceptance Criteria

From REQ-PROC-011 Future-Proofing section (remaining criteria):

- [ ] `tool_dependency` field added to requirement metadata standards:
  - [ ] Field specification documented (name, allowed values, purpose)
  - [ ] Example usage shown
  - [ ] Guidelines for when to use each value
  - [ ] Location documented where this standard lives
- [ ] Deprecation pattern documented for future use:
  - [ ] Step-by-step process written
  - [ ] DO/DON'T guidelines included
  - [ ] Reference to REQ-PROC-011 as example implementation
  - [ ] Location documented where this pattern lives

## Where to Document

**Option A: Existing Requirements Documentation**
- If there's existing documentation about requirement metadata, add `tool_dependency` field there
- If there's existing documentation about processes, add deprecation pattern there

**Option B: Create New Documentation**
- Create `doc/processes/requirement_metadata.md` for metadata standards
- Create `doc/processes/tool_migration_pattern.md` for deprecation pattern

**Recommended**: Use Option A if existing docs exist, otherwise Option B

The implementation plan will determine the exact location based on current documentation structure.

## Dependencies

**Depends On**:
- TASK-PROC-011-01 (SEC-01): Archival complete - provides reference for deprecation pattern
- TASK-PROC-011-02 (SEC-02): Knowledge transfer complete - shows knowledge preservation approach
- TASK-PROC-011-03 (SEC-03): Task cancellations complete - demonstrates task handling in deprecation

**Blocks**: Nothing (optional enhancement for future)

## Additional Notes

### Why Tool Dependency Field Matters

Without this field, during the next tool migration:
- Must manually review ALL requirements to find tool-specific ones
- Risk missing requirements that need updates
- No systematic way to track tool-agnostic patterns

With this field:
- Filter requirements by `tool_dependency: claude_code`
- Quickly identify what needs attention
- Systematically review and update

### Pattern Documentation Value

The deprecation pattern we followed for Roo Code should be reusable:
- When Claude Code eventually gets replaced (it will happen)
- When adding other tool-specific components
- When sunsetting any project tooling

Documenting it now (while fresh) ensures we don't have to reinvent it later.

### Cross-References

After completion:
- Future tool migrations can reference this pattern
- New requirements should include `tool_dependency` field
- REQ-PROC-011 serves as canonical example

---

**Note**: This task describes WHAT to document (metadata field + pattern), not HOW to write it (specific wording).
The implementation plan will determine the exact documentation structure and location.
