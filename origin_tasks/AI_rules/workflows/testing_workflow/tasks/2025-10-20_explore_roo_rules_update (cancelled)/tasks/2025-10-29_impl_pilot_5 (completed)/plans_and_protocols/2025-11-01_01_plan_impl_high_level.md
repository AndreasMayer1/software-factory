# High-level implementation plan — 2025-10-29_impl_pilot_5

produced_by: Roo (architect-mode)
timestamp: 2025-11-01T06:57:57Z
guidelines_read:
- doc/architecture.md
- doc/testing.md
- requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_5/goal.md
- .roo-templates/high_level_impl_plan.md
- test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart

summary:
This plan defines a focused, test-only Scope of Work to pilot the hierarchical testing orchestrator pattern using the plan_templates feature as the representative example. It intentionally targets unit/widget test updates and test-helper additions only. No application implementation changes are included in this scope.

goal:
- Pilot the orchestrator workflow (Outer Orchestrator -> Testing Orchestrator -> Test File Orchestrator -> Test-level subtasks) using plan_templates.
- Verify "code -> architect -> code" discipline at leaf-level subtasks.
- Ensure Phase 3 verification runs unit/widget tests via flutter test <file>.

Scope of Work (what will be done)
- Update or create only test files and test helpers required to make the pilot executable and verifiable.
- Do not modify application feature implementation files (lib/) as part of this pilot. If test results show application bugs that block verification, produce an explore_test_blocker protocol and escalate.

Files to be created or modified (canonical list)
1. test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart (MODIFY)
2. test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart (MODIFY)
3. test/helpers/pump_until_bloc_state.dart (CREATE)
4. test/helpers/test_app_wrapper.dart (MODIFY)

Justification for each file
- test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  - Why: This is the representative, currently-failing, comprehensive widget test exercising the orchestrator behavior (redirect-to-first-item, master/detail layout). The pilot requires updating this file to be deterministic, to follow the project's testing guidelines (use SafePump, pump-until patterns), and to be runnable via flutter test <file>. It is the primary artifact that the Testing Orchestrator will operate on.
- test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart
  - Why: Provides a minimal, fast set of assertions that exercise the master/detail rendering and routing logic. Keeping a small, deterministic minimal test helps isolate failures quickly and serves as a litmus test for the orchestrator's subtasks.
- test/helpers/pump_until_bloc_state.dart
  - Why: The testing guidelines (doc/testing.md) recommend helpers that wait for BLoC state sequences (pumpUntilBlocState/pumpUntilFound). Creating a small, shared helper reduces flaky timing issues and consolidates the "explicit state waiting" strategy used by multiple PlanTemplates tests.
- test/helpers/test_app_wrapper.dart
  - Why: Adjusting this helper to ensure the provided routerWidget from MaterialApp.router.builder is used (and to document DI/reset expectations) ensures tests that rely on GoRouter/StatefulShellRoute are executed inside the same widget tree used in production. This reduces a common class of test failures regarding missing router context.

Scope size check
- Count of Dart files to be modified/created in this scope: 4
- Is scope > 4 Dart files? NO
- Because the scope is within the allowed size, proceed with a single implementation task (no forced slicing required).

High-level steps (phases and verification)
- Phase 1 — Test authoring & update (what/why only)
  - Update the comprehensive widget test to be deterministic and aligned with guidelines (safe pumps and explicit BLoC waits).
  - Provide a minimal test variant for fast feedback.
  - Add the shared pumpUntilBlocState helper to reduce flakiness.
  - Update the test app wrapper to ensure routerWidget is used where necessary.
- Phase 2 — Implementation
  - NONE for this pilot (scope contains only test files and helpers). Per .roo-templates/high_level_impl_plan.md: skip Phase 2 when only test files are in scope.
- Phase 3 — Verification (Verification Level 2)
  - Execute targeted file-level tests using flutter test <file> (run each file individually).
  - Primary verification commands:
    - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
    - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart
  - Verification Level rationale: Level 2 (widget tests) is appropriate because acceptance criteria specify unit and widget tests in Phase 3; integration tests are explicitly out-of-scope.

Testing strategy (what tests to add/run, when)
- Focus on widget tests only (unit tests may be added if helpful, but widget tests are required by acceptance criteria).
- Run tests individually (not as part of full suite) to reduce flakiness and speed iteration.
- Use the new helper test/helpers/pump_until_bloc_state.dart to await BLoC emissions instead of relying on pumpAndSettle in places that cause router microtask loops.
- For any failing tests that appear to be caused by application logic (not test flakiness or environment setup), create an explore_test_blocker protocol documenting:
  - exact failing assertions and stack traces
  - which test(s) reproduce the failure in isolation
  - suggested minimal changes (for orchestrator review)
- Verify that test execution follows the orchestrator rule: tests must be executed by running flutter test <file> during Phase 3 (the Testing Orchestrator will record the command).

