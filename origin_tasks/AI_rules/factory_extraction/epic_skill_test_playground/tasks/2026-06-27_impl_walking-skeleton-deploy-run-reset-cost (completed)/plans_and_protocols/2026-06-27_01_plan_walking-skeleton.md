# Plan — Walking Skeleton: Deploy → Run → Git-Reset → Cost

Task: TASK-PROC-068-04 · REQ-PROC-068 · type impl · effort L
Covers AC-07 (F/MEDIUM), AC-08 (C/MEDIUM), AC-09 (S/HIGH)

## Objective (single fixture, single-cell loop)

Minimum viable substrate loop on ONE fixture:
1. **Deploy** a candidate factory (snapshot of `.claude/skills/`) into a harness dir.
2. **Run** a skill with the harness dir as cwd (child `claude` session).
3. **Git-reset** the harness to clean state between runs.
4. **Capture** real token + wall-clock cost from the child session.

No multi-pair corpus, no discriminating-maturity walk, no behavioural oracle (all out of scope).

## Distilled crux (so build agent need not re-read orchestrate.py — 3793 lines)

`scripts/automation/orchestrate.py`:
- **`run_session_with_hung_detection(cmd, env, session_uuid, hung_check_interval, hung_timeout_secs, session_timeout_secs, stop_flag, deps)`** (line ~1579) is the launch core: `deps.popen_subprocess(...)` then polls for (a) stop_flag, (b) proc exit, (c) hard session ceiling, (d) JSONL-mtime-stale-AND-no-children → hung.
- **`JSONL_BASE`** (line ~1573) is **hardcoded** to the *current* project's JSONL dir:
  `/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app`.
  `jsonl_path = os.path.join(JSONL_BASE, f"{session_uuid}.jsonl")` (line ~1614). **This is the SG-01 blocker**: hung-detection watches the *host* project's JSONL, not the child's.
- The core is entangled with `OrchestratorDeps` (popen/sleep/get_mtime/run_subprocess), `stop_flag`, and the `_LaunchOSError` wrapper `_launch_claude_session`. It is NOT a reusable API — `OrchestratorDeps`, `state.json`, `inbox.md`, `stop_flag` are required. "Thin facade" is wishful (SG-01 red-team finding).

## Mandatory first-build gates (accepted SG corrections — NOT open debate)

- **SG-01 (feasibility floor)**: build a REAL launch adapter, not a facade. Extract the launch core
  into a standalone module that (a) does not require orchestrator-global deps (state.json / inbox /
  stop_flag), and (b) **parameterizes the JSONL hung-detection path on the CHILD's cwd**, not the
  hardcoded host `JSONL_BASE`. Independently testable module.
- **SG-04 (child_session_safety floor, AC-09, archetype-S/HIGH)**: re-instate ONE OS-level
  containment layer to close CON-04's absolute-path cwd-escape. Worktree alone does NOT close it.
  Recommended: Linux `unshare` (user + mount namespace) — cheapest, no new pip/npm dependency, no OS
  user provisioning. The containment must DEMONSTRABLY block a child reaching the host factory tree
  via an absolute path; this closure MUST be tested (AC-09).
- **SG-02 (already PASS — reuse, do not re-litigate)**: cost capture via
  `claude -p --output-format json` → `.total_cost_usd` (+ `.duration_ms`). Verified PASS in
  TASK-PROC-073-01-01 (run1 $0.2706, run2 $0.2784). Reuse this exact path; do NOT try `--bare` or
  re-verify from scratch.
- **SG-03 (advisory scope — bake into output)**: ~100 paired-fixture validity floor is unreachable at
  skeleton stage. Skeleton-stage regression verdicts are ADVISORY. Every result artifact MUST carry a
  visible note saying so (T-corpus + T-maturity will address the floor later).

## Module layout (proposed — build agent finalizes)

`scripts/playground/` (Python package, `# tier:` headers per REQ-PROC-051):
- `launch_adapter.py` — standalone child-session launcher: Popen + hung-detection with JSONL path
  **parameterized on child cwd**; wraps the child in OS containment (SG-04). No orchestrator deps.
- `containment.py` (or folded into launch_adapter) — `unshare`-based confinement; the CON-04 closure.
- `deploy.py` — snapshot `.claude/skills/` (candidate factory) into the harness dir.
- `reset.py` — `git`-reset the harness to clean state between runs; verify harness unmodified (AC-07).
- `cost_ledger.py` — parse the JSON envelope, accumulate `total_cost_usd` + `duration_ms`, enforce a
  hard `max_budget_usd` cap (warn — do not silently overrun), emit the ledger + ADVISORY annotation.
- `run_skeleton.py` — orchestrates deploy → run → reset → cost for the single fixture.
- `tests/` — unit tests per module; an AC-09 escape-attempt test; an AC-07 clean-state test;
  an AC-08 ledger/cap test. All FIVE Python gates must PASS (G1 ruff, G2 mypy, G3 pytest,
  G4 no hand-rolled YAML, G5 print discipline).

## Hard constraints

- Use `claude-write-script` skill for EVERY file created/modified under `scripts/` (no exceptions).
- HIGH-consequence scripts need a `contract.yaml` EGP disposition — claude-write-script handles it.
- No new top-level dependency (REQ-PROC-060): `unshare` is OS-level, `claude` CLI already present.
- AC-09 is archetype-S/HIGH: the escape vector MUST be exercised by a real test that proves the host
  factory tree is unreachable from the child via absolute path / cwd escape.

## Execution

Background `implementation-engineer` agent owns the closed loop (design details → implement all
modules → write tests → run Python gates → iterate to GREEN → persist protocol + tracker → return
short summary). 4:30 heartbeat in main session while it runs. Then: `verify-quality` (lib/test
untouched, but Python gates already enforced by claude-write-script) → `task-complete`.
