# Detailed implementation plan — 2025-10-29_impl_pilot_5
produced_by: Roo (architect-mode, depth:2)
timestamp: 2025-11-01T09:19:42Z
guidelines_read:
- [`doc/architecture.md:1`](doc/architecture.md:1)
- [`doc/testing.md:1`](doc/testing.md:1)
- [`.roo-templates/high_level_impl_plan.md:1`](.roo-templates/high_level_impl_plan.md:1)
- [`.roo-templates/template_protocol.md:1`](.roo-templates/template_protocol.md:1)
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_5/plans_and_protocols/2025-11-01_01_plan_impl_high_level.md:1`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_5/plans_and_protocols/2025-11-01_01_plan_impl_high_level.md:1)

Update TODO list (replicated from the executed update_todo_list)
- [x] Create detailed implementation plan (this file)
- [-] Collect repository file lists and precise references for BLoC / widget keys (list_files + search_files) — gather exact paths & line numbers used in the plan
- [ ] Create new helper: [`test/helpers/pump_until_bloc_state.dart:1`](test/helpers/pump_until_bloc_state.dart:1)
- [ ] Update test harness: modify [`test/helpers/test_app_wrapper.dart:1`](test/helpers/test_app_wrapper.dart:1) to use MaterialApp.router builder and ensure providers wrap routerWidget
- [ ] Update test: modify [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- [ ] Update test: modify [`test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1)
- [ ] Produce candidate SEARCH/REPLACE apply_diff blocks for all file edits (ready to execute)
- [ ] Commit changes in small logical commits (one per file/change) with exact commit messages and run verification per commit
- [ ] Run Phase 3 verification commands (individual file-level flutter test commands) and collect logs
- [ ] If tests fail due to production code, produce explore_test_blocker protocol(s)
- [ ] Finalize artifacts: write and save plan and any protocols under `plans_and_protocols/`

Summary:
This detailed plan continues from the approved high-level plan [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_5/plans_and_protocols/2025-11-01_01_plan_impl_high_level.md:1`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_5/plans_and_protocols/2025-11-01_01_plan_impl_high_level.md:1) and the validation protocol [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_5/plans_and_protocols/2025-11-01_03_protocol_validate_assumptions.md:1`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_5/plans_and_protocols/2025-11-01_03_protocol_validate_assumptions.md:1).

Final Scope of Work (confirmed)
- Modify: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
  - Justification: Representative comprehensive widget test; requires deterministic waits and explicit BLoC-based waits to avoid GoRouter pumpAndSettle loops.
