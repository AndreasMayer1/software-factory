---
task_id: TASK-PROC-068-20
type: explore
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-07-09
session_completed_at: 2026-07-09T13:13:07Z
effort: L
created: 2026-07-08
started: 2026-07-08
expected_tool_calls: 55
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold the deploy/isolation model (build.py), the derivation chain's file-memory resumability (feat_backfill/feat_fixpoint), and the shared-account usage-limit/session model together to design one coherent cross-session resume mechanism."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore + design a mechanism making a DEPLOYED build-mode layer-derivation run resumable across session termination / usage-limit hits (start-terminate-resume), via ideation; then update requirements and create impl tasks. Unblocks TASK-PROC-068-12."
release_description: ""
opus_recommended: true   # reason: synthesis that cannot be split — cross-session resume design spanning deploy wrapper + derivation chain + usage-limit model
writes_requirements: true
requirements_version:
  commit: 524a8867
  file: ../requirements.md
session_id: f9f98c5d-e1ce-4c6a-a3a5-dbbff842e229
session_account: gmail2
---
# Goal: Make the Deployed Build-Mode Derivation Run Resumable (Start → Terminate → Resume)

## Objective

The deployed build/maintain layer-derivation run is **single-shot and non-resumable**. When a run is
interrupted mid-derivation — a usage-limit hit, a hung/`session_timeout`, or any non-clean child exit —
the current wrapper still harvests a partial result and destroys the copy, losing all committed work.

What we do **not** yet know, and this exploration must discover:

- If the isolated deployed copy is normally discarded, **where does resumable state live** between a
  session that starts a run and a later session that resumes it? Preserve the copy keyed by a run
  handle? Persist ChainState + partial commits somewhere durable and re-deploy/re-seed from partial
  progress? A run registry the resuming session reads?
- **How does a later, cold session discover an in-progress deployed run and re-attach** to it — resuming
  autorun from ChainState — without a human threading paths by hand? Does `layer-derivation-resume` /
  `claude-autorun` extend cleanly to the deployed wrapper, or is a new handle needed?
- **What is the completion signal**, and how do we gate harvest + discard on it? On an incomplete exit
  the copy must be **preserved** and the harvest **skipped or marked partial** — never a partial deposit
  into the real `test_harness_app/`.
- **Usage-limit specifics**: the whole session tree shares one account/auth window (the `~/.claude`
  bind, AC-12), so a limit takes down every level at once. How is the limit detected, checkpointed
  cleanly, and resumed after the window resets? How does this compose with the factory's sequential-spawn
  philosophy (bound loss to the one in-flight unit)?
- How does all of this interact with the **"never git-reset, harvest-before-discard"** build-mode model
  and the snapshot-diff harvest-scoping already in `build.py`?

## Background

`scripts/playground/build.py::run_build_mode` launches ONE contained `claude -p` child session, then
unconditionally runs `record cost → harvest_authored → shutil.rmtree(copy)` with **no** check on
`LaunchResult.returncode` / `.succeeded` / `.reason` (`reason ∈ {exited, session_timeout, hung,
stop_requested}` is available but unused). The LOCAL derivation is already resumable — loop-state in
file-memory (`feat_fixpoint_loop` REQ-PROC-071-01 AC-02), commit-per-unit (`feat_backfill_orchestration`
REQ-PROC-071-06 AC-01), and `layer-derivation-resume` mints each next unit task. The DEPLOYED wrapper
discards that resumability because the copy is single-shot. TASK-PROC-068-18 proved AC-11's plumbing with
a cheap deterministic child that could not hit a usage limit, so the interrupted-mid-chain case has never
been exercised; TASK-PROC-068-12 (the first real harness middle-layer derivation) is the blocked consumer.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-07-08_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 524a8867:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

