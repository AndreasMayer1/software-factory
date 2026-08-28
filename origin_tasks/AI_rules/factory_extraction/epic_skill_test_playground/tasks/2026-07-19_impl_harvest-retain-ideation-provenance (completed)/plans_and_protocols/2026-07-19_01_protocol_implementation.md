---
task_id: TASK-PROC-068-35
agent_id: ae7b8361385f6dec1
role: implementation-engineer
date: 2026-07-19
skills_used:
  - task-create
  - task-complete
  - claude-commit
---

# Protocol: AC-11 retention clause implementation

## Read before starting

- `goal.md` (full)
- `automation/pending_feedback/TASK-PROC-068-26/question.md` (context only, not answered here)
- `scripts/playground/build.py` (harvest pipeline, `_gate_harvest`)
- `scripts/user_needs/check_materialization_provenance.py` (the downstream gate this retention feeds)
- `scripts/playground/workspace.py` (`create_workspace`, `restore_workspace_git`,
  `export_workspace_git_bundle`, `compact_workspace_git`, `harness_git_bundle_path`)
- `scripts/util/task_folder_resolver.py` (`resolve_task_folder_path`)
- `scripts/ideation/index_session.py` (`load_index`/`save_index` — reused, not reimplemented)
- `scripts/tests/test_playground_build.py`, `test_playground_workspace.py`,
  `test_check_materialization_provenance.py` (patterns for the new e2e test)
- `doc/python/README.md`, `anti_patterns.md`, `architecture.md` (per claude-write-script skill step 0c)

## What changed

### `scripts/playground/build.py`

Added imports: `YAMLError`, `scripts.ideation.index_session.{load_index,save_index}`,
`scripts.user_needs.check_materialization_provenance.DECIDED_BY_RE`,
`scripts.util.task_folder_resolver.resolve_task_folder_path`.

New section "AC-11 retention clause — scoped ideation-provenance retention", inserted right
after `harvest_authored` (before the AC-20 compaction section):

- `_MATERIALIZATION_RELPATH` / `_IDEATION_INDEX_RELPATH` — the two fixed relpaths this
  retention step operates on.
