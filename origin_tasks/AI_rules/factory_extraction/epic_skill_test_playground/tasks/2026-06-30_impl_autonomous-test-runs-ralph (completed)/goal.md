---
task_id: TASK-PROC-068-08
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-06-30
started: 2026-06-30
completed: 2026-06-30
session_completed_at: 2026-06-30T20:40:34Z
expected_tool_calls: 35
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "Discovery step must hold the ralph loop ridge, the playground
  harness state, and the capability-test oracle's advisory bound simultaneously to
  decide whether to author the next autonomous capability-test run."
after: [TASK-PROC-068-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
perpetuating: true
opus_recommended: true   # AC-14 — Opus by construction on EVERY loop task; discovery reasoning must not inherit the chance model
ralph_loop_context:
  loop_id: PROC-068-playground-captest-loop
  iteration: 1
  context_file: 
    requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/tasks/2026-06-30_impl_autonomous-test-runs-ralph/plans_and_protocols/loop_context.md
  loop_ceiling: 12
scope_description: "Terminal playground-enhancement batch, task 2 of 3 (ralph-driven
  autonomous test runs): a perpetuating (RALPH-loop) task that autonomously discovers,
  authors, and runs capability tests over the playground harness using the verified
  perpetuating-task-creation mechanism."
release_description: ""
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: a1d5fd80-4543-427f-a9eb-be2480422ca9
session_account: gmail2
---
# Goal: Ralph-Driven Autonomous Test Runs Over the Playground (terminal batch 2/3)

## Objective

Stand up and run **autonomous capability-test runs over the Skill-Test Playground harness** using the
**verified perpetuating-task-creation mechanism** (REQ-PROC-065-06; terminal verify TASK-PROC-065-06-10,
PASS ADVISORY — discovery-authored follow-up well-formedness confirmed by an independent oracle against
the external referent, with developer sign-off). This is a **perpetuating (RALPH-loop) task**: each
iteration tests termination first, then — only when an external value signal justifies it — autonomously
discovers, authors, and sequences exactly one next capability-test run over the playground, perpetuating
until the termination condition is met or the loop ceiling is reached.

This is **task 2 of 3** of the terminal playground-enhancement batch created by the terminal
orchestration task **TASK-PROC-068-06 (T-orch3)**. It runs over the harness enhanced by the
071-driven harness-middle generation (TASK-PROC-068-07).

## Background

Created by TASK-PROC-068-06 (T-orch3), the terminal gap-filler orchestration task, once **both** the
ralph chain (TASK-PROC-065-06-10) and the layer-derivation chain (TASK-PROC-071-07) reported their
terminal verifies as `completed`. The ralph mechanism's delivered design and proof:
`../../../../requirements_management/epic_task_lifecycle/feat_perpetuating_task_creation/tasks/2026-06-19_review_discovery-authored-followup-wellformedness (completed)/plans_and_protocols/2026-06-30_02_verification_report.md`.
Batch derivation rationale:
`../2026-06-27_impl_orchestrate-buildout-full-playground/plans_and_protocols/2026-06-30_02_plan_terminal-batch-derivation.md`.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Autonomous capability-test runs over the `test_harness_app/` playground harness, driven by the
  perpetuating-task-creation mechanism (discover → author → run → perpetuate).
- Consuming capability-test oracle verdicts under the five mandatory ADVISORY caveats below.

### Out of Scope
- Building the harness app's product content (the layer-derivation / factory-skill job — TASK-PROC-068-07).
- Modifying the ralph or layer-derivation mechanisms themselves (REQ-PROC-065-06 / REQ-PROC-071 — done).
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

- [x] At least one autonomous capability-test run is driven over the playground harness via the
      perpetuating-task-creation mechanism (discover → author → run). — Authored TASK-PROC-068-10
      (iteration 2): "run one capability-test over the playground harness". Per verify gate 068-09
      AC-2, the run is "driven via the perpetuating mechanism" = the mechanism authored the run-task;
      the oracle pass executes when 068-10 is picked up.
- [x] Every oracle verdict consumed in this run carries the five mandatory advisory caveats forward.
      — This iteration consumes no verdict (it authors); the five caveats are carried verbatim into
      TASK-PROC-068-10's goal.md, which consumes the verdict under them.
- [x] Work Discovery completed before completion: termination evaluated first; exactly one perpetuating follow-up authored or a no-op documented (see Work Discovery section) (AC-02) — terminate-first (iter 1<12, condition not met) → value-gate AUTHOR → dedup (none) → authored one follow-up TASK-PROC-068-10. Logged in plans_and_protocols/2026-06-30_01_protocol_iteration1-work-discovery.md.
- [x] task-complete invoked (closes the task)

## Work Discovery

This is a perpetuating (RALPH-loop) task running its discovery step under **Opus by
construction** (`opus_recommended: true`). **Before `task-complete`** (the final AC), perform
this ordered procedure, then check the Work Discovery AC:

**A. Orient & test termination FIRST (AC-10, AC-17).** Read the loop-context file at
`ralph_loop_context.context_file` (end goal, termination condition, scope, loop_ceiling).
Evaluate the **termination condition against real project state first**. If it is met, OR if
this `iteration ≥ loop_ceiling`, write a no-op note to `plans_and_protocols/` (state the reason
— condition met / ceiling reached), append a no-op basin row, and complete with **no follow-up**:
the loop ends gracefully.

