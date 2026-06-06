produced_by: testfile_orchestrator_2025-11-01_plan_templates_plan_templates_orchestrator
parent_plans_and_protocols:
- requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/
timestamp: 2025-11-01T10:38:14Z
guidelines_read:
- doc/testing.md:2025-11-01T10:28:09Z
- doc/architecture.md:2025-11-01T10:28:09Z
- doc/general/documentation_process.md:2025-11-01T10:28:09Z
no_changes_to_commit: true
suggested_helpers:
- test/helpers/test_router_helpers.dart

title: Arch test plan — plan_templates_orchestrator_test.dart
summary: >
  Architect-level plan that splits the widget test file
  test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  into small, independently verifiable parts. This plan records required helpers, exact verification commands,
  and Test Part Orchestrator instructions. Phase 2 implementation is intentionally skipped here; missing helpers
  and failing tests will be handled by code-mode impl_test_part subtasks spawned by the Test Part Orchestrators.

context_inputs_read:
- path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/goal.md
  read_at: 2025-11-01T10:28:03Z
- path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/2025-11-01_01_plan_impl_pilot.md
  read_at: 2025-11-01T10:13:38Z
- path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/2025-11-01_02_protocol_validate_impl_pilot.md
  read_at: 2025-11-01T10:21:30Z
- path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/2025-11-01_01_startup_protocol.md
  read_at: 2025-11-01T10:29:01Z
- path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/logs/test_file_list.txt
  read_at: 2025-11-01T10:29:01Z

# Parts (split from the test file)
parts:
- part_id: part_01
  short_description: Redirect - auto-open first plan on large screen
  acceptance_condition: "plain-name test 'should redirect to first plan on large screen when no planId is selected' passes OR expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/plan1')"
  selectors:
    - "router.routerDelegate.currentConfiguration.uri.path"
  expected_widget_states:
    - "router resolved path ends with /plan1"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should redirect to first plan on large screen when no planId is selected\""
    - "OR full file: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart"
  mock_strategy: |
    - Provide MockPlanTemplatesBloc and MockPlanTemplateDetailBloc via whenListen with the sequence:
      initial PlanTemplatesInitial then PlanTemplatesLoaded with at least one plan (uuid plan1).
    - Stub IScreenSizeService.isLargeScreen(any()) => true.
    - Ensure GetIt registrations for PlanTemplatesBloc, PlanTemplateDetailBloc, IScreenSizeService (tests already register in setUp).
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
    - test/helpers/pump_until_bloc_state.dart (exists: true)
  estimated_complexity: medium
  recommended_max_attempts: 5
  fallbacks:
    - "If router path check is flaky, verify presence of PlanTemplateDetailContent widget and then assert the router location as a secondary check."
    - "Use extra pumps: pumpAndSettleSafe() then pump() before asserting."

- part_id: part_02
  short_description: Redirect - no redirect on small screens
  acceptance_condition: "plain-name test 'should not redirect on small screens' passes OR expect(router.routerDelegate.currentConfiguration.uri.path, AppRoutes.therapistPlans.pathTemplate)"
  selectors:
    - "router.routerDelegate.currentConfiguration.uri.path"
  expected_widget_states:
    - "router resolved path equals therapistPlans path (no planId)"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should not redirect on small screens\""
  mock_strategy: |
    - Stub IScreenSizeService.isLargeScreen(any()) => false.
    - Stubbing PlanTemplatesBloc not required to be loaded for the negative case; still ensure initial state stub (PlanTemplatesInitial).
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
  estimated_complexity: low
  recommended_max_attempts: 5
  fallbacks:
    - "If path is still changing due to async emissions, assert widget tree state (PlanTemplateList visible) instead of router path."

- part_id: part_03
  short_description: Redirect - preserve existing planId in URL
  acceptance_condition: "plain-name test 'should not redirect if planId is already present' passes OR expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/existing_plan_id')"
  selectors:
    - "router.routerDelegate.currentConfiguration.uri.path"
  expected_widget_states:
    - "router path contains existing_plan_id and PlanTemplateDetailContent is visible"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should not redirect if planId is already present\""
  mock_strategy: |
    - whenListen PlanTemplatesBloc to emit PlanTemplatesLoaded with mockPlans (so list exists).
    - Ensure initial router location includes /existing_plan_id.
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
  estimated_complexity: low
  recommended_max_attempts: 5
  fallbacks:
    - "If the router assertion is flaky, check that PlanTemplateDetailContent is present and its loaded state contains the expected plan id."

