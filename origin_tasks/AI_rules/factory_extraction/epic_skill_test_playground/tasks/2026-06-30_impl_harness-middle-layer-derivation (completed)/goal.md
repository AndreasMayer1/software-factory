---
task_id: TASK-PROC-068-07
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
session_completed_at: 2026-06-30T20:22:54Z
expected_tool_calls: 35
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "Must hold the layer-derivation mechanism's contract (fixpoint_loop/coverage_delta/backfill_orchestration CLI) and the playground harness's artifact stack simultaneously to drive middle-layer generation from anchored endpoints."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Terminal playground-enhancement batch, task 1 of 3 (071-driven harness-middle generation): apply the verified layer-derivation mechanism to generate the middle artifact layers of the test-harness app's stack from its anchored endpoints."
release_description: ""
opus_recommended: true   # reason: synthesis that cannot be split — holds the layer-derivation mechanism contract + the harness artifact stack at once; consumes ADVISORY oracle verdicts
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: d792b971-10d2-48d2-8a00-fa27eb6cc8c7
session_account: web
---
# Goal: 071-Driven Harness-Middle Generation (terminal batch 1/3)

## Objective

Apply the **verified layer-derivation mechanism** (REQ-PROC-071, terminal verify TASK-PROC-071-07,
PASS ADVISORY) to **generate the middle artifact layers of the Skill-Test Playground harness's stack**
from its anchored endpoints. The harness's product-definition stack (in the `test_harness_app/` tree)
is layered `personas → scenarios → flows → requirements → tasks → code`; this task demonstrates that
the **middle** of that stack is mechanically derivable from anchored neighbours rather than
hand-authored, using the same mechanism that reconstructed a physically-deleted real layer to its
canonical oracle (coverage-closed, minimal, COVERAGE_FIXPOINT).

This is **task 1 of 3** of the terminal playground-enhancement batch created by the terminal
orchestration task **TASK-PROC-068-06 (T-orch3)**. The batch is the genuine end of the
Capability-Testing Oracle build-out chain.

## Background

Created by TASK-PROC-068-06 (T-orch3), the terminal gap-filler orchestration task, once **both** the
layer-derivation chain (TASK-PROC-071-07) and the ralph chain (TASK-PROC-065-06-10) reported their
terminal verifies as `completed`. The mechanism's delivered design and proof:
`../../../epic_layer_derivation/tasks/2026-06-27_impl_re-capstone-epic-layer-derivation-end-to-end (completed)/plans_and_protocols/2026-06-28_02_protocol_re-capstone-results.md`.
Batch derivation rationale:
`../2026-06-27_impl_orchestrate-buildout-full-playground/plans_and_protocols/2026-06-30_02_plan_terminal-batch-derivation.md`.

The harness instrument spec and the two-tree split (factory-tree spec vs. `test_harness_app/` product
definition): `../requirements.md`.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Use the layer-derivation mechanism (`fixpoint_loop` + `coverage_delta` + the `backfill_orchestration`
  CLI) to generate the middle layers of the harness's artifact stack from its anchored endpoints.
- Verify each generated layer closes coverage against its neighbour anchors and stays minimal
  (no invented artifacts), terminating in COVERAGE_FIXPOINT, exactly as the mechanism's terminal
  verify demonstrated.
- Operate on the `test_harness_app/` tree (the product-definition tree), honoring the two-tree split.

### Out of Scope
- Modifying or re-verifying the layer-derivation mechanism itself (REQ-PROC-071 — done, ADVISORY).
- Authoring harness *product* content by hand in the factory tree (AC-06: product definition lives in
  `test_harness_app/`, authored by the factory skills/mechanisms).
- Autonomous capability-test runs (terminal batch task 2/3, TASK-PROC-068-08).

## ADVISORY caveats — MANDATORY (this task consumes oracle verdicts)

The capability-tester / oracle whose verdicts this work consumes established only a **qualitative,
advisory** discriminating scope. The five mandatory advisory caveats below MUST accompany every
downstream use of any oracle verdict produced here. Source:
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

- [x] The layer-derivation mechanism is applied to the harness's artifact stack to generate ≥1 middle
      layer from its anchored endpoints (not hand-authored). — FLOW layer reconstructed from empty draft
      by the fixpoint loop against scenario+requirement anchors (PASS ADVISORY).
- [x] Each generated layer closes coverage against its neighbour anchors and stays minimal (no invented
      artifacts), terminating in COVERAGE_FIXPOINT. — is_closed=True, invented=∅, COVERAGE_FIXPOINT.
- [x] Work stays within the `test_harness_app/` tree, honoring the two-tree split (no harness product
      content authored in the factory tree). — all product artifacts under `test_harness_app/requirements_*`.
- [x] The five mandatory advisory caveats are carried into any artifact/report that consumes an oracle
      verdict produced here. — carried in `2026-06-30_02_protocol_harness-middle-results.md` + FLOW_INDEX.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-071-07 | completed | Layer-derivation mechanism terminal verify (R1 epic re-capstone), PASS (ADVISORY); the mechanism this task applies |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-06](../2026-06-27_impl_orchestrate-buildout-full-playground/goal.md) | Terminal orchestration task (T-orch3) — created this task; read its terminal-batch derivation plan |
| [TASK-PROC-071-07](../../../epic_layer_derivation/tasks/2026-06-27_impl_re-capstone-epic-layer-derivation-end-to-end/goal.md) | Layer-derivation mechanism this task applies; its terminal verify proved the mechanism (ADVISORY) |
| [TASK-PROC-068-08](../2026-06-30_impl_autonomous-test-runs-ralph/goal.md) | Terminal batch task 2/3 (ralph-driven autonomous runs); runs after this task |

## Notes

- **Coordinator-derived, covers-empty by design.** Like the orchestration tasks of this chain
  (T-orch1/2/3), this task does not cover specific REQ-PROC-068 ACs. The `task-create` standalone
  redirect-to-`task-derive-from-requ` (3c) was intentionally **not** taken: (1) the terminal batch is a
  specific coordinator-derived shape (apply the two delivered mechanisms), not a holistic AC
  decomposition; (2) REQ-PROC-068 AC-06 mandates the harness product definition be authored in the
  `test_harness_app/` tree by the factory skills/mechanisms themselves — decomposing those ACs into
  factory-tree tasks would violate the two-tree split. Override rationale logged here per the skill.
- **Process task, no `target_package`** → surfaces to `next_tasks.py` only via
  `.claude/task_ordering_priority_override.txt` (appended by T-orch3 per the DEVELOPER DIRECTIVE).
