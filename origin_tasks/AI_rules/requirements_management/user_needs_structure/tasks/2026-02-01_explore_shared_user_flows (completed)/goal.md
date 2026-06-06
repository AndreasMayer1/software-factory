---
task_id: TASK-PROC-010-08
type: explore
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-02-01
completed: 2026-02-01
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections:
    - SEC-02  # Folder Structure
    - SEC-05  # User Flow Definition
    - SEC-08  # Skill Modifications
scope_description: "Restructure user flows to be shared across personas/scenarios, eliminating duplication while keeping personas and scenarios persona-specific"
requirements_version:
  commit: 08f8e76
  file: ../requirements.md
---

# Goal: Restructure User Needs to Support Shared User Flows

## Objective

Redesign the user needs folder structure and related tooling to eliminate duplicate user flows by making them shared across multiple personas and scenarios, while keeping personas and scenarios persona-specific.

## Requirements Summary

**The Problem Identified:**
The current structure nests user flows under individual personas:
```
personas/dr_sarah/scenarios/hand_out_plan/user_flows/hand_out_flow/
personas/dr_thomas/scenarios/hand_out_plan/user_flows/hand_out_flow/
```

This creates nearly identical user flows when different personas have similar scenarios (e.g., "hand out questionnaire plan"). The app will only have ONE workflow implementation, so writing separate user flows for each persona leads to:
- **Duplication**: Same flow described multiple times with minor variations
- **Maintenance burden**: Changes must be synchronized across multiple files
- **Inconsistency risk**: Flows can diverge over time
- **Harder implementation mapping**: One epic/feature maps to N nearly-identical flows

**The Proposed Solution:**
Keep personas and scenarios (valuable for understanding different user perspectives), but extract user flows to be shared:
```
personas/dr_sarah/scenarios/hand_out_plan/ → references FLOW-XXX
personas/dr_thomas/scenarios/hand_out_plan/ → references FLOW-XXX
user_flows/hand_out_plan/ → THE single source of truth (works for both personas)
```

One user flow serves multiple scenarios from different personas. Example: ONE "Hand out questionnaire plan" user flow that works for Dr. Sarah, Dr. Thomas, AND their respective client scenarios.

For complete requirements at task creation time:
```
git show 08f8e76:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
1. **Analyze current structure**: Understand existing personas/scenarios/user_flows and identify duplication
2. **Design new folder structure**: Propose new organization for shared user flows
3. **Update file format specifications**: Modify user flow format to support multi-persona/multi-scenario references
4. **Identify skill changes needed**: Document required changes to `create-user-flow`, `modify-user-needs`, and related skills
5. **Assess merge script impact**: Determine if `merge_user_needs.py` (or similar) needs updates
6. **Plan content migration**: Strategy for migrating existing user flows to new structure
7. **Update cross-referencing system**: How scenarios reference flows and vice versa

### Out of Scope
- Actual implementation of skill changes (separate impl task)
- Migration of existing content (separate impl task)
- Creation of new user flows (content creation task)

## Acceptance Criteria

- [ ] New folder structure designed and documented
- [ ] User flow file format updated to reference multiple scenarios/personas
- [ ] Scenario file format updated to reference shared user flows
- [ ] All affected skills identified with required changes documented
- [ ] Merge script impact assessed
- [ ] Migration strategy defined for existing content
- [ ] Updated documentation reviewed and approved by user

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-010 | implemented | Parent requirement |
| Existing personas | complete | Need to analyze for common scenarios |

## Impact Analysis

**Affected Files/Systems:**
- `requirements_user_needs/README*.md` files (structure documentation)
- `requirements_user_needs/personas/` structure
- Skills: `create-user-flow`, `modify-user-needs`, potentially `create-scenario`
- Merge script: `scripts/merge_user_needs.py` (if exists)
- Cross-referencing notation (SEC-12)
- Validation rules (SEC-10)

**Benefits:**
- Eliminates duplicate user flow content
- Single source of truth for each workflow
- Easier to maintain and update flows
- Clearer epic/feature → flow mapping (1:1 instead of 1:N)
- Better reflects implementation reality (one workflow in app)

## Notes

**Key Design Questions to Answer:**
1. Where do shared user flows live? (New top-level `user_flows/` folder? Separate from personas?)
2. How do scenarios reference shared flows? (YAML frontmatter? Markdown links?)
3. How do flows reference multiple scenarios? (Reverse mapping)
4. How does versioning work when flows are shared? (One flow changes → affects multiple scenarios)
5. What happens to flow IDs? (Currently FLOW-[SCEN_ID]-[NUMBER] - needs rethinking)
6. How do we handle flow variations? (When 95% same but 5% differs per persona?)

**User's Context:**
- Just completed creating therapist and client personas
- Noticed during that work that scenarios/flows will be very similar across personas
- Wants to prevent duplication before creating more content
- Example given: "Hand out questionnaire plan" workflow is identical regardless of which therapist persona or client persona is involved
