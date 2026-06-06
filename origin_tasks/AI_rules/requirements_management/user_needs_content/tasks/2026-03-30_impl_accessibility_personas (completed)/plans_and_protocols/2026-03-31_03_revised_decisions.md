# Revised Decisions: Accessibility Personas
**Date**: 2026-03-31
**Task**: TASK-PROC-027-36
**Supersedes**: `2026-03-31_02_preanalysis.md` (partially — see Section 2)

---

## 1. Therapist Accessibility Gap Analysis

### Q1 — Does Felix's persona cause flow authors to apply flash rate constraints to the therapist's visualization?

**Answer: No.**

Felix (PERSONA-018) is a **client**. His VCD primary value states "every animated element must be evaluated against the ≤3Hz flash rate threshold before deployment," and this is true — but the framing is from Felix's perspective as a user of the **client-side app**. When a flow author reads Felix's persona, they understand that Felix holds his phone toward the therapist's webcam (FLOW-003 Step 3). Felix's own screen shows the animated QR code sequence. The therapist looks at their own laptop.

The two screens are physically separate and role-separate:

| Screen | Who experiences it | What's animated | Flash risk |
|--------|-------------------|-----------------|------------|
| Client phone — QR Transfer Screen | Felix (and any photosensitive client) | Animated QR code sequence | **High** — the core WCAG 2.3.1 risk |
| Therapist laptop — QR Receive Screen | Dr. Sarah / Turan / Weber | Progress indicator, "Receiving from [Name]" — no QR animation | Low |
| Therapist laptop — Client Data View | Dr. Sarah / Turan / Weber | Entrance animation ~1–2s (VTR-005) + chart renderings | Potentially present but separate from Felix's screen |

A flow author reading Felix's persona will correctly conclude: "the animated QR code on the client's phone must comply with ≤3Hz." They will **not** automatically apply this to the therapist's visualization entrance animation (FLOW-003 Step 6, VTR-005), because that animation plays on the therapist's screen while Felix is standing a meter away pointing his phone at a webcam. Felix cannot see it; it is not Felix's problem.

**Consequence**: The therapist's visualization entrance animation (VTR-005) and any future animated chart elements are **outside the reach of Felix's constraint persona**. If those animations ever violate WCAG 2.3.1, Felix's persona will not have caught the problem.

---

### Q2 — Does Rahel's persona (proposed PERSONA-019, low vision self_user) cause flow authors to consider the therapist's visualization contrast and text scaling?

**Answer: No.**

Rahel is a **self_user** — she uses the app independently without a therapist. Her usage context encompasses: data entry screens, self-review/reflection screens, app settings. She does not participate in FLOW-002 (therapist sends protocol) or FLOW-003 (session data transfer), because those flows are structurally therapist-client flows.

A flow author authoring FLOW-003 reads: "primary personas: client side — Max (PERSONA-002), Sophie (PERSONA-010), Jana (PERSONA-014); therapist side — Dr. Sarah (PERSONA-001), Dr. med. Turan (PERSONA-012)." Rahel is not in this list. Her low-vision constraints (contrast, text scaling, non-color redundancy in visualizations) will apply when flow authors work on self-review flows or data entry flows — not when they author the therapist's Client Data View.

**Consequence**: The therapist's Client Data View visualization — charts showing client mood trends, medication adherence, narrative entries — has no accessibility persona driving contrast, text scaling, or non-color redundancy considerations on the therapist's screen. Rahel covers the self-user's data entry and self-review screens; she does not cover the therapist's analysis screens.

---

### Q3 — Do existing therapist personas carry any accessibility-relevant constraints?

**Answer: No.**

All three therapist personas (PERSONA-001 Dr. Sarah, PERSONA-011 Prof. Dr. Weber, PERSONA-012 Dr. med. Turan) have:
- `conditions: []` — no documented accessibility conditions
- `pcd.device: Windows desktop` — Windows desktop or no in-session device

Their personas describe clinical workflow frustrations, protocol preferences, data sensitivity concerns, and professional values. No therapist persona references visual impairment, motor constraints, cognitive load (beyond professional time pressure), or any other characteristic that would cause a flow author to apply accessibility constraints to the therapist-side UI.

Prof. Dr. Weber is notable: his persona explicitly documents that he uses **no technology in the therapeutic context** (clinical design decision DEV-1 in FLOW-003). This means the therapist-side accessibility gap is moot for Weber — he is not served by FLOW-003's visualization at all.

