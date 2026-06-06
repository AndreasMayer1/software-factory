---
task_id: TASK-PROC-041-01-08
type: impl
parent_requirement: REQ-PROC-041-01
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-RELIABILITY
status: completed
completed: 2026-04-24
effort: M
created: 2026-04-24
started: 2026-04-24
after: [TASK-PROC-041-01-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-29, AC-30, AC-32, AC-33]
  sections: []
scope_description: "Implement hung-session detection and recovery in orchestrate.py (AC-29, AC-30, AC-32, AC-33)"
release_description: ""
worktree_path: ""
session_id: ""
session_account: ""
---

# Goal: Implement Hung Session Detection & Recovery

## Objective

Implement AC-29, AC-30, AC-32, AC-33 in `scripts/automation/orchestrate.py`:

- Switch session launch from `subprocess.run` to `subprocess.Popen` + polling loop
- Poll every `--hung-check-interval` seconds (default: 60) to check liveness
- Kill sessions detected as hung (no children + JSONL stale for `--hung-timeout` min, default: 30)
- Log hung kills as WARNING; record kill reason in run report
- Leave `goal.md` unchanged after kill so existing AC-15 resume logic takes over

## Context

See the exploration task `TASK-PROC-041-01-07` and its `plans_and_protocols/2026-04-24_01_opus_plan.md`
for the full analysis (approach evaluation, threshold rationale, edge-case handling).

**Incident that motivated this**: Session `1ce0fdc2` (2026-04-23) ran 13+ hours with JSONL
stale since 10:08 but 4 active dart/bash children — it was genuinely working, not hung.
The detection logic must account for this: child process presence = not hung.

## Required Changes

### 1. `OrchestratorDeps` — add `popen_subprocess: Callable`

Add a `popen_subprocess: Callable` field (default: `subprocess.Popen`) to `OrchestratorDeps`.
Keep `run_subprocess` for all non-session subprocesses. Update the real-deps wiring in `main()`.

### 2. New function: `run_session_with_hung_detection()`

Replace the direct `run_normal_session()` / `run_resume_session()` / `run_fresh_session_with_answer()` calls with a wrapper that:

1. Launches the process via `Popen` (not `run`)
2. Records `start_time = time.monotonic()`
3. Records initial JSONL mtime (or `None` if JSONL doesn't exist yet)
4. Enters a poll loop (sleep `hung_check_interval` s between iterations):
   a. `proc.poll()` — if process exited, return normally (build `CompletedProcess`)
   b. Check hard ceiling: `elapsed >= session_timeout_secs` → kill, reason `session_timeout`
   c. Check liveness: get current JSONL mtime (`os.path.getmtime` or `None`)
      - If mtime changed: reset stale counter
      - If mtime unchanged: check `ps --ppid <proc.pid>` for child processes
        - Children present: not hung (tool call in flight), reset stale counter
        - No children: increment stale duration; if ≥ `hung_timeout_secs` → kill, reason `hung`
5. Kill sequence: `proc.send_signal(SIGTERM)` → sleep 10 s → `proc.poll()` → if alive, `proc.kill()`
6. Return a synthetic `CompletedProcess` with a sentinel exit code (e.g. `-15` for SIGTERM, `-9` for SIGKILL) and a `"killed_reason"` field accessible to the caller

### 3. CLI arguments

Add to `parse_args()`:
- `--hung-check-interval N` (int, default 60, metavar "SECONDS")
- `--hung-timeout N` (int, default 30, metavar "MINUTES")

Pass these down to `run_normal_session_step()` and the analogous resume/fresh-session paths.

### 4. Caller integration

In `run_normal_session_step()` (and the resume paths in `process_answered_feedback` /
`process_in_progress_resume`): pass the new args to `run_session_with_hung_detection()`.
After the call:
- If killed: emit `WARNING: session <uuid> killed (reason: <reason>) after <elapsed>s`
- Record `"hung_killed": True, "kill_reason": reason` in the session record
- Do NOT mark task as failed — leave `goal.md` unchanged

### 5. Run report

In `write_report()`: add a `### Hung / Timed-Out Sessions` section if any session record has
`hung_killed: True`. Format per entry: task_id, session UUID (first 8 chars), reason, elapsed.

### 6. Tests

Update / add tests in `scripts/automation/tests/test_orchestrate.py`:
- `test_hung_detection_no_children_stale_jsonl`: mock `popen_subprocess` to return a process that never exits; mock JSONL mtime as frozen and `ps --ppid` as empty → assert kill called after threshold
- `test_hung_detection_children_present_not_hung`: same but `ps --ppid` returns children → assert no kill
- `test_session_timeout`: mock process that never exits; elapsed > session_timeout → assert kill with reason `session_timeout`
- `test_kill_sequence_sigterm_then_sigkill`: mock process that ignores SIGTERM; assert SIGKILL follows after 10 s

## Notes

- JSONL path: `/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app/<uuid>.jsonl`
  — use the `session_uuid` already passed to the session launch commands.
- `ps --ppid <pid>` child check: `ps --ppid <pid> --no-headers` — non-empty stdout = children present.
  Use `deps.run_subprocess` (not `popen_subprocess`) for this auxiliary call.
- The polling loop must also check the stop flag (`stop_flag["requested"]`) on each iteration so
  SIGTERM to the orchestrator propagates into the session kill during the poll.
- `os.path.getmtime()` raises `FileNotFoundError` if JSONL doesn't exist yet (new session, Claude
  hasn't written the first token). Treat as "no growth" but do NOT count stale time until the file
  exists — the session just started.
