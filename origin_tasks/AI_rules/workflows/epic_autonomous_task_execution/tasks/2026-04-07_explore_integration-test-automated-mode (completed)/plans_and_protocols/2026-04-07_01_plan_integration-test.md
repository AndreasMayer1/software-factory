# Plan: Integration Test — Autonomous Task Execution System

## Overview

End-to-end validation of the full orchestrator + automated session pipeline using 3 dummy tasks.

## Execution Plan

### Step 1: Infrastructure changes
- Add `--max-tasks N` argument to `orchestrate.py` (missing; required by goal.md)
- Create dummy tasks under `requirements_tasks/automation_test/` (scanned by next_tasks.py)

### Step 2: Dummy Tasks
- **Dummy A** (TASK-TEST-001-01): Write `automation/test_outputs/dummy_a.txt` with "DUMMY_A_DONE"
- **Dummy B** (TASK-TEST-001-02): Write `automation/test_outputs/dummy_b.txt` with "DUMMY_B_DONE"
- **Dummy C** (TASK-TEST-001-03): Feedback gate test — requires human decision, triggers question.md + terminate

All at urgency=5, impact=5 (priority=55) → appear above all real tasks in queue.

### Step 3: Run orchestrator
```
python3 scripts/automation/orchestrate.py --max-tasks 3 --accounts gmail,web,gmail2
```

Expected behavior:
- Session 1: picks dummy A → executes → completes
- Session 2: picks dummy B → executes → completes
- Session 3: picks dummy C → detects human input needed → writes question.md → terminate_session.sh exits → session terminates
- Orchestrator sees 3 sessions processed → stops

### Step 4: Haiku evaluation agent
Reads: reports/, session_outputs/, pending_feedback/, test_outputs/
Produces: structured pass/fail verdict

### Step 5: Auto-fix loop (max 3 iterations)
Track fixes in `iteration_log.md`.

## Key Risk Areas

- `code-simple` skill trying to run Flutter tests for text-file tasks → may be no-op since no .dart files changed
- Task C: session must write question.md BEFORE calling terminate_session.sh
- Orchestrator `--max-tasks` must count sessions (not just successes)
- next_tasks.py must surface dummy tasks above all real tasks (priority 55 > all current tasks max 45)

## Location

- Dummy tasks: `requirements_tasks/automation_test/tasks/`
- Test outputs: `automation/test_outputs/`
- Orchestrator outputs: `automation/session_outputs/`, `automation/reports/`
