---
task_id: TASK-PROC-068-10
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-30
completed: 2026-06-30
session_completed_at: 2026-06-30T20:57:37Z
effort: M
created: 2026-06-30
expected_tool_calls: 30
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "The run must hold the harness artifact under test, the Capability-Testing
  oracle's procedure, and the oracle's demonstrated discriminating scope (the five
  advisory caveats) simultaneously to decide whether the oracle's verdict on the harness
  result is admissible."
after: [TASK-PROC-068-08]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
perpetuating: true
opus_recommended: true   # AC-14 — Opus by construction on EVERY loop task; discovery reasoning must not inherit the chance model
ralph_loop_context:
  loop_id: PROC-068-playground-captest-loop
  iteration: 2
  context_file: 
    requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-30_impl_autonomous-test-runs-ralph/plans_and_protocols/loop_context.md
  loop_ceiling: 12
scope_description: "Iteration 2 of the ralph-driven autonomous-test-run loop (PROC-068-playground-captest-loop):
  execute exactly one autonomous capability-test run over the test_harness_app/ playground
  harness — exercise a factory skill/workflow against a harness governed artifact
  and consume the Capability-Testing oracle's verdict on the result, under the five
  mandatory advisory caveats — then perpetuate per Work Discovery."
release_description: ""
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: 970697fe-b232-417b-99f7-3d0a00bc64c7
session_account: gmail2
---
# Goal: Run One Capability-Test Over the Playground Harness (loop iteration 2)

## Objective

Execute **exactly one autonomous capability-test run over the `test_harness_app/` playground harness**,
driven by the verified perpetuating-task-creation mechanism (REQ-PROC-065-06). This is **iteration 2** of
loop `PROC-068-playground-captest-loop`, authored by iteration 1 (TASK-PROC-068-08) — it delivers the
landed capability-test run that the terminal-batch verify gate (TASK-PROC-068-09) confirms, then runs its
own Work Discovery to perpetuate or terminate.

