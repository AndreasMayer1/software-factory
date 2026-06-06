---
task_id: TASK-PROC-027-36
type: impl
parent_requirement: REQ-PROC-027
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-01
started: 2026-03-31
effort: M
created: 2026-03-30
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-04]
scope_description: "Create accessibility personas to embed accessibility constraints naturally into future user flow generation; update app_provider persona accordingly"
release_description: ""
cascade_type: user_needs
cascade_status: complete
requirements_version:
  commit: bfaa1913
  file: ../requirements.md
---

# Goal: Accessibility Personas and App Provider Update

## Objective

The user needs system is the primary source of truth when user flows are generated. Personas are always read during flow authoring — which means persona attributes are the most reliable mechanism for ensuring accessibility constraints are naturally respected in every future flow.

Currently, no persona carries an accessibility-specific constraint. This task addresses that gap.

## Why This Matters

When a flow AI authors a new screen or interaction, it reads the relevant personas. If no persona has photosensitive epilepsy, the flow will not consider flash rate limits. If no persona is blind, the flow will not consider screen reader paths. The goal is not to create personas for their own sake — it is to ensure that accessibility constraints enter the flow generation process through realistic, concrete human stories rather than abstract rules.

## Pre-Work: Think Before You Write

Before creating any persona, reason carefully about the following questions. Write your analysis to `plans_and_protocols/` before authoring any persona content.

**Question 1 — What accessibility categories are actually relevant to this app?**
Read the app's existing accessibility requirements (REQ-NFUNC-002) and the current persona set. Consider: which categories of impairment or constraint create genuine design decisions in an app like this? Not all categories are equally relevant — a hearing impairment matters very little in an app with no audio; a photosensitive constraint matters greatly in an app with animated QR codes.

**Question 2 — Does each category warrant a persona, or is it already covered?**
A persona is justified when: (a) the constraint would change how a flow is designed, AND (b) that constraint is not already represented by an existing persona or requirement. Some accessibility needs may already be implicitly covered by existing personas (e.g., motor constraints appear in Jana, Nina, Sophie). Avoid duplicating what already exists.

**Question 3 — Does each persona need scenarios?**
The existing scenarios in this project are as-is scenarios — they describe how users behave in their lives *without* the app. For many accessibility conditions, the as-is behavior is identical to a non-impaired user (a person with epilepsy uses pen and paper the same way anyone else does). Only write a scenario if the as-is situation is genuinely different in a way that matters for product design.

**Question 4 — How should the app_provider persona be updated?**
Read the current app_provider persona. The app provider has a role in communicating the product's accessibility stance: what is committed to in v1, and what is planned but deferred. The update should be honest and specific enough to generate real constraints during flow authoring — not just "we care about accessibility."

## Scope

### In Scope
- Analysis of which accessibility categories warrant new personas
- Creating those personas (number and type to be determined through pre-work analysis)
- Updating the app_provider persona to reflect WCAG compliance commitment and scope by release
- Deciding and documenting whether scenarios are needed per persona

### Out of Scope
- Modifying REQ-NFUNC-002 (the engineering-facing accessibility requirement)
- Implementing any accessibility features in code
- Creating scenarios unless the pre-work analysis concludes they add genuine value

## Constraints

- Personas must follow the conventions established in REQ-PROC-010 and the existing persona set
- Accessibility personas should feel like real people, not diagnostic checklists
- The constraint must be specific enough to drive concrete design decisions in a flow

## Cascade Passes

This task propagates changes through the user needs hierarchy across multiple sessions.
**Read `plans_and_protocols/cascade_log.md` before starting any pass.**

| Pass | Level | Skill | Status |
|------|-------|-------|--------|
| 1 | Persona | `ux-write-persona` | pending |
| 2 | Scenario | `ux-write-scenario` | pending |
| 3 | Flow | `ux-create-flow` | pending |
| 4 | Requirements | `requ-derive-from-flow --incremental` | pending |

**Pass 3 requires three sub-steps** (all must complete before Pass 3 is done):
1. `ux-flow-draft` — update each affected flow with the required changes
2. `ux-flow-complete` — content-complete each updated flow (moves to `aligned`)
3. `ux-flow-approve` — joint-approve the full cluster (moves all to `approved`)

**Resuming**: Check `cascade_log.md` status field → execute the next incomplete pass.
**Completing**: Task is done after Pass 4 (requirement-update goal.md files created).

## Acceptance Criteria

- [ ] Pass 1: Pre-work analysis written, personas created, cascade_log.md Pass 1 written
- [ ] Pass 1: Each created persona has a clearly stated accessibility constraint specific enough to influence flow design
- [ ] Pass 1: Persona count and scenario decisions justified in the analysis
- [ ] Pass 1: app_provider persona updated with accessibility commitment and release scope
- [ ] Pass 1: No persona duplicates accessibility coverage already present in the existing set
- [ ] Pass 2: Scenario work addressed (created, updated, or explicitly skipped with reason), cascade_log.md Pass 2 written
- [ ] Pass 3: Affected flows updated AND re-approved (content-complete + joint-approve for the full cluster), cascade_log.md Pass 3 written
- [ ] Pass 4: `requ-derive-from-flow --incremental` run, requirement-update goal.md files created → DONE

## Notes

Context from the design conversation that prompted this task:
- The immediate trigger was: animated QR codes in FLOW-003 may flash faster than WCAG 2.3.1 allows (>3Hz), posing a photosensitive epilepsy risk
- The broader goal is: any future flow involving animation, contrast, text size, or navigation should naturally respect the right constraints because the relevant persona is in the room
- Text output for data (alongside visualizations) is already planned — this improves the screen reader story for blind users without requiring a separate implementation effort
- Full screen reader support (TalkBack/VoiceOver optimization) is a post-v1 goal; app_provider should reflect this distinction clearly
