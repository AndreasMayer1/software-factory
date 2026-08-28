---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - claude-write-script
  - claude-log
  - task-complete
  - claude-commit
---

# Protocol — build.py resumable wrapper (TASK-PROC-068-21)

Session: d5b03ce0-cddb-4f2a-9a79-9429f3ad2571 (automated, opus). Inline execution (all context loaded).

## What was implemented (matches plan 01)

### `scripts/playground/build.py`
- **AC-13**: Dropped `tempfile.mkdtemp()`. `run_build_mode` now builds the isolated copy via
  `_prepare_workspace`: `create_workspace(host, target, uuid, workspace_root=<worktree_root>)`
  → `deploy_candidate` → `init_workspace_git` → `sync_product_definition` (seed + manifest
  `seeded_paths`) → `snapshot_product_definition` (Option-B baseline). Copy lives at the
  config-resolved out-of-project location (`worktree_root.py` + `worktree.config.json`) and is
  its own git repo. Teardown via `destroy_workspace` (prefix-guarded), never git-reset (C1).
- **AC-14**: `_gate_harvest` (inputs grouped in `_HarvestGateInputs` to keep params ≤5).
  `verified = result.succeeded and result.reason == 'exited' and predicate(copy)`.
  Verified → `harvest_authored` + registry→complete + `destroy_workspace`. Any non-verified
  outcome → registry→preserved, workspace kept, harvest skipped (preserve-by-default). No
  try/finally destroy: a crash/kill leaves the copy for resume.
- **Run registry (write side)**: `write_run_registry_running` writes
  `<workspace_root>/.playground_runs/<uuid>.json` (status=running + durable copy path + target/
  host/model) BEFORE launch (ADV-synthesize-gate-02). `_update_run_registry` flips to
  complete/preserved. Cold-session re-attach READS are T2.
- **AC-17**: `run_build_mode(..., *, completion_predicate: Callable[[str], bool] | None = None)`.
  Predicate takes the copy path; None → gate reduces to succeeded+clean-exit. No ChainState import.
- Config: `isolated_dir` → `workspace_root`; added `run_registry_dir`; `jsonl_dir` now optional
  (derived from the workspace). CLI: `--isolated-dir` → `--workspace-root` (default
  `worktree_root()`); added `--run-registry-dir`. Manifest adds `completed`,
  `workspace_preserved`, `run_registry_path`.

### `scripts/playground/workspace.py`
- `create_workspace` gained optional `workspace_root: str | None = None` (parent override,
  backward-compatible — default parent-of-host equals the worktree-root default, so run_skeleton
  is unaffected).

### `scripts/dev_env/worktree_root.py`
- No code change needed; imported as-is (namespace package). "Change with awareness of all three"
  satisfied by confirming it already provides the config-aware out-of-project root.

### `scripts/tests/test_playground_build.py`
- Reworked existing tests for `workspace_root`. Added AC-13/AC-14 (out-of-project git repo +
  preserve-on-incomplete; harvest+discard on complete) and AC-17 (injected predicate receives the
  copy path; no hard-coded ChainState) tests. `_authoring_deps` popen side-effect authors a
  net-new persona to exercise harvest vs preserve.

## Gates (`scripts/quality/check_python_gates.sh`)
- G1 lint, G2 type, G4 no-handrolled, G5 print, G6 complexity, G7 canonical-lib: **PASS**.
- G3 tests: the 47 tests in test_playground_build/workspace/run_skeleton all **PASS**. The only
  G3 failures are `test_aggregate_read_metrics.py::{test_aggregate_logs_reads_jsonl,
  test_aggregate_logs_skips_malformed_lines}` — **pre-existing on develop** (confirmed by
  `git stash` + rerun), unrelated to this change. Not a regression for this task.

## Out of scope (per goal) — deferred to T2/T3
- Run-registry cold-session re-attach/resume + `playground-build-resume` skill → T2 (068-22).
- End-to-end AC-13..17 real-artifact verification (subject-independent oracle) → T2.
- REQ-PROC-071-06 AC-08 real-limit derivation-resumability proof → T3.
