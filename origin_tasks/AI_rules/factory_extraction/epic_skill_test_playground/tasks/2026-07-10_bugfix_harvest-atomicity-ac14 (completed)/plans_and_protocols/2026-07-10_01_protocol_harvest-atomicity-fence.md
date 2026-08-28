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

# Protocol — TASK-PROC-068-24: harden build-mode harvest atomicity (AC-14)

Date: 2026-07-10
Mode: code-bugfix slim (scripts/ Python; no worktree)
Governance: claude-write-script + Python gates (REQ-PROC-051)

## Bug

`build.py`'s harvest (`harvest_authored` copy loop → flip registry `complete` →
`destroy_workspace`) has no atomicity. A mid-run crash of the `build.py` process
during `harvest_authored` can leave a **partial/torn deposit** in `test_harness_app/`.
AC-14 (HIGH) guarantees no partial/incoherent deposit is ever observable/consumable.

## Design (per goal.md, decided with developer — not re-litigated)

- Recovery = the existing idempotent re-harvest the resume path already runs.
  `harvest_authored` is copy-only, so a partial deposit is always a *subset* of the
  full deposit; re-running reproduces the coherent set and overwrites any torn file
  (`shutil.copy2`). No in-script git-commit transaction.
- The load-bearing safeguard is ONE fencing invariant: nothing may consume/commit the
  `test_harness_app/` deposit while the run's registry record is `running`/`preserved`
  — only after `complete`.

## Changes

`scripts/playground/build_resume.py`
- **FENCE (scope 1):** `deposit_blocking_runs(registry_dir, target)` + predicate
  `deposit_is_safe_to_consume(...)` — return the running/preserved runs whose harvest
  target matches (realpath-normalised); safe iff none. New `fence-check` CLI subcommand
  prints the blocking runs and exits `0` (safe) / `FENCE_EXIT_FENCED = 3` (fenced). This
  is the gate the outer-session / task-complete commit flow calls before committing the
  deposit.
- **ORPHAN-COPY edge (scope 2):** `discard_orphan_copies(registry_dir)` — reclaims the
  leaked workspace of a `complete` record whose copy was never destroyed (crash between
  the gate's flip-to-complete and `destroy_workspace`). Never re-harvests. Wired into the
  `resume` CLI path before `find_resumable_run`.
- Imports `RUN_STATUS_COMPLETE`, `destroy_workspace`; module docstring `Output:` updated.

`scripts/tests/test_playground_build_resume.py`
- `test_resume_reharvest_overwrites_partial_torn_deposit` — crash-injection: a subset of
  child-authored files (one TORN) pre-present in target; resume re-harvest overwrites to
  the full coherent set. (scope 2 verify)
- `test_discard_orphan_copies_removes_leaked_complete_workspace` /
  `..._leaves_resumable_workspace` — orphan-copy edge.
- `test_deposit_fenced_while_run_preserved` / `..._safe_after_run_complete` /
  `..._ignores_run_targeting_other_harness` / `test_main_fence_check_exit_codes` — fence.
- Added `_multi_persona_authoring_deps` helper; generalised `_preserve_a_run` with an
  optional `deps_factory` (default unchanged).

## Audit result (scope 1 — "add the gate where missing")

Grepped every path committing/consuming harvested `test_harness_app/` content
(`scripts/`, `.claude/`). There is **no existing automated committer** of the deposit —
the outer commit is skill/human-driven (`task-complete` flow), not a dedicated script.
So "add the gate where missing" = provide the callable/CLI fence for that flow to invoke;
no existing script had a gate to retrofit.

## Scope 3 (DEFENSIVE CLEANUP) — deliberately SKIPPED

The goal marks the pre-harvest path-scoped `git restore`/`git clean` as *optional* and
"proportionate to rarity". Overwrite semantics already yield a coherent set for every
torn/partial file (a torn file always corresponds to a child-authored file present in the
preserved workspace, so re-harvest overwrites it whole — verified by the crash-injection
test). The git surgery adds no correctness, only tidiness, while carrying exactly the
blanket-reset hazard the goal warns against. Skipped as net-negative.

## Verification

- `pytest scripts/tests/test_playground_build_resume.py scripts/tests/test_playground_build.py` → 39 passed.
- `scripts/quality/check_python_gates.sh`: G1/G2/G4/G5/G6/G7 PASS. G3's only failures
  (`test_aggregate_read_metrics.py` ×2 + `test_check_dependency_usage.py` collection error)
  are the **pre-existing develop baseline** — confirmed identical with this task's changes
  stashed. No new failure introduced by this change.
