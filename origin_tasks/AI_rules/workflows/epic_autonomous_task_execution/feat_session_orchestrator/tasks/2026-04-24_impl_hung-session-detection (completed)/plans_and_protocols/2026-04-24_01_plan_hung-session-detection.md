# Plan: Hung Session Detection & Recovery (TASK-PROC-041-01-08)

## Files to Change

1. `scripts/automation/orchestrate.py` (~2162 lines)
2. `scripts/automation/tests/test_orchestrate.py` (~2725 lines)

## Changes in orchestrate.py

### A. OrchestratorDeps — add popen_subprocess (line ~789)
Add `popen_subprocess: Callable` field after `run_subprocess`. Default in `main()`: `subprocess.Popen`.

### B. parse_args() — add CLI args (line ~1959)
Add two arguments:
- `--hung-check-interval N` (int, default 60, metavar "SECONDS")
- `--hung-timeout N` (int, default 30, metavar "MINUTES")

### C. New function run_session_with_hung_detection() — insert after run_fresh_session_with_answer (~line 597)
Parameters: `cmd: list`, `env: dict`, `session_uuid: str`, `hung_check_interval: int`, `hung_timeout_secs: int`, `session_timeout_secs: int`, `stop_flag: dict`, `deps: OrchestratorDeps`

Logic:
1. `proc = deps.popen_subprocess(cmd, stdout=PIPE, stderr=STDOUT, text=True, env=env)`
2. Record `start_mono = time.monotonic()`, `last_mtime = None`, `stale_since_mono = None`
3. JSONL path: `/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app/<session_uuid>.jsonl`
4. Poll loop (sleep hung_check_interval between iterations):
   a. If stop_flag["requested"] → kill(SIGTERM/SIGKILL), return sentinel
   b. `rc = proc.poll()` — if not None, return CompletedProcess(rc, stdout, stderr)
   c. Elapsed check: if elapsed ≥ session_timeout_secs → kill, reason="session_timeout"
   d. JSONL mtime: `os.path.getmtime(jsonl_path)` or None if FileNotFoundError
      - If file doesn't exist yet: skip stale counting (session just started)
      - If mtime changed: reset stale_since_mono
      - If mtime unchanged and file exists: check children via `deps.run_subprocess(["ps", "--ppid", str(proc.pid), "--no-headers"], ...)`
        - Non-empty stdout → children present, reset stale_since_mono
        - Empty stdout → if stale_since_mono is None: set stale_since_mono = now; if (now - stale_since_mono) >= hung_timeout_secs → kill, reason="hung"
5. Kill sequence: SIGTERM → sleep 10s → poll → SIGKILL if alive
6. Return synthetic CompletedProcess with returncode=-15 (SIGTERM) or -9 (SIGKILL), store kill_reason in a custom attribute

Note: `proc.communicate()` can't be used with polling. Capture stdout by reading `proc.stdout` after kill via `proc.communicate(timeout=5)`.

### D. Wire callers — 3 places
For each: replace `run_normal_session(...)` / `run_resume_session(...)` / `run_fresh_session_with_answer(...)` with `run_session_with_hung_detection(cmd, env, session_uuid, ...)`.

Callers need to be refactored slightly: the 3 `run_*` functions currently build the command list internally. We need to either:
- Extract command-building as a separate helper, OR
- Pass the result of a "build cmd" helper to `run_session_with_hung_detection`

Simpler approach: each `run_normal_session`, `run_resume_session`, `run_fresh_session_with_answer` returns a cmd list (rename to `_build_normal_session_cmd`, etc.) and `run_session_with_hung_detection` launches it.

After the call in each caller:
- If `result.returncode < 0` (sentinel): extract `kill_reason` from result (via custom attribute)
  - `WARNING: session <uuid> killed (reason: <reason>) after <elapsed>s`
  - Set `session_record["hung_killed"] = True`, `session_record["kill_reason"] = reason`
  - Do NOT modify goal.md

### E. write_report() — add Hung section (line ~853)
After the Pending Feedback section:
- If any session has `hung_killed: True` → add `### Hung / Timed-Out Sessions` section
- Per entry: task_id, uuid[:8], reason, elapsed

## Changes in test_orchestrate.py

Add 4 tests in a new `TestRunSessionWithHungDetection` class:

1. `test_hung_detection_no_children_stale_jsonl`: mock popen returns never-exits proc; JSONL mtime frozen; ps empty → assert kill after threshold
2. `test_hung_detection_children_present_not_hung`: same but ps returns children → no kill
3. `test_session_timeout`: mock never-exits proc; elapsed > session_timeout → kill, reason=session_timeout
4. `test_kill_sequence_sigterm_then_sigkill`: mock proc ignores SIGTERM (still alive after 10s) → SIGKILL follows

Also update `make_deps()` to add `popen_subprocess` default and `make_args()` to add new args.

## Key Constants
- `JSONL_BASE = "/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app"`
- Default session_timeout_secs: 14400 (4 hours) — from exploration plan
