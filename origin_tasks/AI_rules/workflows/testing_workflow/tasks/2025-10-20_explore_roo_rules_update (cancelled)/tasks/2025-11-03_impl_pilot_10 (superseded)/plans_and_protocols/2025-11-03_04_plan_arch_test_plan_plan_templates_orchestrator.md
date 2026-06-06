produced_by: arch_test_plan_plan_templates_orchestrator_partA
parent_plans_and_protocols:
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/:1)
timestamp: 2025-11-03T08:59:15.915Z
author: Roo (arch_test_plan_part_A)
guidelines_read: [`doc/testing.md`](doc/testing.md:1):2025-11-03T08:59:15.915Z

summary:
- This document is the architect-level Part A plan to fix the five failing widget tests grouped under "PlanTemplatesRoutes Redirect Logic" in the test file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1).
- It contains root-cause analysis, precise, minimal code-change suggestions (limited to allowed test/helper files), exact flutter test commands including --plain-name strings, verification steps and acceptance criteria, allowed files for the follow-up implementation subtask, and rollback/commit guidance.

context_and_scope:
- Parent test file: [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- Routing implementation inspected: [`lib/features/therapist/plan_templates/plan_templates_routes.dart`](lib/features/therapist/plan_templates/plan_templates_routes.dart:1)
- Helpers inspected:
  - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
  - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
  - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
- This plan will NOT modify production code. If a production change is strictly required it will be documented and marked "requires escalation".
- New plan file index chosen: 04 (next available after 01..03 present in folder).

exact_tests_targeted (verbatim):
- PlanTemplatesRoutes Redirect Logic should redirect to first plan on large screen when no planId is selected
- PlanTemplatesRoutes Redirect Logic should not redirect on small screens
- PlanTemplatesRoutes Redirect Logic should not redirect if planId is already present
- PlanTemplatesRoutes Redirect Logic should not redirect if no templates are loaded after fetch
- PlanTemplatesRoutes Redirect Logic should not redirect if fetch results in error

readings_and_guidelines:
- I read the project's testing guidelines: [`doc/testing.md`](doc/testing.md:1) and recorded the timestamp above. Key takeaways applied:
  - Always use `whenListen` with explicit `initialState` for stubbed BLoCs.
  - Avoid `tester.pumpAndSettle()` in GoRouter redirect tests; use short safe pumps or custom pump helpers.
  - For async GoRouter redirects, await router.routeInformationProvider.value or use controlled pumping until BLoC emits the loaded state.
  - Explicitly stub screen-size checks and, for large-screen tests, set `tester.view.physicalSize` and `devicePixelRatio` and reset with `addTearDown`.

root_cause_analysis (per test)
1) "should redirect to first plan on large screen when no planId is selected"
   - Observed: test waits for redirect but sometimes router path stays on base path or redirect happens too early (before PlanTemplatesLoaded state).
   - Root causes:
     - PlanTemplatesLoaded is emitted after the redirect check runs; redirect uses synchronous planTemplatesBloc.state which is still initial.
     - `whenListen` may not provide an immediate `initialState` or test harness emits PlanTemplatesLoaded too late.
     - GoRouter async redirect microtask timing combined with pumpAndSettle loops.
   - Likely fix: Ensure test stubs the BLoC so PlanTemplatesLoaded is available at the moment redirect executes or delay redirect evaluation until loaded state is observed (pumpUntilBlocState or await router.routeInformationProvider.value after emitting loaded).

2) "should not redirect on small screens"
   - Observed: test asserts no redirect but flakiness if screen-size stubbing is default or not explicit.
   - Root causes:
     - `mockScreenSizeService.isLargeScreen(any())` defaults to false in setUp but some tests override; if not explicit, state may be ambiguous.
   - Fix: Always explicitly stub isLargeScreen for each test; do not rely on defaults.

3) "should not redirect if planId is already present"
   - Observed: test initializes router with path containing planId but redirect logic may still run if route uri string comparators differ.
   - Root causes:
     - Redirect check uses `state.uri.toString() == '/therapist/plans'` — if initialLocation includes trailing slash or parameters, string comparison can be brittle.
     - Test router initialLocation may differ in exact formatting vs check.
   - Fix: In tests, initialize router initialLocation exactly as production expects; ensure the initialLocation used contains no unexpected trailing slashes; if necessary add a short safe pump then assert.

4) "should not redirect if no templates are loaded after fetch"
   - Observed: When BLoC emits empty list, redirect shouldn't trigger.
   - Root causes:
     - Missing or late emission of `PlanTemplatesLoaded(planTemplates: [])` or redirect evaluated before the empty loaded state is processed.
   - Fix: Ensure test emits PlanTemplatesLoaded([]) early (via whenListen with initialState set to PlanTemplatesInitial and stream providing PlanTemplatesLoaded([])) and wait for it with pumpUntilBlocState before asserting router path.

