---
task_id: TASK-PROC-068-02
type: impl
orchestration_task: true
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-27
completed: 2026-06-27
session_completed_at: 2026-06-27T08:20:34Z
effort: M
created: 2026-06-26
expected_tool_calls: 60
skill_chain_depth: 4
after: [TASK-PROC-073-01-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "First gap-filler orchestration task: read the disproof-spike go/no-go; on GREEN author the deferred REQ-PROC-073-01 slice (AC-01 corpus, AC-03 maturity) + create the skeleton/corpus/maturity batch + the next orchestration task; on RED create the stop-loss fallback. Re-point the finalization terminus and append every created task to the visibility override."
release_description: ""
opus_recommended: true  # reason: explicit decision task (GREEN/RED stop-loss branch) + authors a deferred requirement slice + wires a task batch with after-edges — synthesis across requirement + graph that cannot be split
writes_requirements: false  # orchestration/impl task; visibility is ensured via the override file (not this flag, which is explore-only). On GREEN it does author the deferred REQ-PROC-073-01 AC-01/03 slice — see body step 2a.
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: cf1ef47f-1bb8-48aa-8377-7a4c1b4cfd33
session_account: gmail2
---
# Goal: Orchestrate the oracle build-out after the disproof spike

## Objective

You are the **first gap-filler** in the self-propagating orchestration chain that builds out the
Capability-Testing Oracle (REQ-PROC-073) on the Skill-Test Playground substrate (REQ-PROC-068). You
run only once the disproof spike (TASK-PROC-073-01-01) has a go/no-go verdict. Your job is to read
that verdict and create the next batch of real work — wiring its `after:` edges to the now-known
outcome — and to create the next orchestration task for the following gap, so the pattern propagates
and never leaves a dangling edge to a non-existent task.

You do NOT implement the build-out yourself. You author the requirement slice the next batch needs,
create the tasks, wire the graph, and hand off.

## Background

The build order lives **entirely in the task graph** (`after:` edges) — no side file carries
ordering. `.claude/task_ordering_priority_override.txt` carries only **visibility**: these process
tasks have no `target_package`, so they surface to `next_tasks.py` only when listed there. (Per the
developer directive in step 4, every task you create must be appended to it.)

The full chain, the stop-loss branches, the four first-build gates (SG-01..04), and the parked
downstream design tasks (071-02 layer-derivation, 065-06-08 ralph) are specified in — read before
acting, do not re-derive:
`../2026-06-11_explore_llm-verifiable-open-ended-skill-tests/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## What to do

1. **Read the spike outcome** — TASK-PROC-073-01-01's go/no-go verdict + cost evidence in its
   `plans_and_protocols/`.

2. **GREEN (detected, and cheaper than manual review):**
   a. **Author the deferred REQ-PROC-073-01 slice** via `requ-explore`: AC-01 (matched-pair corpus)
      and AC-03 (discriminating-maturity walk) in full — reopen the `## Deferred` items now that the
      spike has proved the cost premise.
   b. **Create the next batch** via `task-derive-from-requ` / `task-create` (plan §"Stage 1"), wiring
      `after:` edges:
      - **T-skeleton** (impl) — walking skeleton deploy→run-as-cwd→git-reset→cost; bake in SG-01 launch adapter + SG-04 OS-containment.
      - **T-corpus** (impl) — seed matched fixtures from ideation git history (covers AC-01).
      - **T-maturity** (verify, `after: [T-skeleton, T-corpus]`, `interactive_required: true`) — the developer-gated, easiest-first batch walk (covers AC-03).
      - **T-orch2** (`orchestration_task: true`, `after: [T-maturity]`) — the next gap-filler.
   c. **Re-point the terminus**: set `TASK-PROC-068-03` (T-finalize) `after:` to the new live frontier
      (T-orch2), so the edge to playground-finalization stays unbroken.

3. **RED (not detected, or not cheaper than manual review):**
   a. Document the stop-loss in `plans_and_protocols/`.
   b. Create **T-fallback** (impl) — build the layer-deriv / ralph path with manual testing instead of
      the oracle; the oracle build-out ends here.
   c. Re-point `TASK-PROC-068-03` (T-finalize) `after:` to T-fallback.

4. **DEVELOPER DIRECTIVE — visibility propagation (2026-06-26):** every task you create (this batch,
   and — by carrying this same instruction into T-orch2's goal.md — every task the chain creates
   thereafter) MUST be appended to `.claude/task_ordering_priority_override.txt` with a one-line
   comment + the task ID, so it surfaces to the orchestrator. This rule self-propagates: T-orch2 /
   T-orch3 carry it forward to the tasks they create.

## Acceptance Criteria

- [x] The spike verdict was read and the GREEN or RED branch taken accordingly — verdict = 🟢 GREEN (developer-approved); GREEN branch taken
- [x] (GREEN) the deferred REQ-PROC-073-01 AC-01/AC-03 slice is authored; the skeleton/corpus/maturity batch + T-orch2 are created with correct `after:` edges — AC section authored in feat_regression_gate/requirements.md; T-skeleton=068-04, T-corpus=073-01-02, T-maturity=073-01-03 (after: [068-04, 073-01-02]), T-orch2=068-05 (after: [073-01-03])
- [x] (RED) the stop-loss is documented and T-fallback created — N/A: GREEN branch taken, RED path not applicable
- [x] T-finalize (TASK-PROC-068-03) `after:` is re-pointed to the new live frontier — re-pointed [TASK-PROC-068-02] → [TASK-PROC-068-05]
- [x] every task created by this task is appended to `.claude/task_ordering_priority_override.txt` — all 4 IDs appended under the Stage 1 GREEN batch section
- [x] a successor orchestration task (T-orch2) exists on GREEN, or the chain is explicitly terminated on RED — T-orch2 (TASK-PROC-068-05, orchestration_task) created

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-073-01-01 | pending | The disproof spike — its go/no-go is this task's input |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-073-01-01](../../../epic_capability_testing/feat_regression_gate/tasks/2026-06-26_impl_disproof-spike-hardest-defect-pair/goal.md) | Predecessor — reads its go/no-go verdict |
| [TASK-PROC-068-03](../2026-06-26_impl_finalize-playground-terminus/goal.md) | The finalization terminus this task re-points to the live frontier |

## Notes

This task hand-instantiates the perpetuating orchestration pattern (the general automated version —
the ralph loop, REQ-PROC-065-06 — is not yet built); it is itself a real exercise of that pattern.
`orchestration_task: true` flags it as a coordinator (no direct deliverable); `covers` is empty by
design — coverage of REQ-PROC-073-01 AC-01/AC-03 lands on the tasks this one creates.
