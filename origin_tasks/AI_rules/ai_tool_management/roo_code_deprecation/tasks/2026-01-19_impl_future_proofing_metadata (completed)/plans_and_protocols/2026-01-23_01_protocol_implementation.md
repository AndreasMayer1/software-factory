# Implementation Protocol: Tool Migration Metadata Standards

## 2026-01-23 15:30
**Agent**: simple-implementation workflow
**Agent ID**: N/A (synchronous execution)
**Action**: Implemented tool_dependency metadata field and deprecation pattern documentation

**What Was Done**:
1. **Updated CLAUDE.md** (line 13): Added clarification that `doc/` folder is ONLY for coding guidelines (lib/, test/, integration_test/), NOT for process docs or requirements metadata

2. **Updated requirements_tasks/README.md** with two major additions:
   - **Tool Dependency Field** (after line 322): Added complete specification including:
     - Field purpose and allowed values (tool_agnostic, claude_code, roo_code, [tool_name])
     - Decision rule with 2-question flow to determine correct value
     - Default value (tool_agnostic)
     - Usage during tool migration
     - Example reference to REQ-PROC-011

   - **Tool Migration and Deprecation Pattern** (after line 400): Added comprehensive pattern documentation including:
     - 6-step process (Create deprecation requirement, Archive files, Add documentation, Cancel tasks, Update docs, Preserve knowledge)
     - DO/DON'T guidelines
     - Reference to REQ-PROC-011 as example implementation
     - Clear instructions for future tool migrations

3. **Updated requirement frontmatter example**: Added `tool_dependency: tool_agnostic` to the YAML example in README.md to show proper usage

**Files Modified**:
- `CLAUDE.md` (1 edit: clarified doc/ scope)
- `requirements_tasks/README.md` (3 edits: added tool_dependency field spec, deprecation pattern, updated example)

**Skills/Agents Reviewed**:
- Checked setup-task, explore-requirements, create-impl-task skills
- Confirmed they don't create requirements.md files (only read them)
- No skill updates needed - the README.md serves as the source of truth for humans creating requirements

**Acceptance Criteria Status**:
✅ `tool_dependency` field added to requirement metadata standards:
  ✅ Field specification documented (name, allowed values, purpose)
  ✅ Example usage shown in YAML frontmatter example
  ✅ Guidelines for when to use each value (2-question decision rule)
  ✅ Location documented (requirements_tasks/README.md, Tool Dependency Field section)

✅ Deprecation pattern documented for future use:
  ✅ Step-by-step process written (6 steps)
  ✅ DO/DON'T guidelines included (5 DOs, 5 DON'Ts)
  ✅ Reference to REQ-PROC-011 as example implementation
  ✅ Location documented (requirements_tasks/README.md, Tool Migration and Deprecation Pattern section)

**Outcome**: SUCCESS - All acceptance criteria met

**Next Step**:
1. Use complete-task skill to mark task as completed
2. Commit changes with reference to task folder

**Notes**:
- Decision rule ensures consistent classification (tool-specific vs tool-agnostic)
- Pattern is reusable for future tool migrations beyond just Roo Code → Claude Code
- Documentation is in README.md which is the existing source of truth for requirements structure
