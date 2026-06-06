---
task_id: TASK-PROC-002-08
type: impl
parent_requirement: REQ-PROC-002
urgency: 1
urgency_reason: U1-LATER-PHASE
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-13
started: 2026-05-18
completed: 2026-05-24
session_completed_at: 2026-05-24T16:17:48Z
after: [TASK-PROC-049-08]  # canon-bootstrap T7 must complete first; see .claude/task_ordering_priority_override.txt
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09]
  sections: []
scope_description: "Restore the integration_test/ infrastructure on the post-pivot execution target: Linux desktop in-container under a headless X virtual framebuffer (REQ-PROC-054 AC-06; win-command-bridge/A40-Windows path deleted). Establish a Linux runner. Write ONE easy integration test: role-selection / first-start onboarding (behavioural flow + accessibility guidelines). SCOPE REDUCED 2026-05-23 per user answer: the primary data-entry test (no persistence yet) and the data-transfer test (0.0.1 alpha partial) are DEFERRED to follow-up tasks. Cold-start and frame-budget integration tests are owned by separate tasks (TASK-PROC-046-02, -10)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: fa1a3718-42a0-4937-ad88-fcd9851a2b3b
session_account: web
---
# Goal: Restore integration-test infrastructure and write critical-flow tests

## Recommended Skill

**Use `code-complex` skill for this task.** The work writes Dart integration tests across multiple flows and requires a plan-and-approve gate before implementation — getting the helper / dependency-injection scaffolding right matters more than getting any single test in.

## Objective

Integration tests existed early in the project but stopped working after refactoring; they are currently broken / absent. The project has since matured (Clean Architecture, dependency injection via GetIt, BLoC, GoRouter) and LLM capability has progressed. Reviving integration tests is now feasible and the back-pressure framework makes them more valuable than before: they're the substrate for G7 dynamic (performance) and the only realistic way to verify end-to-end accessibility flows.

This task restores the infrastructure and writes the critical-flow tests named in REQ-PROC-002 AC-09 (a), (b), and accessibility-through-onboarding. Cold-start (AC-09 c) and frame-budget (AC-09 d) integration tests are owned by separate already-scheduled tasks but depend on this scaffolding existing.

## Scope Revision (2026-05-23)

This goal was authored against the old Windows/A40 + `win-command-bridge` model and three flow
tests. Per the user's answer (`automation/pending_feedback/TASK-PROC-002-08/answer.md`), the
authoritative current scope is in `plans_and_protocols/2026-05-23_02_plan_revised.md`:

- **Execution target pivoted** to Linux desktop in-container under a headless framebuffer
  (`xvfb-run -a flutter test integration_test -d linux`), per REQ-PROC-054 AC-06. The
  `win-command-bridge` is deleted; the `.ps1` runner is legacy.
- **Only one test in scope**: role-selection / first-start onboarding (behavioural + accessibility).
- **Deferred to follow-up tasks**: primary data-entry (no persistence yet) and data-transfer
  pipeline (0.0.1 alpha partial).
- The Phase-2 (a)/(b) flow descriptions below are superseded by the revised plan.

## Requirements Summary

REQ-PROC-002 AC-09 (integration test coverage for critical surfaces). `scripts/integration_test_runner/` already exists for orchestrating individual test runs (per CLAUDE.md §11) — this task uses it but does not rewrite it.

Current requirements: ../../requirements.md

## Scope

### In Scope

**Phase 1 — Scaffolding (the brittle part that historically broke):**
- Audit the current state of `integration_test/`. List any existing tests; classify each as: (a) working, (b) broken with known cause, (c) broken with unknown cause.
- Establish a per-test setup pattern that survives refactoring:
  - Use `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` consistently.
  - Use stable widget selectors: `find.byKey(...)`, `find.bySemanticsLabel(...)`, never `find.text("hardcoded display string")`.
  - Centralise dependency-injection setup in `integration_test/helpers/test_di.dart` (or equivalent) so tests don't each rebuild the DI graph.
  - Centralise test-fixture user-creation (synthetic user per REQ-PROC-052 AC-07).
- Document the patterns in `doc/testing/integration_tests.md` so future tests follow the same shape.

**Phase 2 — Critical-flow tests:**
- **Primary data-entry workflow** (AC-09 a): test launches the app, navigates onboarding (or skips it if already past), reaches the data-entry surface, fills a representative entry, submits, verifies persistence.
- **Data-transfer pipeline** (AC-09 b): test the QR send + receive flow as a **single-process simulation** (user-confirmed approach 2026-05-14): encode payload in test, decode in same test, verify round-trip and per-chunk correctness. Two-process screen-to-camera optical testing is **out of scope** — the app provider tests that manually with two physical devices. Single-process covers the pipeline correctness (serialization, chunking, framing, error correction) without the harness complexity of `flutter drive` multi-device.
- **Accessibility flow through onboarding** (cross-cuts AC-07 of REQ-PROC-046): test navigates onboarding with `tester.ensureSemantics()` invoked, asserting every interactive widget on every screen of the flow passes `AccessibilityGuideline` checks.

