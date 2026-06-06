# PR: roo-rules/testing-workflow-update

Branch: roo-rules/testing-workflow-update

Summary

- This PR implements the Testing Orchestrator updates described in the task. It adds the Test Part Orchestrator specification, updates orchestrator rules to use the Test File Orchestrator → Test Part Orchestrator → impl_test_part lifecycle, and provides templates and metrics for pilots and production use.

Changed / Added files

- .roo/rules-orchestrator/test_part_orchestrator.md (new)
- .roo/rules-orchestrator/orchestrator_testing_process.md (updated)
- .roo/rules-orchestrator/implementation_workflow.md (updated)
- .roo/rules-code/rules.md (updated)
- .roo/rules-architect/rules.md (updated)
- requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/plans_and_protocols/2025-10-20_03_rule_changes_and_gap_analysis.md (updated)
- requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/plans_and_protocols/templates/arch_test_plan_template.md (new)
- requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/plans_and_protocols/metrics.md (new)
- requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md (updated)

Rationale

- Consolidate testing orchestration into a hierarchical pattern that centralizes retries, improves observability, and preserves Phase 2/Phase 3 separation (tests only in Phase 3).
- Ensure every implementation attempt documents that it read the testing guidelines and produces a per-attempt protocol.
- Provide templates so architects and implementers produce consistent artifacts.

Key changes / highlights

- New `Test Part Orchestrator` spec with iterative attempt lifecycle and artifact schema.
- `arch_test_plan` template (required fields: guidelines_read, parts[], selectors, run_commands, acceptance_condition, recommended_max_attempts).
- `plans_and_protocols/metrics.md` template for per-part metrics (total_attempts_for_part, time_to_first_success_seconds, flakiness flags, attempts array).

Acceptance criteria for this PR

- The files listed above are present and accurate.
- `.roo/rules-orchestrator/implementation_workflow.md` explicitly states Phase 3 contains tests only.
- `.roo/rules-code/rules.md` enforces `guidelines_read` and per-attempt protocol fields.
- Templates exist under the task `plans_and_protocols/templates/` and `plans_and_protocols/metrics.md`.

How to create, commit and push (suggested commands)

git checkout -b roo-rules/testing-workflow-update
git add .roo/rules-orchestrator/test_part_orchestrator.md
git add .roo/rules-orchestrator/orchestrator_testing_process.md
git add .roo/rules-orchestrator/implementation_workflow.md
git add .roo/rules-code/rules.md
git add .roo/rules-architect/rules.md
git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/plans_and_protocols/2025-10-20_03_rule_changes_and_gap_analysis.md
git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/plans_and_protocols/templates/arch_test_plan_template.md
git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/plans_and_protocols/metrics.md
git add requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update/tasks/2025-10-20_impl_pilot/goal.md
git commit -m "roo(rules): update testing orchestrator, add Test Part Orchestrator and templates - refs requirements_tasks/process/AI_rules/code_and_guidelines/testing_workflow/tasks/2025-10-20_explore_roo_rules_update"
git push origin roo-rules/testing-workflow-update

Suggested PR body (paste into PR editor)

Summary:
- Implemented the Testing Orchestrator improvements: Test Part Orchestrator, clarified Phase 3 verification responsibilities, added arch_test_plan template and metrics schema.

What to review:
- Correctness and clarity of `acceptance_condition` syntax in `plans_and_protocols/templates/arch_test_plan_template.md`.
- Whether the `guidelines_read` requirement is clearly expressed and pragmatic for implementers.
- That Phase 3 remains the exclusive phase for running tests.
- Artifact paths and naming consistency for per-attempt protocols and aggregated logs.

Post-merge steps (what I will do after you merge)
1. Run the pilot for feature `plan_templates` (unit & widget tests only), recording all `plans_and_protocols` artifacts.
2. Append per-part metrics to `plans_and_protocols/metrics.md`.
3. Produce a pilot report including `fileId_protocol.md`, `part_attempts_log.md`, verification logs, and a short summary of lessons learned.

Requested reviewers
- @repo-maintainer (or you)

Notes
- If you prefer separate commits (one per logical change) instead of a single commit, tell me and I will prepare a split commit list.
- If you want me to run the pilot after you create or approve the PR (I cannot push or open the PR from here), I will run the pilot and then produce the artifact files for review.

End of PR description