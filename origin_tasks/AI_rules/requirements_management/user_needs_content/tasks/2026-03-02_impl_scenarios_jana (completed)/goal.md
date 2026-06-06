---
task_id: TASK-PROC-027-23
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
scope_description: "Write scenario artifacts for Jana (PERSONA-014, Borderline & Trauma) — consolidated from 5 to 4 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 4 New Scenarios for Jana (PERSONA-014)

## Objective

Write 5 new scenario artifacts for the existing persona Jana (`jana_high_strung`, PERSONA-014, Borderline & Trauma). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/jana_high_strung/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Blind Panic Skill Search | `intervention.coping` | Tunnel-vision UX during BPD emotional cascade: finding the right DBT skill card |
| 2 | The Black Book Explosion | `capture.spontaneous` | BPD data silos: mood entries scattered across 5+ media, none complete |
| 3 | The Harm Reduction Dilemma | `capture.spontaneous` | Addiction cluster: how to track a "partial success" when binary pass/fail fails |
| 4 | Tracking the Void | `capture.routine` | Trauma cluster: capturing dissociation — how do you document what you weren't conscious for? |

## Consolidation Notes

**Absorbed into The Blind Panic Skill Search:**
- *The Freeze Lockdown* — muscle freeze vs. swipe gestures (a11y). Same crisis context and persona. In Act 2 of The Blind Panic Skill Search, include: once Jana locates the correct skill card, her hands are rigid (hypertonus from panic) and she cannot execute the fine-motor interaction required. Derived need: gross-motor swipe gestures must substitute for precision tapping during crisis states.

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/jana_high_strung/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 4 scenario files written and saved to the Jana persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Jana scenarios
