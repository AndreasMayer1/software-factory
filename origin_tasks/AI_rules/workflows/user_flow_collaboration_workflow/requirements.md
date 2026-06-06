---
id: REQ-PROC-040
status: active
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: The user flow lifecycle (creation, iteration, cross-flow alignment, requirements derivation) has no single governing requirement — it is distributed across guidelines files and individual skill implementations"
impact: 5
impact_reason: "I5-ENAB: User flows are the bridge between user needs and requirements. A well-governed flow lifecycle enables every downstream process; a broken one cascades into missed requirements and misaligned design decisions"
effort: ongoing
stakeholder: developer
created: 2026-03-27
updated: 2026-03-27
after: [REQ-PROC-039, REQ-PROC-030]
blocks: []
market_research_refs: [] # No relevant findings identified — pure internal process requirement
trackable_items:
  sections:
    - id: SEC-01
      name: "User Story"
      heading: "## User Story"
    - id: SEC-02
      name: "Purpose"
      heading: "## Purpose"
    - id: SEC-03
      name: "Outcome Requirements"
      heading: "## Outcome Requirements"
    - id: SEC-04
      name: "Scope Boundaries"
      heading: "## Scope Boundaries"
    - id: SEC-05
      name: "References"
      heading: "## References"
---

# User Flow Collaboration Workflow

## User Story

As a product developer, I want a governed process for creating, evolving, and connecting user flows, so that the entire lifecycle — from first draft to approved requirements input — is traceable, consistent, and resilient to change.

## Purpose

User flows are the primary bridge between user needs (personas, scenarios) and functional requirements. Their quality and consistency directly determine the quality of every downstream artifact.

This requirement governs the **lifecycle** of user flows — not the content rules for an individual flow (those are in REQ-PROC-039), but the process that takes a flow from non-existent to approved and keeps it consistent with the flows around it.

## Outcome Requirements

The following outcomes must hold at all times. They are stated as verifiable properties of the system, independent of how they are achieved.

### OR-1: Collaborative Creation

A user flow can always be initiated through a structured AI-human collaboration process. The result of that process meets all quality standards defined in REQ-PROC-039 without requiring manual post-editing by the developer.

### OR-2: Iterative Refinement

Any existing user flow can be revised in response to new information, user feedback, or evolving design decisions. Revision is non-destructive: prior content is traceable through the flow's version history. A flow at any lifecycle stage can receive feedback and be improved.

### OR-3: Lifecycle Transparency

Every user flow has a defined, observable status at all times. The progression from initial draft to approved is:
- Deterministic: the same inputs always produce the same status transition
- Reversible: a previously approved flow can re-enter review if its content is invalidated
- Auditable: every status change is logged with a reason

### OR-4: Cross-Flow Consistency

When a user flow's content changes — whether through iteration, feedback incorporation, or structural revision — all other flows that overlap in domain, persona, or scenario are assessed for impact. Identified inconsistencies are:
- Documented in the affected flows
- Tracked until resolved
- Never silently discarded

A flow reaches final approval only when cross-flow consistency has been verified.

### OR-5: Requirements Derivation Readiness

Every approved user flow is ready to serve as input to the requirements derivation process (REQ-PROC-030) without additional human curation. No gap analysis step is required after approval — all necessary information is already present in the flow artifact.

### OR-6: Cluster Approval

When multiple flows share overlapping scope, personas, or design decisions, they can be approved as a coherent group rather than independently. Group approval ensures mutual consistency and prevents isolated approvals from creating silent contradictions between flows.

## Scope Boundaries

This requirement governs the **workflow** — the lifecycle process and its outcomes. It does **not** govern:

- The content rules for individual flow documents → see REQ-PROC-039
- The mechanism for deriving requirements from approved flows → see REQ-PROC-030
- The rules for cross-referencing flows with scenarios, epics, or features → see guidelines in `requirements_user_needs/`

## References

- REQ-PROC-039: Quality standards for individual user flows (content rules)
- REQ-PROC-030: Requirements derivation from approved flows (downstream process)
- `requirements_user_needs/README_12_REVIEW_STATUS.md`: Review lifecycle and status definitions
- `requirements_user_needs/user_flows/FLOW_INDEX.md`: Registry of all user flows
