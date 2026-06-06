---
task_id: TASK-PROC-046-16
type: impl
parent_requirement: REQ-PROC-046
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: S
created: 2026-05-19
after: [TASK-PROC-046-13, TASK-PROC-046-19]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Apply user-approved quality-rule changes. Reads proposals from `scripts/quality/proposals/`, applies the decisions in `automation/pending_feedback/<TASK_ID>/answer.md`, commits, runs the reset script. This task folder is PERMANENT — it is never renamed with `(completed)` suffix and never auto-deleted. Each round resets it back to `status: pending` via `scripts/quality/reset_proposals_loop.py`."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: ""
session_account: ""
---
# Goal: Apply quality-rule proposals (permanent loop-task)

## Objective

This is the **permanent loop-task** that turns AI-filed quality-rule
proposals into actual gate changes after user review. The task folder
lives forever — it is the same physical directory every round. Each
round goes:

```
AI agents file proposals → user fills answer.md → orchestrator
resumes this task → session applies decisions → commits →
reset script restores pending Q&A → ready for next round.
```

## Why this task is never marked completed

`task-complete` is coupled to commit. If this task ever transitioned to
`status: completed`, the next round would need a new task — exactly the
proliferation the user rejected in `2026-05-14_feedback_03.md`
Allgemeines 1.

Instead the round ends with `scripts/quality/reset_proposals_loop.py`
restoring:

- `goal.md` `status: pending` (the orchestrator's `update_goal_session_fields`
  may have written `in_progress` during execution — reset back).
- `goal.md` `session_id: ""` (next round starts fresh).
- `automation/pending_feedback/<this task_id>/question.md` (re-created from
  the generic template, with a new `asked_at`).
- `automation/pending_feedback/<this task_id>/answer.md` (verbatim copy of
  `automation/pending_feedback/TEMPLATE_answer.md`).

The previous round's `pending_feedback/<task_id>/` has already been moved
to `automation/answered_feedback/<task_id>/timestamp_<UTC>/` by the
orchestrator on successful resume (research §1) — audit trail is
preserved there plus in the round's git commits.

## Round execution — what an agent picking this up does

When the orchestrator launches a fresh session on this task (because
`answer.md` was filled), the session runs:

### Step 1 — Read the answer

Read `<the answer that the orchestrator passed as the prompt context>`.
The format (per question.md) is one entry per proposal, blank-line-
separated:

```
proposal_id: <slug>
decision: accepted | rejected | superseded_by:<other_slug>
notes: <free text — optional reasoning or amendments>
```

### Step 2 — For each entry

1. Locate the proposal file at
   `scripts/quality/proposals/<category>/<filename containing the slug>.md`.
2. If `decision: accepted`:
   - Apply the `## Proposed change` body to the indicated file(s)
     (`analysis_options.yaml`, `scripts/quality/check_*.sh`, requirement
     ACs, etc.). If the change is non-trivial enough that it warrants a
     dedicated impl task, instead create a follow-up impl task via
     `task-create` and leave a note in the proposal's body —
     `decision: accepted` does not have to mean "applied in this same
     commit".
   - Update the proposal file frontmatter: `status: accepted`.
3. If `decision: rejected`:
   - Update the proposal frontmatter: `status: rejected`.
   - Append a `## Decision` section quoting the `notes:` text so the
     audit trail is in the proposal file itself.
4. If `decision: superseded_by:<other_slug>`:
   - Set this proposal's `status: superseded`.
   - Append `## Superseded by` linking to the other proposal file.

### Step 3 — Commit

Use `claude-commit` to stage and commit:

- Edited `analysis_options.yaml` / `scripts/quality/check_*.sh` / requirement
  files (the applied changes).
- Updated proposal files (their `status:` field bumped + decision sections).
- Any new follow-up impl-task `goal.md` files created in Step 2.

**Do not** include this `goal.md` in the commit (its `status` is still
`pending` after the reset — see Step 4 — but the orchestrator will have
flipped it to `in_progress` during the run; that flip will be reverted by
the reset script and should NOT appear in this round's commit).

**Do not** include the round's archived `answered_feedback/<TASK_ID>/`
folder in this commit — the orchestrator moves it after the session ends.

### Step 4 — Reset

Run `python3 scripts/quality/reset_proposals_loop.py`. This re-creates
`automation/pending_feedback/<this task_id>/` from the templates, resets
this `goal.md` `status` to `pending`, and clears `session_id`.

The reset's filesystem changes will appear in the NEXT round's commit
(intentional — keeps this round's commit scoped to its decisions).

## Acceptance Criteria (per round)

- [ ] Each entry in `answer.md` is reflected in the corresponding
      proposal file's frontmatter `status:` field.
- [ ] All accepted-and-in-scope changes are present in the round commit.
- [ ] Accepted changes that need a follow-up impl task have a new
      `goal.md` under `requirements_tasks/`.
- [ ] `scripts/quality/reset_proposals_loop.py` has run and exited 0.
- [ ] This goal.md's `status` is `pending` again, and `session_id` is empty.
- [ ] A fresh `question.md` and template `answer.md` exist under
      `automation/pending_feedback/<this task_id>/`.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-13 (proposals collection mechanism) | In progress | Creates this task folder, the proposals folder, and the reset script |
| `automation/pending_feedback/TEMPLATE_question.md` and `TEMPLATE_answer.md` | Live | Used verbatim by the reset script |
| `scripts/automation/orchestrate.py` | Live | No changes needed; `NEW_SESSION_REQUIRED` already supports pre-session Q&A (research §3) |

## Notes

**Why `status: pending` rather than a new `active` status**: the project's
lifecycle is `pending` / `in_progress` / `completed` / `blocked`. Adding
`active` would break `next_tasks.py`, status overviews, and the
orchestrator's queue. `pending` + a non-template `answer.md` is the right
signal: `next_tasks.py` hides it from the runnable queue
(`load_pending_feedback_ids` — research §3), and the orchestrator picks it
up only when the answer arrives.

**Why the reset script is separate from `task-complete`**: per the user's
feedback, the loop is "completed" only conceptually. A future improvement
could couple the reset into `task-complete` via a skill flag, but that
expands `task-complete`'s contract — out of scope for the initial design.

**Audit trail**: every round produces (a) a git commit on `develop` with the
applied changes, (b) an archived `answered_feedback/<task_id>/timestamp_*/`
directory containing the round's `question.md` and `answer.md`. Both
together let a reader reconstruct what was proposed, decided, and applied,
without needing the session JSONL.
