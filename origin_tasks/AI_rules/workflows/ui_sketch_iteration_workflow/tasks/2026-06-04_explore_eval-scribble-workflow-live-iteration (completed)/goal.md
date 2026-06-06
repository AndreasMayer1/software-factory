---
task_id: TASK-PROC-032-28
type: explore
parent_requirement: REQ-PROC-032
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-06-04
started: 2026-06-04
completed: 2026-06-04
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Live evaluation of the scribble workflow quality by running TASK-FUNC-007-01-05 through additional iteration rounds while collecting developer feedback on each skill's performance; produces improvement documents."
release_description: ""
expected_tool_calls: 45
skill_chain_depth: 3
synthesis_dependent: true
synthesis_justification: "Must hold findings across multiple iteration rounds and multiple skill evaluations simultaneously to produce coherent improvement recommendations."
opus_recommended: true   # reason: explicit evaluation/compare task — quality signals from multiple skills must be synthesized into improvement proposals; cross-cutting judgment across generator, reviewers, persona-walker, heuristics, and feedback-classifier
writes_requirements: false
requirements_version:
  commit: d29b49c9
  file: ../requirements.md
---

# Goal: Live Evaluation of Scribble Workflow via Iterative Pilot

## Objective

The scribble workflow has been substantially rebuilt (REQ-PROC-032 AC-01 through AC-41). TASK-FUNC-007-01-05 is the first real use of the new workflow — it has just reached the Phase 3 user-feedback gate at v2. This task captures a structured evaluation of how well each skill in the chain performs, by running TASK-FUNC-007-01-05 through its remaining iterations while simultaneously collecting the developer's qualitative assessment of each skill's output.

The outcome is NOT another iteration of the scribble. The outcome is a set of improvement documents that tell future tasks exactly what to fix in which skill.

## Background

TASK-FUNC-007-01-05 (`feat_therapist_transfer_ui`, client-send-screen scribble) is the pilot task for the new scribble skill chain. The old run (archived at `archive/scribble-pilot-v1-old-skill`) used the pre-rebuild skill; the new run reached v2 after:
- Phase 1 (pre-brief + generation by `ui-scribble-generator`)
- Phase 2 (auto-review by `ui-scribble-auto-review`, which runs rule-reviewer, persona-walker, heuristics-reviewer, cross-feature checker)
- Phase 3 (user-feedback gate — blocked at `automation/pending_feedback/TASK-FUNC-007-01-05/question.md`)

The v2 scribble is ready for developer review. The pending gate contains: three decisions (RQ1 requirement inconsistency, D1 discard placement, D2 discrete control), a PILOT comparison instruction, and 14 auto-review fixes applied in v2.

This task runs alongside TASK-FUNC-007-01-05 — the pilot task continues to iterate toward approval while this evaluation task records what the developer observes.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-04_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show d29b49c9:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Two threads run in parallel — do not merge them:

**Thread A — Pilot execution**: Progress TASK-FUNC-007-01-05 through its remaining iteration rounds (v3, v4, … until approved). Each round: present the scribble to the developer, collect feedback, classify it (Phase 4), regenerate, auto-review, return to Phase 3 gate. This is the normal scribble workflow; treat it as the specimen under observation.

**Thread B — Evaluation**: After each Phase 3 gate, pause and ask the developer how the skills performed. Capture responses in `plans_and_protocols/`. Between rounds, synthesize patterns: which skills are catching real problems, which are generating noise, which are missing gaps the developer had to catch manually.

Do not evaluate in the abstract. Evaluation must be grounded in what actually happened in each round — what the auto-review said, what the developer said differently, and what the scribble looks like before and after.

## Seeds

1. **Old vs. new baseline**: The PILOT comparison instructions in the pending gate ask to compare v2 against the old archived run. What changed? Is the new v2 visibly better or just differently wrong?

2. **Auto-review signal quality**: The 14 fixes in v2 came from auto-review. How many of those did the developer also notice independently? How many were surprises? This ratio reveals whether auto-review is a useful pre-filter or a source of noise.

3. **Skill weak-link detection**: Of the five review agents (rule-reviewer, persona-walker, heuristics-reviewer, cross-feature checker, per-flow walk), which one produced the least actionable output in the first round? Does this hold across subsequent rounds?

4. **Convergence rate**: How many iteration rounds does it take before the developer is satisfied enough to approve? Is the workflow converging, plateauing, or oscillating?

5. **Friction points**: Where in the workflow does the developer feel most uncertain about what to do next (Phase 3 gate instructions unclear, feedback classification surprising, pre-brief missing something, scribble diff hard to read)? These are UX problems in the workflow itself.

6. **Rule update protocol in practice**: Does the Phase 4 feedback classifier correctly distinguish "requirement gap" from "missing rule" from "persona-derived constraint"? Does the developer agree with the classification? Misclassification means skills route feedback to the wrong place.

## Execution Model

This task is inherently interactive — it cannot be executed in a single automated session. Each evaluation round requires the developer to review the scribble and answer questions. The protocol is:

1. Progress TASK-FUNC-007-01-05 to the next Phase 3 gate (or resume from the current v2 gate).
2. Ask the developer the evaluation questions for that round (see Output section).
3. Record responses in `plans_and_protocols/[date]_round_N_evaluation.md`.
4. After ≥2 completed rounds (or after approval of 007-01-05, whichever comes first): synthesize findings into improvement proposals.

**Web research**: If seeds require external benchmarks (e.g., how other AI design tools approach auto-review quality), delegate to a `general-purpose` agent with a focused question. Never run WebSearch inline.

## Output

When this exploration is complete, `plans_and_protocols/` should contain:

1. **Per-round evaluation records** (`[date]_round_N_evaluation.md`) — raw developer feedback on each skill's output, captured in structured form.

2. **Skill-level quality assessments** (`synthesis_skill_quality.md`) — per skill: what it reliably produces, what it consistently misses, and whether its scope/rubric needs narrowing or expanding.

3. **Improvement proposals** (`improvement_proposals.md`) — concrete, actionable proposals for each skill that needs changing. Each proposal identifies: which skill, which specific behavior, what the current output looks like, what the desired output looks like, and which AC or section of REQ-PROC-032 the fix should be anchored to.

4. **Workflow UX findings** (`workflow_ux_findings.md`) — friction points in the gate instructions, diff readability, feedback-classification surprise rate, or any other workflow interaction issues.

The documents must be written so that a future `impl` task can take each proposal and execute it without needing to re-read the evaluation session history.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round (after ≥2 iteration rounds of TASK-FUNC-007-01-05 or after its approval)
- [x] The synthesis defines the problem space in terms that were not fully known at task creation — not just "the persona-walker is weak" but "the persona-walker consistently misses cognitive-load constraints on screens with >4 interactive elements"
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide (e.g., "should the heuristics-reviewer be merged into rule-reviewer, or kept separate?")
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-FUNC-007-01-05 | in_progress | The pilot scribble task whose iterations this evaluation observes |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-08](../2026-05-26_analyze_scribble-quality-task-func-007-01-05%20(completed)/goal.md) | Predecessor — retrospective analysis of the old (pre-rebuild) scribble run; read it for baseline quality signals |
| [TASK-PROC-032-02](../2026-04-18_explore_scribble_skill_evaluation%20(completed)/goal.md) | Predecessor — internet research evaluation of AI wireframing tools; established context for what "good" looks like |
