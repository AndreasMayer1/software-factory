# 2025-11-02_02_plan_high_level_impl.md

produced_by: Roo (architect mode)
timestamp: 2025-11-02T21:05:10Z
parent_plans_and_protocols: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols
template_filename: .roo-templates/high_level_impl_plan.md
target_plans_and_protocols_path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols
required_whitelist_fields:
  - produced_by
  - timestamp
  - guidelines_read
forbidden_blacklist_fields:
  - next_steps
  - owner_assignments
guidelines_read:
  - doc/architecture.md
  - doc/testing.md
  - .roo/rules-orchestrator/implementation_workflow.md

Title: High-level implementation plan — Pilot 7: hierarchical testing orchestrator pattern (amended)

Goal summary:
- Pilot the hierarchical testing orchestrator pattern for the testing workflow (Pilot 7) and produce an amended high-level plan that corrects the failed assumption identified by the validation protocol.
- Ensure the plan explicitly lists the missing test-file as a scoped artifact and prescribes the required test-harness checklist items for reliable widget testing.

Goal (2–4 sentences):
This amended plan updates the Phase 1 deliverable to correct the missing-file assumption reported in the validation protocol and prescribes a minimal, enforceable test-harness checklist so that Phase 3 targeted test execution can proceed deterministically.

Corrected Scope of Work (exact list of files/components expected to be created or modified):
- [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) (create or update)
- This amended plan file: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols/2025-11-02_02_plan_high_level_impl.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols/2025-11-02_02_plan_high_level_impl.md:1)
- Plans and protocol artifacts in the plans_and_protocols folder: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols:1) (part_attempt_<n>_protocol.md, explore_test_blocker.md as required)

Rationale for corrected scope:
- The validation protocol [`2025-11-02_02_protocol_validation.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols/2025-11-02_02_protocol_validation.md:1) found the plan's target test file missing. To resolve the validation failure the orchestrator must treat the test file as an explicit artifact to create or update.

Risk and regressions assessment:
- Risk: Low-to-moderate. Test creation can hide implementation issues if mocks or setup are incorrect.
- Regressions to watch: routing/navigatorKey mismatches, DI state leakage (GetIt), improper BLoC stubbing, pumpAndSettle hangups.
- Mitigations: enforce the test-harness checklist below and reuse shared test helpers.

Test-harness checklist (required — derived from validation protocol and doc/testing.md):
- Router replication / navigatorKey setup
  - Replicate the nested `StatefulShellRoute`/branch structure and use the same `navigatorKey` for the branch under test when constructing the `GoRouter` in tests.
- DI reset and localization setup in setUp/tearDown
  - Call `GetIt.I.reset(dispose: true)` in `setUp` and re-register test doubles; ensure localization delegates and supportedLocales are present.
- BLoC / stream stubbing using `whenListen`
  - Use `whenListen(mockBloc, Stream.fromIterable([...]), initialState: initial)` for each mock BLoC the widget depends on to ensure `.stream` and `.state` are defined.
- pumpAndSettleSafe / avoiding GoRouter infinite pumps
  - Use `pumpAndSettleSafe()` from [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1) or an explicit controlled `pump()` sequence instead of `pumpAndSettle()` in GoRouter tests.
- Test helpers to reuse
  - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
  - [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1)
  - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
- Additional notes
  - Keep mocks narrow; do not over-mock production code. Document each attempt with a part_attempt_<n>_protocol.md entry in plans_and_protocols.

Verification Level recommendation:
- Recommended Verification Level: 3 (Targeted Test)
  - Rationale: This pilot targets test files only; Level 3 matches the requirement to run targeted `flutter test <file>` plus code review/static analysis.

Phase 1 / Phase 2 / Phase 3 statement and Phase 2 splitting:
- Phase 1: This is the amended Phase 1 high-level plan correcting the failed assumption.
- Phase 2: Skipped — per the template, when the scope only includes `test/` files, Phase 2 is skipped. No split of Phase 2 is required.
- Phase 3: Testing Orchestrator will execute Phase 3 verification for the listed test file: `flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart -d windows`.

Timeline / estimate:
- Author amended plan: immediate.
- Architect re-validation subtask: 1 working day.
- Test creation/update attempts (Phase 3): 0.5–1 day for the single test file.

Files to be created by this plan:
- This plan file: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols/2025-11-02_02_plan_high_level_impl.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-02_impl_pilot_7/plans_and_protocols/2025-11-02_02_plan_high_level_impl.md:1)
- Test file to create/update: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- Per-attempt protocols saved in the same plans_and_protocols folder.

Verification artifacts to be produced:
- Updated test file (see above).
- Re-validation protocol confirming file presence and harness checklist compliance.
- If blocked: explore_test_blocker protocol documenting logs and root-cause analysis.

Constraints and checklist (enforced):
- Use template: `.roo-templates/high_level_impl_plan.md`.
- Required metadata included: produced_by, timestamp, parent_plans_and_protocols, guidelines_read.
- Forbidden fields: do not include `next_steps` or `owner_assignments`.
- If Scope-of-Work >4 Dart files, create blocker using `.roo-templates/template_scope_too_large.md` (not applicable).

Embedded recursive listing of lib/ (representative):

config/
config/routes/
config/routes/app_route_info.dart
config/routes/app_router.dart
config/routes/app_routes.dart
config/routes/route_utils.dart
config/theme/
config/theme/theme.dart
core/
core/data/
core/data/adapters/
core/data/adapters/app_role_adapter.dart
core/data/repositories/
core/data/repositories/local_role_repository.dart
core/design_system/
core/design_system/atoms/
core/design_system/atoms/background_svg.dart
core/design_system/molecules/
core/domain/
core/injection/
core/widgets/
features/
features/client/
features/client/data_input/presentation/bloc/data_input_bloc.dart
features/home/presentation/screens/home_screen.dart
features/more/presentation/screens/more_root_screen.dart
features/role_selection/presentation/bloc/role_selection_bloc.dart
features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart
features/therapist/plan_templates/presentation/organisms/plan_list.dart
features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart
generated/
generated/l10n/app_localizations.dart
l10n/
(End of listing)

Status: Phase 1 amended high-level plan. Do not start Phase 2 from this subtask. Submit this plan for re-validation (architect-mode) and then proceed per orchestrator rules.