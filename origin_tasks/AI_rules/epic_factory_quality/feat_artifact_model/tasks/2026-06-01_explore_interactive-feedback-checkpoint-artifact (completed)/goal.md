---
task_id: TASK-PROC-044-02-05
type: explore
parent_requirement: REQ-PROC-044-02
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-DEV-EXP
status: completed
started: 2026-06-02
completed: 2026-06-02
session_completed_at: 2026-06-02T00:07:48Z
effort: S
created: 2026-06-01
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Survey where and how skills capture interactive developer feedback during execution; define what a structured artifact type for these checkpoints should look like; produce a new registry token proposal"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore spanning multiple skill workflows across multiple features
writes_requirements: false
requirements_version:
  commit: 4d4b3e26
  file: ../requirements.md
session_id: 28452283-423e-48d2-a44e-65e45af9406e
session_account: gmail
---
# Goal: Define Artifact Type for Interactive Skill Feedback Checkpoints

## Objective

We do not know what "interactive developer feedback during skill execution" is, as an artifact. Skills for persona authoring, flow creation, requirement review, and plan-review all pause and ask the developer questions. The responses influence the produced artifacts but are not captured in any structured form — they live in plans_and_protocols/ prose and disappear after context compression. We need to understand the shape of this gap well enough to define a registry token (and potentially a schema) that makes these interactions first-class artifacts.

## Background

The artifact registry (`.factory/registry/artifacts.yaml`) currently has 46 tokens across 11 categories. Two tokens are adjacent to this gap but do not fill it:

- **`user-input`** (`task-workspace` category): verbatim developer seed captured at explore-task start — covers the initial prompt, not mid-skill decisions.
- **`pending-question` / `pending-answer`** (`automation` category): escalation checkpoints written in automated mode when a session cannot proceed — not for interactive, developer-present skill sessions.

During the ratification session for TASK-PROC-044-02-01, the developer noted that skills ask for input in persona/scenario/flow creation, requirement structuring, and architectural decisions, but the responses are not a predefined form and have no defined artifact. The suggestion was to explore formalizing this as a `feedback-checkpoint` (or equivalent) token.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-01_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 4d4b3e26:requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **Where do skills interrupt and ask?** Walk through the skills that pause for developer input during execution: `ux-write-persona`, `ux-create-flow`, `requ-explore`, `task-create`, `architecture-advisor` plan reviews, `code-complex`. Map what questions they ask and at what phase.

2. **What gets preserved vs. lost today?** In current plans_and_protocols/ narrative, interactive decisions are embedded in prose. After context compression, what is still recoverable? What is silently lost? Is there a pattern to what matters?

3. **Boundary with existing tokens.** `user-input` covers the explore-task seed (one artifact per task, at start). `pending-question`/`pending-answer` cover automated-mode escalation (one question per escalation, structured). What lives in the gap — the series of interactive back-and-forth decisions during a single interactive skill run?

4. **Schema vs. token only.** Is a registry token + filesystem glob sufficient (as for most tokens), or does the richness of mid-skill decisions warrant a structured YAML schema? Compare to how `scribble-feedback.md` (unstructured prose) differs from `pending-question.md` (structured YAML-like).

5. **Impact on skill design.** Would formalizing this artifact change HOW skills ask for input (e.g., emit a structured checkpoint file before asking), or only HOW the response is stored after? What is the minimal viable intervention?

## Execution Model

Gather raw material — read skills, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline.

## Output

A future implementer should be able to read the synthesis and immediately know: what the new registry token is named, what filesystem path or glob it covers, its one-line definition, which category it belongs to, and whether a schema file is warranted (and if so, what fields it has). If the exploration concludes that no new token is needed (the gap is already covered), that decision and its reasoning must be equally clear.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-02-01 | completed | Registry foundation — exploration builds on the existing 46-token registry |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-044-02-01](../2026-05-31_impl_create-and-seed-artifact-registry%20(completed)/goal.md) | Predecessor — ratification protocol (protocol_ratification.md) is the direct source of this task's seed |