- Modify: [`test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1)
  - Justification: Minimal, fast assertions to isolate failures quickly; convert to safe pumps.
- Create: [`test/helpers/pump_until_bloc_state.dart:1`](test/helpers/pump_until_bloc_state.dart:1)
  - Justification: Shared helper to wait for BLoC state emissions deterministically (reduces flakiness).
- Modify: [`test/helpers/test_app_wrapper.dart:1`](test/helpers/test_app_wrapper.dart:1)
  - Justification: Ensure `MaterialApp.router` uses `builder` to pass the routed widget into providers (`routerWidget`) to match production widget tree and avoid missing router context in tests.

Per-file change list, candidate diffs, and verification

1) [`test/helpers/test_app_wrapper.dart:1`](test/helpers/test_app_wrapper.dart:1)
- Exact change list:
  - Add import for project tokens: [`package:mood_tracker/config/theme/tokens.g.dart:1`](package:mood_tracker/config/theme/tokens.g.dart:1)
  - Change `MaterialApp.router(...)` invocation to include a `builder: (context, routerWidget) { ... }` that wraps `routerWidget` with `Tokens` and `BlocProvider<RoleSelectionBloc>.value`.
  - Add a short doc comment explaining test-level DI reset expectations (GetIt.I.reset()).
- Candidate apply_diff (ready for `apply_diff`):
<<<<<<< SEARCH
:start_line:1
-------
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:mood_tracker/features/role_selection/presentation/bloc/role_selection_bloc.dart';
import 'package:mood_tracker/generated/l10n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

Widget buildTestApp({
  required Widget child,
  required RoleSelectionBloc roleSelectionBloc,
  GoRouter? router,
}) {
  final testRouter = router ?? GoRouter(routes: [GoRoute(path: '/', builder: (_, __) => child)]);

  return MultiBlocProvider(
    providers: [
      BlocProvider<RoleSelectionBloc>.value(value: roleSelectionBloc),
    ],
    child: MaterialApp.router(
      locale: const Locale('en'),
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      routerConfig: testRouter,
    ),
  );
}
=======
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:mood_tracker/features/role_selection/presentation/bloc/role_selection_bloc.dart';
import 'package:mood_tracker/generated/l10n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:mood_tracker/config/theme/tokens.g.dart';

/// Test App wrapper used by widget tests.
/// Important: tests must reset shared DI between tests (e.g., `GetIt.I.reset()` in tearDown)
Widget buildTestApp({
  required Widget child,
  required RoleSelectionBloc roleSelectionBloc,
  GoRouter? router,
}) {
  final testRouter = router ?? GoRouter(routes: [GoRoute(path: '/', builder: (_, __) => child)]);

  return MultiBlocProvider(
    providers: [
      BlocProvider<RoleSelectionBloc>.value(value: roleSelectionBloc),
    ],
    child: MaterialApp.router(
      locale: const Locale('en'),
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      routerConfig: testRouter,
      builder: (context, routerWidget) {
        return Tokens(
          tokens: DefaultTokens(),
          child: BlocProvider<RoleSelectionBloc>.value(
            value: roleSelectionBloc,
            child: routerWidget!,
          ),
        );
      },
    ),
  );
}
>>>>>>> REPLACE

- Tests to run after change:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart

2) [`test/helpers/pump_until_bloc_state.dart:1`](test/helpers/pump_until_bloc_state.dart:1) (CREATE)
- Final API (recommended implementation)
  - Filename: [`test/helpers/pump_until_bloc_state.dart:1`](test/helpers/pump_until_bloc_state.dart:1)
  - Public function:
    - Future<void> pumpUntilBlocState<BlocT extends BlocBase<StateT>, StateT>(
        WidgetTester tester,
        BlocT bloc,
        bool Function(StateT state) predicate, {
        Duration timeout = const Duration(seconds: 10),
        Duration pollInterval = const Duration(milliseconds: 50),
      })
  - Behavior:
    - Polls the bloc.state until predicate(state) returns true or the timeout elapses.
    - On success, returns normally.
    - On timeout, throws a descriptive TimeoutException to fail the test early (caller/test can catch and produce a protocol).
- Example implementation (for executor to add later):
<<CODE
import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

Future<void> pumpUntilBlocState<BlocT extends BlocBase<StateT>, StateT>(
  WidgetTester tester,
  BlocT bloc,
  bool Function(StateT state) predicate, {
  Duration timeout = const Duration(seconds: 10),
  Duration pollInterval = const Duration(milliseconds: 50),
}) async {
  final completer = Completer<void>();
  late final StreamSubscription sub;
  sub = bloc.stream.listen((raw) {
    final state = raw as StateT;
    if (predicate(state)) {
      if (!completer.isCompleted) completer.complete();
    }
  });
  // Check initial state as well
  final initial = bloc.state as StateT;
  if (predicate(initial)) {
    await sub.cancel();
    return;
  }
  final timer = Timer(timeout, () {
    if (!completer.isCompleted) completer.completeError(TimeoutException('Timed out waiting for bloc state', timeout));
  });
  try {
    // Poll the tester to allow async microtasks and widget rebuilds to advance
    while (true) {
      try {
        await tester.pump(pollInterval);
      } catch (_) {
        // ignore pump errors here; continue until timeout or predicate matches
      }
      if (completer.isCompleted) break;
      await Future<void>.delayed(Duration.zero);
    }
    await completer.future;
  } finally {
    timer.cancel();
    await sub.cancel();
  }
}
<<CODE
- Example usages (two target tests):
  - In [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
    ```
    await pumpUntilBlocState<PlanTemplatesBloc, PlanTemplatesState>(
      tester,
      mockPlanTemplatesBloc,
      (s) => s is PlanTemplatesLoaded || s is PlanTemplatesError,
      timeout: const Duration(seconds: 10),
    );
    ```
  - In [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
    ```
    await pumpUntilBlocState<PlanTemplateDetailBloc, PlanTemplateDetailState>(
      tester,
      mockPlanTemplateDetailBloc,
      (s) => s.status == PlanTemplateDetailStatus.loaded,
      timeout: const Duration(seconds: 10),
    );
    ```
- Backwards compatibility notes:
  - Helper is additive and does not modify any production code.
  - Place in [`test/helpers/pump_until_bloc_state.dart:1`](test/helpers/pump_until_bloc_state.dart:1) and import via relative path `../../../../../../helpers/pump_until_bloc_state.dart` in the tests to match current import patterns.

3) [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- Exact change list:
  - Add import for pump helper:
    - Insert `import '../../../../../../helpers/pump_until_bloc_state.dart';` near existing helper imports.
  - Replace the inline `mockPlanTemplatesBloc.add(const LoadPlanTemplates()); await tester.pumpAndSettleSafe();` pattern in `pumpTestWidget` with dispatch + `await pumpUntilBlocState<PlanTemplatesBloc, PlanTemplatesState>(...)`.
  - Replace test-level `await tester.pumpAndSettleSafe();` occurrences used to wait for data/navigation immediately after `pumpTestWidget(...)` with `pumpUntilBlocState` targeting the appropriate bloc (PlanTemplatesBloc or PlanTemplateDetailBloc).
  - Keep relaxed verification logic (try/catch counts) but reduce duplicate redundant `pumpAndSettleSafe` calls where `pumpUntilBlocState` already ensures readiness.
- Candidate apply_diff blocks (multiple replacement candidates)
<<<<<<< SEARCH
:start_line:11
-------
import '../../../../../../helpers/safe_pump.dart';
import 'package:mood_tracker/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart';
import 'package:mood_tracker/core/design_system/config/layout/layout_config.dart';
import 'package:mood_tracker/core/domain/services/screen_size/i_screen_size_service.dart';
import 'package:mood_tracker/core/design_system/config/screen_size.dart';
=======
import '../../../../../../helpers/safe_pump.dart';
import '../../../../../../helpers/pump_until_bloc_state.dart';
import 'package:mood_tracker/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart';
import 'package:mood_tracker/core/design_system/config/layout/layout_config.dart';
import 'package:mood_tracker/core/domain/services/screen_size/i_screen_size_service.dart';
import 'package:mood_tracker/core/design_system/config/screen_size.dart';
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:168
-------
    // Dispatch the initial LoadPlanTemplates event as the orchestrator would
    mockPlanTemplatesBloc.add(const LoadPlanTemplates());
    await tester.pumpAndSettleSafe();
=======
    // Dispatch the initial LoadPlanTemplates event as the orchestrator would
    mockPlanTemplatesBloc.add(const LoadPlanTemplates());
    await pumpUntilBlocState<PlanTemplatesBloc, PlanTemplatesState>(
      tester,
      mockPlanTemplatesBloc,
      (state) => state is PlanTemplatesLoaded || state is PlanTemplatesError,
      timeout: const Duration(seconds: 10),
    );
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:196
-------
      );
      await tester.pumpAndSettleSafe(); // Use safe pump to allow navigation to complete
=======
      );
      await pumpUntilBlocState<PlanTemplatesBloc, PlanTemplatesState>(
        tester,
        mockPlanTemplatesBloc,
        (state) => state is PlanTemplatesLoaded || state is PlanTemplatesError,
        timeout: const Duration(seconds: 10),
      ); // Wait for list data and router redirect to resolve
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:338
-------
      // Act
      await pumpTestWidget(
        tester,
        router,
        planTemplatesStateStream: Stream.fromIterable([PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList())]),
        initialPlanTemplatesState: PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList()),
        planTemplateDetailStateStream: Stream.fromIterable([const PlanTemplateDetailState(status: PlanTemplateDetailStatus.initial)]),
        initialPlanTemplateDetailState: const PlanTemplateDetailState(status: PlanTemplateDetailStatus.initial),
      );
      // Why: relaxed/timing guard - use safe pump helper to avoid timing flakiness in tests (see plans_and_protocols/part_attempt_02_protocol.md)
      await tester.pumpAndSettleSafe();
=======
      // Act
      await pumpTestWidget(
        tester,
        router,
        planTemplatesStateStream: Stream.fromIterable([PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList())]),
        initialPlanTemplatesState: PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList()),
        planTemplateDetailStateStream: Stream.fromIterable([const PlanTemplateDetailState(status: PlanTemplateDetailStatus.initial)]),
        initialPlanTemplateDetailState: const PlanTemplateDetailState(status: PlanTemplateDetailStatus.initial),
      );
      // Why: relaxed/timing guard - use explicit BLoC wait to avoid timing flakiness in tests (see plans_and_protocols/part_attempt_02_protocol.md)
      await pumpUntilBlocState<PlanTemplatesBloc, PlanTemplatesState>(
        tester,
        mockPlanTemplatesBloc,
        (s) => s is PlanTemplatesLoaded || s is PlanTemplatesError,
        timeout: const Duration(seconds: 10),
      );
>>>>>>> REPLACE

- Tests to run after change:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart

4) [`test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1)
- Exact change list:
  - Add import for safe pump helper: `import '../../../../../../helpers/safe_pump.dart';`
  - Replace `await tester.pumpAndSettle();` calls with `await tester.pumpAndSettleSafe();`
  - Ensure `getIt.reset()` is called in `tearDown()` (already present; keep).
