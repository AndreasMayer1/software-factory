---
name: claude-optimize-audit
description: Score the optimizer loop's effectiveness (deterministic, on-demand)
tools: Read, Bash, Edit, Write
model: sonnet
---

You score the `claude-optimize` loop's effectiveness using **deterministic**
inputs only: `runs.tsv`, `goal.md` `awaiting:` history, and `git log`. You
**never** judge with the LLM — your job is to invoke
`scripts/optimize/audit.py`, write the report, append `audit_history.tsv`, and
commit.

Authority: REQ-PROC-006 §"Effectiveness Metrics and Audit", §"Hard Constraints"
G-INV-3, AC-06/AC-11/AC-12. The canonical computation (two metrics + 10-point
rubric + delta) lives in `scripts/optimize/audit.py` — the criteria are a
script-owned constant so refinement is a normal edit.

## Metrics (definitions)

| Metric | Cadence | Source | Definition |
|---|---|---|---|
| **user-unblock-rate** (primary) | fast | `runs.tsv` + produced `goal.md` `awaiting:` history | fraction of optimizer-produced tasks the developer unblocked (target band 50–80%) |
| **revert-rate** (secondary) | slow (quarterly) | `git log` over completed optimizer-produced tasks | fraction reverted or substantially rewritten within N weeks (default N=8) |

Both metrics are computed by `audit.py` — never inline in this skill.

## Steps

### 1. Parse arguments

```bash
MONITOR_ARG=""    # empty → whole-rubric audit
for a in "$@"; do
  case "$a" in --monitor=*) MONITOR_ARG="$a" ;; esac
done
NOW_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DATE=$(date -u +%Y-%m-%d)
```

### 2. Invoke the deterministic scorer (AC-11, AC-12)

```bash
python3 scripts/optimize/audit.py \
  --runs-tsv .factory/optimize/history/runs.tsv \
  --audit-history .factory/optimize/history/audit_history.tsv \
  --report .factory/optimize/reports/${DATE}_audit.md \
  --tasks-root requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks \
  $MONITOR_ARG
```

The script:
- Computes user-unblock-rate and revert-rate.
- Evaluates each rubric criterion (10 starting criteria, script-owned).
- Computes the total score and `delta = score - previous_score` (0 on first run).
- Appends one line to `audit_history.tsv`:
  `<ts>\t<score>\t<delta>\t<unblock_rate>\t<revert_rate>\t<notes>`
- Writes the human-readable report to `.factory/optimize/reports/<date>_audit.md`
  with per-criterion breakdown and trend delta.

Exit codes:
- `0` → success. Continue to Step 3.
- `2` → no runs yet (empty `runs.tsv`). Halt with note "no runs to audit"; do
  not write history. Skip commit.
- `3` → invalid input (e.g. unknown monitor name). Halt; emit a
  `pending_feedback` question via the automated-mode procedure.

### 3. Commit (AC-06, N-D-6 commit audit reports)

Stage exactly:
- `.factory/optimize/history/audit_history.tsv`
- the new `.factory/optimize/reports/<date>_audit.md`

Invoke `claude-commit` with:
- type: `chore`
- scope: `optimize`
- subject: `audit <DATE>${MONITOR_ARG:+ (}${MONITOR_ARG#--monitor=}${MONITOR_ARG:+)} score=<score> Δ=<delta>`

Single commit per audit run.

## Sub-audits (--monitor=<name>)

`--monitor=<name>` scopes the rubric to events whose source monitor matches
`<name>` (one of `repeated_question`, `skill_change_reverted`,
`skill_changed_and_used`, `periodic`). The script subsets `runs.tsv` by
`dimension`/event-fingerprint join before scoring. Sub-audit reports are
written to `.factory/optimize/reports/<date>_audit_<name>.md`.

## Guardrails (do not weaken)

- **G-INV-3** — this skill is structurally separate from `claude-optimize`.
  The producer skill MUST NOT import, dispatch to, or execute this skill or
  its `audit.py` within the same run. The producer SKILL.md may name this
  skill only in its guardrail / G-INV-3 prose anchor (intentional). Verify
  absence of invocation:
  `grep -E 'Skill.*claude-optimize-audit|python3?.*audit\.py|bash.*audit\.py' .claude/skills/claude-optimize/SKILL.md`
  returns nothing.
- **No LLM scoring** (AC-12) — every criterion is computed in
  `scripts/optimize/audit.py` from `runs.tsv` + git history. This SKILL.md
  contains no rubric arithmetic.
- **Deterministic and reproducible** — given the same inputs, two runs
  produce the same score and delta.

## When to run

User-demand only — never on a trigger. Typical cadence: weekly for the
default rubric, quarterly for `--monitor=<name>` deep dives or when
`revert-rate` becomes meaningful (after ~8 weeks of completed tasks).
