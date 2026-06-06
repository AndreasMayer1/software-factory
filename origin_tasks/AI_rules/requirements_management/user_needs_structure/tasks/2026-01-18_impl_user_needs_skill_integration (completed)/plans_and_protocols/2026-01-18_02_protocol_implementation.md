# Protocol: Implementation of User Needs Validation Scripts

**Date**: 2026-01-18
**Task**: TASK-PROC-010-03 - Implement User Needs Validation Scripts
**Status**: COMPLETE

---

## 2026-01-18 18:35

**Agent**: simple-implementation orchestrator
**Agent ID**: simple-impl-validation-scripts-2026-01-18-001
**Action**: Implemented validation script enhancements for user needs structure
**Outcome**: ✅ PASS - All acceptance criteria met, quality checks passed
**Next Step**: Use complete-task skill to mark task complete and commit changes

---

## Implementation Summary

### Objective
Implement the validation script enhancements defined in Phase 5 planning document (Agent 4 specifications).

### Scope
- Enhanced `scripts/validate_meta.py` with user needs validation
- Enhanced `scripts/generate_user_needs_status.py` with coverage reporting

### Work Completed

#### 1. validate_meta.py Enhancements

**New Data Structures**:
- Added `UserNeedsMeta` dataclass (lines 51-62)
  - Fields: id, doc_type, path, review_status, parent_id, implementation_status, implementing_epics
- Added ID pattern regexes (lines 75-77):
  - `PERSONA_ID_PATTERN`: `^PERSONA-\d{3}$`
  - `SCENARIO_ID_PATTERN`: `^SCEN-\d{3}-\d{2}$`
  - `FLOW_ID_PATTERN`: `^FLOW-\d{3}-\d{2}-\d{2}$`
- Added `self.user_needs` dictionary to constructor (line 85)

**New Validation Functions**:
1. `_validate_user_needs_file()` (lines 421-486)
   - Validates single persona/scenario/flow file
   - Checks YAML frontmatter, ID format, review_status, parent references
   - Returns UserNeedsMeta object

2. `_extract_implementing_epics()` (lines 488-511)
   - Extracts epic IDs from flow.md "Implementing Epics/Features" section
   - Uses regex to find REQ-* and EPIC-* references

3. `validate_user_needs()` (lines 513-604)
   - Scans requirements_user_needs/personas/ folder
   - Validates all persona.md, scenario.md, flow.md files
   - Checks parent reference consistency (scenario→persona, flow→scenario)
   - Populates self.user_needs dictionary

4. `validate_epic_user_needs_references()` (lines 606-682)
   - Validates user_needs field in epic requirements.md files
   - Checks implements_flows[], addresses_scenarios[], personas_served[]
   - Verifies referenced flows/scenarios/personas exist
   - Warns if referenced documents not approved
   - Checks coverage vs implementation_status consistency

5. `validate_cross_reference_symmetry()` (lines 684-727)
   - Checks bidirectional references are symmetric
   - If flow lists epic, epic should reference flow back
   - Reports asymmetric references as warnings

**Enhanced Output** (lines 729-810):
- Added user needs scanning before requirements (line 737)
- Display counts: personas, scenarios, flows (lines 740-746)
- Added "Validating user needs references..." section (lines 760-761)
- Added "Validating cross-reference symmetry..." section (lines 763-764)
- Added "USER NEEDS SUMMARY" section before final summary (lines 793-810)
  - Shows approved counts for each document type

#### 2. generate_user_needs_status.py Enhancements

**New Helper Methods**:
1. `_extract_epic_references()` (lines 121-126)
   - Extracts epic IDs from flow content using regex

2. `_find_epic_path()` (lines 128-142)
   - Finds path to epic requirements.md file
   - Searches requirements_tasks/ for matching epic ID

3. `_epic_references_flow()` (lines 144-151)
   - Checks if epic references given flow in user_needs field

