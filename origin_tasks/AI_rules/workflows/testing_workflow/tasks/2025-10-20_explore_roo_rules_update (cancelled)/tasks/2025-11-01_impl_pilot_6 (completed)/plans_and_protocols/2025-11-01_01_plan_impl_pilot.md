template_filename: .roo-templates/high_level_impl_plan.md
target_plans_and_protocols_path: requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/plans_and_protocols/

produced_by: Roo (architect subtask: arch_analyze_define_scope_2025-11-01_impl_pilot_6)
timestamp: 2025-11-01T10:13:38Z
guidelines_read:
- doc/architecture.md
- doc/testing.md
- doc/general/documentation_process.md

title: High-level implementation plan — Pilot 6 (testing-workflow)
summary:
- Purpose: Produce a high-level implementation plan for the pilot that validates the hierarchical testing orchestrator pattern for the plan_templates feature focusing on unit and widget tests.
- Scope: Analysis & planning only. No source code or tests will be modified in this subtask.

1) Context and goal (short)
- Reference goal: See goal at [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-11-01_impl_pilot_6/goal.md:1).
- Pilot intent: Validate orchestrator hierarchy and "code -> architect -> code" workflow for test improvements in plan_templates. Limit tests to unit/widget; do not create or run integration tests.

2) Recursive lib/ listing (snapshot)
- The plan includes the recursive listing of `lib/` (produced by list_files during analysis). Key feature area relevant to the pilot:
  - lib/features/therapist/plan_templates/
    - plan_templates_routes.dart
    - presentation/bloc/plan_templates_bloc.dart
    - presentation/bloc/plan_template_detail_bloc.dart
    - presentation/organisms/plan_list.dart
    - presentation/organisms/plan_detail_view.dart
    - presentation/widgets/plan_templates_orchestrator.dart
    - presentation/widgets/plan_templates_orchestrator_test.dart (test exists under test/widget/features/therapist/plan_templates/... as referenced in goal)
  - (Full lib/ tree available in the repository — included as attachment in the plans_and_protocols folder by reference; implementers should consult `lib/` directly.)

3) Assumptions (explicit — must be validated by next subtask)
- A1: The failing test file to target is:
  - test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  This must be validated by the next subtask (confirm exact failing tests and current failures).
- A2: The orchestrator rules and templates available under the parent task provide the required orchestration artifacts and templates (plans_and_protocols/templates exist).
- A3: No integration tests will be added or run for this pilot.
- A4: Test helpers referenced in doc/testing.md are present and usable (e.g., pump helpers, mock classes). If missing, next subtask must create or declare them.
- A5: Changes will be limited to tests and test-support code (no product feature changes) unless test failures indicate a necessary implementation fix — then create separate impl task.

4) Acceptance criteria (explicit)
- AC1: Outer Orchestrator created exactly one Testing Orchestrator for plan_templates (evidence: one plans_and_protocols entry created by orchestrator).
- AC2: Test File Orchestrator spawned the expected subtasks (Test File Orchestrator plan + Architect plan + code subtasks) and corresponding plan/protocol files exist.
- AC3: All code subtasks followed "code -> architect -> code" pattern (evidence: commit history and plans_and_protocols entries showing architect plans between code attempts).
- AC4: Phase 3 verification executed targeted unit/widget tests via `flutter test <file>`; tests either pass or `explore_test_blocker` protocols created and documented.
- AC5: Deliverables: plans_and_protocols entries for orchestrator, test-file-orchestrator, architect plan, and part_attempt protocols.

Recommended Verification Level for Phase 3: L1 (targeted verification)
- Rationale: Pilot focuses on a single feature's test file(s). Use targeted runs of `flutter test` for affected test files. L1 (targeted) balances speed and confidence. If blockers appear that require more system-level checks, escalate to L2.

5) Required tests to add/update
- Update/fix existing widget test:
  - test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
    - Focus: stabilize GoRouter-related setup, provide correct router builder, stub BLoCs using whenListen, ensure pumpAndSettleSafe usage.
