---
task_id: TASK-PROC-001-01
type: impl
parent_requirement: REQ-PROC-001
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2025-08-31
completed: 2025-08-31
after: []
awaiting: []
covers:
  sections: [SEC-01, SEC-02]
scope_description: "Update .clinerules and .clinerules-code files to incorporate context window management requirements"
requirements_version:
  commit: 7b08c37
  file: ../requirements.md
---

# Goal

The goal of this task is to update the `.clinerules` and `.clinerules-code` files to incorporate the new requirements regarding the AI's context window, as described in `requirements_tasks/AI_rules/context_window/2025-08-31_requirement.md`.

This includes:
- Adding rules for the AI to write a report markdown file containing relevant information when the user indicates a context condensation.
- Adding rules for the AI to re-read relevant files (guidelines, report, relevant files from report, and other implementation files) after context condensation.

# Suggested Steps

1.  Read the `requirements_tasks/AI_rules/context_window/2025-08-31_requirement.md` file to fully understand the new requirements.
2.  Analyze the existing `.clinerules` and `.clinerules-code` files to determine where the new rules should be added or modified.
3.  Formulate the exact text for the new rules, ensuring they are clear, concise, and align with the existing rule format.
4.  Apply the changes to the `.clinerules` and `.clinerules-code` files.
5.  Verify that the changes have been applied correctly.

# Relevant Context

-   The primary goal is to ensure the AI respects the context window management rules at all times.
-   The rules should guide the AI on how to behave before and after a context condensation event.
-   The rules should specify what information needs to be included in the report markdown file.
-   The rules should specify which files the AI needs to re-read after context condensation.