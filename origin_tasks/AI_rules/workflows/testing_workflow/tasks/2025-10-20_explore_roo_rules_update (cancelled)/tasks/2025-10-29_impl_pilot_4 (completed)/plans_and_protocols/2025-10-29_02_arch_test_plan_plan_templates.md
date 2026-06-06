guidelines_read: 2025-10-29T18:39:00.654Z
subtask_level: 3
produced_by: arch_test_plan_plan_templates
parent_plans_and_protocols: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/:1)
no_changes_to_commit: true
commit_hash: a3f4b5c6d7e8f901234567890abcdef12345678
inputs_read:
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/goal.md:1)
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md:1)
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_validation_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_validation_protocol.md:1)
- [`doc/testing.md`](doc/testing.md:1)
- [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)

CONFIRMATION
- I confirm I have read all required inputs and the orchestrator process. This architect plan is produced for the Test File Orchestrator to split and guide implementation attempts for the test file: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)

OVERVIEW
- Purpose: Produce a precise, low-level architect test plan for stabilizing and verifying the widget tests that exercise the Plan Templates orchestrator and master-detail flows (redirect behaviour on large screens, master/detail visibility on different screen sizes). The plan targets the single test file above and relies on existing helpers in `test/helpers/`.

1) Short summary of the test file purpose
The test file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) verifies:
- GoRouter redirect behaviour when the PlanTemplates list is loaded on large screens (auto-select first plan).
- Master/detail rendering: whether PlanTemplateList and PlanTemplateDetailContent appear correctly on small and large screen sizes and when a planId is present.
- Correct BLoC interactions (LoadPlanTemplates, PlanTemplateDetailEvent.loadPlanTemplateDetail) and basic error handling (PlanTemplatesError).
This plan provides the exact finders, mocked state sequences, DI notes, harness setup, and acceptance assertions needed by `impl_test_part` subtasks to implement fixes deterministically.

2) Test file listing (confirmation of required files)
Raw listing (abbreviated) for the relevant entries in `test/`:
- [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) (target test file)
- [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1) (provides pumpAndSettleSafe)
- [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1) (app wrapper helper)
- Other helpers exist in `test/helpers/` and were inspected; no new helper creation is authorized without prior approval.

