# Plan: overrides-first (TASK-PROC-042-12)

## Objective
Refactor `scripts/tasks/next_tasks.py` so that it returns ONLY tasks from
`.claude/task_ordering_priority_override.txt` until all of them are completed.

## Approach: inline

## Changes

### 1. scripts/tasks/next_tasks.py

Replace the current override block (lines 531–543) which prepends override tasks
before normal ranking. New behavior:

- Compute `override_nonterminal`: override tasks whose status NOT IN TERMINAL_STATUSES
- If `override_nonterminal` is non-empty → override mode is active:
  - `override_runnable` = nonterminal AND status NOT IN EXCLUDED_STATUSES AND NOT is_blocked()
  - If runnable exist: `ranked = override_runnable` (only override tasks surfaced)
  - If none runnable: print blocked message (NOT matching orchestrator regex) → sys.exit(0)
- If `override_nonterminal` is empty → normal ranking (no change)

### 2. .claude/task_ordering_priority_override.txt

Add a behavior-description comment to the header explaining the blocking semantics.

### 3. scripts/tests/test_next_tasks.py

Add tests for:
- override blocks normal tasks (runnable override task surfaces, normal task suppressed)
- all-blocked override tasks: sys.exit(0) with informational message (no task format lines)
- all-terminal override tasks: normal ranking resumes

## Orchestrator safety
The blocked-tasks message uses plain text (no `1. [TASK-...]` format), so
`pick_next_task_for_session`'s regex finds zero entries → returns None → no
spurious fresh session launched.