The gap is specifically on the screens used by Dr. Sarah and Dr. med. Turan: the Client Data View visualization on their laptop.

---

### Summary of Gap

The **preanalysis (2026-03-31_02_preanalysis.md)** correctly identified photosensitive epilepsy and low vision as the two accessibility gaps needing persona coverage. What it missed is the **scope of coverage**: both proposed personas (Felix as client, Rahel as self_user) cover only their own screens. Neither reaches the therapist's Client Data View — the one screen in the app that displays data visualizations (charts, trends, timeline views) as a primary interface, under clinical time pressure, for a user who is not represented by any accessibility persona.

---

## 2. Revised Minimum Persona Set

### Evaluation framework (applied in order)

A new therapist accessibility persona is justified **only if** all three conditions hold:
1. There is a real constraint that would change how a flow is designed
2. That constraint is not already covered by an existing rule (REQ-NFUNC-002) or persona
3. No existing persona causes flow authors to encounter this constraint as a natural consequence

Applying this to the two candidate therapist gaps:

---

### Candidate A: Therapist with low vision reading the Client Data View visualization

**Condition 1 — Real constraint?** Yes.
The Client Data View (FLOW-003 Step 6) is a data visualization screen — charts, timeline views, trend lines. These screens carry specific accessibility risks that flat text or form screens do not:
- Color-only encoding of data series (e.g., red line vs. blue line for two protocol tracks) → invisible to color-blind users; contrast requirement applies differently to chart elements than to text
- Small axis labels and data point annotations rendered at fixed density → break at text scaling
- Non-color redundancy (patterns, shapes, labels alongside colors) is not enforced by generic WCAG AA contrast rules

These are visualization-specific constraints, not generic screen constraints.

**Condition 2 — Already covered by existing rules?** Partially, but not completely.
- WCAG AA contrast (AC-04, AC-05): covered by REQ-NFUNC-002 universally — applies to the therapist's visualization equally.
- Text scaling to 200% (AC-11): covered universally.
- Non-color redundancy: **not** covered by REQ-NFUNC-002. The existing requirements focus on contrast ratios and touch target sizes. Chart-specific non-color redundancy (the principle that a color-encoded data series must have a second distinguishing property — shape, pattern, label) is not stated anywhere in the current requirements or persona set.
- WCAG 2.3.1 flash rate: **not** covered in REQ-NFUNC-002. Felix's persona covers it for the client's animated QR screen but not for the therapist's visualization.

**Condition 3 — Does any existing persona reach this screen?** No.
- Felix is a client; his persona covers the client's QR Transfer Screen.
- Rahel is a self_user; her persona covers self-review and data entry screens.
- All three therapist personas have `conditions: []`.

**Verdict: Gap exists. But is it large enough to warrant a new persona?**

Here the minimum-count principle applies. Consider what a therapist accessibility persona would actually add:
- Contrast and text scaling on the visualization: already required by REQ-NFUNC-002 for all screens. A persona would reinforce this for the visualization specifically, but would not add a constraint that doesn't already exist in rule form.
- Non-color redundancy: this is a gap. But it is also a **visualization design principle** that belongs in the visualization epic's design requirements, not exclusively in a persona. The persona would be the vehicle that causes flow authors to discover this need, but the actual constraint is a design rule.
- Flash rate on entrance animation (VTR-005): marginal risk. The entrance animation is specified as ~1–2s, silent, and non-interactive. A smooth fade or slide of that duration does not produce repeated flashes — it produces one continuous transition. WCAG 2.3.1 targets repeated luminance changes (strobing), not a single fade-in. This is genuinely not a flash risk for the therapist's visualization.

**Decision: No therapist accessibility persona.**

The gap in non-color redundancy for the Client Data View is real, but it is **not best addressed by a persona**. The reasoning:

1. The therapist's visualization screen is explicitly **out of scope for the current approved flows** — "the specific layout details of the visualization beyond the Adaptive UI hierarchy rules are intentionally out of scope for this flow and will be specified in a dedicated visualization / collaborative analysis flow" (FLOW-003). This means the visualization epic has not been authored yet. A therapist accessibility persona created now would generate constraints that cannot be acted on until the visualization epic is written.

