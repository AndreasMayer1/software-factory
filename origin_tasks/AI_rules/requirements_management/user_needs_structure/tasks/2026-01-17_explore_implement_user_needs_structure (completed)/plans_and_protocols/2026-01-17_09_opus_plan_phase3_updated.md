# Opus Plan: Phase 3 - Initial Content Creation (UPDATED)

**Date**: 2026-01-17
**Agent**: Opus (planning)
**Agent ID**: opus-plan-003
**Phase**: 3 (Initial Content Creation)
**Update Reason**: Incorporate non-user personas (shadow personas) and environmental constraints

---

## Objective

Create initial persona files, example scenarios, and user flows using the **updated templates** that now include:
- **8 elements** for personas (7 original + Environmental Constraints)
- **Device & Ecological Constraints** section
- **Privacy Glitch patterns** in scenarios
- **Environment/Non-User swimlane** in user flows

---

## Key Changes from Previous Plan

| Aspect | Previous Plan | Updated Plan |
|--------|---------------|--------------|
| Persona elements | 7 elements | **8 elements** (+ Environmental Constraints) |
| Non-user threats | Not included | **3 shadow personas** per user persona |
| Device constraints | Not included | **PCD constraints** section added |
| Scenario structure | 3-act + internal monologue | 3-act + **Privacy Glitch pattern** |
| Flow table format | 4 columns | **5 columns** (+ Environment) |
| Quality checklist | 11 items | **13 items** (+ non-user + PCD) |

---

## Analysis Summary

### The Three Shadow Personas (Non-Users)

These "shadow personas" don't use the app but fundamentally shape how users interact with it:

1. **The Shoulder Surfer**
   - *Who*: Stranger in public space (train, waiting room, café)
   - *Behavior*: Casually glances at bright display
   - *Threat*: Reads sensitive words ("Therapy", "Depression", mood graphs)
   - *Design need*: Discreet Mode, low-contrast theme, no visible medical labels

2. **The Auditory Witness**
   - *Who*: Colleague in open office, family in adjacent room
   - *Behavior*: Hears voice input or app sounds without looking
   - *Threat*: Hears voice-to-text entries, embarrassing app sounds
   - *Design need*: Whisper detection, panic-mute, visual feedback only

3. **The Intimate Intruder**
   - *Who*: Partner, parent, child, roommate with device access
   - *Behavior*: Picks up unlocked phone, swipes through apps
   - *Threat*: Accesses app via multitasking, reads intimate entries
   - *Design need*: Blurred app-switcher preview, biometric re-auth, hidden notifications

### Device & Ecological Constraints (PCD)

New mandatory section for personas:
- **Device Range**: Oldest to newest devices to support
- **Energy Sensitivity**: Battery concerns (Low/Medium/High)
- **Data Sensitivity**: Storage/cleanup concerns (Low/Medium/High)
- **Suffizienz Alignment**: Does persona want quick in/out? (Yes/No/Partial)

### Privacy Glitch Pattern for Scenarios

Scenarios must include a moment where a non-user appears and the user must protect their content:

```
**[Privacy Glitch]**
- **Non-User**: [Who appears/is present]
- **User Reaction**: [What user does]
- **System Response**: [How app helps]
- **Outcome**: [Resolution]
```

### Environment Swimlane for User Flows

Flows involving sensitive content must include an Environment column:

