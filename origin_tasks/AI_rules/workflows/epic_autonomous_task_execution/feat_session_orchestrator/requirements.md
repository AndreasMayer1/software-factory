---
id: REQ-PROC-041-01
status: in_progress
updated: 2026-04-10
stakeholder: developer
created: 2026-04-06
parent: REQ-PROC-041
after: [REQ-PROC-041-03]
blocks: []
market_research_refs: [] # No relevant findings identified
user_needs:
  implements_flows: []
  addresses_scenarios: []
  personas_served: [PERSONA-004]
trackable_items:
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
    - id: AC-04
    - id: AC-05
    - id: AC-06
    - id: AC-07
    - id: AC-08
    - id: AC-09
    - id: AC-10
    - id: AC-11
    - id: AC-12
    - id: AC-13
    - id: AC-14
    - id: AC-15
    - id: AC-16
    - id: AC-17
    - id: AC-18
    - id: AC-19
    - id: AC-20
    - id: AC-21
    - id: AC-22
    - id: AC-23
    - id: AC-24
    - id: AC-25
    - id: AC-26
    - id: AC-27
    - id: AC-28
    - id: AC-29
    - id: AC-30
    - id: AC-32
    - id: AC-33
    - id: AC-34
    - id: AC-35
    - id: AC-36
    - id: AC-37
    - id: AC-38
---

# Session Orchestrator

## Overview

A Python orchestrator script (`scripts/automation/orchestrate.py`) that drives unattended batch processing of the task queue: launches sequential `claude` sessions with per-account `CLAUDE_CONFIG_DIR` rotation, handles rate limits with automatic restart, supports scheduled or manual stop, captures session output for a final report, and requeues feedback-paused sessions when the user has provided answers.

## Purpose

The orchestrator enables the developer to start a single command, walk away, and return later to review completed tasks, pending questions, and a structured session report — without having to manually start, monitor, or stop individual Claude Code sessions.

## Scope

**Included:**
- Launching `claude` sessions directly via `CLAUDE_CONFIG_DIR` (not `ccs <account>`) — tested and confirmed; CCS nesting fails inside a running Claude session
- Round-robin account rotation on each new session using `CLAUDE_CONFIG_DIR=/home/vscode/.ccs/instances/<account>`
- Rate-limit detection from exit code + output; parsing the reset time and waiting until reset + 5 min buffer
- Sequential execution (one session at a time)
- Pre-assigning session UUIDs via `--session-id <uuid>` before launch
- Writing session metadata to the active task's goal.md before launch
- Two termination modes: endless (runs until signaled) and scheduled (user provides stop datetime)
- Manual stop via `automation/.stop-requested` sentinel file or SIGTERM
- Automatic restart after rate limit reset
- Per-session stdout capture (stripped of hook reminder footers) stored at session close
- Report file written on any termination event
- Detecting feedback-paused sessions (question.md without answer.md) and requeuing on next run when answered
- State persistence to `automation/state.json` for restart resilience

**Excluded:**
- Parallel session execution
- Task prioritization or selection logic (delegates to existing "Do Next Task" routing)
- Creating or modifying task goal.md files beyond writing session metadata fields

## Behavior

### Launch Command

The orchestrator launches each session as:
```python
env = {
    **os.environ,
    "CLAUDE_AUTOMATED_MODE": "1",
    "CLAUDE_CONFIG_DIR": f"/home/vscode/.ccs/instances/{account}"
}
result = subprocess.run(
    ["claude", "--dangerously-skip-permissions",
     "--session-id", session_uuid, "-p", "Do next task"],
    capture_output=True, text=True, env=env
)
```

`claude -p` exits automatically after the response (exit code 0 on success, exit code 1 on rate limit).

### Account Rotation

Accounts rotate round-robin from a configured list (default: `["gmail", "web", "gmail2"]`). Each new session uses the next account. The current account index is persisted in `automation/state.json`.

### Rate Limit Handling

