# Research: Automation Q&A Mechanism and Self-Regenerating Task Pattern

Date: 2026-05-14
Scope: Factual investigation of how the `automation/pending_feedback/` Q&A mechanism and the self-perpetuating orchestration-task pattern work, so that task `goal.md` files can reference them accurately.

---

## §1 Q&A files: frontmatter and body shapes

### `question.md` — written by the AI

Canonical template: `automation/pending_feedback/TEMPLATE_question.md`. Verbatim frontmatter (live example: `automation/pending_feedback/TASK-PROC-006-02/question.md`):

```yaml
---
task_id: TASK-PROC-006-02
session_id: 7e90a3be-126e-4e21-ab14-78cd3f18d323
account: web
status: awaiting_answer
asked_at: 2026-05-07T19:15:00Z
skill: requ-explore
---
```

Field meanings (from `scripts/automation/orchestrate.py:1385–1416` `find_answered_feedback`):

- `task_id` — TASK-ID, also used as the folder name under `pending_feedback/`.
- `session_id` — UUID of the paused session, used by `claude --resume <uuid>`. Sentinel `NEW_SESSION_REQUIRED` is accepted; it tells the orchestrator the original session bypassed `claude-route` so no JSONL exists — a fresh session is launched with the answer as context (see `run_fresh_session_with_answer`, line 697).
- `account` — required. Selects `CLAUDE_CONFIG_DIR` so the JSONL session file is found.
- `status: awaiting_answer` — descriptive only; not parsed by the orchestrator.
- `asked_at` — ISO-8601 UTC timestamp, informational.
- `skill` — name of the skill that paused; informational.

The body is free-form Markdown. The live `TASK-PROC-006-02/question.md` body uses sections: `# Pending Question — <TASK-ID> (<title>)`, `## Where this task is`, `## Decisions (paste your answers under each)` with `### D1.`/`### D2.`/... sub-sections each containing `**Proposal:**`, `**Alternative:**`, `**Your answer:**`, then a closing `## How this task closes` and `## Default-accept escape hatch`. No section structure is enforced by the orchestrator — the entire body below the frontmatter is human-facing context, and the entire `answer.md` content is passed verbatim to `claude --resume … -p <answer>`.

### `answer.md` — written by the developer

Created by the AI by copying `automation/pending_feedback/TEMPLATE_answer.md`. Verbatim template content:

```
<!-- AWAITING_HUMAN_ANSWER -->

⚠️  AUTOMATED SESSIONS: Do NOT write to this file.
This file is reserved for human responses only.
Writing here as an automated session violates the safety protocol.

The developer will open this file and type their answer below — replacing or appending to this text.
```

`answer.md` has no frontmatter. "Answered" is detected with the sentinel logic in `scripts/automation/orchestrate.py` `answer_is_empty()` (lines 226–263) and the mirror in `scripts/tasks/is_awaiting_answer.py`: the file is treated as unanswered if it is missing, zero-byte, whitespace-only, starts with `<!-- AWAITING_HUMAN_ANSWER -->` and equals the template content, or contains the template sentinel line with nothing appended (see `_ANSWER_TEMPLATE_SENTINEL` in `scripts/tasks/next_tasks.py:62`).

### Other files in the folder

`automation/pending_feedback/` also contains:
- `README.md` — developer-facing operating instructions.
- `TEMPLATE_question.md`, `TEMPLATE_answer.md` — schemas.

Each task folder under `pending_feedback/` contains only `question.md` and `answer.md`. After successful resume the orchestrator `shutil.move()`s the whole folder to `automation/answered_feedback/<TASK-ID>/` (orchestrate.py:1800–1809).

---

## §2 Orchestrator scripts and the session-UUID ↔ task-folder link

- `scripts/automation/orchestrate.py` — the orchestrator. Constants at lines 43–50: `FEEDBACK_DIR`, `ANSWERED_DIR`, `ANSWER_TEMPLATE_PATH`, `ANSWER_TEMPLATE_MARKER`.
- `scripts/automation/terminate_session.sh` — invoked by `claude-automated-mode` Step 4; exits the current Claude session cleanly after `question.md` has been written.
- `scripts/tasks/is_awaiting_answer.py` — query script used by the orchestrator's `check_queue_state` (orchestrate.py:2089–2096) to filter `next_tasks.py` candidates.
- `scripts/tasks/next_tasks.py` — calls `load_pending_feedback_ids()` (lines 74–122) so unanswered tasks never surface as "next task".

