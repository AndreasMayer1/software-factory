# Scenario Index Design Proposal

**Task**: TASK-PROC-010-12
**Date**: 2026-02-06
**Agent**: Opus (direct content creation)
**Depends on**: `2026-02-06_01_scenario_pattern_analysis.md`

## 1. Design Goals

The scenario index must serve three audiences with different needs:

| Audience | Need | Usage |
|----------|------|-------|
| **Human (user/reviewer)** | See at a glance which scenario patterns exist, which personas have them, and where gaps are | Strategic overview, approval decisions |
| **AI (create-scenario skill)** | Look up canonical names, validate new scenario names, suggest missing scenarios | Automation, consistency enforcement |
| **Process (cross-referencing)** | Link scenario instances to archetypes, track coverage | Traceability, gap analysis |

## 2. Index Structure Decision

### Option A: Pure Markdown Table
```markdown
| Pattern | Description | Roles | Dr. Sarah | Max | Sophie | ... |
```
**Pro**: Human-readable, simple to maintain.
**Con**: Hard for AI to parse reliably, gets wide with many personas.

### Option B: YAML Document
```yaml
patterns:
  - canonical_name: transfer_data_to_therapist
    description: "..."
    roles: [client]
    instances:
      - persona: max_client
        scenario_id: SCEN-002-02
```
**Pro**: Machine-parseable, structured.
**Con**: Harder for humans to scan quickly, verbose.

### Option C: Hybrid — YAML Frontmatter + Markdown Body (Recommended)

```markdown
---
# Machine-readable index
patterns:
  - canonical_name: transfer_data_to_therapist
    roles: [client]
    instances:
      - persona_id: PERSONA-002
        scenario_id: SCEN-002-02
---

# Scenario Index (Human-Readable)

## Pattern: Transfer Data to Therapist
**Canonical name**: `transfer_data_to_therapist`
...
```

**Pro**: Best of both worlds. YAML for tooling, markdown for humans.
**Con**: Must keep both in sync. But the YAML is the source of truth, and the markdown body can be regenerated.

### Decision: **Option C (Hybrid)**

Rationale: The create-scenario skill needs machine-readable data. Humans need scannable overview. A single file with both avoids the "two files, which is truth?" problem.

## 3. File Location

### Option A: `requirements_user_needs/SCENARIO_INDEX.md`
**Pro**: Top-level visibility, easy to find. Same level as README files.
**Con**: Adds another file to an already file-heavy directory.

### Option B: `requirements_user_needs/indexes/scenario_index.md`
**Pro**: Leaves room for future indexes (persona_index, flow_index). Clean separation.
**Con**: Extra directory for potentially just one file.

### Option C: `requirements_user_needs/SCENARIO_INDEX.md` now, move later if needed

### Decision: **Option A** — `requirements_user_needs/SCENARIO_INDEX.md`

Rationale: Start simple. One file at the top level. If we later need persona_index or flow_index, we can create an `indexes/` folder and move everything. Premature directory creation is worse than a later migration.

## 4. Index Schema (YAML Frontmatter)

