---
task: TASK-PROC-068-05 (T-orch2)
date: 2026-06-27
session: a3f14541 (gmail)
step: 1 — plan (main session synthesis)
---

# Plan — Stage-2 batch creation (T-orch2)

## Gate input — maturity verdict (read, cited, not re-derived)

Source: `…/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk (completed)/plans_and_protocols/2026-06-27_02_verdict_maturity-walk.md`

- **Verdict: GREEN** for proceeding with the Stage-2 batch.
- Demonstrated discriminating scope = `{ pair-002, pair-003 }` (both caught, mechanism-precise, position-robust), under a tightened mechanism-and-symptom-precision rubric. `pair-001` admission-excluded (no behavioural symptom). No termination boundary triggered (corpus exhausted at rank 3).
- **Verdicts are ADVISORY, not authoritative** — corpus N=3 << floor_n=100; paired-fixture validity floor unmet; HJR calibration (REQ-PROC-044-05) not established. Five mandatory advisory caveats (verdict §"Mandatory advisory caveats") MUST accompany every downstream use.
- The verdict directs T-orch2 to: create T-unblock-071-02, T-unblock-065-06-08, T-orch3; and to **propagate the advisory caveats** into the goal.md of every task it creates that (transitively) consumes oracle verdicts.

## Parent requirements (verified)

- TASK-PROC-071-02 → parent `REQ-PROC-071` (`…/epic_layer_derivation/requirements.md`). Status `in_progress`, parked in `automation/pending_feedback/TASK-PROC-071-02/`.
- TASK-PROC-065-06-08 → parent `REQ-PROC-065-06` (`…/feat_perpetuating_task_creation/requirements.md`). Status `in_progress`, parked in `automation/pending_feedback/TASK-PROC-065-06-08/`.
- T-orch3 → parent `REQ-PROC-068`.

## Creation-mode decision (avoids the redirect trap)

Both REQ-PROC-071 and REQ-PROC-065-06 have trackable ACs with uncovered ACs. Creating the two
developer-gate unblock tasks as **standalone** impl tasks would trip `task-create` §3c automated
redirect → `task-derive-from-requ` (always-redirect in automated mode). That is wrong: these are
**coordinator / developer-gate tasks with empty `covers`**, not AC-decomposition tasks. Fix: create
all three via `task-create` **plan-driven mode** (pass a plan entry), which skips §3c redirect, §3b
coverage-asking, §4 confirmation. Then edit each goal.md to its bespoke body + `interactive_required`.

## Tasks to create (3)

1. **T-unblock-071-02** — developer-gate for TASK-PROC-071-02 (layer-derivation design).
   parent REQ-PROC-071, type impl, `after: []`, `interactive_required: true`, covers [].
   Surfaces the parked `pending_feedback/TASK-PROC-071-02/question.md` 10-decision gate with the
   pre-answers (`…/epic_layer_derivation/…/2026-06-26_02_developer_pre-answers-parked.md`) as DRAFT.
   Decision #10 (go/no-go) explicitly withheld; #1,#2,#4,#7,#9 still open. **Session MUST NOT fabricate
   `answer.md`.** Carry advisory-caveat pointer (the unblocked layer-deriv chain runs against the
   advisory-scoped tester).

2. **T-unblock-065-06-08** — developer-gate for TASK-PROC-065-06-08 (ralph design).
   parent REQ-PROC-065-06, type impl, `after: []`, `interactive_required: true`, covers [].
   Surfaces parked `pending_feedback/TASK-PROC-065-06-08/question.md` (4-decision synthesis-approval
   gate; synthesis at `…/feat_perpetuating_task_creation/…/2026-06-19_01_synthesis_discovery-agent-authoring-contract.md`) as DRAFT. **Session MUST NOT fabricate `answer.md`.** Same advisory caveat pointer.

3. **T-orch3** — next gap-filler orchestration task.
   parent REQ-PROC-068, type impl, `orchestration_task: true`, covers [], opus_recommended: true.
   `after: [T-unblock-071-02, T-unblock-065-06-08]` (conservative placeholder; TASK-PROC-071-02 /
   TASK-PROC-065-06-08 must re-point it forward to their terminal verify tasks when they emit chains).
   Goal: once layer-deriv + ralph chains complete, derive full playground enhancements (071-driven
   harness-middle generation; ralph-driven autonomous test runs); create terminal batch; create NO
   successor orchestration task — chain ends. **Carries the DEVELOPER DIRECTIVE forward verbatim** and
   the advisory caveats.

## Post-creation wiring

- **Re-point T-finalize (TASK-PROC-068-03)**: `after: [TASK-PROC-068-05]` → `after: [<T-orch3 ID>]`;
  update Dependencies table + Related Tasks row + Notes wording to reference T-orch3 (keep the
  "re-pointed forward by each orchestration task" framing).
- **Append to `.claude/task_ordering_priority_override.txt`**: all 3 new IDs under a new
  "Stage-2 batch (2026-06-27, from T-orch2/TASK-PROC-068-05)" section, following existing comment style.
  Also update the T-orch2 comment line (currently `after: T-maturity`) — it stays; add the Stage-2 section.

## Execution

Delegated to one background subagent (isolates 3× plan-driven `task-create` from main context;
terminal closed loop; matches the T-orch1 precedent where a subagent created the whole batch).
Agent persists a batch-creation protocol with its agent ID and returns the allocated IDs + wiring summary.
