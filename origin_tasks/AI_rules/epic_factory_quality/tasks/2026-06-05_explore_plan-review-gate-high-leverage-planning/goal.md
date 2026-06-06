---
task_id: TASK-PROC-044-18
type: explore
parent_requirement: REQ-PROC-044
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-05
expected_tool_calls: 30
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "must weigh planning-quality, agent-delegation economics, model-selection cost, and cross-skill applicability simultaneously"
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Design a generalizable plan-review gate: an independent review of high-leverage plans before execution"
release_description: ""
opus_recommended: true  # reason: explicit decision/trade-off task — synthesis across planning-quality, cost, and cross-skill design
writes_requirements: false
requirements_version:
  commit: c8899408
  file: ../../requirements.md
---

# Goal: Plan-Review Gate for High-Leverage Planning — a Generalizable Defense-in-Depth Pattern

## Objective

Can the factory catch a *flawed plan before it executes* — reliably, across every planning phase,
without paying for it on trivial work? We do not yet know the right *shape* of such a gate: who
reviews, against what, where the mechanism lives, when it fires, and how disagreement resolves.

This exploration must DESIGN that mechanism (a synthesis + recommendation), not implement it.

## Background

The factory plans work in many places — task-resolve's inline-vs-agent work split, architecture-advisor /
code-complex architectural planning, release planning, requ/ux planning phases. Planning errors are
*second-order*: a bad plan silently shapes all downstream execution, and unlike artifact I/O there is no
test that catches "this plan is wrong." Today nothing independently checks a plan before it runs.

The concrete trigger (TASK-PROC-069-03) and its two lessons are recorded in:
`plans_and_protocols/2026-06-05_00_user_initial_input.md` — **read it as a seed bed, not a spec.**

Why this lives under REQ-PROC-044 (Factory Quality): a flawed plan is the "silent failure / silent
corruption" risk that AC-01 (functional reliability — no silent failure) and AC-04 (robustness — visible
warning / graceful stop, never silent corruption) already guard against — here applied to the *planning*
sub-phase. REQ-PROC-044 governs the quality OF the factory machinery (its skills/scripts/process), which
is exactly what a planning-review gate protects.

For complete requirements at task creation time:
```
git show c8899408:requirements_tasks/process/AI_rules/epic_factory_quality/requirements.md
```

Current requirements: ../../requirements.md

## How to Approach This

Use design thinking — empathize with the failure mode before defining the fix, diverge across mechanism
shapes before converging, let the open questions lead. A single pass will not be enough. The most valuable
output is a clear recommendation the developer can ratify, plus an honest account of what stays uncertain.

## Seeds

- **Defense-in-depth, not a model crutch.** The trigger failure was a *missing rule*, now fixed (CLAUDE.md
  §2 Agent Delegation Economics, commit 588325cf), after which a plain Sonnet session planned correctly.
  Rules generalize; a stronger model on one run does not. What is the gate's honest marginal value *on top of*
  well-written rules — and when is "write the rule down" the better answer than "add a review"?
- **Favored direction = option (c): an independent plan-REVIEW gate.** A reviewer (separate from the planner)
  checks the plan before execution. Tension to resolve: it is model-agnostic about the planner, so it adds
  value *even when the session is already on Opus* — an independent reviewer catches what a planner cannot see
  in itself. Is that the decisive advantage it appears to be?
- **The two alternatives, and why (c) is preferred — verify or overturn:**
  - (a) task-create criterion → `opus_recommended: true` for non-trivial skill/CLAUDE.md tasks. Reuses the
    existing mechanism, but makes the WHOLE session Opus (paying Opus for mechanical edits too) and does
    nothing for in-flight planning.
  - (b) spawn an Opus PLANNING agent for the planning phase only. Cost-efficient, fits the delegation
    economics, but adds the most new machinery for the least-proven benefit — and does nothing for sessions
    already on Opus.
- **Generalization.** The pattern must apply to ALL planning work, not just task-resolve's work-split. Where
  must the gate live so it is reusable across planning skills (architecture-advisor, code-complex, release,
  requ/ux) — a shared mechanism, not duplicated per skill?
- **The trigger must be tight.** Fire only for HIGH-LEVERAGE / structurally non-trivial planning (authoring or
  restructuring a skill, changing governance/CLAUDE.md rules, multi-file/multi-skill or architectural change).
  NOT for trivial edits (a 1-line skill wording fix). What crisply *counts* as high-leverage, and how is it
  detected from goal.md / scope without a human judging each time?
- **Open design questions to resolve:** Who/what is the reviewer (a dedicated review agent? an existing agent
  like han-adversarial-validator? Opus by default for the review)? Where is the gate encoded (CLAUDE.md? a
  shared skill? a per-planning-skill reference to one central rule)? What does the reviewer check against (the
  Agent Delegation Economics ruleset + the task's goal/ACs + relevant `doc/` guidelines)? How does it interact
  with the existing `opus_recommended` / claude-route opus-check? How is disagreement handled (reviewer rejects
  → revise loop, with a cycle bound like the REQ-PROC-046 back-pressure protocol)?
- **Feature-or-invariant.** Should the result be a new feature under REQ-PROC-044 (`feat_plan_review_gate`)
  or an added cross-feature invariant (a 9th epic AC)? Decide and justify.

## Execution Model

Gather raw material — read the relevant planning skills, the CLAUDE.md §2 ruleset, REQ-PROC-044's invariants,
and the back-pressure protocol — then synthesize iteratively. The session's model is fixed at launch (Opus
here, `opus_recommended: true`); no mid-session switching.

**Web research** (if a seed needs external prior art — e.g. how other agentic systems gate or review plans):
delegate to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. The
subagent returns a distilled summary while raw content stays in its context.

## Output

A synthesis document in `plans_and_protocols/` that: states the problem space in terms sharper than this
goal; recommends a concrete gate design (favoring option (c) unless the analysis overturns it) with the
reviewer, encoding location, trigger definition, check-against set, and disagreement/cycle handling all
pinned down; compares (a)/(b)/(c) with an explicit rationale for the choice; says whether it becomes a
REQ-PROC-044 feature or a cross-feature invariant; and is honest about what remains uncertain. A future
implementer should be able to author the requirement and build the gate from it without replaying this session.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain
- [ ] The user has approved the final synthesis and stated what to do next
- [ ] The action stated by the user as the next step was performed successfully

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Defense-in-depth framing is load-bearing: the gate is belt-and-suspenders on top of good rules, NOT a
replacement for writing rules down. If the synthesis concludes a rule would do the job better than a gate
for some class of planning, say so.
