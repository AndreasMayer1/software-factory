---
id: REQ-PROC-044-01
status: active
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
effort: M
stakeholder: app_provider
created: 2026-05-31
after: []
blocks: []
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Creating or modifying a `.claude/agents/*.md` file is governed by a dedicated `claude-create-agent` / `claude-modify-agent` skill pair: the pair enforces a collision-checked naming scheme (against Claude built-in agents, Han imports, and existing project agents), an `allowed_tools` heuristic by intent class (no bare `*` without a recorded justification), a when-to-create-an-agent gate, the required structural sections, and an agent-vs-session suitability check — an agent file authored through the pair always carries those sections and passes those checks. The name follows the scheme `{expertise}-{role}`: `role` is the agent's output type drawn from the closed set {writer, transformer, reviewer, classifier} (a 2×2 partition over the axes persist-vs-return and synthesized-vs-mechanical), extended only by demonstrating a new output-type axis and never for an activity, lifecycle, or tool difference; `expertise` names the artifact-or-lens token the agent operates on, drawn from the artifact registry (REQ-PROC-044-02), with the artifact never placed in the role slot and the operation never in the expertise slot; an agent that maps to zero or to two-or-more roles causes the pair to stop and ask the developer; the collision check is retained as a sub-rule"
      target_package: unassigned
    - id: AC-02
      text: "Every agent authored or modified through the pair has a role identity of ≤50 tokens and contains the sections `## Domain Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, and `## Rules`"
      target_package: unassigned
    - id: AC-03
      text: "The capability-authoring skills include a Domain-Vocabulary authoring aid that produces 10–25 expert-tier terms for the agent's domain, each passing the \"15-year practitioner test\" (a term a 15-year practitioner would use that a novice would not), with shallow/common-web vocabulary rejected; terms are formatted as a single comma-separated plain-text line (no bullets, no bold, no inline explanations) — the term alone activates the LLM's existing domain knowledge; the han-adversarial-validator agent is the reference model for this format"
      target_package: unassigned
    - id: AC-04
      text: "An agent or skill authored through the pair integrates with the skill-interface-contract mechanism without re-deriving it: it emits/maintains its `contract.yaml` and conforms to the sub-skill-vs-agent split rubric already established under REQ-PROC-044 (AC-03), referencing that rubric rather than restating it"
      target_package: unassigned
    - id: AC-05
      text: "The factory's capability-authoring meta-skills — `claude-create-skill`, `claude-modify-skill`, `claude-create-agent`, `claude-modify-agent`, `claude-write-script`, `claude-modify-ordering-rules` — are owned by this feature: a single authoritative index lists them as the governed set, and each ownership entry cross-links the existing ACs that already govern a meta-skill (e.g. REQ-PROC-044 AC-03 split rubric) rather than duplicating them"
      target_package: unassigned
    - id: AC-06
      text: "Establishing an artifact type is a human-authorized act: when an authoring skill (`claude-create-skill`/`claude-modify-skill`, `claude-create-agent`/`claude-modify-agent`) would emit a `produces:`/`derived_from:` token, or compose an agent-name artifact-or-lens segment, that is absent from the artifact registry (REQ-PROC-044-02), it eagerly proposes a registry entry (token + path + definition) which the developer ratifies, renames to an existing token, or rejects before authoring proceeds; the entry is appended only on ratification and a duplicate or alias is refused; in automated mode the proposal escalates via pending_feedback rather than auto-appending; initial seeding of the registry is this same gate applied to the proposed initial token set; the resolve lint (REQ-PROC-044-02 AC-02) is the backstop for anything authored outside these skills."
      target_package: unassigned
personas_served: [PERSONA-004]
---

# Capability-Authoring Skills

## Overview

The factory authors its own building blocks through a family of **capability-authoring meta-skills**: skills and scripts whose job is to create or change what the factory can do (`claude-create-skill`, `claude-modify-skill`, `claude-create-agent`, `claude-modify-agent`, `claude-write-script`, `claude-modify-ordering-rules`). Their output quality directly determines factory quality. This feature defines what these meta-skills must guarantee and brings them under single ownership.

## Purpose

Two gaps motivated this feature (TASK-PROC-032-10 quality review → TASK-PROC-032-16 remediation):

1. **There was no governed way to author or modify agents.** `.claude/agents/*.md` files were created ad-hoc — the `ui-scribble-*` agents shipped without a skill, and the six general agents (architecture-advisor, implementation-engineer, opus-advisor, quality-checker, setup-optimizer, test-engineer) carry no `## Domain Vocabulary`. Skill authoring is governed by `claude-create-skill`/`claude-modify-skill`; agent authoring had no equivalent. A poorly-scoped agent (over-broad `allowed_tools`, a name colliding with a built-in, a missing protocol section, shallow domain vocabulary) degrades every task it touches.
2. **The meta-skills had no single requirement owning them.** They were scattered; "good authoring tools make a good factory," but nothing defined what "good" meant for them as a family.

This matters now because the recovered scribble-pipeline work (REQ-PROC-032 AC-37..41) and routine agent maintenance both depend on a reliable agent-authoring path existing first.

## Behavior

**Agent authoring is governed.** A new or changed `.claude/agents/*.md` file is produced through `claude-create-agent` / `claude-modify-agent`. The pair enforces, as observable end-state properties of the resulting agent file:

- **Naming**: the agent name follows `{expertise}-{role}` — `role` from the closed output-type set {writer, transformer, reviewer, classifier}, `expertise` an artifact-or-lens token drawn from the artifact registry (REQ-PROC-044-02); the artifact never appears in the role slot nor the operation in the expertise slot; a name that maps to zero or ≥2 roles triggers stop-and-ask. Collision-checking against Claude built-in agents, Han-imported agents, and existing project agents remains a sub-rule; a colliding name is rejected before the file is written.
- **Artifact establishment**: a `produces:`/`derived_from:` token or an agent-name artifact-or-lens segment absent from the artifact registry (REQ-PROC-044-02) is eagerly proposed at authoring time and the developer ratifies (renames to an existing token, or rejects) before authoring proceeds; appended only on ratification, duplicates/aliases refused, automated mode escalates via `pending_feedback`. Initial seeding is the same gate over the proposed initial token set.
- **`allowed_tools` by intent class**: the tool list matches the agent's intent class (e.g. a read-only reviewer gets read/search tools, not `Write`/`Bash`); a bare `*` appears only with a recorded justification.
- **When-to-create gate**: a set of disqualifying questions distinguishes "this needs a new agent" from "extend an existing skill or agent"; an agent is created only when the gate passes.
- **Required sections**: the agent file has a role identity of ≤50 tokens and the sections `## Domain Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules`.
- **Agent-vs-session suitability**: a check confirms the work belongs in a spawned agent rather than the main session (per TASK-PROC-032-10 file 13 §5).

**Domain-Vocabulary authoring aid.** The pair produces 10–25 expert-tier terms for the agent's domain. Each term passes the "15-year practitioner test": it is vocabulary a long-time practitioner uses that a novice would not. Because such terms are book/research-tier and rare on the open web, the aid is instruction-driven and may draw on delegated web/research lookup; shallow or common-web vocabulary is rejected rather than padded in. This aid is the home of the previously-dropped capability D9 — the same mechanism later applies `## Domain Vocabulary` + `## Anti-Patterns` to the six existing agents.

**Contract-mechanism integration.** Agents and skills authored through the pair integrate with the skill-interface-contract mechanism established under REQ-PROC-044 (sidecar `contract.yaml` + schemas + lint): they emit/maintain their contract and follow the sub-skill-vs-agent split rubric (REQ-PROC-044 AC-03) rather than re-deriving it.

**Single ownership of the meta-skill family.** The six capability-authoring meta-skills are listed in one authoritative index as the governed set. Ownership cross-links the existing ACs that already govern a meta-skill (notably REQ-PROC-044 AC-03's split rubric, codified into `claude-create-skill`/`claude-modify-skill`) instead of duplicating them, so there is no stale or double ownership.

## Examples

- **Existing meta-skills**: `.claude/skills/claude-create-skill/SKILL.md` (naming convention, phase-split rubric, `tools:` discipline), `.claude/skills/claude-modify-skill/`, `.claude/skills/claude-write-script/`, `.claude/skills/claude-modify-ordering-rules/`.
- **Existing agents needing the new sections**: `.claude/agents/architecture-advisor.md`, `quality-checker.md`, `implementation-engineer.md`, `opus-advisor.md`, `setup-optimizer.md`, `test-engineer.md`.
- **Ad-hoc agents to bring under the rubric**: the `ui-scribble-*` agents shipped by TASK-PROC-044-07.

## Developer Guidelines

### Key Decisions

- The agent-authoring skills are a **standalone pair** (`claude-create-agent` / `claude-modify-agent`), not folded into the skill-authoring skills — agent files have a distinct structure (role identity, `allowed_tools`, protocol sections) that warrants dedicated governance.
- `allowed_tools` defaults to the **narrowest set** that satisfies the agent's intent class; widening to `*` requires a recorded justification (mirrors the `tools: "*"` rule in `claude-create-skill`).
- The Domain-Vocabulary aid must **push past shallow vocabulary**: the bar is the 15-year-practitioner term, not the first ten words a web search returns.
- Ownership is recorded by **cross-link, not restatement**: an existing AC governing a meta-skill (e.g. the split rubric) stays where it is and is referenced.

### Common Pitfalls

- An agent named identically to a Claude built-in or a Han import silently shadows it — the collision check exists to prevent this.
- A `## Domain Vocabulary` section padded with generic terms passes a line count but fails the practitioner test — it must be rejected, not accepted.
- Restating an existing meta-skill AC under this feature creates two sources of truth that drift apart — always cross-link.

## Related Requirements

- REQ-PROC-044: Software Factory Quality (parent epic) — the cross-cutting quality invariants this feature's meta-skills must uphold; AC-03 (extensibility / split rubric) and the contract mechanism are referenced, not duplicated.
- REQ-PROC-032 (ui_sketch_iteration_workflow) — its scribble-pipeline tasks edit `ui-scribble-*` agents through `claude-modify-agent`; this feature is the prerequisite that makes those references valid.
- [REQ-PROC-044-02](../feat_artifact_model/requirements.md) — Artifact Model: defines the artifact registry this feature's naming scheme draws from (the `expertise` token) and that validates agent names; the naming AC references it rather than restating registry rules.
- REQ-PROC-042: Intelligent Task Ordering — owns `claude-modify-ordering-rules` behaviour; this feature owns the skill as part of the meta-skill family by cross-link.
- [REQ-PROC-043](../../../tooling_rules/scripts_organization/requirements.md) — owns `claude-write-script` and the scripts-organization rules; this feature owns `claude-write-script` as part of the meta-skill family by cross-link, referencing REQ-PROC-043's governing ACs rather than duplicating them.

## References

- `.claude/skills/claude-create-skill/SKILL.md`, `.claude/skills/INDEX.md`
- `.claude/agents/` (existing agent files)
- Remediation plan §A2: `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-05-31_explore_review-scribble-contract-explore-task/plans_and_protocols/2026-05-31_03_remediation_plan.md`