**Phase 3 — Runner integration:**
- Confirm `scripts/integration_test_runner/run_individual_integration_tests.ps1` (per CLAUDE.md §11) discovers and runs the new tests.
- Ensure tests are runnable both on a connected device (the Galaxy A40 — important for AC-09 c/d which are owned by other tasks) and on a desktop / emulator for fast iteration.

### Out of Scope

- Cold-start integration test — TASK-PROC-046-02 owns it.
- Frame-budget integration test — TASK-PROC-046-10 owns it.
- Mutation testing of integration tests — REQ-PROC-002 AC-02 is unit/widget-test scoped; integration-test mutation is exotic.
- Restoring legacy integration tests that have been broken so long they reference removed code paths — if a test points at code that no longer exists, delete the test rather than spending hours rewriting it.

## Acceptance Criteria

- [x] `integration_test/` contains the flows in revised scope: role-selection / first-start onboarding (behavioural + accessibility). Primary data-entry deferred → TASK-PROC-002-26; data-transfer pipeline deferred → TASK-PROC-002-27.
- [x] Each test uses stable selectors (`byKey` for interactive elements, `byType` for containers) — no `find.text("display string")` patterns.
- [x] `integration_test/helpers/` contains the centralised DI setup (`test_di.dart` with reset-in-tearDown) and mock helpers (`mock_use_cases.dart`, `mock_role_repository.dart`, `mock_config_helpers.dart`). Synthetic isolation achieved via mock injection rather than a dedicated fixture object.
- [x] `doc/testing/integration_tests.md` documents the Linux-in-container patterns (xvfb-run, CMakeCache gotcha, DI teardown pattern) for future tests.
- [x] Linux runner `scripts/integration_test_runner/run_integration_tests_linux.sh` runs tests under `xvfb-run` (headless), verified 5× consecutive. The `.ps1` / A40 criterion is superseded: execution target pivoted to Linux in-container per REQ-PROC-054 AC-06 (scope revision 2026-05-23).
- [x] All 21 legacy broken integration tests deleted with explicit rationale in protocol (post-pivot, referencing removed code paths).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Galaxy A40 physical device | Available | Same instrument as TASK-PROC-046-02 |
| `scripts/integration_test_runner/` | Exists | Per CLAUDE.md §11 |
| TASK-PROC-052-03 (toString redaction) | Pending (helpful, not blocking) | Synthetic-user fixtures benefit from the redaction pattern landing first |

## Notes

**Scheduling**: this task is deliberately ordered late — `urgency: 1` keeps `next_tasks.py` from surfacing it until the per-change gates and the simpler infrastructure are in place. The app provider's preference (2026-05-14) is to handle integration tests near the end of the gate-set rollout.

**Historic fragility — diagnosed.** The user's recall (2026-05-14): the previous integration-test attempt failed because **test state did not reset between tests**. Tests had to be invoked individually to pass, each rebuilding the full DI graph. The framework's own state-reset hooks didn't work reliably. This concrete diagnosis sharpens Phase 1's scaffolding work: the central `integration_test/helpers/test_di.dart` must explicitly tear down GetIt registrations between tests (`GetIt.I.reset()`), and the per-test setUp must rebuild the graph from scratch. Verify by writing the three flows and running them as a single suite, then re-running 5 consecutive times — the same suite should pass identically each time. If state leakage returns, isolate which test pollutes which (likely a singleton or static field).

The Phase 1 scaffolding choices (stable selectors, centralised DI tear-down/rebuild, centralised fixtures) are the difference between integration tests that survive refactoring and tests that break on every PR. Cutting corners here defeats the purpose of having integration tests at all.

If multi-device QR transfer testing turns out impractical, prefer the split-into-two-single-side-tests pattern over abandoning the transfer flow entirely. Even one-side coverage of the serialization + chunk emission is significantly better than zero coverage.

Accessibility-flow tests are the strongest argument for integration tests on this project. Widget tests can verify a single screen's `AccessibilityGuideline` compliance (REQ-PROC-046 AC-07), but they cannot verify that *navigation between screens* preserves accessibility — that the focus order is sensible, that the screen-reader announcement of a new screen is meaningful, that no modal traps focus. Onboarding is the right starting flow because it's the user's first impression and the most likely place to lose someone with accessibility needs.
