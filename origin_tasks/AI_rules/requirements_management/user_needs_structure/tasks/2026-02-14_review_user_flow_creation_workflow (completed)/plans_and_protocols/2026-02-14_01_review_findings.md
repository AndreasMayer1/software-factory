# Review Findings: create-user-flow Skill and READMEs

**Task**: TASK-PROC-010-16
**Date**: 2026-02-21
**Agent**: claude-opus-4-6
**Status**: Review complete (phases 1-3). Awaiting user review before phase 4 (updates).

**Scope**: Retrospective review of the `create-user-flow` skill and associated READMEs based on their first real-world usage in TASK-PROC-027-13 (creating FLOW-002: "Instruct Client on Protocol").

**Method**: Compared TASK-PROC-027-13 protocols, user feedback files (first_iteration.md, second_iteration.md), the created flow (flow.md), and the third-iteration completion log against the skill definition and all 9 governing READMEs.

---

## Summary of Real-World Usage

TASK-PROC-027-13 created FLOW-002, a dual-perspective flow spanning 3 therapist personas and 5 client personas. The task went through:

1. **Pre-skill analysis phase** (not in skill, added via goal.md custom guidance) producing a structured analysis of requirements vs. user needs with 5 explicit user design decisions
2. **First iteration** via create-user-flow skill (new mode) producing initial flow.md
3. **User review** with extensive feedback (first_iteration.md, ~48 feedback points in German)
4. **Second iteration** via create-user-flow skill (continue mode)
5. **User review** with additional feedback (second_iteration.md, 12 feedback points in German)
6. **Third iteration** via create-user-flow skill (continue mode) producing the final draft

The resulting flow is 423 lines with 12 happy path steps across 2 phases, 11 exceptions, adaptive UI rules, a plan template architecture section, 4 documented deviations, and 12 open questions.

---

## Category 1: Skill Workflow Steps

### Issue 1.1: Missing Analysis Phase

- **What happened**: The task's goal.md defined a mandatory pre-creation analysis phase (read all scenarios + requirements, document gaps/tensions/missing needs, get user approval before creating the flow). This phase produced the most valuable artifact of the entire task (2026-02-14_01_analysis_requirements_vs_user_needs.md). Without it, the first flow draft would have been based on incomplete understanding.
- **What the skill says**: Step 1 says "Gather Flow Information" and asks for flow name, approach, and scenarios. Step 3 says "Investigate Existing Requirements" with a brief instruction to list and read relevant requirement files. There is no structured analysis step.
- **Gap**: The skill assumes the agent already understands the domain well enough to write a flow. For complex flows (especially those bridging multiple personas and existing requirements), a structured analysis phase with user review checkpoint is essential. The analysis in TASK-PROC-027-13 identified 4 gaps, 5 tensions, and 6 missing needs that would never have surfaced from a simple "gather info and write" approach.
- **Proposed fix**: Add an optional "Analysis Phase" between Steps 3 and 4 in new mode. The skill should detect when analysis is warranted (multiple personas, existing requirements to reconcile, dual-perspective flows) and offer it. The analysis should follow a structured template: (a) what requirements assume, (b) what scenarios describe, (c) gaps, (d) tensions, (e) missing needs, (f) synthesis recommendations. Include a user review checkpoint before proceeding to flow creation. Make it optional for simple single-scenario flows.
- **Priority**: **High** — This was the single most impactful process element in TASK-PROC-027-13, and it was entirely outside the skill.

### Issue 1.2: Iterative Workflow Not Explicitly Modeled

