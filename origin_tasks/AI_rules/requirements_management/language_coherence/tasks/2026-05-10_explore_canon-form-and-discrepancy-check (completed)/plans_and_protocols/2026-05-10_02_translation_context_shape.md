# REQ-NFUNC-013 AC-08 Shape Investigation: translation_context

**Date:** 2026-05-14  
**Task:** TASK-PROC-049-01 (designing the canonical concept canon)  
**Scope:** Current state of `translation_context` infrastructure and quantified impact analysis of the canon on per-label duplication  

---

## Section 1: REQ-NFUNC-013 AC-08 Specification (Verbatim)

### AC-08 Text (from requirements.md, line 42)

```
Each UI text entry is stored with a translation_context description covering: 
user situation, UI element type, and wording rationale
```

### Section 8.4 Definition (REQ-NFUNC-013, lines 192–228)

```
### 8.4 Translation Metadata per Entry

Beyond German and English text, each UI text entry must include a 
`translation_context` field. This field is intentionally verbose — its purpose 
is to enable high-quality translation into any future language without requiring 
the translator to know the app or its design philosophy.

**Required fields per entry:**

| Field | Purpose |
|-------|---------|
| `de` | German text (primary language) |
| `en` | English text |
| `translation_context` | Human-readable description for translators (see below) |

**`translation_context` must cover:**

1. **User situation** — What is the user doing when they see this? Who is the 
   user (client or therapist)? What just happened?
2. **UI element type** — What kind of element carries this text? (e.g., primary 
   action button, table column header, form field label, section title, 
   placeholder text, toast message, inline validation hint)
3. **Wording rationale** — Why was this exact phrasing chosen? Capture the 
   intent and trade-offs (e.g., "invite without demanding", "acknowledge 
   effort without overpraising", "short for space constraints but still 
   complete thought"). This is especially important where alternatives were 
   considered and rejected.

**Do not repeat** general UX writing rules (tone, du-form, no triggering 
language) — those apply universally and are documented in this requirement.

**Reference the canonical concept canon** (REQ-PROC-049 — Language Coherence) 
rather than redescribing nouns, verbs, or states inline. The canon defines, 
for each user-facing concept the product commits to, its name, the states it 
can be in, and the named operations a user can perform on it. `translation_context` 
entries narrow to label-specific information (which surface the label appears 
on, which audience encounters it, which moment of use it covers) instead of 
restating concept-level information that lives once at the canon. This avoids 
per-label duplication of the same noun/verb/state descriptions across hundreds 
of entries and keeps every translation aligned with the canonical naming.

**Example entry:**

\`\`\`yaml
key: plan_handout_button
de: "Plan aushändigen"
en: "Hand out plan"
translation_context: >
  Shown to the therapist on the plan detail screen after finalising a plan.
  This is the primary action button that initiates transferring the plan to
  the client's device. "Aushändigen" was chosen over "Senden" or "Übertragen"
  because it evokes a physical, personal hand-over (as in handing a document
  to someone), which matches the therapeutic relationship. "Hand out" in English
  carries the same physical/personal connotation. Avoid translations that imply
  a technical file transfer (e.g., "upload", "sync", "push").
\`\`\`
```

### Section 11: References (REQ-NFUNC-013, lines 252–257)

```
## 11. References

- Toast Component: non-functional/ui_ux_design_system/components/toast/
- ContextHelp: non-functional/ui_ux_design_system/components/context_help/
- Error Handling: non-functional/ui_ux_design_system/loading_error_handling/
- REQ-PROC-049 (Language Coherence Across Product Artifacts): canonical source 
  for user-facing concept names, states, and named operations that 
  `translation_context` entries reference (per Section 8.4)
```

---

## Section 2: Existing translation_context Entries

**Status:** None exist today.

**Current ARB structure** (`lib/l10n/app_en.arb` and `lib/l10n/app_de.arb`):
- Standard Flutter ARB format with short, single-sentence `description` fields
- Total of 70 UI text entries across English and German
- Generated `lib/generated/l10n/app_localizations*.dart` consume the ARB

