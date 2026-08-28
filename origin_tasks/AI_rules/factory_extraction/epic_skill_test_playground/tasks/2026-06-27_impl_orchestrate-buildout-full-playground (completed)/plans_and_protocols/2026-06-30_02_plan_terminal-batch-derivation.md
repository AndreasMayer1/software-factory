---
task: TASK-PROC-068-06 (T-orch3, terminal)
session: 2ebbd3af-83e1-48c9-9d1d-3120d6b5d3c6
date: 2026-06-30
model: Opus 4.8
step: 2 — both chains verified → derive + create the terminal playground-enhancement batch
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - task-create
---

# Plan — Terminal playground-enhancement batch derivation (T-orch3)

## Readiness — both chain outcomes now available (the deferral in step 1 is resolved)

| Half | Terminal verify | Status | Outcome consumed |
|------|-----------------|--------|------------------|
| Layer-derivation | TASK-PROC-071-07 (R1 epic re-capstone) | completed | **PASS (ADVISORY)** — mechanism reconstructed a *physically-deleted* real flow layer to the EXACT canonical oracle (coverage closed, minimality held, COVERAGE_FIXPOINT); full V1–V9 + 5 invariants GREEN simultaneously; cross-process V8 span. Source: `…/epic_layer_derivation/tasks/2026-06-27_impl_re-capstone-epic-layer-derivation-end-to-end (completed)/plans_and_protocols/2026-06-28_02_protocol_re-capstone-results.md` |
| Ralph | TASK-PROC-065-06-10 (subject-independent verify, AC-25) | completed | **PASS (ADVISORY)** — discovery-authored follow-up `goal.md` confirmed well-formed by an oracle independent of the producing run, against the external referent, per the impl per-type bar (not schema-validity alone), with developer sign-off. Source: `…/feat_perpetuating_task_creation/tasks/2026-06-19_review_discovery-authored-followup-wellformedness (completed)/plans_and_protocols/2026-06-30_02_verification_report.md` |

Step-1 deferral (`2026-06-30_01_protocol_ralph-half-repoint-deferral.md`) re-pointed the ralph half to
065-06-10 and re-blocked Stage 3 until the ralph chain was *verified, not merely emitted*. That
condition is now met: both terminal verifies are `completed`, so the terminal batch can be derived
from both delivered designs as one coherent unit.

## What the two delivered designs make possible (the batch shape)

**071-driven harness-middle generation.** The layer-derivation mechanism (fixpoint_loop +
coverage_delta + `backfill_orchestration` CLI) is proven to regenerate a missing artifact layer from
its neighbour anchors to the canonical oracle. Applied to the playground's own artifact stack
(personas → scenarios → flows → requirements → tasks → code in `test_harness_app/`), it can generate
the **middle layers** of the harness from the anchored endpoints — i.e. the harness's middle is
mechanically derivable, not hand-authored.

**ralph-driven autonomous test runs.** The perpetuating-task-creation mechanism (ralph loop:
`task-create-perpetuating`, `ralph_loop_context`, the Work Discovery step, and discovery-authored
follow-ups whose well-formedness is confirmed by an independent oracle) drives **autonomous**
capability-test runs over the playground: each iteration discovers the next capability test to run,
authors it, runs it against the harness, and perpetuates until its termination condition.

## Terminal batch (3 tasks) — wiring

1. **T-harness-middle** (impl) — 071-driven harness-middle generation. `after: []` (both chains done).
2. **T-autonomous-runs** (impl, perpetuating) — ralph-driven autonomous capability-test runs over the
   playground. `after: [<T-harness-middle>]` (runs over the enhanced harness).
3. **T-batch-verify** (verify) — gates after both impl tasks; verifies the terminal playground
   enhancements landed and the build-out is functionally complete. **This is the new live frontier**
   that T-finalize (TASK-PROC-068-03) re-points its `after:` to.

All three **consume oracle verdicts** → all three MUST carry the five mandatory advisory caveats
(AC #5). All three are process tasks (parent REQ-PROC-068, no `target_package`) → all three MUST be
appended to `.claude/task_ordering_priority_override.txt` (DEVELOPER DIRECTIVE).

**NO successor orchestration task** — this is the terminal orchestration task; the chain ends here.
The directive's self-propagation ends with this terminal batch's tasks (each still appended to the
override file).

## The five mandatory advisory caveats (carried verbatim into each created task)

Source: `…/epic_capability_testing/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk (completed)/plans_and_protocols/2026-06-27_02_verdict_maturity-walk.md` §"Mandatory advisory caveats":

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

## After creating the batch

- Re-point T-finalize (TASK-PROC-068-03) `after:` `[TASK-PROC-068-06]` → `[<T-batch-verify id>]`;
  update its Dependencies + Related Tasks rows, keeping the "re-pointed forward by each orchestration
  task" wording.
- Append all three new task IDs to `.claude/task_ordering_priority_override.txt`.
- Create NO successor orchestration task.
