---
task: TASK-PROC-068-07 (T-harness-middle, terminal batch 1/3)
session: d792b971-10d2-48d2-8a00-fa27eb6cc8c7
date: 2026-06-30
model: Opus 4.8
authority: ADVISORY
skills_used:
  - claude-automated-mode
  - claude-watch-tool-reliability
  - task-start
  - claude-route
  - task-resolve
  - claude-log
  - doc-update-guidelines
  - task-complete
  - claude-commit
---

# Protocol — Harness-Middle Layer Derivation Results

## Authority bound (recorded on EVERY verdict below)
The capability-tester / oracle gating this chain is **ADVISORY**
`[ADVISORY: N=3 ≪ floor_n=100; not HJR-calibrated]`. Carried on every verdict.

## What was done
Applied the **verified layer-derivation mechanism** (REQ-PROC-071 — `fixpoint_loop` + `coverage_delta`
+ the `backfill_orchestration` contract; terminal verify TASK-PROC-071-07 PASS ADVISORY) to
**generate a middle artifact layer of the Skill-Test Playground harness's product-definition stack**
in the `test_harness_app/` tree, from its anchored endpoints — mechanically derived, not hand-authored.

Starting state: `test_harness_app/` held only the **bottom endpoint** (the React/Vite `src/` app); the
product stack `personas → scenarios → flows → requirements → tasks → code` was empty above `code`.

### Layer derived — the FLOW layer (the mechanism's canonical default hinge, scenario↔flow)
Exactly the case the re-capstone proved (flow ← scenario + requirement). Authored, all in
`test_harness_app/`:
- **Top anchor — scenario layer** (grounded on 2 minimal personas, Archivist / Quick-Logger):
  `requirements_user_needs/personas/{archivist,quick_logger}/` — each scenario declares
  `flows_required` (the upper flow demand).
- **Bottom anchor — requirement layer**: `requirements_tasks/functional/rating_app/requirements.md` —
  four product requirements (dashboard, form, browse, insights) whose `flow_coverage` declares the
  lower flow demand.
- **Derived middle — flow layer**: `requirements_user_needs/user_flows/` — generated to satisfy the
  union of upper+lower demand, minimal (authored ⊆ demanded).

### Mechanism run (real CLI/library, throwaway driver — not committed; mirrors the re-capstone driver)
The driver derived the demand from the **actual authored neighbour files** (not hand-fed), then ran
the real `coverage_delta` + `fixpoint_loop`:

```
UPPER (scenario flows_required):   ['FLOW-HARNESS-01','FLOW-HARNESS-02','FLOW-HARNESS-03']
LOWER (requirement flow_coverage): ['FLOW-HARNESS-01','FLOW-HARNESS-02','FLOW-HARNESS-03']
TWO-SIDED BALANCED (upper == lower): True
NEIGHBOUR DEMAND (union):          ['FLOW-HARNESS-01','FLOW-HARNESS-02','FLOW-HARNESS-03']
AUTHORED flow layer (on disk):     ['FLOW-HARNESS-01','FLOW-HARNESS-02','FLOW-HARNESS-03']

[A] AUTHORED-DRAFT COVERAGE (coverage_delta, flow_coverage extractor):
    required_count: 3  satisfied_count: 3  is_closed: True  unsatisfied: []
    minimality (authored ⊆ demand, nothing invented): True | invented: []

[B] RECONSTRUCTION FROM EMPTY DRAFT (fixpoint_loop):
    outcome: coverage_fixpoint
    reconstructed: ['FLOW-HARNESS-01','FLOW-HARNESS-02','FLOW-HARNESS-03']
    DIFF vs demand   -> missing: [] | invented: []
    DIFF vs authored -> exact match: True

VERDICT: PASS (ADVISORY)
```

## Verdict against the task's Acceptance Criteria
- **AC-1 — mechanism applied to generate ≥1 middle layer from anchored endpoints (not hand-authored):**
  PASS (ADVISORY). The flow layer was reconstructed from an empty draft by the fixpoint loop against
  the neighbour demand alone, reproducing the exact set.
- **AC-2 — closes coverage against neighbour anchors, minimal, COVERAGE_FIXPOINT:** PASS (ADVISORY).
  `is_closed=True`, `invented=[]`, terminal `RunOutcome.COVERAGE_FIXPOINT`, reconstruction diff
  `missing=∅ / invented=∅`.
- **AC-3 — work stays within `test_harness_app/`, two-tree split honored:** PASS. All product content
  was authored under `test_harness_app/requirements_*`; no harness product content was authored in the
  factory tree. The throwaway driver/coverage-report live only in `/tmp` (not committed).
- **AC-4 — five mandatory advisory caveats carried:** PASS — recorded below and in the FLOW_INDEX /
  flow frontmatter (`status: derived`, `authority: ADVISORY`).

## Five mandatory advisory caveats (carried verbatim — this task consumed an oracle verdict)
Source: `…/epic_capability_testing/feat_regression_gate/tasks/2026-06-27_verify_discriminating-maturity-walk (completed)/plans_and_protocols/2026-06-27_02_verdict_maturity-walk.md` §"Mandatory advisory caveats".
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

## Scope notes
- The mechanism itself was **not** modified or re-verified (REQ-PROC-071 — done, ADVISORY).
- Only ≥1 middle layer (flow) was generated, per AC-1; the remaining middle layers (scenarios as a
  *derived* layer, tasks) are out of scope for this single bounded demonstration. Here scenarios and
  requirements served as the fixed anchored endpoints of the derivation span.
- No Dart `lib/`/`test/`/`integration_test/` was touched → no `verify-quality` Dart gate applies; the
  deliverables are process/product documentation in the harness tree.
- Terminal batch task 1/3. Successor: TASK-PROC-068-08 (ralph-driven autonomous runs over the harness),
  then TASK-PROC-068-09 (verify). No successor orchestration task — the chain ends with this batch.
