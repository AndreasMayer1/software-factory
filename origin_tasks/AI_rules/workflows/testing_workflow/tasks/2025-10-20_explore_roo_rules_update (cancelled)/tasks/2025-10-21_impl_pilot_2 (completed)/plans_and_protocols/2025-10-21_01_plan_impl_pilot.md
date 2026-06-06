# 2025-10-21_01_plan_impl_pilot.md

Date: 2025-10-21T20:24:00+02:00
Author: Roo (architect)

Summary

This plan implements the Task Kick-off Protocol for the pilot described in
[`goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/goal.md:3).

Key quoted lines from the goal:

> "Pilot the hierarchical testing orchestrator pattern for the testing workflow."
> (see [`goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/goal.md:3))

> "Fix the problem discovered by the last pilot by adjusting the orchestrator rules in `.roo\rules-orchestrator`: Dateien im plans_and_protocols Ordner: Die part_attempt_X_protocol.md Dateien wurden ohne Datum und Nummerierung erstellt. Sie sollten sich an die gleichen Regeln halten wie alle anderen Dateien in dem Ordner auch: Prefix Datum_#_"
> (see [`goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/goal.md:10))

> "To have something to test you can update the currently failing tests for `test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`"
> (see [`goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/goal.md:25))

Scope of Work (validated)

The following exact relative file paths are in-scope for code subtasks (definitive list).
Only these files may be modified by implementation subtasks created from this plan.

