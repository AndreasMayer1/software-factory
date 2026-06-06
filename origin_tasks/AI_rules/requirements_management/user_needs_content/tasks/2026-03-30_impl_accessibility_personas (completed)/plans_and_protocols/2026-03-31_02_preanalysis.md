# Pre-Work Analysis: Accessibility Personas
**Date**: 2026-03-31
**Task**: TASK-PROC-027-36

---

## Question 1 — What accessibility categories are actually relevant to this app?

The app is a mood/self-tracking tool with: mood entry via text and voice-to-text, animated QR-code data transfer, data visualizations (charts/graphs), and standard tap/button navigation.

From REQ-NFUNC-002, the categories under consideration and their relevance:

| Category | Relevance | Reason |
|---|---|---|
| Motor constraints | **Already covered** | Jana (trembling hands in crisis), Sophie (motor imprecision), Nina (fatigue coordination). REQ AC-01 48dp targets grounded in these. |
| Photosensitive epilepsy | **High** | Animated QR code in FLOW-003 flashes at a rate that may exceed WCAG 2.3.1 (≤3Hz). Flash limits affect every future animation decision. |
| Low vision (partial sight) | **Medium–High** | Charts/visualizations in therapy data transfer, font scaling, color contrast. Hanna covers environmental light, not physiological impairment. AC-07 (high-contrast) has no persona justification yet. |
| Blindness / screen reader | **High (post-v1 design)** | Screen reader paths for semantic labels (AC-09a MVP, AC-08 Phase 2). "If no blind persona exists, flows won't consider screen reader paths." Text output alongside visualizations already planned. |
| Color blindness | **Medium** | Data visualizations use color. Mitigation is usually covered by contrast + non-color redundancy. Does not create a sufficiently distinct user journey from low vision persona. |
| Hearing impairment | **Not relevant** | No audio output. Voice input is optional, not required. |
| Cognitive impairment | **Already covered** | Max (cognitive overwhelm), Sophie (Simple Mode), David. Not a gap. |
| Keyboard / switch access | **Phase 2 only** | AC-10 is 1.0.0. No immediate persona gap for MVP. |

---

## Question 2 — Does each category warrant a new persona?

### Photosensitive epilepsy

**Warrants a persona.** The constraint directly changes how FLOW-003 is authored (flash rate limit on animated QR sequence). It will affect every future animation or transition decision.

**Constraint persona classification**: A person with photosensitive epilepsy uses pen-and-paper for mood journaling IDENTICALLY to any other user. Their defining characteristic IS the medical constraint, not a different user journey. → **Constraint persona — no scenario needed.**

### Low vision + screen reader

**Warrants a persona.** Currently:
- No persona drives the high-contrast mode requirement (AC-07)
- No persona drives screen reader path requirements (AC-08, AC-09a)
- Hanna covers poor-lighting contrast, not physiological visual impairment
- The goal explicitly states: "If no persona is blind, the flow will not consider screen reader paths"

**Type classification**: A partially-sighted or low-vision person's daily digital life IS meaningfully different — they use their phone with magnification, large text settings, high-contrast OS themes, and may rely partially on VoiceOver/TalkBack. For mood journaling, their as-is differs: paper feels easier because it's infinitely scalable; most apps break their accessibility settings. These are genuine pain points that differ from other personas and generate specific design constraints.

Per the guideline "when uncertain: default to regular" → **Regular persona — scenario needed.**

**Scope note on blindness vs. low vision**: The goal says "full screen reader support is post-v1." A low-vision persona (partial sight) covers both contrast/scaling (v1) AND the foundation for screen reader paths (post-v1) without overpromising. Creating a fully blind persona would imply complete screen reader optimization is in scope now — which contradicts the product decision. Low vision is the right scope.

### Color blindness

**Does not warrant a separate persona.** The constraints (color is decorative, not the sole information carrier; contrast ratios) are already addressed by the low-vision persona and WCAG AA requirements. Creating a separate color blindness persona would duplicate these constraints without adding a meaningfully different user journey.

---

## Question 3 — Does each persona need scenarios?

| Persona | Scenario needed? | Reason |
|---|---|---|
| Photosensitive epilepsy (constraint) | **No** | As-is behavior (pen-paper journaling) is identical to non-impaired users. No meaningful difference in user journey. |
| Low vision (regular) | **Yes** | As-is digital life is different: avoids apps that break their accessibility settings, has adapted journaling strategies (paper preferred, large print). Scenario in category `capture.routine` — how they currently manage mood tracking with their accessibility constraints. |

---

## Question 4 — How should the app_provider persona be updated?

The current app_provider section "Accessibility as Core Value" (line ~202) is:
> "The app must be usable by everyone — including users with visual impairments (screenreader), motor disabilities, or cognitive limitations. Accessibility is not a 'nice to have'..."

This is philosophically correct but **not specific enough** to drive flow authoring decisions. It doesn't distinguish:
- What is committed to in v1
- What is deferred to post-v1
- The specific WCAG standard for animated elements (2.3.1, ≤3Hz)

**Required update**: Add a release-scoped commitment table to the accessibility section:

| v1 (0.0.5 / 1.0.0) | Post-v1 |
|---|---|
| WCAG AA contrast (4.5:1 text, 3:1 UI) | Full TalkBack/VoiceOver optimization (AC-08) |
| 48dp touch targets (AC-01) | High-contrast theme variant (AC-07) |
| Basic semantic labels — every element labeled (AC-09a) | Advanced semantic descriptions (AC-09b) |
| Text scaling to 200% without overflow (AC-11) | Switch/keyboard focus navigation (AC-10) |
| Reduce Motion system setting respected (AC-12) | |
| WCAG 2.3.1: animated elements ≤3Hz flash rate | |

The flash rate rule (WCAG 2.3.1) must be explicit — it directly constrains the animated QR code design and any future animation feature.

---

## Decision Summary

| Action | Artifact | Type | ID |
|---|---|---|---|
| Create | Photosensitive epilepsy persona | Constraint persona | PERSONA-018 |
| Create | Low vision persona | Regular persona (scenario needed) | PERSONA-019 |
| Update | app_provider | Add accessibility commitment with release scope | PERSONA-015 |

---

## Names

Following the naming convention (real first names, not diagnostic labels):
- PERSONA-018: **Felix** — photosensitive epilepsy client
- PERSONA-019: **Rahel** — low-vision self-user (uses the app independently without a therapist; this role matches better given that severe accessibility barriers often mean therapy access is also compromised)

Name conflict check: No existing persona named Felix or Rahel in the system.
