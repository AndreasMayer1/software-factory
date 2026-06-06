---
id: REQ-PROC-044-02
status: active
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
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
      text: "A canonical artifact registry exists at `.factory/registry/artifacts.yaml`. Each entry declares a unique `token`, a filesystem `path` (or glob) at which that artifact lives, and a one-line `definition`. No two entries share a token or describe the same artifact (no-overlap)."
      target_package: unassigned
    - id: AC-02
      text: "Every `produces:` and `derived_from:` value in any `.claude/skills/*/contract.yaml` or `.claude/agents/*.contract.yaml` is a token defined in the registry. A value that resolves to no registry token — or a registry containing a duplicate token — causes the per-change quality gates to emit a visible warning and stop, never a silent pass. The resolving check is a lint in the same family as the boundary-contract lint (REQ-PROC-044 AC-08)."
      target_package: unassigned
    - id: AC-03
      text: "The artifact-or-lens segment of every agent name governed by REQ-PROC-044-01 AC-01 is a token defined in the registry."
      target_package: unassigned
    - id: AC-04
      text: "The registry is open and append-structured: it gains entries over the factory's life without altering existing ones, and it never holds two tokens for the same artifact (a duplicate or alias is absent). The establishment gate that decides when, how, and by whom an entry is added is owned by REQ-PROC-044-01 (eager human ratification at authoring time), with this feature's resolve lint (AC-02) as the backstop."
      target_package: unassigned
    - id: AC-05
      text: "`.factory/registry/artifacts.yaml` is committed and is not subject to the runtime pruning that governs `.factory/session_logs/` and `.factory/optimize/`. `.factory/README.md` exists and states the authored-vs-generated lifecycle split, inventories the `.factory/` subfolders with their owners, and records that tech-dictated meta (`.claude/`, root `CLAUDE.md`) is out of `.factory/`'s scope."
      target_package: unassigned
    - id: AC-06
      text: "The registry is reachable from the factory's single authoritative location set (REQ-PROC-044 AC-06), and its entries are consistent with the artifact names already declared across existing `contract.yaml` files, the factory map, and the CLAUDE.md Information Map."
      target_package: unassigned
    - id: AC-07
      text: "A `.claude/schemas/user_input_gate.yaml` schema defines the structure of a `user_input_gates` entry in a skill or agent contract. The required fields are `phase` (a string unique within a single contract's `user_input_gates` list), `description`, `decision_kind` (vocabulary: `approval`, `revision`, `selection`, `path-selection`, `free-text`), and `required` (vocabulary: `always`, `conditional`). The contract lint treats any `user_input_gates` entry that violates this schema as a gate failure — a visible stop, consistent with the treatment of an unresolved `produces:` token (AC-02)."
      target_package: unassigned
    - id: AC-08
      text: "A script `scripts/factory/render_user_input_gates.py` is the canonical source for a flat, operator-readable index of all developer-decision checkpoints declared across skill and agent contracts. The index lists each gate's skill name, phase, description, decision_kind, and required."
      target_package: unassigned
    - id: AC-09
      text: "The artifact registry contains a `user-input-gate` token (category: `factory-skills`, path: `.claude/schemas/user_input_gate.yaml`) with a definition identifying it as the schema-typed checkpoint entry in skill and agent contracts."
      target_package: unassigned
personas_served: [PERSONA-004]
---

# Artifact Model

## Overview

The factory's artifacts (scribbles, handoffs, plans, requirements, code, tests, …) have a
single source of truth for their **definitions**: a canonical registry naming each artifact
type, where it lives, and what it is. Producer/consumer **relationships** stay where they
already are — distributed across each capability's `contract.yaml`. A lint binds the two so
every declared relationship and every governed agent name refers to a defined artifact.

## Purpose

The skill-interface-contract mechanism (REQ-PROC-044 AC-08) gave every skill and agent a
`contract.yaml` whose `produces:` / `derived_from:` fields name the artifacts it makes and
consumes. Those names are free text today: the same artifact can be spelled differently in two
contracts, a typo silently mints a phantom artifact, and there is no place that authoritatively
says what `scribble` *is* or where it lives. The agent-naming work (REQ-PROC-044-01) compounds
this — it wants the artifact a reviewer/writer operates on to appear *in the agent's name*,
which is only safe if "the set of artifacts" is a controlled, defined vocabulary.

This matters now because both consumers are active: contracts already carry free-text artifact
names, and the agent-naming scheme is being sharpened in the sibling feature. A controlled
artifact vocabulary is the shared dependency of both.

## Behavior

**Definitions centralize; relationships stay distributed (node/edge split).** An artifact's
*definition* — its canonical token, filesystem location, and meaning — belongs to no single
producer, so it lives once in the registry (the node table). Who *produces* or *derives* each
artifact remains declared by each capability in its own `contract.yaml` (the edges), so each
relationship is still owned once by its owner. This is the DRY-correct split: leaving
definitions implicit across N contracts would duplicate the artifact name with no authority.

**The registry is the controlled vocabulary.** `produces:` / `derived_from:` values and the
artifact-or-lens segment of governed agent names are valid only when they resolve to a registry
token. An unresolved token or a duplicate registry entry is a gate failure with a visible
warning and graceful stop — consistent with the factory's robustness invariant
(REQ-PROC-044 AC-04) and enforced by a lint in the boundary-contract-lint family
(REQ-PROC-044 AC-08).

