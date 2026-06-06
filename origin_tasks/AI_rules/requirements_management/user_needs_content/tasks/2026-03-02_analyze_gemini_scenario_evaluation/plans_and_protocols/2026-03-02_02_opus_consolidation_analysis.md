# Opus Analysis: Scenario Consolidation — Can We Reduce 77 Without Losing Information?

**Task**: TASK-PROC-027-20 (addendum)
**Date**: 2026-03-02
**Model**: claude-opus-4-6

---

## Executive Summary

**Yes, we can reduce meaningfully.** The 77 suggestions contain genuine value, but Gemini was operating in "brainstorm mode" — generating ideas per persona without enforcing the project's own quality bar. When we apply the project's existing scenario standards (three-act narrative, status-quo only, ~200-300 lines, derived needs, failure modes), many of the 77 items are **ideas, not scenarios**. Some are duplicates in disguise, some are too thin to justify a standalone scenario, and some can be absorbed into richer combined scenarios.

**Proposed reduction: 77 → ~45 standalone scenarios + ~12 items absorbed as variants/notes into other scenarios.**

The remaining ~20 items should be **declined or deferred** — either because they don't surface unique design requirements, overlap with existing scenarios, or describe features rather than status-quo problems.

---

## Analysis Framework

### What makes a scenario worth writing at full depth?

Based on the existing gold-standard scenarios (SCEN-002-01, SCEN-002-05), a scenario earns its existence when it:

1. **Surfaces a unique design requirement** that no other scenario reveals
2. **Has a distinct physical/emotional context** (different trigger, environment, constraints)
3. **Tells a story that changes how we think about the product** — not just confirms what we already know
4. **Cannot be reduced to a paragraph within another scenario** without losing critical information

### What should NOT be a standalone scenario?