- `_load_materialization_frontmatter(artifact_path)` — private, duplicated from
  `check_materialization_provenance.py`'s own private `_load_frontmatter` (identical shape).
  Deliberate duplication, not a cross-module private import — `check_materialization_provenance.py`
  is explicitly out of scope for this task, and the codebase already has this convention
  (`_derive_jsonl_dir`'s own documented duplication in the same file).
- `_upsert_ideation_index_entry(index_path, entry)` — insert-or-replace the SINGLE entry with
  this id via `index_session.load_index`/`save_index` (reused, not reimplemented — G4 compliance
  through reuse of the module that already owns index.yaml's read/write convention).
- `_copy_ideation_provenance_paths(workspace, target_project_dir, entry)` — resolves BOTH
  `task_path` and `ledger_path` via `resolve_task_folder_path` (never a literal join — the
  anti_patterns.md "status-suffix rename" lesson), copies the whole task folder (which is what
  makes `resolve_task_folder_path` succeed for `task_path` on the far side too) plus the ledger
  file, at the RESOLVED relpath (`.relative_to(workspace)`), not the possibly-stale stored one.
- `retain_ideation_provenance(workspace, target_project_dir, harvested_relpaths)` — the public
  orchestrator: gated on the materialization relpath being present in `harvested_relpaths` (T-1
  scoping — only inspects an artifact this run actually harvested); parses `decided_by`; looks up
  the id in the WORKSPACE's own index (never test_harness_app's — the workspace is the source of
  truth for a build run in progress); no-ops (returns `None`, never raises) on any unparsable/
  missing step; otherwise upserts the single entry and copies its files, returns the retained id.

Wired into `_gate_harvest`: `retain_ideation_provenance(gate.workspace, cfg.target_project_dir,
harvested)` called immediately after `harvest_authored(...)`, before the AC-20
compaction/export block — so it inspects exactly the artifacts that made it out this run.

### `scripts/tests/test_playground_provenance_retention.py` (new)

4 tests, all against REAL functions (no mocking of the functions under test):

1. `test_harvest_and_redeploy_resolves_materialization_provenance_ok` — the full AC T-2
   sequence: build a deterministic "completed child copy" (scenario.md, task folder with
   goal.md, ledger.yaml referencing the scenario, `.factory/ideation/index.yaml` entry
   `IDEATION-900`, git-init + commit → capture sha, THEN write
   `product_materialization.md` with `decided_by: IDEATION-900 @ <sha>`) → run
   `harvest_authored` (empty baseline) + `retain_ideation_provenance` into a fresh
   `test_harness_app` → assert all 5 retained/harvested artifacts exist → persist via
   `compact_workspace_git` + `export_workspace_git_bundle` → REDEPLOY via
   `create_workspace` + `restore_workspace_git` into a fresh `workspace2` → assert
   `check_materialization_provenance.check()` returns `(True, "OK IDEATION-900 ...")`.
2. `test_retain_ideation_provenance_is_harmless_noop_without_decided_by` — T-1: no
   `decided_by` field → `None`, no crash, nothing written to target's index.
3. `test_retain_ideation_provenance_skips_when_materialization_not_harvested` — T-1 gating:
   materialization present in the copy but absent from `harvested_relpaths` (byte-identical
   carryover) → no-op.
4. `test_retain_ideation_provenance_upserts_single_entry_without_leaking_others` — AC-21:
   target index gains ONLY the referenced entry; a pre-existing unrelated entry in the
   WORKSPACE's own index is never copied; a pre-existing entry already in the TARGET's index
   survives untouched.

## Retention design as built (matches goal.md's decided design)

- Scalpel, not a category flag: `_PRODUCT_DEFINITION_CATEGORIES` is UNCHANGED (still
  `{user-needs, requirements, scribble, source-code}`) — `factory-runtime`/`task-workspace`
  were NOT added, confirmed by re-reading the constant post-edit.
- Single entry upsert, never a wholesale index copy — confirmed by test 4 above.
- Copies task folder (whole) + ledger file, at resolved (not literal-stored) relpaths.
- Never raises on absent/malformed provenance (T-1) — every failure branch returns `None`
  and logs at INFO, no exception propagates.

## Gate results

`scripts/quality/check_python_gates.sh` — ALL PASS (G1 lint, G2 type/mypy, G3 tests — 3313
passed/17 skipped/6 xfailed including the 4 new tests, G4 no-hand-rolled-YAML, G5 print
discipline, G6 complexity, G7 canonical-library). No new violations introduced.

Also ran, before the full gate suite, in isolation:
- `scripts/tests/test_playground_provenance_retention.py` — 4/4 passed.
- `scripts/tests/test_playground_build.py` + `test_playground_workspace.py` +
  `test_check_materialization_provenance.py` — 91/91 passed (no regression).

## E2E test result

PASSES — `test_harvest_and_redeploy_resolves_materialization_provenance_ok` drives the exact
AC-11/AC T-2 end-to-end path (harvest → retain → persist bundle → real redeploy via
`create_workspace`+`restore_workspace_git` → `check_materialization_provenance.check()`) and
asserts `ok is True` with the message starting `OK IDEATION-900`.

## CLAUDE.md Section 11

Not updated — `retain_ideation_provenance` is an internal harvest step inside the existing
`build.py`, not a standalone ad-hoc analytical tool a session would reach for via grep/find
(Rule 3/5 exclusion, claude-write-script skill).

## Files touched

- `scripts/playground/build.py` (modified, via claude-write-script skill)
- `scripts/tests/test_playground_provenance_retention.py` (new, via claude-write-script skill)
- `.factory/registry/artifacts.yaml` (pre-existing working-tree change per goal.md note — left
  untouched, commits with this task)

## Blockers

None. No genuine blocker encountered; all gates green on first full run after the initial
implementation pass.
