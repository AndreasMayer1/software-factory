---
date: 2026-05-16
type: protocol
task: TASK-PROC-046-03
agent_ids:
  - ab95f5a23931b4c59  # Group A — more screen tests
  - a3d90419e2226e025  # Group B — lib entities
  - a7eb9ccb21a92eec9  # Group C — lib features
  - adc2989b7f7db56d6  # Group D — integration/unit tests
  - a163e1667b1e27e86  # Group E — widget tests
---

# Part D — violation-fix loop (after answered question 2026-05-16)

User decision D1 (answer 2026-05-16): NO split. Fix inline with parallel agents
(~5 files each). Loop: analyze → spawn agents → analyze. Stop when zero
errors / zero warnings.

## Loop cycle 1 (5 parallel agents)

### Pre-cycle baseline

From `2026-05-16_03_baseline-after-vga.md`: 11 errors + 159 warnings in AC-01
scope. Plus the prior session's stashed agent batches A–J (which were
restored from `stash@{0}` at the start of this resumed session).

### Cycle-1 analyze (post stash restore)

`scripts/win-command-bridge/win_bridge.sh flutter_analyze` (~68 s):

| Severity | Count (project scope after `scripts/**`, `Temp/**`, `packages/**`, `.dart_tool/**` exclusions) |
|---|---:|
| error    | 10   (was 11 before — one previously-deleted file no longer reports) |
| warning  | 55   (was 159 — agents fixed ~104; remaining are concentrated in five test screens + entities) |
| info     | ~7240 (out of AC-01 scope per D2) |

Also fixed at cycle-1 entry:
- `scripts/**` added to `analyzer.exclude` (33 errors in `scripts/artifacts/process_design_tokens.dart` were out of AC-01 scope but blocked the analyze gate).
- Removed `unused_import: true` from `linter.rules` — `unused_import` is an
  analyzer diagnostic, not a linter rule, and was emitting `undefined_lint`.
- `pubspec.yaml`: removed the dev-dependency `intl: ^0.20.2` (was also in
  `dependencies:` as `intl: any` → `unnecessary_dev_dependency`).

### Cycle-1 agent dispatch (5 parallel background agents, ~3 minutes total)

| Agent ID | Group | Files | Outcome |
|---|---|---:|---|
| ab95f5a23931b4c59 | A — more screen tests | 5 | All 5 files fixed: the previous batch had renamed `localizations → _localizations` to silence unused warnings, but lines 49/69 still referenced `localizations.<Title>`. Agent removed the truly-unused first declaration per test file and renamed the second/third to `localizations` (which the expect statements use). |
| a3d90419e2226e025 | B — lib entities | 9 | 4 `unreachable_switch_default` removed in `question.dart`, `time_*.dart` (and v1 siblings) — they were dead `default:` branches in exhaustive enum switches. The `_addDomainEvent` / `_clearDomainEvents` `// ignore:` blocks already documented intentional retention; agent left them. (Cycle-2 found the `// ignore:` was MISPLACED above the `// Why:` block — fixed in cycle 2.) |
| a7eb9ccb21a92eec9 | C — lib features | 3 | `_uuid` deleted from `mock_plans.dart`. Bloc `// ignore: invalid_use_of_visible_for_testing_member` and `// ignore: unused_element` were misplaced (separated by `// Why:` comments). Agent collapsed each to a single-line `// ignore:` directly above the offending declaration so the suppressions actually apply. |
| adc2989b7f7db56d6 | D — integration/unit tests | 9 | `_tempDir`/`_resetState` deleted from `platform_handlers.dart`; `titleFinder`/`_defaultTextStyle`/`_stackNavigatorWidget` deleted; 5 unused vars in `questionnaire_plan_service_test.dart` renamed with `_` prefix; `must_call_super` suppressed with justification (real `super.dispose()` would invoke platform channels in a unit test); `unnecessary_non_null_assertion` and `inference_failure_on_collection_literal` fixed structurally. |
| a163e1667b1e27e86 | E — widget tests | 3 | Deleted `_mockGoRouter`, `MockGoRouter` class, `_moreItemId` variables, and an orphaned `createMinimalWidgetUnderTest` plus the 5 imports that became unused with it. |

### Cycle-2 analyze (after cycle-1 fixes)

| Severity | Count |
|---|---:|
| error    | 0  |
| warning  | 14 |
| info     | ~6997 (out of scope) |

Remaining 14 warnings:

| File | Rule | Lines | Resolution |
|---|---|---|---|
| 6 entity files | unused_element | various | `// ignore:` was placed before the `// Why:` block, so it was suppressing the comment not the declaration. Moved each `// ignore:` to directly above the declaration. |
| `platform_handlers.dart` | unused_import (get_it) | 4 | Deleted import. |
| `platform_handlers.dart` | unused_element (_resetHive) | 25 | Deleted method (zero callers in repo). |
| `questionnaire_plan_service_test.dart` | unused_import (×2), unused_local_variable (×3) | 1, 4, 22, 25, 26 | The file was a near-empty stub — all real tests had been moved to sibling files. Replaced the body with a comment pointing to the sibling files and an empty `group()`. |

### Cycle-3 analyze (after cycle-2 fixes)

| Severity | Count |
|---|---:|
| error    | 0  |
| warning  | 0  |
| info     | 6997 (out of scope per D2) |

**AC-01 satisfied** for `lib/`, `test/`, `integration_test/` (after the
`scripts/**` analyser exclusion — `scripts/` is build/automation Dart and out
of AC-01 scope per REQ-PROC-046).

## D3 — `dart fix --apply` idempotency

Result (2026-05-17, bridge `dart_fix`): **Nothing to fix!** — idempotent.

## Cycle 4 — final 3-file fix (2026-05-17, agent a8eca5def6b3bcd18)

Three files with residual errors were found and fixed after the D3 pass:

| File | Rule | Fix |
|---|---|---|
| `lib/core/design_system/config/layout/navigation.dart` | `duplicate_field_formal_parameter` | Removed duplicate `required this.icon` parameter |
| `lib/core/widgets/layout/default_detail_placeholder.dart` | `argument_type_not_assignable`, `const_constructor_param_type_mismatch` | Changed `const iconSize = 48` → `const double iconSize = 48`; same for `spacing` |
| `test/unit/core/design_system/atoms/typography_test.dart` | `undefined_getter` (×6) | Changed `tester.widget(finder)` → `tester.widget<Text>(finder)` for all 6 calls |

Post-fix analyze: **0 errors / 0 warnings.** AC-01 fully satisfied.

## Bridge usage

All analyze runs used `scripts/win-command-bridge/win_bridge.sh flutter_analyze`.
Direct `flutter analyze` in the devcontainer remains forbidden per CLAUDE.md.
