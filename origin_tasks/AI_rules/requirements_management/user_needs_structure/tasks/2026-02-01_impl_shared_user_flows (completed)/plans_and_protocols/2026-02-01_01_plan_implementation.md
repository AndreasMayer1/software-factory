---
type: plan
created: 2026-02-01
agent_id: architecture-advisor-2026-02-01-001
status: ready_for_review
---

# Implementation Plan: Shared User Flows Structure

## Summary

This plan implements the architectural changes designed in TASK-PROC-010-08 (exploration task). The goal is to restructure user flows from a nested persona-specific model to a shared model where flows live in `requirements_user_needs/user_flows/` and are referenced by multiple scenarios through bidirectional YAML fields.

**Current state**: 1 flow exists (FLOW-002-01-01) nested under `max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/`

**Target state**: Flow migrated to `user_flows/quick_night_entry/` with ID FLOW-001, bidirectional references established

**Complexity**: Medium - involves 6 README updates, 5 skill updates, 2 script updates, 1 flow migration

---

## Phase Analysis

### Phase 1: Folder Structure

**What needs to be created**:
- `requirements_user_needs/user_flows/` directory (currently does not exist)

**Verification**:
```bash
# Check folder exists
ls requirements_user_needs/user_flows/
```

**Status**: ✅ Straightforward - single directory creation

---

### Phase 2: README Updates

All files located in `requirements_user_needs/`.

#### README_2_FOLDER_STRUCTURE.md

**Current state**: Lines 7-59 show folder structure with flows nested under scenarios

**Changes needed**:
1. Line 7-44: Update folder diagram to show `user_flows/` at top level alongside `personas/`
2. Remove nested `user_flows/` from under scenarios (lines 15-20, 32-35, 42-43)
3. Add new section showing shared flows structure
4. Lines 46-52: Update naming conventions - remove flow folder naming (now handled in user_flows/)
5. Lines 54-59: Update integration explanation - flows now reference scenarios, not vice-versa

**Specific additions**:
```markdown
requirements_user_needs/
├── personas/                              # Persona-specific (psychology, scenarios)
│   └── ...                                # (scenarios no longer contain user_flows/)
└── user_flows/                            # NEW - Shared flows (solution-oriented)
    ├── quick_night_entry/
    │   └── flow.md                        # FLOW-001
    └── protocol_handout/
        └── flow.md                        # FLOW-002 (future)
```

**Estimated complexity**: Medium (structural diagram changes)

---

#### README_5_USER_FLOW_DEFINITION.md

**Current state**: Template shows hierarchical ID (FLOW-[SCENARIO_ID]-[SEQUENCE]) and single scenario reference

**Changes needed**:
1. Lines 260-267: Update template YAML frontmatter:
   - Change `flow_id: FLOW-[SCENARIO_ID]-[SEQUENCE]` → `flow_id: FLOW-[NNN]`
   - Remove `scenario_id: SCEN-[PERSONA_ID]-[SEQUENCE]` field
   - Add `serves_scenarios` array field (see exploration plan for format)
2. Lines 273-274: Update "## Scenario" section to "## Scenarios Served"
   - Change from single reference to table format (Flow ID, Persona, Scenario, Relationship)
3. Add new section after line 280: "## Flows Serving Multiple Scenarios"
   - Explain adaptive UI rules for parameterization
   - When to create separate flows vs one parameterized flow
4. Lines 296-299: Update happy path table - fix "Related Epic/Feature" column examples
5. All path examples throughout file: Change from `../../scenario.md` to `../personas/[persona]/scenarios/[scenario]/scenario.md`

**Specific YAML changes**:
```yaml
# OLD:
flow_id: FLOW-002-01-01
scenario_id: SCEN-002-01

# NEW:
flow_id: FLOW-001
serves_scenarios:
  - scenario_id: SCEN-002-01
    persona_id: PERSONA-002
    persona_name: "Max (Client)"
    scenario_name: "Brain Dump at Night"
```

**Estimated complexity**: High (template changes affect all future flows)

---

#### README_7_META_INFO_STANDARDS.md

**Current state**: Lines 56-73 define hierarchical flow ID generation

**Changes needed**:
1. Lines 56-73: Replace entire "User Flow YAML Frontmatter" section
   - Remove hierarchical encoding explanation (lines 77-98)
   - Add sequential ID generation: FLOW-NNN (3-digit, zero-padded)
   - Remove `scenario_id` field from template
   - Add `serves_scenarios` array field specification
