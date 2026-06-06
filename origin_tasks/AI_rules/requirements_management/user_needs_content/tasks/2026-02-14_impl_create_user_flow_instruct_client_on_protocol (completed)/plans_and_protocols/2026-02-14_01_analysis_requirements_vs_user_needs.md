# Analysis: Requirements vs. User Needs — "Instruct Client on Protocol"

**Task**: TASK-PROC-027-13
**Date**: 2026-02-15
**Status**: Approved (2026-02-15, human review)

## Documents Analyzed

### Therapist-Side Scenarios (instruct_client_on_protocol)
| ID | Persona | Status | Duration | Approach |
|----|---------|--------|----------|----------|
| SCEN-001-03 | Dr. Sarah (VT/CBT) | **Gold standard**, approved | 10 min instruction | Didactic, column-by-column, barrier discussion |
| SCEN-011-03 | Prof. Dr. Weber (Depth/PA) | Approved | 12+ min, open-ended | Ritual, minimal words, silence, waiting |
| SCEN-012-03 | Dr. med. Turan (Psychiatry) | Approved | 4 min total (within 12 min slot) | Efficiency-driven, safety-first, medical |

### Client-Side Scenarios (receive_protocol_homework)
| ID | Persona | Status | Core Challenge |
|----|---------|--------|----------------|
| SCEN-002-04 | Max (Depression) | **Gold standard**, approved | White Sheet Syndrome, cognitive paralysis, context collapse |
| SCEN-010-03 | Sophie (ADHD) | Approved | Object permanence cliff, hyperfocus-to-abandonment cycle |
| SCEN-014-03 | Jana (BPD) | Approved | Volatility erasure fear, format resistance, alliance fragility |
| SCEN-009-01 | Elias (Social phobia) | Approved | Evidence creation anxiety, storage crisis, privacy obsession |
| SCEN-016-01 | Lena (Grief/Depth) | Approved | 3 AM capture problem, medium confusion, transitional objects |

### Requirements
| ID | Document | Status |
|----|----------|--------|
| REQ-FUNC-007 | epic_data_transfer | Draft |
| REQ-FUNC-007-01 | feat_therapist_transfer_ui | Draft |
| REQ-FUNC-007-02 | feat_plan_receiving | **Placeholder** (not yet explored) |

### Additional Context
| Document | Relevance |
|----------|-----------|
| PERSONA-015 (App Provider) | Product philosophy: zero-cloud, gaps-are-data, no shame, local-first |

---

## 1. What the Requirements Assume About the Session Moment

The epic_data_transfer requirements were created from Figma prototypes that preceded the persona system. They make the following assumptions — some explicit, most implicit:

### Explicit Assumptions
- The therapist has already created a "plan" in the app and is ready to transfer it
- The client either has the app installed (returning client) or will install it (new client)
- The transfer happens either face-to-face ("Vor Ort") or remotely ("Fernübertragung")
- Privacy concerns are about the **client database** (no autocomplete to expose other patient names)
- The dialog title is "Plan aushändigen" — framing the moment as **handing out** a deliverable

### Implicit Assumptions
- **The instruction already happened**: The requirements start at "therapist clicks transfer button." They assume the therapeutic instruction (explaining the protocol, discussing barriers, calibrating expectations) has already occurred through some other means. The transfer dialog is pure logistics.
- **The client is cognitively ready**: The requirements assume the client can hold their phone, open the app, navigate to the scanner, and scan a QR code — all while processing the emotional weight of what was just explained in session.
- **The transfer is the event**: The requirements structure (dialog → client selection → pairing → QR beam) treats the digital transfer as the primary interaction. In reality, it is a supporting act within a much larger therapeutic moment.
- **One-way flow**: The requirements flow is therapist → app → QR → client app. There is no concept of the client's emotional state, their readiness to engage with technology, or the therapist's judgment about whether this is the right moment for a digital handover.
- **Session time is available**: The requirements don't model session time pressure. The pairing flow (new client) adds steps that consume scarce session minutes.

---

## 2. What the Scenarios Describe as the Real Session Context

The 8 scenarios paint a fundamentally different picture of this moment:

### The Instruction IS the Event
Every therapist scenario treats the **verbal instruction** as the primary therapeutic intervention:
- **Dr. Sarah** spends 10 minutes walking through columns, proactively discussing barriers, calibrating expectations ("three honest entries > seven dutiful ones"). The instruction is psychoeducation — teaching a skill, not delivering a form.
- **Prof. Dr. Weber** creates a ritual around the handover. He places the handwritten page, waits in silence for Lena to read, speaks only when she asks. The instruction is relational — the act itself carries therapeutic meaning.
- **Dr. Turan** compresses everything into 90 seconds of essential safety information. He says "call if agitated" twice — the one instruction he permits himself to repeat. The instruction is medical triage.

