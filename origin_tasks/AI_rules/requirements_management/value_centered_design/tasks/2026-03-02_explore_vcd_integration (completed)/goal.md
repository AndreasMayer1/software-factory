---
task_id: TASK-PROC-033-01
type: explore
parent_requirement: REQ-PROC-033
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-PAIN
status: completed
completed: 2026-03-02
effort: M
created: 2026-03-02
after: []
awaiting: []
covers:
  acceptance_criteria:
    - AC-01
    - AC-02
    - AC-03
    - AC-04
    - AC-05
    - AC-06
    - AC-07
    - AC-08
    - AC-09
    - AC-10
  sections:
    - SEC-01
    - SEC-02
    - SEC-03
    - SEC-04
    - SEC-05
    - SEC-06
scope_description: "Explore all open questions for VCD integration before any implementation begins. Produce a consolidated findings document with answers, recommendations, and a proposed implementation plan."
requirements_version:
  commit: dcc97ff
  file: ../requirements.md
---

# Goal: Explore Value Centered Design Integration

## Objective

Before changing anything in the project, explore and answer all open questions around integrating Value Centered Design (VCD) into the software factory.

This task produces a comprehensive findings document that the next implementation tasks can build on directly.

## Background

VCD extends our current user-needs → design bridge (REQ-PROC-026) with an explicit value layer. Personas will carry "Primary Values" and "Value Conflicts" fields. Design decisions that pit persona values against each other must be documented in a structured Value Trade-off Record. The goal: transparent, auditable, consistent design decisions.

For complete requirements at task creation time:
```
git show dcc97ff:requirements_tasks/process/AI_rules/requirements_management/value_centered_design/requirements.md
```

Current requirements: ../requirements.md

## Open Questions to Answer

### Q1: Persona Value Sources (Critical — no real user research)
- **What we have**: `app_provider` = real user (product owner) → values can come directly from them
- **What we lack**: All other personas have no empirical user research backing their values
- **Questions**:
  - Can an AI meaningfully define persona values for therapeutic app users? What are the risks?
  - Are there published studies on values of people with mood disorders, anxiety, or therapy clients?
  - What methodology gives us the most defensible/useful values? (AI-derived? Literature-backed hybrid? Explicit uncertainty tagging?)
  - Should AI-derived values be tagged differently than user-confirmed values?

### Q2: Value Trade-off Record — Scope & Triggers
- When exactly is a Value Trade-off Record mandatory?
  - Every design decision? Only when personas conflict? Only at explicit conflict points?
- What is "too small" for a record? (Avoid documentation overhead killing productivity)
- Should records be inline (in the requirement/flow file) or in a separate log file per artifact?
- How do we handle code-level decisions — always reference back to the requirement?

### Q3: Standalone "Value Principles as Design Constraints" Document
- **User's concern**: High maintenance cost, AI can read values directly from persona files anyway
- **Potential benefit**: Central reference for quick lookup; makes conflicts visible at a glance
- **Questions**:
  - Is there a lightweight form that provides value without heavy maintenance?
  - Could the aggregation script (AC-08) replace this entirely?
  - Decision: needed or not?

### Q4: Skills Adaptation
- Which skills need adapting?
  - `ux-validate-rule`, `code-complex`, `code-simple`, `ux-create-flow`, `requ-explore`, others?
- What does "consult persona values" look like in a skill? (A checklist step? A mandatory question?)
- How do we avoid adding so much overhead that skills become slow?

### Q5: Aggregation Script (AC-08)
- What format should value trade-off records use so they are parseable by a script?
  - Markdown section with specific heading pattern?
  - YAML frontmatter block?
- Where does the aggregated output file live?
- What does the output file enable? (Audit, consistency checks, pattern review)

### Q6: VCD Activation Scope
- Apply VCD retroactively to existing decisions? Or only new decisions going forward?
- If forward-only: Do we mark a "VCD activation date" somewhere?

### Q7: Persona Count & Scope Confirmation
- Confirm: exclude `system_maintenance`, include `app_provider` and all 13 client/therapist personas
- Are there any other personas where value fields don't make sense?

## Scope

### In Scope
- Answer all 7 open question groups above
- Review relevant literature / design methodology frameworks for Q1
- Produce recommendations for: record format, trigger criteria, skill adaptation strategy, script approach
- Propose concrete acceptance criteria updates to requirements.md if questions reveal gaps
- Propose implementation task breakdown (which tasks follow this exploration)

### Out of Scope
- Any actual implementation (no persona files modified, no skills changed, no code written)
- Writing the trade-off records themselves (this is exploration only)

## Acceptance Criteria

- [ ] All 7 question groups answered with clear, actionable recommendations
- [ ] Q1 (value sources) answered with a chosen methodology + risk assessment
- [ ] Q3 (standalone doc) decision closed: needed or not, with justification
- [ ] Value Trade-off Record format finalized (incl. parseable marker for aggregation script)
- [ ] List of skills to adapt produced, with brief description of what changes
- [ ] Implementation task breakdown proposed (task list for follow-up impl tasks)
- [ ] All findings written to `plans_and_protocols/2026-03-02_01_findings_vcd_exploration.md`

## Dependencies

None — this is the first task for REQ-PROC-033.

## Notes

- User preference: AI flags value conflicts and pauses for human decision, rather than auto-resolving
- User preference: Aggregation script (not a static "Value Principles" doc) for audit/review
- app_provider values: product owner will provide these directly
- system_maintenance: explicitly excluded from VCD fields