2. Lines 75-98: Update "ID Generation Rules" section
   - Change User Flow IDs format from `FLOW-[SCENARIO_ID]-[SEQUENCE]` to `FLOW-[NNN]`
   - Remove hierarchical encoding explanation
   - Add note: "Sequential numbering across all flows (not per-scenario)"
3. Add new subsection: "Scenario `implements_flows` Field"
   - Field specification (flow_id, relationship, coverage, notes)
4. Add new subsection: "Flow `serves_scenarios` Field"
   - Field specification (scenario_id, persona_id, persona_name, scenario_name)

**Estimated complexity**: Medium (ID generation rules are central but well-defined)

---

#### README_8_CROSS-REFERENCING_SYSTEMS.md

**Current state**: Lines 13-58 show unidirectional references (flows → epics)

**Changes needed**:
1. Lines 13-35: Update "From User Flows to Epics/Features" section
   - Path examples now start from `user_flows/` instead of nested under scenarios
   - Update relative paths: `../../../requirements_tasks/...` → `../../requirements_tasks/...`
2. Lines 36-58: Update "From Epics/Features to User Flows" section
   - Update path examples to point to `user_flows/` location
3. Add new section after line 58: "From Scenarios to User Flows"
   - How scenarios reference flows via `implements_flows` YAML field
   - Table format for markdown section
4. Add new section: "From User Flows to Scenarios"
   - How flows reference scenarios via `serves_scenarios` YAML field
   - Bidirectional validation rules
5. Lines 117-140: Update validation rules section
   - Add: Scenarios must reference at least one flow (warning if missing)
   - Add: Flows must reference at least one scenario (error if missing)
   - Add: Bidirectional consistency check (scenario references flow ↔ flow references scenario)

**Specific additions**:
```markdown
### From Scenarios to User Flows (Upward References)

Scenarios link to shared flows that address their goals.

**In scenario.md**:
```yaml
implements_flows:
  - flow_id: FLOW-001
    relationship: primary
    coverage: full
```

### From User Flows to Scenarios (Downward References)

Flows track which scenarios they serve.

**In flow.md**:
```yaml
serves_scenarios:
  - scenario_id: SCEN-002-01
    persona_id: PERSONA-002
    persona_name: "Max"
    scenario_name: "Brain Dump at Night"
```
```

**Estimated complexity**: High (bidirectional validation is critical)

---

#### README_13_CROSS_REFERENCE_NOTATION.md

**Current state**: Lines 19-26 show hierarchical flow ID format (FLOW-XXX-XX-XX)

**Changes needed**:
1. Lines 19-26: Update examples - change `FLOW-002-01-01` → `FLOW-001`
2. Lines 33-34: Update flow ID format in section references
3. Lines 76-95: Update "From User Flows to Epics/Features" table
   - Fix flow ID format in examples
4. Lines 96-116: Update "From Epics/Features to User Flows" YAML example
   - Change flow ID format: `FLOW-002-01-01` → `FLOW-001`
5. Lines 246-250: Update Rule 5 (Step Range Validity)
   - Change example flow ID format

**Estimated complexity**: Low (search-and-replace with validation)

---

#### CHANGE_PROPAGATION.md

**Current state**: Lines 125-168 describe user flow modification cascade (flow → epics/features only)

**Changes needed**:
1. Add new section after line 123: "Content Flow vs. Reference Flow"
   - Clarify: Content flows ONE-WAY down (Personas → Scenarios → Flows → Features)
   - Clarify: Cross-references are bidirectional for traceability
   - Clarify: Changes to flows NEVER auto-modify scenarios (only trigger review notification)
