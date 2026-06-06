# Opus Plan: Restructure User Flows to Shared Model

**Agent ID**: opus-2026-02-01-shared-flows-001
**Created**: 2026-02-01
**Status**: Draft plan awaiting user approval

---

## Objective

Redesign the user needs folder structure to eliminate duplicate user flows by extracting them to a shared location, while preserving personas and scenarios in their current persona-specific locations.

---

## Analysis Summary

### The Core Problem

The current structure nests user flows under personas → scenarios → user_flows:

```
personas/dr_sarah/scenarios/hand_out_plan/user_flows/some_flow/
personas/dr_thomas/scenarios/hand_out_plan/user_flows/some_flow/  # Nearly identical!
```

**Why this creates duplication**: Different personas often have similar scenarios leading to nearly identical user flows. Example: "Hand out questionnaire plan to client" is essentially the same workflow whether performed by Dr. Sarah, Dr. Thomas, or Lisa the waitlist bridger. The app will have ONE implementation, so maintaining N nearly-identical flow documents is:

1. **Wasteful**: Same content written multiple times
2. **Error-prone**: Changes must be synchronized across N files
3. **Confusing for implementation**: Which flow is authoritative?
4. **Violates DRY**: The fundamental "Don't Repeat Yourself" principle

### What We Preserve

- **Personas remain persona-specific**: Each persona captures unique psychology, mental models, constraints
- **Scenarios remain persona-specific**: Scenarios describe the persona's specific context, triggers, emotional state - these differ meaningfully even when goals are similar

### What Changes

- **User flows become shared**: A single flow serves multiple scenarios from different personas
- **Scenarios reference flows**: Instead of containing flows, scenarios link to shared flows
- **Flow IDs change**: No longer encode parent scenario (since flows are now shared)

### Current State Inventory

- **Personas**: 10 total (dr_sarah, max_client, lisa_waitlist_bridger, jana_high_strung, elias_skeptical_guardian, sophie_structure_seeker, david_structure_seeker, hanna_sleepless, michael_high_performer, system_maintenance)
- **Scenarios**: 4 total (across dr_sarah and max_client)
- **User Flows**: 1 total (FLOW-002-01-01 under max_client/brain_dump_at_night)
- **Migration scope**: Minimal - only 1 flow needs restructuring

---

## Proposed Architecture

### New Folder Structure

```
requirements_user_needs/
├── README.md                              # Main documentation
├── README_*.md                            # Modular documentation (unchanged)
├── personas/                              # UNCHANGED - persona-specific
│   ├── dr_sarah/
│   │   ├── persona.md
│   │   └── scenarios/
│   │       ├── prepare_protocol_for_client/
│   │       │   └── scenario.md            # Now references flows via YAML
│   │       └── review_protocol_with_client/
│   │           └── scenario.md
│   ├── max_client/
│   │   ├── persona.md
│   │   └── scenarios/
│   │       ├── brain_dump_at_night/
│   │       │   └── scenario.md            # References FLOW-001
│   │       └── forgotten_protocol_transfer/
│   │           └── scenario.md
│   └── ...
│
└── user_flows/                            # NEW - shared flows location
    ├── quick_night_entry/
    │   └── flow.md                        # FLOW-001 (migrated from max_client)
    ├── protocol_handout/
    │   └── flow.md                        # FLOW-002 (future, serves multiple therapists)
    └── protocol_review/
        └── flow.md                        # FLOW-003 (future)
```

### Key Design Decisions

#### 1. Flow Location: `requirements_user_needs/user_flows/`

**Decision**: Create a new `user_flows/` folder at the same level as `personas/`.

**Rationale**:
- Clear separation: personas → who/why, flows → how
- Easy to find all flows in one place
- Maintains the `requirements_user_needs/` container (flows are still user needs)
- Parallel to the implementation structure: `requirements_tasks/` has epics containing features; `requirements_user_needs/` has personas containing scenarios, PLUS shared flows

