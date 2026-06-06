---
id: REQ-PROC-032
status: active
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
effort: XL
stakeholder: developer
created: 2026-02-28
updated: '2026-06-06'
after: []
blocks: []
market_research_refs: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      name: Scribble Core Artifact feature exists
      description: "feat_scribble_core_artifact/requirements.md has status: defined or active"
    - id: AC-02
      name: Iteration and Rule Protocol feature exists
      description: "feat_iteration_and_rule_protocol/requirements.md has status: defined or active"
    - id: AC-03
      name: Handoff Skills and Contract feature exists
      description: "feat_handoff_skills_and_contract/requirements.md has status: defined or active"
    - id: AC-04
      name: Scribble Content Extensions feature exists
      description: "feat_scribble_content_extensions/requirements.md has status: defined or active"
    - id: AC-05
      name: Consistency SCI Layer feature exists
      description: "feat_consistency_sci_layer/requirements.md has status: defined or active"
    - id: AC-06
      name: Carrier and Auto-Review feature exists
      description: "feat_carrier_and_auto_review/requirements.md has status: defined or active"
    - id: AC-07
      name: Embedded Flow Viewer feature exists
      description: "feat_embedded_flow_viewer/requirements.md has status: defined or active"
  sections: []
---

# UI Scribble Iteration Workflow


## Purpose

As a developer, I want the AI to produce UI that matches my vision — respecting the design system, applying correct information architecture, and grounding decisions in persona constraints. However, design rules are inherently incomplete: a fixed rule set cannot anticipate everything every screen needs.

Rather than specifying all rules upfront (which requires knowing all edge cases in advance), the preferred approach is to iterate: let the AI generate a lightweight UI scribble first, review it, identify missing rules, anchor those rules, then refine. This is more efficient because the first iteration is always a throwaway — it reveals where rules are missing.

Iterating directly in real Flutter code is costly because:
- Flutter widget trees are complex and deeply nested
- Implementation already couples to Domain layer (data binding, events)
- Restructuring UI architecture (e.g., switching from form to wizard) requires extensive refactoring

A lightweight, static scribble format enables fast and cheap iteration before any Flutter work begins. Post-implementation, two dedicated skills handle structural verification and visual polish iteration on the real code.


## Features

This epic is non-implementable. All acceptance criteria and body sections have been
distributed to the following child feature requirements:

| Feature | REQ-ID | Folder |
|---------|--------|--------|
| Scribble Core Artifact | REQ-PROC-032-01 | [feat_scribble_core_artifact](feat_scribble_core_artifact/requirements.md) |
| Iteration and Rule Protocol | REQ-PROC-032-02 | [feat_iteration_and_rule_protocol](feat_iteration_and_rule_protocol/requirements.md) |
| Handoff Skills and Contract | REQ-PROC-032-03 | [feat_handoff_skills_and_contract](feat_handoff_skills_and_contract/requirements.md) |
| Scribble Content Extensions | REQ-PROC-032-04 | [feat_scribble_content_extensions](feat_scribble_content_extensions/requirements.md) |
| Consistency SCI Layer | REQ-PROC-032-05 | [feat_consistency_sci_layer](feat_consistency_sci_layer/requirements.md) |
| Carrier and Auto-Review | REQ-PROC-032-06 | [feat_carrier_and_auto_review](feat_carrier_and_auto_review/requirements.md) |
| Embedded Flow Viewer | REQ-PROC-032-07 | [feat_embedded_flow_viewer](feat_embedded_flow_viewer/requirements.md) |

## References

- [REQ-PROC-044](../../epic_factory_quality/requirements.md) — Software Factory Quality. The scribble–coder contract (SEC-15) is surfaced through the per-skill `contract.yaml` / `.claude/schemas/` mechanism that REQ-PROC-044 establishes; the `ui-scribble-*` producer split and the revision channel referenced in SEC-16 were built under its program.
- [REQ-PROC-026](../../requirements_management/user_needs_to_design_system_bridge/requirements.md) — Persona–design bridge / T1·T2·T3 tier model that the rule-reviewer and persona-walker apply (referenced throughout SEC-04, SEC-07, SEC-16).

