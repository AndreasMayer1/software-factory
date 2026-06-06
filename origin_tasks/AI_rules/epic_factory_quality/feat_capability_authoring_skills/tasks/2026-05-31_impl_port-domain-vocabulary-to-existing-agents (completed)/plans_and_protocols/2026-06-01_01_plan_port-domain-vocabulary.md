# Plan: Port Domain Vocabulary + Anti-Patterns to the six existing agents

Task: TASK-PROC-044-01-02 · Session: 6409479f-48d4-4c57-8ad5-68025aa4f9e1 · 2026-06-01

## Objective (from goal.md)

Through the `claude-modify-agent` skill, add a `## Domain Vocabulary` (10–25
expert-tier, domain-distinct terms passing the 15-year-practitioner test) and a
`## Anti-Patterns` section to the six general agents, and bring each agent's
`contract.yaml` into sync. Exercises REQ-PROC-044-01 AC-03's Domain-Vocabulary aid.

## Current state (inspected)

| Agent | Has `## Domain Vocabulary`? | Has `## Anti-Patterns`? | contract.yaml? |
|---|---|---|---|
| architecture-advisor | no | no | missing |
| implementation-engineer | no | no | missing |
| opus-advisor | no | no | missing |
| quality-checker | no | no | missing |
| setup-optimizer | no | no | missing |
| test-engineer | no | no | missing |

None of the six carry a sidecar contract. The governed end-state (claude-create-agent
§4) requires the full section set; this task supplies the two missing knowledge
sections + the contract sidecar. The other required sections (`## Protocols`,
`## Output`, `## Rules`) are out of scope unless the structural check forces them —
the existing bodies already encode protocol/output/rules content under their own
headings, so per the goal's Out-of-Scope clause we do NOT restructure them.

## Format convention (matched from ui-scribble-persona-walker.md)

- `## Domain Vocabulary` = bulleted list of `- **term**: one-line expert definition`.
- `## Anti-Patterns` = bulleted list of the agent's own characteristic failure modes.
- contract sidecar = `{name}.contract.yaml` with `contract_version: 1`, `purpose`,
  `derived_from`, `consumes`, `produces`.

## Domain-distinctness map (no cross-agent padding)

- **architecture-advisor** → boundary/coupling/DDD vocabulary (seams, ports, blast radius).
- **implementation-engineer** → Dart/Flutter/BLoC mechanics (element reuse, async gaps, DI scopes).
- **opus-advisor** → investigation/epistemics (triangulation, falsifiability, provenance).
- **quality-checker** → static-analysis/gate vocabulary (baseline ratchet, mutation score, suppression hygiene).
- **setup-optimizer** → process/flow-optimization (theory of constraints, toil, Goodhart, Conway).
- **test-engineer** → testing craft (Meszaros doubles, pyramid, goldens, hermeticity).

Each set is 15–18 terms — comfortably inside the 10–25 band, each chosen to fail
a novice and pass a long-time practitioner; no generic "code review"/"unit test"
filler.

## Execution

For each agent, run the `claude-modify-agent` governed process:
1. Read the agent file.
2. Insert `## Domain Vocabulary` + `## Anti-Patterns` (after the role/intro,
   before the existing procedural body so the knowledge frames the procedure).
3. Re-assert §4 structure (role identity ≤50 tokens already holds).
4. Write the `{name}.contract.yaml` sidecar (AC-04).
5. Record file changes in the protocol.

## Acceptance check

- [ ] 6 × `## Domain Vocabulary` (10–25 expert terms, domain-distinct)
- [ ] 6 × `## Anti-Patterns`
- [ ] 6 × `contract.yaml` in sync
- [ ] all done through claude-modify-agent governed steps (not hand-edited)
