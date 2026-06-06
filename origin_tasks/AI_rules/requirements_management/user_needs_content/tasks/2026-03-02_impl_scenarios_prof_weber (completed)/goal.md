---
task_id: TASK-PROC-027-32
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
scope_description: "Write scenario artifacts for Prof. Dr. Weber (PERSONA-011, Psychoanalyse) — consolidated from 5 to 4 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 4 New Scenarios for Prof. Dr. Weber (PERSONA-011)

## Objective

Write 5 new scenario artifacts for the existing persona Prof. Dr. Weber (`prof_dr_weber`, PERSONA-011, Psychoanalyse). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/prof_dr_weber/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Obergutachter Report | `analysis.therapist_solo` | Motif search across 300 sessions — seeking recurring themes, not counting numbers |
| 2 | The 300-Session Archive | `management.archive` | Local-first, air-gapped storage: 4+ years of patient data per patient, all on paper |
| 3 | The Intrusive Quantifier | `modification.collaborative` | Fending off pie charts in the psychoanalytic frame: the tool's visualizations threaten the therapy approach |
| 4 | The Wordless Weight | `capture.spontaneous` | Body maps for pre-verbal states — patients who cannot name their emotions but can point to where it hurts |

## Consolidation Notes

**Declined — convert to non-functional requirement:**
- *The Login Rupture* — IT problems disrupting therapeutic silence is a general usability concern, not a scenario-specific insight. Doesn't surface a design requirement beyond "don't crash during sessions." Add as a non-functional reliability requirement: "The app must not require login or authentication during an active session view."

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/prof_dr_weber/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 4 scenario files written and saved to the Prof. Dr. Weber persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Prof. Dr. Weber scenarios
