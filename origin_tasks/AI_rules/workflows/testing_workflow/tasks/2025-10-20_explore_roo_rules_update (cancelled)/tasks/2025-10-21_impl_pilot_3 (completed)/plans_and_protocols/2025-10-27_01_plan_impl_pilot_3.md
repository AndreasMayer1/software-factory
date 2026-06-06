# 2025-10-27_01_plan_impl_pilot_3.md

- Created: 2025-10-27T11:07:39Z (UTC)
- Author: Roo (architect)
- Git pre-change snapshot: branch main

## Context (files read)
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_3/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_3/goal.md:1)
- [`doc/architecture.md`](doc/architecture.md:1)
- [`doc/testing.md`](doc/testing.md:1)
- Current failing test observed: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)

## Goal of this plan
Produce a verifiable, executable implementation plan to pilot the hierarchical testing orchestrator pattern described in the goal above, using the `plan_templates` feature as the example. The plan must be explicit and scoped so code-mode subtasks can implement it without further design work.

## High-level approach
1. Validate and stabilize the representative failing widget tests for the `plan_templates` feature.
2. Use the stabilized tests as the verification target for the Testing Orchestrator pilot.
3. Record all artifacts under the task's `plans_and_protocols` folder (`arch_test_plan`s, per-attempt protocols, verification logs).

