---
task_id: TASK-PROC-035-21
type: explore
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-06-05
started: 2026-06-05
completed: 2026-06-05
session_completed_at: 2026-06-05T15:04:55Z
expected_tool_calls: 35
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "The two-wave split spans REQ-PROC-035 (orchestration) AND REQ-PROC-058 (plan format) at once — the scribble-gate terminal, the release-derive-code skill, and the --scope plan mode are one coupled design; splitting loses the cross-requirement coherence."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Author the REQ-PROC-035 + REQ-PROC-058 ACs for the two-wave orchestration spine: presentation-wave/code-wave bisection, the scribble-gate terminal, the new release-derive-code skill, the release-begin-impl-finalize→release-finalize-impl rename, the skill-design trade-off-record AC, the registry routing-contract, and the session/token cut map."
release_description: ""
opus_recommended: true   # reason: cross-requirement architectural synthesis (035+058); the two-wave spine everything else derives from
writes_requirements: true
requirements_version:
  commit: a57fca07
  file: ../requirements.md
session_id: 4e50ff12-0cbc-4992-b5e0-3bc9a50eaaa8
session_account: web
---
# Goal: Author the Two-Wave Orchestration Spine (REQ-PROC-035 + REQ-PROC-058)

## Objective

Author the requirement ACs (via `requ-explore`) that define the **structural spine** of the scribble-gate
redesign — the part everything else hangs off. This is task **T-A1** of the implementation manifest. What
must be turned from design into ACs:
- The **two-wave decomposition**: Wave 1 (`release-begin-impl`) decomposes only scribble + pure-domain tasks;
  Presentation coding tasks are decomposed only post-approval. Make the bisection a **hard requirement**, with
  the **per-design-unit** escape (pure-domain units get code in Wave 1).
- The **scribble-gate terminal** in the orchestration chain (alongside today's `_VALIDATION` terminal).
- The new middle skill **`release-derive-code`** (Wave 2); the rename **`release-begin-impl-finalize` →
  `release-finalize-impl`** (+ the SCI audit it gains).
- The **`task-derive-from-requ --scope {presentation,code}`** plan mode (REQ-PROC-058 plan format).
- The **skill-design trade-off-record AC** (fused-responsibility skills only; objective trigger = >1
  artifact-in→artifact-out pair OR a mode flag).
- The **registry routing-contract** extension (`.factory/registry/artifacts.yaml`): every plan-entry
  `task_type` must resolve to a registered skill — this closes the D-0 bug class.
- The **session/token cut map** as ACs (which work is orchestrator vs spawned agent vs new task).

## Background

This is the S1 stage of the redesign synthesized in TASK-PROC-032-29. The complete design, the resolutions,
and the task manifest are in that task's `plans_and_protocols/` — read as the authoritative substrate (not a
seed bed; the design is settled, this task encodes it as ACs):
`../../../../workflows/ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate/plans_and_protocols/`
— esp. `2026-06-04_02_round_1_synthesis.md` (§0,§2,§8), `2026-06-05_10_synthesis_next-steps-plan.md`,
`2026-06-05_11_synthesis_resolve-open-questions.md` (B1/B2/B4/C5), and
`2026-06-05_13_implementation-task-manifest.md` (row T-A1).

Current requirements: ../requirements.md (REQ-PROC-035). Also authors into REQ-PROC-058
(`../../implementation_task_planning/requirements.md`).

## How to Approach This

The design is decided; this is disciplined AC authoring, not open exploration. Read the substrate, then author
ACs in REQ-PROC-035 and REQ-PROC-058 via `requ-explore`. Where a decision is recorded as a recommendation in
`11`, encode the recommended option and note the trade-off (the skill-design trade-off-record format).

## Seeds

1. The presentation/code wave boundary — how is "pure-domain unit" defined precisely enough for an AC?
2. The scribble-gate terminal vs the existing `_VALIDATION` terminal — how do they compose in the chain?
3. The `--scope` mode as REQ-PROC-058 plan-format ACs — what fields does a wave-tagged plan entry carry?
4. The registry routing-contract — what schema change makes "every `task_type` resolves to a skill" checkable?

## Execution Model

`requ-explore` for REQ-PROC-035 and REQ-PROC-058. Run heavy reads as a background agent if the
context-window rule (`should_use_agents.py`) trips. Respect the doc-lookup budget.

**Task-ordering (developer directive 2026-06-05):** every task this task creates (the impl tasks
`task-derive-from-requ` derives from these requirements) MUST be appended to
`.claude/task_ordering_priority_override.txt` — they carry no `target_package`, so they will not surface in
`next_tasks.py` otherwise.

## Output

REQ-PROC-035 and REQ-PROC-058 carry ACs sufficient for `task-derive-from-requ` to generate the spine impl
tasks (manifest T-C1…C7). Each new/changed skill's responsibility is stated; fused skills carry a trade-off
record.

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
| — | — | No blocking dependencies. This is the spine; T-A2 depends on it, not the reverse. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../../../../workflows/ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — the redesign synthesis + manifest this task authors into ACs. |