- A scenario that differs from another only by persona (same story, different name)
- A scenario that describes a **feature need** rather than a **status-quo problem** (e.g., "Widget Lifeline" is a solution, not a problem)
- A scenario whose unique design requirement is already covered by another scenario in the same persona
- A scenario that is really a **failure mode** of an existing scenario (belongs in that scenario's Failure Modes section)

---

## Consolidation Recommendations by Persona

### Max (PERSONA-002) — 5 suggested → 3 standalone + 1 absorbed + 1 declined

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Bed-Gravity Paradox | **KEEP** | Unique context: zero-energy coping access. Distinct from capture scenarios — this is about *reading* resources, not *recording*. Surfaces the "horizontal UX" requirement. |
| The BDI-2 Fog | **KEEP** | Unique context: structured medical questionnaire at GP visit. Surfaces export-format requirements (standard clinical instruments). |
| The Cheerful Mockery | **DECLINE** | This describes a *feature anti-pattern* (bad notifications), not a status-quo problem with paper/analog tracking. Max doesn't currently receive push notifications from his paper notebook. Violates the status-quo rule. Convert to a design rule in `doc/presentation/` instead. |
| The Friction of Help | **KEEP** | Safety-critical. Unique: finding emergency numbers during crisis under cognitive impairment. Status-quo problem with paper safety cards. |
| The Tiny Checkbox Defeat | **ABSORB into routine_data_entry** | The tremor is a *variant* of the existing routine data entry scenario — same context (kitchen table, paper protocol), same task (filling in columns), different physical constraint. Add as a dedicated "Accessibility Variant" section to SCEN-002-05 rather than creating a near-duplicate scenario. The design requirement (chunky UI) can be stated in 2 paragraphs. |

### Sophie (PERSONA-010) — 4 suggested → 3 standalone + 1 absorbed

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Time Blindness Blackout | **ABSORB into existing capture.routine gap** | Time blindness affecting routine entries is a variant of the routine entry scenario, not a standalone. Sophie's object permanence failure is already documented in her prepare_for_session scenario. Fold into a single "Sophie's Routine Entry" scenario that includes the timestamp problem as a key friction point. |
| The Missing Blue Pen | **KEEP** | Unique context: ADHD executive collapse at first-time setup. This is an *onboarding* scenario, distinct from routine use. Surfaces "zero-setup" requirement. |
| The Typo Catastrophe | **KEEP** | Genuinely novel: the OCD-perfectionism cluster where visual imperfection triggers destruction. Not covered elsewhere. |
| The Bathtub Disaster | **KEEP** | Hardware loss + serverless backup paradox. Critical for local-first architecture. |

### Jana (PERSONA-014) — 5 suggested → 4 standalone + 1 absorbed

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Blind Panic Skill Search | **KEEP** | Critical intervention scenario. Tunnel-vision UX during BPD crisis. Surfaces "1-tap skill access" requirement. Matches existing SCENARIO_INDEX idea "Jana in BPD crisis at home alone" (intervention.coping, HIGH priority). |
| The Black Book Explosion | **KEEP** | Data silos / shadow records. Unique problem: BPD users track in 5+ places simultaneously. Surfaces "import/consolidation" requirement. |
| The Harm Reduction Dilemma | **KEEP** | Addiction cluster. Genuinely novel: tracking partial success when the binary "did you / didn't you" model fails. |
| Tracking the Void | **KEEP** | Dissociation capture. Truly unique: how do you track something you weren't conscious for? Surfaces "retrospective gap-fill" and "time-hole" UI patterns. |
| The Freeze Lockdown | **ABSORB as a11y variant of Blind Panic Skill Search** | Same crisis context as the panic skill search, same persona, same emotional state — just focused on the motor impairment aspect. Combine: the panic skill search scenario should include an Act 2 section on "even if she finds the right skill, her hands can't execute the interaction." The design requirement (gross-motor gestures) fits naturally as a derived need of that scenario. |

### Lena (PERSONA-015) — 5 suggested → 4 standalone + 1 declined

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Ephemeral Voice | **KEEP** | Audio capture in grief context. Unique: the "vulnerability hangover" — wanting to capture while crying but regretting the rawness later. Surfaces "ephemeral vs. permanent" recording mode. |
| The Continuing Bonds Protocol | **KEEP** | Anti-metrics tracking. Genuinely novel: "letters to the dead" as a tracking modality that has no numerical score. Surfaces "unstructured freeform capture" requirement distinct from standard mood tracking. |
| The Weight of the Archive | **KEEP** | Long-term grief data management. Unique: the emotional weight of old data that can't be deleted (because it's the last trace of a relationship) but hurts to keep. Surfaces "archive with care" UX pattern. |
| The Daylight Flashback | **KEEP** | Delayed dream fragments. Unique temporal pattern: the insight arrives 8 hours after the dream. Surfaces "retroactive entry with original timestamp" requirement. |
| The Poisoned Metaphor | **DECLINE** | This describes a philosophical concern (metrics corrupting narrative therapy) rather than a concrete status-quo problem. Prof. Weber's "Intrusive Quantifier" already covers the tension between quantification and depth therapy from the therapist side. Converting this to a design principle ("metrics must not override narrative") is more useful than a full scenario. |

### Elias (PERSONA-009) — 3 suggested → 3 standalone

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Shoulder-Surfer Paralysis | **KEEP** | Public-space capture under surveillance anxiety. Matches existing SCENARIO_INDEX idea "Commute capture under social pressure" (medium priority). Elias is the natural anchor persona. |
| The Notebook Breach | **KEEP** | Over-sharing fear as capture barrier. Distinct from privacy-from-others: this is about Elias censoring *himself* because the medium might be seen. Surfaces "content-level privacy" (not just device-level). |
| The Panic Delete | **KEEP** | Emergency data destruction. Matches existing SCENARIO_INDEX idea "Elias panic-deletes everything after partner finds app" (medium priority). Safety-critical. |