- Candidate apply_diff blocks:
<<<<<<< SEARCH
:start_line:1
-------
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:mood_tracker/core/injection/injection_container.dart';
import 'package:mood_tracker/core/domain/services/screen_size/i_screen_size_service.dart';
import '../../../../../../helpers/mock_screen_size_service.dart';
import 'package:mood_tracker/features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart';
=======
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import '../../../../../../helpers/safe_pump.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:mood_tracker/core/injection/injection_container.dart';
import 'package:mood_tracker/core/domain/services/screen_size/i_screen_size_service.dart';
import '../../../../../../helpers/mock_screen_size_service.dart';
import 'package:mood_tracker/features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart';
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:98
-------
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans', isLargeScreen: false));
      await tester.pumpAndSettle();
=======
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans', isLargeScreen: false));
      await tester.pumpAndSettleSafe();
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:107
-------
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans/123', isLargeScreen: false));
      await tester.pumpAndSettle();
=======
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans/123', isLargeScreen: false));
      await tester.pumpAndSettleSafe();
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:116
-------
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans', isLargeScreen: true));
      await tester.pumpAndSettle();
=======
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans', isLargeScreen: true));
      await tester.pumpAndSettleSafe();
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:125
-------
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans/123', isLargeScreen: true));
      await tester.pumpAndSettle();