- **What happened**: The flow required 3 full iterations. The skill has a "continue mode" that technically supports this, but the workflow description implies a single pass: new mode creates the flow, output says "review and provide feedback or approve." The task naturally evolved into a multi-iteration cycle, but the skill doesn't set this expectation.
- **What the skill says**: Step 12 (Output) for new mode says "Next steps: 1. Review happy path and exceptions. 2. Provide feedback or approve." Continue mode exists but is described as a separate invocation path, not as an expected part of the workflow.
- **Gap**: The skill doesn't tell the orchestrating agent (or the user) that multiple iterations are normal and expected. A complex flow like FLOW-002 went through 3 iterations before reaching a usable draft. The skill should normalize this.
- **Proposed fix**: Add a note in the skill's Purpose section or after Step 12: "Complex flows typically require 2-4 iterations. The user provides feedback after each iteration, and the skill is re-invoked in continue mode. This is normal, not a failure." Consider also adding guidance on how to structure feedback files (e.g., numbered points, one concern per bullet) to make continue mode more efficient.
- **Priority**: **Medium** — Continue mode works mechanically, but the expectation-setting is missing.

### Issue 1.3: Step Order for Continue Mode

- **What happened**: In continue mode, the skill says to load context (existing flow + feedback + scenarios + personas + requirements), then proceed to Step 6 (generate/improve with Opus). Steps 7-11 follow. In practice, for iterations 2 and 3, some steps (7: scenario references, 8: YAML, 9: epic links, 11: FLOW_INDEX) had already been done in the first iteration and only needed verification or minor updates.
- **What the skill says**: Steps 7, 9, and 11 have brief "Continue mode: Skip if already handled" notes. Step 7 says "Skip if references already exist and are unchanged."
- **Gap**: The skip conditions are vague. When does a reference count as "unchanged"? If the serves_scenarios list changed (e.g., a scenario was added or removed), all downstream steps need re-execution. The skill doesn't help the agent decide.
- **Proposed fix**: Make continue mode skip conditions explicit: "If serves_scenarios YAML changed since last iteration, re-execute Steps 7-9. If unchanged, skip. Always verify Step 11 (FLOW_INDEX) reflects current state."
- **Priority**: **Low** — The current wording works but could be clearer.

### Issue 1.4: Token Waste in First Iteration

- **What happened**: During the first iteration, an agent was used to read 3 files and return their full content. This doubled token usage (content loaded into agent context, then written as output tokens, then loaded again into main session context). The main session then had to re-read one file because the agent output was truncated.
- **What the skill says**: The skill invokes switch-to-opus for Step 6 but gives no guidance on how context should be passed to the Opus call. The skill says "Full context (including READMEs) is preserved" but doesn't address whether file content should be pre-read or left for Opus to read.
- **Gap**: No guidance on context management between the orchestrating session and the Opus subagent call.
- **Proposed fix**: Add a note to Step 6: "Before invoking switch-to-opus, ensure all relevant context (scenarios, requirements, feedback) has been read in the current session. The switch-to-opus call inherits the current context window — do NOT use subagents to re-read files that are already in context. If files were read earlier in the session, they are available to Opus without re-reading."
- **Priority**: **Medium** — Token waste is a real cost, and this is an easy fix.

---

## Category 2: Analysis Phase Guidance

### Issue 2.1: No Analysis Template or Structure

- **What happened**: The analysis in TASK-PROC-027-13 followed a custom 6-section structure defined in goal.md: (1) what requirements assume, (2) what scenarios describe, (3) gaps, (4) tensions, (5) missing needs, (6) synthesis recommendations. This structure was highly effective — the user approved it and referenced it throughout all iterations.
- **What the skill says**: Nothing. The analysis phase doesn't exist in the skill.
- **Gap**: If the analysis phase is added to the skill (per Issue 1.1), it needs a template.
- **Proposed fix**: Define a lightweight analysis template for the skill:

  ```
  ## Analysis: [Flow Name]
  1. What existing requirements assume about this interaction
  2. What scenarios describe as the real user context
  3. Gaps: requirement elements with no scenario support
  4. Tensions: requirements that conflict with scenario reality
  5. Missing: user need moments not addressed by requirements
  6. Synthesis: recommendations for the flow (happy path, exceptions, priorities)
  ```

  The template should be optional (skip for simple flows) and should explicitly include a "USER REVIEW CHECKPOINT" instruction.
