---
task_id: TASK-PROC-042-12
type: impl
parent_requirement: REQ-PROC-042
urgency: 5
impact: 5
status: completed
effort: S
created: 2026-05-26
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T12:15:27Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Refactor `scripts/next_tasks.py` so that it does not return any other tasks than those specified in `flutter_app/.claude/task_ordering_priority_override.txt` until all of the tasks defined in the file are completed."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
session_id: f36b6683-eba4-4a0e-b2be-299e5bd075ec
session_account: gmail

---
# Goal: Refactor next_tasks.py to block until task_ordering_priority_override.txt is completed

## Objective

Refactor `scripts/next_tasks.py` so that it does not return any other tasks than those specified in `flutter_app/.claude/task_ordering_priority_override.txt` until all of the tasks defined in the file are completed.

The script must retrun a message stating that the tasks in `flutter_app/.claude/task_ordering_priority_override.txt` have to be completed first beofre any other tasks surface. It can happen that the tasks on the override list are blocked by other tasks and the script can't return any task that is pending and not blocked. In that case the script must also return which tasks on the list are currently blocked. Blocked can be because of awaits or because of after dependencies. 

the `flutter_app/.claude/task_ordering_priority_override.txt` file must contain a statement in the header as comment that states how it behaves.

## Acceptance Criteria

- [x] No other behaviour changed
- [x] while there are still pending or in_progress tasks in flutter_app/.claude/task_ordering_priority_override.txt: returns only tasks listed in the file 
- [x] if all tasks that are not completed or in_progress in flutter_app/.claude/task_ordering_priority_override.txt are blocked (awaiting or after): return a message and list all blocked tasks 
- [x] the orchestrator (`scripts/automation/orchestrate.py`) continues to work correctly: when `next_tasks.py` returns no task IDs (because all override tasks are blocked), the orchestrator must stop gracefully — the blocked-tasks message in the output must NOT be parsed as a list of runnable tasks
