# FINAL REPORT: A Unified Framework for AI-Driven Development
**Date:** 2025-10-09T16:30:11Z
**Status:** Final & Approved

## 1. Executive Summary

This report concludes our exploration task to improve the AI process. Through a collaborative, interactive brainstorming process, we have designed a new, unified framework that clarifies and enhances the workflows for both the `architect` and `orchestrator` modes. This framework introduces a formal process for exploration, creates a single robust workflow for all implementation tasks, and, most importantly, establishes an **iterative "Analysis & Validation Loop"** to ensure plans are sound before implementation begins.

## 2. The "Interactive Brainstorming Workflow" for Architect Mode

This new workflow formalizes the process for all `explore_` tasks, ensuring a collaborative and structured approach to problem-solving.

-   **Process:**
    1.  **Information Gathering & Initial Ideation:** The AI gathers project context and forms preliminary ideas.
    2.  **Present and Inquire:** The AI presents its findings and asks for user input.
    3.  **Iterative Deepening:** A collaborative loop of feedback and refinement.
    4.  **Conclusion Trigger:** The user decides when the exploration is complete.
    5.  **Flexible Outcomes:** Can result in a report, an `impl_` task, or a new `explore_` task.

## 3. The Unified "Implementation Workflow" for Orchestrator Mode

This single, maintainable workflow will replace the previous, fragmented processes. It provides a clear structure for all `impl_` tasks.

-   **Core Phases:**
    1.  **Phase 1: Analysis & Validation Loop:**
        a.  **Analyze:** The orchestrator performs a high-level analysis and defines the initial "Scope of Work".
        b.  **Validate:** A subtask in `architect` mode verifies a checklist of the plan's core assumptions.
        c.  **Loop or Proceed:** If validation fails, the orchestrator **must** update the plan and re-validate, repeating the loop. If validation succeeds, the orchestrator proceeds to the next phase.
    2.  **Phase 2: Iterative Implementation Cycle:** The core "Analyze -> Implement -> Verify" loop for each part of the task.
    3.  **Phase 3: Final Integration Verification:** A final phase to run all relevant tests and ensure the feature is complete and stable.

-   **Delegation to Specialized Workflows:**
    -   **Test Debugging:** If any test fails, the orchestrator **must** delegate to the specialized process in `orchestrator_testing_process.md`.

-   **Verification Levels:**
    -   **Level 0 (Manual):** A user-driven check for UI-heavy tasks.
    -   **Level 1 (Code Review):** The default check against the plan and guidelines.
    -   **Level 2 (Static Analysis):** L1 + `flutter analyze`.
    -   **Level 3 (Targeted Test):** L1 + L2 + running a single, relevant, pre-existing test.

## 4. Supporting "Considerations" Documents

New, lightweight documents will be created to provide context for different task types:
-   `impl_considerations_new_feature.md`
-   `impl_considerations_refactoring.md`
-   `impl_considerations_bug_fixing.md`

## 5. New Guidelines

-   **Scope Enforcement:** A strict rule forbidding file modifications outside the defined "Scope of Work".
-   **Iterative Test Creation:** A rule mandating that test setups are built and stabilized before writing the full suite of test cases.

## 6. Next Steps

This exploration task is now complete. The clear outcome is the creation of a new `impl_` task to implement the changes detailed in this report.