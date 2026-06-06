# Opus Plan: Phase 4 - User Needs Structure Content Improvement

**Date**: 2026-01-18
**Phase**: 4 (Content Improvement)
**Status**: PLANNING
**Planner**: Opus (claude-opus-4-5-20251101)

---

## Objective

Implement the user's comprehensive feedback from `2026-01-18_12_user_instructions_phase_4.md`, which requires:

1. **Persona corrections** - Fix content issues (therapist persona rewrite, remove solutions from personas)
2. **Technology neutrality** - Remove implementation details from scenarios and user flows
3. **Document management system** - Implement review/approval workflow with YAML status tracking
4. **Cross-reference notation** - Define standardized referencing system between documents
5. **Deviation documentation** - Create mechanism to track when user flows can't fully satisfy needs
6. **Change propagation process** - Define how persona changes cascade through all layers
7. **Task placement strategy** - Determine where tasks for user_needs modifications should live
8. **Update requirements.md** - Reflect all structural changes

---

## Analysis Summary

### Key User Feedback (Translated from German)

**Therapist Persona (PERSONA-001) - Major Rewrite Required**:
- Change to female psychologist (psychological psychotherapist for behavioral therapy)
- Focus on anxiety protocols and typical VT protocols (not medication - that's for psychiatrist persona later)
- Remove "waiting room with patients" scenario - never happens
- Main scenarios: (1) Prepare plan for client, hand it out, instruct client; (2) Review filled plan with client, discuss patterns, identify influences on anxiety, assess therapy progress
- Therapist analyzes data WITH client (like paper protocol), not alone
- Must not accidentally see client list with real names

**Personas Contain Solutions - FORBIDDEN**:
- Current personas describe what the app does, not pre-software status quo
- Personas must only describe needs BEFORE the software exists
- Current state: Therapists use paper questionnaires (good for privacy, bad for filling/analysis)
- Paper requires carrying it + pen everywhere, easy to forget
- Analysis: overlaying anxiety protocols of different days is easier on screen than paper

**Technology Neutrality**:
- Scenarios and user flows must keep technology open
- Focus on WHAT users need and HOW interaction supports goals
- SQLite vs Flutter Hive storage = irrelevant and counterproductive
- Premature solution narrowing = bad
- User flows derived from scenarios is creative process with surprising solutions
- Example: If persona has need for physical closeness, social media app flow is NOT suggesting romantic content but reminding user to close app and seek real connection

**Gap Documentation**:
- User flows can't always satisfy all needs
- User flows to epics/features may require compromises (technical feasibility, effort)
- Changes must be conscious and reflected - does value still exist?
- Need standardized deviation documentation at specific locations in documents
- Perhaps use same reference mechanism as tasks referencing requirements

**Cross-Reference Notation**:
- Need general notation to reference content between files
- Similar to how tasks reference requirement sections (REQ-PROC-010#SEC-01)

**Review Status System**:
- Documents need review level (draft, approved, etc.)
- Collaborative work (user + LLM) requires bi-directional reviews
- Documents start as draft
- User wants to actively approve all documents before they're referenced
- Changes to approved documents reset status to review
- YAML entry for script readability
- Need status overview script (like STATUS.md for requirements_tasks)

**Apply Changes to ONE Persona First**:
- User wants to review result before applying to all
- May discover more issues when seeing the result

---

## Structural Changes Required

### 1. New YAML Fields for All User Needs Documents

```yaml
# For personas, scenarios, user flows
review_status: draft | in_review | approved | deprecated
review_history:
  - date: 2026-01-18
    from: draft
    to: in_review
    reviewer: LLM
    notes: "Initial creation"
  - date: 2026-01-19
    from: in_review
    to: approved
    reviewer: user
    notes: "Approved after corrections"
```

### 2. Cross-Reference Notation Standard

Format: `[DOC_TYPE]-[ID]#[SECTION]@[COMMIT]`

Examples:
- `PERSONA-001#mental_model@abc123` - Reference persona mental model section at specific commit
- `SCEN-002-01#privacy_glitch` - Reference scenario privacy glitch section (no commit = latest)
- `FLOW-002-01-01#step_5` - Reference specific flow step

For deviations/compromises:
```markdown
## Deviations from User Needs

| User Need Reference | Deviation | Reason | Value Impact |
|---------------------|-----------|--------|--------------|
| SCEN-002-01#success_criteria.3 | Cannot guarantee <10 min sleep | Technical: STT accuracy varies | Low - primary goal (externalization) still met |
```

### 3. Persona Structure Changes

**Remove** (solutions/implementation):
- "Implications for the App" sections that describe app features
- Technical references (SQLite, OLED, etc.)
- Flow steps that describe app behavior

**Add/Keep**:
- Status quo (how they work TODAY without the app)
- Pain points with current approach (paper, manual, etc.)
- What they need (not how app solves it)
- Environmental constraints (non-user threats) - KEEP but as context, not solution

### 4. Scenario Structure Changes

**Remove**:
- App behavior descriptions
- Technical implementation details
- System responses

**Keep/Add**:
- Goal (what user wants to achieve)
- Context (when, where, emotional state)
- Success criteria (outcome, not how achieved)
- Privacy considerations (the threat, not the solution)

### 5. User Flow Structure Changes

User flows ARE solution-oriented but must:
- Stay technology-agnostic (no SQLite, no specific storage)
- Describe interaction patterns, not implementation
- Allow for creative solutions
- Document deviations from scenario needs

---

## Execution Plan

### Agent 1: Structure & Standards Implementation

**Purpose**: Update README.md, create status script, update requirements.md

**Steps**:

1. **Update README.md** with new sections:
   - Review status system (YAML format, workflow description)
   - Cross-reference notation standard
   - Deviation documentation format
   - Updated persona/scenario/flow templates with new YAML fields
   - Section on technology neutrality principle
   - Section on "personas describe status quo, not solutions"

2. **Create status overview script** for user_needs:
   - Path: `scripts/generate_user_needs_status.py`
   - Reads all persona/scenario/flow YAML frontmatter
   - Outputs `requirements_user_needs/STATUS.md` showing:
     - Documents by review status (draft, in_review, approved)
     - Documents pending review
     - Cross-reference validation (broken links)

3. **Update requirements.md** (REQ-PROC-010):
   - Add new sections for:
     - SEC-11: Review Status System
     - SEC-12: Cross-Reference Notation
     - SEC-13: Deviation Documentation
     - SEC-14: Technology Neutrality Principle
   - Update version history

4. **Create task folder location guidance**:
   - Add to README.md: Tasks modifying user_needs content go in `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/`
   - This keeps tasks in requirements_tasks (existing script compatibility)
   - But clearly scoped to user_needs changes

**Quality Criteria**:
- [ ] README.md contains all new sections
- [ ] Status script runs without errors
- [ ] Requirements.md has new sections with SEC-11 through SEC-14
- [ ] Cross-reference notation is documented with examples

---

### Agent 2: Therapist Persona Rewrite (Single Persona Example)

**Purpose**: Rewrite PERSONA-001 (Dr. Thomas -> Dr. Sarah?) as model for others

**Steps**:

1. **Create new therapist persona** following user feedback:
   - Female psychologist (psychological psychotherapist, behavioral therapy)
   - Focus: anxiety protocols, VT protocols
   - Remove all app solutions
   - Describe status quo (paper questionnaires, locked filing cabinet)
   - Document pain points with paper (carrying, forgetting, analysis difficulty)
   - Two main scenarios:
     - Preparing plan for client + instructing client
     - Reviewing filled plan WITH client in session

2. **Add new YAML fields**:
   ```yaml
   review_status: draft
   review_history:
     - date: 2026-01-18
       from: null
       to: draft
       reviewer: LLM
       notes: "Rewritten per user feedback 2026-01-18_12"
   ```

3. **Rewrite scenarios for new therapist**:
   - Remove SCEN-001-01 (pre_session_patient_review) or adapt
   - Create scenario for "Preparing protocol plan for client"
   - Create scenario for "Reviewing filled protocol with client in session"
   - Remove technology-specific details
   - Keep success criteria outcome-focused

4. **Add deviation section** to existing user flow (if adapting):
   - Document any compromises from scenario needs
   - Use cross-reference notation

**Quality Criteria**:
- [ ] Persona describes status quo without app
- [ ] No technical implementation details in persona
- [ ] Scenarios describe goals, not app behavior
- [ ] New YAML fields present and valid
- [ ] Pain points with paper approach documented
- [ ] Two main scenarios exist (prepare + review with client)

---

### Agent 3: Change Propagation Process Documentation

**Purpose**: Document how changes cascade and create follow-up task

**Steps**:

1. **Create change propagation process document**:
   - Path: `requirements_user_needs/CHANGE_PROPAGATION.md`
   - Define cascade flow: Persona -> Scenario -> User Flow -> Epic -> Feature -> Task
   - For each transition:
     - What triggers change check
     - Who reviews (user vs LLM)
     - How to document impact
     - When to create tasks

2. **Define skill modifications needed** (documentation only):
   - `modify-persona` skill: Changes persona, triggers review of all child scenarios
   - `modify-scenario` skill: Changes scenario, triggers review of all child flows
   - `modify-user-flow` skill: Changes flow, checks epic/feature alignment
   - Each modification resets document to `in_review` status

3. **Create follow-up task** for remaining persona refinements:
   - Path: `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-XX_impl_refine_remaining_personas/goal.md`
   - References: user feedback file, new therapist persona as template
   - Scope: Apply same changes to Max, Sarah, System personas
   - Include scenario/flow cascade updates

**Quality Criteria**:
- [ ] Change propagation process documented
- [ ] Skill modifications specified (not implemented)
- [ ] Follow-up task created with proper YAML
- [ ] Task references source documents correctly

---

## Detailed Work Items by Agent

### Agent 1 Deliverables

| Item | File | Action |
|------|------|--------|
| README update | `requirements_user_needs/README.md` | Edit - add 5 new sections |
| Status script | `scripts/generate_user_needs_status.py` | Create new |
| Status output | `requirements_user_needs/STATUS.md` | Generated by script |
| Requirements | `.../user_needs_structure/requirements.md` | Edit - add SEC-11 to SEC-14 |

### Agent 2 Deliverables

| Item | File | Action |
|------|------|--------|
| Therapist persona | `requirements_user_needs/personas/dr_sarah/persona.md` | Create new (or heavy edit dr_thomas) |
| Scenario 1 | `.../dr_sarah/scenarios/prepare_client_protocol/scenario.md` | Create new |
| Scenario 2 | `.../dr_sarah/scenarios/review_protocol_with_client/scenario.md` | Create new |
| Old persona | `requirements_user_needs/personas/dr_thomas/` | Delete or archive |
| Old scenarios | `.../dr_thomas/scenarios/` | Delete or archive |

### Agent 3 Deliverables

| Item | File | Action |
|------|------|--------|
| Propagation doc | `requirements_user_needs/CHANGE_PROPAGATION.md` | Create new |
| Follow-up task | `.../tasks/2026-01-19_impl_refine_remaining_personas/goal.md` | Create new |
| Skill spec | Document in propagation doc | Part of propagation doc |

---

## Quality Criteria (Overall)

### Structural Quality
- [ ] All new YAML fields documented in README
- [ ] Status script generates valid STATUS.md
- [ ] Cross-reference notation has clear examples
- [ ] Deviation documentation format is clear

### Content Quality
- [ ] Therapist persona describes pre-software status quo
- [ ] No app features described in persona
- [ ] Scenarios are goal-oriented, not solution-oriented
- [ ] Pain points with paper approach are concrete

### Process Quality
- [ ] Change propagation process is actionable
- [ ] Follow-up task references all source documents
- [ ] Review status workflow is clear

### Traceability
- [ ] requirements.md reflects all structural changes
- [ ] README updates match requirements.md
- [ ] Follow-up task covers remaining personas

---

## Risks and Mitigations

### Risk 1: Scope Creep
**Description**: Phase 4 has many items; may try to do everything at once
**Mitigation**: User explicitly asked for ONE persona first. Agent 2 stops after therapist persona. Agent 3 creates task for rest.

### Risk 2: Existing Documents Inconsistency
**Description**: Max, Sarah, System personas still have old format after Agent 2 completes
**Mitigation**: Acceptable - follow-up task handles this. User wants to review one first.

### Risk 3: Status Script Complexity
**Description**: Script may be complex with cross-reference validation
**Mitigation**: MVP script: just read YAML and list by status. Cross-ref validation in v2.

### Risk 4: User Flow Technology Details
**Description**: Existing flows (FLOW-002-01-01, FLOW-003-01-01) have SQLite/OLED references
**Mitigation**: Out of scope for Phase 4 - focus on therapist persona/scenarios. Flows updated in follow-up task.

### Risk 5: Breaking Existing References
**Description**: Renaming dr_thomas to dr_sarah may break references
**Mitigation**: Use search/replace across codebase, or keep dr_thomas folder but update content to female persona.

---

## Execution Order

```
[Agent 1] ──┬──> README.md, Status Script, requirements.md
            │
[Agent 2] ──┼──> Therapist Persona + Scenarios (waits for README if needed)
            │
[Agent 3] ──┴──> Change Propagation Doc, Follow-up Task (can run parallel)
```

**Dependencies**:
- Agent 2 should read updated README (from Agent 1) for new YAML format
- Agent 3 can run in parallel with Agent 2 (documentation work)
- All agents should use the cross-reference notation once Agent 1 defines it

**Recommended**: Run Agent 1 first, then Agent 2 + Agent 3 in parallel.

---

## Protocol for This Plan

When executing:
1. Each agent logs to `plans_and_protocols/2026-01-18_14_protocol_phase4_[agent].md`
2. Mark this plan as executed after all agents complete
3. User review required after Agent 2 (therapist persona)

---

## Summary

**Total Agents Needed**: 3

| Agent | Focus | Deliverables |
|-------|-------|--------------|
| Agent 1 | Structure & Standards | README, Script, requirements.md |
| Agent 2 | Therapist Persona Example | 1 persona, 2 scenarios (rewritten) |
| Agent 3 | Process & Follow-up | Propagation doc, follow-up task |

**Estimated Effort**: Medium-Large (significant documentation + 1 complete persona rewrite)

**User Checkpoint**: After Agent 2 completes - user reviews therapist persona before proceeding with other personas.

---

**Plan Status**: Ready for execution
**Created**: 2026-01-18
**Planner**: Opus (claude-opus-4-5-20251101)
