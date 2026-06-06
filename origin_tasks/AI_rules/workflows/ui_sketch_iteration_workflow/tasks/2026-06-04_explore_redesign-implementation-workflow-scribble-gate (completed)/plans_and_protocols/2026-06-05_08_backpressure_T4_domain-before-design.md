# Back-pressure report — T4: should domain entities exist before scribbles are created?

Task: TASK-PROC-032-29. Date: 2026-06-05.
Developer's words: *"release-begin-impl (Wave 1) creates coding tasks for pure-domain units (no scribble).
would it make the creation of the scribbles easier if the domain entities already exist on scribble creation?
imagine a complex form that asks the user for many data points, all with different format and validation.
creating the ui for that will be much easier with a complete and precise definition of those data points…"*

Grounded against Round-1 synthesis §2.4 (per-design-unit, pure-domain units get coding tasks in Wave 1),
§3.4 (task-creation timeline), and the eval substrate PROP-8 RE-DERIVE note (the scribble depicts *design*,
not *implementation* — D1–D8 wireframe/implementation separation).

---

## Level 1 — the topic as a whole

### The rationale being pressured
*"A scribble that depicts a data-rich screen (a complex validated form) is easier and more accurate to draw
if the domain model behind it already exists — so build the domain entities before drawing the scribble."*

This is correct in spirit and it sharpens the design. But it must be stated precisely, because a naïve
reading ("always build all domain code before any scribble") would re-introduce exactly the serialisation
cost the per-design-unit gate (D-2) exists to avoid.

### The reframing that makes it fit cleanly
The scribble gate sits between **design and Presentation-code**, *not* between domain-code and design. Domain
code is **upstream of both** — it is the substrate the UI presents. So the developer's instinct doesn't
contradict the gate; it reveals a **third layer** that was implicit:

> **domain-code  →  design (scribble)  →  presentation-code**

- This is fully consistent with P-A (no *Presentation* coding before scribble approval) — domain code was
  never the thing P-A gated.
- It answers a question Round-1 left soft: *what is the relationship between the Wave-1 pure-domain coding
  tasks and the scribble tasks of the same design-unit?* Answer: for **data-bound** scribbles, the domain
  task is upstream of the scribble task.

So Wave 1 is not flat. It bisects into **Wave 1a (domain code) → Wave 1b (scribbles)**, with conditional
1a→1b edges, then the gate, then Wave 2 (presentation-code).

### What speaks against it — the two real dangers
1. **Over-serialisation if applied universally.** Most scribbles are *not* data-bound — a navigational
   screen, a confirmation dialog, an empty-state, a settings toggle. Forcing "domain before scribble"
   everywhere serialises the whole design wave behind the domain wave, which is the same liveness cost as a
   global gate. The benefit is real only for data-bound screens (forms, validated inputs, lists/tables of
   domain entities, anything whose layout is driven by field cardinality/types). → the edge must be
   **conditional**, detected from whether the requirement's Presentation ACs reference domain value-objects/
   entities that carry their own (non-Presentation) ACs.

