---
task_id: TASK-PROC-001-06
type: impl
parent_requirement: REQ-PROC-001
urgency: 4
urgency_reason: U4-PROC
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-06-02
completed: 2026-06-02
session_completed_at: 2026-06-02T14:57:54Z
effort: S
created: 2026-05-19
after: [TASK-PROC-001-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03]
  sections: []
scope_description: "Add a creation-time sizing gate to the task-create skill: require new goal.md frontmatter fields expected_tool_calls / skill_chain_depth / synthesis_dependent, and block creation when S1-high tasks lack Opus / split / fan-out plan."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ba1e025f
  file: ../../requirements.md
session_id: e1394763-9206-422d-8408-8b8a74c922d1
session_account: web
---
# Goal: task-create sizing gate

## Objective

The synthesis from TASK-PROC-001-02 concluded that the most reliable place to size a task to fit Sonnet's context budget is at task-creation time, before any session is launched. This task wires REQ-PROC-001 AC-01, AC-02, AC-03 into `.claude/skills/task-create/skill.md`: every new goal.md must declare at least one of `expected_tool_calls` or `skill_chain_depth`, and `synthesis_dependent` (with justification) when true. A gate blocks creation — or warns loudly — when a high-S1 task has neither Opus, a split plan, nor a documented fan-out plan.

## Scope

- Edit `.claude/skills/task-create/skill.md` to require `expected_tool_calls` (int) or `skill_chain_depth` (int) in new goal.md frontmatter.
- Add optional `synthesis_dependent: true` with required one-line justification when true; omitted otherwise.
- Add a creation-time check: if `expected_tool_calls > 60` or `skill_chain_depth >= 4`, the task must satisfy at least one of: `opus_recommended: true`, child tasks declared, or a named fan-out plan in goal.md body — else block or warn.
- Replace the "Opus Recommendation Check" trigger table in `.claude/skills/task-create/skill.md` with the refined complexity-based criteria below. The vague `urgency ≥ 4 AND impact ≥ 4` rule is removed. Splitting is always the preferred resolution for high volume; model escalation is reserved for irreducible reasoning complexity:
  - **Synthesis that cannot be split**: multiple domains must be held simultaneously AND splitting would lose the synthesis value (e.g. architectural trade-off across layers, design decision requiring all context at once).
  - **Cross-cutting invariant**: task edits ≥3 files and every file must be changed with awareness of all others simultaneously (API rename, layer boundary change, shared constraint enforcement).
  - **Architectural judgment**: touches domain boundary, dependency-injection wiring, or a layer-purity rule in `doc/architecture/`.
  - **Explicit decision task**: type is `define`, or goal text contains "evaluate options", "decide approach", "architectural decision", "trade-off", "compare approaches".
  - **Security / privacy / compliance domain**: subtle reasoning errors have large consequences.
  - **Prior model failure**: the `verify-quality` cycle counter reached ≥3 on a previous attempt — escalate on the retry rather than exhausting the remaining budget.
  - Default: `opus_recommended: false`. If the task is large but not complex — split it instead.
- Add optional `discovery_command` field to the goal.md frontmatter template in `.claude/skills/task-create/skill.md`. When a task has open scope (S2), the field holds a shell command whose stdout integer is the work-item count at execution time (e.g. `flutter analyze 2>&1 | grep -c error`). Document when to populate it: open-scope tasks where the item count is unknown at creation and determines inline vs. fan-out approach. TASK-PROC-001-10 consumes this field in execution skills — define it here, use it there.
- Keep the skill body within its token budget; reference REQ-PROC-001 §"Signals recap" rather than restating it.

## Acceptance Criteria

- [x] **AC-01** — Every new task's `goal.md` declares at least one of: `expected_tool_calls` (estimated count of Bash + Read + Edit calls the task will make at runtime) or `skill_chain_depth` (count of heavy-skill invocations). The value is visible to creation-time tooling so a gate can act on it.
- [x] **AC-02** — Every task whose deliverable requires the executing session to hold multiple input domains simultaneously has `synthesis_dependent: true` in `goal.md` with a one-line justification. (Default is `false`; the field is omitted in that case.)
- [x] **AC-03** — No task with `expected_tool_calls > 60` or `skill_chain_depth ≥ 4` has both `opus_recommended: false` *and* no documented agent fan-out plan. At least one of three end states holds: Opus is recommended; the task has been split into child tasks; or `goal.md` contains a named fan-out plan describing which agents are spawned, what they distill, and what they return.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed-after-this-runs | Synthesis from explore task |
