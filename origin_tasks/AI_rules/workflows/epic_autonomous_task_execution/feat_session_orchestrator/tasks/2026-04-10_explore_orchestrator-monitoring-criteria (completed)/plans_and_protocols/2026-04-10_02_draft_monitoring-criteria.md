# DRAFT: automation/MONITORING_CRITERIA.md

> This is the draft content for the monitoring criteria file.
> Once approved, write verbatim to `automation/MONITORING_CRITERIA.md`.

---

# Orchestrator Monitoring Criteria

Reference for the monitoring LLM (cron check every 15 min).
Read this file BEFORE analyzing `automation/orchestrate.log`.

## How to Use This File

1. Read the entire file to understand expected orchestrator behavior
2. Read `automation/orchestrate.log` (tail ~200 lines for recent activity)
3. For each log pattern, check against the scenarios below
4. Report anomalies using the severity levels defined here
5. Always report current progress (sessions launched, tasks completed)

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Orchestrator is wasting resources or stuck | Report immediately; suggest user intervention |
| **WARNING** | Potential issue, may self-resolve | Report; flag for user review |
| **INFO** | Notable state change, not a problem | Include in progress summary |

## Scenario Reference

### Normal Operation

**Log pattern**:
```
[orchestrator] Launching session <uuid> with account <name>
```
Followed (after 1-60 min) by the next session launch.

**Expected**: Each session uses a unique UUID. Sessions complete with exit 0. Tasks progress (complete or write question.md).

**Check**: Are sessions making progress? Look for task completions or new question.md files in session output excerpts.

---

### Rate Limit — Single Account

**Log pattern**:
```
[orchestrator] Account <name> rate-limited until <datetime>, rotating to next account
```

**Severity**: INFO — always normal. Orchestrator continues with other accounts.

---

### Rate Limit — All Accounts

**Log pattern**:
```
[orchestrator] All accounts rate-limited. Waiting <N>s until <datetime>
```

**Severity**: INFO if wait ≤ 7200s (2 hours). **WARNING** if wait > 7200s — may indicate a reset-time parsing error.

**Check after wait**: Does a new session launch after the wait period? If not, report as WARNING.

---

### Permanent Access Error

**Log pattern**:
```
[orchestrator] Account <name> has no access — disabling for this run
```

**Severity**: WARNING for each disabled account. **CRITICAL** if all configured accounts are disabled (no sessions can run).

**Detection**: Count distinct "has no access — disabling" messages. Compare against the total number of accounts (default: 3).

---

### Unanswered Questions (Blocked Tasks)

**Log pattern**:
```
[orchestrator] Note: unanswered questions for <task_ids> — these tasks are skipped
```

**Severity**: INFO — normal behavior. But note: if the same "unanswered questions" message appears and the set of task IDs grows to 3+, report as **WARNING** ("user input backlog growing — orchestrator may run out of runnable tasks soon").

---

### In-Progress Session Resume

**Log pattern**:
```
[orchestrator] Resuming in-progress <task_id> (session <uuid>) with account <name>
```

**Severity**: INFO — normal. This means a previous session exited before completing the task.

**Anomaly check**: If the **same task_id** is resumed 3+ times within the same orchestrator run (count "Resuming in-progress <task_id>" messages for each task_id), report as **CRITICAL** — the task is stuck in a resume loop.

---

### Feedback Resume (Answered Question)

**Log pattern**:
```
[orchestrator] Resuming <task_id> with account <name>
```
(Note: no "in-progress" — this is the answered-feedback path, distinct from S4.)

**Severity**: INFO — always normal.

---

### Orchestrator Stop — Clean

**Log pattern**:
```
[orchestrator] Stopped. Reason: <reason>
```

Valid reasons: `manual`, `scheduled`, `max_tasks`, `all_tasks_awaiting_answer`.

**Severity**: INFO for all clean stops. If reason is `all_tasks_awaiting_answer`, also note that user input is needed.

**Action for monitoring cron**: When "Stopped. Reason:" is detected, cancel the monitoring cron job (CronDelete).

---

### Orchestrator Stop — Crash

**Detection**: The `.automated_mode` sentinel exists (contains a PID), but:
- The PID is not alive (`kill -0 <PID>` fails), AND
- The log does NOT end with "Stopped. Reason:"

**Severity**: **CRITICAL** — orchestrator crashed without cleanup.

**Action**: Report the crash. Note: the sentinel file must be manually cleaned up before restarting.

---

### Duplicate Task Work (Wasted Sessions)

**Detection**: In the session output excerpts within the log, look for the same TASK-ID appearing in 2+ separate non-resume session blocks. Specifically:

1. For each "Launching session" (normal, not resume), find the TASK-ID in the subsequent output
2. If the same TASK-ID appears in 2+ "Launching session" blocks (NOT "Resuming" blocks), this is a duplicate

**Severity**: **CRITICAL** — sessions are being wasted on the same task.

**Common cause**: The "Do next task" routing is not properly filtering blocked/in-progress tasks. This was the pattern on 2026-04-10 (sessions 4 & 5 re-encountering TASK-FUNC-007-14).

---

### No Progress

**Detection**: Over 3+ consecutive sessions (all exit 0):
- No task completions visible in output
- No new question.md files written
- No commit messages in output

**Severity**: **WARNING** after 3 sessions without progress. **CRITICAL** after 5 sessions without progress.

---

### Generic Session Failure

**Log pattern**:
```
[orchestrator] WARNING: resume of <task_id> (session <uuid>) failed with exit <code> — skipping for this run
```

**Severity**: WARNING — single occurrence is normal (transient error). **CRITICAL** if 3+ generic failures occur in the same run — indicates a systemic problem.

---

## Quick Anomaly Checklist

For the monitoring LLM — check these in order:

1. **Is the orchestrator still running?** Check for "Stopped. Reason:" at end of log. If stopped, cancel cron and report final status.
2. **Any CRITICAL patterns?**
   - All accounts disabled?
   - Same task in 2+ non-resume sessions?
   - Same task resumed 3+ times?
   - 5+ sessions without progress?
   - Crash (sentinel exists, PID dead, no clean stop)?
3. **Any WARNING patterns?**
   - Wait time > 2 hours?
   - 3+ blocked tasks accumulating?
   - 3+ sessions without progress?
   - 3+ generic failures?
4. **Progress summary**: How many sessions since last check? Any tasks completed? Any new questions?

## Maintenance

This file should be updated when:
- New orchestrator features add new log patterns
- A new anomaly pattern is discovered in production
- Severity classifications need adjustment based on experience

Last updated: 2026-04-10 (initial version)
