# Plan — Playground build/maintain mode + registry-driven harvest (TASK-PROC-068-18)

**Date:** 2026-07-03 · session 9593db43-e956-4c9a-99a3-66b04cd1418f (account web)

## Grounding (read before starting)

- Investigation: `.../2026-07-01_impl_orchestrate-deploy-and-resolution-chain (completed)/plans_and_protocols/2026-07-02_03_investigation_target-project-autorun.md`
  — lays out **Strategy A** (relocate + inherited cwd): deploy whole factory into a copy → the
  copy self-scopes (`PROJECT_ROOT` from `__file__`) → a child launched with cwd=copy inherits that
  project. All three blocking prerequisites it names are now DONE:
  - T-B (TASK-PROC-068-16): `deploy.py` copies the **whole factory** (not just `.claude/skills/`).
  - T-C (TASK-PROC-071-06-06): `layer-derivation-start`/`resume` author unit tasks project-relative
    (`unit_task_req_id`/`unit_task_req_path` spec fields), no hardcoded main-factory path.
  - T-E (TASK-PROC-041-01-12): `orchestrate.py` derives `JSONL_BASE` from `PROJECT_ROOT` and passes
    `cwd=PROJECT_ROOT` to the child launch — a relocated copy self-scopes its own autorun.
- `scripts/playground/deploy.py`: whole-factory copy, exclude-based (`_TOP_LEVEL_EXCLUDES` /
  `_SUBFOLDER_EXCLUDES`). Notably excludes `requirements_user_needs` and
  `requirements_tasks/{functional,non-functional}` entirely (app-owned product content, not
  factory machinery), and excludes `test_harness_app` itself (deploy target, avoid self-nesting).
- `scripts/playground/reset.py`: `git reset --hard` + `git clean -fdx` — **test-mode only**. Build
  mode must NOT use this (test_harness_app is not its own git repo — confirmed:
  `git -C test_harness_app rev-parse --show-toplevel` returns the OUTER repo root, so a git-reset
  scoped to test_harness_app would nuke the whole factory repo — this is the hazard T-B's protocol
  already documented for the AC-10 proof).
- `scripts/playground/run_skeleton.py`: existing test-and-reset walking skeleton (deploy → budget
  gate → contain → launch → cost → git-reset). Build mode is an **additive sibling**, not a
  replacement (goal.md Out-of-Scope).
