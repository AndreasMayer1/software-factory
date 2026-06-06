---
task_id: TASK-PROC-054-08
type: impl
parent_requirement: REQ-PROC-054
urgency: 4
urgency_reason: U4-FAIL
impact: 5
impact_reason: I5-ENAB
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 35
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-19]
  sections: []
scope_description: "Create the write-setup-manual skill that reads environment sources, proposes updates to setup guides at a user gate, and applies approved changes"
release_description: ""
opus_recommended: true
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 30ea8ea0
  file: ../requirements.md
---

# Goal: Implement write-setup-manual Skill (REQ-PROC-054 AC-19)

## Objective

Create the `write-setup-manual` skill in `.claude/skills/`. The skill is the maintenance mechanism for keeping the project's setup guides current whenever environment-related changes are made (REQ-PROC-054 AC-19).

When invoked, the skill must:

1. **Investigate** — read all environment-configuration sources of truth
2. **Compare** — diff each source against the current content of the relevant setup guides to identify stale steps, wrong version numbers, missing sections, and gaps
3. **User gate** — present a structured proposal of all findings to the developer for review and feedback before writing anything
4. **Apply** — write only the developer-approved changes to the affected guides

The skill's description must explicitly state it must be invoked whenever any of the following change: `.devcontainer/devcontainer.json`, `.devcontainer/setup.sh`, `scripts/windows/`, quality-gate scripts, toolchain version pins, or any AC of REQ-PROC-054.

## Requirements Summary

REQ-PROC-054 AC-19 requires this skill to exist and serve as the primary maintenance mechanism for the setup guides under `setup_guides/`.

For complete requirements at task creation time:
```
git show 30ea8ea0:requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- The skill file `.claude/skills/write-setup-manual.md` (created via `claude-create-skill`)
- The investigation phase: which sources to read, in what order
- The comparison logic: how to identify divergences between sources and guides
- The user gate: how to present proposed changes and collect developer feedback
- The application phase: how to write approved changes to the correct guides
- The skill description text, which must list trigger conditions explicitly

### Out of Scope

- Running the skill (updating the actual setup guides) — that happens when the skill is executed separately
- A consolidated DEVELOPER_SETUP_MANUAL.md or similar document
- Automated invocation hooks — the skill is developer-triggered

## Acceptance Criteria

- [ ] `.claude/skills/write-setup-manual.md` exists and follows project skill conventions (created via `claude-create-skill`)
- [ ] Skill description explicitly names all trigger conditions: devcontainer.json, setup.sh, scripts/windows/, quality-gate scripts, toolchain version pins, any REQ-PROC-054 AC change
- [ ] Skill reads every source listed in REQ-PROC-054 AC-19 during its investigation phase
- [ ] Skill has a user gate before writing any guide: proposed changes are shown and developer feedback is collected before anything is written
- [ ] Skill applies only developer-approved changes to the affected guides

## Design Notes

**Sources of truth the skill must read** (from AC-19):

- `.devcontainer/devcontainer.json`
- `.devcontainer/setup.sh`
- `scripts/windows/` (all scripts)
- Quality-gate scripts (`scripts/quality/`)
- Toolchain version pins (pubspec.yaml Flutter/Dart SDK constraints, devcontainer image tag)
- REQ-PROC-054 acceptance criteria

**Setup guides to maintain**:

- `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/wsl_devcontainer_setup.md`
- `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/sync_setup.md`
- `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/android_device_setup.md`
- `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/alternative_environment_setup.md`
- `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/backup_and_restore.md`

**Open design question for implementer — user gate granularity**: Should the gate occur once (all proposed changes across all guides as one summary) or per-guide (each guide's changes reviewed separately)?
Recommendation: once at the end — reviewing all changes together gives better cross-guide context and reduces back-and-forth. Override if per-guide approval produces a better UX in practice.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

**Standalone override**: The redirect to `task-derive-from-requ` was bypassed per explicit user instruction. REQ-PROC-054 has 11 uncovered ACs (AC-02 to AC-13 plus AC-19). The other 10 ACs describe environment states already implemented and predating the task-tracking system; only AC-19 represents new deliverable work here.

**MANDATORY**: Use `claude-create-skill` to create the skill file — no direct write to `.claude/skills/` is allowed. Use `task-complete` to close this task when done.
