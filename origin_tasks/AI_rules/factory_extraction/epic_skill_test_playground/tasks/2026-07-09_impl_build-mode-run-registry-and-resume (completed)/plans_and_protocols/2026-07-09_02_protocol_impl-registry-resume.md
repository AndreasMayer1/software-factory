# Protocol — Deliverables 1/2/3/5 implementation (TASK-PROC-068-22)

Agent ID: a3a028cba9882ec13 (implementation-engineer, this session).

Scope executed: Deliverables 1, 2, 3, 5 of
`2026-07-09_01_plan_run-registry-and-resume.md`. Deliverables 4 (skill) and 6 (real-artifact
folded verification) explicitly OUT of scope for this session — not touched, not committed.

Note: on starting, `.claude/skills/playground-build-resume/` (Deliverable 4) and this task's
`plans_and_protocols/` dir already existed on disk (untracked), created by a prior/parallel step.
Its documented CLI surface (`build_resume.py list [--registry-dir]`, `build_resume.py resume
[--registry-dir]`, manifest JSON to stdout) matched the plan and was treated as the confirmed
target shape for Deliverable 2 — no conflict, nothing in that skill file was edited.

## Deliverable 1 — `scripts/playground/build.py`

- Registry constants made public: `RUN_REGISTRY_DIRNAME`, `RUN_STATUS_RUNNING/COMPLETE/PRESERVED`,
  new `BASELINE_SIDECAR_SUFFIX = ".baseline.json"`. Old leading-underscore names kept as aliases
  (`_RUN_REGISTRY_DIRNAME = RUN_REGISTRY_DIRNAME`, etc.) — no in-module reference broke.
- `write_run_registry_running(cfg, workspace, *, jsonl_dir, baseline)`: new required
  keyword-only params. Record gained `prompt`, `jsonl_dir`, `registry_path` (== `cfg.registry_path`,
  the artifacts.yaml path — NOT the run-registry record path; see naming-collision note below),
  `workspace_root`, `max_budget_usd`, `baseline_snapshot_ref`. The baseline dict is persisted to a
  sidecar `<uuid>.baseline.json` in the registry dir; the record stores only the sidecar's path.
- **Refactor**: extracted the launch->gate tail of `run_build_mode` into a new public
  `launch_and_gate`. Exact signature:

  ```python
  @dataclass
  class LaunchAndGateInputs:
      workspace: str
      globs: list[str]
      baseline: dict[str, str]
      registry_path: str      # the RUN-REGISTRY record's own path (not cfg.registry_path)
      jsonl_dir: str
      ledger: CostLedger

  def launch_and_gate(
      cfg: BuildModeConfig,
      inputs: LaunchAndGateInputs,
      *,
      launch_deps: LaunchDeps | None = None,
      probe_fn: object = None,
      completion_predicate: Callable[[str], bool] | None = None,
  ) -> dict[str, Any]:
  ```

  Returns the manifest WITHOUT `seeded_paths` (a fresh-run-only concept) — `run_build_mode` adds
  `manifest["seeded_paths"] = seeded` after the call; `resume_run` adds `manifest["seeded_paths"] = []`
  (documented: resume never re-seeds, AC-15).
- `run_build_mode` now: derives `jsonl_dir` BEFORE the registry write (moved up, per plan), writes
  the enriched registry record, then delegates the entire launch->gate tail to `launch_and_gate`.

### Deviation from the plan's literal signature (documented, not a scope change)

