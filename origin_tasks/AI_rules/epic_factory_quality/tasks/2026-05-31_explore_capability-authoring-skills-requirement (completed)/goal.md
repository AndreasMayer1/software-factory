---
task_id: TASK-PROC-044-16
type: explore
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-05-31
effort: M
created: 2026-05-31
started: 2026-05-31
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Promote REQ-PROC-044 to an epic and author a new feature requirement for the factory's capability-authoring meta-skills (incl. claude-create-agent/claude-modify-agent with a Domain-Vocabulary authoring aid); migrate the existing meta-skills under it."
release_description: ""
opus_recommended: true   # reason: requirements restructure (epic promotion) + cross-cutting factory-capability requirement authoring — architectural judgment
writes_requirements: true
requirements_version:
  commit: a7fe5b32
  file: ../requirements.md
---

# Goal: Factory Capability-Authoring Skills — epic promotion + new feature requirement

## Objective

The factory has a family of **capability-authoring meta-skills** — skills whose job is to create or change the factory's own capabilities (`claude-create-skill`, `claude-modify-skill`, `claude-write-script`, `claude-modify-ordering-rules`). Their quality directly determines factory quality. Two things are unresolved:

1. **There is no governed way to author or modify agents.** `.claude/agents/*.md` files are created ad-hoc (the `ui-scribble-*` agents shipped without a skill; the 6 general agents have no `## Domain Vocabulary`). The developer approved a dedicated `claude-create-agent` / `claude-modify-agent` pair (TASK-PROC-032-10 file 14) but it was never built — 044-08 only codified the *sub-skill-vs-agent split rubric* into the skill-authoring skills, not agent authoring.
2. **These meta-skills have no single requirement owning them.** They are scattered; "good skills to do this result in a good factory," but nothing defines what "good" means for them as a family.

This task enters that space: should REQ-PROC-044 become an epic that contains a feature requirement for these capability-authoring skills, and what must that requirement guarantee?

## Background

Seeded by the TASK-PROC-032-10 quality review (TASK-PROC-032-16). The developer's decision: create a new requirement bundling the factory's capability-authoring skills, with **REQ-PROC-044 promoted to an epic (`epic_factory_quality`)** as the parent, and the existing meta-skills **migrated** under the new feature now.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-31_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show a7fe5b32:requirements_tasks/process/AI_rules/factory_quality/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking — empathize before defining, diverge before converging. The structural decision (epic promotion) is already made by the developer; the open work is *what the feature requirement must guarantee* so that agent/skill authoring reliably produces high-quality, non-shallow capabilities.

## Seeds

1. **Epic promotion shape.** REQ-PROC-044 is a flat `active` requirement with 7 cross-cutting quality ACs (AC-01..07). Which of those are genuinely epic-level invariants (stay at the epic) vs. feature-level? What is the minimal, clean `epic_factory_quality` body (≤90 lines per the epic size gate)?

2. **What must `claude-create-agent` / `claude-modify-agent` guarantee?** Naming scheme (collision-checked against built-ins, Han imports, existing agents); `allowed_tools` heuristic by intent class (no bare `*` without justification); a when-to-create-an-agent gate (disqualifying questions vs. extending an existing skill/agent); required structural sections (≤50-token role identity, `## Domain Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules`); an agent-vs-session suitability check (from TASK-PROC-032-10 file 13 §5).

3. **The Domain-Vocabulary authoring aid (capability D9).** How does a skill push an LLM past shallow vocabulary to 10–25 expert-tier terms passing the "15-year practitioner test"? These terms are rare on the web (book/research-tier). What instruction design, and what role for web/research lookup, makes this work? This capability is the home of the previously-dropped D9 (Domain Vocabulary + Anti-Patterns for the 6 existing agents — applied later via the new skill).

4. **Migration scope.** Bring `claude-create-skill`, `claude-modify-skill`, `claude-write-script`, `claude-modify-ordering-rules` under the new feature requirement now. What does "owned by this requirement" mean concretely — cross-link existing ACs (e.g. REQ-PROC-044 AC-03 split rubric), or restate? Avoid duplicate/stale ownership.

5. **Relationship to the skill-interface-contract mechanism (REQ-PROC-044 program).** The new skills must emit `contract.yaml` and follow the split rubric already shipped. How do they integrate without re-deriving that mechanism?

## Execution Model

Gather raw material, synthesize iteratively. The session's model is fixed at launch (Opus). Requirements authoring goes through `requ-explore` (this task `writes_requirements: true`).

**Web research**: if needed (e.g. agent-prompt design best practices, expert-terminology sourcing), delegate to a spawned `general-purpose` agent with a focused question; never run WebSearch inline.

## Output

A future implementer can: see `epic_factory_quality` with a clean ≤90-line body; read `feat_capability_authoring_skills/requirements.md` with ACs that make agent/skill authoring quality verifiable (agent-authoring governance + Domain-Vocabulary aid + migration ownership); and derive the impl tasks (create the skill pair; apply Domain Vocabulary to the 6 existing agents) from those ACs.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] REQ-PROC-044 is promoted to an epic and `feat_capability_authoring_skills/requirements.md` exists with ACs covering agent-authoring governance, the Domain-Vocabulary authoring aid, and meta-skill ownership/migration

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies (it unblocks N1/N2 and the scribble agent-editing tasks) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-16](../../../workflows/ui_sketch_iteration_workflow/tasks/2026-05-31_explore_review-scribble-contract-explore-task/goal.md) | Origin — the quality review whose remediation plan seeded this task |
