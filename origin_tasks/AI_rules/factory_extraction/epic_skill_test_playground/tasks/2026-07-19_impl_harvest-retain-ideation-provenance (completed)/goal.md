---
task_id: TASK-PROC-068-35
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U4-BLOCKING
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-07-19
started: 2026-07-19
effort: M
created: 2026-07-19
expected_tool_calls: 45
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11]
  sections: []
egp:
  - { ac: AC-11, archetype: F, referent: "a real build/maintain run observed to deposit the registry-classified product-definition artifacts into test_harness_app/ and to retain its own factory-runtime provenance (the ideation index and ledger backing a derived decision) as project data" }
consequence: MEDIUM
scope_description: "Conform the build-mode harvest to REQ-PROC-068 AC-11's retention clause: scoped retention of the ideation index entry + ledger + task folder backing the harvested materialization's decided_by, as test_harness_app project data, so provenance resolves after a future deploy."
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: edddd25f
  file: ../../requirements.md
---

# Goal: Retain the Harness's Ideation Provenance at Harvest (AC-11 conformance)

## Objective

Complete the **retention clause** of REQ-PROC-068 **AC-11**, which the harvest currently does not
implement. AC-11 requires that a build/maintain run, in addition to depositing the four product-definition
categories into `test_harness_app/`, also causes *"the harness [to retain] its own factory-runtime
provenance grounding its product definition (the ideation index and ledger backing a derived decision) as
project data of the standalone harness."*

Today `scripts/playground/build.py` harvest copies back only `_PRODUCT_DEFINITION_CATEGORIES`
(`user-needs, requirements, scribble, source-code`). The harvested `product_materialization.md`
(category `user-needs`) carries `decided_by: IDEATION-NNN @ <sha>`, but the **ideation index**
(`.factory/ideation/index.yaml`, category `factory-runtime`) and the **ideation ledger**
(category `task-workspace`) that back it are **not** retained. Consequence: after a future deploy of the
harness, `check_materialization_provenance.py` fails at the index-lookup / ledger-file steps
(`MISSING <id> not found in index`) even though the referenced commit is already kept reachable by the
persisted harness bundle (TASK-PROC-068-32/34). This blocks TASK-PROC-068-26 (and its dependent
TASK-PROC-068-12).

## Background

Design established across the 2026-07-19 investigation (see the pending question at
`automation/pending_feedback/TASK-PROC-068-26/question.md` and the blocker
`.../2026-07-14_impl_harness-materialization-layer-derive/plans_and_protocols/2026-07-15_05_blocker_provenance-harvest-gap.md`):

- **Deploy leak** (Blocker 1) is already fixed — TASK-PROC-068-33 excludes
  `requirements_user_needs/product_materialization/` in `deploy.py::_SUBFOLDER_EXCLUDES`.
- **Commit reachability** (the hard half of Blocker 2) is already built — TASK-PROC-068-32/34: harvest
  compaction preserves referenced provenance commits, exported to
  `test_harness_app/.playground_harness_git/harness.bundle`, restored on the next deploy via
  `restore_workspace_git` (which fetches the bundle + `symbolic-ref`s HEAD **without touching the
  worktree** — so it provides commit *reachability*, not file *presence*).
- **What is left** = this task: the provenance check ALSO reads the index entry and ledger **as files on
  disk** (`check_materialization_provenance.py` steps 2 and 3). Neither harvest (wrong categories) nor
  bundle-restore (no checkout) puts them on disk. So the harness must retain them as project files.

**Host-side git access is NOT needed** and must not be added: the provenance check is only ever invoked
by `layer-derivation-start`/`-resume` and `ux-flow-draft`, all of which run *inside a deployed copy*
(where the bundle is restored → commit reachable). `test_harness_app` is not its own git repo.