**Who writes `question.md`:** the AI session itself, following the procedure in `.claude/skills/claude-automated-mode/skill.md` (lines 99–139). The orchestrator never writes `question.md`.

**Who detects `answer.md`:** the orchestrator on every main-loop iteration via `find_answered_feedback(FEEDBACK_DIR, deps)` (orchestrate.py:1362–1419). It returns `{task_id, session_id, account, answer_content, folder_path, requires_fresh_session}` for each folder whose `answer.md` is not empty / template-only.

**Resume path:** `process_answered_feedback` (orchestrate.py:1667–1819) runs `run_resume_session(env, session_id, answer_content, …)` which calls `claude --dangerously-skip-permissions --resume <session_id> -p <answer_content>` (lines 663–694). If `requires_fresh_session` (session_id == `NEW_SESSION_REQUIRED`) it instead allocates a new UUID, runs `grep -rl "^task_id: <task_id>" requirements_tasks --include=goal.md` to find the `goal.md`, and launches `run_fresh_session_with_answer(...)` with a prompt embedding the answer.

**Linking session UUID ↔ task folder:** four places, all consistent:

1. `goal.md` YAML frontmatter has `session_id:` and `session_account:`. The orchestrator writes these via `update_goal_session_fields` (orchestrate.py:473–517) when it launches a normal session.
2. `question.md` frontmatter mirrors `session_id`, `account`, and `task_id`. This is what `find_answered_feedback` reads — it does NOT re-read `goal.md`.
3. JSONL path: `JSONL_BASE = /home/vscode/.ccs/shared/context-groups/default/projects/-workspaces-private-mood-tracker-flutter-app/<session_uuid>.jsonl` (orchestrate.py:741–744). Used for hung-session detection (`get_mtime` polling at line 819).
4. The folder name under `pending_feedback/` MUST equal the `task_id` (orchestrate.py:1453 derives the path as `os.path.join(feedback_dir, task_id)`).

**Canonical user-facing rule for invoking the Q&A:** `.claude/skills/claude-automated-mode/skill.md` lines 76–139. Summary: in automated mode every "ask the user" checkpoint is replaced with (a) verify `claude-route` has been called so `goal.md` has `status: in_progress` and a `session_id`, (b) write `automation/pending_feedback/<TASK_ID>/question.md` with the four required frontmatter fields, (c) `cp TEMPLATE_answer.md <TASK_ID>/answer.md`, (d) run `bash scripts/automation/terminate_session.sh`. `claude-ask` is the unrelated Opus-research skill — it does NOT use `pending_feedback`.

### Documentation

- `automation/pending_feedback/README.md` — the only narrative doc; describes the developer flow.
- `automation/MONITORING_CRITERIA.md` — references question.md for orchestrator-health checks (malformed/repeated questions).
- No `doc/` page covers this mechanism.

---

## §3 Pre-session Q&A support (does it work?)

**Question:** can a `question.md` be created BEFORE the task's first session runs (so the task starts life as "blocked, awaiting human answer")?

**Findings:**

- `next_tasks.py` `load_pending_feedback_ids()` (lines 74–122) reads `pending_feedback/` directly off the filesystem with no requirement on session state. So a task with a pre-created `question.md` and empty `answer.md` IS hidden from the next-task queue. Good.
- `scripts/tasks/is_awaiting_answer.py` likewise checks only filesystem presence/emptiness. Good.
- `orchestrate.py` `find_answered_feedback` (line 1362) requires `question.md` frontmatter to contain non-empty `session_id` AND non-empty `account` (line 1390). Without both, the entry is skipped with `"malformed question.md"`.

**Pre-session viability:** YES with one caveat. To create a Q&A "in advance" of any session, the `question.md` must carry valid `session_id` and `account` values. There are two practical paths:

1. **Use `session_id: NEW_SESSION_REQUIRED`** — already supported. `find_answered_feedback` accepts this sentinel (lines 1386–1388) and triggers the `run_fresh_session_with_answer` path. The orchestrator finds the task's `goal.md` by `grep -rl "^task_id: <task_id>" requirements_tasks --include=goal.md` (orchestrate.py:1727), so the `goal.md` must exist with that exact `task_id`. `account` still has to be a real account name (e.g. `web`).

