# Plan: Wire propose_after.py into Task-Create Skills

**Task**: TASK-PROC-042-09
**Date**: 2026-04-23
**Agent**: 365a6393-1424-423d-8d40-834b6e9eda57 (automated session, gmail)

## Goal

Add propose_after.py invocation to three skills: task-create, task-create-code (= "task-create-impl"), requ-derive-from-flow.

## Key Finding: task-create-impl = task-create-code

The goal.md references "task-create-impl" which does not exist as a distinct skill.
Based on release_preparation/requirements.md: "Implementation tasks for a release are created
package-by-package using task-create-impl." This maps exactly to task-create-code (zero-parameter mode).

## Insertion Points

### task-create/skill.md
- Step 5a creates directory, 5c writes goal.md
- Insert new step 5d between them: run propose_after.py, present proposals, user confirms `after:`

### task-create-code/skill.md
- Section 3.2.5 has manual heuristics (enumerate siblings → classify layer → apply heuristics → present → write)
- REPLACE manual heuristics with propose_after.py call (script implements the same logic portably)
- Update automated mode table entry for 3.2.5

### requ-derive-from-flow/skill.md
- Phase 4.2 spawns batch agents that call task-create
- Since task-create will have the propose_after step, it runs automatically inside batch agents
- Add a note to the Phase 4.2 mandatory instruction to clarify this behavior

## Automated Mode Behavior

- Same-package continuation proposals → auto-accept (write to after:)
- All other proposals → skip (do not write, do not use pending_feedback — non-blocking)
- Script failure → warn, continue with after: []
- No proposals → skip silently

## Changes

1. task-create/skill.md: new step between 5a and 5c
2. task-create-code/skill.md: replace section 3.2.5 body + update automated mode table
3. requ-derive-from-flow/skill.md: add note to Phase 4.2 batch agent instructions

## Status: executing
