---
task_id: TASK-PROC-010-02
type: impl
parent_requirement: REQ-PROC-010
urgency: 4
urgency_reason: U4-QUAL
impact: 4
impact_reason: I4-CORE
status: completed
effort: L
created: 2026-01-19
completed: 2026-01-18
after: []
awaiting: []
covers:
  sections: [SEC-01, SEC-02, SEC-11, SEC-12, SEC-14, SEC-15]
scope_description: "Apply Phase 4 persona refinements to remaining personas (Max, Sarah, System) using Dr. Sarah therapist persona as template"
requirements_version:
  commit: f95f611841ad397f909dde5d7f8be94b0fbf933a
  file: ../requirements.md
  note: "Phase 4: Content Improvement requirements"
user_needs_references:
  template: PERSONA-001
  affected: [PERSONA-002, PERSONA-003, PERSONA-004]
---

# Goal: Refine Remaining Personas Based on Phase 4 Standards

## Objective

Apply the improvements and standards from Phase 4 to the remaining personas (Max, Sarah, System), using the rewritten therapist persona (Dr. Sarah) as a template.

**Key Changes to Apply**:
1. **Remove Solutions**: Personas must describe status quo before the app, not app features
2. **Technology Neutrality**: No implementation details (SQLite, Flutter, etc.)
3. **Add Review Status**: Include review_status and review_history YAML fields
4. **Update Scenarios**: Ensure scenarios are goal-oriented, not app-behavior descriptions
5. **Update User Flows**: Remove technology-specific details, maintain interaction patterns only
6. **Document Deviations**: Add deviation tables where flows cannot fully satisfy scenario needs

## Context & References

### User Feedback Source

**Reference**: `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-18_12_user_instructions_phase_4.md`

**Key User Instructions** (translated from German):
- Personas currently contain solutions (forbidden) - must only describe needs BEFORE software exists
- Scenarios and user flows must keep technology open (no SQLite, no Flutter references)
- Documents need review status tracking (YAML entries)
- Changes to one persona first, review result before applying to all

### Template Reference

**Reference**: `PERSONA-001` (Dr. Sarah, Therapist)

**Created in**: Phase 4 Agent 2 work
**Status**: Should be reviewed and approved by user before using as template
**Location**: `requirements_user_needs/personas/dr_sarah/persona.md`

**What to replicate**:
- Structure: Status quo description instead of app features
- YAML: review_status and review_history fields
- Scenarios: Goal-oriented, not app-behavior
- Technology Neutrality: No implementation details in persona, scenarios, or flows
- Pain Points: Concrete, specific to current (pre-app) workflow

### Standards References

**README.md Sections**:
- Section 12: Review Status System → YAML format and workflow
- Section 13: Cross-Reference Notation → How to reference between documents
- Section 14: Deviation Documentation → Format for documenting compromises
- Section 15: Technology Neutrality Principle → What to avoid, what to include

**requirements.md Sections**:
- SEC-11: Review Status System
- SEC-12: Cross-Reference Notation
- SEC-14: Technology Neutrality Principle

### Change Propagation Process

**Reference**: `requirements_user_needs/CHANGE_PROPAGATION.md`

**Relevant Sections**:
- "Persona Modification" cascade process
- "Review Status Workflow"
- "Change Impact Analysis Template"

## Scope

### In Scope

**For each persona (Max, Sarah, System)**:

1. **Persona File Updates**:
   - Add review_status and review_history YAML fields
   - Remove "Implications for the App" or similar solution sections
   - Rewrite to describe status quo (pre-app) not app features
   - Remove technology references (databases, frameworks, etc.)
   - Keep environmental constraints but as context, not solutions
   - Add concrete pain points with current (pre-app) approach
   - Set review_status to `draft` initially

2. **Scenario Updates**:
   - Review all scenarios for each persona
   - Remove app behavior descriptions
   - Focus on goals, context, success criteria (outcome-focused)
   - Remove technical implementation details
   - Add review_status YAML fields
   - Update scenarios to align with persona changes