**Key insight**: In all three cases, the physical handover of paper (or digital transfer) is a **footnote** to the instruction. The instruction cannot be replaced, accelerated, or automated. The digital transfer must fit around it, not compete with it.

### Client Cognitive State at Handover
The client-side scenarios reveal that at the moment of receiving the protocol, clients are in varying states of cognitive/emotional load:

| Client | State at Handover | Implication for Digital Transfer |
|--------|-------------------|----------------------------------|
| Max | Session-fatigued, cognitively depleted, fragile intention | Cannot process additional technology steps; needs seamless, invisible transfer |
| Sophie | Hyperfocused, excited, system-building | Might enjoy the QR scanning as a novelty; risk of overengineering the moment |
| Jana | Wary, relationally fragile, quietly defiant | Technology adds distance; the alliance is more important than the mechanism |
| Elias | Threat-scanning, evidence-averse, calculating exposure risk | QR scanning in presence of therapist may feel like surveillance; needs maximum control |
| Lena | Ambivalent, grief-tinged hope, holding a transitional object | The handwritten page IS the intervention; digitizing it may strip meaning |

### Time Pressure Is Real and Variable
- **Dr. Sarah**: 10 min for instruction within 50-min session. Medium pressure. Digital transfer would add 2-3 min.
- **Prof. Dr. Weber**: Open-ended. No time pressure. But the digital transfer would break the ritual silence.
- **Dr. Turan**: 4 min total within a 12-min slot. **Zero margin**. Digital transfer would consume time he does not have.

### Privacy Means Different Things
The requirements address **database privacy** (no client list exposure). The scenarios describe **protocol privacy** — fundamentally different concerns:

| Concern | Source | What It Means |
|---------|--------|---------------|
| Database privacy | Requirements | Other patients' names must never appear (no autocomplete) |
| Transit privacy | Anna (SCEN-001-03) | The protocol is visible on the train, at the desk — column headers reveal the condition |
| Storage privacy | Elias (SCEN-009-01) | The protocol must be hideable from a partner in a shared apartment |
| Evidence privacy | Elias (SCEN-009-01) | The protocol's very existence proves he's in therapy |
| Content privacy | Lena (SCEN-016-01) | Dream journal entries are the most vulnerable text she'll ever produce |
| Physical privacy | Dr. Turan (SCEN-012-03) | Medication name + "suicidality" on the form, open-plan office |

The requirements' database privacy is necessary but insufficient. The app must support the client's privacy **after** transfer — but this belongs to the client-side experience, not the transfer dialog.

---

## 3. Gaps: Requirements That Have No User Needs Grounding

These are requirement elements with no scenario support:

### Gap G1: Self-Test Mode ("Testen" tab)
**Requirement**: Therapist switches to client mode to preview how questions appear.
**Scenarios**: No scenario describes a therapist wanting to preview client experience before handover. Dr. Sarah prepares the paper form the evening before (SCEN-001-01). Dr. Turan photocopies a standard form. Prof. Dr. Weber handwrites prompts on personal stationery. None of them test the form from the client's perspective.
**Assessment**: This is a **reasonable product feature** with no user needs evidence. It may address a real need that hasn't been captured in scenarios — especially for therapists learning the app. Not a tension, but a gap to acknowledge.

### Gap G2: Verbal Pairing Alternative (BIP-39 word chain)
**Requirement**: 8-word German mnemonic read aloud for phone-only remote sessions.
**Scenarios**: All 8 scenarios describe face-to-face handovers. Remote therapy sessions are mentioned nowhere.
**Assessment**: Remote transfer is a valid product capability (especially post-COVID), but the user flow should treat it as an **exception path**, not a primary flow.

### Gap G3: Animation Speed Slider
**Requirement**: QR animation speed adjustable from 100ms to 500ms.
**Scenarios**: No scenario discusses QR scanning or technical transfer parameters.
**Assessment**: Pure technical detail. Should not appear in the user flow.

### Gap G4: Client Selection (Existing vs. New Client)
**Requirement**: Segmented button toggling between "Bestehender Klient" and "Neuer Klient."
**Scenarios**: Therapist scenarios don't model client database management. The therapist knows who is sitting across from them.
**Assessment**: Necessary product UI, but in the user flow, this is a **transparent step** — the therapist types a name, the system figures out whether pairing is needed.

