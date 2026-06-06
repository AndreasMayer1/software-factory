---
task_id: TASK-PROC-069-01
type: explore
parent_requirement: REQ-PROC-069
urgency: 3
urgency_reason: U3-FIX
impact: 4
impact_reason: I4-PAIN
status: completed
effort: S
created: 2026-06-05
started: 2026-06-05
completed: 2026-06-05
expected_tool_calls: 30
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Must hold claude-route internals, CLAUDE.md invocation contract, scribble redesign decisions (D-3), and automated-mode dispatch simultaneously"
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and design the task-start skill: a wrapper over claude-route that adds context loading and pre-flight checks at task execution entry"
release_description: ""
opus_recommended: false
writes_requirements: true
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Design the task-start Skill (Wrapper over claude-route)

## Objective

Design a new `task-start` skill that acts as the canonical entry point for executing a task. Currently, `claude-route` handles this directly. The exploration must determine what `task-start` adds on top of `claude-route`, where the boundary between the two skills lies, and what the skill's contract looks like — so that a follow-on impl task can write it.

The Round-1 synthesis for TASK-PROC-032-29 resolved in Round 2 that `task-start` and `claude-route` should both exist but be separated ("both, separated"). This task defines what that separation means in practice.

## Background

Today, when a user or the orchestrator says "do [task]", `claude-route` is invoked directly (CLAUDE.md §4 "Default Workflow"). `claude-route` reads the task's `goal.md`, detects task type, and delegates to the right execution skill (code-simple, code-complex, ui-scribble-iterate, etc.).

The Round-2 discussion (referenced in TASK-PROC-032-29's synthesis at §8, last row) concluded that a `task-start` wrapper should sit above `claude-route`:
- Handle pre-flight steps that apply to ALL tasks regardless of type (context loading, pre-condition checks)
- `claude-route` retains responsibility for type detection and skill dispatch

This separation was confirmed as correct but was explicitly NOT included in the scribble workflow redesign (TASK-PROC-032-29 D-3: "confirm it lands in this redesign vs its own task" → user said: own task).

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-05_00_user_initial_input.md`

Read it as a seed bed, not a spec.

## How to Approach This

Use design thinking as the guiding process. Read `claude-route` and `CLAUDE.md §4` carefully — understand what the current entry point does and what it does NOT do. The exploration should produce a concrete skill design (phases, inputs, outputs, boundary with claude-route) that an implementer can execute without further design work.

## Seeds

1. **What does `task-start` add that `claude-route` doesn't already do?**
   Read the current `claude-route` skill end-to-end. What pre-flight steps are currently missing, redundant across execution skills, or performed inconsistently? The answer determines whether `task-start` is a thin adapter or a substantive layer.

2. **Context loading: who is responsible for reading goal.md + protocol.md?**
   Currently each execution skill reads these itself. If `task-start` loads context first and passes it downstream, execution skills become simpler — but does that create a rigid coupling? Or should `task-start` merely verify that goal.md exists and is readable, leaving the actual read to the execution skill?

3. **What is the exact boundary between `task-start` and `claude-route`?**
   The synthesis says "both, separated." `claude-route` stays but its invocation point shifts — what does `claude-route`'s input/output contract look like when called by `task-start` vs. called directly? Does `claude-route` need changes, or is `task-start` purely additive?

4. **How does `task-start` interact with automated mode?**
   The automated orchestrator (`create_orchestration_task.py`) currently invokes skills directly per task type. Does `task-start` become the single entry point in automated mode too, or does it only apply to interactive sessions? If both: how does `task-start` detect context (interactive vs. automated) and adjust?

5. **What pre-conditions does `task-start` enforce?**
   Candidate checks: goal.md present and parseable, `status: pending` (not already in_progress or completed), `after:` dependencies completed, no `.git/index.lock` stale lock, `awaiting:` is empty. Which of these belong in `task-start` vs. the execution skill vs. the orchestrator? Are any already covered elsewhere?

6. **What is the CLAUDE.md change?**
   The current CLAUDE.md §4 says "invoke `claude-route` with the path, task ID, or the instruction." If `task-start` becomes the new entry point, CLAUDE.md must change. What is the exact new wording, and what does the migration path look like (are there any in-flight tasks or skills that hard-code `claude-route` invocations that must be updated)?

## Execution Model

Read `claude-route` skill fully. Read CLAUDE.md §4 in full. Read the Round-1 synthesis for TASK-PROC-032-29 (especially §8 last row and §9 D-3) to understand the resolved design context. Read the automated orchestrator script (`scripts/tasks/create_orchestration_task.py`) to understand the automated entry point.

For any seed requiring external knowledge, delegate to a spawned `general-purpose` agent with a focused question.

## Output

A concrete skill design document in `plans_and_protocols/` describing:
- `task-start` phases and per-phase responsibilities
- Exact boundary with `claude-route` (inputs, outputs, who calls whom)
- Pre-conditions `task-start` enforces and what happens on failure
- How automated mode is handled
- Required changes to CLAUDE.md and any other affected skills/scripts
- Whether `claude-route` itself needs changes
- Honest residuals (what remains uncertain or requires developer decision)

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
| TASK-PROC-032-29 | completed | Scribble-gate redesign that produced D-3; synthesis at `plans_and_protocols/2026-06-04_02_round_1_synthesis.md` §9 |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../../ui_sketch_iteration_workflow/tasks/2026-06-04_explore_redesign-implementation-workflow-scribble-gate%20(completed)/goal.md) | Predecessor — D-3 in §9 of Round-1 synthesis is the origin of this task |
