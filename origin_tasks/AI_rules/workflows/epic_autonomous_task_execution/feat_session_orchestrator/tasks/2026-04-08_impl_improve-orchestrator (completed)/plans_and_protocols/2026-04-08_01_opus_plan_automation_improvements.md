# Opus Plan: Automation Orchestrator Improvements

## Objective

Improve `scripts/automation/orchestrate.py` and the `claude-autorun` skill to handle the full spectrum of session lifecycle scenarios reliably — particularly: resuming in_progress tasks correctly, detecting permanent account failures, fixing status reporting, and improving log visibility.

---

## Analysis Summary

### What was observed in the last run

- **Session 2 (gmail)** completed real work on TASK-FUNC-007-17 (concluded "all clear") but stopped at a confirmation point — "Should I apply housekeeping and complete, or skip?" — and **exited 0 without writing `question.md`**. The automated-mode rules require writing `question.md` in this case, but the underlying skill didn't do it.
- **Session 3 (web)** was launched as a fresh "Do next task" session. The orchestrator had already overwritten `session_id` in `goal.md` with session 3's UUID. Session 3 saw the in_progress task and asked "do you want to work on it or skip?" — not knowing what session 2 had already done.
- **Session 1 (gmail2)** failed permanently with "Your organization does not have access to Claude" — a non-rate-limit failure that the orchestrator doesn't handle specially.

### Dropped suggestion (Problem 3 — auto-answer confirmations)

The original plan suggested injecting default answers for confirmations. This is **rejected**: it is not possible to reliably distinguish safe auto-answers from decisions that genuinely need human judgment. The correct mechanism already exists (`pending_feedback` + `question.md`). The problem is enforcement — sessions aren't always writing `question.md` when they should.

---

## Full Scenario Map

Before prescribing fixes, every session-end state must be considered:

| # | Scenario | Current behavior | Desired behavior |
|---|----------|-----------------|-----------------|
| A | Fresh task, session completes successfully | Works | Works (keep) |
| B | Session writes `question.md` and terminates | Orchestrator stops, waits for answer | Works (keep) |
| C | User writes `answer.md` → resume | Resume via `--resume <session_id from question.md>` | Works (keep) |
| D | **Session exits 0, task still `in_progress`, no `question.md`** | Next session launches fresh, re-encounters in_progress task, asks user | **Must resume the previous session using its `session_id`** |
| E | Session rate-limited, exits non-0 | Orchestrator records rate limit, rotates account | Works — but need to resume that session when account resets, not start fresh |
| F | Account permanently inaccessible | Treated same as rate limit rotation | **Must skip account for rest of run** |
| G | Multiple tasks `in_progress` simultaneously | All encountered in "Do next task", all ask "skip?" | **Resume each in_progress session in order; start fresh tasks only after all in_progress ones are resolved** |

### The session_id overwrite problem (affects D and E)

`update_goal_session_fields()` is called **before** the new session runs. This overwrites the previous session's UUID in `goal.md` before we've had a chance to use it for resumption.

For Scenario D: By the time we want to resume session 2, `goal.md` already shows session 3's UUID. Session 2's UUID is lost unless it's in the session_outputs file or CCS logs.

**Fix**: Store a `previous_session_id` field alongside `session_id` in `goal.md`, or — simpler — move `update_goal_session_fields` to run AFTER the session completes. But the reason it runs before is so the session itself can read its own UUID from goal.md. Alternative: pass the UUID only via env var (`CLAUDE_SESSION_ID` is already set), remove the goal.md update entirely since the AI can read the env var.

Actually the cleanest fix: **do not overwrite `session_id` in goal.md when an in_progress task's session is going to be resumed**. Only update it when launching a brand-new fresh session. The orchestrator will know which path it's taking, so this is straightforward.

### Why "Do next task" sees in_progress tasks and asks

The `claude-route` / "Do next task" mechanism picks the highest priority task, and if it's `in_progress`, asks the user whether to continue or skip. In automated mode, this question should not be asked — but the skill only outputs text and exits.

The correct fix is at the **orchestrator level**: detect in_progress tasks BEFORE launching "Do next task", and route to a resume session instead. This way "Do next task" only ever sees tasks that are NOT yet started.

---

## Execution Plan

### Phase 1 — Quick wins (one agent, `implementation-engineer`)

These are safe, isolated changes with no logic risk.

**File: `scripts/automation/orchestrate.py`**

1. **Increase report excerpt: 500 → 1500 chars** (line ~517 and ~798: `cleaned[:500]` → `cleaned[:1500]`)
2. **Reset `start_time` unconditionally on each run** — remove the `if not state.get("start_time"):` guard (lines ~673-676); always write `start_time = datetime.now().isoformat()` into state on each orchestrator launch
3. **Detect permanent account errors** — in the non-zero exit handling block (line ~803), add a check before the rate-limit check:
   ```python
   PERM_ERROR_PATTERNS = ["does not have access", "organization does not have access"]
   if result.returncode != 0 and any(p in result.stdout for p in PERM_ERROR_PATTERNS):
       print(f"[orchestrator] Account {account} has no access — disabling for this run")
       run_data.setdefault("disabled_accounts", set()).add(account)
       state["account_index"] = (state["account_index"] + 1) % len(accounts)
       save_state(STATE_PATH, state)
       continue
   ```
   Update `next_available_account()` to also skip accounts in `run_data["disabled_accounts"]` (pass `run_data` or a set to that function).

**File: `.claude/skills/claude-autorun/skill.md`**

4. **Fix status check**: Replace `python3 -c "import json; d=json.load(...); print('RUNNING' if d.get('running') else 'STOPPED')"` with a check that reads the PID from the `.automated_mode` sentinel and verifies it's alive:
   ```bash
   if [ -f automation/.automated_mode ]; then
     PID=$(cat automation/.automated_mode)
     kill -0 "$PID" 2>/dev/null && echo "RUNNING" || echo "STOPPED"
   else
     echo "STOPPED"
   fi
   ```
