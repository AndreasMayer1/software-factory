---
task_id: TASK-PROC-044-03
type: impl
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-05-29
started: 2026-05-29
completed: 2026-05-29
session_completed_at: 2026-05-29T20:51:53Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04]
  sections: []
scope_description: "Wave 1 of the skill-interface-contracts rollout. Author contract.yaml for the 4 producer skills (task-create, requ-explore, ui-create-scribble, ux-write-canon-concept). Author 5 initial schemas (.claude/schemas/{scribble_metadata, goal_metadata, flutter_handoff, concept_canon_entry, requirements_frontmatter}.yaml). Productionize the prototype lint at scripts/quality/check_skill_contracts.py with full named-producer verification (not the PoC simplification). Atomically delete the prose specs the new schemas replace. Wire the lint into verify-quality per-change gates."
release_description: ""
opus_recommended: true   # reason: cross-cutting infrastructure spanning 4 producer skills + 5 schemas + lint productionization; precedent set in exploration parent
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-1
session_id: 86f3d13f-416d-46b9-ab86-c898e841a583
session_account: gmail
---
# Goal: Wave 1 — Skill Contracts for Producer Skills

## Objective

Land the first wave of the contract mechanism rolled out by REQ-PROC-044 (see exploration synthesis in `requirements_tasks/process/AI_rules/factory_quality/tasks/2026-05-29_explore_skill-interface-contracts-mechanism/plans_and_protocols/05_round_3_synthesis.md` and amendments in `09_amendments.md`).

This wave covers the **producer skills** — the 4 skills whose outputs are consumed by many other skills. Landing them first means the rest of the migration can reference real producer contracts, not stubs.

## Background

The exploration in TASK-PROC-044-02 settled on a three-component mechanism:
1. Sidecar `contract.yaml` per skill (PRINCE2-aligned 4-field minimum + `source:` annotation per Round 2 prototype findings)
2. `.claude/schemas/<artifact>.yaml` for shared shapes
3. 5-line bash pre-checks at each consumer's skill entry (this wave: producers don't need pre-checks themselves; Wave 2 adds them to consumers)

Prototype reference: `requirements_tasks/process/AI_rules/factory_quality/tasks/2026-05-29_explore_skill-interface-contracts-mechanism/prototypes/` contains 3 contract.yaml + 2 schemas + the 76-line lint + a demo of catching a violation.

## How to Approach This

1. Read the exploration synthesis files (`05_round_3_synthesis.md` + `09_amendments.md`) and the prototype README.
2. For each of the 4 producer skills, author `.claude/skills/<name>/contract.yaml` per the canonical field set:
   - `contract_version: 1`, `purpose:`, `derived_from: { required, optional }` (each item with `source: external | skill:<name>` MANDATORY), `produces: { required, conditional }`, `quality_criteria:`, `may_invoke:`, `side_effects: [{target, action, note}]`, `preconditions:`, `postconditions:`
3. Author 5 schemas under `.claude/schemas/`. Each schema's leading comment block declares which prose-spec sections it replaces.
4. For each schema, perform the **atomic cleanup**: in the same commit as the schema is introduced, delete the prose-spec sections it replaces, replacing them with `> See `.claude/schemas/<artifact>.yaml` for the canonical structure.`
5. Promote the prototype lint to `scripts/quality/check_skill_contracts.py` with full named-producer verification (Round 2 PoC skipped this; production must verify). Use `claude-write-script` skill per CLAUDE.md §"Python gates".
6. Wire the lint into `verify-quality` per-change gates (G-series).
7. Add a Wave-1 commit fixture: a tiny pre-check `[ -f X ]` style assertion at the top of one consumer skill (suggest `ui-verify-flutter`) as a smoke test demonstrating the runtime-check pattern that Wave 2 generalizes.

## Acceptance Criteria

- [x] `.claude/skills/task-create/contract.yaml` exists and the lint passes against it
- [x] `.claude/skills/requ-explore/contract.yaml` exists and the lint passes
- [x] `.claude/skills/ui-create-scribble/contract.yaml` exists and the lint passes
- [x] `.claude/skills/ux-write-canon-concept/contract.yaml` exists and the lint passes
- [x] `.claude/schemas/{scribble_metadata, goal_metadata, flutter_handoff, concept_canon_entry, requirements_frontmatter}.yaml` all exist
- [x] For each schema landed: the prose-spec sections it replaces are deleted IN THE SAME COMMIT (no dual maintenance phase)
- [x] `scripts/quality/check_skill_contracts.py` is the productionized version (named-producer verification ON, not skipped)
- [x] Lint is wired into `verify-quality` per-change gates and fires on `.claude/skills/*/contract.yaml` modifications
- [x] One Wave-1 fixture pre-check at the top of a consumer skill demonstrates the runtime-check pattern
- [x] Plans_and_protocols/ documents which prose specs were deleted (audit trail)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-02 | (will be `completed`) | Parent exploration that produced the mechanism design + prototype |

## Notes

This task is added to `flutter_app/.claude/task_ordering_priority_override.txt` to outrank the 0.0.1 release work. Wave 2 (TASK-PROC-044-04) and Wave 3 (TASK-PROC-044-05) follow this task; SCRIBBLE-SPLIT (TASK-PROC-044-07) is blocked until Wave 3 completes.

Per the exploration synthesis: full contract-mechanism rollout (Waves 1-3) completes before SCRIBBLE-SPLIT starts; SCRIBBLE-SPLIT completes before 0.0.1 release work resumes.
