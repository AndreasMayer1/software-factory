# Protocol 08 — Ephemeral-workspace + deploy-fix implementation

Task: TASK-PROC-068-11 · 2026-07-04 · implementation-engineer
Agent ID: 148705861ae4e713
Plan followed: `2026-07-04_07_plan_ephemeral-workspace-and-deploy-fix.md`

## Summary

Implemented all four changes from plan 07. Every `scripts/` edit went through
the `claude-write-script` skill (invoked once at task start; subsequent edits
in the same skill-covered scope followed the same read-doc/python-guidelines
→ edit → test → gate flow the skill mandates).

### Change 1 — `scripts/playground/deploy.py`
- Removed `"requirements_user_needs"` from `_TOP_LEVEL_EXCLUDES`.
- Added `requirements_user_needs/personas` and `requirements_user_needs/user_flows`
  to `_SUBFOLDER_EXCLUDES`.
- Updated the WHY comment above `_SUBFOLDER_EXCLUDES` to explain the
  entangled-tree rationale (machinery kept, product content dropped).
- Tests (`scripts/tests/test_playground_deploy.py`): extended the
  `tmp_whole_host` fixture with a `user_flows/` dir and a `README_3_persona.md`
  machinery file; replaced the old `test_deploy_excludes_top_level_app_dirs`
  assertion (which asserted the whole `requirements_user_needs/` dir was
  absent — that assertion now FAILS against the new code, as expected for a
  behavior change) with two new tests:
  `test_deploy_copies_requirements_user_needs_machinery` and
  `test_deploy_excludes_requirements_user_needs_product_content`.

### Change 2 — `scripts/playground/reset.py`
- Added `HarnessNotOwnRepo(RuntimeError)` and `_verify_own_repo()`, called at
  the top of `reset_harness()` before any `git reset`/`git clean`. Uses
  `git rev-parse --show-toplevel` and compares `os.path.realpath` on both
  sides.
- Updated the module docstring with a "Why the own-repo guard" section.
- Tests: added `test_reset_refuses_when_not_own_repo` (real git repo, no
  mocking — points reset at a subdirectory of a real repo, asserts
  `HarnessNotOwnRepo` raised AND an untracked sentinel file inside survives,
  proving no reset/clean ran), `test_reset_harness_calls_toplevel_check_before_reset`,
  and `test_harness_not_own_repo_carries_paths`. Also had to fix the two
  PRE-EXISTING mocked-git tests (`test_reset_harness_calls_git_reset_and_clean`,
  `test_reset_harness_raises_harness_not_clean_when_dirty`) — their fake
  `git` responder previously returned `stdout=""` unconditionally, which
  would now trip the new own-repo guard; updated both to return the harness
  path for `rev-parse` calls.

### Change 3 — `scripts/playground/workspace.py` (new, tier B)
- `create_workspace(host_project_dir, harness_app_dir, session_uuid) -> str`:
  copies `harness_app_dir` into `<parent-of-host_project_dir>/playground_ws_<uuid8>`;
  idempotent (removes a same-named leftover via `destroy_workspace` first).
- `init_workspace_git(workspace)`: `git init` + `git add -A` + `git commit
  --allow-empty -c user.email=... -c user.name=...` (the `--allow-empty` was
  a judgment call — needed because a just-copied harness seed can be empty,
  e.g. in tests; without it `git commit` exits 1 and the baseline commit
  reset_harness() depends on never gets created).
- `destroy_workspace(workspace)`: SAFETY-gated `shutil.rmtree` — refuses
  (raises `ValueError`) unless the resolved path's basename starts with
  `playground_ws_`, and refuses the literal filesystem root as a second,
  belt-and-braces check.
- New `WorkspaceError(RuntimeError)` for I/O/git failures during
  create/init/destroy, kept deliberately distinct from the safety-guard's
  `ValueError` (see class docstring).
- Tests (`scripts/tests/test_playground_workspace.py`, new file, 14 tests):
  create/copy/sibling-location/prefix/idempotency/missing-seed;
  init makes a real standalone repo root with clean status, and wraps a git
  failure as `WorkspaceError`; destroy removes a real workspace AND explicitly
  refuses (with assertions that the real dir still exists afterward) the host
  project dir, the harness seed dir, the parent-of-host-project dir, and `"/"`
  — SAFETY evidence per the task's hard requirement.

### Change 4 — `scripts/playground/run_skeleton.py` wiring
- Imports: `HarnessNotOwnRepo` from `reset`; `WorkspaceError`,
  `create_workspace`, `destroy_workspace`, `init_workspace_git` from the new
  `workspace` module.
- `FixtureConfig.jsonl_dir` changed from required `str` to `str | None = None`
  — the ephemeral workspace the default derives from does not exist until
  `run_single_fixture` creates it, so the CLI can no longer resolve the
  default at parse time. `main()` now passes `args.jsonl_dir` through as-is
  (may be `None`); `run_single_fixture` resolves
  `cfg.jsonl_dir or _derive_jsonl_dir(workspace)` at Step 5, after the
  workspace exists.
- `run_single_fixture`: Step 0 `create_workspace(...)`; everything else
  (`deploy_candidate`, `init_workspace_git`, `wrap_with_containment`,
  `scrub_env`, `_derive_jsonl_dir`, `reset_harness`) now keys off `workspace`,
  never `cfg.harness_dir` directly. Wrapped in `try/finally` with
  `destroy_workspace(workspace)` in `finally`.
