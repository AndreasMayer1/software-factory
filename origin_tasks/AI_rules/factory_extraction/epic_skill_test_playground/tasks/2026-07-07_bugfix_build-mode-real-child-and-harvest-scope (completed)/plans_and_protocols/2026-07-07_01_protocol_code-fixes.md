# Protocol 01 — Code fixes (Defects 1 & 2) + unit tests

Task: TASK-PROC-068-19 · Date: 2026-07-07 · Mode: code-bugfix (slim/scripts)
Session: ed35d6af-be83-477a-a5d1-1339cef455f0 (gmail2)

## Summary

Fixed both build-mode defects in the source scripts (never fixed after
TASK-PROC-068-11 hand-patched them in a throwaway driver) and updated the unit
tests so both fixes are asserted, not silently faked past.

## Defect 1 — build-mode auth (AC-1)

`scripts/playground/build.py`

- **Before**: `child_env = scrub_env(dict(os.environ), cfg.isolated_dir)` — this
  redirected `HOME` into the (unbound) isolated copy, so the contained `claude`
  expanded `~/.claude` → `<isolated_dir>/.claude` and failed to authenticate,
  defeating AC-12's real-path bind.
- **After**: `child_env = dict(os.environ)` — inherits the REAL HOME +
  CLAUDE_CONFIG_DIR unchanged, so `containment._auth_config_binds`' real-path
  `~/.claude` bind resolves. This mirrors the working reference at
  `run_skeleton.py:238` (real HOME, cited AC-12). Added a why-comment; removed
  the now-unused `scrub_env` import.
- Rationale for NOT making scrub_env conditional on a bwrap-unavailable
  fallback: `run_skeleton.py` uses real HOME **unconditionally** (never calls
  scrub_env), and scrub_env would break auth on every path — bwrap (bind is at
  real path), unshare (host tree present, ~/.claude at real path), and the
  PLAYGROUND_ALLOW_UNCONTAINED opt-out (no isolation). So full alignment with
  run_skeleton (real HOME, no scrub_env) is correct and simplest.

## Defect 2 — harvest over-inclusion, fixed at the root (AC-2)

`scripts/playground/deploy.py`

- Added `os.path.join("requirements_tasks", "process")` to `_SUBFOLDER_EXCLUDES`.
- Updated the exclude-set comment to record *why*: the ~130
  `requirements_tasks/process/AI_rules/**/requirements.md` files are the specs
  that DEFINE the factory's own skills/scripts — authoring-time inputs, read
  only when developing the factory, which never happens inside the harness. They
  had no runtime justification for being deployed; deploying them let the
  full-registry harvest glob `requirements_tasks/**/requirements.md` sweep them
  into `test_harness_app/`. Build mode harvests-before-discard and never
  git-resets, so (unlike test-mode) the over-inclusion persisted. Excluding
  process/ removes it at the root — nothing to sweep in.

## Tests updated (AC-5)

`scripts/tests/test_playground_build.py`
- New `test_run_build_mode_child_env_preserves_real_home`: captures the env
  handed to the popen boundary and asserts `HOME == /home/vscode` (real) and
  `HOME != <isolated_dir>`. Fails against the pre-change scrub_env code.

`scripts/tests/test_playground_deploy.py`
- Inverted `test_deploy_copies_factory_requirements_tasks_subfolder`
  → `test_deploy_excludes_factory_process_corpus`: asserts
  `requirements_tasks/process` is ABSENT from a deployed copy. Updated the
  `tmp_whole_host` fixture comment so the process/ file is a MUST-NOT-copy
  example.

## Quality gates

`scripts/quality/check_python_gates.sh`:
- G1 lint PASS · G2 type PASS · G4 PASS · G5 PASS · G6 PASS · G7 PASS.
- G3 tests: FAIL is **pre-existing baseline** — `test_aggregate_read_metrics.py`
  (2 failures) + `test_check_dependency_usage.py` (collection error). Confirmed
  by `git stash` of my 4 files: identical failures on clean develop. My own two
  test modules pass fully (38/38). No new G3 finding introduced by this change.

## Remaining (next protocol)

- AC-3 (AC-10 guard): real factory skill completes end-to-end with process/
  excluded.
- AC-4 (combined AC-11 ∧ AC-12): real authenticating `claude -p` child through
  `run_build_mode()`; assert child authenticated, wrote a product-def artifact,
  and target gained ONLY that artifact (zero process files).
- Static pre-check done: skills referencing `requirements_tasks/process/**` do so
  as example paths / task-folder locations / soft "refer to" pointers — the
  empirical run is the arbiter per the goal. If a real run actually reads a
  process `requirements.md` and fails, ESCALATE (AC-10 tension), do not work
  around.