**The registry is open but guarded.** New artifacts are expected over the factory's life, so the
registry is append-structured and the no-overlap property is preserved as it grows — a token that
duplicates or aliases an existing one never enters it. *When*, *how*, and *by whom* an artifact is
established is the establishment gate owned by REQ-PROC-044-01: an authoring skill eagerly proposes
a registry entry the developer ratifies (renames to an existing token, or rejects) before authoring
proceeds; this feature's resolve lint (AC-02) is the backstop for anything authored outside those
skills.

**`.factory/` separates authored canon from generated runtime.** The registry is authored
canon: committed, curated, never pruned. It sits under `.factory/registry/`, apart from the
generated runtime subtrees (`.factory/optimize/`, `.factory/session_logs/`) that are
regenerable and age-pruned (REQ-PROC-044 AC-07). `.factory/README.md` documents this lifecycle
split, inventories the subfolders, and fixes the boundary that tech-dictated meta (`.claude/`,
root `CLAUDE.md`) stays where its tooling requires it.

**User input gates are a governed contract field (AC-07 – AC-09).** Every developer-decision checkpoint a skill reaches — an approval gate, a revision loop, a selection prompt — is a point where the factory's human-autonomy boundary is crossed. Declaring these checkpoints in `contract.yaml` under a `user_input_gates:` section, validated by the schema at `.claude/schemas/user_input_gate.yaml` and rendered into a flat index by `scripts/factory/render_user_input_gates.py`, makes the complete human-in-the-loop surface of the factory visible in one place. An operator can see at a glance which checkpoints exist across all skills, which always fire, and which are conditional. The declared gates do not constrain *how* a skill implements the interaction — they record *that* the interaction exists and *what kind of decision* it is.

## Examples

- **Registry node**: `scribble: { path: "**/scribbles/v*/", definition: "versioned HTML wireframe" }`.
- **Edge that must resolve**: `ui-scribble-handoff-emitter`'s contract declares
  `derived_from: [scribble]` and `produces: [handoff]` — both must be registry tokens.
- **Agent name that must resolve**: under REQ-PROC-044-01 AC-01, `ui-scribble-handoff-transformer`
  carries the artifact token `handoff` in its expertise slot — `handoff` must be a registry token.
- **User input gate declaration** (in a skill's `contract.yaml`):
  ```yaml
  user_input_gates:
    - phase: location-approval
      description: "Developer confirms target folder for new requirement"
      decision_kind: path-selection
      required: always
    - phase: package-assignment
      description: "Developer assigns release package to UI-touching ACs"
      decision_kind: selection
      required: conditional
  ```

## Developer Guidelines

### Key Decisions

- **Definitions in the registry, relationships in contracts.** Do not move `produces:` /
  `derived_from:` into the registry, and do not duplicate artifact definitions into contracts.
- **The registry is the only artifact vocabulary.** Agent names (REQ-PROC-044-01) and contract
  fields both draw from it; neither defines its own parallel list.
- **Authored vs generated is load-bearing.** Anything under `.factory/registry/` is canon and
  is never bulk-pruned or gitignored; only the generated subtrees are disposable.
- **Contracts remain colocated.** `contract.yaml` files stay beside the skill/agent they
  describe (tech-adjacent); only the definitions centralize.
- **User input gates are contract instances, not registry tokens.** The registry is a vocabulary of artifact *types* — each token names a kind of thing and where instances of that kind live. A `user-input-gate` is a repeating structural element inside a contract file, not a distinct file type of its own. Minting one registry token per gate (e.g. `requ-explore-location-approval`) would inflate the registry with implementation details that belong in the contract. One token (`user-input-gate`) covers the entire class; the schema defines what every instance must look like; the index script renders all instances. This mirrors how `skill-contract` is one token even though there are many contract files.

### Common Pitfalls

- A free-text `produces:` value that never resolves to a token passes a naive read but is a phantom
  artifact — the resolve lint exists to make it a visible failure.
- Two tokens for one artifact (e.g. `scribble` and `wireframe`) silently fork the vocabulary —
  the no-overlap rule rejects the alias.
- Treating the registry as regenerable runtime data and pruning/ignoring it destroys canon.

## Related Requirements

- [REQ-PROC-044](../requirements.md) — parent epic; AC-04 (robustness / graceful stop), AC-06
  (single authoritative location), AC-08 (boundary-contract lint) are the invariants this feature
  realizes for the artifact dimension, referenced not duplicated.
- [REQ-PROC-044-01](../feat_capability_authoring_skills/requirements.md) — consumes this
  registry: the agent-naming scheme draws each name's artifact-or-lens token from it (AC-03 here
  is the enforcement of that link). The authoring skills (`claude-modify-skill`, `claude-create-skill`) are also the natural point where `user_input_gates` entries are added to a skill's contract when a new gate is introduced.
- [REQ-PROC-043](../../../tooling_rules/scripts_organization/requirements.md) — the resolve lint
  is a script and is governed by the scripts-organization rules; referenced, not duplicated.
- REQ-PROC-046 — the resolve lint runs as a per-change quality gate; this feature adds a check
  to that gate set rather than defining a parallel enforcement mechanism.

## References

- `.claude/agents/*.contract.yaml`, `.claude/skills/*/contract.yaml` — current free-text producers/consumers
- `scripts/factory/render_factory_map.py` — the factory map (artifact-dependency view)
- `.factory/` — `optimize/` and `session_logs/` (generated runtime); `registry/` (authored canon)
