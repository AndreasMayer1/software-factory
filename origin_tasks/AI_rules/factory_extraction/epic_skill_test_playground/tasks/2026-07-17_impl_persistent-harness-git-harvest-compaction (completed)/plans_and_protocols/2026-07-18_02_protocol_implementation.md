---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - task-resolve
  - claude-write-script
  - verify-quality
  - doc-update-guidelines
  - task-complete
  - claude-commit
---

# Protocol: Harvest-time compaction of the persisted harness git (TASK-PROC-068-32)

**Session**: a6a7121a-4276-4d00-b537-fcd6b12d68a6 (automated, account gmail)
**Date**: 2026-07-18
**Mode**: inline (no subagents — all touched files already in session context)

## What was done

Implemented the compaction half of AC-20 on top of TASK-PROC-068-31's bundle round-trip.
All changes inside `scripts/playground/` + its tests (AC-21 encapsulation).

### The constraint-forced shape (see plan file for the full derivation)

A git commit hash covers its full ancestry, so preserving a referenced commit's hash freezes
all its ancestors. On the linear maintenance history the ONLY legally squashable region is
the trailing segment above the newest preserved point (prior persisted tip P from the pre-run
bundle, or the newest resolved referenced commit). Each run therefore compacts exactly its own
unreferenced tail at harvest; everything at or below a preserved point — including every
prior-run persisted commit — is untouched by construction. Unreferenced gaps below a referenced
commit are frozen by the backward-reference constraint itself and stay uncompacted (correct,
not a limitation).

### `scripts/playground/workspace.py`

- `_run_git` now returns stripped stdout (read-side git calls need it; existing callers
  ignored the return).
- `compact_workspace_git(workspace, bundle_path, referenced_commits) -> int` — normalizes the
  branch (same as export), computes P via `git bundle list-heads` on the PRE-RUN bundle,
  resolves raw candidates via `git rev-parse --verify <c>^{commit}` (unresolvable = foreign/
  noise → dropped; resolution against the workspace repo IS the harness-vs-factory-ref
  filter), finds the unreferenced tail, squashes it into one `commit-tree` commit carrying
  the tip's tree (worktree/harvest content byte-identical), moves the ref with an
  old-value-guarded `update-ref`. Returns the number of commits squashed.
- Safe-no-op degradations (return 0, full history exported): merge commits present, persisted
  tip off the first-parent line, AMBIGUOUS reference abbreviation (the one resolution failure
  that could hide a real reference), tail < 2 commits. Mechanical git failures still raise
  WorkspaceError; a bundle that exists but lacks the maintenance head raises (restore fetched
  exactly that ref, so the state is impossible for a legitimately restored run).
- Helpers: `_persisted_bundle_tip`, `_resolve_workspace_commits`, `_unreferenced_tail`,
  `_squash_tail_into_one` (keeps everything within G6 complexity limits).

### `scripts/playground/build.py`

- `_PROVENANCE_REF_PATTERNS` — the two commit-reference shapes this factory records:
  `@ <hex{4,40}>` (materialization `decided_by: IDEATION-NNN @ <sha>`, mirroring
  DECIDED_BY_RE in scripts/user_needs/check_materialization_provenance.py) and
  `commit: <hex{4,40}>` line (task goal.md `requirements_version.commit`). Trailing
  `\b`/line-anchor make 64-hex sha256 content hashes unmatchable (no word boundary inside
  the first 40 chars → whole match fails). Over-match is fail-safe; resolution drops noise.
- `_collect_referenced_commits(workspace, harvested_relpaths)` — scans the harvested files
  (workspace side) + every `requirements_tasks/**/goal.md` under the copy (task pins are not
  product-def globs, so scanned additionally).
- `_gate_harvest` COMPLETE branch: collect → `compact_workspace_git` → export, i.e. AFTER
  harvest (scan sees exactly what got out) and BEFORE export (the pre-run bundle head is how
  P — the immutability boundary — is recovered). Applies to fresh runs and cold resumes alike
  (build_resume reuses launch_and_gate).

### Not touched (scope guards honored)

