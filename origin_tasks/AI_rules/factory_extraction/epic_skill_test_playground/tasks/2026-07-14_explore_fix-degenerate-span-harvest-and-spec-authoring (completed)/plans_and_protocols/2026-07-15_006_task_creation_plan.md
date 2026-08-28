---
requirement: REQ-PROC-071-06 + REQ-PROC-068 (cross-requirement fix, one task per requirement)
requirements_version: 3206532a
created: 2026-07-15
mode: full
concept: 2026-07-15_004_synthesis.md (SOL-01, IDEATION-023, developer-approved)
---

# Task Creation Plan — degenerate-span harvest fix (impl chain)

The fix is one coherent implementation split per the one-requirement-per-task rule: Task 1 owns the
mechanism primitive + authoring surface (REQ-PROC-071-06); Task 2 owns the playground-side classification
+ harvestability pre-flight (REQ-PROC-068), depending on Task 1. Both appended to the priority override
(recursive override rule).

## Tasks

- task_name: "vacuous span disposition + spec-authoring surface (mechanism)"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_layer_derivation/feat_backfill_orchestration/requirements.md"
  requirements_version: "3206532a"
  covers_acs: [AC-09, AC-10]
  effort: L
  layer: factory-mechanism (scripts/factory/layer_derivation/*, scripts/playground/acceptance_oracles.py, layer-derivation-* skills)
  after: []
  task_type: impl
  opus_recommended: true   # HIGH-consequence AC-09 + synthesis_dependent (mechanism + oracle + skill + migration held together)
  target_package: ""       # process/factory tooling — unassigned; surfaces via priority override
  egp: [AC-09 F/HIGH, AC-10 F/MEDIUM]
  consequence: HIGH
  implementation_notes: >
    Add a distinct vacuous-complete UnitStatus to backfill_orchestration, granted ONLY by a structural
    zero-authoring-pair proof from anchor_span_engine (wire in the currently-dead screen_derivability /
    empty-required-elements case — R2); complete_unit assigns it instead of ESCALATED('gate_content_fail')
    for an empty gate, WITHOUT weakening the content-gate poka-yoke for spans that have authoring pairs
    (ADV-01: a real-authoring span still needs a passing gate to reach DONE). Make chainstate_complete_
    predicate (acceptance_oracles.py) satisfied by DONE∪VACUOUS. Migrate persisted
    ESCALATED('gate_content_fail') units on structurally zero-pair spans to vacuous-complete, keying on
    span structure AND that no authoring pairs existed (ADV-sg-03: do not silently reclassify a real past
    gate-fail). Fix layer-derivation-status to report vacuous-complete as "no-op complete", not a phantom
    pending_feedback (ADV-03). Migrate the ≥7 ESCALATE-skip test sites via ONE shared test helper, TDD-first
    (ADV-02). Spec-authoring (AC-10): derive span_units from fixed_layers in layer-derivation-start so a
    mismatched/degenerate-span mapping is inexpressible; a governed spec template + a teaching linter that
    IS the same check Task 2's harvestability pre-flight runs (author-time guidance == plan-time gate).
    Guidance in the skill/mechanism layer, NOT doc/. Generality (ADV-04/05): vacuous applies to any
    zero-pair span regardless of direction (FORWARD/REVERSE/BIDIRECTIONAL, incl. task_code) and to
    multiple degenerate spans. Read the concept: 2026-07-15_004_synthesis.md SP-1/SP-4. AC text is
    authoritative; concept grounds the HOW only where the AC is silent.
    Verification (AC-09/AC-10, EGP-bearing; oracle-independence): golden ChainState fixtures for every
    degenerate configuration (single/multiple/edge/mid/all-degenerate, each direction) assert the oracle
    verdict; assert a real-authoring span still requires the content gate (no empty-gate/self-declared
    pass); assert the linter and the pre-flight predicate agree on the same specs (referent = fixtures +
    real worktree, not the artifact's own constants). consequence: HIGH (computed floor, not self-rated).

- task_name: "harvestability pre-flight + vacuous-aware run classification (playground)"
  req_path: "requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md"
  requirements_version: "3206532a"
  covers_acs: [AC-18, AC-19, AC-22]
  effort: L
  layer: playground build-mode (scripts/playground/build.py + new planner-oracle module, layer-derivation-start)
  after: [TASK-1]
  task_type: impl
  opus_recommended: true   # HIGH-consequence AC-18/AC-19/AC-22 + synthesis_dependent
  target_package: ""
  egp: [AC-18 F/HIGH, AC-19 F/HIGH, AC-22 F/HIGH]
  consequence: HIGH
  implementation_notes: >
    Realize the vacuous-aware completion classification in build.py: AC-18 abandoned = a unit WITH real
    authoring pairs left non-terminal only (a degenerate no-op span is never abandoned/blamed); AC-19
    "finished" = every real-authoring span at its authored terminal ∧ every degenerate span vacuous-complete;
    the oracle counts vacuous-complete as satisfying. Add the harvestability pre-flight (AC-22): a shared
    planner-oracle module reusing resolve_spans + per-span disposition typing + the injected acceptance-
    oracle predicate to predict, over the best-case terminal, whether the spec can EVER be certified
    complete; a spec that cannot — including an all-degenerate spec (R1) and a spec with a real span that
    can never reach an authored terminal, e.g. no authoring skill registered for its pair (ADV-sg-02) —
    fails at plan time with a distinct doomed-spec exit code and consumes no deployed run. Persist the
    pre-flight verdict as a harvestable stamp re-validated on -start AND every resume (ADV-sg / ADV-06 —
    no resume path reaches harvest without a current positive pre-flight). Reuse Task 1's linter as the
    pre-flight check (author-time == plan-time). On landing, the 068-26 / 068-12 Option-A per-task workaround
    (hand-certifying span-0 to DONE) is RETIRE-ABLE — document its removal. Read the concept:
    2026-07-15_004_synthesis.md SP-2/SP-3. AC text authoritative; concept grounds HOW where AC is silent.
    Verification (AC-18/AC-19/AC-22, EGP-bearing; oracle-independence): a real doomed spec (incl.
    all-degenerate) observed to fail pre-flight and consume no deployed run; a real resume observed to
    re-validate the stamp before harvest; the predicted verdict checked against the ACTUAL deployed-run
    classification (referent = real run behaviour, not the predictor's own output). consequence: HIGH.

## Coverage Matrix

| AC | Task | Requirement |
|----|------|-------------|
| AC-09 | Task 1 | REQ-PROC-071-06 |
| AC-10 | Task 1 | REQ-PROC-071-06 |
| AC-18 | Task 2 | REQ-PROC-068 |
| AC-19 | Task 2 | REQ-PROC-068 |
| AC-22 | Task 2 | REQ-PROC-068 |

Verification: < 3 impl tasks per requirement → verification folded into each task's implementation_notes
(no separate verify task). Both tasks carry EGP-bearing ACs → oracle-independence declared above.
