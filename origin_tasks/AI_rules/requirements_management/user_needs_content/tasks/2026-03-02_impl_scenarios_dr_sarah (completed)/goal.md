---
task_id: TASK-PROC-027-30
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for Dr. Sarah (PERSONA-001, VT Therapeutin) — consolidated from 9 to 7 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 7 New Scenarios for Dr. Sarah (PERSONA-001)

## Objective

Write 9 new scenario artifacts for the existing persona Dr. Sarah (`dr_sarah`, PERSONA-001, Strukturierte VT Therapeutin). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/dr_sarah/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Friday Night Gutachten | `analysis.therapist_solo` | Aggregating 15 weeks of patient data alone for an insurance report |
| 2 | The Mid-Session Protocol Pivot | `modification.collaborative` | On-the-fly protocol adjustment when a pattern emerges mid-session |
| 3 | The Intervision Wheel-Reinvention | `sharing.peer_exchange` | Every therapist reinvents the same tracking template — no standard exchange mechanism |
| 4 | The 10-Year Burden | `management.archive` + `management.preservation` | Combined: archiving therapy data after end of therapy (legal 10-year retention) AND secure hardware migration during that period without cloud |
| 5 | The Copy-Paste Routine | `workflow.documentation` | 10-minute daily ritual of transcribing session notes from paper to PVS |
| 6 | The Excel-Nightmare | `analysis.therapist_solo` | PiA cluster: building supervision graphs manually in Excel from paper entries |
| 7 | Forensic Pattern Hunting | `analysis.review_collaboratively` | Searching weeks of data for the pre-relapse inflection point before a patient deteriorates |

## Consolidation Notes

**Merged into The 10-Year Burden (scenario #4):**
- *The 10-Year Safe Squeeze* + *The Decade Lifespan* — both describe the same compliance challenge (§630f SGB V, 10-year retention). The Squeeze is the archiving moment (therapy ends, data must be preserved); the Lifespan is hardware migration during those 10 years. Combined as a single two-act story: Act 1 = end-of-therapy archiving decision; Act 2 = 5 years later, new practice PC, no cloud, how to migrate.

**Declined — convert to requirement:**
- *The Discharge Folder* — handover-to-self-user transition doesn't describe a current status-quo problem (therapy simply ends, patient keeps the paper stack). This is a feature need. Add as a requirement note in the parent requirements.md or a future flow task.

Cross-references to SCENARIO_INDEX ideas (mark `status: accepted` when writing):
- Friday Night Gutachten matches "Therapist solo analysis for insurance report" (HIGH priority)
- Mid-Session Protocol Pivot matches "Dr. Sarah iterates protocol after pattern discovery" (medium priority)

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/dr_sarah/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 7 scenario files written and saved to the Dr. Sarah persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing Dr. Sarah scenarios
