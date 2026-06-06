# Architect Test Plan — Onboarding Screen

Author: Roo, AI Architect
Date: 2025-10-20T20:31:22Z

Purpose

- Produce an architecture-level test plan for the Onboarding screen so the Test Part Orchestrator can create implementation subtasks.

Production files inspected

- [`lib/features/role_selection/presentation/screens/onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1)
- [`lib/features/role_selection/presentation/organisms/role_selection_dialog.dart`](lib/features/role_selection/presentation/organisms/role_selection_dialog.dart:1)
- [`lib/features/role_selection/presentation/molecules/role_selection_form.dart`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:1)
- [`lib/features/role_selection/presentation/bloc/role_selection_bloc.dart`](lib/features/role_selection/presentation/bloc/role_selection_bloc.dart:1)
- [`lib/features/role_selection/presentation/bloc/role_selection_state.dart`](lib/features/role_selection/presentation/bloc/role_selection_state.dart:1)
- [`lib/features/role_selection/domain/usecases/get_stored_role_use_case.dart`](lib/features/role_selection/domain/usecases/get_stored_role_use_case.dart:1)
- [`lib/features/role_selection/domain/usecases/persist_role_use_case.dart`](lib/features/role_selection/domain/usecases/persist_role_use_case.dart:1)
- [`lib/core/domain/entities/app_role.dart`](lib/core/domain/entities/app_role.dart:1)

Guidelines read

- [`doc/testing.md`](doc/testing.md:1)
- [`doc/architecture.md`](doc/architecture.md:1)

Summary

- Onboarding behaviour: On init the screen dispatches [`CheckFirstLaunchRequested`](lib/features/role_selection/presentation/bloc/role_selection_event.dart:10) to the [`RoleSelectionBloc`](lib/features/role_selection/presentation/bloc/role_selection_bloc.dart:11). Depending on the use case responses the bloc either emits `DialogRequested` (display role selection dialog) or `RolePersisted(AppRole)` (existing role — navigation handled by router).

High-level test goals

- Verify render and accessibility of onboarding UI (background, appbar, loading state).
- Verify behavior when stored role is present (no dialog, navigation state).
- Verify behavior when stored role is absent or first launch (dialog appears, role selection flow works, persistence called, navigation triggered).
- Verify error handling (snackbars) and edge cases.

1) Existing widget Keys (exact list)

- Found in production files:
  - [`ValueKey('onboardingScreen')`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:31) — Scaffold key in [`OnboardingScreen`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:30).
  - [`ValueKey('therapistRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:46) — label Text key inside [`RoleSelectionForm`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:40).
  - [`ValueKey('clientRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:52) — label Text key inside [`RoleSelectionForm`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:49).

2) Recommended stable Key strings (explicit proposals)

- Role buttons (preferred stable keys; existing keys are present but to ensure consistency across tests prefer onboarding-scoped keys):
  - `Key('onboarding_therapist_button')` (recommended replacement/alias for [`ValueKey('therapistRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:46))
  - `Key('onboarding_client_button')` (recommended replacement/alias for [`ValueKey('clientRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:52))
- Dialog & form:
  - `Key('role_selection_dialog')` — add to top-level `RoleSelectionDialog` widget (recommended).
  - `Key('role_selection_form')` — add to `RoleSelectionForm` root (recommended).
- Confirm/action button inside the dialog:
  - `Key('onboarding_confirm_button')` — add to the confirm `IconButton.filled` in [`role_selection_dialog.dart`](lib/features/role_selection/presentation/organisms/role_selection_dialog.dart:42).
- Optional keys for robustness:
  - `Key('onboarding_loading_indicator')` — add to loading CircularProgressIndicator to make loading assertions less brittle.

Rationale: Tests should prefer stable, explicit keys that include feature/screen prefixes to avoid collisions and make finders readable and maintainable.

3) Exact widget finders recommended

Note: acceptance snippets below use the project's style but to keep them compatible with orchestrator parsing use the shortfinder form and a precise Dart example for implementers.

Core finders (strings to use)

- Onboarding screen root:
  - Short form: [`find.byKey('onboardingScreen')`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:31)
  - Dart example: [`find.byKey(const ValueKey('onboardingScreen'))`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
- Background:
  - [`find.byType(BackgroundSvg)`](lib/core/design_system/atoms/background_svg.dart:9)
- Loading state:
  - [`find.byType(CircularProgressIndicator)`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:74)
  - Optional (if you add key): [`find.byKey('onboarding_loading_indicator')`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:74)
- RoleSelection dialog:
  - Short form: [`find.byType(RoleSelectionDialog)`](lib/features/role_selection/presentation/organisms/role_selection_dialog.dart:10)
  - If `role_selection_dialog` key added: [`find.byKey('role_selection_dialog')`](lib/features/role_selection/presentation/organisms/role_selection_dialog.dart:10)
- Role buttons:
  - Existing keys: [`find.byKey('therapistRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:46) and [`find.byKey('clientRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:52)
  - Recommended stable keys: [`find.byKey('onboarding_therapist_button')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:46) and [`find.byKey('onboarding_client_button')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:52)
  - Dart example: [`final clientButton = find.byKey(const ValueKey('clientRoleButton'));`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
- Confirm button:
  - Short form: [`find.byKey('onboarding_confirm_button')`](lib/features/role_selection/presentation/organisms/role_selection_dialog.dart:42)
  - Dart example: [`final confirm = find.byKey(const ValueKey('onboarding_confirm_button'));`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
- Snackbars / error messages:
  - [`find.byType(SnackBar)`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:56)
  - [`find.text('...')`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:58) — use localized message text where possible.

4) Helpers & test setup (which to reuse from repo)

Required / strongly recommended helpers (select from orchestrator list)

- [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:8)
  - Why: provides a MaterialApp.router wrapper and convenient injection of a `RoleSelectionBloc`. Use it to inject a mocked bloc or use the `getMockRoleSelectionBloc()` from bloc_test_helper.
- [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
  - Why: provides a small, deterministic pump pattern (`pumpAndSettleSafe`) to avoid flaky pumps in CI.
- [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:11)
  - Why: provides `MockGetStoredRoleUseCase`, `MockPersistRoleUseCase`, `MockCheckFirstLaunchUseCase` and `getMockRoleSelectionBloc()` — useful for unit-testing the bloc or for wiring use-case mocks into the bloc instance.
- [`test/helpers/more_screen_test_helpers.dart`](test/helpers/more_screen_test_helpers.dart:28)
  - Why: includes `MockRoleSelectionBloc` and `MockGoRouter` plus `pumpAndSettleMoreScreenTestApp` which helps assert navigation interactions when an initial role is present.
- [`test/helpers/ui_test_helper.dart`](test/helpers/ui_test_helper.dart:14)
  - Why: wrapping helpers, screen sizes and accessibility helpers; useful when running tests with various screen sizes.

Optional helpers (use if needed)

- [`test/helpers/mock_screen_size_service.dart`](test/helpers/mock_screen_size_service.dart:1) — if Onboarding contains responsive behaviour you need to control.
- [`test/helpers/fake_path_provider_platform.dart`](test/helpers/fake_path_provider_platform.dart:1) — only if persistence uses path_provider/hive during tests that must be sandboxed.

Additional helpers I recommend creating (do not implement here)

- `test/helpers/role_test_helpers.dart`
  - Purpose: small helpers to create commonly used mocked responses, e.g. `stubCheckFirstLaunchTrue(MockCheckFirstLaunchUseCase)`, `stubGetStoredRoleClient(MockGetStoredRoleUseCase)`, `stubPersistRoleSuccess(MockPersistRoleUseCase)` — reduces duplication across parts.
- `test/helpers/mock_router_verifier.dart`
  - Purpose: a small wrapper that exposes `verifyDidNavigateTo(String routeName)` using `MockGoRouter` or `MockNavigatorObserver` so tests can assert navigation without depending on concrete route implementation.

5) Mocking & repository/service contract (exact signatures and examples)

Use-case method signatures to mock

- [`CheckFirstLaunchUseCase.call()`](lib/features/role_selection/domain/usecases/check_first_launch_use_case.dart:12)
  - signature: `Future<Either<Failure, bool>> call()`
- [`GetStoredRoleUseCase.call()`](lib/features/role_selection/domain/usecases/get_stored_role_use_case.dart:13)
  - signature: `Future<Either<Failure, AppRole?>> call()`
- [`PersistRoleUseCase.call(String? roleValue)`](lib/features/role_selection/domain/usecases/persist_role_use_case.dart:13)
  - signature: `Future<Either<Failure, void>> call(String? roleValue)`

Mocking examples (using mocktail style — adapt to existing test conventions)

- Case: getStoredRole returns null (not stored)
  - Stubs:
    - `when(() => mockCheckFirstLaunchUseCase.call()).thenAnswer((_) async => Right(false));`
    - `when(() => mockGetStoredRoleUseCase.call()).thenAnswer((_) async => Right(null));`
  - Timing: immediate async response (use `async => Right(...)`) is sufficient. Test pump sequence should allow bloc events to process (see pumps section).

- Case: getStoredRole returns Client
  - Stubs:
    - `when(() => mockCheckFirstLaunchUseCase.call()).thenAnswer((_) async => Right(false));`
    - `when(() => mockGetStoredRoleUseCase.call()).thenAnswer((_) async => Right(const AppRole.client()));`
  - Expected: bloc emits `RolePersisted(const AppRole.client())` and router navigation should be triggered by app wiring.

- Case: getStoredRole returns Therapist
  - Stubs:
    - `when(() => mockCheckFirstLaunchUseCase.call()).thenAnswer((_) async => Right(false));`
    - `when(() => mockGetStoredRoleUseCase.call()).thenAnswer((_) async => Right(const AppRole.therapist()));`

- Persist role (when user confirms):
  - Stubs for success:
    - `when(() => mockPersistRoleUseCase.call(AppRole.client().value)).thenAnswer((_) async => Right(null));`
  - Stubs for failure:
    - `when(() => mockPersistRoleUseCase.call(any())).thenAnswer((_) async => Left(RoleFailure('persist error')));`

Notes on dartz/Either typing
- Some usecases return `Either<Failure, void>` — returning `Right(null)` is acceptable in tests for the success branch, or use `Right(unit)` if `unit` is available. Match repository conventions used elsewhere in tests.

6) Test splitting & per-part acceptance criteria

Part 1 — Render & accessibility
- part_id: p1
- description: Verify OnboardingScreen renders and shows loading state initially.
- required_helpers:
  - [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:8)
  - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
- mock_strategy:
  - Stub `mockCheckFirstLaunchUseCase.call()` to complete slowly if you want; by default return `Right(true)` or leave the bloc in `RoleSelectionInitial`.
- selectors / finders:
  - [`find.byKey('onboardingScreen')`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:31)
  - [`find.byType(BackgroundSvg)`](lib/core/design_system/atoms/background_svg.dart:9)
  - [`find.byType(CircularProgressIndicator)`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:74)
- acceptance condition (Dart-like snippet):
  - [`expect(find.byKey(const ValueKey('onboardingScreen')), findsOneWidget);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
  - [`expect(find.byType(BackgroundSvg), findsOneWidget);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
  - [`expect(find.byType(CircularProgressIndicator), findsOneWidget);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
- run_commands:
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "renders onboarding loading" -d windows`
- estimated_complexity: low
- recommended_max_attempts: 2

Part 2 — Initial state & stored-role behavior
- part_id: p2
- description: Verify behavior when stored role exists or is missing.
- required_helpers:
  - [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:11)
  - [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:8)
  - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
- cases:
  - Case A: `getStoredRole` returns `null` -> dialog shown
    - stubs:
      - `when(() => mockCheckFirstLaunchUseCase.call()).thenAnswer((_) async => Right(false));`
      - `when(() => mockGetStoredRoleUseCase.call()).thenAnswer((_) async => Right(null));`
    - actions:
      - pump app and allow bloc to process: [`await tester.pumpAndSettleSafe();`](test/helpers/safe_pump.dart:1)
    - assertions:
      - [`expect(find.byType(RoleSelectionDialog), findsOneWidget);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
  - Case B: `getStoredRole` returns `AppRole.client` -> role persisted, no dialog
    - stubs:
      - `when(() => mockCheckFirstLaunchUseCase.call()).thenAnswer((_) async => Right(false));`
      - `when(() => mockGetStoredRoleUseCase.call()).thenAnswer((_) async => Right(const AppRole.client()));`
    - assertions:
      - [`expect(find.byType(RoleSelectionDialog), findsNothing);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
      - Optionally verify navigation via `MockGoRouter`:
        - `verify(() => mockGoRouter.go(any())).called(1);` (use `more_screen_test_helpers` MockGoRouter).
- run_commands:
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "stored role behavior" -d windows`
- estimated_complexity: medium
- recommended_max_attempts: 3

Part 3 — Role selection interactions & navigation
- part_id: p3
- description: Verify the user can select a role, confirm, the usecase `persistRole` is invoked, and navigation/RolePersisted occurs.
- required_helpers:
  - [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:8)
  - [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:11)
  - [`test/helpers/more_screen_test_helpers.dart`](test/helpers/more_screen_test_helpers.dart:28)
  - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
- actions (exact finder + action sequence):
  - Show the dialog (either stub CheckFirstLaunch as `Right(true)` or force bloc to emit `DialogRequested`).
  - Find client button:
    - [`final clientButton = find.byKey(const ValueKey('clientRoleButton'));`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
    - [`await tester.tap(clientButton);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
    - [`await tester.pumpAndSettleSafe();`](test/helpers/safe_pump.dart:1)
  - Find confirm button:
    - [`final confirm = find.byKey(const ValueKey('onboarding_confirm_button'));`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
    - [`await tester.tap(confirm);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
    - [`await tester.pumpAndSettleSafe();`](test/helpers/safe_pump.dart:1)
- mock strategy:
  - `when(() => mockPersistRoleUseCase.call(AppRole.client().value)).thenAnswer((_) async => Right(null));`
- acceptance assertions:
  - Persist usecase called:
    - `verify(() => mockPersistRoleUseCase.call(AppRole.client().value)).called(1);`
  - RolePersisted emitted and navigation attempted:
    - [`expect(find.byType(RoleSelectionDialog), findsNothing);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
    - `verify(() => mockGoRouter.go(any())).called(1);`
- run_commands:
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "role selection flow" -d windows`
- estimated_complexity: medium
- recommended_max_attempts: 5

Part 4 — Optional edge cases
- part_id: p4
- description: Persist failure and CheckFirstLaunch / getStoredRole failures produce SnackBar errors; accessibility checks.
- required_helpers:
  - [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:8)
  - [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:11)
- example failure case (persist fails):
  - stub:
    - `when(() => mockPersistRoleUseCase.call(any())).thenAnswer((_) async => Left(RoleFailure('persist error')));`
  - actions:
    - select role + tap confirm as in Part 3
  - assertions:
    - [`expect(find.byType(SnackBar), findsOneWidget);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
    - [`expect(find.text('persist error'), findsOneWidget);`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
- accessibility checks:
  - `expect(find.bySemanticsLabel(l10n.roleSelectionFormLabel), findsOneWidget);`
- run_commands:
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "onboarding edge cases" -d windows`
- estimated_complexity: medium
- recommended_max_attempts: 3

7) Test order, pumps, and timing (recommended)

- General pump pattern (use `safe_pump.dart`):
  - `await tester.pumpWidget(buildTestApp(...));`
  - `await tester.pump(); // allow initState to run and bloc to receive CheckFirstLaunchRequested`
  - `await tester.pumpAndSettleSafe(); // small extra pump to process microtasks`
  - `await tester.pumpAndSettle(); // final settle for animations if necessary`
- When you rely on bloc events that `add` additional events (the bloc uses `add(ShowRoleDialog())`), include one extra `await tester.pump();` after `pumpAndSettleSafe()` to give the event loop a chance to deliver the new state.
- Avoid long artificial delays; prefer small pumps (100ms) and `pumpAndSettle` with a moderate timeout.

8) Failure escalation rules

- If tests require changes to production source (e.g., missing keys that make tests brittle) you may add recommendation but do not change production files in this architect task.
- If implementing the tests will require modifying more than 4 production files or adding integration-level side-effects, create a blocker protocol file:
  - `requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_blocker_protocol.md`
  - The blocker file must list the required production changes and affected files.
- Current analysis: no blocker required. Tests can be implemented with existing code. Recommended improvements (adding keys for dialog and confirm button) are optional and will make tests more robust but are not mandatory.

9) Verification commands (Phase 3)

- Run the specific part tests:
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "renders onboarding loading" -d windows`
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "stored role behavior" -d windows`
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "role selection flow" -d windows`
  - `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart --plain-name "onboarding edge cases" -d windows`

10) Artifacts and where to save

- Save this plan as:
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md:1)
- Per-part attempt logs:
  - `plans_and_protocols/part_attempt_<n>_protocol.md`

11) Commit instructions (manual steps for the architect task)

- After this file is created run (do not chain commands):
  1. `git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md`
  2. `git commit -m "test(onboarding): add arch_test_plan - refs 2025-10-20_impl_pilot"`
- If `git commit` fails capture `git status` and save it as:
  - `plans_and_protocols/git_commit_error_protocol.md`

12) Short summary for orchestrator (keys / finders)

- Keys found: [`ValueKey('onboardingScreen')`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:31), [`ValueKey('therapistRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:46), [`ValueKey('clientRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:52)
- Keys proposed: `onboarding_therapist_button`, `onboarding_client_button`, `role_selection_dialog`, `role_selection_form`, `onboarding_confirm_button`, `onboarding_loading_indicator`
- Primary finders to implement first in tests:
  - [`find.byKey('clientRoleButton')`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:52)
  - [`find.byKey('onboarding_confirm_button')`](lib/features/role_selection/presentation/organisms/role_selection_dialog.dart:42)

---------------------------------------------------------------------
End of architect test plan.