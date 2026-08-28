# Plan: Harvest-time compaction of the persisted harness git (TASK-PROC-068-32)

**Session**: a6a7121a-4276-4d00-b537-fcd6b12d68a6 (automated, account gmail)
**Date**: 2026-07-18
**Approach**: inline (no subagents — all touched files already read in-session; delegation
net-negative per CLAUDE.md §2 economics, same call as predecessor TASK-PROC-068-31)
**Ideation**: skip — design fixed by TASK-PROC-068-28 protocol ("do NOT re-open")

## The one non-obvious derivation (from the backward-reference constraint)

A git commit hash covers its full ancestry. So "preserve referenced commit R with a stable
hash" transitively freezes **every ancestor of R**. On the playground's linear single-branch
(`main`, no merges) history this collapses the compaction policy to exactly one legal shape:

- Preserved boundary **B** = the NEWEST commit on `main` that is either (a) the prior
  persisted tip **P** (immutability — never rewrite anything already persisted, and P's
  ancestors include all prior runs' referenced commits) or (b) a commit referenced by this
  run's harvested artifacts / tasks.
- Everything from root..B stays byte-identical (forced — they are ancestors of B or B itself).
- The only squashable region is the **trailing segment (B, HEAD]** — this run's unreferenced
  tail intermediates, which nothing references and no prior run has persisted. Squash them
  into ONE commit carrying HEAD's tree with parent B.
- Unreferenced commits BETWEEN preserved points are ancestors of a preserved point → their
  hashes are frozen → correctly NOT squashable. "Squash unreferenced intermediates" therefore
  means: each run compacts its own unreferenced tail at harvest; gaps that ended up below a
  referenced commit are permanently frozen by the constraint itself.

This satisfies all three AC-20 compaction clauses simultaneously: referenced commits keep
stable hashes (they are ≤ B), unreferenced intermediates are omitted (trailing squash, the
maximal legal set), prior runs' commits are immutable (all ≤ P ≤ B).

## Changes (all inside scripts/playground/ — AC-21)

### 1. `scripts/playground/workspace.py`
- `_run_git` returns captured stdout (stripped) — needed by the new read-side git calls;
  existing callers ignore the return value (backward compatible).
- New `compact_workspace_git(workspace, bundle_path, referenced_commits: set[str]) -> int`:
  1. P := sha of `refs/heads/main` from `git bundle list-heads <bundle>` if the (pre-run,
     not-yet-re-exported) bundle exists, else None (first run).
  2. Resolve each candidate in `referenced_commits` via
     `git rev-parse --verify --quiet <c>^{commit}` — unresolvable candidates (deployed
     factory-repo refs, hash-like noise) are silently dropped; resolution against the
     workspace repo IS the filter separating harness-git refs from factory-git refs.
  3. Safety fallbacks → return 0 (skip compaction, export full history — compaction is an
     optimization; reachability is the correctness property): history has merge commits;
     P exists but does not resolve / is not on `rev-list --first-parent main`.
  4. Walk `git rev-list --first-parent main` newest-first; trailing segment = commits above
     the first member of {P} ∪ resolved-referenced (whole list when none — first run,
     nothing referenced).
  5. len(segment) < 2 → return 0 (nothing to compact; avoid a pointless hash rewrite).
  6. `git commit-tree HEAD^{tree} [-p B]` + `git update-ref refs/heads/main <new>`;
     return len(segment).

### 2. `scripts/playground/build.py`
- New `_collect_referenced_commits(workspace, harvested_relpaths) -> set[str]`: scan the
  harvested files (workspace side) plus every `requirements_tasks/**/goal.md` under the
  workspace for the two provenance shapes this factory records:
  - `… @ <hex>` (materialization `decided_by: IDEATION-NNN @ <sha>` shape, mirroring
    DECIDED_BY_RE in scripts/user_needs/check_materialization_provenance.py — hex{4,40})
  - `commit: <hex>` line (task goal.md `requirements_version.commit` pin)
  Returns raw candidate strings; resolution happens inside compact_workspace_git.
  Over-matching is fail-safe (preserves more); under-matching breaks references.
- `_gate_harvest` COMPLETE branch: after `harvest_authored`, BEFORE
  `export_workspace_git_bundle` (and before the pre-run bundle is overwritten — list-heads
  of the old bundle is how P is recovered): collect → compact → log squash count → export.

### 3. Tests
- `scripts/tests/test_playground_workspace.py` (unit):
  - trailing unreferenced commits squashed to one; HEAD tree identical; referenced commit
    hash stable; prior persisted tip and its ancestors byte-stable (rev-list prefix equal).
  - referenced commit mid-segment → commits up to it untouched, only tail squashed.
  - no-op (<2 trailing); first-run-no-bundle squash-all-to-root; unresolvable candidates
    ignored; merge history → skip (returns 0, history intact).
- `scripts/tests/test_playground_build.py` (integration): 2 consecutive complete
  `run_build_mode` runs where run 2's child records a `@ <sha>` reference in a harvested
  artifact and makes extra unreferenced commits → re-exported bundle still reaches run 1's
  tip AND the referenced commit (stable hashes), while the unreferenced tail is squashed
  (commit count check); prior-run rev-list prefix unchanged (immutability).

### 4. Gates & wrap-up
- Route all edits via `claude-write-script`; `bash scripts/quality/check_python_gates.sh`
  (all 7 must PASS). Then doc-update-guidelines check, task-complete (owns the commit).

## Out of scope guards
- `run_skeleton.py` untouched (test mode carries no persisted history).
- No global squash-and-rewrite anywhere (rejected by design).
- Nothing outside scripts/playground/ + scripts/tests/ (AC-21).
