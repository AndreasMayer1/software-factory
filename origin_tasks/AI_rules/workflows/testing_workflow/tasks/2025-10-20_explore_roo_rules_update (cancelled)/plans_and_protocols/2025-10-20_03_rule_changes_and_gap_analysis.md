# Report: 2025-10-20_03 — Proposed roo rule edits and gap analysis

Created: 2025-10-20T15:50:43Z

Context
- Requirement: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/2025-10-04_requirement.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/2025-10-04_requirement.md:1)
- Current task folder: [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/:1)
- Pilot goal (to be adjusted to remove explicit steps): [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md:1)
- Roo files modified so far: [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1), [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)

Purpose
- Produce a concise specification of the rule changes, a clear mapping "which subtask starts which subtask when", per-role step-by-step responsibilities, and a gap analysis of missing information required to implement the changes safely.

High-level change summary
1. Clarify orchestration hierarchy and responsibility boundaries: Outer Orchestrator -> Testing Orchestrator -> Test File Orchestrator -> Architect plans -> Code parts.
2. Preserve the iterative "leaf-level" testing cycle: code (run failing test) -> architect (plan) -> code (implement) -> commit -> stop (no re-run).
3. Default behavior: create and run unit & widget tests during Phase 3 verification using `flutter test <file>`. Integration tests are created/run only on explicit user request.
4. Introduce required artifacts and templates (architect plan template, per-subtask protocol files, integration run-manifest).
5. Add flakiness probe rules with defaults (N=5 runs), log storage and quarantine markers.

Files to change (proposed)
- Update: [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)
- Update: [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)
- Update: [`.roo/rules-code/rules.md`](.roo/rules-code/rules.md:1)
- Update: [`.roo/rules-architect/rules.md`](.roo/rules-architect/rules.md:1)
- Add new: [`.roo/rules-orchestrator/test_subtask_lifecycle.md`](.roo/rules-orchestrator/test_subtask_lifecycle.md:1)

Detailed role responsibilities and step-by-step approach

Outer Orchestrator (existing)
- When to create: After Phase 2 implementation is complete or when tests are explicitly in scope and the feature is ready for verification.
- Primary actions:
  1. Define Scope of Work and list files changed.
  2. Decide whether tests are required now; if yes, create exactly one Testing Orchestrator subtask: `testing_orchestrator_YYYYMMDD_<feature>`.
  3. Provide testing entry inputs: changed files list, plan references, and branch/commit range.
- Deliverables: `plans_and_protocols/outer_orchestrator_scope.md` (brief), and the created `testing_orchestrator` task reference.

Testing Orchestrator
- Purpose: Own the test program for the feature and run Phase 3 verification.
- Primary actions (step-by-step):
  1. Read parent scope, commit range, and `plans_and_protocols`.
  2. Produce an initial `plans_and_protocols/testing_scope.md` enumerating candidate test files and the proposed prioritization (unit first, widget next, integration only on request).
  3. For each selected test file, create a Test File Orchestrator task: `testfile_orchestrator_YYYYMMDD_<feature>_<fileId>` and attach `testing_scope.md` subset for that file.
  4. Wait for per-file protocols (arch plans and impl part commits).
  5. Run Phase 3 verification: run targeted unit and widget tests (`flutter test <file>`). If user explicitly requested integration tests, run them per manifest and with `-d windows`.
  6. If verification failures occur, trigger `impl_flakiness_probe_*` (for intermittent failures) or create `explore_test_blocker_*` (for deterministic unfixable failures).
- Deliverables: `plans_and_protocols/testing_orchestrator_protocol.md` (aggregated), verification logs, flakiness probe reports.

Test File Orchestrator
- Purpose: Own a single test file's lifecycle: plan, split, implement, and produce protocol.
- Step-by-step:
  1. Create `arch_test_plan_YYYYMMDD_<feature>_<fileId>` (architect) with a mandatory template (see below). Provide the test file path and the minimum context.
  2. Wait for the `arch_test_plan` output (must be a complete, low-level plan).
  3. From the architect plan, spawn one `impl_test_part_...` code subtask per part defined in the plan.
  4. Collect per-part protocol entries and, upon completion of all parts, produce `plans_and_protocols/<fileId>_protocol.md`.
  5. Hand protocol to Testing Orchestrator for Phase 3 verification.
- Deliverables: `arch_test_plan_...`, per-part `impl_test_part` tasks, `fileId_protocol.md`.

