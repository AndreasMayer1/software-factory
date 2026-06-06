# Back-pressure report — T3: is it safe to forbid recursion at L3 (and L5)?

Task: TASK-PROC-032-29. Date: 2026-06-05.
Developer's words: *"L3 Seam owner is depth-1; the source check does not recurse. => is it safe to forbid
recursion? (also L5)"*

Grounded against Round-1 §3.2 (loopback table) and §5 (lazy-wavefront cascade).
- **L3** = scribble generator can't *source* an entry from the requirement → creates a requ-explore task
  against the **seam-owner** requirement, **depth-1, no recursion**.
- **L5** = cross-requirement UI cascade → **lazy wavefront**, depth-1 *per hop* but advancing hop-by-hop on
  approval, bounded by a visited-set.

The single biggest finding of this report: **L3 and L5 are not the same question and have different
answers.** Lumping them ("also L5") is the trap.

---

## Level 1 — the topic as a whole

### The rationale being pressured
*"Bounding loopbacks to depth-1 / forbidding recursion keeps them finite and cheap; deeper chasing risks
runaway token cost and infinite loops."*

### What speaks against forbidding recursion (the real risk)
A genuine **transitive** gap is missed by a single depth-1 check. Concretely for L3:
> Requirement A's scribble needs an entry that requirement **B** owns (depth-1 → fine, we file against B).
> But B's *own* definition of that entry depends on requirement **C** (depth-2). The depth-1 source-check
> against B will not discover the C-gap.

If nothing else catches the C-gap, forbidding recursion is unsafe.

### Why it is nonetheless safe at L3 — the reframing
The recursion is **not eliminated; it is relocated to the task graph.** Under PROP-9 coverage, **every**
Presentation requirement gets its own scribble task and its own depth-1 source-check. So C's gap is found
**when C's own scribble runs.** Depth-1-per-task × universal-coverage ⇒ the *transitive closure* is achieved
**across tasks**, not inside one check. The wavefront of source-checks marches over the whole requirement set
exactly once; each does one hop; together they cover all hops.

> **L3 no-recursion is safe iff coverage is complete.** The single check doesn't recurse because the *set of
> checks* does the recursing.

This converts a scary "we forbid recursion" into a precise, provable claim with one explicit precondition.

### What this demands we add
- **An asserted precondition:** the SCI/coverage audit MUST assert that *no Presentation requirement lacks a
  source-check* (i.e. PROP-9 coverage is 100% before the gate releases). If coverage can be partial, the
  no-recursion rule silently leaks transitive gaps. Make the dependency explicit in the requirement, not
  implicit in two skills that each assume the other is total.
- **A diagnostic when a seam-owner is itself incomplete:** when L3 files against B and B's scribble later
  *also* fires an L3 against C, that is the transitive case resolving correctly — but it should be *logged as
  a chain* (A→B→C) so a pathologically deep chain is visible to the developer rather than silent.

### L5 is a different animal — do NOT apply the L3 answer to it
L5 **does not forbid recursion.** The lazy-wavefront cascade is *intentionally* recursive: a refreshed
scribble that changes its own outward entry surface enqueues its depth-1 dependents, who may enqueue theirs,
hop by hop. The depth-1 is per *hop*, not a global stop. So the L3 safety argument (universal coverage)
**doesn't apply** — there is no "every requirement runs once" guarantee here; a single edit drives the wave.

L5's real questions are:
1. **Termination** — already solved: the visited-set (keyed on cascade origin) prevents re-enqueue, and most
   refreshes are entry-context-only and don't move the dependent's *own* outward surface, so branches die.
   No infinite loop. (Round-1 §5.2.)
2. **Blast-radius / width** — **un-solved and flagged in Round-1 §10.** A single dashboard edit *could*
   fan out to many dependents in one wave. Correctness is fine (each refresh is correct); the concern is a
   surprise mass of auto-created tasks. **The substrate already named this exact danger in its own words:**
   PROP-11 **G3** (the *basis*-resolution depth-1 guard) chose depth-1 precisely because *"brownfield would
   otherwise spawn a blocking wave,"* and PROP-10 states the governing principle — *"bounded recovery; never
   unbounded auto-create."* So the width-breaker below is not a new invention; it is honouring a principle the
   substrate already committed to, at the one loopback (L5) where it was left unenforced.

