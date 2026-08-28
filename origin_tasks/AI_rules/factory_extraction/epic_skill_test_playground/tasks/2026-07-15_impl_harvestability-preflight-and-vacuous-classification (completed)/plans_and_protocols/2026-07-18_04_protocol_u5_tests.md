---
skills_used:
  - claude-automated-mode
  - claude-watch-tool-reliability
  - task-start
  - claude-route
  - task-resolve
  - claude-write-script
  - loop
  - task-complete
  - claude-commit
---

# Protocol — U5: EGP-referent tests for AC-18/19/22 (end-to-end)

Task: `../goal.md` (TASK-PROC-068-30) · Unit: U5 of `2026-07-18_01_plan_preflight-and-classification.md`.
Agent ID: `a1150e8864b770707` (implementation-engineer subagent).

## Context at start

U1–U4 were already landed (uncommitted) in the working tree. Python gates were GREEN except
G1 lint, which failed with exactly two F401 "imported but unused" findings in
`scripts/tests/test_playground_build.py`: `EXIT_DOOMED_SPEC` and `DoomedSpecError` — imported
by the U2–U4 agent but not yet consumed by any assertion. This unit's job was to write the
EGP-referent tests that make those imports load-bearing, without touching production code
unless a real bug surfaced (none did).

## Scope executed

Per SCOPE, only test files were touched, both routed through the `claude-write-script` skill
(invoked once at the start, before any Edit):
- `scripts/tests/test_playground_build.py` — added a `bo` (backfill_orchestration) import via
  the same sys.path-insert convention `test_playground_build_resume.py` already uses, plus 6
  new tests (see below).
- `scripts/tests/test_playground_build_resume.py` — added `DoomedSpecError` to the existing
  `scripts.playground.build` import and 1 new test.

No production code under `scripts/playground/**` or `scripts/factory/layer_derivation/**` was
modified — every referent was reachable by driving the U2–U4 implementation as-is (real
`fixed_layers` inputs, or the same `authoring_skill_for` monkeypatch seam U1's own
`test_backfill_orchestration.py::test_real_span_with_unmapped_layer_pair_is_rejected` already
established for the one class that is defensive-only/unreachable via real input).

## Tests added — which EGP referent each grounds

### `scripts/tests/test_playground_build.py`

