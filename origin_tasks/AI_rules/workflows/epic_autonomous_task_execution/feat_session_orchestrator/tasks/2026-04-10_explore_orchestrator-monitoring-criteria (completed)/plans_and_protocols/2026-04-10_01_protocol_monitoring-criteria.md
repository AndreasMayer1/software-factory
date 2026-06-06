# Protocol: Orchestrator Monitoring Criteria

## 1. Problem Statement

On 2026-04-10, the orchestrator ran 5 sessions. Sessions 4 and 5 both re-encountered TASK-FUNC-007-14 (which had an unanswered question from session 1) and wasted slots by re-asking the same question. The 15-minute cron monitoring LLM did not flag this as anomalous because no criteria existed to define what "anomalous" means.

The root cause — blocked task IDs not injected into the session prompt — has been fixed in `run_normal_session()`. What remains is the **observability gap**: the monitoring LLM needs objective, unambiguous criteria to evaluate orchestrator health from the log.

## 2. Scenario Catalog with Expected Behavior

Each scenario below defines: what the log looks like when it's **normal**, and what pattern in the log indicates an **anomaly**.

### S1: Normal Task Progression

**Expected**: Sequential sessions, each launching with a different UUID, tasks completing.
```
[orchestrator] Launching session <uuid-A> with account gmail
[orchestrator] Launching session <uuid-B> with account web
```

**Normal signals**:
- Time between sessions: 1–60 min (depending on task complexity)
- Each session uses a different UUID
- Exit code 0 for most sessions

**Anomaly**: More than 3 consecutive sessions that all exit 0 but no task status changes appear in the log (no "completed", no "question.md" written, no progress). This indicates the agent is silently failing or looping.

---

### S2: Task with Pending Question (Blocked)

**Expected**: Orchestrator logs the unanswered question, skips the task, continues with other tasks.
```
[orchestrator] Note: unanswered questions for TASK-XXX — these tasks are skipped; other tasks will continue.
[orchestrator] Launching session <uuid> with account web
```

**Normal signals**:
- "Note: unanswered questions for ..." appears once per loop iteration
- A different task is launched (not the blocked one)
- Orchestrator does NOT stop

**Anomaly**:
- Same task ID from the "unanswered questions" note appears as the task being worked on in a subsequent session output — indicates the skip mechanism failed
- "Note: unanswered questions for ..." messages accumulate (3+ distinct task IDs all blocked) — orchestrator is running but running out of work

---

### S3: Session Exits 0 but Task Remains in_progress

**Expected**: This can happen legitimately when a session hits a confirmation checkpoint or runs out of context. The orchestrator's resume logic (S4) will pick it up next iteration.

**Normal signals**:
- Happens once per task — next iteration resumes via S4
- The session output shows meaningful work was done (not empty)

**Anomaly**:
- Same task resumed 3+ times without completing — indicates the task is stuck in a loop or the agent cannot make progress
- Session output is very short (<100 chars) or empty — indicates the session crashed or failed silently

---

### S4: In-Progress Session Resume

**Expected**: Task with session_id and no pending question is resumed instead of launching "Do next task".
```
[orchestrator] Resuming in-progress TASK-XXX (session <uuid>) with account gmail
```

**Normal signals**:
- Resume happens at most once per task per orchestrator run
- After resume, task either completes or writes question.md

**Anomaly**:
- Same task_id + session_id resumed 3+ times in a single orchestrator run — stuck loop
- Resume followed immediately by another resume of the same task (no work done between them)

---

### S5: Rate Limit on One Account

**Expected**: Account is marked rate-limited, rotation continues to next account.
```
[orchestrator] Account gmail rate-limited until 2026-04-10T15:05:00+00:00, rotating to next account
[orchestrator] Launching session <uuid> with account web
```

**Normal signals**:
- At most 1 rate-limit event per account per hour
- Orchestrator continues with remaining accounts

**Anomaly**: None — this is always normal behavior.