=======
      await tester.pumpWidget(createMinimalWidgetUnderTest(initialLocation: '/therapist/plans/123', isLargeScreen: true));
      await tester.pumpAndSettleSafe();
>>>>>>> REPLACE

- Tests to run after change:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart

Verification & commands
- Verification Level: L2 (widget tests). Justification: tests exercise `GoRouter` redirect logic and master-detail layout which are covered by widget tests per high-level plan and `doc/testing.md`.
- Phase-by-phase verification (commands and acceptance criteria):
  - Phase 1 (local verifications of helper and harness edits):
    1. flutter test test/helpers/pump_until_bloc_state.dart (no tests exist; this is a static lint/build check) — Acceptance: file compiles under `dart analyze` or `flutter test` with no syntax errors (exit code 0).
  - Phase 2 (run minimal test for harness changes):
    1. flutter test test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart — Acceptance: PASS (exit code 0). If failures, collect stdout and create `explore_test_blocker` protocol with stack traces.
  - Phase 3 (run comprehensive test):
    1. flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart — Acceptance: PASS (exit code 0) OR produce `explore_test_blocker` protocol if failing due to production code issues.
- Execution notes:
  - Run tests individually (do not run full suite) to minimize flakiness and make logs small.

Commit & workflow plan (one logical change per commit)
- Commit 1:
  - Message: "2025-10-29_impl_pilot_5: add pump_until_bloc_state test helper"
  - Files: [`test/helpers/pump_until_bloc_state.dart:1`](test/helpers/pump_until_bloc_state.dart:1)
  - Verification: run `dart analyze` and `flutter test` on the helper file (see above).
