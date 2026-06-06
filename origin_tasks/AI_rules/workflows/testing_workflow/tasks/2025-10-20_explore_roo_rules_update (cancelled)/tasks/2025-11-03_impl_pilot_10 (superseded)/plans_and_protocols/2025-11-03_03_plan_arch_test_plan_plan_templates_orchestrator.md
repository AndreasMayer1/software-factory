produced_by: arch_test_plan_plan_templates_orchestrator
parent_plans_and_protocols:
- requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/
timestamp: 2025-11-03T08:49:44.000Z
author: Roo (architect-testing-file-plan)
guidelines_read:
- [`doc/testing.md`](doc/testing.md:1):2025-11-03T08:47:41.656Z
test_file:
- path: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
helpers_reviewed:
- [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
- [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
- [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
templates_referenced:
- [`.roo-templates/template_arch_test_plan.md`](.roo-templates/template_arch_test_plan.md:1)
- [`.roo-templates/template_test_run_protocol.md`](.roo-templates/template_test_run_protocol.md:1)

no_changes_to_commit: false
commit_hash: PENDING_COMMIT

short_summary:
- This architect-level plan splits the single widget test file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) into three implementable parts (Part A..C). Each part has explicit acceptance criteria, exact test names (copied verbatim), exact flutter test commands for whole-file and single-test runs, recommended debug steps limited to the allowed scope, and a per-part scope-of-work listing the files implementers may modify. The plan follows the project templates: see [`.roo-templates/template_arch_test_plan.md`](.roo-templates/template_arch_test_plan.md:1) and uses the test-run protocol format in [`.roo-templates/template_test_run_protocol.md`](.roo-templates/template_test_run_protocol.md:1).

parent_plans_and_protocols_listing:
- 2025-11-03_01_plan_high_level_impl_plan.md
- 2025-11-03_02_plan_high_level_impl_plan.md
- 2025-11-03_02_protocol_validation_report.md
- part_attempt_01_protocol.md

parts:
- part_id: part_A
  title: PlanTemplatesRoutes Redirect Logic
  description: Verify router redirect logic and routing decisions (large vs small screen, planId presence, empty/error flows).
  tests_included:
    - "PlanTemplatesRoutes Redirect Logic should redirect to first plan on large screen when no planId is selected"
    - "PlanTemplatesRoutes Redirect Logic should not redirect on small screens"
    - "PlanTemplatesRoutes Redirect Logic should not redirect if planId is already present"
    - "PlanTemplatesRoutes Redirect Logic should not redirect if no templates are loaded after fetch"
    - "PlanTemplatesRoutes Redirect Logic should not redirect if fetch results in error"
  rationale: These tests validate the route-level redirect behaviour and are a logical grouping because they exercise the router + PlanTemplatesBloc interactions and the ScreenSizeService decision path.
  acceptance_condition:
    - All listed tests pass.
    - Programmatic checks: for redirect tests, verify router final path equals expected path per test (example: expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/plan1')).
  required_helpers:
    - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
    - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
    - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
  mock_strategy:
    - Provide mocks used in the test file: `PlanTemplatesBloc`, `PlanTemplateDetailBloc`, `IScreenSizeService`.
    - Use `whenListen` from `bloc_test` to stub BLoC streams and `when(() => mockScreenSizeService.isLargeScreen(any())).thenReturn(...)` accordingly.
  selectors:
    - For router assertions use router.routerDelegate.currentConfiguration.uri.path (no widget finder required).
  expected_widget_states:
    - When redirect occurs, master/detail navigation should update router location to include selected plan id.
  run_commands:
    - Full-file: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
    - Single-test example:
      - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesRoutes Redirect Logic should redirect to first plan on large screen when no planId is selected"
    - For Phase 3 verification (one-line plain-name commands allowed).
  fallbacks_and_debug_steps:
    - Flaky symptoms: router.location not updated, pumpAndSettle timeouts, GoRouter pump loops.
    - Minimal debugging steps (allowed files only):
      1. Re-check and adjust `whenListen` stubbing in the test harness in the test file itself: ensure initialState and stream are provided for `PlanTemplatesBloc`.
      2. Ensure `mockScreenSizeService.isLargeScreen` is stubbed explicitly for each test scenario.
      3. Use `await tester.pump(); await tester.pump(const Duration(milliseconds:100));` (safe pump) instead of `pumpAndSettle` where timeouts occur — helpers present in [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1).
      4. If redirect isn't observed, add `await pumpUntilBlocState(tester, getState: () => mockPlanTemplatesBloc.state, expectedState: PlanTemplatesLoaded(...))` pattern using [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1) to await the loaded state before asserting router location.
      5. If still failing, relax event call-count verifications to >=1 (as test already does) to avoid brittle exact counts.
    - Possible root causes:
      - Missing `whenListen` initialState causing `BlocProvider` to access null stream (see doc/testing.md lines about whenListen).
      - GoRouter async redirect microtask loop causing pumpAndSettle timeouts (use SafePump).
      - ScreenSizeService not stubbed per-test leading to different branch execution.
  scope_of_work_allowed:
    - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) (modify test code only)
    - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1) (adjust safe pump timing if justified)
    - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1) (tweak timeouts/poll intervals)
    - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1) (add helper wrappers or usage comments)
  estimated_effort: low
  recommended_max_attempts: 3

