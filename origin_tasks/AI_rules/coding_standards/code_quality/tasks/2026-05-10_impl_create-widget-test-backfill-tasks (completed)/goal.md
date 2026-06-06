---
task_id: TASK-PROC-046-08
type: impl
parent_requirement: REQ-PROC-046
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 3
impact_reason: I3-PROC
status: completed
completed: 2026-05-19
session_completed_at: 2026-05-19T04:06:00Z
effort: S
created: 2026-05-10
after: [TASK-PROC-046-03, TASK-PROC-046-07]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Read the screens inventory produced by TASK-PROC-046-07 and use the task-create skill to create one impl task per screen-gap (or per logical batch of related screens), each scoped to add a widget test invoking tester.ensureSemantics() with the four AccessibilityGuideline checks."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: 88542c8e-69c8-40cf-93b5-a224c15eed94
session_account: gmail
---
# Goal: Create widget-test backfill tasks from screens inventory

## Objective

TASK-PROC-046-07 produces an inventory of screens that lack a widget test exercising `tester.ensureSemantics()`. This task converts that inventory into actual scheduled work: one impl task per gap (or per logical batch), each created via `task-create` so it appears in the queue alongside other ready work. Without this step, the inventory remains a passive document and the backfill never gets scheduled.

## Requirements Summary

REQ-PROC-046 AC-07 (every screen has at least one widget test that runs `tester.ensureSemantics()` against the four `AccessibilityGuideline` checks). The screens inventory (TASK-PROC-046-07 output) is the input.

Current requirements: ../../requirements.md

## Scope

### In Scope

- Read `plans_and_protocols/screens_inventory.md` from TASK-PROC-046-07.
- For each screen categorized as (b) "test exists but no semantics check" or (c) "no widget test":
  - Decide batching: a single screen with one form is a separate task; a related cluster (e.g. two onboarding screens, three settings sub-screens) may be one task.
  - Invoke `task-create` skill (or its scripts directly) to allocate a `TASK-FUNC-*` or `TASK-NFUNC-*` ID under the screen's owning feature requirement, with type `impl`, scope describing the widget test to add and **the full active set of accessibility checks per REQ-PROC-046 AC-07** — not just the four built-in `AccessibilityGuideline` calls. The accessibility-task-summary report (`2026-05-14_accessibility_task_summary.md`) shows that the previously-scoped four built-ins miss text scaling (REQ-NFUNC-002 AC-11), non-tap semantic labels (AC-09a), reduce-motion handling (AC-12), Simple-Mode parity (AC-02/03), keyboard navigation (AC-15), component-semantics roles (AC-16), and the linguistic-complexity gate (AC-14). Each created task's scope must enumerate every active AC its screen falls under, not a subset.
  - Set `after:` to `[TASK-PROC-046-03]` (analyzer config must land first so any test-smell rules are active during the backfill) and `[TASK-PROC-046-07]` (this very inventory).
- Record the list of created task IDs in `plans_and_protocols/created_tasks.md` so the backfill is traceable.
- If TASK-PROC-046-07 finds zero gaps: this task is a no-op. Record that fact and complete.

### Out of Scope

- Writing the widget tests themselves. Each created task does that.
- Modifying the inventory. If the inventory is wrong, fix it in TASK-PROC-046-07 and re-run.
- Cross-cutting refactors needed before testing is feasible (testability blockers identified in the inventory). Those become their own tasks, separate from the widget-test backfill.

## Acceptance Criteria

- [x] Every gap entry in the inventory has a corresponding scheduled task (or is bundled into a batch task with rationale).
- [x] `plans_and_protocols/created_tasks.md` lists every created task ID with a one-line description and a pointer to its goal.md.
- [x] Each created task has appropriate `after:` dependencies, urgency / impact inherited from the parent requirement, and a clear scope description.
- [x] If the inventory contained zero gaps, that is recorded explicitly. (N/A — inventory had 17 gaps; documented in created_tasks.md "No-Op Check" section.)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-07 | pending | Provides the inventory this task consumes |

## Notes

The size of this task is bounded by the inventory: 5 gaps → 5 task creations; 30 gaps → 30 task creations. Effort estimated as S because each task creation is mechanical (`task-create` does the heavy lifting) — but if the inventory is large, this task may take longer than expected.

Per `task-create` skill rules: each new task must use `allocate_task_id.py` (no hand-numbered IDs); each must have a populated `covers` field referencing the AC of the owning feature requirement that the screen serves; each must have a `target_package` if the screen is in a packaged feature.

Important — the user feedback memory `feedback_task_resolve_no_agent_for_simple_process.md` applies here: do not spawn an agent to do the read-and-create-tasks loop; do it inline. Spawning an agent for a clear procedural task is wasteful.