2. **Pre-assign a real session UUID** — possible but pointless: no JSONL exists, so `--resume <uuid>` would fail. Use path 1 instead.

**Gaps to be aware of:**

- The `session_id` field in `goal.md` is independently updated by `update_goal_session_fields` when a fresh session is later launched (orchestrate.py:496–507). So the `question.md` and `goal.md` values may diverge during the first run — that is expected. Only `question.md`'s `session_id` drives the resume decision.
- `next_tasks.py` and the orchestrator's queue-state check (`check_queue_state`, orchestrate.py:2058–2105) treat an unanswered question.md as blocking the task. So a pre-created question.md will keep the task off the queue until `answer.md` is filled — exactly the intended "blocked, awaiting answer" semantics.

Bottom line: a task can ship into the repo with `automation/pending_feedback/<TASK_ID>/question.md` already populated (session_id=`NEW_SESSION_REQUIRED`, account=any valid account, task_id matching `goal.md`), and the orchestrator will only launch a session on it after `answer.md` becomes non-template.

---

## §4 Self-regenerating task pattern (orchestration tasks)

**Location of the mechanism:** `scripts/tasks/create_orchestration_task.py` (only invoked from inside an orch task's own AC checklist; also invoked once by `release-begin-impl` Phase 6 step 6.3 to seed the chain). The `release-begin-impl` skill itself does not loop — the loop is in the orch tasks' goal.md body.

**How it works:**

1. `release-begin-impl` Phase 6 calls `python3 scripts/tasks/create_orchestration_task.py --after-task <explore_task_id> --plan-path <plan path>` to create the first orchestration task.
2. The script (lines 191–241) writes a `goal.md` whose ACs list every per-task `task-create-code` (or `ui-create-scribble`) skill invocation for one package, then add this AC line (template lines 182–186):
   ```
   - [ ] Run `python3 scripts/create_orchestration_task.py --after-task {task_id} --plan-path {plan_path}` — creates next orch task OR validation task
   ```
3. When the autorun session executes that AC, it spawns the next orchestration task via the same script. The new task is the successor; the script's name in the AC is the regeneration trigger.

**Successor naming:** `{today}_explore_create-impl-tasks-release-{version}` (orchestrate-task.py:429). Date prefix is FRESH each run (today's date), NOT inherited. There is no numeric counter — the file's task folder name relies on the day plus the version. (Multiple successors in one day would collide on directory name; the script's `find_existing_orchestration_task` guard at line 123 rejects creation if a pending/in_progress orchestration task already exists, so the chain is single-threaded.)

**Termination:** when `parse_task_creation_plan.py --next-uncreated-package` exits 3 (all plan entries created), the script instead writes the **validation orchestration task** at `{today}_explore_validate-release-{version}` using `_VALIDATION_GOAL_TEMPLATE` (orchestrate-task.py:243–299). That task's ACs do NOT include the regeneration line — it is the chain terminator. It hands off to `release-begin-impl-finalize`.

**Inheritance from parent:**

- `after:` — explicit. Each successor's frontmatter has `after: ["<previous_task_id>"]` via the `--after-task` flag (template line 203, `_build_after_field`).
- `plan_path:` — passed forward verbatim (`--plan-path`).
- `target_release:` — re-read from `RELEASES.md` (`status: active`) each run, not copied from parent. So if the active release changes mid-chain, the chain follows.
- `parent_requirement: REQ-PROC-035` — hard-coded constant in `create_orchestration_task.py` (line 42). Every orch task has the same parent.
- `task_id` — freshly allocated via `scripts/tasks/allocate_task_id.py` (line 392). No relation to the parent's task ID.
- `covers`, `awaiting`, `awaiting_note` — empty.

**The "self-perpetuating" string** appears in `scope_description` of the impl template: `"Orchestration: create impl tasks for package … on release … . Same-package per session; chain self-perpetuates."` (line 209). That phrase is the search anchor — no other tasks in the repo use this pattern. `find_orchestration_tasks.py` and `create_orchestration_task.py` itself use the structural signature (`scope_description` starts with `"Orchestration:"` AND `target_release` is set AND status is pending/in_progress) to identify them.

**A SessionStart locking mechanism** (`fcntl.flock`, lines 309–319) prevents two parallel orchestrator sessions from creating duplicate successors.

---

## §5 task-create skill integration: existing state and required gaps

**Existing references:**

- `.claude/skills/task-create/SKILL.md` — **no mention** of `pending_feedback`, `question.md`, `answer.md`, or self-regenerating tasks. The skill is purely about classification, ID allocation, goal.md authoring, and coverage tracking.
- `.claude/skills/task-create-code/skill.md` — mentions `question.md` four times: lines 80, 399, 441, 446. All are about writing a question.md to the orchestration task's folder when `parse_task_creation_plan.py` fails or there is a plan-mode mismatch. Line 448 says: `**When auto-accept is NOT safe** — use pending_feedback instead (see claude-automated-mode skill for the question.md procedure)`. So `task-create-code` defers entirely to `claude-automated-mode` for the Q&A protocol.
- `.claude/skills/claude-automated-mode/skill.md` — owns the procedure (see §1, §2 above). It is the single source of truth for "how to write a question.md".

**What would need to be added** to support "task created with a pre-populated question.md":

1. `task-create` skill needs a new option ("create with pending question") that:
   - After writing `goal.md`, also writes `automation/pending_feedback/<TASK_ID>/question.md` with `session_id: NEW_SESSION_REQUIRED`, `account: <pick-any-valid>`, `task_id: <newly-allocated>`, `status: awaiting_answer`, `asked_at: <now>`, `skill: task-create`.
   - Copies `TEMPLATE_answer.md` to `<TASK_ID>/answer.md`.
   - Sets `goal.md` `status: pending` (the orchestrator's `is_awaiting_answer.py` check works regardless of status because it only inspects `pending_feedback/`).

2. `task-create` MUST NOT mark the task `in_progress`. The orchestrator currently expects:
   - For `find_answered_feedback`-driven resume of `NEW_SESSION_REQUIRED`: the task is queryable by `grep -rl "^task_id: <id>" requirements_tasks --include=goal.md` (orchestrate.py:1727) — no status precondition.
   - For `find_resumable_session`-driven resume: `status: in_progress` AND `session_id` set (lines 936–944). This path does NOT apply to pre-session tasks because their session_id is `NEW_SESSION_REQUIRED`, which is explicitly excluded for that scanner — but is accepted by `find_answered_feedback`.

3. No changes to `next_tasks.py` are needed. `load_pending_feedback_ids` already removes the task from the runnable queue.

4. No changes to `orchestrate.py` are needed for the basic flow. The fresh-session path (`run_fresh_session_with_answer`) is the perfect fit: the orchestrator launches a brand-new session with the prompt `"Then do <goal.md path>. Context: a pending question was already answered. The answer was: <answer>. Proceed from there."` (orchestrate.py:715–722).

---

## §6 Integration-test requirements pathway

**Question:** which skill should own "create a non-functional epic for integration tests for this user flow"?

**Findings on `requ-derive-from-flow`:**

- Invoked manually with `"Use derive-requirements-from-flow skill for [path/to/flow.md]"` (line 10). Triggered by a person; NOT auto-fired by any release/lifecycle skill.
- Output is one goal.md per flow gap, each targeting either a new requirements path or an existing one. The skill produces ONLY `type: explore` goal.md files (template at lines 521–594). It never directly creates non-functional epic requirement folders — that work happens in the downstream `requ-explore` skill that processes each generated goal.md.
- The skill's gap taxonomy (line 267) is: `exists_complete`, `exists_needs_update`, `exists_placeholder`, `new_needed`, `decision_needed`, `decision_needed_exploration`, `foundation_gap`, `out_of_scope`. There is no taxonomy slot for "integration-test coverage for this flow". A new "integration-test gap" type could be added to Phase 2 Opus instructions, with a fixed target path under `requirements_tasks/non-functional/`.
- The flow-to-requirements scan in Phase 1.3 only looks at `requirements_tasks/functional/**/requirements.md` and `requirements_tasks/non-functional/**/requirements.md`. It would naturally find existing integration-test requirements if they live under `non-functional/`.

**Findings on `release-begin-impl-finalize`:**

- Phase 1 verifies impl-task coverage per package; Phase 3 spawns one semantic-validation agent per feature. Neither phase considers integration-test requirements. Adding integration-test coverage here would be a NEW phase ("Phase 2.5: integration-test requirement coverage check") that runs script-driven against a known integration-test epic location.

**Recommendation:**

`requ-derive-from-flow` is the better home for "create a non-functional epic for integration tests for this user flow." Reasons:

1. It already reads the flow.md and knows which scenarios, steps, exceptions, and screens are in scope — exactly the input an integration-test requirement set needs.
2. It already produces `type: explore` goal.md files targeted at non-functional paths; adding a per-flow integration-test exploration task is a small extension of Phase 4.2.
3. It runs early in the per-flow lifecycle (before any code exists), so integration-test requirements are produced when they are still useful as design constraints.

`release-begin-impl-finalize` is the wrong home — by the time it runs, all impl tasks already exist; integration-test requirements would arrive too late to inform what those tasks build.

**What would need to change in `requ-derive-from-flow`:**

1. Phase 2 Opus matrix instruction (around line 261): add a side-output instruction "For each flow, always emit one row of status `integration_test_needed` targeted at a fixed path under `requirements_tasks/non-functional/integration_tests/<flow_id>/` UNLESS such a requirement already exists." This keeps integration-test coverage in the same matrix as functional gaps so the user sees it at the Phase 3 review.
2. Phase 4.2 goal.md template needs a small variant for the integration-test rows: scope text like "Define what integration-test coverage this flow requires (happy path + each exception)."
3. The "Suggested Package" rule (line 339) for integration-test rows: use the same package as the primary functional gap of the flow, so they ship together.

No change to `release-begin-impl-finalize` is required — Phase 1 coverage audit already iterates over every package's requirements, so integration-test requirements would be picked up automatically once they exist.

---

## §7 Reference paths to cite from goal.md updates

- `automation/pending_feedback/README.md` — developer-facing protocol overview.
- `automation/pending_feedback/TEMPLATE_question.md` — canonical frontmatter shape.
- `automation/pending_feedback/TEMPLATE_answer.md` — sentinel marker `<!-- AWAITING_HUMAN_ANSWER -->`.
- `automation/pending_feedback/TASK-PROC-006-02/question.md` — live worked example.
- `scripts/automation/orchestrate.py` — orchestrator source of truth. Key landmarks:
  - `find_answered_feedback` lines 1362–1419 (detects answered Q&A).
  - `process_answered_feedback` lines 1667–1819 (resume/fresh-session decision).
  - `run_resume_session` lines 663–694, `run_fresh_session_with_answer` lines 697–738.
  - `NEW_SESSION_REQUIRED` handling lines 1386–1388, 1719–1734.
  - `update_goal_session_fields` lines 473–517 (writes `session_id` into `goal.md`).
  - `check_queue_state` lines 2058–2105 (queue gating using `is_awaiting_answer.py`).
- `scripts/tasks/is_awaiting_answer.py` — single-task awaiting check used by the orchestrator.
- `scripts/tasks/next_tasks.py` lines 58–122 — queue-level pending_feedback filter (`load_pending_feedback_ids`, `_ANSWER_TEMPLATE_SENTINEL`).
- `scripts/automation/terminate_session.sh` — script the AI calls after writing question.md.
- `.claude/skills/claude-automated-mode/skill.md` lines 76–139 — canonical procedure for writing question.md.
- `.claude/skills/claude-autorun/skill.md` — start/stop/status of the orchestrator (no Q&A logic itself).
- `.claude/skills/claude-ask/skill.md` — UNRELATED (Opus research skill, not the Q&A mechanism).
- `.claude/skills/release-begin-impl/skill.md` Phase 6 step 6.3 — first invocation of `create_orchestration_task.py`.
- `.claude/skills/release-begin-impl-finalize/skill.md` — chain terminator handoff.
- `scripts/tasks/create_orchestration_task.py` — source of truth for the self-perpetuating chain:
  - `_GOAL_TEMPLATE` lines 191–241 (impl orch task body, including the regeneration AC).
  - `_VALIDATION_GOAL_TEMPLATE` lines 243–299 (chain terminator).
  - `find_existing_orchestration_task` lines 123–143 (duplicate guard).
  - `_build_ac_block` lines 169–188 (regeneration AC line construction).
- `.claude/skills/task-create/SKILL.md` — does NOT currently know about pending_feedback or self-regen.
- `.claude/skills/task-create-code/skill.md` lines 80, 399, 441, 446, 448 — task-create-code's `question.md` references (defers to `claude-automated-mode`).
- `.claude/skills/requ-derive-from-flow/skill.md` — recommended home for the integration-test-requirements extension; Phase 2 lines 261–355, Phase 4.2 lines 499–594.
