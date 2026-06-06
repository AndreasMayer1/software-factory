---
task_id: TASK-PROC-030-06
type: explore
status: completed
started: 2026-04-02
completed: 2026-04-03
created: 2026-04-02
parent_requirement: REQ-PROC-030
urgency: 4
urgency_reason: U4-DEP
impact: 4
impact_reason: I4-UX
effort: S
after: []
awaiting: []
---

# Explore: target_package Propagation Gap for Impl Tasks

## Context

When `requ-explore` runs and the user defers package assignment (answers "skip" or "let's wait"), the ACs in the resulting requirement have no `target_package`. This is intentional — a batch package assignment is planned for later.

The potential gap: if `task-create-impl` is invoked for those ACs before the batch assignment runs, the impl task inherits nothing (rule 3 fires, user can skip), and the impl task is created with no `target_package`. When the batch assignment later assigns packages to the ACs, the already-created impl tasks are NOT updated.

Result: impl tasks are permanently orphaned from any package — they never surface in `next_tasks.py` in the correct package context.

A second scenario: batch assignment runs first, but `task-create-impl` is called after. In this case inheritance works correctly (rule 2). So the gap only manifests when task creation races ahead of package assignment.

## Goal

1. **Confirm** whether this gap actually exists in the current skill set (trace the full flow: `requ-explore` → deferred packages → `task-create-impl` → batch assignment → `next_tasks.py`).

2. **Identify** all places where `target_package` on impl tasks can become stale or absent after package assignment happens on the parent requirement's ACs.

3. **Propose a fix** — options to consider:
   - Block `task-create-impl` from creating impl tasks until all covered ACs have `target_package` assigned
   - Add a "sync task packages" step to `requ-explore` Step 2: after assigning `target_package` to ACs, scan for existing goal.md files whose `covers.acceptance_criteria` reference those ACs and update their `target_package` field
   - Add a standalone script / skill action that propagates AC package assignments to all covering tasks on demand

4. **Recommend** which fix (or combination) is least disruptive and most consistent with the existing skill design.

## Relevant Files

- `.claude/skills/requ-explore/skill.md` — Step 2 Package Assignment
- `.claude/skills/task-create-impl/skill.md` — Section 3.4 Package Inheritance
- `.claude/skills/task-create/skill.md` — Package Inheritance section
- `scripts/next_tasks.py` — ranking logic (`_is_blocked`, `rank_tasks_by_package`)

## Acceptance Criteria

- [ ] Gap confirmed or ruled out with a concrete example trace
- [ ] If confirmed: fix proposal written to `plans_and_protocols/`
- [ ] If fix requires skill changes: specific edit locations identified (file + section)
- [ ] If fix requires a new script: scope defined
