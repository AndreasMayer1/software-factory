---
task_id: TASK-PROC-032-30
type: explore
parent_requirement: REQ-PROC-032-05
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-06-05
completed: 2026-06-06
session_completed_at: 2026-06-06T12:10:27Z
effort: XL
created: 2026-06-05
expected_tool_calls: 50
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "The consistency layer (SCI invariant, the 5-edge rot-graph, loopback taxonomy, lazy-wavefront cascade + width breaker, entry-context spine, coverage/ordering, domain→design + facet-tagging) is one tightly-coupled model — SCI edges reference the cascade and the coverage assertion references the facet tags; splitting loses the invariant's coherence."
after: [TASK-PROC-035-21]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Author the REQ-PROC-032 ACs for the consistency & scribble-layer model: the Scribble-Currency Invariant + audit, the five-edge staleness rot-graph, loopback-as-task (L1–L6), the lazy-wavefront cross-requirement cascade + two-stage width breaker, the L3 coverage assertion, the entry-context spine (PROP-8) incl. container dimension, coverage/ordering (PROP-9/11), the domain→design conditional edge, and AC facet-tagging."
release_description: ""
opus_recommended: true   # reason: large non-splittable synthesis — the consistency invariant couples SCI, cascade, coverage, entry-context and facet-tagging; must be held at once
writes_requirements: true
requirements_version:
  commit: d29b49c9
  file: ../requirements.md
session_id: dc27d645-874a-4cd6-b6ac-8852c1dabf72
session_account: gmail
---
# Goal: Author the Scribble Consistency & Layer Model (REQ-PROC-032)

## Objective

Author the REQ-PROC-032 ACs (via `requ-explore`) for the **consistency spine** of the redesign — manifest
task **T-A2**. What must become ACs:
- The **Scribble-Currency Invariant (SCI)** + the standing **SCI audit** (no coding task runnable against a
  missing/unapproved/stale scribble), and the **five-edge staleness rot-graph** (requirement→scribble;
  scribble→coding; domain-code→data-bound-scribble; scribble→dependent-scribble; scribble→verify-verdict),
  each with its detector.
- **Loopback-as-task** taxonomy L1–L6 (normative-upstream edits spawn NEW tasks; un-approved scribble loopback
  = same task, new version).
- The **lazy-wavefront cross-requirement cascade** (P-F) + the **two-stage width breaker** (soft N1=3 / hard
  N2=7, escalate at N2; values tunable).
- The **L3 coverage assertion** (no-recursion source-check is safe iff every Presentation requirement has a
  scribble/source-check) + the **L3 chain-length alert**.
- The **entry-context spine (PROP-8)**: emit + reviewer check + bounded reconciliation; container **dimension**
  visibility.
- **Coverage/ordering (PROP-9/11 R1–R4 + guards G1–G4)** — note R4 (the app-shell/launch-map requirement +
  two-tier seam detection) is authored here as a constraint even though the skill change lands in T-C17.
- The **domain→design conditional edge** + **data-bound detector** + **AC facet-tagging** ({presentation |
  behaviour | both}).

## Background

S2 stage of the redesign (TASK-PROC-032-29). Substrate (authoritative — the design is settled) is a sibling
under this very `tasks/` folder:
`../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/plans_and_protocols/`
— esp. `2026-06-04_02_round_1_synthesis.md` (§1,§3,§4,§5), `2026-06-05_11_synthesis_resolve-open-questions.md`
(B3/B5/B6/C1–C4/C6), `2026-06-05_12_contingency_branch-plans.md` (soft-SCI mode question), and
`2026-06-05_13_implementation-task-manifest.md` (row T-A2). The eval substrate (PROP-8/9/10/11/12, F8–F16) is
in the sibling `2026-06-04_explore_eval-scribble-workflow-live-iteration (completed)/plans_and_protocols/`.

Current requirements: ../requirements.md (REQ-PROC-032).

## How to Approach This

The design is decided; author ACs, don't re-derive. Two **authoring decisions** (`14`§7) must be made here and
flagged for the developer: (a) whether soft-SCI is an explicit configurable-but-sign-off-gated mode or a
documented pivot only (recommendation: mode, default OFF); (b) whether the `12`§0.6 thresholds are baked into
validation ACs (recommendation: into T-CV's acceptance). Watch the doc-lookup budget — if capped, split this
task rather than thinning the synthesis.

## Seeds

1. SCI as a continuously-enforced invariant vs a one-time gate — how to phrase the AC so both t=start and
   t=mid-release are covered by one rule?
2. The generative-blocks / referential-flags discriminator — which readers block, which flag?
3. Facet-tagging accuracy is empirical — how should the AC hedge (auto-tag + human confirm; fail-safe to
   `presentation` on ambiguity)?
4. The width-breaker thresholds are unmeasured — phrase as configurable with measured-on-fixture defaults.

## Execution Model

`requ-explore` on REQ-PROC-032. This is XL — run as a background agent (+ 4:30 heartbeat per the
long-running-agent rule); it will exceed the 5-file/30 KB threshold. If `doc-lookup-dependencies` returns
BUDGET_CAPPED, route to the developer (raise budget / split).

**Task-ordering (developer directive 2026-06-05):** every task this task creates (the impl tasks
`task-derive-from-requ` derives from these requirements) MUST be appended to
`.claude/task_ordering_priority_override.txt` — they carry no `target_package`, so they will not surface in
`next_tasks.py` otherwise.

## Output

REQ-PROC-032 carries ACs sufficient for `task-derive-from-requ` to generate the consistency-layer impl tasks
(manifest T-C8…C14, C17). The two authoring decisions (soft-SCI mode; thresholds-as-ACs) are surfaced.

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
| TASK-PROC-035-21 | pending | T-A1 — SCI's coding-block edges reference the two-wave model authored there. |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-29](../2026-06-04_explore_redesign-implementation-workflow-scribble-gate/goal.md) | Source — the redesign synthesis + manifest this task authors into ACs. |
| [TASK-PROC-035-21](../../../requirements_management/release_preparation/tasks/2026-06-05_explore_author-two-wave-orchestration-spine/goal.md) | Predecessor — the two-wave spine SCI edges depend on. |
