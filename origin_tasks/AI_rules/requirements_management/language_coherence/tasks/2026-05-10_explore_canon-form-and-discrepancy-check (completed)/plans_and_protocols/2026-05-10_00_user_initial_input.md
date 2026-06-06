# User initial input — TASK-PROC-049-01

> Captured verbatim from the conversation that triggered this task. Read it as a seed bed, not a spec.

---

The trigger for this exploration was a review of the layers-skills toolkit (https://github.com/jamiemill/layers-skills), specifically its `/layers-conceptual-model` skill — which captures the idea that a product's *user-facing* concept canon (objects, states, vocabulary, named operations) is the most neglected load-bearing layer of product design.

The user's framing across the conversation:

> *"i'd like to always have requirements, also for process topics like this, so the first step would be to define requirements. but of course they must be solution agnostic. they must define the motivation, the goal, not the spolution. i think the concrete processes and skills are the how. who knows, maybe in the future there will be a better approach than creatuing skills."*

REQ-PROC-049 was written in that spirit — purely the goal, no implementation form prescribed. This explore task is the place where the *how* gets designed.

The user's specific pointers across the conversation:

- *"how does it relate to the plan to define not only labels, but also descriptions of the labels so that translation can be done by a llm?"* — referring to REQ-NFUNC-013 AC-08 (`translation_context`). The user identified this as the strongest pull on the canon: per-label descriptions will redundantly redescribe nouns/verbs/states unless a canon exists upstream.

- *"I like the ubiquitous language check"* — referring to the verb-precision tests (synonym drift + semantic flattening) from `/layers-conceptual-model` Phase 6. This is the part of the canon's discipline the user found most concretely useful, distinct from the canon-as-artifact question.

- *"how does it relate to other ux artifacts we already create (note we have a ux workflows but never really used it yet)?"* — caution against adding more unused UX skill machinery. The exploration should weigh whether the canon's form leans on existing under-used UX infrastructure or sits adjacent to it.

- *"do code"* (in answer to "should AC-05 enforcement scope cover code identifiers?") — the discrepancy check is expected to span all four artifact types (requirements, UI labels, `translation_context`, user-facing identifiers in `lib/`), not just textual artifacts.

- The user's prior memory `feedback_requ_explore_for_modifications.md` and the meta-rule "the concrete processes and skills are the how" reinforce that this exploration should not pre-commit to a skill or markdown form — those are option-space items, not constraints.

The motivation grounding throughout: PERSONA-015 (app provider — solo developer, *"longevity over velocity"*, *"simplicity is a survival strategy for one-person maintenance over years"*). Whatever the canon's form, it must minimize ongoing maintenance burden. A canon that requires per-feature manual sync is worse than no canon.

Counter-pulls the exploration should treat seriously:

- The user explicitly noted the project "already creates a lot of markdown documents" — adding another large markdown artifact is not free. The cost of authoring and maintaining the canon must be weighed against the duplication cost it removes (notably AC-08).
- The user noted the existing UX workflow infrastructure (`ux-create-flow`, `ux-write-persona`, `ux-write-scenario`) has been authored but never used in practice — adding more under-used machinery is a real risk.
- The user resisted importing the layers-skills toolkit wholesale; the exploration should keep that posture — *the framework is one inspiration, not the implementation*.

REQ-PROC-049 was authored as the requirement; REQ-PROC-050 (Artifact Soundness) was authored as a sibling; REQ-NFUNC-013 was extended with a forward link to REQ-PROC-049 (Section 8.4) so that AC-08's downstream implementation can pick up the canon when it exists. A one-page soundness checklist (`requirements_user_needs/SOUNDNESS_REVIEW_CHECKLIST.md`) was authored separately as REQ-PROC-050's first concrete implementation.

This task is REQ-PROC-049's first concrete implementation — but the form is open.
