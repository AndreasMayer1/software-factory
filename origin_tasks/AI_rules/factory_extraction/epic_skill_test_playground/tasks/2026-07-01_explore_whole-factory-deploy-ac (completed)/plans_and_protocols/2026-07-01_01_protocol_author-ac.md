---
skills_used:
  - claude-automated-mode
  - task-start
  - claude-route
  - requ-explore
  - task-complete
  - claude-commit
---

# Protocol — author whole-factory-deploy AC (TASK-PROC-068-14)

Agent: main session (orchestrator). Date: 2026-07-01.

## Phase 1 — investigation (read-only)
Read (context, no files written):
- `goal.md` — objective: add ONE intent-level AC to REQ-PROC-068; no file/artifact enumeration.
- `../../requirements.md` (REQ-PROC-068 epic, instrument spec) — carries AC-01..AC-09 directly (special
  "instrument spec" epic; ACs are cross-cutting, not one-per-feature). AC-09 is the S/HIGH containment
  (child cannot reach OUT). AC-07 is F/MEDIUM deploy→run→reset cycle. AC-04 is F/MEDIUM probe emission.
- Seed/spec: `…/2026-06-26_11_plan_orchestration-chain-buildout.md` §"Revision (2026-07-01, developer)" —
  D1 resolved: home = REQ-PROC-068, decoupled from REQ-PROC-066; T-A (external manifest) DROPPED;
  requirement = one intent-level AC; developer's candidate wording captured verbatim.
- `plans_and_protocols/2026-07-01_00_user_initial_input.md` — verbatim developer thinking: "what the
  factory is will be defined once the factory exists as an independent project: everything it provides";
  no enumeration in a requirement outside the factory. Exclude-list = T-B (impl) guidance, NOT this AC.

## Gap being closed
Existing deploy copies only `.claude/skills/`. A *contained* child (AC-09) cannot reach host `scripts/`
and does not have them locally → any script-calling skill breaks. AC-07/AC-09 are legitimately met for
what they assert; neither mandates copying the whole factory. New AC expresses "whole factory present so a
contained child can run any skill end-to-end" as intent — no file list.

## Decisions
- Phases 1.5 (ideation) / 1.6 (concept completion): SKIP — requirement shape is fully decided by the
  developer (candidate wording given verbatim); no open shaping question remains.
- Facet tagging (§2.2a): SKIP — process epic, not presentation-touching.
- EGP (§2.2b): archetype **F** (empirical fidelity), referent = a real workflow run of a script-calling
  skill inside the harness jail completing without host reach-back; consequence **MEDIUM** (matches sibling
  F ACs AC-04/AC-07; the S/HIGH containment concern is already owned by AC-09). auto==confirmed → no
  egp_auto. Judgment-Relocation sub-trigger: no K-kind match (a deploy mechanism, not an autonomous
  human-judgment decision).
- `source:` (§2.2c): ABSENT — valid. The AC is pure developer-decided intent; its implementation (T-B) is
  a separate downstream task. The grounding plan is cited at epic `## References` (input-coverage
  disposition), not as a per-AC design-concept source.
- Package assignment (§2.4): SKIP — internal process tooling (unassigned).

## Input-coverage (§2.6)
- goal.md objective + developer principle (no enumeration) → expressed in AC-10 + its parenthetical.
- Plan §Revision candidate wording → expressed (AC-10 text) + referenced (## References).
- user_initial_input (defer "what is factory" to the factory) → expressed in AC-10 parenthetical.
- Exclude-list → deliberately omitted (belongs to T-B impl, per developer).
