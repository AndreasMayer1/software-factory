---
task_id: TASK-PROC-031-02
type: impl
parent_requirement: REQ-PROC-031
urgency: 3
urgency_reason: "U3-WASTE"
impact: 3
impact_reason: "I3-QUALITY"
status: completed
effort: XS
created: 2026-02-07
completed: 2026-02-07
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add rules to CLAUDE.md preventing verbose WHY comments in skill files, and clean up existing violations"
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Add Rules to Prevent Verbose WHY Comments in Skill Files

## Objective

Add explicit scoping rules to CLAUDE.md Section 5 that confine `/// Why:` comments to code files only, and forbid them in `.claude/` skill/agent files. Clean up 22 existing violations across 6 skill files.

## Scope

### In Scope
- Edit CLAUDE.md Section 5 to add scope and exclusion rules
- Remove/convert all `/// Why:` comments from skill files in `.claude/`

### Out of Scope
- Comprehensive "skill writing guidelines" document
- Changes to how WHY comments work in code files

## Acceptance Criteria

- [ ] CLAUDE.md Section 5 explicitly scopes WHY comments to code files
- [ ] CLAUDE.md Section 5 explicitly forbids `///` comments in `.claude/`
- [ ] Zero `/// Why:` occurrences in `.claude/` directory
- [ ] No skill functionality lost from cleanup
