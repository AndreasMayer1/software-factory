# Opus Plan: Phase 1 - User Needs Structure Foundation

## Objective

Create the `requirements_user_needs/` folder structure and comprehensive README.md that incorporates all best practices from the German appendix for mental health personas, scenarios, and user flows.

**Phase 1 Scope**: Foundation only (folder structure + README.md), no actual persona files.

## Analysis Summary

### Key Insights from Requirements Appendix (REQ-PROC-010)

The appendix contains 290+ lines of German-language best practices that MUST be incorporated:

**Personas (Lines 586-708)**:
1. Psychology over demographics ("Energiehaushalt und Scham-Grenze, nicht Alter")
2. Mental models ("Wie glaubt sie, dass das System funktioniert?")
3. Jobs to be Done (functional, emotional, social)
4. Emotional & physical context (triggers, stress levels, environment)
5. Tech ecosystem (digital fluency, anchor tools, device reality)
6. Friction & barriers (fears, inertia)
7. Anti-persona traits (what they are NOT)
8. Real quotes from user interviews
9. Mental health specific: energy budget, shame threshold, vulnerability hangover
10. Three example archetypes provided:
    - "Der High-Functioning Verdränger" (external RAM user)
    - "Der therapiebegleitende Musterschüler" (therapy companion)
    - "Der skeptische Selbst-Optimierer" (quantified self)

**Scenarios (Lines 710-794)**:
1. Scenarios ≠ Use Cases (stories with context, conflict, resolution)
2. Three-act structure:
   - Act 1: Context & Inciting Incident (physical state, cognitive load, trigger)
   - Act 2: Interaction & Resistance (obstacles, internal monologue)
   - Act 3: Result & Feeling (emotional change, next step)
3. State-of-the-art elements: privacy glitches, imperfection, micro-goals
4. Two detailed examples provided (brain dump, therapy preparation)
5. Checklist: time pressure, internal dialogue, errors, emotional goals

**User Flows (Lines 796-872)**:
1. Happy path vs. unhappy paths (exception model)
2. Main path + numbered exceptions structure
3. Local storage problems (not server errors): corruption, full storage, app kill
4. System errors vs. user errors
5. Recovery always leads back to happy path
6. "Moments of Truth": onboarding, core interaction, crisis
7. Adaptive UI based on state (mood < 3 → hide streaks, show crisis hotline)
8. Detailed table example with flow steps and edge cases

### Data Grounding Methodology (Required)

From lines 172, 232, 287 - Need standardized approach:
- **Evidence levels**: grounded | proto_persona | hypothesis
- **Inline markers**: `[Data-Grounded: source]`, `[Proto-Persona: assumption]`, `[Hypothesis: to validate]`
- **Commit hash references**: Because persona files evolve with data

### ID System

- `PERSONA-001`, `PERSONA-002`, ...
- `SCEN-001-01`, `SCEN-001-02`, ... (SCEN-[PERSONA_NUMBER]-[SEQUENCE])
- `FLOW-001-01-01`, `FLOW-001-01-02`, ... (FLOW-[SCEN_NUMBER]-[SEQUENCE])

## Execution Plan

### Agent 1: Implementation Engineer

Execute ALL steps in sequence:

#### Step 1: Create Folder Structure
```
mkdir requirements_user_needs
mkdir requirements_user_needs/personas
```

Verify: Both folders exist.

#### Step 2: Create Comprehensive README.md

Create `requirements_user_needs/README.md` with the following 10 sections (matching SEC-01 through SEC-10).

**CRITICAL**: Templates should be embedded as code blocks in README.md, not separate files (keeps everything in one authoritative place).

---

### README.md Content Specification

#### Section 1: Overview (SEC-01)
~50-60 lines

Content:
- **The Problem**: Implementation-focused structure lacks "why" (copy from lines 55-64)
- **The Solution**: New layer above epics with personas → scenarios → flows
- **Complete Hierarchy Diagram**: Show full chain from personas to tasks
- **Benefits**: Traceability, gap analysis, consistency, context, validation (lines 105-109)

Key quote to incorporate: "A single user flow can touch multiple epics, making it difficult to see the big picture."

#### Section 2: Folder Structure (SEC-02)
~40-50 lines

Content:
- **Visual tree** of `requirements_user_needs/` structure (copy from lines 115-151)
- **Naming conventions**:
  - Persona folders: `snake_case` (e.g., `dr_thomas`, `max_client`)
  - Scenario folders: `snake_case` describing goal (e.g., `pre_session_patient_review`)
  - Flow folders: `snake_case` describing approach (e.g., `quick_triage_view`)
