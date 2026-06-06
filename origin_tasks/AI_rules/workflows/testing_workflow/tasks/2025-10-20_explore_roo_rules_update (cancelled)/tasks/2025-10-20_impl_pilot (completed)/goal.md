---
task_id: TASK-PROC-005-04
type: impl
parent_requirement: REQ-PROC-005
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2025-10-20
completed: 2025-10-20
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02]
scope_description: "Pilot the hierarchical testing orchestrator pattern for the testing workflow"
requirements_version:
  commit: 1d3a2f9
  file: ../../../requirements.md
---

# Goal

Pilot the hierarchical testing orchestrator pattern for the testing workflow.

Objective:

- Validate the new orchestration hierarchy (Outer Orchestrator -> Testing Orchestrator -> Test File Orchestrator -> Architect plans -> Code part subtasks).
- Verify that leaf-level code subtasks follow the "code -> architect -> code" iterative cycle and do not re-run verification inside the same subtask.
- Confirm that unit and widget tests are executed with `flutter test <file>` during Phase 3 verification.
- Confirm that integration tests are not created or run unless explicitly requested by the user.

Scope:

- Feature: plan_templates (representative example).
- Test types: unit and widget tests only for this pilot.
- Do not add or run integration tests unless the user requests them.

Notes on execution:
- Do not include a step-by-step implementation list in this pilot goal. The pilot's purpose is to validate whether the new orchestration rules produce the correct sequence of subtasks and artifacts when applied by the orchestrator.
- The Test File Orchestrator, Test Part Orchestrator, Architect and Code subtasks must derive their actions from the updated `.roo` rules and the `arch_test_plan` artifacts. The pilot must follow those rules strictly (unit/widget tests only during Phase 3 verification; integration tests only on explicit user request).
- To have something to test you can write a test for lib\features\role_selection\presentation\screens\onboarding_screen.dart 

Pilot execution guidance (for the orchestrator, not part of the goal):
- The orchestrator will create the necessary Testing Orchestrator and Test File Orchestrator tasks, request `arch_test_plan` artifacts from Architect subtasks, and run Phase 3 verification (`flutter test <file>`) after the orchestrator reports completion per file.
- The pilot must record all `plans_and_protocols` artifacts (architect plans, per-attempt protocols, `part_attempts_log.md`, aggregated `fileId_protocol.md`, and verification logs) for review.

(Implementation steps are intentionally omitted so the pilot must derive them from the rules.)

Acceptance criteria:

- Outer Orchestrator created exactly one Testing Orchestrator for this feature.
- Test File Orchestrator produced an `arch_test_plan` and spawned `impl_test_part` subtasks.
- Each `impl_test_part` followed the "code -> architect -> code" workflow and did not re-run verification.
- Phase 3 verification completed for unit/widget tests; tests pass or `explore_test_blocker` protocols were created.

Deliverables:

- `plans_and_protocols/` entries: `2025-10-20_01_plan.md`, per-subtask protocol files, and any `explore_test_blocker` reports.
