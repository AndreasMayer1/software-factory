---
task_id: TASK-PROC-038-01
type: impl
parent_requirement: REQ-PROC-038
urgency: 3
urgency_reason: U3-CTX
impact: 3
impact_reason: I3-PROC
status: completed
completed: 2026-03-14
effort: M
created: 2026-03-14
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04, AC-05, AC-06]
  sections: [SEC-01]
target_release: ~
scope_description: "Add CodeGraph context step to code-complex, code-bugfix, requ-explore, claude-create-skill, and claude-modify-skill"
release_description: ""
requirements_version:
  commit: 520a6f8
  file: ../requirements.md
---

# Implementation Task: Integrate CodeGraph into Skills

## Requirement Reference
- **Requirement**: `requirements_tasks/process/AI_rules/ai_tool_management/codegraph_integration/requirements.md` (REQ-PROC-038)
- **Status**: Not Started

## Goal

Add a "CodeGraph First" step to all skills that read or understand code, so that agents use `codegraph context` for semantic orientation before falling back to Glob/Grep/Read exploration.

## Scope Overview

Five skill files need a CodeGraph step added at the appropriate point in their workflow:

| Skill | Where to add | Priority |
|-------|-------------|----------|
| `code-complex` | Before spawning architecture-advisor agent (Step 2) | High |
| `code-bugfix` | Before Opus planning in resume run (Step 5) | High |
| `requ-explore` | Phase 1.5 — before Glob/Grep loop | Medium |
| `claude-create-skill` | When new skill needs to read existing code patterns | Medium |
| `claude-modify-skill` | When modifying a skill that touches code-reading steps | Medium |

**Affected Layers**: Process / AI workflow (`.claude/skills/`)
**Estimated Files**: 5 skill files
**Patterns to Follow**: See REQ-PROC-038 (SEC-01) for the exact integration pattern — do not duplicate it here.

## Additional Details

For `claude-create-skill` and `claude-modify-skill`: the instruction should be lightweight — a note that says *"if the skill you are creating/modifying reads or understands code, read REQ-PROC-038 to understand how and where to add the CodeGraph step."* This keeps the meta-skills DRY and points authors to the single source of truth for the pattern.

Do **not** inline the CodeGraph usage pattern in these skill files. Reference REQ-PROC-038 instead.

## Acceptance Criteria

- AC-04: `code-complex` invokes `codegraph context` before spawning architecture-advisor
- AC-05: `code-bugfix` invokes `codegraph context` before Opus bug investigation planning
- AC-06: `requ-explore` invokes `codegraph context` in Phase 1.5 before the Glob/Grep loop
- `claude-create-skill` and `claude-modify-skill` contain a note directing authors to REQ-PROC-038 when the skill reads code

## Dependencies

- REQ-PROC-038 is the integration spec — read it before implementing
- CodeGraph CLI must be installed (`codegraph --version`) — already done as of 2026-03-14
- `.codegraph/` must be initialized — already done as of 2026-03-14

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
