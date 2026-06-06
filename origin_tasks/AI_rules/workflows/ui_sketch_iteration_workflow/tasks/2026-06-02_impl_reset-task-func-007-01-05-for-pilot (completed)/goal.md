---
task_id: TASK-PROC-032-27
type: impl
parent_requirement: REQ-PROC-032
urgency: 4
urgency_reason: U4-BLOCKING
impact: 4
impact_reason: I4-ENAB
status: completed
effort: XS
created: 2026-06-02
started: 2026-06-02
completed: 2026-06-02
session_completed_at: 2026-06-02T17:52:23Z
expected_tool_calls: 15
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Reset TASK-FUNC-007-01-05 for a pilot run of the reworked scribble skill: archive old output to a branch, wipe develop's scribble + pending_feedback, reset task status, annotate with pilot context."
release_description: ""
opus_recommended: false
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
session_id: caccf56a-05ef-4dbe-ba4c-69ecd39d90c6
session_account: gmail
---
# Goal: Reset TASK-FUNC-007-01-05 for pilot run of reworked scribble skill

## Objective

Reset TASK-FUNC-007-01-05 ("Client Send Screen — UI Scribble") so it can be re-executed with the reworked ui-scribble-* skill and agent suite (reworked May/June 2026). The previous run produced v1+v2 scribbles using the old skill; those must be preserved on an archive branch for later comparison, then deleted from `develop` along with the stale pending_feedback checkpoint. The task's own goal.md must be reset to `not_started` and annotated as a pilot.

## Scope

### In Scope

1. **Create archive branch** `archive/scribble-pilot-v1-old-skill` from current HEAD on `develop`. This branch preserves the v1+v2 scribbles, the pending_feedback checkpoint, and the in-progress task state. Switch back to `develop` immediately after — never leave the session on the archive branch.

2. **Delete old scribbles** on `develop`:
   - Remove `requirements_tasks/scribbles/therapist/data_transfer/` (entire folder, including v1/ and v2/).
   - Use `git rm -r requirements_tasks/scribbles/therapist/data_transfer/`.

3. **Delete pending feedback** on `develop`:
   - Remove `automation/pending_feedback/TASK-FUNC-007-01-05/` (both `question.md` and `answer.md`).
   - Use `git rm -r automation/pending_feedback/TASK-FUNC-007-01-05/`.

4. **Delete plans_and_protocols folder contents** on `develop`:
   - Run `git ls-files requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/tasks/2026-04-26_impl_client-send-screen-scribble/plans_and_protocols/` to list any tracked files.
   - If any files are tracked: `git rm -r .../plans_and_protocols/`
   - Also delete any untracked files present (check with `ls .../plans_and_protocols/ 2>/dev/null`).
   - Git investigation result (2026-06-02): no `plans_and_protocols/` files were committed during the previous run — the folder likely does not exist. Still run the check to confirm a clean state.

5. **Reset TASK-FUNC-007-01-05 goal.md** frontmatter on `develop`:
   - `status: in_progress` → `status: not_started`
   - Remove `started: 2026-05-26`
   - Remove `session_id:` line
   - Remove `session_account:` line

6. **Append a Pilot Note section** to TASK-FUNC-007-01-05 goal.md (see "Pilot Note content" below).

7. **Commit** the changes using the `claude-commit` skill.

### Out of Scope

- Modifying any scribble skill or agent files (the rework is already done).
- Executing TASK-FUNC-007-01-05 itself (that is the next step after this task completes).
- Any other pending_feedback items.

## Pilot Note content

Append the following section to `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/tasks/2026-04-26_impl_client-send-screen-scribble/goal.md` after the existing content:

```markdown
## Pilot Note

**This task is a PILOT run for the reworked ui-scribble-* skill and agent suite.**

The ui-scribble-* skills and agents were substantially reworked in May/June 2026 (see
`requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/`
for the improvement chain — TASK-PROC-032-08 through TASK-PROC-032-26).

**Primary goal**: produce an approved scribble for REQ-FUNC-007-01 (unchanged from before).

**Secondary goal**: identify gaps, friction points, or regressions in the new skills and
agents by observing the run live. Any issues found should be filed as follow-up tasks
in `ui_sketch_iteration_workflow/tasks/`.

**Archive**: The previous run's output (v1+v2 scribbles and the old pending_feedback
checkpoint) is preserved on branch `archive/scribble-pilot-v1-old-skill`.

**IMPORTANT — REMINDER FOR USER**: Once the first user-approval gate is reached again
(i.e., a new `automation/pending_feedback/TASK-FUNC-007-01-05/question.md` appears),
do the following before approving or requesting changes:

1. Open `requirements_tasks/scribbles/therapist/data_transfer/` — this is the new scribble.
2. `git checkout archive/scribble-pilot-v1-old-skill -- requirements_tasks/scribbles/therapist/data_transfer/`
   to temporarily restore the old scribble alongside for comparison (or open a second
   terminal on the archive branch).
3. Compare quality, completeness, and AC coverage between old and new.
4. Note any differences — positive or negative — as feedback in this task's
   `plans_and_protocols/` folder.
```

## Acceptance Criteria

- [x] Branch `archive/scribble-pilot-v1-old-skill` exists and contains the v1+v2 scribble files and `automation/pending_feedback/TASK-FUNC-007-01-05/`
- [x] `requirements_tasks/scribbles/therapist/data_transfer/` is deleted from `develop`
- [x] `automation/pending_feedback/TASK-FUNC-007-01-05/` is deleted from `develop`
- [x] `plans_and_protocols/` in the scribble task folder is confirmed empty / non-existent (any tracked or untracked files removed)
- [x] TASK-FUNC-007-01-05 goal.md has `status: not_started`, no `started:`, no `session_id:`, no `session_account:`
- [x] TASK-FUNC-007-01-05 goal.md has the `## Pilot Note` section with archive branch name and comparison reminder
- [x] All changes committed on `develop` via `claude-commit`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies — can start immediately |

## Notes

- **standalone_override** applied: the user explicitly specified all task parameters. The uncovered REQ-PROC-032 ACs (AC-08..11) are unrelated to this operational reset; redirect to `task-derive-from-requ` was skipped.
- The TASK-FUNC-007-01-05 task folder is at: `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/tasks/2026-04-26_impl_client-send-screen-scribble/`
- After this task completes, TASK-FUNC-007-01-05 should appear in the priority override list and can be executed normally.
- **Git investigation (2026-06-02)**: Two commits touched this task's output:
  - `88dc1e4c` — recorded session ID in goal.md
  - `4c51e105` — pause commit: wrote v1+v2 scribbles to the OLD co-located path (`feat_therapist_transfer_ui/scribbles/`) + pending_feedback
  - The old co-located scribbles were migrated to `requirements_tasks/scribbles/therapist/data_transfer/` by TASK-PROC-032-22 (`52ff0009`); nothing remains at the old path.
  - No `plans_and_protocols/` files were ever committed. Current file state: only `goal.md` in the task folder.
