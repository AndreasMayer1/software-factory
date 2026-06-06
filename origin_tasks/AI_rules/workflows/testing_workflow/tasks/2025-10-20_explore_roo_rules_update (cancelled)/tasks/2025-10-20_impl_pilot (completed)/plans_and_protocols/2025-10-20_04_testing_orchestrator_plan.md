# 2025-10-20_04_testing_orchestrator_plan — Testing Orchestrator plan (Onboarding Screen)

Timestamp: 2025-10-20T20:10:17.607Z

Author: architect_subtask_2025-10-20_impl_pilot_depth_3

---

1) Header

- Title: 2025-10-20_04_testing_orchestrator_plan — Testing Orchestrator plan (Onboarding Screen)
- Timestamp: 2025-10-20T20:10:17.607Z
- Author: architect_subtask_2025-10-20_impl_pilot_depth_3

2) Concise summary of Phase 1 conclusions

- Phase 1 confirmed the pilot is tests-only and explicitly targets the onboarding screen ([`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md:1)).
- The initial plan verified the production file exists and scoped the work to a single test file to keep the pilot small and verifiable ([`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_01_plan_initial.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_01_plan_initial.md:1)).
- Validation confirmed core assumptions PASS; only advisory gaps were found (missing ancillary `.roo` checklists and explicit test helper documentation) that must be addressed by the Architect `arch_test_plan` ([`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_02_validation_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_02_validation_protocol.md:1)).
- The Phase 1 summary recommends proceeding to Phase 2: create an Architect `arch_test_plan` and then Code subtasks to implement `test/features/role_selection/presentation/screens/onboarding_screen_test.dart` ([`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_03_summary.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_03_summary.md:1)).

3) Risk assessment (top 3)

- Missing test helpers / DI hooks
  - Impact: Tests may require modifying production code or will be unimplementable until helpers exist.
  - Mitigation: Architect `arch_test_plan` must enumerate required helpers; reuse existing helpers under [`test/helpers/`](test/helpers/safe_pump.dart:1) (e.g., [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1), [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1), [`test/helpers/ui_test_helper.dart`](test/helpers/ui_test_helper.dart:1), [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:1)). If missing, Code subtasks should create small test-only helpers (suggested names: `test/helpers/router_test_helpers.dart`, `test/helpers/test_di.dart`).

- Untestable navigation / router-dependent flows
  - Impact: Navigation assertions and end-to-end flows cannot be verified in widget tests.
  - Mitigation: Use a router-aware test wrapper ([`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1)), or mock the navigation by stubbing the RoleSelectionBloc to produce `DialogRequested` states instead of relying on GoRouter redirects.

- Flaky async/pump timing and GoRouter initialization
  - Impact: Intermittent test failures (flaky CI).
  - Mitigation: Use [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1) patterns, prefer `pumpAndSettleSafe` helpers, and prefer explicit whenListen / MockBloc streams instead of complex real-time interactions.

4) Test File Orchestrator split (exact names)

- Test File Orchestrator name (exact): testfile_orchestrator_2025-10-20_onboarding_screen
- Target production file: [`lib/features/role_selection/presentation/screens/onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1)
- Target test file to be implemented by code subtasks: [`test/features/role_selection/presentation/screens/onboarding_screen_test.dart`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
- Exact deliverables the Test File Orchestrator must produce:
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_05_testfile_orchestrator_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_05_testfile_orchestrator_plan_onboarding_screen.md:1)
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md:1)

5) Architect requirement for the Test File Orchestrator