5. **Fix Python stdout buffering**: Change the launch command from `python3 scripts/automation/orchestrate.py` to `python3 -u scripts/automation/orchestrate.py` so log output appears in real-time in `orchestrate.log`.

---

### Phase 2 — Core fix: in_progress task resume (one agent, `implementation-engineer`)

**File: `scripts/automation/orchestrate.py`**

Add a new function and a new pre-session check in the main loop.

#### New function: `find_resumable_session(project_root, feedback_dir)`

```python
def find_resumable_session(project_root: str, feedback_dir: str) -> "dict | None":
    """Find an in_progress task whose session can be resumed.

    Returns {goal_path, session_id, task_id, account} or None.
    Only returns tasks that have a session_id and no pending unanswered question
    (those are handled by the answered/unanswered feedback paths).
    """
```

Logic:
1. Find all `goal.md` files with `status: in_progress` (existing `find_active_task_goal` only returns the first — extend to return all)
2. For each, read `session_id` and `session_account` from frontmatter
3. Skip any that have a pending `question.md` (already handled by the feedback path)
4. Return the first one that has a `session_id` set

#### New path in main loop (insert between "unanswered question guard" and "normal session"):

```python
# === In-progress session resume ===
# If a task is in_progress with a known session_id and no pending question,
# resume that session rather than launching a fresh "Do next task".
# Why: starting fresh would re-encounter the in_progress task and either ask
#      the user to skip or redo work already completed in the prior session.
resumable = find_resumable_session(PROJECT_ROOT, FEEDBACK_DIR)
if resumable:
    account = resumable["account"] or accounts[state["account_index"] % len(accounts)]
    env = build_env(account)  # no new UUID — resuming existing session
    print(f"[orchestrator] Resuming in-progress {resumable['task_id']} "
          f"(session {resumable['session_id']}) with account {account}")
    
    session_record = {
        "start": datetime.now(),
        "account": account,
        "task_id": resumable["task_id"],
        "is_resume": True,
    }
    
    result = run_resume_session(
        env,
        resumable["session_id"],
        f"Continue from where you left off. Task {resumable['task_id']} is still in_progress. "
        f"If you completed the work in the previous session, call task-complete now. "
        f"If you still need user input, write question.md to automation/pending_feedback/ "
        f"following the automated-mode rules."
    )
    
    session_record["end"] = datetime.now()
    session_record["exit_code"] = result.returncode
    cleaned = strip_hook_footer(result.stdout)
    write_session_output(OUTPUTS_DIR, resumable["session_id"], cleaned)
    session_record["output_excerpt"] = cleaned[:1500]
    run_data["sessions"].append(session_record)
    run_data["accounts_used"].add(account)
    
    state["run_count"] += 1
    sessions_launched += 1
    save_state(STATE_PATH, state)
    
    if args.min_wait_seconds > 0:
        time.sleep(args.min_wait_seconds)
    continue
```

#### Update `update_goal_session_fields` call site

Currently called before every normal session, even when a task is already in_progress. Since the resume path bypasses the normal session path, this is automatically safe. However, add a guard: only call `update_goal_session_fields` if the task found is NOT already `in_progress` (i.e., it's a fresh task "Do next task" is picking up for the first time).

Since `find_active_task_goal` is called after "Do next task" has started (we don't know what task it'll pick), this is harder to guard. Simpler: always update goal.md session_id before a normal session as before — but since the resume path intercepts in_progress tasks before we ever get to a normal session, the overwrite problem is eliminated by design.

---

### Phase 3 — Validation (manual, by user or via next autorun)

After Phase 1 and 2 are implemented:

1. Run `autorun status` — verify it correctly reports RUNNING/STOPPED using PID check
2. Check `orchestrate.log` during a run — verify real-time log output (Python -u fix)
3. Run `autorun start 2` — observe that:
   - TASK-FUNC-007-17 (still in_progress) is resumed via `--resume` rather than a fresh session
   - The resumed session either completes the task or writes `question.md`
4. Verify that if `gmail2` is tried, it's skipped permanently for the rest of that run

---

## Quality Criteria

- [ ] `autorun status` correctly reports RUNNING when orchestrator PID is alive
- [ ] `orchestrate.log` shows real-time print output during a run
- [ ] In_progress tasks are resumed (not restarted) on the next orchestrator run
- [ ] `gmail2` (or any "no access" account) is skipped permanently within a run without stopping the orchestrator
- [ ] Report excerpts show enough context (≥1500 chars) to understand session outcome
- [ ] `start_time` in state.json reflects the current run, not the previous one

## Risks

- **Resume session compatibility**: `--resume` on an already-exited session works in Claude Code (adds a new message to the conversation history). If the resumed session is too old or its JSONL file has been cleaned up by CCS, the resume will fail. Mitigation: the `run_resume_session` result is checked for exit code; on failure, log a warning and fall through to a normal session.
- **Multiple in_progress tasks**: `find_resumable_session` returns the first one found. If there are multiple (legitimate in cases of parallel work across accounts), they'll be processed in subsequent orchestrator runs one at a time. This is acceptable — the orchestrator is sequential by design.
- **Permanent account error false positives**: The `PERM_ERROR_PATTERNS` check could match unexpected error messages. Keep the check narrow and log it clearly so it's visible in the report.

## Execution Agents

- **1 agent** for Phase 1 (quick wins, low risk, all isolated changes)
- **1 agent** for Phase 2 (core resume logic, medium complexity)
- Total: 2 sequential `implementation-engineer` agents