**Alternative considered**: `requirements_user_needs/shared_flows/` - rejected because "shared" is implicit; all flows in this location are shared by design.

#### 2. Flow ID Scheme: Sequential, Not Hierarchical

**Old scheme**: `FLOW-[PERSONA]-[SCENARIO]-[SEQUENCE]` (e.g., FLOW-002-01-01)
- Encoded parent scenario
- Made sense when flows were nested under scenarios

**New scheme**: `FLOW-[SEQUENCE]` (e.g., FLOW-001, FLOW-002)
- Simple sequential numbering
- Three-digit zero-padded (FLOW-001, FLOW-002, ... FLOW-999)
- No parent encoding because flows are now shared

**Why simpler is better**:
- Flows are no longer owned by a single scenario
- Hierarchical IDs become misleading when a flow serves 5 scenarios
- Sequential IDs are stable - they don't change when scenarios are added/removed
- Easier to reference: "FLOW-001" vs "FLOW-002-01-01"

#### 3. Scenario → Flow References: YAML Frontmatter

**In scenario.md**, add a new YAML field:

```yaml
---
scenario_id: SCEN-001-01
persona_id: PERSONA-001
name: "Prepare Protocol for Client"
# ... existing fields ...
implements_flows:
  - flow_id: FLOW-002
    relationship: primary      # This flow is THE solution for this scenario
    coverage: full             # Flow fully addresses scenario success criteria
  - flow_id: FLOW-007
    relationship: alternative  # An alternative approach
    coverage: partial          # Only covers some success criteria
    notes: "Only for returning clients who already know the process"
---
```

**Field definitions**:
- `flow_id`: Reference to flow (e.g., FLOW-002)
- `relationship`: `primary` (main solution) | `alternative` (another approach) | `supporting` (helps but not main)
- `coverage`: `full` | `partial` | `minimal`
- `notes`: Optional clarification

**Why YAML over markdown links**:
- Machine-readable for validation scripts
- Explicit relationship types (primary vs alternative)
- Coverage tracking enables gap analysis
- Consistent with existing cross-referencing patterns

#### 4. Flow → Scenario References: YAML Frontmatter

**In flow.md**, modify YAML frontmatter:

```yaml
---
flow_id: FLOW-002
name: "Protocol Handout Flow"
created: 2026-02-01
updated: 2026-02-01
implementation_status: not_started
review_status: draft
serves_scenarios:
  - scenario_id: SCEN-001-01
    persona_id: PERSONA-001
    persona_name: "Dr. Sarah"
    scenario_name: "Prepare Protocol for Client"
  - scenario_id: SCEN-003-01
    persona_id: PERSONA-003
    persona_name: "Lisa"
    scenario_name: "Bridge Client to Therapy"
# ... rest of frontmatter ...
---
```

**Why include persona info in flow**:
- Complete context without needing to resolve paths
- Enables validation: "Does this flow actually serve the referenced personas?"
- Documentation: Readers see at a glance who this flow serves

#### 5. Handling Flow Variations: Parameterization Over Duplication

**Problem**: Sometimes a flow is 95% the same across personas but has 5% differences.

**Solution**: Use **adaptive rules** within a single flow, not separate flows.

**Example** (from existing FLOW-002-01-01):
```markdown
## Adaptive UI Rules

**If user role == therapist**, then:
- Skip client selection (they ARE the client)
- Show "Create for Client" vs "Personal Entry" choice

**If user role == client**, then:
- Direct entry mode (no selection needed)
- Simpler interface (fewer options)

**If persona archetype == "High-Functioning Verdränger"**, then:
- Skip reflection prompts (too cognitively demanding)
- Voice-first input (typing too effortful)
```

**When to create separate flows instead**:
- Core steps differ significantly (>30% different)
- Target different scenario goals
- Implementation would be separate features/screens

**Decision rule**: If the app will have ONE feature that handles multiple personas with conditional logic, use ONE flow with adaptive rules. If the app will have SEPARATE features, use separate flows.

#### 6. Version Implications

