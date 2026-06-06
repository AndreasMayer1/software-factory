---
skill: requ-explore
mode: automated
decision: ""
task_id: TASK-PROC-032-32
captured_at: 2026-06-06
---

# Question

---
task_id: TASK-PROC-032-32
session_id: 67771920-7253-4a95-8b15-547e7ff5208f
account: gmail
status: awaiting_answer
asked_at: 2026-06-05T00:00:00Z
skill: requ-explore
---

# Pending Question

## Task
TASK-PROC-032-32 — Author the Auto-Review Control Model (REQ-PROC-032)

## What was done

Authored the following ACs into REQ-PROC-032 (`requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`):

### Updated AC-31 (was: "Iteration-fatigue detection")
**New name:** Severity-driven iteration stop and non-convergence circuit-breaker
**New description:** A scribble is converged when the latest review round (auto or developer-provided) contains no finding with severity ≥ MEDIUM. If severity ≥ MEDIUM findings persist across a defined number of consecutive auto-review rounds without being resolved, ui-scribble-iterate escalates to requ-explore rather than continuing indefinitely. No version-count ceiling or complexity-score threshold applies — severity governs whether iteration continues.

### New AC-63: Sequential auto-reviewer execution
The auto-review phase runs each reviewer agent sequentially — one completes before the next starts. No parallel fan-out of reviewer agents occurs. At most one reviewer is in flight at any time, bounding the scope of a session-limit hit to a single incomplete agent rather than requiring all agents to restart.

### New AC-64: Gate-on-convergence default cadence
The default cadence for the human review gate is auto-to-converged: the gate fires only when the auto-review round finds no severity ≥ MEDIUM finding. Alternative cadence policies (every, after:[N], gate-at-v1) exist as named overrides configurable per invocation; the default is not overridden absent explicit configuration.

### New AC-65: Selective reviewer skip on low-severity rounds (PROP-7)
A reviewer whose previous round produced no severity ≥ MEDIUM finding is skip-eligible in the next auto-review round; its agent is omitted to reduce token cost. Skip-eligibility is overridden when developer feedback incorporated since the last run touches that reviewer's declared scope. The skip applies per-round, not permanently.

### New AC-66: question.md carries decision-asks only (PROP-6)
The Phase-3 developer-feedback gate emits a question.md that contains only the decision-asks for that round. Orientation content (what the scribble covers, what changed) lives in the scribble. The fix-recap (issues the auto-review resolved) is absent from question.md; it lives in auto_review_brief.md and the per-reviewer finding files.

### New Section SEC-20: Auto-Review Control Model
Body section added to requirements.md with full descriptive prose for all 5 properties.

### Body update (Scribble Review Doctrine)
The body reference to AC-31 was updated to match the new severity-driven model (was: "version threshold"; now: severity-driven).

## What remains uncertain

- The exact threshold (number of consecutive rounds) for the non-convergence circuit-breaker is deliberately left as "a defined number" — it's a tunable impl detail for T-C16, not a requirement.
- Whether "scope touched by new feedback" for the skip override (AC-65) needs a formal list of reviewer scopes or uses heuristic matching is left for T-C16 to decide.

## Question

Please review the ACs above. If you approve:

**Next step:** Run `task-derive-from-requ` on REQ-PROC-032 to generate T-C16 impl tasks for `ui-scribble-auto-review` and `ui-scribble-iterate`.

**After T-C16 tasks are created:** Append them to `.claude/task_ordering_priority_override.txt` (developer directive 2026-06-05 — they carry no `target_package` and won't surface in `next_tasks.py` otherwise).

If you want changes to any AC, specify them in answer.md and the session will resume.

# Developer Answer

approved.

---
## ⚠ STRUCTURE CHANGE — developer-authorized (2026-06-06)

REQ-PROC-032 was restructured into an EPIC + 7 child FEATURES (zero specification change; all AC/section
text migrated byte-exact and independently verified). The ACs you authored now live in feature **REQ-PROC-032-06** (`feat_carrier_and_auto_review/`). Your authored ACs AC-31→AC-01, AC-63..66→AC-09..12.

AUTHORING COMPLETE — your deliverable (auto-review control ACs) is done. Do NOT run task-derive-from-requ
on F06 yourself: F06 is fused (carrier + auto-review) and is derived ONCE by the dedicated task
**TASK-PROC-032-06-01** (derive-F06), gated after TASK-PROC-032-31 and this task.
CONTINUE against the FEATURE, not the epic (the epic is non-implementable).

DEVELOPER DIRECTIVE: every task you create via task-derive-from-requ MUST be appended to
`.claude/task_ordering_priority_override.txt` (process tasks carry no target_package and won't
surface in next_tasks.py otherwise).

Crosswalk + restructure record:
requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/tasks/2026-06-06_impl_restructure-req-proc-032-into-epic/plans_and_protocols/

# Rationale Captured

(Automated archival — no rationale extracted.)
