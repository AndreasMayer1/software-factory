---
task_id: TASK-PROC-061-05
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-02
completed: 2026-06-03
session_completed_at: 2026-06-03T11:01:33Z
effort: S
created: 2026-06-02
expected_tool_calls: 25
skill_chain_depth: 2
after: []
covers:
  acceptance_criteria: [AC-06, AC-08]
  sections: []
scope_description: "Apply the 16 patch/minor dependency bumps from the 2026-06 monthly review that passed all DG1–DG4 gates"
release_description: "Updates 16 patch/minor Flutter dependencies to their latest stable versions."
opus_recommended: false
requirements_version:
  commit: 3cbd51ab
  file: ../requirements.md
session_id: 8abc0468-6dde-42c3-ba57-965540765938
session_account: gmail
---
# Goal: Apply 2026-06 Autonomous Dependency Bumps

## Objective

Apply the 16 patch/minor version bumps identified in the June 2026 monthly dependency review. All 16 packages have passed the DG1–DG4 intake gates (REQ-PROC-056). No human pre-authorization is required (REQ-PROC-061 AC-06). After bumping, run `flutter pub get`, `dart fix --apply`, and the full quality gates to satisfy the regression-confirmation contract (AC-08a).

## Requirements Summary

REQ-PROC-061 AC-06 authorises autonomous patch/minor bumps when DG1–DG4 pass and quality gates pass after the update. AC-08a defines the regression-confirmation contract for this change class: existing quality gates (G1–G8, TQ1–TQ4, SP1–SP6) are sufficient — no additional testing required.

For complete requirements at task creation time:
```
git show 3cbd51ab:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Edit `pubspec.yaml` to apply the 16 version bumps listed below
- Run `flutter pub get` to resolve the new lockfile
- Run `dart fix --apply`
- Run `verify-quality` to confirm all gates pass
- Record the DG1–DG4 evidence reference in `plans_and_protocols/` (source: `automation/dependency_reviews/2026-06/proposal.md`)

### Out of Scope
- Major-version bumps (`get_it`, `injectable`, `go_router`, `camera`) — require separate human-authorised tasks
- `sqlite3_flutter_libs` EOL assessment — separate intake task
- Python `ruff` and `image` dev dep — deferred (DG1 not yet met at review time)
- `bloc_lint` — pinned intentionally (analyzer conflict documented in proposal)

## Packages to Bump

| Package | pubspec.yaml section | Current | Target |
|---|---|---|---|
| equatable | dependencies | 2.0.7 | 2.0.8 |
| shared_preferences | dependencies | 2.5.3 | 2.5.5 |
| uuid | dependencies | 4.5.1 | 4.5.3 |
| meta | dependencies | 1.17.0 | 1.18.2 |
| flutter_svg | dependencies | 2.2.1 | 2.3.0 |
| wakelock_plus | dependencies | 1.4.0 | 1.6.1 |
| logger | dependencies | 2.6.2 | 2.7.0 |
| bloc | dependencies | 9.0.1 | 9.2.1 |
| drift | dependencies | 2.31.0 | 2.33.0 |
| drift_dev | dev_dependencies | 2.31.0 | 2.33.0 |
| mocktail | dev_dependencies | 1.0.4 | 1.0.5 |
| mockito | dev_dependencies | 5.6.3 | 5.7.0 |
| freezed | dev_dependencies | 3.2.3 | 3.2.5 |
| json_serializable | dev_dependencies | 6.11.2 | 6.14.0 |
| build_runner | dev_dependencies | 2.12.2 | 2.15.0 |
| camera_platform_interface | dev_dependencies | 2.12.0 | 2.13.0 |

Note: `drift` and `drift_dev` must be bumped together (constrained `^2.22.0`; both must resolve to 2.33.0).

## Evidence Reference

DG1–DG4 evaluation is documented in `automation/dependency_reviews/2026-06/proposal.md` (committed `16a86d94`). No additional gate evaluation is needed — the proposal already records pass evidence for all 16 packages.

## Acceptance Criteria

- [~] **AC-1 — PARTIALLY MET.** 9 of 16 packages reached their documented target
  (equatable, shared_preferences, uuid, flutter_svg, logger, bloc, mocktail,
  build_runner, camera_platform_interface). 2 reached a lower bump than target
  (mockito 5.6.3→5.6.4, target 5.7.0; wakelock_plus 1.4.0→1.5.2, target 1.6.1).
  The remaining 7 documented targets are **not solver-reachable** in this
  devcontainer and are **deferred** per the developer's Option-A decision
  (2026-06-03, recorded in `plans_and_protocols/2026-06-03_feedback-checkpoint.md`).
  Each deferral mapped to its real blocker:
  - drift 2.33.0, drift_dev 2.33.0, freezed 3.2.5, json_serializable 6.14.0,
    mockito 5.7.0 — **analyzer ceiling** (`clean_architecture_kit ^2.0.1` /
    `bloc_lint ^0.3.7` pin `analyzer 8.4.0` / `_fe_analyzer_shared 91`; targets
    need analyzer > 8.4.0). → follow-up: re-evaluate the analyzer ceiling.
  - meta 1.18.2 — **Flutter SDK pin** (Flutter 3.41.4 pins `meta 1.17.0`). →
    follow-up: fold into the next Flutter-SDK-bump task.
  - wakelock_plus 1.6.1 — **plugin graph** (`1.6.1` needs `win32 >=6` and
    `package_info_plus >=10.1`, both capped by other plugins). → follow-up:
    coordinated win32 / package_info_plus bump.
  Rationale: the source proposal ran in a cloud container with no Flutter SDK,
  so its "target" column was the pub.dev `Latest`, not solver-`Resolvable`.
- [x] `flutter pub get` exits 0 with the new versions resolved (via targeted
  `flutter pub upgrade`; constraints in `pubspec.yaml` are `any`, so pins live
  in `pubspec.lock`)
- [x] `dart fix --apply` run; the `comment_references` fixer introduced 5
  `ambiguous_import` regressions, which were reverted to keep the change
  regression-free (only `pubspec.lock` retained)
- [x] All quality gates pass (`verify-quality` — G1 analyze GREEN, G3 tests
  GREEN, all SP/complexity/arch gates GREEN)
- [x] Evidence reference recorded in `plans_and_protocols/`
  (`2026-06-02_01_protocol_apply-bumps.md`)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
