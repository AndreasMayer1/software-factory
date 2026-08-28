# Plan — build-mode run registry + resume + dynamic poll + folded verification (TASK-PROC-068-22)

Design source (developer-approved SOL-02): `2026-07-09_006_synthesis_v2.md` §SP-2/§SP-4.
T1 (TASK-PROC-068-21) landed the wrapper (`build.py`: out-of-project git copy, completion-gated
harvest, injected predicate, run-registry **write** side). T2 adds the **read/re-attach** side, the
resume control skill, the dynamic-poll helper, and the folded real-artifact AC-13..AC-17 proof.

## The seam (established by T1, verified this session)
`run_build_mode` = `_prepare_workspace` (create_workspace → deploy_candidate → init_workspace_git →
sync_product_definition seed → snapshot_product_definition baseline) → `check_budget` →
`write_run_registry_running` → launch (`run_with_hung_detection`) → `_gate_harvest`
(verified-complete → `harvest_authored` + registry→complete + `destroy_workspace`; else
registry→preserved, workspace kept, harvest skipped).

Resume must reuse the **preserved workspace** + the **persisted pre-child baseline** and run ONLY
the launch→gate tail — SKIP deploy/seed/snapshot (AC-15).

## Deliverable 1 — enrich the registry write (`scripts/playground/build.py`)
The current record has: session_uuid, workspace_path, target/host_project_dir, model, status,
started_at. Resume also needs: **prompt, jsonl_dir, registry_path, workspace_root, max_budget_usd**,
and a **baseline snapshot ref**.
- Change `write_run_registry_running(cfg, workspace)` → `write_run_registry_running(cfg, workspace,
  *, jsonl_dir, baseline)`. Write the extra fields; persist `baseline` to a sidecar
  `<uuid>.baseline.json` in the registry dir and store `baseline_snapshot_ref` (its path) in the
  record. (Sidecar keeps the main record readable; matches goal's "baseline snapshot ref" wording.)
- In `run_build_mode`: derive `jsonl_dir` BEFORE the registry write (move the existing
  `cfg.jsonl_dir or _derive_jsonl_dir(workspace)` line up), pass jsonl_dir + pre_child_state in.
- **Refactor for reuse**: extract the launch→gate tail of `run_build_mode` into a PUBLIC
  `launch_and_gate(cfg, *, workspace, globs, baseline, registry_path, jsonl_dir, ledger,
  launch_deps, probe_fn, completion_predicate) -> dict` (the manifest). `run_build_mode` keeps
  `_prepare_workspace` + `check_budget` + `write_run_registry_running`, then calls
  `launch_and_gate`. This is the single seam both fresh-run and resume use (no dup).
- Export registry constants as needed (`_RUN_REGISTRY_DIRNAME`, statuses) — either make public
  (`RUN_REGISTRY_DIRNAME`, `RUN_STATUS_*`) or import via module in build_resume. Prefer public
  aliases to avoid cross-module private import.

## Deliverable 2 — resume/read side (`scripts/playground/build_resume.py`, NEW, tier C CLI + tier-B fns)
Mirrors how `layer-derivation-resume` calls `backfill_orchestration.py`. Functions:
- `read_run_record(path) -> dict`
- `list_runs(registry_dir) -> list[dict]` — glob `*.json`, EXCLUDE `*.baseline.json` sidecars.
- `find_resumable_run(registry_dir) -> dict | None` — the run to re-attach: status in
  {running, preserved} AND `workspace_path` still exists on disk. (running = killed before gate;
  preserved = gate ran, not-complete. Both resumable. complete = done.)
- `load_baseline(record) -> dict[str,str]` — read `baseline_snapshot_ref` sidecar.
- `resume_run(record, *, launch_deps=None, probe_fn=None, completion_predicate=None) -> dict` —
  reconstruct `BuildModeConfig` from the record; load globs via `load_product_definition_globs`
  (record's registry_path); load baseline; call `build.launch_and_gate(...)` with the RECORDED
  workspace_path/jsonl_dir. **Never** calls `_prepare_workspace` (AC-15: no re-deploy/seed/snapshot).
- CLI: `list [--registry-dir D]`, `resume [--registry-dir D]` (default `<worktree_root>/.playground_runs`).
  `resume` finds the resumable run and re-attaches; prints the manifest JSON.
Imports from build.py: `BuildModeConfig`, `launch_and_gate`, `load_product_definition_globs`,
`RUN_REGISTRY_DIRNAME`, `RUN_STATUS_*`.

## Deliverable 3 — dynamic-poll helper (`scripts/playground/completion_poll.py`, NEW, tier B)
SP-4/IDEA-35, U6 (sane floor/ceiling — "not a fixed 15 min").
- `compute_poll_interval(remaining_units, *, floor_secs=60, ceiling_secs=900, secs_per_unit=60)
  -> int` = `max(floor, min(ceiling, remaining_units * secs_per_unit))`. remaining_units<=0 → floor.
- `poll_until_complete(is_complete, remaining_units_fn, *, sleep=time.sleep, floor_secs=60,
  ceiling_secs=900, secs_per_unit=60, max_polls=None) -> bool` — loop: if is_complete() → True;
  else sleep(compute_poll_interval(remaining_units_fn())); stop at max_polls → False. Injectable
  sleep for tests. This is the outer-session self-poll primitive (SOL-02 D5(a)).

## Deliverable 4 — `playground-build-resume` control skill (via `claude-create-skill`)
Mirror `layer-derivation-resume`. tools: [Bash, Read]. Steps: (1) resolve registry dir; (2)
`python3 scripts/playground/build_resume.py list` → if none resumable, say so & stop; (3)
`build_resume.py resume` re-attaches (no human path-threading); (4) surface manifest summary. Note
the usage-limit case needs no action (orchestrator freeze/resume) and `stop_requested` is the
documented pause extension point.

## Deliverable 5 — tests (all via `claude-write-script`; G3 pytest)
- `test_playground_build.py` (extend): registry record now carries jsonl_dir/prompt/registry_path/
  workspace_root/max_budget_usd + baseline_snapshot_ref; sidecar written & re-readable.
- `test_playground_build_resume.py` (NEW): `find_resumable_run` picks running/preserved with an
  existing workspace, skips complete/missing; `resume_run` reuses baseline + workspace and runs the
  gate WITHOUT deploy/seed/snapshot — assert create_workspace/deploy_candidate are NOT called
  (monkeypatch to raise) → AC-15; a resumed run whose predicate returns True harvests the
  child-authored net-new artifact (real tmp dirs + `_authoring_deps` style).
- `test_completion_poll.py` (NEW): interval scales with units and clamps to floor/ceiling; poll
  loop terminates on is_complete and honours max_polls (AC-16 dynamic poll, U6).

## Deliverable 6 — folded AC-13..AC-17 real-artifact verification
Methodology = the developer-accepted AC-11 functional-proof precedent
(`2026-07-02_.../plans_and_protocols/2026-07-03_02_evidence_ac11-functional-proof.md`): exercise the
REAL building blocks against real artifacts with a **cheap deterministic contained child**, NOT a
multi-hour `claude -p` derivation (expensive + could hit the shared usage-limit and freeze this
session). Write `plans_and_protocols/2026-07-09_03_evidence_ac13-17-folded-proof.md`:
- **AC-13**: real create_workspace+deploy+git-init at the real worktree_root → copy exists there
  (not /tmp), `.git` present.
- **AC-14**: interrupted run (predicate False / non-clean) preserves + harvests nothing; complete
  run (predicate True + clean exit) harvests the net-new artifact + discards. Real-artifact oracle:
  a real deterministic contained child authors a real net-new product-def file.
- **AC-15**: a real cold process (`build_resume.py resume`) discovers the preserved run from the
  registry and resumes reusing the preserved workspace + persisted baseline, WITHOUT re-running
  deploy/seed/snapshot (assert the workspace mtime/inode is the preserved one; deploy not re-run).
- **AC-16**: `rate_limit_sleep` (orchestrate.py:213) recomputes remaining from the absolute reset
  time each tick and is called by BOTH inner and outer orchestrators — shared-window freeze/resume
  with NO orchestrator change (code-inspection proof, verified this session). The dynamic-poll
  helper supplies the non-fixed interval. The full real-limit derivation-resumability proof
  (REQ-PROC-071-06 AC-08) is explicitly T3, per goal Out-of-Scope.
- **AC-17**: injected predicate over the copy path (re-confirm T1's test).

## Execution structure
- Deliverables 1-3 + tests (5): ONE background `implementation-engineer` agent (write-heavy,
  iterative, >5min → background + 4:30 heartbeat; pro tier → single sequential agent). It reads this
  plan + goal + the named files, does the closed loop, runs `scripts/quality/check_python_gates.sh`
  to green, persists a protocol, returns a short summary.
- Deliverable 4 (skill): inline via `claude-create-skill` (syncs INDEX/factory_flows — shared write,
  keep in main).
- Deliverable 6 (real proof): inline Bash after the agent lands (deterministic, cheap).
- Wrap: claude-log, doc-update-guidelines, task-complete.

## Constants / defaults
poll floor 60s, ceiling 900s (== the old fixed 15 min, now the ceiling not the constant),
secs_per_unit 60. Registry dir default `<worktree_root>/.playground_runs`.
