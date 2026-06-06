# Protocol: lib/ Requirements Backfill Scan

**Task**: TASK-PROC-030-01-03
**Date**: 2026-04-09
**Status**: AWAITING USER REVIEW

---

## 1. Scan Method

- Listed all directories under `lib/` recursively
- Enumerated Dart files per feature area
- Checked each feature against `requirements_tasks/functional/` and `requirements_tasks/non-functional/` via:
  - Folder-walk of requirement hierarchy
  - Keyword grep for domain terms
- Read key implementation files to assess stability (stub vs. real)

---

## 2. Feature-to-Requirement Coverage Map

### COVERED — no action needed

| lib/ Area | Covering Requirement(s) |
|-----------|------------------------|
| `config/routes/` | REQ-NFUNC-011 (main_navigation), REQ-NFUNC-014 (responsive_layout_master_detail) |
| `config/theme/` | non-functional/ui_ux_design_system/theming/growth_tree_theme |
| `core/data/database/` (Drift) | REQ-NFUNC-016 (local_database_technology) |
| `core/domain/entities/questionnaire_plan_entities/` | REQ-FUNC-007-05 (client_data_model) |
| `core/domain/entities/contact.dart` + repositories | REQ-FUNC-007-06 (feat_pairing_management) |
| `core/domain/services/questionnaire_plan/` | functional/therapist/epic_plan_management features |
| `core/services/logging/` | non-functional/architecture/logging |
| `core/design_system/organisms/layout/` | REQ-NFUNC-014 (responsive_layout_master_detail) |
| `features/role_selection/` | REQ-FUNC-011-01 (feat_role_selection) — status: placeholder |
| `features/client/data_input/` | functional/client/epic_data_input features |
| `features/client/data_receive/` | REQ-FUNC-007-02 (feat_plan_receiving), REQ-FUNC-007-12 (feat_qr_data_transfer) |
| `features/therapist/plan_templates/` | functional/therapist/epic_plan_management features |
| `features/therapist/data_transfer/` | REQ-FUNC-007-12, REQ-FUNC-007-04, feat_therapist_transfer_ui |
| `features/therapist/data_receive/` | REQ-FUNC-007-12 (reverse scan direction) |
| `features/therapist/clients/` | functional/therapist/epic_client_management |
| `features/more/privacy_policy, terms_of_service, open_source_licenses` | REQ-FUNC-020 (feat_legal_notices) |
| `core/data/repositories/drift_questionnaire_plan_repository.dart` | REQ-FUNC-007-08 (feat_storage_management) |
| `features/therapist/data_transfer/data/services/plan_serialization_service.dart` | REQ-FUNC-007-03 (feat_plan_serialization) |
| Design system specific components (skeleton, toast, etc.) | dedicated requirements in ui_ux_design_system/components/ |

### STUB / NOT STABLE — excluded from backfill

| lib/ Area | Reason |
|-----------|--------|
| `features/home/home_screen.dart` | Stub: shows title + role name only |
| `features/therapist/inbox/` | Explicit `Placeholder` widget; "Full implementation in Phase 3" comment |
| `features/more/appearance_settings_screen.dart` | Stub body: only shows title text |
| `features/more/notification_preferences_screen.dart` | Stub body: only shows title text |
| `features/more/about_screen.dart` | Stub body: only shows title text |
| `features/client/data_send/` (`ClientSendScreen`, `SpikePayloadService`) | Debug/spike screen only; accessible via `/debug/client-send`, not app navigation |

---

## 3. Gap Candidates

### CANDIDATE A: "More" Tab Navigation Structure

**Files**:
- `lib/features/more/presentation/screens/more_root_screen.dart`
- `lib/features/more/presentation/widgets/more_master_view.dart`
- `lib/features/more/presentation/layout/more_layout_config.dart`
- `lib/core/domain/entities/action_group.dart`, `action_item.dart`, `action_type.dart`

**What's implemented**: Role-aware master-detail navigation container. `MoreLayoutConfig` builds role-specific `ActionGroup` lists. `MoreMasterView` renders them via `GroupedActionList`. `MoreRootScreen` wires the responsive layout, routes to sub-screens by `moreItemId` path param, and handles the case where no detail item is selected.

**Coverage gap**: No requirement in functional/shared or functional/client covers the "More" tab's navigation structure, role-specific grouping, or the `ActionGroup`/`ActionItem` domain entities.

**Stability assessment**: STABLE — this is real, non-trivial navigation infrastructure used as container for legal, appearance, notification, and future sub-screens.

**Suggested requirement location**: `requirements_tasks/functional/shared/feat_more_navigation/`

---

### CANDIDATE B: Hive Key-Value Preferences Storage

