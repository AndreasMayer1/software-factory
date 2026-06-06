---
task_id: TASK-PROC-034-02
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-04
effort: S
created: 2026-03-04
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-01]
scope_description: "Create requirements_tasks/RELEASES.md — the single source of truth for all release definitions — with the initial release plan."
requirements_version:
  commit: c8c9ac7
  file: ../requirements.md
---

# Goal: Create RELEASES.md — Release Definition Document

## What

Create the file `requirements_tasks/RELEASES.md` following the format defined in REQ-PROC-034 SEC-01.

## Scope

- Create `requirements_tasks/RELEASES.md` with YAML frontmatter + Markdown body
- Populate with the initial 6 releases defined in REQ-PROC-034:
  - `0.0.1` Alpha - Data Transfer
  - `0.0.2` Alpha - Data Transfer Encryption
  - `0.0.3` Alpha - Storage Encryption
  - `0.1.0` Beta MVP
  - `0.2.0` Beta 2 (TBD)
  - `1.0.0` Release (TBD)
- Each release entry must include all required fields: `version`, `name`, `status`, `description`
- Optional fields (`goals`, `scope_boundaries`, `planned_date`) should be populated where content is known; set to `null` / omit where TBD
- Markdown body section should document the release lifecycle (`planned → active → released`) and how to add new releases

## Format Reference

See `requirements.md` SEC-01 for the exact YAML structure. The `releases` list lives in the YAML frontmatter; the Markdown body provides human-readable context.

## Out of Scope

- Modifying any scripts or skills (separate tasks)
- Assigning releases to existing requirements/tasks (TASK-PROC-034-07)
