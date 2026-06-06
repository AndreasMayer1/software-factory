---
task_id: TASK-PROC-027-27
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
scope_description: "Write scenario artifacts for Lisa (PERSONA-005, Diagnostik-Wüste) — consolidated from 6 to 5 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 5 New Scenarios for Lisa (PERSONA-005)

## Objective

Write 6 new scenario artifacts for the existing persona Lisa (`lisa_waitlist_bridger`, PERSONA-005, Diagnostik-Wüste). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/lisa_waitlist_bridger/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Ratgeber Template Trap | `creation.prepare` | Templates from self-help books that don't fit a real diagnostic situation |
| 2 | The Proof of Suffering | `management.share_externally` | Using self-tracked data to prove severity at the GP and to navigate the system (combines "116 117 Hustle") |
| 3 | The Accountability Void | `capture.routine` | Tracking dies without a feedback loop — no therapist means no external motivation |
| 4 | The Hormonal Blind Spot | `analysis.self_reflect` | PMDS / custom tags vs. medical stigma — tracking a cyclical pattern the system dismisses |
| 5 | The "Faking it" Dilemma | `analysis.self_reflect` | Masking vs. inner exhaustion: social performance of wellness contradicts tracked data |

## Consolidation Notes

**Merged into The Proof of Suffering (scenario #2):**
- *The 116 117 Hustle* — both describe Lisa navigating the medical system with her tracking data. The 116 117 call (finding a therapist slot) and the GP visit (proving severity) are two acts of the same story. In The Proof of Suffering, Act 2 should include Lisa's phone call to 116 117 and her attempt to use her tracked data to accelerate triage. Combined derived needs: quick clinical summary, system-navigation log.

Cross-reference: The Proof of Suffering matches the existing SCENARIO_INDEX idea "Lisa shows mood data to GP as proof" (HIGH priority). Mark `status: accepted` when writing.

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/lisa_waitlist_bridger/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 5 scenario files written and saved to the Lisa persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Lisa scenarios
