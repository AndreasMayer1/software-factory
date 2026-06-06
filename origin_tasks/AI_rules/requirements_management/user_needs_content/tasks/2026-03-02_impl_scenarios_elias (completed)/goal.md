---
task_id: TASK-PROC-027-25
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-03
effort: S
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for Elias (PERSONA-009, Soziale Phobie & Paranoia) based on Gemini gap analysis"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 3 New Scenarios for Elias (PERSONA-009)

## Objective

Write 3 new scenario artifacts for the existing persona Elias (`elias_skeptical_guardian`, PERSONA-009, Soziale Phobie & Paranoia). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/elias_skeptical_guardian/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Shoulder-Surfer Paralysis | `capture.in_the_moment` | Stealth UX on public transport |
| 2 | The Notebook Breach | `capture.spontaneous` | Over-sharing fear and boundaries |
| 3 | The Panic Delete | `management.destruction` | Emergency exit with therapist recovery |

## Consolidation Notes

All 3 scenarios retained as standalone. No merges or absorptions.

Cross-references to existing SCENARIO_INDEX ideas (mark these as `status: accepted` when writing):
- The Shoulder-Surfer Paralysis matches idea: "Commute capture under social pressure" (medium priority)
- The Panic Delete matches idea: "Elias panic-deletes everything after partner finds app" (medium priority)

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/elias_skeptical_guardian/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 3 scenario files written and saved to the Elias persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Elias scenarios
