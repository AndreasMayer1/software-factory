---
task_id: TASK-PROC-032-10
type: explore
parent_requirement: REQ-PROC-032
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-05-27
started: 2026-05-27
completed: 2026-05-31
session_id: 6a260b9e-9f09-42b4-9f17-bbcff0c697bc
session_account: gmail2
after: [TASK-PROC-044-03, TASK-PROC-044-04, TASK-PROC-044-05, TASK-PROC-044-06, TASK-PROC-044-07, TASK-PROC-044-08, TASK-PROC-044-09, TASK-PROC-044-10, TASK-PROC-044-13]
awaiting: []
awaiting_note: ""
# Block reason (per user direction 2026-05-29 after TASK-PROC-044-02 conclusion):
# Do NOT resume before TASK-PROC-044-03..10 (the full skill-interface-contracts
# mechanism rollout) are completed. Iteration 6 of this exploration reconciles
# the 10 deferred bundles from file 09 §11 against the ratified mechanism + the
# SCRIBBLE-SPLIT shape revised by TASK-PROC-044-02.
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore two open questions: (1) whether Han's factory has a UX-review agent or skills we can adopt; (2) what the exact contract is between scribble output and the coding consumer, and what that implies for the skill's design"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore — spans scribble skill, coding consumer skills, and potential external tool adoption
writes_requirements: false
requirements_version:
  commit: b58e7cca
  file: ../requirements.md
---

# Goal: Explore Scribble–Coder Contract and Han UX-Review Adoption

## Objective

Two tightly linked questions are unresolved after the recent scribble-quality improvement rounds (TASK-PROC-032-08, TASK-PROC-032-09). This task enters both problem spaces without trying to close them prematurely.

**Q1 — Han UX-review agent**: Han's factory reportedly has a UX-review agent (and possibly other skills). We do not yet know what it does, how it works, or whether/how it could slot into our scribble review step. We need to find out before deciding.

**Q2 — Scribble–coder contract**: It is unclear what the scribbles currently "commit to" versus what the coder re-derives from `doc/` rules at coding time. If the contract is "1:1 implement", scribbles must carry full UX writing, tier levels, and all UX/UI rules — a heavy, fragile approach. If the contract is "structural wireframe only", scribbles must make that explicit (for the human reviewer) and the consumer skills must make it explicit too (so nothing is silently lost). The current state is implicit; the right state is explicit.

## Background

The two most recent improvement tasks improved scribble generation quality but deliberately stopped short of these deeper questions:
- `2026-05-26_analyze_scribble-quality-task-func-007-01-05` — diagnosed specific scribble quality failures
- `2026-05-26_impl_improve-scribble-skill-flow-and-states` — fixed generation and auto-review rules

Both tasks left open the systemic question: *what does a scribble guarantee?*

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-27_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show b58e7cca:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **What does Han's UX-review agent actually do?** What inputs does it take, what does it output, and at what point in the workflow does it run? Is it a pass/fail gate, a scored rubric, or a generative critic? Is it Haiku/Sonnet/Opus?

2. **Are there other Han skills relevant to scribble generation or iteration?** The user only checked the UX agent; what else exists? Could any skill replace or augment a phase in `ui-create-scribble`?

3. **What does `ui-verify-flutter` actually consume from a scribble today?** Read the skill and the `flutter_handoff.yaml` spec. Does it implement every element in the scribble, or does it check against it? What happens to elements that conflict with `doc/` rules?

4. **What does `code-simple` / `code-complex` consume from a scribble?** Trace the path: when a coder receives a scribble, what is the stated contract? Is it "implement this exactly" or "use this as structural guidance and derive everything else from `doc/`"? Where is this written (or not written)?

5. **What would "contract-explicit" scribbles look like?** If the answer to Q2 is "structural wireframe only", what exactly must be labelled "these are the things the scribble locks in" (layout, screen order, component choices, navigation) versus "these are not set here" (colors, spacing, copy, tier rules, accessibility)? What would that annotation look like in the HTML output and in the `flutter_handoff.yaml`?

6. **What is the minimum scribble fidelity that still gives reviewers enough to approve meaningfully?** If we strip out everything the coder re-derives anyway, what is left? Is it still useful to a human reviewer?

7. **What would a scribble-contract gap look like as a bug?** Look at TASK-PROC-032-08's findings — were any of the quality failures actually contract-ambiguity failures (coder assumed something was committed, but it wasn't)?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — Han's factory structure, what a "UX-review agent" looks like in other AI factories, prior art on wireframe-to-code contracts — delegate to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates context fast; the subagent returns only a distilled summary.

Frame search queries as questions rather than keyword bags — e.g. *"what does a UX-review agent do in an AI-assisted design workflow?"* rather than *"UX agent AI design"*.

**Han artifact access**: If Han's skills/agents are available on disk (check `.claude/` or any referenced path), read them directly. If not, surface what is known from the skill index and ask the user whether to request access.

## Output

A future implementer reading the synthesis should be able to answer:
- Whether Han's UX-review agent is adoptable as-is, adaptable, or not applicable
- Exactly what a scribble commits to (the "set in stone" list) and what it explicitly does not commit to
- What changes are needed in `ui-create-scribble`, `ui-verify-flutter`, and/or the coding consumer skills to make the contract explicit
- What, if anything, should be added to the scribble HTML output or `flutter_handoff.yaml` to carry the contract signal to the reviewer and to the coder

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

<!-- Closure (2026-05-31): the iteration-5 §11 hold condition is satisfied — iteration 6
     (file 15) reconciled the deferred bundles against the ratified REQ-PROC-044 mechanism,
     and the remaining scribble-content work is now seeded as REQ-PROC-032 AC-21..AC-36 with
     9 derived tasks (TASK-PROC-032-11..-20, excl -16). The after-chain (044-03..10,13) is
     complete. ACs genuinely met; completing per developer direction. -->


## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
