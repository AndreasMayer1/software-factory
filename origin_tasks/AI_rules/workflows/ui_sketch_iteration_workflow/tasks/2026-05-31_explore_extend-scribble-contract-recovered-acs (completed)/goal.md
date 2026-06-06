---
task_id: TASK-PROC-032-21
type: explore
parent_requirement: REQ-PROC-032
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-05-31
effort: M
created: 2026-05-31
started: 2026-05-31
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add AC-37..AC-41 to REQ-PROC-032 and amend AC-23 to encode the accidentally-lost scribble-contract strand from TASK-PROC-032-10 (storage mirror, per-flow navigation, per-flow walk validation, approval trail, contributing-requirements discovery, design_decisions propagation)."
release_description: ""
opus_recommended: true   # reason: explore task that writes cross-cutting requirements (scribble pipeline spans generator/iterate/review/handoff/verify + coder) — architectural judgment
writes_requirements: true
requirements_version:
  commit: 6886298f
  file: ../requirements.md
---

# Goal: Extend the scribble–coder contract with the recovered ACs (AC-37..AC-41 + AC-23 amend)

## Objective

The TASK-PROC-032-10 scribble-contract exploration adopted decisions that were never encoded as acceptance criteria — an accidentally-lost strand surfaced by the TASK-PROC-032-16 quality review. This exploration enters that space: what end-state must REQ-PROC-032 describe so that those decisions become verifiable, without re-opening already-decided design?

The open work is the precise end-state phrasing of five new ACs and one amendment, anchored to schema fields and skills that already exist:

- **AC-37** — scribble storage mirrors `lib/features/` (and `lib/core/` → `_core/`) 1:1; existing scribble migrated; parity check; consumers discover scribbles via the `feature_path` mirror. (recovers D33–36)
- **AC-38** — each participating flow has a `flow_navigation.yaml` (edges, triggers, escape paths, back-stack policy); emitted by `ui-scribble-handoff-emitter`; pointed to by `flutter_handoff.yaml`; consumed by `ui-verify-flutter` + coder. (D20)
- **AC-39** — before approval, `ui-scribble-auto-review` walks the scribble per participating flow in step order, verifies each step's intent; flow flaw routed upstream via the revision channel; brief carries one-line human walk instructions. (D39)
- **AC-40** — on approval, `APPROVAL_TRAIL.md` aggregates decision history across versions (rejected alternatives, trade-offs, rationale) from per-version feedback + auto-review briefs + diffs; emitted by `ui-scribble-approve-handoff`. (D43)
- **AC-41** — a script auto-discovers `contributing_requirements` (primary + cross-cutting) and `participating_flows` from `feature_path` + `requirements_matrix.md` + a UI-scope heuristic (NO new frontmatter — fields exist in `.claude/schemas/scribble_metadata.yaml`), populates `scribble_metadata.yaml`, flags ambiguities; a consistency lint requires the primary contributing requirement to match `feature_path`. (D29/D30/D40)
- **Amend AC-23** — `flutter_handoff.yaml` also carries a `design_decisions:` block (propagating scribble metadata `design_decisions` to the coder), validated by `.claude/schemas/flutter_handoff.yaml`. (recovers D8)

## Background

Why are we here? The scribble–coder contract (AC-21..AC-36) was encoded by TASK-PROC-032-10's follow-on work, but six decisions adopted in that exploration were never written down. The TASK-PROC-032-16 quality review found them and the remediation plan (§A1, §C1b) recovers them. The schema fields (`feature_path`, `contributing_requirements`, `participating_flows`, `design_decisions`) and the consuming skills (`ui-scribble-*`, `ui-verify-flutter`, `code-simple`/`-complex`) already exist — this is an encoding gap, not a new design.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-31_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 6886298f:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking — empathize before defining, diverge before converging, let questions lead. The structural decisions are already made (remediation plan §A1/§C1b); the open work is end-state phrasing that passes the requ-explore end-state and transition-language tests, anchored to the existing schemas and skills. Read the remediation plan and the existing AC-21..36 body prose first to keep voice and contract single-sourcing consistent.

## Seeds

1. **Single source of truth for the contract.** AC-21's "What a Scribble Commits To" is the single normative contract source. Where do AC-37..41 attach without restating that list — new body subsections, or extensions to Storage / Scribble–Coder Contract / Review Doctrine?
2. **Schema reuse.** `feature_path`, `contributing_requirements`, `participating_flows`, `design_decisions` already exist in `.claude/schemas/scribble_metadata.yaml`. AC-41 explicitly adds NO new frontmatter — how is "discovered, not hand-authored" phrased as an end state?
3. **`lib/features/` parity.** AC-37 asserts parity against a `lib/features/` structure policy that is itself underspecified. How is the parity check phrased so it does not over-commit to a policy that does not yet exist?
4. **Upstream routing.** AC-39's flow-flaw routing uses the existing revision channel (REQ-PROC-044 program). How is the routing phrased as an end state rather than a step?
5. **Handoff propagation.** AC-23 amend + AC-38 + AC-40 all touch `flutter_handoff.yaml` / handoff-emitter. Are they one coherent contract extension or independent blocks?

## Execution Model

Gather raw material, synthesize iteratively. The session's model is fixed at launch (Opus). Requirements authoring goes through `requ-explore` (this task `writes_requirements: true`).

**Web research**: not expected — this is an internal encoding task. If needed, delegate to a spawned `general-purpose` agent; never run WebSearch inline.

## Output

A future implementer can read REQ-PROC-032 and find AC-37..AC-41 in the frontmatter `trackable_items.acceptance_criteria` with matching body prose, and an amended AC-23 carrying the `design_decisions:` block — each phrased as a verifiable end state, anchored to the existing schemas/skills, with the AC-21 contract still the single normative source. The recovered strand is then derivable into impl tasks (S1–S5, C1b) by `task-derive-from-requ`.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] AC-37..AC-41 are added to REQ-PROC-032 (frontmatter + body prose) and AC-23 is amended with the `design_decisions:` block

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies — recovers an encoding gap; the existing schemas/skills already exist |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-16](../2026-05-31_explore_review-scribble-contract-explore-task/goal.md) | Origin — the quality review whose remediation plan (§A1, §C1b) seeded these recovered ACs |
