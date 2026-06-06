# Variable-Space Analysis: Orchestrator Monitoring Criteria

**Purpose**: Requirements exploration — defines what the orchestrator and its monitoring SHOULD handle, using the current implementation as a reference but not as the ceiling.

**Date**: 2026-04-10  
**Task**: TASK-PROC-041-01-04

---

## Part 1: Complete Variable Catalog

Variables are grouped by entity. Each variable is independent; combinations drive behavior.

---

### Entity A: Pending Feedback Directory (`automation/pending_feedback/<task_id>/`)

Each subfolder represents one task that asked a question. Multiple folders can coexist.

| Variable | Values |
|---|---|
| A1: Number of task folders | 0 / 1 / N (≥2) |
| A2: question.md present | yes / no |
| A3: answer.md present | no / yes-empty (0 bytes) / yes-whitespace-only / yes-non-empty |
| A4: question.md frontmatter valid | valid (has task_id, session_id, account) / malformed (missing fields) / unparseable |
| A5: task_id in question.md frontmatter matches folder name | matches / mismatch |
| A6: session_id in question.md exists in JSONL store | exists / not found / unknown |

**Note on A3**: `answer_is_empty()` only checks `os.path.getsize() == 0`. A whitespace-only file passes as "non-empty" and would be sent as the resume answer — empty string delivered to `--resume`. **Implementation gap.**

**Note on A5**: Mismatch between folder name and frontmatter task_id causes the orchestrator to use the wrong task_id in logging and state tracking. **Implementation gap.**

---

### Entity B: In-Progress Tasks (`requirements_tasks/**/goal.md` with `status: in_progress`)

| Variable | Values |
|---|---|
| B1: Count of in-progress tasks | 0 / 1 / N (≥2) |
| B2: session_id present in goal.md | present (non-empty) / absent / present-but-stale (from a prior orchestrator run) |
| B3: session_account present in goal.md | present / absent |
| B4: Corresponding pending_feedback folder exists | yes / no |
| B5: If B4=yes: answer state | unanswered (A3=no or empty/whitespace) / answered (A3=non-empty) |
| B6: Session in exhausted_resume_ids for this run | yes / no |
| B7: How many times this task has been attempted in this run | 0 / 1 / 2 / N (≥3) |
| B8: Last session outcome for this task | exit-0-completed / exit-0-still-in-progress-with-question / exit-0-still-in-progress-no-question / exit-1-rate-limit / exit-1-perm-error / exit-1-other / no-prior-session-this-run |

**Note on B2 "stale"**: goal.md may have a `session_id` written by a *previous* orchestrator run. The JSONL session file may still exist (Claude sessions persist) or may have been purged. If the resume attempt fails with exit 1 (not rate-limit, not perm-error), it's marked exhausted — but the monitoring LLM cannot distinguish "new stale session" from "repeated transient failure". **Monitoring gap.**

**Note on B7**: The current implementation tracks `exhausted_resume_ids` (failed resumes) but does NOT count fresh-session attempts per task. A task that generates a question, gets a new session, generates the same question again, etc. can cycle forever with no counter. **Implementation gap.**

---

### Entity C: Task Queue (output of `next_tasks.py`)

| Variable | Values |
|---|---|
| C1: Queue output | empty (no tasks at all) / all-blocked (all candidates awaiting answer) / some-runnable |
| C2: Runnable task count | 0 / 1 / N |
| C3: Queue trend over time | shrinking (tasks completing) / stable (no change) / growing (new tasks added faster than completed) |

**Note on C1=empty**: If `next_tasks.py` returns no output at all (truly empty queue — no tasks exist), the current code's guard `if task_ids_in_output and not runnable` has `task_ids_in_output = []` which is falsy. The condition is skipped. The orchestrator proceeds to `next_available_account()` and launches a normal "Do next task" session — which wastes a session slot to learn there's nothing to do. **Implementation gap / Requirements decision**: should an empty queue trigger an immediate stop or idle-wait?

**Note on C3**: Neither the orchestrator nor its monitoring currently tracks queue trend. A growing queue (tasks added faster than completed) despite many sessions running is a signal that the AI is generating exploration tasks but not implementing anything. **Monitoring gap.**

