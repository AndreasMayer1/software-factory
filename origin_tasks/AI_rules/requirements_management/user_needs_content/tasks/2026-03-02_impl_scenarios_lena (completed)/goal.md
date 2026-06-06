---
task_id: TASK-PROC-027-24
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
scope_description: "Write scenario artifacts for Lena (PERSONA-015, Trauer & Tiefenpsychologie) — consolidated from 5 to 4 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 4 New Scenarios for Lena (PERSONA-015)

## Objective

Write 5 new scenario artifacts for the existing persona Lena (`lena_depth_seeker`, PERSONA-015, Trauer & Tiefenpsychologie). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/lena_depth_seeker/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Ephemeral Voice | `capture.spontaneous` | Audio-to-text capture in grief: wanting to record while crying but regretting the rawness later |
| 2 | The Continuing Bonds Protocol | `capture.routine` | Anti-metrics tracking: "letters to the dead" as a modality with no numerical score |
| 3 | The Weight of the Archive | `management.archive` | The Horcrux dilemma: old grief data that cannot be deleted (last trace) but hurts to keep |
| 4 | The Daylight Flashback | `modification.autonomous` | Dream fragments arriving 8 hours later: retroactive entry with original timestamp |

## Consolidation Notes

**Declined — convert to design principle:**
- *The Poisoned Metaphor* — a philosophical concern (metrics corrupting narrative therapy) rather than a concrete status-quo problem. Overlaps with Prof. Weber's "Intrusive Quantifier" from the therapist side. Capture as a T1 design rule in `doc/presentation/design/`: "Numeric metrics must never be surfaced in a way that overrides or reframes a user's own narrative entry."

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/lena_depth_seeker/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 4 scenario files written and saved to the Lena persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Lena scenarios
