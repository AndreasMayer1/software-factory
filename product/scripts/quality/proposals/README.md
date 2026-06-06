# Quality-rule improvement proposals

This folder is the channel through which AI agents file proposed changes to
the project's quality gates without bypassing user review.

Why this exists: REQ-PROC-046 Developer Guidelines forbids AI from
autonomously editing the gate set (Goodhart's-Law protection). AI proposes
here; the user decides via the permanent loop-task
**TASK-PROC-046-16 — Apply quality-rule proposals loop** (located at
`requirements_tasks/process/AI_rules/coding_standards/code_quality/tasks/2026-05-14_impl_apply-quality-rule-proposals-loop/`).

## Categories

Pick the subfolder that matches the kind of change:

- `analysis_options/` — proposed changes to `analysis_options.yaml`
  (linter rules, severity, enabled/disabled lints, package overrides).
- `grep_gates/` — proposed changes to `scripts/quality/check_*.sh` or
  `check_*.py` gates (new pattern, relaxed pattern, additional exclusion).
- `thresholds/` — proposed tightening / loosening of numeric thresholds
  (complexity bounds, coverage %, cold-start ms, bundle size MB, etc.).
- `new_gates/` — entirely new gates not yet covered by any existing check.

Each category subfolder has its own `README.md` with more specific guidance.

## Filename pattern

```
<YYYY-MM-DD>_<short_slug>_<source_task_id>.md
```

Examples:
- `2026-05-19_reduce-cyclomatic-bound_TASK-PROC-046-22.md`
- `2026-05-19_add-arb-key-naming-gate_TASK-FUNC-014-03.md`

`<short_slug>` is kebab-case, descriptive enough to identify the proposal
in a directory listing.

## Required YAML frontmatter

```yaml
---
proposal_id: <slug>                  # matches the slug part of the filename
proposal_type: analysis_options | grep_gates | thresholds | new_gates
proposed_at: <YYYY-MM-DD>
proposed_by_model: <exact model identifier>
  # E.g. claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5-20251001.
  # This supports a future "archive proposals from older models" cleanup
  # without forcing that mechanism to be built today.
source_task: <TASK-ID where the AI noticed the opportunity>
status: pending_review               # set by the agent that files it
  # The loop-task changes this to `accepted`, `rejected`, or
  # `superseded` based on the answer.md decision.
---
```

`status` lifecycle:

| status              | meaning                                                                  |
|---------------------|--------------------------------------------------------------------------|
| `pending_review`    | filed by AI, awaiting user decision                                      |
| `accepted`          | user accepted; the loop-task has applied (or scheduled) the change       |
| `rejected`          | user rejected; loop-task records rationale in the body                   |
| `superseded`        | replaced by another proposal (referenced inline)                         |

## Required body sections

```markdown
## Reason
What the AI observed that prompted this proposal. Concrete evidence
(recurring false positive, missing rule, observed pattern). Cite source-task
findings or commit hashes if relevant.

## Proposed change
Exact mechanical change: file path, old line(s), new line(s), or a unified
diff. The user must be able to apply this without further investigation.

## Expected effects
What will start failing or passing. Which files / paths / requirements are
affected. Migration cost estimate.

## Alternatives considered
Other approaches the AI thought about and why they were rejected.
```

## How a proposal gets reviewed

1. AI files the proposal here with `status: pending_review`.
2. AI finishes its current task normally (it does NOT block on the proposal).
3. The user, when ready, opens
   `automation/pending_feedback/TASK-PROC-046-16/answer.md` and lists their
   decisions one entry per proposal (see that file's `question.md` for
   format).
4. The orchestrator picks up the non-template answer, resumes a session on
   the loop-task, and the session applies each accepted proposal:
   - edits `analysis_options.yaml` / `scripts/quality/check_*.sh` / the
     relevant requirement, as appropriate,
   - updates the proposal file's `status:` field,
   - commits,
   - runs `scripts/quality/reset_proposals_loop.py` to restore the
     pending_feedback folder for the next round.

## What NOT to do

- Do not edit `analysis_options.yaml`, `scripts/quality/check_*.sh`,
  or the requirement ACs that define gates autonomously. Always file a
  proposal first.
- Do not skip the `Alternatives considered` section. A proposal without
  alternatives signals shallow reasoning — the user will likely reject.
- Do not file overlapping proposals. Search existing
  `pending_review` files before writing a new one; if there is an
  overlap, supersede the older one (set its status to `superseded` and
  reference the new file).
