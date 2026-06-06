---
task_id: TASK-PROC-001-07
type: impl
parent_requirement: REQ-PROC-001
urgency: 4
urgency_reason: U4-PROC
impact: 4
impact_reason: I4-ENAB
status: completed
completed: 2026-06-02
session_completed_at: 2026-06-02T17:38:53Z
started: 2026-06-02
effort: S
created: 2026-05-19
after: [TASK-PROC-001-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-03]
  sections: []
scope_description: "Replace the LLM-driven Quick-Explore-Agent file-count estimate in task-create-code skill Phase 2.3 with an automated structural check. Add S1 (skill-chain depth) as a co-equal signal alongside the existing file-count tiers."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ba1e025f
  file: ../../requirements.md
session_id: a63355a5-7097-47a9-badd-587fe571078c
session_account: gmail
---
# Goal: task-create-code automated structural check

## Objective

`.claude/skills/task-create-code/skill.md` Phase 2.3 currently asks a Quick-Explore-Agent to estimate the file count touched by a proposed code task. That estimate is variable — agent runs disagree across invocations on the same input — and the resulting tier (small / medium / large) drives whether the task gets `opus_recommended: true`. This task replaces the LLM-driven estimate with an automated structural check based on the deterministic file globs in goal.md scope, and adds S1 (skill-chain depth) as a co-equal signal so the tier decision reflects per-task tool-call volume too.

## Scope

- Replace the Quick-Explore-Agent step in `.claude/skills/task-create-code/skill.md` Phase 2.3 with a structural check (e.g. count files matched by goal.md scope globs, count of explicit file paths).
- Add S1 (skill-chain depth: number of heavy-skill invocations the task requires) as a co-equal signal alongside file-count tiers. Either signal crossing its threshold triggers the higher tier.
- Document the new check inline in the skill body and remove the Quick-Explore-Agent invocation.
- Preserve the existing tier → `opus_recommended` mapping; only the upstream signal source changes.

## Acceptance Criteria

- [x] **AC-01** — Every new task's `goal.md` declares at least one of: `expected_tool_calls` (estimated count of Bash + Read + Edit calls the task will make at runtime) or `skill_chain_depth` (count of heavy-skill invocations). The value is visible to creation-time tooling so a gate can act on it.
- [x] **AC-03** — No task with `expected_tool_calls > 60` or `skill_chain_depth ≥ 4` has both `opus_recommended: false` *and* no documented agent fan-out plan. At least one of three end states holds: Opus is recommended; the task has been split into child tasks; or `goal.md` contains a named fan-out plan describing which agents are spawned, what they distill, and what they return.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed-after-this-runs | Synthesis from explore task |