---

### S6: All Accounts Rate-Limited

**Expected**: Orchestrator sleeps until earliest reset, then continues.
```
[orchestrator] All accounts rate-limited. Waiting 3600s until 2026-04-10T15:05:00+00:00
```

**Normal signals**:
- Wait time is 0–7200s (0–2 hours)
- After wait, sessions resume normally

**Anomaly**:
- Wait time exceeds 7200s — something is wrong with reset time parsing
- Multiple "All accounts rate-limited" messages without any successful sessions between them — potential infinite wait loop

---

### S7: Permanent Access Error

**Expected**: Account disabled for the run, continues with remaining accounts.
```
[orchestrator] Account gmail2 has no access — disabling for this run
```

**Normal signals**:
- Each account disabled at most once per run
- Orchestrator continues with remaining accounts

**Anomaly**:
- All accounts disabled — orchestrator has no way to launch sessions (should stop gracefully, but monitor should flag this immediately)
- Same account disabled that was already disabled — logic error

---

### S8: max-tasks Reached

**Expected**: Clean stop after N sessions.
```
[orchestrator] Reached --max-tasks 5, stopping
[orchestrator] Stopped. Reason: max_tasks
```

**Normal signals**: Always normal. Report is written.

**Anomaly**: None — this is always expected behavior.

---

### S9: All Tasks Awaiting Answers

**Expected**: No runnable tasks remain — orchestrator stops.
```
[orchestrator] No runnable tasks — all candidates are awaiting answers. Waiting: TASK-A, TASK-B. Answer pending questions to continue.
[orchestrator] Stopped. Reason: all_tasks_awaiting_answer
```

**Normal signals**: Orchestrator stops, report written with pending questions listed.

**Anomaly**: None — this is correct behavior. But monitoring should **notify the user** that their input is needed.

---

### S10: Duplicate Task Work (the "wasted sessions" pattern)

**Expected**: Each session works on a distinct task (or resumes its own in-progress task).

**Anomaly signals** (from log patterns):
- Two or more sessions in a row where the session output references the same TASK-ID being **started fresh** (not resumed)
- Session output contains "question.md" or "awaiting answer" for a task that already had an unanswered question from an earlier session

**Detection method**: Parse session output excerpts in the report for TASK-IDs. If the same TASK-ID appears in 2+ non-resume sessions, flag as anomaly.

---

### S11: No Progress Over Time

**Expected**: Over any window of 3+ sessions, at least one task should change status (complete, or write question.md, or make visible progress).

**Anomaly**:
- 3+ consecutive sessions all exit 0 but: no tasks completed, no new questions written, no commit messages in output
- Total session time >2 hours with zero task completions

---

### S12: Orchestrator Crash / Unexpected Stop

**Expected**: Log ends with `[orchestrator] Stopped. Reason: {reason}`.

**Anomaly**:
- Log does not end with the "Stopped. Reason:" line — process was killed or crashed
- `.automated_mode` sentinel exists but PID is not alive — orphaned sentinel from crash

## 3. Documentation Location Analysis

### Option A: `automation/MONITORING_CRITERIA.md` (RECOMMENDED)

| Aspect | Assessment |
|--------|------------|
| **Token cost** | Zero — not loaded by default. Monitoring LLM reads it only when explicitly told to in the cron prompt |
| **Discoverability** | Good — lives next to `orchestrate.log`, `state.json`, `reports/` |
| **Editability** | Excellent — standalone file, no YAML frontmatter constraints, can be updated freely |
| **Monitoring LLM access** | Requires one `Read` call — cron prompt tells it to read the file before analyzing the log |
| **Versioning** | Git-tracked alongside the orchestrator code |
| **Freshness** | Can be updated without touching skill files or requirement docs |

### Option B: In `claude-autorun` skill

