---
proposal_id: arch-imports-allow-material-in-domain-services
proposal_type: grep_gates
proposed_at: 2026-05-24
proposed_by_model: claude-sonnet-4-6
source_task: TASK-NFUNC-002-02
status: pending_review
---

## Reason

`check_architectural_imports.sh` flags all `package:flutter/{material,widgets}.dart`
imports under `lib/core/domain/`. Three files have genuine Flutter-type
dependencies that cannot be trivially removed:

1. `lib/core/domain/entities/action_item.dart` — uses `IconData` and
   `VoidCallback`. These are navigation-action descriptors that carry UI
   metadata (icon reference) alongside routing data. Separating them would
   require a parallel domain type and a mapping layer.

2. `lib/core/domain/entities/questionnaire_plan_entities/time_interval.dart`
   and its v1 counterpart — use `TimeOfDay` to represent a time-of-day
   field in a questionnaire plan. `TimeOfDay` is structurally a value object
   (hour + minute pair) but lives in Flutter's material library.

3. `lib/core/domain/services/screen_size/i_screen_size_service.dart` and
   `screen_size_service_impl.dart` — the screen-size service takes a
   `BuildContext` parameter because its purpose is to read `MediaQuery`.
   It was placed in domain to allow DI injection, but its contract is
   inherently presentation-aware.

The 8 `flutter/foundation.dart` violations (for `@immutable`) have already
been fixed by TASK-NFUNC-002-02 (replaced with `package:meta/meta.dart`).

## Proposed change

**Option A (preferred):** Create domain-level value types to replace the
Flutter dependencies, then update `action_item.dart` and `time_interval.dart`:

- Replace `IconData` with `String iconKey` (resolved to `IconData` in the
  presentation layer via a registry).
- Replace `TimeOfDay` with a `TimeValue` value object (`hour`, `minute`
  ints) in `lib/core/domain/entities/`.
- Move `IScreenSizeService` / `ScreenSizeService` from
  `lib/core/domain/services/screen_size/` to
  `lib/core/presentation/services/screen_size/` (it is presentation-layer
  by nature).

**Option B (gate relaxation only):** Exclude the three specific files from
the architectural import check via the exclusions mechanism:
```
# scripts/quality/architectural_imports_exclusions.txt
lib/core/domain/entities/action_item.dart
lib/core/domain/entities/questionnaire_plan_entities/time_interval.dart
lib/core/domain/entities/questionnaire_plan_entities/v1/time_interval.dart
lib/core/domain/services/screen_size/i_screen_size_service.dart
lib/core/domain/services/screen_size/screen_size_service_impl.dart
```

## Expected effects

- 5 remaining arch-import violations removed (the 8 `foundation.dart` ones
  are already fixed).
- Option A: cleaner domain model, more migration work (~1 person-day).
- Option B: gates pass immediately, technical debt documented here.

## Alternatives considered

1. **Ignore all arch-import violations** — rejected. The gate correctly
   catches new violations; these 5 are pre-existing and should be addressed,
   not silenced globally.
2. **Move all domain files with Flutter imports to presentation layer** —
   partially correct for `IScreenSizeService` but wrong for `ActionItem`
   and `TimeInterval`, which represent pure data.
