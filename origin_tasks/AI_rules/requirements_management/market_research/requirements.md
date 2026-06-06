---
id: REQ-PROC-029
status: defined
urgency: 2
urgency_reason: U2-PLANNED
impact: 4
impact_reason: I4-PRODUCT_DIRECTION
effort: L
stakeholder: developer
created: 2026-02-14
after: [REQ-PROC-009, REQ-PROC-027]
blocks: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Market research folder structure defined and documented"
    - id: AC-02
      text: "Workflow exists to push research findings into requirements_tasks/functional/ and requirements_tasks/non-functional/"
    - id: AC-03
      text: "Every research-influenced requirement references its market research source"
    - id: AC-04
      text: "The workflow supports adding new research rounds incrementally"
    - id: AC-05
      text: "Quality evaluation process defined for research gaps and coverage"
---

# Market Research Integration

## User Story

As a developer, I want market research continuously incorporated into the requirements process, so that feature priorities and decisions are grounded in evidence that real users are willing to use the app — and so those decisions remain traceable and reevaluable as new research data arrives.

## Overview

This requirement defines a **3rd requirements flow** alongside the two existing ones:

1. **User Needs Flow**: Persona → Scenario → User Flow → Functional Requirement
2. **Design Bridge Flow**: User Needs → UX/Design System Rules (REQ-PROC-026)
3. **Market Research Flow** *(this)*: Market Research → Feature Priorities & Decisions

Market research provides an outside-in perspective: are there real users in the market who would use this? Do competitors show what works? Does the data support building a given feature at all? This flow does not replace user needs — it validates, challenges, and prioritizes them.

## Scope

### In Scope
- Storing and versioning market research data inside the project
- A workflow for translating research findings into influence on requirements
- Traceable references: every market-research-influenced decision cites its source
- Extensibility: new research rounds can be added without restructuring

### Out of Scope
- Conducting the research itself (done externally, e.g., via Gemini, surveys)
- Replacing the persona/user-needs flow with market data

## Acceptance Criteria

- [ ] Market research folder structure defined and documented
- [ ] Workflow exists to push research findings into `requirements_tasks/functional/` and `requirements_tasks/non-functional/`
- [ ] Every research-influenced requirement references its market research source
- [ ] The workflow supports adding new research rounds incrementally
- [ ] Quality evaluation process defined for research gaps and coverage
