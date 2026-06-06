# Opus Plan: Phase 3 - Initial Content Creation

**Date**: 2026-01-17
**Agent**: Opus (planning)
**Agent ID**: opus-plan-002
**Phase**: 3 (Initial Content Creation)

---

## Objective

Create initial persona files, example scenarios, and user flows using the templates and best practices defined in Phase 1-2. Transform the German appendix personas and requirements_general_overview content into structured English files that demonstrate proper usage of the templates.

---

## Analysis Summary

### Available Context

1. **Templates** (from README.md):
   - Persona template with 7 elements, YAML frontmatter, data grounding methodology
   - Scenario template with 3-act structure, state-of-the-art elements
   - User flow template with exception model, adaptive UI rules

2. **German Appendix Personas** (from requirements.md appendix):
   - **Persona 1**: "High-Functioning Verdränger" - Uses app as external RAM for brain dumps before sleep
   - **Persona 2**: "Therapiebegleitender Musterschüler" - Therapy companion who wants to make therapy efficient
   - **Persona 3**: "Skeptischer Selbst-Optimierer" - Quantified self user who wants correlations and insights

3. **Requirements Mapping** (from requirements_general_overview):
   - **Therapist** (Dr. Thomas): Data protection, questionnaire management, client management, efficient workflows
   - **Client** (Max): Simple UI, low friction, questionnaires, reminders, data privacy
   - **Self-User** (Sarah): Self-reflection, custom plans, data analysis, autonomy

4. **App Features**:
   - Privacy-first (local storage, encryption, PIN/password)
   - Questionnaire-based tracking
   - Data visualization
   - Therapist-client data transfer
   - Backup/export functionality

### Key Insights

The German appendix provides rich psychological details (mental models, JTBD, barriers, anti-traits) that perfectly align with the template structure. The requirements_general_overview provides functional requirements that ground the personas in real app capabilities.

**Critical decision**: Align personas with app roles:
- Persona 1 (Dr. Thomas) → Therapist role
- Persona 2 (Max) → Client role
- Persona 3 (Sarah) → Self-User role
- Persona 4 (System/Maintenance) → Technical persona (edge cases, migrations, errors)

---

## Execution Plan

### Agent 1: Content Creation (Implementation Engineer)

**Purpose**: Create persona files, scenario files, and user flow files following templates exactly.

#### Step 1: Create Persona Files (All 4)

Create folder structure and persona.md files for:

1. **PERSONA-001: Dr. Thomas (Therapist)**
   - Folder: `requirements_user_needs/personas/dr_thomas/`
   - File: `persona.md`
   - Map German "High-Functioning Verdränger" insights → Therapist context
   - Mental model: "App is my professional tool for efficient client management"
   - JTBD: Prepare for sessions efficiently, maintain data security, reduce administrative overhead
   - Tech ecosystem: Desktop + mobile, expects professional software UX
   - Evidence level: `proto_persona` (based on requirements + German archetype translation)
   - Include mental health specific: Energy budget (high stress, time pressure), privacy paranoia (GDPR compliance critical)

2. **PERSONA-002: Max (Client with Depression/ADHD)**
   - Folder: `requirements_user_needs/personas/max_client/`
   - File: `persona.md`
   - Map German "Therapiebegleitender Musterschüler" insights → Client context
   - Mental model: "App is my therapy assistant/medical record"
   - JTBD: Track patterns for therapy, avoid wasting therapy time, manage symptoms
   - Tech ecosystem: Mobile-first, needs simple/forgiving UI
   - Evidence level: `proto_persona`
   - Include mental health specific: Energy budget (depression = low energy, ADHD = needs low friction), shame threshold (fear of "bad patient" label), vulnerability hangover

3. **PERSONA-003: Sarah (Self-User)**
   - Folder: `requirements_user_needs/personas/sarah_self_user/`
   - File: `persona.md`
   - Map German "Skeptischer Selbst-Optimierer" insights → Self-user context
   - Mental model: "App is my dashboard/spreadsheet for life"
   - JTBD: Find correlations, optimize habits, gain self-insight
   - Tech ecosystem: Tech-savvy, expects data viz, wants CSV export
   - Evidence level: `proto_persona`
   - Include anti-traits: NOT in acute distress, NOT interested in therapy relationship, allergic to "woo-woo"