A **capability-test run over the playground harness** means: exercise a **factory skill/workflow against a
governed artifact in the `test_harness_app/` tree** (personas, user_flows, or `rating_app` requirements),
producing a result the **Capability-Testing oracle** (the old-vs-new regression gate, REQ-PROC-073-01) can
judge, and **consume that oracle verdict under the five mandatory advisory caveats** below. Concretely
(executor discovers the exact fixture — this is the loop's "discover" step):

1. **Discover** one in-scope capability under test over the harness — e.g. form a matched old-vs-new pair
   over a harness governed artifact (run a factory skill to produce a revised version of a harness flow /
   requirement, against the version 068-07 generated), or run a generative factory workflow over a harness
   flow and treat its output as the new artifact to judge.
2. **Run** the Capability-Testing oracle on the result: the regression-gate LLM-judge procedure
   established by the disproof spike and bounded by the discriminating-maturity walk (see References).
   Record the detection/quality outcome.
3. **Consume** the verdict **under the five mandatory advisory caveats** — the verdict is advisory and
   cannot displace human judgment.

Keep the run to **one** bounded capability-test (one fixture, one oracle pass). Do not build harness
product content beyond what the single run requires.

## Background

Authored by **TASK-PROC-068-08** (iteration 1 of this loop), per its Work Discovery value gate: the
terminal-batch verify gate **TASK-PROC-068-09 AC-2** requires "≥1 autonomous capability-test run driven
over the playground via the perpetuating mechanism" — this task is that landed run. The loop's ridge
(end goal / termination condition / scope) lives in the loop-context file referenced in
`ralph_loop_context.context_file`; read it before the Work Discovery step.

The mechanism's delivered design and proof:
`../../../../requirements_management/epic_task_lifecycle/feat_perpetuating_task_creation/tasks/2026-06-19_review_discovery-authored-followup-wellformedness (completed)/plans_and_protocols/2026-06-30_02_verification_report.md`.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## References (oracle procedure — read before running)

- **Capability-Testing oracle (regression gate)**: `../../../epic_capability_testing/feat_regression_gate/requirements.md` (REQ-PROC-073-01) — old-vs-new of the same governed artifact, both run fresh under the current model.
- **Run procedure (disproof spike)**: `../../../epic_capability_testing/feat_regression_gate/tasks/2026-06-26_impl_disproof-spike-hardest-defect-pair (completed)/plans_and_protocols/2026-06-26_02_verdict_disproof-spike-go-no-go.md`.
- **Demonstrated discriminating scope (maturity walk)**: `../../../epic_capability_testing/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk (completed)/plans_and_protocols/2026-06-27_02_verdict_maturity-walk.md` §"Mandatory advisory caveats".
- **Corpus tooling**: `scripts/regression_gate/extract_ideation_corpus.py` (corpus extraction reference).

## Scope

### In Scope
- One autonomous capability-test run over the `test_harness_app/` playground harness: exercise a factory
  skill/workflow against a harness governed artifact and consume the oracle's verdict on the result.

### Out of Scope
- Building the harness app's product content beyond the single run's fixture (the layer-derivation /
  factory-skill job — TASK-PROC-068-07, done).
- Modifying the ralph or capability-testing mechanisms themselves (REQ-PROC-065-06 / REQ-PROC-073-01 — done).
- Any work outside the playground harness.

## ADVISORY caveats — MANDATORY (this task consumes oracle verdicts)

The capability-tester / oracle whose verdicts this work consumes established only a **qualitative,
advisory** discriminating scope. The five mandatory advisory caveats below MUST accompany every
downstream use of any oracle verdict produced here — including every follow-up this loop authors that
consumes an oracle verdict. Source:
`../../../epic_capability_testing/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk (completed)/plans_and_protocols/2026-06-27_02_verdict_maturity-walk.md` §"Mandatory advisory caveats".

1. **Corpus N=3 ≪ floor_n=100.** Demonstrated scope is qualitative, not statistical — the oracle *can*
   detect defects of the demonstrated kinds, not how reliably it does so at scale.
2. **Pairs above the termination point are not authoritative.** Future corpus pairs ruled "too hard"
   sit outside the demonstrated scope.
3. **Demonstrated scope is the demonstrated *set*, not a generalized capability claim.** Verdicts on
   defect kinds outside { control-flow contract violation; instruction-following semantic
   contradiction } remain advisory until extended by additional walks.
4. **Calibration (REQ-PROC-044-05) is not established.** Even within scope, verdicts are not
   Human-Judgment-Register-calibrated and cannot displace human judgment on consequential decisions.
5. **Artifact-level oracle, not behavioural.** The oracle judges artifact text without executing it;
   the stronger behavioural oracle is not exercised and its discriminating scope must be established
   separately.

## Acceptance Criteria

- [x] Exactly one autonomous capability-test run is executed over the `test_harness_app/` playground
      harness: a factory skill/workflow is exercised against a harness governed artifact and the
      Capability-Testing oracle judges the result; the detection/quality outcome is recorded to
      `plans_and_protocols/`. (FLOW-HARNESS-01 matched OLD/NEW pair, blind A/B Opus oracle, 2 swapped passes → detection 2/2; recorded in `plans_and_protocols/2026-06-30_01_protocol_captest-run-and-discovery.md`)
- [x] The oracle verdict consumed in this run carries the five mandatory advisory caveats forward (stated verbatim alongside the recorded outcome). (Protocol Part 2)
- [x] Work Discovery completed before completion: termination evaluated first; exactly one perpetuating follow-up authored or a no-op documented (see Work Discovery section) (AC-02) (NO-OP documented — apoptosis default; loop ends gracefully)
- [x] task-complete invoked (closes the task)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-08 | in_progress | Iteration 1 of this loop — authored this task; this run is the landed capability-test run its Work Discovery emitted |
| TASK-PROC-073-01 | implemented | Capability-Testing oracle (regression gate) — the mechanism this run exercises over the harness |
| TASK-PROC-068-07 | completed | 071-driven harness-middle generation — this run operates over the harness it enhanced |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-08](../2026-06-30_impl_autonomous-test-runs-ralph/goal.md) | Iteration 1 — authored this follow-up; shares loop `PROC-068-playground-captest-loop` |
| [TASK-PROC-068-09](../2026-06-30_verify_terminal-playground-batch/goal.md) | Terminal-batch verify gate — confirms ≥1 landed capability-test run; this task delivers it |
| [TASK-PROC-073-01](../../../epic_capability_testing/feat_regression_gate/requirements.md) | Capability-Testing oracle (regression gate) exercised by this run |

## Notes

- **Perpetuating follow-up, coordinator-derived.** Same shape as its predecessor TASK-PROC-068-08:
  coordinator-derived, covers-empty process task (parent REQ-PROC-068, no `target_package`). The literal
  step-E sequencing substrate (`create_orchestration_task.py --after-task`) was **not** used because that
  script creates a release-orchestration task for the active release (`target_release`) — the wrong
  artifact for this two-tree, release-unassigned process batch (REQ-PROC-068 AC-06 two-tree split). The ID
  was pre-allocated atomically via `allocate_task_id.py`, mirroring how T-orch3 (TASK-PROC-068-06) created
  the terminal batch. Rationale logged in TASK-PROC-068-08's
  `plans_and_protocols/2026-06-30_01_protocol_iteration1-work-discovery.md`.