2. Lines 125-168: Update "### 3. User Flow Modification" section
   - Add step: Identify all scenarios in `serves_scenarios` field
   - Add step: Notify scenarios for review (don't auto-modify)
   - Add note: Manual review needed to assess if scenario success criteria still met
3. Add new section: "### 3.5. Scenario → Flow Reference Changes"
   - When scenario adds/removes flow from `implements_flows`
   - Update flow's `serves_scenarios` to match
   - Validate bidirectional consistency
4. Lines 290-357: Update skill modification descriptions
   - Reference new bidirectional flow-scenario model
   - `modify-scenario` must update flow's `serves_scenarios`
   - `modify-user-flow` must check all referencing scenarios

**Specific additions**:
```markdown
## Content Flow vs. Reference Flow

**CRITICAL DISTINCTION**:

- **Content flow** (one-way): Personas inform Scenarios → Scenarios define needs for Flows → Flows specify requirements for Features
  - Content propagates DOWN only
  - Changes to higher levels may invalidate lower levels

- **Reference flow** (bidirectional): For traceability and impact analysis
  - Scenarios reference Flows (implements_flows)
  - Flows reference Scenarios (serves_scenarios)
  - References enable: "Which scenarios are affected by this flow change?"
  - References DO NOT auto-modify content (manual review required)

**Example**: If FLOW-001 changes its steps, all scenarios in `serves_scenarios` are NOTIFIED (review_status → in_review), but their content is NOT automatically updated. Human review determines if scenario success criteria are still met.
```

**Estimated complexity**: Medium (conceptual clarification, cascade rule updates)

---

### Phase 3: Skill Updates

All skills located in `.claude/skills/`.

#### create-user-flow/skill.md

**Current state**: Lines 90-104 create flow under `personas/[p]/scenarios/[s]/user_flows/[flow_name]/`

**Major changes needed**:
1. Lines 90-104: Change folder creation path to `requirements_user_needs/user_flows/[flow_name]/`
2. Lines 88-98: Change ID generation:
   - Old: Count flows under scenario, extract persona/scenario numbers, format FLOW-PPP-SS-FF
   - New: Count flows in `requirements_user_needs/user_flows/`, generate FLOW-NNN (sequential)
3. Lines 69-84: Add prompt: "Which scenario(s) will this flow serve?" (allow multiple)
4. Lines 113-121: After generating flow.md, populate `serves_scenarios` array in YAML
5. Lines 122-140: Update referenced scenarios:
   - For each scenario selected, add this flow to its `implements_flows` YAML field
   - Read scenario.md, parse YAML, add entry, write back
6. Lines 42-67: Update all path references and examples in documentation sections

**New workflow step** (insert after line 84):
```markdown
**Which scenarios will this flow serve?**:
- Provide scenario IDs (e.g., SCEN-002-01, SCEN-003-01)
- Or scenario paths (I'll extract IDs)

For each scenario, you'll be asked:
- Relationship: primary | alternative | supporting
- Coverage: full | partial | minimal
- Notes (optional)
```

**Bidirectional reference logic** (new step after flow.md creation):
```markdown
### 6.5. Update Scenario References

For each scenario provided:
1. Read scenario.md
2. Parse YAML frontmatter
3. Add to `implements_flows` array:
   ```yaml
   implements_flows:
     - flow_id: FLOW-[NNN]
       relationship: [user choice]
       coverage: [user choice]
       notes: "[user notes]"
   ```
4. Write back scenario.md
5. Set scenario review_status to "in_review" (change notification)
```

**Estimated complexity**: Very High (central workflow, bidirectional updates, ID generation changes)

---

#### create-scenario/skill.md

**Current state**: Lines 94-98 create `user_flows/` subfolder under scenario

**Changes needed**:
1. Lines 94-105: REMOVE `user_flows/` subfolder creation (flows no longer live under scenarios)
2. Lines 69-78: ADD prompt: "Which existing flows serve this scenario?" (optional, can be added later)
3. NEW step after line 109: If user selects existing flows:
   - Populate `implements_flows` YAML field in scenario.md
   - Update each selected flow's `serves_scenarios` field to add this scenario
4. Lines 109-115: Update scenario.md generation to include `implements_flows` field (initially empty or populated from user choice)

**Estimated complexity**: Medium (remove folder creation, add optional flow references)

---

#### modify-user-needs/skill.md

**Current state**: Generic modification skill, needs bidirectional flow-scenario awareness

**Changes needed**:
1. Add section: "When modifying a user flow"
   - Read `serves_scenarios` field
   - Identify all scenarios affected
   - After modification, ask: "Should review notification be sent to scenarios?"
   - If yes: Set each scenario's review_status to "in_review", add review_history entry
2. Add section: "When modifying a scenario's `implements_flows`"
   - If adding flow: Update flow's `serves_scenarios` to include this scenario
   - If removing flow: Update flow's `serves_scenarios` to remove this scenario
   - Validate bidirectional consistency after changes
3. Add validation step: "Check cross-reference consistency"
   - For each flow in scenario's `implements_flows`: Does flow's `serves_scenarios` include this scenario?
   - For each scenario in flow's `serves_scenarios`: Does scenario's `implements_flows` include this flow?
   - Report asymmetries as warnings

**Estimated complexity**: High (bidirectional consistency logic, cascade notifications)

---

#### explore-requirements/skill.md

**Current state**: Section 1.6 searches for user flows in nested locations

**Changes needed**:
1. Section 1.6 "Map User Needs": Update grep patterns
   - Old: Search `personas/*/scenarios/*/user_flows/*/flow.md`
   - New: Search `user_flows/*/flow.md`
2. Update documentation: Flow location changed
3. Update path examples in skill output

**Estimated complexity**: Low (path updates)

---

#### setup-task/skill.md

**Current state**: "User Needs Reference Check" validates flow ID format and existence

**Changes needed**:
1. Update flow ID format expectations:
   - Old regex: `FLOW-\d{3}-\d{2}-\d{2}`
   - New regex: `FLOW-\d{3}`
2. Update flow path resolution:
   - Old: Extract persona/scenario from ID, construct path
   - New: Search `requirements_user_needs/user_flows/*/flow.md` for matching ID
3. Update validation messages to reflect new format

**Estimated complexity**: Low (regex update, path search logic)

---

### Phase 4: Script Updates

#### scripts/merge_user_needs.ps1

**Current state**: Lines 52-59 collect markdown files from `personas/` only

**Changes needed**:
1. Lines 52-59: Add `user_flows/` folder to processing paths
2. Update collection logic:
   ```powershell
   # After line 59, add:
   $flowFiles = Get-MarkdownFiles -FolderPath (Join-Path $folderPath "user_flows")
   ```
3. Lines 202-225: Update section ordering in output
   - Current: Only personas/scenarios/flows nested
   - New: Personas → Scenarios → User Flows (separate section)
4. Insert new section after line 182:
   ```powershell
   # User Flows section
   $content += "## User Flows (Shared)"
   $content += ""

   foreach ($file in $flowFiles) {
       # ... (same processing as scenario files)
   }
   ```

**Estimated complexity**: Medium (section ordering, folder addition)

---

#### scripts/generate_user_needs_status.py

**Current state**: Validates flow IDs, checks epic references, detects orphans

**Changes needed**:
1. Lines 38-90: Update `scan_documents()` method:
   - Add scanning of `user_flows/` folder at root level (currently only scans nested under scenarios)
   ```python
   # After line 90, add:
   flows_root = self.root_dir / "user_flows"
   if flows_root.exists():
       for flow_dir in flows_root.iterdir():
           flow_file = flow_dir / "flow.md"
           if flow_file.exists():
               flow_data = self._parse_document(flow_file, "flow")
               # ...
   ```
2. Lines 153-189: Update `validate_cross_references()` method:
   - Add validation: Scenarios `implements_flows` ↔ Flows `serves_scenarios` bidirectional check
   - For each scenario: Check if flows in `implements_flows` exist
   - For each flow: Check if scenarios in `serves_scenarios` exist
   - Check bidirectional consistency: If scenario references flow, flow must reference scenario back
3. Add new validation function: `_validate_bidirectional_flow_scenario()`:
   ```python
   def _validate_bidirectional_flow_scenario(self):
       """Check scenario ↔ flow bidirectional consistency."""
       issues = []

       for scenario in self.scenarios:
           implements_flows = scenario.get('implements_flows', [])
           for flow_ref in implements_flows:
               flow_id = flow_ref['flow_id']
               # Find flow
               flow = next((f for f in self.flows if f.get('flow_id') == flow_id), None)
               if not flow:
                   issues.append({...})  # Flow doesn't exist
               else:
                   # Check if flow references scenario back
                   serves = flow.get('serves_scenarios', [])
                   scenario_id = scenario.get('scenario_id')
                   if not any(s['scenario_id'] == scenario_id for s in serves):
                       issues.append({...})  # Asymmetric reference

       return issues
   ```
4. Lines 498-540: Update `_generate_orphan_flows()`:
   - Also check: Flows with empty `serves_scenarios` (not referenced by any scenario)
5. Add new report section: "Bidirectional Reference Warnings"

**Estimated complexity**: Very High (bidirectional validation logic, new scanning location)

---

### Phase 5: Content Migration

**Single flow to migrate**: FLOW-002-01-01 → FLOW-001

#### Step 5.1: Create target directory
```bash
mkdir -p requirements_user_needs/user_flows/quick_night_entry
```

#### Step 5.2: Move flow file (preserve git history)
```bash
git mv "requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/flow.md" \
       "requirements_user_needs/user_flows/quick_night_entry/flow.md"
```

#### Step 5.3: Update flow YAML frontmatter

**Read**: `requirements_user_needs/user_flows/quick_night_entry/flow.md`

**Changes**:
1. Line 2: `flow_id: FLOW-002-01-01` → `flow_id: FLOW-001`
2. Line 3: Remove `scenario_id: SCEN-002-01` line
3. After line 7 (after `implementation_status`), add:
   ```yaml
   serves_scenarios:
     - scenario_id: SCEN-002-01
       persona_id: PERSONA-002
       persona_name: "Max (Client)"
       scenario_name: "Brain Dump at Night"
   ```
4. Add `version: "1.0"` if missing (after `updated` field)

#### Step 5.4: Update flow markdown content

**Changes**:
1. Line 24: `**Reference**: [Brain Dump at Night](../../scenario.md)`
   → `**Reference**: [Brain Dump at Night](../personas/max_client/scenarios/brain_dump_at_night/scenario.md)`
2. Search for all `../../../requirements_tasks/` paths → Change to `../../requirements_tasks/`

#### Step 5.5: Update scenario YAML

**Read**: `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/scenario.md`

**Add to YAML frontmatter** (after `review_history`):
```yaml
implements_flows:
  - flow_id: FLOW-001
    relationship: primary
    coverage: full
    notes: ""
```

#### Step 5.6: Update scenario markdown

**Current** (if "User Flows" section exists):
```markdown
## User Flows

- [Quick Night Entry](user_flows/quick_night_entry/flow.md)
```

**Replace with**:
```markdown
## User Flows

This scenario is addressed by:

| Flow ID | Flow Name | Relationship | Coverage | Notes |
|---------|-----------|--------------|----------|-------|
| FLOW-001 | [Quick Night Entry](../../../user_flows/quick_night_entry/flow.md) | primary | full | |
```

#### Step 5.7: Remove empty directories

```bash
# Check if directory is empty first
ls requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/
# If empty:
rmdir requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry
rmdir requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows
```

#### Step 5.8: Check other scenarios for empty `user_flows/` folders

```bash
find requirements_user_needs/personas -type d -name "user_flows" -empty
# Remove any found
```

**Estimated complexity**: Medium (single file migration, but YAML updates are critical)

---

### Phase 6: Validation

After implementation, validate:

1. **Run merge script** (test output):
   ```powershell
   .\scripts\merge_user_needs.ps1 -NoCommit
   ```
   - Verify output includes "User Flows (Shared)" section
   - Verify no broken paths in generated file

2. **Run status script**:
   ```bash
   python scripts/generate_user_needs_status.py
   ```
   - Verify FLOW-001 appears in output
   - Verify no bidirectional reference warnings
   - Verify orphan flows section is empty

3. **Manual checks**:
   - `requirements_user_needs/user_flows/quick_night_entry/flow.md` exists
   - YAML `flow_id: FLOW-001` (not FLOW-002-01-01)
   - YAML `serves_scenarios` array populated
   - Scenario `brain_dump_at_night/scenario.md` has `implements_flows` array
   - No broken cross-references (all paths resolve)
   - Old nested folder removed (no `user_flows/` under scenario)

4. **README consistency**:
   - All 6 README files mention new structure
   - No references to old hierarchical flow IDs (FLOW-XXX-XX-XX)
   - Path examples all use new locations

5. **Skill consistency**:
   - All 5 skills updated with new paths and ID formats
   - `create-user-flow` creates in `user_flows/` folder
   - `create-scenario` does NOT create `user_flows/` subfolder

6. **Test skill execution** (dry run):
   - Invoke `create-user-flow` skill manually (test mode)
   - Verify folder creation path is correct
   - Verify ID generation produces FLOW-00N format
   - Verify bidirectional reference update logic

---

## Risk Assessment

### High Risk Items

1. **Bidirectional reference consistency** (Phase 3, 4, 5)
   - **Risk**: Scenarios reference flows but flows don't reference scenarios back (or vice versa)
   - **Mitigation**: Validation script checks bidirectional consistency
   - **Recovery**: Run validation script after each phase, fix asymmetries immediately

2. **Git history loss during migration** (Phase 5.2)
   - **Risk**: Using `mv` instead of `git mv` loses file history
   - **Mitigation**: ALWAYS use `git mv` for file moves
   - **Recovery**: If history lost, use `git log --follow` to trace original file

3. **Path breakage in READMEs** (Phase 2)
   - **Risk**: Relative paths break when flow location changes
   - **Mitigation**: Test all paths after README updates using link checker
   - **Recovery**: Systematic path search-and-replace based on new structure

### Medium Risk Items

4. **Skill workflow breakage** (Phase 3)
   - **Risk**: `create-user-flow` creates flows in old location, breaking structure
   - **Mitigation**: Thorough testing of skill in dry-run mode before production use
   - **Recovery**: Manual cleanup of incorrectly created folders

5. **Merge script section ordering** (Phase 4)
   - **Risk**: Generated `user_needs.md` has flows in wrong section or duplicated
   - **Mitigation**: Use `-NoCommit` flag for testing before actual commit
   - **Recovery**: Fix script, re-run merge

### Low Risk Items

6. **Empty folder cleanup** (Phase 5.7)
   - **Risk**: Forgetting to remove old `user_flows/` folders under scenarios
   - **Mitigation**: Automated check using `find` command
   - **Recovery**: Manual removal

---

## Recommended Order

Execute phases in strict sequence (dependencies):

```
Phase 1 (Folder Structure)
  → Phase 2 (README Updates)
  → Phase 5 (Content Migration)     # Migrate flow BEFORE updating skills (avoid breaking existing flow)
  → Phase 3 (Skill Updates)         # Skills now work with new structure
  → Phase 4 (Script Updates)        # Scripts now find flows in new location
  → Phase 6 (Validation)            # Verify everything works
```

**Rationale for order**:
- READMEs before migration: Documentation reflects new structure before files move
- Migration before skill updates: Existing flow updated first, skills don't break it
- Skills before scripts: Scripts depend on skill-generated content being in correct location
- Validation last: Checks everything is consistent

---

## Estimated Effort by Phase

| Phase | Complexity | Estimated Time | Risk Level |
|-------|------------|----------------|------------|
| Phase 1: Folder Structure | Low | 5 min | Low |
| Phase 2: README Updates | High | 2-3 hours | High |
| Phase 3: Skill Updates | Very High | 4-5 hours | High |
| Phase 4: Script Updates | Medium | 1-2 hours | Medium |
| Phase 5: Content Migration | Medium | 1 hour | High |
| Phase 6: Validation | Medium | 1 hour | Low |
| **Total** | **High** | **9-13 hours** | **High** |

**Recommendation**: Implement over 2-3 sessions with validation checkpoints between phases.

---

## Success Criteria

After full implementation:

- [ ] `requirements_user_needs/user_flows/` folder exists with FLOW-001
- [ ] All 6 README files updated (no references to FLOW-XXX-XX-XX format)
- [ ] All 5 skills updated (paths, ID generation, bidirectional logic)
- [ ] Merge script produces correct output with "User Flows (Shared)" section
- [ ] Status script shows no warnings (bidirectional consistency OK)
- [ ] FLOW-001 has `serves_scenarios` array with SCEN-002-01
- [ ] SCEN-002-01 has `implements_flows` array with FLOW-001
- [ ] No broken cross-references (all paths resolve)
- [ ] No empty `user_flows/` folders under scenarios
- [ ] Git history preserved for migrated flow file
- [ ] User approves final implementation

---

## Open Questions

1. **Cascade behavior**: When a flow changes, should scenarios automatically move to `in_review`, or should this be manual?
   - **Recommendation**: Automatic (safer, prevents stale references)

2. **Flow versioning**: Should flows have version numbers like scenarios?
   - **Current plan**: Yes - add `version: "1.0"` field to flow YAML
   - **Rationale**: Enables tracking which version of flow was used for implementation decisions

3. **Alternative flow handling**: When creating alternative flows, should skill prompt for "parent" flow?
   - **Recommendation**: No parent relationship - alternatives are standalone flows that serve same scenarios

---

## Next Steps

1. **User approval**: Review this plan for correctness and completeness
2. **Phase execution**: If approved, execute phases in recommended order
3. **Checkpoint validation**: Run validation after Phases 2, 3, 4, 5 (not just at end)
4. **Documentation**: Update CHANGE_PROPAGATION.md with lessons learned during implementation
5. **Skill testing**: After Phase 3, test `create-user-flow` and `create-scenario` skills in dry-run mode

---

**Status**: Ready for user review
**Agent**: architecture-advisor-2026-02-01-001
**Related exploration**: TASK-PROC-010-08 (2026-02-01_explore_shared_user_flows)
