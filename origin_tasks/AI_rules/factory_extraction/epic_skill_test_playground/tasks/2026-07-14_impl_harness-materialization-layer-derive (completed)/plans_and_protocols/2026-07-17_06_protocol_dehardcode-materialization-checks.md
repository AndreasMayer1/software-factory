# Protocol — De-hardcode the two materialization check scripts (project-agnostic)

Date: 2026-07-17 · agent `aa129601e70ef5551` · implementation-engineer subagent
Bugfix scope, no requirement change (REQ-PROC-074-02 AC-06 / AC-04 were already
project-agnostic in wording; only the implementation was hardwired to flutter_app).

## Why this protocol exists here

This is not a fix to Blocker 2 in `2026-07-15_05_blocker_provenance-harvest-gap.md` (the
provenance-cannot-resolve-post-harvest problem is still open — the ideation ledger + index still
live only in the ephemeral build-mode copy and are never harvested). This protocol closes a
narrower, separately-scoped bug: the two `check_materialization_*` scripts could not even be
**pointed at** another project's materialization artifact, because their project-root resolution
was hardwired to `Path(__file__).resolve().parents[N]` (always flutter_app, or whatever copy the
script file itself happens to be running from) instead of being derived from the artifact path the
caller supplies. Fixing this is a **precondition** for any future Option A/B fix to Blocker 2 (both
of those options still need the host-side check to be able to resolve a foreign project's
artifact) but does not by itself resolve AC-1 for TASK-PROC-068-26.

## What changed

### `scripts/user_needs/check_materialization_provenance.py`
- Added `_derive_project_root(artifact_path) -> Path` = `artifact_path.resolve().parents[2]` (the
  materialization artifact is always at
  `<project_root>/requirements_user_needs/product_materialization/product_materialization.md`).
- `main()` now derives `project_root` from `--artifact`, then defaults `index_path` to
  `project_root/.factory/ideation/index.yaml` and `repo_root` to `project_root` — both overridable
  via new `--index PATH` / `--repo PATH` flags. `main()` passes the resolved paths through to
  `check()` explicitly (previously it called `check(Path(args.artifact))` and let `check()`'s own
  defaults silently fall back to the flutter_app-anchored module constants `DEFAULT_INDEX`/`ROOT`).
- `_REPO_ROOT` (used only for the `sys.path` bootstrap so `scripts.util.task_folder_resolver` is
  importable) and the module-level `DEFAULT_ARTIFACT`/`DEFAULT_INDEX`/`ROOT` constants are
  unchanged — they still anchor off `__file__` and remain the correct choice for the bare
  no-argument invocation (see verification below) and as `check()`'s own fallback defaults for
  programmatic callers that don't pass `index_path`/`repo_root`.

### `scripts/user_needs/check_materialization_flow_reference.py`
- Same treatment: added `_derive_project_root`, `main()` now derives `project_root` from
  `--artifact` and defaults `--flows-root` to `project_root/requirements_user_needs/user_flows`,
  overridable via the (already-existing) `--flows-root` flag (its default changed from the
  `__file__`-anchored `DEFAULT_FLOWS_ROOT` to `None`, resolved in `main()` body).
