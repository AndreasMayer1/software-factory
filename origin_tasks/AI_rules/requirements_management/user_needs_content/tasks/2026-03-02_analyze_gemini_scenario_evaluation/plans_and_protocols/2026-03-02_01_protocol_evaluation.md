# Protocol: Gemini Scenario & Persona Evaluation

**Task**: TASK-PROC-027-20
**Date**: 2026-03-02
**Status**: Completed

---

## Summary

Gemini was asked to identify missing scenarios across all existing personas in the mood tracker app. The suggestions were reviewed interactively with the user. Deduplication was performed by Gemini before review. All suggestions were accepted.

| Metric | Count |
|---|---|
| Total suggestions reviewed | 77 |
| Accepted | 77 |
| Rejected | 0 |
| Deferred | 0 |
| New personas proposed | 1 (Amina, PERSONA-016) |
| Follow-up tasks created | 13 |

---

## Decisions by Persona Group

### Group 1: Therapy Clients (Existing Personas)

#### Max (PERSONA-002 / max_client / Schwere Depression) — 5 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Bed-Gravity Paradox | `intervention.coping` | ACCEPTED | Real barrier for severe depression; zero-energy access is a genuine gap |
| 2 | The BDI-2 Fog | `management.share_externally` | ACCEPTED | Standard GP questionnaire workflow not yet covered |
| 3 | The Cheerful Mockery | `UX/Passive` | ACCEPTED | Toxic push notification UX is distinct from existing notification scenarios |
| 4 | The Friction of Help | `intervention.safety` | ACCEPTED | Emergency services barrier is safety-critical and uncovered |
| 5 | The Tiny Checkbox Defeat | `capture.routine` | ACCEPTED | Medication-induced tremor + chunky UI is an a11y gap for this persona |

#### Sophie (PERSONA-010 / sophie_structure_seeker / ADHS) — 4 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Time Blindness Blackout | `capture.routine` | ACCEPTED | Automatic timestamps are a specific ADHD requirement not yet documented |
| 2 | The Missing Blue Pen | `capture.routine` | ACCEPTED | Executive collapse at setup is a real onboarding barrier for ADHD users |
| 3 | The Typo Catastrophe | `management.destruction` | ACCEPTED | OCD cluster + visual noise as a destruction trigger is a gap |
| 4 | The Bathtub Disaster | `management.preservation` | ACCEPTED | Hardware loss + serverless backup paradox for ADHD users is uncovered |

#### Jana (PERSONA-014 / jana_high_strung / Borderline & Trauma) — 5 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Blind Panic Skill Search | `intervention.coping` | ACCEPTED | Tunnel vision UX in crisis state is a genuine gap for Borderline persona |
| 2 | The Black Book Explosion | `capture.spontaneous` | ACCEPTED | Data silos and shadow records are a real risk not yet addressed |
| 3 | The Harm Reduction Dilemma | `capture.spontaneous` | ACCEPTED | Addiction cluster + partial success capture is uncovered |
| 4 | Tracking the Void | `capture.routine` | ACCEPTED | Dissociation/blank film capturing is a trauma-specific gap |
| 5 | The Freeze Lockdown | `capture.spontaneous` | ACCEPTED | Muscle freeze vs swipe gestures is an a11y gap for trauma states |

#### Lena (PERSONA-015 / lena_depth_seeker / Trauer & Tiefenpsychologie) — 5 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Ephemeral Voice | `capture.spontaneous` | ACCEPTED | Audio-to-text vs vulnerability hangover is a grief-specific capture gap |
| 2 | The Continuing Bonds Protocol | `capture.routine` | ACCEPTED | Anti-metrics (letters into the void) is a unique requirement for grief work |
| 3 | The Weight of the Archive | `management.archive` | ACCEPTED | Horcrux dilemma for old grief data is uncovered |
| 4 | The Daylight Flashback | `modification.autonomous` | ACCEPTED | Delayed dream fragment entry is a gap for depth psychology users |
| 5 | The Poisoned Metaphor | `analysis.self_reflect` | ACCEPTED | When metrics corrupt the narrative is a deep design concern |

#### Elias (PERSONA-009 / elias_skeptical_guardian / Soziale Phobie & Paranoia) — 3 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Shoulder-Surfer Paralysis | `capture.in_the_moment` | ACCEPTED | Stealth UX on public transport is a real barrier for social phobia |
| 2 | The Notebook Breach | `capture.spontaneous` | ACCEPTED | Over-sharing fear as a barrier to capture is not yet documented |
| 3 | The Panic Delete | `management.destruction` | ACCEPTED | Emergency exit with therapist recovery path is a safety gap |

---

### Group 2: Self-Users (Existing Personas)