Risk analysis (concise)
- Risk: GoRouter and pumpAndSettle infinite microtask loops.
  - Impact: tests hang or timeout.
  - Mitigation: use SafePump and pumpUntilBlocState helper; avoid pumpAndSettle on router-involved flows without controlled waits.
- Risk: DI/GetIt state leakage between tests.
  - Impact: tests pass in isolation but fail in suite, or vice versa.
  - Mitigation: ensure tests reset GetIt between tests (getIt.reset() or unregister in tearDown). Document this expectation in the test helpers.
- Risk: Test flakiness due to timing/async dispatch.
  - Impact: intermittent test failures causing false blockers.
  - Mitigation: use explicit state-wait helpers, relax exact duplicate event count assertions (use >=1 where appropriate) and prefer deterministic mocks.
- Risk: The redirect-to-first-item orchestration depends on BLoC timeline.
  - Impact: redirect may not occur in a single pump; test must await router resolution (`await router.routeInformationProvider.value` or use pumpUntil helper).
  - Mitigation: the Verification Phase must run tests individually and include explicit waits; create explore_test_blocker if redirect does not happen due to production code bug.

Open assumptions (items that must be validated)
1. Tests are failing due to timing/flakiness rather than a deep application logic regression. Validation: run the failing test in isolation locally.
2. Existing test helpers (safe_pump, mock_screen_size_service) are usable; minor additions (pumpUntilBlocState) will be sufficient.
3. The feature implementation (lib/features/therapist/plan_templates/...) is functionally correct for the scenarios covered by the tests; code changes are only a fallback.
4. CI environment will run widget tests using `flutter test <file>` and has necessary desktop platform support when required by the test harness.

Acceptance / exit criteria for the implementation task following this plan
- The Testing Orchestrator can run the two test files listed above using flutter test <file> and reach a terminal PASS or produce explore_test_blocker protocols where necessary.
- The "code -> architect -> code" discipline is observable in the orchestrator subtask flow (reported by the orchestrator artifacts).
- The Phase 3 verification is completed at Verification Level 2 (widget tests).

Questions for orchestrator
- Are there any CI constraints (e.g., known differences in the CI test environment) we must consider when authoring tests for this pilot?
- Should the pilot include additional minimal unit tests for PlanTemplates BLoC to speed up diagnosis, or keep scope strictly to existing widget tests?

Appendix A — recursive listing of lib/ (shortened)
config/
config/routes/
config/routes/app_route_info.dart
config/routes/app_router.dart
config/routes/app_routes.dart
config/routes/route_utils.dart
config/theme/
config/theme/readme.me
config/theme/theme.dart
config/theme/tokens_extra.g.dart
config/theme/tokens.g.dart
core/
core/data/
core/data/adapters/
core/data/adapters/app_role_adapter.dart
core/data/repositories/
core/data/repositories/local_role_repository.dart
core/data/repositories/questionnaire_plan/
core/data/repositories/questionnaire_plan/local_choice_repository.dart
core/data/storage/
core/data/storage/storage_initializer.dart
core/design_system/
core/design_system/atoms/
core/design_system/atoms/background_svg.dart
core/design_system/atoms/client_status.dart
core/design_system/atoms/grid_example.dart
core/design_system/atoms/grid_layout.dart
core/design_system/atoms/typography.dart
core/design_system/atoms/inputs/likert_scale.dart
core/design_system/config/screen_size.dart
core/design_system/config/layout/layout_config.dart
core/design_system/config/layout/navigation.dart
core/design_system/config/layout/README.md
core/design_system/molecules/action_item_button.dart
core/design_system/molecules/error_display.dart
core/design_system/molecules/form_row.dart
core/design_system/molecules/input_field.dart
core/design_system/molecules/list_item.dart
core/design_system/molecules/radio_card.dart
core/design_system/organisms/grouped_action_list.dart
core/design_system/organisms/modal_dialog.dart
core/design_system/organisms/layout/base/app_bar_config.dart
core/design_system/organisms/layout/base/custom_navigation_bar.dart
core/design_system/organisms/layout/base/inherited_back_navigator.dart
core/design_system/organisms/layout/base/inherited_stack_navigator.dart
core/design_system/organisms/layout/base/stack_navigator_layout.dart
core/design_system/organisms/layout/base/stack_navigator.dart
core/design_system/organisms/layout/base/view_config.dart
core/design_system/organisms/layout/master_detail/detail_layout.dart
core/design_system/organisms/layout/master_detail/master_detail_layout.dart
core/design_system/organisms/layout/master_detail/master_layout.dart
core/design_system/organisms/layout/responsive/responsive_layout_builder.dart
features/
features/client/data_input/...
features/therapist/plan_templates/
features/therapist/plan_templates/plan_templates_routes.dart
features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart
generated/
generated/l10n/app_localizations_de.dart
generated/l10n/app_localizations_en.dart
generated/l10n/app_localizations.dart

Appendix B — relevant existing tests (short)
- test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- test/widget/features/therapist/plan_templates/presentation/widgets/orchestrator_minimal_test.dart

End of plan.