---
task_id: TASK-PROC-041-04-03
type: impl
parent_requirement: REQ-PROC-041-04
urgency: 4
urgency_reason: U4-DEV-PRODUCTIVITY
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-06-02
started: 2026-06-02
completed: 2026-06-02
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06, AC-09]
  sections: []
scope_description: "Change post-resume cleanup: archive answered feedback as feedback-checkpoint files in the task's plans_and_protocols/, update orchestrator resume prompt with archive path, update all affected requirements/skills/scripts/artifacts"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: abd72adf
  file: ../requirements.md
---

# Goal: Archive Answered Feedback to Task Protocols

## Objective

Change the post-resume cleanup behavior in the automated-mode orchestrator so that answered `pending_feedback/` Q&A pairs are archived as `feedback-checkpoint` files inside the answering task's own `plans_and_protocols/` folder, rather than moved to the global `answered_feedback/` folder. Update the resume prompt so the resumed session is told where its answer record now lives.

## Requirements Summary

The `feat_feedback_pause_resume` feature (REQ-PROC-041-04) currently defines post-resume cleanup as: move `automation/pending_feedback/<TASK-ID>/` → `automation/answered_feedback/<TASK-ID>/`. The updated AC-06 changes this to:

1. Merge `question.md` + `answer.md` into a single `feedback-checkpoint` file in the task's `plans_and_protocols/`, named `YYYY-MM-DD_feedback-checkpoint_<TASK-ID>.md`
2. Delete `automation/pending_feedback/<TASK-ID>/`

New AC-09 requires the resume prompt to include a preamble with the archive path so the resumed session is not confused by the now-empty `pending_feedback/`.

For complete requirements at task creation time:
```
git show ffc602c7:requirements_tasks/process/AI_rules/workflows/epic_autonomous_task_execution/feat_feedback_pause_resume/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- `scripts/automation/orchestrate.py`: After detecting `question.md` + `answer.md`, before invoking `claude --resume`:
  1. Resolve the task folder from the `task_id` in `question.md` frontmatter
  2. Merge Q+A into a `feedback-checkpoint` file in the task's `plans_and_protocols/`
  3. Prefix the `-p` resume prompt with the archive path preamble
  4. Delete `automation/pending_feedback/<TASK-ID>/` after successful resume exit (existing AC-06 timing — only on normal exit, no new `question.md`)
- `feedback-checkpoint` file format: YAML envelope (`skill`, `mode: automated`, `decision`, `task_id`, `captured_at`) + free-form body sections `# Question`, `# Developer Answer`, `# Rationale Captured`
- Requirements updated: `feat_feedback_pause_resume/requirements.md` (AC-06, AC-09, AC-10), `feat_session_orchestrator/requirements.md` (any ACs referencing `answered_feedback/` or resume prompt construction)
- Skills updated: any skill that references `answered_feedback/` or describes the post-resume cleanup behavior
- Artifact registry: add `feedback-checkpoint` token to `.factory/registry/artifacts.yaml` under the `task-workspace` category (path glob: `requirements_tasks/**/plans_and_protocols/*feedback-checkpoint*.md`), as proposed in TASK-PROC-044-02-05 synthesis

### Out of Scope

- Changes to how `question.md` is written by the session (AC-01, AC-02 unchanged)
- The `answered_feedback/` folder itself — existing entries are left as-is, not migrated
- Interactive-mode feedback-checkpoint authoring (covered by a separate future task)
- Deleting the `answered_feedback/` folder from the repo

## Acceptance Criteria

- [x] AC-06: When a resumed session exits normally, the orchestrator merges `question.md` + `answer.md` into a `feedback-checkpoint` file in the task's `plans_and_protocols/`, deletes `pending_feedback/<TASK-ID>/`, and no longer writes to `answered_feedback/`
- [x] AC-09: The `-p` resume prompt is prefixed with a one-line preamble giving the archived feedback-checkpoint file path
- [x] AC-11: The `feedback-checkpoint` token is added to `.factory/registry/artifacts.yaml` under the `task-workspace` category with path glob `requirements_tasks/**/plans_and_protocols/*feedback-checkpoint*.md`, a one-line definition ("Developer decision captured at an automated-mode skill feedback gate"), and `mode: automated` noted in the description
- [x] AC-10 (task-level): All requirements, skills, scripts, and other artifacts that reference `answered_feedback/` or describe the post-resume cleanup behavior are updated before this task is marked complete — specifically:
  - `feat_session_orchestrator/requirements.md` (REQ-PROC-041-01) — update any ACs about `answered_feedback/` archival
  - Any skills referencing `answered_feedback/` (search `.claude/skills/`)
  - `.factory/registry/artifacts.yaml` — add `feedback-checkpoint` token
  - `CLAUDE.md` if it references `answered_feedback/`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-041-04-01](../2026-04-07_impl_feedback-pause-resume-files%20(completed)/goal.md) | Predecessor — original implementation of the pause/resume files this task modifies |
| [TASK-PROC-044-02-05](../../../../epic_factory_quality/feat_artifact_model/tasks/2026-06-01_explore_interactive-feedback-checkpoint-artifact%20(completed)/goal.md) | Predecessor — synthesis that proposed the feedback-checkpoint format and registry token |

## Notes

The `task_id` field in `question.md` frontmatter is the key for resolving the task folder. The orchestrator needs a helper (or inline logic) to walk `requirements_tasks/` looking for a `goal.md` whose `task_id` matches. The `scripts/tasks/` directory may already have utilities for this lookup; check before writing new code.

The `feedback-checkpoint` token name was recommended as Option A in the TASK-PROC-044-02-05 synthesis. This task locks in that choice and implements it for automated mode only. Interactive-mode capture (the skill writing the record post-decision) is a separate follow-up.
