---
task_id: TASK-PROC-026-04
type: impl
parent_requirement: REQ-PROC-026
urgency: 2
urgency_reason: U2-PLAN
impact: 3
impact_reason: I3-INFRA
status: completed
completed: 2026-03-01
effort: M
created: 2026-02-08
after:
  - TASK-PROC-026-03
awaiting:
  - TASK-PROC-026-03
covers:
  acceptance_criteria:
    - AC-09
  sections:
    - "4.7"
    - "6.2"
scope_description: "Create new ux-validate-rule skill for Stream 2 (human-defined UX rule validation)"
requirements_version:
  commit: null
  file: ../../../requirements.md
  note: "REQ-PROC-026 section 4.7 defines the skill workflow, section 6.2 describes the skill"
---

# Implementation Task: Create ux-validate-rule Skill

## Requirement Reference
- **Requirement**: [REQ-PROC-026](../../../requirements.md) — Section 4.7 "Validating Human-Defined UX Rules", Section 6.2 "The ux-validate-rule Skill"
- **Roadmap Position**: T3

## Goal

Create a new skill at `.claude/skills/ux-validate-rule/skill.md` that enables humans to validate their UX proposals against personas before implementation (Stream 2 workflow). This prevents wasted implementation cycles when a human idea conflicts with documented user needs.

## Scope Overview

**What the skill does** (from REQ-PROC-026 section 4.7):

1. Takes human UX proposal as input (rule description, target feature/screen, optional rationale)
2. Identifies relevant personas for the proposed rule
3. Extracts design-relevant traits from those personas
4. Checks alignment per persona: SUPPORTS / NEUTRAL / CONFLICTS
5. Detects conflicts with existing persona-derived rules
6. Classifies tier (AI proposes T1/T2/T3, human confirms)
7. Generates a structured validation report with recommendation (APPROVE / MODIFY / REJECT)
8. If approved: documents the rule at the tier-appropriate location with provenance marker `Human-Defined, [Tier] (persona-validated)`
9. If conflicting: suggests modifications

**User invocation**:
- `"Use ux-validate-rule skill for [UX proposal]"`
- `"Validate this UX idea against personas: [description]"`

**Affected Layers**: Orchestration/Skills only
**Estimated Files**: 1 new file (`.claude/skills/ux-validate-rule/skill.md`)
**Patterns to Follow**: Existing skill structure (YAML frontmatter + numbered workflow steps). See `ux-create-persona/skill.md` or `requ-explore/skill.md` for similar validation-oriented skills.

## Important Constraints

- The skill must reference `doc/presentation/design/persona_design_bridge.md` (created in T2) as the lookup table for trait categories
- Keep the skill token-efficient — reference external docs rather than duplicating content
- The validation report format is specified in REQ-PROC-026 section 4.7 (includes persona alignment table, tier classification, recommendation, conflict detection)
- The skill must support the "AI flags and pauses" review mode (human decides, AI doesn't auto-approve)

## Acceptance Criteria

- [ ] AC-09: `ux-validate-rule` skill created for proactive validation of human UX proposals
- [ ] Skill follows existing skill structure conventions (YAML frontmatter, numbered steps)
- [ ] Validation report format matches REQ-PROC-026 section 4.7 specification
- [ ] Skill references persona-design bridge document (not hardcoded persona data)
- [ ] Provenance markers included for approved rules
- [ ] Tier classification step included (AI proposes, human confirms)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-026-03 (Persona-design bridge) | pending | **BLOCKER** — skill references the bridge document for trait lookups |
| Existing personas (all 13) | approved | Read during validation |

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
