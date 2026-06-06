# FLOW-003 Fit Review: Max (PERSONA-002) — SCEN-002-02

**Reviewed**: 2026-03-23
**Reviewer**: Opus (claude-opus-4-6)
**Flow version**: Third iteration (updated 2026-03-23, review_status: in_review)
**Persona version**: 5.2 (review_status: in_review)
**Scenario version**: 1.3 (review_status: approved, gold_status: true)

---

## Fit Score: 7/10

The flow resolves the scenario's core structural failure mode (physical object forgotten) decisively and with appropriate technical depth. The shame-awareness built into the flow's emotional design is genuine and shows careful persona reading. The score is held below 8 primarily because the flow underserves Max's specific cognitive and emotional context at the moment of transfer — the session-start environment — and because "full" coverage is claimed for a scenario whose success criteria extend meaningfully beyond what the flow addresses.

---

## What Works Well

### 1. Core Problem Elimination

The scenario's foundational failure is structural: data exists in exactly one physical location, and Max forgot to carry that location to the session. The flow eliminates this failure mode completely. Data stored on a phone Max already carries everywhere (Derived Need 2) is always with him. This is the right architectural response and the flow articulates it explicitly in its Overview section: "A digital transfer eliminates both failure modes while preserving the ritual quality of the handover moment."

### 2. Shame-Free Exception Design

The most carefully executed section of the flow for Max is Exception 2.2 (no transferable data). The language "No data to transfer yet" with explicit non-shameful framing and no error state is precisely aligned with Max's primary VCD value of Non-maleficence (Shame-Free Design). The therapist is not involved — no notification, no awkward moment — which prevents the exact dynamic the scenario documents: the hot-faced confession across from Dr. Sarah.

Similarly, the emotional success metrics are well-grounded in Max's psychology:
- "Client with missing/incomplete data does not feel shamed — 'what you have is enough for now'"
- "Client confirming a failed transfer is not blamed — the app treats this as a recoverable situation, not an error"
- Troubleshooting hints designed explicitly not to create pressure or urgency

These are not generic UX platitudes. They reflect the specific shame cycle documented in the persona and scenario.

### 3. Privacy Boundary as Structural Guarantee

Max's VCD includes Self-Direction (Private vs. Shared Data) as a secondary value: "He must control which data the therapist sees — blurring this boundary violates his sense of autonomy." The flow's structural (not behavioral) exclusion of private entries — Brain Dump lists, Energie-Tankstelle, Erfolgs-Tagebuch — directly serves this. The client never sees private entries listed as "shareable." They are absent from the transfer view. This is stronger than a toggle because it removes the cognitive burden of deciding and the fear of accidental inclusion.

### 4. Handover Ritual Preservation

The scenario notes that the paper system's clear handover ritual is one of its genuine strengths: "The physical act of handing paper to Dr. Sarah creates a clear beginning to the data review portion of the session. It's a concrete transition moment." The flow consciously preserves ritual quality. The dedicated navigation entry for transfer, the explicit "Transfer Successful" confirmation (Step 8), and the automatic visualization opening (Step 9) all create a structured moment of handover rather than a silent background sync. The emotional success metric "Client feels the handover moment is meaningful — 'I shared my data, it counts'" directly mirrors Sophie's paper handover ritual (cited in the flow), and it applies equally to Max's social job-to-be-done: demonstrating effort to the therapist.

### 5. Skip Persistence

Exception 3.2 and its persistence mechanism deserve specific mention in Max's context. Max has private protocols he will never share. The scenario documents that Dr. Sarah has private data (Brain Dump at night) that sits alongside his therapy homework in any app. The skip persistence feature — "if the client decided not to share something in session 1, they likely still do not want to share it in session 2" — respects Max's autonomy without requiring him to re-exercise that decision every session. This reduces cognitive load and prevents a recurring moment of vulnerability.

### 6. QR Troubleshooting Tone

Exception 4.1B (client side troubleshooting) is carefully written for Max's emotional profile: "Hold your phone steady with the screen facing the webcam. No urgency language. No error framing." The explicit constraint — the hint must never cover the QR code, must not create a feeling of rush, shame, or guilt — is consistent with an anti-trait: "unwilling to spend more than 2-3 minutes on an entry." Any technical friction that produces a shame response could cause Max to abort the transfer, which is worse than a suboptimal paper handover.

### 7. Adequate Battery Awareness

The Adaptive UI Rule for very low battery ("Battery low — keep your phone screen on during transfer") acknowledges Max's PCD constraint directly: Budget Android 2020-2022 with often degraded battery, high energy sensitivity. The QR transfer requires the screen to stay on, and the flow correctly identifies this as a risk. The mitigation is appropriately non-blocking — warn but proceed.

