---
task_id: TASK-PROC-046-13
type: impl
parent_requirement: REQ-PROC-046
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-05-23
session_completed_at: 2026-05-23T21:45:06Z
effort: M
created: 2026-05-14
after: [TASK-PROC-046-11]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Build the proposals-collection folder + a permanent (always-pending) generic loop-task that applies user-approved rule changes via the automation Q&A mechanism + a reset-script that resets the answer/question files so the same task folder serves every future round. Implements user feedback Allgemeines 1 in 2026-05-14_feedback_03.md (revised from the original Allgemeines 1 in feedback_02)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
session_id: eff133cc-ab0a-4138-aa84-d9e637f1df18
session_account: gmail
---
# Goal: Quality-rule proposals collection + permanent loop-task with reset script

## Objective

Build the channel through which AI-discovered improvement ideas reach the user without breaking the Goodhart's-Law protection (per REQ-PROC-046 Developer Guidelines: AI may propose, never autonomously modify gates). The user's revised design (2026-05-14_feedback_03.md, Allgemeines 1):

- **The question.md is a generic permanent reference**, not a per-round summary. It points at the proposals folder and to the answer-format spec; it does NOT duplicate the content of the individual proposal files.
- **There is no separate "review task"** that writes the question. There is one generic always-pending task whose *only goal* is to apply user-approved rule changes.
- **The task remains the same physical folder forever.** When a round completes, a reset script restores the task and Q&A files to their "awaiting-answer" state so the next round uses the same folder. No task proliferation.

## Requirements Summary

Implements user feedback in `2026-05-14_feedback_03.md` Allgemeines 1 (supersedes the design in `2026-05-14_feedback_02.md` Allgemeines 1+2). References the project's automation Q&A mechanism per `2026-05-14_research_automation_and_self_regen.md` and `.claude/skills/claude-automated-mode/skill.md` lines 76–139.

Current requirements: ../../requirements.md

## Scope

### In Scope

**Part A — Proposals collection folder.**

Create `scripts/quality/proposals/` with category subfolders, each with a brief `README.md`:

- `analysis_options/` — proposed analyzer-config changes
- `grep_gates/` — proposed `scripts/quality/check_*.sh` changes
- `thresholds/` — schwellwert tightenings / loosenings
- `new_gates/` — entirely new gates

Filename pattern: `<YYYY-MM-DD>_<short_slug>_<source_task_id>.md`.

Mandatory YAML frontmatter:

```yaml
---
proposal_id: <slug>
proposal_type: analysis_options | grep_gates | thresholds | new_gates
proposed_at: <YYYY-MM-DD>
proposed_by_model: <exact model identifier — e.g. claude-opus-4-7, claude-sonnet-4-6>
source_task: <TASK-ID where the AI noticed the opportunity>
status: pending_review | accepted | rejected | superseded
---
```

Body sections: `## Reason`, `## Proposed change`, `## Expected effects`, `## Alternatives considered`. Format spec in `scripts/quality/proposals/README.md`.

**Part B — Permanent loop-task.**

A single task folder under `requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-14_impl_apply-quality-rule-proposals-loop/` whose goal.md:

- `status: pending` permanently. Never renamed with `(completed)` suffix.
- `scope_description`: "Apply user-approved quality-rule changes. Reads proposals from `scripts/quality/proposals/`, applies the decisions in `automation/pending_feedback/<TASK_ID>/answer.md`, commits, runs the reset script."
- Body explains the loop semantics so a future agent picking this up understands why the folder is not renamed at the end.

**Part C — Permanent Q&A pair.**

Pre-create at task-creation time:

`automation/pending_feedback/<LOOP_TASK_ID>/question.md` with GENERIC reference body:

```yaml
---
task_id: <LOOP_TASK_ID>
session_id: NEW_SESSION_REQUIRED
account: <pick a valid account>
status: awaiting_answer
asked_at: <task creation timestamp>
skill: apply-quality-rule-proposals
---
```

```markdown
# Apply Quality-Rule Proposals

This is the recurring quality-rule application loop. It is *always* awaiting answer.

## Where the open proposals live
`scripts/quality/proposals/<category>/<YYYY-MM-DD>_<slug>_<source_task>.md`

Each file has `status: pending_review` until you decide. Read each one before writing your answer.

## How to write your answer
Open `answer.md` in this folder and replace the template content with your decisions, one entry per proposal:

```
proposal_id: <slug>
decision: accepted | rejected | superseded_by:<other_slug>
notes: <free text — optional reasoning or amendments>
```

Multiple decisions stacked, blank-line-separated.

## What happens after you save
The orchestrator detects the non-template answer, resumes a session on this task, the session reads each decision and applies the accepted ones (updates `analysis_options.yaml`, `scripts/quality/check_*.sh`, or the relevant rule definition), commits the change set, then runs the reset script to restore this folder to its awaiting-answer state for the next round.
```

`automation/pending_feedback/<LOOP_TASK_ID>/answer.md` is a verbatim copy of `automation/pending_feedback/TEMPLATE_answer.md` (sentinel `<!-- AWAITING_HUMAN_ANSWER -->` plus the warning text). AI never writes here.

**Part D — Reset script.**

`scripts/quality/reset_proposals_loop.py`:

1. Verifies the task folder exists at the canonical loop-task path.
2. Note: per research §1, after a successful resume the orchestrator already moves `automation/pending_feedback/<TASK_ID>/` to `automation/answered_feedback/<TASK_ID>/timestamp_<UTC>/`. The reset script's job is to **re-create** `pending_feedback/<TASK_ID>/` with a fresh question.md (from the template above, with a new `asked_at`) and a fresh `answer.md` (from `TEMPLATE_answer.md`).
3. Verifies the loop-task's goal.md `status` is still `pending` (the orchestrator's `update_goal_session_fields` may have written `in_progress` during execution — reset back to `pending`).
4. Clears the goal.md `session_id` field (per `update_goal_session_fields` semantics) — next round starts fresh.
5. Does NOT commit. The caller (the loop-task's last AC) is responsible for commit ordering.

**Part E — CLAUDE.md and skill updates.**

CLAUDE.md gets a new section instructing AI agents:

> When an AI agent (during normal coding or audit work) spots an opportunity for a quality-gate rule improvement — a recurring false positive, a missing rule pattern, a threshold consistently too tight or too loose, a new gate worth adding — it MUST file a Markdown proposal under `scripts/quality/proposals/<category>/` before declaring its task complete. The AI does NOT autonomously edit `analysis_options.yaml`, `scripts/quality/check_*.sh`, or the requirement ACs that define gates. The proposal flows through TASK-PROC-046 / proposals-loop for user review.

The `task-complete` skill is updated (via `claude-modify-skill`) to check: did this task touch quality-related files in a way that suggests an improvement? If yes, remind the agent to file a proposal.

### Out of Scope

- Building a UI for browsing proposals. The Markdown files are the UI.
- Periodic / cron triggers for the loop task. The loop runs whenever the user fills `answer.md`. Voluntary cadence.
- Multi-developer voting. Solo-dev project.
- Auto-categorization of proposals. AI agents pick the right subfolder.

## Acceptance Criteria

- [x] `scripts/quality/proposals/{analysis_options,grep_gates,thresholds,new_gates}/` exist, each with `README.md`.
- [x] `scripts/quality/proposals/README.md` documents the proposal-file format (frontmatter + body sections + filename pattern).
- [x] The permanent loop-task folder `2026-05-14_impl_apply-quality-rule-proposals-loop/` exists with the generic goal.md.
- [x] Pre-populated `automation/pending_feedback/<LOOP_TASK_ID>/question.md` exists with `session_id: NEW_SESSION_REQUIRED` and the generic reference body documented in Part C.
- [x] `automation/pending_feedback/<LOOP_TASK_ID>/answer.md` is a verbatim copy of `TEMPLATE_answer.md`.
- [x] `scripts/quality/reset_proposals_loop.py` exists and re-creates the `pending_feedback/<LOOP_TASK_ID>/` folder from the templates, resets goal.md status, and clears the session_id.
- [x] CLAUDE.md (or a new dedicated skill / agent guideline file) instructs AI agents to file proposals when they spot rule-improvement opportunities. The instruction explicitly forbids autonomous gate-set edits.
- [x] End-to-end smoke test documented in `plans_and_protocols/`:
  - AI files a sample proposal under `scripts/quality/proposals/grep_gates/`.
  - User fills `answer.md` with one accept and one reject.
  - Orchestrator picks up the answer, resumes the loop-task session.
  - Session reads decisions, marks proposal-1 as `accepted` (creates downstream impl task), marks proposal-2 as `rejected` with rationale in the proposal file.
  - Session commits.
  - Reset script runs, re-creates `pending_feedback/<LOOP_TASK_ID>/` from templates.
  - Subsequent `git status` is clean.
  - Orchestrator on the next iteration sees the new question.md, answer.md template, and treats the loop-task as awaiting-answer again.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-046-11 (gate enforcement mechanism) | Pending | The verify-quality skill must exist for AI agents to recognise rule-improvement opportunities |
| `automation/pending_feedback/TEMPLATE_question.md`, `TEMPLATE_answer.md` | Live in repo | Used verbatim — single source of truth |
| `scripts/automation/orchestrate.py` | Live in repo | No orchestrator changes needed; pre-session Q&A is already supported via `NEW_SESSION_REQUIRED` (research §3) |

## Notes

**Why a permanent task instead of self-regenerating-via-successor**: the user explicitly rejected the per-round-new-task design (Allgemeines 1 in feedback_03) because `task-complete` is coupled to the commit step and creating a new folder per round adds clutter. The reset-script approach keeps one folder forever, archives the answered-feedback under `automation/answered_feedback/<TASK_ID>/timestamp_*/` (the orchestrator's default behavior), and re-creates the pending Q&A files for the next round. Audit trail is preserved via the `answered_feedback/` history plus git commits.

**Why `status: pending` and not a special `active` status**: the project's task lifecycle uses `pending` / `in_progress` / `completed` / `blocked`. Introducing an `active` status would break the existing scripts (`next_tasks.py`, status-overview generator). `pending` is the right conceptual fit — the orchestrator picks up tasks with `status: pending` and non-template answer.md just fine; no orchestrator changes needed.

**Why proposals live next to the rules (`scripts/quality/proposals/`) and not in the task folder**: per the user's instruction in feedback_02 Allgemeines 1, the ideas live "where the rules are defined." That keeps the proposals discoverable to whoever opens `scripts/quality/` and prevents the loop-task folder from accumulating per-round content. The loop-task folder stays generic; the proposals folder accumulates the actual change candidates.

**Why `proposed_by_model:` is mandatory in proposal frontmatter**: this addresses E.2 from feedback_02 — an LLM-version-tagged proposal supports future archival of "stale proposals from older / weaker models" without forcing the archival mechanism to be built today.

**Commit semantics in the loop**: the loop-task's last AC is "commit the proposal applications then run reset_proposals_loop.py". The commit must include: edits to analyzer config / scripts / requirements, the proposal files (with their `status:` field updated), and the archived answer. The reset script's changes (re-created question.md + fresh answer.md template) are committed in the NEXT round's first commit — they intentionally fall outside this round's audit.

If the user wants tighter coupling (reset done in the same commit), the `task-complete` skill itself can be extended to call the reset script as part of its workflow. That's a separate change to `task-complete` and out of scope here.
