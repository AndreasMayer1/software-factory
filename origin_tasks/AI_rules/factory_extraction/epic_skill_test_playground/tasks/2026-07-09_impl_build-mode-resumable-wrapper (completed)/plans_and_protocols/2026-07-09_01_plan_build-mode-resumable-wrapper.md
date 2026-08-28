# Plan — build.py resumable wrapper (TASK-PROC-068-21)

Agent: (main session, inline — all context loaded; delegating would force re-reads)
Design source: `../2026-07-08_explore_build-mode-resumability (completed)/plans_and_protocols/2026-07-09_006_synthesis_v2.md` (SOL-02)
ACs: AC-13 (F/MEDIUM), AC-14 (F/HIGH), AC-17 (not-bearing seam).

## Files changed (the three the goal enumerates)
1. `scripts/playground/build.py` — main changes.
2. `scripts/playground/workspace.py` — add optional `workspace_root` to `create_workspace`.
3. `scripts/dev_env/worktree_root.py` — **no code change needed**; already exports `worktree_root()`
   with config precedence. build.py imports it. (The "change with awareness of all three" opus reason
   is satisfied by confirming worktree_root already provides the out-of-project root + config override.)
Plus tests: `scripts/tests/test_playground_build.py`.

## AC-13 — parent-dir git-init workspace instead of mkdtemp
- Drop `tempfile.mkdtemp()`. Resolve out-of-project parent via `worktree_root()` (config-aware).
- `create_workspace(host, target, uuid, workspace_root=<root>)` → `<root>/playground_ws_<uuid8>`,
  seeded by copytree of test_harness_app (same convention run_skeleton uses).
- `deploy_candidate(host, workspace)` merges factory (dirs_exist_ok=True).
- `init_workspace_git(workspace)` → own git repo (AC-13 "its own git repository").
- Teardown via `destroy_workspace` (prefix-guarded) — never rmtree of an arbitrary path, never git-reset (C1).

## AC-14 — completion-gated harvest, preserve-by-default (HIGH)
Gate around harvest+discard:
```
is_complete   = completion_predicate(workspace) if completion_predicate else True
verified      = result.succeeded and result.reason == "exited" and is_complete
if verified:  harvest_authored(...) ; destroy_workspace(workspace)      # discard-only-on-verified-complete
else:         (skip harvest) ; preserve workspace                        # preserve-by-default
```
- NO try/finally destroy (run_skeleton destroys always; build must preserve on any non-complete/crash).
- On exception → preserve (don't destroy), re-raise.
- Preserve harvest snapshot-diff scoping (net-new Option B, REQ-PROC-068-19) — unchanged.

## Run registry (status=running + durable path BEFORE launch) — ADV-synthesize-gate-02
- Minimal inline helpers in build.py (T2 owns re-attach/resume READS + the skill; T1 writes the record):
  - `_run_registry_dir(cfg)` = `cfg.run_registry_dir or <workspace_root>/.playground_runs` (out-of-project,
    survives workspace discard — NOT `.factory/playground/runs/` inside the tree, per synthesis G2-1).
  - `_write_run_registry_running(...)` writes `{session_uuid, workspace_path, target/host, model,
    status:"running", started_at}` BEFORE `run_with_hung_detection`.
  - `_update_run_registry(path, status=..., ...)` flips to `complete` / `preserved` after the gate.

## AC-17 — injected completion-predicate seam (not-bearing)
- `run_build_mode(..., *, completion_predicate: Callable[[str], bool] | None = None)`.
- Predicate takes the isolated-copy path; None default → always-complete (gate reduces to succeeded+exited,
  a safe generic default). Layer-derivation (ChainState complete) injects its own — NOT hard-coded here.

## Config / CLI
- `BuildModeConfig`: replace `isolated_dir` → `workspace_root: str=""`; add `run_registry_dir: str=""`.
- `main()`: `--workspace-root` (default `worktree_root()`), `--run-registry-dir` (default derived);
  drop `--isolated-dir`. jsonl_dir default moves inside run_build_mode (after workspace known).
- Manifest adds: `completed`, `workspace_preserved` (path|None), `run_registry_path`.

## Tests (unit, mocked — HIGH real-oracle verification is folded into T2)
- Rework isolated_dir → workspace_root in existing tests.
- Add: AC-13 (preserved workspace lives under workspace_root + has `.git`), AC-14 (preserve+skip on
  non-complete; harvest+discard on complete — fake popen side-effect authors a net-new persona),
  AC-17 (injected predicate honored; recorded call; no ChainState import).

## Gates
Route every scripts/**/*.py edit through `claude-write-script`; then Python gates (ruff/mypy/pytest/G4/G5).