1. **`test_run_build_mode_doomed_spec_never_calls_prepare_workspace_and_creates_no_workspace`**
   — AC-22 referent A ("a real doomed spec … observed to fail the pre-flight at plan time and
   consume no deployed run"). Drives `run_build_mode` with an all-degenerate `fixed_layers`
   (all 7 layer names). **"No deployed run" assertion**: `scripts.playground.build._prepare_workspace`
   is monkeypatched to `raise AssertionError` if ever called (a tripwire, not a spy-and-count
   — same technique `test_playground_build_resume.py`'s pre-existing AC-15 no-redeploy test
   uses for `create_workspace`/`deploy_candidate`/`init_workspace_git`), PLUS the isolated
   copy's deterministic path is asserted absent, PLUS `workspace_root.glob("playground_ws_*")`
   is asserted empty, PLUS the durable `.playground_runs` registry dir is asserted absent (no
   run was ever registered either). `DoomedSpecError` is asserted raised with non-empty
   `.errors`.

2. **`test_main_returns_exit_doomed_spec_for_all_degenerate_fixed_layers`** — AC-22 referent A
   at the CLI entry point (`main`, not just the library call `run_build_mode` — the goal
   explicitly named both). Asserts `rc == EXIT_DOOMED_SPEC` (2) and that no
   `playground_ws_*` directory was ever created under `workspace_root`.

3. **`test_run_build_mode_doomed_for_real_span_with_unmapped_layer_pair`** — AC-22's second
   doomed class (D3 item 2 / ADV-sg-02: "a real span whose layer pair has no registered
   authoring skill"), propagated through `build.py`'s pre-flight boundary call. U1's own
   protocol (`2026-07-18_02_protocol_u1_linter.md`) recorded that this class is **not
   reachable via any real `fixed_layers` input today** — `_layer_pairs_for_span` already
   filters to `AUTHORING_SKILL_BY_PAIR` membership before a span's `authoring_pairs` are
   built, so an unmapped pair never reaches the check. This test therefore uses the same
   defensive-seam technique U1's backfill test used: `monkeypatch.setattr(bo,
   "authoring_skill_for", lambda _pair: None)` against a real `fixed_layers=("flow",)` (2 real
   non-degenerate spans). Asserts `DoomedSpecError` with an error containing "no authoring
   skill is registered", and — same "no deployed run" discipline as test 1 —
   `_prepare_workspace` is monkeypatched to raise as a tripwire and the workspace path is
   asserted absent.

4. **`test_predicted_harvestable_spec_actually_proceeds_past_preflight_to_real_classification`**
   — AC-18/AC-19 oracle-independence, first half: "a spec the pre-flight predicts HARVESTABLE
   … actually proceeds past the pre-flight into the real launch→classify path (is NOT
   rejected)". Calls `run_harvestability_preflight(("flow",))` directly first (asserts
   `(True, ())` — the PREDICTED verdict), then drives a REAL `run_build_mode` with
   `fixed_layers=("flow",)` through the mocked-subprocess launch path to an ACTUAL
   `outcome == "complete"` / `completed is True`. The registry record's persisted
   `harvestable: True` / `fixed_layers: ["flow"]` are asserted too — predicted and actual
   verdicts checked against each other, not the predictor's own say-so re-asserted.

5. **`test_run_build_mode_inconclusive_end_to_end_when_oracle_negative_and_no_real_unit_unfinished`**
   — AC-18/AC-19 oracle-independence, second half + the D1 narrowing "observed end-to-end, not
   just in the isolated unit test U2–U4 already wrote" (explicit goal instruction). Writes a
   REAL `ChainState` (via a `_popen` side effect, exactly the pattern every other
   `_*_deps` helper in this file uses) with one `DONE` real-authoring unit and one `PENDING`
   unit that already carries a `vacuous_proof` stamp — the exact "legacy un-migrated state"
   shape plan D1's own docstring names ("a degenerate span parked at PENDING/ESCALATED
   instead of VACUOUS_COMPLETE"). This makes `chainstate_complete_predicate` return `False`
   (oracle-negative: a PENDING unit is not a completed terminal) while
   `real_authoring_unfinished_predicate` ALSO returns `False` (the PENDING unit's
   `vacuous_proof` is set, so it's not counted as real-authoring-unfinished) — the precise D1
   precondition. Drives this through `run_build_mode` with
   `acceptance_oracle_kind="chainstate"` and **no injected `completion_predicate` /
   `degeneracy_inspector`** — both are constructed from `cfg` via the REAL production wiring
   (`build_acceptance_predicate` / `build_degeneracy_inspector`), not the test-only injection
   seam every other classify_run_outcome test in this file uses. Asserts
   `outcome == "inconclusive"`, not `"abandoned"` and not `"complete"`.

### `scripts/tests/test_playground_build_resume.py`

6. **`test_resume_run_revalidates_preflight_and_never_reaches_launch_and_gate_when_spec_became_doomed`**
   — AC-22 referent B ("a real resume observed to re-validate the pre-flight verdict before
   reaching harvest"). Preserves a REAL run (via `run_build_mode`, non-clean exit →
   `INTERRUPTED`/preserved) with `fixed_layers=("flow",)` — harvestable AT WRITE TIME (asserts
   the persisted record's `harvestable: True`). Then simulates the spec becoming doomed
   *since* preservation via the same `authoring_skill_for` monkeypatch seam as test 3, and
   calls `resume_run` on the loaded record. **"Launch/gate not reached" assertion**:
   `scripts.playground.build_resume.launch_and_gate` is monkeypatched to `raise
   AssertionError` if ever called — a tripwire, not a call-count spy, mirroring the file's own
   pre-existing AC-15 no-redeploy pattern. Asserts `DoomedSpecError` is raised and that the
   preserved workspace is left untouched (`workspace.exists()` still `True` — a doomed resume
   neither harvests nor destroys the copy, it stays resumable once the registered skills are
   fixed).

## Production bug found

None. Every referent was reachable by driving the U2–U4 implementation through its existing
public seams (`run_build_mode`, `main`, `resume_run`, `run_harvestability_preflight`) with
real inputs (`fixed_layers`, a real `ChainState` file) or the one already-established
defensive-seam monkeypatch (`authoring_skill_for`) — no workaround, no unexpected behavior,
no divergence from what the U1–U4 protocols documented. `DoomedSpecError` is raised exactly
where documented (before `_prepare_workspace` in `run_build_mode`; before `launch_and_gate` in
`resume_run`), `EXIT_DOOMED_SPEC` (2) is returned exactly where documented (`main`'s
`except DoomedSpecError` clause), and `classify_run_outcome`'s D1 narrowing produces
`INCONCLUSIVE` exactly as the plan's D1 section specifies when driven through the real
chainstate oracle + degeneracy inspector rather than injected fakes.

## Gate outcome

`scripts/quality/check_python_gates.sh` — **ALL 7 GREEN**:
- G1 lint (ruff): PASS — the two F401 findings the U2–U4 agent left (`EXIT_DOOMED_SPEC`,
  `DoomedSpecError` imported-but-unused in `test_playground_build.py`) are gone: both are now
  consumed by real assertions (tests 1/2 use `EXIT_DOOMED_SPEC`; tests 1/2/3 use
  `DoomedSpecError` via `pytest.raises`).
- G2 type (mypy): PASS — 320 source files, no issues.
- G3 tests (pytest): PASS — 3240 passed (up from 3219 at the end of U1), 17 skipped
  (pre-existing PyYAML-not-installed skips, unrelated), 6 xfailed (pre-existing known
  limitations, unrelated). 21 new tests total accounts for the delta: 7 new in
  `test_playground_build.py`, 1 new in `test_playground_build_resume.py`, plus the tests U2–U4
  already added elsewhere that were not yet counted in U1's snapshot.
- G4 no-handrolled-YAML: PASS
- G5 print discipline: PASS
- G6 complexity: PASS
- G7 canonical-library: PASS

No back-pressure cycles needed (all gates passed on the first run after the edits). Isolated
run of just the two touched test files: `68 passed` in `0.79s`
(`scripts/tests/test_playground_build.py scripts/tests/test_playground_build_resume.py`).

## Not done in U5 (explicitly out of scope, per the plan)

- D5 Option-A workaround retirement, `contract.yaml` EGP disposition — **U6**, not this unit.

No commit was made (per dispatcher instruction — "Do NOT commit").
