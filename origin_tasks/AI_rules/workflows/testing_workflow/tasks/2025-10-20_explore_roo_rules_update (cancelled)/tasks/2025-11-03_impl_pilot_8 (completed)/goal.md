---
task_id: TASK-PROC-005-11
type: impl
parent_requirement: REQ-PROC-005
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2025-11-03
completed: 2025-11-03
after: []
awaiting: []
covers:
  sections: [SEC-01, SEC-02]
scope_description: "Pilot 8: Validate hierarchical testing orchestrator pattern with plan_templates feature, testing unit and widget tests only"
requirements_version:
  commit: de03866
  file: ../../../requirements.md
---

# Goal

Pilot the hierarchical testing orchestrator pattern for the testing workflow.
This is already the 8th pilot. The orchestrator rules have been adjusted to fix some problems that were discovered by the first pilots.


Objective:

- Validate the new orchestration hierarchy (Outer Orchestrator -> Testing Orchestrator -> Test File Orchestrator -> Test File Part Orchestrator -> Architect plans -> Code part subtasks).
- Verify that leaf-level code subtasks follow the "code -> architect -> code" iterative cycle and do not re-run verification inside the same subtask.
- Confirm that unit and widget tests are executed with `flutter test <file>` during Phase 3 verification.
- Confirm that integration tests are not created or run unless explicitly requested by the user.

Scope:

- Feature: plan_templates (representative example).
- Test types: unit and widget tests only for this pilot.
- Do not add or run integration tests unless the user requests them.

Notes on execution:
- Do not include a step-by-step implementation list in this pilot goal. The pilot's purpose is to validate whether the new orchestration rules produce the correct sequence of subtasks and artifacts when applied by the orchestrator.
- To have something to test you can update the currently failing tests for test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart

Pilot execution guidance (for the orchestrator, not part of the goal):
- This is about writing tests, not about implementing a new feature. You should have the information what that means for the process.

(Implementation steps are intentionally omitted so the pilot must derive them from the rules.)

Acceptance criteria:

- Outer Orchestrator created exactly one Testing Orchestrator for this feature.
- Test File Orchestrator spawned the correct subtasks and the correct artifacts have been created.
- The "code -> architect -> code" workflow was followed.
- Phase 3 verification completed for unit/widget tests; tests pass or `explore_test_blocker` protocols were created.

Deliverables:

- The correct `plans_and_protocols/` entries defined by the workflow.
