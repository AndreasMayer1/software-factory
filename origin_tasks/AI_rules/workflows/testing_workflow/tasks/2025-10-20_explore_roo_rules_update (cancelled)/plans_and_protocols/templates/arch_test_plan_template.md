# Architect Test Plan Template

Author: Roo, AI Architect
Date: 2025-10-20

Purpose

- This template standardizes the `arch_test_plan_...` artifact required by the Test File Orchestrator.
- It ensures the Test Part Orchestrator can interpret acceptance conditions and orchestrate impl attempts.

Context

- test_file_path: <!-- e.g. test/widget/features/..._test.dart -->
- feature: <!-- e.g. plan_templates -->
- parent_testfile_orchestrator: <!-- task id -->
- author:
- created_at: <!-- ISO8601 -->

Guidelines read

- Minimum: [`doc/testing.md`](doc/testing.md:1)
- Other referenced guidelines: (list each file path and timestamp)

Summary

- Short summary of the problem the tests address and the intended behavior to validate.

Parts

- part_id: p1
  description: Short, one-line description of the behavior to implement/verify.
  acceptance_condition: |
    # Provide an explicit, machine-evaluable condition that the Test Part Orchestrator can check.
    # Examples:
    # expect(find.byKey('PLAN_LIST'), findsOneWidget)
    # tests named 'renders list' pass
  run_commands:
    - flutter test test/path/to/test_file_test.dart --plain-name "renders list" -d windows
  required_helpers:
    - test_helpers/setup_mock_services.dart
  mock_strategy:
    - list mocks and example stub responses; show how to register them in setUp.
  selectors:
    - find.byKey('PLAN_LIST')
    - find.text('No plans found')
  expected_widget_states:
    - PLAN_LIST exists and displays at least one item.
  fallbacks:
    - If widget not found, retry with a pumpAndSettle timeout; alternative is to mock the repository to return a default item.
  estimated_complexity: medium
  recommended_max_attempts: 5

- part_id: p2
  description: ...
  acceptance_condition: ...
  run_commands:
    - flutter test test/path/to/another_test.dart --plain-name "..."
  required_helpers:
    - ...
  mock_strategy:
    - ...
  selectors:
    - ...
  expected_widget_states:
    - ...
  fallbacks:
    - ...
  estimated_complexity: low
  recommended_max_attempts: 3

Verification commands (Phase 3)

- List the exact one-line commands the Testing Orchestrator should run during Phase 3 to verify the implemented parts.
- Example:
  - flutter test test/path/to/test_file_test.dart --plain-name "renders list" -d windows

Blocker checklist (for explore_test_blocker subtasks)

- Missing test helpers (list files)
- Hard-to-mock dependencies
- Non-deterministic behavior (timers, async boundaries)
- Platform-specific assets or services required
- Long-running network calls not stubbed

Observability & artifacts

- Specify where logs, diffs, and per-attempt protocols should be placed in the task folder:
  - plans_and_protocols/logs/
  - plans_and_protocols/part_attempts/
- Recommended filenames:
  - arch_test_plan_<timestamp>_<fileId>.md
  - part_attempt_<n>_protocol.md
  - part_attempts_log.md
  - fileId_protocol.md

Notes and guidance

- Acceptance conditions must be as specific as possible and, when possible, use `expect(...)` expressions that the orchestrator can match against test runner output.
- Keep parts small and focused to limit implementation scope per `impl_test_part`.
- If global helpers are missing, mark the part as blocked and include a required_helpers entry that triggers an `explore_test_blocker`.

Template checklist

- [ ] test_file_path
- [ ] guidelines_read entries
- [ ] at least one part with acceptance_condition and run_commands
- [ ] verification_commands
- [ ] blocker checklist completed

End of template