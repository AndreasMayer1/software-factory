Depth level: 1

# 2025-10-20_01_plan_initial.md

Goal restatement:

- Pilot the hierarchical testing orchestrator pattern for the testing workflow as described in [`goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md:1). Primary objectives: validate orchestration hierarchy (Outer Orchestrator -> Testing Orchestrator -> Test File Orchestrator -> Architect plans -> Code part subtasks), ensure leaf-level subtasks follow the code -> architect -> code cycle, and confirm Phase 3 verification uses targeted `flutter test <file>` for unit/widget tests; do not create or run integration tests unless explicitly requested.

Daily task rollover:

- Task folder date (2025-10-20) matches today (2025-10-20). No rollover performed; did not invoke [`scripts/automate_task_rollover.ps1`](scripts/automate_task_rollover.ps1:1).

Prior work / context assimilation:

- No existing plan/protocol files present in this task's `plans_and_protocols` directory (verified empty).
- Reviewed: [`doc/architecture.md`](doc/architecture.md:1), [`doc/testing.md`](doc/testing.md:1), and the unified orchestrator workflow: [`.roo implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1).

Core assumptions (explicit):

1. The pilot scope will be tests-only and limited to a single representative test (onboarding screen).
2. Target file exists at [`lib/features/role_selection/presentation/screens/onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1).
3. Phase 3 verification will run `flutter test <file>` for unit/widget tests (per implementation workflow).
4. Integration tests are excluded unless explicitly requested by the user.
5. Required test helpers / DI setup can be provided in tests without changing production code; if not present, architect subtask will document required helpers.

Analysis results:

- The target screen file is present and suitable for a widget test: [`lib/features/role_selection/presentation/screens/onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1).
- The project's testing guidelines (see [`doc/testing.md`](doc/testing.md:1)) prescribe patterns and helpers (GoRouter-aware test helpers, DI reset, `whenListen`) that should be followed when writing the test.
- The implementation workflow (see [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)) indicates tests-only scope triggers direct Phase 3 verification and simplifies the plan.

Recursive lib/ listing (verbatim):

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
core/domain/entities/action_group.dart
core/domain/entities/action_item.dart
core/domain/entities/action_type.dart
core/domain/entities/app_role.dart
core/domain/entities/questionnaire_plan_entities.dart
core/domain/entities/questionnaire_plan/questionnaire.dart
core/domain/entities/questionnaire_plan/version_constants.dart
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

(File list truncated. Use list_files on specific subdirectories if you need to explore further.)

Scope of Work (explicit — files to be created/modified):

- `test/features/role_selection/presentation/screens/onboarding_screen_test.dart`

Note: Scope contains 1 file — meets the implementation workflow slicing rule (<= 4 files). If the user requests a broader pilot (e.g., plan_templates end-to-end), split into separate `impl_` tasks per feature or per test file.

Implementation steps (high-level — Phase 1 → Phase 3 path for tests-only scope):

1. Outer Orchestrator: create exactly one Testing Orchestrator task for the chosen feature (pilot).
2. Testing Orchestrator: create a Test File Orchestrator task for the target file and instruct it to request an `arch_test_plan` from an Architect subtask.
3. Architect subtask (Test File Orchestrator's architect): produce `arch_test_plan_<timestamp>_onboarding_screen.md` describing test parts and mocks per arch_test_plan requirements (see [`doc/testing.md`](doc/testing.md:1) and `.roo` rules).
4. Code subtask(s): create the test file at `test/features/role_selection/presentation/screens/onboarding_screen_test.dart` following guidelines in [`doc/testing.md`](doc/testing.md:1) (widget test, mock BLoCs, DI setup, GoRouter-aware helper).
5. Testing Orchestrator Phase 3: run targeted verification `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart` and collect verification logs.

Recommended verification level and actions:

- Verification Level: 3 (Targeted Test). Actions:
  - Run `flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart`
  - If failures occur, create `explore_test_blocker` protocols per the implementation workflow and delegate debugging to orchestrator testing process.

Risks & mitigations:

- Missing test helpers / DI setup (Risk): Mitigation — Architect subtask must declare required helpers in its `arch_test_plan` and either implement them in test helper files or add a follow-up small task to implement them.
- GoRouter test flakiness (Risk): Mitigation — follow `pumpAndSettleSafe` / `SafePump` patterns in [`doc/testing.md`](doc/testing.md:1) and use the recommended router-aware test helper.

Open questions for the orchestrator / user:

- Confirm pilot target: [`onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1) (current plan) or switch to `plan_templates` as the representative feature?

End.