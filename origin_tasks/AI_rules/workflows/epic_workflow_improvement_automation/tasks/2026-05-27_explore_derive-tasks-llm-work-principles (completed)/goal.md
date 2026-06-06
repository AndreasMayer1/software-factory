---
task_id: TASK-PROC-006-05
type: explore
parent_requirement: REQ-PROC-006
urgency: 3
urgency_reason: U3-FRES
impact: 4
impact_reason: I4-QUAL
status: completed
created: 2026-05-27
started: 2026-05-28
completed: 2026-05-30
session_completed_at: 2026-05-30T11:52:32Z
after: [TASK-PROC-006-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Derive the implementation task set for the cross-factory LLM-work-principles requirement created by TASK-PROC-006-03, using task-derive-from-requ. Add every created task to the priority override file and wire the validation task."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
session_id: cec5738a-1c07-42c1-839c-0ed21166613d
session_account: gmail2
---
# Goal: Derive Implementation Tasks from the LLM-Work-Principles Requirement

## Objective

TASK-PROC-006-03 creates a new **cross-factory LLM-work-principles requirement**
(round-4 IMPL-K; proposed location
`requirements_tasks/process/AI_rules/llm_work_principles/`). This task decomposes
that requirement into implementation tasks using the **`task-derive-from-requ`**
skill.

## Locate the requirement first

The principles requirement did not exist when this task was created. Find it:
```
grep -rl "llm.work.principles\|irreversibility threshold\|just-in-time context" requirements_tasks/process/ --include="requirements.md"
```
or check the id_registry for the new REQ-PROC id allocated by TASK-PROC-006-03.
Confirm it is the principles requirement before deriving.

## MANDATORY READING — the concept (read before any work)

`requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-05-01_explore_redesign-claude-optimize-skill/plans_and_protocols/`

- `2026-05-16_08_opus_synthesis_round4.md` — **Part 5 lists principles a–h with sources and the irreversibility threshold. Start here.**
- `2026-05-16_06_web_research_round2.md` — Q3, the sourced principle list

The principles (factory-wide): (a) scripts over instructions; (b) save tokens;
(c) force-via-hooks **only when violation is unrecoverable** (irreversibility
threshold); (e) just-in-time context loading; (f) the feedback loop is the product
(prefer a deterministic gate over a new skill/instruction for recurring failures);
(g) sub-agent context isolation; (h) smallest-set-of-high-signal-tokens as a
measured target.

## What the derived tasks should look like (intent — authoritative source is the requirement's ACs)

These principles are mostly **codification + targeted audits**, e.g.: a task to add
the principles to a guideline doc; a task to audit CLAUDE.md size against principle
(b)/(e) and propose a split; a task to define the irreversibility-threshold test for
promoting prompt rules to hooks. Keep scope tight — do NOT let this balloon into a
factory-wide rewrite (round-4 §9 scope-creep warning).

## Post-creation obligations (MANDATORY)

1. **Add every created task ID to** `.claude/task_ordering_priority_override.txt`
   under a `# --- LLM-work-principles impl ---` section, with one-line comments.
2. **Wire the validation task**: append every created task ID to the `after:` list
   of **TASK-PROC-006-06** so validation runs only after these complete too.

## Acceptance Criteria

- [x] Principles requirement located and confirmed (REQ-PROC-059 at requirements_tasks/process/AI_rules/llm_work_principles/requirements.md)
- [x] Every AC of the principles requirement covered by ≥1 created task (100% coverage: 3/3 ACs by TASK-PROC-059-01)
- [x] A verification task exists (per task-derive-from-requ) — < 3 impl tasks so verification section is inline in TASK-PROC-059-01 per skill rules
- [x] All created tasks reference the concept docs in their goal.md (TASK-PROC-059-01 references 2026-05-16_08_opus_synthesis_round4.md Part 5)
- [x] Every created task ID added to `.claude/task_ordering_priority_override.txt` (TASK-PROC-059-01 under `# --- LLM-work-principles impl ---`)
- [x] Created task IDs appended to TASK-PROC-006-06's `after:` list (TASK-PROC-059-01 added)
- [x] Scope kept tight (no factory-wide rewrite) — 1 XS task, purely documentation verification

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-006-03 | pending | Must create the principles requirement first |