## Full lib/ directory snapshot (recursive)
(snapshot taken using the project file listing tool)
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
config/theme/figma/
config/theme/figma/tokens.json
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
core/design_system/actions_interface.dart
core/design_system/atoms/
core/design_system/atoms/background_svg.dart
core/design_system/atoms/client_status.dart
core/design_system/atoms/grid_example.dart
core/design_system/atoms/grid_layout.dart
core/design_system/atoms/typography.dart
core/design_system/atoms/inputs/likert_scale.dart
core/design_system/config/screen_size.dart
core/design_system/config/layout/layout_config.dart
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
core/domain/entities/action_group.dart
core/domain/entities/action_item.dart
core/domain/entities/action_type.dart
core/domain/entities/app_role.dart
core/domain/entities/questionnaire_plan_entities.dart
core/domain/entities/questionnaire_plan/questionnaire_plan.dart
core/domain/entities/questionnaire_plan_entities/choice_options.dart
core/domain/entities/questionnaire_plan_entities/choice.dart
core/domain/entities/questionnaire_plan_entities/exceptions.dart
core/domain/entities/questionnaire_plan_entities/likert_options.dart
core/domain/entities/questionnaire_plan_entities/question_type.dart
core/domain/entities/questionnaire_plan_entities/question.dart
core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart
core/domain/entities/questionnaire_plan_entities/questionnaire.dart
core/domain/entities/questionnaire_plan_entities/time_input_type.dart
core/domain/entities/questionnaire_plan_entities/time_interval_type.dart
core/domain/entities/questionnaire_plan_entities/time_interval.dart
core/domain/entities/questionnaire_plan_entities/time_label_type.dart
core/domain/entities/questionnaire_plan_entities/time_options.dart
core/domain/entities/questionnaire_plan_entities/version_constants.dart
core/domain/entities/questionnaire_plan_entities/v1/choice_options.dart
core/domain/entities/questionnaire_plan_entities/v1/choice.dart
core/domain/entities/questionnaire_plan_entities/v1/exceptions.dart
core/domain/entities/questionnaire_plan_entities/v1/likert_options.dart
core/domain/entities/questionnaire_plan_entities/v1/question_type.dart
core/domain/entities/questionnaire_plan_entities/v1/question.dart
core/domain/entities/questionnaire_plan_entities/v1/questionnaire_plan.dart
core/domain/entities/questionnaire_plan_entities/v1/questionnaire.dart
core/domain/entities/questionnaire_plan_entities/v1/time_input_type.dart
core/domain/entities/questionnaire_plan_entities/v1/time_interval_type.dart
core/domain/entities/questionnaire_plan_entities/v1/time_interval.dart
core/domain/entities/questionnaire_plan_entities/v1/time_label_type.dart
core/domain/entities/questionnaire_plan_entities/v1/time_options.dart
core/domain/entities/questionnaire_plan_entities/v1/v1.dart
core/domain/entities/questionnaire_plan_entities/v1/version_constants.dart
core/domain/events/questionnaire_plan/event_publisher.dart
core/domain/events/questionnaire_plan/events.dart
core/domain/failures/failures.dart
core/domain/failures/questionnaire_plan/choice_failures.dart
core/domain/failures/questionnaire_plan/question_failures.dart
core/domain/failures/questionnaire_plan/questionnaire_failures.dart
core/domain/failures/questionnaire_plan/questionnaire_plan_failures.dart
core/domain/repositories/role_repository.dart
core/domain/repositories/questionnaire_plan/choice_repository.dart
core/domain/repositories/questionnaire_plan/mock_choice_repository.dart
core/domain/repositories/questionnaire_plan/mock_question_repository.dart
core/domain/repositories/questionnaire_plan/mock_questionnaire_plan_repository.dart
core/domain/repositories/questionnaire_plan/mock_questionnaire_repository.dart
core/domain/repositories/questionnaire_plan/question_repository.dart
core/domain/repositories/questionnaire_plan/questionnaire_plan_repository.dart
core/domain/repositories/questionnaire_plan/questionnaire_repository.dart
core/domain/services/questionnaire_plan/choice_service_impl.dart
core/domain/services/questionnaire_plan/choice_service.dart
core/domain/services/questionnaire_plan/question_service_impl.dart
core/domain/services/questionnaire_plan/question_service.dart
core/domain/services/questionnaire_plan/questionnaire_plan_service_impl.dart
core/domain/services/questionnaire_plan/questionnaire_plan_service.dart
core/domain/services/questionnaire_plan/questionnaire_service_impl.dart
core/domain/services/questionnaire_plan/questionnaire_service.dart
core/domain/services/questionnaire_plan/serialization_utils.dart
core/domain/services/screen_size/i_screen_size_service.dart
core/domain/services/screen_size/screen_size_service_impl.dart
core/error/failure.dart
core/injection/injection_container.config.dart
core/injection/injection_container.dart
core/injection/presentation_di.dart
core/widgets/client/client_navigation_ui.dart
core/widgets/layout/default_detail_placeholder.dart
core/widgets/layout/scaffold_builder.dart
core/widgets/therapist/therapist_navigation_ui.dart
features/
features/client/data_input/injection_container.dart
features/client/data_input/presentation/bloc/data_input_bloc.dart
features/client/data_input/presentation/bloc/data_input_event.dart
features/client/data_input/presentation/bloc/data_input_state.dart
features/client/data_input/presentation/organisms/data_input_detail_view.dart
features/client/data_input/presentation/screens/client_data_input_root_screen.dart
features/client/data_input/presentation/widgets/empty_state.dart
features/client/data_input/presentation/widgets/likert_input.dart
features/client/data_input/presentation/widgets/question_card.dart
features/client/data_input/presentation/widgets/question_header.dart
features/home/presentation/screens/home_screen.dart
features/more/presentation/layout/more_layout_config.dart
features/more/presentation/screens/about_screen.dart
features/more/presentation/screens/appearance_settings_screen.dart
features/more/presentation/screens/more_root_screen.dart
features/more/presentation/screens/notification_preferences_screen.dart
features/more/presentation/screens/privacy_policy_screen.dart
features/more/presentation/screens/terms_of_service_screen.dart
features/more/presentation/widgets/more_master_view.dart
features/role_selection/domain/usecases/check_first_launch_use_case.dart
features/role_selection/domain/usecases/get_stored_role_use_case.dart
features/role_selection/domain/usecases/persist_role_use_case.dart
features/role_selection/presentation/bloc/role_selection_bloc.dart
features/role_selection/presentation/bloc/role_selection_event.dart
features/role_selection/presentation/bloc/role_selection_state.dart
features/role_selection/presentation/molecules/role_selection_form.dart
features/role_selection/presentation/organisms/role_selection_dialog.dart
features/role_selection/presentation/screens/onboarding_screen.dart
features/therapist/therapist_routes.dart
features/therapist/clients/clients_routes.dart
features/therapist/clients/presentation/bloc/client_plan_detail_bloc.dart
features/therapist/clients/presentation/bloc/client_plan_detail_event.dart
features/therapist/clients/presentation/bloc/client_plan_detail_state.dart
features/therapist/clients/presentation/bloc/client_plans_bloc.dart
features/therapist/clients/presentation/bloc/client_plans_event.dart
features/therapist/clients/presentation/bloc/client_plans_state.dart
features/therapist/clients/presentation/bloc/therapist_clients_bloc.dart
features/therapist/clients/presentation/bloc/therapist_clients_event.dart
features/therapist/clients/presentation/bloc/therapist_clients_state.dart
features/therapist/clients/presentation/molecules/client_action_buttons.dart
features/therapist/clients/presentation/molecules/client_title_description.dart
features/therapist/clients/presentation/organisms/client_list.dart
features/therapist/clients/presentation/organisms/client_plan_detail_view.dart
features/therapist/clients/presentation/organisms/client_plans_view.dart
features/therapist/clients/presentation/screens/therapist_client_detail_screen.dart
features/therapist/clients/presentation/widgets/therapist_clients_orchestrator.dart
features/therapist/inbox/presentation/screens/inbox_screen.dart
features/therapist/inbox/presentation/screens/therapist_inbox_root_screen.dart
features/therapist/plan_templates/plan_templates_routes.dart
features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart
features/therapist/plan_templates/presentation/bloc/plan_template_detail_event.dart
features/therapist/plan_templates/presentation/bloc/plan_template_detail_event.freezed.dart
features/therapist/plan_templates/presentation/bloc/plan_template_detail_state.dart
features/therapist/plan_templates/presentation/bloc/plan_template_detail_state.freezed.dart
features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart
features/therapist/plan_templates/presentation/bloc/plan_templates_event.dart
features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart
features/therapist/plan_templates/presentation/mock/mock_plans.dart
features/therapist/plan_templates/presentation/molecules/plan_action_buttons.dart
features/therapist/plan_templates/presentation/molecules/plan_title_description.dart
features/therapist/plan_templates/presentation/organisms/plan_detail_view.dart
features/therapist/plan_templates/presentation/organisms/plan_list.dart
features/therapist/plan_templates/presentation/organisms/plan_template_detail_content.dart
features/therapist/plan_templates/presentation/widgets/plan_details_form.dart
features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart
features/therapist/plan_templates/presentation/widgets/questionnaire_details_view.dart
features/therapist/plan_templates/presentation/widgets/questionnaire_summary_card.dart
features/therapist/plan_templates/presentation/widgets/responsive_questionnaire_list.dart
generated/
generated/l10n/app_localizations_de.dart
generated/l10n/app_localizations_en.dart
generated/l10n/app_localizations.dart
l10n/

