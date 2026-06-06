# Plan to Update .clinerules and .clinerules-code

This plan outlines the changes needed to incorporate the new context window management rules into the AI's guidelines.

## 1. Update .clinerules

A new section, "Context Window Management," will be added under "Task Management and Workflow."

```diff
--- a/.clinerules
+++ b/.clinerules
@@ -98,6 +98,20 @@
 -   If a subtask reports being blocked due to plan discrepancies, external issues (like tooling problems), or persistent test failures preventing verification, the orchestrator must first analyze the subtask's findings (including any generated documentation like `doc-temp/.../blocker_summary.md`). The orchestrator must then update the relevant plan documents to address the issue before creating new, correctly scoped subtasks for implementation or fixing.
 
+## Context Window Management
+
+-   If the user tells the AI that he wants to condense the context, the AI must write a report markdown file that contains all relevant information. Relevant information is:
+    -   What steps have been tried to solve the task so far?
+    -   In which files are those steps documented?
+    -   What worked and what didn't?
+    -   What could be the next step to solve the task and why?
+    -   Which files are relevant to work on the task?
+-   After the report file is written, the AI must ask the user if he already condensed the context.
+-   If the user tells the AI that the context has been condensed, the AI must read all relevant files again:
+    -   The guidelines.
+    -   The created report from before.
+    -   All relevant files stated in the report.
+    -   All relevant implementation files beyond that.
+
 # Development and Testing
 
 -   When running the Flutter commands that need a platform (e.g., integration tests), always provide `-d windows`. Otherwise, the user is asked which platform shall be used, and you get stuck.

```

## 2. No Changes to .clinerules-code

The new rules are strategic and procedural, making them a better fit for the general `.clinerules` file. The `.clinerules-code` file is more focused on specific coding practices and tool usage, so no changes are needed there at this time.