- part_id: part_04
  short_description: Redirect - no redirect when no templates are loaded
  acceptance_condition: "plain-name test 'should not redirect if no templates are loaded after fetch' passes OR expect(router.routerDelegate.currentConfiguration.uri.path, AppRoutes.therapistPlans.pathTemplate)"
  selectors:
    - "router.routerDelegate.currentConfiguration.uri.path"
  expected_widget_states:
    - "router remains on therapistPlans path and no PlanTemplateDetailContent"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should not redirect if no templates are loaded after fetch\""
  mock_strategy: |
    - whenListen PlanTemplatesBloc with PlanTemplatesLoaded(planTemplates: []) to simulate empty result.
    - Screen size stub as appropriate for the test (default small screen).
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
  estimated_complexity: low
  recommended_max_attempts: 5
  fallbacks:
    - "Assert absence of PlanTemplateDetailContent widget instead of relying solely on router path."

- part_id: part_05
  short_description: Redirect - no redirect on fetch error
  acceptance_condition: "plain-name test 'should not redirect if fetch results in error' passes AND verify mockPlanTemplatesBloc.add(const LoadPlanTemplates()) called(1)"
  selectors:
    - "router.routerDelegate.currentConfiguration.uri.path"
    - "verify calls on mock blocs"
  expected_widget_states:
    - "router stays on therapistPlans path and PlanTemplatesBloc received LoadPlanTemplates() event"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should not redirect if fetch results in error\""
  mock_strategy: |
    - whenListen PlanTemplatesBloc to emit PlanTemplatesError('Error loading plans').
    - Verify that LoadPlanTemplates was dispatched once as the test asserts.
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
  estimated_complexity: low
  recommended_max_attempts: 5
  fallbacks:
    - "If event-count verification is flaky, relax to called >=1 and rely on router path assertion."

- part_id: part_06
  short_description: Orchestrator - show list on small screen (happy path)
  acceptance_condition: "plain-name test 'should display PlanTemplateList when no planId is selected on small screen' passes OR expect(find.byType(PlanTemplateList), findsOneWidget) and PlanTemplateDetailContent not found"
  selectors:
    - "find.byType(PlanTemplateList)"
    - "find.byType(PlanTemplateDetailContent)"
  expected_widget_states:
    - "PlanTemplateList present, PlanTemplateDetailContent absent"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should display PlanTemplateList when no planId is selected on small screen\""
  mock_strategy: |
    - whenListen PlanTemplatesBloc to emit PlanTemplatesLoaded([...]) with at least one plan.
    - whenListen PlanTemplateDetailBloc with initial state PlanTemplateDetailState.initial.
    - Ensure GetIt registrations in setUp are respected; tests already do GetIt register/unregister in setUp/tearDown.
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
    - test/helpers/pump_until_bloc_state.dart (exists: true)
  estimated_complexity: medium
  recommended_max_attempts: 5
  fallbacks:
    - "If PlanTemplateList presence is flaky, check for expected text present in the rendered list items."

- part_id: part_07
  short_description: Orchestrator - show detail when planId selected on small screen
  acceptance_condition: "plain-name test 'should display PlanTemplateDetailContent when planId is selected on small screen' passes OR expect(find.byType(PlanTemplateDetailContent), findsOneWidget) AND verify PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1') was dispatched"
  selectors:
    - "find.byType(PlanTemplateDetailContent)"
    - "verify mockPlanTemplateDetailBloc.add(const PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1'))"
  expected_widget_states:
    - "PlanTemplateDetailContent present and PlanTemplateList absent"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should display PlanTemplateDetailContent when planId is selected on small screen\""
  mock_strategy: |
    - whenListen PlanTemplateDetailBloc to emit sequence [initial, loaded with plan plan1].
    - whenListen PlanTemplatesBloc as needed (initial).
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
    - test/helpers/pump_until_bloc_state.dart (exists: true)
  estimated_complexity: medium
  recommended_max_attempts: 7
  fallbacks:
    - "If exact event call counts are flaky, relax to >=1 and assert widget presence."

- part_id: part_08
  short_description: Orchestrator - large screen both master and detail visible when planId selected
  acceptance_condition: "plain-name test 'should display PlanTemplateList and PlanTemplateDetailContent on large screen when planId is selected' passes OR findsOneWidget for both PlanTemplateList and PlanTemplateDetailContent"
  selectors:
    - "find.byType(PlanTemplateList)"
    - "find.byType(PlanTemplateDetailContent)"
  expected_widget_states:
    - "Both master and detail widgets present"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should display PlanTemplateList and PlanTemplateDetailContent on large screen when planId is selected\""
  mock_strategy: |
    - Stub IScreenSizeService.isLargeScreen(any()) => true.
    - whenListen PlanTemplatesBloc to emit PlanTemplatesLoaded with mockPlans and PlanTemplateDetailBloc loaded with plan.
    - Set tester.view.physicalSize and devicePixelRatio in test (tests already do).
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
  estimated_complexity: medium
  recommended_max_attempts: 7
  fallbacks:
    - "If device-size based assertions are flaky, assert presence of both widgets without relying on router path."