- `DEFAULT_ARTIFACT`/`DEFAULT_FLOWS_ROOT`/`ROOT` module constants unchanged, same rationale as
  above (bare invocation + `check()`'s own defaults).

## New CLI surface

```
check_materialization_provenance.py [--artifact PATH] [--index PATH] [--repo PATH]
check_materialization_flow_reference.py [--artifact PATH] [--flows-root PATH]
```

`--index`/`--repo`/`--flows-root` are optional overrides; when omitted they are derived from
`--artifact`'s own project root (`parents[2]`), not from where the script file itself lives.

## Tests added

`scripts/tests/test_check_materialization_provenance.py`:
- `test_main_derives_project_root_from_artifact_for_foreign_project` — points `--artifact` at a
  wholly separate tmp-dir "foreign project" (its own git repo, its own `.factory/ideation/index.yaml`)
  with NO `--index`/`--repo` given; asserts `main()` returns 0, proving resolution happened against
  the foreign project, not flutter_app. This fails on pre-fix code (old `main()` would fall back to
  flutter_app's `DEFAULT_INDEX`/`ROOT` and return 1/MISSING).
- `test_main_explicit_index_and_repo_override_artifact_derived_defaults` — artifact sits under a
  project root with no ideation index at all; `--index`/`--repo` explicitly point elsewhere; asserts
  the override wins.
- Rewrote `test_main_returns_zero_on_ok` to place the artifact at the canonical nested path under a
  real git repo and drop the `monkeypatch.setattr(..., DEFAULT_INDEX/ROOT)` calls — `main()` no
  longer reads those module constants when an explicit `--artifact` is given, so the old
  monkeypatch-based test would false-pass without exercising the real code path. Confirmed the new
  version fails against the pre-fix `main()` (returns 1) and passes against the fixed one.

`scripts/tests/test_check_materialization_flow_reference.py`:
- `test_main_derives_flows_root_from_artifact_for_foreign_project` — same shape, artifact + flow
  under a foreign tmp-dir project, no `--flows-root` given, asserts OK.
- `test_main_explicit_flows_root_overrides_artifact_derived_default` — artifact-derived
  `user_flows/` dir exists but is empty (would DRIFT if used); explicit `--flows-root` points at
  the real flow; asserts the override wins.
- `_write_artifact` test helper gained `root.mkdir(parents=True, exist_ok=True)` (non-behavioral —
  prior tests always passed an already-existing `tmp_path`; new tests pass a not-yet-created nested
  project directory).

## Verification (manual, beyond pytest)

1. Bare no-arg invocation on both scripts still prints the same `OK ...` line and exits 0 against
   flutter_app's real artifact (confirms the "keep the bare invocation working exactly as today"
   requirement — `parents[2]` of the `__file__`-derived `DEFAULT_ARTIFACT` still resolves to
   flutter_app's own root, since the script always executes from wherever it physically lives,
   including inside a deployed build-mode copy).
2. Built a synthetic `/tmp/demo_project` (separate git repo, separate `.factory/ideation/index.yaml`,
   separate `product_materialization.md` with its own `decided_by`) and ran both scripts with only
   `--artifact /tmp/demo_project/...` — both printed `OK` and exited 0, with no `--index`/`--repo`/
   `--flows-root` flags needed. This is the concrete proof the scripts are now project-agnostic.
3. `--help` output on both scripts documents the new/re-anchored flags.

## Gate results (final, GREEN for this change)

```
scripts/quality/check_python_gates.sh
```

```
  PASS   G1 lint
  PASS   G2 type
  FAIL   G3 tests   <- pre-existing baseline failures, NOT a regression (see below)
  PASS   G4 no-handrolled
  PASS   G5 print-discip.
  PASS   G6 complexity
  PASS   G7 canonical-lib
```

Targeted run for the two files touched by this task:
```
python3 -m pytest scripts/tests/test_check_materialization_provenance.py \
  scripts/tests/test_check_materialization_flow_reference.py -q
...
25 passed in 0.40s
```

`python3 -m ruff check` on all 4 changed files: `All checks passed!`

### G3 residual note (not a regression)

The full-suite G3 run reports 2 failures in `scripts/tests/test_aggregate_read_metrics.py`
(`test_aggregate_logs_reads_jsonl`, `test_aggregate_logs_skips_malformed_lines`) — confirmed via
`git stash` to fail identically on unmodified `develop` HEAD (04ad97df), unrelated to
`scripts/aggregate_read_metrics.py` or `.jsonl` log format and untouched by this task's scope. Not
a new finding introduced by this change; left as-is per the back-pressure protocol's "block only on
findings YOUR change introduced" rule.

## Residual / not addressed here

- Blocker 2 (provenance harvest gap for TASK-PROC-068-26 AC-1) is still open — this fix makes the
  host-side check *able* to resolve a foreign project's artifact, but the harness's
  `product_materialization.md` (once authored via a build-mode run) would still carry a
  `decided_by` pointing at ideation ledger/index entries that live only in the discarded ephemeral
  copy, never harvested into either flutter_app's or `test_harness_app`'s own `.factory/ideation/`.
  Options A/B/C from the blocker file still apply; this task did not choose among them.
- Blocker 1 (deploy.py leaking flutter_app's `product_materialization.md` into seeded copies) is
  also untouched — out of scope per the task instructions (deploy.py explicitly excluded).