- **Priority**: **High** — Directly supports Issue 1.1.

### Issue 2.2: User Design Decisions Not Captured in Skill

- **What happened**: The user made 5 explicit design decisions during the analysis review (Q1-Q5 in the analysis document). These decisions shaped the entire flow (e.g., "first-time client is happy path," "paper+digital hybrid is NOT happy path," "instruction persistence is in scope"). The analysis document recorded these decisions inline.
- **What the skill says**: Nothing about capturing design decisions.
- **Gap**: Design decisions are a critical artifact. If the analysis phase is formalized, the skill should instruct the agent to record user decisions in a structured format that can be referenced during flow writing.
- **Proposed fix**: Add to the analysis template: "After user review, append a 'User Review Decisions' section documenting each decision with: question asked, user's answer, and implications for the flow. These decisions are binding for the flow creation phase."
- **Priority**: **Medium** — Useful structure, but agents naturally recorded decisions when the goal.md told them to.

---

## Category 3: Cross-Referencing (README_8 / README_13)

### Issue 3.1: Bidirectional Epic Links Not Completed

- **What happened**: The flow (flow.md) includes a detailed "Implementing Epics/Features" table mapping flow steps to REQ-FUNC-007, REQ-FUNC-007-01, and REQ-FUNC-007-02. However, the reverse direction was NOT done: the epic/feature requirements.md files were NOT updated with `user_needs.implements_flows` referencing FLOW-002. The task's acceptance criteria listed this ("epic_data_transfer/requirements.md has user_needs.implements_flows updated") but it was not completed.
- **What the skill says**: Step 9 says "Ask user which existing epics/features implement this flow" with three options (provide paths, use TBD, or search). The step focuses on populating the flow's table but does not explicitly say "update the epic/feature requirements.md files with reverse references."
- **Gap**: Step 9 is one-directional. It helps populate the flow's epic links but does not instruct the agent to update the epic side. README_8 clearly defines bidirectional consistency ("if flow references epic -> epic should reference flow back") and README_13 provides the YAML format for `user_needs.implements_flows` in epic files. But the skill doesn't connect these requirements to a concrete action.
- **Proposed fix**: Split Step 9 into two sub-steps:
  - **9a**: Populate the flow's "Implementing Epics/Features" table (existing behavior)
  - **9b**: For each epic/feature referenced, open its requirements.md and add/update the `user_needs` YAML section with `implements_flows`, `addresses_scenarios`, and `personas_served` per README_13 format. If the epic has no `user_needs` section yet, create one.

  Add a note: "This step creates the bidirectional link. Skipping it will cause validation warnings (README_8 Rule 2: asymmetric references)."
- **Priority**: **High** — Bidirectional traceability is a core principle of the cross-referencing system. One-directional links defeat the purpose.

### Issue 3.2: "Implementing Epics/Features" Table Format Evolved Beyond README_13

- **What happened**: The flow's Implementing Epics/Features table uses columns: User Flow Step | Implementing Epic/Feature | Status | Coverage Notes. This matches the format in README_13. But the flow also added a separate "Gaps Requiring New Requirements" section listing 7 gaps. This gap documentation is valuable but has no template or guidance in any README.
- **What the skill says**: Nothing about gap documentation.
- **Gap**: When a flow identifies steps that have NO implementing epic/feature, these need to be documented somewhere. The flow solved this organically by adding a "Gaps Requiring New Requirements" section, but neither the skill nor README_5 (template) nor README_13 (notation) defines this section.
- **Proposed fix**: Add "Gaps Requiring New Requirements" as an optional section in the flow template (README_5), placed after the Implementing Epics/Features table. Format: numbered list of gaps with brief description of what new epic/feature is needed and which flow steps it covers.
- **Priority**: **Medium** — The organic solution worked, but formalizing it prevents future agents from omitting gap documentation.

