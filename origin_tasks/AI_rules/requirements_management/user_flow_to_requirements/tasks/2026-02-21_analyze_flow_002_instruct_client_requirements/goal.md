---
task_id: TASK-PROC-030-02
type: explore
parent_requirement: REQ-PROC-030
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: FLOW-002 is now approved — requirements derivation must happen before implementation planning can start"
impact: 4
impact_reason: "I4-PAIN: FLOW-002 covers 8 scenarios across 2 personas and identifies 7+ gaps. Without this analysis, functional requirement coverage for client-protocol onboarding is unknown and implementation will be blocked."
status: completed
completed: 2026-02-22
effort: M
created: 2026-02-21
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Run derive-requirements-from-flow pipeline on FLOW-002 (Instruct Client on Protocol) to identify, document, and queue all requirement gaps as explore-requirements tasks"
requirements_version:
  commit: 4bd297e
  file: ../requirements.md
---

# Goal: Derive Requirements from FLOW-002 (Instruct Client on Protocol)

## Objective

Run the full `derive-requirements-from-flow → explore-requirements` pipeline for FLOW-002 to close all requirement gaps identified in the approved flow.

FLOW-002 is now **approved** (2026-02-21) and documents the complete therapist-client protocol onboarding experience across 8 scenarios. The flow explicitly identifies 7+ requirement gaps. This task ensures every gap becomes either a well-documented requirement or a documented decision.

## Requirements Summary

REQ-PROC-030 defines the three-skill pipeline for turning an approved user flow into actionable requirements:

1. **`derive-requirements-from-flow`** — Analyzes the flow, scans existing requirements for coverage, builds a Requirements Matrix, and (after user approval) creates `goal.md` files per gap
2. **`explore-requirements`** — Writes the actual requirement document (WHAT + WHY) for each goal.md created in step 1
3. **`create-impl-task`** — (Optional/later) Creates implementation tasks from finished requirements

For complete requirements at task creation time:
```
git show 4bd297e:requirements_tasks/process/AI_rules/requirements_management/user_flow_to_requirements/requirements.md
```

Current requirements: ../requirements.md

## Input

**User Flow**: `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md`
- Flow ID: FLOW-002
- Status: approved (2026-02-21)
- Scenarios served: 8 (SCEN-001-03, SCEN-002-02, SCEN-003-01, SCEN-003-02, SCEN-004-01, SCEN-005-01, SCEN-006-01, SCEN-007-01)
- Known gaps: 7 explicitly documented in the flow's "Gaps Requiring New Requirements" section

## Scope

### In Scope
- Running `derive-requirements-from-flow` skill on FLOW-002
- User review and prioritization of the Requirements Matrix
- Creating `goal.md` files for all user-approved gaps
- Running `explore-requirements` for each created goal.md (one by one, with user review)
- Saving `requirements_matrix.md` alongside the flow file

### Out of Scope
- `create-impl-task` — implementation planning happens in a later phase
- Deciding WHAT to implement (user approves the matrix first)
- Modifying FLOW-002 itself (it is now approved and locked)

## Acceptance Criteria

- [x] `derive-requirements-from-flow` skill executed on FLOW-002
- [x] Requirements Matrix created at `requirements_user_needs/user_flows/instruct_client_on_protocol/requirements_matrix.md`
- [x] All 7 known gaps categorized (exists_complete / exists_needs_update / new_needed / decision_needed / out_of_scope)
- [x] User has reviewed and approved the matrix
- [x] `goal.md` files created for all user-approved gaps
- [x] `explore-requirements` run for each goal.md (iteratively)
  - [x] Gap #2 (REQ-FUNC-014 Section 8 — Client Copy Architecture) — commit bdb4006
  - [x] Gap #3 (REQ-FUNC-007-02 — Plan Receiving full spec) — commit 96f3eb8
  - [x] Gap #4 (REQ-FUNC-002 — First-Entry UX) — commit aa268b6
  - [x] Gap #1 (REQ-FUNC-007-01 — Plan Handout Preview / Instruction View) — commit 0ba428c
  - [x] Gap #5 (feat_notification_time_mapping — REQ-FUNC-017) — commit d3866c7
  - [x] Gap #7 (feat_per_question_help_text — REQ-FUNC-018) — 2026-02-22
  - [x] Gap #10 (epic_onboarding — Quick Start mode) — REQ-FUNC-019, 2026-02-22
  - [x] OQ-8 (epic_plan_management — Reflection Prompt Type explore) — commit c5fc471
- [x] Each resulting requirement references FLOW-002 in its user_needs section

## Execution Steps

1. Use `derive-requirements-from-flow` skill:
   ```
   Use derive-requirements-from-flow skill for requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md
   ```

2. Review and approve the Requirements Matrix with the user

3. For each created goal.md, use `explore-requirements`:
   ```
   Do [path/to/goal.md]
   ```

4. After all requirements are written, mark this task complete via `complete-task` skill

## Notes

- FLOW-002 is the largest flow to date (400+ lines, 8 scenarios, 2 personas)
- The flow contains known gaps related to: data transfer UI, plan receipt, client pairing, notification time mapping, crisis safety, and adaptive UI rules
- Some gaps may result in new epics (not just features) — `explore-requirements` handles both
- Open Questions in the flow that are `decision_needed` must be resolved with the user before requirements can be written for those items