When `result.returncode != 0` and the output contains `"hit your limit"` or similar, the orchestrator:
1. Parses the reset time from the message (e.g. "resets 11am (Europe/Berlin)")
2. Waits until that time + 5 minutes
3. Rotates to the next account and continues (does not retry on the exhausted account until its window clears)

### Termination Modes

**Endless mode** (default): runs until one of:
- `automation/.stop-requested` file is created by the user
- SIGTERM/SIGINT received

**Scheduled mode** (`--stop-at "YYYY-MM-DD HH:MM"`): stops after the current session completes once the specified datetime is reached; does not interrupt a running session.

In both modes, after stopping, a report is written (see below) and `automation/.automated_mode` and `automation/.stop-requested` are cleaned up.

### Session Output Capture

Each session's stdout is captured into `result.stdout`. Before storing, the script strips the hook reminder footer: any content matching `\n---\n**Reminder:**.*` (appended by Claude's session hooks). The cleaned output is stored in `automation/session_outputs/<session_uuid>.txt` immediately after the session exits.

### Report Generation

On any termination event, the orchestrator writes `automation/reports/YYYY-MM-DD_HH-MM_report.md` containing:
- Orchestrator run summary (start time, stop reason, accounts used, total sessions)
- Per-session entry: task ID, account, start/end time, exit status, cleaned stdout output
- List of tasks still in `pending_feedback/` with their questions

Report generation is entirely script-based (no LLM call, no API tokens consumed).

### Feedback Resumption

When the orchestrator's session loop iterates, it checks `automation/pending_feedback/*/` for tasks that have both `question.md` and `answer.md`. These are added to the front of the queue as resume sessions (see REQ-PROC-041-04 for resume command construction).

### Unanswered Questions — Non-Blocking

Tasks with an unanswered `question.md` (i.e. `question.md` present, no `answer.md`) are skipped silently by the session loop: `find_resumable_session` already excludes them, and the "Do next task" routing will not pick up a task that is `in_progress` with a pending question. The orchestrator logs a note and continues with other available tasks. **It does NOT stop.**

The orchestrator only stops for unanswered questions when there are no other tasks to run (natural idle) or when a stop signal is received.

## Acceptance Criteria

