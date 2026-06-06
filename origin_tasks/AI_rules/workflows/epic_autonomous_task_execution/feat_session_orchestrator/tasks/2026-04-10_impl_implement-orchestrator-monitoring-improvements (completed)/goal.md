---
task_id: TASK-PROC-041-01-05
type: impl
parent_requirement: REQ-PROC-041-01
urgency: 3
urgency_reason: U3-RELIABILITY
impact: 4
impact_reason: I4-QUALITY
status: completed
completed: 2026-04-10
effort: L
created: 2026-04-10
started: 2026-04-10
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-17, AC-18, AC-19, AC-20, AC-21, AC-22, AC-23, AC-24, AC-25, AC-26]
  sections: []
scope_description: "Implement orchestrator monitoring improvements: queue_empty stop, all-accounts-disabled graceful stop, whitespace answer fix, resume attempt limit, no-session-id skip, git auto-commits, lock file, same-question detection"
release_description: "Orchestrator handles edge cases reliably and auto-commits session reports to git"
requirements_version:
  commit: 97f1418d
  file: ../requirements.md
---

# Goal: Implement Orchestrator Monitoring Improvements (AC-17–AC-26)

## Objective

Implement all new acceptance criteria added to REQ-PROC-041-01 as a result of the monitoring criteria exploration task (TASK-PROC-041-01-04). All changes are to `scripts/automation/orchestrate.py` plus a minor update to `.gitignore`.

## Requirements Summary

REQ-PROC-041-01 AC-17 through AC-26 define improvements to the session orchestrator covering:
- Robustness fixes (AC-18, AC-19, AC-20)
- Observability improvements (AC-21, AC-22, AC-26)
- Git audit trail (AC-23, AC-24)
- Concurrent-instance prevention (AC-25)
- Monitoring criteria file already written (AC-17 — `automation/MONITORING_CRITERIA.md` exists)

For complete requirements: `git show 97f1418d:requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/feat_session_orchestrator/requirements.md`

Current requirements: ../requirements.md

## Scope

### In Scope

All changes to `scripts/automation/orchestrate.py`:

**AC-18: Empty queue → stop with `queue_empty`**
In the normal session pre-flight (after the `is_awaiting_answer` check), detect when `next_tasks.py` returns no task IDs at all (empty output, not "all blocked") and break with `stop_reason = "queue_empty"`.

**AC-19: All accounts permanently disabled → graceful stop**
Fix `next_available_account()`: when all accounts are in `disabled_accounts` AND none are in `rate_limited_until`, the current `min()` call raises `ValueError`. Fix: detect this state and return `(None, None)` sentinel; handle in main loop by breaking with `stop_reason = "all_accounts_disabled"`.

**AC-20: Whitespace-only `answer.md` treated as empty**
Fix `answer_is_empty()`: after the size check, if the file is non-empty, open it and check `content.strip() == ""`. If so, return True. Add log: `[orchestrator] WARNING: answer.md for <task_id> contains only whitespace — treating as unanswered`.

**AC-21: Max 3 resume attempts per session_id**
Add `resume_attempt_counts: dict` to `run_data` (keyed by session_id). In both the answered-feedback resume path and the in-progress resume path, increment the count before running. After 3 attempts for the same session_id, add to `exhausted_resume_ids`, log: `[orchestrator] WARNING: resume of <task_id> exhausted 3 attempts — giving up this run`. Collect exhausted tasks in `run_data["exhausted_resume_tasks"]` for reporting.

**AC-22: In-progress task without session_id — skip and log**
In the main loop, before calling `find_resumable_session()`, scan for in-progress tasks without a session_id. Log each: `[orchestrator] WARNING: <task_id> is in_progress but has no session_id — skipping (may have been started manually)`. Collect in `run_data["skipped_no_session_id"]` for reporting.

**AC-23: Git commit on start (answers)**
Add `git_commit_best_effort(files: list[str], message: str)` helper that runs `git add <files>` then `git commit -m <message>`. Non-fatal (log WARNING on failure). Call at start (before first session loop) with `automation/pending_feedback/*/answer.md` and message `chore(automation): record user answers YYYY-MM-DD HH:MM`. Use `glob.glob()` to expand the wildcard.