---

## 4. Tensions: Requirements That Conflict With the Session Reality

### Tension T1: Transfer-First vs. Instruction-First
**Requirements say**: Dialog opens → select client → start QR beam. Transfer is the action.
**Scenarios say**: Therapist explains protocol (2-10+ minutes) → client processes → physical handover → THEN (maybe) digital transfer. Instruction is the action.

**Impact**: If the user flow follows the requirements, it tells a story of "click button, scan code, done." If it follows the scenarios, it tells a story of "therapist teaches, client receives, paper changes hands, and oh — there's also a digital copy being transferred."

**Recommendation**: The flow's happy path must start with the instruction moment and embed the digital transfer as a **concurrent or concluding step**, not the main event.

### Tension T2: "Plan aushändigen" vs. "Instruct Client on Protocol"
**Requirements frame**: "Plan aushändigen" — handing out a plan. Transactional.
**Scenarios frame**: "Instruct client on protocol" — teaching a skill. Therapeutic.

**Impact**: The naming reveals the worldview gap. The requirements see this as delivery logistics. The scenarios see this as a psychoeducation intervention. The user flow must honor the therapeutic reality.

**Recommendation**: The flow should use language that centers the instruction, not the transfer. The transfer dialog is a tool the therapist uses within the instruction moment, not the moment itself.

### Tension T3: QR Scanning During Emotional Processing
**Requirements say**: After pairing, "Data Beam starts immediately." Client scans QR sequence.
**Scenarios say**: At this moment, Max is cognitively depleted. Jana is emotionally fragile. Elias is threat-scanning. Lena is holding a transitional object.

**Impact**: Asking a client who just received emotionally significant therapy homework to immediately pull out their phone and scan a QR code creates a **register clash** — switching from therapeutic reception to technical interaction.

**Recommendation**: The flow must acknowledge this transition. The therapist decides when to initiate the digital transfer. It may happen immediately (Sophie: eager), after a pause (Max: needs a moment), or at the end of the session (Jana: alliance first). The flow should model this as a **therapist-paced transition**, not an automatic sequence.

### Tension T4: Pairing Adds Steps That Consume Session Time
**Requirements say**: New client requires pairing (static QR → client scans → stores secret → then data beam).
**Scenarios say**: Dr. Turan has 12 minutes total for the entire appointment. Adding pairing + transfer would consume 2-4 minutes he does not have.

**Impact**: For high-volume practitioners, the first-session digital handover may be **impossible within the appointment**. This is not a UI problem — it's a structural constraint.

**Recommendation**: The flow must include an exception path: "Pairing happens outside the instruction moment" — e.g., at reception before the appointment, or the client does it at home later. The instruction and the digital transfer are separable events.

### Tension T5: One-Way Communication vs. Client Readiness
**Requirements say**: "App cannot detect when client has scanned (one-way communication)."
**Scenarios say**: The therapist is the one who monitors whether the client is ready. Dr. Sarah watches Anna's face. Dr. Turan observes the jacket pocket.

**Impact**: The lack of bidirectional confirmation is fine technically but should be reflected in the flow — the therapist visually confirms the client has received the plan, then closes the dialog.

**Recommendation**: Minor. The flow should note that the therapist verbally confirms with the client ("Got it? Can you see the plan?") rather than relying on app confirmation.

---

## 5. Missing: User Need Moments That Requirements Don't Address

### Missing M1: The Bridge to First Entry
**Every client scenario** describes the critical moment between receiving the protocol and making the first entry. Max faces the blank form alone at home. Sophie builds an elaborate fridge station. Elias hides the paper and agonizes over opening it. Lena places the handwritten page in a notebook and wonders if she'll write tonight.

**The requirements address**: Transfer mechanics (how the plan gets to the device).
**The requirements miss**: What happens when the client opens the app for the first time after the session. The "bridge to first entry" is the moment where compliance lives or dies.

**Implication for flow**: The flow should extend past the in-session transfer to include the client's first interaction with the received plan at home. This is where the app can do what paper cannot — persist the therapist's verbal instruction, display a gentle first-entry prompt, communicate "gaps are data."

### Missing M2: Instruction Persistence
**Dr. Sarah's central design implication**: "The verbal instruction evaporates by Thursday." Anna has no reference for how Dr. Sarah said to fill out the form. The column headers are terse. The nuance ("avoidance counts," "even a guess is useful," "shorthand is fine") lives only in memory.

