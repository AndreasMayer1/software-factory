# 2025-11-03_02_protocol_validation_report.md

timestamp: 2025-11-03T08:21:30Z
author: Roo (validation_protocol)
parent_plan: [`2025-11-03_01_plan_high_level_impl_plan.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-03_impl_pilot_10/plans_and_protocols/2025-11-03_01_plan_high_level_impl_plan.md:1)

## Purpose
Validate the high-level plan in the referenced plan file and confirm the assumptions required to proceed to Phase 2 (implementation). This protocol either confirms the plan or lists failed assumptions with evidence and exact recommended corrections.

## Files checked (Scope of Work)
- [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1)
- [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1)
- [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
- [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1)
- Router/config files:
  - [`lib/config/routes/app_router.dart`](lib/config/routes/app_router.dart:1)
  - [`lib/config/routes/app_routes.dart`](lib/config/routes/app_routes.dart:1)
  - [`lib/config/routes/app_route_info.dart`](lib/config/routes/app_route_info.dart:1)
  - [`lib/config/routes/route_utils.dart`](lib/config/routes/route_utils.dart:1)
- Feature orchestrator:
  - [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:1)
- Guidelines:
  - [`doc/architecture.md`](doc/architecture.md:1)
  - [`doc/testing.md`](doc/testing.md:1)

All above files were inspected for alignment with the plan's Scope of Work and assumptions.

---

## Confirmed assumptions
1. The test and helper files listed in the plan exist at the paths specified.
   - Evidence: Files open and readable; initial lines present:
     - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) (contains mocked blocs, createTestRouter with `StatefulShellRoute.indexedStack`, and tests referencing `AppRoutes.therapistPlans`).
     - [`test/helpers/pump_until_bloc_state.dart`](test/helpers/pump_until_bloc_state.dart:1) (provides pumpUntilBlocState helper).
     - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1) (provides SafePump extension).
     - [`test/helpers/test_router_helpers.dart`](test/helpers/test_router_helpers.dart:1) (provides pumpMoreScreenTestApp and pumpAndSettleMoreScreenTestApp).
2. The repository uses `GoRouter` with `StatefulShellRoute` patterns and centralized route metadata.
   - Evidence: `lib/config/routes/app_router.dart` constructs `GoRouter` with `StatefulShellRoute.indexedStack` and uses `AppRoutes.shellPlansBranch.navigatorKey` and spreads `PlanTemplatesRoutes.routes` (see [`lib/config/routes/app_router.dart`](lib/config/routes/app_router.dart:122)).
   - `lib/config/routes/app_routes.dart` contains `AppRouteInfo` entries for `therapistPlans` and `therapistPlanDetail` including `pathTemplate` and navigator keys (see [`lib/config/routes/app_routes.dart`](lib/config/routes/app_routes.dart:45)).
   - `doc/architecture.md` documents the orchestrator + nested shell + redirect patterns used by the plan (see [`doc/architecture.md`](doc/architecture.md:326)).
3. The `PlanTemplatesOrchestrator` exists and implements the pattern the plan expects (reads screen size service, uses `ResponsiveLayoutBuilder`, triggers redirect to first plan on large screens).
   - Evidence: [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:24) shows `PlanTemplatesOrchestrator` reading `IScreenSizeService`, obtaining `planId` from `GoRouterState.of(context).pathParameters['planId']`, and performing a `BlocListener` that calls `context.go()` to select the first plan on large screens when needed (lines 29-42).

## Failed assumptions (with evidence and recommended corrections)
No critical missing files were detected. However, I observed the following assumptions that require clarification or small plan updates to avoid surprises during implementation:

1. Assumption: Plan expects router-level "state-aware async redirects" may be present and preferable to widget-level `BlocListener` redirects.
   - Evidence: The plan (Phase 1) mentions "State-Aware Redirect" pattern in `doc/architecture.md` recommending async redirects on the GoRoute for auto-selection (see [`doc/architecture.md`](doc/architecture.md:424-436)). The actual current implementation in the code uses a widget-level `BlocListener` inside `PlanTemplatesOrchestrator` to perform redirect via `context.go(...)` (see [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:35-42)).
   - Impact: This is not a blocking failure, but it contradicts the "recommended" implementation style in the guidelines. Tests and plan should acknowledge that the codebase currently uses widget-level `BlocListener` redirect; the plan must accept this or require refactoring.
   - Recommendation: Update the high-level plan to explicitly allow either:
     - "Adapt tests to the current widget-level `BlocListener` redirect implementation", OR
     - "Add a refactor step to move to async router `redirect` before test adaptation" (if project maintainers prefer guideline-conformant redirect).
   - Exact plan change: Add a bullet under "Open questions / Assumptions" stating which redirect pattern to target: widget-listener (current) vs async route redirect (guideline). If choosing route-level redirect, add a small refactor subtask to implement it before test edits.

2. Assumption: BLoCs are provided at shell/router level and tests will not need to register additional DI bindings beyond GetIt singletons used in tests.
   - Evidence: `app_router.dart` creates BLoC providers inside the top-level `StatefulShellRoute.indexedStack` (see [`lib/config/routes/app_router.dart`](lib/config/routes/app_router.dart:126-152)). In tests, `plan_templates_orchestrator_test.dart` registers mocks with `GetIt.I.registerSingleton<...>(...)` (see lines 57-59 in the test). That pattern is consistent, but the test code both registers GetIt singletons and uses `MultiBlocProvider` in its `createTestRouter` helper. This duplication can cause confusion if DI reset is not managed in setUp/tearDown.
   - Impact: Potential test flakiness if GetIt is not reset between tests.
   - Recommendation: Emphasize in the plan that test implementation subtasks must reset GetIt between tests (use `GetIt.I.reset()` or `GetIt.I.unregister` as appropriate) and follow test guidelines (document `guidelines_read: <timestamp>` in each `part_attempt` protocol). Add this explicit instruction to the plan's Phase 2 checklist.

3. Assumption: Helper files are sufficient and correctly scoped for stable pumping with GoRouter.
   - Evidence: There are two safe pump helpers: `test/helpers/safe_pump.dart` and a similar extension within `test/helpers/test_router_helpers.dart` (lines 74-80). Duplicate helpers are present; this duplication is harmless but may lead to inconsistent usage or confusion.
   - Impact: Low. Could cause minor maintenance confusion.
   - Recommendation: Note in the plan that tests should consistently import the canonical `test/helpers/safe_pump.dart` rather than duplicated local helpers; optionally consolidate helpers in a future cleanup task.

## Excerpts (evidence) — selected file + lines
- Redirect pattern in orchestrator (widget-level redirect):
  - [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:35-41)
    - 35 |       listener: (context, state) {
    - 36 |         print('DEBUG: BlocListener triggered. State: $state, isLargeScreen: $isLargeScreen, planId: $planId');
    - 37 |         if (isLargeScreen && planId == null && state is PlanTemplatesLoaded && state.planTemplates.isNotEmpty) {
    - 38 |           print('DEBUG: Redirecting to: ${AppRoutes.therapistPlans.pathTemplate}/${state.planTemplates.first['uuid']}');
    - 39 |           WidgetsBinding.instance.addPostFrameCallback((_) {
    - 40 |             context.go('${AppRoutes.therapistPlans.pathTemplate}/${state.planTemplates.first['uuid']}');
    - 41 |           });
- Router uses StatefulShellRoute as expected:
  - [`lib/config/routes/app_router.dart`](lib/config/routes/app_router.dart:122-129)
    - 122 |     StatefulShellRoute.indexedStack(
    - 123 |       builder: (context, state, navigationShell) {
    - 124 |         // This builder now constructs the main layout (Scaffold/Row)
    - 125 |         // and places the navigation elements and the navigationShell (content) accordingly.
    - 126 |         return MultiBlocProvider(
- Test helper safe pump:
  - [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:3-7)
    - 3 | extension SafePump on WidgetTester {
    - 4 |   Future<void> pumpAndSettleSafe() async {
    - 5 |     await pump();
    - 6 |     await pump(const Duration(milliseconds: 100));
    - 7 |   }
- Test file confirms use of StatefulShellRoute in test router helper:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:88-96)
    - 88 |   GoRouter createTestRouter(String initialLocation) {
    - 89 |     return GoRouter(
    - 90 |       initialLocation: initialLocation,
    - 91 |       routes: [
    - 92 |         StatefulShellRoute.indexedStack(
    - 93 |           builder: (context, state, navigationShell) {
    - 94 |             return MultiBlocProvider(
    - 95 |               providers: [
    - 96 |                 BlocProvider<PlanTemplatesBloc>(

## Final verdict
Plan Invalid — requires a minor plan update before Phase 2.

Rationale: The high-level plan's Scope of Work and test targets are valid and the listed files exist. However, the plan implicitly assumes the "State-Aware Redirect" pattern (router-level async redirect) described in `doc/architecture.md`. The repository currently implements auto-selection using a widget-level `BlocListener` inside the orchestrator. This is not strictly a blocker to writing tests, but it is a deviation from the guideline recommendation and must be resolved by either:
- updating the plan to explicitly target the current widget-listener redirect pattern (preferred minimal-change path), or
- adding a refactor step to migrate the redirect to an async router redirect before updating tests (larger change).

Because this is a decision with architectural implications, the plan must be updated with the chosen approach before proceeding to Phase 2 implementation subtasks.

## Required exact changes to the plan (edit suggestions)
1. Under "Open questions, assumptions, blockers" (in the high-level plan file), add:
   - "Decision: Which redirect pattern should the implementation target? Choose one:
     a) Adapt tests to current widget-level `BlocListener` redirect (fast, minimal change), OR
     b) Refactor the feature to use an async router-level redirect per `doc/architecture.md` before updating tests (aligns with guidelines but adds work)."
2. Add an explicit test-subtask precondition:
   - "Tests must reset GetIt between tests and ensure `whenListen` is used for all mock BLoCs. Each `impl_test_part` must record `guidelines_read: <timestamp>` in its `part_attempt_<n>_protocol.md`."
3. Optional cleanup note:
   - "Consolidate duplicate safe pump helpers; canonicalize on `test/helpers/safe_pump.dart`."

Applying the above edits will make the plan consistent with the current codebase and avoid implementation surprises.

## Recommended Verification Level and effort estimate
- Recommended Verification Level: 2 (targeted verification)
  - Rationale: Keep to the plan's original recommendation — run focused widget tests for `plan_templates_orchestrator_test.dart` and associated helper tests.
- Effort estimate: Low-to-Medium
  - If tests are adapted to the current widget-listener redirect: Low-to-Medium.
  - If the repo is refactored to use async router redirects prior to test changes: Medium-to-High (refactor + tests).

## Risk / Impact analysis and blockers
- Risks:
  - Test flakiness if DI (GetIt) is not reset properly between tests.
  - Unclear redirect decision could cause wasted work (writing tests for one pattern then refactoring code).
- Blockers:
  - None immediate for Phase 1 analysis.
  - Decision required (redirect pattern) before Phase 2 implementation begins.
- Mitigations:
  - Update the plan with an explicit decision about redirect pattern; proceed with tests targeting current behavior if no refactor is desired.

## Action items taken in this protocol
1. Read and validated all files listed in the plan's Scope of Work.
2. Collected evidence and produced this protocol file with recommendations and required exact plan edits.

## Conclusion / Recommendation
- Recommendation: Update the high-level plan to explicitly state which redirect pattern to target (widget-level `BlocListener` vs router-level async redirect). Then proceed to Phase 2 (detailed implementation) with Verification Level 2, adapting tests to the actual chosen redirect approach and enforcing DI reset and `whenListen` usage in each test attempt protocol.
- Proceed to Phase 2 (detailed implementation) after the plan update if you accept adapting tests to the current implementation; otherwise, add a small refactor step in the plan before Phase 2.

End of validation protocol.