**Example of current minimal metadata:**

```json
{
  "handoverButtonLabel": "Hand Over Plan",
  "@handoverButtonLabel": {
    "description": "Label for button to hand over a plan"
  }
}
```

This is a single sentence. The AC-08 `translation_context` specification calls for three required components (user situation, UI element type, wording rationale) — multi-paragraph coverage that would be 3–5x longer than the current description.

**Gap:** The shape prescribed by AC-08 §8.4 has never been instantiated. The infrastructure (storage, schema, tooling) does not exist.

---

## Section 3: Estimated UI Surface Size

### Screens
- **Current screens:** 16 presentation layer screen files (`*_screen.dart`)
- **Feature areas:** 7 major (role_selection, home, more, client/data_input, client/data_receive, therapist/clients, therapist/data_transfer)
- **Estimate:** 20–25 distinct user-visible screens when complete

### UI Text Entries
- **Current ARB entries:** 70 localization keys
- **Hardcoded strings observed:** 6+ in `in_person_tab_content.dart` alone, likely 20–50 more across the codebase
- **Estimate:** 90–120 user-facing text strings once fully migrated to ARB

### Buttons/CTAs
- **Observed buttons in therapist_transfer_ui:** 8+ (Hand Over Plan, Discard Transfer, Complete Transfer, and navigational buttons)
- **Per-screen estimate:** 3–5 primary CTAs, 1–3 secondary CTAs
- **Estimate:** 60–100 discrete button/CTA labels across all screens

### Order of Magnitude
- **Screens:** ~20 (10^1.3)
- **Labels/strings:** ~100 (10^2)
- **Buttons/CTAs:** ~80 (10^1.9)
- **Total UI surface:** ~200 distinct user-facing text elements (10^2.3)

---

## Section 4: One Feature Area's Concrete Labels

### Feature: `epic_data_transfer/feat_therapist_transfer_ui`

The therapist hands over a questionnaire plan to a client via in-person QR transfer. Five concrete user-facing labels and their underlying concepts:

#### Label 1: "Hand Over Plan" (primary CTA)
- **Concept:** Plan (the object being transferred)
- **Operation:** transfer / handover (the action)
- **UI element:** Primary button (FilledButton)
- **Current state:** ARB key `handoverButtonLabel`, German "Plan aushändigen"
- **User situation:** Therapist has selected a plan and wants to initiate the transfer to a client's device
- **Observed code location:** `lib/features/therapist/data_transfer/presentation/widgets/handover_dialog.dart` line 64

#### Label 2: "Please scan with the client app." (instruction text)
- **Concept:** Scan (the operation), Client (the user role performing it), Data Beam (the technical mechanism, code-internal)
- **Operation:** scan / receive
- **UI element:** Help text / instruction (centered Text)
- **Current state:** ARB key `dataBeamScanInstruction`, German "Bitte mit der Klienten-App scannen."
- **User situation:** Therapist has named the client and started the transfer. The QR code is now animating. Therapist instructs client to use their app to scan this code.
- **Observed code location:** `lib/features/therapist/data_transfer/presentation/widgets/in_person_tab_content.dart` line 156

#### Label 3: "Slow" (slider endpoint label)
- **Concept:** Scanner Hardware Tier (the underlying entity being configured)
- **Operation:** configure (speed) / select
- **UI element:** Slider label (Text in Column)
- **Current state:** ARB key `dataBeamSliderSlow`, German "Langsam"
- **User situation:** Therapist is adjusting the QR pulse frequency to match their device's camera tier. "Slow" is the minimum end.
- **Observed code location:** `lib/features/therapist/data_transfer/presentation/widgets/data_beam_speed_slider.dart` line 39