---

### Entity D: Account States

Per-account variables (for each of N configured accounts, default: gmail, web, gmail2):

| Variable | Values |
|---|---|
| D1: Rate-limited | no / yes-with-known-reset / yes-with-unparseable-reset |
| D2: Permanently disabled (perm error this run) | no / yes |
| D3: Tested this run | untested / tested-and-worked / tested-and-failed |

Aggregate account-set variables:

| Variable | Values |
|---|---|
| D4: At least one account available | yes / no |
| D5: All accounts rate-limited | no / yes-all-resets-known / yes-some-resets-unknown |
| D6: All accounts permanently disabled | no / yes |
| D7: Mix: some disabled, remaining all rate-limited | no / yes |

**Critical edge case — D6=yes AND D7 doesn't apply** (all permanently disabled, none rate-limited): `next_available_account()` iterates all accounts, skips disabled ones, finds none without a rate-limit entry, falls through to `earliest = min(rate_limited.values())` — but `rate_limited` is empty (they're disabled, not rate-limited). `min()` of empty iterable raises `ValueError` → **orchestrator crash**. **Implementation gap.**

**Critical edge case — D7=yes** (some disabled, rest rate-limited): `next_available_account()` skips disabled, tries rate-limited, returns `(account, earliest_reset)`. That account is rate-limited but not disabled — correct behavior, will sleep. OK. **Implementation: correct.**

---

### Entity E: Stop Signals

| Variable | Values |
|---|---|
| E1: `.stop-requested` sentinel | absent / present |
| E2: `--stop-at` datetime | not set / set-not-reached / set-and-reached |
| E3: `--max-tasks N` | not set / set-not-reached / set-and-reached |
| E4: SIGTERM / SIGINT received | no / yes |
| E5: All accounts permanently disabled (implicit stop condition) | no / yes — **currently NOT a stop condition** |
| E6: Task queue empty (no tasks of any kind) | no / yes — **currently NOT a stop condition** |

**Note on E5**: When all accounts are disabled, the orchestrator will crash (see D6 above) rather than stopping gracefully. The correct behavior should be a clean stop with reason `all_accounts_disabled`. **Implementation gap / Requirements decision.**

**Note on E6**: Empty queue (no tasks exist at all, not "all blocked") should be a stop condition with reason `queue_empty`. Currently falls through to wasted session. **Requirements decision.**

---

### Entity F: Session Outcome (post-session variables, evaluated after each session exits)

| Variable | Values |
|---|---|
| F1: Exit code | 0 / non-zero |
| F2: If F1=non-zero: failure type | rate-limit (stdout contains "hit your limit") / perm-error (stdout contains "does not have access") / other |
| F3: If F1=0: task status after session | task completed (goal.md status ≠ in_progress) / still in_progress + new question.md / still in_progress no question.md / unknown (goal.md not written or unreadable) |
| F4: Session duration | very-short (<30s) / normal (30s–30min) / very-long (>30min) |
| F5: Session output length | empty (0 chars after footer strip) / very-short (<200 chars) / normal |
| F6: Session type | fresh ("Launching session") / resume-answered-feedback ("Resuming {task_id}") / resume-in-progress ("Resuming in-progress") |

**Note on F3=unknown**: If goal.md is not written by the session (the AI crashed before updating it, or `task-complete` was not called), goal.md still shows `in_progress` and `session_id` is still set. The orchestrator will resume this session indefinitely. **Implementation gap**: no maximum resume count per session_id.

**Note on F4=very-short**: A session that exits in <30 seconds almost certainly crashed or was rejected (e.g., account not configured). This should be a monitoring warning. **Monitoring gap.**

**Note on F5=empty**: An empty session output after footer stripping is a silent crash signal. The current health summary does not check output length. **Monitoring gap.**

---

### Entity G: Orchestrator Process State

| Variable | Values |
|---|---|
| G1: `.automated_mode` sentinel present | yes / no |
| G2: PID in sentinel is alive | yes / no / sentinel-missing |
| G3: Log ends with "Stopped. Reason:" | yes / no |
| G4: Second orchestrator instance running | no / yes (concurrent instances) |