### A grounding note: there are *three* depth-1 guards, not two — don't conflate them either
The substrate actually has three distinct depth-1 mechanisms, and they must not be merged:
- **G3 (PROP-11 R3) — basis ordering.** "Block on the **direct** opener only (depth-1), never the transitive
  upstream chain." *Forbids* recursion. Safe by the same logic as L3: the transitive chain is covered because
  every opener is itself a scribble with its own basis resolution.
- **L3 — requirement-source check.** *Forbids* recursion (this report's main subject). Safe iff coverage.
- **L5 — cross-requirement cascade.** *Allows* recursion (lazy multi-hop). Safe on termination (visited-set);
  width still needs the breaker.
Pattern: the two *forbidding* guards (G3, L3) are safe because universal coverage runs the recursion at the
task-graph level; the one *allowing* guard (L5) needs the width breaker because no coverage guarantee bounds
its fan-out.

### What L5 demands we add
- **A width circuit-breaker.** PROP-10's own principle is "bounded recovery; never unbounded auto-create."
  Honour it literally: if a cascade's cumulative dependent count exceeds a threshold **N**, stop
  auto-creating refresh tasks and **escalate to the developer** (same shape as the v6 auto-review fatigue
  breaker). This turns the "unmeasured width" residual into a *safe, escalating* bound rather than an
  unbounded surprise.
- **Make N configurable and logged**, and have the breaker emit the wave so far (the dependency sub-graph it
  walked) so the developer escalation is actionable, not just "too big."

### The synthesis
| Loopback | Recursion? | Safety mechanism | What to add |
|----------|-----------|------------------|-------------|
| **L3** (seam-owner source check) | **Forbidden** within a check | Universal coverage runs the recursion at task-graph level | Assert 100% coverage as a precondition; log A→B→C chains |
| **L5** (cross-requirement cascade) | **Allowed**, lazy multi-hop | Visited-set (termination) | Width circuit-breaker at N dependents → escalate |

---

## Level 2 — chapter by chapter

### "Seam owner is depth-1"
- **Pressure:** depth-1 is correct only if the seam-owner's *own* dependencies are covered elsewhere.
- **Verdict:** correct, *given* coverage. The seam-owner is the right depth-1 target (it owns the entry); its
  transitive deps are other requirements' responsibility.

### "the source check does not recurse"
- **Pressure:** sounds like transitive gaps are dropped.
- **Verdict:** they are not — they are deferred to the gap-owner's own scribble task. The recursion lives in
  the *set* of source-checks. Reframe in the docs from "does not recurse" to "recurses across tasks, not
  within a check." This wording change prevents a future maintainer from 'fixing' it by adding intra-check
  recursion (which would re-centralise and duplicate work).

### "=> is it safe to forbid recursion?"
- **Pressure:** the honest answer is *conditionally*.
- **Verdict:** **safe iff PROP-9 coverage is complete.** Add the coverage assertion as the explicit
  precondition. Without it, unsafe. With it, provably safe.

### "(also L5)"
- **Pressure:** this is the assumption to break. L5 ≠ L3.
- **Verdict:** L5 *is* recursive by design; the question is not "is depth-1 enough" but "does the wave
  terminate and how wide does it get." Termination: solved (visited-set). Width: add a circuit-breaker.

---

## Residual uncertainty (honest)
- **Coverage completeness is the load-bearing assumption for L3.** If, in practice, some Presentation
  requirements legitimately have no scribble (e.g. a requirement that only constrains backend behaviour but
  is tagged Presentation by accident), the coverage assertion will false-positive and block the gate. We need
  a clean definition of "Presentation requirement that must have a scribble" vs. "tagged Presentation but
  has no UI surface" — the `--scope presentation/code` separability problem (Round-1 §10) resurfaces here.
- **The width threshold N is unmeasured.** We can't set a good N until a real cross-feature edit (the
  dashboard case) runs — the same empirical gap as Round-1 §10's "wave width unmeasured." Until then N is a
  guess; the breaker's *existence* is the safety guarantee, the *value* is tunable. This is another argument
  for the T2 fixture being engineered to actually produce a cascade so N can be observed.
- **Deep L3 chains (A→B→C→…) are possible in principle** even if each step is depth-1. The chain-logging
  diagnostic surfaces them but there is no hard bound on chain length; a degenerate requirement graph could
  produce a long chain of source-gaps. Probably rare, but unbounded — worth a soft alert at chain length > k.
