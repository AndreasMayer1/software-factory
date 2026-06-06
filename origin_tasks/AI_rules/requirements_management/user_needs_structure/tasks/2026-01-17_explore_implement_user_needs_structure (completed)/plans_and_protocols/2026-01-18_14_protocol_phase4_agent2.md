# Protocol: Phase 4 Agent 2 - Therapist Persona Rewrite

**Date**: 2026-01-18
**Agent**: Agent 2 (Sonnet 4.5)
**Phase**: 4 (Content Improvement)
**Status**: COMPLETED
**Plan Reference**: `2026-01-18_13_opus_plan_phase4.md` (lines 197-242)

---

## Assignment

Execute Agent 2 section of Opus Plan Phase 4:
- Rewrite PERSONA-001 (therapist) from Dr. Thomas to Dr. Sarah
- Change to female psychologist specializing in behavioral therapy
- Focus on paper-based status quo (BEFORE app exists)
- Remove all app solution descriptions
- Create 2 new scenarios: (1) Preparing protocol, (2) Reviewing WITH client
- Apply new review status system from Agent 1
- This is a MODEL for remaining personas (user will review before applying to others)

---

## Steps Executed

### Step 1: Folder Rename ✅

**Action**: Renamed `dr_thomas` folder to `dr_sarah`

**Command**:
```bash
mv dr_thomas dr_sarah
```

**Result**: Folder successfully renamed. All existing content (persona.md, scenarios/) moved to new location.

**Rationale**: Per user feedback, therapist persona should be female psychologist, not male. Name change reflects gender change.

---

### Step 2: Persona Rewrite ✅

**File**: `requirements_user_needs/personas/dr_sarah/persona.md`

**Changes Made**:

1. **YAML Frontmatter Updates**:
   - Changed `name` from "Dr. Thomas" to "Dr. Sarah"
   - Changed `role` to explicit "therapist" (was implicit)
   - Added `review_status: draft`
   - Added `review_history` with 2 entries (initial creation, this rewrite)
   - Updated `version` from 1.0 to 2.0
   - Updated `updated` date to 2026-01-18
   - Added `data_sources` field referencing user feedback

2. **Content Rewrite** (Major):
   - **Gender change**: All pronouns changed to she/her
   - **Specialty change**: Changed from generic therapist to "Psychologische Psychotherapeutin für Verhaltenstherapie" (psychological psychotherapist for behavioral therapy)
   - **Focus shift**: Anxiety protocols and VT protocols (not medication)
   - **Status quo emphasis**: Added extensive "Current Status Quo (Before Digital Solution)" section describing paper-based workflow
   - **Pain points articulated**: Separated pain points for clients (portability, forgetting) vs. therapist (analysis difficulty, time-consuming)
   - **Removed solution descriptions**: Deleted entire "Design Implications" section (was describing app features)
   - **Anti-persona clarification**: Added explicit items from user feedback (NOT psychiatrist, NOT analyzing alone, NOT sitting in waiting rooms)
   - **Environmental constraints updated**: Changed "waiting room review" scenario to "office desk review" (user said therapist never sits in waiting room with patients)
   - **Added new constraint**: Must not accidentally show client list with real names during session review (user feedback explicit requirement)

3. **Structure Changes**:
   - Removed "Trigger 1: Pre-Session Review" from context (that was describing app usage)
   - Removed "When does Dr. Thomas use the app?" section (describes solution, not status quo)
   - Removed "Design Implications" section entirely (was listing app features)
   - Added "Summary: Core Needs" section (what therapist needs, not how to solve it)
   - Added version history at bottom
   - Added status note: "Draft - awaiting user review before approval"

