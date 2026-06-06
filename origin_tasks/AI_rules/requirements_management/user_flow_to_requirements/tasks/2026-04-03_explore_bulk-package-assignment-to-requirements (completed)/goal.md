---
task_id: TASK-PROC-030-08
type: explore
parent_requirement: REQ-PROC-030
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: After release-plan creates packages, there is no mechanism to bulk-assign them to existing unassigned requirements — requires tedious per-requirement requ-explore re-runs"
impact: 4
impact_reason: "I4-PAIN: Without bulk assignment, next_tasks.py cannot prioritize by package for any requirement written before release-plan ran"
status: completed
effort: S
created: 2026-04-03
started: 2026-04-03
completed: 2026-04-03
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and propose a bulk package assignment mechanism that propagates packages from RELEASE_BACKLOG.md to unassigned ACs in existing requirements"
requirements_version:
  commit: e9382676
  file: ../requirements.md
---

# Explore: Bulk Package Assignment from release-plan to Unassigned Requirements

## Context

After `release-plan` creates or formalizes packages in `RELEASE_BACKLOG.md`, existing
requirements written before those packages existed still have no `target_package` on their
ACs. The only current mechanism to assign packages to ACs is `requ-explore` Phase 2.4,
which runs interactively per-requirement.

This means that after running `release-plan`, a developer must re-run `requ-explore` on
each unassigned requirement individually to trigger package assignment — tedious and
error-prone when many requirements exist.

A related gap was explored in TASK-PROC-030-06 (sync requirements → tasks). This task
addresses the upstream gap: RELEASE_BACKLOG.md → requirements.

## Goal

1. **Confirm** the gap: verify there is no existing bulk assignment mechanism between
   `release-plan` and unassigned requirements (check `release-plan`, `requ-explore`,
   and any scripts).

2. **Identify** the right location for a fix:
   - New action in `release-plan` (e.g., "Action 6: Assign packages to unassigned requirements")?
   - New script `scripts/bulk_assign_packages.py` callable standalone or from skills?
   - Extension to `requ-explore` Phase 2.4 (batch mode)?

3. **Propose a design** for the bulk assignment workflow:
   - How does the user map packages to ACs/sections at scale?
   - Should it be interactive (per-AC) or rule-based (by requirement ID / release chunk)?
   - How does it interact with the `sync_task_packages.py` script from TASK-PROC-030-06?
     (Once requirements get packages, tasks must be synced too — the two fixes should compose cleanly.)

4. **Recommend** the least-disruptive implementation that is consistent with the existing
   skill design.

## Relevant Files

- `.claude/skills/release-plan/skill.md` — current release-plan actions
- `.claude/skills/requ-explore/skill.md` — Phase 2.4 Package Assignment
- `scripts/next_tasks.py` — `rank_tasks_by_package()` (shows what's broken without assignment)
- `scripts/migrate_target_release_to_package.py` — prior bulk migration script (reusable patterns)
- `requirements_tasks/process/AI_rules/requirements_management/user_flow_to_requirements/tasks/2026-04-02_explore_target-package-propagation-gap/plans_and_protocols/2026-04-02_01_protocol_target-package-propagation-gap.md` — sister exploration (requirements → tasks sync)

## Acceptance Criteria

- [ ] Gap confirmed or ruled out
- [ ] Fix location identified (release-plan / script / requ-explore)
- [ ] Design proposal written to plans_and_protocols/ including:
  - [ ] How packages are mapped to ACs at scale
  - [ ] How it composes with sync_task_packages.py (from TASK-PROC-030-06)
- [ ] Specific edit locations or new script scope defined