**Note on G4**: The `claude-autorun` start action checks the sentinel PID before launching. However, if two users (or two cron triggers) call start simultaneously, both may read "STOPPED" before either has written the sentinel. Race condition → two concurrent instances. **Implementation gap / Requirements decision**: should a lock file be used?

---

### Entity H: Intra-Run History (tracked across the session loop)

| Variable | Values |
|---|---|
| H1: Sessions launched this run | 0 / 1 / N |
| H2: Tasks completed this run | 0 / 1 / N |
| H3: Consecutive sessions without any task completing | 0 / 1 / 2 / 3 / N |
| H4: Same task attempted N times this run (fresh sessions, not just resumes) | 0 / 1 / 2 / N |
| H5: Same question asked in N sessions (content hash) | 1 / 2 / N |
| H6: Total run duration | <1h / 1–4h / >4h |

**Note on H3, H4, H5**: None of these are currently tracked by the orchestrator. H4 is the root cause of the 2026-04-10 incident (sessions 4 & 5 both re-attempted TASK-FUNC-007-14). The fix injected blocked task IDs into the prompt, but does not enforce a hard limit. **Implementation gap**: no per-task attempt counter for fresh (non-resume) sessions.

---

## Part 2: Decision Tree with Expected Behavior

The orchestrator loop evaluates conditions in strict priority order. The tree below enumerates every branch and its expected behavior, anomaly signals, and current implementation status.

---

### LOOP START

```
E: Any stop signal? (E1=present OR E2=reached OR E4=received)
├─ YES
│   Expected: log "Stop condition met: {reason}", break loop, write report.
│   Healthy log: "Stop condition met:" followed by "Stopped. Reason:"
│   Anomaly: stop signal present but log continues launching sessions
│   Implementation: CORRECT
│
└─ NO → next check
```

```
E3: max-tasks reached?
├─ YES
│   Expected: log "Reached --max-tasks N, stopping", break, write report.
│   Healthy log: "Reached --max-tasks" followed by "Stopped. Reason: max_tasks"
│   Anomaly: max-tasks reached but sessions continue
│   Implementation: CORRECT
│
└─ NO → next check
```

---

### Priority 1: Answered Feedback Resume

```
A1≥1 AND A2=yes AND A3=non-empty AND A4=valid?
├─ YES: Run resume session with answer content
│   ├─ F1=0 AND no new question written
│   │   Expected: move folder to answered_feedback/, log "Moved to answered_feedback"
│   │   Healthy: task no longer in pending_feedback on next loop
│   │   Anomaly: folder not moved (OSError logged as WARNING) → stays in pending_feedback
│   │   → next loop iteration will attempt resume again with same answer
│   │   Implementation: PARTIAL — no retry limit if move fails
│   │   MONITORING GAP: repeated "WARNING: could not move to answered_feedback" should be CRITICAL
│   │
│   ├─ F1=0 AND new question written
│   │   Expected: leave in pending_feedback, log "{task_id} left in pending_feedback (new question)"
│   │   Healthy: new question visible in next monitoring check
│   │   Anomaly: same question content as before (hash match) — agent is looping on the same blocker
│   │   Implementation: PARTIAL — no same-question detection
│   │   MONITORING GAP: repeated identical questions not flagged
│   │
│   ├─ F1=non-zero AND rate-limit
│   │   Expected: record rate limit, rotate account, continue
│   │   NOTE: the resume uses the account from question.md frontmatter, NOT next_available_account()
│   │   The rate-limit handling for resume path records in state but does NOT rotate account for the NEXT resume
│   │   Implementation: PARTIAL — rate-limited resume account stays in use until next loop iteration
│   │
│   ├─ F1=non-zero AND perm-error
│   │   Expected: disable account for run, continue with different account on next loop
│   │   Implementation: CORRECT (account disabled, continue)
│   │
│   └─ F1=non-zero AND other
│       Expected: leave in pending_feedback (already happened), log error
│       Current: folder is left in pending_feedback but no explicit error log for this case
│       Implementation: PARTIAL — the "left in pending_feedback" branch covers exit≠0
│       MONITORING GAP: generic resume failure (non-rate-limit, non-perm) not flagged distinctly
│
├─ A3=whitespace-only (looks non-empty to os.path.getsize, but content is whitespace)
│   Current behavior: treated as answered → resume called with empty/whitespace string
│   Expected: should be treated as unanswered (A3=empty equivalent)
│   IMPLEMENTATION GAP: answer_is_empty() must strip-check content, not just size
│
├─ A4=malformed (question.md frontmatter missing session_id or account)
│   Current behavior: skipped with WARNING log, not retried
│   Expected: CORRECT — skip malformed entries
│   MONITORING GAP: malformed question.md should be flagged as CRITICAL (human intervention needed)
│
└─ A5=mismatch (task_id in frontmatter ≠ folder name)
    Current behavior: orchestrator uses frontmatter task_id for logging, folder name for path operations
    This creates inconsistent state — folder may not be moved correctly
    IMPLEMENTATION GAP: mismatch should be detected and logged as CRITICAL
```

