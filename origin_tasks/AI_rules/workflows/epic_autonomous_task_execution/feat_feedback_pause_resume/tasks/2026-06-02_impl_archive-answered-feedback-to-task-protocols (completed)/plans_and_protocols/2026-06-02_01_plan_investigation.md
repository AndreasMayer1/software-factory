# Investigation Notes — TASK-PROC-041-04-03

## orchestrate.py — resume/cleanup section

The "process answered feedback" method is `process_answered_feedback` (lines 2341–2712, class method).

Key sub-sections:

**Detection / scanning (lines 2361–2372):**
```python
all_answered = find_answered_feedback(FEEDBACK_DIR, self.deps)
answered = [
    a for a in all_answered
    if a["session_id"] not in run_data.exhausted_resume_ids
    and a["task_id"] not in exhausted_task_ids
]
```

`find_answered_feedback` (lines 2011–2065) scans `automation/pending_feedback/*/` for dirs containing both `question.md` and `answer.md`. Returns list of dicts with fields:
`{task_id, session_id, account, answer_path, folder_path, requires_fresh_session}`

**The section that currently moves `pending_feedback/` → `answered_feedback/` (lines 2684–2699):**
```python
# Decide whether to move to answered_feedback
if result.returncode == 0 and not new_question_written_for(item["task_id"], FEEDBACK_DIR, self.deps):
    _clear_inbox()
    if not os.path.exists(item["folder_path"]):
        _proto(f"{item['task_id']} pending_feedback folder already removed (task-complete cleaned up)")
    else:
        dst = os.path.join(ANSWERED_DIR, item["task_id"])
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(item["folder_path"], dst)
            _proto(f"Moved {item['task_id']} to answered_feedback/")
        except OSError as e:
            _proto(f"WARNING: could not move to answered_feedback ({e}), leaving in pending_feedback")
else:
    _proto(f"{item['task_id']} left in pending_feedback (new question or failure)")
```

Constants (lines 86–88):
```python
FEEDBACK_DIR = os.path.join(AUTOMATION_DIR, "pending_feedback")
ANSWERED_DIR = os.path.join(AUTOMATION_DIR, "answered_feedback")
ANSWER_TEMPLATE_PATH = os.path.join(FEEDBACK_DIR, "TEMPLATE_answer.md")
```

**Safety-net mtime check before the cleanup decision (lines 2663–2682):**
Detects if a follow-up question was written after the answer (question.md mtime > answer.md mtime)
and resets answer.md to the template if so. This runs BEFORE the move decision.

## orchestrate.py — resume prompt construction

**`run_resume_session` — prompt for `--resume` path (lines 1102–1139):**
```python
def run_resume_session(
    env, session_id, answer_path,
    hung_check_interval, hung_timeout_secs, session_timeout_secs,
    stop_flag, deps, model=None,
) -> subprocess.CompletedProcess[Any]:
    prompt = f"Your pending question has been answered. Read the answer at {answer_path} and continue the task."
    cmd = ["claude", "--dangerously-skip-permissions"]
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["--resume", session_id, "-p", prompt])
```
The prompt is assembled at line 1127. The `answer_path` is the path to `pending_feedback/<TASK-ID>/answer.md` (passed in from `process_answered_feedback` at line 2500: `item["answer_path"]`).

**`run_fresh_session_with_answer` — prompt for fresh-session recovery path (lines 1142–1181):**
```python
prompt = (
    "Invoke the claude-automated-mode skill immediately "
    "(CLAUDE_AUTOMATED_MODE=1 is active and automation/.automated_mode exists). "
    f"Then do {goal_path}. "
    "Context: a pending question was already answered. "
    f"Read the answer at {answer_path} and proceed from there."
)
cmd.extend(["--session-id", session_uuid, "-p", prompt])
```
Assembled at lines 1163–1168.