---

## Missing Elements

### 1. The Commute Moment Is Not Served

The scenario's inciting event happens on the S-Bahn, 15 minutes before the session. Max discovers the folder is missing. He panics. He tries to reconstruct data from memory on his phone.

In the digital world, this moment transforms completely: Max opens the app and sees his data is there. The folder is not missing. But **the flow does not address the commute-time reassurance moment at all**.

FLOW-003 begins at Step 1 with "Client opens the transfer section." It assumes Max is already in the therapy room, ready to transfer. But Max's emotional arc in the scenario — Prepared → Panic → Guilt → Shame — is the exact arc the flow must interrupt. The interruption point is on the S-Bahn, not in the therapy room.

A client using the app would presumably open it on the train, see that their data is intact, and feel relief. But this moment is not modeled anywhere in the flow. There is no mention of:
- How Max confirms pre-session that his data is present and will transfer
- Whether the app provides any pre-session summary or readiness signal
- Whether Max can review his own entries on the train before the session (a natural reassurance behavior)

This gap also connects to a scenario in the Related Scenarios section that does not yet exist: "Pre-Therapy Review (Not yet created — Max reviews entries before session)." The flow's scope boundary (data transfer begins at session start) means the commute-time moment is explicitly out of scope — but this leaves a significant portion of Max's actual emotional experience unaddressed and uncovered.

**Impact on "full" coverage claim**: Scenario success criterion 4 ("Max feels prepared and competent") begins on the train, not in the therapist's office. The flow addresses this criterion only at the session level.

### 2. The "Filled But Blank" Failure Mode Is Not Addressed

The scenario documents a failure mode that is arguably more psychologically significant for Max than the forgotten folder: "Filled But Blank — Max brings the protocol but realizes he never actually filled it out (thought about it, but never wrote) → Shame of appearing unprepared."

The digital equivalent is: Max has the app on his phone, but has not entered any data during the week. He opens the transfer section and sees Exception 2.2: "No data to transfer yet." This is handled with shame-free framing — good. But the deeper issue is not handled: Max's tendency to procrastinate and then panic, which is the same whether the protocol is paper or digital.

The flow treats the no-data state as a one-time informational moment. It does not address:
- Whether the app supports mid-week entry reminders (mentioned nowhere in FLOW-003)
- Whether Max's pattern of last-minute filling (Parking Lot Syndrome) transforms into last-minute digital entry in the waiting room — which the flow implicitly supports but does not explicitly design for
- Whether "no data to transfer" in the waiting room triggers the same shame spiral as arriving with an empty paper

The flow's success metrics include "Client with missing/incomplete data does not feel shamed." But this framing assumes partial data. The zero-data case — no entries at all — may require different handling, and the scenario suggests this is a real failure mode for Max.

### 3. Cognitive Load of the Transfer Steps Themselves

Max is described as unwilling to spend more than 2-3 minutes on an entry, not interested in complex features or customization, and susceptible to cognitive paralysis from blank forms or complex UIs. The flow's happy path requires:

- Step 1: Navigate to transfer section in the nav bar/rail
- Step 2: Review the Data Scope Screen (understand entry counts, date ranges, default scope)
- Step 3: Confirm scope AND select transfer mode (two decisions)
- Step 4: Wait while animated QR code displays; understand that they need to hold the phone toward the webcam
- Step 6: Actually walk to the webcam and hold the phone steady; understand the working-distance slider if QR fails

This is a multi-step, multi-decision flow that requires active engagement. For Sophie (Structure Seeker) or Jana (who tracks extensively), this is manageable. For Max — who can barely get to his desk at home — the cognitive load of Steps 3-6 in a therapy waiting room while anxious is non-trivial.

The flow partially mitigates this by:
- Making the transfer section a prominent nav entry (Step 1 requires only one tap)
- Defaulting to the most recent therapist (no selection needed in happy path)
- Collapsing advanced controls by default

But the mode selection (Step 3: "In-Person" vs. "Remote"), the Data Scope Screen review (Step 2), and the physical choreography of Steps 4-6 (display QR, walk to webcam, hold phone steady) all add friction that the flow does not assess against Max's specific capacity constraints.

**Missing**: An explicit Adaptive UI Rule for Max-type users — "If the client has never transferred before (first time), show a one-step guided walkthrough" — or at minimum, acknowledgment that the happy path was designed for the multi-persona case and may require simplification for Max's cognitive profile.

### 4. No Acknowledgment of the Commute-Time Entry Possibility

In the scenario, Max's Act 2 is attempting reconstruction on the train. In the digital world, this transforms: Max could potentially add entries on the train (late entries for the days he missed). The flow is silent on whether this is supported, encouraged, or even possible.

