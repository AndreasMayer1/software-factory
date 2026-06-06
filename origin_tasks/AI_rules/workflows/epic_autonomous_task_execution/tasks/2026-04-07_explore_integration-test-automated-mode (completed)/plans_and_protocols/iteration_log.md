# Integration Test Iteration Log

## Iteration 1 — First orchestrator run (2026-04-07 14:10–14:14)

**Accounts**: gmail, gmail2, web  
**Sessions**: 3 (2 completed, 1 failed)  
**Report**: `automation/reports/2026-04-07_14-14_report.md`

### What broke

**Bug 1: gmail2 account not authorized**  
Session 3 (TASK-TEST-001-03, gmail2) exited immediately with:  
> "Your organization does not have access to Claude. Please login again or contact your administrator."  
Exit code: 1. No task work was done.

### Fix applied

Removed `gmail2` from the accounts list. Subsequent runs use only `gmail,web`.

### Result

Sessions 1 (gmail) and 2 (web) completed cleanly:
- dummy_a.txt written with `DUMMY_A_DONE`
- dummy_b.txt written with `DUMMY_B_DONE`
- Both tasks renamed to `(completed)` and committed

Task C was not executed in this run.

---

## Iteration 2 — Second orchestrator run, retry #1 for task C (2026-04-07 ~14:20)

**Accounts**: gmail, web  
**Sessions**: 2 (1 completed, 1 hit rate limit)  
**Session ID**: `1668d0aa-c2dd-4cfb-95e6-c34c195cf703`

### What broke

**Bug 2: `build_env` missing CLAUDE_SESSION_ID / CLAUDE_SESSION_ACCOUNT**  
The orchestrator did not pass `CLAUDE_SESSION_ID` or `CLAUDE_SESSION_ACCOUNT` into the subprocess environment. When the session hit the feedback gate and wrote `question.md`, those fields were empty strings.

Additionally, the `web` account session hit a rate limit ("You've hit your limit · resets 4pm (Europe/Berlin)") and exited with code 1 before doing any work.

### Fix applied

`scripts/automation/orchestrate.py` — `build_env(account, session_uuid)` updated to inject both `CLAUDE_SESSION_ID` and `CLAUDE_SESSION_ACCOUNT` into the subprocess environment.

### Result

The gmail session wrote `question.md` but with empty `session_id` and `account` fields — **not yet correct**.

---

## Iteration 3 — Retry #2 for task C (2026-04-07 14:21–14:23)

**Accounts**: gmail, web  
**Sessions**: 2 (1 completed, 1 rate-limited)  
**Session ID**: `ba95aeb0-36af-4162-9d6a-7645dd782dd1`  
**Report**: `automation/reports/2026-04-07_14-23_report.md`

### What happened

The web account was still rate-limited (exit 1, no work). The gmail session ran TASK-TEST-001-03, hit the feedback gate, wrote `question.md` with correct frontmatter, and terminated cleanly via `terminate_session.sh` (exit 144).

### Result

question.md contains:
- `session_id: ba95aeb0-36af-4162-9d6a-7645dd782dd1` (non-empty)
- `account: gmail` (non-empty)
- `asked_at: 2026-04-07T12:23:30Z` (non-empty)
- Correct question body

**All test scenarios passed.**

---

## Additional bugs identified (not blocking the test, fixed separately)

**Bug 3: `complete_task.py` does not update YAML `status:` field**  
Sessions A and B used `python3 scripts/complete_task.py` to close tasks. This renames the folder to `(completed)` but leaves `status:` unchanged in `goal.md`. Sessions should use the `task-complete` skill instead. Fix: update goal.md instructions for automated sessions.

**Bug 4: `next_tasks.py` TERMINAL_STATUSES missing `deprecated`**  
Deprecated tasks (e.g. TASK-FUNC-007-02) appeared in the queue. Fix: `deprecated` added to `TERMINAL_STATUSES` in `scripts/next_tasks.py`.