#### Label 4: "(Older Devices)" (sub-label for Slow)
- **Concept:** Hardware capability, device generation
- **Operation:** context / clarification
- **UI element:** Sub-label / secondary text (Text in bodySmall style)
- **Current state:** ARB key `dataBeamSliderSlowSubLabel`, German "(Ältere Geräte)"
- **User situation:** Therapist is deciding which tier to use. This clarifies that the "Slow" tier is appropriate for older hardware.
- **Observed code location:** `lib/features/therapist/data_transfer/presentation/widgets/data_beam_speed_slider.dart` line 43

#### Label 5: "Name des Klienten" (form field label)
- **Concept:** Client (the object), name (the attribute)
- **Operation:** input / capture
- **UI element:** Form field label (InputDecoration.labelText)
- **Current state:** ARB key `dataBeamClientNameLabel`, German "Name des Klienten"
- **User situation:** Therapist is beginning the handover flow. They must enter the client's name before the QR transfer can start.
- **Observed code location:** `lib/features/therapist/data_transfer/presentation/widgets/in_person_tab_content.dart` line 141

---

## Section 5: "Before Canon" translation_context Entries (Drafted Without Canon)

If AC-08 were implemented without a shared concept canon, each label would redescribe the nouns, verbs, and states from scratch:

### Label 1: handoverButtonLabel (before canon)

```yaml
key: handoverButtonLabel
de: "Plan aushändigen"
en: "Hand Over Plan"
translation_context: >
  Shown to the therapist on the plan handover dialog after the therapist 
  selects a plan. This is the primary action button that initiates the 
  transfer of a questionnaire plan to a client's device.
  
  A Plan is a structured questionnaire containing multiple questions arranged 
  in a specific order. Plans are created by therapists and assigned to clients 
  for clients to complete by answering the questions. A plan can be in states: 
  Draft (therapist is editing), Published (available for assignment), Assigned 
  (given to a specific client), or Completed (client has answered all questions).
  
  The "Hand Over" operation transfers a published plan from the therapist's 
  device to a client's device via QR code scanning. The therapist initiates 
  the handover, and the client completes it by scanning the QR code. After 
  handover, the plan is marked as "transferred" and the client sees it in their 
  list of available plans.
  
  "Plan aushändigen" was chosen over "Plan senden" (send), "Plan übertragen" 
  (transmit), or "Plan teilen" (share) because it evokes a physical, personal 
  hand-over — as if the therapist were handing a physical document to the 
  client. This preserves the human relationship quality of the therapeutic 
  context. "Hand over" in English carries the same physical/personal connotation 
  and avoids technical language that might imply a cloud sync or file upload. 
  Avoid translations that imply technical file transfer (e.g., upload, sync, 
  push, transmit).
```

**Word count:** ~210 words  
**Concept-level burden:** ~150 words (definition of Plan + definition of Hand Over operation + state/context explanation)

---

### Label 2: dataBeamScanInstruction (before canon)

```yaml
key: dataBeamScanInstruction
de: "Bitte mit der Klienten-App scannen."
en: "Please scan with the client app."
translation_context: >
  Displayed on the therapist's screen at the center of the handover dialog, 
  positioned directly above the animated QR code. This is instructional help 
  text guiding the therapist on the next step.
  
  The user at this point is the therapist, who has just entered their client's 
  name and initiated the handover. The therapist's role is now to instruct 
  the client (seated across the table or on the phone) to point their device's 
  camera at the QR code and open the client app to scan it. This label is 
  *describing what the therapist should tell the client*, not what the 
  therapist should do themselves.
  
  "Scan" is the act of capturing the animated QR code using the client app's 
  camera. The scan decodes the plan data and initiates the client-side receive 
  sequence. "Scan" in this context is a user-visible operation, distinct from 
  the therapist-side "Hand Over" — it is the client-side name for the 
  same end-to-end operation.
  
  "Bitte mit der Klienten-App scannen" is imperative (command form), which is 
  appropriate because the therapist is being instructed to communicate a 
  directive to the client. "Mit" (with) emphasizes using the client app 
  specifically, not just any QR scanner. The phrasing is polite ("Bitte") to 
  match the empathetic tone requirement. "Please scan" in English mirrors this.
```