**When a shared flow changes**:
1. Flow's `updated` date and `version` change
2. All referencing scenarios should be notified (via validation script)
3. Scenario review_status MAY need reset if flow changes affect them

**Cascade rule** (add to CHANGE_PROPAGATION.md):
```
Flow modified → Notify all scenarios in `serves_scenarios`
  - If flow step changes affect scenario success criteria → scenario needs review
  - If only flow details change (UI refinements) → no cascade needed
```

---

## File Format Changes

### Scenario YAML Frontmatter (Updated)

**Current format**:
```yaml
---
scenario_id: SCEN-001-01
persona_id: PERSONA-001
name: "Scenario Name"
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: "1.0"
evidence_level: proto_persona
review_status: approved
review_history: [...]
---
```

**New format** (additions in bold):
```yaml
---
scenario_id: SCEN-001-01
persona_id: PERSONA-001
name: "Scenario Name"
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: "1.0"
evidence_level: proto_persona
review_status: approved
review_history: [...]
**implements_flows:**                      # NEW FIELD
  **- flow_id: FLOW-002**
    **relationship: primary**
    **coverage: full**
---
```

**Markdown section change**:
Remove the `## User Flows` section that currently lists flow paths. Replace with:

```markdown
## User Flows

This scenario is addressed by the following shared user flows:

| Flow ID | Flow Name | Relationship | Coverage | Notes |
|---------|-----------|--------------|----------|-------|
| FLOW-002 | [Protocol Handout](../../user_flows/protocol_handout/flow.md) | primary | full | |
| FLOW-007 | [Quick Handout](../../user_flows/quick_handout/flow.md) | alternative | partial | For returning clients only |
```

### User Flow YAML Frontmatter (Updated)

**Current format**:
```yaml
---
flow_id: FLOW-002-01-01
scenario_id: SCEN-002-01           # Single parent
name: "Flow Name"
created: YYYY-MM-DD
updated: YYYY-MM-DD
implementation_status: not_started
---
```

**New format**:
```yaml
---
flow_id: FLOW-001                  # Simplified ID
name: "Flow Name"
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: "1.0"                     # Added for versioning
implementation_status: not_started
review_status: draft               # Added per README_12
review_history: [...]              # Added per README_12
serves_scenarios:                  # REPLACES scenario_id
  - scenario_id: SCEN-002-01
    persona_id: PERSONA-002
    persona_name: "Max (Client)"
    scenario_name: "Brain Dump at Night"
  - scenario_id: SCEN-004-01       # Can serve multiple!
    persona_id: PERSONA-004
    persona_name: "Jana"
    scenario_name: "Racing Thoughts at Night"
---
```

**Markdown section changes**:

Replace:
```markdown
## Scenario

**Reference**: [Brain Dump at Night](../../scenario.md)
```

With:
```markdown
## Scenarios Served

This flow addresses the following scenarios:

| Persona | Scenario | Path |
|---------|----------|------|
| Max (Client) | Brain Dump at Night | [SCEN-002-01](../personas/max_client/scenarios/brain_dump_at_night/scenario.md) |
| Jana | Racing Thoughts at Night | [SCEN-004-01](../personas/jana_high_strung/scenarios/racing_thoughts/scenario.md) |
```

---

## Skill Modifications Required

### 1. `create-user-flow` Skill

**Current behavior**: Creates flow under `personas/[persona]/scenarios/[scenario]/user_flows/[flow]/`

**New behavior**:
1. Ask: "Which scenario(s) will this flow serve?" (allow multiple selection)
2. Create flow in `requirements_user_needs/user_flows/[flow_name]/`
3. Generate simple sequential ID (FLOW-NNN)
4. Populate `serves_scenarios` array in YAML
5. Update referenced scenarios to add `implements_flows` entry

**Key changes to skill.md**:
- Change folder creation path
- Change ID generation logic (no longer hierarchical)
- Add multi-scenario support
- Add bidirectional reference creation

