---
task_id: TASK-PROC-044-01-01
type: impl
parent_requirement: REQ-PROC-044-01
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-31
started: 2026-05-31
completed: 2026-05-31
session_completed_at: 2026-05-31T15:14:47Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05]
  sections: []
scope_description: "Create the claude-create-agent and claude-modify-agent skills (via claude-create-skill), baking in governed agent authoring, required sections, the Domain-Vocabulary aid, contract integration, and single meta-skill ownership."
release_description: ""
opus_recommended: true  # reason: skill design + agent-authoring judgment + domain-vocabulary pedagogy (synthesis-dependent)
writes_requirements: false
requirements_version:
  commit: 6ece1dc7
  file: ../../requirements.md
session_id: 24743901-2c9e-411f-b98a-cff14bafd4fa
session_account: gmail
---
# Goal: Create the claude-create-agent / claude-modify-agent skill pair

## Objective

Create two new meta-skills, `claude-create-agent` and `claude-modify-agent`, that
govern the authoring and modification of `.claude/agents/*.md` files — the agent
equivalent of the existing `claude-create-skill` / `claude-modify-skill` pair.
Both skills MUST be created USING the `claude-create-skill` skill (mandatory for
skill creation; do not hand-roll the SKILL.md structure).

The pair must bake in, as enforced and observable end-state guarantees on the
resulting agent file, the five behaviours below (mapped to the parent ACs).

## Requirements Summary

REQ-PROC-044-01 (Capability-Authoring Skills) defines what the factory's
capability-authoring meta-skills must guarantee and brings them under single
ownership. This task delivers the previously-missing agent-authoring path.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

- **AC-01 — governed agent authoring.** Both skills enforce:
  - a **collision-checked naming scheme** — the agent name is checked against
    Claude built-in agents, Han-imported agents (e.g. `han-adversarial-validator`),
    and existing project agents under `.claude/agents/`; a colliding name is
    rejected before the file is written;
  - an **`allowed_tools` heuristic by intent class** — the narrowest tool set that
    satisfies the agent's intent class (a read-only reviewer gets read/search
    tools, not `Write`/`Bash`); a bare `*` appears only with a recorded
    justification (mirrors the `tools: "*"` rule in `claude-create-skill`);
  - a **when-to-create-an-agent gate** — disqualifying questions distinguishing
    "needs a new agent" from "extend an existing skill or agent"; an agent is
    created only when the gate passes;
  - the **agent-vs-session suitability check** per TASK-PROC-032-10 file 13 §5 —
    confirms the work belongs in a spawned agent rather than the main session.
- **AC-02 — required structural sections.** Every agent authored/modified through
  the pair has a role identity of ≤50 tokens and the sections `## Domain
  Vocabulary`, `## Anti-Patterns`, `## Protocols`, `## Output`, `## Rules`.
- **AC-03 — Domain-Vocabulary authoring aid (home of capability D9).** Produces
  10–25 expert-tier terms for the agent's domain, each passing the "15-year
  practitioner test" (a term a long-time practitioner uses that a novice would
  not). The aid is instruction-driven with strong language pushing the LLM past
  shallow/common-web vocabulary; it MAY delegate web/research lookup (these are
  book/research-tier terms, rare on the open web — delegate to a spawned
  general-purpose agent, never run WebSearch inline). Shallow or common-web
  vocabulary is REJECTED, not padded in to hit the count.
- **AC-04 — contract-mechanism integration.** Agents and skills authored through
  the pair emit/maintain their `contract.yaml` per the REQ-PROC-044 mechanism and
  REFERENCE the sub-skill-vs-agent split rubric (REQ-PROC-044 AC-03) rather than
  re-deriving it.
- **AC-05 — single meta-skill ownership.** Record, in `.claude/skills/INDEX.md`,
  the six capability-authoring meta-skills as the governed set: the two new skills
  plus `claude-create-skill`, `claude-modify-skill`, `claude-write-script`,
  `claude-modify-ordering-rules`. Each ownership entry CROSS-LINKS the existing AC
  that already governs that meta-skill (e.g. REQ-PROC-044 AC-03 split rubric;
  REQ-PROC-042 for ordering rules; REQ-PROC-043 for write-script) rather than
  duplicating it. `claude-create-skill` handles the INDEX.md + factory_flows.md
  updates for the two new skills.

### Out of Scope

- Applying `## Domain Vocabulary` / `## Anti-Patterns` to the six existing agents
  — that is TASK-PROC-044-01-02 (which exercises this skill's AC-03 aid).
- **Deferred (YAGNI):** retro-justifying the `ui-scribble-*` agents under the new
  rubric — reopen when: a REQ-PROC-032 scribble task edits those agents through
  the new pair (tracked there, not here).

## Acceptance Criteria

- [x] `claude-create-agent` and `claude-modify-agent` exist, created via `claude-create-skill`
- [x] AC-01: naming collision check, `allowed_tools` intent-class heuristic, when-to-create gate, and agent-vs-session check are enforced by the pair
- [x] AC-02: the pair guarantees ≤50-token role identity + the five required sections
- [x] AC-03: the Domain-Vocabulary aid produces 10–25 expert-tier terms passing the practitioner test, rejecting shallow vocabulary; optional delegated web/research lookup
- [x] AC-04: the pair emits/maintains `contract.yaml` and references (not re-derives) the REQ-PROC-044 AC-03 split rubric
- [x] AC-05: `.claude/skills/INDEX.md` lists the six meta-skills as the governed set with cross-links to their governing ACs
- [x] INDEX.md + factory_flows.md updated for the two new skills

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Root task; no blocking dependencies (`after: []`) |

## Notes

This skill pair is a prerequisite for the recovered REQ-PROC-032 scribble strand
(032-11/-12/-13/-14/-19 reference `claude-modify-agent` / `claude-create-agent`)
and for TASK-PROC-044-01-02. Per the remediation plan §C3 it is a priority-override
candidate (the orchestrator owns that file).
