---
task_id: TASK-PROC-026-07
type: impl
parent_requirement: REQ-PROC-026
urgency: 3
urgency_reason: U3-CTX
impact: 3
impact_reason: I3-INFRA
status: completed
completed: 2026-03-01
effort: M
created: 2026-02-08
after:
  - TASK-PROC-026-02
  - TASK-PROC-026-03
awaiting:
  - TASK-PROC-026-02
  - TASK-PROC-026-03
covers:
  acceptance_criteria:
    - AC-14
  sections:
    - "4.3"
    - "4.5"
scope_description: "Create individual t1_*.md and t2_*.md rule files from exploration findings"
requirements_version:
  commit: null
  file: ../../../requirements.md
  note: "REQ-PROC-026 sections 4.3 (examples) and 4.5 (file naming) define the content and structure"
---

# Implementation Task: Extract Initial T1/T2 Design Rules

## Requirement Reference
- **Requirement**: [REQ-PROC-026](../../../requirements.md) — Section 4.3 "Concrete Examples", Section 4.5 "File Naming Conventions"
- **Roadmap Position**: T6

## Goal

Create individual design rule files in `doc/presentation/design/` for the most important persona-derived rules identified during the exploration. These are the first concrete T1 and T2 rule files that AI will read during UI implementation.

The exploration identified 7 concrete persona→design mappings. This task extracts the T1 and T2 rules into their own files following the naming conventions.

## Architectural Context

These files are **`doc/` guidelines** — actionable instructions for implementation agents. They are NOT requirements. Each file follows the WHAT + HOW + WHY pattern:

- **WHAT**: The design constraint (specific, measurable)
- **HOW**: Token reference or code pattern to use (e.g., `ComponentTokens.buttonMinHeight`)
- **WHY**: Persona justification with PERSONA-IDs (armor against future weakening)

Files reference tokens in `lib/config/theme/tokens.json` — they do NOT redefine values. If a rule needs a token that doesn't exist yet (e.g., crisis-mode 64dp target), the file documents the need for a new token.

## Scope Overview

**Rules to extract** (from REQ-PROC-026 section 4.3):

| File | Tier | Content | Token Reference | Source Personas |
|------|------|---------|-----------------|-----------------|
| `t1_touch_targets.md` | T1 | All touch targets >= 48dp | `ComponentTokens.buttonMinHeight` (exists: 48.0) | Jana (PERSONA-014), Sophie (PERSONA-010) |
| `t1_dark_mode.md` | T1 | Dark mode uses OLED-true black (#000000) | Needs token: dark mode surface color override | Hanna (PERSONA-007) |
| `t1_interaction_budget.md` | T1 | Core capture flows <= 3 interactions, auto-save | No token (behavioral rule) | David (PERSONA-008), Jana (PERSONA-014) |
| `t1_input_scaffolding.md` | T1 | Never show empty free-text fields without scaffolding | No token (pattern rule) | Max (PERSONA-002), Sophie (PERSONA-010) |
| `t1_discrete_identity.md` | T1 | App identity must not signal mental health | No token (design direction) | Elias (PERSONA-009), Michael (PERSONA-006) |
| `t2_crisis_mode_targets.md` | T2 | Crisis-mode touch targets >= 64dp | Needs token: `component.button.crisisMinHeight` | Jana (PERSONA-014) |
| `t2_destructive_actions.md` | T2 | Destructive actions in overflow menu, two-step confirmation | `SpacingTokens.md` for spacing | Jana (PERSONA-014), Max (PERSONA-002) |

**Each file follows the naming convention** (REQ-PROC-026 section 4.5):
- `t1_` prefix for system-level rules
- `t2_` prefix for pattern-level rules

**Each file contains** (WHAT + HOW + WHY):
- **WHAT**: The design rule (specific, measurable constraint)
- **HOW**: Token reference (existing token name, or flagged need for new token) + code pattern guidance
- **WHY**: Persona justification (which personas and traits drove this rule, with PERSONA-IDs)
- Provenance marker: `AI-Derived, [Tier] (persona-grounded)`
- Scope definition (where the rule applies)
- Related rules or overrides (if any)

**Affected Layers**: Documentation only
**Estimated Files**: 7 new files in `doc/presentation/design/`
**Patterns to Follow**: File naming conventions from REQ-PROC-026 section 4.5

## Important Constraints

- These are the FIRST rule files — they set the template for all future rules
- The file format must be consistent and AI-parseable (structured, not prose)
- Each rule must be traceable back to specific persona traits (not vague)
- Rules reference existing tokens where possible; flag need for new tokens where not
- Not all rules map to tokens (behavioral rules like "auto-save" or "max 3 interactions" are pattern guidance, not token values)
- T2 rules should document their relationship to T1 rules (e.g., `t2_crisis_mode_targets.md` overrides `t1_touch_targets.md` for crisis screens)

## Acceptance Criteria

- [ ] AC-14: File naming conventions for design rules applied (`t1_`, `t2_` prefixes)
- [ ] 7 rule files created in `doc/presentation/design/`
- [ ] Each file has persona justification with specific PERSONA-IDs
- [ ] Each file has provenance marker
- [ ] Each file has measurable, specific design rule (not vague guidance)
- [ ] T2 rules document their relationship to T1 rules where applicable
- [ ] Files follow consistent template (established here for future rules)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-026-02 (Restructure subfolders) | pending | **BLOCKER** — `doc/presentation/design/` must exist |
| TASK-PROC-026-03 (Persona-design bridge) | pending | **BLOCKER** — bridge provides the methodology these files follow |
| Exploration protocol (TASK-PROC-026-01) | completed | Source for the 7 examples |

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