This is not a gap in FLOW-003 per se (it belongs to the data capture flow), but the flow's Overview says it replaces the paper system. If Max's Parking Lot Syndrome (filling the paper in the waiting room) has a digital analog — entering data on the phone in the waiting room — the flow should acknowledge this and not inadvertently prevent it. The "no data to transfer" state (Exception 2.2) must gracefully handle the case where Max just entered data 10 minutes ago and wants to immediately transfer it.

The flow's Preconditions include "Client has at least one transferable data entry for this therapist" — this is satisfied by waiting-room entries. But whether such late entries are clearly visible in the Data Scope Screen and clearly dated (so Dr. Sarah can see they were entered 10 minutes ago, not during the week) is not addressed.

### 5. The Failure Confirmation UX (Step 8) for Max

Step 8 requires Max to make an explicit judgment: "Transfer Successful" or "Transfer Failed." This is acknowledged as Open Question 11 (client-side failure confirmation UX). But for Max specifically, this decision has a shame dimension that is not currently modeled.

If Max attempts the QR transfer and it fails (poor webcam distance, etc.), he must confirm "Transfer Failed." This creates a documented failure state. Max's primary fear is being seen as failing or not trying. Confirming "Transfer Failed" in the presence of Dr. Sarah, in the therapy room, may trigger the same shame response as announcing "I forgot the folder."

The flow's language for failure handling is careful on the system side but does not consider the interpersonal dynamics of the failure confirmation. Dr. Sarah can see what Max is tapping. The act of tapping "Transfer Failed" may itself be a shame moment.

**Missing**: A note in the emotional success metrics or exception design that the failure confirmation at Step 8 should be low-profile (not a big red "FAILED" button), and that the fallback option (client-side self-analysis on their own screen) should be framed as a positive alternative, not a consolation.

---

## Contradictions

### 1. Multi-Step Flow vs. Max's "2-3 Minutes Maximum" Anti-Trait

The flow's happy path covers 9 steps (Steps 1-9, though Step 9 is therapist-side). For Max's portion alone (Steps 1-8), this is a meaningful interaction sequence. The Success Metrics state "Transfer completes in under 60 seconds for a typical week of entries" — but this measures only the QR transmission time (Steps 4-8, the actual data transfer). The total time from Max opening the transfer section (Step 1) to confirmation (Step 8) includes:

- Navigation to transfer section
- Reading and comprehending the Data Scope Screen
- Making mode selection
- Waiting for QR to load
- Walking to the webcam and positioning the phone
- Waiting during QR transmission (up to 60 seconds)
- Confirming success/failure

For a technically confident user, this is 90-120 seconds total. For Max, with anxiety in the waiting room, poor spatial navigation under stress, and potential first-time unfamiliarity with QR transfer, this could extend to 3-4 minutes — exceeding his self-reported 2-3 minute tolerance for any task.

The anti-trait ("Unwilling to spend more than 2-3 minutes on an entry") was defined for data *entry*, not for data *transfer*. It is plausible that Max would accept a longer transfer time if the payoff (the handover moment) is emotionally rewarding. However, the flow does not explicitly reason through this distinction, and the 60-second metric covers only transmission, not the full interaction.

**This is not a hard contradiction but an unresolved tension** that deserves explicit acknowledgment.

### 2. "Advanced Scope Controls" and Max's Anti-Trait for Complexity

The flow's Data Scope Screen includes progressive disclosure for advanced scope controls: cross-therapist data opt-in, supplementary data opt-in, re-inclusion of previously skipped entries, date range narrowing. These are collapsed by default — good design. But their mere presence on the Data Scope Screen may be cognitively visible to Max.

The anti-trait is "Not interested in complex features or customization options." The progressive disclosure pattern is designed precisely to hide complexity from casual users. However, the flow does not confirm whether the advanced controls are truly invisible or merely collapsed (but labeled, suggesting "there's more here"). For a depressed client under session-start anxiety, a collapsed-but-present "Advanced Options" affordance may still register as "this is more complicated than I thought," increasing activation energy.

**Mitigation already in flow**: Progressive disclosure collapses these by default. This is the right call. **What is missing**: An explicit note that the collapsed state's visual treatment must be minimal enough to be truly ignorable by Max — not a chevron with "Advanced: Cross-therapist data, date range, 3 more options" as its collapsed label.

### 3. Battery Warning as Possible Anxiety Trigger

The Adaptive UI Rule for low battery: "Battery low — keep your phone screen on during transfer." Max has a Budget Android 2020-2022 with often degraded battery. A low battery warning during the transfer — presented in the therapy waiting room, with the session starting in minutes — adds one more failure anxiety to an already anxious moment.