### Issue 3.3: Scenario References Were Handled Correctly

- **What happened**: Step 7 (update scenario references) was executed. All 8 scenarios received `implements_flows` entries referencing FLOW-002 with relationship and coverage values. The flow's `serves_scenarios` YAML was populated correctly.
- **What the skill says**: Step 7 provides clear instructions for bidirectional scenario-flow links.
- **Gap**: None for scenario-flow links. This worked as designed.
- **Proposed fix**: None needed.
- **Priority**: N/A

---

## Category 4: Scenario Status Warnings

### Issue 4.1: Warning System Worked Correctly

- **What happened**: The goal.md noted that "all instruct_client_on_protocol therapist scenarios currently have review_status: draft." The skill's warning mechanism was triggered, the user was informed, and the user confirmed to proceed.
- **What the skill says**: Step 1 includes a clear warning template for non-approved scenarios.
- **Gap**: None. This worked as intended.
- **Proposed fix**: None needed.
- **Priority**: N/A

### Issue 4.2: Warning Doesn't Cover Mixed Approval States

- **What happened**: The 8 scenarios had mixed states: therapist scenarios were draft/approved, client scenarios were approved. The skill warns per-scenario, which is correct. However, the warning doesn't aggregate the risk: "3 of 8 scenarios are not approved — this flow may need significant rework when those scenarios are finalized."
- **What the skill says**: Per-scenario warning only.
- **Gap**: For flows serving many scenarios, a summary warning would be more useful than 3 individual warnings.
- **Proposed fix**: After the per-scenario warnings, add a summary: "N of M scenarios are not approved. Flows based on non-approved scenarios may require rework. The more non-approved scenarios, the higher the rework risk." This is a minor enhancement.
- **Priority**: **Low** — Current behavior is functional, summary would be a quality-of-life improvement.

---

## Category 5: Multi-Perspective Flows

### Issue 5.1: No Guidance for Dual-Perspective Flows

- **What happened**: FLOW-002 spans both therapist and client perspectives across two locations (therapy room and home) and two time periods (in-session and at-home). This is fundamentally different from a single-persona flow. The flow solved this by using two phases (Phase 1: In-Session, Phase 2: At Home) and a swimlane column to identify whose perspective each step describes. This structure emerged organically during creation — no guidance existed.
- **What the skill says**: Step 1 asks "which scenario(s) will this flow serve?" and allows multiple scenarios. But it doesn't address the structural challenge of flows spanning different user roles (therapist vs. client), locations, or time periods.
- **Gap**: Multi-perspective flows need different structural guidance than single-persona flows:
  - **Swimlane identification**: Each step needs a clear "who is acting" indicator
  - **Phase separation**: When the flow spans different contexts (in-session vs. at-home), phases help organize the narrative
  - **Handoff moments**: The transition from therapist's device to client's device is a critical design moment that needs explicit attention
  - **Exception scoping**: Some exceptions apply to Phase 1 only, others to Phase 2 only
- **Proposed fix**: Add a section to the skill after Step 1 (or as a sub-step within Step 1):

  "If the flow serves scenarios from different user roles (e.g., therapist AND client), it is a **multi-perspective flow**. Additional considerations:
  - Use a Swimlane column in the happy path table to identify the acting role at each step
  - Consider splitting into phases if the flow spans different locations or time periods
  - Identify handoff moments (where control/data passes between roles) as critical design points
  - Scope exceptions to specific phases where applicable (e.g., 'Phase 1 Exceptions', 'Phase 2 Exceptions')"

  Also add a note to README_5's template showing the swimlane column option in the happy path table.
- **Priority**: **High** — FLOW-002 is unlikely to be the last multi-perspective flow. Data transfer back (client to therapist) and collaborative review flows will also be dual-perspective.

### Issue 5.2: Happy Path Table Column Structure

