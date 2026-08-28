# Protocol 11 — AC-12 (contained-child auth binding) implementation

Task: TASK-PROC-068-11 · 2026-07-04 · implementation-engineer agent (agent ID: 39c55918760b7ead).
Follows plan 10 exactly (`2026-07-04_10_plan_ac12-auth-binding.md`). Implements the three
changes; does NOT commit and does NOT run the live smoke (session-owned per plan §After
implementation).

## Change 1 — scripts/playground/containment.py

- Added `AuthConfigUnavailable(RuntimeError)` next to `ContainmentUnavailable`.
- Added `_auth_config_binds(claude_dir, ccs_dir) -> list[str]`:
  - `os.path.isdir(claude_dir)` false → raises `AuthConfigUnavailable` naming `~/.claude` and
    explaining `ccs` cannot work without it either (symlink web).
  - Always emits `--bind <claude_dir> <claude_dir>`.
  - `os.path.isdir(ccs_dir)` true → also emits `--bind <ccs_dir> <ccs_dir>`; false → silent, no
    error, no extra flag.
  - WHY comment cites the protocol-09 destructive-auto-recovery incident and explains rw +
    both-together + mandatory/optional split.
- `_build_bwrap_cmd` gained keyword-only `claude_dir`/`ccs_dir` params, `None` by default,
  resolved via `os.path.expanduser` at call time (not a module-level constant, so a test that
  monkeypatches HOME still resolves correctly). Calls `_auth_config_binds` and splices its flags
  into the bwrap command, between the harness bind and `--chdir`. The `unshare` fallback
  (`_build_unshare_cmd`) is untouched, per plan (host paths already visible there).
- `wrap_with_containment`'s public signature is unchanged — it still calls `_build_bwrap_cmd(cmd,
  harness_dir)` with implicit real-path defaults; no override plumbing was added there (plan
  scoped the injectable override to `_build_bwrap_cmd` only).

## Change 2 — scripts/playground/run_skeleton.py

- Import list: swapped `scrub_env` for `AuthConfigUnavailable` (scrub_env is still defined in
  containment.py and still used by `scripts/playground/build.py`, unaffected — out of this
  change's scope).
- Step 4 in `run_single_fixture`: replaced `child_env = scrub_env(dict(os.environ), workspace)`
  with `child_env = dict(os.environ)`, with a WHY comment explaining that AC-12's real-path binds
  only work if the child's `HOME` is still the real host home and `CLAUDE_CONFIG_DIR` is still
  inherited — scrubbing HOME to the workspace would point both `claude` and `ccs` at a location
  with no config, defeating the binds. cwd remains the workspace (untouched Step 5 logic).
- `main()`'s except ladder: added `except AuthConfigUnavailable as exc: _LOG.error(...); return 1`
  immediately after the `ContainmentUnavailable` branch (before the generic
  `(OSError, ValueError, RuntimeError)` catch-all, so it gets its own clear message rather than
  falling through to the generic one).
- Touched one stale docstring line in `_derive_jsonl_dir` that referenced `scrub_env()`'s HOME
  redirect (no longer the mechanism in play) — reworded to note the CCS base path is a fixed
  constant independent of the child's HOME, and that AC-12 keeps HOME as the real host home anyway.

## Change 3 — scripts/tests/test_playground_containment.py

Added 7 new tests, all tmp-dir-only (no real `~/.claude`/`~/.ccs` touched):
- `test_auth_config_binds_both_present` — both dirs exist → both `--bind` triples.
- `test_auth_config_binds_claude_only` — ccs absent → only the claude bind, no ccs flag.
- `test_auth_config_binds_claude_absent_raises` — claude absent (ccs present) →
  `AuthConfigUnavailable`, message matches `.claude`.
- `test_auth_config_binds_both_absent_raises` — both absent → `AuthConfigUnavailable`.
- `test_auth_config_binds_are_bind_dir_dir_shape` — asserts the `--bind <dir> <dir>` triple shape.
- `test_build_bwrap_cmd_includes_claude_bind_when_injected_dir_exists` — `_build_bwrap_cmd` with an
  injected tmp `claude_dir` includes it in the emitted binds.
- `test_build_bwrap_cmd_raises_when_injected_claude_dir_absent` — propagates
  `AuthConfigUnavailable` through `_build_bwrap_cmd`.

Also updated two **existing** structural tests (`test_wrap_bwrap_cmd_binds_harness_dir`,
`test_wrap_bwrap_cmd_retains_network`) to pass explicit tmp `claude_dir`/`ccs_dir` overrides
instead of relying on the real `~/.claude` existing on the host — judgment call: this decouples
those tests from host filesystem state even though the real dirs happen to exist in this
devcontainer (verified: both present under `/home/vscode`). `test_wrap_uses_bwrap_when_probe_available`
was left untouched (it goes through the public `wrap_with_containment`, which has no
injectable override for the auth dirs per plan's scope) — it exercises the real
`~/.claude`/`~/.ccs` defaults read-only (`os.path.isdir` checks only, no bwrap execution, so no
mutation risk).
Module docstring's numbered test list updated to add item 5 (AC-12 coverage note).

## Gate / test results

- `scripts/quality/check_python_gates.sh`: G1 lint PASS, G2 type PASS, G3 tests **2 known
  pre-existing failures** in `scripts/tests/test_aggregate_read_metrics.py`
  (`test_aggregate_logs_reads_jsonl`, `test_aggregate_logs_skips_malformed_lines`) — confirmed via
  `git stash` + re-run against the pre-change tree: same 2 failures, same file, unrelated to this
  change (2 failed, 22 passed in that file both before and after). G4 no-handrolled PASS, G5
  print-discipline PASS, G6 complexity PASS, G7 canonical-lib PASS.
- `python3 -m pytest scripts/tests/test_playground_*.py -q`: **119 passed**, 0 failed.

## Deviations / judgment calls

- Updated two pre-existing tests' `_build_bwrap_cmd` calls to inject tmp auth dirs (see Change 3)
  rather than leaving them to depend on real `~/.claude` presence — a portability/hygiene
  improvement within the spirit of "tests must use tmp dirs", not a deviation from the plan's
  contract.
- Reworded one stale docstring line in `_derive_jsonl_dir` referencing `scrub_env` (Change 2) —
  accuracy fix, not a behavior change.
- No other deviations from plan 10.

## Not done here (session-owned, per plan §After implementation)

- Live smoke run of `run_skeleton.py` against the real `~/.claude`/`~/.ccs`.
- Commit of the whole mechanism (containment/workspace/deploy/reset/run_skeleton + tests +
  protocols 07/08/09/10/11).
- Unparking TASK-PROC-068-11 via pending_feedback.
