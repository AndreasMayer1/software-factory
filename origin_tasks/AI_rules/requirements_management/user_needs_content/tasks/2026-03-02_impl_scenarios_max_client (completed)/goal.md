---
task_id: TASK-PROC-027-21
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-02
effort: M
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for Max (PERSONA-002, Schwere Depression) — consolidated from 5 to 3 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 3 New Scenarios for Max (PERSONA-002)

## Objective

Write 5 new scenario artifacts for the existing persona Max (`max_client`, PERSONA-002, Schwere Depression). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/max_client/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Bed-Gravity Paradox | `intervention.coping` | Zero-energy access to coping resources in severe depression |
| 2 | The BDI-2 Fog | `management.share_externally` | Completing standard clinical questionnaires (BDI-2) at the GP visit |
| 3 | The Friction of Help | `intervention.safety` | Finding emergency contact information during cognitive impairment |

## Consolidation Notes

**Absorbed into existing SCEN-002-05 (routine_data_entry):**
- *The Tiny Checkbox Defeat* — medication-induced tremor making checkboxes unusable. Add as an accessibility variant section in Act 2 of the existing routine_data_entry scenario. Derived need: chunky / fat-finger UI with large tap targets.

**Declined — convert to design rule:**
- *The Cheerful Mockery* — describes a feature anti-pattern (condescending push notifications), not a status-quo problem with analog tools. Violates the status-quo rule. Capture as a T1 design rule in `doc/presentation/design/`: "Push notifications must never be condescending or imply the user has failed."

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/max_client/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 3 scenario files written and saved to the Max persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Max scenarios
