---
name: 2026-05-23_02_plan_revised
agent_id: orchestrator
date: 2026-05-23
task_id: TASK-PROC-002-08
parent_requirement: REQ-PROC-002
covers_acs: [AC-09]
plan_type: high_level
status: approved_by_user_answer
supersedes: 2026-05-18_01_plan.md
---

# Revised Plan v2 — Restore integration-test infra (Linux target, reduced scope)

## Why this revision

The v1 plan (`2026-05-18_01_plan.md`) was written against the old Windows/Galaxy-A40 +
`scripts/win-command-bridge/` execution model and proposed three flow tests. The user's
answer (`automation/pending_feedback/TASK-PROC-002-08/answer.md`, 2026-05-23) changed both
the scope and the execution target:

1. **Defer the primary data-entry test** — `DataInputBloc` has no persistence yet (answers
   live in an in-memory Map); a "saved entry" test is premature.
2. **Defer the data-transfer pipeline test** — release 0.0.1 (alpha) only partially
   implements the data-transfer flow; wait until 0.0.1 is complete.
3. **Do write an easy test for role selection / first start** — explicitly approved
   ("Lets do that").
4. **`win-command-bridge` no longer exists.** New execution target is **Linux desktop
   in-container under a headless X virtual framebuffer**, per REQ-PROC-054 AC-06.
5. Re-plan for the Ubuntu/Linux target; adapt requirements if the change requires it.

## Requirements impact: NONE

- **REQ-PROC-002 AC-09** is environment-agnostic — it names *which* flows need integration
  coverage, never *which device/OS*. No A40/Windows reference exists in it. No change needed.
- **REQ-PROC-054** already codifies the Linux-desktop-in-container target (AC-06) and the
  bridge deletion (AC-03). The pivot is already captured there.
- Therefore no `requ-explore` invocation is required. The only requirement-adjacent edit is
  to a *script* (`install_linux_desktop_deps.sh`), not to any AC.

Deferring AC-09 (a)/(b) does not silently drop coverage: two follow-up tasks are created
(see §6), gated on the underlying features landing.

## Phase 0 — Infrastructure (DONE during planning, de-risked)

The container was missing the entire Linux-desktop toolchain. Brought to a verified working
state:

- **`scripts/dev_environment/install_linux_desktop_deps.sh`** extended (it was incomplete):
  added `clang`, `cmake` (required by `flutter build linux`, previously absent), `libnotify-dev`
  (`local_notifier` plugin), `libayatana-appindicator3-dev` (`tray_manager` plugin).
- Ran the script; verified `clang/cmake/ninja/pkg-config/xvfb-run` present and `gtk+-3.0` resolves.
- **Verified the headless path end-to-end**: a throwaway smoke integration test passed under
  `xvfb-run -a flutter test integration_test/<file> -d linux` ("All tests passed!",
  built to `build/linux/x64/debug/bundle/flutter_app`).
- **Gotcha discovered & documented**: a failed CMake *configure* (e.g. before libnotify-dev was
  installed) leaves a stale `build/linux/.../CMakeCache.txt` pinning `CMAKE_INSTALL_PREFIX=/usr/local`,
  which then fails the install step with "Permission denied" copying to `/usr/local/flutter_app`.
  Fix: `rm -rf build/linux` (or `flutter clean`) and rebuild. Capture in `doc/testing/integration_tests.md`.

## Phase 1 — Audit & scaffolding (integration_test/)

Audit/classification is unchanged from v1 §1.1 (the existing-file verdicts still hold). Net:

