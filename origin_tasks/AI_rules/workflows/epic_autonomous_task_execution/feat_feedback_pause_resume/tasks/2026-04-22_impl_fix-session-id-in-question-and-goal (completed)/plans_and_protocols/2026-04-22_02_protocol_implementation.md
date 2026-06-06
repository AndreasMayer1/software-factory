# Protocol: Implementation of TASK-PROC-041-04-02

Date: 2026-04-22
Agent: implementation-engineer (claude-sonnet-4-6)

## Status: Complete

## Files Modified

### 1. `scripts/automation/terminate_session.sh`

Added an inline Python heredoc (`PYEOF`) before the `kill -TERM` line.

The Python block:
- Scans all `automation/pending_feedback/*/question.md` for empty/missing `session_id`
- Reads `$CLAUDE_SESSION_ID` from env; patches `session_id` to the real UUID if available,
  otherwise writes `"NEW_SESSION_REQUIRED"` as a detectable marker
- Finds the corresponding `goal.md` via `task_id` field using `grep -rl` on `requirements_tasks/`
- Writes `session_id` to `goal.md` if absent; sets `status: in_progress` if still `pending`
- Prints `[terminate] Patched session_id in <path> → <value>` for each change made

Existing `set -euo pipefail` and `kill -TERM` lines are intact.

### 2. `scripts/automation/orchestrate.py`

**Change A — `find_answered_feedback` (around line 1013)**

Changed the malformed-check from:
```python
if not frontmatter.get("session_id") or not frontmatter.get("account"):
```
to:
```python
sid = frontmatter.get("session_id", "")
if not sid or not frontmatter.get("account"):
```
Added `"requires_fresh_session": sid == "NEW_SESSION_REQUIRED"` to the returned dict.
`"NEW_SESSION_REQUIRED"` is accepted as valid (non-malformed); truly empty stays rejected.

**Change B — New `run_fresh_session_with_answer` helper (after `run_resume_session`)**

Added a function that launches a new session with `--session-id <uuid>` and a prompt
that includes the goal.md path + the human answer as context. Used when no JSONL file
exists to `--resume`.

**Change C — `process_answered_feedback` method**

- Added `exhausted_task_ids` set derived from `exhausted_resume_tasks` to exclude
  `requires_fresh_session` items that have already been given up on this run.
- Changed `attempt_key` to use `task_id` (not `session_id`) for `requires_fresh_session`
  items, since "NEW_SESSION_REQUIRED" is not a unique UUID.
- Added branch: if `item["requires_fresh_session"]`, grep for goal.md by task_id, generate
  a new `session_uuid`, call `run_fresh_session_with_answer`, log
  `[orchestrator] Launching fresh session for <task_id> (answered pending question)`.
- Else: existing `run_resume_session` path unchanged.
- Both paths share the same `write_session_output` / session_record tail.

### 3. `.claude/skills/claude-automated-mode/skill.md`

Added a **MANDATORY pre-condition** block at the top of "When Human Input Is Genuinely
Needed", before Step 1. The block instructs the LLM to:
1. Check for an `in_progress` task with `session_id` set in goal.md
2. If either is missing: STOP and call `claude-route` on the task's goal.md first
3. Provides the exact bash commands to check

## Tests

- `python3 -m pytest scripts/automation/tests/test_orchestrate.py` — 164 passed, 0 failed
- `bash -n scripts/automation/terminate_session.sh` — syntax OK
- `python3 -m py_compile scripts/automation/orchestrate.py` — syntax OK

## Acceptance Criteria Status

- [x] `terminate_session.sh` patches empty `session_id` in `question.md` from `$CLAUDE_SESSION_ID`
- [x] `terminate_session.sh` also patches the corresponding `goal.md` and sets `in_progress`
- [x] If `$CLAUDE_SESSION_ID` is empty, `"NEW_SESSION_REQUIRED"` is written
- [x] `find_answered_feedback` accepts `"NEW_SESSION_REQUIRED"` without "malformed" warning
- [x] `requires_fresh_session: True` added to returned dict when marker present
- [x] Orchestrator launches fresh session (not `--resume`) when `requires_fresh_session`
- [x] `claude-automated-mode` skill asserts in_progress + session_id before question.md write
- [ ] Manual test: TASK-PROC-027-01 `question.md` repaired by patch logic (manual verification needed)
