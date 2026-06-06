---
task_id: TASK-PROC-010-12
type: explore
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-02-05
completed: 2026-02-06
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections:
    - SEC-04  # Scenario Definition
    - SEC-09  # Writing Guidelines
scope_description: "Create a centralized scenario index/catalog to prevent naming chaos when generating similar scenarios across multiple personas, and establish naming conventions for cross-persona scenario consistency"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
use_opus: true
---

# Goal: Create Scenario Index and Naming Conventions

## Objective

Create a systematic index/catalog of scenario types to ensure consistent naming and prevent chaos when generating similar scenarios across multiple personas.

**Problem**: As we batch-generate scenarios using Option F (Example-Driven Batch Generation), we'll create the "same" scenario (e.g., "successful protocol handover") for multiple personas. Without standardized naming, we risk:
- Inconsistent names: "successful_protocol_handover" (Persona A) vs "protocol_handover" (Persona B)
- Missing scenarios: No way to see which personas have which scenario types
- Duplication confusion: Multiple variations of the same scenario pattern with different names

**Solution**: Create a **Scenario Index** - a centralized table/registry that:
1. Lists all scenario archetypes/patterns with canonical names
2. Shows which persona roles each pattern applies to (therapist, client, self-user)
3. Tracks which personas have implemented each pattern
4. Provides abstract descriptions to guide generation

## Requirements Summary

From REQ-PROC-010:
- SEC-04: Scenario Definition guidelines and structure
- SEC-09: Writing Guidelines for consistency

**Context from user feedback** (2026-02-05):
> "Wir werden für mehrere Personas die 'gleichen' Szenarien anlegen. Gleich natürlich nur in den Grundzügen. Zum Beispiel ein successful protocol handover Szenario. Wir müssen darauf achten, dass hierbei kein Chaos entsteht, also zum Beispiel das successful protocol handover Szenario bei Persona A 'successful protocol handover' heißt und bei Persona B 'protocol handover'. Wie stellen wir das sicher? Sollen wir eine Szenerio Index erstellen, also eine Tabelle mit den Szenarien, die es gibt mit Name und kleiner abstrakten Inhaltsangabe und für welche Persona Rollen das Szenario Sinn macht (therapeut, klient, selbstnutzer)? Ja mir gefällt die Idee."

For complete requirements at task creation time:
```
git show 08f8e76:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

**Exploration Phase** (this task):
1. **Analyze existing scenarios** to identify patterns:
   - 6 existing gold standard scenarios (4 original + 2 new)
   - What patterns emerge? (prepare, review, capture, transfer, etc.)
   - What variations exist within each pattern?

2. **Design scenario index structure**:
   - Table format or markdown registry?
   - Location: `requirements_user_needs/` root or subfolder?
   - Fields: canonical_name, abstract_description, applicable_roles, status, notes
   - Versioning: How to track as new patterns emerge?

3. **Define naming conventions**:
   - Pattern: `[action]_[object]_[context]` (e.g., `successful_protocol_handover`)
   - Negative cases: How to name failure scenarios? (e.g., `forgotten_protocol_transfer`)
   - Variations: How to distinguish similar patterns? (e.g., `prepare_protocol_before_session` vs `prepare_protocol_during_session`)

4. **Propose integration with batch generation**:
   - How does the create-scenario skill use the index?
   - Validation: Check if new scenario name matches index entry
   - Discovery: Suggest missing scenarios from index

5. **Create prototype index** with current 6+ scenarios

**Implementation** (separate task or include here):
- Create the actual SCENARIO_INDEX.md file
- Update README_4 to reference the index
- Update create-scenario skill to validate against index

### Out of Scope

- Retroactively renaming existing scenarios (handled separately if needed)
- Creating scenario archetypes/templates (Option E - already decided against)
- User flow indexing (separate concern)

## Acceptance Criteria

- [ ] Analysis document showing scenario patterns identified from existing 6+ scenarios
- [ ] Proposed scenario index structure (table format, fields, location)
- [ ] Naming convention rules documented (with examples and counter-examples)
- [ ] Prototype SCENARIO_INDEX.md created with current scenarios
- [ ] Integration plan for create-scenario skill
- [ ] User approval of proposed structure before implementation

## Deliverables

1. **Analysis document**: `plans_and_protocols/[date]_01_scenario_pattern_analysis.md`
   - Lists all existing scenarios
   - Groups by pattern
   - Identifies canonical names

2. **Design proposal**: `plans_and_protocols/[date]_02_index_design_proposal.md`
   - Index structure
   - Naming conventions
   - Integration approach
   - Examples

3. **Prototype index**: `plans_and_protocols/[date]_03_prototype_scenario_index.md`
   - Actual index with current scenarios
   - Ready for user review

## Approach

**Use Opus for exploration and design**:
1. Read all 6 existing gold standard scenarios
2. Identify underlying patterns (not just filenames - the actual scenario purposes)
3. Design index structure that's:
   - Easy to maintain (low friction for updates)
   - Easy to query (can we find scenarios by role/pattern?)
   - Flexible (can accommodate new patterns)
4. Propose naming conventions that are:
   - Consistent (same pattern = same structure)
   - Descriptive (name tells you what the scenario is)
   - Unambiguous (no confusion between similar scenarios)
5. Show examples and get user approval

## Scenario Patterns Observed So Far

From the 6 gold standards:
1. **Therapist prepares homework** (Dr. Sarah) - prepare_protocol_for_client
2. **Therapist reviews with client** (Dr. Sarah) - review_protocol_with_client
3. **Client captures data spontaneously** (Max) - brain_dump_at_night
4. **Client transfers data (failure)** (Max) - forgotten_protocol_transfer
5. **Client prepares for session** (Max) - prepare_for_therapy_session
6. **Client transfers data (success)** (Sophie) - successful_protocol_handover

**Observed patterns**:
- **Prepare** (therapist homework, client pre-session)
- **Capture/Record** (client data entry)
- **Transfer/Handover** (client to therapist, success vs failure)
- **Review** (therapist with client, client alone)

**Open questions**:
- Should success/failure be in the name or metadata?
- How granular should patterns be?
- Are there persona-specific variations that need distinction?

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-010-11 | pending | Scenario fixes in progress |
| 6 gold standard scenarios | exists | Source data for pattern analysis |
| README_4_SCENARIO_DEFINITION.md | exists | Will be updated with index reference |

## Notes

**User preference**:
- Likes the scenario index idea
- Wants to prevent naming chaos across personas
- Index should include: name, abstract description, applicable roles

**Integration opportunity**:
- create-scenario skill could validate names against index
- Could suggest missing scenarios from index during batch generation

**Future value**:
- Index becomes a requirements artifact (shows what user scenarios we're covering)
- Can derive app feature requirements from scenario patterns
- Enables gap analysis (which persona roles lack which patterns?)

**Design consideration**:
- Index should be lightweight enough that updating it isn't a burden
- But structured enough that tools can parse it (YAML? Markdown table?)
