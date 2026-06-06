# Screens Inventory — REQ-PROC-046 AC-07 Backfill Scope

Task: TASK-PROC-046-07
Date: 2026-05-15

## Summary

| Category | Count | Total effort |
|---|---|---|
| (a) Covered fully (`ensureSemantics()` + 4 `AccessibilityGuideline` checks) | **0** | — |
| (b) Test exists but no semantics guideline check | **17** | 6 × S + 10 × M + 1 × L ≈ 30 h |
| (c) No widget test at all | **0** | — |
| n/a (router target is `Placeholder` stub — no real UI yet) | **2** | excluded from backfill |
| **Total reachable screens** | **19** | (17 real + 2 placeholders) |

**Headline**: Zero screens currently satisfy AC-07. Every reachable screen needs new accessibility coverage. Most existing screen tests can be extended in-place by one `testWidgets` group (`ensureSemantics()` + 4 guideline checks + a `textScaleFactor: 2.0` no-overflow test + a `disableAnimations: true` test, per AC-07 sub-clauses (a)/(b)/(c)). The two camera/scanner screens are the only L-effort entries because guideline-passing semantics depend on dynamic camera state that must be mocked.

**Total backfill effort estimate**: ~30 person-hours (S ≈ 1 h, M ≈ 2 h, L ≈ 4 h per screen for new tests inside existing files), assuming the four sub-clauses of AC-07 are added as a single shared helper (e.g. `test/helpers/accessibility_test_helper.dart`) that each screen test invokes. Without that helper, double the estimate.

**Recommendation**: Break the backfill into two impl tasks:
1. **Setup task (S)** — Author the shared accessibility test helper that runs the four `AccessibilityGuideline` checks, the `textScaleFactor: 2.0` overflow check, and the `disableAnimations: true` check via a single call. This must land first; it defines the contract every screen test will call.
2. **Backfill task (L)** — Apply the helper to every screen test below (16 screens × extension + 2 screens × new file). Can be parallelised by feature area if needed but is mechanically uniform.

The shared helper avoids drift: AC-07 explicitly says the gate "tracks REQ-NFUNC-002's currently-active acceptance criteria", so the helper is the single point that must be updated when REQ-NFUNC-002 promotes a Phase-2 AC.

## Testability Blockers

| Blocker | Affected screens | Resolution |
|---|---|---|
| Two routes still resolve to `Placeholder(child: Text('Client Analysis Screen'))` and `Placeholder(child: Text('Client Inbox Screen'))` (see `app_router.dart:286, :296`). They are not real screens and cannot be meaningfully accessibility-tested. | `/client/analysis`, `/client/inbox` | Exclude from this backfill. Re-include when those routes get a real implementation. Track as a follow-up `awaiting:` link on the AC-07 closure task. |
| Camera-backed screens (`DataBeamScannerScreen`) bind to platform plugins; rendering them in widget tests requires plugin shims. The existing test file already does this (572 lines) but extending semantics coverage requires camera-state mocks for label/contrast tests on the live scanner overlay. | `DataBeamScannerScreen` | L effort. May require widening existing helpers in `test/widget/features/client/data_receive/`. |
| Master-detail screens (`TherapistClientsOrchestrator`, `PlanTemplatesOrchestrator`, `MoreRootScreen` in detail mode) require `MediaQuery` width + `IScreenSizeService` mocks to render the relevant layout. Existing tests already handle this but accessibility checks need to run for both master and detail variants. | All 4 master-detail screens | Add as M (not S) — two `testWidgets` per screen, one per layout variant. |
| Dead/orphaned screen files exist in `lib/` but are not reachable via `GoRouter` (see "Orphan files" below). | 4 files | Out of scope for AC-07 (AC-07 is per-route). Optional cleanup: delete or wire up. |

## Inventory

Legend: **A** = covered, **B** = test exists / no guideline checks, **C** = no test. `Effort` = effort to bring the screen to category A.