Architect plan (template and requirements)
- The architect subtask `arch_test_plan_...` must produce a file in `plans_and_protocols` containing:
  1. Guideline references read (minimum [`doc/testing.md`](doc/testing.md:1)).
  2. The proposed split: part list with short description and acceptance criteria per part.
  3. Exact selectors & finders to be used in tests (`find.byKey('...')`, `find.text('...')`) and rationale.
  4. Mock and DI notes: which mocks, how to register them in the test setup, and sample stubs/responses.
  5. Run commands for verification (unit/widget: `flutter test test/..._test.dart`; integration only with explicit user request and manifest).
  6. A small "blocker checklist": prerequisites that must be present before code subtasks start (e.g., test helper availability).
  7. Estimated complexity and recommended part ordering (smallest first).
- This template is mandatory; code subtasks should refuse to proceed without it.

Code subtask: `impl_test_part_...` (leaf-level iterative workflow)
- Required behavior (strict):
  1. Start in `code` mode, read the `arch_test_plan` artifact and the target test file.
  2. Run only the relevant failing test(s) (unit/widget) to capture full output and stack traces (example: `flutter test test/unit/..._test.dart -r json` when available).
  3. Switch to `architect` mode and pass the captured logs and context. Request a deterministic, low-level plan.
  4. Return to `code` mode and implement exactly the changes described by the architect plan.
  5. Stage and commit changes: `git add <files>`; `git commit -m "test(impl): <file> - refs <task-folder>"`.
  6. Do not re-run the failing test or any full verification in the same subtask. End the subtask and write a `plans_and_protocols/part_<idx>_protocol.md` entry describing the commit and rationale.
- Rationale: avoid code-mode unbounded retries and ensure architect oversight for test changes.

Flakiness probe and quarantine
- Default probe: run failing test N=5 times (configurable). Collect timestamps, machine env, and full traces.
- If non-deterministic failures observed, mark the test as quarantined by inserting `// TODO: flaky - investigate` in test source and adding `plans_and_protocols/<fileId>_flaky_report.md`.
- Testing Orchestrator creates `explore_test_blocker_...` (architect) for root cause analysis if flakiness persists.

Integration test policy (user-controlled)
- Integration tests are not created or run by default. The user must explicitly request integration tests.
- When requested, the Test File Orchestrator or the responsible code subtask must add the test's full name to [`scripts/integration_test_runner/run_individual_integration_tests.ps1`](scripts/integration_test_runner/run_individual_integration_tests.ps1:1) or add a `plans_and_protocols/<fileId>_integration_manifest.md` that contains the plain-name and run instructions.

Per-subtask artifacts (mandatory)
- `arch_test_plan_...` (architect) — required for any test file.
- `impl_test_part.../plans_and_protocols/part_<idx>_protocol.md` (code) — per part.
- `fileId_protocol.md` (test file orchestrator) — aggregates part protocols.
- `testing_orchestrator_protocol.md` — aggregates per-file protocols and verification logs.
- `integration_manifest.md` — only if integration tests are requested.

Enforcement and checks to add to rules
1. Architect plan template mandatory; code subtasks must verify presence before implementation.
2. Commit message template enforced in guidelines.
3. Require `plans_and_protocols` entries for all created test artifacts.
4. Testing Orchestrator must record verification logs and a short metrics line in its protocol (number of parts, architect round-trips, time-to-commit).

Missing information / open decisions (must be resolved before large-scale rollout)
- Metrics collection method: where to store aggregated metrics (suggest `plans_and_protocols/metrics.md`) and which fields to capture.
- Default N for flakiness probe and whether to allow adjustable per-task N.
- CI vs local test runs: clarify if the orchestrator will run tests in CI, local dev machines, or both (affects `flutter test` availability).
- Permissions & environment for running tests (some tests rely on platform-specific assets or services).
- Integration test resource usage policy (CI runtime, device requirements).
- A concrete architect-plan template file to place under `doc/` or `requirements_tasks/.../plans_and_protocols/` (I propose to add `templates/arch_test_plan_template.md`).

Proposed next steps
1. Finalize the architect-plan template and place it in the task `plans_and_protocols` or `doc/` as agreed.
2. Implement the `.roo` edits listed above on a feature branch `roo-rules/testing-workflow-update` and open a PR for review.
3. Remove explicit step-list from the pilot goal file so the pilot must derive steps from the new rules; replace with objective, scope, acceptance criteria and deliverables.
4. Run the small pilot (one feature) and collect the metrics described above.

If you confirm I will:
- Create the architect-plan template file.
- Apply the proposed edits to the remaining `.roo` files: [`.roo/rules-code/rules.md`](.roo/rules-code/rules.md:1) and [`.roo/rules-architect/rules.md`](.roo/rules-architect/rules.md:1), and add [`.roo/rules-orchestrator/test_subtask_lifecycle.md`](.roo/rules-orchestrator/test_subtask_lifecycle.md:1).
- Update the pilot goal to remove explicit steps and leave objectives only.

End of report
## Addendum: Final decision — Test Part Orchestrator iterative attempt lifecycle
Date: 2025-10-20T18:42:07Z