- **What happened**: The flow used two different table structures for Phase 1 and Phase 2:
  - Phase 1: # | Swimlane | User Action | System Response | UI State / Screen | Related Epic/Feature
  - Phase 2: # | Environment | User Action | System Response | UI State / Screen | Related Epic/Feature
- **What the skill says**: Nothing specific. README_5's template shows: # | Environment (if applicable) | User Action | System Response | UI State/Screen | Related Epic/Feature
- **Gap**: The template has no "Swimlane" column option. The flow had to invent this column for multi-perspective flows. The "Environment" column (from README_5) serves a different purpose (non-user presence, privacy concerns) and was repurposed for Phase 2.
- **Proposed fix**: Update README_5's template to show both column options:
  - **Swimlane** (for multi-perspective flows): identifies which role is acting
  - **Environment** (for privacy-sensitive flows): identifies non-user presence

  These can coexist if needed. Example table header: # | Swimlane | Environment | User Action | System Response | UI State | Related Epic/Feature
- **Priority**: **Medium** — The flow found a good solution, but the template should document it for consistency.

---

## Category 6: ID Regeneration

### Issue 6.1: ID Registry Regeneration Worked

- **What happened**: Step 4 (regenerate ID registry) was executed. FLOW-002 was correctly assigned as the next available ID.
- **What the skill says**: "MANDATORY: Before generating a flow ID, regenerate the registry: `python scripts/generate_id_registry.py --user-needs`"
- **Gap**: None. This worked as designed.
- **Proposed fix**: None needed.
- **Priority**: N/A

### Issue 6.2: Post-Creation Registry Regeneration Not Mentioned

- **What happened**: The skill regenerates the registry before ID assignment (Step 4) but doesn't mention regenerating it after the flow is created (to include the new flow in the registry). The goal.md's acceptance criteria included "ID registry regenerated after flow creation." It's unclear whether this was done.
- **What the skill says**: Registry regeneration only in Step 4 (pre-creation).
- **Gap**: After flow creation, the registry should be regenerated so the new flow appears in it. This is especially important if other tasks will be created soon that need to reference the new flow.
- **Proposed fix**: Add to Step 12 (Output) or after Step 11: "Regenerate the ID registry to include the newly created flow: `python scripts/generate_id_registry.py --user-needs`"
- **Priority**: **Low** — The registry can be regenerated at any time; it's not blocking. But including it in the workflow ensures it doesn't get forgotten.

---

## Category 7: YAML Frontmatter Completeness

### Issue 7.1: README_7 User Flow Template Missing Fields

- **What happened**: The created flow's YAML frontmatter includes fields not present in README_7's user flow template:
  - `evidence_level`: Present in flow.md, absent from README_7 flow template (but present in README_7 persona and scenario templates)
  - `review_status`: Present in flow.md, absent from README_7 flow template (but defined in README_12)
  - `review_history`: Present in flow.md, absent from README_7 flow template (but defined in README_12)
- **What the skill says**: The skill references README_7 for YAML frontmatter but doesn't list which fields are required for flows specifically. The skill's Step 8 says "Ensure flow.md includes the `serves_scenarios` array in YAML frontmatter" but doesn't mention other fields.
- **Gap**: README_7's user flow YAML template shows only: flow_id, name, created, updated, implementation_status, serves_scenarios. It's missing evidence_level, review_status, and review_history. These fields are defined in other READMEs (README_7 for evidence_level on personas/scenarios, README_12 for review fields) but not included in the flow template.
- **Proposed fix**: Update README_7's User Flow YAML Frontmatter section to include:
  ```yaml
  evidence_level: grounded | proto_persona | hypothesis
  review_status: draft | in_review | approved | deprecated
  review_history:
    - date: YYYY-MM-DD
      from: null
      to: draft
      reviewer: user | LLM | [name]
      notes: "Description"
  ```
  This aligns the flow template with the persona/scenario templates and with README_12's requirements.