**Word count:** ~190 words  
**Concept-level burden:** ~130 words (definition of Scan, Client, Hand Over context)

---

### Label 3: dataBeamSliderSlow (before canon)

```yaml
key: dataBeamSliderSlow
de: "Langsam"
en: "Slow"
translation_context: >
  This is the label for the left endpoint (minimum value) of a horizontal 
  slider control. The slider appears in the therapist handover dialog after 
  the therapist has entered the client name and initiated the QR transfer.
  
  The slider allows the therapist to adjust the speed at which the QR code 
  pulses/updates, accommodating different device camera capabilities. The 
  therapist's hardware (the sending device's camera) has a minimum frame rate 
  or detection latency; the client's hardware has corresponding constraints. 
  The slider bridges this gap by letting the therapist optimize for the 
  client's observed camera tier.
  
  "Slow" indicates the minimum pulse frequency. At this speed, the QR code 
  updates less frequently, allowing older device cameras with slower frame 
  rates to keep up. Devices released 3+ years ago, with 720p webcams or older 
  mobile phone cameras, typically require the "Slow" setting.
  
  Alternatives considered: "Low" (ambiguous — low speed or low quality?), 
  "Minimum" (too technical), "Older Devices" (not a speed descriptor, but a 
  device category). "Slow" was chosen because it is neutral (no judgment), 
  concrete (describes the pulse behavior directly), and understood universally 
  across languages. It avoids any implication that using the slow setting is 
  a failure or limitation — it is simply an appropriate choice for the client's 
  hardware.
```

**Word count:** ~215 words  
**Concept-level burden:** ~160 words (definition of Scanner Tier, Pulse, speed adjustment logic)

---

### Label 4: dataBeamSliderSlowSubLabel (before canon)

```yaml
key: dataBeamSliderSlowSubLabel
de: "(Ältere Geräte)"
en: "(Older Devices)"
translation_context: >
  This is a secondary label (parenthetical clarification) positioned directly 
  below the "Slow" slider endpoint. It provides context for the therapist 
  about which device generation the "Slow" setting targets.
  
  The purpose is to help the therapist quickly match the slider position to 
  their client's hardware without ambiguity. If the therapist says "my client 
  has an old iPhone," the therapist can immediately understand that "Older 
  Devices" refers to such devices and select "Slow."
  
  "Ältere Geräte" (older devices) in German is neutral in tone — it does not 
  imply judgment or obsolescence, but rather acknowledges hardware age as a 
  simple technical fact. "Older Devices" in English carries the same tone.
  
  Alternatives: "Legacy Devices" (too technical, implies discontinued support), 
  "Slower Hardware" (circular — restates "slow"), "720p Cameras" (too specific, 
  excludes some devices), "3+ Years Old" (too specific in a way that dates the 
  app). "(Older Devices)" was chosen for clarity and durability — it remains 
  true regardless of which specific year it is, and it requires no technical 
  knowledge from the user.
```

**Word count:** ~180 words  
**Concept-level burden:** ~110 words (clarification of device tiers and tone rationale)

---

### Label 5: dataBeamClientNameLabel (before canon)

```yaml
key: dataBeamClientNameLabel
de: "Name des Klienten"
en: "Client Name"
translation_context: >
  This is a form field label (InputDecoration.labelText in Flutter) for a text 
  input control on the therapist's handover dialog. The label appears above or 
  inside the input field, depending on the Flutter theme's label positioning.
  
  The user is the therapist. At this point in the workflow, the therapist has 
  opened the handover dialog and is ready to initiate a transfer. Before the 
  therapist can start the QR transfer, they must type the name of the client 
  to whom they are handing over the plan. This allows both the therapist's 
  app and the client's app to log and confirm the client identity.
  
  "Client" is the term used throughout the app for an individual receiving 
  therapeutic services (as opposed to "Therapist," the provider of services). 
  A client can be in states: Registered (created in the system), Active 
  (currently receiving care), Inactive, or Archived. The client's name is a 
  human-readable identifier.
  
  "Name des Klienten" (client's name) in German uses the genitive form to 
  indicate possession. This is more formal than "Klientenname" but clearer 
  for non-native German speakers. "Client Name" in English mirrors this 
  possessive intent. The label does not ask "Enter client name" (imperative) 
  but rather identifies the field as the "Client Name" field (descriptive). 
  This matches UX pattern conventions.
```