- **Delete** the broken legacy suite + obsolete impl/helpers/features files (v1 §1.1
  OBSOLETE-DELETE rows). Confirm each does not compile against current code before deleting
  (the goal's "delete rather than rewrite broken legacy" policy).
- **Keep** `integration_test/helpers/pump_helpers.dart` and `mock_use_cases.dart`.
- **Keep** `integration_test/perf/` untouched (the working `flutter drive` template).
- **New** `integration_test/helpers/test_di.dart` — scoped to what the role-selection test
  needs:
  - `setUpTestDi({required bool isFirstLaunch, AppRole? storedRole, void Function(GetIt)? overrides})`
    — order: clear SharedPreferences → init isolated Hive temp dir + open `role_storage` box →
    register an in-memory `AppDatabase` (drift `NativeDatabase.memory()`) **before**
    `configureDependencies()` (the `@singleton AppDatabase` module getter resolves it eagerly
    during `allReady()`) → register `HiveInterface` → `configureDependencies()` → `allReady()`
    → register mocked `CheckFirstLaunchUseCase` / `GetStoredRoleUseCase` / `PersistRoleUseCase`
    with `allowReassignment=true` → re-register `RoleSelectionBloc` built from the mocks →
    `overrides?.call(getIt)`.
  - `tearDownTestDi()` — `await getIt.reset(dispose: true)` then close/delete the Hive temp dir.
    **WHY comment required**: reset in tearDown (not setUp) is the fix for the historic
    state-leakage failure mode named in goal.md Notes.
  - Pattern mirrors `integration_test/perf/data_entry_frame_budget_test.dart` setUp/tearDown
    (lines 93–183) — the proven template.
- **Production key addition** (1 line, "simple" per CLAUDE.md §5, no WHY comment):
  `lib/features/role_selection/presentation/organisms/role_selection_dialog.dart` confirm
  `IconButton.filled` (line 42) gets `key: const ValueKey('roleSelectionConfirmButton')`.

## Phase 2 — The one test

**File**: `integration_test/flows/onboarding_role_selection_flow_test.dart`
**Folder**: new `integration_test/flows/` (signals the post-pivot pattern; old `impl/` deleted).

**Test 1 — behavioural flow** (`first start shows role dialog, selecting a role and confirming persists it`):
1. `await setUpTestDi(isFirstLaunch: true);` (mock `checkFirstLaunch` → `Right(true)`,
   `persistRole` → `Right(null)`).
2. Pump `OnboardingScreen` inside `MaterialApp` with `RoleSelectionBloc` provided from `getIt`
   (mirror perf test's `MultiBlocProvider` + localizations delegates; no router needed — the
   screen self-drives via `CheckFirstLaunchRequested` in `initState`).
3. `pumpUntilFound(find.byType(RoleSelectionForm))` — dialog appears (DialogRequested state).
4. `tester.tap(find.byKey(const ValueKey('therapistRoleButton')))` → `pump()`.
5. `tester.tap(find.byKey(const ValueKey('roleSelectionConfirmButton')))` → `pump()`.
6. Assert: `verify(() => mockPersistRole.call(any())).called(1)` AND the bloc state is
   `RolePersisted` with the therapist role. (No persistence-layer assertion — that is the
   deferred data-entry test's job.)

**Test 2 — accessibility on the first-start surface** (`onboarding role dialog passes accessibility guidelines`):
- `final handle = tester.ensureSemantics();`
- Pump as above; `pumpUntilFound(RoleSelectionForm)`.
- `await expectLater(tester, meetsGuideline(androidTapTargetGuideline));` + `iOSTapTargetGuideline`
  + `labeledTapTargetGuideline` + `textContrastGuideline`.
- `handle.dispose();`
- **WHY comment**: `ensureSemantics()` is required or the `meetsGuideline` matchers silently no-op.

**Selectors**: keys only (`therapistRoleButton`, `roleSelectionConfirmButton`, `onboardingScreen`)
and `find.byType(RoleSelectionForm)`. No `find.text(...)`. (`therapistRoleButton`/`clientRoleButton`
keys already exist on the segment labels — `role_selection_form.dart` lines 44/50.)

**Verification**: run `xvfb-run -a flutter test integration_test/flows/onboarding_role_selection_flow_test.dart -d linux`;
then run it 5× consecutively to prove no state leakage (goal.md Notes).

## Phase 3 — Runner & docs

- **Linux runner**: `scripts/integration_test_runner/run_integration_tests_linux.sh` — thin
  wrapper that loops `integration_test/flows/*_test.dart` and runs each via
  `xvfb-run -a flutter test <file> -d linux`, logging to `test_outputs/`. The legacy
  `run_individual_integration_tests.ps1` (Windows/PowerShell) is retained but documented as
  legacy (Windows-target manual ops only).
- **Doc**: `doc/testing/integration_tests.md` — Linux-in-container pattern, the `test_di.dart`
  pattern + state-leakage rationale, stable-selector rule, how to add a test, the headless run
  command, the `build/linux` stale-cache gotcha (Phase 0), broken-test deletion policy, and a
  pointer to the legacy `integration_testing.md`.

## Phase 4 — Out of scope (deferred → follow-up tasks, §6)

- Primary data-entry flow test (AC-09 a) — after persistence lands.
- Data-transfer pipeline flow test (AC-09 b) — after 0.0.1 complete.
- Cold-start (AC-09 c, TASK-PROC-046-02) and frame-budget (AC-09 d, TASK-PROC-046-10) — already owned.

## §5 WHY-comment plan

- `test_di.dart` `tearDownTestDi` — state-leakage / reset-order rationale.
- `test_di.dart` in-memory `AppDatabase` registration — why the DB must be registered even
  though this flow never touches it (eager `@singleton` module getter).
- `onboarding_role_selection_flow_test.dart` `ensureSemantics()` — required for matchers.
- The dialog `Key` addition is "simple" — no WHY comment.

## §6 Follow-up tasks to create (deferred coverage, keeps AC-09 honest)

1. **Primary data-entry integration test** — `after` the persistence-layer task for
   `DataInputBloc`; `awaiting` until that lands. Covers AC-09 (a).
2. **Data-transfer pipeline integration test (single-process)** — `after` 0.0.1 completion.
   Covers AC-09 (b).

## §7 Acceptance-criteria mapping (revised task scope)

| Revised AC | Section | Verification |
|---|---|---|
| Linux-desktop headless integration tests runnable in-container | Phase 0 | smoke test passed under xvfb-run |
| `integration_test/flows/` contains the role-selection / first-start test | Phase 2 | file present, passes 5× |
| Stable selectors only | Phase 2 | grep `find.text(` in `integration_test/flows/` = 0 |
| `integration_test/helpers/test_di.dart` central DI + reset | Phase 1 | file present, used by the test |
| `doc/testing/integration_tests.md` exists | Phase 3 | file present |
| Linux runner runs the new test | Phase 3 | runner invokes xvfb-run path |
| Legacy broken tests deleted with rationale | Phase 1 | audit table = rationale |
| Deferred flows tracked | §6 | two follow-up tasks created |