| Aspect | Assessment |
|--------|------------|
| **Token cost** | HIGH — skill.md is loaded into every agent that invokes `claude-autorun`. Criteria are ~200 lines; this nearly triples the skill size |
| **Discoverability** | Excellent — monitoring LLM already reads the skill |
| **Editability** | Constrained — skills are token-sensitive, CLAUDE.md explicitly warns against bloating skills |
| **Monitoring LLM access** | Already loaded (but at the cost of loading for ALL skill invocations, not just monitoring) |
| **Versioning** | Git-tracked |
| **Freshness** | Updates require skill modification (heavier process) |

**Rejected**: Token cost is prohibitive. The skill is loaded for start/stop/status actions too, not just monitoring. Adding 200 lines of criteria that only the monitoring cron needs wastes tokens on every other invocation.

### Option C: As ACs in `REQ-PROC-041-01`

| Aspect | Assessment |
|--------|------------|
| **Token cost** | Zero for monitoring — requirements are not loaded by the monitoring LLM |
| **Discoverability** | Poor for monitoring — the monitoring LLM has no reason to read requirements |
| **Editability** | Constrained — requirement format rules, YAML frontmatter, trackable items overhead |
| **Purpose fit** | Requirements define WHAT to build, not operational runbooks. Monitoring criteria are operational — they describe how to evaluate a running system |

**Rejected**: Wrong abstraction level. Requirements are blueprints for building; monitoring criteria are operational runbooks for evaluating. However, a **single new AC** should be added to REQ-PROC-041-01 to formalize that monitoring criteria must exist and be maintained.

### Option D: In the cron prompt

| Aspect | Assessment |
|--------|------------|
| **Token cost** | Moderate — prompt text is included in every cron invocation |
| **Discoverability** | Excellent — the LLM sees it immediately |
| **Editability** | Terrible — cron prompts are created via CronCreate and cannot be easily updated; changing criteria means deleting and recreating the cron job |
| **Length limits** | Cron prompts should be concise; 200+ lines of criteria would be unwieldy |

**Rejected**: Impractical for maintenance. Criteria will evolve as the orchestrator evolves.

### Recommendation

**Primary**: `automation/MONITORING_CRITERIA.md` — standalone, zero token cost except when monitoring, easily editable, lives alongside the orchestrator.

**Secondary**: Add one new AC to `REQ-PROC-041-01` formalizing that monitoring criteria must be maintained.

**Tertiary**: Update the `claude-autorun` skill's monitoring cron prompt template to include: "Read `automation/MONITORING_CRITERIA.md` first, then analyze `automation/orchestrate.log` against those criteria."

## 4. Draft: automation/MONITORING_CRITERIA.md

See the content in the "Deliverable" section below — this is the actual file to be written.

## 5. Proposed Changes to REQ-PROC-041-01

Add one new AC:

> AC-17: `automation/MONITORING_CRITERIA.md` exists and defines expected behavior and anomaly signals for every significant orchestrator scenario; the monitoring cron prompt references this file before analyzing the log.

## 6. Proposed Change to claude-autorun Skill

Update step 4 (monitoring cron prompt) from:

> Check automation/orchestrate.log for errors, warnings, or unexpected behavior — report anything suspicious and the current session progress. If the orchestrator has stopped (log contains "Stopped. Reason:"), call CronDelete with this job's ID to cancel further checks.

To:

> Read automation/MONITORING_CRITERIA.md first. Then check automation/orchestrate.log against the criteria in that file. Report any anomalies found, using the severity levels from the criteria (CRITICAL / WARNING / INFO). Also report current session progress. If the orchestrator has stopped (log contains "Stopped. Reason:"), call CronDelete with this job's ID to cancel further checks.

## 7. Deliverable Status

- [x] All 12 significant orchestrator scenarios documented with expected behavior
- [x] Anomaly signals defined for each scenario
- [x] Decision made on documentation location (with rationale)
- [x] Draft monitoring criteria file ready to write
- [x] Proposed requirement update (AC-17) drafted
- [x] Proposed skill update drafted
## 8. Requirements Decisions — User Answers (2026-04-10)

