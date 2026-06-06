# FLOW-003 Fit Review: Dr. Sarah (PERSONA-001) — SCEN-001-02

**Reviewer**: Opus (deep investigation specialist)
**Date**: 2026-03-23
**Artifacts reviewed**:
- PERSONA-001 (Dr. Sarah, v4.7, in_review)
- SCEN-001-02 (Review Protocol WITH Client in Session, v1.4, approved, gold_status: true)
- FLOW-003 (Session Start & Data Transfer, third iteration, in_review, 2026-03-23)
- READMEs 5, 6, 7, 8, 10, 12, 13, 14, 15

---

## Fit Score: 7/10

**Scope-adjusted score**: Within its declared scope — covering only the data transfer and visualization opening — FLOW-003 is a strong, well-considered partial solution. The 7/10 score reflects that the flow correctly solves the problems it claims to solve for Dr. Sarah, but leaves the heart of her scenario (the collaborative analysis) entirely unaddressed. The score would drop significantly if evaluated against the full scenario goal rather than just the transfer phase.

---

## What Works Well

### 1. Eliminates the root cause of Dr. Sarah's primary pain point

Dr. Sarah's key quote crystallises the problem: "But when they bring me crumpled papers filled out in the parking lot, what patterns can we possibly find?" FLOW-003 directly attacks Parking Lot Syndrome at the data-quality level. When entries are captured digitally on the client's device at the moment of experience, each entry carries a system timestamp. A client who batch-completes in the waiting room cannot forge 7 days of authentic timestamps. This is a structural improvement over paper that the flow implicitly enables — even though the flow document does not call it out explicitly as a benefit for Dr. Sarah. The scenario notes "All entries — Monday through Sunday — are written with exactly the same blue ballpoint pen" as the key diagnostic signal for compliance fraud; timestamps replace this unreliable visual heuristic with objective data.

### 2. Therapist device alignment is correct

The flow specifies: "Therapist has the app open on a laptop or desktop computer with a functioning webcam." Dr. Sarah's PCD field confirms "Windows desktop (office), occasional tablet." This is one of the most persona-specific design decisions in the flow and it is correct. A mobile-first therapist receive experience would have been a mismatch. The flow does not force Dr. Sarah to adopt an unfamiliar device form factor.

### 3. Privacy architecture addresses Dr. Sarah's GDPR fears directly

Dr. Sarah's top barrier is "Digital alternatives that sync to cloud without explicit control" and her VCD Security value states: "Patient data must never leave Dr. Sarah's physical control or go to cloud services. GDPR violations could end her practice. Technology requiring cloud infrastructure is a non-starter regardless of clinical benefits." FLOW-003's privacy architecture responds to every dimension of this fear:
- Local-only transfer (no internet required)
- Per-client data space isolation on the therapist device (preventing accidental exposure of another client's data — the scenario's "Intimate Intruder" threat)
- Structural (not behavioral) exclusion of private diary entries
- No cloud, no sync, no external server

The flow's own Environmental Considerations section explicitly names the "Intimate Intruder" threat from the persona YAML and specifies the mitigation: "the app must ensure the client data view does not display other clients' data in a visible sidebar." This is directly derived from Dr. Sarah's environmental threats and is correctly handled.

### 4. Visualization opens immediately without administrative friction

The scenario's success criterion states: "Review happens within 10-15 minutes (doesn't consume entire session)." The flow design decision to open the visualization immediately after transfer — no confirmation screen, no tap required — eliminates a potential time sink that would eat into the already-tight review window. The flow states explicitly: "No confirmation screen, no tap required — the visualization IS the confirmation." This respects Dr. Sarah's Efficiency value (her secondary VCD value: "10-15 minutes of a 50-minute session consumed by reviewing handwritten entries is 20-30% of therapeutic contact time lost").

### 5. CBT protocol type drives correct visualization variant

The Adaptive UI Rules specify: "If the protocol type is a structured mood/medication log (Dr. Sarah, Dr. Turan use case): visualization opens a timeline/trend view with numerical fields prominent." Dr. Sarah uses anxiety diaries (0–10 scale), activity schedules (mood + mastery ratings), and sleep diaries — all structured numerical protocols. A timeline/trend view is exactly what enables fast pattern recognition for these protocol types. The flow correctly identifies Dr. Sarah's therapeutic modality and maps it to the appropriate visualization — without requiring Dr. Sarah to configure this manually.