- [ ] AC-01: `scripts/automation/orchestrate.py` exists and runs with `python3 scripts/automation/orchestrate.py`
- [ ] AC-02: Script accepts `--accounts <list>` (default `gmail,web,gmail2`), `--stop-at "YYYY-MM-DD HH:MM"` (scheduled stop), `--min-wait-seconds N` (minimum pause between sessions, default 0), and `--max-tasks N` (stop after N sessions have been launched, default: run indefinitely)
- [ ] AC-03: Each session is launched via `subprocess.run(["claude", ...])` with `CLAUDE_CONFIG_DIR` set to `/home/vscode/.ccs/instances/<account>` and `CLAUDE_AUTOMATED_MODE=1` in the subprocess environment
- [ ] AC-04: Accounts rotate round-robin; each new session uses the next account in the configured list
- [ ] AC-05: When a session exits with code 1 and output contains a rate-limit message, the orchestrator parses the reset time, waits until reset + 5 min, then continues with the next account; when a session exits with a permanent access error (e.g. "does not have access"), the account is disabled for the remainder of the run (not just rate-limit rotated)
- [ ] AC-06: At most one session runs at a time; `subprocess.run` (blocking) is used for the session call
- [ ] AC-07: A UUID is generated and passed via `--session-id <uuid>` before each launch; UUID and account are written to the active task's goal.md before subprocess starts
- [ ] AC-08: Creating `automation/.stop-requested` or sending SIGTERM causes the orchestrator to stop after the current session completes
- [ ] AC-09: When `--stop-at` datetime is reached, the orchestrator stops after the current session completes
- [ ] AC-10: After each session exits, stdout is captured, the hook reminder footer is stripped, and the result is written to `automation/session_outputs/<session_uuid>.txt`
- [ ] AC-11: On any termination, `automation/reports/YYYY-MM-DD_HH-MM_report.md` is written with run summary and per-session entries using only script logic (no LLM call)
- [ ] AC-12: Orchestrator state (account index, paused task list, run count) is persisted to `automation/state.json` and re-read on restart; `start_time` is reset to the current datetime on every new orchestrator launch (not preserved from previous runs)
- [ ] AC-13: Tasks with `answer.md` present in `pending_feedback/` are resumed via `claude --resume <session-id> -p "$(cat answer.md)"` with the account from `question.md` frontmatter
- [ ] AC-14: A `claude-autorun` skill exists in `.claude/skills/` with three actions — `start` (launches orchestrator in background via `python3 -u`, checks if already running by reading PID from `automation/.automated_mode` sentinel and verifying process is alive), `stop` (creates `automation/.stop-requested`), and `status` (reads `automation/.automated_mode` PID for running check + latest report and summarises current state to the user)
- [ ] AC-16: After every orchestrator termination, a health summary section is appended to the run report using only script logic (no LLM call); it includes: tasks that were in_progress at run start and their final status, sessions that exited 0 but left their task still in_progress, and unanswered questions remaining in pending_feedback/
- [ ] AC-15: Before launching a new "Do next task" session, the orchestrator checks for any task with `status: in_progress` in `goal.md` that has a `session_id` set and no unanswered `question.md` in `pending_feedback/`; if found, it resumes that session via `claude --resume <session_id> -p "<context prompt>"` instead of launching a fresh session — preventing the "Do next task" flow from re-encountering and re-asking about in_progress tasks
- [ ] AC-17: `automation/MONITORING_CRITERIA.md` exists and defines expected behavior and anomaly signals for every significant orchestrator scenario; the monitoring cron prompt (in the `claude-autorun` skill) references this file before analyzing the log
- [ ] AC-18: When `scripts/next_tasks.py` returns an empty result (no tasks of any kind), the orchestrator stops with reason `queue_empty` rather than launching a wasted session
- [ ] AC-19: When all configured accounts are permanently disabled (perm error) with none rate-limited, the orchestrator stops gracefully with reason `all_accounts_disabled` rather than crashing with `ValueError`
- [ ] AC-20: `answer_is_empty()` treats whitespace-only `answer.md` files as empty (uses `strip()` check on content, not just file size)
- [ ] AC-21: The orchestrator tracks per-session-id resume attempts within a run; after 3 failed resume attempts for the same session_id, it logs a warning, skips the session for the remainder of the run, and includes the stuck task in the run report
- [ ] AC-22: When a task with `status: in_progress` has no `session_id` in `goal.md`, the orchestrator logs `WARNING: <task_id> is in_progress but has no session_id — skipping (may have been started manually)` and includes the task in the run report under a dedicated "Skipped (no session_id)" section
- [ ] AC-23: On orchestrator **start**, a git commit is made containing any new `answer.md` files in `automation/pending_feedback/`; commit message: `chore(automation): record user answers YYYY-MM-DD HH:MM`; non-fatal if git fails (log WARNING)
- [ ] AC-24: On orchestrator **stop** (in the `finally` block, after report is written), a git commit is made containing the new report file and any `question.md` files in `automation/pending_feedback/`; commit message: `chore(automation): session report YYYY-MM-DD HH:MM [stop_reason]`; non-fatal if git fails (log WARNING)
- [ ] AC-25: A lock file (`automation/.orchestrator.lock`) is created at startup using `fcntl.flock` (exclusive, non-blocking); if the lock cannot be acquired, the process logs `ERROR: orchestrator already running — aborting` and exits immediately without writing the `.automated_mode` sentinel
- [ ] AC-26: When a new `question.md` is detected for a task that already has a fingerprint in `state.json["question_fingerprints"]`, the orchestrator computes Jaccard similarity between the normalized word sets; if ≥ 0.60, it logs `WARNING: <task_id> appears to be asking the same question again (similarity 0.XX) — possible loop` and includes the task in the run report; the fingerprint stored in `state.json` contains both the normalized word set and the first 300 normalized characters of the question body
- **AC-27**: `automation/MONITORING_CRITERIA.md` covers bootstrap-signal patterns (S21–S24): bootstrap-created orchestration task (INFO), duplicate-guard skip (INFO), bootstrap loop with no progress (WARNING/CRITICAL), and release-complete clean stop (INFO). S11 includes a note distinguishing `queue_empty` during active release build-out from legitimate end-of-release stop.
- **AC-28**: `run_preflight_queue_check()` or `claude-automated-mode` emits informational log lines for uncovered ACs using a non-`WARNING:` prefix (e.g., `[bootstrap-signal]`) to avoid false-positive matching by the monitoring LLM. Behavior is unchanged; the line is purely diagnostic.
- **AC-29**: The orchestrator implements liveness-based hung-session detection. A session is considered hung when both of the following have been true continuously for at least `--hung-timeout` minutes (default: 30): (a) the session's JSONL file mtime has not advanced, and (b) `ps --ppid <claude_pid>` reports no child processes (dart/bash). When the hung condition is met, the orchestrator sends SIGTERM to the `claude` process, waits up to 10 seconds, then sends SIGKILL if the process is still alive.
- **AC-30**: The orchestrator accepts `--hung-check-interval N` (seconds, default: 60) and `--hung-timeout N` (minutes, default: 30) CLI parameters. `--hung-check-interval` controls how often the liveness poll runs; `--hung-timeout` is the consecutive-stale threshold before a session is treated as hung.
- **AC-32**: When a session is killed via hung detection, the orchestrator emits `WARNING: session <uuid> killed (reason: hung) after <elapsed>s` and records the kill reason in the run report's per-session entry. The monitoring criteria file (S25) covers the expected recovery pattern for this log line.
- **AC-33**: After killing a hung or timed-out session, the active task's `goal.md` fields (`status: in_progress`, `session_id`) are left unchanged. The orchestrator's next loop iteration applies existing in-progress resume logic (AC-15): it resumes the JSONL session. If the resume fails (exit ≠ 0), existing exhaustion limits (AC-21, max 3 attempts) apply. The orchestrator does not skip or reset the task outside these existing mechanisms.
- **AC-34**: `state.json` exposes runtime observability fields maintained by the orchestrator: `is_running` (bool, `true` at startup / `false` in `finally`), `active_session` (string UUID of the session currently being executed, `null` when idle), `stop_requested` (bool, written `false` at startup; set to `true` on SIGTERM, SIGINT, or external write), `rate_limit_reached` (bool, `true` only while sleeping in `rate_limit_sleep` for a rate-limit reset), `next_wake_time` (ISO 8601 string with timezone offset of the planned resume time when `rate_limit_reached` is `true`, `null` otherwise), `stop_reason` (str | null, the stop-reason string of the last run written in the `finally` block, `null` at startup).
- **AC-35**: All datetime values written to `state.json` by the orchestrator are aware ISO 8601 strings carrying a timezone offset (never naive). A top-level `timezone` field is written at startup and on every state save with the IANA name of the OS local timezone (e.g. `"Europe/Berlin"`, `"UTC"`). The orchestrator's `get_now_local` dependency returns aware local-timezone datetimes by default.
- **AC-36**: `scripts/sleep_when_autorun_done.ps1` uses `state.json["is_running"]` as the primary stop-detection signal. When `is_running` is absent (older orchestrator) or `state.json` is unreadable, the script falls back to the existing `.automated_mode` sentinel + `orchestrate.log` mtime heuristic. The `LogStaleMinutes` parameter is retained for the fallback path.
- **AC-37**: When `state.json["rate_limit_reached"]` is `true`, `sleep_when_autorun_done.ps1` treats the orchestrator as "paused but will resume" and proceeds to suspend the PC immediately, scheduling the wake task from `state.json["next_wake_time"]` minus `WakeBeforeResetMinutes`. It does not wait for `is_running` to become `false` first.
- **AC-38**: Stop signalling is consolidated into `state.json["stop_requested"]`. The orchestrator no longer creates, reads, or unlinks the `automation/.stop-requested` file. The `claude-autorun stop` action writes `stop_requested: true` to `state.json` (preserving all other fields) instead of touching a sentinel file. The `claude-autorun status` action reads `stop_requested` from `state.json`.