**RD-01 (Empty queue)**: Stop with reason `queue_empty`. Valid termination. No wasted session.

**RD-02 (In-progress task, no session_id)**: Skip the task. Log it with task ID (e.g. `[orchestrator] WARNING: TASK-XXX is in_progress but has no session_id — skipping (may have been started manually)`). Must appear in the run report.

**RD-03 (Max resume attempts)**: 3 attempts per session_id per orchestrator run, then give up. Must appear in the run report — user decides what to do. Reasons a session may not resume: full context window, transient Claude error, etc.

**RD-04 (Concurrent instances)**: Yes, prevent via lock file. Second start attempt must be blocked and logged.

**RD-05 (Same question detection)**: Open — see section 9 for analysis and follow-up question.

**Git tracking (side note)**: The run report should be git-tracked. Auto-commit mechanism needed. User asks which other files make sense — see section 9.

## 9. Open Items

### RD-05: Same-Question Detection — DECIDED

**Decision**: Jaccard word-overlap similarity stored in `state.json`, with both the word set AND first 300 normalized chars of the question body.

**Implementation spec**:
- Normalize: lowercase, strip punctuation, collapse whitespace
- Store in `state.json["question_fingerprints"][task_id]`:
  - `words`: set of normalized words (for Jaccard computation)
  - `preview`: first 300 normalized chars (for human readability when WARNING is reported)
- Jaccard threshold: ≥ 0.60 → WARNING in log + report
- Written when orchestrator detects question.md exists for a task (at loop start, before resume path)
- Survives moves/deletions of question.md (state.json persists across runs)

### Git Tracking — DECIDED

**Files to track**:

| File | Track? | Reason |
|---|---|---|
| `automation/reports/*.md` | **YES** | Audit trail |
| `automation/pending_feedback/*/question.md` | **YES** | What the AI asked |
| `automation/pending_feedback/*/answer.md` | **YES** | User's decisions (user accepts this is in git history) |
| `automation/pending_feedback/README.md` | YES (already static) | Documentation |
| `automation/state.json` | **NO** | Too volatile |
| `automation/orchestrate.log` | **NO** | Too large/volatile |
| `automation/session_outputs/*.txt` | **NO** | Large; CCS is authoritative |
| `automation/.automated_mode` | NO | Transient sentinel |
| `automation/.stop-requested` | NO | Transient sentinel |

**Two-phase auto-commit strategy**:

**Phase 1 — On orchestrator START** (before first session loop):
```
git add automation/pending_feedback/*/answer.md
git commit -m "chore(automation): record user answers YYYY-MM-DD HH:MM"
```
Semantics: "what the user decided before this run". May be a no-op if no answers exist — that's fine.

**Phase 2 — On orchestrator STOP** (`finally` block, after report + health summary written):
```
git add automation/reports/YYYY-MM-DD_HH-MM_report.md automation/pending_feedback/*/question.md
git commit -m "chore(automation): session report YYYY-MM-DD HH:MM [stop_reason]"
```
Semantics: "what this run produced". Runs even on crash (finally block).

Both commits are best-effort (non-fatal if git fails — log WARNING).

- [x] All significant orchestrator scenarios documented (12 original + variable-space analysis)
- [x] Anomaly signals defined
- [x] Decision made on documentation location: `automation/MONITORING_CRITERIA.md`
- [x] RD-01: Empty queue → stop with reason `queue_empty`
- [x] RD-02: In-progress task without session_id → skip + log + report
- [x] RD-03: Max 3 resume attempts per session_id → report for user review
- [x] RD-04: Lock file to prevent concurrent instances
- [x] RD-05: Jaccard similarity (≥0.60) + 300-char preview stored in state.json
- [x] Git auto-commit: two-phase (start: answers / stop: report + questions)
- [ ] **Next step**: finalize MONITORING_CRITERIA.md, new ACs, and implementation gap requirements