- **Priority**: **High** — The current template is incomplete. Agents that follow only README_7 will produce YAML missing critical fields. The flow in TASK-PROC-027-13 got it right because the skill references README_12 separately, but the inconsistency between README_7 and README_12 is a maintenance hazard.

### Issue 7.2: serves_scenarios Missing relationship and coverage Fields

- **What happened**: README_7's `serves_scenarios` template shows: scenario_id, persona_id, persona_name, scenario_name. The actual flow.md does NOT include relationship or coverage in `serves_scenarios` (those fields appear only in the markdown table, not the YAML). Meanwhile, the `implements_flows` field in scenario YAML DOES include relationship and coverage.
- **What the skill says**: Step 1 asks for relationship and coverage per scenario. Step 7 shows these fields in the `implements_flows` YAML. Step 8 says to populate `serves_scenarios` but doesn't specify whether relationship/coverage should be included.
- **Gap**: Asymmetry between `implements_flows` (has relationship + coverage) and `serves_scenarios` (lacks them). The scenario side is richer than the flow side. This means if you read a flow's YAML, you can see which scenarios it serves but not how (primary/alternative/supporting, full/partial/minimal). You have to go to the markdown table for that.
- **Proposed fix**: Either (a) add relationship and coverage to the `serves_scenarios` YAML template in README_7, or (b) explicitly document that these fields live only in the scenario-side `implements_flows` YAML and the flow-side markdown table (not duplicated in flow YAML). Option (b) is simpler and avoids data duplication. Recommend option (b) with a note in README_7.
- **Priority**: **Medium** — The asymmetry is confusing but not blocking. Documenting the intentional asymmetry resolves it.

---

## Category 8: Technology Neutrality

### Issue 8.1: Borderline Cases Handled Well

- **What happened**: The flow maintained technology-neutral language throughout. It refers to "secure local transfer channel," "visual transfer data," "data entry component," "encryption credentials" without naming specific technologies (no QR code protocol names, no encryption algorithm names, no framework references).
- **What the skill says**: Key Principles section says "Technology-agnostic language per README_15 (no SQLite, Firebase, Flutter specifics)."
- **Gap**: None significant. The flow does mention "QR code" and "BIP-39 word list" — these are borderline. QR codes are an interaction modality (visual transfer) which README_15 says is allowed. BIP-39 is a specific standard but is used as a reference, not an implementation requirement.
- **Proposed fix**: Consider adding to README_15's "Allowed References" section: "Specific standards (e.g., QR code, BIP-39) are acceptable when they describe interaction modalities or security properties, not implementation details. The test is: could this be replaced with an equivalent standard without changing the flow's meaning?"
- **Priority**: **Low** — Current guidance was sufficient for this flow.

### Issue 8.2: Transfer Mechanism Details

- **What happened**: The flow describes animated QR codes, static QR codes, file transfer, and verbal passphrases as transfer methods. These are described at the interaction level ("therapist shows visual data, client scans") rather than the implementation level ("use zxing library to generate QR").
- **What the skill says**: README_15 allows "interaction modalities: touch, voice input, visual display."
- **Gap**: The flow walks a fine line between "interaction modality" (acceptable) and "specific technology" (forbidden). The animated QR code discussion (speed slider, chunk size, resolution) in the exceptions approaches implementation detail. However, this detail was driven by user feedback (first_iteration.md discussed video call QR viability) and is necessary for the flow to be implementable.
- **Proposed fix**: No change needed. The current level of detail is appropriate for a user flow that needs to inform implementation decisions. README_15's principle ("could this be implemented in multiple different ways?") is still satisfied — the flow describes the interaction pattern, not the code.
- **Priority**: N/A — No action needed.

---

## Additional Findings (Outside the 8 Categories)

### Issue 9.1: FLOW_INDEX.md Maintenance

