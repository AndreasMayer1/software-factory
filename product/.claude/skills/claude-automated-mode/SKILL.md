---
name: claude-automated-mode
description: Load automated mode rules for unattended session execution
tools: Bash, Write
model: inherit
---

You load and apply the rules for running in automated (unattended) mode.

## Detection

Automated mode is active when **both** are true:
- `CLAUDE_AUTOMATED_MODE=1` (env var)
- `automation/.automated_mode` exists

Verify:
```bash
[ "$CLAUDE_AUTOMATED_MODE" = "1" ] && [ -f "automation/.automated_mode" ] && echo "AUTOMATED" || echo "MONITORING"
```

If MONITORING — stop immediately. These rules do not apply.

## Bootstrap: Release Build-Out Check

Run at session start, before "Do next task":

```bash
python3 scripts/tasks/next_tasks.py 2>&1
```

<!-- TRANSITION BLOCK — Cases A and B removed (TASK-PROC-035-08, Group 4)

Removal condition: Cases A and B were removed because the new self-perpetuating
orchestration task template (Group 3) makes them redundant:

- Case A (uncovered ACs → create orchestration task): the chain self-perpetuates
  via create_orchestration_task.py invoked inside each orch task's own ACs. No
  bootstrap trigger is needed to create the next orchestration task.

- Case B (all packages covered → create validation task): when all packages are
  covered, create_orchestration_task.py creates a validation orchestration task
  instead of returning Exit 3. The chain handles it.

GUARD: Do NOT delete this transition block (or re-introduce Cases A/B logic in
any reduced form) until ALL of the following are true:
  1. The new self-perpetuating orchestration task template (Group 3) is deployed.
  2. All in-flight old-template orchestration tasks have reached terminal status.

To verify (2), run:
  python3 scripts/tasks/find_orchestration_tasks.py --status pending,in_progress

If that command returns any old-template orch tasks, keep this transition block
in place; the bootstrap is intentionally minimal during the transition cycle.
-->

**Case C — all packages covered, all completed, no open questions**: Check:
   ```bash
   # Any pending impl tasks for active release?
   python3 scripts/tasks/next_tasks.py --type impl 2>&1 | head -5
   # Any unanswered questions?
   ls automation/pending_feedback/*/question.md 2>/dev/null
   # Validation report exists?
   find requirements_tasks/ -name "validation_report.md" 2>/dev/null | head -1
   ```
   If no runnable impl tasks AND no unanswered questions AND a validation report exists AND all 0.0.1 packages have non-terminal impl tasks → write release-complete summary to `automation/release_status/<version>_complete.md`:
   ```markdown
   # Release <version> Complete
   Date: <today>
   All packages covered. Impl tasks created and completed. Validation passed. No open questions.
   Next step: Run /release-begin-impl-finalize for final review, then /release to cut the release.
   ```
   Then proceed normally (orchestrator will stop with queue_empty on its own).

**Case D — runnable tasks exist**: Skip bootstrap entirely. Proceed to "Do next task".

## The One Rule

**Never ask the user a question.** This covers:
- Text output that ends with "?" or asks for confirmation
- The `AskUserQuestion` tool
- Any checkpoint in any skill that says "ask the user" or "wait for confirmation"

## Responsibility Boundary — Orchestrator vs Session

The orchestrator and the session it launches have strictly separated responsibilities. Do not cross this line.

**The orchestrator owns** (the session must never do these): scheduling; deciding *when* a task runs or resumes; rate-limit / reset-time tracking; account rotation; waiting out a limit; restarting a session after a reset.

**The session owns**: doing the task work, and reporting *why* it cannot proceed. A session has exactly four valid exits:
1. `task-complete` — the work is done.
2. Write `question.md` for a genuine human decision, then terminate (see § "When Human Input Is Genuinely Needed").
3. Re-emit a rate/session-limit line verbatim, then terminate (see § "When a Spawned Agent Hits a Rate / Session Limit").
4. State in one line why it cannot make progress right now, then terminate.

**Prohibited — the session must NEVER**: call `ScheduleWakeup`; set any future wakeup; "wait out" or sleep through a limit; reason about reset clocks (e.g. "it's before the 17:50 reset, I'll come back later"). Scheduling is not the session's job. A self-scheduled wakeup is a session-local timer the orchestrator cannot see or honor; it makes the session second-guess the orchestrator's timing and produces no-op resumes the orchestrator counts as failed attempts. If you cannot advance, take exit 3 or 4 and terminate — the orchestrator decides when to bring the task back.

## When a Spawned Agent Hits a Rate / Session Limit

A rate/session limit is a transient infrastructure condition, NOT a human-decision
gate. It must be propagated to the orchestrator — never turned into a question.

**Detection.** A spawned agent (Task tool) — or any nested agent it spawned — returns
a failure whose text contains a usage-limit marker: `hit your` together with `limit`,
or `session limit`, `usage limit`, or `resets <time> (<timezone>)`. If two or more
parallel agents fail this way at once, it is the same condition — handle it once.

**Why (do not collapse this into the question path).** The orchestrator detects
throttling ONLY by scanning the main session's stdout for the limit message
(`orchestrate.py:classify_session_failure`). A `pending_feedback` question hides the
limit from it AND makes `find_resumable_in_progress_task` skip the task as
"awaiting a human" — so it stalls indefinitely on a human who was never needed.

**Procedure (this OVERRIDES the pending_feedback path below):**

1. Do **not** write `question.md` / copy `answer.md`. Do **not** keep doing task work
   (the account is throttled — retries just burn the cap). Leave the task
   `status: in_progress` and do not commit anything.