### 6. Client-controlled data scope respects the therapeutic alliance

The scenario emphasises that the collaborative review is about the client seeing their own patterns, not being judged. Exception 3.2 (client narrows scope) and Exception 3.1 (client declines to share) are handled non-judgmentally: "The app must make scope adjustment easy and non-judgmental — no 'Are you sure?' friction for narrowing." This aligns with the scenario's failure mode: "Client defensiveness: Dr. Sarah focuses on 'you didn't fill this out correctly' instead of 'what made it hard to log?'" The flow gives the client agency without penalizing non-disclosure, which supports the therapeutic relationship that Dr. Sarah depends on.

### 7. Bidirectional cross-referencing is correctly maintained

The scenario YAML references FLOW-003 with coverage: partial and the flow's serves_scenarios list includes SCEN-001-02. The coverage note in the scenario accurately describes what is and is not in scope. This is proper metadata hygiene per READMEs 7 and 8.

### 8. Skip persistence prevents re-traumatisation

Exception 3.2 documents that entries a client excludes in one session remain excluded in future sessions by default. The scenario mentions that Anna admitted she "left the paper at work Friday evening" — in the digital equivalent, a client who chose not to share crisis entries in session 1 should not find those same entries re-surfacing in session 2 as the default. The skip persistence rule is not explicitly derived from Dr. Sarah's scenario, but it protects her patients (especially Jana, PERSONA-014) and thereby protects Dr. Sarah from the failure mode of "Client defensiveness."

---

## Missing Elements

### 1. The collaborative analysis phase — the heart of the scenario — is entirely absent

This is the critical gap. SCEN-001-02's narrative is structured in three acts:
- Act 1 (2 paragraphs): Anna arrives, paper handover, Parking Lot Syndrome detected
- Act 2 (8 paragraphs): The 12-minute collaborative analysis — 4 observations, therapeutic dialogue, pattern identification
- Act 3 (5 paragraphs): Insights crystallised, next steps agreed, client leaves grounded

FLOW-003 covers Act 1 only (the handover moment). Acts 2 and 3 — which represent 80% of the scenario's content and all 7 success criteria — are explicitly declared out of scope. This is the correct scoping decision (collaborative analysis is per-therapist and belongs in a dedicated flow), but it means FLOW-003 is the door to the room, not the room itself. For Dr. Sarah specifically, the gap includes:

- **Pattern recognition features**: The scenario shows Dr. Sarah making 4 specific observations from paper data. In the digital equivalent, she needs to be able to point at the visualization and say "This spike on Thursday — tell me about that." The flow delivers a visualization but does not define what interactive capabilities it has.
- **Cross-week comparison**: The scenario pain point states "To compare across weeks, must pull out previous week's paper and hold them side-by-side." FLOW-003 delivers the current week's data in a visualization but is silent on whether prior weeks' data (already received in previous sessions) is visible alongside it, or how multi-week comparison is presented.
- **Compliance detection UI**: The scenario's Act 1 is about Dr. Sarah noticing Parking Lot Syndrome from physical cues (uniform pen, identical handwriting). In the digital equivalent, timestamps provide objective compliance data. But FLOW-003 does not specify whether the visualization surface entry timestamps prominently or whether compliance patterns are surfaced to Dr. Sarah. This is a gap in the flow's specification of the visualization, even within its declared scope.
- **Next steps documentation**: The scenario ends with Dr. Sarah and Anna agreeing on a modified protocol for next week ("Add a new column: 'What I feared would happen' vs. 'What actually happened'"). This protocol modification workflow (SCEN-001-04, the planned Mid-Session Protocol Pivot) is not addressed by FLOW-003 or any existing flow.

### 2. The tactile collaboration ritual is not replaced or re-imagined

The scenario describes Dr. Sarah unfolding the paper "on the small table between them — not on her desk — symbolic of collaboration." This physical placement is deliberate: it signals to the client that the data belongs to them and will be reviewed together. The scenario explicitly lists "Physically collaborative: Both can see the same paper, point to same entries" as one of the four things that works well in the paper system.

