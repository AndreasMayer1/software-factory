---
task_id: TASK-PROC-027-33
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-BACKLOG
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-03-04
effort: L
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04]
scope_description: "Create PERSONA-016 Amina (The Dual-World Navigator) with 5 scenario artifacts — consolidated from 6 to 5 standalone scenarios"
requirements_version:
  commit: e938267
  file: ../requirements.md
---

# Goal: Create New Persona Amina (PERSONA-016) with 5 Scenarios

## Objective

Create a new persona Amina (The Dual-World Navigator / Die Grenzgängerin) as PERSONA-016, then write 6 scenario artifacts for her. Amina was proposed by Gemini as a genuine gap in the existing persona set and accepted in TASK-PROC-027-20.

Amina represents a user type not covered by any existing persona: the intersection of cultural shame around mental health, patriarchal safety risk, somatization of psychological distress, and dual-language therapy context (mother tongue vs. German professional context).

## Source

- Evaluation task: TASK-PROC-027-20 (`2026-03-02_analyze_gemini_scenario_evaluation/`)
- Gemini gap analysis: `2026-03-02_analyze_gemini_scenario_evaluation/gemini_suggestions.md`
- Evaluation protocol: `2026-03-02_analyze_gemini_scenario_evaluation/plans_and_protocols/2026-03-02_01_protocol_evaluation.md`

## Target Location

`requirements_user_needs/personas/amina/` (new folder to be created)

## Persona Specification

**ID**: PERSONA-016
**Name**: Amina
**Archetype**: The Dual-World Navigator / Die Grenzgängerin
**Role**: Therapy client (self-user with therapeutic guidance)
**Diagnosis**: Mild-to-moderate depression, often presenting somatized (headaches, fatigue, stomach pain)

**Background**:
- Young woman (~25 years old)
- Lives with a conservative or patriarchal family or is embedded in a tight cultural community
- Speaks fluent German but thinks and feels in her mother tongue (Arabic, Turkish, or Farsi)
- Therapy is conducted in German, but her inner emotional world is coded in another language
- Mental health is a taboo in her community — framed as weakness, family shame, or spiritual failure

**Key Persona Clusters**:
- **Somatization**: Presents psychological distress as physical symptoms; finds body-based entry points more acceptable than direct emotional language
- **Low-Literacy/Bureaucracy-Fatigue**: Navigates German health system with limited support; exhausted by forms, referrals, and jargon
- **High-Obligation/Caregiver**: Her own needs are subordinated to family obligations; self-care is culturally framed as selfish

**Core UI Requirements derived from this persona**:
- UI input language must be decoupled from export/report language (she inputs in German or mother tongue; therapist export must be in clinical German)
- Somatic entry point: body map or symptom-first capture mode (not "how do you feel?" but "where does it hurt?")
- Critical privacy: app icon must be camouflage-capable (looks like a calendar or notes app); stealth mode with instant screen-blank gesture

## Scenarios to Write

| # | Title | Category Tag | Key Theme |
|---|---|---|---|
| 1 | The Double Translation | `capture.routine` | UI language vs. export language AND Western therapy bias vs. collective obligations — two translation layers in one story |
| 2 | The Physical Disguise | `capture.spontaneous` | Somatization as entry point: tracking "migraine" when the real problem is family conflict |
| 3 | The Danger of the Analog Record | `management.destruction` | Patriarchal safety risk at home: written records must not exist — higher severity than Elias's privacy concern |
| 4 | The Unlisted Resource | `intervention.coping` | Faith/religion as a coping skill — not on any standard DBT skill list |
| 5 | Defending the Data | `analysis.review_collaboratively` | Self-censorship under therapist bias: Amina edits entries before showing them, anticipating cultural misunderstanding |

## Consolidation Notes

**Merged into The Double Translation (scenario #1):**
- *The Translation Tax* + *The Self-Care Guilt* — both describe the same fundamental conflict: Western therapy frameworks don't fit Amina's cultural reality. The linguistic translation struggle (Turkish/Arabic feelings → German clinical jargon) and the cultural translation struggle (therapist says "take a bath", Amina must cook for 8 people) are Act 1 and Act 2 of one story. Combined name: "The Double Translation."

## Reference Documents

- Persona writing standards: `requirements_user_needs/README_3_PERSONA_DEFINITION.md`
- Scenario writing standards: `requirements_user_needs/README_4_SCENARIO_DEFINITION.md`
- Existing personas (for format reference): `requirements_user_needs/personas/`
- Scenario index: `requirements_user_needs/SCENARIO_INDEX.md`

## Skills

- Use `ux-create-persona` to create the Amina persona file
- Use `ux-create-scenario` for each of the 6 scenarios

## Acceptance Criteria

- [ ] New persona folder `requirements_user_needs/personas/amina/` created
- [ ] Amina persona file written following `README_3_PERSONA_DEFINITION.md` format
- [ ] Amina assigned PERSONA-016
- [ ] All 5 scenario files written and saved to the Amina persona folder
- [ ] Each scenario follows the format defined in `README_4_SCENARIO_DEFINITION.md`
- [ ] SCENARIO_INDEX.md updated to include Amina and her 6 scenarios
- [ ] Persona index (if it exists) updated to include PERSONA-016

## Notes

- Amina fills a genuine gap: no existing persona covers the intersection of somatization, cultural taboo around mental health, patriarchal household safety risk, and dual-language cognition
- The "Translation Tax" scenario is particularly important — it reveals a hard technical requirement (input language != export language) that affects the data model
- The "Danger of the Analog Record" scenario surfaces a safety requirement that has direct UX implications (no persistent local plaintext, instant wipe gesture)
- Consider how Amina's scenarios might interact with Elias's privacy scenarios — they share a stealth UX need, but for different reasons (paranoia/social phobia vs. physical safety)