- `_derive_jsonl_dir`: renamed the parameter `harness_dir` → `run_dir` (no
  behavior change) and expanded its docstring to note the CCS base path is
  NOT `$HOME`-derived (so `scrub_env`'s HOME redirect to the workspace does
  not affect it) — only the project-name segment tracks whichever dir is
  now the child's cwd (the workspace).
- `main()`'s except ladder: added `HarnessNotOwnRepo` and `WorkspaceError`
  clauses (each with its own log message), placed before the generic
  `(OSError, ValueError, RuntimeError)` catch-all.
- `--harness-dir` and `--jsonl-dir` help text updated per plan.
- Tests (`scripts/tests/test_playground_run_skeleton.py`):
  - Judgment call: rather than re-mock `reset.subprocess.run` in the two
    pre-existing "returns ledger"/"resets harness" tests, I removed that
    mocking entirely. Reasoning: the workspace `init_workspace_git` call now
    makes the ephemeral workspace a REAL, valid git repo before
    `reset_harness` ever runs against it in these tests (previously the test
    harness dir was NOT a real repo, which is exactly why git was mocked).
    Letting the whole deploy→init→reset chain run for real is simpler, more
    faithful to production, and avoids re-deriving a `rev-parse` mock that
    doesn't know the dynamically-generated workspace path in advance. Only
    the expensive/networked child launch stays faked via `launch_deps`.
  - `test_run_single_fixture_resets_harness_after_run` now asserts via
    `patch("scripts.playground.run_skeleton.reset_harness")` call count
    instead of scanning captured git argv lists.
  - Added `test_run_single_fixture_wires_workspace_through_deploy_containment_reset`
    (mocks `create_workspace`/`init_workspace_git`/`deploy_candidate`/
    `reset_harness`/`destroy_workspace`; asserts each receives the workspace
    path, not `cfg.harness_dir`) and
    `test_run_single_fixture_destroys_workspace_even_when_launch_raises`
    (forces `wrap_with_containment` to raise; asserts `destroy_workspace`
    still ran and `reset_harness` did NOT).
  - `test_run_single_fixture_budget_exceeded_raises` needed no code change;
    verified it still passes (workspace create/init now run for real before
    the mocked `check_budget` raises, then `finally` destroys it — harmless).

## Gate / test results

`scripts/quality/check_python_gates.sh` (full run, after fixes):

```
PASS   G1 lint
PASS   G2 type
FAIL   G3 tests   -- 2 failures, BOTH pre-existing develop baseline,
                     confirmed via `git stash` + re-run:
                     scripts/tests/test_aggregate_read_metrics.py::test_aggregate_logs_reads_jsonl
                     scripts/tests/test_aggregate_read_metrics.py::test_aggregate_logs_skips_malformed_lines
                     Unrelated file; nothing this task touches imports it.
PASS   G4 no-handrolled
PASS   G5 print-discip.
PASS   G6 complexity
PASS   G7 canonical-lib
```

Playground blast-radius, isolated:

```
python3 -m pytest scripts/tests/test_playground_*.py -q
........................................................................ [ 64%]
........................................                                 [100%]
112 passed in 0.39s
```

(112 = all playground test files: build, containment, cost_ledger, deploy,
launch_adapter, run_skeleton, workspace.)

## Safety verification (explicit, per task instructions)

- `test_destroy_workspace_refuses_host_project_dir`,
  `test_destroy_workspace_refuses_harness_seed_dir`,
  `test_destroy_workspace_refuses_parent_of_host_project`,
  `test_destroy_workspace_refuses_filesystem_root` — all pass; each asserts
  the target directory STILL EXISTS after the refusal (not just that an
  exception was raised).
- `test_reset_refuses_when_not_own_repo` — uses a REAL git repo (no
  subprocess mocking) with a subdirectory as the reset target; asserts
  `HarnessNotOwnRepo` raised and an untracked sentinel file inside the outer
  repo survives (proving `git clean -fdx` never ran).

## Deviations / judgment calls (flagged for review)

1. `git commit --allow-empty` in `init_workspace_git` — not explicitly
   specified in the plan; added because a harness seed can legitimately have
   no files yet (surfaced by the test suite), and without it the baseline
   commit `reset_harness()` requires never gets created.
2. Dropped `reset.subprocess.run` mocking in two pre-existing run_skeleton
   tests (see Change 4 notes above) rather than trying to pre-compute the
   dynamically-generated workspace path for a mock's `rev-parse` response.
3. `WorkspaceError` — the plan named it in Change 4 ("Add WorkspaceError
   handling to main()'s except ladder") without defining it in Change 3;
   defined it in `workspace.py` as a `RuntimeError` subclass wrapping
   subprocess/OS failures during create/init/destroy, kept distinct from the
   safety-guard's `ValueError` so a guard trip can never be silently folded
   into a generic "something failed" bucket.
4. `_derive_jsonl_dir` parameter renamed `harness_dir` → `run_dir` (pure
   rename, no behavior change) for clarity given it now always receives the
   workspace path, never `cfg.harness_dir`.

## Files touched

- `scripts/playground/deploy.py`
- `scripts/playground/reset.py`
- `scripts/playground/run_skeleton.py`
- `scripts/playground/workspace.py` (new)
- `scripts/tests/test_playground_deploy.py`
- `scripts/tests/test_playground_run_skeleton.py`
- `scripts/tests/test_playground_workspace.py` (new)

Not committed (per task instructions — developer/task flow owns the commit).