FLOW-003 delivers the data to the therapist's desktop screen. But the flow does not address the question of how both parties view the visualization simultaneously. Does the client see the therapist's screen? Is the screen turned to face the client? Is there a shared view? The scenario's success criterion — "Client gains insight from seeing their own data (not just therapist's interpretation)" — depends on the client being able to see the data during the review. The flow's environmental note says "Both therapist and client can see the screen" at Step 9 (after transfer), but this is a single sentence with no flow steps supporting it. It is assumed, not designed. The paper system's physicality (paper on a shared table) made this joint visibility automatic. The digital system requires it to be explicitly designed into the collaborative analysis phase — which is out of scope for this flow, creating a gap that the planned analysis flow must address.

### 3. No mechanism for the client to take insights home

The scenario lists "Tangible: Client can take paper home as reminder of insights" as one of the four things that works well about paper. In the digital system, the client's own app still contains their data, so they have access to their entries. But the specific artifact created in the session — the patterns identified, the therapeutic insights written on the protocol, the next-step annotations — has no equivalent. The paper protocol Anna folds and puts back in her bag carries the session's output. The digital equivalent needs to be defined somewhere, and FLOW-003 is silent on it. This gap likely belongs in the planned collaborative analysis flow, but it should be flagged here because it is one of the scenario's explicit "what works" items.

### 4. The Environment column is not used despite qualifying conditions

README_5 specifies: "Include Environment column when: flow involves sensitive content (mood entries, therapy notes); flow could be interrupted by others (home, office, public); user might need to quickly hide content." FLOW-003 meets all three criteria — it involves sensitive therapy data, occurs in a therapy office where colleagues can walk past (shoulder surfer threat from persona YAML), and the client's Data Scope Screen shows entry summaries in a waiting room context.

The flow uses a Swimlane column (for client vs. therapist perspective) but does not use the Environment column. The environmental considerations are documented in a separate section at the end of the flow rather than integrated into the step-by-step table. This is a structural gap relative to README_5's guidance. For Dr. Sarah specifically: a colleague walking past during Step 9 (when the therapist's screen shows client data) is a real threat that the persona YAML flags but the flow table does not surface at the step level.

### 5. No guidance on the Data Scope Screen interaction during the session moment

The scenario is set in the therapy room at the start of the session. The client (Anna) is sitting across from Dr. Sarah. The happy path steps 2–3 have the client reviewing the Data Scope Screen and confirming scope. This is a non-trivial in-session interaction: the client is using their phone in front of the therapist, potentially feeling evaluated for what they choose to share or exclude.

The flow does handle Exception 3.1 (client declines to share) and Exception 3.2 (client narrows scope) non-judgmentally. But it does not address the interactional dynamic from Dr. Sarah's perspective — what does she do while the client navigates the Data Scope Screen? What is the intended conversational rhythm? The paper equivalent (client pulls paper from bag, hands it over) took 10 seconds. The digital equivalent could take 30–60 seconds if the client needs to review scope options. This is not necessarily a problem, but it is an unexamined dimension of the session moment that the scenario captures richly and the flow does not.

---

## Contradictions

### 1. The "Fit" for SCEN-001-02 is listed as `relationship: primary` — which is an overstatement

In SCEN-001-02's implements_flows YAML, the relationship is `primary`. In FLOW-003's Scenarios Served table, the relationship is also listed as `primary`. But SCEN-001-02's goal is "Review a client's filled anxiety protocol together during the therapy session, identify patterns, discuss influences on anxiety, and assess therapy progress." FLOW-003 does not address pattern identification, discussion, or therapy progress assessment. These are the goal's core verbs.

A `primary` relationship implies that this flow is the main approach to achieving the scenario goal. But FLOW-003 delivers only the setup for the goal, not the goal itself. The relationship should arguably be `supporting` (partial solution or prerequisite flow) rather than `primary`. The coverage: partial designation is correct and the coverage notes are accurate, but the combination of `primary` + `partial` creates a misleading impression. README_7 defines: `primary` = "Main approach to achieve scenario goal." FLOW-003 is not the main approach to achieving SCEN-001-02's goal — it is the necessary prerequisite.

This is not a contradiction within the flow itself but between the flow's declared relationship to the scenario and the scenario's actual goal. It should be corrected.

### 2. The "No confirmation screen" design conflicts with the collaborative handover ritual