| Step | Environment (Non-User) | User Action | System Response | UI State |
|------|------------------------|-------------|-----------------|----------|
| 1 | [Who's present] | [Action] | [Response] | [Screen] |

---

## Execution Plan

### Agent 1: Content Creation (Implementation Engineer)

**Purpose**: Create persona files, scenario files, and user flow files following the **updated** templates.

---

#### Step 1: Create Persona Files (All 4)

##### PERSONA-001: Dr. Thomas (Therapist)

**Folder**: `requirements_user_needs/personas/dr_thomas/`
**File**: `persona.md`

**Core Identity**:
- Mental model: "The app is my professional assistant for efficient client management"
- JTBD: Prepare for sessions efficiently, maintain data security, reduce administrative overhead
- Evidence level: `proto_persona`

**Environmental Constraints (NEW)**:

```markdown
## Environmental Constraints

### Non-User: Intimate Intruder (Colleague in Practice)
- **Context**: Shared office, colleague walks behind desk, glances at screen
- **Threat**: Sees client data (names, mood graphs, therapy notes)
- **Impact**: Violates client confidentiality; therapist may avoid reviewing sensitive data at work
- **Requirement**: Quick-minimize gesture; screen blur on rapid movement; no client names visible in overview

### Non-User: Shoulder Surfer (Waiting Room)
- **Context**: Reviewing data on tablet in waiting room between sessions
- **Threat**: Next patient (or their family) sees previous patient's data
- **Impact**: GDPR violation; loss of professional trust
- **Requirement**: Automatic screen lock after 30s; privacy screen filter detection; "panic button" to clear screen
```

**Device & Ecological Constraints (NEW)**:

```markdown
## Device & Ecological Constraints

**Device Range**: Modern Windows laptop (primary), Android tablet, occasionally iPhone
**Energy Sensitivity**: Low (devices always charged at office)
**Data Sensitivity**: High (client data must be manageable; old clients should be archivable)
**Suffizienz Alignment**: Yes (wants efficiency; no feature bloat)
```

---

##### PERSONA-002: Max (Client with Depression/ADHD)

**Folder**: `requirements_user_needs/personas/max_client/`
**File**: `persona.md`

**Core Identity**:
- Mental model: "The app is my therapy assistant/external brain"
- JTBD: Track patterns for therapy, offload circular thoughts, avoid "I don't know how my week was"
- Evidence level: `proto_persona`
- Mental health specifics: Energy budget (depression = very low), shame threshold (high), vulnerability hangover (frequent)

**Environmental Constraints (NEW)**:

```markdown
## Environmental Constraints

### Non-User: Intimate Intruder (Partner at Home)
- **Context**: Partner picks up Max's phone from nightstand, swipes through apps
- **Threat**: Sees app in recent-apps list, opens it, reads mood entries or therapy homework
- **Impact**: Max censors entries; avoids honest reflection; relationship tension
- **Requirement**: Biometric re-auth on resume (immediate, no delay); blurred app-switcher preview; neutral notification text

### Non-User: Auditory Witness (Partner in Bed)
- **Context**: Max uses voice-to-text at 1 AM, partner sleeping next to him
- **Threat**: Partner hears whispered entries; wakes up; asks "What are you doing?"
- **Impact**: Max abandons entry; feels exposed; loses therapeutic moment
- **Requirement**: Whisper-level voice detection; visual waveform (no audio feedback); panic-mute on phone flip

### Non-User: Shoulder Surfer (Public Transit)
- **Context**: Commuting on train; stranger sits adjacent
- **Threat**: Sees "Mood: 2/10" or "Therapy Homework" on screen
- **Impact**: Max won't log moods in public; loses data during commute times
- **Requirement**: Discreet Mode toggle; low-contrast theme; no visible labels ("2/10" shows as subtle color bar only)
```

**Device & Ecological Constraints (NEW)**:

```markdown
## Device & Ecological Constraints

**Device Range**: Mid-range Android phone (2-3 years old), occasional old tablet
**Energy Sensitivity**: Medium (forgets to charge; app must work at 10% battery)
**Data Sensitivity**: Medium (rarely cleans up; app should handle years of entries gracefully)
**Suffizienz Alignment**: Yes (low energy = minimal interaction needed)
```

---

##### PERSONA-003: Sarah (Self-User)

**Folder**: `requirements_user_needs/personas/sarah_self_user/`
**File**: `persona.md`

**Core Identity**:
- Mental model: "The app is my dashboard/spreadsheet for life"
- JTBD: Find correlations, optimize habits, gain self-insight, feel in control
- Evidence level: `proto_persona`
- Anti-traits: NOT in acute distress, NOT interested in therapy relationship, allergic to "woo-woo"

**Environmental Constraints (NEW)**:

```markdown
## Environmental Constraints

### Non-User: Shoulder Surfer (Café/Coworking)
- **Context**: Working from café; logging mood during coffee break
- **Threat**: Someone at adjacent table glances at "Mood Tracker" app
- **Impact**: Sarah feels exposed; prefers app that looks like productivity tool
- **Requirement**: Camouflage Mode (app looks like calendar or notes app); discreet icon; no medical terminology visible

### Non-User: Intimate Intruder (Curious Friend)
- **Context**: Friend borrows phone to "quickly Google something"; swipes through apps
- **Threat**: Sees personal mood data; asks awkward questions
- **Impact**: Sarah becomes secretive about app usage; feels privacy violated
- **Requirement**: App hidden from recent apps (optional); biometric lock; plausible deniability UI
```

**Device & Ecological Constraints (NEW)**:

```markdown
## Device & Ecological Constraints

**Device Range**: Latest iPhone (primary), MacBook for data analysis (CSV export)
**Energy Sensitivity**: Low (always charged; cares about performance)
**Data Sensitivity**: Low (organized; exports data regularly; clean device)
**Suffizienz Alignment**: Partial (wants features, but efficient ones; no bloat)
```

---

##### PERSONA-004: System/Maintenance (Technical Persona)

**Folder**: `requirements_user_needs/personas/system_maintenance/`
**File**: `persona.md`

**Note**: This is a non-human persona representing technical edge cases. It does NOT have Environmental Constraints (no human user) but DOES have Device & Ecological Constraints.

**Core Identity**:
- Mental model: N/A (system perspective)
- JTBD: Handle device migrations, crashes, database corruption, storage issues, OS updates
- Evidence level: `grounded` (based on technical requirements)

**Device & Ecological Constraints**:

```markdown
## Device & Ecological Constraints

**Device Range**: ALL supported devices (oldest Android 8.0 to latest iOS/Android/Windows)
**Energy Sensitivity**: Critical (must handle low-battery scenarios gracefully; atomic writes)
**Data Sensitivity**: Critical (must handle storage-full scenarios; auto-cleanup of orphaned files)
**Suffizienz Alignment**: N/A (system-level concerns, not user preference)
```

---

#### Step 2: Create Example Scenarios (At Least 2, Recommend 3)

##### SCENARIO 1: SCEN-001-01 - Pre-Session Patient Review (Dr. Thomas)

**Folder**: `requirements_user_needs/personas/dr_thomas/scenarios/pre_session_patient_review/`
**File**: `scenario.md`

**3-Act Structure with Privacy Glitch**:

**Act 1: Context & Inciting Incident**
> Dr. Thomas glances at the clock: 10 minutes until his next client. He realizes he hasn't reviewed her week's data yet. He opens the app on his tablet, hoping to quickly scan for patterns.

**Act 2: Interaction & Resistance**
> He navigates to the client dashboard. The trend chart loads within a second. He sees a red flag: mood ratings dropped below 3 on three consecutive days last week.
>
> *Internal thought: "I should ask about Tuesday. Something happened."*

**[Privacy Glitch]** (NEW)
- **Non-User**: Colleague passes behind his desk on the way to the coffee machine
- **User Reaction**: Dr. Thomas instinctively angles the tablet away
- **System Response**: App detects rapid device movement; automatically dims screen and shows generic "Dashboard" header
- **Outcome**: Colleague doesn't see client data; Dr. Thomas relaxes and continues

> He makes a mental note of the pattern and closes the app just as his receptionist knocks.

**Act 3: Result & Feeling**
> Dr. Thomas feels prepared. Instead of starting with "How was your week?", he can ask "I noticed something difficult might have happened around Tuesday. Want to talk about it?"

---

##### SCENARIO 2: SCEN-002-01 - Brain Dump at Night (Max)

**Folder**: `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/`
**File**: `scenario.md`

**3-Act Structure with Privacy Glitch**:

**Act 1: Context & Inciting Incident**
> It's 1:15 AM. Max lies in darkness next to his partner. His heart races slightly as tomorrow's meeting replays in his mind. He's tried deep breathing—nothing works. The thoughts keep circling.
>
> *Internal thought: "If I don't get this out of my head, I won't sleep."*

**Act 2: Interaction & Resistance**
> Max reaches for his phone on the nightstand. The app opens in OLED dark mode—the room stays dark. His eyes are tired. Typing feels like too much effort, and the keyboard clicks would be loud.
>
> He sees the voice-to-text button. He brings the phone close and whispers three sentences into the mic: the meeting worry, the email he forgot to send, the uncertainty about his boss's reaction.
>
> *Internal thought: "I hope this isn't being uploaded somewhere..."*
>
> He glances at the screen. A small lock icon appears: "Only stored locally, encrypted." He exhales.

**[Privacy Glitch]** (NEW)
- **Non-User**: Partner shifts in bed; mumbles something
- **User Reaction**: Max freezes; lowers voice to barely audible
- **System Response**: Voice-to-text adjusts sensitivity automatically; waveform shows it's still capturing; no audio confirmation beeps
- **Outcome**: Partner settles back to sleep; Max finishes his entry in a whisper

> He doesn't press Save—the app auto-saves. He lets the phone drop to his chest.

**Act 3: Result & Feeling**
> The thought is now "in the box." Max feels the mental loop stop. He places the phone face-down on the nightstand and turns over. Within five minutes, he's asleep.
>
> *Next morning*: The app doesn't push a notification saying "Review your reflection!" It just sits there quietly, having done its job.

---

##### SCENARIO 3: SCEN-003-01 - Discreet Check-In on Transit (Sarah)

**Folder**: `requirements_user_needs/personas/sarah_self_user/scenarios/discreet_checkin_transit/`
**File**: `scenario.md`

**3-Act Structure with Privacy Glitch**:

**Act 1: Context & Inciting Incident**
> Sarah sits on the S-Bahn during her morning commute. She had a rough night—woke up multiple times—and wants to log her sleep data before she forgets. The train is crowded; a businessman sits adjacent, scrolling his phone.

**Act 2: Interaction & Resistance**
> She opens the app. It launches in Discreet Mode (she set this as default for commute times). The UI looks like a simple notes app—no "MOOD TRACKER" header, no medical symbols.
>
> She taps the quick-entry widget. Instead of a labeled "Mood: 1-10" slider, she sees a subtle color gradient. She slides to the orange zone (4/10).

**[Privacy Glitch]** (NEW)
- **Non-User**: Businessman glances at her screen (idle curiosity)
- **User Reaction**: Sarah doesn't panic—the screen looks innocuous
- **System Response**: Discreet Mode shows only color bars and icons; no text labels; "Sleep: 4.5h" displays as a small gray number
- **Outcome**: Businessman looks away (boring app); Sarah continues logging

> She adds "woke up 3x" in a text field that looks like a plain notes input. Done in 20 seconds.

**Act 3: Result & Feeling**
> Sarah feels in control. She logged her data without anyone knowing what the app does. Later, at the office, she'll check the correlation chart on her laptop.

---

#### Step 3: Create Example User Flows (At Least 2)

##### FLOW 1: FLOW-002-01-01 - Quick Night Entry (from SCEN-002-01)

**Folder**: `requirements_user_needs/personas/max_client/scenarios/brain_dump_at_night/user_flows/quick_night_entry/`
**File**: `flow.md`

**Happy Path with Environment Swimlane** (NEW FORMAT):

| # | Environment (Non-User) | User Action | System Response | UI State |
|---|------------------------|-------------|-----------------|----------|
| 1 | Partner asleep in bed | Opens app | Detects time (1 AM); launches in forced dark mode | Home (OLED black) |
| 2 | Partner asleep | Taps voice-to-text | Activates whisper-sensitive mic; shows waveform | Voice input active |
| 3 | **Partner stirs** | Lowers voice to whisper | Auto-adjusts mic sensitivity; continues capture | Waveform adapts |
| 4 | Partner settles | Finishes speaking | Transcribes text; shows privacy lock icon | Entry preview |
| 5 | Partner asleep | Lets phone drop | Auto-saves (no manual action); no confirmation sound | "Saved" (subtle) |

**Unhappy Paths**:

| Exception | Trigger | Recovery |
|-----------|---------|----------|
| 1.1 | App opens in light mode (setting error) | Detect time; force dark mode; never show light UI after 9 PM |
| 2.1 | Partner wakes up, asks "What are you doing?" | Provide "Panic Mute" (flip phone face-down = instant stop + save draft) |
| 3.1 | Voice too quiet; transcription fails | Show "Couldn't hear. Tap to type instead?" with large touch target |
| 4.1 | Storage full | Detect before entry screen; show warning; offer export of old entries |
| 5.1 | App killed before auto-save | Atomic transactions; recover draft on next launch with "Continue your entry?" |

**Adaptive UI Rules**:
- IF time 9 PM - 6 AM → Force dark mode
- IF time 9 PM - 6 AM → Hide gamification elements (no streaks)
- IF previous mood < 3 → Show "Quick Entry" shortcut instead of reflection prompts

---

##### FLOW 2: FLOW-003-01-01 - Discreet Quick Log (from SCEN-003-01)

**Folder**: `requirements_user_needs/personas/sarah_self_user/scenarios/discreet_checkin_transit/user_flows/discreet_quick_log/`
**File**: `flow.md`

**Happy Path with Environment Swimlane** (NEW FORMAT):

| # | Environment (Non-User) | User Action | System Response | UI State |
|---|------------------------|-------------|-----------------|----------|
| 1 | **Shoulder Surfer adjacent** | Opens app | Detects "Discreet Mode" preference (or location-based trigger) | Camouflage home screen |
| 2 | Surfer present | Taps quick-entry widget | Shows unlabeled color gradient (no "MOOD" text) | Discreet entry |
| 3 | **Surfer glances** | Slides to orange zone (4/10) | Registers value; no visible numbers; subtle color change | Color feedback |
| 4 | Surfer looks away | Types "woke 3x" in notes field | Plain text input; no "Sleep Notes" label | Notes field |
| 5 | Alone (surfer exits) | Confirms entry | Saves; shows subtle checkmark; offers "Exit Discreet Mode?" | Confirmation |

**Unhappy Paths**:

| Exception | Trigger | Recovery |
|-----------|---------|----------|
| 1.1 | App opens in normal mode (Discreet Mode off) | Provide "panic button" (3-tap on icon = instant camouflage switch) |
| 2.1 | User forgets what color means what | On long-press: show tooltip with number; hide again on release |
| 3.1 | Surfer tries to read screen | Discreet Mode has no readable text; plausible deniability maintained |
| 5.1 | User wants to add more detail | "Add more?" button leads to full entry; warns "Exiting Discreet Mode" |

**Adaptive UI Rules**:
- IF location = "commute" (based on time/movement pattern) → Suggest Discreet Mode on launch
- IF Discreet Mode ON → Hide all text labels; use colors and icons only
- IF Discreet Mode ON → "Fake Exit" button shows calculator or calendar instead of closing app

---

#### Step 4: Create Folder Structure

```
requirements_user_needs/
├── README.md (already exists, updated with non-user personas)
└── personas/
    ├── dr_thomas/
    │   ├── persona.md (with Environmental Constraints + PCD)
    │   └── scenarios/
    │       └── pre_session_patient_review/
    │           ├── scenario.md (with Privacy Glitch)
    │           └── user_flows/
    │               └── client_data_quick_review/
    │                   └── flow.md (with Environment column)
    ├── max_client/
    │   ├── persona.md (with 3 non-user threats + PCD)
    │   └── scenarios/
    │       └── brain_dump_at_night/
    │           ├── scenario.md (with Privacy Glitch)
    │           └── user_flows/
    │               └── quick_night_entry/
    │                   └── flow.md (with Environment column)
    ├── sarah_self_user/
    │   ├── persona.md (with 2 non-user threats + PCD)
    │   └── scenarios/
    │       └── discreet_checkin_transit/
    │           ├── scenario.md (with Privacy Glitch)
    │           └── user_flows/
    │               └── discreet_quick_log/
    │                   └── flow.md (with Environment column)
    └── system_maintenance/
        └── persona.md (PCD only, no Environmental Constraints)
```

---

## Quality Criteria (UPDATED)

### Persona Quality Checklist (13 items)

- [ ] All YAML frontmatter fields present and valid
- [ ] All **8 elements** included (7 original + Environmental Constraints)
- [ ] Mental health specific fields populated (energy budget, shame threshold, vulnerability hangover)
- [ ] **Environmental constraints identified**: At least one non-user threat documented with mitigation
- [ ] **PCD constraints documented**: Device range, energy/data sensitivity, suffizienz alignment
- [ ] Evidence level markers used inline (🟢, 🟡, 🔴)
- [ ] Anti-traits defined (what persona is NOT)
- [ ] Real quotes included (or representative examples)
- [ ] Design implications translate to actionable requirements
- [ ] English language throughout
- [ ] Psychology over demographics (no age/gender fluff)
- [ ] Mental model clearly stated
- [ ] JTBD articulated (functional, emotional, social)

### Scenario Quality Checklist (11 items)

- [ ] All YAML frontmatter fields present
- [ ] 3-act structure followed (Context → Interaction/Resistance → Result/Feeling)
- [ ] Internal monologue included
- [ ] Time pressure or physical stressor present
- [ ] Emotional goal defined (not just functional)
- [ ] Shows imperfection/friction (not just happy path)
- [ ] **Privacy Glitch pattern included**: Non-user appears, user reacts, system helps, resolution
- [ ] Evidence level markers used inline
- [ ] English language
- [ ] Specific environment described (not generic "at home")
- [ ] Design implications documented ("What this scenario reveals")

### User Flow Quality Checklist (12 items)

- [ ] All YAML frontmatter fields present
- [ ] Happy path clearly defined with **Environment swimlane column**
- [ ] Unhappy paths documented (at least 3-5 exceptions)
- [ ] Recovery paths shown (lead back to happy path)
- [ ] Local storage edge cases covered (corruption, full storage, app kill)
- [ ] **Non-user interruption handled** in at least one step
- [ ] Adaptive UI rules specified
- [ ] Links to implementing epics/features (placeholders OK)
- [ ] Implementation status tracked
- [ ] Panic/emergency actions documented (mute, hide, camouflage)
- [ ] Plausible deniability considered (for sensitive flows)
- [ ] English language

---

## Content Strategy (UPDATED)

### Non-User Assignment Matrix

| Persona | Shoulder Surfer | Auditory Witness | Intimate Intruder |
|---------|-----------------|------------------|-------------------|
| Dr. Thomas (Therapist) | ✅ (waiting room) | ❌ (office = private) | ✅ (colleague) |
| Max (Client) | ✅ (transit) | ✅ (partner in bed) | ✅ (partner access) |
| Sarah (Self-User) | ✅ (café/cowork) | ❌ (not voice user) | ✅ (friends borrow phone) |
| System/Maintenance | N/A | N/A | N/A |

### PCD Constraints Summary

| Persona | Device Range | Energy | Data | Suffizienz |
|---------|--------------|--------|------|------------|
| Dr. Thomas | Modern (laptop, tablet, phone) | Low | High | Yes |
| Max | Mid-range (2-3 yr old Android) | Medium | Medium | Yes |
| Sarah | Latest (iPhone, MacBook) | Low | Low | Partial |
| System | ALL (Android 8+, iOS, Windows) | Critical | Critical | N/A |

---

## Risks & Mitigations (UPDATED)

### Risk 1: Non-User Threats Feel Artificial
**Mitigation**: Ground each threat in specific, relatable context from German appendix (Marcus's wife stirring in bed, Sarah in waiting room). Real details create authenticity.

### Risk 2: Privacy Glitches Dominate Scenarios
**Mitigation**: Privacy Glitch is ONE MOMENT in Act 2, not the entire scenario. Keep focus on user's primary goal; glitch is friction, not plot.

### Risk 3: Environment Column Clutters Flows
**Mitigation**: Only include Environment column for privacy-sensitive flows. Skip for technical flows (backup, migration).

### Risk 4: PCD Constraints Too Detailed
**Mitigation**: Keep PCD section brief (4 lines). Purpose is to flag constraints, not document every device.

### Risk 5: System/Maintenance Persona Feels Out of Place
**Mitigation**: Clearly label it as non-human "technical persona." It exists to capture edge cases that don't fit user personas. No Environmental Constraints needed.

---

## Execution Instructions (UPDATED)

**For Implementation Engineer Agent**:

1. Read this updated plan thoroughly
2. Read README.md templates (sections 3, 4, 5) with focus on:
   - Section 3.8: Environmental Constraints (Non-User Personas)
   - Section 3.9: Device & Ecological Constraints
   - Section 4.4: Non-User Integration in Scenarios
   - Section 5.7: Environment/Non-User Swimlane
3. Read German appendix (requirements.md lines 584-881) for persona insights
4. Read requirements_general_overview files for app context
5. Create files in order: **Personas → Scenarios → User Flows**
6. For each persona, identify which of the 3 shadow personas apply (use matrix above)
7. For each scenario, include ONE Privacy Glitch moment in Act 2
8. For each flow, include Environment column with non-user presence
9. Verify each file against UPDATED quality checklists (13/11/12 items)
10. Log completion to protocol with agent ID

**Timeline**: Single execution pass (all files in one session for consistency)

**Output**:
- 4 persona.md files (with Environmental Constraints + PCD)
- 3 scenario.md files (with Privacy Glitch patterns)
- 2 flow.md files (with Environment swimlane)
- All using English
- All following UPDATED templates exactly

---

## Success Definition (UPDATED)

Phase 3 is complete when:

1. **Minimum acceptance criteria met** (1-1-1 files created)
2. **Recommended target achieved** (4-3-2 files created)
3. **All files pass UPDATED quality checklists** (13/11/12 items)
4. **Non-user threats documented** for each user persona (not System/Maintenance)
5. **Privacy Glitch pattern** appears in every scenario
6. **Environment column** appears in every privacy-sensitive flow
7. **PCD constraints** documented for all personas
8. **Personas feel real** (empathy test + privacy empathy: would you feel safe using this app?)
9. **Scenarios tell privacy-aware stories** (user is never caught off-guard by non-users)
10. **Flows handle interruptions gracefully** (panic actions, auto-save, camouflage)

---

## Summary of Changes

| Component | What Changed |
|-----------|--------------|
| **Personas** | +8th element (Environmental Constraints), +PCD section, +non-user threat matrix |
| **Scenarios** | +Privacy Glitch pattern in Act 2, +specific non-user interruption |
| **User Flows** | +Environment column in swimlane, +panic/camouflage actions |
| **Quality Checklists** | +2 items per checklist (non-user + PCD) |
| **Folder Structure** | Unchanged (same hierarchy) |
| **Deliverables** | 4 personas, 3 scenarios (was 2-3), 2 flows |

---

**Agent ID**: opus-plan-003
**Status**: UPDATED Plan READY for execution
**Date**: 2026-01-17
**Previous Plan**: 2026-01-17_06_opus_plan_phase3_content_creation.md (superseded)
**Estimated effort**: XL (1-2 hours for content creation)
