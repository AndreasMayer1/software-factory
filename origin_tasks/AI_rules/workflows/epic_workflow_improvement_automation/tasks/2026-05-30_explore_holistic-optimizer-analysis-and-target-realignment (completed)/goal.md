---
task_id: TASK-PROC-006-20
type: explore
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
effort: XL
created: 2026-05-30
started: 2026-05-30
completed: 2026-06-01
session_completed_at: 2026-06-01T23:07:21Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Holistic analysis of the claude-optimize loop — implementation + design + target alignment — and a redesign proposal. Make the optimization targets explicit and verify the optimizer can actually move toward them (incl. running on itself)."
release_description: ""
opus_recommended: true   # reason: cross-cutting redesign + explicit trade-off/target decisions; holds a large multi-component model
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 645bf249
  file: ../requirements.md
session_id: b7511056-7384-471c-9739-2489bef37cca
session_account: web
---
# Goal: Holistic Optimizer Analysis & Target Re-alignment

## Objective

The `claude-optimize` self-improvement loop (REQ-PROC-006) has a first implementation.
We do not yet know whether it is **aimed at the right things**, nor whether it can
**actually move the factory toward them**. This exploration must answer, holistically:

- What should the optimizer optimize *toward*? Today it only measures `user-unblock-rate`
  and `revert-rate` — loop *process-health*, not the factory's real goals. The targets are
  under-specified.
- Is the current **design** sound, independent of bugs? (The 247-events-block-everything
  case is a missing-target symptom, not just a bug.)
- Can the optimizer **demonstrably improve** toward its targets — ideally by optimizing
  itself, more frequently now while it is young?

This is not a bug-patching task. It is a re-examination of the optimizer's purpose,
design, and efficacy. It supersedes the narrow "finish the bugfix" path.

## Background

A first implementation exists and was validated (TASK-PROC-006-06 validation report) —
structurally faithful to the rounds-1–4 concept but with 4 failures. Follow-up work
(TASK-PROC-006-18) fixed F-2 (deny-list case) and then revealed that F-1 (autonomous
trigger) is a **design** problem, not a bug. The developer stepped back and asked for a
complete analysis instead of more patching.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-30_00_user_initial_input.md`

Read it as a seed bed, not a spec. The orchestrator's approved analysis plan (the same
content, structured) is in `plans_and_protocols/2026-05-30_01_plan_analysis-scope.md`.

The original redesign exploration (model your method on it — multi-round Opus synthesis,
web research delegated) is at:
`../2026-05-01_explore_redesign-claude-optimize-skill (completed)/plans_and_protocols/`
(rounds 1–4 + `2026-05-16_07_decisions_applied.md`). **Check the implementation AND the
current REQ-PROC-006 requirements against those decisions, and re-open any decision the
real backlog has shown to be wrong** (e.g. queue domination).

F-1's first implementation is held in `git stash` ("F-1 autonomous optimize-cycle trigger
— HELD pending optimizer analysis") and documented in TASK-PROC-006-18's protocol — treat
it as a starting artifact for the redesign, not a settled answer.

For complete requirements at task creation time:
```
git show 645bf249:requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/requirements.md
```
Current requirements: ../requirements.md

## How to Approach This

Use design thinking — empathize before defining, diverge before converging, let questions
lead, iterate. One pass will not be enough. Surface surprises. Targets (Seed 1) frame
everything else, so enter there first. End by surfacing the value-laden decisions clearly
enough for the developer to choose (north-star, token budget, self-run aggressiveness).

## Seeds

1. **Targets & alignment (enter here first).** The north-star is **app quality** — but the
   app is produced through many factory stages, each emitting artifacts consumed downstream.
   "The end result must be good" is the right star but too distal to use as a metric
   directly. So: does each stage/skill need a **scope-local proxy metric that ladders up**
   to app-quality? What is the right structure (north-star + per-stage leading indicators +
   guardrails)? Two guardrails the developer named: a weekly **token-budget** constraint
   (limited plan → tokens = calendar weeks of delivery) and **meta-work subordination**
   (the optimizer must not starve product delivery). How are these made measurable and
   deterministic (G-INV-3)? Which become requirement-level vs tuning constants?

2. **Design critique & redesign.** Independent of bugs: one-event-per-cycle consumption
   (queue domination with a backlog); preempt-all surfacing vs subordinate/budget-rationed
   ranking; unbounded event accumulation (247 queued) and the monitor commit-window /
   cooldown / dedup-by-target tuning; whether per-event task production is the right unit;
   whether auto-block + manual-unblock is worth its token cost. Produce a concrete redesign
   aligned to Seed 1.

3. **Bug reconciliation.** Fold the validation failures (F-1 autonomous trigger; F-3 audit
   `--monitor` exit code; F-4 TASK-PROC-044 dependency gate — see TASK-PROC-006-19) plus the
   new findings — the `skills_used:` Stage-2 trigger gap (`task-complete` step 3.4b only
   fires on `*_protocol.md`, silently skipping other `plans_and_protocols/` filenames) and
   the event-explosion root cause — into the redesign. F-2 is already fixed; decide which
   remaining bugs survive the redesign, which are obviated.

4. **Efficacy & self-optimization.** Can the optimizer *measurably* improve toward Seed-1
   targets? Design a controlled experiment where the optimizer **runs on itself** (higher
   cadence now, while young), measured by `claude-optimize-audit` plus the new target
   metrics, with explicit success/failure criteria and a hard **token kill-switch** so the
   experiment cannot blow the weekly budget.

## Execution Model

Gather raw material — read the implementation (`scripts/optimize/`, the two skills,
`.factory/optimize/`), the requirements, the original concept, and the audit metrics —
then synthesize iteratively across multiple rounds. The session model is fixed at launch
(Opus, since `opus_recommended: true`).

**Web research**: delegate to a spawned `general-purpose` agent with a focused question;
never run WebSearch inline. Frame queries as questions (e.g. *"how do self-improving agent
loops define an objective function without letting meta-work starve primary work?"*,
*"how to choose leading-indicator proxy metrics that ladder up to a distal quality goal?"*).

**Token discipline (meta):** this analysis and the self-run both spend the same limited
weekly tokens they aim to protect. Bias toward cheap structural inspection; reserve agents
for synthesis and web research; the self-run experiment must carry the token kill-switch.

## Output

A synthesis in `plans_and_protocols/` that: (a) makes the optimization targets explicit and
measurable (north-star + scope-local proxies + token-budget & subordination guardrails),
with sources and deterministic computation; (b) gives a concrete redesign proposal
reconciled with the bug list; (c) defines the self-optimization experiment + token
kill-switch with success/failure criteria; (d) frames the value-laden decisions (north-star,
budget numbers, self-run aggressiveness) for the developer; (e) is honest about residual
uncertainty. The synthesis must be enough for `requ-explore` (to amend REQ-PROC-006 /
REQ-PROC-059 if targets become normative) and `task-derive-from-requ` to mint the redesign
tasks afterward.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space (esp. the targets) in terms that were not
      fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough to decide
- [x] The output is honest about what remains uncertain
- [x] The user approved the result and gave instructions about the next steps.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies (after: []). TASK-PROC-006-19 (F-4) feeds Seed 3 but does not block. |