### David (PERSONA-008) — 11 suggested → 7 standalone + 2 merged + 2 declined

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Endless Template Hunt | **KEEP** | Matches existing SCENARIO_INDEX idea for sharing.independent_discovery. Self-user onboarding gap. |
| The 3-Second Friction | **MERGE with The Native Notes Success** | Both describe the same problem (ADHD working memory fails at app startup) from slightly different angles. Combine into one scenario: "The 3-Second Window" — David's thought evaporates during the 3 seconds it takes to open any app, which is why his lockscreen notes win. One scenario surfaces both requirements (instant capture, lockscreen integration). |
| The Native Notes Success | **MERGE with above** | See above. |
| The 3-Day Hyperfocus | **KEEP** | Dopamine-driven routine abandonment. Genuinely novel: the scenario isn't about *starting* tracking (covered by template hunt) but about the predictable *decay* at day 4. Surfaces "anti-streak / gentle re-engagement" requirement. |
| "Did I take my meds?" | **KEEP** | Passive read-only quick access. Unique interaction pattern: David doesn't want to *write* anything, he wants to *check* if he already did something. Surfaces "read-only dashboard" requirement. |
| The Toxic Streak | **KEEP** | Shame-deletion on gaps. Genuinely novel: the streak mechanic itself becomes the trigger for destruction. Surfaces "never show streaks" design rule. |
| The Widget Lifeline | **DECLINE** | Describes a solution (home screen widget), not a status-quo problem. There is no analog equivalent of "object permanence on home screen" in the paper world. Violates status-quo rule. Convert to a derived need in another David scenario (e.g., add to "3-Day Hyperfocus" derived needs: "the tracking tool must maintain visibility without requiring the user to remember it exists"). |
| Consulting the Dopamine Menu | **KEEP** | Coping resource access for self-users. Distinct from Jana's crisis skill search: David isn't in acute crisis, he's in a "low dopamine afternoon" looking for alternatives to doomscrolling. Different emotional register, different urgency level. |
| The Data Dump at First Consult | **KEEP** | Self-user→professional handoff. Critical transition scenario: David has been tracking alone and now arrives at a psychiatrist for the first time. Surfaces "clinical export for self-tracked data" requirement. |
| The Infinite Tweaking Loop | **DECLINE** | This describes an ADHD behavioral pattern (procrastination via plan redesign) but doesn't surface a *design requirement* that isn't already covered. The requirement "don't let users endlessly customize" is a general UX principle, not a scenario-specific insight. Better as a design rule. |
| The Invisible Alarm | **ABSORB into The 3-Day Hyperfocus** | Notification blindness is a *symptom* of the dopamine decay described in 3-Day Hyperfocus, not a separate scenario. The hyperfocus scenario should include: "By day 4, David has unconsciously muted the app's reminders — they've joined the grey mass of notifications he swipes away without reading." The design requirement (non-notification re-engagement) belongs in that scenario's derived needs. |

### Lisa (PERSONA-005) — 6 suggested → 5 standalone + 1 merged

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Ratgeber Template Trap | **KEEP** | Matches existing SCENARIO_INDEX idea for sharing.independent_discovery. Lisa's version of template discovery. |
| The Proof of Suffering | **KEEP** | Matches existing SCENARIO_INDEX idea "Lisa shows mood data to GP as proof" (HIGH priority). Critical access-to-care scenario. |
| The 116 117 Hustle | **MERGE with The Proof of Suffering** | Both describe Lisa navigating the medical system with her tracking data. The 116 117 call (finding a therapist slot) and the GP visit (proving severity) are two acts of the same story: "Lisa uses her self-tracked data to fight for care." One combined scenario surfaces both requirements (quick summary for GP, system-navigation log). |
| The Accountability Void | **KEEP** | Tracking dies without feedback loop. Unique to self-users: no therapist to review data = no external motivation. Surfaces "self-generated insight feedback" requirement. |
| The Hormonal Blind Spot | **KEEP** | PMDS / custom tags vs stigma. Genuinely novel: tracking a cyclical pattern that the medical system systematically dismisses. Surfaces "custom variable creation" and "cycle overlay" requirements. |
| The "Faking it" Dilemma | **KEEP** | Masking vs. inner exhaustion. Unique: the social performance of wellness that contradicts the tracked data. Surfaces "discrepancy detection" between reported mood and behavioral indicators. |