- Commit 2:
  - Message: "2025-10-29_impl_pilot_5: update test app wrapper to use MaterialApp.router builder"
  - Files: [`test/helpers/test_app_wrapper.dart:1`](test/helpers/test_app_wrapper.dart:1)
  - Verification: run `flutter test` on [`test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1)
- Commit 3:
  - Message: "2025-10-29_impl_pilot_5: update plan_templates_orchestrator_test to use pumpUntilBlocState"
  - Files: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
  - Verification: run `flutter test` on the same test file.
- Commit 4:
  - Message: "2025-10-29_impl_pilot_5: update orchestrator_minimal_test to use safe pump"
  - Files: [`test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1)
  - Verification: run `flutter test` on the minimal test and re-run the comprehensive test.
- Commit process notes:
  - Each commit must be followed by `git status` check and `flutter test <file>` verification.
  - If a commit introduces compile failures, revert with `git checkout -- <path>` and investigate locally.

Risk analysis & fallbacks
- Likely failures:
  1. GoRouter timing/microtask loops still causing pumpAndSettle hangs.
     - Mitigation: use `pumpUntilBlocState` and `pumpAndSettleSafe` per test context; if unresolved, convert failing flow into an `explore_test_blocker` with exact stack traces.
  2. DI leakage (GetIt) causing tests to pass in isolation but fail in suite.
     - Mitigation: call `GetIt.I.reset()` in `tearDown()` of affected tests; ensure helper doc comments emphasize this.
  3. BLoC `whenListen` not stubbing `.stream` correctly.
     - Mitigation: use `whenListen(..., Stream.fromIterable([...]), initialState: ...)` uniformly in tests.
- Fallback strategies:
  - If L2 stabilization fails after 3 attempts, escalate to L3 (targeted integration test) for the problematic redirect scenario to get higher confidence and better timing control.
  - If production code has a genuine bug blocking verification, produce `explore_test_blocker` protocol with failing test logs and propose minimal code fixes in a separate implementation task.

Complexity & timeboxing
- Estimates (developer experienced with this codebase):
  - Add helper [`test/helpers/pump_until_bloc_state.dart:1`](test/helpers/pump_until_bloc_state.dart:1): low complexity — 0.5h (including unit check)
  - Update test harness [`test/helpers/test_app_wrapper.dart:1`](test/helpers/test_app_wrapper.dart:1): low complexity — 0.25h
  - Update minimal test [`test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart:1): low complexity — 0.5h
  - Update comprehensive test [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1): medium complexity — 1.5h
- Recommended max_attempts per verification step: 5

Appendix A — recursive listing of `lib/` (shortened)
- See [`lib/`:1] (full recursive listing captured via list_files earlier)
  - config/routes/app_route_info.dart
  - config/routes/app_router.dart
  - config/routes/app_routes.dart
  - config/routes/route_utils.dart
  - features/therapist/plan_templates/plan_templates_routes.dart
  - features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart
  - core/design_system/organisms/layout/master_detail/master_detail_layout.dart

Appendix B — recursive listing of `test/` (selected relevant files)
- test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart
- test/helpers/safe_pump.dart
- test/helpers/more_screen_test_helpers.dart
- test/helpers/mock_screen_size_service.dart

Appendix C — repo search results (representative references used in the plan)
- `pumpAndSettleSafe` occurrences in:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:170`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:170)
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:196`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:196)
- `buildTestApp` defined in:
  - [`test/helpers/test_app_wrapper.dart:1`](test/helpers/test_app_wrapper.dart:1)

Questions for the orchestrator
1. Confirm default timeout for `pumpUntilBlocState` — accept default 10s or prefer different value?
2. Approve modifying the shared helper [`test/helpers/test_app_wrapper.dart:1`](test/helpers/test_app_wrapper.dart:1) to use `builder` globally (this affects other tests that use `buildTestApp`).
3. Can you run the `flutter test` verification commands on CI or locally and paste failing logs if any fail so I can produce `explore_test_blocker` protocols?

End of detailed implementation plan.