**Files**:
- `lib/core/data/storage/storage_initializer.dart`
- `lib/core/data/repositories/local_role_repository.dart`
- `lib/core/data/adapters/app_role_adapter.dart`

**What's implemented**: Hive-based key-value store used for role persistence (`role_storage` box) and first-launch flag. Separate from Drift (which handles structured plan/contact data). `StorageInitializer` handles Hive initialization and adapter registration on all platforms.

**Coverage gap**: REQ-NFUNC-016 covers Drift/SQLite technology selection. No requirement addresses the two-tier storage strategy (Hive for preferences, Drift for structured data) or documents why Hive was chosen for the preferences layer.

**Stability assessment**: STABLE — this is core infrastructure used from app startup.

**Suggested requirement location**: Either extend REQ-NFUNC-016 (if user prefers grouping storage tech into one requirement) or create `requirements_tasks/non-functional/architecture/preferences_storage/`

---

### CANDIDATE C: Core Design System Foundation Components

**Files** (not individually documented):
- `lib/core/design_system/atoms/typography.dart`
- `lib/core/design_system/atoms/grid_layout.dart` + `grid_example.dart`
- `lib/core/design_system/atoms/inputs/likert_scale.dart`
- `lib/core/design_system/molecules/input_field.dart`
- `lib/core/design_system/molecules/form_row.dart`
- `lib/core/design_system/molecules/list_item.dart`
- `lib/core/design_system/molecules/radio_card.dart`
- `lib/core/design_system/molecules/action_item_button.dart`
- `lib/core/design_system/molecules/error_display.dart`
- `lib/core/design_system/organisms/grouped_action_list.dart`
- `lib/core/design_system/organisms/modal_dialog.dart`
- `lib/core/design_system/organisms/layout/base/` (AppBarConfig, CustomNavigationBar, StackNavigator, InheritedBackNavigator, etc.)

**What's implemented**: The foundational atoms/molecules/organisms used throughout the app. Individual components have no requirements, though many are referenced by higher-order requirements (e.g., `likert_scale` used in data_input, `grouped_action_list` used in More navigation, `AppBarConfig` used in navigation patterns).

**Coverage gap**: The design system's specific component components (excluding skeleton, toast, leaf_popout, context_help, time_range_selector, collapsible_form_section which have requirements) are implemented but not documented.

**Stability assessment**: STABLE — these are core primitives used across the entire codebase.

**Note**: This could be one grouped requirement ("Core Design System Foundation Components") rather than individual requirements per component, or it could be argued that these are pure implementation details below the requirements level.

**Suggested requirement location**: `requirements_tasks/non-functional/ui_ux_design_system/components/core_foundation/`

---

## 4. Excluded (Not a Gap)

- `ScreenSizeService` (`core/domain/services/screen_size/`) — implementation detail of navigation requirements; referenced in REQ-NFUNC-011 and REQ-NFUNC-014
- `AppRole` entity — covered by REQ-FUNC-011-01 (role selection)
- Domain failure types (`core/domain/failures/`) — implementation details, not standalone features
- `core/injection/` — DI setup, infrastructure artifact
- `core/error/` — error infrastructure
- Generated files (`lib/generated/`, `lib/l10n/`) — auto-generated

---

## 5. User Decisions

| Candidate | Decision | Notes |
|-----------|----------|-------|
| A: More Tab Navigation | ✅ APPROVED — create placeholder | Location: non-functional/ui_ux_design_system/navigation_patterns/overflow_more_navigation/ (REQ-NFUNC-019). Follow-up explore task: TASK-NFUNC-019-01 |
| B: Hive Preferences Storage | ✅ NO ACTION — already covered | REQ-NFUNC-016 already documents Hive as "temporary, pre-Drift usage" with AC-07 for migration path |
| C: Core Design System Foundation | ✅ APPROVED — epic-level only | Created REQ-NFUNC-018 at non-functional/ui_ux_design_system/requirements.md. Status: active. Component details remain in doc/presentation/coding/ only — no per-component requirements |

## 6. Created Artifacts

| Artifact | Path | ID |
|----------|------|----|
| REQ-NFUNC-019 placeholder | `navigation_patterns/overflow_more_navigation/requirements.md` | REQ-NFUNC-019 |
| REQ-NFUNC-018 epic | `non-functional/ui_ux_design_system/requirements.md` | REQ-NFUNC-018 |
| TASK-NFUNC-019-01 explore task | `overflow_more_navigation/tasks/2026-04-09_explore_overflow-more-navigation/goal.md` | TASK-NFUNC-019-01 |

## 7. Outcome

- All major feature areas in lib/ are mapped (covered or stub)
- 3 gaps found; 2 resulted in placeholder requirements (A, C); 1 already documented (B)
- ID registry regenerated; no stale markers remaining
- Status: COMPLETE
