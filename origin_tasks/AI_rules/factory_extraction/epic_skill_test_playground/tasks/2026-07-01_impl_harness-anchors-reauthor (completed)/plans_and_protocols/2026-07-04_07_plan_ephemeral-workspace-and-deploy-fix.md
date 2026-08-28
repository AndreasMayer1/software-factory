# Plan 07 — Ephemeral workspace + deploy exclude fix + reset guard

Task: TASK-PROC-068-11 · 2026-07-04 · developer-directed mechanism repair.

Unblocks the resolver loop documented in protocol 06. Developer decisions this turn:
- **containment.py**: DONE this session — added bwrap `--share-net` so the jail keeps
  the host network namespace (child `claude -p` needs api.anthropic.com); CON-04/AC-09
  filesystem isolation is a *mount-namespace* guarantee, unaffected. Regression test
  `test_wrap_bwrap_cmd_retains_network` added. Gate-clean for the change.
- **Reset (option A)**: ephemeral workspace. Deploy target moves OUT of the in-tree
  `test_harness_app/` (which is NOT its own git repo → `git reset --hard` would wipe the
  outer repo) into a throwaway dir under the **parent folder of the host project**, with
  `git init` after copying everything in (skills-under-test need a real repo).
- **Deploy (approved)**: replace the coarse top-level `requirements_user_needs` exclude
  with sub-folder excludes (`personas/`, `user_flows/`) — mirroring the existing
  `requirements_tasks/{functional,non-functional}` treatment — so the factory machinery in
  `requirements_user_needs/` (README_*.md authoring guides, SCENARIO_INDEX.md, _meta/,
  CHANGE_PROPAGATION.md) is present under the run cwd while the mood-tracker's product
  CONTENT (personas/user_flows) is not.

## Change 1 — deploy.py (small, surgical)
- Remove `"requirements_user_needs"` from `_TOP_LEVEL_EXCLUDES`.
- Add to `_SUBFOLDER_EXCLUDES`:
  `os.path.join("requirements_user_needs", "personas")`,
  `os.path.join("requirements_user_needs", "user_flows")`.
- Update the WHY comment near `_SUBFOLDER_EXCLUDES` to state requirements_user_needs is the
  same entangled-tree case: machinery (READMEs/_meta/indexes) kept, product content dropped.
- Test: extend `scripts/tests/test_playground_deploy.py` — assert after a deploy that
  `requirements_user_needs/README_*.md` (a machinery file) IS copied and
  `requirements_user_needs/personas/` is NOT. (Test would FAIL against the pre-change code.)

## Change 2 — reset.py guard (defense-in-depth, keep regardless of option A)
- In `reset_harness()`, BEFORE running `git reset --hard`, verify the harness dir is the
  ROOT of its OWN git repo: `git -C harness_dir rev-parse --show-toplevel` must equal
  `os.path.realpath(harness_dir)`. If not, raise a new `HarnessNotOwnRepo(RuntimeError)`
  (do NOT run reset). This is the guardrail that prevents `git reset --hard` ever resolving
  to an enclosing repo — the exact catastrophe (wiping the outer flutter_app tree).
- Test: `test_reset_refuses_when_not_own_repo` — point reset at a subdir of a temp git repo
  (not the repo root) and assert `HarnessNotOwnRepo` raised and NO reset ran.

## Change 3 — new module scripts/playground/workspace.py (tier B)
Ephemeral-workspace lifecycle. Pure-ish, injectable subprocess boundary for tests.
- `create_workspace(host_project_dir, harness_app_dir, session_uuid) -> str`
  - parent = `os.path.dirname(os.path.realpath(host_project_dir))`  (=/workspaces/private_mood_tracker)
  - workspace = `os.path.join(parent, f"playground_ws_{session_uuid[:8]}")`
  - if exists → remove first (idempotent); `shutil.copytree(harness_app_dir, workspace)`
    (the persistent test_harness_app becomes the project base).
  - return workspace path. Does NOT deploy or git-init (caller composes — keeps SRP).
- `init_workspace_git(workspace) -> None`
  - `git init`, `git add -A`, `git commit -m "playground baseline"` inside workspace.
    Set a local user.email/user.name via `-c` flags so commit works in a bare env.
    This baseline is what `reset_harness` restores to between runs.
- `destroy_workspace(workspace) -> None`
  - `shutil.rmtree(workspace, ignore_errors=False)`. SAFETY: refuse (raise ValueError) if
    workspace resolves to the host_project_dir, the harness_app_dir, or any path that is a
    parent of host_project_dir — never rmtree something enclosing the real tree. Callers pass
    a `playground_ws_*` sibling; assert the basename startswith `playground_ws_`.
- Tests in `scripts/tests/test_playground_workspace.py`: create→copies harness content;
  init→workspace is its own git repo root (rev-parse toplevel == workspace) with a clean
  status; destroy→removes it AND refuses on a guard-violating path.

## Change 4 — run_skeleton.py wiring
Reorder `run_single_fixture` to use the workspace as the deploy target / run cwd / reset
target; keep `--harness-dir` meaning the PERSISTENT test_harness_app seed.
- Step 0 (new): `workspace = create_workspace(host_project_dir, harness_dir, session_uuid)`.
- Step 1: `deploy_candidate(host_project_dir, workspace)` (was `harness_dir`).
- Step 1b (new): `init_workspace_git(workspace)`.
- Steps 3–5: `wrap_with_containment(base_cmd, workspace)`, `scrub_env(env, workspace)`,
  and `_derive_jsonl_dir(workspace)` — everything keys off `workspace`, not `harness_dir`.
  NOTE the jsonl_dir: `_derive_jsonl_dir` currently derives from harness_dir; it must derive
  from `workspace` now (child cwd = workspace). Verify hung-detection still points at the
  dir the child actually writes (HOME is scrubbed to workspace, so also consider the CCS
  path derived from the workspace path). Keep the existing `--jsonl-dir` override intact.
- Step 7: `reset_harness(workspace)` (now a real own-repo → guard passes).
- Wrap steps in try/finally: `destroy_workspace(workspace)` in `finally` so a crash never
  leaves a `playground_ws_*` dir or (worse) a half-run behind. Add `WorkspaceError` handling
  to `main()`'s except ladder.
- Update `--harness-dir` help text: "Absolute path to the persistent test_harness_app
  product tree (seed for the ephemeral run workspace)" — it is NOT a git repo and no longer
  the reset target.
- Update the module docstring flow (deploy→run→reset) to note the workspace lifecycle.
- Tests: update `scripts/tests/test_playground_run_skeleton.py` — the injected flow now
  creates+destroys a workspace; assert deploy/containment/reset all receive the workspace
  path and that destroy runs even when the child launch raises.

## Gates / process
- Every script edit goes through the `claude-write-script` skill (mandatory, REQ-PROC-051).
- Run `scripts/quality/check_python_gates.sh`; block only on findings NEW to this change.
  Known develop baseline: G3 has a pre-existing collection error in
  `test_check_dependency_usage.py` (unrelated file) — not a regression for this change.
- No new top-level dependency (uses stdlib shutil/subprocess only) — dependency gate N/A.
- Do NOT commit; the developer/task flow owns the commit. Persist results to a protocol
  file before returning.
