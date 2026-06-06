Depth level: 1

# 2025-10-29_01_plan_impl_pilot_4.md

Timestamp: 2025-10-29T18:18:43.681Z

Author: architect_subtask_2025-10-29_impl_pilot_4


1) Goal & Inputs

- Goal (read): [`goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/goal.md:1)
- Required rules read: [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1), [`doc/testing.md`](doc/testing.md:1), [`doc/architecture.md`](doc/architecture.md:1)
- Relevant previous pilot artifacts read: [`2025-10-20_01_plan_initial.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot (completed)/plans_and_protocols/2025-10-20_01_plan_initial.md:1), [`2025-10-20_04_testing_orchestrator_plan.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot (completed)/plans_and_protocols/2025-10-20_04_testing_orchestrator_plan.md:1), [`2025-10-21_01_final_report.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot (completed)/plans_and_protocols/2025-10-21_01_final_report.md:1)
- Codebase entrypoint inspected: [`lib/`](lib/:1) (recursive listing performed).

2) Context summary

- Pilot objective: Validate the hierarchical testing orchestrator pattern for feature `plan_templates` using unit/widget tests only (see parent goal).
- The immediate implementable target for this pilot is the failing test set at [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1).
- Existing helpers present in `test/helpers/` (examples): [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1), [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1), [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:1).

3) Lib scan (relevant files)

- [`lib/features/therapist/plan_templates/plan_templates_routes.dart`](lib/features/therapist/plan_templates/plan_templates_routes.dart:1)
- [`lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart`](lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart:1)
- [`lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart`](lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart:1)
- [`lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart`](lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart:1)

4) Minimal Scope of Work (explicit files to create or modify)

- Create: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md:1) (this document)
- Modify (test): [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) — update to fix failing assertions, stabilize async waits, and ensure deterministic BLoC stubbing.

Note: Scope contains 1 Dart test file and 1 md artifact (plan). This is <= 4 Dart files; Phase 2 can proceed (tests-only special case applies).

5) Phase 2 — Implementation decomposition (small, verifiable parts)

- NOTE: Per `.roo/rules-orchestrator/implementation_workflow.md` ([`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)), when the Scope of Work is tests-only, Phase 2 implementation cycle is skipped and the Testing Orchestrator proceeds directly to Phase 3 (targeted verification) after the Architect `arch_test_plan` and Code subtask create the test file. The sequence below reflects the required subtasks and artifacts for that flow.

Part 1 — Architect: Produce `arch_test_plan`
- Goal: produce an `arch_test_plan` artifact that splits the test file into parts per the `arch_test_plan` template in the rules and `doc/testing.md`.
- Deliverable file: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md:1)
- Files affected: plan file above (create), no production code changes.
- Mode: architect
- Verification level: 1 (Code Review of plan)
- Tests required: none (this is planning)
- Estimated effort: low (1–2 hours)
- Risk & rollback: low risk; rollback by updating/removing the arch_test_plan file.

Part 2 — Code: Implement/Update widget test
- Goal: update [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) to fix deterministic BLoC seeding, use `pumpAndSettleSafe` where needed, and stabilize router/redirect assertions.
- Files affected:
  - [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) (modify)
- Mode: code (create a code subtask per test file as `impl_test_part`)
- Verification level: 3 (Targeted Test — run the test file)
- Tests required: widget tests (the file itself). Suggested verification command:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- Estimated effort: medium (2–4 hours) — depends on flakiness and missing helpers.
- Risk & rollback:
  - Risk: flakiness due to GoRouter async redirects and pump timing. Mitigation: follow `doc/testing.md` guidance (use safe pumping, seed BLoC streams, add stable Keys for critical widgets).
  - If tests cause regressions elsewhere, revert the test commit (git revert) and create an `explore_test_blocker` architect subtask for deeper investigation.

Part 3 — Testing Orchestrator: Phase 3 verification & logs
- Goal: run targeted verification and save outputs.
- Files/artifacts to produce:
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_03_test_run_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_03_test_run_protocol.md:1)
- Mode: orchestrator / testing
- Verification level: 3 (Targeted Test execution)
- Command to run (single-file targeted run): flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- Capture: save stdout/stderr and full test output to the `2025-10-29_03_test_run_protocol.md` artifact; if failures are reproducible create `explore_test_blocker_<timestamp>.md` per workflow.

6) Files mapping & reasons (minimal set)

- [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1) — Type: dart (test). Reason: primary failing test file to stabilize; will be updated to use stable keys, deterministic BLoC seeding, and SafePump patterns.
- [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md:1) — Type: md. Reason: this plan (artifact).
- Conditional (only if arch_test_plan finds missing helpers): create `test/helpers/router_test_helpers.dart` and/or `test/helpers/test_di.dart`. These are small test-only helpers (Dart). If required, include them as separate code subtasks — ensure total Dart files modified remains <=4; otherwise stop and split tasks (see blocking protocol below).

7) Preconditions & dependencies

- Development environment: Flutter SDK compatible with project's pubspec; tests run with `flutter test`. Follow `doc/testing.md` guidance.
- Dev dependencies expected: `mocktail`, `bloc_test`, `flutter_test`. Confirm in `pubspec.yaml` before Phase 3.
- Required read: [`doc/testing.md`](doc/testing.md:1) (test patterns), [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1) (workflow constraints), [`doc/architecture.md`](doc/architecture.md:1) (DI guidance).
- Confirm the following test helpers exist or the Architect author will request them in the `arch_test_plan`: [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1), [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1), [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:1).

8) Tests in this plan and Testing Orchestrator notes

- Tests: widget tests only (no integration tests) as required by the parent goal.
- Testing Orchestrator behavior:
  1. Create a Test File Orchestrator for the file [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1).
  2. The Test File Orchestrator requests an `arch_test_plan` from an Architect subtask (see Part 1).
  3. The Code `impl_test_part` subtask implements the test file (see Part 2).
  4. Testing Orchestrator runs Phase 3 verification using `flutter test <file>` and collects logs into [`plans_and_protocols/2025-10-29_03_test_run_protocol.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_03_test_run_protocol.md:1).

9) Acceptance criteria (Phase 3 verification)

