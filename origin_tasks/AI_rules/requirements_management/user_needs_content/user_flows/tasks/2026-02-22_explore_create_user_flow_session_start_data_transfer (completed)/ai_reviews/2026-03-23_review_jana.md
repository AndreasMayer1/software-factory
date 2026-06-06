-02

**Reviewed**: 2026-03-23
**Reviewer**: Opus (claude-opus-4-6), investigation specialist
**Artifacts reviewed**:
- PERSONA-014 v1.4 (`requirements_user_needs/personas/jana_high_strung/persona.md`)
- SCEN-014-02 v1.0 (`requirements_user_needs/personas/jana_high_strung/scenarios/transfer_data_to_therapist/scenario.md`)
- FLOW-003 third iteration (`requirements_user_needs/user_flows/session_start_data_transfer/flow.md`, updated 2026-03-23)
- FLOW_INDEX.md, all nine READMEs

---

## Fit Score: 5/10

**Rationale**: FLOW-003 reliably addresses Jana's most basic need — forgetting-proof availability — and gets the privacy architecture right in ways that matter enormously for BPD. It is genuinely thoughtful about shame mechanics. However, five of Jana's seven derived needs are either unaddressed or only superficially touched, and the claim of "full" coverage obscures structural gaps that will surface during implementation if not addressed now. The flow is a sound foundation for Max (PERSONA-002, whose primary failure mode is the forgotten object) and Sophie (PERSONA-010, whose data is already rich). For Jana, whose primary failure mode is that the data arrives but lies, the flow solves the wrong problem at a level of detail that does not match the complexity of her needs.

---

## What Works Well

### 1. Forgetting-Proof Availability (Derived Need 5) — Fully addressed

The scenario's most visceral pain point is that the physical object might not make it: "If the diary is forgotten, damaged, or emotionally destroyed (torn pages), the data is gone" (SCEN-014-02 Pain Points). FLOW-003 eliminates this structurally. The data lives on the device Jana already carries. There is no secondary object to remember, check twice on the way out, or destroy during a crisis episode. This directly addresses the morning-alarm, double-check, nightstand-to-backpack ritual documented in the scenario's "How This Works Today" step 1.

### 2. Shame-Resistant Handover Mechanics (Derived Need 2) — Substantially addressed

The scenario documents Jana's pre-emptive disclosure ("I have it. Three days filled, five blank") as a defensive move — she states the failure before Frau Albrecht can react to it. FLOW-003 addresses this in several ways:

- **Exception 2.2**: When there is no data, the app says "No data to transfer yet" — non-shameful, non-error framing. This is especially important because the scenario documents a failure mode where the fourth week the diary is not brought at all ("forgotten, hidden, or destroyed").
- **Emotional success metrics**: "Client with missing/incomplete data does not feel shamed — flow communicates 'what you have is enough for now.'"
- **Exception 3.2**: Scope narrowing is frictionless and non-judgmental. No "Are you sure?" dialog. The note explicitly calls Jana out by name as the primary motivation: "especially relevant for Jana (BPD), who may not want to share crisis entries she self-censored before the session."
- **Skip persistence**: Entries excluded in session 1 remain excluded in session 2 without re-prompting. This is architecturally important for Jana's self-censorship failure mode (SCEN-014-02 Failure Modes: "Jana re-reads the diary in the waiting room, panics about what Frau Albrecht will see, and tears out Monday's page").

### 3. Schwarzes Buch Privacy Boundary — Correctly modeled

Jana's persona establishes a non-negotiable constraint: "Any blurring of private and shared data boundaries betrays her trust and destroys the protective function of private expression" (PERSONA-014 VCD, secondary value: Autonomy). The Schwarzes Buch and the Trigger-Logbuch are explicitly listed as private — never to reach the therapist under any circumstances.

FLOW-003's structural privacy boundary handles this correctly:
- Private diary entries are **architecturally excluded**, not controlled by a toggle
- "Private diary entries remain excluded regardless of any opt-in action" (Privacy Boundary section, item 3)
- The Data Scope Screen never shows private entries as shareable — they are simply absent

This is the right design for Jana's value conflict between absolute private space and therapeutic data sharing (PERSONA-014 VCD value_conflicts).

### 4. Self-Censorship Without Therapist Notification (Derived Need 2, Exception 3.1)

