# GATHER — Context Summary

Ideation run for TASK-PROC-068-20 (make the deployed build-mode derivation run resumable).
Ledger: `2026-07-09_001_ideation_ledger.yaml`. Effort: Standard. Placement: inline (see ledger `meta`).

## Prior-run index

Not market/name/competitor-facing → no prior-art web leaf. No prior *ideation* run in the index matched
this exact problem domain; the closest prior work is the brownfield-layer-derivation-mechanism synthesis
(REQ-PROC-071 lineage) which established the LOCAL chain's resumability — reused here as a constraint,
not re-derived.

## Information Map (topic-scoped — names/signatures/purposes, not full content)

### The gap — the single-shot deployed wrapper
- `scripts/playground/build.py::run_build_mode(cfg, *, launch_deps, probe_fn)` — the whole deployed
  build/maintain run. Linear, synchronous, single-shot:
  1. `deploy_candidate(host, isolated)` — whole factory into a fresh `tempfile.mkdtemp()` copy.
  2. `sync_product_definition(target, isolated, globs)` — seed the copy with test_harness_app's current
     product-definition state.
  3. `snapshot_product_definition(isolated, globs)` → `pre_child_state` (hash baseline for net-new harvest).
  4. `check_budget(ledger)`.
  5. `wrap_with_containment(cmd, isolated)` + child env keeps REAL HOME (AC-12 auth bind).
  6. `result = run_with_hung_detection(LaunchRequest(...))` — launches ONE `claude -p` child.
  7. `record_run(ledger, uuid, result.stdout)`.
  8. `harvest_authored(isolated, target, globs, pre_child_state)` — copy back net-new/modified files.
  9. `shutil.rmtree(cfg.isolated_dir)` — **unconditional discard**.
- **The defect**: steps 7–9 run **unconditionally**, with NO check on `result.returncode` / `result.succeeded`
  / `result.reason`. `LaunchResult.reason ∈ {exited, session_timeout, hung, stop_requested}` and
  `.succeeded == (returncode == 0)` are computed and logged but never gate the harvest+discard.
- `cfg.isolated_dir` defaults to an anonymous `tempfile.mkdtemp(prefix="playground-build-")`; `session_uuid`
  defaults to a fresh `uuid4()`. **No durable run handle** ties a later session to an in-progress run; the
  copy path is ephemeral and, after rmtree, gone.

### The launch outcome contract (already rich, currently unused)
- `scripts/playground/launch_adapter.py::LaunchResult{returncode, stdout, reason, succeeded}`.
- `run_with_hung_detection` returns `reason="exited"` on natural exit (any rc), `"session_timeout"` at the
  1h `DEFAULT_SESSION_TIMEOUT_SECS` ceiling, `"hung"` on frozen-JSONL+no-children, and kill returncodes
  `-15`/`-9`. A usage-limit hit surfaces as `reason="exited"` with a **non-zero rc** and a stdout envelope
  whose text carries the limit marker (`hit your ... limit`).

### The LOCAL derivation chain — ALREADY resumable (the model to mirror)
- `feat_backfill_orchestration` (REQ-PROC-071-06): AC-01 "chain of tasks, each a fresh session running one
  bounded unit, **loop state in file-memory and a commit per unit**"; AC-05 dedicated control skills
  (`layer-derivation-start/status/resume`); AC-06 max-coverage-session-per-unit cost guard + stale-decision
  invalidation. "The termination signal lives in file-memory, so the chain resumes correctly after any cold start."
- `scripts/factory/layer_derivation/backfill_orchestration.py`: `ChainState`/`UnitEntry` are "the only
  cross-session memory, committed atomically (tmp-write + rename)"; `save_chain`/`load_chain`; `next_unit`
  yields the next directive; `complete: true` when all units done.
- `layer-derivation-resume` (SKILL.md): takes only `chain_state_path`, gets next directive, checks stale
  answers, creates the next unit task, re-dispatches via autorun. Harness-unaware — reads REQ path from
  ChainState, resolved against the run's own cwd.
- **Key**: this resumable ChainState lives INSIDE the deployed copy's tree (its own project). When build.py
  rmtrees the copy, that resumable state is destroyed.

### The OUTER orchestrator — ALREADY has the rate-limit/resume machinery
- `scripts/automation/orchestrate.py::classify_session_failure` returns `"rate_limited"` when stdout contains
  `hit your` + `limit`; `rate_limited_until: {account -> ISO reset}`; reset regex parses `resets H[:MM]am/pm (TZ)`.
- Resumes `in_progress` tasks after reset (`find_resumable_in_progress_task`); rotates accounts.
- **Shared account window (AC-12)**: the whole session tree binds ONE `~/.claude`, so a usage limit takes down
  every level at once (host wrapper + contained child + any inner orchestrator).

### Developer-added dimensions (input 01)
- **Nested orchestrators**: the derivation task may itself be dispatched by the OUTER autorun orchestrator;
  the deployed copy contains the WHOLE factory, hence its own autorun/orchestrator (an INNER orchestrator
  starts inside the copy). To pause the derivation, the OUTER orchestrator must ALSO be paused, else it
  launches the next task while we are trying to checkpoint. Two orchestrators, one account window.
- **Generalize**: the pause/resume mechanism should serve ALL long build-mode playground runs (e.g. a
  multi-task skill-under-test), not just layer-derivation.

## Existing constraints & already-implemented solutions (recorded as ledger rows)
- C1 Never git-reset the copy; harvest-before-discard; discard is rmtree (topology hazard T-B).
- C2 Harvest is snapshot-diff scoped (net-new/modified only) — REQ-PROC-068-19.
- C3 AC-10 whole-factory deploy must stay intact (copy must remain a runnable project).
- C4 AC-12 single shared `~/.claude` auth window across the whole tree.
- C5 Local chain resumability primitives already exist (ChainState, commit-per-unit, resume skill).
- C6 Outer orchestrator already detects rate limits and resumes in_progress tasks.
- C7 Depth-1 spawn topology + sequential-spawn-on-tight-tier philosophy (bound loss to one in-flight unit).