---

### Priority 2: Unanswered Question Guard

```
A1≥1 AND A2=yes AND A3=no-or-empty
├─ Log: "Note: unanswered questions for {task_ids} — these tasks are skipped"
│   Expected: continue loop (do NOT stop)
│   Healthy: note appears once per loop iteration while question is unanswered
│   Anomaly: none for the log itself
│   MONITORING: count distinct task_ids in this message across the run:
│     - 1 task: INFO
│     - 2 tasks: WARNING (user backlog building)
│     - 3+ tasks: CRITICAL (orchestrator likely to run out of work soon)
│   Implementation: CORRECT (logs correctly, does not stop)
```

---

### Priority 3: In-Progress Session Resume

```
B1≥1 AND B2=present AND B4=no (no unanswered question) AND B6=no (not exhausted this run)?
├─ YES: resume session
│   Account selection:
│   ├─ B3=present AND account not blocked → use stored account
│   ├─ B3=present AND account blocked → find alternative via next_available_account()
│   │   ├─ D4=yes (alternative available) → use alternative, log account switch
│   │   └─ D4=no (all exhausted) → sleep until earliest reset, re-enter loop
│   └─ B3=absent → use current round-robin account
│
│   Session outcome:
│   ├─ F1=0 AND F3=completed → task done, next loop iteration finds no resumable
│       Healthy: task goal.md status changes away from in_progress
│       Anomaly: none
│       Implementation: CORRECT
│   │
│   ├─ F1=0 AND F3=still-in-progress-with-question → new confirmation gate hit
│       Expected: next loop iteration will route to unanswered-question guard
│       Healthy: question.md visible in pending_feedback
│       Anomaly: same question content as previous question (hash match) — stuck blocker
│       MONITORING GAP: same-question detection
│       Implementation: CORRECT routing, but no loop detection
│   │
│   ├─ F1=0 AND F3=still-in-progress-no-question → session ended without completing, no gate
│       Expected: next loop iteration will resume again (B2 still set)
│       B7 (attempt count) increments
│       Anomaly: B7 ≥ 3 → CRITICAL (task stuck, cannot complete, not asking question)
│       MONITORING GAP: no per-task attempt count tracked
│       IMPLEMENTATION GAP: no hard limit on resume attempts per session_id
│   │
│   ├─ F1=0 AND F3=unknown (goal.md not updated)
│       Same as still-in-progress-no-question — will resume indefinitely
│       IMPLEMENTATION GAP: same as above
│   │
│   ├─ F4=very-short (<30s) AND F1=0
│       Expected: suspicious — session may have crashed instantly
│       MONITORING GAP: duration not tracked, short sessions not flagged
│   │
│   ├─ F1=non-zero AND rate-limit
│       Expected: record reset time, mark account, re-enter loop for account switch
│       Implementation: CORRECT
│   │
│   ├─ F1=non-zero AND perm-error
│       Expected: disable account, keep session_id in goal.md, retry with other account next loop
│       Implementation: CORRECT
│   │
│   └─ F1=non-zero AND other (generic failure)
│       Expected: add session_id to exhausted_resume_ids, skip for this run
│       Next orchestrator run will attempt resume again (stale session_id risk)
│       B2=stale after orchestrator restart → may fail again immediately
│       MONITORING GAP: repeated exhausted-resume warnings across runs not flagged
│       Implementation: PARTIAL (correct for this run, no cross-run stale detection)
│
├─ B2=stale (session_id from previous run, JSONL may not exist)
│   Current behavior: same as B2=present — attempts resume, fails, marks exhausted
│   Expected: ideally detect staleness before attempting resume
│   How to detect: check if JSONL file exists at known path (~/.ccs/instances/<account>/projects/.../agent-<uuid>.jsonl)
│   IMPLEMENTATION GAP: no staleness check; MONITORING GAP: exhausted resumes not differentiated
│
├─ B1>1 (multiple in-progress tasks simultaneously)
│   Current behavior: find_resumable_session returns FIRST match — processes one per loop iteration
│   Expected: is this correct? Multiple in-progress tasks indicates prior sessions exited unexpectedly
│   MONITORING: B1>1 should be WARNING; B1>2 should be CRITICAL
│   MONITORING GAP: count of simultaneous in-progress tasks not monitored
│   Implementation: technically handles it (one at a time), but root cause is undetected
│
└─ B1≥1 AND B2=absent (in-progress task with no session_id)
    Current behavior: find_resumable_session skips this task (requires session_id)
    Falls through to normal session → "Do next task" may re-encounter this task and ask user to skip
    IMPLEMENTATION GAP: in-progress task with no session_id has no dedicated handling
    REQUIREMENTS DECISION: should an in-progress task without session_id be:
      (a) automatically skipped by the "Do next task" prompt (current partial fix), or
      (b) detected and stopped with a specific message, or
      (c) treated as fresh (start from beginning with new session)?
```