2. A therapist with low vision is a real user archetype, but the therapist's workflow is fundamentally different from a client's: the therapist reviews data in a clinical session context (time pressure, professional context, Windows desktop), not in personal health tracking. Creating a low-vision therapist persona would need to be grounded in the clinical therapist workflow — not a diagnostic checklist. This is a legitimate future persona, but it requires the same pre-work rigor applied to all therapist personas. Creating it now, without scenario grounding, risks producing a thin constraint persona that doesn't hold up under scrutiny.

3. The correct mechanism for the non-color redundancy constraint on the visualization is a **note added to the task or planning record** that flags this for the visualization epic author, combined with the app_provider commitment (see Section 4) that makes WCAG compliance universal. This is a planning artifact, not a persona artifact.

4. Under the minimum-count principle: a persona that merely restates universal WCAG rules for one specific screen adds token cost to every future flow generation call without adding a constraint that isn't already law. The rule exists; the persona is not the right vehicle.

---

### Candidate B: Therapist with photosensitive epilepsy and the entrance animation (VTR-005)

**Verdict: No gap requiring a persona.**

The FLOW-003 entrance animation (VTR-005) is ~1–2 seconds, silent, non-interactive, triggered once per transfer completion. A smooth entrance animation of this duration — a fade or slide — does not produce repeated luminance flashes. WCAG 2.3.1 applies to "flashing" defined as rapid repeated luminance changes; a single fade-in event does not meet this definition. The risk exists if a future animation is designed as a strobe or repeated flash, not for the currently specified entrance animation.

Additionally: Felix's VCD states "every animated element must be evaluated against the ≤3Hz flash rate threshold before deployment." While Felix is a client persona and cannot directly reach the therapist's screen, his VCD's "every animated element" framing creates a universal principle that a careful flow author should recognize. The app_provider update (Section 4) makes this universal in the governance documentation.

---

### Final minimum persona set

| # | Persona | Role | Status | Rationale |
|---|---------|------|--------|-----------|
| PERSONA-018 | Felix | client | Already written — confirmed correct | Photosensitive epilepsy; covers animated QR code (FLOW-003 client side) and all future client-app animations |
| PERSONA-019 | Rahel | self_user | Create (as per preanalysis) | Low vision; covers contrast, text scaling, non-color redundancy for self-review and data entry screens; drives AC-07 and AC-08 persona justification |
| PERSONA-015 | app_provider | system | Update (as per preanalysis, with one addition) | Add release-scoped commitment table + WCAG 2.3.1 explicit; add note that flash rate constraint applies to ALL screens including therapist-side visualizations |
| Therapist accessibility persona | therapist | **Do not create** | Gap exists but is not mature enough; visualization epic not yet authored; constraints are better placed in visualization epic planning notes |

---

## 3. Decision Table

| Action | Artifact | Type | Constraint driven | Scenario | ID |
|--------|----------|------|-------------------|----------|----|
| Already written — confirmed | Felix persona | Constraint persona | WCAG 2.3.1 flash rate ≤3Hz on all animated elements in client app; photosensitive epilepsy medical constraint | None (as-is identical to non-impaired users) | PERSONA-018 |
| Create | Rahel persona | Regular persona | Low vision: WCAG AA contrast, text scaling 200%, non-color redundancy in data visualizations, screen reader path foundation | Yes — `capture.routine` category: how Rahel currently manages mood tracking with her accessibility constraints | PERSONA-019 |
| Update | app_provider persona | System persona update | All v1/post-v1 accessibility commitments with release scope; WCAG 2.3.1 explicit as universal rule covering all screens including therapist-side; non-color redundancy flag for visualization epic | N/A | PERSONA-015 |
| Flag for visualization epic | Planning note (not a persona) | Documentation | Non-color redundancy in Client Data View charts; therapist-side text scaling at visualization density; confirm no flash animation in chart rendering | N/A | N/A |

---

## 4. app_provider Update

### Confirmation

The release-scoped commitment table proposed in the preanalysis is confirmed, with **one addition**: the WCAG 2.3.1 flash rate rule must be stated as applying to **all screens in the app** — not only screens where Felix is a primary persona. This is the mechanism by which the therapist's visualization entrance animation (VTR-005) and any future chart animations fall under the flash rate constraint even without a therapist accessibility persona.

### Updated commitment table (for app_provider persona, Accessibility as Core Value section)

