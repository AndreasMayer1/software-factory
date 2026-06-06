---
task_id: TASK-PROC-046-01
type: explore
parent_requirement: REQ-PROC-046
urgency: 3
urgency_reason: U3-PROCESS
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-05-10
started: 2026-05-15
completed: 2026-05-15
session_completed_at: 2026-05-15T06:29:09Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and define concrete, measurable code quality requirements using the LLM back-pressure concept — automated quality gates that force revision until measurable thresholds are met"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore spanning process + architecture layers; requires trade-off judgment on threshold selection and gate design
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: ""
  file: ../requirements.md
session_id: 22810811-9b32-4fa4-9e0f-742f2c82c444
session_account: gmail2
---

# Goal: Define Concrete LLM Code Quality Requirements via Back-Pressure Gates

## Objective

What does "good code quality" actually mean in this project — in terms a machine can verify and an LLM can be measured against? We do not yet have a requirement that captures this concretely. The exploration must produce a requirements document (REQ-PROC-046) that:

- Translates the app provider's longevity and maintainability values into measurable thresholds
- Defines which automated gates enforce those thresholds (the "back-pressure" mechanism)
- Specifies what the LLM must do when a gate fails (revise, not proceed)
- Is grounded in what the project's existing tooling (`analysis_options.yaml`, `dart analyze`, `flutter test`) already measures

The exploration should surface which thresholds are well-justified and which are arbitrary, what the research says about LLM back-pressure effectiveness, and what trade-offs exist between strictness and development velocity for a solo developer.

## Background

The app provider persona (PERSONA-015) values longevity over velocity: "the codebase must survive periods where the creator has no time to touch it." This drives a need for objectively measurable quality, not subjective assessments.

The project already has some quality tooling in place:
- `analysis_options.yaml`: `dart_code_linter` with metrics — cyclomatic-complexity ≤ 20, number-of-parameters ≤ 4, source-lines-of-code ≤ 50
- `doc/linter/linter_setup_and_guidelines.md`: architectural rules (`avoid-banned-imports`, `avoid-dynamic`, `avoid-global-state`), `dart fix --apply` as a mandatory step
- `doc/testing/testing.md`: test folder structure and process, but no coverage threshold

What is missing is a requirement that names the gates, specifies pass/fail thresholds, defines the LLM's obligation when a gate fails, and explains the reasoning behind each threshold.

Web research conducted (2026-05-10) found:
- Back-pressure = automated feedback loops (compiler/linter errors → LLM → revised code → re-check)
- Effectiveness decreases after 3–5 iterations; LLMs optimizing one metric often degrade others
- DCM defaults: cyclomatic-complexity ≤ 20, LOC ≤ 100, nesting ≤ 5, parameters ≤ 4
- `very_good_analysis` is a strict Flutter linting preset
- Branch coverage for LLM-generated tests averages ~17% on real-world functions (research baseline)
- StarCoder2 reduced AvgCyclomatic by 17.4% vs developer baseline of 14.6%

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-10_00_user_initial_input.md`

Read it as a seed bed, not a spec.

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **The threshold origin problem**: Our current thresholds (cyclomatic ≤ 20, SLOC ≤ 50, params ≤ 4) exist in `analysis_options.yaml`. Were they chosen deliberately or as defaults? What happens if an LLM consistently hits the limit without margin? Should the gate threshold differ from the analyzer warning threshold?

2. **What "back-pressure" actually means for a solo dev**: Academic back-pressure loops assume an automated CI pipeline. Here, the LLM agent IS the developer. What does it mean to "reject and revise"? Is it sufficient for the requirement to say "LLM must not proceed if gate fails" — or does the gate need to be enforced by the harness (hooks, pre-commit)?

3. **The coverage gap**: `doc/testing/testing.md` describes test structure but no coverage %. Research shows LLM-generated code has very low branch coverage (~17%). Should this requirement set a minimum? What's realistic for a solo dev with limited test-writing time?

4. **App provider values → thresholds**: The persona says "minimum effective dose" and "simplicity is a survival strategy." Does that argue for loose thresholds (so the LLM has room to express solutions naturally) or tight ones (so complexity doesn't accumulate)? Is there a conflict between strictness and sustainability?

5. **What existing requirements already govern**: `REQ-PROC-044` (factory quality), `REQ-PROC-002` (testing), `doc/linter/` — which of these already cover quality gates implicitly, and what is genuinely missing?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline.

Frame search queries as questions rather than keyword bags — this produces more useful results.

## Output

A future implementer reading the output should understand:
- Exactly which gates the LLM is subject to, with pass/fail thresholds
- Why each threshold was chosen (persona grounding + research justification)
- What the LLM must do when a gate fails (the back-pressure mechanism)
- How these gates relate to existing tooling and do not duplicate REQ-PROC-044 or REQ-PROC-002
- Where the boundaries are (what this requirement covers, what it intentionally excludes)

## Acceptance Criteria

- [x] Exploration produced at least one Opus synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
