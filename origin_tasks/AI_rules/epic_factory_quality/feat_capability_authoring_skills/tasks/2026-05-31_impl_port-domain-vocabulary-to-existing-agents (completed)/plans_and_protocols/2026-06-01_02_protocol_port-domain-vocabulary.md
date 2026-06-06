---
skills_used:
  - claude-automated-mode
  - claude-route
  - claude-modify-agent
  - task-complete
  - claude-commit
---

# Protocol: Port Domain Vocabulary + Anti-Patterns to the six existing agents

Task: TASK-PROC-044-01-02 · Session: 6409479f-48d4-4c57-8ad5-68025aa4f9e1 · 2026-06-01
Mode: automated · model: opus (opus_recommended honored by orchestrator launch)

## What was done

Entered the `claude-modify-agent` governed process and applied it to each of the
six general agents (AC-05 — through the skill, not hand-edited). For every agent:
added `## Domain Vocabulary` + `## Anti-Patterns` immediately after the role line
(so the knowledge frames the existing procedural body), and authored a
`{name}.contract.yaml` sidecar (AC-04).

The Domain-Vocabulary aid bar (claude-create-agent §5, REQ-PROC-044-01 AC-03) was
applied directly by the Opus session — each term was chosen to fail a novice and
pass a long-time practitioner; no shallow/common-web padding to hit the count. No
lookup delegation was needed: each domain yielded ≥15 strong terms from knowledge.

## Files changed

| Agent | `.md` change | new contract |
|---|---|---|
| architecture-advisor | +Domain Vocabulary (16), +Anti-Patterns (6) | architecture-advisor.contract.yaml |
| implementation-engineer | +Domain Vocabulary (15), +Anti-Patterns (7) | implementation-engineer.contract.yaml |
| opus-advisor | +Domain Vocabulary (17), +Anti-Patterns (7) | opus-advisor.contract.yaml |
| quality-checker | +Domain Vocabulary (17), +Anti-Patterns (7) | quality-checker.contract.yaml |
| setup-optimizer | +Domain Vocabulary (16), +Anti-Patterns (7) | setup-optimizer.contract.yaml |
| test-engineer | +Domain Vocabulary (16), +Anti-Patterns (7) | test-engineer.contract.yaml |

Plus this task's plan + protocol under `plans_and_protocols/`, and goal.md →
`status: in_progress` / `started: 2026-06-01`.

## Domain-distinctness (no cross-agent overlap of focus)

- architecture-advisor → boundaries/coupling/DDD (seam, port/adapter, blast radius, Ca/Ce, aggregate root)
- implementation-engineer → Dart/Flutter/BLoC mechanics (element reuse, async gap, DI scope, copyWith, buildWhen)
- opus-advisor → investigation epistemics (triangulation, falsifiability, provenance, MECE, abductive inference)
- quality-checker → static-analysis/gates (baseline ratchet, mutation score, suppression hygiene, blocking contract)
- setup-optimizer → process/flow optimization (theory of constraints, toil, Goodhart, Conway, WIP limit)
- test-engineer → testing craft (Meszaros doubles, pyramid, goldens, hermeticity, mutation testing)

## Scope decision (recorded)

Goal Out-of-Scope says only add `## Protocols`/`## Output`/`## Rules` if the
structural check finds them missing AND not to restructure existing bodies. The
six bodies already encode protocol/output/rules content under their own headings;
restructuring them is explicitly out of scope. Therefore only the two knowledge
sections + the contract sidecar were added. The goal (immutable objective) governs
over the skill's generic "add any missing required section" step here.

## Verification

- Section presence: each agent has exactly one `## Domain Vocabulary` and one
  `## Anti-Patterns`; term counts 15–17, inside the 10–25 band.
- All six `contract.yaml` parse as valid YAML with `contract_version: 1`,
  `purpose`, `derived_from`, `produces` present (two initial multi-line list-item
  YAML errors found and fixed by moving the wrapped descriptions into comments).
- No Dart/`lib/`/`test/` files touched → verify-quality Dart gates N/A. The
  skill-contract and boundary-contract validators target `.claude/skills/` and
  `.claude/contracts/external/` respectively, not agent sidecars, so no scripted
  gate governs these files.

## Acceptance criteria

- [x] All six agents have `## Domain Vocabulary` authored via claude-modify-agent
- [x] Each set is 10–25 expert-tier, domain-distinct terms (no shallow padding)
- [x] All six agents have `## Anti-Patterns`
- [x] Each agent's contract.yaml in sync (created — none existed before)
- [x] Modifications made THROUGH claude-modify-agent (governed process), not hand-edited
