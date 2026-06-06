# 2025-10-29_02_validation_protocol.md
Timestamp: 2025-10-29T18:30:24.912Z
Author: architect_subtask_2025-10-29_impl_pilot_4

Executive verdict
- Plan Valid — The implementation plan's assumptions are actionable and test-only scope is supported by the codebase. Phase 2 may proceed with the recommended "arch_test_plan" creation and then the test modification `impl_test_part`.

Validated assumptions (each assumption from the impl plan with result, evidence and remediation if failed)

1) Assumption: Scope is tests-only (only the failing test file will be modified) and total Dart files to change <= 4.
- validated: true
- evidence:
  - Plan states scope: test-only and minimal files (see plan): [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md:31-36)
  - The referenced test file exists: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- remediation: N/A

2) Assumption: Required test helper `SafePump` exists.
- validated: true
- evidence:
  - `test/helpers/safe_pump.dart` present and exposes `pumpAndSettleSafe` extension: [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1-8)
- remediation: N/A

3) Assumption: Required test helper `test_app_wrapper` exists (or equivalent) for building MaterialApp.router test environment.
- validated: true
- evidence:
  - `test/helpers/test_app_wrapper.dart` exists and builds `MaterialApp.router` with localization and optional router param: [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:8-31)
- remediation: N/A

4) Assumption: BLoC/test stubbing patterns (mocktail, bloc_test, whenListen) are available in project and used in the test plan.
- validated: true
- evidence:
  - The test file imports `bloc_test`, `mocktail`, and uses `whenListen`, `MockBloc` pattern: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1-4,28-31,129-138)
  - `doc/testing.md` prescribes these patterns and provides `whenListen` guidance: [`doc/testing.md`](doc/testing.md:565-576,631-642)
- remediation: N/A

5) Assumption: The GoRouter-based orchestrator pattern used by the test can be constructed in a unit/widget test by creating a `StatefulShellRoute` test router with `PlanTemplatesRoutes.routes`.
- validated: true
- evidence:
  - Test file constructs `GoRouter` with `StatefulShellRoute.indexedStack` and spreads `PlanTemplatesRoutes.routes`: [`test/widget/.../plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:86-117,108-113)
  - `doc/testing.md` contains explicit guidance and examples for `StatefulShellRoute` test setup and confirms this approach: [`doc/testing.md`](doc/testing.md:947-977)
- remediation: N/A

6) Assumption: Screen size service helper `IScreenSizeService` is available and mockable for switching large/small screen logic in tests.
- validated: true
- evidence:
  - The test imports and mocks `IScreenSizeService` and stubs `getLayoutConfig` and `isLargeScreen`: [`test/.../plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:31-39,69-76)
  - `doc/architecture.md` references screen size patterns and `LayoutConfig` usage: [`doc/architecture.md`](doc/architecture.md:324-336)
- remediation: N/A

7) Assumption: Localization wiring (AppLocalizations) is available and included in test environment.
- validated: true
- evidence:
  - Test includes `localizationsDelegates` and `supportedLocales` in its `pumpWidget` setup: [`test/.../plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:146-157,148-153)
  - `test/helpers/test_app_wrapper.dart` also provides localization delegates: [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:19-29)
- remediation: N/A

8) Assumption: Required dev_dependencies (mocktail, bloc_test, flutter_test) are present in `pubspec.yaml`.
- validated: partial (quick check required)
- evidence:
  - The repo contains many tests that use `mocktail` and `bloc_test` (multiple test imports across `test/`), implying dev deps exist. Example usages: see test file imports: [`test/.../plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1-4)
- remediation: Before Phase 3 test execution, confirm `pubspec.yaml` contains `mocktail`, `bloc_test`, `flutter_test`, and run `flutter pub get`. If missing, add to `dev_dependencies`.

9) Assumption: No production source code changes are required for test stabilization (i.e., fixes are test-only or small test-helper additions).
- validated: true (with caution)
- evidence:
  - Plan explicitly aims to modify the test file only and suggests adding small test-only helpers only if needed: [`2025-10-29_01_plan_impl_pilot_4.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md:31-36,78)
  - The test file already contains stable patterns (whenListen, pumpAndSettleSafe, GetIt registration), indicating test-only approach is viable: [`test/.../plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:129-170,141-169)