- **Integration note**: How this relates to `requirements_tasks/`

#### Section 3: Persona Definition (SEC-03)
~120-150 lines (LONGEST SECTION - incorporates appendix wisdom)

Content structure:
1. **What is a Persona?** (basic definition)
2. **Why Demographics Are Not Enough** (translate appendix insight: "Bullshit-Bingo mit Stockfotos")
3. **The 7 Elements of an Effective Persona** (from appendix):
   - Mental Models & Expectations
   - Jobs to Be Done (functional, emotional, social)
   - Emotional & Physical Context (environment)
   - Tech Ecosystem & Competence
   - Friction & Barriers (fears, inertia)
   - Anti-Persona Traits
   - Real Quotes
4. **Mental Health Specific Requirements**:
   - Energy budget > demographics
   - Shame threshold
   - Vulnerability hangover
   - Adaptive UI needs
   - Example: "Mental state dictates UX requirements"
5. **Data Grounding Methodology**:
   - Evidence levels (grounded, proto_persona, hypothesis)
   - How to mark in content
   - Commit hash references
6. **Persona Template** (YAML frontmatter + markdown sections)
7. **Persona Writing Checklist**

Include example archetypes from appendix (translated to English):
- The High-Functioning Suppressor
- The Therapy Companion
- The Skeptical Self-Optimizer

#### Section 4: Scenario Definition (SEC-04)
~80-100 lines

Content structure:
1. **What is a Scenario?** (goal-oriented situation)
2. **Scenarios vs. Use Cases** (stories vs. technical steps)
3. **The Three-Act Structure** (from appendix):
   - Act 1: Context & Inciting Incident
   - Act 2: Interaction & Resistance
   - Act 3: Result & Feeling
4. **State-of-the-Art Elements**:
   - Privacy glitches
   - Imperfection and abandonment
   - Micro-goals
   - Internal monologue
5. **Scenario Template** (YAML frontmatter + markdown sections)
6. **Scenario Writing Checklist** (from appendix lines 785-793):
   - Contains time pressure or physical stressor?
   - Has internal dialogue?
   - Shows a failure/error?
   - Has emotional (not just functional) goal?

Include one translated example from appendix (brain dump scenario).

#### Section 5: User Flow Definition (SEC-05)
~100-120 lines

Content structure:
1. **What is a User Flow?** (how app solves scenario goal)
2. **Happy Path vs. Unhappy Paths**
3. **The Exception Model** (main path + numbered exceptions)
4. **Local Storage Edge Cases** (critical for this app):
   - Database corruption
   - Storage full
   - App kill during write
   - Accidental deletion
5. **System Errors vs. User Errors**
6. **Recovery Paths** (always lead back to happy path)
7. **Moments of Truth**:
   - Onboarding
   - Core interaction
   - Crisis response
8. **Adaptive UI Based on State** (mood < 3 example)
9. **User Flow Template** (YAML frontmatter + markdown with table format)
10. **Flow Writing Checklist**

Include table format example from appendix (lines 826-833).

#### Section 6: Meta Information Standards (SEC-06)
~40-50 lines

Content:
- **Persona YAML frontmatter** specification
- **Scenario YAML frontmatter** specification
- **User Flow YAML frontmatter** specification
- **ID generation rules**:
  - PERSONA-001, PERSONA-002, ... (sequential)
  - SCEN-[PERSONA_NUMBER]-[SEQUENCE]
  - FLOW-[SCEN_NUMBER]-[SEQUENCE]
- **Evidence level field** (new field for data grounding)
- **Version tracking** with `updated` field

#### Section 7: Cross-referencing System (SEC-07)
~50-60 lines

Content:
1. **From User Flows to Epics/Features** (downward references)
2. **From Epics/Features to User Flows** (upward references)
3. **Commit Hash References** (for evolving personas)
4. **Reference Format Examples**:
   - Simple: `[Dr. Thomas](personas/dr_thomas/persona.md)`
   - With commit: `[Dr. Thomas](personas/dr_thomas/persona.md) @ abc123f`
5. **Validation Rules for References**

#### Section 8: Skill Modifications (SEC-08)
~40-50 lines

Content:
1. **New Skills Needed**:
   - `create-persona`: Prompts, generates ID, creates file
   - `create-scenario`: Links to persona, generates ID
   - `create-user-flow`: Links to scenario, generates ID
2. **Modified Skills**:
   - `setup-task`: Check for user flow links
   - `verify-quality`: Validate references, check contradictions
   - `explore-requirements`: Read user needs first
