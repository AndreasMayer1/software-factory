---
task_id: TASK-PROC-030-01
type: impl
parent_requirement: REQ-PROC-030
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP"
impact: 4
impact_reason: "I4-PAIN"
status: completed
effort: S
created: 2026-02-21
completed: 2026-02-21
after: []
awaiting: []
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12]
  sections: []
scope_description: "Build the derive-requirements-from-flow skill and update workflow-wizard routing"
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Implementation Task: Build the derive-requirements-from-flow Skill

## Requirement Reference

- **Requirement**: `requirements_tasks/process/AI_rules/requirements_management/user_flow_to_requirements/requirements.md`
- **Status**: Not Started

## Goal

Build a new Claude Code skill (`.claude/skills/derive-requirements-from-flow/skill.md`) that bridges the gap between an approved user flow and the requirements it implies.

After running this skill on a user flow, the developer has:
1. A **Requirements Matrix** listing all gaps found in the flow with their status
2. A set of **goal.md files** (one per approved gap) ready for `explore-requirements` to execute

## Scope Overview

Single skill file to create. No code changes to `lib/`, `test/`, or `integration_test/`.

**Affected areas**:
- `.claude/skills/derive-requirements-from-flow/skill.md` — new file (primary deliverable)
- `.claude/skills/workflow-wizard/skill.md` — add the new skill to the routing options

**Patterns to follow**: `.claude/skills/explore-requirements/skill.md` and `.claude/skills/create-impl-task/skill.md` as structural examples.

**Estimated size**: Small (1 new skill file, 1 minor edit to workflow-wizard)

## What the Skill Must Do

See `requirements.md` sections 4.1–4.4 for full behavior spec. Summary:

1. **Read the flow**: Extract Implementing Epics/Features, Gaps, Open Questions, Screens/Components, Scope Boundaries
2. **Scan existing requirements**: Determine coverage status for each gap
3. **Build Requirements Matrix**: Categorize each gap as `exists_complete` / `exists_needs_update` / `exists_placeholder` / `new_needed` / `decision_needed` / `out_of_scope`
4. **Present to user**: Show matrix, allow corrections and priority selection
5. **Generate work items**: Create goal.md files for user-approved gaps, save matrix as `requirements_matrix.md` next to the flow

## Validation Test

After building the skill, run it on FLOW-002:
```
"Use derive-requirements-from-flow skill for requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md"
```

Expected: 7 gaps identified (matching the "Gaps Requiring New Requirements" section in flow.md), correct status categorization, goal.md files created for at least the top 3 gaps.

## Acceptance Criteria

From `requirements.md` section 6:

- [ ] Skill file exists at `.claude/skills/derive-requirements-from-flow/skill.md`
- [ ] Reads all relevant flow sections (Gaps, Implementing Epics, Open Questions, Screens, Scope Boundaries)
- [ ] Scans existing requirements and correctly categorizes each gap
- [ ] Generates Requirements Matrix with all gaps
- [ ] User reviews and approves before any files are created
- [ ] Creates goal.md files for approved gaps, each referencing source flow + gap
- [ ] Open Questions flagged as `decision_needed`, not silently skipped
- [ ] Scope boundaries documented as `out_of_scope`
- [ ] Matrix saved as `requirements_matrix.md` alongside the flow
- [ ] Validation test on FLOW-002 passes (7 gaps found)
- [ ] workflow-wizard updated to include this skill

## Dependencies

None — this is a standalone skill file with no code dependencies.

## Notes

- Keep the skill token-efficient (short, focused steps)
- Use Opus via `switch-to-opus` for the analysis step (gap identification and matrix generation benefit from deeper reasoning)
- The skill should NOT write requirements — it only sets up workspace for `explore-requirements`
- After building, this skill should be added to the system-reminder list of available skills
