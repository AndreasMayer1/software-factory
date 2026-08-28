# Quality review — TASK-PROC-068-25 (REQ-PROC-068 AC-18/AC-19)

Reviewer: quality-checker agent · date 2026-07-10 · cadence: --per-change

## Verdict: STATUS: YELLOW

All Python quality gates pass except two PRE-EXISTING, unrelated G3 baseline
failures (confirmed failing identically on clean develop HEAD 15615c4e via
`git stash` before/after comparison — `test_aggregate_read_metrics.py::
test_aggregate_logs_reads_jsonl` / `test_aggregate_logs_skips_malformed_lines`).
G1/G2/G4/G5/G6/G7 all PASS. No Dart files changed (Dart gates N/A).

## What was verified

- `RunOutcome` enum (named-outcome rule, doc/python/architecture.md) with 5
  cases; `classify_run_outcome` precedence exactly matches AC-18/AC-19:
  non-clean termination -> INTERRUPTED (dominates, oracle never consulted) ->
  recorded blocker -> BLOCKED (checked before oracle, fail-safe direction) ->
  absent oracle -> INCONCLUSIVE (AC-19 fail-safe) -> oracle True/False ->
  COMPLETE/ABANDONED. Verified both the pure decision function AND its
  wiring through `_gate_harvest`/`run_build_mode` at integration level (real
  `harvest_authored`/`destroy_workspace`/registry-write execute for real in
  the tests; only the child `popen` boundary is mocked — the load-bearing
  logic under test is genuinely exercised, not stubbed).
- `_RESUMABLE_STATUSES = {running, preserved}` in build_resume.py confirmed
  to exclude blocked/abandoned/inconclusive via a parametrized test
  (`test_find_resumable_run_skips_non_resumable_outcomes`) — the core
  "resume can't fix a skill that stops early" invariant holds.
- `chainstate_complete_predicate`: strict all-DONE semantics tested against
  independently-constructed ChainState fixtures (all-done / one-pending /
  one-escalated / empty / missing-file) — genuinely external referents, no
  self-comparison against the subject's own output (oracle-independence axis,
  REQ-PROC-046 AC-14: clean).
- Would the new tests have caught the pre-change bug? Yes —
  `test_classify_inconclusive_on_absent_oracle` and
  `test_run_build_mode_inconclusive_when_no_oracle_injected` explicitly pin
  "absent oracle -> INCONCLUSIVE, never harvested" where the old code's
  `predicate(ws) if predicate else True` would have produced `True` /
  harvested. Confirmed no remnant of the old default-True logic anywhere in
  build.py or build_resume.py (`grep` clean).
- `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` set unconditionally in `child_env`
  and asserted via captured-popen-env test — matches orchestrate.py's
  `build_env` defense.
- No anti-pattern hits: no hand-rolled YAML (ruamel.yaml via
  `load_product_definition_globs`), no blanket `except Exception`/bare
  `except:` in the reviewed files, magic strings for statuses/reasons are all
  named module constants (`RUN_STATUS_*`, `_REASON_EXITED`,
  `ACCEPTANCE_ORACLE_CHAINSTATE`), functions stay small and single-purpose
  (G6 complexity gate green). Tier headers correct: build.py tier C
  (pre-existing), acceptance_oracles.py tier B (reusable, imported library) —
  correctly the new module, not folded into build.py, preserving AC-17's
  `"ChainState" not in dir(build)` invariant (asserted by an existing test).
- No new top-level dependency; no `doc/`-editable-generated-file touched
  outside the sanctioned `scripts/quality/proposals/` path. WHY comments are
  thorough and correctly source-cited throughout both new/changed modules.
- `covers.acceptance_criteria: [AC-18, AC-19]` both exist verbatim in the
  parent `requirements.md` (lines 70/74, 189/190) and match the implemented
  semantics exactly.

## Gap found (non-blocking, flagged for follow-up)

**`build_resume.py`'s new oracle-reconstruction-from-record path is entirely
untested.** The diff adds, in `resume_run`:
```python
acceptance_oracle_kind=record.get("acceptance_oracle_kind", ""),
chain_state_path=record.get("chain_state_path", ""),
...
if completion_predicate is None:
    completion_predicate = build_acceptance_predicate(cfg)
```
Every existing `resume_run(...)` call in `test_playground_build_resume.py`
passes an explicit `completion_predicate=` kwarg, so this reconstruction
branch (record -> cfg -> `build_acceptance_predicate` -> real chainstate
oracle) is never exercised by any test. Likewise no test asserts that
`write_run_registry_running` actually persists `acceptance_oracle_kind` /
`chain_state_path` into the record (only `prompt`/`jsonl_dir`/
`registry_path`/`workspace_root`/`max_budget_usd` are asserted in
`test_registry_record_carries_resume_fields_and_baseline_sidecar`).

This matters because the plan/protocol explicitly claim "AC-19 holds across
resume, not just fresh runs" — that specific claim is currently unproven by
any test, for a HIGH-consequence / EGP-F acceptance criterion.

**Why this is YELLOW and not RED**: the code is a straightforward field
passthrough mirroring the already-tested `run_build_mode` equivalent, and any
failure mode here is fail-safe by construction — a missing/mis-threaded
`acceptance_oracle_kind` on resume yields `""` -> `build_acceptance_predicate`
returns `None` -> INCONCLUSIVE (preserved, never harvested, never reported
successful), never a false COMPLETE. So the untested path cannot silently
produce the dangerous outcome (premature harvest) even if broken; it can only
under-resume (safe direction). Recommend adding, before closing out the
async EGP sign-off: a test that (1) asserts the record carries
`acceptance_oracle_kind`/`chain_state_path`, and (2) drives `resume_run`
with `completion_predicate=None` + a real chain-state fixture in the
preserved workspace, proving the reconstructed oracle actually classifies
COMPLETE/ABANDONED correctly across the cold-resume boundary.

## Minor note (cosmetic, not actionable)

No pure-`classify_run_outcome` test pins that a non-clean termination
dominates a simultaneous `blocker_detector=True` (only inferable from control
flow: `blocker_detector` is never even called once the termination guard
returns). Fine as-is given the short-circuit structure, but a one-line test
would make the precedence claim self-evident rather than inferred.