**AC-24: Git commit on stop (report + questions)**
Call `git_commit_best_effort()` in the `finally` block, after `write_health_summary()`, with the report file path and `automation/pending_feedback/*/question.md`. Message: `chore(automation): session report YYYY-MM-DD HH:MM [stop_reason]`.

**AC-25: Lock file using `fcntl.flock`**
At the very start of `main()`, before writing `.automated_mode`:
```python
import fcntl
lock_path = os.path.join(AUTOMATION_DIR, ".orchestrator.lock")
lock_fd = open(lock_path, "w")
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("[orchestrator] ERROR: orchestrator already running — aborting")
    sys.exit(1)
```
In the `finally` block: `fcntl.flock(lock_fd, fcntl.LOCK_UN); lock_fd.close()`.

**AC-26: Same-question detection (Jaccard similarity)**

Add two functions:
- `compute_question_fingerprint(text: str) -> dict`: normalize (lowercase, strip punctuation via `re.sub(r'[^\w\s]', '', text)`, collapse whitespace), return `{"words": set_of_words, "preview": normalized[:300]}`
- `check_and_update_question_fingerprint(task_id: str, question_body: str, state: dict, run_data: dict) -> None`: load existing fingerprint from `state["question_fingerprints"][task_id]` if present; compute new fingerprint; if Jaccard ≥ 0.60 log WARNING and append to `run_data["repeated_questions"]`; update fingerprint in state.

Call in the unanswered-question guard section, reading question.md body for each unanswered task.

**Report additions** (`write_report()` or `write_health_summary()`):
- "Skipped Tasks (no session_id)": from `run_data["skipped_no_session_id"]`
- "Exhausted Resumes": from `run_data["exhausted_resume_tasks"]`
- "Repeated Questions": from `run_data["repeated_questions"]` with similarity scores

**`.gitignore` update**:
Check `automation/` entries. Ensure these are ignored:
- `automation/session_outputs/`
- `automation/state.json`
- `automation/orchestrate.log`
- `automation/.automated_mode`
- `automation/.stop-requested`
- `automation/.orchestrator.lock`

Ensure these are NOT ignored (remove if present):
- `automation/reports/`
- `automation/pending_feedback/`

### Out of Scope

- Changes to `claude-autorun` skill (cron prompt already updated in TASK-PROC-041-01-04)
- `automation/MONITORING_CRITERIA.md` (already written in TASK-PROC-041-01-04)
- Any changes to task routing, session launch logic, or report format beyond the additions above

## Acceptance Criteria

- [ ] AC-18 implemented: empty `next_tasks.py` output → stop with `queue_empty`
- [ ] AC-19 implemented: all accounts disabled → stop with `all_accounts_disabled` (no `ValueError`)
- [ ] AC-20 implemented: whitespace-only `answer.md` treated as empty, with WARNING log
- [ ] AC-21 implemented: 3-attempt limit per session_id, exhausted tasks in report
- [ ] AC-22 implemented: in-progress tasks without session_id logged with task_id, in report
- [ ] AC-23 implemented: git commit of answer.md files on orchestrator start
- [ ] AC-24 implemented: git commit of report + question.md files on orchestrator stop
- [ ] AC-25 implemented: `fcntl.flock` lock file prevents concurrent instances
- [ ] AC-26 implemented: Jaccard ≥ 0.60 triggers WARNING, fingerprints stored in state.json
- [ ] Report includes new sections: Skipped (no session_id), Exhausted Resumes, Repeated Questions
- [ ] `.gitignore` correctly ignores volatile files and tracks reports + pending_feedback
- [ ] All existing tests pass (run `python3 -m pytest scripts/` if tests exist)

## Notes

- `automation/MONITORING_CRITERIA.md` was written during the explore task and references the new log messages introduced by these ACs — the implementation must use the exact log message strings documented there.
- The `fcntl` module is Unix-only (Linux/macOS). This is acceptable as the orchestrator only runs in the devcontainer (Linux).
- For AC-26: `state.json` already uses `json.dump/load`; the word set must be serialized as a list (JSON does not support sets). Deserialize back to set when loading.
