# Cross-Reference Gap Candidates — REQ-PROC-032 (task-derive-from-requ Phase 1.5)

Detector: `scripts/requirements/check_cross_refs.py --terms scribble consistency staleness two-wave`
Target currently has `after: []`, `blocks: []`, and 2 Related Requirements entries (REQ-PROC-044, REQ-PROC-026).

## Relevant candidates (recommended classification)

| REQ-ID | Title / matched | Why it matters to the new consistency ACs | Recommended |
|--------|-----------------|-------------------------------------------|-------------|
| REQ-PROC-035 | release_preparation / two-wave orchestration (matched: consistency, scribble) | AC-42/AC-46 (SCI coding-block edges, cross-requirement cascade) reference the **two-wave model** authored under REQ-PROC-035 (T-A1 = TASK-PROC-035-21). Direct ordering dependency. | **hard** → `after` |
| REQ-PROC-058 | implementation_task_planning (matched: scribble, two-wave) | AC-18 there exposes `task-derive-from-requ --scope {presentation,code}` bisecting a requirement's decomposition — the mechanism that consumes AC-53 facet-tags. | **semantic** |
| REQ-PROC-069 | task_execution_entry (matched: scribble, staleness) | Same TASK-PROC-032-29 scribble-workflow redesign program; task-start/claude-route wrapping referenced by the SCI gate. | **semantic** |
| REQ-PROC-030-01 | requirements_pipeline_consistency (matched: consistency) | Consistency / conflict-prevention for `requ-derive-from-flow` + `requ-explore`, adjacent to the L3 coverage assertion (AC-48) and cascade. | **semantic** |

## Likely false positives (generic "consistency"/"scribble" mentions) — recommended `ignore`

REQ-FUNC-007-03, REQ-NFUNC-007, REQ-NFUNC-009, REQ-NFUNC-010, REQ-NFUNC-011, REQ-NFUNC-018,
REQ-PROC-006-04, REQ-PROC-008, REQ-PROC-011, REQ-PROC-036, REQ-PROC-040, REQ-PROC-042,
REQ-PROC-043, REQ-PROC-044-01, REQ-PROC-044-02, REQ-PROC-045, REQ-PROC-049, REQ-PROC-061,
REQ-PROC-062 — generic keyword hits, no load-bearing relationship to the consistency-spine ACs.

> Note: this classification only needs to be acted on **if** the derivation proceeds now (see the
> sequencing decision in question.md). REQ-PROC-035 (`hard`) is worth adding to the requirement's
> `after:` regardless, since the new SCI ACs depend on the two-wave model.