4. `validate_cross_references()` (lines 153-189)
   - Validates all cross-references in user needs documents
   - Checks if epic files exist for flow references
   - Checks if epic references flow back (symmetry)
   - Returns list of issues with severity (error/warning)

**New Report Sections**:
1. `_generate_implementation_progress()` (lines 376-418)
   - Shows percentage of flows by implementation_status
   - Displays: complete, partial, not_started counts
   - ASCII progress bar visualization (width 50 chars)

2. `_generate_epic_coverage()` (lines 420-476)
   - Shows which epics implement which flows
   - Table format: Epic/Feature | Flows Implemented | Implementation Status
   - Aggregate status calculation (complete/partial/not_started)

3. `_generate_orphan_flows()` (lines 478-521)
   - Lists flows not referenced by any epic
   - Scans all requirements.md files for FLOW-* references
   - Identifies orphaned flows for follow-up

**Enhanced Report Structure** (lines 191-240):
- Inserted implementation progress after summary (line 210)
- Inserted epic coverage after status summary (line 216)
- Inserted orphan flows after epic coverage (line 219)
- Added cross-reference warnings section (lines 222-229)
- Preserves all existing sections

### Testing Results

**validate_meta.py**:
```
✅ Executed successfully with --verbose flag
✅ Found 4 personas, 4 scenarios, 2 flows
✅ User needs summary displayed correctly
✅ Cross-reference validation working
✅ Detected existing issues in codebase (24 errors, 16 warnings)
```

**generate_user_needs_status.py**:
```
✅ Executed successfully
✅ Generated STATUS.md with all new sections
✅ Implementation Progress section present (with progress bar)
✅ Epic/Feature Coverage section present
✅ Orphan Flows section present
✅ All existing sections preserved
```

**STATUS.md Verification**:
- Line 13-23: Implementation Progress with ASCII progress bar
- Line 33-35: Epic/Feature Coverage (currently empty - expected)
- Line 37-39: Orphan Flows (all flows referenced - correct)
- All existing sections intact

### Quality Verification

**Audit Report**: `plans_and_protocols/2026-01-18_01_audit_report.md`

**Results**: ✅ **GREEN - Ready to commit**
- Meta Information: PASS (valid YAML, all covers references exist)
- Code Quality: PASS (follows existing patterns)
- Implementation Completeness: PASS (13/13 acceptance criteria met)
- Manual Testing: PASS (both scripts execute without errors)
- WHY Comments: N/A (validation scripts, spec serves as documentation)

### Acceptance Criteria Status

From goal.md (lines 81-90):

**Validation Scripts**:
- ✅ `scripts/validate_meta.py` has UserNeedsMeta dataclass
- ✅ `scripts/validate_meta.py` has validate_user_needs() function
- ✅ `scripts/validate_meta.py` has validate_epic_user_needs_references() function
- ✅ `scripts/validate_meta.py` has validate_cross_reference_symmetry() function
- ✅ `scripts/validate_meta.py` output includes user needs summary
- ✅ `scripts/generate_user_needs_status.py` has epic coverage report
- ✅ `scripts/generate_user_needs_status.py` has orphan flow detection
- ✅ `scripts/generate_user_needs_status.py` has implementation progress section
- ✅ Both scripts tested and produce expected output

**Quality**:
- ✅ All code follows existing patterns in respective files
- ✅ No regressions in existing functionality
- ✅ Manual testing confirms all features work
- ✅ CLAUDE.md update not needed (no new skill usage patterns)

**ALL ACCEPTANCE CRITERIA MET**: 13/13 ✅

### Files Modified

1. `scripts/validate_meta.py`
   - +314 lines of new validation logic
   - 3 new validation functions
   - 1 new dataclass
   - Enhanced output format

2. `scripts/generate_user_needs_status.py`
   - +141 lines of new reporting logic
   - 4 new report generation methods
   - 4 new helper methods
   - Enhanced report structure

