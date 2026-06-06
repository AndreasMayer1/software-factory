---
task_id: TASK-PROC-034-18
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-IMPL
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-04-22
effort: S
created: 2026-04-22
after: []
awaiting: []
target_package: "Release Tooling"
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Fix next_tasks.py to stop unrelated explore tasks from blocking current-release impl work via new writes_requirements frontmatter flag"
release_description: "Autorun picks the correct next task — current-release impl tasks are no longer blocked by unrelated forward-looking explore tasks."
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Implementation Task: Fix next_tasks.py Explore/Impl Prioritization

## Goal

Stop `scripts/next_tasks.py` from letting unrelated, low-priority explore tasks (future features, flow exploration, market research) block implementation of the current release, while preserving the original safety guarantee: requirements-writing explore tasks (from `requ-derive-from-flow`) always run before their corresponding impl tasks.

## Background

`next_tasks.py` currently sorts ALL explore tasks before ALL impl tasks globally. This was introduced to protect the `requ-derive-from-flow` workflow (explore tasks write requirements, impl must wait). But it also causes low-priority forward-looking explores (e.g. Therapy End Flow, Backup flows) to block current-release impl work.

The fix: introduce a `writes_requirements: true` frontmatter flag. Only tasks with this flag get the critical-path priority. All other explores fall to their natural position.

## Plan

See `plans_and_protocols/2026-04-22_02_opus_plan.md` for full analysis and implementation steps.

## Scope

- `scripts/next_tasks.py` — new sort key with `writes_requirements` lane
- `.claude/skills/requ-derive-from-flow/skill.md` — add flag to task templates
- `scripts/validate_meta.py` — accept new field
- Audit other requirement-writing skills