### 2. `modify-user-needs` Skill

**Current behavior**: Handles modifications with cascade analysis

**New behavior additions**:
1. When modifying a flow: Identify all scenarios in `serves_scenarios` for cascade notification
2. When modifying a scenario: Check if flows in `implements_flows` are still appropriate
3. When adding a scenario-flow link: Validate both sides exist

**Key changes to skill.md**:
- Update impact analysis to handle bidirectional flow-scenario references
- Add validation for cross-references

### 3. `create-scenario` Skill

**Current behavior**: Creates scenario with empty `user_flows/` folder

**New behavior**:
1. Do NOT create `user_flows/` subfolder (flows no longer live under scenarios)
2. Ask: "Which existing flows serve this scenario?" (or "create new flow later")
3. If flows selected, populate `implements_flows` YAML field
4. Update selected flows to add this scenario to `serves_scenarios`

**Key changes to skill.md**:
- Remove `user_flows/` folder creation
- Add flow linking step
- Add bidirectional reference creation

---

## README Updates Required

### README_2_FOLDER_STRUCTURE.md

**Replace** the current structure diagram with the new one showing `user_flows/` at top level.

### README_5_USER_FLOW_DEFINITION.md

**Update**:
- Template YAML to show `serves_scenarios` instead of `scenario_id`
- Path references (flows now in `user_flows/` not under scenarios)
- Add section on "Flows Serving Multiple Scenarios"
- Update the "Scenario" section template to show "Scenarios Served" table

### README_7_META_INFO_STANDARDS.md

**Update**:
- Flow ID generation rules (now sequential, not hierarchical)
- New YAML fields for scenarios (`implements_flows`)
- New YAML fields for flows (`serves_scenarios`)

### README_8_CROSS-REFERENCING_SYSTEMS.md

**Update**:
- Scenario → Flow reference format
- Flow → Scenario reference format
- Bidirectional validation rules

### README_13_CROSS_REFERENCE_NOTATION.md

**Update**:
- Flow ID format (FLOW-NNN instead of FLOW-NNN-NN-NN)
- Examples showing new notation

### CHANGE_PROPAGATION.md

**Add**:
- Cascade rules for shared flows
- When flow changes trigger scenario review

---

## Merge Script Impact

### `scripts/merge_user_needs.ps1`

**Current behavior**: Traverses `requirements_user_needs/personas/` recursively, collecting all `.md` files.

**Required change**: Also traverse `requirements_user_needs/user_flows/`.

**Specific modification**:
```powershell
# Current: Only processes personas folder
$sourceFolder = "requirements_user_needs"

# Add: Explicitly include user_flows
$folderPath = Join-Path $projectRoot $sourceFolder
$personasPath = Join-Path $folderPath "personas"
$flowsPath = Join-Path $folderPath "user_flows"   # NEW

# Modify Get-MarkdownFiles calls to include both paths
```

**Section ordering in merged file**:
1. Introduction (unchanged)
2. Folder Structure (updated to show new structure)
3. Personas and their scenarios (unchanged)
4. **User Flows** (new section, all flows listed here)

---

## Migration Strategy

### Existing Content to Migrate

Only 1 user flow exists: `FLOW-002-01-01` (Quick Night Entry)

**Location**: `personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/flow.md`

### Migration Steps

1. **Create new location**:
   ```bash
   mkdir -p requirements_user_needs/user_flows/quick_night_entry
   ```

2. **Move and rename** (via git mv for history):
   ```bash
   git mv "requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/flow.md" \
          "requirements_user_needs/user_flows/quick_night_entry/flow.md"
   ```

3. **Update flow YAML**:
   - Change `flow_id: FLOW-002-01-01` → `flow_id: FLOW-001`
   - Remove `scenario_id: SCEN-002-01`
   - Add `serves_scenarios` array with SCEN-002-01 entry

4. **Update scenario YAML** (brain_dump_at_night/scenario.md):
   - Add `implements_flows` with FLOW-001 entry