- `run_skeleton.py` (test mode — no persisted history, nothing to compact).
- No global squash-and-rewrite anywhere.
- No mechanism outside `scripts/playground/` grew harness handling (AC-21).

## Empirical pre-verification

Raw git 2.43 in a temp repo confirmed before implementation: commit-tree+update-ref squash
keeps the boundary commit's hash and the tip tree byte-identical with clean status;
`rev-parse --verify` fails loud on unknown refs and resolves 8-hex prefixes;
`bundle list-heads` emits `<sha> <ref>`.

## Tests

7 new tests initially (+1 more added during quality review, see below); all 77 tests in the
two touched modules pass.

- `scripts/tests/test_playground_workspace.py` (5): tail squash keeps referenced (given as
  8-hex abbreviation) + persisted prefix hash-stable and tree unchanged; no-op below the
  2-commit minimum; first-run squash-all-to-root; unresolvable candidates dropped without
  blocking; merge history → safe no-op.
- `scripts/tests/test_playground_build.py` (2): `_collect_referenced_commits` extracts both
  provenance shapes and never a 64-hex sha256; end-to-end 2-run `run_build_mode` sequence
  where run 2's child commits a base, references it `@ <8-hex>` from a harvested persona,
  and piles junk commits — re-exported bundle history is exactly
  [squash, referenced, baseline2, run1-tip] (stable hashes for referenced + run-1 tip,
  tail squashed).

## Gates

`scripts/quality/check_python_gates.sh`: **all 7 PASS** (G1 lint, G2 type, G3 tests, G4
no-handrolled-YAML, G5 print-discipline, G6 complexity, G7 canonical-lib).

CLAUDE.md §11: no update — Rule 3 (playground-subsystem-internal functions, no ad-hoc
analytical use), no generated file.

## Outcome

AC-20 compaction half (preserve-referenced / squash-unreferenced / immutable-once-persisted)
and AC-21 (encapsulation) implemented. End-to-end ≥2-run verification stays with the sibling
`verify-persistent-harness-git` task per goal.md.

## verify-quality — quality-checker review (cycle 1)

The `quality-checker` agent returned RED: it claimed `_resolve_workspace_commits`'s ambiguous-
short-hash safety branch (`if "ambiguous" in str(exc).lower(): return None`) was dead code
under git 2.43.0, because it tested `git rev-parse --verify --quiet <ambiguous>^{commit}` and
found `--quiet` suppresses the distinguishing "ambiguous" text.

**Verified and found to be a false positive against the actual implementation**: the code does
NOT pass `--quiet` (`["git", "rev-parse", "--verify", f"{candidate}^{{commit}}"]`). Re-tested
directly against `_resolve_workspace_commits` with a real forced 4-hex short-hash collision
(`git hash-object -w --stdin` on ~600 throwaway blobs until two shared a prefix): git's stderr
without `--quiet` DOES read `error: short object ID <pfx> is ambiguous ...`, `WorkspaceError`
embeds `exc.stderr` into its message, and the function correctly returned `None` (skip
compaction for the run) — the branch is live and correct, not dead.

The agent's secondary point stood: no test exercised this real-ambiguity scenario (all prior
resolution tests used ordinary unresolvable noise, which is dropped individually rather than
blocking the whole run — a different code path). Added
`test_compact_skips_on_genuinely_ambiguous_referenced_commit` (+ its
`_find_ambiguous_short_prefix` helper, brute-forcing a REAL 4-hex collision via
`git hash-object` rather than asserting against a hypothetical error string) to
`scripts/tests/test_playground_workspace.py`. 77 tests total in the two touched modules now
pass; `scripts/quality/check_python_gates.sh` re-run: all 7 PASS.

## verify-quality — quality-checker re-review (cycle 2, GREEN)

Re-spawned `quality-checker` with the correction + new test. It independently reproduced a
real short-hash collision, confirmed the live `_resolve_workspace_commits` call carries no
`--quiet`, confirmed git 2.43.0's real stderr contains "ambiguous" without `--quiet`, retracted
the original RED, verified the new regression test is genuine (non-mocked), and ran a full
structural pass (tiers, no hand-rolled YAML, no bare except, no print, docstring quality, no
new dependency). **STATUS: GREEN.**