- part_id: part_B
  title: PlanTemplatesOrchestrator Widget Tests — small-screen behaviors
  description: Verify widget composition and event dispatch on small screens (PlanTemplateList vs PlanTemplateDetailContent when planId absent or selected).
  tests_included:
    - "PlanTemplatesOrchestrator Widget Tests should display PlanTemplateList when no planId is selected on small screen"
    - "PlanTemplatesOrchestrator Widget Tests should display PlanTemplateDetailContent when planId is selected on small screen"
  rationale: These tests validate the small-screen master/detail rendering and that the detail BLoC receives the load event when appropriate.
  acceptance_condition:
    - For "list" test: expect(find.byType(PlanTemplateList), findsOneWidget) and expect(find.byType(PlanTemplateDetailContent), findsNothing).
    - For "detail" test: expect(find.byType(PlanTemplateDetailContent), findsOneWidget) and verify `mockPlanTemplateDetailBloc.add(const PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1'))` called (allow >=1).
  required_helpers:
    - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
    - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
  mock_strategy:
    - Use `whenListen` to emulate PlanTemplatesLoaded and PlanTemplateDetailState changes.
    - Stub `mockScreenSizeService.getLayoutConfig(any())` to return default `LayoutConfig`.
  selectors:
    - find.byType(PlanTemplateList)
    - find.byType(PlanTemplateDetailContent)
    - find.text('Select a plan template to view its details.') (if present)
  expected_widget_states:
    - Small-screen: when no planId selected, master list visible only.
    - Small-screen with planId: detail content visible, list hidden.
  run_commands:
    - Full-file: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
    - Single-test examples:
      - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesOrchestrator Widget Tests should display PlanTemplateList when no planId is selected on small screen"
      - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesOrchestrator Widget Tests should display PlanTemplateDetailContent when planId is selected on small screen"
  fallbacks_and_debug_steps:
    - Flaky symptoms: missing widget, event verify failing due to timing.
    - Minimal debugging steps (allowed files only):
      1. Confirm `whenListen` sets both `initialState` and `Stream.fromIterable([...])` for both blocs in the test harness.
      2. Use `await tester.pumpAndSettleSafe()` (from [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)) instead of `pumpAndSettle`.
      3. If event verification fails intermittently, change verification to `called(greaterThanOrEqualTo(1))` as permitted by project guidelines (see existing tests).
      4. Add localized debug prints in the test file (temporary) to confirm router location and bloc.state values before assertions.
    - Possible root causes:
      - Missing stubbed `.stream` causing BLoC stream access errors.
      - Race between router navigation and BLoC stream emission.
  scope_of_work_allowed:
    - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
    - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
    - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
  estimated_effort: medium
  recommended_max_attempts: 4

