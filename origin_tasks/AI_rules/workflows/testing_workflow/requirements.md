---
id: REQ-PROC-005
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: implemented
effort: L
stakeholder: developer
created: 2025-10-04
after: []
blocks:
  - REQ-PROC-008  # Orchestrator workflow depends on this (symmetric)
trackable_items:
  sections:
    - id: SEC-01
      name: "User Story"
      heading: "# User Story"
    - id: SEC-02
      name: "Design Decisions"
      heading: "# Design Decisions"
---

# User Story

As a developer, I want a comprehensive testing workflow that provides clear guidelines for writing different types of tests and integrates seamlessly with the orchestrator workflow.

# Design Decisions

The testing workflow should include clear guidelines for writing:

*   Unit tests
*   Widget tests
*   Integration tests

The testing workflow should be:

*   Integrated with the orchestrator workflow, ensuring that tests are written and run as part of the feature implementation process.
*   Used in the refactoring workflow.
*   Satisfy all the requirements of the general workflow.

The testing workflow should:

*   Start with the simplest tests and stop if the AI starts to fail to implement the more complex ones. When it stops, it should write a report.
*   Integrate manual tests by the user.
*   Integrate a way for improving the process and the guidelines.
*   Handle test flakiness (to be explored).

The goal of the task is to find a better way to implement tests, because eventually the orchestrator's context window is full, and writing tests takes a lot of iterations. One seuggestion is that the orchestrator doesn't start subtasks in architect mode, but instead starts orchestrator task as subtasks for each test file that is created or modified.

## Related Tasks

### Cancelled Tasks
- TASK-PROC-005-03: Explore Roo Rules Update - Cancelled 2026-01-19 due to Roo Code → Claude Code migration. See REQ-PROC-011.

---
## Version History
Consolidated from:
- 2025-10-04_requirement.md (original)
Consolidation date: 2026-01-04
Pre-migration commit: 1d3a2f9
