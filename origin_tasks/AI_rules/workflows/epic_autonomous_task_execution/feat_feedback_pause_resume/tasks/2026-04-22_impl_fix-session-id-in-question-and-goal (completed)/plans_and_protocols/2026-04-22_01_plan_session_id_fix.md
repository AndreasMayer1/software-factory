# Opus Plan: Fix session_id in question.md / goal.md

## Objective

Ensure that every `question.md` written by an automated session always carries a
valid `session_id`, and that the corresponding `goal.md` is always `in_progress`
with the same `session_id`. Achieve this through structural enforcement, not just
instructions, so it holds even when the session bypasses `claude-route`.

---

## Analysis Summary

### Root cause chain

1. Session 9 (2026-04-19, TASK-PROC-027-01) completed two other tasks and then
   self-identified the next task — but called `task-resolve` directly instead of
   going through `claude-route`.
2. `claude-route` is the only place that writes `session_id` + `in_progress` to
   `goal.md` (step 2b). Skipping it means `goal.md` stays `status: pending` with
   no `session_id` field.
3. `claude-automated-mode` reads `SESSION_ID` from `goal.md` via grep. If the field
   is absent, `SESSION_ID=""` and `question.md` gets `session_id: ""`.
4. `find_answered_feedback` in `orchestrate.py` rejects `session_id: ""` as
   "malformed" — so the question is never processed, the orchestrator loops
   indefinitely, and the same-question-repeated CRITICAL fires.

### Why instruction-only fixes are insufficient

Telling the LLM "always call `claude-route` first" is what we already (implicitly)
rely on — and it failed once. For a safety property like session_id correctness, we
need a structural backstop that runs in code, not in the LLM's attention.

### Why `terminate_session.sh` is the right backstop

