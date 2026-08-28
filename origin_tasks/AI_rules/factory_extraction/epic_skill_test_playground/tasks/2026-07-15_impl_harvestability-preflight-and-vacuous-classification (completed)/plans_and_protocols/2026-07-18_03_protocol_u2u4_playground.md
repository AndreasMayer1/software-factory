# Protocol — U2–U4 (playground: classification narrowing + pre-flight + resume revalidation)

Reconstructed by the orchestrator from the working tree: the U2–U4 implementation agent
(`aa72b390befdd1ea4`) was terminated by a session limit mid-run and never wrote its own protocol.
Its implementation was complete and gate-green at termination (it died while starting U5 tests);
this record is derived from `git diff` of the delivered files, then verified by the full python
gate suite (all 7 GREEN).

## U2 (D1) — vacuous-aware classification
- `scripts/playground/acceptance_oracles.py`: added `real_authoring_unfinished_predicate(...)` — the
  injected AC-18 structural-degeneracy inspector. True iff ≥1 unit with REAL authoring pairs is left
  non-terminal (terminal = DONE ∪ VACUOUS_COMPLETE). Missing/malformed chain-state fails SAFE (returns
  True → the run is never silently exonerated). Same lazy-sys.path-import convention as the existing
  chainstate oracle, so build.py stays layer-derivation-free (AC-17).
- `scripts/playground/build.py`: `classify_run_outcome` gained an injected `degeneracy_inspector`
  parameter, wired like the existing `completion_predicate`/`blocker_detector`. Final-branch precedence:
  oracle positive → COMPLETE; oracle negative AND (inspector True OR inspector absent) → ABANDONED;
  oracle negative AND inspector False (no real unit unfinished) → INCONCLUSIVE (D1). Absent inspector
  defaults to ABANDONED so the fail-safe never weakens. `build_degeneracy_inspector(cfg)` constructs it.

## U3 (D4) — plan-time pre-flight + doomed exit code + stamp
- `EXIT_DOOMED_SPEC = 2` (distinct: 0=success, 1=generic failure, 2=doomed spec; build_resume's
  FENCE_EXIT_FENCED=3 is unrelated). `class DoomedSpecError(RuntimeError)`.
- `run_harvestability_preflight(fixed_layers)` calls `acceptance_oracles.harvestability_preflight_verdict`
  (boundary-module indirection → `backfill_orchestration.harvestability_preflight`/`lint_spec`), so
  author-time linter == plan-time gate, and build.py never imports layer-derivation.
- `run_build_mode` runs the pre-flight FIRST, before `_prepare_workspace`/deploy; a doomed verdict raises
  `DoomedSpecError` → consumes no deployed run. `main` maps `DoomedSpecError` → `EXIT_DOOMED_SPEC`.
- The run-registry record persists a `harvestable` stamp alongside `acceptance_oracle_kind`; re-validated
  on `-start`.

## U4 (D4) — resume revalidation
- `scripts/playground/build_resume.py`: `resume_run` RECOMPUTES `run_harvestability_preflight` from the
  spec and raises `DoomedSpecError` BEFORE `launch_and_gate` — a spec that has become doomed since the
  original launch fails the resume; `build_resume.main` returns `EXIT_DOOMED_SPEC`. Satisfies AC-22 "no
  start or resume path reaches harvest without a current positive pre-flight" (ADV-sg-06).

## Verification
- Full `scripts/quality/check_python_gates.sh`: all 7 gates GREEN (after U5 consumed the two imports
  that had briefly left G1 red). AC-17 invariant test (`"ChainState" not in dir(build)`) still passing.