4. **Key Content Additions**:
   - **Current Status Quo section**: How therapist works TODAY with paper
   - **Pain points section**: Explicit friction with paper (overlaying days' data is hard)
   - **Mental models**: Protocols are collaborative tools, analysis happens WITH client
   - **Jobs to Be Done**: Separated into "Prepare Protocols" and "Review Protocols WITH Client"

**Quality Check**:
- [x] Persona describes status quo without app
- [x] No technical implementation details (no SQLite, no OLED, etc.)
- [x] Focus on behavioral therapy (anxiety protocols, VT)
- [x] Female psychologist (not male, not psychiatrist)
- [x] Anti-persona traits match user feedback
- [x] Environmental constraint includes "no client list with names" requirement
- [x] Review status YAML added
- [x] Pain points with paper approach documented

---

### Step 3: Delete Old Scenario ✅

**Action**: Removed `pre_session_patient_review` scenario folder

**Command**:
```bash
rm -rf dr_sarah/scenarios/pre_session_patient_review
```

**Rationale**: Old scenario described app usage (therapist reviewing client data on screen), which violates "status quo" principle. User feedback stated therapist does NOT review data alone - only WITH client in session. Old scenario is incompatible with new approach.

---

### Step 4: Create Scenario 1 - Prepare Protocol for Client ✅

**File**: `requirements_user_needs/personas/dr_sarah/scenarios/prepare_protocol_for_client/scenario.md`

**Content**:

1. **YAML Frontmatter**:
   - `scenario_id: SCEN-001-01`
   - `persona_id: PERSONA-001`
   - `review_status: draft`
   - `review_history` with initial creation entry

2. **Scenario Structure**:
   - **Goal**: Prepare customized anxiety protocol, hand to client, instruct them
   - **Context**: Day before session or at session start, 5-10 minutes available
   - **Three-Act Story**:
     - Act 1: Dr. Sarah decides client needs anxiety protocol, pulls blank paper template
     - Act 2: Customizes template (writes margin notes, situation examples), plans verbal instructions
     - Act 3: Hands paper to client in session, explains what/when/how to track, addresses barriers (forgetting, privacy)
   - **Success Criteria**: Protocol customized in <10 min, instructions clear, barriers addressed, privacy maintained
   - **Failure Modes**: Too generic, unclear instructions, time overrun, client overwhelmed
   - **Current Status Quo**: Paper-based (filing cabinet, handwritten notes, physical handover)
   - **Pain Points**: Client must carry paper+pen, easy to forget, risk of loss, no reminders

3. **Technology Neutrality**:
   - [x] No app behavior described
   - [x] Focus on WHAT needs to happen (customization, instruction, handover)
   - [x] Current solution (paper) described as status quo
   - [x] Pain points implicit (portability, forgetting)

4. **Cross-References**:
   - References PERSONA-001#jobs_to_be_done
   - Links to SCEN-001-02 (downstream scenario)

**Quality Check**:
- [x] Scenario describes goal, not app behavior
- [x] No technical details (no "database", no "push notifications")
- [x] Success criteria outcome-focused
- [x] Current status quo (paper) documented
- [x] Pain points articulated (forgetting paper, portability)
- [x] Review status YAML added
- [x] Cross-references use new notation

---

### Step 5: Create Scenario 2 - Review Protocol WITH Client ✅

**File**: `requirements_user_needs/personas/dr_sarah/scenarios/review_protocol_with_client/scenario.md`

**Content**:

1. **YAML Frontmatter**:
   - `scenario_id: SCEN-001-02`
   - `persona_id: PERSONA-001`
   - `review_status: draft`
   - `review_history` with initial creation entry

2. **Scenario Structure**:
   - **Goal**: Review filled protocol WITH client in session, identify patterns, discuss influences on anxiety, assess therapy progress
   - **Context**: During 50-minute session, 10-15 minutes for protocol review
   - **Three-Act Story**:
     - Act 1: Client brings filled paper protocol, Dr. Sarah unfolds it on table between them
     - Act 2: Collaborative analysis - scan entries together, discuss patterns (team meetings = high anxiety, anticipatory anxiety > actual anxiety, avoidance reinforcing fear)
     - Act 3: Client gains insight ("my anxiety is about what MIGHT happen, not what happens"), next steps informed by data
   - **Success Criteria**: Identify 1-2 patterns, review in 10-15 min, client gains insight, gaps discussed therapeutically, privacy maintained, next steps informed by data
   - **Failure Modes**: Dr. Sarah analyzes alone (not collaborative), data overload, pattern blindness, privacy breach, client defensiveness
   - **Current Status Quo**: Paper on table, both look at same physical paper, manual pattern scanning
   - **Pain Points**: Hard to compare across days (must overlay papers), handwriting legibility, time-consuming scanning, no visual trends (graphs)

3. **Technology Neutrality**:
   - [x] No app behavior described
   - [x] Focus on WHAT needs to happen (collaborative analysis, pattern identification, insight generation)
   - [x] Current solution (paper on table) described as status quo
   - [x] Pain points explicit (overlaying multiple days' data is difficult with paper - user feedback quote)

4. **Process-Oriented Insights**:
   - Added section on what ELSE review reveals (compliance patterns, avoidance, honesty indicators, barriers)
   - Meta-data as therapeutically valuable as the data itself

5. **Cross-References**:
   - References PERSONA-001#jobs_to_be_done
   - Links to SCEN-001-01 (upstream scenario)
   - References PERSONA-001#environmental_constraints (privacy)

**Quality Check**:
- [x] Scenario describes collaborative review (WITH client, not alone)
- [x] No technical details
- [x] Success criteria outcome-focused
- [x] Current status quo (paper on table) documented
- [x] Pain points match user feedback (overlaying days' data is hard)
- [x] Review status YAML added
- [x] Cross-references use new notation
- [x] Emphasizes collaboration (per user feedback)

---

## Quality Criteria Verification

From Opus Plan Agent 2 quality criteria:

- [x] **Persona describes status quo without app**: YES - extensive "Current Status Quo" section, no app features
- [x] **No technical implementation details in persona**: YES - removed all references to SQLite, OLED, specific app features
- [x] **Scenarios describe goals, not app behavior**: YES - both scenarios focus on WHAT therapist wants to achieve, not HOW app solves it
- [x] **New YAML fields present and valid**: YES - `review_status: draft`, `review_history` with proper entries
- [x] **Pain points with paper approach documented**: YES - in persona (pattern recognition difficulty) and scenarios (overlaying data, portability)
- [x] **Two main scenarios exist (prepare + review with client)**: YES - SCEN-001-01 and SCEN-001-02

---

## Adherence to Technology Neutrality Principle

From README.md Section 15:

**Personas**:
- ✅ Removed "Implications for the App" section
- ✅ Added "Current Status Quo (Pre-App)" section
- ✅ Focus on paper-based workflow TODAY
- ✅ Pain points describe limitations of paper, not features of app

**Scenarios**:
- ✅ No "app dashboard loads" or "system queries database"
- ✅ Focus on goals: "prepare protocol", "review with client"
- ✅ Success criteria outcome-focused: "client understands instructions", "identify patterns in <15 min"
- ✅ No Material 3, no cloud sync, no technical details

---

## Cross-Reference Notation Usage

From README.md Section 13:

**Examples used in scenarios**:
- `PERSONA-001#jobs_to_be_done` (section reference)
- `PERSONA-001#current_status_quo` (section reference)
- `PERSONA-001#environmental_constraints` (section reference)
- `SCEN-001-01` (scenario reference)
- `SCEN-001-02` (scenario reference)

**Format**: `[DOC_TYPE]-[ID]#[SECTION]`
- ✅ Consistent with README standard
- ✅ No commit hash needed (all draft documents, not yet approved)

---

## Deviations from Plan

**None**. Plan was followed precisely:
1. Renamed folder ✅
2. Rewrote persona as female psychologist ✅
3. Focused on status quo (paper) ✅
4. Created 2 scenarios ✅
5. Removed technology details ✅
6. Applied review status system ✅

---

## Files Modified/Created

### Modified
- `requirements_user_needs/personas/dr_sarah/persona.md` (rewritten)

### Created
- `requirements_user_needs/personas/dr_sarah/scenarios/prepare_protocol_for_client/scenario.md`
- `requirements_user_needs/personas/dr_sarah/scenarios/review_protocol_with_client/scenario.md`

### Deleted
- `requirements_user_needs/personas/dr_sarah/scenarios/pre_session_patient_review/` (folder and contents)

### Renamed
- `requirements_user_needs/personas/dr_thomas/` → `requirements_user_needs/personas/dr_sarah/`

---

## Output for User

**Completion Summary**:

Agent 2 execution complete. Therapist persona (PERSONA-001) rewritten as requested:

**Changes Made**:
1. **Persona renamed**: Dr. Thomas → Dr. Sarah (female psychologist)
2. **Specialty updated**: Behavioral therapy (anxiety protocols, VT)
3. **Status quo focus**: Extensive documentation of paper-based workflow BEFORE app
4. **Solutions removed**: Deleted all app feature descriptions ("Design Implications" section)
5. **Anti-persona clarified**: NOT psychiatrist, NOT analyzing alone, NOT in waiting rooms
6. **Privacy constraint added**: Must not accidentally show client list with real names
7. **Review status added**: `review_status: draft`, awaiting user approval

**Scenarios Created** (2 new):
1. **SCEN-001-01**: Prepare Protocol for Client
   - Customizing paper protocol, handing to client, instructing them
   - Pain points: Clients forget paper, must carry pen, risk of loss

2. **SCEN-001-02**: Review Protocol WITH Client in Session
   - Collaborative analysis during session (not alone)
   - Pain points: Hard to overlay multiple days' data, handwriting legibility, time-consuming manual scanning
   - Explicit user feedback quote: "das Angstprotokoll verschiedener Tage übereinander legen kann"

**Old Scenario Removed**:
- Pre-Session Patient Review (described app usage, violated status quo principle)

**Files**:
- Persona: `requirements_user_needs/personas/dr_sarah/persona.md`
- Scenario 1: `requirements_user_needs/personas/dr_sarah/scenarios/prepare_protocol_for_client/scenario.md`
- Scenario 2: `requirements_user_needs/personas/dr_sarah/scenarios/review_protocol_with_client/scenario.md`

**Review Status**: All 3 documents marked as `draft` - awaiting user review before applying approach to remaining personas.

**Quality Verification**:
- ✅ Persona describes status quo (paper-based), not app solutions
- ✅ Scenarios are technology-neutral (no SQLite, no technical details)
- ✅ Cross-references use new notation (PERSONA-001#section)
- ✅ Review status YAML applied to all documents
- ✅ Pain points with paper explicitly documented

**Next Steps** (per plan):
- User reviews Dr. Sarah persona and scenarios
- If approved, Agent 3 documents change propagation process
- Follow-up task created to apply same changes to remaining personas (Max, Sarah self-user, System)

---

**Agent ID**: Sonnet 4.5 (Agent 2, Phase 4)
**Completion Time**: 2026-01-18
**Status**: COMPLETED - ready for user review