4. **PERSONA-004: System/Maintenance (Technical Persona)**
   - Folder: `requirements_user_needs/personas/system_maintenance/`
   - File: `persona.md`
   - This is a non-human persona representing technical edge cases
   - Mental model: N/A (system perspective)
   - JTBD: Handle device migrations, crashes, database corruption, storage issues
   - Coverage: All edge cases that don't fit user personas (OS updates, low storage, power loss during write, etc.)
   - Evidence level: `grounded` (based on technical requirements)

**Quality Criteria for Personas**:
- [ ] All YAML frontmatter fields present and valid
- [ ] All 7 elements included (mental models, JTBD, context, tech, barriers, anti-traits, quotes)
- [ ] Mental health specific fields populated (energy budget, shame threshold, vulnerability hangover)
- [ ] Evidence level markers used inline (🟢, 🟡, 🔴)
- [ ] English language throughout
- [ ] Persona writing checklist from README satisfied (11 items)

#### Step 2: Create Example Scenarios (At Least 1, Recommend 3)

Create scenario files for different personas to demonstrate variety:

**SCENARIO 1: SCEN-001-01 - Pre-Session Patient Review (Dr. Thomas)**
- Folder: `requirements_user_needs/personas/dr_thomas/scenarios/pre_session_patient_review/`
- File: `scenario.md`
- Goal: Quickly review client's week before session to prepare talking points
- Context: 10 minutes before session, in office, time pressure, needs overview
- 3-Act Structure:
  - Act 1: Between sessions, therapist realizes next client is in 10 minutes, hasn't reviewed data yet
  - Act 2: Opens app, navigates to client dashboard, scans for patterns/red flags, makes mental notes
  - Act 3: Feels prepared, confident to start session with specific questions
- Include: Time pressure, privacy glitch (colleague walks by screen), micro-goal (quick triage vs. deep analysis)
- Evidence level: `proto_persona`

**SCENARIO 2: SCEN-002-01 - Brain Dump at Night (Max)**
- Folder: `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/`
- File: `scenario.md`
- Goal: Offload circular thoughts to enable sleep
- Context: 1 AM, lying in bed, anxious about tomorrow, can't sleep, partner sleeping nearby
- 3-Act Structure (use German appendix example):
  - Act 1: Lying in dark, thoughts racing, doesn't want to wake partner
  - Act 2: Opens app in dark mode, whispers into voice-to-text, sees privacy indicators, auto-save happens
  - Act 3: Feels thoughts are "in the box", falls asleep within minutes
