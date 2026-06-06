---
task_id: TASK-PROC-035-13
type: impl
parent_requirement: REQ-PROC-035
urgency: 4
urgency_reason: U4-PLAN
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-04-27
started: 2026-04-27
completed: 2026-04-27
after: []
awaiting: []
awaiting_note: ""
target_package: "Transfer Data Model"
covers:
  acceptance_criteria: []
  sections: [SEC-05, SEC-06]
scope_description: "Improve orchestration chain: batch all tasks for one package per session (max 6), orch tasks always rank above impl tasks in next_tasks.py"
release_description: "Orchestration chain creates all tasks per package per session, eliminating false AC-coverage warnings."
opus_recommended: true  # reason: urgency 4 + impact 4; architectural change to core release pipeline
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 4ca5a917
  file: ../requirements.md
---

# Goal: Batch Orchestration Task Creation (Per-Package, Max 6) + Orch-First Ranking

## Objective

Improve the release orchestration chain in two related ways:

1. **Batch creation**: Each orchestration task creates all pending impl tasks for one package (instead of one task total), capped at 6 tasks per session. The same-package constraint keeps session context focused.
2. **Orch-first ranking**: Orchestration tasks always rank above impl tasks in `next_tasks.py`, so the entire chain runs to completion before any implementation starts.

These two changes together give Model A's upfront-creation semantics (all tasks visible before impl starts) while preserving Model B's sequential chain infrastructure.

## Context

See `plans_and_protocols/2026-04-27_analysis_task_creation_models.md` for the full pro/con analysis that led to this decision.

**Root bug**: `next_tasks.py` guard (lines 617–624) checks for an open explore task with `target_package == active_package`. Orchestration tasks carry `target_release` but no `target_package`, so the guard misses them and the "UNCOVERED ACs" warning fires as a false positive.

**Why orch-first ranking eliminates the false positive**: once orch tasks always run first (before any impl task is surfaced), the coverage check is only ever evaluated after all tasks are created — so it's either silent (all covered) or a real signal (plan was incomplete).

## Scope

### In Scope
- Phase 1: Update REQ-PROC-035 (SEC-05, SEC-06) to reflect batch-per-package behavior and orch-first ranking rule. Update REQ-PROC-042 if any AC or section references the ranking mechanism. Use `requ-explore` skill.
- Phase 2: Implement the code changes — see Implementation Targets below.

### Out of Scope
- Changing the overall sequential chain architecture (stays as Model B)
- Changing `release-begin-impl` Phase 6 (first orch task creation stays as-is)
- `check_ac_coverage.py` logic changes (orch-first ranking makes this unnecessary)
- Parallelising impl tasks across sessions

## Implementation Targets

| File | Change |
|---|---|
| `scripts/parse_task_creation_plan.py` | Add `--next-uncreated-package` mode: returns all plan entries for the next uncreated package (all tasks in one batch), exits 3 when all packages created |
| `scripts/create_orchestration_task.py` | Call `--next-uncreated-package` instead of `--next-uncreated`; build a multi-step AC list in the orch task template (one `task-create-code` call per task in the batch, capped at 6) |
| Orch task goal.md template (in `create_orchestration_task.py`) | Replace single Step 1 AC with variable list: `- [ ] Run task-create-code for [task_name] (AC: [acs])` × N entries |
| `scripts/next_tasks.py` or `.claude/task_ordering_rules.yaml` | Add ranking rule: any non-terminal orch task (scope_description starts with "Orchestration:") ranks above any impl task |

## Acceptance Criteria

- [ ] Phase 1 complete: REQ-PROC-035 SEC-05 and SEC-06 updated; requ-explore approved by developer
- [ ] `parse_task_creation_plan.py --next-uncreated-package` implemented and tested
- [ ] `create_orchestration_task.py` creates an orch task with N `task-create-code` ACs (N = tasks in next package, max 6)
- [ ] Orch task goal.md lists each impl task to create as a separate AC bullet
- [ ] Orch tasks rank above impl tasks in `next_tasks.py` output (verified by running the script against current task list)
- [ ] False-positive "UNCOVERED ACs" warning no longer appears when TASK-PROC-035-12 is open
- [ ] Existing unit tests for `parse_task_creation_plan.py` and `create_orchestration_task.py` still pass
- [ ] New tests cover the `--next-uncreated-package` batch mode and the capped-at-6 behaviour

## Execution Plan

### Phase 1 — Requirements (run first, blocking)
Use `requ-explore` skill to update REQ-PROC-035 (and REQ-PROC-042 if affected).
Wait for developer approval before proceeding to Phase 2.

### Phase 2 — Implementation
1. Spawn `opus-advisor` agent: read this goal.md + implementation targets + `plans_and_protocols/2026-04-27_analysis_task_creation_models.md` → produce a detailed implementation plan in `plans_and_protocols/YYYY-MM-DD_01_opus_plan.md`
2. Developer reviews and approves plan
3. Spawn implementation-engineer agents (can run in parallel per file group):
   - Agent A: `parse_task_creation_plan.py` changes + tests
   - Agent B: `create_orchestration_task.py` + template changes + tests
   - Agent C: `next_tasks.py` / `task_ordering_rules.yaml` ranking rule
4. Integration smoke test: run `python3 scripts/next_tasks.py` against current task list; verify orch task ranks #1 and no false-positive warning

## Notes

- The cap of **6 tasks per session** is a fixed guard against context blowup on large packages. The natural boundary is "one full package"; 6 is the safety ceiling.
- The same-package constraint is enforced by `--next-uncreated-package` returning only entries for the *next uncreated* package — the orch task never mixes packages.
- If a package has more than 6 tasks, the orch task creates the first 6; the next orch task (auto-created by the chain) picks up the remainder of the same package before moving on.