#### David (PERSONA-008 / david_structure_seeker / ADHS Self-User) — 11 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Endless Template Hunt | `sharing.independent_discovery` | ACCEPTED | 3-in-1 tool search is a self-user onboarding gap |
| 2 | The 3-Second Friction | `capture.spontaneous` | ACCEPTED | Working memory fails at app start is a critical ADHD UX gap |
| 3 | The Native Notes Success | `capture.spontaneous` | ACCEPTED | Lockscreen notes winning over app is a design lesson not yet captured |
| 4 | The 3-Day Hyperfocus | `capture.routine` | ACCEPTED | Dopamine crash on day 4 explains routine abandonment |
| 5 | "Did I take my meds?" | `analysis.self_reflect` | ACCEPTED | Passive read-only quick access is a medication management gap |
| 6 | The Toxic Streak | `management.destruction` | ACCEPTED | Shame-deletion on gaps is a motivational design problem |
| 7 | The Widget Lifeline | `UX/Passive` | ACCEPTED | Object permanence on home screen is an ADHD retention mechanism |
| 8 | Consulting the Dopamine Menu | `intervention.coping` | ACCEPTED | Alternatives to doomscrolling as coping tool is uncovered |
| 9 | The Data Dump at First Consult | `management.share_externally` | ACCEPTED | Arriving at the psychiatrist with data is a critical handoff scenario |
| 10 | The Infinite Tweaking Loop | `modification.autonomous` | ACCEPTED | Procrastination through plan design is an ADHD-specific trap |
| 11 | The Invisible Alarm | `capture.routine` | ACCEPTED | Notification blindness is distinct from existing reminder scenarios |

#### Lisa (PERSONA-005 / lisa_waitlist_bridger / Diagnostik-Wüste) — 6 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Ratgeber Template Trap | `creation.prepare` | ACCEPTED | Templates without psychoeducation is a gap for undiagnosed users |
| 2 | The Proof of Suffering | `management.share_externally` | ACCEPTED | 3-minute GP report generation is a real access-to-care scenario |
| 3 | The 116 117 Hustle | `capture.spontaneous` | ACCEPTED | Tracking while navigating system strain is uncovered |
| 4 | The Accountability Void | `capture.routine` | ACCEPTED | Tracking dies without feedback loop is a retention insight |
| 5 | The Hormonal Blind Spot | `analysis.self_reflect` | ACCEPTED | PMDS / custom tags vs stigma is a gap for this persona |
| 6 | The "Faking it" Dilemma | `analysis.self_reflect` | ACCEPTED | Masking vs inner exhaustion is a diagnostic-journey-specific gap |

#### Michael (PERSONA-006 / michael_high_performer / Biohacker & Burnout) — 5 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Missing Link | `capture.routine` | ACCEPTED | Garmin body battery vs board meeting integration is uncovered |
| 2 | The MDM Paranoia | `management.preservation` | ACCEPTED | Employer security blocks download is a real barrier for this persona |
| 3 | Rationalizing the Crash | `analysis.self_reflect` | ACCEPTED | Ignoring tinnitus without external threshold warning is a safety gap |
| 4 | A/B Testing the Wrong Variable | `creation.prepare` | ACCEPTED | Optimizing macros instead of stress is a biohacker-specific trap |
| 5 | Stealth Capture in the Boardroom | `capture.spontaneous` | ACCEPTED | Stealth UI for executives is a distinct professional context |

#### Nina (PERSONA-013 / nina_energy_budgeter / CFS & Pacing) — 8 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Energy Cost of Tracking | `capture.routine` | ACCEPTED | Zero-friction on crash day is the core CFS design challenge |
| 2 | The 72-Hour PEM Lag | `analysis.self_reflect` | ACCEPTED | Delayed trigger search is a unique analytical need for PEM |
| 3 | The Wearable Gaslighting | `capture.spontaneous` | ACCEPTED | Subjective experience overriding smartwatch data is uncovered |
| 4 | The Quantified Cancellation | `management.share_externally` | ACCEPTED | Data as emotional boundary support is a novel use case |
| 5 | The Silent Exertion Trap | `capture.spontaneous` | ACCEPTED | Separating cognitive vs physical load is a CFS-specific gap |
| 6 | The Variable Avalanche | `modification.autonomous` | ACCEPTED | Death by tracking overload is a pacing-specific design risk |
| 7 | The "Your Labs Are Normal" Encounter | `management.share_externally` | ACCEPTED | PDF burden of proof at specialist is a CFS advocacy scenario |
| 8 | The Migraine Squint | `capture.spontaneous` | ACCEPTED | Visual accessibility in low-light is an a11y gap for this persona |

---

### Group 3: Therapists (Existing Personas)