The flow states: "No confirmation screen, no tap required — the visualization IS the confirmation." This is efficient (it reduces friction for Dr. Sarah). But it removes the brief interstitial moment that could serve as a digital equivalent of the paper handover ritual. In the paper system, Dr. Sarah takes the paper, unfolds it, places it on the table — a 15-second ritual that signals "we are now entering the review phase together." In the digital system, the visualization opens automatically on the therapist's screen without any shared moment.

This is not necessarily wrong — the QR transfer process (client holds phone toward webcam, both watch progress) may serve as the ritual equivalent. But the flow does not explicitly acknowledge this substitution or design it as such. The scenario notes the collaborative quality of the handover as a feature, not merely an incidental. The flow's efficiency-first approach to Step 9 may inadvertently sacrifice this dimension.

This is a soft contradiction: the flow optimises for one of Dr. Sarah's values (Efficiency) in a way that may work against another implicit value (the therapeutic relationship's collaborative texture, which the scenario documents carefully).

### 3. Client confirmation of transfer success creates an unexpected new friction point

At Step 8, the client must explicitly choose "Transfer Successful" or "Transfer Failed" before entries are marked as shared. The rationale is technically sound (the QR channel is optically unidirectional; the client's app has no way to verify receipt). But this creates a new interaction that has no equivalent in the paper system — and it happens at the end of the transfer, which is already a multi-step process.

The scenario's paper handover takes: (1) client pulls paper from bag, (2) Dr. Sarah takes paper, (3) Dr. Sarah unfolds it. Three actions, 10 seconds, zero decisions required of the client. The digital flow requires: (1) client opens transfer section, (2) reviews Data Scope Screen, (3) confirms scope and mode, (4) displays QR code, (5) holds phone toward webcam for ~45 seconds, (6) confirms success or failure. Six steps, one explicit binary decision, 60+ seconds.

The flow's success metric states: "Transfer completes in under 60 seconds for a typical week of entries." The paper handover takes 10 seconds. The flow is 6x slower for the handover moment alone — before the collaborative analysis even begins. This is likely acceptable given the quality improvement (digital data vs. paper), but the scenario's emphasis on session time preservation ("10-15 minutes of a 50-minute session consumed") means this overhead deserves explicit acknowledgment. The flow does not quantify the session-time cost of the transfer itself.

### 4. The `relationship: primary` claim in the Scenarios Served table conflicts with the "partial" coverage note

Within FLOW-003 itself, the Scenarios Served table lists SCEN-001-02 with `relationship: primary` and `coverage: partial`. The flow's coverage note then states: "This flow covers partial coverage of SCEN-001-02, SCEN-011-02, and SCEN-012-02. It handles the data transfer and visualization opening — the universal entry point. The subsequent collaborative analysis... has high persona-specific variance and is addressed by dedicated per-therapist analysis flows (planned)."

The flow acknowledges that what it covers is only the "entry point" to the scenario goal. An entry point to a goal is not the primary approach to the goal — it is a prerequisite. This internal tension within the flow document is minor but worth correcting for precision.

---

## Observations on Partial Coverage

### Is "partial" the right call?

Yes. "Partial" is the correct and honest coverage designation, and the notes explaining what is and is not in scope are well-written and accurate. The alternative designations would be:
- `full`: Wrong. The scenario's goal (collaborative pattern identification, therapeutic discussion, insight generation, next steps) is not addressed by FLOW-003.
- `minimal`: Too harsh. FLOW-003 solves a real, painful problem (the paper handover's failures) and creates the precondition for everything that follows.
- `partial`: Correct. FLOW-003 handles the transfer and visualization opening — two of the scenario's sub-goals — but not the core goal.

### What would full coverage require?

Full coverage of SCEN-001-02 would require addressing all 7 success criteria:

| Success Criterion | FLOW-003 Status | Gap |
|---|---|---|
| Collaboratively identify 1–2 meaningful patterns | Not addressed | Needs dedicated collaborative analysis flow |
| Review in 10–15 minutes | Partially addressed (visualization opens fast) | The analysis tools within the visualization are unspecified |
| Client gains insight from seeing own data | Not addressed | Requires client-visible shared screen design |
| Gaps/inconsistencies discussed therapeutically | Not addressed | Requires compliance metadata surfacing in visualization |
| Privacy maintained (no other clients' data visible) | Fully addressed | Per-client data space isolation |
| Next steps informed by data | Not addressed | Requires protocol modification or annotation capability |
| Client feels validated for effort | Partially addressed (non-judgmental scope handli