- Add/adjust unit tests if BLoC logic must be verified in isolation (use mocktail + bloc_test).
- No integration tests to be added for this pilot.

6) Risks and blocking dependencies
- R1: Missing or outdated test helpers (e.g., safe pump, router test helpers). Blocker if not present.
- R2: Test instability due to GoRouter + StatefulShellRoute complexity — may require architect-level redesign of test helper usage.
- R3: Generated code issues (freezed/build_runner) may block test compilation. Mitigation: run build_runner as pre-step in implementation subtasks.
- R4: If repository DI or Hive initialization is required in tests and not stubbed, integration-like setup may be necessary — this is out-of-scope and must be escalated.
Rollback strategy:
- Keep changes restricted to test files and test-only helpers. If a change causes regressions, revert the commit that introduced the test changes. Maintain granular commits per test file.

7) Concrete verification commands (to be used in Phase 3)
- Analyze:
  - flutter analyze
- Targeted tests (example):
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
  - If individual test names are needed (plain-name):
    - flutter test test/widget --plain-name "Name of failing test" 
- If build runner needed:
  - flutter pub run build_runner build --delete-conflicting-outputs

8) File-level Scope of Work (minimal set)
- The analysis indicates test fixes only. Proposed minimal Scope of Work (files to create/modify):
  1. test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
     - Modify: stabilize setup, use router helper, stub BLoCs, apply SafePump.
     - Justification: This is the failing test the pilot targets (mentioned in goal).
  2. test/helpers/test_router_helpers.dart (or reuse existing test helper if present)
     - Create or modify: provide `pumpMoreScreenTestApp` style helper for GoRouter + Tokens + BlocProviders as described in doc/testing.md.
     - Justification: GoRouter tests require a correct router builder and helper.
  3. test/helpers/safe_pump.dart
     - Create if missing: SafePump extension to avoid pumpAndSettle infinite loops.
     - Justification: Recommended in guidelines for GoRouter tests.
  4. requirements_tasks/.../plans_and_protocols/<new plan/protocol files>
     - Create: plans/protocol artifacts documenting orchestrator and architect steps (this file and subsequent protocol files).
     - Justification: Required deliverables per workflow.

- Note: This is exactly 3 Dart test files to modify/create (plus plans/protocols markdown). The scope does NOT exceed 4 Dart files; therefore the subtask can continue with this plan. (ScopeTooLarge = false)

9) Tests and verification to add to plan
- Unit/widget tests to be run locally via the commands above.
- Phase 3 verification strategy:
  - Run `flutter analyze`
  - Run targeted `flutter test` for the test file
  - If failures are due to environment/setup, create `explore_test_blocker` protocol and document findings in plans_and_protocols.

10) Assumptions to validate in next subtask (explicit)
- V1: Confirm exact failing test file(s) and current failing test output (test names + stack traces).
- V2: Confirm presence or absence of test helpers: `pumpMoreScreenTestApp`, `pumpAndSettleMoreScreenTestApp`, `pumpUntilBlocState`, `SafePump`.
- V3: Confirm whether any generated code (freezed) must be rebuilt before tests (i.e., verify build_runner status).
- V4: Confirm whether any global DI/Hive setup is required for those tests.

11) Deliverables this subtask produces
- This plan file:
  - requirements_tasks/.../plans_and_protocols/2025-11-01_01_plan_impl_pilot.md (this file)
- A list of files proposed in Scope of Work (see section 8).

ScopeTooLarge: false
Slicing recommendation (if needed in future): If additional failing tests are discovered beyond plan_templates, split by feature and create a separate pilot per feature.

Notes and next actions for implementer (to be performed in following subtasks)
- Validate assumptions V1-V4 by reading test outputs and listing current test helpers.
- Create the file-scope changes in a new impl_test_part subtasks, each starting with a commit and ending with a commit, and produce part_attempt protocols as required by Test-writing subtask rules.
- Use the project's testing guidelines (doc/testing.md) as mandatory reference during implementation and record guidelines_read timestamp in each part_attempt protocol.
