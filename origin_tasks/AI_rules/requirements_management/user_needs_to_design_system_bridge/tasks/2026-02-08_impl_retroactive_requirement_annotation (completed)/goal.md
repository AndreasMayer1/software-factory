---
task_id: TASK-PROC-026-06
type: impl
parent_requirement: REQ-PROC-026
urgency: 3
urgency_reason: U3-CTX
impact: 3
impact_reason: I3-INFRA
status: completed
completed: 2026-03-01
effort: L
created: 2026-02-08
after:
  - TASK-PROC-026-03
awaiting:
  - TASK-PROC-026-03
covers:
  acceptance_criteria:
    - AC-03
    - AC-15
  sections:
    - "6.2"
scope_description: "Add persona justifications and tier classifications to ALL existing design system requirements"
requirements_version:
  commit: null
  file: ../../../requirements.md
  note: "REQ-PROC-026 section 6.2 'Existing Design System Requirements' table defines the mappings"
---

# Implementation Task: Retroactive Annotation of ALL Existing Design System Requirements

## Requirement Reference
- **Requirement**: [REQ-PROC-026](../../../requirements.md) — Section 6.2 "Existing Design System Requirements (Retroactive Annotation)"
- **Roadmap Position**: T5

## Goal

Add persona justifications and tier classifications to ALL existing design system requirements. Every rule in the design system should be traceable to the personas it serves, so that future modifications understand *who* would be affected.

User decision (2026-02-08): Annotate ALL requirements immediately for a clean start, not just the highest-impact ones.

## Scope Overview

**13 requirement files** to annotate in `requirements_tasks/non-functional/ui_ux_design_system/`:

| Requirement | Expected Tier | Key Persona Justifications |
|------------|---------------|---------------------------|
| accessibility/requirements.md | T1 | 48dp targets (Jana, Sophie), WCAG AA (all), Simple Mode (Sophie cluster) |
| ux_writing/requirements.md | T1 | Empathetic tone (Max, Jana), sensitive context (all clients), no guilt language (Sophie, David) |
| loading_error_handling/requirements.md | T1/T2 | Timing rules (David), retry patterns (Nina), confirmation dialogs (Jana) |
| theming/growth_tree_theme/requirements.md | T1 | Dark mode (Hanna), discrete appearance (Elias, Michael), Simple Mode (Sophie cluster) |
| navigation_patterns/main_navigation/requirements.md | T2 | Master-detail (Dr. Sarah, Dr. Turan) |
| navigation_patterns/in_detail_navigation/requirements.md | T2 | In-detail nav patterns |
| navigation_patterns/responsive_layout_master_detail/requirements.md | T2 | Responsive layout for therapist workflow |
| components/collapsible_form_section/requirements.md | T2 | Progressive disclosure (Max, David cognitive load) |
| components/context_help/requirements.md | T2 | Help patterns for confused users |
| components/leaf_popout/requirements.md | T2 | Component interaction patterns |
| components/skeleton/requirements.md | T2 | Loading indicators (Nina, David) |
| components/toast/requirements.md | T2 | Error/success feedback (Max, UX writing) |
| components/time_range_selector/requirements.md | T2 | Time input (David, time-to-capture) |

**What each annotation includes**:
- Tier classification (T1 or T2)
- Persona justification section listing which personas and traits drove these rules
- Provenance marker: `Pre-Framework, Human-Defined` (these rules predate the persona-design methodology)

**Affected Layers**: Requirements documentation only
**Estimated Files**: 13 requirement files
**Patterns to Follow**: The persona-design bridge document (T2) provides the trait-to-persona mapping

## Important Constraints

- These are retroactive annotations — the rules themselves don't change, only their documentation
- All existing requirements are marked as `Pre-Framework, Human-Defined` since they were created before the persona-design methodology existed
- Some persona-to-requirement connections require judgment (not all are obvious). The persona-design bridge provides the 8 trait categories to guide this.
- The user chose to annotate ALL 13 requirements for a clean start (not incremental)

## Acceptance Criteria

- [ ] AC-03: Existing design system rules annotated with persona justifications
- [ ] AC-15: Existing design system requirements retroactively annotated with persona justifications
- [ ] All 13 requirement files have tier classification (T1 or T2)
- [ ] All 13 requirement files have persona justification section with specific PERSONA-IDs
- [ ] All 13 requirement files have provenance marker: `Pre-Framework, Human-Defined`
- [ ] Annotations reference trait categories from the persona-design bridge

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-026-03 (Persona-design bridge) | pending | **BLOCKER** — provides the trait-to-persona mapping used for annotations |
| All 13 personas | approved | Referenced in annotations |

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