- The plan file was created at [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md:1) and committed.
- The Testing Orchestrator created exactly one Testing Orchestrator for this feature (orchestrator-level check is external to this plan).
- Test File Orchestrator produced an `arch_test_plan` file: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_arch_test_plan_plan_templates.md:1).
- The `impl_test_part` implemented the test file at [`test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`](test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart:1).
- Phase 3: Running `flutter test` for the file returns:
  - PASS: all tests pass, OR
  - If failing, an `explore_test_blocker_<timestamp>.md` architect protocol was created with logs and reproduction steps.

10) Risks, mitigations & rollback

- Risk: test flakiness and timeouts caused by GoRouter async redirects and pumpAndSettle loops.
  - Mitigation: Add `pumpAndSettleSafe`, seed BLoC streams via `whenListen`, add stable Keys to critical widgets (`ValueKey` usage exists in code), and avoid `pumpAndSettle` where microtask loops occur.
- Risk: missing test helpers or DI hooks requiring production changes.
  - Mitigation: Architect must list required helpers in `arch_test_plan`; small test-only helpers may be created as separate code subtasks. If more than 4 Dart files must be modified, STOP and create a blocking protocol (see below).
- Rollback: revert commits, and create an `explore_test_blocker` artifact for deeper analysis.

11) Blocking conditions and protocol

- If implementing the approved test changes would require editing more than 4 Dart files (production + tests), stop and produce:
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_protocol_scope_too_large.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_02_protocol_scope_too_large.md:1)
- If missing information or helpers prevent an actionable plan, produce:
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_03_blockers.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_03_blockers.md:1)

12) Next actions (suggested execution order)

1. Confirm this impl_plan and authorise the Testing Orchestrator to create the Test File Orchestrator (orchestrator-level action).
2. Create Architect `arch_test_plan` (Part 1).
3. Create Code `impl_test_part` to update the test file (Part 2).
4. Testing Orchestrator runs Phase 3 verification and saves `2025-10-29_03_test_run_protocol.md` (Part 3).
5. If tests pass, proceed to Post-Implementation Documentation (architect) per implementation workflow.

13) References (read & followed)

- Workflow: [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)
- Testing guidelines: [`doc/testing.md`](doc/testing.md:1)
- Architecture guidelines (DI): [`doc/architecture.md`](doc/architecture.md:1)

14) Confirmation of required git actions (you ran step 1)

- Pre-analysis commit: user confirmed running: git commit --allow-empty -m "chore(2025-10-29_impl_pilot_4): start analysis"
- Next required local commands (please run after this file is created):
  - git add [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-29_impl_pilot_4/plans_and_protocols/2025-10-29_01_plan_impl_pilot_4.md:1)
  - git commit -m "docs(plan): add impl plan for 2025-10-29_impl_pilot_4"

End of plan.