**Call sites in `process_answered_feedback`:**
- `--resume` path: line 2499–2503: `run_resume_session(env, session_id, item["answer_path"], ...)`
- Fresh session path: line 2472–2476: `run_fresh_session_with_answer(env, session_uuid, goal_path, item["answer_path"], ...)`

## orchestrate.py — existing task-id lookup

**`_resolve_task_goal_and_model` (lines 1184–1206):**
```python
def _resolve_task_goal_and_model(
    task_id: str, deps: "OrchestratorDeps"
) -> "tuple[str, str | None]":
    """Find a task's goal.md path and decide its model from frontmatter."""
    req_dir = os.path.join(PROJECT_ROOT, "requirements_tasks")
    grep_result = deps.run_subprocess(
        ["grep", "-rl", f"^task_id: {task_id}", req_dir, "--include=goal.md"],
        capture_output=True, text=True,
    )
    goal_path = next(
        (p for p in grep_result.stdout.strip().splitlines() if p.endswith("goal.md")),
        None,
    )
    if not goal_path:
        return task_id, None
    fm = read_yaml_frontmatter(goal_path)
    model = "opus" if _is_opus_recommended(fm) else None
    return goal_path, model
```
This helper greps `requirements_tasks/` recursively for `goal.md` files containing `^task_id: <TASK-ID>` in frontmatter. Returns `(goal_path, model)`. When not found, returns `(task_id, None)` as a fallback (preserves a recognizable identifier in the prompt).

Call sites in `process_answered_feedback`:
- Fresh session path: line 2455: `goal_path, fresh_model = _resolve_task_goal_and_model(item["task_id"], self.deps)`
- Resume path: line 2485: `_, resume_model = _resolve_task_goal_and_model(item["task_id"], self.deps)`
- Also called in the `prompt_too_long` recovery branch at line 2609.

The `goal_path` returned is an absolute filesystem path like:
`/workspaces/private_mood_tracker/flutter_app/requirements_tasks/.../tasks/YYYY-MM-DD_impl_name/goal.md`

The `plans_and_protocols/` sibling directory for archiving is derived by replacing `goal.md` with `plans_and_protocols/` from this path.

## feat_feedback_pause_resume/requirements.md — AC-06, AC-09

**AC-06 (line 114):**
> When a resumed session exits normally (no new `question.md` written), the orchestrator: (1) merges `question.md` and `answer.md` into a single `feedback-checkpoint` file written to the task's `plans_and_protocols/` folder, named `YYYY-MM-DD_feedback-checkpoint_<TASK-ID>.md`, with a YAML envelope (fields: `skill`, `mode: automated`, `decision`, `task_id`, `captured_at`) and free-form body sections `# Question`, `# Developer Answer` (verbatim), and `# Rationale Captured`; (2) deletes the `automation/pending_feedback/<TASK-ID>/` folder. The `answered_feedback/` folder is no longer used for new entries; existing entries remain as-is.

**AC-09 (line 117):**
> The resume prompt injected by the orchestrator (the `-p` argument to `claude --resume`) is prefixed with a one-line preamble that gives the path of the archived `feedback-checkpoint` file, so the resumed session can locate the answer record without accessing `pending_feedback/`. Example preamble: `[Answer archived at: requirements_tasks/.../plans_and_protocols/YYYY-MM-DD_feedback-checkpoint_TASK-ID.md]`

Note: The requirements.md for feat_feedback_pause_resume has only AC-01 through AC-09. There is no AC-10 in this file. AC-09 is the last AC.

## feat_session_orchestrator/requirements.md — answered_feedback refs

`answered_feedback` does not appear as a string in the session_orchestrator requirements.md. The word "answered_feedback" does not appear in any AC text. AC-10 in that file is:

**AC-10 (line 163):**
> After each session exits, stdout is captured, the hook reminder footer is stripped, and the result is written to `automation/session_outputs/<session_uuid>.txt`

This AC is about session output capture, not feedback archival. It has no relationship to `answered_feedback/`.

