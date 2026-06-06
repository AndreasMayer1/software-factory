---
id: REQ-PROC-050
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: active
effort: M
stakeholder: app_provider
created: 2026-05-10
updated: 2026-05-10
after: [REQ-PROC-045]
blocks: []
market_research_refs: [] # No relevant findings identified
target_package: ""  # internal process tooling — unassigned
personas_served: [PERSONA-015]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "For every artifact in the user-needs cascade (each persona, each scenario, each user flow, each requirement category), an assessment can be produced that classifies the artifact's state of decisions as one of: Strong (decided and evidenced), Partial (decided but partially evidenced), Assumed (asserted without evidence), Weak (visibly thin or undecided), Not started, or N/A."
    - id: AC-02
      text: "When the assessment is run, its output names the bottleneck — the lowest layer in the cascade (Persona → Scenario → Flow → Requirement) with non-Strong state — and explains which decisions are missing or thin and what risk that creates for layers above. The bottleneck is named specifically, not vaguely gestured at."
    - id: AC-03
      text: "Assumed and Weak are surfaced as distinct categories in the output. Assumed entries are explicitly flagged with language that distinguishes them from Weak — they are not collapsed into a single bucket, because assumptions that look solid hide the most risk."
    - id: AC-04
      text: "The assessment is repeatable: applying the same classification criteria to the same input artifacts produces the same classification, regardless of whether the operator is a human reviewer or an LLM agent. The criteria are explicit enough that two operators reach a similar result without coordination."
    - id: AC-05
      text: "The assessment has a defined trigger — it is invocable on demand, and a stated recommendation exists for at least one moment in the factory's lifecycle when running it adds value. The specific trigger and cadence are not prescribed by this requirement; what must exist is a documented answer to the question 'when should this run?'."
---

# User-Needs Artifact Soundness Assessment

## Overview

The factory measures coverage — how many personas, scenarios, flows, and requirements exist per area, and which artifacts reference which others. This requirement defines what must be true for the factory to also assess *soundness*: whether the decisions captured at lower layers of the cascade are evidenced and decided, or merely asserted. It does not specify how the assessment is produced or where the output lives.

## Purpose

`STATUS.md` (`requirements_tasks/STATUS.md`, `requirements_user_needs/STATUS.md`) and the existing structural quality requirement REQ-PROC-045 measure coverage and structural conformance. They answer: *do the right artifacts exist in the right places, with the right links?* They do not answer: *are the decisions captured in those artifacts grounded in evidence, or are they assumptions in disguise?*

A persona whose grounded_values are unverified hypotheses passes coverage. A scenario paraphrased from a feature wishlist passes coverage. A user flow built from team belief rather than observed behaviour passes coverage. A requirement that ratifies all of the above passes coverage. Each layer's weakness propagates downstream: assumed user-needs become assumed requirements become assumed implementations, and the assumption is invisible because every artifact looks complete.

The factory's cascade — Persona → Scenario → Flow → Requirement → Task → Code — depends on the soundness of its lower layers. PERSONA-015 (app provider — solo developer, *"longevity over velocity"*, *"simplicity is a survival strategy for one-person maintenance over years"*) carries a structural risk here: building features on assumed user-needs costs more than not building them, because corrections happen after implementation rather than before.

The critical distinction is between **Assumed** and **Weak**. Weak artifacts are visibly thin — short personas, sparse scenarios, undocumented flows. They are easy to spot during review. Assumed artifacts look solid: they have full prose, named details, plausible motivations. Their risk is invisible because nothing in the artifact itself signals "this was not actually evidenced." Treating Assumed as a separate category — explicitly flagged as *looks solid, may not be* — is what makes the assessment useful. Coverage metrics cannot make this distinction; they treat full prose as proof of completeness.

This requirement establishes the contract for how that distinction is captured and surfaced. It originates from review of the Layers of Product Design *orient* diagnostic pattern, which assesses each design layer as Strong / Partial / Assumed / Weak / Not started and identifies the lowest weakly-grounded layer as the bottleneck. The pattern is adapted here to the factory's user-needs cascade rather than imported wholesale; the framework is one possible inspiration, not the prescribed implementation.

## When This Requirement Applies

- When the factory's user-needs cascade artifacts (personas, scenarios, user flows, requirement categories) are reviewed for quality, not just coverage.
- At factory inflection points where decisions in lower layers are about to be relied upon by a large amount of downstream work — e.g. before adopting a new persona's needs at scale, before committing a scenario into a release.
- On demand, when a contributor or LLM agent suspects that artifacts presented as decided are actually assumed.

## When This Requirement Does NOT Apply

- Implementation artifacts (code, tests, integration tests) — soundness of code is governed by REQ-PROC-046.
- Structural conformance of the requirements folder layout — covered by REQ-PROC-045.
- Language coherence across artifacts — covered by REQ-PROC-049 (separate dimension of artifact quality).
- One-off ad-hoc reviews that do not produce a repeatable, reproducible classification.