**The requirements address**: Plan template transfer (questions, schedules).
**The requirements miss**: The instruction layer — the therapist's verbal explanation of how to use the plan, which barriers to expect, what "good enough" looks like.

**Implication for flow**: The flow should note that the transferred plan carries more than data structure — it should carry (or support) the instruction context. This could be as simple as a "therapist note" field or as rich as per-question guidance text.

### Missing M3: Expectation Calibration
**All three therapists** calibrate expectations differently:
- Dr. Sarah: "Three honest entries > seven dutiful ones"
- Dr. Turan: "Five out of seven is enough"
- Prof. Dr. Weber: "When something surfaces" (no frequency target)

**The requirements address**: Plan structure and transfer.
**The requirements miss**: How the app communicates expectations to the client after the session, when the therapist's voice is no longer present.

**Implication for flow**: The flow should note that expectation calibration is part of the handover — and that the app must reinforce (not contradict) the therapist's verbal calibration. "Gaps are data, not failure" (App Provider principle) is the product-level answer, but the therapist must be able to customize this.

### Missing M4: Safety Instruction Persistence
**Dr. Turan's scenario** contains a critical safety need: "Call if agitation or dark thoughts — don't wait." This instruction is written on the paper protocol. If the paper is lost (jacket pocket → washing machine), the safety instruction is lost.

**The requirements address**: Transfer encryption and pairing.
**The requirements miss**: Safety instructions that must survive the destruction of the carrier medium.

**Implication for flow**: The flow should note that for medication monitoring protocols, safety instructions are not optional metadata — they are life-critical content that must be persistently accessible to the client, independent of whether they open the tracking form.

### Missing M5: Client-Side Emotional Onboarding
**Max's scenario** describes "context collapse at the door" — the protocol has meaning in the therapy room but feels like an obligation at home. **Sophie's scenario** describes "object permanence cliff" — the app must remain visible or it ceases to exist.

**The requirements address**: Technical receiving (scan QR, import file, decrypt).
**The requirements miss**: The emotional transition from "I received this in session" to "I'm using this at home alone."

**Implication for flow**: The flow's client-side steps should address this transition — not with technical steps but with emotional design moments: a warm first-open experience, a gentle reminder of why this plan was created, absence of any "you haven't started yet" guilt.

