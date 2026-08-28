---
task_id: TASK-PROC-068-01
type: explore
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-06-11
started: 2026-06-11
completed: 2026-06-26
expected_tool_calls: 30
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-04]
  sections: []
scope_description: "Design how the Skill-Test Playground tests OPEN-ENDED skills (no single correct output, e.g. the ideation workflow) with an LLM-verifiable outcome rubric — refining REQ-PROC-068 AC-04 for the no-golden-answer case."
release_description: ""
opus_recommended: true  # reason: explicit decision/design task — defines an evaluation methodology (rubric + judge + golden-trace) that must be coherent across skills; synthesis that cannot be split
writes_requirements: true
requirements_version:
  commit: 47852849
  file: ../requirements.md
session_id: ecaffbbb-79f4-4959-81fe-53557d7bdd95
session_account: gmail2
---
# Goal: Define an LLM-verifiable test for open-ended skills

## Objective

How do we test a skill whose output is *open-ended* — where there is no single correct
result to assert against? The Skill-Test Playground (REQ-PROC-068) gives the factory a real
app to run skills on, and its **AC-04** already mandates a *non-boolean quality-scale outcome
rubric*. But the rubric's shape for the hard case is not yet defined: the new **ideation
workflow** is the canonical example — two correct runs on the same topic can legitimately
produce very different ledgers, so output-equality is meaningless.

This exploration should discover:

- **What can actually be asserted about an open-ended skill** without asserting on content
  correctness? Candidate framing to test and refine: assert on **process and the artifact's
  internal consistency**, not on whether the produced idea/answer is "right".
- **Which quality dimensions are invariant across topics** for a given open-ended skill, such
  that an LLM judge can score them with anchored 1–5 descriptions? (For ideation, candidates:
  coverage of declared frames/scope-dims, non-redundancy of divergent ideas, criteria
  soundness/weight justification, synthesis fidelity — does the viable set trace to
  high-scoring ideas — and gate honesty — does the mid-run summary faithfully represent the
  ledger?)
- **What is deterministically checkable vs. what genuinely needs an LLM judge?** Many
  structural invariants (artifact present, frame×technique counts, post-check PASS, criteria
  panel present, gate written) need no LLM at all. Draw the line cleanly so the LLM is used
  only where judgment is irreducible.
