---
task_id: TASK-PROC-044-17
type: explore
parent_requirement: REQ-PROC-044
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-05-31
effort: M
created: 2026-05-31
after: []
awaiting: []
awaiting_note: ""
writes_requirements: true
opus_recommended: true   # reason: cross-cutting factory-quality design (artifact model + naming governance)
covers:
  acceptance_criteria: []
  sections: []
requirements_version:
  commit: b4332140
  file: ../../requirements.md
---

# Goal: Artifact Model + Agent Naming Scheme

## Objective
Author two coordinated requirement changes under epic REQ-PROC-044 (Software Factory
Quality): a new feature defining a factory-wide artifact model with enforcement, and a
sharpening of the agent-naming AC to a closed `{expertise}-{role}` scheme.

## Context
Design dialogue (2026-05-31) refined how `.claude/agents/*.md` should be named, by analogy
to `claude-create-skill`'s naming convention. Two structural conclusions emerged:

1. **Agent names** are `{expertise}-{role}`. The **role** is the agent's *output type*, drawn
   from a closed 2x2 partition over two axes — persist-vs-return and synthesized-vs-mechanical
   — giving exactly `{writer, transformer, reviewer, classifier}`. Activities, lifecycles, and
   tool capabilities are NOT roles (this is why `-engineer`/`-advisor`/`-checker`/`-walker`
   collapse into the four). The **expertise** names the artifact (or review lens) the agent
   works on, never an operation. The set is closed: a new role requires proving a new
   output-type axis. Ambiguity (zero or >=2 roles) triggers stop-and-ask.

2. **Artifacts** need a single source of truth. DRY analysis (node/edge split): producer/
   consumer *relationships* stay distributed in each `contract.yaml` `produces:`/`derived_from:`
   (each edge owned once); artifact *definitions* (canonical token + path + meaning) must
   centralize — no single contract can own a shared definition, so leaving them implicit across
   N contracts is a DRY violation. The registry is the node table; a lint binds edges to nodes.

The registry lives under the new `.factory/` meta-folder, which holds all files that
describe/run the factory (exception: tech-dictated meta like `.claude/` and root `CLAUDE.md`).
`.factory/` already holds GENERATED runtime data (`optimize/`, `session_logs/`); the registry
is AUTHORED canon, so it must be separated by lifecycle (`.factory/registry/`) and never pruned.

Current state (REQ-PROC-044-01 AC-01) only collision-checks agent names; no expertise/role
scheme and no artifact vocabulary exist. `produces:`/`derived_from:` are free-text today.

## Acceptance Criteria
- [x] `feat_artifact_model/requirements.md` created (new feature under the epic) with ACs for:
      the canonical registry at `.factory/registry/artifacts.yaml` (unique token + path + defn);
      a per-change lint resolving every `produces:`/`derived_from:` value and every governed
      agent-name artifact-slot token to a registry token (graceful stop on unresolved);
      open-extension via must-ask + append with no-overlap rejection; authored-canon lifecycle +
      `.factory/README.md` (authored-vs-generated split, inventory, `.claude/`/`CLAUDE.md` out of
      scope); registry seeded from existing contracts + factory map + Information Map and part of
      the AC-06 authoritative-location set.
- [x] REQ-PROC-044-01 AC-01 extended with the `{expertise}-{role}` naming scheme and the closed
      `{writer, transformer, reviewer, classifier}` role set, stop-and-ask on ambiguity, and the
      existing collision check retained as a sub-rule; cross-links REQ-PROC-044-02 for the
      artifact vocabulary (does not restate it).
- [x] The two requirements cross-link each other and reference — not duplicate — the epic's
      AC-06 (single authoritative location) and AC-08 (boundary-contract lint pattern).

## Notes
- Contracts stay colocated beside their skills/agents (tech-adjacent exception); only artifact
  DEFINITIONS centralize into `.factory/registry/`.
- Implied follow-up (out of scope here, separate impl tasks): build `artifacts.yaml` + lint,
  write `.factory/README.md`, and rename existing agents to the new scheme
  (e.g. `opus-advisor`→`investigation-writer`, `architecture-advisor`→`architecture-writer`,
  `implementation-engineer`→`implementation-writer`, `quality-checker`→`quality-reviewer`,
  `ui-scribble-generator`→`ui-scribble-writer`, `ui-scribble-handoff-emitter`→`-transformer`,
  `ui-scribble-persona-walker`→`-reviewer`, `ui-scribble-cross-feature-checker`→`-reviewer`).