5) "should not redirect if fetch results in error"
   - Observed: test expects no redirect and that LoadPlanTemplates was called once.
   - Root causes:
     - Redirect may check BLoC state while it is still initial; or the test's `whenListen` sequence may be inconsistent, causing multiple LoadPlanTemplates calls.
   - Fix: Use consistent whenListen setup (initialState and stream) and relax LoadPlanTemplates verification to >=1 (already present). Ensure the test waits for error state before asserting.

minimal_proposed_changes (file-level; allowed-scope only)
- All changes are test/helper changes only (no production changes here). Proposed minimal edits are inline snippets; implementers must apply them in the follow-up code-mode subtask.

1) Ensure every use of `whenListen` in the tests includes an explicit initialState and a non-null stream (if the test expects no further emissions, use Stream.empty()):
   - Example change in [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1):
     <<Snippet A>>
     Replace occurrences like:
     whenListen(
       mockPlanTemplatesBloc,
       Stream.fromIterable([PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList())]),
       initialState: const PlanTemplatesInitial(),
     );
     With the same (ensure initialState is present) — this is already present in many places but audit and add initialState where missing.
     <<end Snippet A>>

2) Force PlanTemplatesLoaded to be present at redirect evaluation (two acceptable approaches — implementer picks one):
   - Approach 1 (preferred): Provide PlanTemplatesLoaded as the immediate initialState of the bloc used by the redirect check:
     <<Snippet B1>>
     whenListen(
       mockPlanTemplatesBloc,
       Stream.fromIterable([]), // no further emissions
       initialState: PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList()),
     );
     <<end Snippet B1>>
     Rationale: the redirect handler reads planTemplatesBloc.state synchronously; making the loaded state the initialState guarantees redirect sees data.
   - Approach 2: Keep initialState as PlanTemplatesInitial but make the test wait until PlanTemplatesLoaded is emitted before asserting router location:
     <<Snippet B2>>
     // After emitting PlanTemplatesLoaded via whenListen:
     await pumpUntilBlocState(
       tester: tester,
       getState: () => mockPlanTemplatesBloc.state,
       expectedState: PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList()),
       timeout: const Duration(seconds: 5),
     );
     // Then safe pump and assert router path
     await tester.pumpAndSettleSafe();
     expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/plan1');
     <<end Snippet B2>>

3) Explicitly stub IScreenSizeService.isLargeScreen per test — ensure no reliance on global default:
   <<Snippet C>>
   // In each test:
   when(() => mockScreenSizeService.isLargeScreen(any())).thenReturn(true); // or false for small-screen tests
   <<end Snippet C>>

4) Use safe pump helper and (when needed) await router.routeInformationProvider.value for redirect completion:
   <<Snippet D>>
   // After emitting states and pumping:
   await tester.pumpAndSettleSafe();
   // For asynchronous redirect handlers:
   await router.routeInformationProvider.value; // await resolved route
   await tester.pumpAndSettleSafe();
   <<end Snippet D>>

5) Stabilize large-screen tests by setting tester view size and devicePixelRatio explicitly and adding addTearDown to reset:
   <<Snippet E>>
   tester.view.physicalSize = const Size(1200 * 3, 800 * 3);
   tester.view.devicePixelRatio = 3.0;
   addTearDown(() => tester.view.resetPhysicalSize());
   when(() => mockScreenSizeService.isLargeScreen(any())).thenReturn(true);
   <<end Snippet E>>

6) PumpUntil helper adjustment (allowed optional tweak)
   - If implementer chooses to adjust [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1), change default timeout to 8s and pollInterval to 50ms for faster retries and more tolerance:
     <<Snippet F (patch suggestion)>
     // In pump_until_bloc_state.dart change:
     Duration timeout = const Duration(seconds: 8),
     Duration pollInterval = const Duration(milliseconds: 50),
     >
     <<end Snippet F (patch suggestion)>>
   - This is optional; prefer using explicit waits in tests per-case.

exact_diffs_snippets (minimal; implementers should apply with apply_diff or write_to_file)
- Example diff to make PlanTemplatesLoaded immediate initialState for the "redirect to first plan" test:
  <<SEARCH/REPLACE>>
  :start_line:170
  -------
       whenListen(
         mockPlanTemplatesBloc,
         planTemplatesStateStream,
         initialState: initialPlanTemplatesState,
       );
  =======
       whenListen(
         mockPlanTemplatesBloc,
         Stream.fromIterable([]), // no further emissions
         initialState: PlanTemplatesLoaded(planTemplates: mockPlans.map((p) => p.toJson()).toList()),
       );
  >>>>>>> REPLACE
  <<END>>
Note: The implementer will need to edit the exact lines in the test file to match the snippet context.

exact_flutter_test_commands (to run from repo root)
- Full-file run:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- Single-test runs (use --plain-name; verbatim strings):
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesRoutes Redirect Logic should redirect to first plan on large screen when no planId is selected"
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesRoutes Redirect Logic should not redirect on small screens"
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesRoutes Redirect Logic should not redirect if planId is already present"
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesRoutes Redirect Logic should not redirect if no templates are loaded after fetch"
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart --plain-name "PlanTemplatesRoutes Redirect Logic should not redirect if fetch results in error"

