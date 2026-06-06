# Integration Test Findings

## Overall Result: PASS (after fixes)

All test scenarios passed across two orchestrator runs (3 iterations total).

---

## Pass/Fail per Test Scenario

| # | Scenario | Status | Evidence |
|---|----------|--------|----------|
| 1 | Session A starts and exits cleanly | PASS | Session `32f5279b` exited 0; report: "Done. TASK-TEST-001-01 completed and committed." |
| 2 | Session B starts and exits cleanly | PASS | Session `e9ad0603` exited 0; task renamed and committed (`3f70eba9`). |
| 3 | dummy_a.txt exists with content `DUMMY_A_DONE` | PASS | `automation/test_outputs/dummy_a.txt` contains exactly `DUMMY_A_DONE`. |
| 4 | dummy_b.txt exists with content `DUMMY_B_DONE` | PASS | `automation/test_outputs/dummy_b.txt` contains exactly `DUMMY_B_DONE`. |
| 5 | Task C writes `pending_feedback/TASK-TEST-001-03/question.md` and exits without blocking | PASS | Session `ba95aeb0` wrote question.md and terminated via `terminate_session.sh` (exit 144). |
| 6 | question.md has non-empty session_id, account, asked_at | PASS | `session_id: ba95aeb0-...`, `account: gmail`, `asked_at: 2026-04-07T12:23:30Z`. |
| 7 | Report files exist with session entries | PASS | Two report files exist under `automation/reports/`; both list sessions with start/end/exit. |
| 8 | Session output files exist for all sessions | PASS | Five `.txt` files present under `automation/session_outputs/`, one per session. |

---

## Fixes Applied and Why

### Fix 1 — Remove gmail2 from accounts
**Why**: gmail2 is not authorized for Claude API access. It fails immediately with an auth error (exit 1), consuming a task slot and producing no work.
**Resolution**: Use only `gmail,web` accounts in all production invocations.

### Fix 2 — Inject CLAUDE_SESSION_ID / CLAUDE_SESSION_ACCOUNT in build_env
**Why**: `orchestrate.py` launched subprocesses without setting these environment variables. The feedback gate reads them to populate question.md frontmatter. Without them, `session_id` and `account` were empty strings, failing scenario 6.
**Fix location**: `scripts/automation/orchestrate.py` — `build_env(account, session_uuid)` now sets both vars.

### Fix 3 — Add `deprecated` to TERMINAL_STATUSES in next_tasks.py
**Why**: Deprecated tasks (e.g. TASK-FUNC-007-02) appeared in the work queue and consumed session slots.
**Fix location**: `scripts/next_tasks.py`.

### Fix 4 (pending) — Use `task-complete` skill instead of `complete_task.py` in automated sessions
**Why**: `scripts/complete_task.py` renames the task folder to `(completed)` but does not update the YAML `status:` field in `goal.md`. The `task-complete` skill does both. Tasks A and B were closed via the script, leaving `status: in_progress` in their frontmatter.
**Resolution**: Update goal.md templates for automated sessions to call the `task-complete` skill.

---

## Confirmed-Working Orchestrator Invocation

```bash
python3 scripts/automation/orchestrate.py \
  --accounts gmail,web \
  --max-tasks 3
```

Requires:
- `CLAUDE_AUTOMATED_MODE=1` environment variable set
- `automation/.automated_mode` file present
- Only authorized accounts listed in `--accounts`

---

## Known Limitations and Edge Cases

- **Rate limits are silent task failures**: When an account hits its rate limit, the session exits with code 1 and the task is not retried automatically. The orchestrator picks it up on the next run if not already marked complete.
- **Single-account fallback**: If one of two accounts is rate-limited, only one session runs per orchestrator invocation; fewer tasks complete per run than `--max-tasks` suggests.
- **`complete_task.py` leaves stale status field**: Automated sessions that close tasks via the script (not the skill) will have inconsistent `status:` in frontmatter even after the folder is renamed.
- **Feedback gate pauses indefinitely**: Once question.md is written, the task stays pending until a human responds and re-runs the orchestrator. There is no timeout or escalation mechanism.
- **Session output is summary-only**: `session_outputs/*.txt` captures only the Claude session's final printed output. Intermediate reasoning and verbose output are not captured; debugging failures relies on the report summary.
