---
task_id: TASK-PROC-006-03
type: explore
parent_requirement: REQ-PROC-006
urgency: 4
urgency_reason: U4-DEP
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-28
completed: 2026-05-28
session_completed_at: 2026-05-27T23:30:29Z
effort: L
created: 2026-05-27
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02]
scope_description: "Codify the decided claude-optimize redesign (4 synthesis rounds) into requirements: rewrite REQ-PROC-006 and create a new cross-factory LLM-work-principles requirement, via requ-explore."
release_description: ""
opus_recommended: true   # reason: requirements authoring across two requirements; must faithfully encode a large, already-decided design with non-obvious guardrails
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
session_id: d8b84f53-26bb-4224-bf11-e69af5bc29ed
session_account: gmail
---
# Goal: Write the Requirements for the Redesigned claude-optimize Skill

## Objective

The design exploration for the `claude-optimize` redesign is **complete and
user-approved** (TASK-PROC-006-02, four synthesis rounds). This task does **not
re-explore** — it codifies the decided design into requirements using the
`requ-explore` skill.

Two requirements must result:

1. **Rewrite REQ-PROC-006** (currently a stub marked `status: implemented` that
   "does almost nothing meaningful") to specify the redesigned claude-optimize
   skill as decided.
2. **Create a new cross-factory LLM-work-principles requirement** (round-4 IMPL-K)
   — proposed location `requirements_tasks/process/AI_rules/llm_work_principles/`.
   This captures factory-wide principles (a–h) that apply beyond claude-optimize.

## MANDATORY READING — the concept (read before any work)

The full, decided concept lives in the sibling explore task's
`plans_and_protocols/`:
`requirements_tasks/process/AI_rules/workflows/workflow_improvement_automation/tasks/2026-05-01_explore_redesign-claude-optimize-skill/plans_and_protocols/`

- `2026-05-16_08_opus_synthesis_round4.md` — **the consolidated final design. Start here.**
- `2026-05-16_05_opus_synthesis_round3.md` — detailed architecture (monitors, events, `.factory/optimize/`, auto-block, two-stage detection)
- `2026-05-16_07_decisions_applied.md` — every user decision (R1–R6, N-D-1–N-D-6) with rationale
- `2026-05-07_01_opus_synthesis.md` + `2026-05-07_03_opus_synthesis_round2.md` — rounds 1–2 (reframe, prior art) for background
- `2026-05-16_06_web_research_round2.md` + `2026-05-07_02_web_research_external_knowledge.md` — external evidence

**You must understand the whole concept before writing requirements.** The design
has non-obvious guardrails (G-INV-1/2/3) and deliberate non-goals that must survive
into the requirement verbatim in intent.

## What REQ-PROC-006 must say (from round-1 §16 + round-2 §E + rounds 3–4)

The rewritten REQ-PROC-006 should specify that the system shall:
- produce **one** improvement task per run (task-producer, not analyzer), or a no-op
- consume cheap structural signals via **monitor scripts** that run after every
  `task-complete`; never read session JSONL in routine operation
- store all state project-locally under **`.factory/optimize/`** (NOT OS memory —
  three Claude accounts do not share memory); `runs.tsv` is the canonical record
- emit candidate **events** to `.factory/optimize/events/` (consume-then-delete)
- prefer **bugfix** candidates strictly over optimization candidates (no fairness rule)
- **auto-block** every produced task with `awaiting: ["user-unblock"]` — permanent default
- declare a **verifiable acceptance criterion** on every produced task (ground-truth
  or structural rubric; never single-LLM judgment)
- use the two-field `optimization_target` / `optimization_dimension` taxonomy
- recommend web research per produced task via the round-3 §2.3 heuristics table, and
  log every performed search to `.factory/optimize/history/web_searches.tsv`
- detect saturation and exit cleanly (no memory entry; `runs.tsv` only)
- always **commit** each run (even no-ops) so the audit skill can read git history

It must encode the three **non-removable self-improvement guardrails** as hard
constraints (round-4 Part 3):
- **G-INV-1** produced tasks are auto-blocked
- **G-INV-2** detection runs outside any agent's tool surface
- **G-INV-3** the scoring/audit skill is separate from the producer skill

Plus the round-3 §1.3 / D9 **write-surface deny-list** as defense-in-depth, and the
**two effectiveness metrics** (user-unblock-rate + revert-rate, round-4 Part 4), and
the separate **`claude-optimize-audit`** skill with a deterministic scoring rubric
(round-4 Part 2.1).

The current REQ-PROC-006 should be marked superseded/replaced as appropriate; reuse
the same ID with new content (it stays REQ-PROC-006).

## What the new principles requirement must say (round-4 Part 5)

Principles a–h, factory-wide, with sources, including the **irreversibility
threshold** for principle (c) (promote a prompt rule to a hook only if violating it
is unrecoverable). Scope it TIGHTLY: state the principles + the threshold; do NOT
re-audit existing skills in this task (that is what claude-optimize is for, later).

## How to Approach This

Invoke `requ-explore` for the requirements authoring. This is a codification task,
not an exploration — the answers are decided. Do not reopen settled decisions; if a
genuine ambiguity surfaces, route a `pending_feedback` question rather than guessing.

## Acceptance Criteria

- [x] REQ-PROC-006 rewritten to specify the redesigned claude-optimize per the concept; trackable ACs added covering producer behavior, signals, `.factory/optimize/` state, auto-block, bugfix-first, saturation, commit-always
- [x] G-INV-1/2/3 present as hard constraints (not goals)
- [x] Write-surface deny-list, two-metric model, and `claude-optimize-audit` skill referenced in the requirement
- [x] New cross-factory LLM-work-principles requirement created (principles a–h + irreversibility threshold), tightly scoped
- [x] Both requirements have proper `id:`, trackable_items, and pass the requirements lint/coverage scripts
- [x] `requirements.md` regenerated where applicable; id_registry updated
- [x] No settled decision from rounds 1–4 silently reversed

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-006-02 | completed | The exploration that produced the concept |

## Notes

This task is step 1 of the user-directed close-out plan for TASK-PROC-006-02.
Downstream: TASK-PROC-006-04 and -05 (derive impl tasks) wait on this task;
TASK-PROC-006-06 validates the end result against this same concept.
