# Opus Plan: FLOW-003 Iteration 1 — Incorporate User Feedback

## Objective

Apply all feedback from `user_feedback/2026-03-20_feedback.md` to FLOW-003 `flow.md`. This is the first feedback iteration on the draft flow. The feedback touches the entire Happy Path (Steps 1–9) and requests a simplification of Exception 2.1 (pairing). The user explicitly stopped feedback at that point, expecting cascading changes to make further feedback premature.

---

## Analysis Summary

### Feedback Classification

| Area | Change Type | Impact |
|------|-------------|--------|
| Step 1 (Home screen indicator) | Remove UX detail, correct entry point | Minor wording |
| Step 3 (Scope selection) | Add progressive disclosure note + bundle concept | Moderate — new capability |
| Steps 4–7 (Transfer mechanism) | **MAJOR** — replace proximity-based with animated QR primary | Structural rewrite of Phase 1 transfer |
| Step 5 (Therapist receives) | **MAJOR** — therapist uses webcam on laptop/desktop, new physical-interaction step | New step + restructure |
| Step 8 (Confirmation screen) | Remove confirmation screen; direct to visualization | Simplification |
| Step 9 (Visualization) | Remove tap-to-open; add note about layout flexibility | Minor |
| Exception 2.1 (Pairing) | Simplify to reference FLOW-002 + epic requirements | Simplification |

### Key Design Decisions to Embed

**Decision 1: Bundle creation is a pre-session preparation, not a session-start action.**

The user described clients wanting to "create a bundle" before the session — potentially including data not from the therapist-assigned protocol. This contradicts the current privacy boundary, which structurally excludes non-therapy data.

**Recommendation**: Model this as a **new precondition variant + an addition to Step 2–3**:
- In Preconditions, add: "Client may have prepared a transfer bundle in advance (see Adaptive UI Rules)"
- In Step 2 (Data Scope Screen), add: if a pre-prepared bundle exists, that bundle is the default scope instead of "all unshared since last transfer"
- In Adaptive UI Rules, add a rule for pre-prepared bundles
- **Critical change to Privacy Boundary**: The feedback says bundles "can include information that is not part of the questionnaire plan that the therapist assigned." This means the privacy boundary must be softened from "structurally excluded" to "excluded by default, but the client can explicitly opt-in to include additional data." The structural exclusion remains for private diary entries and data from OTHER therapists' protocols — but self-tracking templates and personal notes CAN be voluntarily included by the client. This is a meaningful design decision that must be clearly documented.

**Decision 2: Discard option — where does it live?**

The user first described a confirmation screen, then reversed: "I do NOT want to show this confirmation screen." The visualization opens directly. However, the therapist needs the ability to discard received data (with a verification prompt).

**Recommendation**: Place the discard option **inside the Client Data View (visualization screen)** as a secondary action (e.g., overflow menu or a small "discard session data" option).

Persona justification:
- **Dr. Sarah** (efficient, time-conscious): Would be irritated by any extra screen between transfer and visualization. She wants to immediately see the data and start pattern-scanning. A discard buried in the overflow menu is fine — she'd almost never need it.
- **Prof. Dr. Weber** (deliberate, narrative-focused): Might want to re-read previous session notes before seeing new data. But the visualization screen can accommodate this — he scrolls or navigates within the view. A separate confirmation screen would break his flow too.
- **Dr. Turan** (safety-first, medication-focused): Most likely to need discard — if the wrong client's data was transferred somehow, or if data arrived corrupted. But even Dr. Turan needs this rarely. A prominent but non-blocking option in the view is correct.

