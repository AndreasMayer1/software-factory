2025-11-01 — Plan: Create orchestrator templates and canonical inventory

Summary

This plan defines the canonical inventory of artifacts produced by orchestrator workflows and maps each artifact type to a template file that will be placed in `.roo-templates/`. It also prescribes filename conventions and the implementation steps to create the templates and update requirements to reference them.

Background

The orchestrator workflow requires that certain steps create files under `plans_and_protocols/`. To enforce consistency we will provide templates that specify filename pattern, goal, whitelist, blacklist, writing guidance and a skeleton example.

Important constraint

Per project rules, process guidance must not be placed under `doc/`. Templates and process rules must live in `.roo`, `.roo-templates`, or `requirements_tasks/`. This plan will therefore place templates in `.roo-templates/` and update `.roo` rules or requirement files to reference them.

Canonical inventory (artifact type → template filename)

- Plan (general): `.roo-templates/template_plan.md`
  - Use for architect-level and orchestrator-level plans saved as `YYYY-MM-DD_##_plan_<short-name>.md`
- Protocol (per-attempt / verification / generic protocol): `.roo-templates/template_protocol.md`
  - Use for protocol files saved as `YYYY-MM-DD_##_protocol_<short-name>.md`
- Analysis / Condensation report: `.roo-templates/template_analysis.md`
  - Use for exploratory analysis artifacts saved as `YYYY-MM-DD_##_analysis_<short-name>.md`
- Architect test plan (arch_test_plan): `.roo-templates/template_arch_test_plan.md`
  - Specialized fields: `guidelines_read`, `parts[]`, `selectors`, `acceptance_condition`, `expected_widget_states`, `run_commands`, `mock_strategy`, `required_helpers`
- Testfile orchestrator plan: `.roo-templates/template_testfile_orchestrator_plan.md`
  - Use for plans produced by Test File Orchestrator (naming: `YYYY-MM-DD_##_plan_testfile_<fileId>.md`)
- Part-attempt protocol (per attempt): `.roo-templates/template_part_attempt_protocol.md`
  - Named: `part_attempt_<n>_protocol.md` (placed under task `plans_and_protocols/`)
- Aggregated file protocol (fileId_protocol): `.roo-templates/template_file_protocol.md`
  - Named: `YYYY-MM-DD_##_<fileId>_protocol.md`
- Test run / verification protocol (captures stdout/stderr & exit code): `.roo-templates/template_test_run_protocol.md`
  - Named: `YYYY-MM-DD_##_test_run_protocol.md` or `YYYY-MM-DD_##_verification_log.txt` depending on content
- Metrics manifest: `.roo-templates/template_metrics.md`
  - Use to standardize metrics fields (attempts_per_part, time_to_first_success_seconds, flakiness_rate)
- Blocker / explore_test_blocker: `.roo-templates/template_blocker.md`
  - Named: `YYYY-MM-DD_##_explore_test_blocker_<short>.md` or `explore_test_blocker_<timestamp>.md`
- Scope-too-large protocol: `.roo-templates/template_scope_too_large.md`
- Git commit error protocol: `.roo-templates/template_git_commit_error_protocol.md`
- Final report / summary: `.roo-templates/template_final_report.md`

Filename conventions (enforced)

- All date-prefixed files under `plans_and_protocols/` must use: `YYYY-MM-DD_##_<type>_<short-name>.md` where `type` ∈ {plan, protocol, analysis, report}
- Per-attempt files use: `part_attempt_<n>_protocol.md` (no date prefix)
- Blocker files use: `YYYY-MM-DD_##_explore_test_blocker_<short>.md` or `explore_test_blocker_<timestamp>.md`
- Metrics: `plans_and_protocols/metrics.md` (single canonical filename per task)

Template content requirements (each `.roo-templates/*.md` template must include)

1. filename pattern (with placeholders and examples)
2. goal: why this file exists (1-3 sentence summary)
3. whitelist: required sections/fields (explicit list)
4. blacklist: forbidden content (e.g., production code, long diffs unless explicitly required, secrets)
5. writing guidance: tone, target depth, exact headings order
6. example skeleton: minimal valid content that satisfies whitelist

Special guidance for `template_arch_test_plan.md`

- Must require `guidelines_read` and include timestamp(s) of guidelines consulted (see rules in `.roo/rules-architect` and `doc/testing.md` — coding guidelines only; do not duplicate process guidance into `doc/`).
- Parts[] entries must contain: part_id, description, acceptance_condition (machine-readable), required_helpers, mock_strategy, selectors, expected_widget_states, run_commands, fallbacks, estimated_complexity, recommended_max_attempts

Implementation steps

1. Create `plans_and_protocols/` entry for this task with a plan file and protocol file:
   - [`requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/tasks/2025-11-01_add_new_templates_requ/plans_and_protocols/2025-11-01_01_plan_create_templates.md:1`](requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/tasks/2025-11-01_add_new_templates_requ/plans_and_protocols/2025-11-01_01_plan_create_templates.md:1)
   - [`requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/tasks/2025-11-01_add_new_templates_requ/plans_and_protocols/2025-11-01_02_protocol_template_creation.md:1`](requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/tasks/2025-11-01_add_new_templates_requ/plans_and_protocols/2025-11-01_02_protocol_template_creation.md:1)
2. Implement the `.roo-templates/` files listed above.
3. Update `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/2025-11-01_requirement.md` to reference the template filenames and instruct the orchestrator to pass those names to subtasks.
4. Add a small unit test skeleton under `test/unit/process/orchestrator_templates_test.dart` that asserts template files exist and the inventory mapping is present.
5. Commit changes in logical chunks (one commit for templates, one commit for requirement update, one for tests).

Acceptance criteria (validation checklist)

- [ ] All template files exist under `.roo-templates/` with required sections and example skeletons.
- [ ] `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/2025-11-01_requirement.md` updated to reference template filenames.
- [ ] `plans_and_protocols/2025-11-01_01_plan_create_templates.md` (this file) and `2025-11-01_02_protocol_template_creation.md` exist and are committed.
- [ ] Unit test skeleton under `test/unit/process/` added.

Risks and open questions

- Confirm final list of artifact types the orchestrator may produce; this inventory is based on current requirements and testing workflow pilots. If we find additional artifact types during template drafting, they will be added and the todo list updated.
- Confirm where to place any high-level process guidance that explains "how subtasks must use templates". Per project rules this must not go into `doc/`. Proposed location: `.roo/rules-orchestrator/templates_usage.md` or as an appended section in `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/2025-11-01_requirement.md`.

Next actions (after you approve this plan)

- I will create the `.roo-templates/` files listed above (template skeletons).
- I will update the orchestrator requirement file to reference template filenames and instruct the orchestrator to pass them to subtasks.
- I will add the unit test skeleton and the protocol file for verification.

Created by: Roo (architect)
Created at: 2025-11-01T05:52:00Z