## Problem statement (from reading the test)
The existing test file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) contains a comprehensive set of widget tests that exercise route redirects, master-detail rendering, and orchestration behavior. Failures observed in CI/local runs for this pilot are consistent with common timing and GoRouter interaction issues documented in [`doc/testing.md`](doc/testing.md:1) (pumpAndSettle timeouts, router async redirects, test isolation / GetIt state leakage).

Key failure modes to address:
- Race conditions between BLoC state emission and GoRouter async redirect handling.
- Missing DI reset between tests causing GetIt registration conflicts.
- Use of `pumpAndSettle` without safe guard causing flakiness with GoRouter microtasks.

## Scope of Work (definitive file list)
The plan is intentionally scoped to a small, implementable set of files to keep the pilot focused and reviewable. These are the only files the implementer is allowed to modify for this task:
1. [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_3/plans_and_protocols/2025-10-27_01_plan_impl_pilot_3.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_3/plans_and_protocols/2025-10-27_01_plan_impl_pilot_3.md:1) (create) — this plan file
2. [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) (modify) — stabilize failing tests and add small test-safety improvements

(Total files to modify: 2 — within the 4-file limit. If maintainers need additional changes, request a separate follow-up task.)

## Recommended Verification Level and justification
Recommendation: Verification Level 2 (run targeted widget tests / file-level verification).
Justification:
- The pilot focuses on widget tests only (per `goal.md`), not integration tests.
- Level 2 maps to executing `flutter test <test-file>` for widget tests and collecting the test output logs.
- Running the single test file keeps feedback fast and isolates regressions to the modified tests.
- If the file-level verification passes reliably across a few iterations, escalate to Level 3 only if broader suite instability is suspected.