The verification prompt on discard is essential (user's own point: "both will be really annoyed if they have to do it again"). Model this as: Discard triggers a confirmation dialog: "Discard received data from [Client Name]? This transfer took [duration]. You would need to transfer again."

**Decision 3: Transfer mechanism structure (Steps 4–7)**

The current flow has a generic "proximity transfer" concept. The feedback specifies animated QR codes as primary, with file transfer and remote session as alternatives.

FLOW-002 already established the QR/file/remote pattern (Exception 1.3), but from the therapist-to-client direction. FLOW-003 is client-to-therapist, which involves:
- **Animated QR**: client phone displays → therapist webcam reads (laptop/desktop). This is the reverse of FLOW-002 where the therapist displayed and the client scanned.
- **File transfer**: encrypted file via email (fallback for large data or no visual channel)
- **Remote session**: video call variant

**New step structure for Phase 1:**
1. Step 1: Client arrives / opens app (simplified — no home screen indicator)
2. Step 2: Client navigates to transfer section → Data Scope Screen
3. Step 3: Client reviews/confirms scope (progressive disclosure for narrowing)
4. Step 4: Client taps "Transfer" → app shows animated QR code + estimated duration. If >2 min, app suggests file transfer. Options visible: switch to file transfer, mark as remote session.
5. Step 5: **NEW** — Client holds phone screen toward therapist's webcam. Therapist's app (on laptop/desktop) detects and reads animated QR via webcam. Client-side has "increase working distance" option (reduces QR density).
6. Step 6: Transfer in progress (both devices show progress)
7. Step 7: Transfer complete — client sees confirmation, entries marked "shared"

Phase 2:
8. Step 8: Therapist device: transfer completes → data stored locally in client's data space → visualization opens **automatically** (no confirmation screen, no tap)
9. Step 9: **Merged into Step 8** — the visualization opening IS the completion. No separate step needed.

Actually, re-examining: the user's correction merges Steps 8 and 9. In the revised flow, after transfer completes on the therapist side, the visualization simply opens. This means:
- Old Step 8 (receipt confirmation) + Old Step 9 (tap to open) → New Step 8: Transfer completes, visualization opens automatically.

This simplifies Phase 2 to a single step. Total happy path: 8 steps (was 9).

**Decision 4: Upstream scenario notification**

The scenarios in `serves_scenarios` describe the **status quo** (paper-based handover pain). They do not describe app behavior. Changes to the flow's transfer mechanism (from generic proximity to QR codes) do not invalidate the scenario problem descriptions.

**Recommendation**: Do NOT update scenario review_status. The scenarios remain valid — they describe the pain that this flow addresses, regardless of whether the flow uses QR codes, Bluetooth, or carrier pigeons. The flow changing its solution approach does not change the problem.

However: if the flow changes its *coverage* (e.g., now covering less of the scenario's success criteria, or adding new capabilities that expand coverage), then scenarios should be notified. In this case, the coverage is equivalent or better (QR is a concrete mechanism vs. the previous abstract "proximity transfer"), so no notification needed.

**Present this recommendation to the user for confirmation.**

**Decision 5: Version field**

The README_7_META_INFO_STANDARDS shows `version` is not part of the standard user flow YAML. Flows use `updated` + `review_history` for version tracking. Do NOT add a version field — use the `updated` date and review_history entry instead.

---

## Execution Plan

### Single Agent: Implementation (Sonnet)

The changes are to a single file with clear, enumerated modifications. One agent is sufficient.

#### Step 1: Update YAML Frontmatter

**Changes to `flow.md` YAML**:
```yaml
updated: 2026-03-20   # was 2026-03-03
review_status: in_review   # was draft (content change triggers this)
review_history:
  - ... (keep existing entry)
  - date: 2026-03-20
    from: draft
    to: in_review
    reviewer: LLM
    notes: "First iteration incorporating user feedback (2026-03-20_feedback.md). Major changes: (1) Transfer mechanism changed from abstract proximity to animated QR codes as primary channel with file transfer and remote session as alternatives. (2) Therapist receives via webcam on laptop/desktop, not mobile device. (3) Removed confirmation screen — visualization opens directly after transfer. (4) Added progressive disclosure for data scope selection. (5) Added pre-session bundle creation concept with opt-in data inclusion beyond therapy protocols. (6) Exception 2.1 (pairing) simplified to reference FLOW-002. (7) Working-distance adjustment mechanism added for QR display. Agent: claude-sonnet-4-6"
```

#### Step 2: Rewrite Overview Section

Replace the current Overview with updated description reflecting:
- Animated QR codes as primary transfer mechanism (not generic "proximity-based")
- File transfer as alternative channel
- Therapist uses laptop/desktop with webcam (not mobile device)
- Unidirectional remains correct

Keep the "Why this approach" paragraph largely intact — the problem description (paper-based handover failures) hasn't changed. Update only the solution description to mention QR codes specifically.

Add to the "Why one flow for all therapist types" paragraph: note that the visualization details are not specified in this flow (may depend on protocol type, therapist configuration, or protocol-embedded layout).

#### Step 3: Update Preconditions

**Client device section** — add:
- "Client may have prepared a transfer bundle before the session (optional — see Step 2 and Adaptive UI Rules)"

**Therapist device section** — change:
- Replace "app open and in 'receive' mode" with "app open on laptop/desktop computer with webcam active (or ready to activate)"
- Add: "Therapist's device has a functioning camera (webcam) for QR code scanning — OR therapist and client agree on file transfer as alternative"

**Privacy boundary section** — modify point 3:
- Current: "The client may further narrow the scope ... but cannot widen it beyond the therapy-protocol boundary"
- New: "The client may further narrow the scope (exclude specific entries or date ranges). Additionally, the client may opt to include supplementary data beyond the assigned therapy protocols — such as self-tracking entries or personal notes they consider relevant for the session. This opt-in inclusion is an explicit, per-transfer decision; it does not change the default scope. Data from OTHER therapists' protocols remains structurally excluded."

#### Step 4: Rewrite Happy Path Phase 1 (Steps 1–7)

**Step 1 (Client)** — Rewrite:
```
| 1 | **Client** | Opens the app and navigates to the transfer section (accessible via the app's main navigation; label TBD) | App opens to its default screen (data entry). Client navigates to the transfer section. If client has unshared therapy protocol data for this therapist: the transfer section shows the Data Scope Screen. | Transfer section — Data Scope Screen | TBD |
```
Key changes: no "session-start indicator" on home screen, explicit navigation action, app starts on data entry screen.

**Step 2 (Client)** — Rewrite:
```
| 2 | **Client** | Reviews the Data Scope Screen: a summary of data ready to transfer — which protocol(s), date range, number of entries. Default scope: all unshared entries from this therapist's protocols since the last transfer. If a pre-prepared bundle exists (see Adaptive UI Rules), that bundle is the default instead. Private diary entries are excluded by default but supplementary self-tracking data can be opted-in. | App displays the scope summary. Advanced scope controls (narrowing, opt-in of additional data) are available via progressive disclosure — collapsed by default, expandable on demand. Most users confirm the default without expanding. | Data Scope Screen | TBD |
```
Key changes: progressive disclosure, bundle reference, opt-in language.

**Step 3 (Client)** — Rewrite:
```
| 3 | **Client** | Confirms the scope (most users: one tap to confirm the default). Or expands advanced options to narrow the date range, exclude specific entries, or include supplementary self-tracking data. | App records the confirmed scope. | Data Scope Screen (confirmed) | TBD |
```
Key changes: simplified, progressive disclosure principle explicit.

**Step 4 (Client)** — Rewrite:
```
| 4 | **Client** | Taps "Transfer" (or equivalent send action) | App displays an animated QR code encoding the transfer data. Below the QR code: estimated transfer duration (e.g., "≈ 45 seconds via QR"). If estimated duration exceeds 2 minutes, app suggests: "Large data set — consider using file transfer instead." Two alternative options are always visible: (a) "Switch to file transfer" (generates an encrypted file for sharing via email or system share sheet; details TBD), (b) "Remote session" (for video call scenarios — adjusts QR display for screen sharing, or switches to file transfer if no visual channel). | QR Transfer Screen (Client) — animated QR code displayed | TBD |
```

**Step 5 (Client + Therapist)** — **New step** (physical interaction):
```
| 5 | **Client → Therapist** | Client holds phone screen toward the therapist's webcam (laptop/desktop). Comfortable distance: approximately 20 cm. If the webcam cannot read the QR at this distance, the client taps "Increase working distance" on the QR Transfer Screen — the app reduces QR density (fewer modules, lower error correction) to make the code readable at greater distances or with lower-resolution cameras. | Therapist's app (on laptop/desktop) detects the animated QR code via webcam and begins reading frames. Both devices show transfer progress. The connection is local (camera-to-screen) and does not require internet. | QR Transfer Screen (Client) ↔ QR Receive Screen (Therapist) | TBD |
```

**Step 6 (Both)** — Transfer in progress:
```
| 6 | **Both** | Transfer in progress. Client holds phone steady. Therapist's app reads successive QR frames. | Both devices show transfer progress — client sees frames sent / total, therapist sees frames received / total. Transfer duration is proportional to data volume and QR density setting. | Transfer In Progress (both devices) | TBD |
```

**Step 7 (Client)** — Transfer complete (client side):
```
| 7 | **Client** | Transfer completes on client side | Client app shows: "Transfer complete. [N entries] shared with [Therapist Name]." Entries are marked as "shared" on the client device (they remain on the client device; only a copy is transferred). Client can put away phone. | Transfer Complete Screen (Client) | TBD |
```

#### Step 5: Rewrite Happy Path Phase 2 (Step 8 — was Steps 8–9)

**Step 8 (Therapist)** — Merged receipt + visualization:
```
| 8 | **Therapist** | Transfer completes on therapist's device | Data is stored locally in the client's dedicated data space (isolated from other clients' data). The app immediately opens the Client Data View: a visualization appropriate to the protocol type. The view adapts to the protocol structure — but the specific layout details are not defined in this flow; they may depend on protocol type, therapist configuration, or layout embedded in the protocol definition itself. | **Client Data View** — Flow ends here | TBD |
```

Add below the table:

**Flow end state**: The therapist's device is displaying the transferred data in a visual representation. Both therapist and client can see the screen. The session's collaborative analysis phase begins — which is outside the scope of this flow. The therapist can discard the received session data from within the Client Data View (via a secondary action such as an overflow menu); discarding triggers a confirmation dialog due to the time cost of re-transferring.

#### Step 6: Update Unhappy Paths

**Exception 2.1 (First-time pairing)** — Simplify to reference:
```
**Exception 2.1**: First-time pairing — client and therapist have not connected via the app before
- **Detection**: At Step 4, app detects no existing pairing between this client and this therapist
- **User impact**: Client cannot initiate data transfer — devices need to establish trust first
- **Recovery**: The pairing process is defined in [FLOW-002 "Instruct Client on Protocol"](../instruct_client_on_protocol/flow.md) (Steps 4–5 and Exception 1.1). In most cases, pairing happens during the first protocol delivery session. If the client arrives at FLOW-003 without a prior pairing, the app initiates the same pairing process before resuming at Step 4.
- **Note**: This exception also covers clients switching therapists. Each therapist pairing is independent — see FLOW-002 Exception 1.1A.
- **Related**: [FLOW-002](../instruct_client_on_protocol/flow.md), [REQ-FUNC-007](../../requirements_tasks/functional/shared/epic_data_transfer/requirements.md)
```

**Exception 4.1 (Therapist device not detected)** — Needs rewrite to match QR mechanism:
```
**Exception 4.1**: QR code not detected — therapist's webcam cannot read the animated QR code
- **Detection**: At Step 5, after a timeout (e.g., 15 seconds of no successful frame reads), the app shows a troubleshooting prompt
- **User impact**: Transfer cannot proceed via QR
- **Recovery**: App shows guidance on the CLIENT's screen: "Having trouble? Try: (1) Move your phone closer to the webcam, (2) Tap 'Increase working distance' to simplify the QR code, (3) Ensure the webcam is not blocked or covered." If repeated failure: app offers "Switch to file transfer" as fallback. The file transfer option is always available regardless of QR success.
- **Related epic/feature**: TBD
```

**Exception 4.2 (Transfer interrupted)** — Minor update to reflect QR:
```
**Exception 4.2**: Transfer interrupted mid-transfer (client moves phone away, app backgrounded, phone locked)
- **Detection**: During Step 5–6, the QR reading stream stops before all frames are received
- **User impact**: Partial data received on therapist device
- **Recovery**: App resumes automatically when client repositions phone and QR frames are detected again. If the interruption is too long (>30 seconds of no frames): therapist's app shows count of frames/entries received so far and offers (A) "Wait for client to resume" or (B) "Accept partial transfer" or (C) "Restart transfer." Data already received is preserved — no duplicate entries on resume.
- **Related epic/feature**: TBD
```

**New Exception 4.3**: File transfer path (not an error, but an alternative flow):
```
**Exception 4.3**: Client selects file transfer instead of QR
- **Detection**: At Step 4, client taps "Switch to file transfer" (manually or after app suggests it for large transfers)
- **User impact**: Transfer channel changes from visual QR to encrypted file
- **Flow**: App generates an encrypted file containing the confirmed data scope. Client shares the file via the system share sheet (email, messaging app, or other channel). Therapist receives the file on their device and imports it into the app. After import, the flow resumes at Step 8 (visualization opens).
- **Note**: File transfer does not require physical co-presence. It is the default for remote sessions where video quality is insufficient for animated QR, and for transfers where data volume makes QR impractical (>2 minutes estimated). Details of the encrypted file format and import process are TBD.
- **Related epic/feature**: TBD
```

**New Exception 4.4**: Remote session — video call variant:
```
**Exception 4.4**: Remote session — therapist and client are in a video call
- **Detection**: At Step 4, client taps "Remote session"
- **User impact**: Physical QR scanning is not possible. Transfer must use an alternative channel.
- **Flow**: App offers two options: (A) If the video call supports screen sharing: client can share their screen showing the animated QR code, and the therapist's app reads it via webcam pointed at the therapist's own screen — but this is typically unreliable due to video compression and frame rate loss. (B) File transfer (recommended for remote sessions): same as Exception 4.3. The app defaults to suggesting file transfer for remote sessions.
- **Note**: The detailed remote transfer flow follows the same patterns established in [FLOW-002 Exception 1.3](../instruct_client_on_protocol/flow.md) but in the reverse direction (client-to-therapist). FLOW-002's guidance on video QR reliability applies here.
- **Related epic/feature**: TBD
```

#### Step 7: Update Adaptive UI Rules

Add new rules, modify existing ones:

**New rule — Pre-prepared bundle**:
```
**If the client has prepared a transfer bundle before the session**:
- Data Scope Screen shows the bundle contents as default scope instead of "all unshared since last transfer"
- Bundle name (if any) displayed at the top
- Client can still modify the bundle scope before confirming
```

**New rule — Large data set / duration estimate**:
```
**If the estimated QR transfer duration exceeds 2 minutes**:
- App prominently suggests: "This is a large data set. File transfer recommended."
- The suggestion is non-blocking — client can proceed with QR if they prefer
- The estimated duration is always visible on the QR Transfer Screen regardless of length
```

**Modify existing rule** ("client has no unshared data"): Keep as-is — still relevant.

**Modify existing rule** ("very large volume"): Merge with the new duration rule above. Remove the standalone "very large volume" rule to avoid duplication.

**Modify existing rule** ("low battery during transfer"): Keep, but update wording from "proximity connection" to "QR display" (client phone screen must stay on during QR transfer).

**Modify existing rule** ("first session with data from this client"): Keep as-is — therapist-side orientation, unaffected by mechanism change.

**Modify existing rule** ("protocol type"): Keep, but add the note that visualization layout details are not specified in this flow (per user feedback).

#### Step 8: Update Privacy Boundary Section

The "Privacy Boundary: Structural Enforcement" section needs updating to reflect the opt-in inclusion of supplementary data.

**Point 1**: Keep "Not a toggle" language but soften: The structural separation between therapy protocol data and private data remains. However, clients can explicitly opt-in to include specific self-tracking entries in a transfer (see Step 2–3, progressive disclosure).

**Point 3**: Change from "Exception 3.2 narrows, never widens" to: "Exception 3.2 narrows by default. The client can also choose to include supplementary self-tracking data not assigned by this therapist — but this requires explicit opt-in via the advanced scope controls (progressive disclosure). Private diary entries remain excluded. Data from other therapists' protocols remains structurally excluded."

#### Step 9: Update Screens/Components Section

Update to reflect new screens:
- Remove "Transfer Waiting Screen" (no longer exists — replaced by QR Transfer Screen)
- Add "QR Transfer Screen (client)": displays animated QR code, estimated duration, working-distance control, alternative channel options
- Add "QR Receive Screen (therapist)": webcam-based QR reader, frame progress
- Remove "Receive Ready Screen (therapist)": no longer a separate screen — therapist's app goes directly from QR reading to transfer progress
- Update "Client Data View": add note that visualization opens automatically, discard option accessible as secondary action

#### Step 10: Update Domain Concepts

**Proximity transfer** → rename/rewrite:
```
**Data transfer (animated QR)**: The primary transfer channel. The client's phone displays an animated sequence of QR codes encoding the transfer data. The therapist's laptop/desktop reads the sequence via webcam. Transfer speed depends on QR density, camera resolution, and distance. No internet required — the data travels optically from screen to camera.
```

Add:
```
**File transfer (alternative)**: An encrypted file containing the transfer data, shared via the system share sheet (email, messaging, or other channel). Used when QR transfer is impractical (large data volume, remote sessions, no visual channel). Details of the encryption and file format are TBD.
```

Add:
```
**Working distance**: The physical distance between the client's phone screen and the therapist's webcam during QR transfer. The app provides a client-side control to reduce QR density (fewer modules per code), making codes readable at greater distances or with lower-quality cameras — at the cost of longer transfer duration.
```

Add:
```
**Transfer bundle**: A pre-prepared collection of data the client assembles before the session. May include therapy protocol entries (default scope) plus optional supplementary data the client wishes to share. Bundles allow the client to take time with scope decisions at home rather than during the session.
```

#### Step 11: Update Gaps Section

Update Gap 1 ("Proximity Transfer Protocol") to reflect QR:
```
1. **Animated QR Transfer Protocol**: The core transfer mechanism (Steps 4–7) — animated QR encoding, webcam-based reading, frame progress tracking, working-distance adaptation, resumable transfer on interruption. This is the central technical challenge of the flow.
```

Add new gap:
```
5. **File Transfer Protocol**: The fallback transfer channel (Exception 4.3) — encrypted file generation, system share sheet integration, import process on therapist device. Details TBD but must integrate with the same Data Scope selection as QR transfer.
```

Add new gap:
```
6. **Transfer Bundle Preparation**: Client-side feature for pre-session bundle assembly (referenced in Preconditions and Adaptive UI Rules). Includes: browsing entries, selecting/deselecting items, opt-in of supplementary data, saving the bundle for later transfer.
```

#### Step 12: Update Edge Cases Summary / Open Questions

Update "Local transfer issues" subsection to reflect QR-specific issues.

Add to Open Questions:
```
6. **Bundle creation scope**: Can a bundle include supplementary data that the client has never shared with any therapist? If so, the Data Scope Screen must support browsing personal entries that are outside the therapy protocol structure. This has UX implications — the client needs to navigate two data structures (therapy protocols and personal tracking). **Proposed**: Start simple — bundles only include therapy protocol entries in v1. Supplementary data opt-in deferred to v2. **Deferred to**: Transfer Bundle Preparation gap.
```

#### Step 13: Update Implementing Epics/Features Table

Add file transfer and bundle gaps to the table. Update references from "Proximity Transfer Protocol" to "Animated QR Transfer Protocol."

#### Step 14: Update Value Trade-offs

No changes needed — the trade-offs (Efficiency vs. Depth, Clinical Safety vs. Client Data Control) are about what happens WITH the data, not how it arrives. The transfer mechanism change doesn't affect these.

However, the bundle/supplementary data opt-in creates a minor tension with Trade-off 2 (Client Data Control vs. Clinical Safety): clients can now include MORE data, which is good for Dr. Turan's safety needs — but the opt-in is still client-controlled. Add a brief note to Trade-off 2's mitigation.

---

## Downstream Impact Assessment

### Scenario Review Status

**Recommendation: Do NOT update upstream scenario review_status.**

Reasoning:
1. All 6 scenarios describe status quo (paper-based workflows) — they are problem descriptions, not solution descriptions
2. The flow change is about HOW the solution works (QR vs. proximity), not WHETHER the solution addresses the scenario pain
3. Coverage (primary/full for clients, primary/partial for therapists) remains identical
4. Changing scenario review_status would create unnecessary review churn for 6 documents that haven't changed in meaning

**Present this to user for confirmation.**

### FLOW_INDEX.md

No update needed — FLOW-003's purpose, name, and status category ("Existing Flows") haven't changed. The `implementation_status` remains `not_started`.

---

## Quality Criteria

- [ ] All 11 feedback points from `2026-03-20_feedback.md` are addressed
- [ ] Animated QR is the primary transfer mechanism in happy path
- [ ] File transfer and remote session are documented as alternatives
- [ ] No confirmation screen between transfer and visualization (Step 8)
- [ ] Discard option documented as secondary action in Client Data View
- [ ] Exception 2.1 references FLOW-002 instead of re-describing pairing
- [ ] Progressive disclosure mentioned for scope selection
- [ ] Bundle concept introduced with clear boundaries
- [ ] Privacy boundary section updated for supplementary data opt-in
- [ ] Working-distance mechanism documented
- [ ] Estimated transfer duration shown to client
- [ ] Therapist uses laptop/desktop with webcam (not mobile)
- [ ] review_status updated to in_review
- [ ] review_history entry added for 2026-03-20
- [ ] Technology-neutral language maintained (QR codes are interaction modality, not implementation tech — per FLOW-002 precedent)
- [ ] FLOW-002 consistency: remote session handling aligns with FLOW-002 Exception 1.3

## Risks

- **Risk 1: Bundle/supplementary data may be premature.** The user mentioned it casually. If the scope is unclear, it could bloat the flow. Mitigation: Introduce the concept briefly, add an open question deferring detailed design, and keep the happy path focused on therapy protocol data only.
- **Risk 2: Privacy boundary softening may concern the user.** The original flow was emphatic about structural exclusion. Allowing opt-in inclusion changes the model. Mitigation: Frame as "client-controlled widening" — the default remains exclusive; opt-in requires explicit action via progressive disclosure. Document clearly.
- **Risk 3: Therapist device assumption (laptop/desktop) may not cover all cases.** Some therapists might use tablets. Mitigation: The flow describes the primary setup; tablet with camera would work similarly. The "webcam" concept generalizes to "device camera."
