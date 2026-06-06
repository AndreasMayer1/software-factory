# Created Backfill Tasks — REQ-PROC-046 AC-07

Task: TASK-PROC-046-08
Date: 2026-05-19

## Source

Read `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-10_analyze_inventory-screens-without-widget-tests (completed)/plans_and_protocols/screens_inventory.md` (TASK-PROC-046-07 output).

## Batching Decision

The inventory found 17 reachable screens needing accessibility backfill and recommended a two-task split:
1. A setup task to author a shared accessibility test helper (centralises the four `AccessibilityGuideline` checks plus `textScaleFactor: 2.0` and `disableAnimations: true` — required by AC-07 sub-clauses a/b/c).
2. A backfill task that applies the helper across all 17 screens, plus per-screen assertions for the active ACs the helper does not centralise (AC-02/03 Simple Mode, AC-06 collapsible section, AC-15 keyboard `Tab`, AC-16 `SemanticsRole`, AC-17 form behaviour).

This task adopts the inventory recommendation. Per the goal.md scope language, "a related cluster ... may be one task" — and the cluster here is "every reachable screen", because (a) the work is mechanically uniform, (b) splitting would force every screen test to duplicate helper logic, and (c) AC-07 tracks REQ-NFUNC-002's currently-active set, so the helper is the single update point when Phase-2 ACs promote. A finer split would multiply drift surface.

## Created Tasks

| Task ID | Effort | Parent Requirement | Goal.md | Description |
|---|---|---|---|---|
| TASK-NFUNC-002-01 | S | REQ-NFUNC-002 (Accessibility Guidelines) | `requirements_tasks/non-functional/ui_ux_design_system/accessibility/tasks/2026-05-19_impl_accessibility-test-helper/goal.md` | Author `test/helpers/accessibility_test_helper.dart` with `assertScreenAccessibility(tester)`, `pumpScreenAt200PercentTextScale(...)`, `pumpScreenWithReduceMotion(...)`. Centralises AC-01, AC-04, AC-05, AC-09a, AC-11, AC-12. Plus its own helper test file. |
| TASK-NFUNC-002-02 | L | REQ-NFUNC-002 (Accessibility Guidelines) | `requirements_tasks/non-functional/ui_ux_design_system/accessibility/tasks/2026-05-19_impl_widget-tests-accessibility-backfill/goal.md` | Apply the helper to every reachable screen widget test (17 screens) and add per-screen assertions for AC-02, AC-03, AC-06, AC-15, AC-16, AC-17 where applicable. Includes renaming + fixing `plan_list_test.dart.skip`. |

## Coverage Verification

The inventory listed 19 reachable routes; 2 are placeholder stubs (`/client/analysis`, `/client/inbox`) explicitly excluded by AC-07's "real screen" gate. The remaining **17 screens are all listed in TASK-NFUNC-002-02's In-Scope table**, with effort, test file path, and per-screen AC extras.

Effort tally inside TASK-NFUNC-002-02:
- 6 × S (#1, #2, #9, #12, #13, #14) ≈ 6 h
- 9 × M (#3, #4, #5, #6, #7, #8, #10, #11, #15, #19) — note: #4 is M, total **10 × M** ≈ 20 h. (Inventory's tally counted 10 M screens; same here.)
- 1 × L (#18 `DataBeamScannerScreen`) ≈ 4 h
- Total ≈ 30 h, matching the inventory estimate.

The setup task (TASK-NFUNC-002-01) adds ~2 h on top.

## Dependency Wiring

Both created tasks have `after: [TASK-PROC-046-03, TASK-PROC-046-07]` per the goal.md instruction:
- TASK-PROC-046-03 (analyzer / test-smell config) must land first so any new test code is linted by the active config.
- TASK-PROC-046-07 (this inventory) is the prerequisite that produced the scope.

TASK-NFUNC-002-02 additionally has `after: TASK-NFUNC-002-01` (helper must exist before backfill applies it). `propose_after.py` produced no proposals — no same-package auto-add was needed.

## Out-of-Scope Tracking (Recorded Here for Traceability)

Items the inventory called out but that AC-07 / this backfill does NOT cover:

1. **`/client/analysis` and `/client/inbox` placeholder routes**: Re-include when real screens are implemented. Will be tracked by adding `awaiting:` entries to the eventual AC-07 closure task. Not a separate task today.
2. **Orphan screen files** (`home_screen.dart`, `therapist_client_detail_screen.dart`, `therapist_inbox_root_screen.dart`, `therapist_receive_screen.dart`): Not reachable via router. Optional cleanup is a separate task — should be opened by whoever owns that code area, not bundled into AC-07 backfill.
3. **AC-14 (ARB linguistic complexity gate)**: Already tracked in REQ-NFUNC-002 trackable_items; needs a separate ARB-validation task under `non-functional/ui_ux_design_system/accessibility/` or `process/AI_rules/.../i18n/`. Out of scope here.

## No-Op Check

The inventory contained **17 gaps** (category B: test exists but no semantics check). It is therefore NOT a no-op. The no-op clause in goal.md does not apply.
