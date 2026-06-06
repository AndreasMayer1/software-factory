---
task_id: TASK-PROC-002-01
type: impl
parent_requirement: REQ-PROC-002
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2025-10-02
completed: 2025-10-02
after: []
awaiting: []
covers:
  sections: [SEC-01]
scope_description: "Add widget test checklist to testing guidelines to improve AI's ability to write widget tests"
requirements_version:
  commit: 7b08c37
  file: ../requirements.md
---

Widget tests are very difficult to write for Google Gemini. Not as difficult as integration tests, but almost. 
My assumption is that setting up the correct state is challenging, as well as correct wait strategy after a simulated user interaction.

This task shall add a checklist to the testing guidelines to improve the writing of widget tests. 

Additional files are provided that contain information to inform this checklist. This information is from the web and might contradict the exisiting guidelines. Therfore it is important that it is not just copied into the guidelines, but adapted in a way that respects the current guidelines. In case of contradictions or alternative suggestions, don't add it to the guideline, but keep what is already defined there.

List the files in this folder to get the input.