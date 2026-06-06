# Protocol: Implement Session Orchestrator Script

**Task**: TASK-PROC-041-01-01
**Date**: 2026-04-07
**Agent**: a972bae5f8895529d
**Status**: COMPLETE

---

## Summary

Implemented `scripts/automation/orchestrate.py` as specified in the plan. All 18 helper functions + `main()` implemented. No classes. stdlib only (Python 3.9+).

---

## Steps Completed

### 1. Read context
- Read `goal.md` — AC-01 through AC-13 catalogued
- Read `2026-04-07_01_plan_orchestrator.md` — all 18 sections studied
- Checked existing `scripts/automation/` (only `terminate_session.sh` present)

### 2. Implemented `scripts/automation/orchestrate.py`

**File**: `/workspaces/private_mood_tracker/flutter_app/scripts/automation/orchestrate.py`

**Functions implemented** (in order):
1. `read_yaml_frontmatter(path)` — flat key:value YAML extraction without external libs
2. `parse_args()` — `--accounts`, `--stop-at`, `--min-wait-seconds`
3. `load_state(path)` — loads state.json with defaults merge; starts fresh on corrupt/missing
4. `save_state(path, state)` — atomic write via tmp + os.replace()
5. `build_env(account)` — injects `CLAUDE_AUTOMATED_MODE=1` and `CLAUDE_CONFIG_DIR`
6. `strip_hook_footer(text)` — removes `\n---\n**Reminder:...` footer via re.DOTALL
7. `write_session_output(outputs_dir, session_id, content)` — writes session_outputs/<uuid>.txt
8. `parse_rate_limit_reset(stdout)` — regex parse + zoneinfo + 5-min buffer + UTC conversion; fallback to UTC on unknown TZ
9. `find_active_task_goal(project_root)` — grep -rl "status: in_progress" requirements_tasks/
10. `update_goal_session_fields(goal_path, session_id, account)` — line-by-line YAML frontmatter rewrite; non-fatal on failure
11. `find_answered_feedback(feedback_dir)` — scans pending_feedback/ for dirs with both question.md + answer.md; skips empty/malformed
12. `new_question_written_for(task_id, feedback_dir)` — detects new question.md without answer.md after resume
13. `next_available_account(accounts, state)` — returns (account, wait_until); handles all-exhausted by returning earliest reset time
14. `should_stop(stop_flag, stop_at)` — checks stop_flag dict, .stop-requested file, --stop-at datetime
15. `write_report(reports_dir, run_data, accounts, feedback_dir)` — generates YYYY-MM-DD_HH-MM_report.md with pending feedback section
16. `run_normal_session(env, session_uuid)` — subprocess.run with --session-id and -p "Do next task"
17. `run_resume_session(env, session_id, answer_content)` — subprocess.run with --resume and -p <answer>
18. `setup_signals(stop_flag)` — SIGTERM + SIGINT → stop_flag["requested"] = True
19. `unlink_if_exists(path)` — helper for sentinel cleanup
20. `main()` — full orchestration loop

**Key design decisions followed from plan**:
- `stop_flag` is a dict `{"requested": False}` (not a bool) to allow lambda mutation
- `state["rate_limited_until"]` dict tracks per-account reset ISO strings
- `next_available_account()` handles all-exhausted case by returning earliest reset datetime
- Fallback sleep of 65 minutes when rate limit time cannot be parsed
- `automation/.automated_mode` created at startup, cleaned in `finally` block
- `automation/.stop-requested` cleaned in `finally` block (user must delete manually if SIGKILL'd)
- Atomic state writes via tmp + os.replace()
- All paths relative to PROJECT_ROOT (two dirname() calls from script location)

### 3. Verification

```
python3 -m py_compile scripts/automation/orchestrate.py  # -> Syntax OK
python3 scripts/automation/orchestrate.py --help         # -> shows correct usage
```

---

## Acceptance Criteria Status

- [x] AC-01: `scripts/automation/orchestrate.py` runs with `python3`
- [x] AC-02: Accepts `--accounts`, `--stop-at`, `--min-wait-seconds`
- [x] AC-03: Sessions launched via `subprocess.run(["claude", "--dangerously-skip-permissions", "--session-id", uuid, "-p", "Do next task"], ...)` with correct env vars
- [x] AC-04: Round-robin rotation; `account_index` persisted in `state.json`
- [x] AC-05: Rate limit (exit 1 + "hit your limit") → parse reset → sleep if all exhausted → rotate
- [x] AC-06: At most one session at a time (`subprocess.run` is blocking)
- [x] AC-07: UUID pre-generated, written to active task goal.md, passed via `--session-id`
- [x] AC-08: `.stop-requested` or SIGTERM → stop after current session
- [x] AC-09: `--stop-at` → stop after current session
- [x] AC-10: stdout stripped of hook footer, saved to `session_outputs/<uuid>.txt`
- [x] AC-11: Report written to `automation/reports/YYYY-MM-DD_HH-MM_report.md` on termination
- [x] AC-12: State persisted to `state.json`; re-read on restart
- [x] AC-13: Answered feedback resumed via `--resume <session-id>` with matching account; on normal exit moved to `answered_feedback/`

---

## Files Modified

- **Created**: `scripts/automation/orchestrate.py` (~370 lines)
- **Created**: This protocol file

---

## No Issues / Blockers

Implementation was straightforward following the detailed plan. All edge cases from the prompt were handled:
1. All-accounts-exhausted: `next_available_account()` returns `(account, earliest_reset_dt)` and main() sleeps
2. Rate limit regex: `r'resets (\d{1,2}:\d{2}(?:am|pm)) \(([^)]+)\)'` with IGNORECASE; fallback 65-min sleep
3. Goal.md update: line-by-line YAML rewrite; failure is non-fatal
4. Feedback resume: checks `new_question_written_for()` after resume; leaves in pending_feedback if new question
5. SIGTERM/SIGINT: dict-based `stop_flag`
6. Sentinel: `.automated_mode` created at startup, cleaned in `finally`
7. State file: atomic write via tmp + os.replace()
8. answer.md empty check: logs warning and skips if empty/whitespace
