---
name: task-start
description: Resolve, gate, mark in_progress, then dispatch via claude-route.
tools: Read, Bash, Edit, Skill, AskUserQuestion
model: inherit
---

Canonical single entry point for executing any already-created task. Phases: resolve → validate → gate → mark → dispatch.

## P0 — Resolve reference

| Input form | Action |
|------------|--------|
| `path/to/goal.md` | Use path as-is |
| `TASK-ID` (e.g. `TASK-PROC-027-25`) | `grep -rl "task_id: TASK-PROC-027-25" requirements_tasks/` → get path |
| `"next task"` / `"next impl task"` | Run `python3 scripts/tasks/next_tasks.py` (add `--type impl` for impl-only); display **full output to user**; see candidate loop below |
| free-text description | AskUserQuestion: ask user to specify a TASK-ID or goal.md path |

**No match**: tell user (interactive) / stop (automated).

**"next task" candidate loop** (top-to-bottom from script output):
- Status `in_progress` or `active`: run `python3 scripts/tasks/is_awaiting_answer.py --task-id <id>`
  - Exit 1 (awaiting answer): skip — move to next candidate
  - Exit 0: automated → proceed; interactive → run `python3 scripts/tasks/goal_preview.py <path>`, ask "Work on this?" (Yes → proceed; No → next)
- Status `pending`: proceed immediately
- All 4 skipped: tell user; suggest `python3 scripts/tasks/next_tasks.py --count 8`

**"next task" AC coverage check**: if output contains `WARNING: UNCOVERED ACs` AND top candidate is `Type: impl` → ask:
- Option 1 (recommended): "Create an exploration task first"
- Option 2: "Start implementation anyway"
If Option 1: invoke `task-create` with goal describing missing tasks; stop.

## P1 — Load & validate

1. Confirm goal.md file exists (error if not)
2. Run: `python3 scripts/quality/validate_against_schema.py <goal.md> .claude/schemas/goal_metadata.yaml`
3. Parse frontmatter: `status`, `after`, `awaiting`, `task_id`, `opus_recommended`
4. **Failure** (missing or off-schema): HALT with exact schema error; do not proceed

## P2 — Pre-condition gates

**P2a — completed check**
- `status: completed` → interactive: warn "Task already completed — re-run anyway?" (Yes → continue; No → stop); automated: skip to next candidate
- `pending` / `in_progress` / absent → proceed

**P2b — awaiting check**
```bash
python3 scripts/tasks/is_awaiting_answer.py --task-id <TASK_ID>
```
- Exit 1: interactive → HALT "Task is parked on developer answer: `<awaiting_note>`"; automated → skip

**P2c — after-deps check**
- For each TASK-ID in `after:`:
  - Find its goal.md: `grep -rl "task_id: <DEP-ID>" requirements_tasks/ | head -1`
  - Check `status:` field in that file; also treat as completed if the task folder name ends in `(completed)`
- Any dep not `completed`: interactive → warn "Depends on unfinished `<TASK-ID>` — proceed anyway?" (Yes → continue; No → stop); automated → skip

## P3 — Mark started

1. If `status: pending` or absent: Edit goal.md → `status: in_progress`, add `started: <YYYY-MM-DD today>`
2. Check automated mode: `echo $CLAUDE_AUTOMATED_MODE`
   - If `1`: read `$CLAUDE_SESSION_ID` and `$CLAUDE_SESSION_ACCOUNT` via Bash; Edit goal.md → write `session_id:` and `session_account:` after `started:` (add if absent, update if present)
3. **Ordering is load-bearing**: P3 MUST complete before P4 — `claude-automated-mode` requires `in_progress` + `session_id` before any `pending_feedback` write

## P4 — Delegate

Invoke `claude-route` skill with the validated goal.md **path** only.
`claude-route` receives a ready, schema-valid, `in_progress` goal.md; it does type→skill match + opus-check + invoke.
