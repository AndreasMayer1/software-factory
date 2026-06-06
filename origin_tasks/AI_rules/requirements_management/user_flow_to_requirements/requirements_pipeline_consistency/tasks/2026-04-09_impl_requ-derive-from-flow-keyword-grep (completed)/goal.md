---
task_id: TASK-PROC-030-01-01
type: impl
parent_requirement: REQ-PROC-030-01
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: Existing skill has a documented gap that can silently create duplicate or contradictory requirements"
impact: 3
impact_reason: "I3-EFFICIENCY: Keyword-grep catches semantic overlaps before new requirements are created, avoiding costly rework"
status: completed
completed: 2026-04-09
session_completed_at: 2026-04-09T10:02:04Z
effort: S
created: 2026-04-09
started: 2026-04-09
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01]
  sections: []
scope_description: "Add keyword-grep step to requ-derive-from-flow section 1.3 so each gap is semantically checked before being categorized as new_needed"
release_description: ""
requirements_version:
  commit: 4c028a3b
  file: ../requirements.md
---

# Goal: Add Keyword-Grep to requ-derive-from-flow Section 1.3

## Objective

Improve the gap-coverage scan in `.claude/skills/requ-derive-from-flow/skill.md` (section 1.3 "Scan existing requirements") by adding a targeted keyword-grep pass that runs before any gap is categorized as `new_needed`.

## Requirements Summary

REQ-PROC-030-01 AC-01 specifies: `requ-derive-from-flow` performs a keyword-grep pass across `requirements_tasks/functional/` and `requirements_tasks/non-functional/` for each gap before categorizing it as `new_needed`, using terms derived from the gap description to surface semantic overlaps where folder names and IDs differ.

Current requirements: ../requirements.md

## Scope

### In Scope
- Editing section 1.3 in `.claude/skills/requ-derive-from-flow/skill.md`
- Adding a prescriptive keyword-grep step (2–4 terms per gap, targeting functional/ and non-functional/)
- Specifying that `new_needed` categorization requires the grep pass to return no relevant hits

### Out of Scope
- Changes to any other section of the skill
- Changes to `requ-explore`
- Scanning `requirements_tasks/process/`

## What to Change

Section 1.3 currently reads:

> For each candidate match, read briefly to assess coverage quality.

After the Glob step, add an explicit keyword-grep substep:

For each gap, derive 2–4 search terms from the gap description (domain nouns, action verbs, component names). Run a grep across `requirements_tasks/functional/` and `requirements_tasks/non-functional/` for those terms. Read any hits to assess whether they constitute existing coverage. A gap must not be categorized as `new_needed` until this grep pass returns no relevant hits.

## Acceptance Criteria

- [ ] Section 1.3 prescribes deriving 2–4 keyword terms from each gap description
- [ ] Section 1.3 prescribes a grep pass targeting functional/ and non-functional/ using those terms
- [ ] Section 1.3 states that `new_needed` categorization requires the grep to return no relevant hits
- [ ] The change does not remove or weaken the existing Glob + read step

## Notes

The keyword-grep supplements (not replaces) the existing Glob approach. The Glob finds files by path pattern; the grep surfaces files by content. Both are needed.