5. **Remove empty directory**:
   ```bash
   rmdir "requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows"
   ```

6. **Update cross-references** in flow.md:
   - Change relative paths to scenario (now `../personas/max_client/scenarios/...`)

---

## Validation Script Updates

### `scripts/generate_user_needs_status.py`

**Add validations**:
1. Every flow in `implements_flows` exists in `user_flows/`
2. Every scenario in `serves_scenarios` exists in `personas/`
3. Bidirectional consistency: If scenario lists flow, flow should list scenario
4. No orphan flows (flows not referenced by any scenario) - warning, not error
5. No orphan scenarios (scenarios without any flow) - warning, not error

---

## Execution Plan

### Agent 1: Documentation Updates (Sonnet)

**Purpose**: Update all README files and documentation.

**Steps**:
1. Update README_2_FOLDER_STRUCTURE.md with new structure
2. Update README_5_USER_FLOW_DEFINITION.md with new templates
3. Update README_7_META_INFO_STANDARDS.md with new ID/YAML specs
4. Update README_8_CROSS-REFERENCING_SYSTEMS.md with new patterns
5. Update README_13_CROSS_REFERENCE_NOTATION.md with new format
6. Update CHANGE_PROPAGATION.md with cascade rules

### Agent 2: Skill Modifications (Sonnet)

**Purpose**: Update all affected skills.

**Steps**:
1. Update `create-user-flow` skill (major changes)
2. Update `create-scenario` skill (remove user_flows folder, add flow linking)
3. Update `modify-user-needs` skill (cascade analysis for shared flows)

### Agent 3: Scripts & Migration (Sonnet)

**Purpose**: Update merge script and migrate existing content.

**Steps**:
1. Update `scripts/merge_user_needs.ps1` to include `user_flows/` folder
2. Migrate existing flow (FLOW-002-01-01 → FLOW-001)
3. Update scenario (brain_dump_at_night) to reference new flow location
4. Remove empty `user_flows/` folders under scenarios
5. Run merge script to verify output

### Agent 4: Validation (Sonnet)

**Purpose**: Verify all changes work correctly.

**Steps**:
1. Validate all updated README files for consistency
2. Test `create-user-flow` skill with the new structure
3. Test `create-scenario` skill (verify no `user_flows/` folder created)
4. Verify merge script output includes flows section
5. Run STATUS script (if exists) to check cross-references

---

## Quality Criteria

- [ ] New folder structure documented and implemented
- [ ] All README files updated consistently
- [ ] Skills updated and tested
- [ ] Existing flow migrated with git history preserved
- [ ] Merge script produces correct output
- [ ] Bidirectional references work correctly
- [ ] No broken cross-references
- [ ] Validation catches missing references
- [ ] User approves final structure

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing references | High | Git mv preserves history; update all references atomically |
| Skill confusion (old vs new behavior) | Medium | Clear documentation; version note in skill files |
| Merge script misses new folder | Medium | Explicit path configuration, not just recursive search |
| Flow variations harder to model | Medium | Clear guidance on adaptive rules vs separate flows |
| Orphan flows accumulate | Low | Validation script warns about unreferenced flows |

---

## Summary

This plan restructures user flows from a nested persona-specific model to a shared model where flows live in `requirements_user_needs/user_flows/` and are referenced by multiple scenarios. The change:

1. **Eliminates duplication** by having one authoritative flow per app workflow
2. **Preserves context** by keeping scenarios persona-specific
3. **Maintains traceability** through bidirectional YAML references
4. **Simplifies IDs** from FLOW-NNN-NN-NN to FLOW-NNN
5. **Requires updates** to 6 README files, 3 skills, and 1 script
6. **Has minimal migration** (only 1 existing flow)

**Execution requires 4 sequential agents** (documentation → skills → migration → validation).

---

## Next Steps

1. **User reviews and approves this plan**
2. If approved, spawn execution agents in sequence
3. Each agent logs completion to this protocol file
4. Final validation confirms all changes work together
