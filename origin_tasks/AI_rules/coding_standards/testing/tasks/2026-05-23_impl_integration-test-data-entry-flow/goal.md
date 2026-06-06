---
task_id: TASK-PROC-002-26
type: impl
parent_requirement: REQ-PROC-002
urgency: 1
urgency_reason: U1-LATER-PHASE
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-05-23
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09]
  sections: []
scope_description: "Integration test for the primary data-entry workflow (AC-09 a): app launch through onboarding, data-entry surface, fill and submit a representative entry, verify persistence via the repository layer. Deferred until DataInputBloc persistence lands (currently in-memory Map only)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 2c52ed48
  file: ../../requirements.md
---
# Goal: Primary data-entry integration test (AC-09 a)

## Recommended Skill

**Use `code-test` skill for this task.**

## Objective

Write the integration test for the primary data-entry workflow named in REQ-PROC-002 AC-09 (a):
launch the app, navigate onboarding (or skip it if already past), reach the data-entry surface,
fill a representative entry, submit, and verify persistence via the repository layer.

## Deferral Reason

`DataInputBloc` currently stores answers in an in-memory Map — there is no persistence layer to
assert against. A "saved entry" test that only checks in-memory BLoC state does not satisfy the
AC-09 (a) intent ("through to a saved entry"). This task must wait until the DataInputBloc
persistence layer lands.

**When to un-defer**: when a task implementing `DataInputBloc` persistence (repository write +
Drift/Hive or equivalent) is created, add its TASK-ID to the `after:` field of this task and
lower `urgency` to 2.

## Scope

- File: `integration_test/flows/data_entry_flow_test.dart`
- Follow the `test_di.dart` pattern from TASK-PROC-002-08 (`integration_test/helpers/test_di.dart`).
- Stable selectors only: `find.byKey(...)`, `find.bySemanticsLabel(...)`,
  `find.byType(Widget)` — no `find.text(...)`.
- The test must:
  1. `setUpTestDi(isFirstLaunch: false)` (past onboarding; skip to data-entry surface).
  2. Navigate to the data-entry screen.
  3. Fill a representative entry with synthetic data (REQ-PROC-052 AC-07).
  4. Submit.
  5. Verify the repository `saveEntry` (or equivalent) was called with the expected data.
- Run under `xvfb-run -a flutter test integration_test/flows/data_entry_flow_test.dart -d linux`.

## Requirements Reference

- **Requirement**: `../../requirements.md` (REQ-PROC-002)
- **AC-09 (a)**: integration test for the primary data-entry workflow — app launch through to a saved entry.
- **Related**: TASK-PROC-002-08 (parent scaffolding task; sets up `test_di.dart` and `pump_helpers.dart`).

## Acceptance Criteria

- `integration_test/flows/data_entry_flow_test.dart` exists and passes under `xvfb-run`.
- Repository persistence is asserted (not just in-memory BLoC state).
- Stable selectors only (grep `find.text(` in file = 0).
- Test passes 5× consecutively without state leakage.
- `doc/testing/integration_tests.md` remains consistent with the pattern used.

---

**Note**: This task describes WHAT to implement, not HOW. The implementation plan is created
fresh at execution time.