Decision summary
- Final decision: adopt the iterative Test Part Orchestrator lifecycle described in [`.roo/rules-orchestrator/test_part_orchestrator.md`](.roo/rules-orchestrator/test_part_orchestrator.md:1). The Test Part Orchestrator manages repeated, one-shot `impl_test_part` attempts up to a configurable MAX_ATTEMPTS (default: 5). On success the loop stops; on exhaustion or an explicit blocker request it creates an `explore_test_blocker_<timestamp>` (architect) with aggregated artifacts.
- This replaces the previous single-attempt-only addendum: the iterative approach preserves per-attempt observability while allowing pragmatic retries coordinated by the orchestrator.

Rationale
- Multiple, small, guided attempts commonly converge faster than a single-shot escalation when the required fix is localized (e.g., mocks, timeouts, widget pump ordering). Centralizing retries in the Test Part Orchestrator keeps `impl_test_part` contexts small and records each attempt for observability and post-mortem.
- Mandatory precondition retained: every `impl_test_part` attempt MUST read `doc/testing.md` and record `guidelines_read: <ISO8601 timestamp>` in its `part_attempt_<n>_protocol.md`.

Status of existing orchestrator files (current)
- [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1) — updated to reference the Test Part Orchestrator iterative loop and to point to the authoritative spec.
- [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1) — updated to clarify Phase 2/Phase 3 responsibilities and to reference the Test Part Orchestrator for test-writing parts.
- [`.roo/rules-orchestrator/impl_considerations_bug_fixing.md`](.roo/rules-orchestrator/impl_considerations_bug_fixing.md:1) — checklists extended to note the TPO retry pattern and mitigation guidance.
- [`.roo/rules-orchestrator/test_part_orchestrator.md`](.roo/rules-orchestrator/test_part_orchestrator.md:1) — authoritative spec for lifecycle, artifacts and metrics (already created).

Concrete changes required (per-file plan) — reconciled for iterative flow
1) Update [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)
   - Ensure language explicitly references the Test File Orchestrator → Test Part Orchestrator (iterative) → `impl_test_part` (one-shot-per-attempt) loop.
   - Document MAX_ATTEMPTS default and escalation behavior, and where per-attempt artifacts are stored.

2) Update [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)
   - Clarify: test-writing parts flow is Test File Orchestrator -> Test Part Orchestrator -> repeated `impl_test_part` attempts -> stop on acceptance_condition or escalate after MAX_ATTEMPTS.

3) Finalize [`.roo/rules-orchestrator/test_part_orchestrator.md`](.roo/rules-orchestrator/test_part_orchestrator.md:1)
   - Confirm artifact schema, naming conventions, and metrics (plans_and_protocols/metrics.md).

4) Confirm [`.roo/rules-code/rules.md`](.roo/rules-code/rules.md:1) enforcements
   - `impl_test_part` must record `guidelines_read`, produce `part_attempt_<n>_protocol.md`, and may optionally run targeted verification; the attempt must record `verification_performed` and `verification_result`.

5) Confirm [`.roo/rules-architect/rules.md`](.roo/rules-architect/rules.md:1) inclusion
   - `arch_test_plan` must include explicit `acceptance_condition`, `run_commands`, `required_helpers`, and `recommended_max_attempts` per part.

Per-subtask artifacts (mandatory) — reconciled
- Each attempt: `part_attempt_<n>_protocol.md` containing:
  - subtask_id, attempt_number, guidelines_read, commands_run, logs_path, modified_files, commit_hash, verification_performed, verification_result, notes.
- Test Part Orchestrator aggregates attempts into `part_attempts_log.md` and writes per-file `fileId_protocol.md`.
- On escalation: `explore_test_blocker_<timestamp>` attaching aggregated attempts, diffs, and logs.

Acceptance criteria for the reconciled decision
- The repository contains [`.roo/rules-orchestrator/test_part_orchestrator.md`](.roo/rules-orchestrator/test_part_orchestrator.md:1) specifying the iterative lifecycle.
- Core rules were updated to reference TPO iterative behavior: [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1) and [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1).
- `impl_test_part` protocol schema is present and enforced by code rules (`.roo/rules-code/rules.md`).
- `arch_test_plan` template includes `recommended_max_attempts` and clear `acceptance_condition`.
- Metrics template exists at `plans_and_protocols/metrics.md` and is used by TPO to record per-part metrics.
- The pilot goal remains objective-only so the pilot derives the exact sequence from the rules.

Proposed next steps (unchanged)
- Finalize any remaining minor textual edits to `.roo` files and commit them on branch `roo-rules/testing-workflow-update`.
- Open PR with a summary and this reconciled report.
- Run the pilot for `plan_templates` (unit/widget only) and collect artifacts in `plans_and_protocols/`.

End of addendum.