```yaml
---
# Scenario Pattern Index
# Source of truth for canonical scenario names and cross-persona coverage
version: "1.0"
updated: 2026-02-06

patterns:
  - canonical_name: "prepare_protocol_for_client"   # snake_case, used as folder name
    display_name: "Prepare Protocol for Client"      # Human-readable
    description: >
      Therapist creates or customizes a structured tracking instrument
      (protocol/questionnaire) tailored to a specific client's therapy goals,
      then plans how to introduce it in the session.
    lifecycle_stage: create                           # create | capture | prepare | transfer | review
    applicable_roles:                                 # Which persona roles this pattern applies to
      - role: therapist
        relevance: primary                            # primary | secondary | edge_case
        notes: "Core therapist workflow"
      - role: self_user
        relevance: edge_case
        notes: "Self-user creating own tracking structure (no client)"
    tags: [protocol, preparation, therapist_workflow]
    instances:                                        # Actual scenarios implementing this pattern
      - persona_id: PERSONA-001
        persona_folder: dr_sarah
        scenario_id: SCEN-001-01
        scenario_folder: prepare_protocol_for_client
        outcome: success
        variant_notes: "Standard case, paper-based preparation"
    predicted_instances:                              # Personas that SHOULD have this but don't yet
      - role: self_user
        notes: "Self-user designing own mood tracking structure"
---
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `canonical_name` | string (snake_case) | yes | **The** name for this pattern. New scenarios SHOULD use this as folder name. |
| `display_name` | string | yes | Human-friendly name for documentation |
| `description` | string | yes | Abstract, persona-agnostic description of the goal pattern. 1-3 sentences. |
| `lifecycle_stage` | enum | yes | Where this pattern falls in the therapy data lifecycle: `create`, `capture`, `prepare`, `transfer`, `review`, `reflect` |
| `applicable_roles` | array | yes | Which persona roles (therapist, client, self_user) this pattern applies to, with relevance level |
| `tags` | array | no | Free-form tags for grouping/searching |
| `instances` | array | yes (can be empty) | Actual scenarios that implement this pattern |
| `predicted_instances` | array | no | Roles/personas that should have this pattern but don't yet |

### Instance Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `persona_id` | string | yes | PERSONA-NNN reference |
| `persona_folder` | string | yes | Folder name for path construction |
| `scenario_id` | string | yes | SCEN-NNN-NN reference |
| `scenario_folder` | string | yes | Actual folder name (may differ from canonical_name for legacy scenarios) |
| `outcome` | enum | no | `success`, `failure`, `partial`, `mixed` — for patterns with outcome variants |
| `variant_notes` | string | no | What distinguishes this instance from others of the same pattern |

## 5. Naming Convention Rules

### 5.1 Primary Rule: Goal-Based Naming

Scenario folder names describe **what the persona is trying to achieve**, not when/where/how it happens, and not whether it succeeds or fails.

**Pattern**: `[action]_[object]_[qualifier]`

| Component | Description | Examples |
|-----------|-------------|---------|
| `action` | The verb — what the persona does | `prepare`, `capture`, `transfer`, `review`, `create`, `enter` |
| `object` | What they act on | `data`, `protocol`, `entry`, `thoughts` |
| `qualifier` | Context that distinguishes from similar patterns (optional) | `for_client`, `spontaneously`, `for_therapy_session`, `collaboratively` |

### 5.2 Handling Success/Failure Variants

**Rule**: The canonical pattern name does NOT include outcome. Outcome is tracked in instance metadata.

When the **same persona** needs both success and failure scenarios of the same pattern, append `__[outcome_qualifier]` (double underscore) to the folder name:

```
personas/max_client/scenarios/
  transfer_data_to_therapist__forgotten/     ← failure variant
  transfer_data_to_therapist__successful/    ← success variant (if ever needed)
```

When **different personas** have the same pattern with different outcomes, no suffix needed — they're in different folders:

```
personas/max_client/scenarios/
  transfer_data_to_therapist/                ← Max's version (failure)
personas/sophie_structure_seeker/scenarios/
  transfer_data_to_therapist/                ← Sophie's version (success)
```

**Double-underscore rationale**: Single underscores separate words within a component. Double underscores separate the canonical name from the variant qualifier. This makes parsing unambiguous.

### 5.3 Handling Context Variants

When the same pattern occurs in **different contexts** for the same persona:

```
capture_data_spontaneously__nighttime/       ← brain dump at night
capture_data_spontaneously__commute/         ← capturing thoughts on the train
```

But if a persona only has ONE instance of a pattern, no qualifier needed:

```
capture_data_spontaneously/                  ← only one variant → no qualifier
```

### 5.4 Word Choice Rules

| Concept | Preferred Term | Avoid | Rationale |
|---------|---------------|-------|-----------|
| Moving data from client to therapist | `transfer` | `handover`, `hand_over`, `deliver` | Consistent single term |
| Therapist's tracking tool | `protocol` | `questionnaire`, `form`, `sheet` | Domain-standard in German psychotherapy |
| Writing something down urgently | `capture` | `dump`, `log`, `record` | Neutral, goal-oriented |
| Looking at data before session | `prepare_for` | `review_before`, `pre_session` | Consistent with existing naming |
| Looking at data together | `review_collaboratively` | `review_with`, `analyze_together` | Explicit about the collaboration aspect |
| Daily/scheduled logging | `routine_data_entry` | `daily_tracking`, `scheduled_logging` | Encompasses various frequencies |

### 5.5 Anti-Patterns (What NOT to Do)

| Bad Name | Problem | Better Name |
|----------|---------|-------------|
| `brain_dump_at_night` | Context-based (when), not goal-based (what) | `capture_data_spontaneously` |
| `forgotten_protocol_transfer` | Outcome-based (forgotten = failure) | `transfer_data_to_therapist` (outcome in metadata) |
| `successful_protocol_handover` | Outcome-based (successful) + inconsistent synonym (handover vs transfer) | `transfer_data_to_therapist` |
| `quick_mood_check_in` | Solution-suggestive (implies app feature) | `routine_data_entry` |
| `monday_anxiety_tracking` | Temporal (specific day) | Not a scenario pattern — too narrow |
| `use_voice_input_feature` | Technology-specific (violates tech neutrality) | Describe the goal, not the tool |

### 5.6 Legacy Names

Existing scenarios already have folder names that predate these conventions. The index tracks both the **canonical name** and the **actual folder name** (`scenario_folder` field). Renaming existing folders is OUT OF SCOPE for this task and should be handled separately if desired.

## 6. Markdown Body Structure (Human-Readable Section)

Below the YAML frontmatter, the file contains a human-readable overview organized by lifecycle stage:

```markdown
# Scenario Index