| v1 (0.0.5 / 1.0.0) | Post-v1 |
|---|---|
| WCAG AA contrast (4.5:1 text, 3:1 UI) — all screens | Full TalkBack/VoiceOver optimization (AC-08) |
| 48dp touch targets (AC-01) | High-contrast theme variant (AC-07) |
| Basic semantic labels — every interactive element labeled (AC-09a) | Advanced semantic descriptions (AC-09b) |
| Text scaling to 200% without overflow (AC-11) | Switch/keyboard focus navigation (AC-10) |
| Reduce Motion system setting respected (AC-12) | |
| **WCAG 2.3.1: all animated elements ≤3Hz flash rate — applies to every screen regardless of role (client, therapist, self-user)** | |

The bolded addition is new relative to the preanalysis. It closes the coverage gap identified in this analysis: by stating the flash rate rule as universal in the app_provider governance documentation, flow authors working on therapist-side flows are bound by the same rule as those working on client-side flows — without requiring a separate therapist accessibility persona to carry the constraint.

### Additional note for app_provider

The accessibility section should also note: "Data visualizations (charts, trend views, timeline displays) must use non-color redundancy — color must not be the sole encoding property for any data dimension. This applies to all visualization screens including the therapist's Client Data View." This seeds the constraint for the visualization epic without requiring a new persona.

---

## 5. Verdict on Felix (PERSONA-018)

**Felix is correct as written. No changes needed.**

Specific confirmations:

- **Role (client)**: Correct. Felix's constraint applies to the client-side app where he uses the QR Transfer Screen with its animated QR code sequence. This is the primary WCAG 2.3.1 risk surface in the current flows.

- **Constraint precision**: Correct. The VCD primary value correctly identifies the ≤3Hz flash rate as a hard medical safety constraint, not a preference. The "every animated element" language is correct — it applies universally within Felix's interaction surface (client app).

- **No scenario**: Correct. Felix's as-is pen-and-paper tracking is identical to non-impaired therapy clients. There is no meaningfully different as-is user journey that would generate scenario content.

- **Scope limitation (clarified by this analysis)**: Felix's persona covers the client-side app. It does not reach the therapist's visualization screen by persona mechanics. This is not a flaw in Felix's persona — it is a correct reflection of who Felix is (a client, not a therapist). The therapist-side flash rate coverage gap is addressed through the app_provider universal commitment (Section 4), not through Felix's persona.

- **One open question flagged for Felix's review**: Felix's VCD "every animated element" language is stated from Felix's first-person use context. If future flows are authored where Felix is in the room during the therapist's visualization rendering (which is the case in FLOW-003 Step 6 — both therapist and client observe the entrance animation), a careful flow author might ask: "Can Felix see the therapist's screen too?" The answer is: yes, Felix is in the room during Step 6. The entrance animation plays on the therapist's laptop screen, which Felix can see from across the desk. This means Felix's flash rate constraint arguably *does* apply to the therapist's entrance animation — Felix experiences it.

  This is a genuine nuance. The entrance animation as specified (~1–2s smooth fade) is not a flash risk, so there is no practical problem with the current design. But if a future flow author introduces an animated visualization element on the therapist's screen (pulsing safety alerts, animated chart transitions), Felix's in-room presence means his constraint applies. The persona as written does not make this explicit. **Recommendation**: No change to the Felix persona is needed now, but the visualization epic planning note (Section 3) should reference this nuance explicitly.

---

## 6. Downstream Actions

The following actions follow from this revised decision and must be completed in the remaining cascade passes:

| Pass | Action | Notes |
|------|--------|-------|
| Pass 1 (current) | Create PERSONA-019 Rahel | Regular persona, self_user, low vision, scenario needed in `capture.routine` |
| Pass 1 (current) | Update PERSONA-015 app_provider | Add release-scoped table + WCAG 2.3.1 universal + non-color redundancy visualization note |
| Pass 1 (current) | Add planning note to this task folder | Flag visualization epic: non-color redundancy in Client Data View; Felix in-room nuance |
| Pass 2 | Create Rahel scenario | `capture.routine` category: current as-is mood tracking with low-vision constraints |
| Pass 3 | Update FLOW-003 | Reference both PERSONA-018 and PERSONA-019 where relevant; confirm entrance animation (VTR-005) complies with ≤3Hz (it does — smooth fade); add note about Felix's in-room presence during Step 6 |
| Pass 4 | requ-derive-from-flow --incremental | Flash rate constraint and non-color redundancy may generate new requirements |

No therapist accessibility persona is created in any pass.