### Missing M6: Protocol Variety
**The scenarios describe radically different protocol types**:
- Structured columns with rating scales (Dr. Sarah's Anxiety Protocol, Dr. Turan's Medication Monitoring)
- Free-form journaling prompts (Prof. Dr. Weber's Dream Journal)
- Adapted formats for specific conditions (Sophie's Mood-and-Medication, Jana's with range notation workaround)

**The requirements address**: "Plan" as a generic transferable unit.
**The requirements miss**: The flow must work for ALL these protocol types — from highly structured daily tracking to open-ended grief journals with no frequency expectation.

**Implication for flow**: The flow should use exception paths or branching to acknowledge that the instruction moment differs fundamentally by protocol type. The "happy path" should work for the common case (structured protocol, face-to-face, returning client) while exceptions handle depth-psychology journals, first-session pairing, remote transfer, and psychiatric efficiency scenarios.

---

## 6. Synthesis Recommendations

### The Happy Path Should Reflect a Real Therapy Session

**Proposed happy path structure** (from the therapist's real experience):

1. **Therapist has prepared protocol** (upstream: SCEN-001-01 category)
2. **Session is underway** — therapist identifies the right moment
3. **Instruction begins** — therapist explains the protocol verbally (2-10+ minutes depending on therapeutic approach)
4. **Barrier discussion** — therapist addresses obstacles (forgetting, privacy, perfectionism, first-entry timing)
5. **Expectation calibration** — therapist communicates "good enough" threshold
6. **Physical/digital handover** — protocol enters the client's world
   - Paper: client takes the form
   - Digital: therapist initiates transfer on their device; client receives on their device
   - Both: therapist hands paper AND transfers digitally (most likely for the app's first users)
7. **Client receives and stores** — the protocol transitions from "therapy room object" to "home object"
8. **First entry** (hours later) — client faces the plan alone for the first time

### The Flow Must Span Both Perspectives

Unlike most user flows (single persona), this flow bridges **therapist and client**:

| Phase | Therapist's Experience | Client's Experience |
|-------|------------------------|---------------------|
| Instruction | Teaching, calibrating, reading the room | Listening, processing, building intention |
| Transfer | Initiating on their device, monitoring client | Scanning/receiving on their device, cognitive switching |
| Post-session | Moving to next client, brief notes | Carrying the plan home, facing first entry alone |

### Exception Model (per README_5)

The following should be modeled as numbered exceptions rather than branching happy paths:

| Exception | Trigger | Impact |
|-----------|---------|--------|
| **E1**: First-time client (pairing required) | No existing key | Additional 1-2 min for pairing step in session |
| **E2**: Remote session | Video/phone, not face-to-face | File export instead of QR; verbal pairing if phone-only |
| **E3**: High-volume psychiatric context | <5 min total appointment | Instruction compressed to essentials; transfer may happen outside session |
| **E4**: Depth-psychology ritual handover | Open-ended therapeutic frame | No time pressure; digital transfer may be deferred or omitted |
| **E5**: Privacy-critical client | Evidence anxiety, shared living | Additional barrier discussion; may use anonymous storage settings |
| **E6**: Client without app installed | First encounter with the app | Instruction includes app installation guidance; pairing deferred |
| **E7**: Paper + digital hybrid | Therapist gives paper AND transfers digitally | Both channels deliver the same content |

### What the Digital Transfer Adds (vs. Paper)

The flow should highlight the value proposition — what the app provides that paper cannot:

| Paper Pain Point (from scenarios) | Digital Solution |
|-----------------------------------|------------------|
| Paper is destroyed (jacket pocket, washing machine) | Data persists on device |
| Verbal instruction evaporates by Thursday | Instruction can persist as in-app guidance |
| Safety instruction unreachable if paper lost | Safety alerts accessible independent of tracking |
| No between-appointment visibility (Dr. Turan) | Potential for data sharing at follow-up |
| Compliance decay without nudges | Gentle, non-shaming reminders (respecting "gaps are data") |
| Retroactive fabrication undetectable | Timestamped entries provide authentic data |
| Paper-KIS disconnect | Potential for structured data export |
| Privacy breach if form discovered | App-level privacy (lock, biometrics, neutral icon) |
| No motif tracking (Lena's dream journal) | Searchable, taggable entries |
| No object permanence (Sophie) | Notifications respecting ADHD medication windows |

### What the Digital Transfer Must NOT Do

Per App Provider principles (PERSONA-015) and scenario evidence:

- **Must NOT create shame**: No "you haven't started yet" messages, no streak counts, no red indicators for gaps
- **Must NOT rush the instruction**: The app supports the therapist's verbal instruction; it does not replace it
- **Must NOT assume daily compliance**: "Gaps are data, not failure" — the app must normalize partial use from day one
- **Must NOT compete with the therapeutic moment**: The QR scanning is a logistics step, not the emotional center of the handover
- **Must NOT flatten protocol variety**: A grief journal with four open prompts and no frequency target must feel as native as a daily anxiety tracking form with five columns

---

## User Review Decisions (2026-02-15)

### Q1: Include first entry at home?
**Decision: YES.** The flow includes the client's first entry at home as a formal step. This is also the moment when the client customizes notification times (app notification schedule is user-configurable).

### Q2: Paper+digital hybrid as happy path?
**Decision: NO.** The happy path is app-only (no paper). The app flow must work standalone. Paper+digital hybrid is not modeled as the primary path — the design decision is to make the app experience self-sufficient, not because paper won't exist but because the app shouldn't depend on it.

### Q3: Include instruction persistence?
**Decision: YES.** The flow includes the in-app instructions the client sees during later usage. The therapist may verbally reference these during the session and even show the UI to the client. Note: existing data domain layer requirements already cover parts of this but are not yet sufficient to cover all user needs. The flow should reference what the app shows, not just what the therapist says.

### Q4: Therapist-paced transfer + protocol preview?
**Decision: YES — with a significant new design insight.** The therapist has full control over when the Data Beam starts. Additionally: **the transfer dialog should show a preview of the protocol that the therapist can use to explain it to the client** — replacing the paper walkthrough with a screen-based one. This works because the therapist is assumed to use a laptop/desktop with a large enough screen to show the client. The transfer dialog becomes a **dual-purpose tool**: instruction aid + transfer mechanism. The therapist opens the dialog, walks through the protocol preview with the client (like Dr. Sarah does column-by-column with paper), then initiates the transfer when ready.

### Q5: Remote transfer as exception?
**Decision: EXCEPTION within same flow.** Remote transfer is modeled as exception paths, keeping the flow as similar as possible to the face-to-face path.
