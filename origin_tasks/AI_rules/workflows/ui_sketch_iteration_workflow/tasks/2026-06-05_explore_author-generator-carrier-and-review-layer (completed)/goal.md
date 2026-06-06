---
task_id: TASK-PROC-032-31
type: explore
parent_requirement: REQ-PROC-032-06
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUALITY
status: completed
effort: L
created: 2026-06-05
started: 2026-06-05
completed: 2026-06-06
session_completed_at: 2026-06-06T11:29:53Z
expected_tool_calls: 30
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "The carrier-format change and the human review layer share one locus (how reviewer detail is carried in the artifact) — the comment-nesting leak fix, PROP-1, the findings overlay, PROP-3/4/5 must be designed together as one artifact contract."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Author the REQ-PROC-032 ACs for the scribble-artifact carrier format & human review layer: replace the nested-HTML-comment carrier with a flat JSON <script> carrier (fixes the comment-nesting render leak), PROP-1 human review layer, PROP-13C findings overlay, PROP-4 per-reviewer persistence, PROP-3 reusable review-guide component, PROP-5 script-generated small-multiples state variants."
release_description: ""
opus_recommended: true   # reason: design of a dual-audience artifact contract (machine + human) sharing one carrier locus
writes_requirements: true
requirements_version:
  commit: d29b49c9
  file: ../requirements.md
session_id: 3faa5909-94d8-469a-8ef0-ec85c62cf326
session_account: web
---
# Goal: Author the Generator Carrier-Format & Review-Layer Requirement (REQ-PROC-032)

## Objective

Author the REQ-PROC-032 ACs (via `requ-explore`) for **how reviewer/coder detail is carried in the scribble
artifact** — manifest task **T-A3**. One coherent contract because all of these share the same locus:
- Replace the nested `<!-- … -->` carrier (which leaks into the render because HTML comments cannot nest) with
  a flat, un-nestable **`<script type="application/json">` carrier** — fixes the concrete leak AND makes it
  structurally impossible.
- **PROP-1** visible human-facing review layer (separate from the terse machine block).
- **PROP-13C** script-rendered findings overlay (count badge + element markers + gate prompt).
- **PROP-4** persist per-reviewer findings.
- **PROP-3** reusable, non-regenerated review-guide component in `_scribble_components/`.
- **PROP-5** script-generated small-multiples state variants (no full-copy drift).

The *requirement* is authored here; the agent/script changes that implement it are manifest T-C15 (the
generator is an **agent** — `claude-modify-agent` + its `.contract.yaml`).

## Background

S3 stage of the redesign (TASK-PROC-032-29). Substrate (sibling under this `tasks/`):
`../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/plans_and_protocols/2026-06-04_02_round_1_synthesis.md` §7
(the carrier-format fix) and `2026-06-05_13_implementation-task-manifest.md` (row T-A3). The eval substrate
(R2§1 comment-leak; PROP-1/3/4/5/13C) is in the sibling
`2026-06-04_explore_eval-scribble-workflow-live-iteration (completed)/plans_and_protocols/`.

Read as authoritative substrate.

Current requirements: ../requirements.md (REQ-PROC-032).

## How to Approach This

Author ACs for the dual-audience artifact contract via `requ-explore`. Disjoint from T-A2's REQ-PROC-032
sections (consistency) — can run in parallel; shares only the small REQ-PROC-032 base read.

## Seeds

1. One carrier, two audiences — what JSON schema serves both the overlay script and the coder/LLM?
2. The review-guide component (PROP-3) — what is reusable-once vs per-screen?
3. Small-multiples (PROP-5) — can a script generate state variants without losing per-state semantics?

## Execution Model

`requ-explore` on REQ-PROC-032 (artifact-contract sections). Background agent if the context-window rule trips.

**Task-ordering (developer directive 2026-06-05):** every task this task creates (the impl tasks
`task-derive-from-requ` derives) MUST be appended to `.claude/task_ordering_priority_override.txt` — they carry
no `target_package`, so they will not surface in `next_tasks.py` otherwise.

## Output

REQ-PROC-032 carries ACs sufficient for `task-derive-from-requ` to generate T-C15 (generator agent +
contract + overlay script). The comment-nesting leak is fixed at the contract level (un-nestable carrier).

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] The user has approved the final synthesis and stated what to do next
- [x] The action stated by the user as the next step was performed successfully

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Independent — disjoint REQ-PROC-032 sections from T-A2; may run in parallel. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — redesign synthesis (§7 carrier fix) + manifest row T-A3. |