2. Re-emit the agent's limit message **verbatim** as your final assistant text. Copy it
   exactly — do not paraphrase, and keep the parentheses around the timezone, e.g.:
   `You've hit your session limit · resets 12:40am (Europe/Berlin)`
   (The substrings `hit your` + `limit` make the orchestrator classify it as
   `rate_limited`; the `resets H[:MM]am/pm (Timezone)` shape lets it parse the exact
   reset — if absent it safely falls back to a ~65-minute wait.)
3. Terminate:
   ```bash
   bash scripts/automation/terminate_session.sh
   ```

The orchestrator waits for the reset, rotates accounts, and resumes this `in_progress`
task — which re-spawns the agents from where the pipeline left off.

**On resume, the same rule applies — do not self-schedule.** When the orchestrator
resumes this task, re-attempt the work immediately. If a limit you depend on is still
active (a re-spawned agent fails again with a limit line), or you otherwise cannot
advance yet, re-emit the limit line verbatim (or state the blocker in one line) and
terminate — exactly as on the original spawn. Do NOT call `ScheduleWakeup` or wait for a
reset; the orchestrator owns reset timing and will resume you again. (See § "Responsibility
Boundary — Orchestrator vs Session".)

## When Human Input Is Genuinely Needed

**FIRST — rate-limit guard.** If the checkpoint was triggered by a spawned agent failing
on a rate/session limit (see § above), STOP — that is not human input. Follow
§ "When a Spawned Agent Hits a Rate / Session Limit" instead of this procedure.

Replace every (genuine) user-confirmation checkpoint with this procedure:

**MANDATORY pre-condition**: Before writing `question.md`, verify that `task-start`
was called for the current task. The task MUST be `in_progress` with `session_id` set
in `goal.md`. Check:
```bash
GOAL=$(grep -rl "^status: in_progress" requirements_tasks/ --include="goal.md" | head -1)
SESSION_ID=$(grep -m1 "^session_id:" "$GOAL" 2>/dev/null | awk '{print $2}')
```
If `GOAL` is empty or `SESSION_ID` is empty: **STOP**. Call `task-start` on the
specific goal.md for this task first (e.g. `task-start requirements_tasks/.../goal.md`).
`task-start` marks the task `in_progress` and writes `session_id` — both required
for the orchestrator to resume after the user answers.

**Step 1 — Get task metadata:**
```bash
GOAL=$(grep -rl "^status: in_progress" requirements_tasks/ | grep goal.md | head -1)
TASK_ID=$(grep -m1 "^task_id:" "$GOAL" | awk '{print $2}')
SESSION_ID=$(grep -m1 "^session_id:" "$GOAL" | awk '{print $2}')
```

**Step 2 — Write question.md:**

File: `automation/pending_feedback/<TASK_ID>/question.md`

```markdown
---
task_id: <TASK_ID>
session_id: <SESSION_ID>
account: <$CLAUDE_SESSION_ACCOUNT>
status: awaiting_answer
asked_at: <date -u +%Y-%m-%dT%H:%M:%SZ>
skill: <name of current skill>
---

# Pending Question

<Full question with all relevant context. The developer has no session history —
include the proposal, the options, and what you need confirmed to proceed.>
```

**Step 3 — Copy answer template:**

```bash
cp automation/pending_feedback/TEMPLATE_answer.md automation/pending_feedback/<TASK_ID>/answer.md
```

This copies the template (which contains an explicit prohibition against automated writing) so the developer only needs to open the file and write their answer. The orchestrator treats a file that still matches the template as "not yet answered".

**MANDATORY for follow-up questions**: If `answer.md` already exists and contains a human answer (the developer answered a previous question and this session is asking a follow-up), the `cp` command above MUST still run — it overwrites the stale answer with the template. Skipping this step leaves the old answer in place; the orchestrator then re-resumes the session every iteration with the stale answer, causing an infinite loop.

**CRITICAL**: Never write content to `answer.md` yourself. The template's prohibition text is there precisely so you read it if you ever attempt to overwrite the file. Automated sessions writing to `answer.md` breaks the human-in-the-loop safety protocol.

**Step 3.5 — Commit task-caused changes** (REQ-PROC-041-04 AC-08):

Commit every change caused by the work on this task — including the freshly written `question.md` and the copied `answer.md`. Do NOT sweep pre-existing uncommitted changes from before the session started.

Stage explicitly (no `git add -A`):
```bash
git add automation/pending_feedback/<TASK_ID>/question.md
git add automation/pending_feedback/<TASK_ID>/answer.md
# Plus every other file the session modified for this task (goal.md, plans_and_protocols/, lib/, test/, etc.).
# List them explicitly — `git status` shows what is new vs. pre-existing.
```

Set `SKIP_QUALITY_GATES=1` for this commit (the escalation commit is a WIP — gates will run again when the task resumes after the human answers; without the bypass the pre-commit hook blocks the commit when `lib/` files are staged and gates are RED, leaving a dirty tree that bleeds into subsequent sessions):
```bash
export SKIP_QUALITY_GATES=1
```

Then invoke the `claude-commit` skill with:
- type: `chore`
- scope: `automation`
- subject: `pause session for <TASK_ID> — <skill>` (where `<skill>` is the name of the skill that triggered the pause, e.g. `requ-explore`, `code-bugfix`)
- body must include: `SKIP_QUALITY_GATES=1 (WIP escalation commit)`

No `git status` cleanliness check — pre-existing untouched changes may legitimately remain in the working tree.

**Step 4 — Terminate:**
```bash
bash scripts/automation/terminate_session.sh
```

## When NOT to Use pending_feedback

Skills that run to completion without needing input (implementation, commits, tests, index updates) should just continue normally. Only use `pending_feedback` when the work genuinely cannot proceed without a human decision.
