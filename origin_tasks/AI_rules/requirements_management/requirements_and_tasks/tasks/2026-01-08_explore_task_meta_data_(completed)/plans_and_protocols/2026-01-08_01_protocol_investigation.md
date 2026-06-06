# Investigation Protocol: Task Meta Data Standards

## 2026-01-08 14:30 (Initial Investigation)
**Agent**: Explore (Opus)
**Agent ID**: ae09352
**Action**: Comprehensive investigation of current meta information state and design of standardized structure
**Outcome**: PASS - Complete investigation report delivered

### Summary
Analyzed 11 requirements.md files and 8 goal.md files across different categories to understand current meta information patterns. Evaluated the user's proposed priority system (URGENCY + IMPACT with reason codes). Designed comprehensive meta information structure for both requirements.md and goal.md files using YAML frontmatter.

### Key Findings

1. **Current State - Requirements.md**:
   - No unique IDs exist
   - Inconsistent status values ("To Be Implemented", "TBD", "Defined")
   - Priority rarely used (only 2/11 files)
   - No structured dependencies
   - Category often redundant with folder path

2. **Current State - Goal.md**:
   - No unique task IDs
   - Status not standardized
   - No priority/urgency/impact metadata
   - No effort estimation
   - Type already in folder name (redundant if duplicated)

3. **Priority System Analysis**:
   - Gemini's URGENCY + IMPACT system is well-designed
   - Score calculation: (URGENCY * 10) + IMPACT
   - Reason codes provide self-documentation
   - Needs addition of EFFORT dimension
   - Needs standardized STATUS values

4. **Proposed Solution**:
   - YAML frontmatter format (industry standard)
   - Unique IDs: `REQ-[CATEGORY]-[NUMBER]` and `TASK-[REQ-ID]-[NUMBER]`
   - Priority fields: urgency (0-5), urgency_reason, impact (0-5), impact_reason
   - Effort: T-shirt sizing (XS, S, M, L, XL)
   - Standardized status enums for requirements and tasks
   - Dependencies: depends_on, blocks/blocked_by arrays

### Files Analyzed
- 11 requirements.md files (process/, non-functional/, functional/)
- 8 goal.md files (impl and explore tasks)

### Detailed Report
Complete investigation report with:
- Current state analysis with code references
- Priority system evaluation
- Complete field definitions and validation rules
- ID generation rules
- Status value enums
- YAML frontmatter templates
- Migration strategy outline
- Script requirements for querying/reporting

### Agent Output Location
The complete investigation report was delivered directly in the agent's output message and includes:
- Section 1: Current State Analysis (11 requirements.md, 8 goal.md)
- Section 2: Priority System Analysis
- Section 3: Meta Information Design (detailed field specs)
- Section 4: Script Requirements (queries and reports)
- Section 5: Migration Strategy
- Section 6: Concrete Proposal (templates and examples)
- Section 7: Recommendations
- Section 8: File References

**Next Step**: Review findings with user, finalize design decisions, and update requirements.md document with the standardized meta information specification

---
