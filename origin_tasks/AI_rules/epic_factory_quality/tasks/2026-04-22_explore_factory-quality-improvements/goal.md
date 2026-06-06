---
task_id: TASK-PROC-044-01
type: explore
parent_requirement: REQ-PROC-044
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: L
created: 2026-04-22
after: []
awaiting: []
awaiting_note: "Unblocked 2026-05-30 by developer. Option B complete via downstream chain (044-02 through 044-10). Remaining open: Option E (skill categorization), Option D completion (skill-invocation tracking in claude-log), Option A (artifact state machine)."
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06]
  sections: []
scope_description: "Implement Software Factory quality improvements layer by layer, starting with low-risk additive changes (skill categorization, observability) and progressing to structural improvements (artifact state machine, skill contracts)"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore spanning ≥2 architectural layers (skills, scripts, artifact states, routing)
writes_requirements: false
requirements_version:
  commit: "pending-first-commit"
  file: ../requirements.md
---

# Goal: Implement Software Factory Quality Improvements

## Objective

Advance the Software Factory toward the quality properties defined in REQ-PROC-044 — functional reliability, transparency, maintainability, robustness, and determinism — by working through the improvement options identified in the Opus strategic analysis.

The strategic analysis is already complete (see References). This task implements the recommendations in the order prescribed by the analysis: lowest risk first, with each layer building on the previous one.

## Context Update (2026-05-30)

**Significant downstream work has been completed since this task was blocked.** Option B (skill contracts) was executed bottom-up through a chain of tasks spun from TASK-PROC-032-10, without waiting for this task to unblock. The current state:

| Task | Scope | Status |
|---|---|---|
| TASK-PROC-044-02 | Design + prototype the contract mechanism (sidecar contract.yaml, schemas, lint, feedback channel, split rubric) | completed |
| TASK-PROC-044-03 | Wave 1: contract.yaml for 4 producer skills + 5 schemas + lint productionized | completed |
| TASK-PROC-044-04 | Wave 2: contract.yaml for 9 consumer skill families + schema validator | completed |
| TASK-PROC-044-05 | Wave 3: contract.yaml for remaining skills (claude-*, doc-*, release-*, misc) + sunset | completed |
| TASK-PROC-044-06 | Revision-target channel (revision_target.yaml schema, task-create sub-procedure, cleanup convention) | completed |
| TASK-PROC-044-08 | Sub-skill-vs-agent rubric codified in claude-create-skill + claude-modify-skill | completed |
| TASK-PROC-044-09 | Factory-map render script + file-read telemetry hooks + read-frequency aggregator | completed |
| TASK-PROC-044-10 | External interface contracts explored (E1–E9 factory-boundary channels inventoried) | completed |
| TASK-PROC-044-07 | Scribble split into sub-skills + agents | **pending** |
| TASK-PROC-044-11 | Amend REQ-PROC-044 to add boundary AC-07 | **pending** |
| TASK-PROC-044-12 | External boundary contracts rollout | **pending** |
| TASK-PROC-044-13 | Verify all REQ-PROC-044 ACs implemented across task set 03–12 | **pending** |

**What this means for this task's original scope** — see the Scope section below.

## Scope

### In Scope

**Layer 1 — Sofortige Wins (implement first)**

- **Option E: Skill Categorization** — Reorganize `.claude/skills/INDEX.md` with a 4-layer taxonomy:
  - Layer 0 (Primitives): claude-log, claude-commit, claude-ask — basic operations
  - Layer 1 (Artifact Workers): ux-write-persona, requ-explore, code-simple — transform one artifact
  - Layer 2 (Orchestrators): product-intake, code-complex, claude-autorun — call Layer-1 skills
  - Layer 3 (Meta): claude-optimize, claude-modify-skill, claude-create-skill — change the system itself
  - *XS effort. No functional change. No regression risk.*
  - **Status: NOT done.** None of the 044-02 through 044-10 tasks touched INDEX.md taxonomy.

- **Option D: Observability** — Extend `claude-log` to capture skill name and outcome (success/failure) per invocation; add a Python aggregator script for `claude-optimize` to read:
  - *S effort. Additive. Enables metrics-based optimization over intuition.*
  - **Status: Partially addressed.** TASK-PROC-044-09 built file-read telemetry (PreToolUse/PostToolUse hooks, read-frequency aggregator, factory-map heat overlay). The specific ask here — skill-invocation outcome tracking in `claude-log` — was not built. The contract.yaml files now provide structural observability (what each skill claims to produce/consume), which partially substitutes.

**Layer 2 — Structural Improvements (after Layer 1 is stable)**