- part_id: part_09
  short_description: Orchestrator - auto-open first plan on large screen and display both master and detail (integration of flows)
  acceptance_condition: "plain-name test 'should auto-open first plan on large screen and display both master and detail' passes OR router path ends with /plan1 and both widgets present"
  selectors:
    - "router.routerDelegate.currentConfiguration.uri.path"
    - "find.byType(PlanTemplateList)"
    - "find.byType(PlanTemplateDetailContent)"
  expected_widget_states:
    - "router resolved to /plan1 and both master and detail present"
  run_commands:
    - "flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name \"should auto-open first plan on large screen and display both master and detail\""
  mock_strategy: |
    - whenListen PlanTemplatesBloc to emit PlanTemplatesLoaded containing plan1 and plan2, then ensure PlanTemplateDetailBloc emits loaded for plan1.
    - Stub IScreenSizeService.isLargeScreen(any()) => true.
  required_helpers:
    - test/helpers/safe_pump.dart (exists: true)
  estimated_complexity: high
  recommended_max_attempts: 7
  fallbacks:
    - "If router-based assertion is unstable, assert the presence of both widgets and that PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1') was dispatched."

# Required test helpers (existence)
required_test_helpers:
- path: test/helpers/test_router_helpers.dart
  exists: false
  reason: "Referenced by prior plans and useful across GoRouter tests; minimal helper recommended implementing pumpMoreScreenTestApp/pumpAndSettleMoreScreenTestApp patterns described in doc/testing.md."
  impl_test_part: 2025-11-01_13_impl_test_part_create_test_router_helpers.md
- path: test/helpers/safe_pump.dart
  exists: true
- path: test/helpers/pump_until_bloc_state.dart
  exists: true

# Verification commands (Phase 3 - one-line)
verification_commands:
- flutter analyze
- flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- For targeted retries use: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "<exact test name>"

# Acceptance criteria (global)
acceptance_criteria:
- All parts' acceptance_condition are explicit and machine-evaluable (plain-name or widget/route assertions).
- Missing helpers are implemented by dedicated impl_test_part code subtasks before Phase 3 verification.
- Each Test Part Orchestrator will spawn impl_test_part attempts up to recommended_max_attempts before escalating to explore_test_blocker.

# Explore blocker checklist (quick)
explore_blocker_checklist:
- Missing helper files in test/helpers/ (e.g., test_router_helpers.dart) — create impl_test_part to add minimal pumpMoreScreenTestApp helper.
- Generated-code issues (freezed/localizations) — run build_runner in impl_test_part as pre-step if tests fail with missing generated artifacts.
- Flaky router pumpAndSettle loops — use SafePump (pumpAndSettleSafe) and add fallback assertions based on widget presence.

# Test Part Orchestrator instructions (summary)
test_part_orchestrator_instructions: |
  For each part above the Test Part Orchestrator must:
  1. Run the indicated targeted command (plain-name) to capture current failure output.
  2. If failure is purely missing helper, create a single impl_test_part subtask to implement the helper (see required_test_helpers.impl_test_part).
  3. If failure is functional (assertion fails), spawn an impl_test_part code-mode subtask to fix the test or underlying test harness, following "code -> architect -> code" loop:
     - Start: create a commit recording start state.
     - Implement change limited to Scope of Work described in the part (only test helpers or the test file).
     - Run targeted flutter test command inside the impl_test_part.
     - Produce part_attempt_<n>_protocol.md under plans_and_protocols for each attempt using the template_part_attempt_protocol.md.
     - Commit changes after successful attempt or before creating next attempt.
  4. Attempt loop: retry up to recommended_max_attempts per part. If attempts exhausted, create explore_test_blocker protocol and stop.

phase_2_statement: "Phase 2 (implementation) skipped for Test File Orchestrator; it will create code-mode impl_test_part subtasks for missing helpers and for captured failing-tests as needed."

evidence_capture_locations:
- plans_and_protocols/logs/
- plans_and_protocols/part_attempts/

notes:
- Scope check: total production files to change implied by this plan is <= 4 (primarily test helper and the test file). If an impl attempt shows more than 4 production files must be changed, create a scope-too-large protocol instead of proceeding.
- The Test File Orchestrator must include the full plans_and_protocols path and scope in every impl_test_part instruction.