For complete requirements at task creation time:
```
git show edddd25f:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- `scripts/playground/build.py`: at harvest, after the net-new product-def harvest, perform a **scoped**
  retention: for each harvested materialization artifact, parse its `decided_by: IDEATION-NNN @ <sha>`;
  look up IDEATION-NNN in the **copy's** `.factory/ideation/index.yaml`; write that single entry into
  `test_harness_app`'s own `.factory/ideation/index.yaml` (create the file if absent; upsert the one
  entry — do NOT copy flutter_app's other ideation entries); and copy the entry's `ledger_path` file and
  its `task_path` task folder (enough for `resolve_task_folder_path` + the ledger read to succeed) into
  `test_harness_app/` at the same relpaths.
- A real deterministic end-to-end extraction test in `scripts/tests/` (see AC below).
- The `task-workspace` registry one-liner clarification in `.factory/registry/artifacts.yaml` (already
  applied in the working tree; commit it with this task).

### Out of Scope
- Wholesale inclusion of the `factory-runtime` or `task-workspace` categories into
  `_PRODUCT_DEFINITION_CATEGORIES` — AC-11 scopes retention to the backing ideation index+ledger only,
  and AC-21 requires `test_harness_app/` present as an ordinary standalone project (no factory subsystem
  runtime). Retention is a scalpel, not a category flag.
- Any host-side (flutter_app) git resolution of the harness's provenance commit.
- Editing `check_materialization_provenance.py` (it is already project-agnostic via `--index`/`--repo`).
- A live build-mode Claude child run (the e2e test constructs the copy state deterministically).

## Acceptance Criteria

- [x] AC-11 — EGP: F (a real build/maintain run observed to deposit the registry-classified
      product-definition artifacts into test_harness_app/ and to retain its own factory-runtime provenance
      — the ideation index and ledger backing a derived decision — as project data); consequence: MEDIUM
      — realized here by the harvest retaining the ideation index entry + ledger + task folder backing the
      harvested materialization's `decided_by`, as `test_harness_app` project data.
- [x] T-1: `build.py` harvest performs **scoped** ideation-provenance retention (only the referenced
      IDEATION-NNN's index entry + ledger + task folder), NOT wholesale category inclusion; a
      materialization with no resolvable `decided_by` is a harmless no-op (does not crash the run).
- [x] T-2: A **real deterministic end-to-end extraction test** in `scripts/tests/` passes: it constructs
      a completed build-mode copy state (`product_materialization.md` with `decided_by: IDEATION-NNN @ <sha>`,
      `.factory/ideation/index.yaml` entry, ledger file, task folder, a referenced `scenario.md`, and a git
      commit at `<sha>`), runs harvest + provenance retention into a fresh `test_harness_app`, persists the
      harness bundle, **redeploys into a fresh workspace via the real deploy+restore path**, and asserts
      `check_materialization_provenance.py` prints `OK` in the redeployed copy.
- [x] T-3: Python gates (`scripts/quality/check_python_gates.sh`) pass for all changed scripts with no new
      violations; `dart fix`/Flutter gates N/A (no `lib/` change). The `task-workspace` registry one-liner
      clarification is committed with this task.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-32 | completed | Harvest-time commit compaction (preserves referenced provenance commit) |
| TASK-PROC-068-34 | completed | Persisted harness git restore/persist bundle (commit reachability after redeploy) |
| TASK-PROC-068-33 | completed | Deploy exclude of product_materialization/ (Blocker 1 already fixed) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-26](../2026-07-14_impl_harness-materialization-layer-derive/goal.md) | This task unblocks it — 068-26's AC-1 provenance resolution depends on this retention |

## Notes

- **Standalone-override (AC-10)**: created as a single focused conformance task rather than routed to
  `task-derive-from-requ` holistic decomposition. REQ-PROC-068 is a mature epic whose ACs are largely
  covered by completed tasks; this completes the unimplemented retention clause of one AC (AC-11).
  Manual (non-automated) session; developer-directed.
- Investigation trail (2026-07-19): `check_materialization_provenance.py` needs index entry + ledger as
  files (steps 2/3); `restore_workspace_git` gives reachability not file presence; deploy-exclude and
  commit-carry already landed. Host-side git access is unnecessary and out of scope.