**AC-13 (line 167)** does describe the resume mechanism but references `-p "$(cat answer.md)"` inline (pre-dates the current implementation which passes a file path instead):
> Tasks with `answer.md` present in `pending_feedback/` are resumed via `claude --resume <session-id> -p "$(cat answer.md)"` with the account from `question.md` frontmatter

## Skills referencing answered_feedback

### `.claude/skills/task-complete/SKILL.md` — lines 156, 159

Context (lines 151–161):
```
3.6. **Clean up autorun pending_feedback** (if applicable):
   Check whether the orchestrator left a feedback folder for this task:
   ```bash
   ls automation/pending_feedback/<TASK-ID>/ 2>/dev/null
   ```
   If it exists, move it to `answered_feedback/` (mirrors what the orchestrator does on a
   successful automated session):
   ```bash
   mv automation/pending_feedback/<TASK-ID> automation/answered_feedback/<TASK-ID>
   ```
   This is a no-op when the task was never run via autorun.
```
This step will need updating to use the new archival logic (merge to feedback-checkpoint, delete pending_feedback folder).

### `.claude/skills/ux-flow-draft/SKILL.md` — lines 213, 434, 446, 500

Line 213 (CONTINUE mode feedback source list):
```
2. `automation/answered_feedback/$TASK_ID/answer.md` — archived (orchestrator already moved it)
```

Lines 432–436 (after presenting output, interactive mode):
```
- **If feedback was consumed from `pending_feedback/` (Step 2.0 source #1)**: archive it first regardless of mode:
  ```bash
  [ -d "automation/pending_feedback/$TASK_ID" ] && mv "automation/pending_feedback/$TASK_ID" "automation/answered_feedback/$TASK_ID"
  ```
  Include this move in the Step 11b commit.
```

Lines 440–448 (automated mode end-of-iteration):
```
1. Archive consumed answer (if feedback came from `pending_feedback/`):
   ```bash
   TASK_ID=<task_id>
   if [ -d "automation/pending_feedback/$TASK_ID" ]; then
     mv "automation/pending_feedback/$TASK_ID" "automation/answered_feedback/$TASK_ID"
   fi
   ```
```

Line 500 (critical rules):
```
- **Mode-agnostic feedback**: CONTINUE mode discovers feedback from `pending_feedback/`, `answered_feedback/`, or `user_feedback/` — works identically whether started by autorun or manually.
```

### `.claude/skills/ux-flow-draft/contract.yaml` — line 58

```yaml
  - target: automation/answered_feedback/<TASK-ID>
    action: write
    note: pending_feedback/<TASK-ID> moved here when an autorun feedback folder exists.
```

### `.claude/skills/task-complete/contract.yaml` — line 61 (approximately, in may_invoke section)

```yaml
  - CONTINUE mode discovers feedback from pending_feedback/, answered_feedback/, or user_feedback/.
```

### `.claude/skills/verify-quality/SKILL.md` — line 278

Context (lines 277–283):
```
The active task stays `in_progress`, its `session_id` is preserved, and the
orchestrator's pending-feedback machinery (`scripts/automation/orchestrate.py:find_answered_feedback`
and `scripts/tasks/next_tasks.py:load_pending_feedback_ids`) keeps the task off
the queue until the developer fills `answer.md`. On resume, the new session's
first verify-quality invocation will see no `cycle_state.json` (the file was
left intact but the developer's answer is expected to either fix the violation
or delete the file) and start fresh from cycle 1 if RED recurs.
```
This reference is to the function name `find_answered_feedback` (the orchestrate.py function), not the `answered_feedback/` directory. No update needed here.

## CLAUDE.md — answered_feedback refs

No matches. `grep -n "answered_feedback" CLAUDE.md` returns empty.

## artifacts.yaml — structure + task-workspace category

**Category definition (line 18):**
```yaml
task-workspace: "Files inside requirements_tasks/**/tasks/<task>/ that drive and log work"
```

