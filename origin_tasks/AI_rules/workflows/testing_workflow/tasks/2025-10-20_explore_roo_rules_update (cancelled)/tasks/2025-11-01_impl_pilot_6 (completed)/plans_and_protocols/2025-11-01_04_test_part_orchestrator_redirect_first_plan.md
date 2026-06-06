produced_by: testfile_orchestrator_2025-11-01_plan_templates_plan_templates_orchestrator
timestamp: 2025-11-01T10:41:28Z
parent_arch_plan: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/2025-11-01_03_plan_arch_test_plan_plan_templates_orchestrator.md
part_id: part_01
title: Test Part Orchestrator — redirect_first_plan
summary: >
  Orchestrator for verifying the redirect behaviour that should auto-open the first plan on large screens.
  This orchestrator runs targeted tests, collects failure output, and spawns impl_test_part subtasks if fixes are required.
reference_test_file:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
acceptance_condition: >
  The targeted test named "should redirect to first plan on large screen when no planId is selected" passes
  OR the router resolves to path '${AppRoutes.therapistPlans.pathTemplate}/plan1' when the test runs.
run_commands:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "should redirect to first plan on large screen when no planId is selected"
verification_commands:
  - flutter analyze
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
mock_strategy: |
  - Register MockPlanTemplatesBloc and MockPlanTemplateDetailBloc via whenListen to emit:
    initial: PlanTemplatesInitial
    then: PlanTemplatesLoaded with at least one plan with uuid 'plan1'
  - Stub IScreenSizeService.isLargeScreen(any()) => true.
required_helpers:
  - test/helpers/safe_pump.dart (exists: true)
  - test/helpers/pump_until_bloc_state.dart (exists: true)
estimated_complexity: medium
recommended_max_attempts: 5
scope_of_work:
  - Allowed files to change in impl_test_part:
    - test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
    - test/helpers/test_router_helpers.dart
    - test/helpers/safe_pump.dart
    - test/helpers/pump_until_bloc_state.dart
  - Any changes outside this list are forbidden.
orchestrator_instructions: |
  1. Run the run_commands to capture current failure output and logs.
  2. If the failure is missing helper(s) (import error for test_router_helpers.dart), create a single impl_test_part code-mode subtask:
     - Name: 2025-11-01_13_impl_test_part_create_test_router_helpers.md
     - Goal: add minimal test helpers implementing pumpMoreScreenTestApp and pumpAndSettleMoreScreenTestApp as described in doc/testing.md.
     - Pre-steps: optional run of build_runner if tests fail with generated-code missing.
     - After implementation, run the run_commands again inside the impl_test_part.
  3. If the failure is functional (assertion or timing), spawn an impl_test_part to:
     - Make minimal test-only changes (test file or helper), run targeted test, produce part_attempt_<n>_protocol.md and commit per rules.
  4. Retry loop: attempt up to recommended_max_attempts. If exhausted, create explore_test_blocker protocol with captured logs and diagnostics.
evidence_locations:
  - plans_and_protocols/logs/
  - plans_and_protocols/part_attempts/
notes: >
  The Test Part Orchestrator must not modify product source files. Only test files and test helpers in scope are allowed.
end