- remediation: If during the `impl_test_part` the author finds missing DI hooks or production-level keys, create explicit small test-only helper files (see next section) and ensure total Dart files modified remains <=4. If more than 4 files are needed, follow the scope-too-large protocol.

Confirmed "Scope of Work" file list for Phase 2 (exact relative paths)
- Primary file to modify (Phase 2 code subtask will update this test file):
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- Architect artifact to be created in Phase 2 (Part 1):
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md:1)

Potential additional small test-only helper files (create only if truly required; each counts toward the 4-file limit):
- `test/helpers/router_test_helpers.dart` — helper to construct routers for tests (if current router creation is duplicated across tests).
- `test/helpers/test_di.dart` — helper to centralize GetIt test registrations and resets.

Note on file count:
- At present, planned modifications are to 1 Dart test file plus up to 2 small test helper files (conditional). This keeps the total <=4 Dart files. Therefore no scope-too-large protocol is required.

Phase 2 proceedability and required plan updates
- Phase 2 may proceed unchanged, subject to the following caveats:
  - Before running tests, confirm dev_dependencies in `pubspec.yaml` include `mocktail`, `bloc_test`, and `flutter_test`; run `flutter pub get`.
  - The `arch_test_plan` (Part 1) must explicitly list which test sections/individual tests will be modified in the test file, identify any missing helper functions, and declare whether any new test helper files are required.
  - If the `arch_test_plan` determines additional helpers are required that cause total Dart files to exceed 4, update the impl plan to slice work and create `2025-10-29_03_protocol_scope_too_large.md` as required by the workflow.
- Suggested edits (if any) to the impl plan:
  - Add a short explicit checklist item in the plan: "Confirm dev_dependencies present in pubspec.yaml and run flutter pub get" (precondition).
  - In the plan's "Files mapping & reasons" section, add exact expected helper file names if the arch_test_plan identifies them.

Preconditions and dependencies (checklist)
- [ ] Confirm `mocktail`, `bloc_test`, `flutter_test` present in `pubspec.yaml` and run `flutter pub get`.
- [ ] Confirm `test/helpers/safe_pump.dart` and `test/helpers/test_app_wrapper.dart` are used by the `arch_test_plan` (they exist and were validated).
- [ ] Ensure GetIt registrations in tests are properly reset in `tearDown` (the test file already unregisters GetIt singletons in `tearDown`).
- [ ] Ensure `AppRoutes.shellPlansBranch.navigatorKey` and `PlanTemplatesRoutes.routes` are stable and available in the library (they are referenced by the test; code inspection during implementation should confirm these declarations).
- [ ] Decide whether to run the widget test in isolation (`flutter test <file>`) or as part of a suite. The plan recommends targeted single-file runs.
- [ ] If any new helper test files are created, ensure they are small, documented, and added as separate `impl_test_part` subtasks as needed.

Next immediate subtask recommendation
- Create arch_test_plan:
  - Recommended subtask name: arch_test_plan
  - Suggested filename for architect deliverable: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md:1)
- Rationale: The arch_test_plan must split the test file into focused parts for `impl_test_part` subtasks, enumerate any missing helper utilities precisely, and include concrete stubbing/state sequences to be used by the code subtask.

If blocked or scope grows
- If during `arch_test_plan` analysis it becomes apparent that production code modification is required across >4 Dart files, follow the "scope too large" protocol by creating:
  - [`plans_and_protocols/2025-10-29_03_protocol_scope_too_large.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_03_protocol_scope_too_large.md:1)
  - The protocol must list the exact files and propose at least one concrete slicing (example slices: tests+helpers only; production router-only changes slice; DI helper slice).

Files created by this validation step
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_validation_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_validation_protocol.md:1)

Summary (one-paragraph)
- I validated the implementation plan for `impl_pilot_4` against the repository and project guidelines. The plan's assumptions are supported by existing helpers and test patterns; only one test file needs modification and any additional helpers are test-only, keeping the scope within the 4-file limit. Proceed to create the `arch_test_plan` artifact and then `impl_test_part` to update the test file.
