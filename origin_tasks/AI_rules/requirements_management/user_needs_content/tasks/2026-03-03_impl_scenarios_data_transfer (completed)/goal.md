---
task_id: TASK-PROC-027-36
type: impl
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-DEP
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-03
effort: M
created: 2026-03-03
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: >
  Write the 4 planned scenarios across TASK-PROC-027-30 and TASK-PROC-027-31
  that are directly relevant to REQ-FUNC-007 (data transfer) — covering both
  the therapist→client plan distribution direction and the client→therapist
  data return direction. All other scenarios in those tasks remain for later.
requirements_version:
  commit: 853d87b
  file: ../requirements.md
---

# Goal: Write Data Transfer Scenarios (REQ-FUNC-007 Coverage)

## Objective

Write 4 scenario artifacts — a focused subset of the scenarios planned in
TASK-PROC-027-30 and TASK-PROC-027-31 — that are directly relevant to the
digital data transfer feature (REQ-FUNC-007). These scenarios ground the
upcoming user flow work (TASK-PROC-027-14, TASK-PROC-027-15) and the UI
spec and implementation task creation work (TASK-FUNC-007-03) in concrete
therapist-side pain points.

**Note**: This task does NOT replace TASK-PROC-027-30 or TASK-PROC-027-31.
Those tasks remain intact and should still be run later. The AI running
those tasks should skip scenarios that have already been written here
(it will recognize this from SCENARIO_INDEX.md coverage).

## Why These 4

All other planned scenarios in tasks 28-35 are about data capture, self-
reflection, archiving, or template sharing — categories unrelated to the
handover of plans and tracked data between therapist and client. Only these
4 directly surface pain points in the **transfer flow**:

| Direction | What it shows |
|-----------|--------------|
| T→C (plan distribution) | What happens when the therapist needs to re-distribute an updated plan in session — the analog pain that motivates a frictionless digital update flow |
| C→T (data return) | What happens when the therapist needs complete, retrospective access to client tracking data — impossible with paper, enabled by digital |
| C→T (multi-provider) | What happens when two providers share the same client but hold separate data silos — motivates unified digital data model |
| C→T (data accessibility) | What happens when the covering colleague has no access to patient data — motivates portable, accessible digital patient records |

---

## Scenarios to Write

| # | Source Task | Persona | Title | Category | Direction |
|---|-------------|---------|-------|----------|-----------|
| 1 | TASK-PROC-027-30 | Dr. Sarah (PERSONA-001) | The Mid-Session Protocol Pivot | `modification.collaborative` | T→C + C→T |
| 2 | TASK-PROC-027-30 | Dr. Sarah (PERSONA-001) | Forensic Pattern Hunting | `analysis.review_collaboratively` | C→T |
| 3 | TASK-PROC-027-31 | Dr. med. Turan (PERSONA-012) | The Blind Colleague Handover | `management.share_externally` | C→T |
| 4 | TASK-PROC-027-31 | Dr. med. Turan (PERSONA-012) | The Frankenstein Protocol | `modification.collaborative` | C→T (multi-provider) |

---

## Scenario Descriptions

### Scenario 1 — The Mid-Session Protocol Pivot (Dr. Sarah)

**Key theme**: On-the-fly protocol adjustment when a pattern emerges mid-session.

Dr. Sarah spots an unexpected pattern in the client's paper entries during
session review — for example, all the bad days cluster around Tuesday
afternoons. She and the client decide in the moment to add a "context" column
to the protocol. Currently: she handwrites the change on the paper form and
sends the client home with an annotated sheet. The client must now manually
mirror those changes on their own copy (if they have one) or work from a
paper with margin scribbles.

**Relevance to data transfer**:
- T→C: Updated plan must reach the client reliably after collaborative
  modification. Today, the modified paper is the only copy — if it's lost,
  the change is gone. A digital update-and-re-send flow would fix this.
- C→T: The pattern was only findable because Dr. Sarah held all the paper in
  her hands at once. With digital data, the system could flag the pattern
  before session — or the therapist could search for it without manually
  scanning rows.