- **What happened**: FLOW_INDEX.md was updated (Step 11 followed). The index includes both existing flows and "needed flows" discovered during the work (Protocol Updates flow, Crisis Response flow). This discovery-during-work pattern is valuable but not modeled in the skill.
- **What the skill says**: Step 11 says to add/update the flow entry. No mention of adding discovered needed flows.
- **Gap**: During flow creation, agents naturally discover related flows that don't exist yet. TASK-PROC-027-13 discovered the Crisis Response flow (marked HIGH PRIORITY in FLOW_INDEX) and the Protocol Updates flow. The skill should encourage documenting these discoveries.
- **Proposed fix**: Add to Step 11: "If during flow creation you identified flows that should exist but don't, add them to the 'Needed Flows' section of FLOW_INDEX.md with: status, purpose, trigger, key questions, and discovery source."
- **Priority**: **Medium** — This is a knowledge-capture opportunity that the skill currently misses.

### Issue 9.2: Deviation Documentation Worked Well

- **What happened**: The flow includes 4 documented deviations following README_14's format (User Need Reference | Deviation | Reason | Value Impact | Mitigation). The deviations are substantive and honest (e.g., acknowledging that digital transfer cannot replicate a transitional object).
- **What the skill says**: Key Principles references README_14 for deviation tables.
- **Gap**: None. The README_14 guidance was sufficient.
- **Proposed fix**: None needed.
- **Priority**: N/A

### Issue 9.3: Open Questions as a Flow Section

- **What happened**: The flow has 12 numbered open questions. These emerged during creation and iterations and serve as a backlog of design decisions to be made later. This section is valuable but has no template in README_5.
- **What the skill says**: README_5's template includes "Open Questions" as a section with bullet points. The template is minimal: just "[Question 1 that needs resolution]."
- **Gap**: The template exists but is minimal. The flow's open questions are more structured (numbered, with context and sometimes proposed answers). A slightly richer template would help future flows.
- **Proposed fix**: Update README_5's Open Questions section template to show numbered format with context:
  ```
  1. **[Question topic]**: [Detailed question]. [Context: why this matters, what the trade-offs are]. [Proposed answer if any]. [Deferred to: epic/flow/version].
  ```
- **Priority**: **Low** — Current template works; enhancement would improve consistency.

### Issue 9.4: User Feedback File Language and Format

- **What happened**: Both user feedback files were in German. The first feedback file was unstructured (stream of consciousness, mixing multiple topics per paragraph). The second was more structured (one point per bullet). The agent handled both but the unstructured first file likely required more processing.
- **What the skill says**: Continue mode says to read "feedback files (from task's user_feedback/ folder or user-provided path)" but gives no guidance on feedback format. README_10 says "all files must be in English" but this applies to personas, scenarios, and flows — feedback files are task artifacts, not user needs documents.
- **Gap**: Two issues: (1) Feedback file format guidance would help users structure their input for efficient processing. (2) The language scope of README_10 should clarify that task-level artifacts (feedback, protocols) are excluded.
- **Proposed fix**: (1) In the skill's Step 12 output section, add a note: "When providing feedback, use numbered points with one topic per point. This helps the agent process feedback systematically in continue mode." (2) In README_10, add a scope note: "These guidelines apply to user needs documents (personas, scenarios, flows). Task artifacts (plans_and_protocols, user_feedback) may use any language."
- **Priority**: **Low** — Nice-to-have clarity.

### Issue 9.5: Plan Template Architecture as Flow Content

- **What happened**: The flow includes a "Plan Template Architecture" section (system templates, master templates, client copies) that is not a flow step but a domain concept needed to understand the flow. This section emerged from user feedback (first_iteration.md) and is essential context. No README provides guidance on including domain concept explanations within flows.
- **What the skill says**: README_5's template has no section for domain concepts. The template goes from Screens/Components to Implementing Epics/Features.
- **Gap**: Complex flows may need to explain domain concepts that are prerequisites for understanding the flow steps. The flow solved this by adding a custom section, but future agents might not think to do this.
- **Proposed fix**: Add an optional section to README_5's template between Screens/Components and Implementing Epics/Features: "Domain Concepts (optional): Brief explanation of domain concepts referenced in the flow that don't have their own specification yet. Keep brief — detailed specification belongs in the implementing epic."
- **Priority**: **Low** — The flow found a good solution organically. Formalizing is a minor improvement.

