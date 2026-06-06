---
id: REQ-PROC-044-03
status: implemented
stakeholder: developer
created: 2026-06-02
updated: 2026-06-02
parent: REQ-PROC-044
after: [REQ-PROC-044-02]
blocks: []
market_research_refs: [] # No relevant findings identified
user_needs:
  implements_flows: []
  addresses_scenarios: []
  personas_served: [PERSONA-015]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      target_package: unassigned
    - id: AC-02
      target_package: unassigned
    - id: AC-03
      target_package: unassigned
target_package: unassigned
---

# Interactive Feedback Capture

## Overview

In interactive (developer-present) skill sessions, when the developer steers a skill decision — modifies, redirects, or rejects the skill's proposal rather than approving it as-is — a `feedback-checkpoint` artifact is written to the affected task's `plans_and_protocols/` folder before the task is closed. This makes steered interactive decisions discoverable and persistent alongside the work they shaped, completing the feedback-checkpoint artifact class for both session modes.

## Purpose

When a skill reaches a decision gate in an interactive session and the developer steers the outcome, that decision encodes rationale that the produced artifact does not record. Currently this rationale exists only in the conversation and is silently lost after context compression. The automated-mode equivalent (via REQ-PROC-041-04) already captures this for unattended sessions — every answered question is archived as a `feedback-checkpoint` file. The gap is the interactive twin: interactive steering decisions have no equivalent capture mechanism.

The result is asymmetric observability: anyone reviewing the factory's decision history sees automated-mode checkpoints but not interactive-mode ones, even though both produce the same kinds of product-shaping decisions. This was identified in the exploration TASK-PROC-044-02-05, which surveyed 37 skills with developer-decision gates and found that the information worth preserving is precisely the "why" that the produced artifact does not record — and that this "why" is only present in steered decisions, not plain approvals.

## Behavior

When the developer approves a skill proposal as-is (no modification or redirection), no checkpoint file is produced — the produced artifact already reflects the proposal, and there is no additional rationale to capture.

When the developer steers — modifies, redirects, or rejects the skill's proposal — a `feedback-checkpoint` file exists in the task's `plans_and_protocols/` folder by the time the task is closed. The file captures the developer's words verbatim. Its name contains `feedback-checkpoint` so it falls within the registry token's glob (`requirements_tasks/**/plans_and_protocols/*feedback-checkpoint*.md`), making interactive and automated checkpoints discoverable in the same pass without additional tooling.

## Acceptance Criteria

- [ ] AC-01: For every developer-steered decision in an interactive skill session — where the developer modifies, redirects, or rejects the skill's proposal rather than approving it as-is — a `feedback-checkpoint` file exists in the affected task's `plans_and_protocols/` folder by the time the task is closed.
- [ ] AC-02: Each interactive `feedback-checkpoint` file conforms to the envelope format defined in REQ-PROC-041-04 AC-06, with `mode: interactive`; the body preserves the developer's decision verbatim.
- [ ] AC-03: Interactive `feedback-checkpoint` files contain `feedback-checkpoint` in their filename and reside in `requirements_tasks/**/plans_and_protocols/`, matching the registry token glob so they are discoverable alongside automated-mode checkpoints without additional tooling.

## Developer Guidelines

### Key Decisions

- Plain approvals do not produce a checkpoint file. The value of capture is the steering rationale — why the developer deviated from or overrode the proposal. An approved-as-is outcome adds no information beyond what the produced artifact already shows.
- The developer's words must be preserved verbatim. No rephrasing or AI-authored summary is an acceptable substitute — what is being preserved is the developer's intent in their own words, not an interpretation of it.
- Capture must occur before task closure while the decision is still in session context. Once context is compressed or the session ends, the rationale is unrecoverable.

### Common Pitfalls

- Writing a checkpoint for every gate interaction including plain approvals: produces a noisy index where most entries add no information.
- Rephrasing the developer's steering response: silently replaces the developer's intent with a model interpretation, defeating the purpose of the artifact.

## Related Requirements

- [REQ-PROC-041-04](../../../../workflows/epic_autonomous_task_execution/feat_feedback_pause_resume/requirements.md) — automated-mode twin: the orchestrator archives answered Q&A pairs as `feedback-checkpoint` files after resume; same artifact format, `mode: automated` instead of `interactive`.
- [REQ-PROC-044-02](../feat_artifact_model/requirements.md) — defines the `feedback-checkpoint` registry token (category: `task-workspace`, glob: `requirements_tasks/**/plans_and_protocols/*feedback-checkpoint*.md`) and the `user_input_gates:` contract field that declares which gates exist across skills.

## References

- Exploration synthesis: `requirements_tasks/process/AI_rules/epic_factory_quality/feat_artifact_model/tasks/2026-06-01_explore_interactive-feedback-checkpoint-artifact (completed)/plans_and_protocols/2026-06-02_01_synthesis.md`
- Registry token definition: `.factory/registry/artifacts.yaml`