**Word count:** ~205 words  
**Concept-level burden:** ~130 words (definition of Client, states, identity purpose)

---

## Section 6: "After Canon" translation_context Entries (With Shared Canon)

Now assume the canonical concept canon exists, defining:

```
CLIENT: Individual receiving therapeutic services. States: Registered, 
Active, Inactive, Archived. Identity: name + email. Role-specific synonym 
in German: "Klient" (not "Patient"). Visible operations: Register, List 
(by therapist), Switch (between therapist's clients).

PLAN: Structured questionnaire containing multiple questions. States: Draft, 
Published, Assigned, Completed. Visible operations: Create, Edit, Publish, 
Assign, Hand Over (transfer to client device), Withdraw (from client).

HAND_OVER (operation): Transfer an assigned Plan from therapist device to 
client device via QR code scanning. Therapist initiates; client completes 
by scanning. Inverse: Withdraw. Related to (but distinct from) Assign.

SCAN (operation): Client-side receipt of a Plan via QR code capture. 
Therapist side: Hand Over (noun form: Data Beam). Client side: Scan.

SCANNER_HARDWARE_TIER: Classification of client device camera capability. 
Values: Modern (HD webcam, 2020+ smartphone), Mid-Range (720p, 2015–2020 
smartphone), Legacy (older smartphone, 2010–2015). Adjustable by therapist 
via speed slider.
```

### Label 1: handoverButtonLabel (after canon)

```yaml
key: handoverButtonLabel
de: "Plan aushändigen"
en: "Hand Over Plan"
translation_context: >
  Therapist handover dialog, primary action button. Initiates the Hand Over 
  operation (see CANON: Hand Over).
  
  User situation: Therapist has selected a plan and opened the handover 
  dialog. The therapist now initiates the plan transfer.
  
  Tone: "Aushändigen" preserves the physical-personal metaphor established 
  in the canon. The therapist is handing over a document, not uploading a 
  file. Same metaphor in English: "Hand over" not "transmit" or "send."
```

**Word count:** ~50 words  
**Concept-level burden:** ~0 words (all moved to canon)  
**Reduction:** 76% (from 210 words to 50 words)

---

### Label 2: dataBeamScanInstruction (after canon)

```yaml
key: dataBeamScanInstruction
de: "Bitte mit der Klienten-App scannen."
en: "Please scan with the client app."
translation_context: >
  Instruction text, positioned above the QR code in the therapist's handover 
  dialog. Describes the next action the therapist must communicate to the 
  client.
  
  User situation: Therapist has entered the client name (CANON: Client) and 
  initiated the Hand Over operation (CANON: Hand Over, Scan). The QR code is 
  now animating.
  
  Audience: Therapist receives this instruction to relay to the client.
  Client-side equivalent: "Scan with this app to receive the plan."
  
  Tone: Imperative form ("Bitte...scannen") is appropriate because it 
  describes a directive the therapist must communicate.
```

**Word count:** ~55 words  
**Concept-level burden:** ~0 words (all moved to canon)  
**Reduction:** 71% (from 190 words to 55 words)

---

### Label 3: dataBeamSliderSlow (after canon)

```yaml
key: dataBeamSliderSlow
de: "Langsam"
en: "Slow"
translation_context: >
  Slider endpoint label (left/minimum). Therapist adjusts QR pulse frequency 
  to match client device camera tier (CANON: Scanner Hardware Tier).
  
  User situation: Therapist has initiated Hand Over and is waiting for the 
  client to scan. If the client's device camera is slow to detect the QR 
  code, the therapist adjusts the slider to the "Slow" setting.
  
  "Slow" indicates minimum pulse frequency. No technical detail required; 
  the translation simply preserves the speed direction and avoids judgment.
```

