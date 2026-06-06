---
id: REQ-PROC-059
status: active
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
effort: S
stakeholder: developer
created: 2026-05-28
updated: 2026-05-28
after: [REQ-PROC-001, REQ-PROC-038]
blocks: []
market_research_refs: [] # No relevant findings identified — internal process principles
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Eight factory-wide LLM-work principles (a–h) are documented, each with a source reference and a one-line rationale"
    - id: AC-02
      text: "An irreversibility threshold decision rule is specified for principle (c): a prompt rule is promoted to a hook only when violating it is unrecoverable"
    - id: AC-03
      text: "The principles document does not contain skill-specific audits or remediation tasks; it states principles and decision rules only"
---

# Cross-Factory LLM Work Principles

> **⚠ Lifecycle / Governance — frozen for new use (2026-06-05):** This requirement remains **valid** — the principles below are in force and continue to govern factory changes. However, it must **not** be used as the home or parent for **new requirements or tasks**: it has grown into a catch-all that can absorb almost anything, which dilutes its scope. Its principles are slated to be **merged into other / new, more specifically-scoped features** over time. Parent new work to a properly-scoped requirement instead.

## Overview

Eight principles governing how the Software Factory interacts with LLMs. These are factory-wide — they apply to every skill, script, and agent, not to any single tool.

## Purpose

The factory accumulates skills, rules, and context over time. Without explicit principles, each addition optimizes locally (solving the immediate problem) while degrading globally (growing token cost, adding unreliable prompt-level rules, duplicating enforcement mechanisms). These principles provide a shared lens for evaluating any factory change.

They emerged from the claude-optimize redesign exploration (TASK-PROC-006-02, rounds 3–4) and were validated against external sources (Anthropic's context engineering guide, kaizen, hooks-as-policy research). They are codified here so that future claude-optimize runs can detect violations across the factory — but the audit itself is not part of this requirement.

## Principles

### (a) Scripts over instructions

Prefer deterministic scripts over LLM prompt instructions whenever possible. Scripts are testable, reproducible, and token-free at runtime. Prompt instructions are probabilistic and consume context on every session.

*Source: round-3 monitor-script architecture; round-4 §5.*

### (b) Token economy

Minimize token consumption: short skill descriptions, efficient context loading, minimal re-reading, lean CLAUDE.md. Every byte in always-loaded context costs on every session start.

*Source: Anthropic context engineering guide; user directive.*

### (c) Force, don't ask — with irreversibility threshold

Use hooks to enforce rules rather than relying on prompt-level instructions. An agent cannot violate what a hook prevents.

**Irreversibility threshold:** promote a prompt rule to a hook if and only if violating it is *unrecoverable* — data loss, secret leak, commit to protected branch, evaluation-surface corruption. Recoverable concerns (formatting, style, naming) stay in prompts. This prevents hook-bloat while ensuring critical invariants are mechanically enforced.

*Source: "Hooks: Policy as Code" (Ranjan Kumar); user directive; round-4 §5.*

### (d) Reserved

Originally the user's prediction that "there are probably more principles." Principles (e)–(h) fulfill that prediction. This slot is kept for numbering stability with the original user input.

### (e) Just-in-time context loading

Load context on demand, not upfront. Reference data by short identifiers; pull into the active window only when a skill or agent needs it. Large always-loaded context degrades every session — even sessions that never touch the loaded material.

*Source: Anthropic, "Effective context engineering for AI agents"; Morph reports ~95% baseline context reduction from lazy tool discovery.*

### (f) The feedback loop is the product

When a recurring failure is observed, prefer adding a deterministic gate or test over writing a new prompt-level instruction or a new skill. The path from "we keep seeing this mistake" to "add a gate" should be shorter than the path to "write a new skill."

*Source: Kobi Kadosh, "The Software Feedback Loop"; Anthropic Agent SDK verification hierarchy (rules-based > visual > LLM-as-judge).*

### (g) Sub-agent context isolation

Long explorations that do not need to leave evidence in the main conversation run in a sub-agent that returns a distilled summary. This preserves the quality of existing context and prevents irrelevant detail from consuming the main window.

*Source: Anthropic agent best practices; community (RichSnapp): "subagents preserve the quality of the context that already exists."*

### (h) Smallest set of high-signal tokens, as a measured target

Extend principle (b) from aspiration to metric: track per-task input-tokens-at-first-message. Flag regressions when a skill or CLAUDE.md edit pushes the median up. Token economy is not just a principle — it is a measurable property of the factory.

*Source: Anthropic context engineering guide.*

## Scope

This requirement states principles and the irreversibility threshold decision rule. It does **not**:
- Audit existing skills or CLAUDE.md against these principles
- Prescribe specific remediation tasks
- Define monitoring or enforcement mechanisms

Those activities belong to `claude-optimize` runs (REQ-PROC-006), which uses these principles as a detection lens.

## Developer Guidelines

### Key Decisions

- Principles are numbered (a)–(h) for stable cross-referencing. Slot (d) is reserved to maintain numbering continuity with the original user input.
- The irreversibility threshold (principle c) is the only principle with a formal decision rule. Other principles guide judgment but do not prescribe mechanical tests.
- Future principles may be added; existing principle letters and meanings remain stable.

### Common Pitfalls

- Treating these principles as enforcement mechanisms (they are evaluation criteria; enforcement happens via REQ-PROC-006 and the irreversibility threshold)
- Promoting every recoverable rule to a hook (violates the irreversibility threshold; produces hook-bloat that itself degrades the factory)
- Letting CLAUDE.md grow indefinitely (violates principles (b), (e), and (h))

## Related Requirements

- REQ-PROC-006: Workflow Improvement Automation — uses these principles as a detection lens for factory regressions
- REQ-PROC-044: Software Factory Quality Properties — these principles contribute to functional reliability and maintainability
- REQ-PROC-031: Smart and Cost-Efficient Model Switching — principle (b) aligns with cost efficiency goals
- REQ-PROC-008: Orchestrator Workflow — the orchestrator and its skills are evaluated against principles (a), (b), (e), (g)

## References

- Design exploration: `requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
- Round-4 synthesis (principles a–h with sources): `2026-05-16_08_opus_synthesis_round4.md` Part 5
- Hooks: Policy as Code: https://ranjankumar.in/hooks-policy-as-code-agent-enforcement
- Anthropic Effective Context Engineering for AI Agents
