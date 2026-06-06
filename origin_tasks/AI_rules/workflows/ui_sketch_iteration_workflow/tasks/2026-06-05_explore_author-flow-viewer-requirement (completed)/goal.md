---
task_id: TASK-PROC-032-33
type: explore
parent_requirement: REQ-PROC-032-07
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-MODERATE
status: completed
started: 2026-06-05
completed: 2026-06-06
session_completed_at: 2026-06-06T11:44:41Z
effort: S
created: 2026-06-05
expected_tool_calls: 15
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Author the REQ-PROC-032 (+ REQ-PROC-060) ACs for the script-driven user-flow viewer embedded in the scribble (PROP-14): a 'Show User Flows' sidebar with tabs, populated by a script copying flow source (NOT LLM re-emission), via a client-side vendored Markdown→HTML renderer — a dependency-admission decision."
release_description: ""
opus_recommended: true  # promoted after context_limit_no_entitlement
writes_requirements: true
requirements_version:
  commit: d29b49c9
  file: ../requirements.md
session_id: 88d0d8be-6ef2-4c61-8107-a33717d03059
session_account: web

---
# Goal: Author the Flow-Viewer Requirement (PROP-14, REQ-PROC-032 + REQ-PROC-060)

## Objective

Author the REQ-PROC-032 ACs (via `requ-explore`) for the **script-driven user-flow viewer** embedded in the
scribble — manifest task **T-A5**:
- A **"Show User Flows" sidebar** with tabs to pick a flow; flow content shown inline.
- **Script-driven, NOT LLM-generated**: a script copies/links the flow source files; the LLM must not re-emit
  flow HTML (token + single-source constraint).
- Needs a **Markdown→HTML renderer** → **dependency-admission decision (REQ-PROC-060, D-5)**. Recommendation
  (`11`B7): a **client-side vendored, pinned** renderer (self-contained, zero-build). This is a
  developer-authorized call — author the AC to *require the decision*, and record the recommendation.
- Cherry-on-top: colour-highlight the flow passages relevant to the scribbled screens, driven purely by
  `flow_positions` step numbers (no LLM re-read).

Implemented later by T-C18.

## Background

S4 (lowest-priority, gated on D-5) stage of the redesign (TASK-PROC-032-29). Substrate (sibling under this
`tasks/`):
`../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/plans_and_protocols/2026-06-05_13_implementation-task-manifest.md`
(row T-A5) + `2026-06-05_11_synthesis_resolve-open-questions.md` (B7). Eval substrate PROP-14 is in
`2026-06-04_explore_eval-scribble-workflow-live-iteration (completed)/plans_and_protocols/2026-06-04_04_round_2_evaluation.md` §3.

Current requirements: ../requirements.md (REQ-PROC-032).

## How to Approach This

Author ACs via `requ-explore`. Independent and lowest priority. The dependency choice (D-5) is the
developer's — author the AC to require a chosen, pinned, vendored renderer and flag the REQ-PROC-060 gate;
do not self-add the dependency.

## Seeds

1. Client-side vendored renderer vs build-step — encode the recommended choice + the REQ-PROC-060 gate.
2. Flow-passage highlighting purely from `flow_positions` step numbers — feasible without an LLM re-read?

## Execution Model

`requ-explore` on REQ-PROC-032; small. The dependency-admission portion routes through REQ-PROC-060.

**Task-ordering (developer directive 2026-06-05):** every task this task creates (the impl tasks
`task-derive-from-requ` derives) MUST be appended to `.claude/task_ordering_priority_override.txt` — they carry
no `target_package`, so they will not surface in `next_tasks.py` otherwise.

## Output

REQ-PROC-032 carries ACs sufficient for `task-derive-from-requ` to generate T-C18, with the MD-renderer
dependency framed as a developer-authorized REQ-PROC-060 decision.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] The user has approved the final synthesis and stated what to do next
- [x] The action stated by the user as the next step was performed successfully

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Independent. Lowest priority of the A-tasks; the renderer choice (D-5) is a REQ-PROC-060 developer decision but does not block authoring the requirement. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — redesign manifest row T-A5; PROP-14. |