---

## Priority Summary

### High Priority (3 issues — should be addressed)

| # | Issue | Category | Fix Target |
|---|-------|----------|------------|
| 1.1 | Missing analysis phase in skill | Skill workflow | create-user-flow skill |
| 2.1 | No analysis template or structure | Analysis phase | create-user-flow skill |
| 3.1 | Bidirectional epic links not completed | Cross-referencing | create-user-flow skill (Step 9) |
| 5.1 | No guidance for dual-perspective flows | Multi-perspective | create-user-flow skill + README_5 |
| 7.1 | README_7 flow template missing fields | YAML frontmatter | README_7 |

### Medium Priority (6 issues — should be addressed unless good reason not to)

| # | Issue | Category | Fix Target |
|---|-------|----------|------------|
| 1.2 | Iterative workflow not explicitly modeled | Skill workflow | create-user-flow skill |
| 1.4 | Token waste guidance missing | Skill workflow | create-user-flow skill (Step 6) |
| 2.2 | User design decisions not captured | Analysis phase | create-user-flow skill |
| 3.2 | Gaps Requiring New Requirements not templated | Cross-referencing | README_5 |
| 5.2 | Happy path table swimlane column not in template | Multi-perspective | README_5 |
| 7.2 | serves_scenarios asymmetry with implements_flows | YAML frontmatter | README_7 |
| 9.1 | Needed flows discovery not modeled | Additional | create-user-flow skill (Step 11) |

### Low Priority (5 issues — nice to have)

| # | Issue | Category | Fix Target |
|---|-------|----------|------------|
| 1.3 | Continue mode skip conditions vague | Skill workflow | create-user-flow skill |
| 4.2 | No aggregate warning for mixed approval states | Scenario warnings | create-user-flow skill |
| 6.2 | Post-creation registry regeneration not mentioned | ID regeneration | create-user-flow skill |
| 8.1 | Borderline technology references not clarified | Technology neutrality | README_15 |
| 9.3 | Open Questions template minimal | Additional | README_5 |
| 9.4 | Feedback file language/format guidance missing | Additional | README_10 + skill |
| 9.5 | Domain concepts section not in template | Additional | README_5 |

### No Action Needed (5 findings — working as designed)

| # | Issue | Category |
|---|-------|----------|
| 3.3 | Scenario references handled correctly | Cross-referencing |
| 4.1 | Warning system worked correctly | Scenario warnings |
| 6.1 | ID registry regeneration worked | ID regeneration |
| 8.2 | Transfer mechanism details appropriate | Technology neutrality |
| 9.2 | Deviation documentation worked well | Additional |

---

## Recommendations for Phase 4

When updating files based on these findings:

1. **Start with the skill** (create-user-flow/skill.md): Issues 1.1, 1.2, 1.4, 2.1, 2.2, 3.1, 5.1, 9.1 all target the skill. Bundle them into one coherent update. Be mindful of token efficiency — the skill is loaded into every agent call.

2. **Then update README_7**: Issue 7.1 is a straightforward template update (add missing fields to the user flow YAML template).

3. **Then update README_5**: Issues 3.2, 5.2, 9.3, 9.5 all add optional template sections. These are additive and low-risk.

4. **Minor README updates last**: Issues 8.1 (README_15), 9.4 (README_10) are small clarifications.

5. **Verify, don't refactor**: Per the goal.md scope — keep changes minimal and targeted. Do not refactor unrelated content in the READMEs.
