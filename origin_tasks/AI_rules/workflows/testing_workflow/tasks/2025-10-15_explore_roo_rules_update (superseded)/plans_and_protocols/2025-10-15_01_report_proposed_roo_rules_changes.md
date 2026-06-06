# Report: Proposed roo rules changes for enhanced testing workflow

Created: 2025-10-15T18:05:00Z

Summary:

This report analyzes existing roo rules and related policy files and proposes concrete edits to support the enhanced testing workflow described in
the requirement file [`requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/2025-10-04_requirement.md`](requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/2025-10-04_requirement.md:1).

Files analyzed:

- [`.roo/rules-architect/rules.md`](.roo/rules-architect/rules.md:1)
- [`.roo/rules-code/rules.md`](.roo/rules-code/rules.md:1)
- [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)
- [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)
- [`.roo/rules-orchestrator/impl_considerations_new_feature.md`](.roo/rules-orchestrator/impl_considerations_new_feature.md:1)
- [`.clinerules`](.clinerules:1)
- Project test runner script: [`scripts/integration_test_runner/run_individual_integration_tests.ps1`](scripts/integration_test_runner/run_individual_integration_tests.ps1:1)

Key issues / gaps

1. Orchestrator context window and subtask strategy
   - Current workflow in [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1) and related files assumes a mix of architect and code subtasks for implementation. The requirement suggests the orchestrator should avoid starting many `architect` subtasks for individual test files, because this fills the orchestrator's context and causes inefficiency. => Ja hier gebe ich dir noch mehr Infos: Es ist wichtig, dass ein Subtask sich um maximal ein Testfile kümmert. Noch besser wäre es sogar, wenn das Testfile in mehrere Teile aufgeteilt wird und für jeden Teil ein neuer Subtask zuständig ist. Das hält den Context der einelnen Tasks klein. Man könnte jetzt also denken: Ok, dann startet der Orchestrator einfach mehrere Subtasks hintereinander: Ein Subtask, um das testfile zu planen und in mehrere Teile zu teilen, dann für jeden Teil jeweils wieder einen Subtask. Das hält den Context der einzelnen Subtasks klein und die Anforderung ist erfüllt. Aber das reicht noch nicht! Denn der Orchestrator selbst hat ja ebenfalls einen Kontext. Er kann also nur eine begrenzte Anzahl an Subtasks starten, bevor der Kontext des Orchestrators selbst zu voll ist. Ich schlage vor, dass der Orchestrator nur einen Subtask für das Testen erstellt. Dieser fürs testen zuständige Subtask kann dann dem oben beschreibenen Prozess folgen und selbst wiederrum neue Subtasks erstellen. Dafür startet der Orchestrator diesen subtask ebenfalls im orchestrator mode. An der Stelle wirds jetzt etwas unübersichtlich und wir brauchen klare Bezeichnungen für die einezelnen Tasks. Da kannst du gerne Namen vorschlagen, ich nehme jetzt einfach irgendwelche. Wir haben den "äußeren" Orchestrator. Der äußere Orchestrator startet einen orchestrator subtask der sich um die Tests kümmert, "testing orchestrator". Der testing Orchestrator startet dann einen weiteren orchestrator subtasks für jede einzelne Testdatei, also ein "test file Orchestrator". Der test file orchestrator ist jetzt der orchestrator task der neue subtasks erstellt um den test zu planen, in Teile zu teilen und die Teile umzusetzen. Hierfür wird dann der architect mode verwendet. Das muss jetzt alles natürlich in den aktuellen Prozess integriert werden. Bitte machen einen Vorschlag dazu. Das muss natürlich gut verständlich dokumentiert werden.

2. Missing "test subtask lifecycle" and escalation policy
   - No single canonical document defines how to create, escalate, and stop when AI fails to implement more complex tests (unit -> widget -> integration). This is needed to meet the requirement "Start with the simplest tests and stop if the AI starts to fail to implement the more complex ones. When it stops, it should write a report."

3. Flakiness handling
   - The repo contains many notes about flakiness in [`doc/testing.md`](doc/testing.md:1) but no formal rule in `.roo` that instructs orchestrator on how to quarantine flaky tests, create flakiness investigation subtasks, or mark tests as flaky/todo.

4. Integration-test registration and runner maintenance
   - The project's integration test runner is a manual list at [`scripts/integration_test_runner/run_individual_integration_tests.ps1`](scripts/integration_test_runner/run_individual_integration_tests.ps1:1). There is no `.roo` rule enforcing that new integration tests must be added to that script.

5. Ambiguity about who runs tests and when
   - Some documents state "Tests can only be ran in code mode" (`.clinerules` / `doc/testing.md`) while others require that subtasks must not re-run tests (e.g., `.roo/rules-orchestrator/orchestrator_testing_process.md` line 9). We need consistent, implementable rules. => Ja das eine schließt das andere nicht aus. Ein (sub)task kann ja auch seinen Mode wechseln. Aber ja, hier ist natürlich trotzdem Luft nach oben, das sollte leichter verständlich sein ohne dass man an einen Widerspruch denkt.