## Testing strategy (which tests to add/update and why)
- Primary target (update): [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
  - Reason: Representative of orchestrator-led master-detail and redirect logic; already contains failing cases used by the pilot.
- Verification commands:
  - Local run (single file): flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  - CI run (after local pass): same command executed by orchestrator during Phase 3 verification.
- Expected verification artifacts:
  - Per-attempt protocol file in `plans_and_protocols/` capturing test run stdout/stderr and exit code.

## Step-by-step implementation breakdown (to hand to code-mode)
Each step must be committed separately. Commit messages must reference the task folder name (impl_pilot_3).

Step 0 — Pre-implementation (manual, by orchestrator): capture exact git commit hash for the branch to be used and attach it to the protocol. (E.g., run `git rev-parse --short HEAD`).

Step 1 — Create the plan file (this file).
- Files changed: (create)
  - [`requirements_tasks/.../2025-10-27_01_plan_impl_pilot_3.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_3/plans_and_protocols/2025-10-27_01_plan_impl_pilot_3.md:1)
- Description: add the plan file to the task's `plans_and_protocols`.
- Tests: none (planning step).
- Commit: git add & commit with message: "impl_pilot_3: add plan 2025-10-27_01"

Step 2 — Stabilize the failing widget tests (main code-mode subtask)
- Files changed:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- Concrete modifications to make (apply as minimal diffs; do not change production code):
  1. Test isolation & DI cleanup
     - In `setUp()` add a defensive call to `GetIt.I.reset()` at the start (or call `GetIt.I.reset(dispose: true)` in `tearDown()`), to ensure no leftover singletons from other tests cause registration conflicts.
     - Replace per-type `GetIt.I.unregister<T>()` calls in `tearDown()` with a single `await GetIt.I.reset();` to ensure clean container.
     - Rationale: the `doc/testing.md` recommends resetting DI between tests to avoid state leakage.
  2. Stream/State stubbing robustness
     - Where `whenListen` is used, ensure `initialState:` is set and that the stream sequence includes the sequence the test relies on (e.g., initial -> loaded).
     - If a test needs to simulate a delayed load (router redirect awaiting data), use a `StreamController` and `add` the loaded state after the test pumps once, to emulate asynchronous arrival. (Example pseudocode will be provided in the code-mode subtask).
  3. GoRouter async redirect stability
     - Replace `await tester.pumpAndSettle()` calls that previously timed out with `await tester.pumpAndSettleSafe()` (the existing helper in `test/helpers/safe_pump.dart`) wherever GoRouter navigation/redirects are expected.
     - After critical navigation steps add `await tester.pump();` then `await tester.pumpAndSettleSafe();` to break potential microtask loops (see `doc/testing.md`).
  4. Explicitly stub BLoC `close()` and `add()` where mocks could throw.
     - Ensure `when(() => mockPlanTemplatesBloc.close()).thenAnswer((_) async {})` etc. (already present in file; confirm).
  5. Add defensive `await tester.pump();` delays in tests that assert router location immediately after state emission to give GoRouter time to complete its redirect (small pump permitted by `doc/testing.md`).
  6. Add verification logs (optional): after test run, print a short debug summary to stdout (e.g., router location) to aid verification and protocol attachment.
- Expected tests to pass:
  - All tests in `plan_templates_orchestrator_test.dart` should pass locally in repeated runs (run the single-file flutter test command at least 3 times to check flakiness).
- Commit policy:
  - Before changes: git add & commit a WIP snapshot with message: "impl_pilot_3: snapshot before stabilizing plan_templates tests"
  - After minimal, passing change: git add & commit with message: "impl_pilot_3: stabilize plan_templates_orchestrator_test.dart — fix DI/reset and safe pumps"

Step 3 — Verification run & artifact collection
- Files changed: none (running tests only).
- Actions:
  - Run: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  - Capture stdout/stderr to `plans_and_protocols/2025-10-27_02_verification_log.txt` (implementer should create this file as part of the per-attempt protocol; if failing, create `explore_test_blocker` report).
  - If tests pass, copy test output summary into `plans_and_protocols/2025-10-27_03_success_protocol.md`.
- Commit: add any protocol/log files and commit: "impl_pilot_3: add verification log and protocol"

Step 4 — If failures persist: create `explore_test_blocker` protocol
- Files changed:
  - `requirements_tasks/.../plans_and_protocols/<timestamp>_explore_test_blocker.md` (create)
- Description: Document failing assertions, stack traces, CI run output, and propose next investigation steps (e.g., deeper orchestrator logic, production code fix, or additional test harness changes).
- This ends the pilot's implementation track; orchestrator will decide whether to spawn further subtasks.

## Risk / Regression analysis
- Risk: Resetting `GetIt` globally in tests may interfere with other tests if run within the same process. Mitigation: restrict `GetIt.I.reset()` usage to the test file's `tearDown()` and ensure all registrations required by the test are re-registered in `setUp()`. The code-mode implementer must prefer `GetIt.I.reset()` over per-type unregister to avoid missed types.
- Risk: Using `pump`/delays to stabilize tests can mask real timing bugs. Mitigation: keep delays minimal and prefer explicit state sequencing with `StreamController` where possible.
- Risk: Modifying tests only may not surface orchestrator-level issues that require code changes. Mitigation: If test fixes reveal production code problems, create an `explore_test_blocker` and do not implement production changes in this pilot without orchestrator approval.

## Assumptions that must be validated (validation report)
1. The project uses BLoC + GetIt DI and tests rely on `GetIt` for test scoping. (Confirmed by reading [`test/widget/.../plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) and [`core/injection/injection_container.dart`](core/injection/injection_container.dart:1).)
2. The failing tests are due to asynchronous timing and router microtasks rather than underlying production logic bugs. (Likely — `doc/testing.md` documents the exact failure modes.)
3. The test helpers `test/helpers/safe_pump.dart` and `test/helpers/test_app_wrapper.dart` exist and are used by tests. (Confirmed.)
4. Running the single test file locally is sufficient for Phase 3 verification for this pilot. (Aligned with `goal.md`.)