- **Option A: Artifact State Machine** — Declare valid artifact states and transitions in `.claude/artifact_states.yaml`; extend relevant scripts to warn on invalid transitions (observe-only mode initially):
  - *S effort. Script-side validation only; LLMs don't need to change.*
  - **Status: NOT done.** No task in the 044 chain addressed this.

- **Option B (Light): Skill Contracts** — Add explicit input/output schema to skills; productionize lint:
  - **Status: COMPLETE.** Executed far beyond the original "top-10" scope — all skill families have contract.yaml (Waves 1–3), schemas live in `.claude/schemas/`, lint is wired into verify-quality (TASK-PROC-044-03 through -05). External-boundary contracts explored (TASK-PROC-044-10) with rollout pending (TASK-PROC-044-12).

**Layer 3 — Strategic Investment (only if a core skill refactor is planned)**

- **Option G (Minimal): Snapshot Tests** — 3–5 golden examples for the top-5 most-refactored skills; LLM-evaluated probabilistic regression test:
  - *L effort. Only implement if a specific refactor that needs test coverage is planned.*
  - **Status: NOT done.** No task addressed this. The sub-skill-vs-agent rubric (TASK-PROC-044-08) is a lighter substitute that prevents structural regressions at creation/modification time.

### Out of Scope

- Option F (Skill Consolidation) — regression risk too high
- Option H (Declarative/Imperative Architecture) — too many skills fall on the boundary
- Option I (Skill-Dependency-Graph) — theoretically optimal but practically too fragile
- Changes to `factory_flows.md` beyond what Option B skill contracts naturally generate

### Potential Future Work (not yet tasked)

- **Option E standalone task** — INDEX.md 4-layer taxonomy is XS effort; can be done independently without unblocking this task.
- **Option D completion** — skill-invocation outcome tracking in `claude-log`; S effort; useful for `claude-optimize` to reason from data rather than intuition.
- **Option A standalone task** — artifact state machine; S effort; no dependency on contracts work being complete.

## Acceptance Criteria

- [ ] Layer 1 complete: INDEX.md has 4-layer taxonomy; claude-log captures skill name + outcome
- [ ] Layer 2 complete: artifact_states.yaml exists; top-10 skills have input/output contracts
- [ ] Layer 3 (conditional): snapshot tests exist for top-5 skills IF a core refactor is planned
- [ ] All changes are additive — no existing skills or scripts are deleted or broken
- [ ] Each improvement is validated against the quality properties in REQ-PROC-044 before marking the layer done

## Dependencies

None. All prerequisite analysis is complete.

## References

- **Strategic analysis (Opus, 2026-04-22)**: `plans_and_protocols/2026-04-22_01_opus_strategic_analysis.md`
- **Parent requirement**: `../requirements.md` (REQ-PROC-044)
- **Skill index**: `.claude/skills/INDEX.md`
- **Information flow overview**: `.claude/factory_flows.md`

### Downstream tasks (created without unblocking this task)

- **TASK-PROC-044-02** (completed): `../2026-05-29_explore_skill-interface-contracts-mechanism (completed)/goal.md`
- **TASK-PROC-044-03** (completed): `../2026-05-29_impl_skill-contracts-wave-1-producers (completed)/goal.md`
- **TASK-PROC-044-04** (completed): `../2026-05-29_impl_skill-contracts-wave-2-consumers (completed)/goal.md`
- **TASK-PROC-044-05** (completed): `../2026-05-29_impl_skill-contracts-wave-3-rest-and-sunset (completed)/goal.md`
- **TASK-PROC-044-06** (completed): `../2026-05-29_impl_revision-target-channel-and-cleanup (completed)/goal.md`
- **TASK-PROC-044-07** (pending): `../2026-05-29_impl_scribble-split-into-sub-skills-and-agents/goal.md`
- **TASK-PROC-044-08** (completed): `../2026-05-29_impl_rubric-codification-in-claude-create-modify-skill (completed)/goal.md`
- **TASK-PROC-044-09** (completed): `../2026-05-29_impl_factory-map-and-token-cost-measurement (completed)/goal.md`
- **TASK-PROC-044-10** (completed): `../2026-05-29_explore_external-interface-contracts (completed)/goal.md`
- **TASK-PROC-044-11** (pending): `../2026-05-30_explore_amend-req-proc-044-boundary-ac/goal.md`
- **TASK-PROC-044-12** (pending): `../2026-05-30_impl_external-boundary-contracts-rollout/goal.md`
- **TASK-PROC-044-13** (pending): `../2026-05-30_verify_req-proc-044-implementation-quality/goal.md`