The plan's prose spells `launch_and_gate(cfg, *, workspace, globs, baseline, registry_path,
jsonl_dir, ledger, launch_deps, probe_fn, completion_predicate)` — 10 flat params. That would
violate PLR0913 (`max-args = 5`, `pyproject.toml:57`, G6-gated). Grouped `workspace, globs,
baseline, registry_path, jsonl_dir, ledger` into `LaunchAndGateInputs` (mirrors the pre-existing
`_HarvestGateInputs` dataclass in the same file, and doc/python/architecture.md's "group params
into a dataclass" decomposition strategy). Final signature: `cfg, inputs, *, launch_deps, probe_fn,
completion_predicate` = 5 total params, exactly at the gate limit. All ten named concerns from the
plan are present, just grouped. Same reasoning applied to `completion_poll.poll_until_complete`
(see Deliverable 3 below).

### Naming-collision note (implementation decision, not plan-specified)

`BuildModeConfig.registry_path` means the ARTIFACTS registry (`.factory/registry/artifacts.yaml`).
`_HarvestGateInputs`/`LaunchAndGateInputs.registry_path` means the RUN-REGISTRY record's own file
path (whose status field the gate flips). These are two different things with the same name,
already true before this task (pre-existing in `_HarvestGateInputs`). `build_resume.py` needed a
way to know the run-registry record's OWN path for `resume_run` to pass into `LaunchAndGateInputs`,
since the on-disk record does not carry its own path. Resolved by having `read_run_record` tag the
loaded dict with a synthesized (never-persisted) `_source_path` key, kept deliberately distinct
from the record's existing `registry_path` key to avoid silently corrupting
`load_product_definition_globs`.

## Deliverable 2 — `scripts/playground/build_resume.py` (NEW)

Functions: `read_run_record`, `list_runs` (excludes `*.baseline.json` sidecars), `find_resumable_run`
(status in {running, preserved} AND `workspace_path` exists on disk), `load_baseline`, `resume_run`
(reconstructs `BuildModeConfig` from the record alone, loads globs via `load_product_definition_globs`,
loads the baseline sidecar, calls `build.launch_and_gate` with the RECORDED workspace/jsonl_dir/
baseline — never calls `_prepare_workspace` / `create_workspace` / `deploy_candidate` /
`init_workspace_git`, AC-15). CLI: `list [--registry-dir D]`, `resume [--registry-dir D]`
(default `<worktree_root>/.playground_runs`), manifest JSON to stdout. Tier: C (mirrors build.py's
own tier annotation despite being test-imported — same precedent build.py itself already sets).

## Deliverable 3 — `scripts/playground/completion_poll.py` (NEW, tier B)

`compute_poll_interval(remaining_units, *, floor_secs=60, ceiling_secs=900, secs_per_unit=60) -> int`
as specified. `poll_until_complete` grouped `floor_secs/ceiling_secs/secs_per_unit/max_polls` into
a `PollLimits` dataclass (mirrors `launch_adapter.SessionConfig`/`LaunchRequest` split: pure config
vs. the injectable `sleep` callable kept as its own parameter) to stay within PLR0913 — final
signature `poll_until_complete(is_complete, remaining_units_fn, *, sleep=time.sleep, limits=None)`,
4 total params.

## Deliverable 5 — tests

- `scripts/tests/test_playground_build.py`: added
  `test_registry_record_carries_resume_fields_and_baseline_sidecar` — asserts prompt/jsonl_dir/
  registry_path/workspace_root/max_budget_usd on the record, and that the baseline sidecar is
  re-readable and contains the pre-child snapshot.
- `scripts/tests/test_playground_build_resume.py` (NEW, 9 tests): `list_runs` sidecar exclusion,
  `read_run_record` source-path tagging, `find_resumable_run` selecting preserved+existing-workspace
  and skipping complete/missing-workspace, `load_baseline`, and two `resume_run` tests — one
  asserting `create_workspace`/`deploy_candidate`/`init_workspace_git` are NEVER called
  (monkeypatched to raise, AC-15 tripwire), one asserting a resumed complete run harvests the
  child-authored net-new file into `target_project_dir` and discards the reused workspace, using
  real tmp dirs (the `_authoring_deps`/`_setup_build_dirs` pattern duplicated from
  `test_playground_build.py`, kept test-file-local per doc/python/testing.md's test-isolation rule).
- `scripts/tests/test_completion_poll.py` (NEW, 7 tests): interval scaling, floor/ceiling clamps
  (default and custom), loop-stops-on-complete (no sleep), interval-per-tick scaling across a
  3-tick sequence, and `max_polls` bound honoured.

## Gate run — final result

```
GATE: G1 lint            PASS  (All checks passed! — one I001 import-order finding auto-fixed
                                 via `ruff check --fix` on build_resume.py, re-verified clean)
GATE: G2 type            PASS  (Success: no issues found in 305 source files)
GATE: G3 tests            FAIL (2 failed, 3070 passed, 17 skipped, 6 xfailed — the 2 failures are
                                 test_aggregate_read_metrics.py::test_aggregate_logs_reads_jsonl and
                                 ::test_aggregate_logs_skips_malformed_lines, PRE-EXISTING on develop,
                                 unrelated to this task's files — confirmed via git log showing no
                                 change to that module/test in this diff)
GATE: G4 no-handrolled    PASS
GATE: G5 print-discip.    PASS
GATE: G6 complexity       PASS
GATE: G7 canonical-lib    PASS
```

All 37 tests in the three touched/new test files (`test_playground_build.py`,
`test_playground_build_resume.py`, `test_completion_poll.py`) pass individually
(`pytest -v` run separately, 37 passed).

## Files touched

- `scripts/playground/build.py` (modified)
- `scripts/playground/build_resume.py` (new)
- `scripts/playground/completion_poll.py` (new)
- `scripts/tests/test_playground_build.py` (extended)
- `scripts/tests/test_playground_build_resume.py` (new)
- `scripts/tests/test_completion_poll.py` (new)

Not committed (per instruction) — working tree left with these changes present.