| # | Route | Backing widget | File | Existing test | Cat | Effort | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `/` | `OnboardingScreen` | `lib/features/role_selection/presentation/screens/onboarding_screen.dart` | `test/widget/features/role_selection/presentation/screens/onboarding_screen_test.dart` (116 L) | B | S | Static screen; existing test sets up role-selection bloc. Adding the 4 guidelines + textScale + disableAnimations is straightforward. |
| 2 | `/therapist/inbox` | `InboxScreen` | `lib/features/therapist/inbox/presentation/screens/inbox_screen.dart` | `test/widget/features/therapist/inbox/presentation/screens/inbox_screen_test.dart` (69 L) | B | S | Simple. |
| 3 | `/therapist/plans` (master) | `PlanTemplateList` + `PlanTemplatesOrchestrator` | `lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart`, `.../widgets/plan_templates_orchestrator.dart` | `test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`, `plan_list_test.dart.skip` | B | M | Master-detail; two layout variants. `plan_list_test.dart.skip` is currently disabled (rename and fix as part of backfill). |
| 4 | `/therapist/plans/:planId` (detail) | `PlanTemplateDetailContent` | `lib/features/therapist/plan_templates/presentation/organisms/plan_template_detail_content.dart` | `test/widget/features/therapist/plan_templates/presentation/organisms/plan_template_detail_content_test.dart` | B | M | Detail pane; needs BLoC mocks already in file. |
| 5 | `/therapist/clients` (master) | `TherapistClientsOrchestrator` | `lib/features/therapist/clients/presentation/widgets/therapist_clients_orchestrator.dart` | `test/widget/features/therapist/clients/clients_routes_test.dart` (uses the orchestrator), `client_list_test.dart` | B | M | Routes-level test already exercises orchestrator. Add accessibility checks to client list. |
| 6 | `/therapist/clients/:clientId` (detail master — plans list) | `ClientPlansView` | `lib/features/therapist/clients/presentation/organisms/client_plans_view.dart` | `test/widget/features/therapist/clients/presentation/organisms/client_plans_view_test.dart` | B | M | |
| 7 | `/therapist/clients/:clientId/plans/:planId` | `ClientPlanDetailView` | `lib/features/therapist/clients/presentation/organisms/client_plan_detail_view.dart` | `test/widget/features/therapist/clients/presentation/organisms/client_plan_detail_view_test.dart` | B | M | |
| 8 | `/more` | `MoreRootScreen` (master view) | `lib/features/more/presentation/screens/more_root_screen.dart` | `test/widget/features/more/presentation/screens/more_root_screen_test.dart` (149 L), `more_navigation_test.dart` | B | M | Master-detail; two layout variants. |
| 9 | `/more/about` | `AboutScreen` (rendered inside `MoreRootScreen` detail switch) | `lib/features/more/presentation/screens/about_screen.dart` | `test/widget/features/more/presentation/screens/about_screen_test.dart` (71 L) | B | S | Pure-content screen. |
| 10 | `/more/appearance` | `AppearanceSettingsScreen` | `.../appearance_settings_screen.dart` | `.../appearance_settings_screen_test.dart` (72 L) | B | M | Has interactive controls (theme selector). Tap-target check is meaningful. |
| 11 | `/more/notifications` | `NotificationPreferencesScreen` | `.../notification_preferences_screen.dart` | `.../notification_preferences_screen_test.dart` (71 L) | B | M | Has switches/toggles. |
| 12 | `/more/privacy` | `PrivacyPolicyScreen` | `.../privacy_policy_screen.dart` | `.../privacy_policy_screen_test.dart` (71 L) | B | S | Pure content. |
| 13 | `/more/terms` | `TermsOfServiceScreen` | `.../terms_of_service_screen.dart` | `.../terms_of_service_screen_test.dart` (71 L) | B | S | Pure content. |
| 14 | `/more/licenses` | `OpenSourceLicensesScreen` | `.../open_source_licenses_screen.dart` | `.../open_source_licenses_screen_test.dart` (50 L) | B | S | Pure content. |
| 15 | `/client/data-input` | `ClientDataInputRootScreen` | `lib/features/client/data_input/presentation/screens/client_data_input_root_screen.dart` | `.../client_data_input_root_screen_test.dart` (137 L) | B | M | Primary entry surface for client role; interactive. |
| 16 | `/client/analysis` | `Placeholder(Text('Client Analysis Screen'))` | (defined inline in `app_router.dart:286`) | — | n/a | — | **Excluded**: not a real screen yet. |
| 17 | `/client/inbox` | `Placeholder(Text('Client Inbox Screen'))` | (defined inline in `app_router.dart:296`) | — | n/a | — | **Excluded**: not a real screen yet. |
| 18 | `/client/receive/scan` | `DataBeamScannerScreen` | `lib/features/client/data_receive/presentation/screens/data_beam_scanner_screen.dart` | `.../data_beam_scanner_screen_test.dart` (572 L) | B | L | Camera-backed; needs plugin shims + state mocks for guidelines. |
| 19 | `/client/receive/scan/confirm` | `PlanReceiptConfirmScreen` | `.../plan_receipt_confirm_screen.dart` | `.../plan_receipt_confirm_screen_test.dart` (152 L) | B | M | Confirmation form; interactive. |

