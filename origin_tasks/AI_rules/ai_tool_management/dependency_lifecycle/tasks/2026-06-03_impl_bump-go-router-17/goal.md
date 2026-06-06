---
task_id: TASK-PROC-061-15
type: impl
parent_requirement: REQ-PROC-061
urgency: 3
urgency_reason: U3-MAINTENANCE
impact: 3
impact_reason: I3-MAINT
status: pending
effort: S
created: 2026-06-03
after: [TASK-PROC-061-07]
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Bump go_router 16.2.4→17.2.3; audit shell-route observer behavior change"
release_description: ""
opus_recommended: false
---
# Goal: Bump go_router 16.2.4 → 17.2.3

## Objective

Apply the approved major-version bump: `go_router` from `16.2.4` to `17.2.3`.

## Background

Decision rationale: `plans_and_protocols/2026-06-03_01_decisions.md` in TASK-PROC-061-07.

## Breaking Changes Confirmed (from TASK-PROC-061-07 investigation)

**go_router 17.0.0 — observer notification behavioral change:**
- Shell routes now notify `GoRouter`'s root observers by default (previously they did not). A `notifyRootObserver` parameter was added to `StatefulShellRoute`, `ShellRoute`, and related classes to opt out.

**Impact on this project:**
- `lib/config/routes/app_router.dart`: `GoRouter(...)` has no `observers:` parameter. No `NavigatorObserver`s are registered.
- Grep for `NavigatorObserver` and `observers:` in `lib/`: **zero hits**.
- The behavioral change has no impact — there are no observers to be notified.

**No other breaking changes** to `GoRoute`, `StatefulShellRoute.indexedStack`, `StatefulShellBranch`, `RouteBase`, `state.matchedLocation`, `state.extra`, redirect callback signatures, or `GoRouterRefreshStream`.

## Steps

1. Update `pubspec.yaml`: `go_router: ^16.2.4` → `go_router: ^17.2.3`
2. Run `flutter pub get` and verify solver resolves without conflicts
3. Run `dart analyze` — expect zero new errors (no API changes)
4. Run `flutter test` — expect zero new failures
5. Verify quality gates (via `verify-quality` skill)

## Acceptance Criteria

- [ ] `go_router` bumped to `^17.2.3` in `pubspec.yaml` and resolved in `pubspec.lock`
- [ ] `flutter pub get` resolves cleanly
- [ ] `dart analyze` reports no new issues
- [ ] All existing tests pass
- [ ] Quality gates green