Mapping: rules -> issues

- [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)
  -> Issue 1, 2
- [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)
  -> Issue 2, 3, 5
- [`.roo/rules-code/rules.md`](.roo/rules-code/rules.md:1)
  -> Issue 4, 5
- [`.roo/rules-architect/rules.md`](.roo/rules-architect/rules.md:1)
  -> Issue 1, 2
- [`.clinerules`](.clinerules:1)
  -> Issue 5 (policy statements referencing who may update which files)

Proposed changes (high level)

- Add a "Test Subtask Strategy" to the orchestrator workflow: orchestrator creates separate, scoped `code` subtasks for each test file to be created/modified (unit/widget/integration) rather than architect subtasks. => Damit bin ich nicht einverstanden, die Gründe habe ich oben schon beschrieben.
- Add a "Test Subtask Lifecycle" document that defines: start-simple-escalate rule; stop-and-report rule; commit-only policy for test creation; flakiness investigation protocol.
- Amend orchestrator testing process with explicit escalation and flakiness handling steps.
- Amend `rules-code` to require code subtasks that create integration tests to update the test runner script and to follow a commit-only practice (do not run full suites within subtask).
- Amend architect rules to limit architect-mode subtasks to planning, validation, and complex test-design tasks — not to author all test files. => Wir müssen allerdings beachten dass der Code mode sehr große probleme hat tests zu schreiben. Der Architect mode muss sehr genaue anleitungen schreiben, die der Code mode dann umsetzt. Darum werden die tests auch nicht direkt vom code mode ausgeführt, sobald er die Änderungen durchgeführt hat. Der Code mode würde dann nämlcih versuchen die Fehler zu beheben. Das wollen wir vermeiden.  
- Update acceptance and verification steps in `implementation_workflow` to make orchestrator responsible for final test execution and verification (Phase 3), with clear boundaries for subtasks.

Concrete proposed edits (pseudo-diffs)

1) `.roo/rules-orchestrator/implementation_workflow.md`

Proposed insertion into Phase 2 (after "Step 2: Implementation (`code` subtask):")

----
Insert (new paragraph)

[PROPOSED TEXT START]
Test Subtask Strategy:
- When the Scope of Work includes creating or modifying test files, the orchestrator must include the tests explicitly in the Scope of Work and create **one** dedicated `code` subtask per test file to be created or modified. Name pattern: `impl_tests_YYYY-MM-DD_<feature>_<index>`.
- Rationale: Test files are implementation artifacts. Creating a separate `architect` subtask for each test file quickly exhausts the orchestrator's context window and mixes planning responsibilities with executable work. Dedicated `code` subtasks keep responsibilities clear and allow parallelization.
- Each test subtask must:
  1. Create or update a single test file (unit/widget/integration) and any necessary test helpers.
  2. If an integration test is added, add the test's full name to [`scripts/integration_test_runner/run_individual_integration_tests.ps1`](scripts/integration_test_runner/run_individual_integration_tests.ps1:1) or add a small manifest file in the task `plans_and_protocols` describing how to run it.
  3. Stage (`git add`) and commit the new/modified test file(s) with a descriptive message referencing the task folder.
  4. Do NOT re-run the entire test suite inside the subtask. The parent orchestrator will run targeted tests during Phase 3 verification.
- Deliverable: a commit that adds the test file and an optional small run-manifest when required.
[PROPOSED TEXT END]

----

2) `.roo/rules-orchestrator/orchestrator_testing_process.md`

Proposed additions: explicit "Start-Simple-Escalate" and "Stop-and-Report" rules and "Flakiness Investigation" protocol.

Insert (new section)

[PROPOSED TEXT START]
Testing Escalation Policy:
1. Start with the simplest relevant test type:
   - Unit test -> Widget test -> Integration test.
   - The orchestrator shall order test subtasks accordingly.
2. If the executor (subtask) fails to implement a test at the current complexity level (for example, the code-mode subtask reports inability to create a reliable integration test), the orchestrator must:
   - Stop escalation at that level.
   - Create an architect-mode investigative task named `explore_test_blocker_<timestamp>` whose goal is to analyze why the AI failed and propose a human-reviewed remediation plan.
   - The investigative task must produce a short report (plans_and_protocols) documenting the failure, key error outputs, and recommended next steps.

Flakiness Investigation Protocol:
- If a test intermittently fails (evidence of flakiness), the orchestrator should:
  1. Create a `code` subtask `impl_flakiness_probe_<timestamp>` limited to running the failing test multiple times and collecting logs (if running tests is allowed in the environment); otherwise, collect failure traces and test environment details.
  2. If the probe shows non-deterministic behavior, open an architect `explore` subtask to analyze possible causes and recommend mitigation (e.g., timeouts, test harness issues, mocking gaps).
  3. Optionally quarantine the flaky test by adding a note to its test file and to the task `plans_and_protocols` with a `// TODO: flaky - investigate` marker.

Stop-and-Report:
- Whenever escalation stops because the AI cannot implement a more complex test, require a brief report in `plans_and_protocols` named `NN_protocol_test_implementation_blocked.md` containing:
  - Which test type failed and why (error logs or summary).
  - Which steps were attempted.
  - A recommended next action (human review, different mocking strategy, or temporary test quarantine).
