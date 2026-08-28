# Plan — build/maintain run-outcome taxonomy (TASK-PROC-068-25, REQ-PROC-068 AC-18/AC-19)

Agent: (main session) 54478fa2-8a57-4e13-ae50-de13ee3e5cb7

## Contract (verbatim ACs)
- **AC-18** (F, HIGH): every run resolves to exactly one classified outcome that determines its disposition:
  - **complete** = clean child exit ∧ injected acceptance oracle confirms finished → the ONLY harvested outcome.
  - **interrupted** = non-clean termination (usage-limit / timeout / hung / crash) → preserve copy for resume (AC-14/15/16).
  - **blocked** = clean exit ∧ explicit blocker/escalation artifact recorded → developer-facing pause; NOT harvested, NOT a skill-under-test failure.
  - **abandoned** = clean exit ∧ oracle reports not-finished ∧ no blocker artifact → run FAILURE attributable to the skill-under-test's completion guidance; NOT harvested, NOT auto-resumed.
- **AC-19** (F, HIGH):
  - part 1: gate never certifies complete without a POSITIVE oracle result; **absent oracle → "cannot certify complete"** → neither harvested nor reported successful.
  - part 2: a clean child process-exit reflects the child's OWN completion decision — a still-working background agent inside the child cannot cause a false clean/complete exit.

## Root problem
`_gate_harvest` today: `is_complete = predicate(ws) if predicate else True`. Absent oracle DEFAULTS to
True → premature clean exit harvested as success (destroys the core measurement) AND (if routed to
resume) loops forever (resume can't fix a skill that stops early). Two clean-exit-not-complete cases
(blocked, abandoned) collapse into "preserved" today and get auto-resumed.

## Design

### RunOutcome (build.py)
`class RunOutcome(str, Enum)`: COMPLETE / INTERRUPTED / BLOCKED / ABANDONED / INCONCLUSIVE.
INCONCLUSIVE = AC-19 fail-safe (no oracle injected → cannot certify). Never arises for a properly
oracle-wired run; documented as the AC-19 guard path (AC-18's 4 outcomes assume oracle present).

### Classifier — `classify_run_outcome(result, workspace, completion_predicate, blocker_detector)`
Pure fn (testable with fabricated LaunchResult). Precedence:
1. `not (result.succeeded and result.reason == "exited")` → **INTERRUPTED** (termination dominates).
2. clean exit → `blocker_detector(ws)` True → **BLOCKED** (conservative: never harvest over a recorded
   escalation; false-blocked preserves the copy = safe, false-complete = unsafe).
3. `completion_predicate is None` → **INCONCLUSIVE** (AC-19: absent oracle).
4. `completion_predicate(ws)` True → **COMPLETE**; else → **ABANDONED**.

### Dispositions in `_gate_harvest` (returns `(RunOutcome, harvested, preserved|None)`)
- COMPLETE → harvest_authored + destroy_workspace; registry status=complete.
- everything else → PRESERVE copy (workspace_preserved=path), skip harvest; registry status =
  interrupted→`preserved` (backward-compat, resumable) / blocked→`blocked` / abandoned→`abandoned` /
  inconclusive→`inconclusive`. Record `outcome` on the record.
- `_RESUMABLE_STATUSES` in build_resume stays {running, preserved} ⇒ blocked/abandoned/inconclusive are
  NEVER auto-resumed (goal: "resume path never re-launches" abandoned). No change to find_resumable_run.

### Blocker detector (generic, factory-wide)
`has_recorded_blocker(ws)`: any `automation/pending_feedback/*/question.md` under ws. Escalating skills
(any under test) surface via pending_feedback (claude-automated-mode). Injectable; default used when None.

### Acceptance oracle wiring (AC-19 part 1, item 2)
- NEW module `scripts/playground/acceptance_oracles.py`: `chainstate_complete_predicate(chain_state_relpath)`
  → returns `Callable[[str],bool]` that loads `<ws>/<relpath>` via backfill_orchestration.load_chain
  (lazy sys.path insert of factory/layer_derivation, mirroring test convention) and returns
  `all(u.status is UnitStatus.DONE for u in state.units)` — STRICT all-DONE (escalated/pending ⇒ not done,
  so an escalated chain w/o pending_feedback is abandoned, never harvested).
- build.py keeps the generic seam; `build_acceptance_predicate(cfg)` LAZY-imports the oracle only when
  `cfg.acceptance_oracle_kind == "chainstate"` ⇒ `"ChainState" not in dir(build_module)` stays true (AC-17 test).
- `BuildModeConfig` gains `acceptance_oracle_kind: str=""`, `chain_state_path: str=""`.
- `run_build_mode`: predicate = injected `completion_predicate` (tests win) else `build_acceptance_predicate(cfg)`.
- `write_run_registry_running` persists oracle kind + chain_state_path ⇒ resume reconstructs the SAME
  oracle from the record ALONE (no re-specification), matching build_resume's cold-reattach philosophy.
- `main()` CLI: `--acceptance-oracle {chainstate}` + `--chain-state-path <rel>` → cfg. This is the
  production build-mode invocation that "must actually pass it".

### Clean-exit attribution (AC-19 part 2, item 3)
`child_env` (build.py `launch_and_gate`): add `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS="0"` — mirrors
orchestrate.py `build_env` (a still-working bg agent can't make `-p` return 0 prematurely).

## Tests
- Pure `classify_run_outcome`: interrupted (rc!=0 / reason hung/timeout), blocked (blocker True),
  complete (oracle True), abandoned (oracle False, no blocker), inconclusive (oracle None).
- Integration via run_build_mode: complete harvest+discard (exists, keep); abandoned preserve+status;
  blocked preserve (child writes pending_feedback) + status blocked; inconclusive (no oracle) no-harvest
  no-success + status inconclusive.
- `test_child_env_sets_bg_wait_ceiling_zero` (capture popen env).
- `test_abandoned_run_is_not_resumable` (find_resumable_run skips abandoned record).
- NEW `test_playground_acceptance_oracles.py`: all-DONE→True, one PENDING→False, missing file→False.
- UPDATE existing:
  - `test_run_build_mode_deploys_seeds_harvests_and_discards`: inject `completion_predicate=lambda:True`
    (was relying on removed default-True) + docstring.
  - `test_workspace_is_out_of_project_git_repo_and_preserved_when_incomplete`: status preserved→abandoned
    (clean exit + oracle False + no blocker = abandoned); copy still preserved.

## Governance
scripts/ change ⇒ claude-write-script + Python gates (REQ-PROC-051) + verify-quality before task-complete.
EGP: AC-18/AC-19 archetype F HIGH — developer sign-off at verification time (approved 2026-07-10 authoring gate).
Out of scope: harvest-atomicity (TASK-PROC-068-24), lease mechanism, orchestrate.py.
