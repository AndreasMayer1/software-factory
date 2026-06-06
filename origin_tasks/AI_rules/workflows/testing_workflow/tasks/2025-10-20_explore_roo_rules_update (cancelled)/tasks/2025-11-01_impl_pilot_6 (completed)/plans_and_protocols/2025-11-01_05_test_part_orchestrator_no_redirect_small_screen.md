produced_by: testfile_orchestrator_2025-11-01_plan_templates_plan_templates_orchestrator
timestamp: 2025-11-01T10:43:09Z
parent_arch_plan: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/2025-11-01_03_plan_arch_test_plan_plan_templates_orchestrator.md
part_id: part_02
title: Test Part Orchestrator — no_redirect_small_screen
summary: >
  Orchestrator for verifying that no redirect occurs on small screens (therapist plans route).
reference_test_file:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
acceptance_condition: >
  The targeted test named "should not redirect on small screens" passes
  OR expect(router.routerDelegate.currentConfiguration.uri.path, AppRoutes.therapistPlans.pathTemplate)
run_commands:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "should not redirect on small screens"
verification_commands:
  - flutter analyze
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
mock_strategy: |
  - Stub IScreenSizeService.isLargeScreen(any()) => false (explicit).
  - Provide PlanTemplatesBloc initial state PlanTemplatesInitial via whenListen or when(() => mockPlanTemplatesBloc.state).thenReturn(...)
  - Ensure GetIt registrations performed in test setUp are available.
required_helpers:
  - test/helpers/safe_pump.dart (exists: true)
estimated_complexity: low
recommended_max_attempts: 5
scope_of_work:
  - Allowed files in impl_test_part:
    - test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
    - test/helpers/safe_pump.dart
orchestrator_instructions: |
  1. Run the run_commands to capture current test output.
  2. If failures are due to missing helpers, create impl_test_part to implement them (see arch plan).
  3. If failures are timing-related, try adjusting pumps (use pumpAndSettleSafe) in a small test-only change attempt.
  4. Retry up to recommended_max_attempts; if still failing, create explore_test_blocker protocol with logs.
evidence_locations:
  - plans_and_protocols/logs/
  - plans_and_protocols/part_attempts/
notes: >
  This orchestrator focuses on the negative/guard behaviour; prefer asserting widget state if router path is unstable.
end