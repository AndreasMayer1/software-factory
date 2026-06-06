---
task_id: TASK-PROC-061-14
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
scope_description: "Bump get_it 8.2.0→9.2.1 + injectable 2.5.1→3.0.0 + injectable_generator 2.9.0→3.0.2 in lockstep; re-run build_runner"
release_description: ""
opus_recommended: false
---
# Goal: Bump get_it + injectable + injectable_generator (Lockstep)

## Objective

Apply the approved major-version bumps for the DI stack in a single coordinated change:

| Package | From | To |
|---|---|---|
| `get_it` | 8.2.0 | 9.2.1 |
| `injectable` | 2.5.1 | 3.0.0 |
| `injectable_generator` | 2.9.0 | 3.0.2 |

These three packages must be bumped together. `injectable` 3.0 requires `get_it >=9.0.0`; `injectable_generator` 3.0 must match `injectable` 3.0.

## Background

Decision rationale: `plans_and_protocols/2026-06-03_01_decisions.md` in TASK-PROC-061-07.

## Breaking Changes Confirmed (from TASK-PROC-061-07 investigation)

**get_it 9.x:**
- `strictDisposalOrder` parameter removed from `reset()`, `resetScope()`, `popScope()`, `popScopesTill()`, `dropScope()`. Grep confirmed: **zero usages** in `lib/` and `test/`.
- `allReady()` now caches its Future. Behavioral change only; call sites unchanged.

**injectable 3.0 / injectable_generator 3.0:**
- `includeMicroPackages` and `usesNullSafety` options removed from `@InjectableInit`. Confirmed absent in `lib/core/injection/injection_container.dart`.
- All other annotations (`@injectable`, `@singleton`, `@lazySingleton`, `@module`, `@Named`, `@Environment`) are unchanged.

**No call-site changes needed.** The only required work after bumping pubspec.yaml constraints is re-running `build_runner` to regenerate `injection_container.config.dart`.

## Steps

1. Update `pubspec.yaml`:
   - `get_it: any` → `get_it: ^9.2.1` (or keep `any` if solver resolves correctly)
   - `injectable: any` → `injectable: ^3.0.0`
   - `injectable_generator: ^2.6.0` → `injectable_generator: ^3.0.2`
2. Run `flutter pub get` and verify solver resolves without conflicts
3. Run `flutter pub run build_runner build --delete-conflicting-outputs` to regenerate `injection_container.config.dart`
4. Run `dart analyze` — expect zero new errors
5. Run `flutter test` — expect zero new failures
6. Verify quality gates (via `verify-quality` skill)

## Acceptance Criteria

- [ ] `get_it`, `injectable`, `injectable_generator` all bumped to target versions in `pubspec.yaml` and `pubspec.lock`
- [ ] `flutter pub get` resolves cleanly with no dependency conflicts
- [ ] `build_runner` completes without errors; `injection_container.config.dart` regenerated
- [ ] `dart analyze` reports no new issues
- [ ] All existing tests pass (`flutter test`)
- [ ] Quality gates green
