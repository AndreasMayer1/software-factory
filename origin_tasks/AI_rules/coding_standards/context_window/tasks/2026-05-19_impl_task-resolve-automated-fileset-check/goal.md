---
task_id: TASK-PROC-001-08
type: impl
parent_requirement: REQ-PROC-001
urgency: 4
urgency_reason: U4-PROC
impact: 4
impact_reason: I4-ENAB
status: pending
effort: S
created: 2026-05-19
after: [TASK-PROC-001-02, TASK-PROC-001-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05]
  sections: []
scope_description: "Replace the LLM-driven '>4 source files → agent-assisted' decision in task-resolve skill Step 2 with an automated structural check using the new per-task should_use_agents.py mode."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ba1e025f
  file: ../../requirements.md
---
# Goal: task-resolve automated file-set check

## Objective

`.claude/skills/task-resolve/skill.md` Step 2 currently uses an LLM-judged rule — "if more than ~4 source files are in scope, switch to agent-assisted mode". That judgement varies and was identified by the TASK-PROC-001-02 synthesis as one of the unreliable per-task budget decisions. With the new per-task mode added to `scripts/util/should_use_agents.py` (TASK-PROC-001-04), this decision becomes mechanical: feed the scope file list to the script and read back a deterministic verdict.

## Scope

- Edit `.claude/skills/task-resolve/skill.md` Step 2 to invoke `scripts/util/should_use_agents.py` in per-task mode against the scope file set instead of using an LLM-judged file count.
- Remove the "~4 source files" heuristic prose; reference the script as the source of truth.
- Preserve the agent-assisted path itself — only the trigger changes.

## Acceptance Criteria

- [ ] **AC-05** — Heavy skills that perform multi-file read passes (currently `requ-explore`, `task-resolve`, `task-create`, `release-begin-impl`) defer to agents for read-set scans when the per-task read budget is exceeded. This budget is distinct from the release-level threshold in `scripts/util/should_use_agents.py`, which governs release-scope scans only.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed-after-this-runs | Synthesis from explore task |
| TASK-PROC-001-04 | completed-after-this-runs | Per-task mode added to should_use_agents.py |

## Follow-on

TASK-PROC-001-10 adds the **open-scope (S2) branch** to `task-resolve` Step 2 on top of this task's closed-scope check. Implement this task first; -10 inserts its discovery gate before the file-set check established here.
