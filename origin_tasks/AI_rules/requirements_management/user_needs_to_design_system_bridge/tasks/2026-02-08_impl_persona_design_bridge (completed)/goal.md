---
task_id: TASK-PROC-026-03
type: impl
parent_requirement: REQ-PROC-026
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: completed
completed: 2026-03-01
effort: M
created: 2026-02-08
after:
  - TASK-PROC-026-02
awaiting:
  - TASK-PROC-026-02
covers:
  acceptance_criteria:
    - AC-01
    - AC-02
    - AC-05
    - AC-06
    - AC-07
    - AC-08
    - AC-10
    - AC-11
    - AC-12
  sections:
    - "4.1"
    - "4.2"
    - "4.3"
    - "4.4"
    - "4.6"
    - "4.7"
    - "4.8"
    - "5"
scope_description: "Create the central persona-design bridge document that AI reads during UI implementation"
requirements_version:
  commit: null
  file: ../../../requirements.md
  note: "REQ-PROC-026 sections 4.1-4.8 and section 5 define the content"
---

# Implementation Task: Create Persona-Design Bridge Document

## Requirement Reference
- **Requirement**: [REQ-PROC-026](../../../requirements.md) — Sections 4.1 through 4.8, Section 5
- **Roadmap Position**: T2 (central reference document — most other tasks depend on this)

## Goal

Create `doc/presentation/design/persona_design_bridge.md` — the central reference document that AI reads during UI implementation to connect persona traits to design rules. This is the "lookup table" that makes the persona→design chain operational.

This document bridges the two pillars that currently never connect: the 13 richly detailed personas and the design system rules.

## Architectural Context

This document is a **`doc/` guideline** — it is read by implementation agents during EVERY UI task. It is NOT a requirements document. The key distinction:

- **Requirements** (`requirements_tasks/`) → define WHAT to build, create tasks
- **This document** (`doc/presentation/design/`) → tells agents HOW to build correctly, with persona justification as armor

Design rule entries in this document follow the WHAT + HOW + WHY pattern:
- **WHAT**: The design constraint (e.g., "touch targets >= 48dp")
- **HOW**: Token reference or code pattern (e.g., "use `ComponentTokens.buttonMinHeight`")
- **WHY**: Persona justification (e.g., "Jana has tremors, Sophie has motor imprecision")

This document does NOT redefine token values — it references tokens in `lib/config/theme/tokens.json`. If a rule needs a token that doesn't exist yet, the document flags that need.

## Scope Overview

**What this document must contain** (consolidated from REQ-PROC-026):

1. **Design-Relevant Trait Categories** (section 4.1): The 8 categories with affected personas and design implications:
   - Motor constraints, Cognitive load budget, Time-to-capture window, Environmental light constraints, Privacy/discreteness, Emotional sensitivity, Sensory/environmental adaptation, Data density tolerance

2. **Two-Stream Rule Creation Methodology** (section 4.2): How design rules are created:
   - Stream 1 (AI-derived, bottom-up): EXTRACT → DERIVE → CLASSIFY → CODIFY → REVIEW
   - Stream 2 (Human-defined, top-down): PROPOSE → VALIDATE → CLASSIFY → DOCUMENT → IMPLEMENT
   - CODIFY/DOCUMENT steps produce WHAT + HOW (token ref) + WHY (persona justification)
   - Provenance markers for both streams

3. **Concrete Examples** (section 4.3): At least the 7 examples from the exploration, with tier annotations and token references

4. **Rule Generality Tiers** (section 4.4): T1/T2/T3 classification system, signals table, promotion workflow, precedence rules

5. **Relationship to regular feature flow** (section 4.0): How T1/T2 rules in `doc/` complement feature-specific T3 decisions in tasks

6. **Human-in-the-Loop Gates** (section 4.6): The 8 decision types requiring human judgment, the review mode (AI flags and pauses), role division

7. **Persona Conflict Resolution** (section 4.8): DDR format, when conflicts arise, AI behavior for conflicts

8. **Design Review Checklist** (section 5): AI-verifiable and human-review-required checks

**Affected Layers**: Documentation only
**Estimated Files**: 1 primary file (`persona_design_bridge.md`), possibly referencing existing persona files
**Patterns to Follow**: Existing `doc/presentation/` source files for formatting conventions

## Important Constraints

- This document is the **single source of truth** for the persona-design methodology. Skills and other docs reference it, not the other way around.
- Content comes from REQ-PROC-026 (the requirements document from the exploration). This task translates the requirement into an operational `doc/` guideline.
- The document must be **AI-readable and actionable** — not academic prose but structured lookup tables and decision trees.
- Design rules reference tokens (`ComponentTokens.*`, `SpacingTokens.*`, etc.) — they do NOT redefine values.
- The exploration protocol (`plans_and_protocols/2026-02-07_01_opus_plan.md`) contains the original analysis with all persona trait extractions.

## Acceptance Criteria

- [ ] AC-01: Persona-to-design mapping methodology documented and referenceable by AI
- [ ] AC-02: Design-relevant trait categories extracted from all personas (8 categories with persona mapping)
- [ ] AC-05: `doc/` presentation guidelines include persona-awareness section
- [ ] AC-06: Validation checklist exists for verifying design serves user needs
- [ ] AC-07: Human-in-the-loop decision points documented
- [ ] AC-08: Two-stream rule creation workflow documented
- [ ] AC-10: Rule generality tiers documented with classification signals and promotion workflow
- [ ] AC-11: Rule precedence logic documented
- [ ] AC-12: Design Decision Record (DDR) format defined
- [ ] Document is structured for AI consumption (lookup tables, decision trees, not prose)
- [ ] All 13 personas referenced with their design-relevant traits

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-026-02 (Restructure subfolders) | pending | **BLOCKER** — `doc/presentation/design/` must exist before this file can be placed |
| Exploration protocol (TASK-PROC-026-01) | completed | Source material for content |
| All 13 personas | approved | Referenced in trait extraction |

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
