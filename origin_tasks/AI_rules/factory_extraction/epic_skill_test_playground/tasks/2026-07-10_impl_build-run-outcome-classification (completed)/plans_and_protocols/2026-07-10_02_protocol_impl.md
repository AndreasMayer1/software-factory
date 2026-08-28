---
skills_used:
  - claude-automated-mode
  - claude-watch-tool-reliability
  - task-start
  - claude-route
  - task-resolve
  - claude-write-script
  - verify-quality
  - task-complete
  - claude-commit
---

# Protocol — implementation (TASK-PROC-068-25)

Agent: (main session) 54478fa2-8a57-4e13-ae50-de13ee3e5cb7 · date 2026-07-10

## Delivered (all three in-scope items + tests)

### 1. Four-way + fail-safe classifier (AC-18/AC-19) — `scripts/playground/build.py`
- New `RunOutcome(str, Enum)`: COMPLETE / INTERRUPTED / BLOCKED / ABANDONED / INCONCLUSIVE
  (named-outcome rule, doc/python/architecture.md §Structural rule 2). INCONCLUSIVE = the AC-19
  absent-oracle fail-safe; AC-18's 4 outcomes are exhaustive for an oracle-wired production run.
- New pure `classify_run_outcome(result, workspace, completion_predicate, blocker_detector)` with
  precedence: non-clean termination → INTERRUPTED; else recorded blocker → BLOCKED (checked BEFORE
  the oracle so an escalation is never harvested over); else absent oracle → INCONCLUSIVE; else oracle
  True → COMPLETE / False → ABANDONED.
- `has_recorded_blocker(ws)`: any `automation/pending_feedback/*/question.md` in the copy (generic
  factory escalation convention).
- `_gate_harvest` rewritten to classify → apply disposition. COMPLETE harvests+discards (status
  `complete`); every other outcome PRESERVES the copy and records a DISTINCT terminal status via
  `_OUTCOME_TO_PRESERVE_STATUS` (interrupted→`preserved`, blocked→`blocked`, abandoned→`abandoned`,
  inconclusive→`inconclusive`). Returns `RunOutcome` now; manifest gains `"outcome"`, keeps `"completed"`
  (== COMPLETE) for back-compat.
- Because build_resume `_RESUMABLE_STATUSES` = {running, preserved}, blocked/abandoned/inconclusive are
  NEVER auto-resumed (the core measurement-correctness fix: resume can't fix a skill that stops early).

### 2. Oracle wiring (AC-19 part 1) — new `scripts/playground/acceptance_oracles.py`
- `chainstate_complete_predicate(chain_state_relpath)`: loads `<ws>/<relpath>` via
  backfill_orchestration.load_chain (lazy sys.path insert) → True iff EVERY unit is DONE (strict; an
  escalated/pending chain is NOT complete → never harvested as finished; missing file → False).
- build.py stays generic: `build_acceptance_predicate(cfg)` LAZY-imports the oracle only for
  kind==chainstate → `"ChainState" not in dir(build)` preserved (AC-17). `BuildModeConfig` gains
  `acceptance_oracle_kind` + `chain_state_path`; `run_build_mode`/`resume_run` derive the predicate from
  cfg when none injected (injected wins). CLI: `--acceptance-oracle {chainstate}` + `--chain-state-path`.
  Oracle spec persisted in the run-registry record → cold resume rebuilds the SAME oracle (AC-19 holds
  across resume, not just fresh runs).

### 3. Clean-exit attribution (AC-19 part 2) — `build.py` child_env
- `child_env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"]="0"` (mirrors orchestrate.py `build_env`): a
  still-working background agent can't hold `-p` to a delayed 0 return → no false clean/complete exit.

### Tests
- `test_playground_build.py`: 6 pure `classify_run_outcome` cases (interrupted×2, blocked-precedence,
  complete, abandoned, inconclusive), `has_recorded_blocker`, `build_acceptance_predicate` (none +
  chainstate), integration blocked (child writes pending_feedback), integration inconclusive (no oracle),
  child-env bg-wait ceiling. Updated 2 existing tests to the new contract (deploys-harvests-discards now
  injects a True oracle; preserved-when-incomplete is now ABANDONED).
- `test_playground_build_resume.py`: `_preserve_a_run` now stages a resumable run via a NON-clean child
  exit (returncode=1 → INTERRUPTED → status `preserved`) instead of the removed default-True/predicate-
  False shortcut; new parametrized test proves find_resumable_run SKIPS abandoned/blocked/inconclusive.
- New `test_playground_acceptance_oracles.py`: all-DONE→True; pending→False; escalated→False; empty→False;
  missing→False.

## Verification
- Python gates (`scripts/quality/check_python_gates.sh`): G1 G2 G4 G5 G6 G7 PASS. G3 = only 2 PRE-EXISTING
  baseline failures in `test_aggregate_read_metrics.py` (confirmed failing on clean develop HEAD 15615c4e,
  unrelated to this change — I did not touch that file). All 3099 other tests + all new playground tests pass.
- CLI `--help` shows the new oracle flags.

## Notes
- No new top-level dependency; no CLAUDE.md §11 change (acceptance_oracles.py is an imported library, not a
  generated-file producer or grep-replacement tool).
- EGP: AC-18/AC-19 archetype F/HIGH. Disposition developer-approved 2026-07-10 (authoring gate). Mechanism
  proven here with mocked-subprocess unit/integration tests; full F-fidelity observation of a REAL run is
  the developer's async sign-off surface (this commit).
- Out of scope (untouched): harvest atomicity (068-24), single-runner lease, orchestrate.py.

## Quality review follow-up (2026-07-10_03_quality_review.md — YELLOW, resolved)
quality-checker verdict YELLOW: GREEN on all correctness/AC-fidelity/anti-pattern axes; one non-blocking
gap — the resume-path oracle reconstruction (build_resume `resume_run` rebuilding the chainstate oracle
from the record when `completion_predicate is None`) was untested, so "AC-19 holds across resume" was
unproven for a HIGH/EGP-F AC (fail-safe by construction: broken/missing spec → None → INCONCLUSIVE, never
a false COMPLETE). CLOSED: added `test_resume_reconstructs_chainstate_oracle_from_record_no_injected_predicate`
to test_playground_build_resume.py — a preserved (interrupted) run persists the chainstate oracle spec, the
copy holds an all-DONE ChainState, and resume with NO injected predicate rebuilds the oracle from the record
and reaches COMPLETE (harvest+discard). Python gates re-run: G1/G2/G4/G5/G6/G7 PASS; G3 only the 2 pre-existing
baseline failures (3100 passed). Gap resolved → GREEN.

## Developer EGP-F sign-off (2026-07-14)
Parked 2026-07-10 for the HIGH-consequence EGP-F sign-off on AC-18/AC-19 (referent = a real observed run;
verified here with the child-process boundary mocked). Developer answered (archived
`plans_and_protocols/2026-07-14_04_feedback-checkpoint.md`): **Option 1 — "Sign off on the test evidence,
we'll see later if it really works."** AC-18/AC-19 checked off; task completed. No code change requested.
