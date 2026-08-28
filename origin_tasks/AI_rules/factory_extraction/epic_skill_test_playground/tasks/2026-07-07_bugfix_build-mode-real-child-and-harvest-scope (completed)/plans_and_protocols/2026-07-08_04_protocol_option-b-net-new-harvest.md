---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - code-bugfix
  - claude-write-script
  - task-complete-bugfix
  - task-complete
  - claude-commit
---

# Protocol 04 — Option B (net-new harvest) + AC-3/AC-4 empirical proofs

Task: TASK-PROC-068-19 · Date: 2026-07-08 · Mode: code-bugfix (slim/scripts)
Session: ed35d6af (gmail2) · Developer decision: Option B (checkpoint 03)

## Decision applied

Developer answered the Protocol-02 escalation with **Option B**: scope the
HARVEST to net-new files (keeps deploy whole → AC-10-safe), plus additionally
exclude `_scribble_components/` (flutter-app product content) from deploy — but
do NOT exhaustively enumerate deploy excludes before the REQ-PROC-066 factory
extraction.

## Code changes (via claude-write-script)

### build.py — net-new harvest (Option B)
- New helpers: `_iter_product_definition_files` (expands dir-glob matches to
  files so the harvest diffs at file granularity), `_hash_file` (SHA-256 over
  **bytes** — newline-exact, per anti_patterns "Text-mode copy"),
  `snapshot_product_definition` (rel→hash map), `harvest_authored` (copies a
  file iff its relpath is absent from the baseline OR its hash differs).
- `run_build_mode`: Step 2b snapshots the product-def state AFTER deploy+seed
  but BEFORE the child; Step 8 now calls `harvest_authored(..., pre_child_state)`
  instead of the blanket `sync_product_definition`. So the harvest copies back
  ONLY what the child newly authored or modified — never deploy-brought
  machinery or untouched seed.
- Why harvest-scoping, not wider deploy-excludes: several residual files
  (`_meta/id_registry.md`, `_scribble_components/*/metadata.yaml`) are
  harness-RUNTIME inputs read by skills that run in the harness; dropping them
  from deploy would risk AC-10. Scoping the harvest keeps the copy whole yet
  stops ALL deploy/seed residue from leaking — generalizes beyond the process/
  corpus.

### deploy.py — exclude `_scribble_components/`
- Added `requirements_tasks/_scribble_components` to `_SUBFOLDER_EXCLUDES` (this
  flutter app's own wireframe components — app-specific product content, leak-
  containment, same class as personas/user_flows). Comment records the
  developer decision and that Option B already covers harvest correctness, so an
  exhaustive app/script-generated deploy-exclude enumeration is deferred to the
  factory extraction.

### Tests (AC-5) — 43/43 pass
- build: `test_snapshot_captures_hash_of_matching_files`,
  `test_harvest_authored_skips_unchanged_baseline_files` (deploy-brought/seed
  NOT harvested), `test_harvest_authored_copies_net_new_child_file`,
  `test_harvest_authored_copies_modified_baseline_file`; updated
  `test_run_build_mode_deploys_seeds_harvests_and_discards` to assert
  `harvested_paths == []` for a no-op mocked child (net-new semantics).
- deploy: `test_deploy_excludes_scribble_components`.

### Gates
`scripts/quality/check_python_gates.sh`: G1 lint · G2 type · G4 · G5 · G6 · G7
= PASS. G3 tests = pre-existing baseline red only
(`test_aggregate_read_metrics.py` ×2 + `test_check_dependency_usage.py`
collection error — confirmed identical on clean develop via git stash; my
playground modules 43/43). No new finding introduced.

## Empirical proofs (real authenticating `claude -p` children)

### AC-4 — combined AC-11 ∧ AC-12, now LITERALLY "only that artifact" ✓
Real child (direct persona write) through `run_build_mode()`, fresh empty
target: build.py rc=0, child rc=0, cost **$0.20** (auth works — real-HOME bind;
the old scrub_env bug returns $0 "Not logged in"). Result:
- `harvested_paths` = **exactly 1 file** — the child-authored persona.
- target tree = **exactly 1 file** (the persona). ZERO deploy-brought machinery
  (the ~13-file residual from Protocol 02 is gone), ZERO process files.
- Isolated copy discarded. → AC-4 fully proven under the literal reading.

### AC-3 — AC-10 guard: real factory skill end-to-end, no process read ✓
Real child ran the **`ux-write-persona`** skill (goal-named) in the process-free
+ scribble-free deployed copy: rc=0, cost $0.63. Transcript shows it read the
deployed README authoring guides + `.claude/schemas/role_tags.yaml`, generated
the ID, authored persona PERSONA-001 (Jamie / HarnessProofUser), validated it,
and stopped at the approval-presentation gate (as instructed) — a genuine
end-to-end skill authoring run.
- **No runtime read of any `requirements_tasks/process/**/requirements.md`.** The
  only `requirements_tasks/process` string in the whole transcript is a
  *provenance comment* inside the deployed `role_tags.yaml` schema — a path
  mention, not a file access. → no AC-10 tension, no escalation.
- Net-new harvest deposited ONLY the authored persona (1 file) — confirms
  Option B again on a real skill run.

## AC status — all met
- AC-1 auth ✓ · AC-2 process/ excluded ✓ · AC-3 skill end-to-end, no process
  read ✓ · AC-4 only-that-artifact ✓ · AC-5 tests+gates ✓ · AC-6 no debug
  artifacts added (permanent fixes only; no `[DIAG-*]`/`// TEMPORARY:` probes).

## Cleanup
All /tmp proof dirs (target/isolated) and child JSONLs removed.
`test_harness_app/` verified clean (proofs used /tmp targets, never the real
harness tree).
