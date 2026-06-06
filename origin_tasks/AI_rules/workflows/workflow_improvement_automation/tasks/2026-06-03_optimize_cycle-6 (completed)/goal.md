---
task_id: TASK-OPT-0-6
type: optimize
parent_requirement: REQ-PROC-006
status: completed
created: 2026-06-03
started: 2026-06-03
completed: 2026-06-03
session_completed_at: 2026-06-03T20:45:00Z
awaiting: []
scope_description: "Autonomous claude-optimize cycle: consume one optimize event, produce one auto-blocked improvement task or a documented no-op."
session_id: cf284aaa-258f-4a71-80e5-6cff96274f72
session_account: web
---
# Goal: run one claude-optimize producer cycle

## Objective

Monitors emitted at least one event into `.factory/optimize/events/`.
Run the claude-optimize producer skill once: select the highest-priority
candidate, produce exactly one auto-blocked improvement task (via
`create_optimize_task.py`) or a documented no-op, and commit `runs.tsv`
and `state.json` (REQ-PROC-006 §Producer Paradigm, §Commit Behavior).

## Source

Created autonomously by `scripts/optimize/run_monitors.py` (REQ-PROC-006 §Monitor-Based Detection). This cycle task runs
unattended (`awaiting: []`); only the improvement task it produces is
auto-blocked (`awaiting: ["user-unblock"]`, G-INV-1 / AC-04).