### Michael (PERSONA-006) — 5 suggested → 4 standalone + 1 declined

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Missing Link | **KEEP** | Wearable data vs. mood tracking correlation. Matches existing SCENARIO_INDEX idea for Nina/Michael. Surfaces "external data import" requirement. |
| The MDM Paranoia | **KEEP** | Employer security blocks download. Genuinely novel professional context: corporate MDM (Mobile Device Management) prevents app installation on work phone, and Michael doesn't want a "therapy app" on the personal phone visible to colleagues during screen sharing. |
| Rationalizing the Crash | **KEEP** | Ignoring warning signs without external threshold. Unique: the high-performer's self-deception pattern where data exists but is rationalized away. Surfaces "escalation alert" requirement. |
| A/B Testing the Wrong Variable | **DECLINE** | Describes a biohacker behavioral trap (optimizing supplements instead of addressing stress) that is interesting but doesn't surface a design requirement beyond "don't enable avoidance." This is a therapy insight, not a product requirement. Better as a note in Michael's persona file. |
| Stealth Capture in the Boardroom | **KEEP** | Professional stealth UX. Unique context: tracking in a corporate meeting where the phone is visible to colleagues. Surfaces "plausible-deniability UI mode" requirement (app looks like a productivity tool). |

### Nina (PERSONA-013) — 8 suggested → 5 standalone + 2 merged + 1 declined

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Energy Cost of Tracking | **KEEP** | Core CFS design challenge. Unique: the act of tracking itself *costs* energy that Nina doesn't have. Surfaces "sub-30-second entry" and "energy cost accounting" requirements. |
| The 72-Hour PEM Lag | **KEEP** | Delayed trigger analysis. Genuinely novel temporal pattern: the crash happens 72 hours after the trigger. Surfaces "retroactive correlation" and "offset analysis" requirements. |
| The Wearable Gaslighting | **MERGE with The Missing Link (Michael)** or keep separate | Both involve wearable data contradicting subjective experience. Nina's version has a unique twist: her smartwatch says "recovered" when she feels destroyed. The emotional stakes are higher (medical gaslighting parallel). **KEEP as separate** — the design requirement is different. Michael wants correlation; Nina needs to *override* the wearable with subjective truth. Surfaces "subjective > objective" principle. |
| The Quantified Cancellation | **KEEP** | Data as emotional boundary support. Genuinely novel: using tracked data to justify cancelling plans ("I'm not lazy, look at my numbers"). Surfaces "shareable summary for social proof" requirement. |
| The Silent Exertion Trap | **MERGE with The Energy Cost of Tracking** | Both describe the challenge of tracking energy expenditure. The distinction (cognitive vs. physical load) is important but is a facet of the energy tracking scenario, not a separate story. Add as a key friction point: "Nina's worst days are the days she spent 'just' thinking — no steps, no movement, but 4 hours of tax paperwork that triggers a 2-day crash. The tracker shows a 'rest day' because it only measures physical exertion." |
| The Variable Avalanche | **KEEP** | Death by tracking overload. Self-referential meta-scenario: CFS tracking requires *so many* variables that the tracking itself becomes overwhelming. Surfaces "smart defaults" and "variable suggestion limits" requirements. |
| The "Your Labs Are Normal" Encounter | **MERGE with The Quantified Cancellation** or keep separate | Both involve Nina presenting data to skeptics. But different contexts: specialist vs. social circle. **KEEP as separate** — the medical authority dynamic is distinct from the social boundary dynamic, and the PDF export requirements (clinical formatting) differ from the social sharing requirements (emotional, visual). |
| The Migraine Squint | **DECLINE as standalone** | The accessibility requirement (high contrast, low-light mode) is real but doesn't need a full 200-line scenario. **ABSORB into The Energy Cost of Tracking** as an accessibility variant: "On migraine days, the screen itself becomes an enemy. Nina needs a capture mode that works with minimal brightness and maximum contrast." Add as a derived need. |