- **Process task, no `target_package`** → surfaces to `next_tasks.py` only via
  `.claude/task_ordering_priority_override.txt` (appended when this task was authored).

## Work Discovery

Perpetuating (RALPH-loop) task; the discovery step runs under **Opus by construction**
(`opus_recommended: true`). **Before `task-complete`** (the final AC) run this ordered
procedure, then check the Work Discovery AC.

**A. Orient & test termination FIRST (AC-10, AC-17).** Read the loop-context file at
`requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-30_impl_autonomous-test-runs-ralph/plans_and_protocols/loop_context.md` (end goal, termination condition, scope, loop_ceiling). Evaluate the
**termination condition against real project state first**. If it is met, OR if
`iteration ≥ 12`, write a no-op note to `plans_and_protocols/` (state the
reason — condition met / ceiling reached), append a no-op basin row, and complete with
**no follow-up**: the loop ends gracefully.

**B. Scan minimized signals (AC-18).** Otherwise gather only **bounded, single-item**
signals within scope — never full-state dumps (oversized output can drive a repeated-query
loop): `python3 scripts/tasks/next_tasks.py` (top unblocked candidate(s) only),
`scripts/requirements/coverage_report.py` (single in-scope requirement),
`python3 scripts/tasks/top_blocked_task.py` and `scripts/requirements/check_cross_refs.py`
as needed, minimized.

**C. Value gate — decide WHETHER to author (AC-20).** Author a follow-up only when an
**external value signal** justifies it — requirement priority, active release scope, or a
persona need — never a self-referential coverage-delta. With no external value, resolve to
the documented no-op (apoptosis default): write the no-op note + basin row, complete with
no follow-up.

**D. Deduplicate — never silently terminate the loop (AC-06).** Before authoring, check for
an equivalent in-scope task:
- (a) equivalent **perpetuating** task already exists (any status) → **no-op**; the loop
  continues through that task's own discovery — cite its id in the basin row.
- (b) equivalent **non-perpetuating, `status: pending`** task → **upgrade it** (add
  `perpetuating: true`, `opus_recommended: true`, the `ralph_loop_context` block, and the
  two perpetuation ACs to ITS goal.md) rather than duplicating — safe only because it is
  pending.
- (c) equivalent **non-perpetuating, `status: in_progress`** task → do **NOT** touch it;
  create a new perpetuating task sequenced `after: [that_task_id]`.
Never mutate the goal.md of an in_progress, completed, or other-loop task. A dedup check
never silently ends the loop.

**E. Author exactly one follow-up via plan-driven creation (AC-03/05/21/22/23).** When work
is warranted and no dedup case fired:
- **Select** the highest-priority unblocked in-scope candidate from `next_tasks.py`.
- **Order**: take `after:` from `python3 scripts/tasks/propose_after.py` where it yields a
  dependency; otherwise fall back to `next_tasks.py` priority order plus an in-flight
  write-set / dependency-conflict screen (process-layer tasks usually take the fallback).
- **Size** with the instrument matched to the target domain (code-task sizing for
  `lib/`/`test/`/`integration_test/`, process/doc/script sizing otherwise), within the
  existing effort bands, under the **one-linear-follow-up ceiling**: emit exactly ONE
  right-sized unit and leave any remainder to a later iteration — never oversized, never
  branched.
- **Author** by feeding a single plan entry into `task-create` plan-driven mode. The
  follow-up is itself perpetuating (this skill, follow-up mode), an agent-chosen **existing**
  type, with the same `ralph_loop_context` and `after: [<THIS_TASK_ID>]`, sequenced via
  `scripts/tasks/create_orchestration_task.py --after-task <THIS_TASK_ID>`.

**F. Meet the per-type well-formedness bar (AC-24, AC-19).** The emitted goal.md must be
well-sized, well-scoped, well-ordered, and self-contained, judged against the externally
stated goal it serves (never its own assertion):
- impl → a cold executor can build it from goal.md + the loop-context file alone;
- explore → its research question is bounded and pre-commits to no solution;
- verification → it carries the subject-independent-oracle clause (REQ-PROC-058).

**G. Record & complete.** Append the outcome (follow-up id or no-op) to the loop-context
basin, then check the Work Discovery AC and invoke `task-complete` (the final AC). Under
`CLAUDE_AUTOMATED_MODE=1`, follow `claude-automated-mode`; the follow-up enters the normal
task queue with no gate bypass (AC-07).

Full contract: REQ-PROC-065-06 AC-02..AC-25.
