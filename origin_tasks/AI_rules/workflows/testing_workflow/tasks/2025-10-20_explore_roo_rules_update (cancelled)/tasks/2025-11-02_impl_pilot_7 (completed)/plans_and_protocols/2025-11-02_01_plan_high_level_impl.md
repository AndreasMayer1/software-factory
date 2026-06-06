# 2025-11-02_01_plan_high_level_impl.md

produced_by: Roo (architect mode)
timestamp: 2025-11-02T20:54:04Z
parent_plans_and_protocols: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols
template_filename: .roo-templates/high_level_impl_plan.md
guidelines_read:
  - doc/architecture.md
  - doc/testing.md
  - .roo/rules-orchestrator/implementation_workflow.md

Title: High-level implementation plan — Pilot 7: hierarchical testing orchestrator pattern (plan only)

Goal summary:
- Pilot the hierarchical testing orchestrator pattern for the testing workflow (Pilot 7) and produce a high-level plan document that defines scope, risks, verification level, and minimal testing strategy for the pilot. The plan must be written according to the required template and saved in the task's plans_and_protocols folder. This plan will be used by the orchestrator to create the next architect validation subtask and (if validated) further implementation subtasks.
- Provide a concise, testable description of what will be modified and why, include a recursive listing of lib/, and recommend a Verification Level per the orchestrator rules.

Goal (2–4 sentences):
This pilot validates the adjusted orchestration hierarchy for test-writing tasks using the plan_templates feature as a representative example. The deliverable is a high-level plan (no Phase 2 implementation steps) that identifies the files expected to be changed, assesses risk and regressions, prescribes a verification level, and specifies the minimal testing strategy required to evaluate the pilot's success.

Initial Scope of Work (exact list of files/components expected to be modified for the whole implementation):
- test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- requirements_tasks/.../tasks/2025-11-02_impl_pilot_7/plans_and_protocols/ (plan and subsequent protocol files created by orchestrator and subtasks)
  - Note: This high-level plan itself is being added at: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols/2025-11-02_01_plan_high_level_impl.md

Rationale for scope:
- The task goal explicitly identifies the plan_templates feature as the representative example and suggests updating the failing widget test at test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart to provide something verifiable for the testing orchestrator. This single test file constitutes the minimal, focused scope for this pilot and keeps the initial Scope of Work under the 4-file threshold required by orchestrator rules.

Risk and regressions assessment:
- Risk: Low-to-moderate. Modifying tests can mask implementation bugs if mocks or test setup are adjusted incorrectly. Tests touching routing or GoRouter state can be fragile and cause flakiness (pumpAndSettle timeouts, async redirect timing).
- Regressions to watch:
  - Test instability due to improper stubbing of BLoC streams or DI setup (GetIt/Hive).
  - Incorrect assumptions about router structure (StatefulShellRoute) causing tests to pass while runtime still fails.
  - Overly broad mocks that hide real problems.
- Mitigations:
  - Follow testing guidelines in doc/testing.md (use whenListen, mock DI clean resets, explicit router setup).
  - Keep changes minimal and focused on the failing assertions or test setup rather than modifying production code.
  - Produce `part_attempt_<n>_protocol.md` files per attempt if this becomes an `impl_test_part` (see Test-writing subtask rules).

Verification Level recommendation (per .roo/rules-orchestrator/implementation_workflow.md):
- Recommended Verification Level: 3 (Targeted Test)
  - Rationale: This pilot is exclusively about tests. Phase 3 verification should run the updated unit/widget test(s) with `flutter test <file>` as described by the orchestrator rules and the task goal. Level 3 ensures code review, static analysis and executing the specific test(s) that cover the changed test file to confirm the workflow and that tests pass or produce a documented blocker protocol.

Minimal testing strategy (what tests will be required):
- For this pilot (test-only scope):
  - Update and re-run the single failing widget test:
    - Command: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart -d windows
    - Use the project's test helper patterns (mock BLoCs, whenListen, proper router setup using StatefulShellRoute where required).
    - If test still fails, produce an explore_test_blocker protocol in plans_and_protocols documenting failure and root-cause hypotheses (include logs and commands run).
  - No new integration tests will be added or run for this pilot (explicit constraint from task goal).
  - Ensure each test attempt produces a part_attempt protocol if this becomes a code subtask as required by Test-writing subtask rules.

Phase 1 / Phase 2 / Phase 3 statement:
- Phase 1 (Analysis & Validation Loop): This file is the Phase 1 high-level plan. Phase 1 must be followed by a separate architect-mode validation subtask that reads this plan and confirms assumptions against code and guidelines.
- Phase 2 (Implementation): SKIP Phase 2 implementation because the Scope of Work contains only test files. Per the template and orchestrator rules: "There must not be a Phase 2 (implementation) if the implementation only contains test files. If only test files are contained in the scope, skip Phase 2 and Phase 3 starts directly after Phase 1."
- Phase 3 (Final Integration Verification): After validation, proceed to the Testing Orchestrator which will coordinate test execution and verification for the specified test file.

Timeline / estimate:
- Author high-level plan (this file): immediate (done).
- Architect validation subtask (Phase 1.2): 1 working day for a human reviewer or automated architect subtask to validate assumptions and confirm the plan or request adjustments.
- Test update attempt(s) (Phase 3, single test file): 0.5–1 day (including writing per-attempt protocol files and iterating on test setup) assuming no large blockers.
- Contingency: If validation fails or the test exposes broader issues (DI, router config), record as blocker and expect additional 1–3 days to investigate.
- Statement on splitting Phase 2: Phase 2 will not be used for this pilot (see Phase 2 statement above). Phase 3 may be split into multiple attempts (part_attempt_1, part_attempt_2) if needed; those attempts must follow the Test-writing subtask rules.

Files to be created by this plan:
- requirements_tasks/.../plans_and_protocols/2025-11-02_01_plan_high_level_impl.md (this file)
- If Phase 3 attempts occur, each attempt must add:
  - requirements_tasks/.../plans_and_protocols/part_attempt_<n>_protocol.md (per Test-writing subtask rules) — list these as expected artifacts in the orchestrator's flow.

Constraints and checklist (enforced):
- Use template file: .roo-templates/high_level_impl_plan.md (observed).
- Metadata fields included: produced_by, timestamp, parent_plans_and_protocols, guidelines_read (observed).
- Forbidden fields: Do not include next_steps or owner_assignments (none included).
- If initial Scope contained >4 Dart files, produce blocker using .roo-templates/template_scope_too_large.md (not required — scope contains 1 test file).

Embedded recursive listing of lib/ (generated via project listing):
- See attached recursive listing appended below. This listing is included to satisfy the orchestrator requirement to append a recursive lib/ listing to the plan.

--- lib/ recursive listing (partial, representative)
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
(End of listing)
---

Recommended verification artifacts to be produced by subtasks:
- Updated test file: test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- Protocol files in plans_and_protocols documenting each test attempt (part_attempt_<n>_protocol.md)
- If blocked: explore_test_blocker protocol per the orchestrator rules (documenting logs, commands run, and root cause analysis)

Verification level recommended: 3 (Targeted Test)

Status: This file is the Phase 1 high-level plan. Do not start implementation (Phase 2) from this subtask. Create the architect validation subtask next to validate assumptions and then proceed per orchestrator rules.