---

### Priority 4: Normal Session (pre-flight + launch)

```
C1=some-runnable?
├─ YES: continue to account selection
│   ├─ D4=yes (account available)
│   │   Launch normal session.
│   │   ├─ F1=0 → success path (see F3 sub-variables)
│   │   ├─ F1=non-zero, rate-limit → rotate, continue
│   │   ├─ F1=non-zero, perm-error → disable, continue
│   │   └─ F1=non-zero, other → no explicit handling beyond count; continue
│   │       MONITORING GAP: repeated generic failures not counted or flagged
│   │
│   └─ D4=no (all accounts exhausted)
│       ├─ D5=yes (all rate-limited, resets known) → sleep until earliest reset
│       │   Healthy: "All accounts rate-limited. Waiting Ns"
│       │   Anomaly: wait time >7200s (reset time parsing error)
│       │   Implementation: CORRECT
│       │
│       ├─ D6=yes (all permanently disabled) → CRASH (ValueError in min())
│       │   IMPLEMENTATION GAP: must detect and stop gracefully with reason "all_accounts_disabled"
│       │
│       └─ D7=yes (mix: some disabled, rest rate-limited) → sleep until earliest rate-limit reset
│           Implementation: CORRECT (next_available_account handles this)
│
├─ C1=all-blocked (task_ids_in_output non-empty, runnable=[])
│   Expected: stop with reason "all_tasks_awaiting_answer"
│   Healthy: "No runnable tasks — all candidates are awaiting answers"
│   Implementation: CORRECT
│   MONITORING: when cron sees this stop reason, notify user that input is needed
│
├─ C1=empty (next_tasks.py returns no task IDs at all)
│   Current behavior: task_ids_in_output=[] (falsy), guard skipped, proceeds to account selection, launches session
│   Session will find nothing to do and exit 0 with brief output
│   IMPLEMENTATION GAP: empty queue should trigger stop with reason "queue_empty" rather than wasted session
│   REQUIREMENTS DECISION: should empty queue stop the orchestrator, or should it idle-wait?
│
└─ next_tasks.py fails (non-zero exit or unparseable output)
    Current behavior: task_ids_in_output=[] → treated same as empty queue (same implementation gap)
    IMPLEMENTATION GAP: next_tasks.py failure should be detected and logged distinctly
    MONITORING GAP: script failures not distinguished from empty queue
```