**Run this exploration through the structured ideation workflow — invoke `ideation-start`** (per the
developer's instruction). Let the five phases diverge on the resume-state-location and re-attach
questions before converging; the problem is a genuine open design space (where cross-session state lives,
how a cold session re-attaches, how completion is signalled), not a known fix. Empathize before defining,
diverge before converging, let the questions lead, iterate — one pass will not be enough. Surface the
non-obvious hazards (partial-harvest coherence, shared-account usage window, the discard-vs-preserve
decision, interaction with harvest-scoping).

## Seeds

- **Preserve vs. re-hydrate.** Is the resumable unit the *whole isolated copy* (preserved between
  sessions), or a *distilled state bundle* (ChainState + committed artifacts) that a fresh deploy
  re-hydrates? What does each cost, and which survives a machine reboot / `/tmp` eviction?
- **The run handle.** What is the minimal durable identifier a cold session needs to find and resume an
  in-progress deployed run — and where does the registry of live runs live (host side, since the copy may
  be gone)?
- **Completion as a first-class signal.** Today "done" is implicit (the child exited). What makes
  completion *explicit and trustworthy* enough to gate an irreversible harvest+discard — ChainState
  all-units-done? a fixpoint marker? a returncode contract from the child?
- **The usage-limit is not an error.** Reframe a usage-limit hit as a *planned pause*, not a failure. What
  would let the wrapper (or the child) checkpoint-and-exit cleanly on a limit, vs. discovering it only via
  a non-zero returncode after the fact?
- **Who owns resume — wrapper or chain?** `layer-derivation-resume` already resumes a LOCAL chain. Is the
  deployed resume just "re-launch the same copy and let autorun resume," or does the host-side wrapper
  need its own resume loop around repeated contained launches?
- **Partial harvest as a hazard, not a feature.** When is depositing partial artifacts ever acceptable,
  and when is it actively harmful (incoherent middle layers in `test_harness_app/`)? This tension likely
  shapes the whole design.
- **Boundary with what already exists.** How much of this is new mechanism vs. wiring `LaunchResult`
  fields + a preserve-on-incomplete branch into the existing `build.py`? Find the smallest change that
  closes the gap.

## Execution Model

Route via `ideation-start` (the structured ideation workflow the developer requested). Gather raw
material — read `build.py`, `launch_adapter.py`, the feat_backfill / feat_fixpoint requirements, the
068-18 AC-11 proof — and let ideation diverge/synthesize across rounds. Model tier, web-research
delegation, and phase mechanics are owned by the routed execution skill, not duplicated here.

Downstream of an approved synthesis, this task's own deliverables are: (2) requirement updates authored
via **`requ-explore`** into REQ-PROC-068 (build-mode ACs) and/or REQ-PROC-071-06
(`feat_backfill_orchestration`, "unattended across fresh sessions") — whichever the design lands on; and
(3) impl tasks created via **`task-derive-from-requ`** to build the mechanism.

## Output

A synthesis that defines the resume design in concrete-enough terms to author requirements from: where
cross-session state lives, how a later session re-attaches and resumes, the completion signal that gates
harvest+discard, and the usage-limit checkpoint/resume behaviour — honest about what stays uncertain
(e.g. usage-window detection reliability). The exploration is "done" only when the requirements are
updated and the impl tasks that build the mechanism exist, so a future session can implement it and
thereby unblock TASK-PROC-068-12.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round (via `ideation-start`)
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
      (state-location, re-attach, completion signal, usage-limit checkpoint)
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] The user has approved the final synthesis and stated what to do next
- [x] The action stated by the user as the next step was performed successfully — the requirement
      updates (via `requ-explore`) and the impl tasks (via `task-derive-from-requ`) that build the
      resume mechanism exist
- [x] TASK-PROC-068-12 is correctly unblocked: its `after:` is populated with the **impl-task IDs that
      build the mechanism** (NOT `TASK-PROC-068-20` itself — an explore completes when the impl tasks are
      created, not built), its "How to Approach" is re-authored to the build-mode/deployed-copy path, its
      `session_id` is left empty (fresh re-run), and its interim `awaiting` hold is cleared

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies (design exploration) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-12](../2026-07-01_impl_harness-middle-rederive/goal.md) | Blocked consumer this mechanism unblocks |
| [TASK-PROC-068-18](../2026-07-02_impl_playground-build-mode-harvest%20(completed)/goal.md) | Built the build-mode + harvest wrapper (AC-11) whose single-shot discard this addresses |
| [TASK-PROC-068-19](../2026-07-07_bugfix_build-mode-real-child-and-harvest-scope%20(completed)/goal.md) | Harvest-scoping (snapshot-diff) this design must compose with |

## Notes

- Coordinator-derived, covers-empty process task (no `target_package`) — surfaces via the override.
- `writes_requirements: true` keeps it on the critical path (it authors requirement updates via
  `requ-explore`).
- Sizing gate (`skill_chain_depth: 4`) satisfied by `opus_recommended: true`.
