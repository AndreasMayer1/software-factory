---
id: REQ-PROC-044
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: L
stakeholder: app_provider
created: 2026-04-22
updated: 2026-05-31
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Every skill has a documented, reachable output: given a valid set of input artifacts, an agent following the skill produces the expected output artifact without silent failure"
    - id: AC-02
      text: "The artifact pipeline is traceable from any code file back through its originating task, requirement, flow, scenario, and persona without gaps in the chain"
    - id: AC-03
      text: "Any new task type, artifact layer, or skill can be integrated into the factory without modifying existing skills or scripts that do not consume the new type"
    - id: AC-04
      text: "Malformed or missing input artifacts cause a visible warning or graceful stop — they never cause a skill to silently produce incorrect output or corrupt a downstream artifact"
    - id: AC-05
      text: "Non-deterministic LLM behavior is isolated to clearly defined decision points; all deterministic steps (ID allocation, status transitions, file writes, script outputs) produce identical results for identical inputs"
    - id: AC-06
      text: "The set of active skills, their artifact dependencies, and the ordering rules governing task execution are documented in a single authoritative location that is kept current as the factory evolves"
    - id: AC-07
      text: "Session read-event logs under .factory/session_logs/ are bounded in age: at each aggregator run, logs whose most recent record timestamp predates the configured retention window (default: 30 days) are pruned; the heat overlay and emitted optimizer events reflect only logs within that window"
      target_package: unassigned
    - id: AC-08
      text: "Every active external factory-boundary interface (E1–E9: developer question-response, product intake, developer notes, web research, OS tooling, dependency admission, release, pending-question schema, and optimizer event channel) has a declared contract in the same format as internal skill contracts, with quality_criteria entries referencing the external-state postcondition vocabulary at scripts/factory/external_state/; a boundary-contract lint resolves each check: term to a concrete validator script and runs in the per-change quality gates; a failing external-state check produces a visible warning or graceful stop"
      target_package: unassigned
personas_served: [PERSONA-004]
---

# Epic: Software Factory Quality

## Overview

The Software Factory is a second-order production system — it produces the Flutter app. This epic groups the quality properties the factory must hold as a whole and the meta-capabilities that author the factory's own building blocks (skills, agents, scripts, ordering rules).

## Purpose

Defects in the factory compound: a broken skill, an inconsistent state model, or an opaque information flow can silently corrupt all downstream work before anyone notices. Factory quality therefore depends both on cross-cutting properties (reliability, transparency, determinism) and on the quality of the meta-skills that create or change factory capabilities — "good authoring tools produce a good factory."

## Scope

- **Included**: factory-wide quality invariants (the eight cross-cutting ACs below); governance of the capability-authoring meta-skills (skill, agent, script, ordering-rule authoring).
- **Excluded**: the app's user-facing functional/non-functional requirements; the per-skill behaviour of individual non-authoring skills (owned by their own requirements).

## Features

- **feat_capability_authoring_skills** — governs the meta-skills that create/modify factory capabilities (skill, agent, script, ordering-rule authoring), incl. the Domain-Vocabulary authoring aid. See `feat_capability_authoring_skills/requirements.md`.
- **feat_artifact_model** — the controlled artifact vocabulary: a registry of artifact definitions (`.factory/registry/artifacts.yaml`) plus a lint binding every `contract.yaml` producer/consumer edge and every governed agent name to a defined token. See `feat_artifact_model/requirements.md`.
- **feat_interactive_feedback_capture** — captures developer steering decisions made during interactive skill sessions as `feedback-checkpoint` artifacts, completing the artifact class for both interactive and automated modes. See `feat_interactive_feedback_capture/requirements.md`.

## Cross-Feature Invariants

These eight ACs (frontmatter AC-01..AC-08) apply to **every** feature and every factory change — new skill, modified script, updated rule:

1. **Functional reliability (AC-01)** — a skill given valid inputs produces the expected output without silent failure; no "succeeds but emits an artifact a downstream skill cannot consume".
2. **Transparency (AC-02, AC-06)** — any code traces back to task → requirement → flow → scenario → persona, and the active skills, their artifact dependencies, and ordering rules are documented in one authoritative place kept current.
3. **Maintainability / extensibility (AC-03)** — a new task type, artifact layer, or skill integrates without modifying unrelated skills or scripts.
4. **Robustness (AC-04)** — malformed or missing inputs cause a visible warning or graceful stop, never silent corruption.
5. **Determinism (AC-05)** — deterministic steps (ID allocation, status transitions, file writes, script outputs) are fully reproducible; LLM non-determinism is confined to declared decision points.
6. **Instrumentation bounds (AC-07)** — read-event logs under `.factory/session_logs/` are age-bounded so stale signals never drive optimizer events.
7. **External-boundary contracts (AC-08)** — every active external channel (E1–E9) has a declared contract validated by a boundary-contract lint in the per-change gates.

## User Needs

PERSONA-004 (system_maintenance): the factory's own data-integrity, retention, and graceful-degradation guarantees protect downstream artifacts from silent corruption.

## Dependencies

- REQ-PROC-042: Intelligent Task Ordering — addresses AC-03 and AC-05 for the task-ordering dimension.
- REQ-PROC-006: Workflow Improvement Automation — addresses functional reliability through metrics-based improvement.

## References

- Strategic analysis (Opus, 2026-04-22): `requirements_tasks/process/AI_rules/requirements_management/task_ordering/tasks/2026-04-22_explore_intelligent-task-ordering/plans_and_protocols/2026-04-22_03_opus_strategic_analysis.md`
- Information flow overview: `.claude/factory_flows.md`
- Skill index: `.claude/skills/INDEX.md`
