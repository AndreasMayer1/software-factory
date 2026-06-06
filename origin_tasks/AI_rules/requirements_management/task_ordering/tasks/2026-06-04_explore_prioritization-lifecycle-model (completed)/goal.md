---
task_id: TASK-PROC-042-13
type: explore
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-06-04
effort: S
created: 2026-06-04
started: 2026-06-04
expected_tool_calls: 10
skill_chain_depth: 2
writes_requirements: true
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
requirements_version:
  commit: 2c96e158
  file: ../requirements.md
---

# Goal: Document the Task Prioritization & Lifecycle Model in REQ-PROC-042

## Objective

Extend REQ-PROC-042 (Intelligent Task Ordering) with the cross-cutting *lifecycle
model* that governs why the ordering mechanism is shaped the way it is — so future
readers (and sessions) stop reverse-engineering it. The runtime behaviour is already
correct; what is missing is the written contract.

## Background

A long interactive investigation (2026-06-04) established the model. The complete,
self-contained synthesis lives at:
`../../implementation_task_planning/tasks/2026-06-04_impl_fix-claude-route-explore-routing/plans_and_protocols/2026-06-04_01_synthesis_routing-and-ordering.md`

Read it as the authoritative seed.

epic_task_lifecycle (REQ-PROC-065) explicitly delegates "task ordering and
prioritization" to REQ-PROC-042, so REQ-PROC-042 is the designated owner — this is an
extension, not a new requirement.

## What to Add (end state)

Two new documentation sections in REQ-PROC-042 body (mirroring the epic's
"Cross-Feature Invariants" non-AC pattern — no new trackable ACs, since these invariants
are already satisfied by existing code):

1. **Lifecycle Constraint & Release-Scoping Contract** — the author-before-assign
   constraint (requirement-authoring tasks structurally cannot carry
   `target_package`/`target_release`; assignment is deferred to `release-plan` after the
   requirement exists), the weak-chunk-priority-vs-strong-package split (chunk priority
   feeds only scheduling urgency, never release binding), and the ordering↔readiness
   interaction (the global `writes_requirements: -10000` priority is counterbalanced by
   `release_readiness.py` staging so far-future authoring never blocks a release).

2. **Rejected Alternatives** — (a) release-scoping authoring tasks: impossible by
   construction; (b) a new task type: rejected by TASK-PROC-034-18, `type` overloaded;
   (c) collapsing the `type`+`writes_requirements` dual signal: the only genuine
   accidental complexity, judged low-ROI. Plus the honest essential-vs-accidental framing.

Add a `## Related Requirements` cross-ref to REQ-PROC-034 / REQ-PROC-058 / REQ-PROC-041 /
REQ-PROC-065.

## Acceptance Criteria

- [x] REQ-PROC-042 documents the lifecycle constraint and the chunk-vs-package split.
- [x] REQ-PROC-042 documents the ordering↔staging interaction (why far-future authoring does not block a release).
- [x] REQ-PROC-042 has a Rejected Alternatives section covering the three rejected options + essential-vs-accidental framing.
- [x] Related Requirements cross-references REQ-PROC-034/058/041/065.
- [x] No duplication: mechanisms owned by REQ-PROC-034 are referenced, not restated.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
