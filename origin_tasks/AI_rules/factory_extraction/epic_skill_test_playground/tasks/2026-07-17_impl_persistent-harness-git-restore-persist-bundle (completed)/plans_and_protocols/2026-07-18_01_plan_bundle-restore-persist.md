# Plan: Persistent harness git — restore-on-deploy + persist-on-harvest (TASK-PROC-068-31)

**Date**: 2026-07-18
**Mode**: inline (files already loaded in session; delegation would be net-negative)
**Fixed design**: `../../2026-07-17_explore_persistent-harness-git (completed)/plans_and_protocols/2026-07-17_01_protocol_persistent-harness-git-design.md` — not re-opened.

## Approach

Maintenance-mode (`build`/`maintain`) runs replace the fresh-`git init` workspace baseline with a
**git bundle round-trip**. Single-branch convention: all maintenance history lives on `main`.

### Mechanism (verified empirically with git 2.43 in a temp dir, this session)

- **Restore-on-deploy** (bundle exists at the persisted location):
  `git init -q -b playground_restore_tmp` (a temp unborn branch we control, never `main`, so the
  fetch below can never hit "refusing to fetch into current branch") →
  `git fetch -q <bundle> +refs/heads/main:refs/heads/main` →
  `git symbolic-ref HEAD refs/heads/main` (doesn't touch worktree/index) →
  `git add -A` → commit `playground baseline`.
  Result: the baseline commit is a **child of the persisted tip**; every earlier referenced commit
  stays reachable with a stable hash (verified: parent == prior run tip, `git cat-file -e` on the
  old hash succeeds).
- **Fresh maintenance init** (no bundle yet — first run): `init_workspace_git` extended with an
  optional `initial_branch` param; maintenance passes `main`, test mode passes nothing (unchanged).
- **Persist-on-harvest** (COMPLETE outcome only): normalize branch to `main`
  (`git branch -M main` if the current branch differs — handles legacy preserved workspaces on a
  resume), `git bundle create <tmp> refs/heads/main`, then `os.replace` → atomic; a failed export
  never corrupts the existing bundle.

### Storage location + naming (AC-20 "persisted with the harness in the container project")

`<harness_app_dir>/.playground_harness_git/harness.bundle` — inside the persistent
`test_harness_app/` tree (in the container project, never an OS temp dir).
`create_workspace`'s copytree **ignores** `.playground_harness_git/` when seeding: otherwise the
bundle file itself would be committed into workspace history and re-exported into the next bundle —
unbounded self-referential growth. Ignoring it in the seed also keeps test-mode copies bundle-free
(AC-20: a test-mode run carries no persisted history).

## Edits

1. `scripts/playground/workspace.py`
   - constants: `MAINTENANCE_BRANCH`, `HARNESS_GIT_DIRNAME`, `HARNESS_BUNDLE_FILENAME`
   - `harness_git_bundle_path(harness_app_dir) -> str`
   - `init_workspace_git(workspace, initial_branch=None)` (default = exact current behavior)
   - `restore_workspace_git(workspace, bundle_path)`
   - `export_workspace_git_bundle(workspace, bundle_path)`
   - `create_workspace`: `ignore=shutil.ignore_patterns(HARNESS_GIT_DIRNAME)`
2. `scripts/playground/build.py`
   - `_prepare_workspace` Step 3: bundle exists → `restore_workspace_git`; else
     `init_workspace_git(workspace, initial_branch=MAINTENANCE_BRANCH)`
   - `_gate_harvest` COMPLETE branch: after `harvest_authored`, **before** `destroy_workspace`:
     `export_workspace_git_bundle(workspace, harness_git_bundle_path(cfg.target_project_dir))`
   - `build_resume.resume_run` needs **no edit** — it reuses `launch_and_gate` → `_gate_harvest`,
     so persist-on-harvest covers resume automatically; restore is deploy-time only and resume
     never re-deploys.
3. Tests: `scripts/tests/test_playground_workspace.py` (restore/export round-trip incl. stable-hash
   reachability across a 2-run sequence; copytree-ignore; atomic replace),
   `scripts/tests/test_playground_build.py` (COMPLETE exports bundle; non-COMPLETE does not;
   restore-vs-fresh-init dispatch in `_prepare_workspace`).

## Scope guards

- **Test mode untouched**: `run_skeleton.py` not edited; `init_workspace_git()` default identical.
- **Compaction out of scope** (AC-20's "omits unreferenced intermediate commits" half): sibling
  successor task. This task exports full history — preserve-everything is a correct (if
  unbounded-growth) interim per the fixed design's immutability constraint; no history rewrite here.
- **AC-21 encapsulation**: every change lives in `scripts/playground/`; no other factory mechanism
  touched.

## Phases

1. Edit workspace.py + build.py + tests via `claude-write-script` → Python gates (G1–G5) green.
2. AC-20 EGP-F grounding at unit level: the 2-run round-trip test asserts an earlier run's commit
   stays reachable with a stable hash after restore. (Full end-to-end ≥2-run maintenance sequence is
   folded into the sibling `verify-persistent-harness-git` task per goal.md.)
3. claude-log → task-complete (commits).