The current language ("warns but proceeds") is appropriate. However, the flow does not address what happens if the battery dies during transfer. The fountain code means incomplete transfer = no usable data. If Max's phone dies at 80% of the QR sequence, the therapist has nothing, and Max has to explain why. The scenario's shame dynamic (failed handover = shame) applies here too.

**Missing**: An acknowledgment in the battery handling that the failure scenario if battery dies mid-transfer should be treated identically to Exception 4.2 (transfer abandoned), with the same non-blame framing at Step 8. File transfer as the recommended alternative when battery is very low (not just large data set) would also reduce risk.

---

## Observations on Full Coverage Claim

SCEN-002-02 is marked `coverage: full` in both the scenario's `implements_flows` YAML and in the flow's "Scenarios Served" table. The scenario's own note states: "Digital transfer flow that directly solves the physical handover failure documented in this scenario — data is accessible regardless of whether the client remembered the paper."

### Evaluating Against the Scenario's Six Success Criteria

**Criterion 1: "Max brings the filled protocol to the therapy session"**
Coverage: Full. The data is on Max's phone, which he already carries. The structural failure mode is eliminated.

**Criterion 2: "The handover happens within the first 2-3 minutes of the session"**
Coverage: Partial-to-full. The flow's 60-second transfer metric addresses this, but only for the transmission phase. The full interaction (Steps 1-8) could exceed 2-3 minutes for first-time users or technically uncertain clients. Whether this criterion is genuinely met depends on implementation details not yet resolved.

**Criterion 3: "Dr. Sarah has accurate, in-the-moment data (not reconstructed from memory)"**
Coverage: Full. Data entered during the week is transferred as entered. No reconstruction. This is the flow's strongest coverage.

**Criterion 4: "Max feels prepared and competent ('I did my homework')"**
Coverage: Partial. The emotional success metrics address how Max feels *during and after* the transfer, but the scenario's emotional arc shows that "feeling prepared" begins on the S-Bahn, not in the therapy room. The flow does not address the moment of relief when Max realizes on the train that his data is intact. A complete coverage of this criterion would require either (a) the flow explicitly addressing the pre-session check moment, or (b) a companion pre-session reassurance flow referenced here.

**Criterion 5: "Session time is spent on therapeutic analysis, not administrative recovery"**
Coverage: Full. The visualization opens immediately after transfer. No reconstruction. The flow ends with the therapist's device showing the data — the session's analytical work can begin immediately.

**Criterion 6: "The therapeutic alliance is strengthened (Max demonstrates follow-through, Dr. Sarah acknowledges effort)"**
Coverage: Partial. The flow creates a meaningful handover moment (Criterion 6a: Max demonstrates follow-through). But Dr. Sarah's acknowledgment of effort (Criterion 6b) is a human behavior that cannot be designed into a data transfer flow. What the flow *can* do — and does not currently address — is provide Dr. Sarah with visibility into how diligently Max recorded entries (total entries, date coverage, consistency of completion). This "effort visibility" data might allow Dr. Sarah to spontaneously acknowledge effort without being prompted. The visualization at Step 9 provides *data* but whether it surfaces effort-relevant information (e.g., "Max made entries on 5 of 7 days this week") is not specified.

### Verdict on "Full" Coverage Claim

The "full" designation is reasonable as a statement about FLOW-003's *scope* — the flow fully addresses the data handover moment, and within that moment, covers Max's needs comprehensively. It is not appropriate as a statement that FLOW-003 *fully satisfies the scenario's complete emotional and functional arc*.

Three of the six success criteria are fully covered. Two are partially covered (Criteria 4 and 6). One has a conditional caveat (Criterion 2, pending implementation). A more precise framing would be: `coverage: full` for the `analysis.transfer_to_therapist` category stage; `partial` for the full scenario including its emotional preconditions and interpersonal outcome.

**Recommendation**: Retain `coverage: full` if the definition is understood as coverage of the transfer *stage* of the scenario. Add a note clarifying that criteria 4 and 6 are partially served by this flow and require either a companion pre-session flow or explicit design work in the visualization's effort-visibility features.

---

## Recommendations

### Recommendation 1: Add a "Pre-Session Check" Adaptive UI State (High Priority)

The scenario's most emotionally significant moment — Max's relief (or continued anxiety) on the S-Bahn — is currently unaddressed. The app should provide a home-screen state or a low-effort entry point that gives Max a session-day signal: "You have N entries ready for Dr. Sarah." This does not need to be in FLOW-003 itself, but FLOW-003 should reference it as a precondition-adjacent