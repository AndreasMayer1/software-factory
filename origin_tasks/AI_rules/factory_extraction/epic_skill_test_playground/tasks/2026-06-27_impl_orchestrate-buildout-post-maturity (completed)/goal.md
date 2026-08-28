---
task_id: TASK-PROC-068-05
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-06-27
started: 2026-06-27
completed: 2026-06-27
session_completed_at: 2026-06-27T16:32:09Z
expected_tool_calls: 30
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "Must read the maturity verdict, derive the Stage-2 batch shape from it, and create tasks with correct after-edges and the self-propagating developer directive — all held in context simultaneously."
orchestration_task: true
after: [TASK-PROC-073-01-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Second gap-filler orchestration task: reads the maturity walk verdict and creates the Stage-2 batch (T-unblock-071-02, T-unblock-065-06-08, T-orch3) and re-points T-finalize (TASK-PROC-068-03) after: to T-orch3."
release_description: ""
opus_recommended: true   # reason: orchestration synthesis — must read verdict, derive batch shape, create tasks with correct wiring and self-propagating developer directive; cross-cutting invariant across multiple requirement parents
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: a3f14541-3db2-4f9c-bcc9-19a14df3accb
session_account: gmail
---
# Goal: Orchestrate Build-Out Post-Maturity (T-orch2)

## Objective

This is the **second gap-filler orchestration task** in the Capability-Testing Oracle build-out
chain. It runs after the discriminating-maturity walk (T-maturity / TASK-PROC-073-01-03) has a
verdict, reads that verdict, and creates the Stage-2 task batch.

**Coordinator only — no direct deliverable.** `covers.acceptance_criteria` is empty.

## DEVELOPER DIRECTIVE (self-propagating — carry forward verbatim)

> Every task this orchestration task creates — and every task that THOSE tasks create thereafter,
> transitively — MUST be appended to `.claude/task_ordering_priority_override.txt` immediately
> after creation, with a one-line comment and the task ID. This rule self-propagates: every
> orchestration task in the chain MUST carry this directive forward verbatim in its own goal.md.
>
> **Failure to append = the task is invisible to `next_tasks.py`** (process tasks have no
> `target_package`; they surface only via this file).

## Inputs to read first (cite, do not re-derive)

1. **Maturity verdict** (primary decision input):
   `requirements_tasks/process/AI_rules/factory_extraction/epic_capability_testing/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk/plans_and_protocols/`
   — read the maturity verdict document written by T-maturity. It states the demonstrated
   discriminating scope and whether the oracle is ready to gate the layer-derivation/ralph work.

2. **Build-out plan** (Stage-2 recipe):
   `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-11_explore_llm-verifiable-open-ended-skill-tests (completed)/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`
   — see "Stage 2" for what this task must create.

3. **Layer-deriv parked pre-answers** (draft for T-unblock-071-02):
   `requirements_tasks/process/AI_rules/factory_extraction/epic_layer_derivation/tasks/2026-06-15_explore_design-real-mechanism-and-derive-impl-verify-chain/plans_and_protocols/2026-06-26_02_developer_pre-answers-parked.md`
   — these are the developer's pre-written answers to the 10-decision gate. They are the DRAFT
   content for T-unblock-071-02's goal.md; the developer fills `answer.md` (a session must NOT
   fabricate it).

4. **This orchestration task's own protocol** (for continuity):
   `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-26_impl_orchestrate-buildout-post-spike/plans_and_protocols/`
   — context from T-orch1's execution (TASK-PROC-068-02).

## Stage-2 tasks to create (via `task-create`)

### T-unblock-071-02 — Developer-gate task for layer-derivation design task

Create a task that surfaces the parked 10-decision gate of TASK-PROC-071-02 to the developer:

