---
task_id: TASK-PROC-032-32
type: explore
parent_requirement: REQ-PROC-032-06
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUALITY
status: completed
effort: M
created: 2026-06-05
expected_tool_calls: 20
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Author the REQ-PROC-032 ACs for the auto-review control model: sequential reviewer execution, gate-on-convergence default cadence, selective-reviewer-skip rule (PROP-7), severity-driven stop + non-convergence circuit-breaker (PROP-13B), and trim question.md by audience (PROP-6)."
release_description: ""
opus_recommended: false   #
writes_requirements: true
requirements_version:
  commit: d29b49c9
  file: ../requirements.md
started: 2026-06-05
completed: 2026-06-06
session_completed_at: 2026-06-06T11:35:23Z
session_id: 67771920-7253-4a95-8b15-547e7ff5208f
session_account: gmail
---
# Goal: Author the Auto-Review Control Model (REQ-PROC-032)

## Objective

Author the REQ-PROC-032 ACs (via `requ-explore`) for **how scribble iteration is controlled** — manifest task
**T-A4**:
- **Sequential** reviewer execution (NOT parallel — a session-limit hit then leaves only one agent incomplete,
  per the developer's resolved decision R2§2).
- **Gate-on-convergence** as the default cadence (gate the human only when auto-review finds no more
  substantial improvements).
- **Selective reviewer skip** (PROP-7): a reviewer skippable next round only if it produced nothing
  `severity ≥ MEDIUM` last round, unless new feedback touched its scope.
- **Severity-driven stop** + the single non-convergence **circuit-breaker** (PROP-13B; escalate persistent
  MEDIUM+ to `requ-explore`). No complexity ceiling.
- **Trim `question.md` by audience** (PROP-6): keep only the decision-asks; orientation moves into the
  scribble; delete the fix-recap.

Implemented later by T-C16 (skills `ui-scribble-auto-review`, `ui-scribble-iterate`).

## Background

S-stage of the redesign (TASK-PROC-032-29). Substrate (sibling under this `tasks/`):
`../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/plans_and_protocols/2026-06-05_13_implementation-task-manifest.md`
(row T-A4). The resolved inputs are in the eval substrate
`2026-06-04_explore_eval-scribble-workflow-live-iteration (completed)/plans_and_protocols/2026-06-04_04_round_2_evaluation.md` §2
(sequential reviewers; gate-on-convergence) and `…_02_round_1_evaluation.md` PROP-6/7/13. Authoritative.

Current requirements: ../requirements.md (REQ-PROC-032).

## How to Approach This

Author ACs via `requ-explore`. Disjoint from T-A2/T-A3 sections; may run in parallel. The decisions here are
already resolved (R2§2) — encode them, do not re-open.

## Seeds

1. "Substantial" / skip-eligibility — phrase it concretely against the severity tags.
2. The convergence-gate cadence as the default vs the optional override policies — which are required ACs?
3. `question.md` audience routing — what stays, what moves into the scribble?

## Execution Model

`requ-explore` on REQ-PROC-032 (iteration-control sections). Light enough to run inline if under the
context-window threshold; agent otherwise.

**Task-ordering (developer directive 2026-06-05):** every task this task creates (the impl tasks
`task-derive-from-requ` derives) MUST be appended to `.claude/task_ordering_priority_override.txt` — they carry
no `target_package`, so they will not surface in `next_tasks.py` otherwise.

## Output

REQ-PROC-032 carries ACs sufficient for `task-derive-from-requ` to generate T-C16.

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
| — | — | Independent — disjoint REQ-PROC-032 sections; may run in parallel. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — redesign manifest row T-A4; resolved inputs R2§2. |
