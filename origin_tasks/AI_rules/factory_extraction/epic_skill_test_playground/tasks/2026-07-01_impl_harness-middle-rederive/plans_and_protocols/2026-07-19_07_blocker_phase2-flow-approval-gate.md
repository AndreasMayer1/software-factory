# 068-12 — Phase 2 (requirements) blocked on flow-approval gate

Date: 2026-07-19 · automated session `05cae057` (gmail2)

## Phase 1 verified complete (carried from session `df7046c8`)

- Run `274b7ad8` registry: `status: complete`, `outcome: complete`, `harvested_count: 6`.
- Confirmed on disk: `test_harness_app/requirements_user_needs/user_flows/detailed_entry_after_movie/flow.md`
  (FLOW-001, `review_status: draft`) and `.../quick_rating_after_movie/flow.md` (FLOW-002,
  `review_status: draft`), plus `FLOW_INDEX.md`. AC-1 mechanically satisfied (README_5-conformant,
  authored via the real chain + `ux-create-flow`).

## Phase 2 blocked before launch — pre-flight gate, not a run failure

`flow_requirement` derivation's registered authoring skill is the combo
`requ-derive-from-flow+requ-explore` (`backfill_orchestration.py:832`). `requ-derive-from-flow`'s
own **Pre-flight: Primary Flow Approval Guard** hard-blocks: "For each flow ID given, find its
`Status:` line in FLOW_INDEX... If any flow is NOT `approved`, block immediately." Both FLOW-001 and
FLOW-002 are `draft` — nowhere near `approved`.

Reaching `approved` requires, per `ux-create-flow`'s state machine: `draft → in_review` (CONTINUE
pass) → `content complete` (via `ux-flow-complete`) → `approved` (direct, if no sibling impacts) or
`aligned` → joint approval. `ux-flow-complete`'s Fit-Score walk is explicitly rater-gated: "the USER
rates the walk/Fit-Score questions... recommend running user research when persona/scenario-distilled
data can't answer the walk/Fit-Score questions" (`ux-create-flow/SKILL.md`). This is a literal
human-rating step, not a mechanical check I can pass through autonomously.

This is also not a new concern — the 2026-07-10 blocker (`2026-07-10_03_blocker_requirement-layer-run-preconditions.md`)
already flagged it as open item **B**: "Confirm the DRAFT flow artifacts pass developer quality
review (071-06-08/071-06-09 gate: 'Developer reviews the harvested flow artifacts for quality before
TASK-PROC-068-12 is accepted')." Checked `automation/pending_feedback/` and
`scripts/decisions/query_decisions.py --keyword "068-12"` — no prior answer/decision capsule exists.
Item A (068-23 build-resume fix) is now resolved (all `after:` predecessors completed); B and C remain
open.

## Why I did not resolve this myself

Two distinct human-gated steps sit between "draft flows exist" and "Phase 2 can run":
1. Whether the harvested DRAFT flows pass developer quality review at all (071-06-08 decision, scoped
   to accepting 068-12).
2. Whether flow *approval* (`review_status: approved`, including the human-rated Fit-Score walk) is a
   real prerequisite here, or whether — since this is synthetic test-harness content used to exercise
   the derivation mechanism itself, not real product content — the developer wants a different path:
   e.g. self-rate the walk as the LLM operator, or bypass `requ-derive-from-flow`'s gate-analysis phase
   and drive `requ-explore` directly for `flow_requirement` (deviating from the registered
   `AUTHORING_SKILL_BY_PAIR` combo, with the same non-conformance risk 068-12 exists to correct for
   068-07's original failure).

Guessing either way risks: (a) silently pushing draft harness content through a rating gate meant for
real product decisions, or (b) reproducing the exact non-conformant-shortcut failure mode 068-12 was
created to fix. Escalating per automated-mode "When Human Input Is Genuinely Needed."

## Task state

`status: in_progress`, `awaiting: []` (about to be set), no code/lib/test files touched this session —
only this protocol file + the pending_feedback question.
