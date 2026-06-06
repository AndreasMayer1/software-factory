---
task_id: TASK-PROC-008-05
type: impl
parent_requirement: REQ-PROC-008
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2025-11-01
completed: 2025-11-01
after: [TASK-PROC-008-04]
awaiting: []
covers:
  acceptance_criteria: [AC-10, AC-11, AC-12, AC-13]
  sections: [SEC-03]
scope_description: "Create canonical template system for orchestrator workflow artifacts (plans, protocols, analyses)"
requirements_version:
  commit: 1d3a2f9
  file: ../requirements.md
---

2025-11-01 — Add new templates required by orchestrator workflow

Goal

Create a set of standardized markdown templates in `.roo-templates/` for every mandatory artifact produced by the orchestrator workflow, and update the orchestrator requirement to reference those template filenames. The templates must be explicit about filename pattern, goal, whitelist, blacklist, writing guidance, and include an example skeleton. They will be used by the orchestrator and passed to subtasks when those subtasks must create plans, protocols, analyses or other artifacts.

Background

The orchestrator workflow requires that "certain steps create files as result of their task" and "There must be a template for each of those mandatory files in the folder `.roo-templates`" (see requirement file: [`requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/2025-11-01_requirement.md:1`](requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/2025-11-01_requirement.md:1)).

Objectives

- Produce a canonical inventory of orchestrator-generated file types and the template that each requires.
- Implement markdown templates in `.roo-templates/` that include: filename pattern, why the file exists (goal), whitelist (what must be present), blacklist (what must not be present), writing guidance (structure, tone, depth), and a skeleton example.
- Update the orchestrator workflow requirement to explicitly reference the template filenames and require the orchestrator to pass the template names to subtasks.
- Add documentation and tests to verify template existence and that orchestrator references templates when creating subtasks.

Scope

In scope:

- Inventory of mandatory artifact types produced by the orchestrator workflow.
- Creation of template specification documents and .md template files in `.roo-templates/`.
- Small updates to the orchestrator workflow requirement file to reference template filenames.
- Documentation describing how to use the templates.
- Unit tests that assert templates exist and orchestrator references them when creating subtasks (test scaffolding only; detailed testing of orchestrator runtime behavior may be added later).

Out of scope:

- Rewriting existing plans/protocols created earlier.
- Implementing changes to the orchestrator runtime beyond passing template names to subtasks (no orchestration engine code changes in this task).

Acceptance criteria (explicit)

1. A canonical inventory file exists listing all artifact types the orchestrator may produce (plans, protocols, analyses, reports, test plans, etc.) and maps each artifact type to the intended template filename. (e.g., `template_plan.md`).
2. For every artifact type in the inventory there is a corresponding template file created under `.roo-templates/`. Each template file contains the required sections:
   - filename pattern (with placeholders)
   - goal (why the file is needed)
   - whitelist (required content items)
   - blacklist (forbidden content)
   - writing guidance (structure, tone, depth)
   - example skeleton (minimal example showing required fields)
3. The orchestrator workflow requirement file [ `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/2025-11-01_requirement.md:1` ] is updated to reference the canonical template filenames and instruct the orchestrator to pass template names to any created subtasks.
4. Documentation added at `doc/process/orchestrator_templates.md` explains how templates are named, where they live, how subtasks should reference and consume them, and how to extend them.
5. Unit test(s) exist under `test/unit/process/` (suggested: `orchestrator_templates_test.dart`) that assert:
   - template files exist in `.roo-templates/`
   - the inventory maps expected artifact types to template filenames
6. A plans_and_protocols record for this task is created: `plans_and_protocols/2025-11-01_01_plan_create_templates.md` (implementation plan) and `plans_and_protocols/2025-11-01_02_protocol_template_creation.md` (protocol / verification).

Deliverables

- `.roo-templates/template_plan.md`
- `.roo-templates/template_protocol.md`
- `.roo-templates/template_analysis.md`
- `.roo-templates/template_test_plan.md` (or `template_arch_test_plan.md` depending on naming convention)
- `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/plans_and_protocols/2025-11-01_01_plan_create_templates.md`
- `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/plans_and_protocols/2025-11-01_02_protocol_template_creation.md`
- `doc/process/orchestrator_templates.md`
- `test/unit/process/orchestrator_templates_test.dart` (skeleton tests)

Recommended approach (high level steps)

1. Produce the canonical inventory of artifact types by scanning the orchestrator workflow and other related process docs.
2. Define filename conventions and placeholders for timestamp/ordinal and suffixes (e.g. `YYYY-MM-DD_##_plan_<name>.md`), and add these rules to the inventory.
3. Draft template specifications (one file per artifact type) including whitelist/blacklist and example skeletons.
4. Implement the templates in `.roo-templates/`.
5. Update the orchestrator requirement file to reference template filenames and require orchestrator to pass template names to subtasks.
6. Create the two plans_and_protocols artifacts documenting the plan and verification protocol.
7. Add small unit tests that check for template presence and inventory correctness.
8. Commit changes and produce completion report.

Files to create / modify

- Add: `.roo-templates/template_plan.md`
- Add: `.roo-templates/template_protocol.md`
- Add: `.roo-templates/template_analysis.md`
- Add: `.roo-templates/template_test_plan.md`
- Add: `doc/process/orchestrator_templates.md`
- Add: `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/plans_and_protocols/2025-11-01_01_plan_create_templates.md`
- Add: `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/plans_and_protocols/2025-11-01_02_protocol_template_creation.md`
- Modify: `requirements_tasks/process/AI_rules/code_and_guidelines/orchestrator_workflow/2025-11-01_requirement.md` (reference template filenames)

Testing and verification

- Run unit tests: `flutter test test/unit/process/orchestrator_templates_test.dart -d windows`
- Manually inspect `.roo-templates/` to verify each template contains the required sections and example skeletons.
- Verify the updated requirement file contains the template filenames and explicit instruction that the orchestrator must pass template names to subtasks.

Stakeholders / reviewers

- Process owner: [mention if known]
- Orchestrator implementation owner (if different)
- Documentation owner

Time estimate

- Inventory & filename convention: 1-2 hours
- Draft templates (4 files): 2-3 hours
- Documentation + tests + requirement update: 1-2 hours
- Buffer & review: 1 hour

Notes

- Follow doc/testing.md and doc/architecture.md where relevant when adding tests or modifying requirement files.
- If additional artifact types are discovered while creating the inventory, add them to the inventory and create templates; update the todo list accordingly.
- After the work is completed and verified by the reviewer, mark the task completed using `scripts/complete_task.ps1` with the task folder path.

Created by: Roo (architect)
Created at: 2025-11-01T05:52:00Z