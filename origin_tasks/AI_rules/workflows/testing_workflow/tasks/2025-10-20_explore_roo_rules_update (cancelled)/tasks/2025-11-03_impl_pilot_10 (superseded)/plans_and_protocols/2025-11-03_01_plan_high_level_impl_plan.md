# 2025-11-03_01_plan_high_level_impl_plan.md

timestamp: 2025-11-03T08:08:03Z
author: Roo (architect-mode analysis)

Summary
- Purpose: Produce a high-level implementation plan (Phase 1) for the pilot described in the goal: validate the hierarchical testing orchestrator pattern for the testing workflow, using the plan_templates feature as a representative example.
- This plan contains what and why only (no implementation steps), follows the repository plan template `.roo-templates/high_level_impl_plan.md` and the task constraints. Phase 2 (implementation) is not included here.

1) Files read for context (key sources)
- Goal file: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/goal.md:1)
- Architecture guidelines: [`doc/architecture.md`](doc/architecture.md:1)
- Testing guidelines: [`doc/testing.md`](doc/testing.md:1)
- Template: [`.roo-templates/high_level_impl_plan.md`](.roo-templates/high_level_impl_plan.md:1)

2) Project lib/ recursive listing (top-level snapshot)
The following listing was produced by a recursive scan of `lib/`. It is included to give implementors a view of the current code structure to be referenced by subtasks.

- [`lib/config/routes/app_route_info.dart`](lib/config/routes/app_route_info.dart:1)
- [`lib/config/routes/app_router.dart`](lib/config/routes/app_router.dart:1)
- [`lib/config/routes/app_routes.dart`](lib/config/routes/app_routes.dart:1)
- [`lib/config/routes/route_utils.dart`](lib/config/routes/route_utils.dart:1)
- [`lib/config/theme/readme.me`](lib/config/theme/readme.me:1)
- [`lib/config/theme/theme.dart`](lib/config/theme/theme.dart:1)
- [`lib/config/theme/tokens_extra.g.dart`](lib/config/theme/tokens_extra.g.dart:1)
- [`lib/config/theme/tokens.g.dart`](lib/config/theme/tokens.g.dart:1)
- core/
  - [`lib/core/data/adapters/app_role_adapter.dart`](lib/core/data/adapters/app_role_adapter.dart:1)
  - [`lib/core/data/repositories/local_role_repository.dart`](lib/core/data/repositories/local_role_repository.dart:1)
  - [`lib/core/data/repositories/questionnaire_plan/local_choice_repository.dart`](lib/core/data/repositories/questionnaire_plan/local_choice_repository.dart:1)
  - [`lib/core/data/storage/storage_initializer.dart`](lib/core/data/storage/storage_initializer.dart:1)
  - [`lib/core/design_system/atoms/background_svg.dart`](lib/core/design_system/atoms/background_svg.dart:1)
  - [`lib/core/design_system/atoms/grid_layout.dart`](lib/core/design_system/atoms/grid_layout.dart:1)
  - [`lib/core/design_system/atoms/typography.dart`](lib/core/design_system/atoms/typography.dart:1)
  - many other core files (design system, domain entities, services, injection containers, widgets)
- features/
  - client/data_input (presentation + bloc files)
  - home/presentation/screens/home_screen.dart
  - more/presentation/screens (about_screen, appearance_settings_screen, more_root_screen, notification_preferences_screen, privacy_policy_screen, terms_of_service_screen)
  - role_selection (usecases, bloc, onboarding_screen)
  - therapist/
    - clients (blocs, views, orchestrator)
    - plan_templates (routes, blocs, widgets, orchestrator) — this feature is explicitly in-scope for the pilot
      - [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:1)
      - plan templates blocs and widgets present under `lib/features/therapist/plan_templates/...`
- generated/ (localization)
- l10n/

(For implementation subtasks, use the repository to expand this listing as needed; the above is a top-level snapshot intended for the high-level plan.)

3) Relevant guideline implications (short review)
- From [`doc/architecture.md`](doc/architecture.md:1):
  - Orchestrator widgets are the canonical entry points for feature master-detail flows. Implementations must respect the rule that BLoCs which need persistent lifecycle across master/detail be provided at ShellRoute level; orchestrators must not incorrectly scope BLoCs.
  - Dependency injection uses injectable/GetIt; new tests that rely on DI must follow the DI initialization and test registration guidance.
- From [`doc/testing.md`](doc/testing.md:1):
  - Integration tests have strong constraints and are explicitly avoided in this pilot. Only unit and widget tests shall be created/updated.
  - Widget tests that involve `GoRouter` and `StatefulShellRoute` must be set up using the correct router structure and helpers (use `MaterialApp.router` with builder and provide the routerWidget to providers).
  - Tests interacting with BLoCs must stub `.state` and `.stream` (use `whenListen`) and provide `initialState`. Tests must use helpers like `pumpUntilBlocState` and `SafePump` patterns where applicable.
  - The project enforces many test best practices: set explicit locale in tests, set physical size for responsive tests, reset DI/GetIt between tests, and avoid pumpAndSettle timeouts.
  - Testing guidelines require that any impl_test_part subtask reads `doc/testing.md` and records `guidelines_read: <timestamp>` in the attempt protocol.

Implication for the pilot:
- All test modifications must follow the testing doc: proper DI setup/reset, correct router scaffolding for `StatefulShellRoute`, `whenListen` for BLoCs, and locale/test environment setup.
- Integration tests must not be added or run unless explicitly requested (pilot acceptance criteria reiterates this).

