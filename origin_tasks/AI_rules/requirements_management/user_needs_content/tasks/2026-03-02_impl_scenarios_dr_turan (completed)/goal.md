---
task_id: TASK-PROC-027-31
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-10
effort: M
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for Dr. med. Turan (PERSONA-012, Psychiater) — consolidated from 5 to 4 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 4 New Scenarios for Dr. med. Turan (PERSONA-012)

## Objective

Write 5 new scenario artifacts for the existing persona Dr. med. Turan (`dr_med_turan`, PERSONA-012, Psychiater). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/dr_med_turan/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Unused Emergency Plan | `intervention.safety` | Patient doesn't call during medication crisis — safety card is lost, unread, or misunderstood |
| 2 | The Blind Colleague Handover | `management.share_externally` | MVZ colleague covers for absent psychiatrist with no access to patient tracking data |
| 3 | The Frankenstein Protocol | `modification.collaborative` | Psychiatrist's medication protocol + psychotherapist's mood protocol for the same patient — two providers, two data silos, no view of the full picture |
| 4 | The MDK Audit | `management.share_externally` | Health insurance (MDK) audit requires medication compliance documentation — PDF export under bureaucratic pressure |

## Consolidation Notes

**Absorbed into The Frankenstein Protocol (scenario #3):**
- *The Somatic Blind Spot* — why generic apps fail at blood pressure and tremor tracking. This is the clinical manifestation of the Frankenstein Protocol problem. In Act 2, include: Dr. Turan opens the patient's generic health app and finds mood data completely separated from vitals — the somatic and psychological data live in different silos with no correlation view. Derived need: single-screen view of somatic + psychological variables for medical users.

Cross-reference: The Unused Emergency Plan matches SCENARIO_INDEX idea "Dr. Turan's patient doesn't call during medication crisis" (HIGH priority). Mark `status: accepted` when writing.

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/dr_med_turan/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 4 scenario files written and saved to the Dr. med. Turan persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Dr. med. Turan scenarios