## Behavior

The end state this requirement targets:

- A contributor or LLM agent can run an assessment and receive, for each artifact in the user-needs cascade, a single classification (Strong / Partial / Assumed / Weak / Not started / N/A) tied to explicit criteria.
- The assessment names the bottleneck — the lowest layer in the cascade where decisions are not Strong — and explains why that layer is the constraint on everything above.
- Assumed entries are visible as their own category. A reader scanning the assessment can answer the question *"which artifacts look solid but may not be?"* without inferring it.
- The assessment is reproducible: the same artifacts and the same criteria produce the same classification across operators and time.
- A trigger and cadence for running the assessment are documented somewhere in the factory's process records — even if that documentation is "run on demand at user request."

## Examples

**Example 1: An Assumed persona that passes coverage**

A persona file lists motivations, grounded_values, scenarios, and review_status approved. The grounded_values were drafted by an LLM from a brief and were never validated against user research. Coverage metrics treat this persona as complete; soundness assessment classifies it as Assumed and flags it as the cascade's bottleneck if downstream scenarios depend on those grounded_values.

**Example 2: A Strong scenario built on an Assumed flow**

A scenario is highly specific and grounded in observable behaviour. The user flow it implements was drafted from team belief without observation. The cascade chain is Strong-on-Assumed; AC-02 surfaces the flow as the bottleneck even though the immediate review focus is the scenario.

**Example 3: A Weak vs. Assumed distinction**

Two requirement categories have similar coverage scores. Category A's requirements are sparse — short, missing several ACs, marked TODO in places. Category B's requirements are full prose with full ACs, but the ACs were derived from a hypothetical scenario rather than from observed need. AC-03 requires Category A to be classified Weak and Category B to be classified Assumed — they are different kinds of risk, addressed differently.

## Developer Guidelines

> Constraints and invariants the final implementation must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **Soundness is a separate dimension from coverage.** A coverage check answers *does it exist?* A soundness assessment answers *is it grounded?* Both are needed; neither substitutes for the other.
- **Assumed is a first-class category.** Collapsing Assumed into Weak (or into Strong, by treating "looks complete" as "is complete") destroys the assessment's value. AC-03 is non-negotiable on this point.
- **The classification criteria must be explicit.** AC-04's repeatability is what distinguishes a soundness assessment from a subjective review. Criteria like "scenario is grounded in observed behaviour" must be operationalized to something checkable (e.g. presence of a research reference, a transcript, an observed-behaviour artifact).
- **The bottleneck is named, not gestured at.** *"User needs are weak"* is not a bottleneck statement; *"Persona PERSONA-007 has Assumed grounded_values that scenarios SCEN-007-* depend on"* is.
- **The trigger documentation is part of the assessment, not separate.** AC-05 is satisfied by recording when the assessment should run. A pure "run on demand at user request" answer satisfies AC-05; an undocumented cadence does not.

### Common Pitfalls

- **Dropping the Assumed category to simplify the output.** Reduces output complexity at the cost of removing the only category that surfaces hidden risk. The whole assessment loses its value.
- **Conflating soundness with completeness.** A complete artifact (no TODOs, full prose) can still be Assumed. Soundness asks whether the substance is evidenced, not whether the form is finished.
- **Producing one-off subjective ratings dressed as soundness.** Without explicit criteria (AC-04), the output looks like an assessment but is actually an opinion. Two reviewers will disagree on the same artifact, and the assessment will not be reproducible.
- **Running the assessment too rarely.** A defined cadence (AC-05) that resolves to "once a year" provides no protection at the moments when soundness matters most — release planning, persona adoption, large-scale requirement creation.

## Related Requirements

- **REQ-PROC-045 (Requirements Structure Quality)** — sibling. Structural sibling: REQ-PROC-045 enforces folder layout and ID registry conformance; this requirement enforces evidential grounding.
- **REQ-PROC-049 (Language Coherence Across Product Artifacts)** — sibling. Language coherence and decision soundness are independent quality dimensions: an artifact can be linguistically coherent and evidentially Assumed, or grounded but linguistically inconsistent.
- **REQ-PROC-046 (Code Quality / LLM Back-Pressure Gates)** — implementation-side analog. REQ-PROC-046 governs whether code is correct; this requirement governs whether the user-needs the code is built on are evidenced. Same factory, different layers.

## References

- `requirements_user_needs/STATUS.md` — coverage view that this requirement complements (not replaces)
- `requirements_tasks/STATUS.md` — coverage view for requirements/tasks
- `requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md` — REQ-PROC-045 (structural sibling)
- `requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md` — REQ-PROC-049 (semantic sibling)
- `requirements_user_needs/personas/app_provider/persona.md` — PERSONA-015 grounded values motivating soundness disciplines
- Layers of Product Design framework, `/layers-orient` diagnostic — conceptual origin of the Strong / Partial / Assumed / Weak / Not started classification and the bottleneck-identification pattern; one of several possible inspirations for implementation