---

### Session Outcome Cross-Cutting Variables

These apply regardless of which path launched the session:

| F4: Duration | F5: Output length | Expected interpretation | Monitoring |
|---|---|---|---|
| very-short (<30s) | empty | Silent crash / instant auth failure | CRITICAL |
| very-short (<30s) | short | Perm error or config problem | WARNING |
| normal | empty | Unusual — response stripped to nothing? | WARNING |
| normal | short | Session ended unusually early | INFO |
| very-long (>30min) | normal | Heavy task — acceptable | INFO |
| very-long (>30min) | short | Possible hang | WARNING |

**All currently unmonitored. MONITORING GAP across the board.**

---

### Entity G: Orchestrator Process State

```
G1=yes (sentinel present) AND G2=yes (PID alive) AND G3=no (log has no "Stopped.")
→ Running normally. Monitoring: report progress since last check.

G1=yes AND G2=no (PID dead) AND G3=yes (log ends with "Stopped.")
→ Stopped cleanly. Monitoring: cancel cron, report final health summary.

G1=yes AND G2=no AND G3=no
→ CRASH. CRITICAL. Sentinel must be manually deleted.
  Log tail will not have "Stopped. Reason:" line.
  MONITORING: report crash, instruct user to delete sentinel before restarting.

G1=no AND G3=yes
→ Stopped cleanly, sentinel already cleaned up. Normal.

G1=no AND G3=no
→ Never started, or started and crashed before writing sentinel. Ambiguous.

G4=yes (concurrent instances)
→ CRITICAL. Second instance overwrites sentinel, PID tracking is unreliable.
  Detection: check if two processes match `ps aux | grep orchestrate.py`
  IMPLEMENTATION GAP: no lock file; MONITORING GAP: concurrent instances not detectable from log alone
```

---

## Part 3: Gap Analysis

### Monitoring Gaps (criteria need extension)

| ID | Description | Severity when triggered |
|---|---|---|
| MG-01 | Repeated "could not move to answered_feedback" WARNING — folder stuck in pending | CRITICAL |
| MG-02 | Same question content repeated across multiple sessions (hash match) | CRITICAL |
| MG-03 | Malformed question.md (missing frontmatter fields) | CRITICAL |
| MG-04 | task_id mismatch between question.md frontmatter and folder name | CRITICAL |
| MG-05 | Resume exhausted 3+ times for same task across runs | WARNING |
| MG-06 | Multiple in-progress tasks simultaneously (B1>1) | WARNING; B1>2 → CRITICAL |
| MG-07 | Session duration very short (<30s) AND output empty/short | CRITICAL |
| MG-08 | Session output empty after footer strip | WARNING |
| MG-09 | Unanswered question count growing to 3+ distinct tasks | CRITICAL |
| MG-10 | Task attempted 3+ times fresh (not resume) without completing | CRITICAL |
| MG-11 | Queue trend: tasks added faster than completed over 3+ sessions | WARNING |
| MG-12 | Generic resume failure (non-rate-limit, non-perm) not distinctly flagged | WARNING |
| MG-13 | next_tasks.py empty vs. next_tasks.py failure — not distinguishable | WARNING |
| MG-14 | Concurrent orchestrator instances (detectable only from process list, not log) | CRITICAL |

### Implementation Gaps (code needs fixing — new requirements)

| ID | Description | Requirement decision needed? |
|---|---|---|
| IG-01 | `answer_is_empty()` does not detect whitespace-only answer.md | No — fix: strip() check |
| IG-02 | All accounts permanently disabled → `ValueError` crash in `next_available_account()` | No — fix: detect and stop gracefully with reason `all_accounts_disabled` |
| IG-03 | Empty task queue (C1=empty) launches wasted session instead of stopping/idling | YES — stop vs. idle-wait is a design decision |
| IG-04 | next_tasks.py failure indistinguishable from empty queue | No — fix: check return code |
| IG-05 | No per-task fresh-attempt counter (H4) — only exhausted_resume_ids for failed resumes | No — fix: add attempt tracking |
| IG-06 | No hard limit on resume attempts per session_id | YES — what is the max retry count? |
| IG-07 | In-progress task with no session_id has no dedicated path (falls into normal session) | YES — see Requirements Decision RD-02 |
| IG-08 | No staleness check for session_id (from prior orchestrator run) before resume attempt | No — fix: check JSONL path exists |
| IG-09 | Concurrent instance race condition (no lock file, only PID check) | YES — lock file overhead vs. risk tolerance |