`terminate_session.sh` is called by the session itself, immediately before it
exits, on the question-writing path. It runs in the same process environment as
the session, so `$CLAUDE_SESSION_ID` is available. LLM compliance with this single
final-step script is high (it's a concrete shell command, always the last step).
Adding validation here requires zero new LLM compliance.

### The resume-flow implication

`run_resume_session` calls `claude --resume <session_id>` — it looks up the JSONL
file for that UUID. If `session_id` is empty or invalid, the command fails. For a
task that was still `pending` when it asked a question (no real session to resume),
a fresh session must be launched instead, with the answer delivered in the prompt.
This requires a new orchestrator code path for `session_id: "NEW_SESSION_REQUIRED"`.

---

## Execution Plan

### Change 1 — `scripts/automation/terminate_session.sh` (primary structural fix)

Before the `kill -TERM` line, add a Python call that:

1. Scans all `automation/pending_feedback/*/question.md` files
2. For each file with `session_id: ""` or missing `session_id`:
   a. Reads `$CLAUDE_SESSION_ID` from env
   b. If non-empty: patches `session_id` in question.md to the real UUID
   c. If empty (edge case — shouldn't happen in automated mode): writes
      `session_id: "NEW_SESSION_REQUIRED"` as a detectable marker
   d. In both cases: finds the corresponding `goal.md` (via `task_id` field)
      and writes `session_id: <value>` if absent, and sets `status: in_progress`
      if it is still `pending`

Why patching `goal.md` here too: the resumed session will find the task
`in_progress`, which is the contract. Without this, `find_resumable_session`
won't pick it up either.

**Result**: By the time the orchestrator reads `pending_feedback/`, every
`question.md` has a non-empty `session_id`. The "malformed" path in
`find_answered_feedback` becomes unreachable for the normal question flow.

### Change 2 — `scripts/automation/orchestrate.py` (two sub-changes)

#### 2a. `find_answered_feedback` — support `NEW_SESSION_REQUIRED` marker

Current check:
```python
if not frontmatter.get("session_id") or not frontmatter.get("account"):
    print("WARNING: malformed question.md ...")
    continue
```

Change to: accept `"NEW_SESSION_REQUIRED"` as a valid (non-malformed) session_id.
Keep rejecting truly empty or missing session_ids. Add a `requires_fresh_session`
flag to the returned dict when the marker is present.

```python
sid = frontmatter.get("session_id", "")
if not sid or not frontmatter.get("account"):
    print(f"[orchestrator] WARNING: malformed question.md in {task_dir.path}, skipping")
    continue

result_item = { ..., "session_id": sid, "requires_fresh_session": sid == "NEW_SESSION_REQUIRED" }
```

#### 2b. Answered-feedback handler — new branch for `requires_fresh_session`

Currently always calls `run_resume_session(env, session_id, answer_content)`.

Add a branch: if `item["requires_fresh_session"]`:
- Find the `goal.md` path from `task_id` (grep)
- Call a new helper `run_fresh_session_with_answer(env, goal_path, answer_content)`
  which launches `claude -p "Invoke claude-automated-mode skill. Then do
  [goal_path]. Context: a pending question was already answered. The answer was:
  [answer_content]. Proceed from there."`

This delivers the answer to the fresh session without needing a resume UUID.

### Change 3 — `.claude/skills/claude-automated-mode/skill.md` (defense in depth)

Replace the current Step 1 with an explicit assertion:

```bash
# Find THIS task's goal.md — must already be in_progress with session_id set
GOAL=$(grep -rl "^status: in_progress" requirements_tasks/ --include="goal.md" | head -1)
if [ -z "$GOAL" ]; then
  echo "ERROR: No in_progress task found. claude-route was not called."
  echo "STOP: call claude-route on the specific goal.md for this task before writing question.md."
  exit 1
fi
SESSION_ID=$(grep -m1 "^session_id:" "$GOAL" | awk '{print $2}')
if [ -z "$SESSION_ID" ]; then
  echo "ERROR: goal.md has no session_id. claude-route step 2b did not run."
  echo "STOP: call claude-route on the specific goal.md for this task before writing question.md."
  exit 1
fi
```

Note: This is still an instruction to the LLM. But it produces a visible error
message if violated, making the problem diagnosable. The `terminate_session.sh`
patch (Change 1) is the actual enforcement.

### Change 4 — `.claude/skills/claude-automated-mode/skill.md` (wording)

Add one explicit sentence at the top of "When Human Input Is Genuinely Needed":

> **MANDATORY**: `claude-route` MUST have been invoked on the current task's
> `goal.md` before this procedure runs. It writes `session_id` and sets
> `status: in_progress` — both are required for the orchestrator to resume the
> session after the user answers.

---

## Files to Change

| File | Change |
|------|--------|
| `scripts/automation/terminate_session.sh` | Add Python patch call before kill |
| `scripts/automation/orchestrate.py` | `find_answered_feedback` + answered-feedback handler |
| `.claude/skills/claude-automated-mode/skill.md` | Assertion + mandatory wording |

No new scripts needed — patching logic goes inline in `terminate_session.sh` via
a Python one-liner or heredoc.

---

## Why NOT the other options

| Option | Why rejected |
|--------|-------------|
| Relax `find_answered_feedback` to accept empty session_id | User correctly pointed out: empty = bug. Don't hide bugs, fix them. |
| Script for creating question.md (user calls it) | Same compliance problem — LLM must call the script. No structural guarantee. |
| Session-id as CLI arg to question-creation script | Doesn't solve goal.md missing session_id (two separate writes still needed). |
| Orchestrator pre-selects task + pre-writes session_id | Too complex, breaks multi-task sessions. |
| One-task-per-session enforcement | Higher billing, bigger architectural change. Future option if other issues arise. |

---

## Quality Criteria

- [ ] `automation/pending_feedback/TASK-PROC-027-01/question.md` has real `session_id`
  after manual test of `terminate_session.sh` patch
- [ ] `goal.md` for TASK-PROC-027-01 has `session_id` and `status: in_progress`
  after patch runs
- [ ] Orchestrator handles `NEW_SESSION_REQUIRED` without crashing
- [ ] Fresh session with answer context produces correct task output
- [ ] `find_answered_feedback` still rejects truly empty/malformed session_id
- [ ] `claude-automated-mode` skill prints clear error if precondition violated

---

## Risks

- **terminate_session.sh patch fails silently**: use `set -e` already present;
  add explicit echo on patch success so orchestrator log shows confirmation
- **Multi-task sessions write multiple question.md files**: scan handles all files
  in the loop, not just the most recent one — safe
- **`$CLAUDE_SESSION_ID` unavailable in terminate_session.sh environment**: verified
  that `build_env` always sets it for normal session launches; edge case where it's
  absent gets the `NEW_SESSION_REQUIRED` marker

---

## Execution: single implementation agent

All changes are straightforward edits to 3 files. One `implementation-engineer`
agent can execute them sequentially. No plan approval needed — the changes are
well-defined.