**Full field set for a task-workspace entry (example — `goal` token, lines 36–39):**
```yaml
goal:
  category: task-workspace
  path: "requirements_tasks/**/tasks/*/goal.md"
  definition: "Task objective, metadata (YAML frontmatter), and acceptance-criteria checklist"
```
Fields: `category` (string, one of the controlled category keys), `path` (glob pattern), `definition` (one-line string).

**All existing task-workspace entries (lines 36–80):**
| Token | Path glob | Definition summary |
|---|---|---|
| `goal` | `requirements_tasks/**/tasks/*/goal.md` | Task objective + metadata |
| `plans-dir` | `requirements_tasks/**/tasks/*/plans_and_protocols/` | Cross-session memory home |
| `plan` | `requirements_tasks/**/plans_and_protocols/*plan*.md` | High-level plan |
| `protocol` | `requirements_tasks/**/plans_and_protocols/*protocol*.md` | Step-by-step execution log |
| `test-plan` | `requirements_tasks/**/plans_and_protocols/*test_plan*.md` | Test strategy |
| `lookup-log` | `requirements_tasks/**/plans_and_protocols/lookup_log.jsonl` | Doc-lookup budget log |
| `cycle-state` | `requirements_tasks/**/plans_and_protocols/cycle_state.json` | Quality-gate back-pressure counter |
| `cascade-log` | `requirements_tasks/**/plans_and_protocols/cascade_log.md` | Multi-pass cascade pass tracker |
| `user-input` | `requirements_tasks/**/plans_and_protocols/*_00_user_initial_input.md` | Verbatim user seed input |

**Existing automation entries (lines 319–327):**
```yaml
pending-question:
  category: automation
  path: "automation/pending_feedback/*/question.md"
  definition: "Escalation checkpoint: question written by a session awaiting developer input"

pending-answer:
  category: automation
  path: "automation/pending_feedback/*/answer.md"
  definition: "Developer response to a pending question; triggers orchestrator session resume"
```
There is no `answered-feedback`, `answered_feedback`, or `feedback-checkpoint` entry yet. The new `feedback-checkpoint` artifact will need to be added here.

## scripts/tasks/ — task-id lookup utilities

| Script | Purpose relevant to task-id lookup |
|---|---|
| `next_tasks.py` | Returns the next N unblocked tasks to work on, ranked. Reads `goal.md` frontmatter (including `task_id`). Includes `load_pending_feedback_ids()` (reads `pending_feedback/*/question.md` frontmatter to extract task_ids of paused tasks and exclude them from the queue). |
| `is_awaiting_answer.py` | Given `--task-id TASK-ID`, checks whether `automation/pending_feedback/<task_id>/question.md` exists and `answer.md` is empty/template. Returns exit code 0 (not awaiting) or 1 (awaiting). |
| `find_orchestration_tasks.py` | Finds orchestration tasks by frontmatter signature (`target_release` set + `scope_description` starts with "Orchestration:"). Not a general task-id lookup. |
| `goal_preview.py` | Prints first N lines of a goal.md body (frontmatter excluded). Takes a path, not a task_id. |
| `allocate_task_id.py` | Allocates a new task ID (registry append). Not a lookup utility. |
| `complete_task.py` | Marks a task complete. Not a lookup utility. |
| `summarize_plan.py` | Summarizes plan files. Not a task-id lookup. |
| `top_blocked_task.py` | Returns the top blocked task. Uses `goal.md` frontmatter. |
| `reconcile_after_chains.py` | Validates/fixes `after:` dependency chains. |
| `parse_task_creation_plan.py` | Parses a task creation plan for uncreated tasks. |
| `propose_after.py` | Proposes `after:` dependency ordering. |
| `create_orchestration_task.py` | Creates an orchestration task. |
| `check_task_against_plan.py` | Validates a task's frontmatter against a plan file. |