Validation outcome:
- Assumptions 1, 3 and 4 are confirmed by inspection of files listed above.
- Assumption 2 is plausible but must be validated by running the modified tests; if repeated failures show production code issues, escalate with `explore_test_blocker`.

## Deliverables produced by this architect subtask
1. Plan file (this file): [`requirements_tasks/.../2025-10-27_01_plan_impl_pilot_3.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_3/plans_and_protocols/2025-10-27_01_plan_impl_pilot_3.md:1)
2. Validation report appended at the end of this file (this same file).

## Blockers / open questions (actionable)
- Confirm which git branch/commit the implementer should use. I recorded "main" as the working branch for the plan; the implementer must capture and record the exact commit hash before making changes.
- Confirm CI environment that will run the Phase 3 verification (so implementer can mirror it locally).

## Next-action to create code-mode subtask(s)
- Create a single code-mode subtask with depth level 2:
  - Mode: code
  - Scope: modify exactly the files in "Scope of Work" (the plan file and the test file).
  - Instruction (exact text to pass to code-mode):
    1. Checkout branch specified by orchestrator and capture commit hash.
    2. Make the changes described in "Step 2 — Stabilize the failing widget tests" to the test file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1).
    3. Commit before & after (see steps above).
    4. Run: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart and save stdout/stderr to `plans_and_protocols/2025-10-27_02_verification_log.txt`.
    5. If tests fail persistently, create `plans_and_protocols/<timestamp>_explore_test_blocker.md` documenting failures and stop.
- The orchestrator should then review the verification protocol and either approve (spawn further orchestrator subtasks) or escalate.

-------------------------
End of plan.

Validation report (appendix — summary)
- Files inspected: [`requirements_tasks/.../goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot_3/goal.md:1), [`doc/architecture.md`](doc/architecture.md:1), [`doc/testing.md`](doc/testing.md:1), and the failing test [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1).
- Core assumptions confirmed: architecture (BLoC + GetIt), test helper availability, and orchestrator testing policy (unit/widget tests only for pilot).
- Remaining validation to perform in code-mode: run stabilized tests to confirm assumption that failures stem from timing and test harness issues rather than production code bugs.

Timestamp: 2025-10-27T11:07:39Z (UTC)
Roo — architect