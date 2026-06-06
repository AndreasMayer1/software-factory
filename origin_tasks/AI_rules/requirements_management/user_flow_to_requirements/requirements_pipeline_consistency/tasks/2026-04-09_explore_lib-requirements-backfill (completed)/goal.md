---
task_id: TASK-PROC-030-01-03
type: explore
parent_requirement: REQ-PROC-030-01
urgency: 2
urgency_reason: "U2-TECHNICAL-DEBT: Implemented features without corresponding requirements create a silent blind spot in the consistency checks being introduced"
impact: 3
impact_reason: "I3-EFFICIENCY: After backfill, requ-explore orphaned-implementation checks have a clean baseline — no legacy gap to re-discover on every run"
status: completed
completed: 2026-04-09
effort: L
created: 2026-04-09
started: 2026-04-09
after: [TASK-PROC-030-01-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04]
  sections: []
scope_description: "One-time analysis of lib/ to identify implemented features that lack a corresponding requirements.md; user reviews each candidate; placeholder requirements created for approved gaps"
release_description: ""
requirements_version:
  commit: 4c028a3b
  file: ../requirements.md
---

# Goal: One-Time lib/ Requirements Backfill

## Objective

Perform a one-time analysis of `lib/` to identify feature implementations that have no corresponding `requirements.md`. For each discovered gap, present it to the user for review. For approved gaps, create placeholder `requirements.md` files. This closes the legacy blind spot that the orphaned-implementation check in `requ-explore` (AC-04) would otherwise have to re-discover on every run.

## Background

The consistency improvements in TASK-PROC-030-01-02 add an orphaned-implementation check to `requ-explore` section 1.5. However, there is a large existing body of code in `lib/` that predates systematic requirements tracking. Without a backfill, every future `requ-explore` run would either re-discover these legacy gaps or silently ignore them. A single, thorough backfill with user involvement closes the gap cleanly.

## Important: Strong User Involvement Required

Not everything in `lib/` is relevant, final, or worth capturing as a requirement. The agent executing this task must **not** create requirements autonomously. Every candidate gap must be presented to the user for a go/no-go decision before any placeholder is created. The user's judgment determines:

- Is this feature actually stable enough to document?
- Is this behavior intentional (not a prototype or dead code)?
- Does an abstraction/grouping make more sense than one-to-one mapping?

## Scope

### In Scope
- Systematic scan of `lib/` to map implemented features to existing requirements
- Presenting each unmatched feature as a candidate gap to the user
- Creating placeholder `requirements.md` files only for user-approved candidates
- Grouping related implementations into sensible requirement boundaries (abstraction)

### Out of Scope
- Writing full requirement documents (placeholders only — full exploration is a follow-up task per placeholder)
- Analyzing `test/` or `integration_test/`
- Automated creation of requirements without user review

## Suggested Approach

1. Use `codegraph context` and targeted Glob/Grep to identify major feature areas in `lib/`
2. For each feature area, check whether a `requirements.md` covers it (keyword-grep in requirements_tasks/)
3. Build a candidate list: feature area → coverage status (covered / partial / none)
4. Present the full candidate list to the user
5. For each user-approved gap: create a placeholder `requirements.md` with `status: placeholder` and a brief description; create a follow-up explore task via `task-create`

## Acceptance Criteria

- [ ] All major feature areas in `lib/` are mapped to an existing requirement or identified as a gap candidate
- [ ] User has reviewed and approved/rejected each gap candidate
- [ ] Placeholder `requirements.md` files exist for all approved candidates (with `status: placeholder`)
- [ ] Each placeholder has a corresponding follow-up explore task created via `task-create`
- [ ] The candidate list and user decisions are documented in `plans_and_protocols/`