3. `requirements_user_needs/STATUS.md`
   - Auto-generated output file
   - Contains all 4 new sections
   - Existing sections preserved

### Design Decisions

**Decision 1: Separate user_needs dictionary in validate_meta.py**
- Rationale: Different data structures (UserNeedsMeta vs RequirementMeta), different ID formats
- Trade-off: More memory usage, but cleaner separation of concerns

**Decision 2: Asymmetric references as warnings**
- Rationale: Allows work to proceed while flagging potential issues
- Trade-off: User must pay attention to warnings

**Decision 3: File system scanning in generate_user_needs_status.py**
- Rationale: No central index of epics yet, must discover from files
- Trade-off: Slower performance, but no additional infrastructure needed

**Decision 4: No WHY comments**
- Rationale: Validation logic directly implements specification, code is self-documenting
- Trade-off: Future maintainers must reference spec docs for context
- Source: Agent 4 Protocol (2026-01-18_20_protocol_phase5_agent4.md)

### Specification References

**Primary Source**:
- `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-17_explore_implement_user_needs_structure (completed)/plans_and_protocols/2026-01-18_20_protocol_phase5_agent4.md`
  - Product 1: validate_meta.py enhancement specification (lines 90-519)
  - Product 2: generate_user_needs_status.py enhancement specification (lines 522-824)

**Secondary Sources**:
- Goal.md: TASK-PROC-010-03 (this task)
- Opus Plan: 2026-01-18_16_opus_plan_phase5.md (lines 595-783)

### Challenges & Solutions

**Challenge 1: Epic reference extraction from flow.md**
- Issue: Need to parse markdown table to extract epic IDs
- Solution: Simple regex pattern matching for `REQ-[A-Z]+-\d{3}` and `EPIC-[A-Z]+-\d{3}`
- Works for current format, flexible enough for variations

**Challenge 2: Cross-reference symmetry checking**
- Issue: Must check both directions (flow→epic and epic→flow)
- Solution: Two-pass validation (validate_epic_user_needs_references + validate_cross_reference_symmetry)
- First pass checks epic side, second pass checks flow side

**Challenge 3: Finding epic files from IDs**
- Issue: No central index, must scan file system
- Solution: `_find_epic_path()` uses Path.rglob() to search requirements_tasks/
- Caches nothing (simple approach), adequate performance for current scale

### Integration Points

**With existing validate_meta.py**:
- Uses existing parse_yaml_frontmatter() method
- Uses existing add_error() method
- Follows existing validation pattern
- Integrates into run() method before requirements validation

**With existing generate_user_needs_status.py**:
- Uses existing scan_documents() data (self.flows, self.personas, self.scenarios)
- Follows existing report section pattern
- Integrates into generate_report() method
- Preserves all existing functionality

### Next Steps

1. ✅ Implementation complete
2. ✅ Quality verification complete (GREEN)
3. ✅ Protocol logged (this file)
4. ⏭️ Use complete-task skill to mark task complete
5. ⏭️ Commit changes with task reference

### Notes

**Skills Implementation Note**:
The goal.md indicates that skills (create-persona, create-scenario, create-user-flow) were already created during Phase 5 execution. This task only covered validation scripts as specified.

**Git Status Note**:
`scripts/generate_user_needs_status.py` appears as untracked in git. This file was created during the previous task (Phase 5) and should be added to git during commit.

---

## Agent Resumability

**Agent ID**: simple-impl-validation-scripts-2026-01-18-001
**Agent Type**: simple-implementation
**Task Path**: requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-18_impl_user_needs_skill_integration

**To Resume**:
```
Resume agent simple-impl-validation-scripts-2026-01-18-001
```

**Context for Resume**:
- All implementation work complete
- Quality verification passed
- Ready for complete-task skill invocation
- All modified files ready for commit

---

**Protocol Complete**: 2026-01-18 18:35
**Status**: READY FOR COMPLETION
