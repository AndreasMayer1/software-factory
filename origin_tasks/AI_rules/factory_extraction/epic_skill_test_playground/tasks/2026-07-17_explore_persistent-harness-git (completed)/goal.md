---
task_id: TASK-PROC-068-28
type: explore
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-BLOCKING
impact: 3
impact_reason: I3-QUALITY
status: completed
completed: 2026-07-17
effort: S
created: 2026-07-17
expected_tool_calls: 20
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-11, AC-20, AC-21]
  sections: []
scope_description: "Author approved REQ-PROC-068 edits: AC-11 reword + new AC-20 (persistent harness git) + new AC-21 (encapsulation invariant)"
release_description: ""
opus_recommended: false
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: e0f9d317
  file: ../requirements.md
---

# Goal: Author REQ-PROC-068 edits for persistent harness git (AC-11 reword + AC-20 + AC-21)

## Objective

Author the approved REQ-PROC-068 edits (AC-11 reword + new AC-20 + new AC-21) that make the
maintenance-mode harness carry its own durable git across runs and keep that realism encapsulated in
the playground.

## Background

The design underlying this edit is already **decided and developer-approved** — this task applies a
closed, verbatim edit, not open exploration. The maintenance-mode (`build`/`maintain`) harness deploy
currently initializes a fresh `git init` on every run (see AC-13); this loses any commit reference a
prior run recorded (a materialization artifact's provenance commit, a task's pinned requirements
version) once that run's deployed copy is harvested and discarded. The approved fix carries the
harness's git history persistently across maintenance runs via a git bundle, restored on deploy and
persisted on harvest, with a compaction policy that preserves every referenced commit and squashes
only unreferenced intermediate ones. A companion encapsulation invariant (AC-21) keeps this realism
owned entirely by the playground deploy/harvest mechanism, so no other factory mechanism grows
harness-specific handling.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-07-17_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show e0f9d317:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

This task is the task-backed tail of a closed `requ-explore` on REQ-PROC-068. The design (persistent
harness git via git bundle; test mode keeps the throwaway `git init`) is already decided and signed
off, including the HIGH-consequence EGP disposition. Do NOT re-open the design, do NOT run ideation,
do NOT ask for approval — apply the verbatim edits below, regenerate, verify, and complete.

## Seeds

- The AC-11 reword: the harness must retain its own factory-runtime provenance (ideation index +
  ledger backing a derived decision) as project data, distinct from the transient deployed factory
  machinery that stays absent from `test_harness_app/`.
- The AC-20 body: persistent harness git — restore-on-deploy, persist-on-harvest, preserve-referenced
  compaction, test-mode excluded — EGP F, consequence HIGH.
- The AC-21 body: encapsulation invariant — the playground owns harness realism; no other factory
  mechanism special-cases the harness — EGP X, consequence MEDIUM.
- The backward-reference constraint: an artifact can't reference its own commit, so referenced commits
  must survive compaction with stable hashes — no global squash-and-rewrite.
- This supersedes earlier options (SHA-rewrite / content-hash approaches) considered during the closed
  exploration, and needs no REQ-PROC-074/075 provenance-contract change.

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize
iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The detailed how — model tier, web-research delegation, and phase mechanics — is owned by the routed
execution skill (`requ-explore`, or `task-resolve` → `ideation-start`), not duplicated here. For this
task specifically: the design is closed, so execution is direct verbatim application (Edit calls to
`requirements.md`, then regeneration scripts), not open-ended ideation.

## Output

`requirements.md` carries the reworded AC-11, the two new AC bodies (AC-20, AC-21) with their EGP
frontmatter dispositions, the aggregate `requirements.md` and `id_registry.md` are regenerated, and
`check_egp_audit.py` reports a clean disposition for REQ-PROC-068. A protocol file captures the
decided design (git bundle mechanism, compaction policy, encapsulation invariant, superseded options,
and the follow-on IMPL tasks to be derived later) so a future session picking up the implementation has
the full rationale without re-deriving it.

## Acceptance Criteria

- [x] AC-11 reworded to state the harness retains its own factory-runtime provenance as project data.
- [x] AC-20 added: persistent harness git (restore-on-deploy / persist-on-harvest / preserve-referenced compaction / test-mode excluded), EGP F/HIGH.
- [x] AC-21 added: encapsulation invariant (playground owns harness realism; no other mechanism special-cases the harness), EGP X/MEDIUM.
- [x] Aggregate requirements.md and id_registry regenerated; `check_egp_audit.py` reports no missing/empty dispositions on REQ-PROC-068.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Closed-design task: no ideation, no re-opened decisions. Applies verbatim edits pre-approved by the
developer, including the HIGH-consequence EGP disposition for AC-20.