**Source**: TASK-PROC-027-30, Scenario #2 (The Mid-Session Protocol Pivot).

---

### Scenario 2 — Forensic Pattern Hunting (Dr. Sarah)

**Key theme**: Searching weeks of data for the pre-relapse inflection point
before a patient deteriorates.

Dr. Sarah realizes during a crisis session that the relapse must have been
building for 2-3 weeks. She needs to go back through the tracking data to
find the inflection point — when mood first started dropping, which
situations preceded it, what events coincided. With paper protocols, she
must manually leaf through a folder of A4 sheets, squinting at pencil
entries for rows from 6 weeks ago. She might miss it entirely.

**Relevance to data transfer**:
- C→T: If tracking data were digital and transferred to the therapist's
  device after each session (or continuously), forensic retrospective
  analysis would take seconds instead of 20 minutes of manual scanning.
  This directly motivates the need for reliable, complete, structured
  C→T data transfer as a core feature — not just convenience.

**Source**: TASK-PROC-027-30, Scenario #7 (Forensic Pattern Hunting).

---

### Scenario 3 — The Blind Colleague Handover (Dr. med. Turan)

**Key theme**: MVZ colleague covers for an absent psychiatrist with no
access to the patient's tracking data.

Dr. Turan is ill. His colleague Dr. Müller covers his afternoon appointments.
Herr Berger arrives for his 4-week SSRI follow-up. Dr. Müller has no access
to Herr Berger's 4 weeks of mood-medication tracking data: it's on paper in
Turan's locked cabinet, or in a practice management system Dr. Müller doesn't
have credentials for. Dr. Müller must make a dose decision based on verbal
self-report alone. Herr Berger understates his side effects (he doesn't want
to worry the unfamiliar doctor).

**Relevance to data transfer**:
- C→T: If tracking data were digitally accessible by any authorized provider
  (not locked in a single paper file), the covering colleague would have the
  same clinical picture as the primary therapist. The scenario motivates
  secure, provider-accessible digital data storage — which is downstream from
  the client-to-therapist transfer flow.

**Source**: TASK-PROC-027-31, Scenario #2 (The Blind Colleague Handover).

---

### Scenario 4 — The Frankenstein Protocol (Dr. med. Turan)

**Key theme**: Psychiatrist's medication protocol and psychotherapist's mood
protocol for the same patient — two providers, two data silos, no unified view.

Herr Berger has both Dr. Turan (psychiatrist, medication monitoring) and
Frau Dr. Köhler (psychotherapist, CBT) as providers. Dr. Turan tracks
medication + side effects; Frau Dr. Köhler tracks mood + cognition. Neither
sees the other's data. Dr. Turan opens the patient's general health app
(used alongside both paper protocols) and finds mood data completely siloed
from medication data — no correlation view. He has to mentally stitch the
picture together from printouts, verbal summaries, and guesswork.

**Relevance to data transfer**:
- C→T (multi-provider): The patient's data flows TO each provider separately
  with no shared format or protocol. A standardized digital transfer mechanism
  (e.g., the app's plan format + secure data structure) would allow different
  providers to share a unified data model for the same client, even if they
  each view separate sections.
- T→C: Each provider sends their own plan to the client independently — two
  separate T→C flows with no coordination. The scenario motivates a
  multi-provider-aware transfer architecture.

**Source**: TASK-PROC-027-31, Scenario #3 (The Frankenstein Protocol).

---

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Personas:
  - `requirements_user_needs/personas/dr_sarah/`
  - `requirements_user_needs/personas/dr_med_turan/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`
- Data transfer requirements (read for context when writing):
  - `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/requirements.md`
  - `requirements_tasks/functional/shared/epic_data_transfer/feat_plan_receiving/requirements.md`

## Skill

Invoke `ux-create-scenario` for each scenario (one invocation per scenario).

## Acceptance Criteria

- [ ] All 4 scenario files written and saved to the respective persona folders
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated: new instances added for all 4 scenarios
- [ ] No overlap with existing Dr. Sarah or Dr. Turan scenarios
