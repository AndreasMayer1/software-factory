---
name: task-unblock-check
description: Investigate whether a blocked task can be unblocked
tools: [Read, Edit, Bash, Grep, Glob, AskUserQuestion]
model: inherit
---

You investigate whether a blocked task's external blocker is still valid and clear it if resolved.

## Invocation

- Default: `"Use task-unblock-check skill"` — iterates all blocked tasks, highest priority first
- Specific: `"Use task-unblock-check skill --task TASK-FUNC-007-02"` — single task only

## Steps

### 1. Load blocked task list

**If `--task TASK-ID` provided:**
```bash
python3 scripts/tasks/top_blocked_task.py --task TASK-ID
```
Exits 1 if not found or not blocked. Process that one task only (skip steps for "next task").

**If no task specified:**
```bash
python3 scripts/tasks/top_blocked_task.py --all
```
Exits 1 if no blocked tasks. Output is N task blocks separated by `---`, sorted highest priority first. Process each task in order.

### 2. For each task: resolve blockers

For each item in `AWAITING`:

| Pattern | Resolution |
|---------|-----------|
| `FLOW-NNN` | `grep -rl "id: FLOW-NNN" requirements_user_needs/` → read flow.md → show `review_status` |
| `REQ-*` | `grep -rl "id: REQ-*" requirements_tasks/` → read requirements.md → show `status` |
| `TASK-*` | `grep -rl "task_id: TASK-*" requirements_tasks/` → read goal.md → show `status` |
| free-text | Present `AWAITING_NOTE` verbatim, ask user if resolved |

### 3. Present and ask (per task)

```
[1/N] Task: TASK-ID — [name]
Blocker: [awaiting items]
Note: [awaiting_note]

Blocker artifact state:
  FLOW-003: review_status = approved
  ...

Still blocked? (yes / no / update-note / stop)
```

`stop` exits the loop early.

### 4. If unblocked

Edit goal.md:
- `awaiting: []`
- `awaiting_note: ""`
- `status: pending`

### 5. If "update-note"

Collect new note text, edit `awaiting_note` only. Task stays blocked.

### 6. After all tasks processed

Regenerate STATUS.md once:
```bash
python3 scripts/artifacts/generate_status_overview.py --blockers
```

Report summary: "X unblocked, Y still blocked, Z skipped."
