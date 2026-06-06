# Protocol: Align REQ-PROC-035 SEC-05/SEC-06 with REQ-PROC-058

## Investigation Summary

Read both requirements in full:
- REQ-PROC-035 (current state) — release_preparation/requirements.md
- REQ-PROC-058 (authoritative source) — implementation_task_planning/requirements.md

Key findings from REQ-PROC-058:
- **AC-14**: release-begin-impl Phase 2c delegates per-requirement decomposition to task-derive-from-requ. Phase 2c assembles per-requirement plans and adds release-level concerns on top.
- **SEC-04**: Defines the unified plan format shared between task-derive-from-requ and Phase 2c. task-create-code consumes plans from either source via Phase 0A.
- **SEC-01**: "task-derive-from-requ orchestrates; task-create / task-create-code create."
- SEC-01 of REQ-PROC-058 explicitly describes the monolithic-vs-delegated target state for Phase 2c.

## Changes Applied

### SEC-05 (Task Creation Process)
Replaced the "Task Creation Plan" paragraph: Phase 2c now spawns one `task-derive-from-requ` agent per in-scope requirement. Each agent produces a per-requirement plan with coverage matrix, mandatory verification task, sizing signals, dependency ordering. Phase 2c assembles these into the release plan and adds release-level concerns (package execution ordering, cross-requirement dependencies, release scope completeness). Plans share the unified format defined in REQ-PROC-058 SEC-04.

### SEC-06 (release-begin-impl Integration)
Replaced the Phase 2c bullet: removed "One agent reads ALL in-scope feature requirements.md files and produces task_creation_plan.md" — now describes delegation to task-derive-from-requ. Updated Phase 5 bullet: per-requirement coverage matrices are presented alongside the plan summary.

### Related Requirements
Added REQ-PROC-058 entry explaining the delegation contract and shared plan format.

### YAML
- `updated:` bumped to 2026-05-24
- `after:` extended with REQ-PROC-058 (REQ-PROC-058 already had `blocks: [REQ-PROC-035]`)

## Synthesis

The change resolves the conflict between REQ-PROC-058 AC-14 and REQ-PROC-035's prior monolithic description. A reader of REQ-PROC-035 now understands the delegation model without needing to cross-read REQ-PROC-058 (though the unified plan format and coverage matrix details remain authoritatively owned by REQ-PROC-058). The "Compute once, trust downstream" pattern (REQ-PROC-058 AC-15) is now reflected in SEC-05/SEC-06: Phase 2c trusts task-derive-from-requ's per-requirement coverage matrices and adds only release-level concerns on top.

## What Remains Uncertain

None for this alignment. The implementation of the delegation (release-begin-impl skill code) is outside this requirement's scope — it is the task layer that operationalises SEC-05/SEC-06. Tracked elsewhere via REQ-PROC-058's task chain.

## Approval

This is an alignment task with well-defined inputs (AC-14, SEC-01, SEC-04 of REQ-PROC-058). No user-facing decisions surfaced. Proceeding to task-complete.