Summary to copy into the Test File Orchestrator instructions (must be produced by the Architect subtask as [`plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md:1)):

- The `arch_test_plan` MUST enumerate:
  1. Required test helpers (reuse and new)
     - Reuse existing helpers where applicable:
       - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
       - [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1)
       - [`test/helpers/ui_test_helper.dart`](test/helpers/ui_test_helper.dart:1)
       - [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:1)
     - New helpers to create if necessary (request from Orchestrator or create in-code-subtask):
       - `test/helpers/router_test_helpers.dart` — GoRouter test wrapper and utilities
       - `test/helpers/test_di.dart` — test-only DI registration helpers (register mocks)
       - `test/helpers/mock_role_repository.dart` — sample mock responses if tests require repository-level stubbing

  2. Explicit widget finders (exact `find.*` expressions and Key strings)
     - find.byKey('onboardingScreen') — main scaffold (exact Key string: onboardingScreen)
     - find.byType(CircularProgressIndicator)
     - find.byType(RoleSelectionDialog)
     - Additional finders (if added by Architect): find.byKey('roleSelectionDialog') — request adding this key if embedding the dialog requires stable selection

  3. Mocked repository / service / bloc responses (exact payloads and emission timing)
     - Use a MockBloc for `RoleSelectionBloc` (reuse [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:1) patterns).
     - Example sequences to stub via whenListen or StreamController:
       - Part A (loading): states -> [RoleSelectionInitial(), RoleSelectionLoading()]. No dialog shown; assert spinner visible.
       - Part B (dialog): states -> [RoleSelectionInitial(), DialogRequested()]. Assert that `RoleSelectionDialog` is present.
       - Part C (error): states -> [RoleSelectionInitial(), RoleSelectionError(message: 'network error')]. Assert SnackBar shows 'network error'.
     - Exact mock payload examples:
       - DialogRequested() // no payload
       - RoleSelectionError(message: 'network error')

  4. Exact assertions (what to assert and why)
     - Part A (Loading): expect(find.byType(CircularProgressIndicator), findsOneWidget) — verifies visual loading state.
     - Part B (Dialog): expect(find.byType(RoleSelectionDialog), findsOneWidget) — verifies the dialog flow is triggered by the bloc state.
     - Part C (Error): expect(find.byType(SnackBar), findsOneWidget) and expect(find.text('network error'), findsOneWidget) — verifies listener side-effect for errors.
     - Event dispatch verification: verify(mockRoleSelectionBloc.add(const CheckFirstLaunchRequested())); — verifies initState requested the check.

  5. Per-part acceptance conditions and acceptance checkers (machine-readable)
     - Part A: PASS if `expect(find.byType(CircularProgressIndicator), findsOneWidget)` passes.
     - Part B: PASS if `expect(find.byType(RoleSelectionDialog), findsOneWidget)` passes.
     - Part C: PASS if `expect(find.byType(SnackBar), findsOneWidget)` and `expect(find.text('network error'), findsOneWidget)` pass.
     - Each part must include `run_commands` (see Section 6) and example test snippets demonstrating `whenListen`/`MockBloc` setup and `verify(...add(...))`.
     - `expected_widget_states` must be explicit (e.g., "spinner visible", "dialog visible", "snackbar visible").
     - `fallbacks`: if finders fail, architect must provide alternate selectors (e.g., add stable Keys for dialog and important controls).

6) Phase 3 test run strategy and commands

- Primary command to run targeted tests (Phase 3 verification):
  - flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart

- Platform note: This is a unit/widget test; do NOT add `-d windows`. Only add `-d windows` when running integration tests that require a platform.

- Capture and artifacts:
  - Save console output, failing stack traces and full test protocol to: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_07_test_run_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_07_test_run_protocol.md:1)
  - Example capture command (orchestrator runs this and saves output):
    - flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart > [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_07_test_run_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_07_test_run_protocol.md:1) 2>&1

7) Acceptance criteria (PASS conditions)

- The Test File Orchestrator has created the Architect `arch_test_plan` and spawned `impl_test_part` code subtask(s).
- The `impl_test_part` subtask(s) implemented the test file at: [`test/features/role_selection/presentation/screens/onboarding_screen_test.dart`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)
- Running the command in Section 6 returns all tests PASS for that file, OR if failing, a documented `explore_test_blocker_<timestamp>` (architect) is created.
- If tests fail or environment blocks reproduction, the Testing Orchestrator (parent) will create `explore_test_blocker_<timestamp>` (architect) with logs and the [`plans_and_protocols/2025-10-20_07_test_run_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_07_test_run_protocol.md:1) attached.

8) Escalation & blocker protocol

- If missing test hooks, or more than 4 files would need modification, STOP Phase 2 and create: [`plans_and_protocols/2025-10-20_04_blocker_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_blocker_protocol.md:1)
  - The blocker file must list:
    - Exact files that would need modification (paths).
    - The reason each change is required.
    - Recommended split of work or permission request text to allow changes.

- If git commit fails at any point, capture `git status` output to: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/git_commit_error_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/git_commit_error_protocol.md:1) and STOP.

9) Git rules (MANDATORY)

- Start with a pre-change commit recording workspace state:
  - git commit --allow-empty -m "test(onboarding): pre-change snapshot - refs 2025-10-20_impl_pilot"
- After creating this plan file, run:
  - git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_testing_orchestrator_plan.md  (file: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_testing_orchestrator_plan.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_testing_orchestrator_plan.md:1))
  - git commit -m "test(onboarding): add testing orchestrator plan - refs 2025-10-20_impl_pilot"
- Important: Do NOT chain git add and git commit. Run `git add` and verify success before running `git commit`.
- If `git commit` fails, capture `git status` output to:
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/git_commit_error_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/git_commit_error_protocol.md:1)

10) Execution steps (suggested)

1. Read Phase 1 artifacts and confirm the production file: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md:1), [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_01_plan_initial.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_01_plan_initial.md:1), [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_02_validation_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_02_validation_protocol.md:1), production file [`lib/features/role_selection/presentation/screens/onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1).
2. Draft the Architect `arch_test_plan` as specified in Section 5 and save it to:
   - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md:1)
3. Test File Orchestrator: produce its plan (`2025-10-20_05_testfile_orchestrator_plan_onboarding_screen.md`) listing scope, files, and instruct Architect subtask to produce the `arch_test_plan`.
4. Code subtask(s): implement `test/features/role_selection/presentation/screens/onboarding_screen_test.dart` using the `arch_test_plan` as the source of truth; create any missing `test/helpers/*` files if required (limit to <= 4 files change rule).
5. Testing Orchestrator Phase 3: run `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart` and save logs as described in Section 6.
6. If tests fail and are reproducible, create `explore_test_blocker_<timestamp>` with attached logs; if failures are due to missing hooks or >4 files required, create [`plans_and_protocols/2025-10-20_04_blocker_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_blocker_protocol.md:1) and stop.

Important constraints

- Only create the single plan file [`plans_and_protocols/2025-10-20_04_testing_orchestrator_plan.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_testing_orchestrator_plan.md:1) in this subtask. Do NOT modify production code or other files.
- If you determine that more than 4 files must be modified to implement the tests, STOP and produce [`plans_and_protocols/2025-10-20_04_blocker_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_04_blocker_protocol.md:1) instead of proceeding.
- Do not spawn other subtasks; the parent orchestrator will create the Test File Orchestrator after you complete.

Signed-off-by: architect_subtask_2025-10-20_impl_pilot_depth_3