## Overview
[Brief explanation of what this file is and how to use it]

## Therapy Data Lifecycle
[Visual diagram of the lifecycle stages]

## Patterns by Lifecycle Stage

### Stage: Create
#### prepare_protocol_for_client
- **Description**: ...
- **Roles**: therapist (primary)
- **Instances**: SCEN-001-01 (Dr. Sarah) ✅
- **Gaps**: self_user (edge case)

### Stage: Capture
...

## Coverage Matrix
[Table showing personas × patterns]

## Naming Quick Reference
[Condensed naming rules for skill integration]
```

## 7. Integration with `create-scenario` Skill

### 7.1 Validation Flow

When `create-scenario` is invoked:

1. **Read SCENARIO_INDEX.md** (parse YAML frontmatter)
2. **Ask user**: "What is this scenario about?" → map to existing pattern or identify as new
3. **If existing pattern**:
   - Suggest canonical folder name
   - Check if this persona already has an instance (warn if duplicate)
   - Pre-populate outcome field if relevant
4. **If new pattern**:
   - Ask user to define: canonical_name, description, lifecycle_stage, applicable_roles
   - Validate name follows convention ([action]_[object]_[qualifier])
   - Add new pattern entry to SCENARIO_INDEX.md YAML
5. **After scenario creation**: Update `instances` array in SCENARIO_INDEX.md

### 7.2 Gap Analysis / Suggestion

When invoked with "suggest missing scenarios for [persona]":

1. Read persona's role (therapist/client/self_user)
2. Filter patterns where `applicable_roles` includes this role
3. Check which patterns already have instances for this persona
4. List patterns WITHOUT instances → "These scenarios are missing for [persona]"
5. Include `predicted_instances` notes for context

### 7.3 Batch Generation Support

For Option F (Example-Driven Batch Generation):

1. User selects pattern from index
2. Skill shows existing gold-standard instance as example
3. Skill generates new instance for target persona, adapting context/details
4. Ensures folder name matches canonical_name (+ qualifier if needed)
5. Updates SCENARIO_INDEX.md with new instance

## 8. Maintenance Rules

1. **SCENARIO_INDEX.md is updated whenever**:
   - A new scenario is created (add instance)
   - A scenario is deleted or deprecated (remove/mark instance)
   - A new pattern is identified (add pattern)
   - A pattern is retired (mark deprecated, don't delete)

2. **Who updates it**:
   - `create-scenario` skill: automatically on scenario creation
   - Manual: when restructuring or discovering new patterns
   - `modify-user-needs` skill: when renaming scenarios

3. **Validation**:
   - All `scenario_id` references must point to existing scenario files
   - All `persona_id` references must point to existing persona files
   - `scenario_folder` must match actual folder name on disk
   - No duplicate `canonical_name` values across patterns

## 9. Open Questions for User

1. **Rename existing scenarios?** The analysis shows 3 of 6 scenarios have names inconsistent with the proposed convention. Should we create a separate task to rename them, or accept the legacy names and only enforce conventions going forward?

2. **Lifecycle stage granularity**: Is the proposed lifecycle (create → capture → prepare → transfer → review → reflect) the right granularity? Or should we use broader categories?

3. **Self-user patterns**: Should we pre-populate predicted patterns for self-user personas now, or wait until we actually write those scenarios?

4. **Index update automation**: Should updating the index be mandatory (skill refuses to create scenario without updating index) or advisory (skill suggests updating but allows skip)?
