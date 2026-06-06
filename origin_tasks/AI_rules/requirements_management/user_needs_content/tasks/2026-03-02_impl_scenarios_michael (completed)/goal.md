---
task_id: TASK-PROC-027-28
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-08
effort: M
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for Michael (PERSONA-006, Biohacker & Burnout) — consolidated from 5 to 4 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 4 New Scenarios for Michael (PERSONA-006)

## Objective

Write 5 new scenario artifacts for the existing persona Michael (`michael_high_performer`, PERSONA-006, Biohacker & Burnout). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/michael_high_performer/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Missing Link | `capture.routine` | Garmin Body Battery vs. board meeting: wearable data and mood tracking in separate silos |
| 2 | The MDM Paranoia | `management.preservation` | Corporate MDM security blocks app installation; work phone unusable, personal phone too visible |
| 3 | Rationalizing the Crash | `analysis.self_reflect` | Ignoring tinnitus and warning signs without an external threshold to override self-deception |
| 4 | Stealth Capture in the Boardroom | `capture.spontaneous` | Tracking in a corporate meeting where the phone screen is visible to colleagues |

## Consolidation Notes

**Declined — convert to persona note:**
- *A/B Testing the Wrong Variable* — describes a biohacker behavioral trap (optimizing supplements instead of addressing stress) that is interesting but doesn't surface a design requirement beyond a general UX principle. Add as a behavioral anti-pattern note in Michael's `persona.md` under "Failure Modes / Self-Sabotage Patterns."

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/michael_high_performer/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 4 scenario files written and saved to the Michael persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Michael scenarios