#### Dr. Sarah (PERSONA-001 / dr_sarah / Strukturierte VT Therapeutin) — 9 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Friday Night Gutachten | `analysis.therapist_solo` | ACCEPTED | 15-week data aggregation is a documentation workflow gap |
| 2 | The Mid-Session Protocol Pivot | `modification.collaborative` | ACCEPTED | On-the-fly adjustments in session are uncovered |
| 3 | The Intervision Wheel-Reinvention | `sharing.peer_exchange` | ACCEPTED | Isolated templates among colleagues is a sharing gap |
| 4 | The 10-Year Safe Squeeze | `management.archive` | ACCEPTED | Archiving nightmare after therapy end is a compliance gap |
| 5 | The Copy-Paste Routine | `workflow.documentation` | ACCEPTED | 10-minute PVS interface pain is a documentation efficiency gap |
| 6 | The Excel-Nightmare | `analysis.therapist_solo` | ACCEPTED | PiA cluster: graphs for supervision is a training-context gap |
| 7 | Forensic Pattern Hunting | `analysis.review_collaboratively` | ACCEPTED | Escalation search before relapse is a safety-critical gap |
| 8 | The Discharge Folder | `management.share_externally` | ACCEPTED | Handover to self-user autonomy is a transition scenario |
| 9 | The Decade Lifespan | `management.preservation` | ACCEPTED | Secure hardware migration without cloud is a compliance need |

#### Dr. med. Turan (PERSONA-012 / dr_med_turan / Psychiater) — 5 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Unused Emergency Plan | `intervention.safety` | ACCEPTED | Failure of analog safety net is a safety-critical gap |
| 2 | The Blind Colleague Handover | `management.share_externally` | ACCEPTED | Information gap in MVZ is a real handover problem |
| 3 | The Frankenstein Protocol | `modification.collaborative` | ACCEPTED | Interdisciplinary data clash with psychotherapists is uncovered |
| 4 | The Somatic Blind Spot | `analysis.review_collaboratively` | ACCEPTED | Why generic apps fail at blood pressure & tremor is a clinical gap |
| 5 | The MDK Audit | `management.share_externally` | ACCEPTED | Health insurance shield via PDF export is a compliance scenario |

#### Prof. Dr. Weber (PERSONA-011 / prof_dr_weber / Psychoanalyse) — 5 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Obergutachter Report | `analysis.therapist_solo` | ACCEPTED | Motif search instead of number crunching is a depth-therapy gap |
| 2 | The 300-Session Archive | `management.archive` | ACCEPTED | Local-first & air-gapped storage for long-term analysis is uncovered |
| 3 | The Intrusive Quantifier | `modification.collaborative` | ACCEPTED | Fending off pie charts in therapy frame is a design philosophy gap |
| 4 | The Wordless Weight | `capture.spontaneous` | ACCEPTED | Body maps for pre-verbal states is an a11y and clinical gap |
| 5 | The Login Rupture | `analysis.review_collaboratively` | ACCEPTED | When IT problems destroy therapeutic silence is a reliability gap |

---

### Group 4: New Persona

#### Amina (PERSONA-016 — NEW) — 6 scenarios

| # | Scenario Title | Category Tag | Decision | Reasoning |
|---|---|---|---|---|
| 1 | The Translation Tax | `capture.routine` | ACCEPTED | UI language vs export language is a localization gap not covered elsewhere |
| 2 | The Physical Disguise | `capture.spontaneous` | ACCEPTED | Somatization as entry point is a cultural-clinical gap |
| 3 | The Danger of the Analog Record | `management.destruction` | ACCEPTED | Patriarchal risk at home is a safety gap unique to this persona type |
| 4 | The Self-Care Guilt | `capture.routine` | ACCEPTED | Western therapy bias vs collective obligations is uncovered |
| 5 | The Unlisted Resource | `intervention.coping` | ACCEPTED | Faith/religion as custom coping skill is a gap for non-Western users |
| 6 | Defending the Data | `analysis.review_collaboratively` | ACCEPTED | Self-censorship under therapist bias is a trust/safety gap |

**New persona decision**: Amina fills a genuine gap. No existing persona represents the intersection of cultural shame, patriarchal safety risk, somatization, and dual-language therapy context. PERSONA-016 is warranted.

---

## Follow-Up Tasks Created

