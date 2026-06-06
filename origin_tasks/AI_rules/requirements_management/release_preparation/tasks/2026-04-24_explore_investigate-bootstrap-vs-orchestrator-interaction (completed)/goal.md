---
task_id: TASK-PROC-035-04
type: explore
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-24
effort: S
created: 2026-04-24
started: 2026-04-24
after: []
awaiting: []
awaiting_note: ""
target_package: "Transfer Data Model"
covers:
  acceptance_criteria: []
  sections: [SEC-05]
scope_description: "Investigate why the bootstrap guard in claude-automated-mode permanently blocks orchestration task creation when unrelated explore tasks are runnable. Analyse the full interaction between claude-automated-mode (bootstrap Cases A–D) and the task-create-code-orchestrator skill. Determine the minimal correct fix and document the required changes."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: b1ea3b31
  file: ../requirements.md
---

# Goal: Investigate Bootstrap Guard vs. Orchestrator Interaction

## Objective

The bootstrap rule in `claude-automated-mode` is designed to automatically create implementation task orchestration tasks when the runnable task list is empty and uncovered ACs exist. In practice, the rule never fires because unrelated explore tasks (e.g. TASK-PROC-027-*, TASK-PROC-029-05) are always present in the task list, keeping Case D active indefinitely.

Investigate whether this is a design flaw, a documentation gap, or expected behaviour that simply needs refinement. Determine the minimal correct fix.

## Background

**Observed behaviour** (2026-04-24): After TASK-PROC-035-03 completed and created TASK-FUNC-007-04-11, no subsequent orchestration task was created. `next_tasks.py` still reports uncovered ACs for "Adaptive Scanner Settings", but the bootstrap never fires because process explore tasks (TASK-PROC-027-*, TASK-PROC-029-05) are always runnable.

**Documented behaviour** (REQ-PROC-035, SEC-05 "Task Creation Process"):
> "Pending explore tasks — including requirements-authoring or flow-writing tasks — prevent premature task creation (they appear in `next_tasks.py` output and keep the list non-empty)."

This was intended as a safety guard: explore tasks might change requirements, so impl task creation should wait. But the guard does not distinguish between explore tasks that could affect the active release and those that are completely unrelated.

**Relevant files**:
- `.claude/skills/claude-automated-mode/skill.md` — Bootstrap Cases A–D
- `.claude/skills/task-create-code-orchestrator/skill.md` — Orchestrator skill
- `requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md` — REQ-PROC-035 (SEC-05)
- `automation/MONITORING_CRITERIA.md` — S21–S24 bootstrap monitoring signals

## Scope

### In Scope
- Read and analyse all four files listed above
- Determine: is the guard intentionally broad, or is it an oversight?
- Identify: under what conditions would Case A ever fire in a mature project with many open explore tasks?
- Evaluate two candidate fixes:
  1. **Narrow guard**: Case D only applies when there are runnable impl tasks for the active release (not any runnable task)
  2. **Scope-filtered check**: Case A checks `next_tasks.py --type impl` instead of the full task list
- Assess impact of each fix on `requirements.md` (SEC-05 guard rationale), `claude-automated-mode`, monitoring criteria, and `task-create-code-orchestrator`
- Document the recommended fix with exact wording changes needed in each affected file

### Out of Scope
- Implementing the fix (this is an explore task)
- Changing `next_tasks.py` ranking logic

## Acceptance Criteria

- [ ] Root cause clearly documented: why Case A never fires with open explore tasks
- [ ] The guard's original design intent is stated and evaluated against real-world behaviour
- [ ] At least two candidate fixes evaluated with pros/cons
- [ ] Recommended fix specified with exact change locations (file + section)
- [ ] Impact on REQ-PROC-035 SEC-05 wording assessed — does it need updating?
- [ ] Findings written to `plans_and_protocols/` before exiting

## Notes

The investigate session MUST write its findings to `plans_and_protocols/` before exiting — this is an explore task and its output is the protocol, not code changes.