4) Scope of Work (definitive, ordered list)
Note: The pilot goal specifically names updating failing tests under `test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`. The Scope below is minimal and restricted to the plans_and_protocols folder plus the tests indicated by the goal. Per task constraints, only files in the plans_and_protocols folder will be created/modified by this Phase 1 plan document. Implementation will be handled by subsequent subtasks if this plan is approved.

Files to be created or modified (ordered):
1. requirements_tasks/.../plans_and_protocols/2025-11-03_01_plan_high_level_impl_plan.md
   - relative path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/2025-11-03_01_plan_high_level_impl_plan.md
   - reason: High-level Phase 1 plan (this file)
   - expected change type: docs (analysis)
2. test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
   - relative path: test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
   - reason: This is the failing widget test referenced by the goal; pilot should update this test so it follows `GoRouter`/orchestrator testing patterns and stabilizes.
   - expected change type: tests (widget)
3. test/helpers (existing helpers may need small updates)
   - potential files: test/helpers/pump_until_bloc_state.dart, test/helpers/safe_pump.dart, test/helpers/test_router_helpers.dart
   - reason: Ensure test helpers used by the updated test provide the correct router setup and safe pumping strategies per `doc/testing.md`.
   - expected change type: tests (helpers)
4. plans_and_protocols/ part_attempt protocol (created during Phase 3 by impl subtasks)
   - relative path: requirements_tasks/.../plans_and_protocols/ (protocol files to be produced by code subtasks)
   - reason: Per test-writing subtask rules, each test implementation attempt must create a `part_attempt_<n>_protocol.md` documenting guidelines_read timestamp, commands run, modified files, verification, etc.
   - expected change type: docs (protocol)

Notes about scope-count:
- The Scope above references 3 Dart test/helper files that may be modified. This is fewer than or equal to 4 Dart files; therefore it is safe to proceed with a single task. If, during deeper analysis, more than 4 Dart files need modification, the recommendation will be to split the task.

5) Verification level, required tests, estimate effort, risks
- Recommended Verification Level: 2 (targeted verification)
  - Rationale: The pilot must perform Phase 3 verification of unit/widget tests (the goal requires Phase 3 verification). Level 2 denotes running targeted widget tests to confirm the orchestrator pattern behaviour for `plan_templates` without broad integration runs.
- Required tests:
  - Update and run the widget test: `test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart` using `flutter test test/widget/...` (unit/widget) — follow `doc/testing.md` guidance for `GoRouter`/ShellRoute setup.
  - Ensure helper tests or unit tests used by the widget test remain stable.
  - Do not add or run integration tests.
- Effort estimate: Low-to-Medium
  - Rationale: Scope limited to tests and test helpers for a focused feature. Main work is ensuring test environment and mocks match the orchestrator/router patterns described in `doc/testing.md`. If router or BLoC scoping surprises occur, work may increase to Medium.
- Risk / Impact analysis:
  - Risks:
    - Test flakiness due to `GoRouter`/StatefulShellRoute complexity and pumpAndSettle timeouts.
    - Missing or incorrectly stubbed BLoC `.stream` / `.state` leading to TypeError in tests.
    - DI state leakage if GetIt is not reset between tests, causing different results when running the suite vs. individual test.
  - Mitigations:
    - Use `whenListen` for all mock BLoCs and provide `initialState`.
    - Use `pumpUntilBlocState` and `SafePump` helpers to avoid pumpAndSettle timeouts.
    - Reset GetIt in `setUp`/`tearDown`.
  - Impact:
    - Low risk to production code; the pilot changes tests and docs. If tests require code changes to align with guidelines, those will be surfaced as separate tasks.

6) Open questions, assumptions, blockers
- Open questions:
  1. Should the pilot modify production code (widgets/blocs) if tests reveal that behavior deviates from orchestrator rules, or should it only adapt tests to the current implementation? (Pilot directive suggests "writing tests, not implementing a new feature", but some test failures may indicate required small fixes.)
  2. Are there any known local test helper updates that must be applied repository-wide before stabilizing `plan_templates` tests? (I flagged probable helper edits above.)
- Assumptions:
  - The failing test referenced in the goal is the only test that must be updated for this pilot's demonstration (the goal explicitly names it).
  - Integration tests will not be added or run for this pilot.
  - The plans_and_protocols folder for this task currently contains no prior plan files (confirmed via workspace listing).
- Blockers:
  - None immediate for Phase 1 (analysis). For Phase 3 verification, common blockers are unstable test helpers, missing `whenListen` stubs, or router configuration mismatch; these will be documented in `part_attempt_<n>_protocol.md` if encountered.

7) Next (after approval)
- If you approve this high-level plan, I will:
  - Commit this Phase 1 plan file to Git (per process).
  - Create a follow-up implementation subtask (code-mode) that:
    - Starts with a git commit,
    - Reads `doc/testing.md` (records guidelines_read timestamp in protocol),
    - Updates the failing widget test and any necessary helpers,
    - Creates the required `part_attempt_<n>_protocol.md` documenting commands and verification,
    - Runs targeted `flutter test` for the widget(s) (per scoped verification rules),
    - Commits changes and produces a verification report.
- If you prefer to split the work (e.g., isolate helper updates vs. test updates), I will slice the implementation into smaller subtasks upon your instruction.

End of high-level plan (Phase 1).