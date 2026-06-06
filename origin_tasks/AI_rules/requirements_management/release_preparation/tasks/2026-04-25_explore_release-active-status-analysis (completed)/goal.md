---
task_id: TASK-PROC-035-07
type: explore
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-25
effort: L
created: 2026-04-25
after: []
awaiting: []
awaiting_note: ""
target_package: "Transfer Data Model"
covers:
  acceptance_criteria: []
  sections: [SEC-05, SEC-06, SEC-07]
scope_description: "Analyze and document the full redesign of the release implementation pipeline — distributed architecture, task creation plan, quality gates, Phase 6 sequence — and update affected requirements"
release_description: ""
opus_recommended: true   # reason: cross-cutting architectural analysis across ≥3 process requirements and ≥5 skills
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: d357041e
  file: ../requirements.md
---

# Goal: Redesign Release Implementation Pipeline

## Objective

The `/release-begin-impl` skill was run on 2026-04-24 and failed — revealing
structural gaps in the release active-status workflow. Three Opus analysis
rounds (2026-04-24/25) have produced a complete redesign. This task finalizes
that redesign and updates all affected requirements so implementation tasks
can be derived from a solid foundation.

**Analysis is complete** (5 plan documents in `plans_and_protocols/`). The
remaining work is requirements updates only.

## Requirements Summary

Primary: REQ-PROC-035 (Release Preparation) — SEC-05, SEC-06, SEC-07 are
directly affected by the redesign.

Also affected:
- **REQ-PROC-041-03** (Automated Mode) — `claude-automated-mode` bootstrap
  simplification (Cases A and B removed; chain self-perpetuates).
- **REQ-PROC-036** (Release Workflow) — new `release-begin-impl-finalize`
  skill must be documented.

For requirements at task creation time:
```
git show d357041e:requirements_tasks/process/AI_rules/requirements_management/release_preparation/requirements.md
```

Current requirements: ../requirements.md

## Plan Summary (from analysis rounds)

The full design is in `plans_and_protocols/`. Summary of key decisions:

### Architecture: Distributed Pipeline
- `release-begin-impl` reduced to scope-only (Phases 0, 1, 2, 2b, 2c, 5, 6).
  Phases 3/4/5 (feature-level task creation) removed — handled by autorun.
- New **Phase 2c: Task Creation Planner** — one agent reads all in-scope
  feature requirements and produces `task_creation_plan.md` with ordered
  tasks, after-chains, layer ordering, and architecture notes.
- **Phase 5** (single user gate): user approves scope findings + plan.
- **Phase 6** sequence (atomic): dry-run check → activate RELEASES.md →
  `create_orchestration_task.py --after-task <explore_id> --plan-path <plan>` →
  mark explore task completed → `task-complete` (one commit).

### Self-Perpetuating Orchestration Chain
Each orchestration task's goal.md includes 3-step ACs: run `task-create-code`,
run `create_orchestration_task.py` (creates next orch task OR validation task),
run `task-complete`. No external bootstrap needed.

`create_orchestration_task.py` Exit 3 (all covered) → replaced by creation of
a validation orchestration task. Case A and Case B removed from
`claude-automated-mode` bootstrap.

### New Skill: `release-begin-impl-finalize`
- Interactive, runs after autorun completes all packages.
- Phase 1: coverage verification (script-driven).
- Phase 2: after-chain reconciliation (script: `reconcile_after_chains.py`).
- Phase 3: semantic validation (N agents, one per feature).
- Phase 4: user review gate.
- Phase 5: finalize RELEASES.md, commit.

### Phase 6 Safety: Option B (after-chain guard)
Orchestration task carries `after: [TASK-PROC-035-07]`. Even partial Phase 6
failures leave the system in a safe, recoverable state. The after-chain
prevents premature execution. Explore task is auto-closed at Phase 6 end.

### New Scripts (7 total)
`check_task_against_plan.py`, `reconcile_after_chains.py`, `summarize_plan.py`,
`check_requirement_implementation.py`, `find_orchestration_tasks.py`,
`should_use_agents.py`, `parse_task_creation_plan.py`.

### `task_creation_plan.md` Schema
Defined in `plans_and_protocols/2026-04-25_05_opus_analysis_round3.md` §7.
YAML frontmatter + per-task YAML blocks + prose rationale. Machine-parseable
by `parse_task_creation_plan.py`. Append-only versioning.

## Scope

### In Scope
- Update REQ-PROC-035 sections SEC-05, SEC-06, SEC-07 to reflect the redesign
  (use `requ-explore` skill for each section update)
- Update REQ-PROC-041-03 (Automated Mode): remove Case A/B from bootstrap
  description, document simplified Case C/D only
- Update REQ-PROC-036 (Release Workflow): add `release-begin-impl-finalize`
  to the workflow sequence

### Out of Scope
- Implementation of any skill, script, or code change (separate impl tasks)
- Changes to requirements not directly impacted by the redesign
- Detailed implementation planning (that is a follow-up task)

## Acceptance Criteria

- [x] Root causes of 2026-04-24 `release-begin-impl` failure documented
      (see `plans_and_protocols/2026-04-24_01_opus_analysis.md`)
- [x] All three architectural plans reviewed, compared, recommended approach chosen
      (distributed pipeline + quality gates, Plan v3)
- [x] Phase 6 sequence designed with failure-safe after-chain (Option B)
- [x] `task_creation_plan.md` schema defined
- [x] Script division of labour specified (7 scripts, ROI documented)
- [x] Responsibility matrix drawn; 4 duplications eliminated
- [x] All Round 2 gaps resolved or explicitly deferred with rationale
- [x] REQ-PROC-035 SEC-05 updated: self-perpetuating chain replaces Bootstrap
      Rule inline task-create; `task_creation_plan.md` artifact referenced
- [x] REQ-PROC-035 SEC-06 updated: Phase 2c Planner, Phase 6 auto-close,
      no Phase 3/4/5; `release-begin-impl-finalize` named as successor skill
- [x] REQ-PROC-035 SEC-07 updated: per-package status table mentioned
- [x] REQ-PROC-041-03 updated: Cases A and B removed; self-perpetuating chain
      described; `find_orchestration_tasks.py` referenced for Case A replacement
- [x] REQ-PROC-036 updated: `release-begin-impl-finalize` added to release
      workflow sequence between autorun and `/release`

## References

| Document | Content |
|----------|---------|
| `plans_and_protocols/2026-04-24_01_opus_analysis.md` | Root cause analysis (Issues 1–4) |
| `plans_and_protocols/2026-04-24_02_opus_analysis_round2.md` | Fix strategy, release-start-impl concept |
| `plans_and_protocols/2026-04-25_01_opus_plan_skill_improvements.md` | Skill bug analysis, Phase-by-phase fixes |
| `plans_and_protocols/2026-04-25_02_opus_plan_distributed_architecture.md` | Distributed pipeline architecture (v2) |
| `plans_and_protocols/2026-04-25_03_opus_plan_distributed_with_quality_gates.md` | Quality gates, v3 — the chosen plan |
| `plans_and_protocols/2026-04-25_04_opus_analysis_round2.md` | Gap analysis (A–G), Bootstrap timing, script list |
| `plans_and_protocols/2026-04-25_05_opus_analysis_round3.md` | Phase 6 sequence, new gaps H–P, plan schema, responsibility matrix |

## Notes

**Status**: Analysis complete. Waiting for user instruction to proceed with
requirements updates. When proceeding, spawn one agent per requirement update
using `requ-explore` skill for each of REQ-PROC-035, REQ-PROC-041-03, and
REQ-PROC-036.
