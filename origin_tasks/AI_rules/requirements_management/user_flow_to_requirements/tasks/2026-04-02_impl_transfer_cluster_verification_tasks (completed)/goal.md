---
task_id: TASK-PROC-030-05
type: impl
parent_requirement: REQ-PROC-030
urgency: 3
urgency_reason: U3-WORKFLOW-GAP
impact: 4
impact_reason: I4-PAIN
status: completed
completed: 2026-04-02
started: 2026-04-02
effort: S
created: 2026-04-02
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Retroactively create the missing verification tasks for the transfer cluster (FLOW-002/003/004) following Phase 4.5 of requ-derive-from-flow: group existing exploration tasks by target_package bundle, create one verification goal.md per bundle with correct depends_on list, update Pipeline Status."
release_description: ""
requirements_version:
  commit: e9382676
  file: ../requirements.md
---

# Goal: Create Missing Verification Tasks for Transfer Cluster

## Objective

The transfer cluster (FLOW-002 / FLOW-003 / FLOW-004) already has 21 exploration
tasks created from the requirements matrix. Phase 4.5 of `requ-derive-from-flow`
did not exist at that time, so no verification tasks were created.

This task retroactively applies Phase 4.5 to create the missing verification tasks.

## Requirements Summary

REQ-PROC-030 defines the flow→requirements derivation pipeline. Phase 4.5 (added
by TASK-PROC-030-04) specifies that one verification task must be created per bundle
(grouped by `target_package`), with `depends_on` pointing to all exploration tasks
in that bundle.

Current requirements: ../requirements.md

## Source Material

- **Matrix**: `requirements_user_needs/user_flows/_clusters/flexible_data_transfer/requirements_matrix.md`
- **Phase 4.5 template**: `.claude/skills/requ-derive-from-flow/skill.md` — Section 4.5
- **Verification skill**: `.claude/skills/requ-verify-flow-coverage/skill.md`

## Scope

### In Scope
1. Read the Pipeline Status table in the transfer cluster matrix
2. Read each existing exploration task's goal.md to extract `task_id` and `target_package`
3. Group tasks by `target_package` — each unique value = one bundle
4. For each bundle: create one verification goal.md following the Phase 4.5 template exactly
   - `type: explore`
   - `verification_task: true`
   - `verification_bundle`: bundle name
   - `verification_gaps`: gap numbers in this bundle (from matrix rows)
   - `verification_foundations`: F-IDs in this bundle (from foundation assignment rule)
   - `source_matrix`: path to the cluster matrix
   - `depends_on`: all TASK-IDs of exploration tasks in this bundle
   - urgency/impact: same as bundle's exploration tasks
   - Gap → Requirement Mapping table pre-computed from the matrix
5. Use `task-create` skill to create each verification task (correct task IDs, proper folder structure)
6. Update the Pipeline Status table: add V-prefixed rows (V1, V2, ...) with status "created"

### Out of Scope
- Executing the verification tasks — those run naturally via "do next task" once
  their bundle's exploration tasks are all complete
- Modifying any existing exploration tasks
- Updating requirements content

## Acceptance Criteria

- [ ] All bundles in the transfer cluster matrix have a corresponding verification goal.md
- [ ] Each verification goal.md has correct `depends_on` list (all exploration task IDs in that bundle)
- [ ] Each verification goal.md has the correct `verification_bundle`, `verification_gaps`, `source_matrix` fields
- [ ] Foundation gaps are assigned to the correct bundle per the Phase 4.5 rule
- [ ] Pipeline Status table updated with V-prefixed rows
- [ ] Verification tasks are blocked (not surfaced by next_tasks.py) until their bundle tasks complete

## Notes

To execute: read the matrix Pipeline Status to understand which tasks exist and
their `target_package` values. Some exploration tasks may already be completed —
those bundles still need a verification task (it will immediately unblock if all
depends_on tasks are done).

Treat completed exploration tasks as eligible `depends_on` entries — `next_tasks.py`
already treats completed tasks as satisfied dependencies.