2. **It may be solving the problem at the wrong layer.** The developer's pain — "a complex form, many data
   points, different formats and validation" — is fundamentally a *specification-precision* problem. What the
   scribble author needs is a **precise definition** of the data points (names, types, formats, validation
   rules, enums, required/optional). That definition belongs in the **requirement**, and exists *before any
   code*. If the requirement already specifies the data model precisely, the scribble author reads the
   requirement — they do not need the *implemented Dart class*. So the first-order fix may be a
   **requirement-completeness expectation** ("a data-bound Presentation requirement MUST carry a precise
   data-point table before its scribble runs"), not a code-ordering edge.

   This connects to the eval substrate's PROP-8 RE-DERIVE separation: the scribble is a *design* artifact; it
   should be derivable from the *requirement*, not require reading implementation. Making the scribble depend
   on implemented code slightly erodes that separation and should be the *secondary*, not primary, mechanism.

### Where code-first genuinely earns its place (the steel-man)
For a genuinely complex/uncertain domain, some constraints are only *discovered* when the value object is
implemented — a validation interaction, a derived field, a format normalisation the requirement author didn't
foresee. In those cases implementing the domain first surfaces constraints the requirement would otherwise
miss, and the scribble drawn afterwards is more faithful. This is the legitimate residual value of code-first
— but it is the exception (discovery), not the rule (specification).

### Synthesis — the two-mechanism answer
1. **Floor (always): requirement-precision.** A data-bound Presentation requirement must define its data
   points precisely (a data-point table: name, type, format, validation, optionality) before its scribble
   task runs. This is a `requ-explore` / requirement-completeness concern and a coverage-report check.
2. **Conditional ordering edge (when warranted): domain-before-scribble.** When a scribble depicts data-bound
   UI *and* the domain model is novel/complex enough that the requirement can't fully specify it
   pre-implementation, add an `after` (or soft-pref) edge: the data-bound scribble task `after` the
   domain-code task(s) of its design-unit. Default to soft-pref (ordering hint) to preserve liveness; harden
   to a blocking `after` only for the flagged complex cases.

Detection of "data-bound" = the requirement's Presentation ACs reference domain value-objects/entities that
have their own non-Presentation ACs in the same design-unit. The design-unit map (from `requ-derive-from-flow`,
Round-1 §6.1) already carries the membership needed to find the domain tasks to point the edge at.

---

## Level 2 — chapter by chapter

### "Wave 1 creates coding tasks for pure-domain units (no scribble)"
- **Pressure:** correct — and those tasks *existing* is not the same as them being *executed*. The
  developer's question is about **execution order**, not task existence. Wave-1 pure-domain tasks can be
  scheduled before the design-unit's scribbles run.
- **Action:** make Wave-1 sub-structure explicit (1a domain → 1b scribbles), not a flat batch.

### "would it make scribble creation easier if the domain entities already exist?"
- **Pressure:** *conditionally* yes — for data-bound scribbles. For non-data-bound scribbles it adds nothing
  and costs serialisation.
- **Action:** conditional edge, gated on a "data-bound" detector; default soft-pref.

### "imagine a complex form … many data points … different format and validation"
- **Pressure:** this is the paradigm case that benefits — *and* the paradigm case where the **requirement**
  should already carry a precise data-point definition. Ask first: is the form hard to scribble because the
  domain isn't coded, or because the **requirement** under-specifies the data model? Usually the latter is
  the cheaper, earlier fix.
- **Action:** add a requirement-completeness expectation (data-point table for data-bound Presentation
  requirements) as the floor; reserve code-first ordering for genuinely discovery-heavy domains.

### "creating the ui … much easier with a complete and precise definition of those data points"
- **Pressure:** "complete and precise definition" is the operative phrase — and a *definition* is a
  requirement/spec artifact, not necessarily code. The strongest version of the developer's point is
  satisfied by precise specification; code-first is only needed when the spec can't be precise until
  implementation reveals constraints.
- **Action:** two mechanisms — precision (always) + conditional code-first (discovery cases).

---

## Residual uncertainty (honest)
- **The "data-bound" detector is unspecified.** Deciding which scribbles depict data-bound UI from AC text is
  heuristic; a mis-classification either over-serialises (false positive) or misses a beneficial edge (false
  negative). Needs a concrete rule (AC references a domain value-object with its own ACs) and probably a
  human override at the gate.
- **Where the data-point definition lives** — in the requirement prose, in a structured table, or in the
  scribble's own information-model boundary — is undecided. If it lives in the requirement, the scribble
  reads it (clean RE-DERIVE separation). If it lives only in code, the scribble must read `lib/` (erodes
  separation, ties scribble currency to code currency — a new staleness coupling). Leaning: structured
  data-point table in the requirement.
- **Interaction with SCI.** If a data-bound scribble now depends on domain code, and that domain code changes
  mid-release, does the scribble go stale? Possibly — this extends the SCI rot graph with a domain-code→
  scribble edge that Round-1's SCI (requirement→scribble→code) did not model. Whether that edge needs its own
  staleness detector is unexamined and should be checked when SCI is specified.
- **Whether code-first actually produces better scribbles** is an empirical claim — untested until a real
  complex-form feature is run both ways. The fixture from T2 could test it deliberately (include one
  validation-heavy form design-unit).