## Developer Guidelines

### Key Decisions

- **`Popen` for session launch (AC-29–33)**: Hung detection requires observing the child process while it runs (checking `ps --ppid` and JSONL mtime). This is incompatible with `subprocess.run` (blocking until exit). The session-launch functions must use `subprocess.Popen` and a polling loop. The `OrchestratorDeps` dataclass requires a `popen_subprocess: Callable` entry (default: `subprocess.Popen`) so tests can inject a fake. The `run_subprocess` callable is retained for all non-session subprocesses (git, grep, next_tasks.py).
- **JSONL liveness signal**: The JSONL file at `/home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app/<uuid>.jsonl` does NOT grow while Claude is waiting for a tool result. Child processes under the `claude` PID (`ps --ppid`) are the only reliable liveness indicator during tool execution. The hung condition requires BOTH signals to be absent for the full threshold duration.
- **`claude` directly, not `ccs <account>`**: CCS refuses nested invocation when called from inside a running Claude Code session (error: "Profile not configured for delegation"). The correct approach is to call `claude` with `CLAUDE_CONFIG_DIR` set per account. Tested and confirmed. This is safe because CCS itself only sets `CLAUDE_CONFIG_DIR` to select the account's OAuth credentials (`sessions/*.json`). The `projects/` folder inside each account instance is a symlink to `~/.ccs/shared/context-groups/default/projects` — all accounts share the same session storage, so cross-account resume works correctly.
- **`capture_output=True`**: Use `subprocess.run(..., capture_output=True, text=True)` to capture both stdout and stderr. Rate limit errors appear in stdout; use `result.stdout` for both output capture and error detection.
- **Hook reminder footer stripping**: Claude's session hooks append `\n---\n**Reminder:** ...` to responses. Strip with regex `re.sub(r'\n---\n\*\*Reminder:.*', '', output, flags=re.DOTALL)` before storing session output.
- **Reset time parsing**: The rate limit message format is `"resets HH:MM(am/pm) (Timezone)"`. Parse with a regex and convert to a local datetime using `pytz` or `zoneinfo`. Add 5 minutes as buffer.
- **SIGTERM handler**: Register a signal handler via `signal.signal(signal.SIGTERM, handler)` that sets a stop flag checked between sessions. Do not use `sys.exit()` inside the handler.
- The sentinel file `automation/.automated_mode` is created by the orchestrator at startup and deleted in a `finally` block — it is always cleaned up even on crash.

