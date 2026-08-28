# 068-12 — spurious resume on 2026-08-01; re-parked via `awaiting[]`

Date: 2026-08-01 · automated session `05cae057` (gmail2)

## What happened

The session was resumed with "Your pending question has been answered", pointing at
`2026-08-01_08_feedback-checkpoint.md`. **No answer was actually given.** That archived record shows:

- frontmatter `decision: ""` (empty)
- `# Developer Answer` section = the verbatim `<!-- AWAITING_HUMAN_ANSWER -->` placeholder + the
  "do not write here" boilerplate
- `# Rationale Captured` = "(Automated archival — no rationale extracted.)"

`automation/pending_feedback/TASK-PROC-068-12/answer.md` on disk was likewise still the untouched
template. So the resume was **spurious** — the 2026-07-19 question (Phase-2 flow-approval gate,
options A–D) remains open and unanswered.

## Root cause — `is_awaiting_answer.py` marker guard vs. the new template frontmatter

`scripts/tasks/is_awaiting_answer.py::answer_is_empty` decides "template-only" like this:

```python
if stripped.startswith(TEMPLATE_MARKER):        # "<!-- AWAITING_HUMAN_ANSWER -->"
    if stripped == template_stripped:
        return True                              # awaiting
return False                                     # treated as ANSWERED
```

`TEMPLATE_answer.md` has since gained a YAML frontmatter block (uncommitted, `M`):

```yaml
---
provenance_declaration: 1
content_owner: factory
---
```

so the file now **begins with `---`, not the marker**. The `startswith` guard short-circuits before
the equality check runs, `answer_is_empty` returns `False`, the script exits 0 ("not awaiting"), and
the orchestrator resumes the task as though a human had answered.

Verified directly — a byte-identical copy of the *current* template is still mis-detected:

```
answer == template bytes : True
answer.startswith(MARKER): False      <-- guard fails here
=> answer_is_empty -> False -> exit 0 -> "not awaiting"
```

**Re-copying the template does NOT re-park a task.** This is why the usual `cp TEMPLATE_answer.md`
remedy was insufficient here.

### Blast radius (measured this session)

Every parked task whose `answer.md` exists is affected; only a task with *no* `answer.md` at all is
still detected correctly:

| Task | answer.md state | `is_awaiting_answer` exit | correct? |
|---|---|---|---|
| TASK-PROC-004-01-27 | template | 0 | ✗ spurious-resume risk |
| TASK-PROC-004-03-11 | template | 0 | ✗ |
| TASK-PROC-046-16 | template | 0 | ✗ |
| TASK-PROC-066-15 | template | 0 | ✗ |
| TASK-PROC-068-12 | template | 0 | ✗ |
| TASK-PROC-066-16 | *absent* | 1 | ✓ |

This matches the recent run of `chore(automation): re-park … — resume was spurious` /
`flag spurious phase-3 checkpoint archival` commits on this branch.

### Ownership — not fixed here (deliberately)

The template's frontmatter is the in-flight deliverable of **TASK-PROC-004-02-58** (`in_progress`,
"declare provenance on the answer file surface" — `provenance_declaration: 1`, `content_owner:
factory`). Reconciling `is_awaiting_answer.py` (and `orchestrate.py`'s twin `answer_is_empty`) with
the new answer-file surface belongs to that task's scope, not to 068-12. I did not edit the script
(out of scope; `scripts/**/*.py` edits also require `claude-write-script`) and did not revert another
task's uncommitted work.

**Suggested fix for 004-02-58**: strip YAML frontmatter before the marker test, or test
`TEMPLATE_MARKER in stripped` plus a frontmatter-insensitive body comparison — and apply the same
change to `orchestrate.py::answer_is_empty` so both detectors agree.

## Action taken — parked via `awaiting[]` instead of the pending_feedback channel

Because the pending_feedback detector cannot currently hold a park, 068-12 is parked at the **task**
level, which `next_tasks.py` honours independently:

- `status: blocked` (schema: valid only with non-empty `awaiting[]`)
- `awaiting: ["user-unblock"]`
- `awaiting_note:` points at the open question + the 07 blocker analysis

Verified: goal.md passes `validate_against_schema.py`, and `next_tasks.py` no longer surfaces the
task. `question.md` and the template `answer.md` are left in place, so the normal channel resumes
working the moment 004-02-58 lands its detector fix.

**To unblock**: answer the A–D question in `automation/pending_feedback/TASK-PROC-068-12/question.md`
(plus target bucket + budget), then clear `awaiting[]` and set `status: in_progress`.

## Task state unchanged otherwise

Phase 1 (flows) remains complete and harvested — FLOW-001 + FLOW-002 conformant in
`test_harness_app/`, `review_status: draft`. Phase 2 (requirements) not started. No derivation run was
launched this session; no budget spent; `test_harness_app/` product content untouched.