1. `.roo/rules-orchestrator/test_part_orchestrator.md` (update naming rules to require Date_#_ prefix)
2. `test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart` (fix failing unit/widget tests used by pilot)

Rationale for scope:

- The naming bug is an orchestrator rule issue; updating a single rule document is the most scoped change to fix file naming.
- The pilot uses `plan_templates` as representative feature; only the failing test file is required to exercise the orchestrator and Phase 3 verification.
- Keeping scope to 2 files keeps the implementation small (<=4 files) per instructions.

Implementation plan (step-by-step)

Precondition (before any code changes)

- Create these plan/protocol artifacts in the main task `plans_and_protocols` directory:
  - [`2025-10-21_01_plan_impl_pilot.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/plans_and_protocols/2025-10-21_01_plan_impl_pilot.md:1)
  - [`2025-10-21_01_protocol_analysis.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/plans_and_protocols/2025-10-21_01_protocol_analysis.md:1)

- Capture a start-of-work commit (empty commit) to mark the beginning of the task:
  - git command to run: git commit --allow-empty -m "2025-10-21_impl_pilot: start work (architect plan)"

Step 1 — Rule update (orchestrator)

- File: `.roo/rules-orchestrator/test_part_orchestrator.md`
- Change: Add an explicit rule requiring per-part protocol filenames to use the prefix pattern: YYYY-MM-DD_##_part_attempt_N_protocol.md (or the project's canonical pattern: YYYY-MM-DD_##_part_attempt_X_protocol.md). The rule must include:
  - When creating per-part protocol files, always prefix with the plan date and a running index.
  - Enforce numeric zero-padded numbering (e.g., 01, 02).
  - Example filename in rule text: `2025-10-21_01_part_attempt_1_protocol.md`
- Deliverable: Updated rule file (document change only).

Step 2 — Create Testing Orchestrator artifacts (simulated by orchestrator)

- The orchestrator (manual/human or an automated orchestrator later) will run using the updated rules. For the pilot we will not run orchestrator code, but code subtasks will rely on the updated rule.

Step 3 — Fix failing test(s)

- File: `test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`
- Change: Update test setup per `doc/testing.md` guidelines:
  - Ensure correct `GoRouter` setup for `StatefulShellRoute` usage or use the `pumpMoreScreenTestApp` helper updated to pass `router`.
  - Stub necessary BLoC streams with `whenListen` (use existing test helpers in `test/helpers/`).
  - Replace fragile `pumpAndSettle` calls with `safe_pump.dart` helper (`pumpAndSettleSafe`) where router instability was observed.
  - Ensure localization delegates are present in the test `MaterialApp.router` builder.
- Deliverable: Tests updated to be deterministic and pass in isolation.

Step 4 — Phase 3 verification (per-file)

- For each modified test file run:
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart
- Expected outcome:
  - Tests pass, or if failing, an `explore_test_blocker` protocol file is produced by the Test Part Orchestrator.

Step 5 — Pilot artifacts and logging

- The orchestrator should (and pilot must record) the following artifacts in the task `plans_and_protocols/`:
  - Per-subtask `part_attempt_*_protocol.md` files (naming per updated rules)
  - `part_attempts_log.md` listing attempts and outcomes
  - Aggregated `fileId_protocol.md` summarizing the file-level pilot run
  - Phase 3 verification logs for the `flutter test` runs

Step 6 — Final commit

- After files are created/modified and verification completed, run:
  - git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/plans_and_protocols/2025-10-21_01_plan_impl_pilot.md
  - git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/plans_and_protocols/2025-10-21_01_protocol_analysis.md
  - git commit -m "2025-10-21_impl_pilot: add architect plan and protocol analysis"

Verification strategy and chosen Verification Level

- Verification Level chosen: 2 (Unit and Widget test verification)
- Reasoning:
  - The pilot scope explicitly restricts to unit and widget tests (no integration tests).
  - Level 2 verifies behavior of the updated rules by exercising unit/widget tests under the orchestrator's Phase 3 verification step.
- Verification steps:
  - Run the targeted `flutter test` command(s) listed above.
  - Capture console logs and save them to `plans_and_protocols/` as verification artifacts.

Tests to add/update and run commands

- Update: `test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart`
- Run (single-file verification):
  - flutter test test/widget/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator_test.dart

Risk analysis and regression considerations

- Risk: Changing `.roo` rules may be misinterpreted by existing orchestrator code or other orchestrator tasks expecting previous names.
  - Mitigation: Keep rule change limited to naming examples and explanatory text; do not change rule semantics beyond filename format.
- Risk: Tests may be flaky due to router/BLoC timing issues.
  - Mitigation: Use `whenListen` stubbing and `safe_pump` helper; run tests in isolation first.
- Risk: Unintended changes to production code if scope slips.
  - Mitigation: Enforce scope of work strictly; implementation subtasks are forbidden to edit files outside the defined list.

Required external dependencies or config changes

- None required for this pilot. The changes are limited to documentation and test code; no new packages are added.

Appendices

A — Files read during context assimilation

- [`requirements_tasks/.../goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-21_impl_pilot/goal.md:1)
- [`doc/architecture.md`](doc/architecture.md:1)
- [`doc/testing.md`](doc/testing.md:1)

B — Recursive listing of `lib/` (excerpt)

lib/config/routes/
lib/config/routes/app_route_info.dart
lib/config/routes/app_router.dart
lib/config/routes/app_routes.dart
lib/config/routes/route_utils.dart
lib/config/theme/
lib/config/theme/readme.me
lib/config/theme/theme.dart
lib/config/theme/tokens_extra.g.dart
lib/config/theme/tokens.g.dart
lib/config/theme/figma/
lib/config/theme/figma/tokens.json
lib/core/data/adapters/app_role_adapter.dart
lib/core/data/repositories/local_role_repository.dart
lib/core/data/storage/storage_initializer.dart
lib/core/design_system/atoms/background_svg.dart
lib/core/design_system/atoms/grid_layout.dart
lib/core/design_system/atoms/typography.dart
lib/core/design_system/atoms/inputs/likert_scale.dart
lib/core/design_system/config/layout/layout_config.dart
lib/core/design_system/config/layout/navigation.dart
lib/core/widgets/layout/scaffold_builder.dart
lib/features/therapist/plan_templates/plan_templates_routes.dart
lib/features/therapist/plan_templates/presentation/bloc/plan_templates_bloc.dart
lib/features/therapist/plan_templates/presentation/bloc/plan_template_detail_bloc.dart
lib/features/therapist/plan_templates/presentation/organisms/plan_list.dart
lib/features/therapist/plan_templates/presentation/widgets/plan_templates_orchestrator.dart

C — Decision log (short)

- Scope was intentionally kept to 2 files to satisfy the "<=4 files" constraint.
- If more than 4 files become necessary, the task will be split and resliced (recommended split described below).

Recommendations if the scope grows

- If fixing tests requires changes to more than 4 files (helpers, multiple tests, and rule files), split into:
  - Slice A: `.roo` rule updates (architectic/documentation change)
  - Slice B: Test fixes for `plan_templates` (code changes + tests)
  - Slice C: Verification orchestrator adjustments (orchestrator-specific code, if any)

Plan timestamp and author

- Plan created: 2025-10-21T20:24:00+02:00
- Author: Roo (architect)

End of plan.