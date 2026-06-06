---
id: REQ-PROC-033
title: "Value Centered Design Integration"
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: implemented
updated: 2026-03-02
effort: XL
stakeholder: developer
created: 2026-03-02
vcd_activation_date: 2026-03-02
after:
  - REQ-PROC-026
  - REQ-PROC-027
blocks: []
user_needs:
  personas_served: all
  notes: "VCD ensures that when the needs of different personas conflict, decisions are made transparently and based on defined values — not arbitrary defaults or AI assumptions."
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "All personas (except system_maintenance) have mandatory 'Primary Values' and 'Value Conflicts' fields"
    - id: AC-02
      text: "app_provider persona has Primary Values and Value Conflicts (sourced from real-user input, evidence_method: grounded)"
    - id: AC-03
      text: "Value Trade-off Record format defined: Problem, beteiligte Werte, Optionen, Entscheidung, Begründung, Folgen"
    - id: AC-04
      text: "Value Trade-off Record template exists at requirements_user_needs/_meta/value_tradeoff_record_template.md"
    - id: AC-05
      text: "Skill vcd-log-tradeoff exists to guide consistent trade-off documentation"
    - id: AC-06
      text: "Implementation and design skills (ux-validate-rule, ux-create-flow, code-complex, code-simple, requ-explore) reference persona values when resolving design conflicts"
    - id: AC-07
      text: "Value trade-off decisions at code/doc level are back-referenced in the originating requirement via WHY comment with VTR-NNN reference"
    - id: AC-08
      text: "Script scripts/aggregate_value_tradeoffs.py exists and generates requirements_user_needs/_meta/value_tradeoff_summary.md"
    - id: AC-09
      text: "Methodology documented: three-pillar framework (Schwartz + Beauchamp-Childress + Nissenbaum) with Design-Relevance Filter, evidence tagging (literature_derived / grounded / user_confirmed)"
    - id: AC-10
      text: "CLOSED: standalone 'Value Principles as Design Constraints' doc NOT needed — aggregation script (AC-08) replaces it"
    - id: AC-11
      text: "Lena (lena_depth_seeker) persona_id conflict resolved: unique ID assigned (PERSONA-016), all references updated"
    - id: AC-12
      text: "VCD activation date recorded in requirements.md YAML (vcd_activation_date field) and as note in doc/presentation/design/persona_design_bridge.md"
    - id: AC-13
      text: "VTR-NNN ID scheme added to scripts/generate_id_registry.py; VTR section appears in _meta/id_registry.md"
  sections:
    - id: SEC-01
      text: "Persona Value Fields (Primary Values + Value Conflicts)"
    - id: SEC-02
      text: "Value Trade-off Record Format & Template"
    - id: SEC-03
      text: "Value Trade-off Documentation Skill"
    - id: SEC-04
      text: "Skills Adaptation for Value-Aware Design"
    - id: SEC-05
      text: "Value Record Aggregation Script"
    - id: SEC-06
      text: "Methodology for Deriving Persona Values"
    - id: SEC-07
      text: "Persona ID Integrity"
    - id: SEC-08
      text: "VCD Activation Date Recording"
    - id: SEC-09
      text: "VTR ID Registry Integration"
---

# REQ-PROC-033: Value Centered Design Integration

## Objective

Integrate Value Centered Design (VCD) into the software factory so that:
1. Every persona carries explicit value information
2. Design conflicts between personas are resolved through a transparent, documented trade-off process
3. All trade-off decisions are traceable and auditable

## Background

Currently the factory bridges user needs to design decisions via REQ-PROC-026. This works for deriving design rules from individual personas but lacks a mechanism for resolving **conflicts between personas** (e.g., simplicity vs. depth, speed vs. accuracy). VCD fills this gap.

## Scope

### In Scope
- Adding "Primary Values" and "Value Conflicts" to all personas except `system_maintenance`
- `app_provider` persona: values sourced from real user (product owner), `evidence_method: grounded`
- All other client/therapist personas: values derived via three-pillar framework, `evidence_method: literature_derived`
- Value Trade-off Record format, template, and documentation skill (`vcd-log-tradeoff`)
- Adaptation of existing design/implementation skills to consult persona values at decision points
- Aggregation script to consolidate all trade-off records into `requirements_user_needs/_meta/value_tradeoff_summary.md`
- Limited retroactive exercise: 2-3 existing decisions documented as VTR records to validate the toolchain

### Out of Scope
- Standalone "Value Principles as Design Constraints" document — **CLOSED as NOT NEEDED** (aggregation script replaces it; see findings Q3)
- Changes to `system_maintenance` persona
- Full retroactive application to all past decisions (new decisions from activation date only; limited retroactive exercise for format validation is in scope)

## Key Design Decisions (Resolved — TASK-PROC-033-01)

All open design decisions were answered in the exploration task. See:
`tasks/2026-03-02_explore_vcd_integration/plans_and_protocols/2026-03-02_01_findings_vcd_exploration.md`

Decisions:
- **Value source methodology**: Three-pillar framework (Schwartz + Beauchamp-Childress + Nissenbaum) with Design-Relevance Filter
- **Standalone doc**: NOT needed — aggregation script replaces it (AC-10 closed)
- **Skills to adapt**: ux-validate-rule, ux-create-flow, code-complex, code-simple, requ-explore (lightweight additions only)
- **Trade-off trigger**: Mandatory when a decision degrades a persona's primary or secondary value to favor another's. Not triggered by single-persona or purely technical decisions.
- **Record placement**: Inline in the artifact where the decision is made (user flow, requirement, design rule)
- **Activation**: Forward-only from activation date; limited retroactive exercise (2-3 decisions) for format validation

## Value Trade-off Record Format (Finalized)

```markdown
### Value Trade-off: [Short Descriptive Title]

<!-- vcd-record
id: VTR-[NNN]
date: [YYYY-MM-DD]
artifact: [relative path to the file containing this record]
personas:
  - id: [PERSONA-NNN]
    value: [value name]
    impact: [supported | degraded | neutral]
  - id: [PERSONA-NNN]
    value: [value name]
    impact: [supported | degraded | neutral]
decision_status: [decided | open]
decided_by: [user | ai_recommended]
-->

- **Problem**: [What conflict or tension exists between persona values?]
- **Personas & Values**: [Which personas are affected? Which specific values are in tension?]
- **Options Considered**:
  1. [Option A]: [description and value impacts]
  2. [Option B]: [description and value impacts]
- **Decision**: [What was decided? Or "OPEN — awaiting user decision" if unresolved]
- **Rationale**: [Why this decision over alternatives?]
- **Consequences**: [What trade-offs does this decision accept?]
```

Template file: `requirements_user_needs/_meta/value_tradeoff_record_template.md`

## Related Requirements
- REQ-PROC-026: User Needs to Design System Bridge (VCD extends this)
- REQ-PROC-027: User Needs Content Creation (VCD adds mandatory fields)
