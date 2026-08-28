---
task_id: TASK-PROC-068-26
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-07-19
session_completed_at: 2026-07-19T11:15:38Z
started: 2026-07-14
effort: M
created: 2026-07-14
expected_tool_calls: 45
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold the approved anchors and the fixed layer-derivation mechanism together to derive a single conformant materialization anchor (forward, from scenarios) as one unit."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Derive ONLY the harness materialization layer (single product_materialization.md / MAT anchor in test_harness_app) via a deployed build-mode run, forward from the approved scenarios (fixed_layers=[persona, scenario]). Upstream prerequisite for 068-12."
release_description: ""
opus_recommended: true   # reason: synthesis — terminal materialization derivation holding approved anchors + fixed mechanism together
writes_requirements: false
requirements_version:
  commit: e0f9d317
  file: ../requirements.md
session_id: 45b4b247-f46f-4843-a9c4-128a9db225a4
session_account: web
session_last_run: 2026-07-19T11:04:22.119060+00:00
---
# Goal: Derive the Harness Materialization Layer (Forward, from Scenarios)

## Objective

Derive **only** the harness materialization layer — the single project-singleton
`product_materialization.md` (`MAT-NNN`) anchor under `test_harness_app/` — from the approved
conformant scenarios, using the fixed layer-derivation mechanism as a **deployed build-mode run**.

This is **phase 1** of the harness middle-layer re-derivation. It isolates the materialization
layer into its own run so that the successor **TASK-PROC-068-12** can then derive flows (now
skill-gated on the present materialization) and requirements against a materialization anchor that
already exists. 068-12 has this task in its `after:` (this task **blocks** 068-12).

## Background

Since 068-12 was first planned, a new **materialization layer** (REQ-PROC-074 / REQ-PROC-075)
landed between Scenario and Flow and became a hard gate: `ux-flow-draft` refuses to author flows
without a materialization artifact, and `layer-derivation-start`/`-resume` enforce a materialization
precondition on every invocation. The harness currently has **no** materialization artifact, so the
flow+requirement derivation cannot run until this anchor exists.

**Configuration — forward from scenarios (`fixed_layers = [persona, scenario]`).** The materialization
is derived **top-down from the approved scenarios** via `scenario_materialization → ux-write-materialization`.

> Decision history (2026-07-14): an earlier draft fixed `code` as a bottom anchor to exercise the
> **bidirectional hinge**. Investigation of REQ-PROC-071/074-03 showed this is hollow: the
> reverse-derivation-over-existing-product feature (`feat_artifact_mutation`, REQ-PROC-071-07) is
> **deferred/unbuilt**, there is **no `code` anchor extractor** (only `explicit_test_targets`,
> `materialization`, `flow_coverage` are registered), and by design the mechanism **never reads
> source code** — "what the app does" enters as the human-authored personas/scenarios (the brownfield
> signal), never from `test_harness_app/src`. Fixing `code` only flipped a direction label without
> feeding any real code in. The developer chose **Option A: drop `code`**, plain forward derivation.

## How to Approach This

Run as a **deployed build-mode run** (`scripts/playground/build.py`), the same resumable wrapper
068-12 uses — deploy the factory into a durable out-of-project git-backed copy, seed it from
`test_harness_app/`, and run the inner derivation there; harvest back only on verified completion.

1. Author an **in-copy** layer-derivation spec with `fixed_layers = [persona, scenario]` (a
   plan-validated draft already lives at
   `plans_and_protocols/harness_materialization_derivation_spec.incopy.json`). The
   `scenario_materialization` boundary dispatches `ux-write-materialization`.
2. Author the build-mode **driver prompt**: the child runs `layer-derivation-start` with this spec,
   authors the `scenario_materialization` boundary via `ux-write-materialization`, and **stops** (do
   not proceed to lower pairs). `layer_pair=None` on that unit is expected — the driver names the skill
   (the proven pattern). Ensure the `unit_task_req_path` bucket exists in the seeded copy.
3. On any mid-run interruption the copy is preserved; re-attach via `playground-build-resume`
   (unblocked by the completed 068-23 fresh-session-id fix). Harvest only on verified completion.
4. Honour the two-tree split: all product content under `test_harness_app/requirements_*`.

## Scope

### In Scope
- Derive the single harness materialization anchor via `ux-write-materialization` through the fixed
  mechanism, forward from the approved scenarios (`fixed_layers = [persona, scenario]`).
- Validate the resolved span structure via the `plan` step before spending budget.

### Out of Scope
- Flows, requirements, tasks, code layers (flows + requirements are TASK-PROC-068-12).
- Any change to the mechanism itself.
- Personas / scenarios (approved anchors — TASK-PROC-068-11).
- Reading/anchoring on `test_harness_app/src` source code — not supported by the mechanism (would be a
  new `code` extractor + the deferred REQ-PROC-071-07).

## Acceptance Criteria

- [ ] AC-1: `product_materialization.md` (`MAT-NNN`) authored under
      `test_harness_app/requirements_user_needs/product_materialization/` via the real
      `ux-write-materialization` path; provenance resolves (`check_materialization_provenance.py`
      prints `OK`).
- [ ] AC-2: The derivation ran as a deployed build-mode run with `fixed_layers=[persona, scenario]`,
      authoring materialization **forward** from the scenarios via the `scenario_materialization`
      boundary.
- [ ] AC-3: Only the materialization layer was authored — no flows, requirements, or tasks were
      produced in this run.
- [ ] AC-4: All product content lives under `test_harness_app/requirements_*` (two-tree split
      honoured).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-11 | completed | Approved conformant anchors (personas + scenarios) |
| TASK-PROC-074-03-04 | completed | Materialization precondition in layer-derivation start/resume |
| TASK-PROC-074-01-03 | completed | `ux-write-materialization` authoring skill |
| TASK-PROC-068-23 | completed | Build-resume fresh-session-id fix (enables resumable run) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-12](../2026-07-01_impl_harness-middle-rederive/goal.md) | Successor — this task is its upstream materialization prerequisite; 068-12 lists it in `after:` |

## Notes

- Coordinator-derived, covers-empty process task (no `target_package`) — surfaces via the priority
  override (`.claude/task_ordering_priority_override.txt`).
- Phase 1 of the harness middle-layer re-derivation; phase 2 (flows + requirements) is 068-12.
- Spec dry-run + the code-anchor investigation are recorded in
  `plans_and_protocols/2026-07-14_01_plan_spec-dry-run-findings.md`.