[PROPOSED TEXT END]

----

3) `.roo/rules-code/rules.md`

Proposed changes: add rules for code-mode subtasks that create tests and for integration test registration.

Insert (append)

[PROPOSED TEXT START]
Test file creation (code-mode subtasks):
- When a code-mode subtask creates or modifies test files it must:
  1. Keep the change scoped to a single test file (plus immediate helpers) per subtask.
  2. If adding an integration test, update [`scripts/integration_test_runner/run_individual_integration_tests.ps1`](scripts/integration_test_runner/run_individual_integration_tests.ps1:1) by adding the test's full name to the `$testNames` array, or add a `plans_and_protocols` manifest describing how to run it.
  3. Stage and commit changes; do not chain `git add` and `git commit` in a single command. (Follow existing policy.)
  4. Do not run the full integration test suite in the subtask. Running targeted tests is allowed only when explicitly requested by the orchestrator and with the correct `-d windows` flag for platform-specific commands.
- Rationale: This keeps test file creation predictable, auditable, and aligned with the orchestrator's verification responsibilities.
[PROPOSED TEXT END]

----

4) `.roo/rules-architect/rules.md`

Proposed addition: clarify architect responsibilities vis-a-vis tests.

Insert into Step 1 / Step 2 clarifications:

[PROPOSED TEXT START]
Architect role for testing:
- Architect mode remains responsible for high-level test strategy, complex test design, and validating test assumptions (e.g., testability of a feature, necessary mocking strategies).
- Architect tasks should NOT be used to author every individual test file. For routine test file creation, use dedicated `code` subtasks created by the orchestrator as described in the "Test Subtask Strategy".
- Architect may create a single "test design" plan that lists the desired test files and their scope; the orchestrator will split those into per-file code subtasks.
[PROPOSED TEXT END]

----

5) New file: `.roo/rules-orchestrator/test_subtask_lifecycle.md`

Proposed content:

[PROPOSED TEXT START]
Test Subtask Lifecycle (summary)
- Purpose: Standardize lifecycle for code-mode test subtasks.
- Naming: `impl_tests_YYYY-MM-DD_<feature>_<index>`
- Steps the subtask must perform:
  1. Create/modify single test file and required helpers.
  2. Add/update test manifest if integration test (script or plans_and_protocols manifest).
  3. `git add` then `git commit` with message `test(impl): add <file> - refs <task-folder>`.
  4. Produce `plans_and_protocols/NN_protocol_test_file_added.md` describing the test purpose, run commands, and any environment notes.
- No test re-running inside the subtask unless explicitly directed by the orchestrator for targeted probes (flakiness probe).
[PROPOSED TEXT END]

----

Verification plan

1. Implement the proposed edits in a feature branch (create small apply_diff patches for each `.roo` file and add the new file).
2. Update one sample implementation task to follow the new pattern:
   - Orchestrator: create Scope of Work that includes 3 test files (unit, widget, integration).
   - Orchestrator: create three `impl_tests_*` code subtasks.
   - Each code subtask: create the test file, commit, and produce `plans_and_protocols` protocol file.
   - Orchestrator: run targeted tests per Phase 3 verification and follow Stop-and-Report if a subtask reported failing to implement a test.
3. Confirm that the new rules reduce architect-mode subtasks for test creation and that the orchestrator's context remains manageable.

Acceptance criteria (aligned with original task)

- The report identifies the rules to change (above) and proposes specific edits and a new file to implement the "Test Subtask Strategy" and "Test Subtask Lifecycle".
- The proposed edits are concrete and include explicit requirements (commit-only policy, per-file test subtasks, script manifest updates, flakiness protocol).
- The verification plan above is clear and actionable.

Next steps / Recommendations

1. Review and approve the proposed changes in this report.
2. If approved, I will create a new branch and apply the diffs to:
   - [`.roo/rules-orchestrator/implementation_workflow.md`](.roo/rules-orchestrator/implementation_workflow.md:1)
   - [`.roo/rules-orchestrator/orchestrator_testing_process.md`](.roo/rules-orchestrator/orchestrator_testing_process.md:1)
   - [`.roo/rules-code/rules.md`](.roo/rules-code/rules.md:1)
   - [`.roo/rules-architect/rules.md`](.roo/rules-architect/rules.md:1)
   - Add new file: [`.roo/rules-orchestrator/test_subtask_lifecycle.md`](.roo/rules-orchestrator/test_subtask_lifecycle.md:1)
3. After changes are applied, update the `requirements_tasks` plan and run a small pilot task (see Verification plan) to validate.

Appendix: example commit messages and subtask naming conventions

- Subtask names:
  - `impl_tests_2025-10-15_plan_templates_01`
  - `impl_flakiness_probe_2025-10-15_plan_templates_01`
- Example commit messages:
  - `test(impl): add test/unit/plan_template_service_test.dart - refs requirements_tasks/.../2025-10-15_explore_roo_rules_update`

End of report.