### Dr. Sarah (PERSONA-001) — 9 suggested → 6 standalone + 2 merged + 1 declined

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Friday Night Gutachten | **KEEP** | Matches existing SCENARIO_INDEX idea "Therapist solo analysis for insurance report" (HIGH priority). Critical documentation workflow. |
| The Mid-Session Protocol Pivot | **KEEP** | Live protocol modification during session. Matches existing SCENARIO_INDEX idea for modification.collaborative. |
| The Intervision Wheel-Reinvention | **KEEP** | Template sharing among colleagues. Unique: the isolation of therapists who each reinvent the same tracking wheel. Surfaces "template marketplace / sharing" requirement. |
| The 10-Year Safe Squeeze | **MERGE with The Decade Lifespan** | Both describe the same core problem: long-term data archiving for legal compliance (§630f SGB V, 10-year retention). The Squeeze is about the *archiving moment* (therapy ends, data must be preserved); the Lifespan is about *hardware migration* during the 10-year period. These are Act 1 and Act 2 of the same story. Combine into one comprehensive scenario: "The 10-Year Burden." |
| The Decade Lifespan | **MERGE with above** | See above. |
| The Copy-Paste Routine | **KEEP** | PVS (Praxisverwaltungssoftware) interface pain. Unique: the 10-minute daily ritual of transcribing session notes from handwritten paper to digital PVS. Surfaces "PVS export/integration" requirement. |
| The Excel-Nightmare | **KEEP** | PiA cluster: building supervision graphs. Unique context: therapist-in-training needs to visualize patient data for supervision but has no tools beyond Excel and manual counting. Surfaces "automated visualization" requirement. |
| Forensic Pattern Hunting | **KEEP** | Pre-relapse escalation search. Safety-critical: therapist suspects a patient is deteriorating and needs to search weeks of data for the inflection point. Surfaces "trend analysis with alerts" requirement. |
| The Discharge Folder | **DECLINE** | The handover-to-self-user transition is important but doesn't describe a *status-quo problem*. Currently, therapy simply ends and the patient keeps their paper stack (or doesn't). The scenario is really about a feature need (structured discharge export). Convert to a requirement note rather than a full scenario. |

### Dr. Turan (PERSONA-012) — 5 suggested → 4 standalone + 1 merged

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Unused Emergency Plan | **KEEP** | Matches existing SCENARIO_INDEX idea "Dr. Turan's patient doesn't call during medication crisis" (HIGH priority). Safety-critical. |
| The Blind Colleague Handover | **KEEP** | Information gap when colleague covers for absent psychiatrist. Unique: the MVZ (Medizinisches Versorgungszentrum) setting where data is siloed per doctor. Surfaces "colleague read-access" requirement. |
| The Frankenstein Protocol | **KEEP** | Interdisciplinary data clash: psychiatrist's medication protocol vs. psychotherapist's mood protocol for the same patient. Unique: two professionals tracking different aspects of the same human, unable to see each other's data. Surfaces "multi-provider data model" requirement. |
| The Somatic Blind Spot | **MERGE with The Frankenstein Protocol** | Both describe the same underlying problem: Dr. Turan can't see the full picture because generic apps separate somatic and psychological tracking. The Somatic Blind Spot (BP + tremor + mood on one screen) is the *clinical manifestation* of the Frankenstein Protocol (two providers, two data silos). Combine: in the Frankenstein Protocol scenario, add an Act 2 section where Turan opens the patient's generic health app and can't find mood data next to the vitals. |
| The MDK Audit | **KEEP** | Insurance compliance via PDF export. Unique bureaucratic context: Medizinischer Dienst der Krankenversicherung audit requires medication compliance documentation. Surfaces "audit-ready export" requirement distinct from the GP/specialist sharing format. |

