---
id: REQ-PROC-039
status: active
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: No explicit process requirement for user flow quality; the guidelines exist but are not referenced from the requirements hierarchy"
impact: 4
impact_reason: "I4-QUAL: User flows are the primary source for requirements derivation — poor flows cascade into missed requirements"
effort: S
stakeholder: developer
created: 2026-03-21
updated: 2026-03-21
after: [REQ-PROC-010, REQ-PROC-027]
blocks:
  - REQ-PROC-040
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
      name: "Authoritative Guidelines"
      heading: "## Authoritative Guidelines"
  acceptance_criteria:
    - id: AC-01
    - id: AC-02
    - id: AC-03
    - id: AC-04
---

# High-Quality User Flows

## User Story

As a developer using the AI requirements workflow, I need user flows to follow established quality guidelines, so that requirements can be reliably derived from them without gaps or ambiguity.

## Purpose

User flows bridge user scenarios and functional requirements. They must be thorough enough that the `requ-derive-from-flow` skill (REQ-PROC-030) can extract a complete requirements matrix without additional context.

The quality rules for user flows are fully documented in the `requirements_user_needs/` README files (see below). This requirement exists to anchor those guidelines in the requirements hierarchy and ensure they are consulted whenever user flows are created or iterated.

## Authoritative Guidelines

All rules for writing good user flows are defined in `requirements_user_needs/`. The `ux-create-flow` skill enforces these by reading them before every flow creation or iteration.

| File | What it covers |
|------|----------------|
| `README_5_USER_FLOW_DEFINITION.md` | Flow template, exception model (happy path + named exceptions), writing checklist |
| `README_6_PCD_LAYER.md` | Resource cost column, sufficiency principle |
| `README_7_META_INFO_STANDARDS.md` | YAML frontmatter fields, flow IDs, evidence level markers |
| `README_8_CROSS-REFERENCING_SYSTEMS.md` | Bidirectional links between flows, scenarios, and epics/features |
| `README_10_WRITING_GUIDELINES.md` | Language, tone, and perspective rules |
| `README_12_REVIEW_STATUS.md` | Review lifecycle (draft → approved), review_history requirements |
| `README_13_CROSS_REFERENCE_NOTATION.md` | Cross-reference notation, `user_needs` YAML in requirements |
| `README_14_DEVIATION_DOCUMENTATION.md` | How to document deviations when a flow cannot fully satisfy a scenario |
| `README_15_TECHNOLOGY_NEUTRALITY.md` | Technology-agnostic language rules |

**These files are the source of truth. Do not duplicate their content here.**

## ux-flow-draft Automated / Manual Mode Mixing

- **AC-01**: `ux-flow-draft` CONTINUE mode resolves feedback from three canonical locations in priority order: (1) `automation/pending_feedback/<TASK_ID>/answer.md`, (2) `automation/answered_feedback/<TASK_ID>/answer.md`, (3) `<task_folder>/user_feedback/*.md`. If none have content, asks interactively. This enables free switching between automated and manual iteration modes without the user touching anything except `answer.md`.
- **AC-02**: After consuming an `answer.md` from `automation/pending_feedback/<TASK_ID>/`, `ux-flow-draft` moves the entire `pending_feedback/<TASK_ID>/` folder to `automation/answered_feedback/<TASK_ID>/` (same operation the orchestrator performs), atomically with the flow.md commit. This prevents the orchestrator from re-queueing an already-consumed answer.
- **AC-03**: In automated mode (`CLAUDE_AUTOMATED_MODE=1` + sentinel), end-of-iteration writes `automation/pending_feedback/<TASK_ID>/question.md` summarizing the iteration changes and asking for review, then calls `terminate_session.sh`. No interactive y/n prompt. Status remains `in_progress`; the `question.md` is the waiting signal.
- **AC-04**: `ux-flow-draft` never writes `status: active` to goal.md. The skill uses `in_progress` during iteration. `active` is a retired status that was previously used as a workaround.
