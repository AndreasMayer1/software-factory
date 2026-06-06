---
task_id: TASK-PROC-027-22
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-03
effort: M
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for Sophie (PERSONA-010, ADHS) — consolidated from 4 to 3 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 3 New Scenarios for Sophie (PERSONA-010)

## Objective

Write 4 new scenario artifacts for the existing persona Sophie (`sophie_structure_seeker`, PERSONA-010, ADHS). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/sophie_structure_seeker/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Missing Blue Pen | `capture.routine` | ADHD executive collapse at first-time tracking setup — the onboarding barrier |
| 2 | The Typo Catastrophe | `management.destruction` | OCD-perfectionism cluster: visual imperfection triggers complete data destruction |
| 3 | The Bathtub Disaster | `management.preservation` | Hardware loss + serverless backup paradox: 3 months of medication-correlation data drowned |

## Consolidation Notes

**Absorbed into The Missing Blue Pen:**
- *The Time Blindness Blackout* — ADHD time blindness causing missing timestamps. This is a friction point within the setup story, not a separate scenario. In Act 2 of The Missing Blue Pen, include Sophie discovering she cannot retroactively timestamp entries because she has no memory of *when* things happened. Derived need: automatic timestamping — no manual time entry required.

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/sophie_structure_seeker/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 3 scenario files written and saved to the Sophie persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Sophie scenarios