- **How to make the test robust and regression-catching without a golden answer** — e.g. a
  frozen **golden-trace** reference run (ledger + gate) for a fixed topic+seed, with an LLM
  judge comparing new-vs-reference ("at least as good, and did the intended improvement
  appear?") instead of asserting equality.
- **How the human-in-the-loop gate is tested.** Part of an open-ended skill's value is the
  gate itself. Can an LLM play a developer persona walking the gate and score the *quality of
  the interaction* (did the gate surface enough to decide well?) — bridging to the sibling
  interactive-required work (TASK-PROC-069-05)?
- **How this feeds the six probes** (feat_measurement_instrumentation, REQ-PROC-068-05) and
  the `run_instructions` + outcome-rubric format AC-04 already requires. Is a new
  sub-requirement needed, or is this a refinement of AC-04 in place?
- **Generality**: is the rubric+judge+golden-trace pattern reusable for *other* open-ended
  skills (requ-explore, product-intake), or ideation-specific?

## Background

The playground (REQ-PROC-068) makes iterating factory workflows cheap by running them on a
small real app instead of a full release. That works naturally for skills with a knowable
expected result. Open-ended skills break the assumption: the new ideation workflow can
produce many valid, divergent outputs for one topic. The two ideation test runs captured at
task-creation time (TASK-PROC-066-05/-06) illustrate this — both reached their mid-run gate
correctly, yet neither has a "correct ledger" to diff against.

This task is the natural refinement of **AC-04**, which already commits the harness to a
non-boolean quality-scale rubric fed by the six probes; it does not introduce a competing
mechanism.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-11_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 47852849:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking — empathize before defining, diverge before converging, let questions
lead, iterate. Ground every proposed rubric dimension in a concrete failure it would catch on
a real ideation run (use TASK-PROC-066-05/-06 ledgers as live material). Be suspicious of any
criterion that secretly asserts content correctness.

## Seeds

- **The "no golden answer" wall.** Take the two existing ideation ledgers (066-05: 114 ideas /
  6 frames; 066-06: 60 ideas / 6 frames) and ask: what could a test legitimately *fail* them
  for, given both are valid? Whatever survives is a real invariant.
- **Deterministic vs. judged.** Inventory what ideation already self-checks deterministically
  (post-check PASS, frame×technique coverage). The LLM judge should start where those stop.
- **Anchored rubric levels.** A 1–5 scale is only LLM-verifiable if each level has a concrete
  anchor. Draft anchors for one dimension (e.g. non-redundancy) and pressure-test
  inter-judge stability.
- **Golden-trace regression.** What exactly is frozen (topic, seed, model?), and how does a
  judge express "at least as good + intended improvement present" without equality?
- **Gate-as-product.** Can an LLM developer-persona walk the mid-run gate and score interaction
  quality? Connect to TASK-PROC-069-05.
- **The probe link.** Map each candidate rubric dimension to which of the six probes (if any)
  supplies its evidence.

## Execution Model

Gather raw material — read REQ-PROC-068 + feat_measurement_instrumentation, the ideation
skill(s) and their deterministic post-checks, the two TASK-PROC-066 ledgers and gate
question.md files, and any prior playground synthesis in
`requirements_tasks/process/AI_rules/factory_extraction/tasks/`. Synthesize iteratively.

The session's model is fixed at launch (Opus when `opus_recommended: true`). No mid-session
model switching.

**Web research**: for prior art on LLM-as-judge reliability, rubric anchoring, and
evaluating open-ended generation, delegate a focused question to a spawned `general-purpose`
agent; never run WebSearch inline. Frame queries as questions (e.g. *"how is LLM-as-a-judge
made reliable for open-ended generation without reference answers?"*).

## Output

A synthesis defining: the assert-on-process principle, the concrete LLM-verifiable rubric
dimensions for the ideation skill (with anchored levels) and which are deterministic vs.
judged, the golden-trace regression scheme, how the human gate is tested via a persona judge,
how it feeds the six probes and AC-04's run_instructions+rubric format, and whether a new
sub-requirement is warranted or AC-04 is refined in place. Honest about judge-reliability
limits and what stays unmeasurable.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] The user has approved the final synthesis and stated what to do next
- [x] The action stated by the user as the next step was performed successfully
- [x] Chain ordering: the oracle implementation/verify tasks — whether derived here or by a follow-up impl task off REQ-PROC-068 — set `after` the playground-build tasks (the oracle runs against the built playground)
- [x] The synthesis reads https://agentskills.io/skill-creation/evaluating-skills and incorporates any relevant findings (e.g. eval artifact schema, with/without-skill baseline, workspace layout, timing capture, benchmark aggregation, human feedback storage, blind comparison) that fill gaps not already covered by the four-layer architecture

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies (uses existing ideation ledgers as material) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-069-05](../../../workflows/task_execution_entry/tasks/2026-06-11_explore_interactive-required-venue-axis/goal.md) | Sibling — the interactive-required venue axis; both arose from the same input and meet at "test the human-in-the-loop gate" |
| [TASK-PROC-044-21](../../../../epic_factory_quality/tasks/2026-06-15_explore_remediate-self-referential-verification-blindspot/goal.md) | Align rubric vocabulary with 044-21's externally-grounded-property class — open-ended quality is the first concrete member whose oracle this task builds. **Non-blocking** (`after: []`): proceeds as the ideation-quality lever rather than waiting on the layer-derivation remediation (TASK-PROC-071-02) |