### Common Pitfalls

- Using `--bare` in the launch command: Disables CLAUDE.md loading, breaking automated-mode rules. Never use `--bare`.
- Not stripping reminder footer: Report entries will contain noise from session hooks unrelated to task output.
- All accounts exhausted simultaneously: If all accounts return rate-limit errors and none have a cleared reset window, the orchestrator should sleep until the earliest reset time + 5 min rather than spinning.

## Related Requirements

- REQ-PROC-041-02 (Session Lifecycle): Provides session ID assignment and termination script
- REQ-PROC-041-03 (Automated Mode): Provides `CLAUDE_AUTOMATED_MODE` flag and CLAUDE.md rules
- REQ-PROC-041-04 (Feedback Pause & Resume): Provides `pending_feedback/` structure and resume protocol

## References

- Epic: `requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/requirements.md`
- Test confirmed: `claude --dangerously-skip-permissions --session-id <uuid> -p "..."` exits code 0 with response in stdout
- Test confirmed: `CLAUDE_CONFIG_DIR=/home/vscode/.ccs/instances/web claude ...` stores session under web instance
- Test confirmed: `claude --resume <uuid> -p "..."` with matching `CLAUDE_CONFIG_DIR` resumes correct session
- CCS account instances: `~/.ccs/instances/{gmail,web,gmail2}/`
