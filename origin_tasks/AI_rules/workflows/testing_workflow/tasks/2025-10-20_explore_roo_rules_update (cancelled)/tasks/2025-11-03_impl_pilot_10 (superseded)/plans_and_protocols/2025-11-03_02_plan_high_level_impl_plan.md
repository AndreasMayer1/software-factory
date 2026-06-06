# 2025-11-03_02_plan_high_level_impl_plan.md

timestamp: 2025-11-03T08:29:22Z
author: Roo (architect-mode update)

Summary
- Purpose: Update the previous high-level plan to make an explicit decision about the redirect approach and to add prescriptive, enforced test rules for Phase 2 (implementation attempts). This file contains only the what and why (per `.roo-templates/high_level_impl_plan.md`) and does not include step-by-step implementation instructions.
- Change: Choose the redirect approach for Phase 2 (tests) and add clear test rules and acceptance criteria to reduce flakiness and DI leakage risk.

Decision: redirect approach (explicit)
- Decision: Adapt Phase 2 tests to the repository's current widget-level BlocListener redirect (no router refactor in this pilot).
- Rationale: The validation protocol (`2025-11-03_02_protocol_validation_report.md`) confirmed the repository implements auto-selection via a widget-level `BlocListener` inside `PlanTemplatesOrchestrator` (evidence included). A refactor to an async router-level redirect would align with guidelines but introduces a larger scope and higher risk (refactor + test churn). For this pilot (limited scope, low-to-medium effort) we will target the current implementation and adapt tests accordingly. If later the team decides to refactor the redirect to router-level, that will be a separate refactor task staged before test changes.

Scope of Work (definitive Phase 2 scope — files to be updated by Phase 2 implementation subtasks)
- test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  - reason: failing widget test referenced by the task goal; must be updated to match current widget-level redirect behaviour and orchestrator/router test scaffolding.
  - expected change type: tests (widget)
- test/helpers/pump_until_bloc_state.dart
  - reason: ensure helper reliably waits for BLoC states used by the orchestrator tests; may require small adjustments to wait logic or exports.
  - expected change type: tests (helpers)
- test/helpers/safe_pump.dart
  - reason: canonicalize safe pump behaviour and require consistent imports across tests.
  - expected change type: tests (helpers)
- test/helpers/test_router_helpers.dart
  - reason: adjust/create router test helpers to consistently construct a test GoRouter with StatefulShellRoute + MultiBlocProvider as needed by the orchestrator tests.
  - expected change type: tests (helpers)
- plans_and_protocols/part_attempt_01_protocol.md (placeholder)
  - reason: Per test-writing rules, create a per-attempt protocol file for the first implementation attempt; subsequent attempts must create their own protocol files.
  - expected change type: docs (protocol)

Enforced test rules for Phase 2 (mandatory)
- Reset/unregister GetIt between tests
  - All updated or new tests must reset DI in setUp/tearDown. Example snippet to include at top of each related test file and in each attempt protocol:
    ```dart
    setUp(() async {
      await GetIt.I.reset(dispose: true);
      // register required test singletons/mocks
    });

    tearDown(() async {
      await GetIt.I.reset(dispose: true);
    });
    ```
  - Requirement: Each `part_attempt_<n>_protocol.md` must document that DI reset was performed and include the snippet and `guidelines_read` timestamp.
- When stubbing BLoCs, always use whenListen and provide initialState
  - Tests that mock BLoCs must use `whenListen(mockBloc, Stream.fromIterable([...]), initialState: initialState)` or equivalent to avoid stream-related race conditions.
- Canonicalize on test/helpers/safe_pump.dart
  - Tests must import and use the canonical `test/helpers/safe_pump.dart` extension rather than duplicates. Phase 2 implementors should consolidate duplicate helpers where small edits are required; consolidation itself may be a small step in Phase 2 but must not expand the scope beyond the listed helper files.
- Part-attempt protocols (per-attempt documentation)
  - The first implementation attempt must create `part_attempt_01_protocol.md` (placeholder created alongside this plan).
  - Each subsequent implementation attempt must create its own `part_attempt_<n>_protocol.md` in the same plans_and_protocols folder and must include at minimum:
    - subtask_id
    - parent_test_part_orchestrator
    - attempt_number
    - guidelines_read: <ISO8601 timestamp>
    - commands_run (list)
    - logs_path
    - modified_files
    - commit_hash
    - verification_performed: true|false
    - verification_result: PASS|FAIL|ERROR|NONE
    - notes
- Verification level and scope
  - Verification Level: 2 (static + targeted widget tests)
  - Reason: Focused widget tests verify the orchestrator redirect behaviour and helper stability without broad integration runs. Level 2 combines code inspection/static checks and running the targeted widget tests listed in Scope of Work.
  - Effort estimate: Low-to-Medium (adapting tests + helpers). If a refactor is later chosen, effort increases significantly.
- Acceptance criteria for Phase 2 tests
  - The updated widget test for plan_templates_orchestrator_test.dart passes when run in isolation and as part of the targeted test group.
  - All related helper tests (if any) pass.
  - Each attempt's `part_attempt_<n>_protocol.md` is present and documents `guidelines_read` with timestamp and the verification result and `commit_hash` for the changes.
  - No changes to production files are required to make tests pass; if changes are required, they must be proposed as a separate, explicit task and not implemented within this test-adaptation pilot.
- Risks and mitigations (short)
  - Flaky tests due to router timing: use SafePump and pumpUntilBlocState to avoid pumpAndSettle timeouts.
  - DI leakage: enforce GetIt reset in setUp/tearDown and document in protocols.
  - Router timing and GoRouter/StatefulShellRoute complexity: ensure test_router_helpers consistently builds the shell and navigator keys matching production usage.
  - If tests require production changes to stabilize, stop and open a refactor task (do not implement production changes in this pilot).

Notes and rationale (why adapt tests to widget-level redirect)
- The validation protocol found the repository currently uses a widget-level `BlocListener` redirect implementation inside `PlanTemplatesOrchestrator`. Adapting tests to the current behaviour minimizes scope, avoids refactoring production code in the pilot, and enables low-to-medium effort verification. This aligns with the pilot's goal to validate and stabilize tests for the plan_templates feature.
- The plan explicitly documents the alternative (refactor to router-level async redirect) and defers it to a separate refactor task if the team prefers guideline-conformant routing.

Files created/modified by Phase 1 (this file)
- requirements_tasks/.../plans_and_protocols/2025-11-03_02_plan_high_level_impl_plan.md (this file — docs)
- requirements_tasks/.../plans_and_protocols/part_attempt_01_protocol.md (placeholder created alongside this file)

End of high-level plan update (Phase 1).