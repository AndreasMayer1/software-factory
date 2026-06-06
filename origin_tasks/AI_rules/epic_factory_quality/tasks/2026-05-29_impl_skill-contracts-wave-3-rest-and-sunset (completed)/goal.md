---
task_id: TASK-PROC-044-05
type: impl
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-30T04:35:30Z
effort: M
created: 2026-05-29
after: [TASK-PROC-044-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-03, AC-06]
  sections: []
scope_description: "Wave 3 of the skill-interface-contracts rollout. Author contract.yaml for all remaining skills (claude-*, doc-*, release-*, misc: brb, codegraph, product-intake, verify-quality). 60 days after Wave 3 starts, remove contract_version: 0 from the lint's allowlist (the sunset commit). Re-run sub-skill-vs-agent rubric per family; document refinements. Final cleanup: delete any prose duplicates remaining in folder-root READMEs."
release_description: ""
opus_recommended: false   # reason: mostly mechanical migration following Wave 1+2 patterns; rubric re-run is documentation
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-3
session_id: 997adaa1-ee64-4c48-a1b5-39d624a95ecc
session_account: web
---
# Goal: Wave 3 — Remaining Skills + Sunset contract_version: 0

## Objective

Complete the contract-mechanism migration started in Waves 1-2. Land contract.yaml for every remaining skill, then enforce: no skill at `contract_version: 0` 60 days after Wave 3 starts.

## Background

After Waves 1-2:
- Producer + heavy consumer skills are contract-managed
- Lint + runtime pre-checks are productionized
- Schemas cover the major shared artifacts

Wave 3 covers the long tail: `claude-*` (15 skills), `doc-*` (4 skills), `release-*` (5 skills), and misc (brb, codegraph, product-intake, verify-quality). These are mostly lower-interface-dependency skills, but landing them removes the `contract_version: 0` opt-out class.

See `requirements_tasks/process/AI_rules/factory_quality/tasks/2026-05-29_explore_skill-interface-contracts-mechanism/plans_and_protocols/05_round_3_synthesis.md` §D-5 Wave 3.

## How to Approach This

1. Read Wave 1+2 deliverables and the exploration synthesis.
2. Inventory the remaining skills (cross-reference against `.claude/skills/INDEX.md`).
3. Author contract.yaml for each. Where multiple skills in a family share patterns (e.g. all `release-*` skills consume `releases/<v>/`), factor those into shared schemas first.
4. Apply the rubric to each migrated skill; document scores; propose refinements to FU-6 via revision_target.yaml if any signal weight needs adjustment.
5. Final prose cleanup: walk every folder-root README in the project tree; delete any sections now duplicated by a schema.
6. **Sunset commit**: at 60 days from this task's start, modify `scripts/quality/check_skill_contracts.py` to remove `contract_version: 0` from the lint allowlist. The lint will now ERROR (not warn) on any skill without a contract.yaml or with `contract_version: 0`.

## Acceptance Criteria

- [x] contract.yaml exists for every skill in `.claude/skills/` (no skill at `contract_version: 0` after sunset)
- [x] Lint passes on the full skill tree
- [x] Rubric re-run results documented in `plans_and_protocols/` per skill family
- [x] No prose duplicates of schema content remain in folder-root READMEs (verified by a final grep pass; results documented)
- [x] Sunset commit removes `contract_version: 0` allowlist entry; commit message references the 60-day sunset target
- [ ] Factory-map render (FU-7) shows the full graph with no unconnected nodes — deferred to TASK-PROC-044-08 (its own task)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-04 (Wave 2) | pending | Consumer contracts + runtime pre-checks must land first |

## Notes

The 60-day sunset is enforced by THIS task carrying the sunset commit at its scheduled date. SCRIBBLE-SPLIT (TASK-PROC-044-07) is blocked until this task completes. This task is in `flutter_app/.claude/task_ordering_priority_override.txt`.