- Include: Internal monologue (shame/privacy fears), imperfection (doesn't press save), privacy glitch (dark mode critical)
- Evidence level: `proto_persona` (translated from German appendix example)

**SCENARIO 3 (OPTIONAL): SCEN-003-01 - Pattern Discovery Before Therapy (Sarah)**
- Folder: `requirements_user_needs/personas/sarah_self_user/scenarios/pattern_discovery/`
- File: `scenario.md`
- Goal: Find correlation between sleep and anxiety before therapy session
- Context: Waiting room before therapy, 5 minutes until session, feels guilty for sparse logging
- 3-Act Structure (use German appendix example):
  - Act 1: Waiting room, nervous, guilt over incomplete data
  - Act 2: Opens app, sees insight despite gaps ("2 days you logged, sleep was <5h"), realizes pattern
  - Act 3: Enters session with specific topic instead of "I don't know what to talk about"
- Include: Handling missing data gracefully, turning guilt into insight
- Evidence level: `proto_persona` (translated from German appendix example)

**Quality Criteria for Scenarios**:
- [ ] All YAML frontmatter fields present
- [ ] 3-act structure followed (Context → Interaction/Resistance → Result/Feeling)
- [ ] Internal monologue included
- [ ] Time pressure or physical stressor present
- [ ] Emotional goal defined (not just functional)
- [ ] Shows imperfection/friction (not just happy path)
- [ ] Evidence level markers used inline
- [ ] English language
- [ ] Scenario writing checklist satisfied (10 items)

#### Step 3: Create Example User Flows (At Least 1, Recommend 2)

**FLOW 1: FLOW-002-01-01 - Quick Night Entry (from SCEN-002-01)**
- Folder: `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/`
- File: `flow.md`
- Scenario: Brain Dump at Night (SCEN-002-01)
- Approach: Voice-to-text entry with auto-save in dark mode
- Happy Path:
  1. User opens app → System launches in dark mode (OLED black)
  2. User taps voice-to-text button → System activates whisper-sensitive mic
  3. User whispers thoughts → System transcribes in real-time, shows privacy lock icon
  4. User lets phone drop → System auto-saves (no manual save required)
- Unhappy Paths:
  - 1.1: App opens in light mode (wrong) → User's eyes hurt, partner wakes → Recovery: Force dark mode after 9 PM
  - 2.1: Mic permission not granted → Show permission request with context ("For private voice notes") → User grants → Return to Step 2
  - 3.1: Background noise interferes → System shows "Couldn't hear clearly, try again?" → User repeats → Return to Step 3
  - 4.1: Storage full → Before opening entry screen, check storage → Show warning → Offer to export old entries → Return to Step 1
- Adaptive UI: If time is 9 PM - 6 AM → Force dark mode, hide gamification, show "Quick Entry" shortcut
- Implementation status: `not_started`
- Implementing epics: TBD (placeholder links to future epics for data input, voice-to-text, privacy features)

**FLOW 2 (OPTIONAL): FLOW-001-01-01 - Client Data Quick Review (from SCEN-001-01)**
- Folder: `requirements_user_needs/personas/dr_thomas/scenarios/pre_session_patient_review/user_flows/client_data_quick_review/`
- File: `flow.md`
- Scenario: Pre-Session Patient Review (SCEN-001-01)
- Approach: Dashboard with trend overview and red flag detection
- Happy Path:
  1. Therapist opens app → System shows client list
  2. Therapist selects client → System loads client dashboard (< 1s)
  3. Therapist scans trend chart → System highlights anomalies (e.g., mood < 3 for 3+ days)
  4. Therapist makes mental note → Closes app, ready for session
- Unhappy Paths:
  - 2.1: Client data corrupted → Show "Data needs repair" → Restore from backup → Return to Step 2
  - 3.1: Privacy glitch (colleague walks by) → Therapist quickly minimizes → System blurs screen content → Resume when alone
  - 3.2: No data from client this week → Show message "No entries this week" + last available data → Therapist notes topic for session
- Adaptive UI: If therapist role → Show client management, if client role → Show own data
- Implementation status: `not_started`

**Quality Criteria for User Flows**:
- [ ] All YAML frontmatter fields present
- [ ] Happy path clearly defined with table format
- [ ] Unhappy paths documented (at least 3-5 exceptions)
- [ ] Recovery paths shown (lead back to happy path)
- [ ] Local storage edge cases covered (corruption, full storage, app kill)
- [ ] Adaptive UI rules specified
- [ ] Links to implementing epics/features (placeholders OK for Phase 3)
- [ ] Implementation status tracked
- [ ] Flow writing checklist satisfied (11 items)

#### Step 4: Create Folder Structure

Ensure proper folder hierarchy:
```
requirements_user_needs/
├── README.md (already exists)
└── personas/
    ├── dr_thomas/
    │   ├── persona.md
    │   └── scenarios/
    │       └── pre_session_patient_review/
    │           ├── scenario.md
    │           └── user_flows/
    │               └── client_data_quick_review/
    │                   └── flow.md
    ├── max_client/
    │   ├── persona.md
    │   └── scenarios/
    │       └── brain_dump_at_night/
    │           ├── scenario.md
    │           └── user_flows/
    │               └── quick_night_entry/
    │                   └── flow.md
    ├── sarah_self_user/
    │   ├── persona.md
    │   └── scenarios/
    │       └── pattern_discovery/
    │           ├── scenario.md
    │           └── user_flows/
    │               └── insight_from_sparse_data/
    │                   └── flow.md
    └── system_maintenance/
        └── persona.md
```

---

## Quality Criteria (Overall)

Phase 3 acceptance criteria from goal.md:

- [ ] Folder structure `requirements_user_needs/personas/` exists ✅ (from Phase 1)
- [ ] README.md exists ✅ (from Phase 1)
- [ ] **At least 1 complete persona file created** → TARGET: 4 personas
- [ ] **At least 1 complete scenario file created** → TARGET: 2-3 scenarios
- [ ] **At least 1 complete user flow file created** → TARGET: 2 user flows
- [ ] Templates documented in README ✅ (from Phase 1-2)
- [ ] Cross-reference examples documented ✅ (from Phase 1)
- [ ] Skill modification requirements documented ✅ (from Phase 1)
- [ ] Validation rules documented ✅ (from Phase 1)
- [ ] All files use English language

**Exceeding minimum requirements**: Instead of 1-1-1, deliver 4-2-2 (4 personas, 2-3 scenarios, 2 user flows) to properly demonstrate template usage across different roles.

---

## Content Strategy

### Persona Content Sources

For each persona, blend three sources:

1. **German Appendix Psychology** (mental models, JTBD, barriers) → Emotional/behavioral depth
2. **Requirements_general_overview** (functional needs) → App-specific grounding
3. **Template Best Practices** (7 elements, mental health specifics) → Structure

### Translation Approach

German appendix content is **gold** - it's detailed, empathetic, and psychologically grounded. Don't just translate words; translate **insights**:

- "Mentales Modell: Die App ist mein externer RAM" → Mental Model: "The app is my external RAM"
- "Hat Angst, dass seine Gedanken 'dumm' klingen" → Fears: "Worries thoughts will sound weak or stupid"
- Keep the raw emotional honesty (e.g., "I click randomly until the window goes away")

### Evidence Level Strategy

All Phase 3 content is `proto_persona` because:
- Based on requirements (functional grounding) ✅
- Based on German appendix (psychological archetypes) ✅
- NOT based on real user interviews ❌

Mark individual claims:
- 🟢 [Data-Grounded]: Use for app features from requirements_general_overview
- 🟡 [Proto-Persona]: Use for psychological insights from German appendix
- 🔴 [Hypothesis]: Use for assumptions that need validation

---

## Risks & Mitigations

### Risk 1: Content Too Generic
**Mitigation**: Use German appendix examples verbatim (translated). They're already specific and detailed.

### Risk 2: Personas Don't Align with App Capabilities
**Mitigation**: Cross-reference every JTBD/feature need with requirements_general_overview to ensure app can support it.

### Risk 3: Scenarios Feel Artificial
**Mitigation**: Use 3-act structure with internal monologue, physical context, and imperfection. The German examples (Markus at 1 AM, Sarah in waiting room) are perfect templates.

### Risk 4: User Flows Too Abstract
**Mitigation**: Include specific exception cases from German appendix (dark mode, voice input, privacy glitches, missing data handling).

---

## Execution Instructions

**For Implementation Engineer Agent**:

1. Read this plan thoroughly
2. Read README.md templates (sections 3, 4, 5)
3. Read German appendix (requirements.md lines 584-881) for persona insights
4. Read requirements_general_overview files for app context
5. Create files in order: Personas → Scenarios → User Flows
6. Use templates exactly (copy YAML frontmatter, section headers)
7. Translate German content while preserving emotional depth
8. Mark evidence levels inline with visual icons
9. Verify each file against quality checklists in README
10. Log completion to protocol with agent ID

**Timeline**: Single execution pass (all files in one session for consistency)

**Output**:
- 4 persona.md files
- 2-3 scenario.md files
- 2 flow.md files
- All using English
- All following templates exactly

---

## Success Definition

Phase 3 is complete when:

1. **Minimum acceptance criteria met** (1-1-1 files created)
2. **Recommended target achieved** (4-2-2 files created)
3. **All files pass quality checklists** from README.md
4. **Content demonstrates proper template usage** (future users can copy/adapt)
5. **Personas feel real** (empathy test: would you change design decisions based on these?)
6. **Scenarios tell stories** (not just use cases)
7. **Flows handle edge cases** (not just happy paths)

---

## Next Steps (After Phase 3)

Phase 4 will be:
- Define how cross-references work in practice
- Document skill modifications needed
- Define validation rules and scripts
- Create task for implementing skill changes

---

**Agent ID**: opus-plan-002
**Status**: Plan READY for execution
**Date**: 2026-01-17
**Estimated effort**: XL (1-2 hours for content creation)