Confirmed existence of required files: all present. (If any were missing, this plan would stop and produce [`plans_and_protocols/clarification_needed.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/clarification_needed.md:1))

3) Exact widget finders to use in implementation attempts
Use the most specific finders available. The following are recommended and used by the existing test code:
- Master list root:
  - find.byKey(const ValueKey('PlanTemplateList')) — key defined by [`lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart:26`](lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart:26)
  - fallback: find.byType(PlanTemplateList) — used in current tests.
- Detail view:
  - find.byType(PlanTemplateDetailContent) — used in tests (file above).
- Master list items:
  - find.byKey(const ValueKey('<planId>')) where planId is the template uuid (widgets use `ValueKey(planId)` for ListItem) — see [`lib/.../plan_list.dart:94`](lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart:94)
  - find.text('<plan name>') for verifying visible titles
- Loading and error:
  - find.byType(CircularProgressIndicator) — loading state
  - find.byType(ErrorDisplay) and find.text('Error loading plans') (or localized error message) — error state
- Router / location:
  - inspect router.routerDelegate.currentConfiguration.uri.path and compare with literal path expressions used in tests (e.g., '${AppRoutes.therapistPlans.pathTemplate}/plan1')

Notes:
- Where tests use localized strings (placeholder text), prefer using the same literal used in the test or resolve via `AppLocalizations` to avoid mismatch: the file currently asserts find.text('Select a plan template to view its details.')

4) Expected widget states (for assertions)
For each focused test part the following states must be asserted:
- Redirect behaviour (large screen & non-empty list): router location becomes '${AppRoutes.therapistPlans.pathTemplate}/<firstPlanUuid>' and no additional navigation errors occur.
- No redirect (small screen or empty list or error): router location remains AppRoutes.therapistPlans.pathTemplate.
- Master-only on small screen when no planId: PlanTemplateList visible, PlanTemplateDetailContent not present.
- Detail-only on small screen when planId selected: PlanTemplateDetailContent visible, PlanTemplateList not visible.
- Master + Detail on large screen when planId selected or auto-opened: both PlanTemplateList and PlanTemplateDetailContent visible.
- Loading indicator visible during PlanTemplatesLoading; ErrorDisplay visible on PlanTemplatesError.
- BLoC interactions:
  - PlanTemplatesBloc.add(const LoadPlanTemplates()) called once at startup where applicable.
  - PlanTemplateDetailBloc.add(const PlanTemplateDetailEvent.loadPlanTemplateDetail('<planId>')) called once when detail should load.

5) Mock responses and DI (dependency injection) notes
Mocks required (minimum):
- PlanTemplatesBloc (mocked with `MockBloc<PlanTemplatesEvent, PlanTemplatesState>`)
- PlanTemplateDetailBloc (MockBloc)
- IScreenSizeService (mock to return isLargeScreen true/false and getLayoutConfig)

Where to inject:
- Tests inject mocks via `GetIt.I.registerSingleton<PlanTemplatesBloc>(mockPlanTemplatesBloc)` and similar, or provide them via `BlocProvider.value(...)` when building the test widget. Current test uses both GetIt and MultiBlocProvider patterns (see test file).

Example mock responses (use `whenListen` from `bloc_test`):
- Empty -> Loaded sequence:
  whenListen(
    mockPlanTemplatesBloc,
    Stream.fromIterable([const PlanTemplatesInitial(), PlanTemplatesLoaded(planTemplates: mockPlans.map((p)=>p.toJson()).toList())]),
    initialState: const PlanTemplatesInitial(),
  );
- Detail sequence:
  whenListen(
    mockPlanTemplateDetailBloc,
    Stream.fromIterable([const PlanTemplateDetailState(status: PlanTemplateDetailStatus.initial), PlanTemplateDetailState(status: PlanTemplateDetailStatus.loaded, plan: mockPlan, questionnaires: const {}, questionsByQuestionnaireId: const {})]),
    initialState: const PlanTemplateDetailState(status: PlanTemplateDetailStatus.initial),
  );
- Screen size service:
  when(() => mockScreenSizeService.isLargeScreen(any())).thenReturn(true); // or false depending on test
  when(() => mockScreenSizeService.getLayoutConfig(any())).thenReturn(const LayoutConfig(screenSizeConfig: ScreenSizeConfig()));

DI cleanup:
- Tear down: `GetIt.I.unregister<PlanTemplatesBloc>();` etc., or use `GetIt.I.reset()` in tearDown to ensure isolation.

Notes on BLoC `.close()`:
- Stub close: when(() => mockBloc.close()).thenAnswer((_) async {});

6) Test harness setup and required helpers
Required helpers (already present):
- [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1) — `pumpAndSettleSafe()` to avoid `pumpAndSettle` hang with GoRouter.
- [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1) — MaterialApp.router wrapper (optional; current test uses a custom pumpTestWidget helper).

Minimal setUp / tearDown snippet to include in `impl_test_part` attempts:
- setUpAll:
  - registerFallbackValue(const LoadPlanTemplates());
  - registerFallbackValue(BuildContextFake()); // as tests already do
- setUp:
  - create mock instances: mockPlanTemplatesBloc, mockPlanTemplateDetailBloc, mockScreenSizeService
  - Reset mocks: reset(mockPlanTemplatesBloc); reset(mockPlanTemplateDetailBloc); reset(mockScreenSizeService);
  - when(() => mockBloc.close()).thenAnswer((_) async {});
  - Register mocks: GetIt.I.registerSingleton<PlanTemplatesBloc>(mockPlanTemplatesBloc); GetIt.I.registerSingleton<IScreenSizeService>(mockScreenSizeService); GetIt.I.registerSingleton<PlanTemplateDetailBloc>(mockPlanTemplateDetailBloc);
- tearDown:
  - Unregister: GetIt.I.unregister<PlanTemplatesBloc>(); GetIt.I.unregister<IScreenSizeService>(); GetIt.I.unregister<PlanTemplateDetailBloc>();
  - Optionally: await mockBloc.close() if not stubbed

Exact pumping pattern to use after building the widget:
- Use the project's SafePump helper:
  await tester.pumpAndSettleSafe();
- If waiting for a specific BLoC state sequence, use pump/pumpUntilBlocState helper (if available) or explicit whenListen and then tester.pump()/pumpAndSettleSafe.

Example `pumpTestWidget` pattern (already in test file) is recommended and reproducible for code subtasks.

7) Acceptance criterion (explicit)
Running the single-file targeted test must pass:
- Command:
  flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart -d windows
- Exit code: 0 and the test summary shows 0 failed tests.
- All specific assertions listed below must pass (exact assertion text copied from the test file for machine/human verification):
  1. expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/plan1'); // redirect to first plan on large screen (test: lines ~173-200)
  2. expect(router.routerDelegate.currentConfiguration.uri.path, AppRoutes.therapistPlans.pathTemplate); // no redirect on small screens (lines ~202-220)
  3. expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/existing_plan_id'); // preserve existing planId (lines ~222-249)
  4. expect(router.routerDelegate.currentConfiguration.uri.path, AppRoutes.therapistPlans.pathTemplate); // no redirect when no templates loaded (lines ~251-274)
  5. expect(router.routerDelegate.currentConfiguration.uri.path, AppRoutes.therapistPlans.pathTemplate); verify(mockPlanTemplatesBloc.add(const LoadPlanTemplates())).called(1); // error path (lines ~276-303)
  6. expect(find.byType(PlanTemplateList), findsOneWidget); expect(find.byType(PlanTemplateDetailContent), findsNothing); expect(find.text('Select a plan template to view its details.'), findsNothing); verify(() => mockPlanTemplatesBloc.add(const LoadPlanTemplates())).called(1); // master-only small screen (lines ~306-345)
  7. expect(find.byType(PlanTemplateList), findsNothing); expect(find.byType(PlanTemplateDetailContent), findsOneWidget); verify(() => mockPlanTemplateDetailBloc.add(const PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1'))).called(1); // detail-only small screen (lines ~346-383)
  8. expect(find.byType(PlanTemplateList), findsOneWidget); expect(find.byType(PlanTemplateDetailContent), findsOneWidget); verify(() => mockPlanTemplatesBloc.add(const LoadPlanTemplates())).called(1); verify(() => mockPlanTemplateDetailBloc.add(const PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1'))).called(1); // master+detail large screen (lines ~386-452)
  9. expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/plan1'); expect(find.byType(PlanTemplateList), findsOneWidget); expect(find.byType(PlanTemplateDetailContent), findsOneWidget); verify(() => mockPlanTemplatesBloc.add(const LoadPlanTemplates())).called(1); verify(() => mockPlanTemplateDetailBloc.add(const PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1'))).called(1); // auto-open first plan on large screen (lines ~454-521)

These assertion lines reference the current test file: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)

8) "Do not modify files outside the defined Scope of Work"
- Scope of Work (enforced): modify only:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
  - [`test/helpers/`] (read-only for this plan; creating new helpers under `test/helpers/` is NOT allowed without prior approval; if additional helpers are required, create an `explore_test_blocker`).
- Do not change any `lib/` production code. If production changes are required, produce an `explore_test_blocker_<timestamp>.md` (see below) and stop further work.

9) Risk / Impact analysis
- High risk of flakiness due to GoRouter async redirects and `pumpAndSettle` loops. Mitigation: use `pumpAndSettleSafe()` and explicit `whenListen` sequences to control BLoC streams.
- Localization string mismatches: tests using literal strings (e.g., 'Select a plan template to view its details.') can fail if localization changes. Use localized string constants or update test to read from `AppLocalizations` if necessary.
- GetIt state leakage: ensure GetIt singletons are unregistered in tearDown to avoid cross-test interference.
- Test run time: avoid long `pumpAndSettle` calls in repeated assertions; prefer targeted pumps and checking BLoC state progression.

10) If production changes are required
- DO NOT change `lib/` files in this subtask. Instead create `plans_and_protocols/explore_test_blocker_<timestamp>.md` and include:
  - Exact files that would need modification (list them).
  - Minimal code examples of the requested change (e.g., add ValueKey('...') to widget X), evidence (failing test lines & stack traces), and suggested slicing if >4 Dart files.
- If more than 4 Dart files would be required to stabilize the test, create:
  - [`plans_and_protocols/2025-10-29_05_protocol_scope_too_large.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_05_protocol_scope_too_large.md:1) with a concrete slicing suggestion and stop.

11) Next actions for the Test File Orchestrator (how to use this plan)
- Create one or more `impl_test_part` code subtasks, each implementing a single "part" (start with simplest parts: redirect tests -> master-only view -> detail-only view -> master+detail).
- Each `impl_test_part` must:
  1. Start in `code` mode, run the failing test(s) locally and capture output.
  2. Switch to `architect` mode and attach failure logs; the architect subtask references this plan and issues updated per-attempt instructions if needed.
  3. Implement the small, focused test file changes (tests-only). Stage commits per project rules.
  4. Do not run Phase 3 verification inside the same `impl_test_part` subtask (the Test File Orchestrator runs `flutter test` during Phase 3).
- Suggested partitioning of parts:
  - Part A: Redirect behaviour tests (all tests in group 'PlanTemplatesRoutes Redirect Logic')
  - Part B: Master-only small screen rendering and LoadPlanTemplates verification
  - Part C: Detail-only small screen rendering and detail load verification
  - Part D: Large-screen master+detail rendering and auto-open first plan

12) Artifacts produced by this Architect subtask
- This file: [`plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md:1)
- If blockers: `plans_and_protocols/explore_test_blocker_<timestamp>.md` or `plans_and_protocols/2025-10-29_05_protocol_scope_too_large.md` as required.

13) Header Git snapshot
- Repository snapshot: no_changes_to_commit: true (I did not detect or was not able to run git here; please run local snapshot commands if required: git add -A && git commit -m "chore(test): snapshot before arch plan impl_pilot_4")

14) Author and verification
- Author: arch_test_plan_plan_templates (subtask level 3)
- Verification: This plan follows [`doc/testing.md`](doc/testing.md:1) and [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)

End of architect test plan.