- **Type**: impl (developer-gate shape — a session surfaces the gate; the developer fills the answer)
- **Parent requirement**: REQ-PROC-071-02 (the layer-derivation design task's requirement)
- **Objective**: Surface the parked `pending_feedback/TASK-PROC-071-02/question.md` gate to the
  developer, with the captured pre-answers
  (`…/2026-06-26_02_developer_pre-answers-parked.md`) as the draft in the goal.md. The executing
  session presents the pre-answers to the developer and asks them to confirm or modify, then writes
  `answer.md` — **a session must NOT fabricate `answer.md`**; only the developer writes it.
  Once `answer.md` is written, TASK-PROC-071-02 resumes and emits its impl/verify/re-capstone chain.
- **after**: [] (unblocked now that the tester is mature; runs immediately)
- **interactive_required**: true (developer must be present to fill answer.md)
- **MUST append to `.claude/task_ordering_priority_override.txt`** (developer directive above)

### T-unblock-065-06-08 — Developer-gate task for ralph design task

Same shape as T-unblock-071-02, but for TASK-PROC-065-06-08 (the ralph / perpetuating-task-creation
design task that is parked in pending_feedback):

- **Type**: impl (developer-gate shape)
- **Parent requirement**: REQ-PROC-065-06 (or the nearest sub-requirement that TASK-PROC-065-06-08
  covers — read its goal.md to determine the exact parent)
- **Objective**: Surface the parked gate for TASK-PROC-065-06-08 to the developer; present the
  parked content as the draft; developer fills `answer.md`. Session must NOT fabricate it.
- **after**: [] (unblocked now that the tester is mature)
- **interactive_required**: true
- **MUST append to `.claude/task_ordering_priority_override.txt`** (developer directive above)

### T-orch3 — Next gap-filler orchestration task

Create the next orchestration task, gated after the layer-derivation and ralph chains complete
their terminal verification tasks:

- **Type**: impl
- **orchestration_task**: true
- **Parent requirement**: REQ-PROC-068
- **after**: [<layer-deriv re-capstone verify task ID>, <ralph verify task ID>]
  — these IDs do not exist yet at T-orch2 creation time. T-orch3 must be created with
  `after: []` initially, and its `after:` must be updated by TASK-PROC-071-02 and
  TASK-PROC-065-06-08 when they emit their chains (each emitting chain re-points T-orch3's
  `after:` to include its terminal verify task, following the same re-pointing mechanic
  used for T-finalize/TASK-PROC-068-03). OR: create T-orch3 now with
  `after: [T-unblock-071-02, T-unblock-065-06-08]` as a placeholder, and note that
  TASK-PROC-071-02 / TASK-PROC-065-06-08 must re-point it forward when they emit chains.
- **Objective** (T-orch3's goal.md): Once layer-derivation and ralph chains are complete, derive
  full playground enhancements (071-driven harness-middle generation; ralph-driven autonomous test
  runs). Creates the terminal batch. Creates NO successor orchestration task — the chain ends.
  Carries the DEVELOPER DIRECTIVE forward verbatim.
- **MUST append to `.claude/task_ordering_priority_override.txt`** (developer directive above)

## After creating the 3 tasks

### Re-point T-finalize (TASK-PROC-068-03)

Edit `requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-26_impl_finalize-playground-terminus/goal.md`:
- Change frontmatter `after:` from `[TASK-PROC-068-02]` (or its current value) to `[TASK-PROC-068-05]`
  — i.e., point it to T-orch3's ID (the new live frontier), NOT to this task (T-orch2).

  **Note**: T-finalize's `after:` should point to T-orch3, not T-orch2. T-orch2 is itself an
  intermediate orchestration task; T-orch3 is the next frontier. Update the Dependencies table row
  and Related Tasks row in T-finalize's body to reference T-orch3, keeping the
  "re-pointed forward by each orchestration task" wording.

### Append to `.claude/task_ordering_priority_override.txt`

Append all three new task IDs (T-unblock-071-02, T-unblock-065-06-08, T-orch3) with comments
following the existing style in that file. This is mandatory per the developer directive.

## Background

Created by T-orch1 (TASK-PROC-068-02) on the spike's GREEN verdict. The pattern:
each "gap" in the build-out gets one orchestration task; its `goal.md` instructs the executing
session to read the predecessor outcome, create the next batch, create the next orchestration task,
and re-point T-finalize. Full chain spec:
`requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-11_explore_llm-verifiable-open-ended-skill-tests (completed)/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`

## Acceptance Criteria

- [x] Maturity verdict read; Stage-2 batch shape derived from it
- [x] T-unblock-071-02 created (TASK-PROC-071-03, developer-gate for layer-derivation 071-02 parked gate); appended to override file
- [x] T-unblock-065-06-08 created (TASK-PROC-065-06-09, developer-gate for ralph 065-06-08 parked gate); appended to override file
- [x] T-orch3 created (TASK-PROC-068-06, next gap-filler orchestration task, after: [TASK-PROC-071-03, TASK-PROC-065-06-09] placeholder); appended to override file
- [x] T-finalize (TASK-PROC-068-03) `after:` re-pointed to T-orch3 (TASK-PROC-068-06, the new live frontier)
- [x] DEVELOPER DIRECTIVE carried forward verbatim in T-orch3's goal.md

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-073-01-03 (T-maturity) | pending | Discriminating-maturity walk must produce a verdict before Stage-2 batch shape is known |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-02](../2026-06-26_impl_orchestrate-buildout-post-spike/goal.md) | Predecessor orchestration task (T-orch1) — created this task; read its protocol for context |
| [TASK-PROC-073-01-03](../../../epic_capability_testing/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk/goal.md) | Gate — discriminating-maturity verdict is this task's primary decision input |
| [TASK-PROC-068-03](../2026-06-26_impl_finalize-playground-terminus/goal.md) | T-finalize — this task re-points its after: to T-orch3 |

## Notes

- **This task is an orchestrator, not an implementer.** Use `task-create` for each new task.
  Do not implement layer-derivation or ralph features here.
- **Layer-derivation parked pre-answers**: the developer captured 9 of 10 decisions in the
  pre-answers file. Decision #10 (go/no-go) is deliberately NOT pre-answered — it stays closed
  until `answer.md` is written. T-unblock-071-02 must present the full gate (all 10 decisions)
  with the 9 pre-answers as draft and explicitly mark Decision #10 as requiring the developer's
  live answer.
- **Human-only-writes-answer.md safety rule**: a session MUST NOT fabricate `answer.md` for either
  unblock task. The rule is absolute — the developer's judgment is the input, not a session's
  inference.
- **T-orch3 after: placeholder**: if the terminal verify task IDs from 071-02 and 065-06-08 are
  not yet known at creation time (they are not — those chains are emitted only when the unblock
  tasks run), create T-orch3 with `after: [T-unblock-071-02, T-unblock-065-06-08]` as a
  conservative placeholder, and note in T-orch3's goal.md that its `after:` must be re-pointed
  forward by TASK-PROC-071-02 / TASK-PROC-065-06-08 when they emit their terminal verify tasks.