### Effort tally

- **S (≈1 h each)**: 6 screens — #1, #2, #9, #12, #13, #14 → 6 h
- **M (≈2 h each)**: 10 screens — #3, #4, #5, #6, #7, #8, #10, #11, #15, #19 → 20 h
- **L (≈4 h each)**: 1 screen — #18 (`DataBeamScannerScreen`) → 4 h
- **Total backfill ≈ 30 h** (plus ~2 h for the shared `assertScreenAccessibility(tester)` helper task)

### Routes that resolve to placeholders (excluded)

| Route | Notes |
|---|---|
| `/client/analysis` | Renders `Placeholder(child: Text('Client Analysis Screen'))` — track in a separate task once the real screen is implemented. |
| `/client/inbox` | Renders `Placeholder(child: Text('Client Inbox Screen'))` — same. |

### Orphan screen files (defined under `lib/.../presentation/screens/` but not reachable via `GoRouter`)

These are listed for completeness; they are **out of scope** for AC-07 because the AC scopes to "widget reachable via `GoRouter` route configuration or `MaterialApp.routes`". They should either be deleted or wired in.

| File | Status |
|---|---|
| `lib/features/home/presentation/screens/home_screen.dart` | Only self-references in `lib/`; no router hookup. Likely dead code. |
| `lib/features/therapist/clients/presentation/screens/therapist_client_detail_screen.dart` | Defined but router uses `TherapistClientsOrchestrator` instead. Dead. |
| `lib/features/therapist/inbox/presentation/screens/therapist_inbox_root_screen.dart` | Defined but router uses `InboxScreen` directly. Dead. |
| `lib/features/therapist/data_receive/presentation/screens/therapist_receive_screen.dart` | Has a 1169-line widget test but is not reachable from the router. The class self-references in its own file; orphaned from production routing. |

## Cross-Reference: `ensureSemantics()` usage in current tests

`grep -r "ensureSemantics" test/` finds exactly **one** file:

- `test/unit/features/role_selection/presentation/molecules/role_selection_form_test.dart` — uses `tester.ensureSemantics()` to inspect a single widget's label/hint via `tester.getSemantics(...)`. **Does not** run any of the four `AccessibilityGuideline` checks (`expectLater(tester, meetsGuideline(...))`).

`grep -r "androidTapTargetGuideline\|iOSTapTargetGuideline\|textContrastGuideline\|labeledTapTargetGuideline" test/` finds **zero** files.

This confirms category (a) is empty: no screen test currently satisfies AC-07.

## Notes on AC-07 sub-clauses

AC-07 (a) — the four `AccessibilityGuideline` checks — is the most mechanical part of the backfill. Sub-clauses (b)–(e) add other surfaces:

- **(b) `MediaQuery.textScaleFactor: 2.0` no-overflow**: zero existing screen tests cover this. Each will need one additional `testWidgets`.
- **(c) `MediaQuery.disableAnimations: true`**: only `in_person_tab_content_exit_test.dart` (a widget test, not a screen test) sets this currently. Each screen test needs one additional check.
- **(d) Simple-Mode rendering**: applies only to screens containing organic graphics or non-essential animations. The current screens are largely text/form — most do **not** need a Simple-Mode test. Flag during backfill, on a per-screen basis.
- **(e) Linguistic-complexity gate on `.arb` strings**: cross-cutting; not a per-screen widget test but an ARB-level check (likely a separate test under `test/unit/l10n/`). Out of scope for the screen-test backfill — should be its own task.

Sub-clauses (a), (b), (c) are what the shared `assertScreenAccessibility(tester)` helper should cover. Sub-clauses (d) and (e) are tracked separately.