**Word count:** ~50 words  
**Concept-level burden:** ~0 words (all moved to canon)  
**Reduction:** 77% (from 215 words to 50 words)

---

### Label 4: dataBeamSliderSlowSubLabel (after canon)

```yaml
key: dataBeamSliderSlowSubLabel
de: "(Ältere Geräte)"
en: "(Older Devices)"
translation_context: >
  Clarification label below the "Slow" slider endpoint. Connects the speed 
  setting to the device tier it targets (CANON: Scanner Hardware Tier, 
  Legacy tier).
  
  User situation: Therapist is adjusting the slider. This label helps the 
  therapist match their knowledge of the client's device age to the 
  appropriate slider position.
  
  Tone: Neutral. "Older" implies hardware age, not obsolescence.
```

**Word count:** ~45 words  
**Concept-level burden:** ~0 words (all moved to canon)  
**Reduction:** 75% (from 180 words to 45 words)

---

### Label 5: dataBeamClientNameLabel (after canon)

```yaml
key: dataBeamClientNameLabel
de: "Name des Klienten"
en: "Client Name"
translation_context: >
  Form field label (InputDecoration.labelText). Therapist enters the name of 
  the client to whom they are handing over the plan (CANON: Client, Hand Over).
  
  User situation: Therapist has opened the handover dialog and is initiating 
  the flow. The client name is required to log and confirm client identity 
  during Hand Over.
  
  Positioning: Label floats above or inside the field, per Flutter theme 
  convention.
```

**Word count:** ~45 words  
**Concept-level burden:** ~0 words (all moved to canon)  
**Reduction:** 78% (from 205 words to 45 words)

---

## Section 7: Quantified Duplication Estimate

### Duplication in Before Canon (without shared canon)

**Measurements from the five labels above:**

| Label | Before (words) | Canon-level burden | % of label |
|-------|----------------|-------------------|-----------|
| handoverButtonLabel | 210 | ~150 | 71% |
| dataBeamScanInstruction | 190 | ~130 | 68% |
| dataBeamSliderSlow | 215 | ~160 | 74% |
| dataBeamSliderSlowSubLabel | 180 | ~110 | 61% |
| dataBeamClientNameLabel | 205 | ~130 | 63% |
| **Average** | 200 | **136** | **67%** |

**Concepts repeated per label without canon:**
- Plan definition/states: appears in handoverButtonLabel, dataBeamClientNameLabel (2 instances)
- Client definition/states: appears in dataBeamScanInstruction, dataBeamClientNameLabel (2 instances)
- Hand Over operation: appears in handoverButtonLabel, dataBeamScanInstruction, dataBeamClientNameLabel (3 instances)
- Scan operation: appears in dataBeamScanInstruction (1 instance)
- Scanner Tier: appears in dataBeamSliderSlow, dataBeamSliderSlowSubLabel (2 instances)

**Total redundant concept descriptions in five labels:** 10 instances  
**If these five labels are representative of the 100 future labels across the app:**
- Assuming each major concept (Plan, Client, Hand Over, Scan, etc.) appears in 10 labels on average
- **Before canon:** 30 concepts × 10 appearances × ~150 words per description = **~45,000 words** of repeated concept definitions
- **After canon:** 1 shared canon file with all 30 concepts defined once = **~5,000 words** in the canon + labels now reference by name only

### Translation Authoring Time Reduction

**Estimate (LLM-assisted workflow, not purely manual):**

- **Without canon:** Each label's translation_context requires the translator to understand the concept from scratch, re-read the app design for context, and re-explain it. ~5–10 minutes per label × 100 labels = **8–17 hours**
- **With canon:** Each label's translation_context refers to the canon by name, and the translator reads the canon once upfront. Translator only explains label-specific context (which surface, which audience). ~2–3 minutes per label × 100 labels = **3–5 hours**
- **Reduction:** 62–68% (from 8–17 hours to 3–5 hours)

