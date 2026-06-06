---
task_id: TASK-PROC-026-05
type: impl
parent_requirement: REQ-PROC-026
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: completed
completed: 2026-03-01
effort: S
created: 2026-02-08
after:
  - TASK-PROC-026-03
awaiting:
  - TASK-PROC-026-03
covers:
  acceptance_criteria:
    - AC-04
  sections:
    - "6.2"
scope_description: "Add persona-reading step and sketch gate to code-simple and code-complex skills"
requirements_version:
  commit: null
  file: ../../../requirements.md
  note: "REQ-PROC-026 section 6.2 'Skills' table defines the changes"
---

# Implementation Task: Update Implementation Skills for Persona Awareness + Sketch Gate

## Requirement Reference
- **Requirement**: [REQ-PROC-026](../../../requirements.md) — Section 6.2 "Skills (.claude/skills/)"
- **REQ-PROC-032** — UI Sketch Iteration Workflow (sketch gate integration)
- **Roadmap Position**: T4

## Goal

Add two things to the `code-simple` and `code-complex` skills:

1. **Persona-reading step**: AI agents consider relevant personas when implementing UI (REQ-PROC-026)
2. **Sketch gate**: Before Presentation Layer work, check for `skip_sketch: true` in `goal.md`; if absent, verify an approved sketch exists in `sketches/`; if not, invoke `ui-create-sketch` first (REQ-PROC-032)

Also update the quality checker agent to include persona-design validation.

Currently, when AI implements a screen, it reads `doc/` guidelines mechanically — without considering *who* the users are or verifying that the UI was visually reviewed before implementation. Both gaps are closed in this task.

## Scope Overview

**Skills to modify**:

| Skill | Change |
|-------|--------|
| `code-simple/skill.md` | (1) Add persona-reading step in "Read & Assess" phase for UI tasks; (2) Add sketch gate check before Presentation Layer implementation |
| `code-complex/skill.md` | (1) Add persona-mapping step in planning phase for UI tasks; (2) Add sketch gate check before Presentation Layer planning |
| Quality checker agent | Add persona-design validation to quality checklist (persona identification, trait scan, DDR check for conflicts) |

**Sketch gate logic** (to add to both code-skills):
```
If task includes Presentation Layer changes:
  1. Check goal.md for skip_sketch: true
  2. If not present: check [requirement]/sketches/ for status: approved version
  3. If no approved sketch: invoke ui-create-sketch, pause for approval
  4. If approved sketch exists: proceed, reference sketch for element choices
```

**Design principle**: Skills should contain a one-line reference to the persona-design bridge, not the full content. Keep skills token-efficient.

**Affected Layers**: Orchestration/Skills only
**Estimated Files**: 2-3 skill files modified (~5-10 lines added per file)
**Patterns to Follow**: Existing skill structure; the persona-design bridge document (T2) is the reference

## Important Constraints

- Skills are token-sensitive context loaded into every agent call. Changes must be minimal — a reference to the bridge document, not duplicated content.
- The existing architecture rule stands: **agents read `doc/` for guidelines + their task's goal.md. They do NOT browse `requirements_tasks/`**. The skill modification should direct agents to read `doc/presentation/design/` files (T1/T2 rules), not requirements files.
- The quality checker needs to validate both AI-verifiable checks (persona identification, trait scan, numeric thresholds) and flag human-review-required checks (brand personality, flow continuity, tone).
- The "AI flags and pauses" review mode means the quality checker should surface persona-related concerns as explicit questions to the user, not silently pass them.
- Sketch gate applies only to Presentation Layer changes. Domain, Data, and infrastructure changes are not affected.
- The sketch gate check must be lightweight — a glob for `[requirement]/sketches/` with `status: approved`. Not a full skill invocation by default.

## Acceptance Criteria

- [ ] AC-04: Implementation skills reference persona traits during UI work
- [ ] `code-simple` skill has persona-reading step for UI tasks
- [ ] `code-simple` skill has sketch gate check before Presentation Layer implementation
- [ ] `code-complex` skill has persona-mapping step in planning phase
- [ ] `code-complex` skill has sketch gate check before Presentation Layer planning
- [ ] Quality checker includes persona-design validation checks
- [ ] Skill additions are token-efficient (reference, not duplication)
- [ ] Non-UI tasks are not burdened by persona-reading or sketch gate steps (conditional: "if Presentation Layer")

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-026-03 (Persona-design bridge) | pending | **BLOCKER** — skills reference this document |
| REQ-PROC-032 (UI Sketch Workflow) | defined | `ui-create-sketch` skill must exist — already created |

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
