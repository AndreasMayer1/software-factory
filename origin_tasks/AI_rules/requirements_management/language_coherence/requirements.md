---
id: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: active
effort: M
stakeholder: app_provider
created: 2026-05-10
updated: 2026-05-10
after: [REQ-PROC-045]
blocks: []
market_research_refs: [] # No relevant findings identified
target_package: ""  # internal process tooling — unassigned
personas_served: [PERSONA-015, PERSONA-001]
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "A single canonical source identifies, for every user-facing concept the product commits to, the concept's name, the states it can be in, and the named operations a user can perform on it. Each concept is defined exactly once; no requirement, label, or code identifier can introduce a new authoritative definition for a concept already in the canon."
    - id: AC-02
      text: "Across requirements bodies (`requirements_tasks/`), UI label entries, `translation_context` entries (REQ-NFUNC-013 AC-08), and user-facing identifiers in `lib/` (object names, action names, state names visible in the UI surface), every reference to a concept that exists in the canon uses the canon's name. Where a synonym is unavoidable (e.g. legacy term, role-specific term), the synonymy is acknowledged at the canon — silent coexistence of multiple names for the same concept does not exist."
    - id: AC-03
      text: "For every generic verb used in user-facing language (such as Edit, Delete, Update, Add, Create, Remove, Save, Submit), one of two conditions holds: (a) the verb's user-visible effect is identical across every object it applies to, or (b) the operations it would otherwise cover are decomposed into separately named operations that match real-world distinctions — e.g. correcting a typo and registering a real-world change of address are named separately when their downstream consequences (history preservation, audit, notifications) differ."
    - id: AC-04
      text: "`translation_context` entries (REQ-NFUNC-013 AC-08) reference the canonical concept by name rather than redescribing the noun, verb, or state from scratch. Per-label context is restricted to label-specific information (e.g. which surface the label appears on, which audience encounters it) — concept descriptions live at the canon."
    - id: AC-05
      text: "Discrepancies between the canon and any artifact under its scope (requirement bodies, UI label entries, `translation_context` entries, user-facing identifiers in `lib/`) are detectable by a repeatable check that produces a pass/fail signal. The check does not require a reviewer to remember every artifact; running it against the current state of the repository is sufficient to surface drift."
---

# Language Coherence Across Product Artifacts

## Overview

The product commits to a set of user-facing concepts — the things, states, and operations a user encounters. This requirement defines what must be true for those concepts to be named coherently across every artifact the factory produces: requirements, UI labels, translation context, and user-facing code identifiers. It does not specify how that coherence is achieved or where the canonical record lives.

## Purpose

The factory currently has no single source identifying which user-facing objects, states, and vocabulary the product commits to. Implementation-level domain modeling exists (`lib/core/domain/`, `lib/features/*/domain/`, `doc/domain/`), but that is the Clean Architecture domain layer — code-internal, not user-facing. Personas describe people, scenarios describe situations, flows describe paths, requirements describe behaviors. None of these establish: *the product calls this thing X (not Y or Z), it can be in these states, and a user can perform these named operations on it.*

Two compounding problems flow from this absence:

1. **Vocabulary drift across artifacts.** Each requirement re-coins terms locally; UI labels can use words that differ from the entities they refer to in code; no canonical inventory exists to detect this. The cost is dormant today but compounds rapidly with the planned translation workflow (REQ-NFUNC-013 AC-08), which requires a `translation_context` description for every UI text entry covering user situation, UI element type, and wording rationale. Without a shared canon, every label entry redescribes the same nouns, verbs, and states from scratch — duplicated effort during translation authoring and inconsistent results when the same concept is described differently per label.

2. **Semantic flattening and synonym drift in user-facing language.** Generic verbs (Edit, Delete, Update, Add, Create) can hide genuinely different real-world operations whose user intent and downstream consequences differ — *correct a typo* versus *register a change of address* should not collapse into one "Edit" action when one preserves history and one does not. Conversely, multiple verbs may be used for one underlying operation (Add, Create, New) without anyone noticing. Both modes degrade user comprehension and create downstream inconsistency between UI, code naming, and translation.

PERSONA-015 (app provider — solo developer maintaining the application alongside a full-time job) holds explicit grounded values: *"longevity over velocity"*, *"simplicity is a survival strategy for one-person maintenance over years"*. Per-label re-explanation and silent vocabulary drift are precisely the kinds of compounding maintenance burden the persona is structurally trying to minimize. PERSONA-001 (Amina) and other end-user personas encounter the surface symptoms — inconsistent labels, ambiguous CTAs, ambiguous semantics for actions whose real-world consequences differ.

This requirement establishes the contract — *what coherence means and how it is detectable* — without prescribing the form of the canonical source or the form of the discrepancy check. Future implementations may use markdown, generated artifacts, code annotations, repository linters, or some combination; that choice is made when implementation tasks are created, not here.

## When This Requirement Applies

- Whenever a new user-facing concept (object, state, named operation) is introduced in a requirement, UI label, `translation_context` entry, or user-facing identifier in `lib/`.
- Whenever an existing concept is referenced in any of those artifact types.
- During requirement authoring, UI label authoring, and translation context authoring.

## When This Requirement Does NOT Apply

- Implementation-internal identifiers in `lib/` that are never surfaced to users (private methods, internal value object names not user-visible, generated code).
- The Clean Architecture domain layer (`doc/domain/`, `lib/**/domain/`) when its terminology is implementation-internal — covered by separate architectural guidelines.
- Marketing copy and external messaging — covered by the marketing writing guidelines (REQ-PROC-027 area).
- Code identifiers that intentionally diverge from user-facing language for technical reasons (e.g. legacy compatibility), provided the divergence is acknowledged at the canon per AC-02.

