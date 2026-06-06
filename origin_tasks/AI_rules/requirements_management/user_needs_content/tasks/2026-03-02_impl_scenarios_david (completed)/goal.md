---
task_id: TASK-PROC-027-26
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-03
effort: L
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Write scenario artifacts for David (PERSONA-008, ADHS Self-User) — consolidated from 11 to 7 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Write 7 New Scenarios for David (PERSONA-008)

## Objective

Write 11 new scenario artifacts for the existing persona David (`david_structure_seeker`, PERSONA-008, ADHS Self-User). These scenarios were identified by Gemini as gaps in coverage and accepted in TASK-PROC-027-20.

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/david_structure_seeker/`

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Endless Template Hunt | `sharing.independent_discovery` | Self-user ADHD onboarding: searching for the perfect 3-in-1 tool, never committing |
| 2 | The 3-Second Window | `capture.spontaneous` | Working memory evaporates in the 3 seconds it takes to open any app — why lockscreen notes win |
| 3 | The 3-Day Hyperfocus | `capture.routine` | Dopamine-driven tracking burst followed by predictable abandonment on day 4 |
| 4 | "Did I take my meds?" | `analysis.self_reflect` | Passive read-only quick access — David wants to check, not write |
| 5 | The Toxic Streak | `management.destruction` | The streak mechanic becomes the destruction trigger: shame-deleting entries to hide gaps |
| 6 | Consulting the Dopamine Menu | `intervention.coping` | Low-dopamine afternoon: self-user needs curated alternatives to doomscrolling |
| 7 | The Data Dump at First Consult | `management.share_externally` | David arrives at a psychiatrist for the first time with months of self-tracked data — no clinical format |

## Consolidation Notes

**Merged into The 3-Second Window (scenario #2):**
- *The 3-Second Friction* + *The Native Notes Success* — both describe the same problem from slightly different angles (ADHD working memory failing at app launch). Combined: David's thought evaporates in the 3 seconds to open any app, which is exactly why his lockscreen notes win. One scenario, two sides of the same coin.

**Absorbed into The 3-Day Hyperfocus (scenario #3):**
- *The Invisible Alarm* — notification blindness is a symptom of dopamine decay, not a separate scenario. Include in Act 2: "By day 4, David has unconsciously muted the app's reminders — they've joined the grey mass of notifications he swipes away without reading." Derived need: non-notification re-engagement mechanisms.

**Declined — convert to design rules:**
- *The Widget Lifeline* — describes a solution (home screen widget), not a status-quo problem. No analog equivalent exists. Add as a derived need in The 3-Day Hyperfocus: "the tracking tool must maintain visibility without requiring the user to remember it exists."
- *The Infinite Tweaking Loop* — describes an ADHD behavioral trap that doesn't surface a unique design requirement beyond a general UX principle. Capture as a T1 rule in `doc/presentation/design/`: "Customization options must have a hard ceiling — infinite tweaking must not be possible."

## Reference Documents

- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing persona: `requirements_user_needs/personas/david_structure_seeker/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skill

Invoke `ux-create-scenario` for each scenario.

## Acceptance Criteria

- [ ] All 7 scenario files written and saved to the David persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to reflect new coverage
- [ ] No overlap with existing David scenarios
