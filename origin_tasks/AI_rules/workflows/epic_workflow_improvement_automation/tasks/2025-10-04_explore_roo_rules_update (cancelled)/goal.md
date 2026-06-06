---
task_id: TASK-PROC-006-01
type: explore
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: cancelled
cancellation_reason: "Tool migration from Roo Code to Claude Code. Roo rules no longer applicable. See REQ-PROC-011 for deprecation strategy."
cancelled_date: 2026-01-19
effort: L
created: 2025-10-04
after: []
awaiting: []
covers:
  sections: [SEC-01, SEC-02]
scope_description: "Explore and propose changes to roo rules to support automated workflow improvement"
requirements_version:
  commit: 1d3a2f9
  file: ../requirements.md
---
# Goal

Explore how to update the existing roo rules to satisfy the requirements for the automated workflow improvement.

# Specification

Analyze the existing roo rules in the `.roo` directory and in the .clinerules file.
Identify the rules that need to be updated to support the automated workflow improvement.
Propose changes to the roo rules to support the automated workflow improvement.
Document the proposed changes in a report.

# Acceptance Criteria

The report clearly identifies the rules that need to be updated and proposes specific changes to support the automated workflow improvement.