| Task ID | Folder | Persona | Scenario Count |
|---|---|---|---|
| TASK-PROC-027-21 | `2026-03-02_impl_scenarios_max_client` | Max (PERSONA-002) | 5 → **3** |
| TASK-PROC-027-22 | `2026-03-02_impl_scenarios_sophie` | Sophie (PERSONA-010) | 4 → **3** |
| TASK-PROC-027-23 | `2026-03-02_impl_scenarios_jana` | Jana (PERSONA-014) | 5 → **4** |
| TASK-PROC-027-24 | `2026-03-02_impl_scenarios_lena` | Lena (PERSONA-015) | 5 → **4** |
| TASK-PROC-027-25 | `2026-03-02_impl_scenarios_elias` | Elias (PERSONA-009) | 3 → **3** |
| TASK-PROC-027-26 | `2026-03-02_impl_scenarios_david` | David (PERSONA-008) | 11 → **7** |
| TASK-PROC-027-27 | `2026-03-02_impl_scenarios_lisa` | Lisa (PERSONA-005) | 6 → **5** |
| TASK-PROC-027-28 | `2026-03-02_impl_scenarios_michael` | Michael (PERSONA-006) | 5 → **4** |
| TASK-PROC-027-29 | `2026-03-02_impl_scenarios_nina` | Nina (PERSONA-013) | 8 → **6** |
| TASK-PROC-027-30 | `2026-03-02_impl_scenarios_dr_sarah` | Dr. Sarah (PERSONA-001) | 9 → **7** |
| TASK-PROC-027-31 | `2026-03-02_impl_scenarios_dr_turan` | Dr. med. Turan (PERSONA-012) | 5 → **4** |
| TASK-PROC-027-32 | `2026-03-02_impl_scenarios_prof_weber` | Prof. Dr. Weber (PERSONA-011) | 5 → **4** |
| TASK-PROC-027-33 | `2026-03-02_impl_create_amina_persona` | Amina (PERSONA-016, NEW) | 6 → **5** + persona creation |

**Total (original)**: 77 new scenario artifacts to be written across 13 tasks.

**Total (after consolidation)**: 59 standalone scenarios across 13 tasks.

---

## Consolidation Addendum

**Date**: 2026-03-02
**Analysis**: `plans_and_protocols/2026-03-02_02_opus_consolidation_analysis.md`
**Result**: 77 → 59 standalone scenarios (23% reduction)

After accepting all 77 Gemini suggestions, an Opus-model consolidation pass was applied to remove redundant, feature-describing, or thin scenarios without losing any unique design requirements.

### Reduction Summary

| Action | Count | Effect |
|---|---|---|
| Kept as standalone | ~51 | Direct transfer to goal.md |
| Merged pairs (2→1) | 6 pairs | 12 suggestions → 6 combined scenarios |
| Absorbed as variant/derived need | 5 | Folded into adjacent scenario |
| Declined → design rule/note | 7 | Insight preserved outside scenario format |

### Declined Items — Insight Destinations

| Declined | Insight | Destination |
|---|---|---|
| Max: The Cheerful Mockery | Push notifications must not be condescending | `doc/presentation/design/t1_notification_tone.md` |
| Lena: The Poisoned Metaphor | Metrics must not override narrative | `doc/presentation/design/t1_metrics_narrative_separation.md` |
| David: The Widget Lifeline | Tracking must stay visible without the user remembering it | Derived need in TASK-PROC-027-26 (The 3-Day Hyperfocus) |
| David: The Infinite Tweaking Loop | Customization must have a hard ceiling | `doc/presentation/design/t1_customization_ceiling.md` |
| Michael: A/B Testing the Wrong Variable | Biohacker self-deception via optimization | Note in `requirements_user_needs/personas/michael_high_performer/persona.md` |
| Dr. Sarah: The Discharge Folder | Structured self-user transition export needed | TASK-PROC-027-34 (`2026-03-02_explore_therapy_end_flow`) |
| Prof. Weber: The Login Rupture | App must not require re-auth during active session | TASK-PROC-027-35 (`2026-03-02_impl_nfr_session_continuity`) |

### Deferred Requirement Notes

**Dr. Sarah: The Discharge Folder** — Transition export for end-of-therapy handover to patient self-management. Currently therapy ends and the patient simply keeps their paper stack. A digital app needs an equivalent: a structured "end-of-therapy package" (summary, skill cards, self-care plan, data export in accessible format) given to the patient. This is a feature need, not a status-quo problem — therefore declined as a scenario. However it is a real requirement. Tracked as: **TASK-PROC-027-34** (`2026-03-02_explore_therapy_end_flow`).

**Prof. Weber: The Login Rupture** — During psychoanalytic sessions, therapeutic silence is a clinical tool. An app requiring re-authentication (session timeout, biometric re-prompt) mid-session destroys that silence. This is a general reliability / UX requirement, not a persona-specific scenario. Tracked as: **TASK-PROC-027-35** (`2026-03-02_impl_nfr_session_continuity`) — to formally document NFR-SESSION-001 in requirements.md with configurable timeout values and role-based defaults.