**Most relevant for this task:** `_resolve_task_goal_and_model` in `orchestrate.py` (lines 1184–1206) is already the canonical in-orchestrator utility that maps a `task_id` string to a `goal.md` absolute path using `grep -rl "^task_id: {task_id}" requirements_tasks/ --include=goal.md`. The `plans_and_protocols/` sibling directory path is derived from the `goal_path` by replacing `goal.md` with `plans_and_protocols/`. No separate external script is needed.

## Implementation notes for the implementer

1. **Archival step replaces the `shutil.move` block (lines 2684–2699).** The new logic, when `result.returncode == 0 and not new_question_written_for(...)`:
   - Call `_resolve_task_goal_and_model(item["task_id"], self.deps)` to get `goal_path` (already called at line 2455 or 2485 earlier in the method — pass it forward or call again).
   - Derive `protocols_dir = os.path.join(os.path.dirname(goal_path), "plans_and_protocols")`.
   - Read `question.md` body and `answer.md` body.
   - Read `skill` field from `question.md` frontmatter (already parsed in `find_answered_feedback`).
   - Compose filename: `f"{date_today}_feedback-checkpoint_{item['task_id']}.md"`.
   - Write the merged file with YAML envelope + `# Question`, `# Developer Answer`, `# Rationale Captured` sections.
   - Delete `item["folder_path"]` with `shutil.rmtree`.
   - Return the archive path for use in the resume prompt preamble.

2. **Resume prompt preamble (AC-09).** The `run_resume_session` call at line 2499 passes `item["answer_path"]` as the path. After the new archival step, the answer is no longer at `answer_path`. The prompt in `run_resume_session` (line 1127) currently reads:
   ```
   "Your pending question has been answered. Read the answer at {answer_path} and continue the task."
   ```
   Per AC-09, the new prompt must be prefixed with:
   ```
   f"[Answer archived at: {archive_path}]\n"
   ```
   The archival step must happen **before** `run_resume_session` is called. The current code calls `run_resume_session` at line 2499 **before** the cleanup block at line 2684. The order must be reversed for AC-06+AC-09: archive first, then resume (or pass the archive path into the resume call as a new parameter).

   **Ordering issue to resolve:** The current sequence is:
   - Line ~2499: `run_resume_session(...)` ← uses answer_path
   - Line 2684+: move pending_feedback → answered_feedback

   New required sequence:
   - Archive (merge + delete pending_feedback) ← produces archive_path
   - `run_resume_session(...)` with preamble containing archive_path

   The `fresh_session` path (line 2472) similarly passes `item["answer_path"]` and must be updated.

3. **`ANSWERED_DIR` constant** (line 87: `ANSWERED_DIR = os.path.join(AUTOMATION_DIR, "answered_feedback")`) will no longer be used for new entries. It can remain for reference but all new code paths must use the task's `plans_and_protocols/` instead.

4. **Skills to update after orchestrate.py change:**
   - `task-complete/SKILL.md` step 3.6: replace `mv ... answered_feedback/` with the merge-and-delete logic (or a script call).
   - `ux-flow-draft/SKILL.md` lines 434, 446: same replacement.
   - `ux-flow-draft/SKILL.md` line 213: update CONTINUE mode source list (answered_feedback fallback becomes the `plans_and_protocols/feedback-checkpoint` file).
   - `ux-flow-draft/contract.yaml` line 58: update target from `answered_feedback/<TASK-ID>` to the new artifact.
   - `artifacts.yaml`: add a `feedback-checkpoint` token under the `task-workspace` or `automation` category.

5. **`question.md` frontmatter fields available** (from `find_answered_feedback` result dict): `task_id`, `session_id`, `account`, `answer_path`, `folder_path`, `requires_fresh_session`. The `skill` field must be read from the raw `question.md` frontmatter (it is not in the result dict — `find_answered_feedback` does not extract it). Use `read_yaml_frontmatter(question_path).get("skill", "")`.
