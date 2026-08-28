# Plan 10 — Implement REQ-PROC-068 AC-12 (contained-child auth binding)

Task: TASK-PROC-068-11 · 2026-07-04. Implements the just-committed AC-12 (commit 524a8867).
Empirical basis: protocol 09. AC-12 contract (authoritative): the requirement text.

## Contract to satisfy (AC-12)
The bwrap jail binds the host auth-config dirs at their REAL absolute paths, read-WRITE:
- `~/.claude` (expanduser) — MANDATORY. Absent → the launch FAILS with a clear error.
- `~/.ccs` (expanduser) — OPTIONAL. Present → also bound. Absent → skipped SILENTLY (no error, no
  warning); a non-CCS host is fully supported.
Both must be bound together when present so the CCS symlink web (`~/.ccs/shared/* -> ~/.claude/*`)
resolves — binding `~/.ccs` WITHOUT `~/.claude` is what let `ccs` auto-recovery DELETE real symlinks
(protocol 09). Native `claude` (via CLAUDE_CONFIG_DIR) and `ccs` (orchestrate.py) both then work.

## Change 1 — containment.py
- Add module constants derived at call time (NOT hardcoded /home/vscode): compute from
  `os.path.expanduser("~/.claude")` and `os.path.expanduser("~/.ccs")`.
- New helper `_auth_config_binds(claude_dir, ccs_dir) -> list[str]` (params injectable for tests):
  - if `claude_dir` does not exist → raise a new `AuthConfigUnavailable(RuntimeError)` with a message
    naming ~/.claude as required (and that ccs cannot work without claude).
  - always emit `--bind <claude_dir> <claude_dir>` (read-write).
  - if `ccs_dir` exists → also emit `--bind <ccs_dir> <ccs_dir>`; else emit nothing for ccs (silent).
  - returns the flag list.
- Call it inside `_build_bwrap_cmd` (bwrap path only — the `unshare` fallback leaves host paths visible,
  so auth already works there; do not add binds to the unshare branch). Compute the real dirs via
  expanduser by default; allow an injected override for tests (e.g. optional params on _build_bwrap_cmd
  defaulting to expanduser).
- WHY comment (Python #): explain both-dirs-together (symlink web / avoid ccs auto-recovery deleting real
  symlinks — cite protocol 09), rw (sessions write), and mandatory-claude/optional-ccs contract → AC-12.
- Export `AuthConfigUnavailable`.

## Change 2 — run_skeleton.py (child env)
The child env must let native `claude` AND `ccs` authenticate:
- Child `HOME` must be the REAL home (`/home/vscode` via expanduser) — NOT the workspace — so `ccs`
  finds `~/.ccs` and `claude` finds `~/.claude`. (This reverses scrub_env's HOME redirect for this use.)
- `CLAUDE_CONFIG_DIR` must be present and point at the active account instance (inherited from the parent
  env, which already sets it). Preserve it.
- Simplest: `child_env = dict(os.environ)` (inherits real HOME + CLAUDE_CONFIG_DIR). Do NOT scrub HOME to
  the workspace. (Optionally still redirect only XDG_CACHE to the workspace to limit cache pollution —
  optional, not required.) Keep cwd = workspace (so claude keys the session JSONL to a NEW project folder,
  not the real app's — the developer confirmed this is the desired isolation of session state).
- Add `AuthConfigUnavailable` to main()'s except ladder (clear error exit).

## Change 3 — tests
- `scripts/tests/test_playground_containment.py`: unit-test `_auth_config_binds` with tmp dirs for all
  four combinations — both present (both --bind flags), claude only (only claude --bind, no ccs flag),
  claude absent (raises AuthConfigUnavailable), and assert the emitted flags are `--bind <dir> <dir>`.
  Assert `_build_bwrap_cmd` includes the claude bind when the injected claude dir exists.
  DO NOT touch the real ~/.ccs or ~/.claude in any unit test — use tmp dirs only.
- Keep the existing `--share-net` and harness-bind assertions green.

## Gates / safety
- Every scripts/ edit via `claude-write-script` (REQ-PROC-051). Run `scripts/quality/check_python_gates.sh`;
  block only on NEW findings. Known baseline: G3 has a pre-existing collection/failure in an unrelated
  test file (test_check_dependency_usage.py / test_aggregate_read_metrics.py) — not a regression.
  Confirm `python3 -m pytest scripts/tests/test_playground_*.py -q` is 100% green.
- SAFETY: no live `ccs`-in-jail run against the REAL ~/.ccs. The run_skeleton smoke uses NATIVE `claude`
  (not `ccs`), and now binds BOTH ~/.claude + ~/.ccs, so the protocol-09 destructive auto-recovery cannot
  recur (it required ~/.claude absent). Unit tests use tmp dirs only.
- No new top-level dependency. Do NOT commit (the session commits the mechanism after the green smoke).

## After implementation (session-owned, not the agent)
- Re-run the live smoke: `PYTHONPATH=. python3 -m scripts.playground.run_skeleton --harness-dir
  .../test_harness_app --host-project-dir .../flutter_app --session-uuid <uuid>
  --prompt "Reply with exactly: SMOKE_OK" --max-budget-usd 0.25 --model claude-sonnet-4-5`.
  Expect a valid JSON ledger with a non-error child result (SMOKE_OK) and recorded cost.
- If green → commit the whole mechanism (containment/workspace/deploy/reset/run_skeleton + tests +
  protocols 07/08/09 + plan 10) as a feat commit; then unpark TASK-PROC-068-11 via pending_feedback.
