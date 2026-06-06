# Cross-Reference Classifications — REQ-PROC-001

Target: `requirements_tasks/process/AI_rules/coding_standards/context_window/requirements.md`
Decided: 2026-05-26 by developer (TASK-PROC-058-07, automated-mode answer.md)
Source proposal: `2026-05-25_cross_ref_gaps.md`

Developer approved the recommendations verbatim.

## Apply

### semantic (add to `## Related Requirements`)

- **REQ-PROC-008** — Orchestrator Workflow
  - path: `requirements_tasks/process/AI_rules/workflows/orchestrator_workflow/requirements.md`
  - rationale: Orchestrator workflow manages context budget via subtasks; REQ-PROC-001's Design Decision references orchestrator mode as a context-management mechanism.

- **REQ-PROC-058** — Implementation Task Planning (task-derive-from-requ)
  - path: `requirements_tasks/process/AI_rules/requirements_management/implementation_task_planning/requirements.md`
  - rationale: REQ-PROC-058 consumes REQ-PROC-001's S1–S4 sizing signals to plan tasks; REQ-PROC-058 already references REQ-PROC-001 one-way, the reciprocal back-reference belongs here.

### hard (add to `after:`)

(none)

### ignore (record reason in protocol)

- **REQ-PROC-046** — Code Quality: REQ-PROC-046 already documents REQ-PROC-001 as "unrelated; concerns conversational context, not code quality." Honour that assessment.
- **REQ-PROC-005** — Testing Workflow: incidental prose mention of "context window".
- **REQ-PROC-026** — UN→Design Bridge: keyword "escalation" used re visual hierarchy emphasis; unrelated.
- **REQ-PROC-032** — metadata `design_decisions`: incidental mention.
- **REQ-PROC-051** — Python Code Quality: gate-boilerplate use of "escalation"; different sense.
- **REQ-PROC-052** — Privacy/Security Gates: same gate boilerplate.
- **REQ-PROC-056** — Dependency Governance: same gate boilerplate.

## Path notes for the apply agent

The target requirement currently has:
- `after: []`
- `blocks: []`
- **no `## Related Requirements` section** — create it (insert before `## Version History` at the end of the file).

Both `semantic` entries are in folders sibling to/below the target's folder. Use these relative paths from the target file:

- REQ-PROC-008 → `../../workflows/orchestrator_workflow/requirements.md`
- REQ-PROC-058 → `../../requirements_management/implementation_task_planning/requirements.md`
