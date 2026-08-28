---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - claude-write-script
  - doc-update-guidelines
  - task-complete
  - claude-commit
---

# Protocol: Persistent harness git — restore/persist bundle (TASK-PROC-068-31)

**Session**: 202535c9-d3d7-47af-a5f0-d9e787274937 (automated, account gmail2)
**Date**: 2026-07-18
**Mode**: inline (no subagents — files already in session context, delegation net-negative)

## What was done

Implemented the fixed design (TASK-PROC-068-28 protocol) — maintenance-mode persistent harness
git via a git-bundle round-trip. All changes inside `scripts/playground/` (AC-21).

### `scripts/playground/workspace.py`

- New constants: `HARNESS_GIT_DIRNAME` (`.playground_harness_git`), `HARNESS_BUNDLE_FILENAME`
  (`harness.bundle`), `MAINTENANCE_BRANCH` (`main`), `_RESTORE_TMP_BRANCH`.
- `harness_git_bundle_path(harness_app_dir)` — AC-20 storage convention:
  `<harness_app_dir>/.playground_harness_git/harness.bundle` (with the harness in the container
  project, never an OS temp dir).
- `restore_workspace_git(workspace, bundle_path)` — restore-on-deploy: `git init -q -b
  playground_restore_tmp` (temp unborn branch — git refuses fetching into the current branch, and
  this also shields against `init.defaultBranch == main`), fetch
  `+refs/heads/main:refs/heads/main` from the bundle, `git symbolic-ref HEAD` (worktree untouched),
  then baseline commit on top → the baseline is a CHILD of the persisted tip; earlier referenced
  commits stay reachable with stable hashes. Fails loud (WorkspaceError) on a missing/corrupt
  bundle — never falls back to fresh init (would orphan persisted references).
- `export_workspace_git_bundle(workspace, bundle_path)` — persist-on-harvest: `git branch -M main`
  (normalizes legacy preserved workspaces), `git bundle create` to `<dest>.tmp`, `os.replace`
  (atomic — a failed export never corrupts the only copy of prior runs' history).
- `init_workspace_git(workspace, initial_branch=None)` — optional `-b` for the maintenance
  first-run; default None keeps test mode byte-identical (AC-07 untouched).
- `create_workspace` — copytree now ignores `.playground_harness_git`: a copied-in bundle would be
  committed into workspace history and re-exported into every later bundle (unbounded
  self-referential growth), and test-mode copies must carry no persisted history.
- Extracted `_commit_baseline()` (shared by init + restore).

### `scripts/playground/build.py`

- `_prepare_workspace` Step 3: bundle exists → `restore_workspace_git`; else
  `init_workspace_git(..., initial_branch=MAINTENANCE_BRANCH)`.
- `_gate_harvest` COMPLETE branch: after `harvest_authored`, before registry flip + destroy →
  `export_workspace_git_bundle`. COMPLETE-only by placement (every other outcome returns earlier —
  no partial history is ever persisted). Covers BOTH fresh runs and cold resumes
  (`build_resume.resume_run` reuses `launch_and_gate` → `_gate_harvest`; build_resume.py needed no
  edit).

### Not touched (scope guards honored)

- `scripts/playground/run_skeleton.py` (test mode) — calls `init_workspace_git(workspace)`
  unchanged.
- Harvest compaction (preserve-referenced / squash-unreferenced) — successor task; this task
  exports full history, appends only, never rewrites (backward-reference constraint).
- No mechanism outside `scripts/playground/` (AC-21 encapsulation; verified by caller grep).

## Tests

8 new tests; all 69 tests in the two touched modules pass.

- `scripts/tests/test_playground_workspace.py`: bundle-path convention; seed-copy exclusion of the
  bundle dir; `-b main` fresh init; **2-run restore/export round-trip asserting run 1's commit
  stays reachable with a stable hash and run 2's baseline is its direct child** (AC-20 core
  property, unit level); legacy-branch normalization on export; atomic re-export (no `.tmp`
  residue, verifies); fail-loud on missing bundle.
- `scripts/tests/test_playground_build.py`: **two consecutive complete `run_build_mode` runs — run
  2's re-exported bundle still reaches run 1's tip (stable hash, `merge-base` ancestor check =
  append-not-rewrite)**; non-COMPLETE run never writes a bundle.

Mechanism was also verified empirically with raw git 2.43 in a temp dir before implementation
(see plan file).

## Gates

`scripts/quality/check_python_gates.sh`: **all 7 PASS** (G1 lint, G2 type, G3 tests, G4
no-handrolled-YAML, G5 print-discipline, G6 complexity, G7 canonical-lib).

CLAUDE.md §11: no update — Rule 3 (skills-only/subsystem-internal library functions; no ad-hoc
analytical use outside the playground modules).

## Learnings

- `git bundle verify` must run with cwd inside a git repository (it checks prerequisites against
  one) — test helper call sites fixed accordingly.
- `git fetch` refuses to update the currently checked-out branch ref; restore therefore inits on a
  controlled temp unborn branch and moves HEAD via `symbolic-ref` afterwards.

## Outcome

AC-20 (restore-on-deploy + persist-on-harvest halves; compaction excluded per scope) and AC-21
(encapsulation) implemented. End-to-end ≥2-run verification remains with the sibling
`verify-persistent-harness-git` task per goal.md.