## Behavior

The end state this requirement targets:

- Any contributor or LLM agent authoring a requirement, UI label, `translation_context` entry, or user-facing identifier can answer the question *"what does this product call this thing?"* by consulting one place.
- When a generic verb is being introduced, the contributor is structurally prompted to check whether it is hiding meaningfully different operations.
- When the same operation appears under different names across artifacts, the inconsistency is surfaced rather than silently shipped.
- The translation workflow (REQ-NFUNC-013 AC-08) operates against the canon, so per-label context narrows to label-specific information.

## Examples

**Example 1: REQ-NFUNC-013 AC-08 (translation_context) is the primary downstream consumer**

REQ-NFUNC-013 AC-08 requires every UI text entry to carry a `translation_context` covering user situation, UI element type, and wording rationale. Without a canon, hundreds of label entries each describe what a "MoodEntry" is, what "Register" means, what "pending sync" means. With a canon, each entry references the concept by name and describes only label-specific context (which surface, which audience, which moment).

**Example 2: Verb decomposition (semantic flattening)**

A "Delete entry" action surfaces in two contexts: the user removing a draft they never saved, and the user removing a previously-synced entry from a paired therapist's view. The first preserves no history; the second has audit and notification consequences. AC-03 requires these to be named separately when their downstream effects differ — e.g. *Discard draft* and *Withdraw shared entry*.

**Example 3: Synonym drift (silent coexistence)**

If "Add client" appears in one requirement, "Create client" in another, and "New client" in a UI label, AC-02 fails. Either the canon resolves to one term (e.g. "Add") and the others are corrected, or the canon explicitly records the synonymy and the rationale.

## Developer Guidelines

> Constraints and invariants the final implementation must satisfy. These describe the destination, not the path to it.

### Key Decisions

- **The canon is the single authority for user-facing concept names.** When a contributor needs the name of a user-facing object, state, or operation, they consult the canon, not a single requirement or a single UI label. If two artifacts disagree, the canon is right and the artifacts are wrong.
- **Implementation-side domain modeling is separate.** `doc/domain/`, `lib/**/domain/` cover the Clean Architecture domain layer. The canon covers the user-facing layer. The two may align (and often should), but neither replaces the other.
- **Synonyms exist at the canon, not silently in artifacts.** A legacy term that cannot be removed is a synonym recorded in the canon with its scope, not a parallel name used somewhere without acknowledgement.
- **Generic verbs are checked for both directions of failure.** Synonym drift (multiple names for one operation) and semantic flattening (one name for multiple operations with different consequences) are both detectable failure modes — neither alone is sufficient.
- **Detection does not require human memory.** AC-05's repeatable check is a property of the running tooling, not a reviewer's vigilance. A reviewer's vigilance is fallible; the check is the reliable signal.
- **The discrepancy check produces a pass/fail signal.** It is not a heatmap or a suggestion list — it answers "does the current repository state satisfy AC-02 and AC-03?" with yes or no, in line with the back-pressure pattern established by REQ-PROC-046.

### Common Pitfalls

- **Treating the canon as a glossary.** A glossary documents terms that already exist in artifacts; the canon is upstream — artifacts derive their terms from it. Building the canon by harvesting current artifact language and then never updating it reproduces the original drift problem.
- **Allowing per-feature vocabulary islands.** A new feature defining its own terms in its own requirement, divergent from existing canon entries, is exactly the failure this requirement targets. New features extend the canon; they do not bypass it.
- **Confusing this requirement with code identifier style guides.** Naming conventions for private code (camelCase, prefix patterns) are unrelated. This requirement is about *which name* is used for a concept, not *how* the name is formatted.
- **Treating verb decomposition as verbose.** "Register change of address" reads longer than "Edit"; that is precisely its value when the operations have different consequences. AC-03 does not push toward minimal verbiage — it pushes toward correct verbiage.

## Related Requirements

- **REQ-NFUNC-013 (UX Writing Guidelines)** — primary downstream consumer. AC-08 (`translation_context`) becomes substantially less duplicative once the canon exists. A follow-up `requ-explore` run on REQ-NFUNC-013 will record the dependency explicitly.
- **REQ-PROC-045 (Requirements Structure Quality)** — sibling structural quality requirement (folder layout, ID registry). This requirement is the semantic-quality counterpart.
- **REQ-PROC-046 (Code Quality / LLM Back-Pressure Gates)** — separate scope. Verb-precision in user-facing language is a UX/copy concern; verb-precision in private code identifiers may later become a code-quality gate but is governed by REQ-PROC-046, not here.
- **REQ-PROC-050 (User-Needs Artifact Soundness Assessment)** — sibling. Soundness is about whether decisions are evidenced; this requirement is about whether language is coherent. Independent dimensions of artifact quality.
- **`doc/domain/`** — the implementation-side complement. The Clean Architecture domain layer covers code-internal modeling; this requirement covers the user-facing complement.

## References

- `requirements_tasks/non-functional/ui_ux_design_system/ux_writing/requirements.md` — REQ-NFUNC-013 (translation context)
- `requirements_tasks/process/AI_rules/coding_standards/code_quality/requirements.md` — REQ-PROC-046 (back-pressure pattern)
- `requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md` — REQ-PROC-045 (structural sibling)
- `doc/domain/entities.md`, `doc/domain/value_objects.md` — implementation-side domain modeling
- `requirements_user_needs/personas/app_provider/persona.md` — PERSONA-015 grounded values motivating longevity-oriented disciplines
- Layers of Product Design framework, *conceptual model* and *ubiquitous language* (Sophia Prater OOUX, Daniel Rosenberg semantic IxD) — conceptual origin of the verb-precision tests in AC-03
