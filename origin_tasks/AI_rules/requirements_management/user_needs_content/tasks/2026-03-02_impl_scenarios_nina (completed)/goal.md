---
task_id: TASK-PROC-027-29
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-09
effort: M
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for Nina (PERSONA-013, CFS & Pacing) — consolidated from 8 to 6 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 6 New Scenarios for Nina (PERSONA-013)

## Objective

Write 8 new scenario artifacts for the existing persona Nina (`nina_energy_budgeter`, PERSONA-013, CFS & Pacing). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/nina_energy_budgeter/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Energy Cost of Tracking | `capture.routine` | The act of tracking itself costs energy Nina doesn't have on crash days |
| 2 | The 72-Hour PEM Lag | `analysis.self_reflect` | The crash happens 72 hours after the trigger — retroactive correlation and offset analysis |
| 3 | The Wearable Gaslighting | `capture.spontaneous` | Smartwatch says "recovered" when Nina feels destroyed — subjective truth must override objective data |
| 4 | The Quantified Cancellation | `management.share_externally` | Using tracked data as emotional boundary support: "I'm not lazy, look at my numbers" |
| 5 | The Variable Avalanche | `modification.autonomous` | Death by tracking overload: CFS tracking requires so many variables that tracking itself becomes overwhelming |
| 6 | The "Your Labs Are Normal" Encounter | `management.share_externally` | PDF burden of proof at the specialist: making invisible illness legible to a skeptical clinician |

## Consolidation Notes

**Absorbed into The Energy Cost of Tracking (scenario #1):**
- *The Silent Exertion Trap* — cognitive vs. physical load distinction. In Act 2 of The Energy Cost of Tracking, include: "Nina's worst days are the days she spent 'just' thinking — no steps, no movement, but 4 hours of tax paperwork that triggers a 2-day crash. The tracker shows a 'rest day' because it only measures physical exertion." Derived need: cognitive load as a trackable variable alongside physical exertion.
- *The Migraine Squint* — visual accessibility in low-light (a11y). Add as a derived need in The Energy Cost of Tracking: "On migraine days, the screen itself becomes an enemy — Nina needs a capture mode that works with minimal brightness and maximum contrast." Derived need: high-contrast low-brightness mode for acute symptom capture.

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/nina_energy_budgeter/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 6 scenario files written and saved to the Nina persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Nina scenarios