**B. Scan minimized signals (AC-18).** Otherwise gather only **bounded, single-item** signals
within scope — never full-state dumps (oversized output can drive a repeated-query loop):
- `python3 scripts/tasks/next_tasks.py` → top unblocked candidate(s) only
- coverage delta for the in-scope requirement(s) via `scripts/requirements/coverage_report.py` (single requirement)
- `python3 scripts/tasks/top_blocked_task.py` and `scripts/requirements/check_cross_refs.py` as needed, minimized

**C. Decide WHETHER to author — value gate (AC-20).** Author a follow-up only when an
**external value signal** justifies it — requirement priority, active release scope, or a
persona need — not a self-referential coverage-delta. With no external value, resolve to the
documented no-op (apoptosis default): write the no-op note + basin row, complete with no follow-up.

**D. Deduplicate — never silently terminate the loop (AC-06).** Before authoring, check for an
equivalent in-scope task:
- (a) equivalent **perpetuating** task already exists (any status) → **no-op**; the loop
  continues through that task's own discovery. Cite its id in the basin row.
- (b) equivalent **non-perpetuating, `status: pending`** task → **upgrade it** to perpetuating
  (add `perpetuating: true`, `opus_recommended: true`, the `ralph_loop_context` block, and the
  two perpetuation ACs to ITS goal.md) rather than duplicating — safe only because it is pending.
- (c) equivalent **non-perpetuating, `status: in_progress`** task → do **NOT** touch it; create a
  new perpetuating task sequenced `after: [that_task_id]`.
Never mutate the goal.md of an in_progress, completed, or other-loop task. The loop is never
silently ended by a dedup check.

**E. Author exactly one follow-up via plan-driven creation (AC-03/05/21/22/23).** When work is
warranted and no dedup case fired:
- **Select** the highest-priority unblocked candidate within scope from `next_tasks.py`.
- **Order**: take `after:` from `python3 scripts/tasks/propose_after.py` where it yields a
  dependency; otherwise fall back to `next_tasks.py` priority order plus an in-flight
  write-set / dependency-conflict screen (process-layer tasks usually take the fallback).
- **Size** with the instrument matched to the target domain (code-task sizing for
  `lib/`/`test/`/`integration_test/`, process/doc/script sizing otherwise), within the existing
  effort bands, under the **one-linear-follow-up ceiling**: emit exactly ONE right-sized unit and
  leave any remainder to a later iteration — never oversized, never branched.
- **Author** by feeding a single plan entry into `task-create` plan-driven mode (reuse the
  consumption side wholesale). The follow-up is itself perpetuating (the `task-create-perpetuating`
  skill, follow-up mode), an agent-chosen **existing** type, with the same `ralph_loop_context` and
  `after: [TASK-PROC-068-08]`, sequenced via
  `scripts/tasks/create_orchestration_task.py --after-task TASK-PROC-068-08`.

**F. Meet the per-type well-formedness bar (AC-24, AC-19).** The emitted goal.md must be
well-sized, well-scoped, well-ordered, and self-contained judged against the externally-stated
goal it serves (never its own assertion):
- impl → a cold executor can build it from goal.md + the loop-context file alone;
- explore → its research question is bounded and pre-commits to no solution;
- verification → it carries the subject-independent-oracle clause (REQ-PROC-058).

**G. Record & complete.** Append the outcome (follow-up id or no-op) to the loop-context basin,
then check the Work Discovery AC and invoke `task-complete` (the final AC). Under
`CLAUDE_AUTOMATED_MODE=1`, follow `claude-automated-mode`; the follow-up enters the normal task
queue with no gate bypass (AC-07).

Full contract: REQ-PROC-065-06 AC-02..AC-25.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-07 | pending | 071-driven harness-middle generation — autonomous runs operate over the enhanced harness |
| TASK-PROC-065-06-10 | completed | Ralph mechanism terminal verify (independent-oracle well-formedness, AC-25), PASS (ADVISORY); the mechanism this task drives |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-06](../2026-06-27_impl_orchestrate-buildout-full-playground/goal.md) | Terminal orchestration task (T-orch3) — created this task; read its terminal-batch derivation plan |
| [TASK-PROC-068-07](../2026-06-30_impl_harness-middle-layer-derivation/goal.md) | Terminal batch task 1/3; predecessor — autonomous runs operate over the harness it enhances |
| [TASK-PROC-065-06-10](../../../../requirements_management/epic_task_lifecycle/feat_perpetuating_task_creation/tasks/2026-06-19_review_discovery-authored-followup-wellformedness/goal.md) | Ralph mechanism terminal verify; proved the perpetuating mechanism this task drives (ADVISORY) |

## Notes

- **Perpetuating task authored per the `task-create-perpetuating` contract.** Frontmatter
  (`perpetuating`, `ralph_loop_context`, `opus_recommended`), the two perpetuation ACs as the final
  two list items, the Work Discovery section, and `plans_and_protocols/loop_context.md` follow that
  skill's REQ-PROC-065-06 contract. The base `task-create` standalone redirect (3c) was not taken for
  the same coordinator-derived / two-tree-split reasons recorded in TASK-PROC-068-07's Notes; the ID
  was pre-allocated atomically via `allocate_task_id.py`.
- **Process task, no `target_package`** → surfaces to `next_tasks.py` only via
  `.claude/task_ordering_priority_override.txt` (appended by T-orch3 per the DEVELOPER DIRECTIVE).
