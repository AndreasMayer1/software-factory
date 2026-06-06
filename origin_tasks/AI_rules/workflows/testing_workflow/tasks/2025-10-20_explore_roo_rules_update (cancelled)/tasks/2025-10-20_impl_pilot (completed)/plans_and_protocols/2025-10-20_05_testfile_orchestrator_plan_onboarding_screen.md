# Test File Orchestrator Plan — Onboarding Screen
Date: 2025-10-20T20:21:56Z

Purpose
- Orchestrate implementation of widget tests for the onboarding screen implemented at [`lib/features/role_selection/presentation/screens/onboarding_screen.dart`](lib/features/role_selection/presentation/screens/onboarding_screen.dart:1).
- Target test file to produce: [`test/features/role_selection/presentation/screens/onboarding_screen_test.dart`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)

Scope of Work (strict)
- Allowed files to create/modify (ONLY these):
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_05_testfile_orchestrator_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_05_testfile_orchestrator_plan_onboarding_screen.md:1)
  - [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md:1)
  - [`test/features/role_selection/presentation/screens/onboarding_screen_test.dart`](test/features/role_selection/presentation/screens/onboarding_screen_test.dart:1)

Test split (parts)
- Part 1 — Render & accessibility
  - Verify core static UI elements render and are accessible:
    - Onboarding title text
    - Supporting description text (if present)
    - Both role selection buttons (Client, Therapist) present and enabled
    - Semantic labels accessible for screen readers
  - High-level acceptance: targeted assertions confirm presence + semantics.

- Part 2 — Initial state & stored-role behavior
  - Verify behavior when stored role is present vs absent:
    - Stored role == null -> show selection UI (both buttons)
    - Stored role == Client -> auto-navigate to client entry screen
    - Stored role == Therapist -> auto-navigate to therapist entry screen
  - Acceptance: navigation detection using the finder recommended by Architect.

- Part 3 — Role selection interactions & navigation
  - Tap each role button:
    - Verify repository/service is updated with the selected role (mocked response verification)
    - Verify navigation to the correct next screen for each role
  - Acceptance: targeted assertions confirm write occurred and navigation to target screen.

- Part 4 — Optional edge cases (if present)
  - E.g., button disabled states, error flows — Architect will enumerate if applicable.

Naming & orchestration conventions
- Architect subtask to create the arch test plan:
  - Subtask name (for reference): `arch_test_plan_onboarding_screen` (mode: `architect`)
  - Architect must produce [`2025-10-20_06_arch_test_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md:1) and commit it.
- Code subtask naming pattern for attempts:
  - `impl_test_part_2025-10-20_onboarding_screen_p<partIdx>_a<attemptIdx>` (mode: `code`)
- MAX_ATTEMPTS: 8
- Per-part acceptance condition: PASS when the architect-provided acceptance checker (exact assertions) returns true in a targeted verification run.

Per-attempt artifacts (location)
- All per-attempt artifacts must be placed under the plans_and_protocols folder above:
  - `part_attempt_<n>_protocol.md` (per attempt)
  - `part_attempts_log.md` (aggregated log)
  - `fileId_protocol.md` (final aggregated protocol on success or escalation)
  - If an escalation is required, produce `explore_test_blocker_<timestamp>.md` in the same folder with aggregated logs.

Phase 3 (final verification) command (Testing Orchestrator)
- flutter test test/features/role_selection/presentation/screens/onboarding_screen_test.dart

Helpers to inspect & prefer (Architect will confirm and reuse)
- [`test/helpers/test_app_wrapper.dart`](test/helpers/test_app_wrapper.dart:1)
- [`test/helpers/safe_pump.dart`](test/helpers/safe_pump.dart:1)
- [`test/helpers/ui_test_helper.dart`](test/helpers/ui_test_helper.dart:1)
- [`test/helpers/mock_screen_size_service.dart`](test/helpers/mock_screen_size_service.dart:1)
- [`test/helpers/bloc_test_helper.dart`](test/helpers/bloc_test_helper.dart:1)
- [`test/helpers/fake_path_provider_platform.dart`](test/helpers/fake_path_provider_platform.dart:1)
- [`test/helpers/more_screen_test_helpers.dart`](test/helpers/more_screen_test_helpers.dart:1)
- [`test/helpers/mock_list_item_actions.dart`](test/helpers/mock_list_item_actions.dart:1)

Failure / blocker rules
- If the Architect or Code subtasks determine that changes to production `lib/` files are required (or more than 4 files must be modified), DO NOT change production code. Instead produce:
  - `2025-10-20_04_blocker_protocol.md` in this plans_and_protocols folder describing required changes and stop.

Git commit messages (required)
- Pre-change snapshot:
  - git commit --allow-empty -m "test(onboarding): pre-change snapshot - refs 2025-10-20_impl_pilot"
- Plan file commit:
  - git add <file>
  - git commit -m "test(onboarding): add testfile orchestrator plan - refs 2025-10-20_impl_pilot"

Next steps after this file is committed
1. Spawn Architect subtask `arch_test_plan_onboarding_screen` (mode: `architect`) with detailed instructions to inspect the production file and produce the arch test plan file at [`2025-10-20_06_arch_test_plan_onboarding_screen.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/plans_and_protocols/2025-10-20_06_arch_test_plan_onboarding_screen.md:1).
2. Wait for Architect completion. If Architect requests new helpers or detects >4 files must change, create `2025-10-20_04_blocker_protocol.md` and stop.
3. When arch plan is present, orchestrate the iterative `impl_test_part` code subtasks per the arch plan.

---