3. **User Flow Updates**:
   - Remove technology-specific details (SQLite, OLED, Material 3, etc.)
   - Keep interaction patterns (what user does, what system responds)
   - Stay technology-agnostic (describe behavior, not implementation)
   - Add deviation tables if flows cannot fully satisfy scenario needs
   - Add review_status YAML fields

4. **Change Documentation**:
   - Follow change propagation process from CHANGE_PROPAGATION.md
   - Document all changes in review_history
   - Reference affected child documents (scenarios/flows)
   - Create change impact analysis for each persona

### Personas to Update

1. **PERSONA-002: Max (Client with Depression/ADHD)**
   - Current location: `requirements_user_needs/personas/max/`
   - Focus: Remove app solution descriptions, describe current coping mechanisms
   - Scenarios: Focus on barriers, motivation, accessibility needs
   - Key change: Describe what Max does NOW (before app), not what app does for Max

2. **PERSONA-003: Sarah (Self-User)**
   - Current location: `requirements_user_needs/personas/sarah/`
   - Focus: Autonomy and insight needs in current (pre-app) context
   - Scenarios: Self-management goals, not app features
   - Key change: What does Sarah do for self-tracking now? What's painful about current methods?

3. **PERSONA-004: System/Maintenance**
   - Current location: `requirements_user_needs/personas/system/`
   - Focus: Non-user constraints (emergency contacts, data retention, etc.)
   - This is not a user persona, so may need different structure
   - Key change: Ensure described as constraints on system, not app features

### Out of Scope

- Creating new personas (only refining existing ones)
- Modifying epics/features (create separate tasks if needed)
- Implementing skills mentioned in CHANGE_PROPAGATION.md (separate task)
- Backfilling references in existing code (separate task)
- User approval of changes (happens after task completion)

## Acceptance Criteria

**For Each Persona**:
- [ ] YAML frontmatter includes review_status and review_history
- [ ] Initial review_status set to `draft`
- [ ] Persona describes status quo (pre-app) not app features
- [ ] No "Implications for the App" or similar solution sections
- [ ] No technology-specific references (SQLite, Flutter, frameworks)
- [ ] Pain points describe current (pre-app) workflow issues
- [ ] Environmental constraints kept as context, not solutions

**For Each Scenario**:
- [ ] YAML frontmatter includes review_status and review_history
- [ ] Scenarios describe goals and context, not app behavior
- [ ] Success criteria are outcome-focused, not implementation-focused
- [ ] No technical details (databases, UI frameworks, etc.)
- [ ] Aligned with parent persona changes

**For Each User Flow**:
- [ ] YAML frontmatter includes review_status and review_history
- [ ] Technology-specific details removed (SQLite, OLED, Material 3, etc.)
- [ ] Interaction patterns preserved (user action → system response)
- [ ] Deviation tables added if flow cannot fully satisfy scenario
- [ ] Aligned with parent scenario changes

**Overall**:
- [ ] Change impact analysis completed for each persona
- [ ] All affected documents (scenarios, flows) identified
- [ ] Review history documents what changed and why
- [ ] Cross-references use proper notation (from Section 13)
- [ ] Technology neutrality verified (checklist from Section 15)

## Implementation Steps

1. **Preparation**:
   - Read user feedback file (2026-01-18_12_user_instructions_phase_4.md)
   - Read Dr. Sarah persona as template (PERSONA-001)
   - Read CHANGE_PROPAGATION.md for process guidance
   - Read README sections 12-15 for standards

