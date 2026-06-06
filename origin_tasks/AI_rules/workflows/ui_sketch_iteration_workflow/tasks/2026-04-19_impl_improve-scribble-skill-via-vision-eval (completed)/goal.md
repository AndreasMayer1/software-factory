---
task_id: TASK-PROC-032-04
type: impl
parent_requirement: REQ-PROC-032-01
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-04-19
effort: L
created: 2026-04-19
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-04]
  sections: [SEC-04, SEC-06]
scope_description: "Autonomously improve ui-create-scribble/skill.md via vision-evaluated iteration loop using 3 fixture requirements"
release_description: "Improves scribble generation quality via automated vision evaluation and targeted skill updates."
opus_recommended: false
requirements_version:
  commit: 399146be
  file: ../requirements.md
---

# Goal: Improve ui-create-scribble skill via vision-evaluated iteration loop

## Objective

Autonomously improve `.claude/skills/ui-create-scribble/skill.md` by running a multi-iteration loop:
1. Select 3 fixture requirements (simple / medium / complex)
2. Generate scribbles using the current skill
3. Evaluate each scribble with vision using an 8-criterion rubric (max 16/16)
4. Identify the weakest criterion and propose one atomic skill.md change
5. Apply the change, recheck the worst fixture, commit if score improves
6. Repeat up to 5 iterations or until average score ≥ 12.8/16

All work happens in a dedicated git worktree on branch `improve/scribble-skill-{DATE}`.

## Requirements Summary

REQ-PROC-032 defines the full ui-create-scribble workflow including AI generation rules,
iteration protocol, T1/T2 design system alignment, and flow-based screen ordering.

Current requirements: ../requirements.md

## Scope

### In Scope
- Editing `.claude/skills/ui-create-scribble/skill.md` only
- Running vision evaluation against 3 fixture requirements
- Up to 5 improvement iterations with commit-or-revert gating

### Out of Scope
- Changes to `ui-verify-flutter`, `ui-improve-flutter`, or other skills
- Editing scribble artifacts in `requirements_tasks/` (test scribbles go to worktree `scribbles/`)
- Manual user interaction during iteration loop

## Acceptance Criteria

- [ ] 3 fixtures selected (simple / medium / complex) and logged
- [ ] ≥1 iteration completed with evaluation YAML written
- [ ] skill.md improved (at least one criterion score raised) OR plateau/budget documented
- [ ] Branch ready for PR with iteration_log.md complete
- [ ] All commits reference TASK-PROC-032-04

## Dependencies

None.

## Notes

Invoked by `ui-create-scribble-improve` skill. See skill.md for full sub-agent orchestration spec.