The scenario documents a failure mode where Jana plays voice memos for Frau Albrecht but refuses to share others because "the voice messages also contain fragments she does not want Frau Albrecht to hear." Exception 3.1 in the flow handles the digital equivalent: if Jana closes the transfer section without sharing, "the app does not need to communicate to the therapist that the client 'chose not to share.'" There is no alert to the therapist, no flag, no record of refusal. This is correct — the paper system had the same property (the diary that stayed in the bag left no trace of its absence on Frau Albrecht's side).

### 5. Pre-Session Bundle Preparation — Matches Jana's pre-session ritual

The scenario documents Jana's Wednesday night preparation session (SCEN-014-01, referenced as the upstream scenario). The flow's optional pre-session bundle creation feature (Preconditions, Adaptive UI Rules) allows Jana to assemble the transfer scope at home during a calm moment — rather than making scope decisions in the waiting room under pre-session anxiety. This matches the scenario's description of Jana rehearsing in her head on the tram, having already reviewed the diary the night before.

### 6. Transfer Duration Appropriate for Session Context

The scenario's PCD check specifies: "Handover completes in minimum necessary time (~2 minutes for physical transfer)." FLOW-003's functional success metric targets "Transfer completes in under 60 seconds for a typical week of entries (7 days x 1–3 entries/day)." This is faster than the paper handover's ~2 minutes of physical handling and faster than the 30 minutes of verbal reconstruction that currently follows. The animated QR mechanism is well-suited to the session waiting-room context.

### 7. Value Trade-off 2 — BPD Shame Dynamics Explicitly Acknowledged

The flow documents the clinical safety vs. client data control tension in its Value Trade-offs section, referencing "PERSONA-014's BPD shame dynamics and self-censorship patterns documented in SCEN-014-02." This demonstrates the flow author was aware of Jana's specific needs. The resolution — client data control is primary; clinical interview supplements; supplementary opt-in provides a voluntary path for more sharing — is the correct approach for a privacy-first therapeutic tool.

---

## Missing Elements

### 1. Multi-Source Integration (Derived Need 3) — Not addressed

The scenario's most clinically significant finding: "We have three data sources here: the diary, which gives us Monday through Wednesday with numbers and brief notes. Your memory, which fills in the gaps but changes each time you access it. And this voice message, which gives us a real-time emotional snapshot but no structure. None of them alone is enough" (SCEN-014-02 Act 2, Frau Albrecht speaking).

The scenario's Derived Need 3 explicitly requires: "A way to consolidate diary entries, voice memos, texts, and phone notes into a single timeline that Frau Albrecht can review — without requiring Jana to curate and de-clutter her personal messaging apps in the waiting room."

FLOW-003 provides no mechanism for this. The flow's supplementary data opt-in (Step 3 advanced controls, Preconditions) covers "protocols from previous therapists, self-assigned protocols, or self-tracking entries" — all of which are data already captured within the app's own data structures. Voice memos sent to Mira, text threads, informal phone notes — data that lives in third-party apps — are not mentioned anywhere in the flow.

This is a significant gap. The scenario documents the 7-second voice message as more therapeutically useful than three days of diary entries. The flow's transfer mechanism is only as good as what was captured in the app itself. If Jana's most emotionally truthful data continues to live in WhatsApp and her phone's voice memo app, FLOW-003 delivers digital transfer of the least useful data and leaves the most useful data exactly where it was.

**Is this legitimately out of scope?** Partially. The general data capture flow (needed: Universal Routine Entry, identified in FLOW_INDEX.md as HIGH PRIORITY) would address whether voice memos can be captured within the app during crisis moments. However, FLOW-003 does not acknowledge this dependency. If the capture flow does not exist yet, the transfer flow cannot be evaluated in isolation — and claiming "full" coverage while this dependency is unresolved is premature.

### 2. Volatility Preservation in Visualization (Derived Need 1) — Deferred without resolution path

The scenario's core data problem: "Mood 2" on Monday was wrong. The day was actually 8→1→6. The paper diary had structural limits — one number per day — that distorted the clinical picture. Jana's annotation "Actually: 8→1→6" in the margin was the correction.

FLOW-003 correctly notes: "Volatility preservation (8→1→6) depends on how data was captured, not on the transfer mechanism itself" (scenario's flow reference notes). The flow transfers whatever was captured — if the capture format supports intra-day trajectories, the transfer preserves them. This is logically correct.

However, the flow's visualization step (Step 9) makes no commitment about how volatility is rendered. The relevant language: "The specific layout details of the visualization are not defined in this flow; they may depend on protocol type, therapist configuration, or layout rules embedded directly in the protocol itself" (Step 9, Overview). The Adaptive UI Rules note for journal/structured protocols does not mention intra-day volatility display at all.

For Jana, the visualization is not a neutral implementation detail. If the Client Data View (Step 9) opens to a daily average view — which is the default presentation of most mood tracking visualizations — the data arrives accurately but the visualization lies in exactly the same way the paper diary did. The scenario's success criterion is: "The data conveys the shape of the week (volatility, crisis peaks, gaps) not just an averaged summary." FLOW-003 makes no commitment that the visualization at Step 9 satisfies this criterion.

**Who is responsible for this?** The flow assigns it to the implementing epic. But without explicit requirements in the flow — a note that BPD-profile protocols must display intra-day trajectories prominently, not average them — the implementing epic may reasonably produce a standard trend chart that replicates the paper diary's structural distortion in digital form.

### 3. Blank Days as Avoidance Data — Not addressed in visualization or transfer

The scenario's second most important clinical finding: "Five days without entries communicate 'did not do homework' when the reality is 'could not face the notebook after a crisis.' The format has no way to distinguish between laziness and avoidance" (SCEN-014-02 Pain Points).

In the paper scenario, Frau Albrecht identifies the blank days as a maintenance cycle — not failure but data. She says: "That's a maintenance cycle. The avoidance of the diary became its own source of distress, which increased the avoidance. We can work with that" (SCEN-014-02 Act 2).

The scenario's success criterion explicitly requires: "Blank days are acknowledged as information (avoidance pattern), not treated as missing data."

FLOW-003 has no mechanism for this. The Data Scope Screen shows "which protocol(s), date range covered, number of entries." It does not distinguish between days where Jana opened the app and chose not to log (active avoidance), days where she never opened the app (passive omission), days where she started an entry and abandoned it (interrupted capture), and days where she was in acute crisis and could not use the app (crisis inaccessibility — documented in PERSONA-014 Anti-traits: "cannot use complex multi-step tools during crisis").

These are clinically different states. A visualization that shows a blank where there was avoidance is less useful than the paper diary's blank, because at least the paper blank is ambiguous in a way the therapist can probe. A digital visualization that shows nothing may actually be harder to interpret than paper blanks — it lacks the physical evidence of blank pages, the stickers, the crinkled entries, the changing pen colors. These contextual signals from the paper system (documented in SCEN-014-02: "The 'Brave' sticker on the cover is peeling at one corner") are lost in digital transfer.

### 4. Session Ritual and Transition Moment — Not addressed

The scenario documents a specific ritual value of the paper handover: "Placing the diary on the table creates a transition moment — small talk ends, clinical work begins. The object marks the boundary" (SCEN-014-02 "What Works Well," item 1: "Physical handover as ritual").

The flow's design ends the moment "the therapist's device is displaying the transferred data in a visual representation" (Step 9 Flow end state). The transfer is intended to be fast — under 60 seconds. But the scenario's handover ritual is not about speed; it is about the quality of the transition.

In the paper system, Jana "pulls the diary from her backpack and places it on the low table between them. The gesture is deliberate. She does this quickly, before she can change her mind." The physical act of placing the object — the deliberateness, the irreversibility of the gesture — has therapeutic significance. It marks the moment of commitment.

FLOW-003's QR transfer is a phone-to-webcam operation. The client holds their phone toward the therapist's laptop camera. This is a functional gesture, not a ritual one. It may feel more like "connecting to a printer" than "handing over something vulnerable." The flow does not acknowledge this difference, nor does it suggest UI or interaction design that might preserve the transitional quality of the handover.

This is not necessarily something the flow must solve — ritual design may be out of scope for a requirements document. But its absence from the "What Works Well" analysis in the flow's Value Trade-offs section suggests it was not considered for Jana's profile.

### 5. Pre-Session Commute — Out-of-scope but unacknowledged dependency

The scenario's Act 1 is entirely set on the tram. Jana cannot review her diary on the commute because entries contain names, crisis details, raw emotional language — legible to a nearby stranger. This is a documented pain point: "The twelve-minute commute is spent in anticipatory rehearsal, not data review" (SCEN-014-02 "How This Works Today," step 2).

Derived Need 4: "Public-Safe Review — A way to review therapy data during commute without risking exposure of crisis content to strangers. The data must be accessible and concealable in the same gesture."

FLOW-003 does not address the commute. The flow begins at the moment of transfer (Step 1: "Client opens the transfer section"). This is correct — a transfer flow should not address what happens on the tram. However, the "full" coverage claim implies that all of Jana's needs in this scenario are addressed. The commute need (Derived Need 4) is not addressed by any existing flow. FLOW_INDEX.md lists "Privacy & Camouflage" (brainstorm ref FLOW-010) as relevant to Jana and "Roommates" context, but that flow is not yet created and is not referenced from SCEN-014-02.

The coverage claim should acknowledge that Derived Need 4 (Public-Safe Review) is out of scope for FLOW-003 and is not yet addressed by any existing flow.

### 6. Format Flexibility Without Guilt (Derived Need 7) — Addressed at wrong layer

The scenario documents the template rejection spiral: "The cycle of format change → initial enthusiasm → abandonment → shame has happened three times before" (SCEN-014-02 Failure Modes). The therapist's introduction of a new multi-column template at session end creates anxiety: "More columns means more obligation, more blank cells to feel guilty about, more chances to fail."

FLOW-003 transfers whatever was captured. It cannot address format flexibility because it is a transfer flow, not a capture flow. However, the "full" coverage claim implicitly includes this need. The note in SCEN-014-02's flow reference acknowledges only that "volatility preservation depends on capture" — not that format flexibility is similarly upstream.

Derived Need 7 depends entirely on the general data capture flow (Universal Routine Entry, FLOW_INDEX.md), which does not yet exist. Claiming "full" coverage for the transfer scenario while the capture scenario has no implementing flow is a gap in the coverage architecture.

---

## Contradictions

### 1. QR Transfer Requires Fine Motor Control During Potential Crisis States

The scenario documents Jana's state during session transitions: "Low-grade anxiety layered over the residue of last night's preparation session" with "medium-high cognitive load" (SCEN-014-02 Context). This is a non-crisis state — Jana is on the tram, not flooding.

However, the flow's QR mechanism requires the client to:
- Open the app and navigate to the transfer section
- Review the Data Scope Screen and confirm scope (Step 2)
- Select a transfer mode (Step 3, "most users: one of two taps")
- Hold the phone steady toward a webcam (Step 6: "Client holds phone screen toward the therapist's webcam")
- Adjust the working-distance slider if needed (Step 6, Exception 4.1B)
- Explicitly confirm "Transfer Successful" or "Transfer Failed" at Step 8

This is a multi-step process requiring sustained attention and some degree of fine motor control (holding the phone steady during a potentially 60-second transfer). The persona explicitly states: "NOT comfortable with tools that require fine motor control during high tension" (PERSONA-014 Anti-traits). The flow assumes a calm-enough client state — which the scenario's context supports (Jana is not in crisis when she arrives at the session). But the flow does not acknowledge that this assumption about client state is load-bearing.

The risk is real: Jana's emotional state on arrival is not guaranteed. The scenario describes a specific failure mode — "Emotional flooding during handover: Jana cannot speak. The session shifts from data review to crisis management" (SCEN-014-02 Failure Modes). If this happens during the QR transfer (after Step 3 but before Step 8), Jana must:
1. Recognize that the transfer has stopped or failed
2. Navigate to "Transfer Failed" at Step 8 — or simply close the app
3. Not accidentally mark the transfer as successful when it was not

The flow handles the interrupted transfer case (Exception 4.2) but does not address what happens when the client floods emotionally during Steps 4–8. The therapeutic priority in that moment is not data transfer — it is clinical intervention. The flow should explicitly state that the client can abandon the transfer at any point without penalty, and that this is expected and gracefully handled (the entries remain unshared, the therapist is not notified, the session proceeds with verbal data).

This is not addressed in Exception 3.1 (which covers "decides not to transfer before starting") or Exception 4.2 (which covers "phone moved away mid-transfer" for technical reasons). There is a gap in the exception model for the emotionally-flooded client who partially initiates transfer and then cannot continue.

### 2. Working-Distance Slider Contradicts Fine Motor Control Constraint

Exception 4.1 and the QR Transfer Screen description include "a slider with a small number of discrete steps" for adjusting working distance. A slider, even with discrete steps, is fine motor interaction under potential session anxiety. The PERSONA-014 Anti-trait is explicit: not comfortable with fine motor control during high tension.

While the working-distance slider is likely needed rarely (the default 20cm works for most cameras), it is presented as a user-facing control rather than an automatic fallback. The flow might bett