- part_id: part_C
  title: PlanTemplatesOrchestrator Widget Tests — large-screen and auto-open behaviors
  description: Validate large-screen master/detail rendering, auto-open first-plan redirect, and combined master+detail visibility & event dispatch on large screens.
  tests_included:
    - "PlanTemplatesOrchestrator Widget Tests should display PlanTemplateList and PlanTemplateDetailContent on large screen when planId is selected"
    - "PlanTemplatesOrchestrator Widget Tests should auto-open first plan on large screen and display both master and detail"
  rationale: These tests exercise the complex interaction between screen-size detection, router redirect logic and bloc-driven detail loading; grouped together because they exercise the large-screen code paths and master-detail simultaneous rendering.
  acceptance_condition:
    - For large-screen with planId: expect both PlanTemplateList and PlanTemplateDetailContent present; verify LoadPlanTemplates and PlanTemplateDetailEvent.loadPlanTemplateDetail('plan1') called (>=1 ok).
    - For auto-open: router final path must equal '${AppRoutes.therapistPlans.pathTemplate}/plan1' and both master and detail widgets present.
  required_helpers:
    - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
    - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
    - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
  mock_strategy:
    - Stub `IScreenSizeService.isLargeScreen(any())` to return true for large-screen tests.
    - Use `whenListen` sequences for PlanTemplatesBloc and PlanTemplateDetailBloc to simulate loaded states and transitions.
    - For auto-open test, emit `PlanTemplatesLoaded` after initial pump to simulate data arrival that triggers redirect.
  selectors:
    - find.byType(PlanTemplateList)
    - find.byType(PlanTemplateDetailContent)
  expected_widget_states:
    - Large-screen: both master and detail visible; router path reflects selected id when auto-open.
  run_commands:
    - Full-file: flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
    - Single-test examples:
      - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesOrchestrator Widget Tests should display PlanTemplateList and PlanTemplateDetailContent on large screen when planId is selected"
      - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesOrchestrator Widget Tests should auto-open first plan on large screen and display both master and detail"
  fallbacks_and_debug_steps:
    - Flaky symptoms: pumpAndSettle loops, test view size not triggering breakpoint, router path not updated after PlanTemplatesLoaded emission.
    - Minimal debugging steps (allowed files only):
      1. Ensure tester.view.physicalSize and devicePixelRatio are set and cleaned up with addTearDown in the test file.
      2. Use `await tester.pumpAndSettleSafe()` to avoid GoRouter pump loops.
      3. If auto-open fails, verify the sequence: emit PlanTemplatesLoaded via `whenListen` or call `whenListen` with the loaded stream before asserting router path; if necessary inject an extra pump after emitting loaded state.
      4. If timing remains flaky, add a short explicit pump delay (`await tester.pump(const Duration(milliseconds:100));`) after pumpAndSettleSafe before asserting router path.
    - Possible root causes:
      - Router redirect asynchronous timing; PlanTemplatesLoaded arrives after redirect check completed.
      - Screen size not set high enough to be considered large (pixel ratio interplay).
  scope_of_work_allowed:
    - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
    - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
    - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
    - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
  estimated_effort: medium
  recommended_max_attempts: 4

verification_commands:
- Full-file run:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- Plain-name examples (single-test runs):
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesRoutes Redirect Logic should redirect to first plan on large screen when no planId is selected"
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesOrchestrator Widget Tests should display PlanTemplateList when no planId is selected on small screen"
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesOrchestrator Widget Tests should auto-open first plan on large screen and display both master and detail"

iterations_and_part_attempt_workflow:
- Spawn pattern for Test File Part Orchestrators:
  1. Orchestrator creates an `impl_test_part` subtask for a single `part_<n>` and provides:
     - full path to parent `plans_and_protocols` folder (this folder).
     - the `parts` entry from this plan (as Scope of Work).
     - the exact `flutter test` run commands for the part (above).
     - required helpers and mock strategy.
     - depth level: 4 (this subtask is level 4).
  2. Test File Part Orchestrator MUST:
     - Start by creating a git commit (message must contain "2025-11-03_impl_pilot_10" and the part id).
     - Read [`doc/testing.md`](doc/testing.md:1) and record `guidelines_read: <ISO8601 timestamp>` in each `part_attempt_<n>_protocol.md`.
     - Implement minimal fixes (only within the `scope_of_work_allowed` files listed for the part).
     - After each attempt (including no-change attempts), produce `part_attempt_<n>_protocol.md` in parent `plans_and_protocols` (see required protocol fields below); save logs under `plans_and_protocols/logs/`.
     - Re-run only the targeted tests listed in `run_commands`.
     - Stop when acceptance_condition is met or `recommended_max_attempts` is reached.
     - On success, commit changes and include commit hash in the final `part_attempt_<n>_protocol.md`.
     - If blocked or MAX_ATTEMPTS reached without success, create an `explore_test_blocker_<timestamp>.md` document in this folder with aggregated artifacts and findings.
  3. The Orchestrator (parent) will consume `part_attempt_<n>_protocol.md` files and append a short entry to `part_attempts_log.md` (create if missing) with summary lines for each attempt.

protocol_files_to_be_created_by_implementers:
- Each attempt must create a protocol file named `part_attempt_<NN>_protocol.md` saved under:
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/:1)
- Required fields for each `part_attempt_<NN>_protocol.md` (minimum):
  - subtask_id: <impl_test_part identifier>
  - parent_test_part_orchestrator: arch_test_plan_plan_templates_orchestrator
  - attempt_number: <n>
  - guidelines_read: <ISO8601 timestamp> (must reference [`doc/testing.md`](doc/testing.md:1))
  - commands_run: [list of exact commands executed]
  - logs_path: relative path to saved full logs under plans_and_protocols/logs/
  - modified_files: [list of paths changed]
  - commit_hash: <git commit hash after changes>
  - verification_performed: true|false
  - verification_result: PASS|FAIL|ERROR|NONE
  - notes: free-text (include debugging steps and root-cause analysis)
- Use the provided template reference: [`.roo-templates/template_test_run_protocol.md`](.roo-templates/template_test_run_protocol.md:1) as the required verification protocol format.