- `.factory/registry/artifacts.yaml`: product-definition categories = `user-needs`, `requirements`,
  `scribble`, `source-code` (goal.md's own wording). Each entry has `category:` + `path:` (glob).
  Harvest must walk this registry, not a hand-maintained file list.
- YAML parsing: canonical library is `ruamel.yaml` (`.factory/registry/capability_library_registry.yaml`
  `yaml-parse-serialize` capability) — use it to read `artifacts.yaml`, not a hand-rolled parser (G4).

## Design

### Why the isolated copy is NOT test_harness_app

Build mode's isolated copy is a **fresh scratch directory** (e.g. `tempfile.mkdtemp()`), never
`test_harness_app/` itself:
- `test_harness_app/` is the **harvest target** — it must only gain the harvested files; it is
  never deployed-into, reset, or discarded.
- The isolated copy is the **transient deployed machinery** (goal.md step 4) — discarded via
  `shutil.rmtree` after harvest, never git-reset (it isn't reliably its own git repo either).

### Why the isolated copy must be *seeded* with the harness's current product state

The derivation session needs the harness's own current anchors (personas/scenarios that already
live in the real `test_harness_app/requirements_user_needs/`) to derive from — `deploy_candidate`
deliberately EXCLUDES `requirements_user_needs` and `requirements_tasks/{functional,non-functional}`
(app-owned, not factory machinery), so a bare deploy gives the copy the factory mechanism but an
**empty** product tree. Build mode must overlay-copy the harness's current registry-classified
product-definition content into the isolated copy **after** deploy (deploy's excludes leave those
paths untouched, so overlay order is safe either way) — this *is* "derives the harness's own layers"
(goal.md Objective): the copy starts from the harness's real current state, using the factory's
mechanism, and produces updated layers in place.

### New module: `scripts/playground/build.py`

Functions:
- `load_product_definition_globs(registry_path) -> list[str]` — parse `artifacts.yaml` via
  `ruamel.yaml`, return `path:` globs for entries whose `category` is in
  `{user-needs, requirements, scribble, source-code}`.
- `sync_product_definition(src_root, dst_root, globs) -> list[str]` — copy every path matching a
  glob from `src_root` into `dst_root` (merge, `dirs_exist_ok=True`); returns the relative paths
  copied. Used BOTH directions: seed (harness → isolated copy) and harvest (isolated copy →
  harness) — same classification logic, opposite src/dst, so the registry-driven rule is defined
  once.
- `run_build_mode(...) -> dict` — orchestrates: mkdir isolated copy → `deploy_candidate(host_project_dir,
  isolated_dir)` → `sync_product_definition(target_project_dir, isolated_dir, globs)` (seed) →
  budget gate + contained launch (reuse `containment.wrap_with_containment` +
  `launch_adapter.run_with_hung_detection` + `cost_ledger`, same pattern as `run_skeleton.py`) →
  `sync_product_definition(isolated_dir, target_project_dir, globs)` (harvest) →
  `shutil.rmtree(isolated_dir)` (discard, no git-reset). Returns a manifest dict (harvested paths +
  ledger).
- CLI mirroring `run_skeleton.py`'s argparse shape: `--target-project-dir` (test_harness_app),
  `--host-project-dir` (the factory), `--isolated-dir` (optional, default `tempfile.mkdtemp()`),
  `--session-uuid`, `--prompt`, `--max-budget-usd`, `--model`.

### Functional proof (AC-11, EGP-F) — real, cheap, not mocked

Mirrors T-B's AC-10 proof pattern (real containment + a cheap deterministic real action, not the
full expensive authoring chain — the real anchors-based middle-layer derivation is TASK-PROC-068-12's
job, explicitly out of scope here):
1. Real `deploy_candidate` into a real scratch isolated dir.
2. Real seed from the REAL `test_harness_app/` (its actual current `requirements_user_needs/`).
3. Real contained child session (bwrap) whose prompt/cmd deterministically writes one small, clearly-
   named synthetic artifact at a registry-classified path inside the isolated copy (e.g. a proof
   flow file under a `_build_mode_proof/` subfolder so TASK-PROC-068-12's real derivation can never
   collide with it) — proves real containment + real execution landed inside the copy's own product
   tree, self-scoped.
4. Real harvest copies the registry-classified categories (including the new proof file) from the
   isolated copy back into the REAL `test_harness_app/`.
5. Assert: the proof file now exists in real `test_harness_app/` and is retained (no reset ran
   against test_harness_app); assert isolated copy is gone (`rmtree`); assert factory-machinery
   categories (scripts/, .claude/skills/, doc/) were NOT copied into test_harness_app/.
6. Document the retained proof artifact's path in the evidence file for TASK-PROC-068-12's
   awareness (not cleaned up — AC-11 requires retention).

### Tests (`scripts/tests/test_playground_build.py`)

Unit-level, mocking launch/subprocess boundaries (same DI pattern as `test_playground_run_skeleton.py`):
- `load_product_definition_globs` returns only the 4 product-definition categories' globs.
- `sync_product_definition` copies matching paths, skips non-matching (factory-machinery) ones.
- `run_build_mode` calls deploy → seed → launch → harvest → rmtree in order (fakes for launch).
- Discard-not-reset: build mode never calls `reset_harness`/`git reset` against the isolated dir
  or the target project.

## Execution

Authored via `claude-write-script` (mandatory, runs Python gates G1-G7). Delegating implementation
+ tests + functional proof to `implementation-engineer` (background — a real child `claude`
session launch is likely >5 min wall-clock; main session runs a 4:30 heartbeat per CLAUDE.md).

## Out of scope (confirmed, not touched here)

- The real anchors-based middle-layer derivation content (TASK-PROC-068-12).
- `deploy.py`/`reset.py`/`run_skeleton.py` internals beyond reuse (T-B, already landed).
- `orchestrate.py`/derivation-skill internals (T-E, T-C, already landed).