2. **For Each Persona** (Max, Sarah, System):
   - Create change impact analysis using template from CHANGE_PROPAGATION.md
   - Update persona.md:
     - Add review_status YAML fields
     - Remove solution sections
     - Rewrite to describe status quo
     - Remove technology references
     - Add concrete pain points
   - Identify all child scenarios
   - Update each scenario.md:
     - Add review_status YAML fields
     - Rewrite to be goal-oriented
     - Remove app behavior descriptions
   - Identify all child user flows
   - Update each flow.md:
     - Add review_status YAML fields
     - Remove technology specifics
     - Add deviation tables if needed
   - Document all changes in review_history

3. **Verification**:
   - Run status script: `python scripts/generate_user_needs_status.py`
   - Verify all modified documents show `draft` status
   - Check cross-references are valid
   - Verify no technology-specific terms remain (SQLite, Flutter, etc.)
   - Run technology neutrality checklist (Section 15)

4. **Documentation**:
   - Log all changes to protocol.md
   - List all modified files
   - Create summary of changes by persona
   - Note any deviations or issues for user review

5. **User Review Preparation**:
   - Set all modified documents to `in_review` status
   - Generate summary report for user
   - List any questions or unclear items

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Phase 4 Agent 1 | complete | README and requirements.md updated with standards |
| Phase 4 Agent 2 | pending user review | Dr. Sarah persona created as template |
| Phase 4 Agent 3 | complete | CHANGE_PROPAGATION.md created |

**Important**: Wait for user review and approval of Dr. Sarah persona (PERSONA-001) before starting this task. The template must be validated first.

## Notes

### Key Insight from User Feedback

> "Personas must only describe what they currently, before the introduction of the software, need. The status quo."

This is the fundamental shift: personas are NOT about what the app does, but about:
- What users do NOW (before the app)
- What's painful about current methods
- What they need (not how app solves it)

### Example Transformation

**Before** (solution-focused):
```markdown
## Implications for the App
- App uses encrypted SQLite database
- OLED dark mode for night usage
- Voice-to-text for quick entry
```

**After** (status quo-focused):
```markdown
## Current Status Quo (Pre-App)
- Uses paper journal (good for privacy, bad for portability)
- Must carry journal + pen everywhere (often forgotten)
- Writing in dark is difficult (wakes partner)
- Typing on phone keyboard is slow and loud

## Pain Points
- Physical tracking: Easy to lose, forget at home
- Night usage: Can't write in dark without waking partner
- Speed: Typing takes too long when experiencing anxiety
```

### Technology Neutrality Examples

**Forbidden in Personas/Scenarios**:
- "SQLite database"
- "Flutter framework"
- "Material 3 design"
- "Firebase backend"
- "OLED screen"
- "BLoC pattern"

**Allowed in User Flows** (interaction patterns):
- "Touch interaction"
- "Voice input"
- "Visual display"
- "Offline capability"
- "Privacy-preserving storage"
- "Quick access"

### Change Propagation Example

When updating Max's persona:
1. Update `personas/max/persona.md` → status: `draft`
2. Identify scenarios: `personas/max/scenarios/*/scenario.md`
3. For each scenario → status: `in_review`, note: "Parent persona updated"
4. Identify flows: `personas/max/scenarios/*/user_flows/*/flow.md`
5. For each flow → status: `in_review`, note: "Cascade from persona change"
6. Document in persona review_history: "Affected: SCEN-002-01, SCEN-002-02, FLOW-002-01-01"

## Success Metrics

- All 3 personas (Max, Sarah, System) updated with status quo descriptions
- All child scenarios and flows updated to align
- No technology-specific references remain
- All documents have review_status tracking
- Technology neutrality checklist passes for all documents
- User can easily review changes (clear change summaries)

## Related Documents

- **User Feedback**: `plans_and_protocols/2026-01-18_12_user_instructions_phase_4.md`
- **Template**: `PERSONA-001` (Dr. Sarah)
- **Process Guide**: `requirements_user_needs/CHANGE_PROPAGATION.md`
- **Standards**: `requirements_user_needs/README.md` (Sections 12-15)
- **Requirements**: `requirements.md` (SEC-11, SEC-12, SEC-14, SEC-15)