explore_blocker_checklist (for explore_test_blocker subtasks):
- Suspected causes:
  - incomplete or missing `whenListen` stubbing for mock blocs
  - GoRouter async redirect microtask loop causing pumpAndSettle timeouts
  - incorrect screen-size stubbing (devicePixelRatio interplay)
  - missing localization causing text mismatches
- Suggested remediation steps:
  1. Confirm `whenListen` calls include `initialState` and a non-null stream.
  2. Replace `pumpAndSettle` with `pumpAndSettleSafe` or `pumpUntilBlocState` where router/BLoC async interactions occur.
  3. Ensure tests set `tester.view.physicalSize` and `devicePixelRatio` to match breakpoints for large-screen tests and add `addTearDown` to reset.
  4. If router redirect not observed, await `router.routeInformationProvider.value` per doc/testing.md guidance for async redirects.
  5. If blocked at build/compilation due to generated types, run `flutter pub run build_runner build --delete-conflicting-outputs` locally (note: code-mode implementers only).

plan_for_iterating_test_parts (short):
- Implementer workflow (per-part):
  1. Create `impl_test_part` subtask (code mode) with this part's scope.
  2. Commit current branch (git add; git commit) with message containing "2025-11-03_impl_pilot_10 part_<n> start".
  3. Attempt to run targeted test(s) (single --plain-name preferred).
  4. If PASS, record `part_attempt_01_protocol.md` with PASS and commit final changes.
  5. If FAIL, apply minimal fixes within allowed scope, commit each attempt, and record `part_attempt_<n>_protocol.md`.
  6. Stop when PASS or when recommended_max_attempts reached; on persistent failure, produce `explore_test_blocker_<timestamp>.md` and escalate to architect (orchestrator will create explore subtask).
- Orchestrator aggregation:
  - For each part, collect all `part_attempt` files and append a single-line summary to `part_attempts_log.md` with: timestamp, part_id, attempts, final_result, link to logs.

exact test names (verbatim) — copied from file for implementers:
- PlanTemplatesRoutes Redirect Logic should redirect to first plan on large screen when no planId is selected
- PlanTemplatesRoutes Redirect Logic should not redirect on small screens
- PlanTemplatesRoutes Redirect Logic should not redirect if planId is already present
- PlanTemplatesRoutes Redirect Logic should not redirect if no templates are loaded after fetch
- PlanTemplatesRoutes Redirect Logic should not redirect if fetch results in error
- PlanTemplatesOrchestrator Widget Tests should display PlanTemplateList when no planId is selected on small screen
- PlanTemplatesOrchestrator Widget Tests should display PlanTemplateDetailContent when planId is selected on small screen
- PlanTemplatesOrchestrator Widget Tests should display PlanTemplateList and PlanTemplateDetailContent on large screen when planId is selected
- PlanTemplatesOrchestrator Widget Tests should auto-open first plan on large screen and display both master and detail

expected_flaky_areas_and_mitigations:
- GoRouter redirect + pumpAndSettle loops: use [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1) and `pumpUntilBlocState` pattern from [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1) (see `doc/testing.md` lines about SafePump and pumpUntilBlocState).
- BLoC stream null errors: always use `whenListen` with `initialState` (see doc/testing.md lines about whenListen).
- Timing-sensitive event verification: relax exact call-counts in `verify()` to `greaterThanOrEqualTo(1)` where appropriate.
- Screen-size detection: explicitly stub `IScreenSizeService.isLargeScreen(any())` and set `tester.view.physicalSize` + `devicePixelRatio` for large-screen tests; reset with `addTearDown`.

files_you_may_modify (strict Scope of Work enforcement):
- Only the following files may be modified by Test File Part Orchestrators under this plan:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
  - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
  - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
  - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
- Implementers MUST NOT change any other files. If a needed change touches other files (e.g., production code or other tests), create an `explore_test_blocker_<timestamp>.md` and request orchestrator approval before changes.

files_to_be_created_by_implementers:
- `part_attempt_<NN>_protocol.md` files under the parent `plans_and_protocols` folder (required per-attempt protocol; template: [`.roo-templates/template_test_run_protocol.md`](.roo-templates/template_test_run_protocol.md:1))
- On persistent blocker: `explore_test_blocker_<timestamp>.md` under same folder, containing aggregated logs and findings.

final_notes_and_next_steps:
- This plan is complete and prescriptive for implementers. It references project guidelines and helper utilities.
- Next operational step (by code-mode implementer): create `impl_test_part` subtasks per part (A..C), run the specified flutter test commands, and follow the per-attempt protocol. Each impl attempt must commit changes as required by the project's workflow and record `guidelines_read` inside attempt protocols.
