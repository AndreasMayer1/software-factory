# 2025-11-03_01_plan_high_level_impl — High-level implementation plan for impl_pilot_9

Created: 2025-11-03T07:31:42Z

Goal / Objective

- Objective: Produce a concise high-level implementation plan for the pilot described in [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_9/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_9/goal.md:1). The plan describes what and why to change to validate the hierarchical testing orchestrator; it does not include Phase 2 implementation steps.

Assumptions

- The active task folder is dated 2025-11-03 and no daily-rollover is required.
- The pilot scope is limited to unit and widget tests (no integration tests).
- The initial failing artifact to update is the test file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1).
- The repository state is buildable and tests can be run in a subsequent code-mode subtask.

Identified affected modules / layers (one paragraph)

- Candidate areas: the therapist plan templates presentation layer (widgets and UI orchestrator) and its presentation BLoC layer are most likely involved. The failing widget test references the orchestrator widget under [`lib/features/therapist/plan_templates/presentation/widgets/`](lib/features/therapist/plan_templates/presentation/widgets/:1); related presentation BLoC and organisms that provide data to the widget (plan list, detail content, mock data) are possible secondary impacts.

Initial candidate Dart files (plain list)

- [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart:1)
- [`lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart`](lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart:1)
- [`lib/features/therapist/plan_templates/presentation/widgets/plan_details_form.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_details_form.dart:1)

Definitive Scope of Work (final list of files to be created or modified)

- Because the pilot goal and template allow a tests-only pilot, and the reported failing artifact is a single test, this plan sets the definitive scope to test-only: update the single test file below. Phase 2 (implementation) is therefore skipped and Phase 3 verification starts after the test update.

- [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)

Verification level recommendation (0–3) and justification

- Recommendation: 2 — targeted unit and widget test execution.
- Justification: The change is a tests-only update for a widget test; verification should run the affected widget test file with `flutter test <file>` to confirm behavior. Level 3 (integration) is unnecessary and explicitly disallowed by the pilot.

Risks & unknowns

- The failing test may reveal a production code issue requiring lib modifications; that would expand scope beyond the single test file.
- Test flakiness or environment differences (local vs CI) may produce intermittent failures.
- Missing mocks or test helpers may require adding or modifying support files in `test/helpers/`, which increases scope.

Required Phase 2 subtasks (brief list with responsible modes)

- None — Phase 2 implementation is skipped because this pilot only contains test file changes. Phase 3 starts directly.

Required Phase 3 subtasks (brief list with responsible modes)

- Update failing test file — mode: code
  - Target file: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- Run targeted verification — mode: code
  - Command: `flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`
- If test now fails due to production code: create a follow-up code-mode subtask to modify production files (architect review before changes) — mode: architect then code

Estimated effort (rough)

- Phase 1 (this plan): 30–60 minutes (analysis + plan file creation).
- Phase 3 (tests-only): 1–3 hours (update test, run tests, iterate). If production changes required, additional 3–8 hours depending on complexity.

Acceptance criteria

- The file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) is updated and the targeted widget tests run and either pass or a formal `explore_test_blocker` protocol file is created in this task folder.
- The orchestrator produces the expected plans_and_protocols entries defined by the workflow (per goal).

Git commands and exact commit messages for the subsequent code-mode subtask

- Start baseline commit (capture current workspace state before edits)
  1) git add .
  2) git commit -m "2025-11-03 impl_pilot_9: start baseline before test updates"

- Work steps (performed in code-mode subtask)
  * Edit [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)

- End commit after successful local verification (or to capture blocker)
  1) git add test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  2) git commit -m "2025-11-03 impl_pilot_9: update failing plan_templates_orchestrator_test"

- If production files also changed, include them explicitly in the git add line above and reflect them in the commit message, for example:
  git add <list of modified files>
  git commit -m "2025-11-03 impl_pilot_9: fix production widget to satisfy test"

Next steps (3–5 lines) for the orchestrator to create Phase 2/3 subtasks

- Create a code-mode subtask to update the failing test: include the full file path to the test and reference this plan file.
- In the code-mode subtask, perform the start baseline commit before edits and the end commit after verification; run `flutter test <file>` as the verification step.
- If the test uncovers production code failures, create an architect-mode subtask to analyze required production changes and produce a separate high-level plan for those changes.

Appendices

A. Recursive lib/ listing (generated with list_files)

- [`lib/config/routes/app_route_info.dart`](lib/config/routes/app_route_info.dart:1)
- [`lib/config/routes/app_router.dart`](lib/config/routes/app_router.dart:1)
- [`lib/config/routes/app_routes.dart`](lib/config/routes/app_routes.dart:1)
- [`lib/config/routes/route_utils.dart`](lib/config/routes/route_utils.dart:1)
- [`lib/config/theme/readme.me`](lib/config/theme/readme.me:1)
- [`lib/config/theme/theme.dart`](lib/config/theme/theme.dart:1)
- [`lib/config/theme/tokens_extra.g.dart`](lib/config/theme/tokens_extra.g.dart:1)
- [`lib/config/theme/tokens.g.dart`](lib/config/theme/tokens.g.dart:1)
- [`lib/config/theme/figma/tokens.json`](lib/config/theme/figma/tokens.json:1)
- [`lib/core/data/adapters/app_role_adapter.dart`](lib/core/data/adapters/app_role_adapter.dart:1)
- [`lib/core/data/repositories/local_role_repository.dart`](lib/core/data/repositories/local_role_repository.dart:1)
- [`lib/core/data/repositories/questionnaire_plan/local_choice_repository.dart`](lib/core/data/repositories/questionnaire_plan/local_choice_repository.dart:1)
- [`lib/core/data/storage/storage_initializer.dart`](lib/core/data/storage/storage_initializer.dart:1)
- [`lib/core/design_system/atoms/background_svg.dart`](lib/core/design_system/atoms/background_svg.dart:1)
- [`lib/core/design_system/atoms/client_status.dart`](lib/core/design_system/atoms/client_status.dart:1)
- [`lib/core/design_system/atoms/grid_example.dart`](lib/core/design_system/atoms/grid_example.dart:1)
- [`lib/core/design_system/atoms/grid_layout.dart`](lib/core/design_system/atoms/grid_layout.dart:1)
- [`lib/core/design_system/atoms/typography.dart`](lib/core/design_system/atoms/typography.dart:1)
- [`lib/core/design_system/atoms/inputs/likert_scale.dart`](lib/core/design_system/atoms/inputs/likert_scale.dart:1)
- [`lib/core/design_system/config/screen_size.dart`](lib/core/design_system/config/screen_size.dart:1)
- [`lib/core/design_system/config/layout/layout_config.dart`](lib/core/design_system/config/layout/layout_config.dart:1)
- [`lib/core/design_system/config/layout/navigation.dart`](lib/core/design_system/config/layout/navigation.dart:1)
- [`lib/core/design_system/config/layout/README.md`](lib/core/design_system/config/layout/README.md:1)
- [`lib/core/design_system/molecules/action_item_button.dart`](lib/core/design_system/molecules/action_item_button.dart:1)
- [`lib/core/design_system/molecules/error_display.dart`](lib/core/design_system/molecules/error_display.dart:1)
- [`lib/core/design_system/molecules/form_row.dart`](lib/core/design_system/molecules/form_row.dart:1)
- [`lib/core/design_system/molecules/input_field.dart`](lib/core/design_system/molecules/input_field.dart:1)
- [`lib/core/design_system/molecules/list_item.dart`](lib/core/design_system/molecules/list_item.dart:1)
- [`lib/core/design_system/molecules/radio_card.dart`](lib/core/design_system/molecules/radio_card.dart:1)
- [`lib/core/design_system/organisms/grouped_action_list.dart`](lib/core/design_system/organisms/grouped_action_list.dart:1)
- [`lib/core/design_system/organisms/modal_dialog.dart`](lib/core/design_system/organisms/modal_dialog.dart:1)
- [`lib/core/design_system/organisms/layout/base/app_bar_config.dart`](lib/core/design_system/organisms/layout/base/app_bar_config.dart:1)
- [`lib/core/design_system/organisms/layout/base/custom_navigation_bar.dart`](lib/core/design_system/organisms/layout/base/custom_navigation_bar.dart:1)
- [`lib/core/design_system/organisms/layout/base/inherited_back_navigator.dart`](lib/core/design_system/organisms/layout/base/inherited_back_navigator.dart:1)
- [`lib/core/design_system/organisms/layout/base/inherited_stack_navigator.dart`](lib/core/design_system/organisms/layout/base/inherited_stack_navigator.dart:1)
- [`lib/core/design_system/organisms/layout/base/stack_navigator_layout.dart`](lib/core/design_system/organisms/layout/base/stack_navigator_layout.dart:1)
- [`lib/core/design_system/organisms/layout/base/stack_navigator.dart`](lib/core/design_system/organisms/layout/base/stack_navigator.dart:1)
- [`lib/core/design_system/organisms/layout/base/view_config.dart`](lib/core/design_system/organisms/layout/base/view_config.dart:1)
- [`lib/core/design_system/organisms/layout/master_detail/detail_layout.dart`](lib/core/design_system/organisms/layout/master_detail/detail_layout.dart:1)
- [`lib/core/design_system/organisms/layout/master_detail/master_detail_layout.dart`](lib/core/design_system/organisms/layout/master_detail/master_detail_layout.dart:1)
- [`lib/core/design_system/organisms/layout/master_detail/master_layout.dart`](lib/core/design_system/organisms/layout/master_detail/master_layout.dart:1)
- [`lib/core/design_system/organisms/layout/responsive/responsive_layout_builder.dart`](lib/core/design_system/organisms/layout/responsive/responsive_layout_builder.dart:1)
- [`lib/core/domain/entities/action_group.dart`](lib/core/domain/entities/action_group.dart:1)
- [`lib/core/domain/entities/action_item.dart`](lib/core/domain/entities/action_item.dart:1)
- [`lib/core/domain/entities/action_type.dart`](lib/core/domain/entities/action_type.dart:1)
- [`lib/core/domain/entities/app_role.dart`](lib/core/domain/entities/app_role.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities.dart`](lib/core/domain/entities/questionnaire_plan_entities.dart:1)
- [`lib/core/domain/entities/questionnaire_plan/questionnaire.dart`](lib/core/domain/entities/questionnaire_plan/questionnaire.dart:1)
- [`lib/core/domain/entities/questionnaire_plan/version_constants.dart`](lib/core/domain/entities/questionnaire_plan/version_constants.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/choice_options.dart`](lib/core/domain/entities/questionnaire_plan_entities/choice_options.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/choice.dart`](lib/core/domain/entities/questionnaire_plan_entities/choice.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/exceptions.dart`](lib/core/domain/entities/questionnaire_plan_entities/exceptions.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/likert_options.dart`](lib/core/domain/entities/questionnaire_plan_entities/likert_options.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/question_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/question_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/question.dart`](lib/core/domain/entities/questionnaire_plan_entities/question.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart`](lib/core/domain/entities/questionnaire_plan_entities/questionnaire_plan.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart`](lib/core/domain/entities/questionnaire_plan_entities/questionnaire.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/time_input_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/time_input_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/time_interval_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/time_interval_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/time_interval.dart`](lib/core/domain/entities/questionnaire_plan_entities/time_interval.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/time_label_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/time_label_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/time_options.dart`](lib/core/domain/entities/questionnaire_plan_entities/time_options.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/version_constants.dart`](lib/core/domain/entities/questionnaire_plan_entities/version_constants.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/choice_options.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/choice_options.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/choice.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/choice.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/exceptions.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/exceptions.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/likert_options.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/likert_options.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/question_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/question_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/question.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/question.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire_plan.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire_plan.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/questionnaire.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/time_input_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/time_input_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/time_interval_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/time_interval_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/time_interval.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/time_interval.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/time_label_type.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/time_label_type.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/time_options.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/time_options.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/v1.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/v1.dart:1)
- [`lib/core/domain/entities/questionnaire_plan_entities/v1/version_constants.dart`](lib/core/domain/entities/questionnaire_plan_entities/v1/version_constants.dart:1)
- [`lib/core/domain/events/questionnaire_plan/event_publisher.dart`](lib/core/domain/events/questionnaire_plan/event_publisher.dart:1)
- [`lib/core/domain/events/questionnaire_plan/events.dart`](lib/core/domain/events/questionnaire_plan/events.dart:1)
- [`lib/core/domain/failures/failures.dart`](lib/core/domain/failures/failures.dart:1)
- [`lib/core/domain/failures/questionnaire_plan/choice_failures.dart`](lib/core/domain/failures/questionnaire_plan/choice_failures.dart:1)
- [`lib/core/domain/failures/questionnaire_plan/question_failures.dart`](lib/core/domain/failures/questionnaire_plan/question_failures.dart:1)
- [`lib/core/domain/failures/questionnaire_plan/questionnaire_failures.dart`](lib/core/domain/failures/questionnaire_plan/questionnaire_failures.dart:1)
- [`lib/core/domain/failures/questionnaire_plan/questionnaire_plan_failures.dart`](lib/core/domain/failures/questionnaire_plan/questionnaire_plan_failures.dart:1)
- [`lib/core/domain/repositories/role_repository.dart`](lib/core/domain/repositories/role_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/choice_repository.dart`](lib/core/domain/repositories/questionnaire_plan/choice_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/mock_choice_repository.dart`](lib/core/domain/repositories/questionnaire_plan/mock_choice_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/mock_question_repository.dart`](lib/core/domain/repositories/questionnaire_plan/mock_question_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/mock_questionnaire_plan_repository.dart`](lib/core/domain/repositories/questionnaire_plan/mock_questionnaire_plan_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/mock_questionnaire_repository.dart`](lib/core/domain/repositories/questionnaire_plan/mock_questionnaire_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/question_repository.dart`](lib/core/domain/repositories/questionnaire_plan/question_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/questionnaire_plan_repository.dart`](lib/core/domain/repositories/questionnaire_plan/questionnaire_plan_repository.dart:1)
- [`lib/core/domain/repositories/questionnaire_plan/questionnaire_repository.dart`](lib/core/domain/repositories/questionnaire_plan/questionnaire_repository.dart:1)
- [`lib/core/domain/services/questionnaire_plan/choice_service_impl.dart`](lib/core/domain/services/questionnaire_plan/choice_service_impl.dart:1)
- [`lib/core/domain/services/questionnaire_plan/choice_service.dart`](lib/core/domain/services/questionnaire_plan/choice_service.dart:1)
- [`lib/core/domain/services/questionnaire_plan/question_service_impl.dart`](lib/core/domain/services/questionnaire_plan/question_service_impl.dart:1)
- [`lib/core/domain/services/questionnaire_plan/question_service.dart`](lib/core/domain/services/questionnaire_plan/question_service.dart:1)
- [`lib/core/domain/services/questionnaire_plan/questionnaire_plan_service_impl.dart`](lib/core/domain/services/questionnaire_plan/questionnaire_plan_service_impl.dart:1)
- [`lib/core/domain/services/questionnaire_plan/questionnaire_plan_service.dart`](lib/core/domain/services/questionnaire_plan/questionnaire_plan_service.dart:1)
- [`lib/core/domain/services/questionnaire_plan/serialization_utils.dart`](lib/core/domain/services/questionnaire_plan/serialization_utils.dart:1)
- [`lib/core/domain/services/screen_size/i_screen_size_service.dart`](lib/core/domain/services/screen_size/i_screen_size_service.dart:1)
- [`lib/core/domain/services/screen_size/screen_size_service_impl.dart`](lib/core/domain/services/screen_size/screen_size_service_impl.dart:1)
- [`lib/core/error/failure.dart`](lib/core/error/failure.dart:1)
- [`lib/core/injection/injection_container.config.dart`](lib/core/injection/injection_container.config.dart:1)
- [`lib/core/injection/injection_container.dart`](lib/core/injection/injection_container.dart:1)
- [`lib/core/injection/presentation_di.dart`](lib/core/injection/presentation_di.dart:1)
- [`lib/core/widgets/client/client_navigation_ui.dart`](lib/core/widgets/client/client_navigation_ui.dart:1)
- [`lib/core/widgets/layout/default_detail_placeholder.dart`](lib/core/widgets/layout/default_detail_placeholder.dart:1)
- [`lib/core/widgets/layout/scaffold_builder.dart`](lib/core/widgets/layout/scaffold_builder.dart:1)
- [`lib/core/widgets/therapist/therapist_navigation_ui.dart`](lib/core/widgets/therapist/therapist_navigation_ui.dart:1)
- [`lib/features/client/data_input/injection_container.dart`](lib/features/client/data_input/injection_container.dart:1)
- [`lib/features/client/data_input/presentation/bloc/data_input_bloc.dart`](lib/features/client/data_input/presentation/bloc/data_input_bloc.dart:1)
- [`lib/features/client/data_input/presentation/bloc/data_input_event.dart`](lib/features/client/data_input/presentation/bloc/data_input_event.dart:1)
- [`lib/features/client/data_input/presentation/bloc/data_input_state.dart`](lib/features/client/data_input/presentation/bloc/data_input_state.dart:1)
- [`lib/features/client/data_input/presentation/organisms/data_input_detail_view.dart`](lib/features/client/data_input/presentation/organisms/data_input_detail_view.dart:1)
- [`lib/features/client/data_input/presentation/screens/client_data_input_root_screen.dart`](lib/features/client/data_input/presentation/screens/client_data_input_root_screen.dart:1)
- [`lib/features/client/data_input/presentation/widgets/empty_state.dart`](lib/features/client/data_input/presentation/widgets/empty_state.dart:1)
- [`lib/features/client/data_input/presentation/widgets/likert_input.dart`](lib/features/client/data_input/presentation/widgets/likert_input.dart:1)
- [`lib/features/client/data_input/presentation/widgets/question_card.dart`](lib/features/client/data_input/presentation/widgets/question_card.dart:1)
- [`lib/features/client/data_input/presentation/widgets/question_header.dart`](lib/features/client/data_input/presentation/widgets/question_header.dart:1)
- [`lib/features/home/presentation/screens/home_screen.dart`](lib/features/home/presentation/screens/home_screen.dart:1)
- [`lib/features/more/presentation/layout/more_layout_config.dart`](lib/features/more/presentation/layout/more_layout_config.dart:1)
- [`lib/features/more/presentation/screens/about_screen.dart`](lib/features/more/presentation/screens/about_screen.dart:1)
- [`lib/features/more/presentation/screens/appearance_settings_screen.dart`](lib/features/more/presentation/screens/appearance_settings_screen.dart:1)
- [`lib/features/more/presentation/screens/more_root_screen.dart`](lib/features/more/presentation/screens/more_root_screen.dart:1)
- [`lib/features/more/presentation/screens/notification_preferences_screen.dart`](lib/features/more/presentation/screens/notification_preferences_screen.dart:1)
- [`lib/features/more/presentation/screens/privacy_policy_screen.dart`](lib/features/more/presentation/screens/privacy_policy_screen.dart:1)
- [`lib/features/more/presentation/screens/terms_of_service_screen.dart`](lib/features/more/presentation/screens/terms_of_service_screen.dart:1)
- [`lib/features/more/presentation/widgets/more_master_view.dart`](lib/features/more/presentation/widgets/more_master_view.dart:1)
- [`lib/features/role_selection/domain/usecases/check_first_launch_use_case.dart`](lib/features/role_selection/domain/usecases/check_first_launch_use_case.dart:1)
- [`lib/features/role_selection/domain/usecases/get_stored_role_use_case.dart`](lib/features/role_selection/domain/usecases/get_stored_role_use_case.dart:1)
- [`lib/features/role_selection/domain/usecases/persist_role_use_case.dart`](lib/features/role_selection/domain/usecases/persist_role_use_case.dart:1)
- [`lib/features/role_selection/presentation/bloc/role_selection_bloc.dart`](lib/features/role_selection/presentation/bloc/role_selection_bloc.dart:1)
- [`lib/features/role_selection/presentation/bloc/role_selection_event.dart`](lib/features/role_selection/presentation/bloc/role_selection_event.dart:1)
- [`lib/features/role_selection/presentation/bloc/role_selection_state.dart`](lib/features/role_selection/presentation/bloc/role_selection_state.dart:1)
- [`lib/features/role_selection/presentation/molecules/role_selection_form.dart`](lib/features/role_selection/presentation/molecules/role_selection_form.dart:1)
- [`lib/features/role_selection/presentation/organisms/role_selection_dialog.dart`](lib/features/role_selection/presentation/organisms/role_selection_dialog.dart:1)
- [`lib/features/role_selection/presentation/screens/onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1)
- [`lib/features/therapist/therapist_routes.dart`](lib/features/therapist/therapist_routes.dart:1)
- [`lib/features/therapist/clients/clients_routes.dart`](lib/features/therapist/clients/clients_routes.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/client_plan_detail_bloc.dart`](lib/features/therapist/clients/presentation/bloc/client_plan_detail_bloc.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/client_plan_detail_event.dart`](lib/features/therapist/clients/presentation/bloc/client_plan_detail_event.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/client_plan_detail_state.dart`](lib/features/therapist/clients/presentation/bloc/client_plan_detail_state.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/client_plans_bloc.dart`](lib/features/therapist/clients/presentation/bloc/client_plans_bloc.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/client_plans_event.dart`](lib/features/therapist/clients/presentation/bloc/client_plans_event.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/client_plans_state.dart`](lib/features/therapist/clients/presentation/bloc/client_plans_state.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/therapist_clients_bloc.dart`](lib/features/therapist/clients/presentation/bloc/therapist_clients_bloc.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/therapist_clients_event.dart`](lib/features/therapist/clients/presentation/bloc/therapist_clients_event.dart:1)
- [`lib/features/therapist/clients/presentation/bloc/therapist_clients_state.dart`](lib/features/therapist/clients/presentation/bloc/therapist_clients_state.dart:1)
- [`lib/features/therapist/clients/presentation/molecules/client_action_buttons.dart`](lib/features/therapist/clients/presentation/molecules/client_action_buttons.dart:1)
- [`lib/features/therapist/clients/presentation/molecules/client_title_description.dart`](lib/features/therapist/clients/presentation/molecules/client_title_description.dart:1)
- [`lib/features/therapist/clients/presentation/organisms/client_list.dart`](lib/features/therapist/clients/presentation/organisms/client_list.dart:1)
- [`lib/features/therapist/clients/presentation/organisms/client_plan_detail_view.dart`](lib/features/therapist/clients/presentation/organisms/client_plan_detail_view.dart:1)
- [`lib/features/therapist/clients/presentation/organisms/client_plans_view.dart`](lib/features/therapist/clients/presentation/organisms/client_plans_view.dart:1)
- [`lib/features/therapist/clients/presentation/screens/therapist_client_detail_screen.dart`](lib/features/therapist/clients/presentation/screens/therapist_client_detail_screen.dart:1)
- [`lib/features/therapist/clients/presentation/widgets/therapist_clients_orchestrator.dart`](lib/features/therapist/clients/presentation/widgets/therapist_clients_orchestrator.dart:1)
- [`lib/features/therapist/inbox/presentation/screens/inbox_screen.dart`](lib/features/therapist/inbox/presentation/screens/inbox_screen.dart:1)
- [`lib/features/therapist/inbox/presentation/screens/therapist_inbox_root_screen.dart`](lib/features/therapist/inbox/presentation/screens/therapist_inbox_root_screen.dart:1)
- [`lib/features/therapist/plan_templates/plan_templates_routes.dart`](lib/features/therapist/plan_templates/plan_templates_routes.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_event.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_event.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_event.freezed.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_event.freezed.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_state.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_state.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_state.freezed.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_state.freezed.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_templates_event.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_templates_event.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_templates_state.dart:1)
- [`lib/features/therapist/plan_templates/presentation/mock/mock_plans.dart`](lib/features/therapist/plan_templates/presentation/mock/mock_plans.dart:1)
- [`lib/features/therapist/plan_templates/presentation/molecules/plan_action_buttons.dart`](lib/features/therapist/plan_templates/presentation/molecules/plan_action_buttons.dart:1)
- [`lib/features/therapist/plan_templates/presentation/molecules/plan_title_description.dart`](lib/features/therapist/plan_templates/presentation/molecules/plan_title_description.dart:1)
- [`lib/features/therapist/plan_templates/presentation/organisms/plan_detail_view.dart`](lib/features/therapist/plan_templates/presentation/organisms/plan_detail_view.dart:1)
- [`lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart`](lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart:1)
- [`lib/features/therapist/plan_templates/presentation/organisms/plan_template_detail_content.dart`](lib/features/therapist/plan_templates/presentation/organisms/plan_template_detail_content.dart:1)
- [`lib/features/therapist/plan_templates/presentation/widgets/plan_details_form.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_details_form.dart:1)
- [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:1)
- [`lib/features/therapist/plan_templates/presentation/widgets/questionnaire_details_view.dart`](lib/features/therapist/plan_templates/presentation/widgets/questionnaire_details_view.dart:1)
- [`lib/features/therapist/plan_templates/presentation/widgets/questionnaire_summary_card.dart`](lib/features/therapist/plan_templates/presentation/widgets/questionnaire_summary_card.dart:1)
- [`lib/features/therapist/plan_templates/presentation/widgets/responsive_questionnaire_list.dart`](lib/features/therapist/plan_templates/presentation/widgets/responsive_questionnaire_list.dart:1)
- [`lib/generated/l10n/app_localizations_de.dart`](lib/generated/l10n/app_localizations_de.dart:1)
- [`lib/generated/l10n/app_localizations_en.dart`](lib/generated/l10n/app_localizations_en.dart:1)
- [`lib/generated/l10n/app_localizations.dart`](lib/generated/l10n/app_localizations.dart:1)
- [`lib/l10n/`](lib/l10n/:1)

B. plans_and_protocols listing for this task folder

- No files found in [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_9/plans_and_protocols/`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_9/plans_and_protocols/:1)

End of plan.