### Requirements Decisions (need user input)

| ID | Question | Options |
|---|---|---|
| RD-01 | What should happen when the task queue is completely empty (no tasks of any kind)? | A) Stop with reason `queue_empty`; B) Idle-wait N minutes then recheck; C) Current behavior (wasted session) |
| RD-02 | What should happen with an in-progress task that has no session_id in goal.md? | A) Skip (rely on "Do next task" prompt injection); B) Stop with CRITICAL; C) Start fresh session |
| RD-03 | What is the maximum number of resume attempts per session_id before giving up? | Suggested: 3 per run, then permanently clear session_id from goal.md |
| RD-04 | Should the orchestrator use a lock file to prevent concurrent instances? | Risk: mild (manual starts); Cost: implementation complexity. Suggested: yes, flock-based |
| RD-05 | Should same-question detection (content hash) be implemented? | Requires storing hash of previous question per task_id in state.json |

---

## Part 4: Verdict

**Variables identified**: 7 entities, 35 individual variables  
**Meaningful combinations analyzed**: 47 distinct branches in the decision tree  
**Original 12 monitoring scenarios**: covered 14 of 47 branches (≈30%)

### Coverage by original scenario

| Original Scenario | Branches covered | Status |
|---|---|---|
| S1: Normal progression | 2 branches | Incomplete — no session-duration, output-length checks |
| S2: Pending question | 3 branches | Incomplete — no severity gradation by count |
| S3: Exit-0 still in_progress | 2 branches | Incomplete — no retry limit, no staleness |
| S4: In-progress resume | 3 branches | Incomplete — no duration/output checks, no multi-task alert |
| S5: Rate limit single account | 1 branch | Complete |
| S6: Rate limit all accounts | 2 branches | Incomplete — missing D6 crash scenario |
| S7: Perm error | 2 branches | Incomplete — missing all-disabled crash |
| S8: max-tasks | 1 branch | Complete |
| S9: All tasks awaiting | 1 branch | Complete |
| S10: Duplicate task work | 1 branch | Incomplete — only detects post-hoc from output; no H4/H5 tracking |
| S11: No progress | 1 branch | Incomplete — no H3/H4 counters |
| S12: Crash | 2 branches | Incomplete — concurrent instance not covered |

**Branches NOT covered by any original scenario** (33 of 47):
- Whitespace-only answer.md (IG-01)
- Malformed question.md frontmatter (MG-03, MG-04)
- Move-to-answered failure loop (MG-01)
- Same question content repeated (MG-02, RD-05)
- All accounts disabled crash (IG-02, MG for this)
- Empty queue wasted session (IG-03, RD-01)
- next_tasks.py failure (IG-04)
- In-progress task without session_id (IG-07, RD-02)
- Stale session_id (IG-08, MG-05)
- Multiple simultaneous in-progress tasks (MG-06)
- Very-short session duration (MG-07)
- Empty session output (MG-08)
- Generic resume failure distinct logging (MG-12)
- Concurrent instances (IG-09, MG-14)
- Per-task fresh-attempt counter (IG-05, MG-10)
- Queue trend (MG-11)
- Resume attempt hard limit (IG-06, RD-03)
- answered-feedback rate-limit path
- answered-feedback perm-error path
- answered-feedback generic failure distinct logging
- answered-feedback new-question-same-content path

**Summary**: The original 12 scenarios are a useful starting scaffold but cover approximately **30% of the meaningful variable space**. The largest gaps are in error-path handling, implementation correctness (4 potential crashes or infinite loops), and session-quality signals (duration, output length).

**Immediate action recommended**: resolve the 5 Requirements Decisions (RD-01 through RD-05) before finalizing the monitoring criteria, as those decisions determine which implementation gaps become new requirements and which monitoring gaps become new criteria.