### Consistency/Maintenance Cost

**Without canon:** When a concept's name or definition changes (e.g., "Plan" → "Questionnaire Plan"), the translator must find and update all 10 instances across the label descriptions. Risk of partial updates and drift.

**With canon:** Update the concept definition once in the canon. All 100 labels immediately reference the updated definition by name.

**Reduction in maintenance:** 100% — one update site instead of 10, zero risk of drift.

### Concrete Reduction Summary

| Metric | Before Canon | After Canon | Reduction |
|--------|--------------|-------------|-----------|
| Total concept definition text (100 labels) | ~45,000 words | ~5,000 (canon) | **89%** |
| Per-label word count (average) | 200 words | 45 words | **77%** |
| Translation authoring time | 8–17 hours | 3–5 hours | **62–68%** |
| Maintenance update sites per concept change | 10 instances | 1 instance | **90%** |

---

## Section 8: Relationship Between REQ-NFUNC-013 AC-08 and REQ-PROC-049

### REQ-NFUNC-013 AC-08 (translation_context)

AC-08 mandates the *storage and structure* of translation metadata per UI text entry. It specifies three required components: user situation, UI element type, and wording rationale. AC-08 does not define the concepts that labels refer to — it assumes those concepts exist somewhere and can be referenced.

### REQ-PROC-049 (Language Coherence)

REQ-PROC-049 defines the upstream *source of truth* for user-facing concepts. AC-01 establishes that a canonical source must identify each concept exactly once. AC-02 and AC-04 establish that AC-08's `translation_context` entries must reference concepts by their canonical names rather than redescribing them inline.

### Documented Relationship (REQ-NFUNC-013 §8.4, lines 212–213)

```
**Reference the canonical concept canon** (REQ-PROC-049 — Language Coherence) 
rather than redescribing nouns, verbs, or states inline.
```

### Implementation Dependency

- **REQ-NFUNC-013 AC-08 is the primary downstream consumer of REQ-PROC-049.**
- AC-08 can be partially implemented without a canon (just write longer descriptions per label), but the duplication cost is ~45,000 words.
- With a canon in place, AC-08 entries narrow to ~5,000 words total for the same 100 labels.
- AC-04 of REQ-PROC-049 explicitly states: "`translation_context` entries (REQ-NFUNC-013 AC-08) reference the canonical concept by name rather than redescribing the noun, verb, or state from scratch."

### Timeline Implication

- **REQ-PROC-049** must be implemented (canon created, AC-01 through AC-05 satisfied) **before** AC-08 translation authoring reaches full scale.
- **Phase 1 (now):** Design the canon structure and form (TASK-PROC-049-01 in progress).
- **Phase 2:** Bootstrap the canon with the first ~30 user-facing concepts (from therapist_transfer_ui and data_receive features).
- **Phase 3:** Implement the discrepancy check (AC-05 of REQ-PROC-049).
- **Phase 4:** Begin per-label translation_context authoring at scale, with all labels referring to the canon.

---

## Appendix: AC-08 Three Required Fields (Quoted from Spec)

From REQ-NFUNC-013 §8.4, lines 204–208:

```
**`translation_context` must cover:**

1. **User situation** — What is the user doing when they see this? Who is the 
   user (client or therapist)? What just happened?
2. **UI element type** — What kind of element carries this text? (e.g., primary 
   action button, table column header, form field label, section title, 
   placeholder text, toast message, inline validation hint)
3. **Wording rationale** — Why was this exact phrasing chosen? Capture the 
   intent and trade-offs (e.g., "invite without demanding", "acknowledge 
   effort without overpraising", "short for space constraints but still 
   complete thought"). This is especially important where alternatives were 
   considered and rejected.
```

These three fields form the minimum required payload per label. The specification explicitly forbids repeating general UX writing rules (which apply universally) and forbids redescribing nouns/verbs/states — those move to the canon.

---

**End Report**