### Prof. Weber (PERSONA-011) — 5 suggested → 4 standalone + 1 declined

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Obergutachter Report | **KEEP** | Motif search in psychoanalytic data. Unique analytical pattern: searching for recurring themes across 300 sessions, not counting numbers. Surfaces "qualitative search / tagging" requirement. |
| The 300-Session Archive | **KEEP** | Long-term air-gapped storage. Unique: a psychoanalyst with 4+ years of data per patient, all on paper, all local. Surfaces "extreme long-term local storage" requirement. |
| The Intrusive Quantifier | **KEEP** | Fending off quantification in the therapy frame. Genuinely novel: the scenario where the *tool itself* threatens the therapeutic approach by visualizing data in ways that violate psychoanalytic principles. Surfaces "visualization suppression" and "narrative-first mode" requirements. |
| The Wordless Weight | **KEEP** | Body maps for pre-verbal states. Unique: patients who cannot name their emotions but can point to where it hurts. Surfaces "somatic/body-map entry mode" requirement (same cluster as Amina's somatization). |
| The Login Rupture | **DECLINE** | IT problems disrupting therapeutic silence is a general usability concern, not a scenario-specific insight. Every app must minimize interruptions. This doesn't surface a design requirement beyond "don't crash during sessions." Better as a non-functional requirement. |

### Amina (PERSONA-016, NEW) — 6 suggested → 5 standalone + 1 merged

| Scenario | Recommendation | Reasoning |
|---|---|---|
| The Translation Tax | **KEEP** | Core persona-defining scenario. Surfaces the hard technical requirement: input language ≠ export language. |
| The Physical Disguise | **KEEP** | Somatization as entry point. Unique: tracking "migraine" when the real problem is family conflict. Surfaces "somatic-to-psychological bridging" requirement. |
| The Danger of the Analog Record | **KEEP** | Patriarchal safety risk. Unique: data discovery doesn't mean embarrassment (Elias) but physical/social danger. Surfaces "plausible deniability at rest" and "instant evidence destruction" requirements at a higher severity level than Elias's scenarios. |
| The Self-Care Guilt | **MERGE with The Translation Tax** | Both describe the same fundamental conflict: Western therapy frameworks don't fit Amina's cultural reality. The "Self-Care Guilt" (therapist says "take a bath," Amina must cook for 8 people) is a natural Act 2 extension of the Translation Tax scenario — after struggling with the *language* of tracking, she struggles with the *content*. One combined scenario ("The Double Translation") captures both the linguistic and cultural translation layers. |
| The Unlisted Resource | **KEEP** | Faith/religion as coping skill. Genuinely novel: standard DBT skill lists don't include prayer, Quran recitation, or community gathering as coping strategies. Surfaces "custom coping resource" and "non-Western skill library" requirements. |
| Defending the Data | **KEEP** | Self-censorship under therapist bias. Unique: Amina edits her own entries before showing them to the therapist because she anticipates cultural misunderstanding. Surfaces "private vs. shared layers" requirement — the ability to have entries that are visible only to oneself. |

---

## Summary Scorecard

| Category | Original | Keep | Merge (→ combined) | Absorb (into existing) | Decline | Net Standalone |
|---|---|---|---|---|---|---|
| Max | 5 | 3 | 0 | 1 | 1 | 3 |
| Sophie | 4 | 3 | 0 | 1 | 0 | 3 |
| Jana | 5 | 4 | 0 | 1 | 0 | 4 |
| Lena | 5 | 4 | 0 | 0 | 1 | 4 |
| Elias | 3 | 3 | 0 | 0 | 0 | 3 |
| David | 11 | 5 | 2→1 | 1 | 2 | 6 |
| Lisa | 6 | 4 | 2→1 | 0 | 0 | 5 |
| Michael | 5 | 4 | 0 | 0 | 1 | 4 |
| Nina | 8 | 5 | 2→1 | 1 | 0 | 6 |
| Dr. Sarah | 9 | 5 | 2→1 | 0 | 1 | 6 |
| Dr. Turan | 5 | 3 | 2→1 | 0 | 0 | 4 |
| Prof. Weber | 5 | 4 | 0 | 0 | 1 | 4 |
| Amina | 6 | 4 | 2→1 | 0 | 0 | 5 |
| **TOTAL** | **77** | **51** | **12→6** | **5** | **7** | **57** |

**Result: 77 → 57 standalone scenarios** (26% reduction)
- 7 items **declined** (converted to design rules or persona notes)
- 5 items **absorbed** into existing or adjacent scenarios as variants
- 6 merged pairs become 6 combined scenarios (12→6)
- The declined items are NOT lost — their design insights are captured as rules/notes

---

## SCENARIO_INDEX Overlap Check

Several Gemini suggestions **match existing ideas** in the SCENARIO_INDEX ideas section:

| Gemini Suggestion | Existing SCENARIO_INDEX Idea | Status |
|---|---|---|
| Jana: Blind Panic Skill Search | "Jana in BPD crisis at home alone" (HIGH) | Direct match |
| Dr. Turan: Unused Emergency Plan | "Dr. Turan's patient doesn't call" (HIGH) | Direct match |
| Dr. Sarah: Friday Night Gutachten | "Therapist solo analysis for insurance report" (HIGH) | Direct match |
| Elias: Shoulder-Surfer Paralysis | "Commute capture under social pressure" (MEDIUM) | Direct match |
| Elias: Panic Delete | "Elias panic-deletes everything" (MEDIUM) | Direct match |
| Sophie: Bathtub Disaster | "Sophie loses phone with all tracking data" (MEDIUM) | Direct match |
| Lisa: Proof of Suffering | "Lisa shows mood data to GP as proof" (HIGH) | Direct match |
| Lisa: Ratgeber Template Trap | "Lisa discovers tracking template from self-help book" (MEDIUM) | Direct match |
| David: Endless Template Hunt | Same idea as Lisa's, David variant | Partial match |
| Dr. Sarah: Mid-Session Protocol Pivot | "Dr. Sarah iterates protocol after pattern discovery" (MEDIUM) | Direct match |

**10 of 77 suggestions** were already identified as ideas in the SCENARIO_INDEX. This is both good (validates the suggestions) and concerning (Gemini was fed the SCENARIO_INDEX as context and may have been "echoing" rather than discovering genuine new gaps).

---

## Declined Items → Where Their Insights Go

| Declined Item | Insight | Destination |
|---|---|---|
| Max: Cheerful Mockery | "Push notifications must never be condescending" | `doc/presentation/` — notification design rule |
| Lena: Poisoned Metaphor | "Metrics must not override narrative" | `doc/domain/` — data model principle |
| David: Widget Lifeline | "Tracking tool must maintain visibility" | Absorbed as derived need in David: 3-Day Hyperfocus |
| David: Infinite Tweaking Loop | "Don't enable infinite customization" | `doc/presentation/` — UX guardrail rule |
| Michael: A/B Testing Wrong Variable | "Biohacker avoidance via optimization" | Note in Michael's persona.md |
| Dr. Sarah: Discharge Folder | "Structured self-user transition export" | Requirement note in REQ-PROC-027 or a future flow |
| Prof. Weber: Login Rupture | "Zero interruption during sessions" | Non-functional requirement / reliability SLA |

---

## Execution Plan

### What Needs to Happen

1. **Update the 13 existing goal.md files** to reflect the consolidated scenario lists
2. **Update the evaluation protocol** (2026-03-02_01_protocol_evaluation.md) with the consolidation decisions
3. **Update SCENARIO_INDEX ideas section** — mark the 10 matching ideas as "accepted" with Gemini task reference
4. **Create design rule notes** for the 7 declined items (so their insights aren't lost)

### Agent Strategy

**Single agent is sufficient.** The changes are file edits (updating goal.md files and the protocol), not new scenario writing. Estimated effort: 1-2 hours of file editing.

### Order of Operations

1. Get user approval on consolidation decisions
2. Update goal.md files for each persona task (adjust scenario counts and lists)
3. Update evaluation protocol with consolidation addendum
4. (Optional) Update SCENARIO_INDEX ideas section

---

## Quality Criteria

- [ ] Every declined item has its insight captured in a specified destination
- [ ] Every merged pair produces a richer combined scenario, not a watered-down compromise
- [ ] Every absorbed item is traceable to the host scenario
- [ ] Net scenario count matches the summary scorecard (57)
- [ ] No unique design requirement is lost in the reduction

---

## Risks

1. **User attachment to specific titles**: Gemini's evocative names (e.g., "The Wearable Gaslighting") may have emotional resonance for the user. Mitigate: decline decisions are about *format* (standalone vs. absorbed), not about discarding the underlying insight.

2. **Over-consolidation**: Merging too aggressively may lose the distinct emotional texture of individual scenarios. Mitigate: only merge when the physical context and emotional arc are genuinely the same; keep separate when the "feel" differs even if the design requirement overlaps.

3. **Scenario Index drift**: The SCENARIO_INDEX ideas section has overlapping items with the Gemini suggestions. Mitigate: explicitly cross-reference and update statuses.