3. **Note**: Implementation is separate task (Phase 4)

#### Section 9: Writing Guidelines (SEC-09)
~40-50 lines

Content:
1. **Language**: English (all files)
2. **Tone**: Professional, clear, empathetic
3. **Perspective by Document Type**:
   - Personas: Third person ("Dr. Thomas is...")
   - Scenarios: User perspective ("The therapist wants...")
   - Flows: Descriptive ("The app displays...")
4. **Psychology over Demographics** (reinforce)
5. **Concrete over Abstract** (real examples, not generic statements)
6. **The Golden Rule**: "A good persona/scenario makes you feel empathy, not boredom"

#### Section 10: Validation Rules (SEC-10)
~60-70 lines

Content as checklists:

1. **Structural Validation**:
   - [ ] All personas have `persona.md` with valid YAML
   - [ ] All scenarios have `scenario.md` with valid YAML and persona reference
   - [ ] All user flows have `flow.md` with valid YAML and scenario reference
   - [ ] ID uniqueness across all files

2. **Cross-reference Validation**:
   - [ ] User flows reference at least one epic/feature (warning)
   - [ ] User flows' references exist (error if broken)
   - [ ] Scenarios reference at least one user flow (warning)
   - [ ] Personas reference at least one scenario (warning)

3. **Content Validation**:
   - [ ] Epics/features should reference user flows (warning)
   - [ ] No contradictions with referenced user flows
   - [ ] Flows are high-level, epics are detailed (no duplication)

4. **Hierarchy Validation**:
   - Rule: Lower levels must never contradict higher levels
   - Examples of contradictions to avoid
   - Process: Check higher levels before creating lower levels

5. **Data Grounding Validation**:
   - [ ] Evidence level specified for new content
   - [ ] Proto-persona assumptions marked as such
   - [ ] Hypotheses marked for validation

---

### Step 3: Verify Quality

After creating README.md, verify:
- [ ] All 10 sections present (SEC-01 through SEC-10)
- [ ] ~550-700 total lines (comprehensive but not bloated)
- [ ] All appendix wisdom incorporated (psychology, JTBD, mental models, etc.)
- [ ] Templates included as code blocks
- [ ] Checklists provided (not just prose)
- [ ] Mental health specific guidance prominent
- [ ] Data grounding methodology defined
- [ ] Examples from archetypes included
- [ ] English language throughout

### Step 4: Log Completion

Use `log-protocol` skill to record:
- Files created
- Key decisions made
- Any questions for user review

## Quality Criteria

- [ ] `requirements_user_needs/` folder exists
- [ ] `requirements_user_needs/personas/` folder exists
- [ ] `requirements_user_needs/README.md` exists with 550+ lines
- [ ] All 10 required sections present
- [ ] Appendix wisdom incorporated throughout (not just referenced)
- [ ] Templates are code blocks (not separate files)
- [ ] Mental health specific guidance is prominent (energy budget, shame threshold)
- [ ] Data grounding methodology is clearly defined
- [ ] Three archetype examples included (translated from German)
- [ ] Writing checklists provided for personas, scenarios, flows
- [ ] Validation rules as checklists
- [ ] English language throughout (German appendix translated)

## Risks

1. **Risk**: README.md becomes too long and unwieldy
   - **Mitigation**: Target 550-700 lines, use collapsible sections if needed, focus on actionable content

2. **Risk**: Appendix wisdom gets lost in translation
   - **Mitigation**: Preserve key German terms as footnotes where useful (e.g., "Energiehaushalt" = energy budget)

3. **Risk**: Templates conflict with requirements.md examples
   - **Mitigation**: Use requirements.md as base, enhance with appendix insights

4. **Risk**: Data grounding methodology too complex
   - **Mitigation**: Start simple (3 levels), can expand later

## Dependencies

- None for Phase 1 (foundation only)

## Estimated Output

- `requirements_user_needs/` folder
- `requirements_user_needs/personas/` folder
- `requirements_user_needs/README.md` (~550-700 lines, all 10 sections)
- Protocol update with completion status

---

## Execution Instructions for Implementation Agent

1. Create folders using Bash
2. Write complete README.md in one pass (use Write tool)
3. Verify all sections present
4. Log completion with agent ID

**Model Recommendation**: Use Sonnet for implementation (straightforward writing task with clear specifications above).

---

**Plan Created By**: Opus
**Plan Date**: 2026-01-17
**Execution Agents Needed**: 1 (Implementation Engineer)