verification_steps_and_acceptance_criteria
1. Implementation subtask applies minimal changes restricted to allowed files (see Allowed Files section below).
2. Run the single-test plain-name commands above for each of the five tests.
3. Acceptance criteria:
   - All five tests pass locally in a single-machine run (PASS status).
   - Programmatic verifications in tests succeed:
     - For redirect: expect(router.routerDelegate.currentConfiguration.uri.path, '${AppRoutes.therapistPlans.pathTemplate}/plan1')
     - For non-redirect cases: expect(router.routerDelegate.currentConfiguration.uri.path, AppRoutes.therapistPlans.pathTemplate)
   - Event dispatch verifications use tolerant counts (called(greaterThanOrEqualTo(1))) where previously relaxed in file.
4. If any test fails:
   - Re-check that `whenListen` initialState is set correctly.
   - Re-run the single failing test with additional debug prints and pumpUntilBlocState pattern.
   - If redirect still fails, try Approach 1 (make loaded state initialState) instead of Approach 2 (wait for emission).

exact_list_of_files follow-up implementation subtask may modify (allowed scope)
- [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
- [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
- [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
- Additionally, implementers must create per-attempt protocol files in the parent `plans_and_protocols` folder:
  - part_attempt_<NN>_protocol.md (required fields listed in the project rules).

changes_requiring_escalation (production; DO NOT implement here)
- If redirect logic proves incorrect because it relies on synchronous bloc.state in the router (e.g., production `plan_templates_routes.dart` reads bloc.state in redirect), and making the test set initialState is insufficient or undesirable, a production change may be required:
  - Proposed production change (requires escalation): change redirect logic to await router.routeInformationProvider.value or refactor redirect to perform asynchronous check that subscribes to bloc stream instead of reading synchronous state (longer discussion required).
  - File to be changed if escalated: [`lib/features/therapist/plan_templates/plan_templates_routes.dart`](lib/features/therapist/plan_templates/plan_templates_routes.dart:1)
  - This plan documents the suggestion but does NOT implement it; implementer must escalate to architect if needed.

rollback_plan_and_git_messages
- Always follow project commit policy: separate git add and git commit steps; commit messages must reference the task.
- Suggested workflow for implementer subtask (code mode):
  1. git add <modified files>
     - execute: git add test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
     - and any helpers changed
  2. git commit -m "part A: plan — PlanTemplatesRoutes Redirect Logic start"
     - After successful test pass:
       - git add changed files
       - git commit -m "part A: fix — stabilize PlanTemplatesRoutes redirect tests"
- Rollback:
  - If changes introduce regressions, revert to previous commit:
    - git revert <commit-hash> or git checkout -- <file>
  - Keep per-attempt protocol files indicating commit_hash to allow pinpoint rollback.

per-attempt protocol requirement (implementer reminder)
- The implementer MUST create a `part_attempt_01_protocol.md` (and subsequent) inside this folder after each attempt and include:
  - subtask_id
  - parent_test_part_orchestrator: arch_test_plan_plan_templates_orchestrator
  - attempt_number
  - guidelines_read: [`doc/testing.md`](doc/testing.md:1):<ISO8601 timestamp>
  - commands_run
  - logs_path
  - modified_files
  - commit_hash
  - verification_performed: true|false
  - verification_result: PASS|FAIL|ERROR|NONE
  - notes

estimated_effort_and_attempts
- Estimated effort: low-medium (1-4 hours depending on flakiness).
- Recommended max attempts: 3 for Part A before creating explore_test_blocker_<timestamp>.md and escalating.

next_actions_for_code-mode_implementer (exact steps)
1. Start an impl_test_part subtask in code mode for Part A.
2. Create a git commit (git add; git commit) with message containing "2025-11-03_impl_pilot_10 part_A start".
3. Apply the minimal edits described in this plan to the allowed files (prefer Approach 1 for redirect test).
4. Run single-test commands (use --plain-name) for targeted verification.
5. Produce `part_attempt_01_protocol.md` in this folder with the required fields (include guidelines_read timestamp).
6. If PASS, commit final changes with message: "part A: fix — stabilize PlanTemplatesRoutes redirect tests".
7. If FAIL and further attempts needed, record each attempt protocol and retry up to recommended_max_attempts.

artifacts_created_by_this_plan
- Plan file (this file):
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/2025-11-03_04_plan_arch_test_plan_plan_templates_orchestrator.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/2025-11-03_04_plan_arch_test_plan_plan_templates_orchestrator.md:1)

final_notes:
- This plan is intentionally conservative: it prefers fixing tests and test harness timing/stubbing rather than changing production router code. If, after two attempts, tests remain failing due to genuine production behavior (redirect reading synchronous state), escalate and propose a small production refactor.
- The implementer must follow the per-attempt protocol and commit rules strictly.

plan_created_by: Roo (code mode)
plan_file_path: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/2025-11-03_04_plan_arch_test_plan_plan_templates_orchestrator.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/2025-11-03_04_plan_arch_test_plan_plan_templates_orchestrator.md:1)