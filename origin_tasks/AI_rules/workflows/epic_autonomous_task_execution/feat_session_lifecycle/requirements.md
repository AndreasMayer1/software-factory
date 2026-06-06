---
id: REQ-PROC-041-02
status: implemented
stakeholder: developer
created: 2026-04-06
updated: 2026-06-03
parent: REQ-PROC-041
after: [REQ-PROC-041-03]
blocks:
  - REQ-PROC-041-04
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
---

# Session Lifecycle

## Overview

Mechanisms that ensure automated Claude Code sessions terminate cleanly on both normal completion and feedback-gate events, plus reliable session identity tracking so paused sessions can be resumed later.

## Purpose

An automated session that never terminates blocks the orchestrator indefinitely. A session that terminates without recording its identity cannot be resumed. These two properties — clean termination and reliable identity — are the foundation on which the rest of the automated execution system depends.

## Scope

**Included:**
- Forcing auto-exit on task completion via the `-p`/`--print` flag
- Pre-assigning session UUIDs via `--session-id <uuid>` before launch
- Writing session metadata (UUID, account, timestamp) to the active task's goal.md before the session starts
- `scripts/automation/terminate_session.sh`: a shell script that exits the current Claude Code process cleanly when invoked during a session
- The `claude-route` skill writing session metadata to goal.md when starting a task in automated mode

**Excluded:**
- Scheduling or orchestration logic (REQ-PROC-041-01)
- Feedback content storage or resume command construction (REQ-PROC-041-04)
- Automated-mode detection or CLAUDE.md rules (REQ-PROC-041-03)

## Behavior

### Normal Completion

All automated sessions are launched with the `-p`/`--print` flag. This makes Claude Code output its response and exit. No explicit termination action is required for normal completion.

### Feedback-Gate Termination

When a feedback gate fires in automated mode, the AI executes `bash scripts/automation/terminate_session.sh` after writing the pending question (see REQ-PROC-041-04). The script exits the current Claude Code process, signaling to the orchestrator that the session has ended due to a pause rather than completion.

### No Self-Scheduling (Orchestrator Owns Timing)

Scheduling, rate-limit/reset timing, account rotation, and the decision of **when** a task runs or resumes belong exclusively to the orchestrator (REQ-PROC-041-01). A session has exactly four valid exits:

1. Complete the task (`task-complete`).
2. Write `question.md` for a genuine human decision, then terminate (REQ-PROC-041-04).
3. Re-emit a rate/session-limit line verbatim, then terminate (REQ-PROC-041-03 § rate-limit rule).
4. State in one line why it cannot make progress right now, then terminate.

A session MUST NOT call `ScheduleWakeup`, set a future wakeup, "wait out" a limit, or reason about reset clocks. If a session is resumed while a limit it depends on is still active — or it otherwise cannot advance — it takes exit (3) or (4); it does **not** defer itself. Self-scheduling makes the session second-guess the orchestrator's timing, produces no-op resumes the orchestrator counts as failed attempts, and leaves a session-local timer the orchestrator cannot honor once it moves on.

This rule was added after a session resumed early (before its subagents' limit reset) called `ScheduleWakeup` to defer itself; the orchestrator counted three such no-op resumes as exhausted attempts and abandoned the task for the run (TASK-FUNC-007-01-05).

### Session Identity

Before the orchestrator launches a CCS session, it:
1. Generates a UUID (`python3 -c "import uuid; print(uuid.uuid4())"`)
2. Writes `session_id: <uuid>` and `session_account: <account>` into the active task's goal.md frontmatter
3. Launches the session with `--session-id <uuid>`

The `claude-route` skill, when running in automated mode, also writes these fields to goal.md as part of marking the task `in_progress`.

Session storage is shared across accounts: the `projects/` folder inside each account instance is a symlink to `~/.ccs/shared/context-groups/default/projects`. Any account can resume any session — cross-account resume works correctly.

## Acceptance Criteria

- [ ] AC-01: All CCS sessions launched by the orchestrator include the `-p`/`--print` flag, causing automatic exit when the task prompt is handled
- [ ] AC-02: The orchestrator generates a UUID and passes it via `--session-id <uuid>` to each session before launch
- [ ] AC-03: `session_id` and `session_account` fields are present in the active task's goal.md frontmatter with values written before the session subprocess starts
- [ ] AC-04: `scripts/automation/terminate_session.sh` exists and, when executed inside a running Claude Code session, causes that session's process to exit with code 0
- [ ] AC-05: The `claude-route` skill writes `session_id` and `session_account` to goal.md when starting a task while `CLAUDE_AUTOMATED_MODE=1` is set
- [ ] AC-06: `session_completed_at` timestamp is written to goal.md when a session exits normally (process exit code 0 and no `pending_feedback` question written)
- [ ] AC-07: An automated session never schedules or defers itself (no `ScheduleWakeup`, no waiting out a limit, no reasoning about reset clocks); when it cannot advance it takes one of the four valid exits and terminates, leaving all scheduling and limit/reset timing to the orchestrator. The `claude-automated-mode` skill and the orchestrator's resume prompt both state this boundary explicitly.

## Developer Guidelines

### Key Decisions

- Pre-assignment (before launch) is the only reliable session ID mechanism. Post-hoc discovery via the newest folder under `~/.ccs/instances/<account>/projects/` is unreliable because multiple sessions or a manual `/clear` command can create newer folders that do not correspond to the current automated session.
- `terminate_session.sh` must kill the process cleanly, not forcefully (prefer `kill -TERM` over `kill -9`). Claude Code handles SIGTERM gracefully and flushes writes before exiting.
- The script must target only the specific Claude Code process for the current session, not all Claude processes. Use the process group or PID file strategy — do not use `pkill claude` as it would kill unrelated manual sessions.

### Common Pitfalls

- Omitting `-p`: A session started without `--print` stays open indefinitely, blocking the orchestrator. `-p` is mandatory for all automated sessions.
- Resume with wrong account: ~~not a pitfall~~ — session storage is shared via symlinks, so any account can resume any session. The orchestrator exploits this to switch to a working account when the original is rate-limited or has no access.
- Not writing session metadata before launch: If the orchestrator crashes between writing metadata and launch, the goal.md fields will reference a session that was never started. This is acceptable — on restart, the orchestrator re-reads goal.md and detects the stale session.

## Related Requirements

- REQ-PROC-041-01 (Session Orchestrator): Consumes session identity fields written by this feature
- REQ-PROC-041-03 (Automated Mode): Provides the CLAUDE.md rule that triggers `terminate_session.sh`
- REQ-PROC-041-04 (Feedback Pause & Resume): Writes `question.md` before `terminate_session.sh` is called

## References

- Epic: `requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/requirements.md`
- Claude CLI flags: `claude --help` — `--session-id`, `--resume`, `-p`/`--print`
- CCS instance storage: `~/.ccs/instances/<account>/projects/<project>/`
