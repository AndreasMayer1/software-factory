# Analysis — Is there a circular dependency between the skill-test playground and layer-derivation / the ralph loop?

**Date:** 2026-06-26 · **Session:** interactive, Opus · **Task:** TASK-PROC-068-01
**Question posed by developer:** layer-derivation and the ralph loop are (believed) needed to
implement the testing playground, yet they aren't built; to build *them* the developer wants a
skill-test mechanism that works **without** the full playground. Is that possible, and how should
the impl tasks be structured?

This file records the **evidence-grounded** answer (the prior session's quick conclusion was an
unverified inference; this corrects it).

## The four concepts, from their authoritative requirement docs

- **REQ-PROC-068 — Skill-Test Playground (substrate).** A small offline media-rating app
  (`test_harness_app/`) the factory *runs on* as a standing test instrument. Core invariants:
  deploy candidate factory → run-as-cwd → git-reset between runs; emit six probes + a non-boolean
  rubric. **Listed dependencies:** web toolchain, structural mirror, execution/assessment protocol,
  tech-agnosticism architecture, extraction (TASK-PROC-066-01). **Neither layer-derivation nor the
  ralph loop is listed.**
- **REQ-PROC-073 — Capability-Testing Oracle.** Tests governed instruction artifacts by running
  them on the playground and judging process + artifact internal-consistency/authoring-quality
  (never content correctness). Tiered: deterministic → anchored rubric → old-vs-new A/B → gate
  persona-walk. Explicitly names **REQ-PROC-071 (layer-derivation) as a *peer* quality loop**
  (completeness/testing/fix-scheduling compose as siblings), **not an input**. Judge calibration
  source = the Human-Judgment Register (REQ-PROC-044-05), *not* layer-derivation.
- **REQ-PROC-071 — Bidirectional Layer Derivation.** Fills middle layers (scenario/flow/requirement/
  task) between fixed anchors. Its **first instantiation was conceived to author the playground's
  hollow middle** (personas + app features known; middle missing) — so the *intended* arrow is
  071 → 068. Status `defined`; the real mechanism is **not built** (current code is a
  control-skeleton with stubbed semantics — TASK-PROC-071-02 is the in-progress remediation-design
  task). Has its **own verification approach**: delete real artifacts in a worktree, diff
  regenerated content against untouched originals as a deterministic oracle.
- **REQ-PROC-065-06 — Perpetuating Task Creation ("ralph loop").** A skill wrapping `task-create`
  that embeds Work-Discovery so each task spawns the next until a termination condition; combined
  with the autonomous orchestrator (REQ-PROC-041) it self-perpetuates. Depends on REQ-PROC-041.
  Has its **own verify tasks** (end-to-end audit + live functional test). Status `defined`.

## The decisive evidence — the feared circularity does not exist

1. **The minimal mechanism is, by design, standalone.** SOL-01 (the developer-accepted design,
   `…/2026-06-24_007_synthesis_playground-deepened.md` §2.1–2.2, §6) builds a worktree-per-invocation
   **walking skeleton** that reuses only **`orchestrate.py::_launch_claude_session`** (L1122, exists)
   + git-worktree (exists) + `test_harness_app/` mirror (partially exists) + the **un-redesigned**
   REQ-PROC-073 oracle run via an LLM matched-pair A/B judge. It uses neither layer-derivation nor
   the ralph loop.
2. **The full playground does NOT hard-depend on layer-derivation.** SOL-01 §5 WI-10 decided
   "**hand-authored minimal-harness fallback as PRIMARY, 071-driven generation later**." 071 is an
   *optional later enhancement* for auto-generating the harness middle, not a build prerequisite.
3. **The full playground does NOT depend on the ralph loop.** It reuses the `_launch_claude_session`
   *primitive* (a REQ-PROC-041 asset), not the perpetuating loop (065-06). REQ-PROC-073: "the
   orchestrator session owns each test run end to end"; the lifecycle trigger is the meta-skills
   (create/modify), not ralph.
4. **Layer-derivation and the ralph loop each already have their own verification** (071-02's
   deterministic diff-against-original oracle; 065-06's end-to-end + live-functional tests). Neither
   needs the skill-test mechanism to be validated.

## Live dependency-graph confirmation (`after:` edges, 2026-06-26)

| Task | status | after: includes 071-02? | reading |
|---|---|---|---|
| TASK-PROC-068-01 (this — oracle design) | in_progress | **no** (`after: []`) | playground/oracle design decoupled from layer-derivation |
| TASK-PROC-066-06 (playground full scope) | **completed** | had it, but completed | design done without waiting on 071 |
| TASK-PROC-066-01 (factory extraction) | pending | **yes** | only **extraction** truly gates on layer-derivation |
| TASK-PROC-071-02 (layer-derivation design) | in_progress | `after: []` | unblocked, ready to run |
| TASK-PROC-065-06-02 (ralph schema) | pending | n/a | ralph chain independent of the playground |

The 071-02 goal claimed all three downstream consumers gate on it; reality: 066-06 completed,
068-01 reconciled to `after: []`, only 066-01 (extraction) still gates. The playground design was
deliberately de-coupled from layer-derivation.

## Conclusion

- **Yes — a skill-test mechanism without the full playground is possible.** It already *is* the
  design's first increment (SOL-01 walking skeleton): standalone, depending on neither
  layer-derivation nor the ralph loop.
- **The motivating circular dependency is not real.** The only hard arrow layer-derivation feeds is
  *extraction* (066-01) and an *optional later* harness-middle-generation enhancement; the ralph
  loop is uncoupled from the playground.
- **Honest nuances:**
  - The skeleton's A/B verdict is **advisory** until judge calibration is satisfied (ADV-01:
    defer/stub/satisfy) and until the paired-fixture floor (SG-03, ~100) is reached. So using it on
    layer-derivation / ralph gives an *advisory cross-check*; their own verify chains remain the
    authoritative gate.
  - Independent reason to build the skeleton first regardless: its **first job is the disproof
    spike** (SOL-01 §6) — a stop-loss gate testing whether the whole 10–100×-cheap, judge-cheaper-
    than-manual premise holds before more is built.

## Implication for sequencing (for developer decision)

The developer's staged plan (minimal mechanism → use on layer-derivation + ralph → then full
playground) is feasible and matches SOL-01's stop-loss philosophy — but the strict ordering is a
*choice driven by "test them with it,"* not a dependency necessity: layer-derivation (071-02 chain)
and ralph (065-06) are independent and can proceed in parallel using their own verification. 071 and
ralph re-enter the playground story later as **enhancements** to the full playground (071-driven
middle generation; ralph-driven autonomous test runs), gated after both exist.

**Scope note:** grounded in the four `requirements.md` + SOL-01 synthesis + the live `after:` graph
(all mutually consistent). Did not exhaustively read the mechanism-detail syntheses (r3 66 KB,
071 blueprint 44 KB, ralph synthesis 24 KB) — the dependency *direction* is settled across the
authoritative sources, but mechanism-level confirmation can be added if the decision needs it.

---

## Optimization: best order for OVERALL QUALITY + MINIMAL developer steering

The developer's real question is not "what do the prerequisites allow" but "what order is best
against the SOL-01 prime lens — minimise developer residual time (gates/steering) AND token cost,
never below the quality/safety floor." Gate-economics facts gathered 2026-06-26:

- **The gate-heavy cost is the DESIGN phase, not the impl chains.** Three tracks each sit behind an
  in-flight explore/design task: 068-01 (this), 071-02, 065-06-08. These are interactive,
  judgment-heavy, gate-rich. The impl/verify chains they emit run largely autonomously.
- **Autonomy substrate already exists** (`orchestrate.py` 171 KB / 75 defs + `claude-autorun`;
  REQ-PROC-041-01 in_progress but usable). A *known, already-derived* chain can be run with few
  steering gates **without** the ralph loop.
- **Ralph (065-06) adds auto-DISCOVERY of the next task**, not autonomous *execution* (that's 041).
  You don't need ralph to run a known chain. Its hard/risky part — not creating busywork/duplicates
  (AC-06/10/18) — is still in design (065-06-08). An immature autonomous discovery loop *increases*
  cleanup steering → negative on the lens until it can be quality-checked.
- **The disproof spike is a stop-loss gate** that can cancel the single largest downstream
  investment (the full 073 oracle + playground build + its judge-calibration manual cost). One
  go/no-go gate that may save an entire chain → highest wasted-work-avoidance per gate.
- **Layer-derivation has DETERMINISTIC verification** (diff regenerated vs untouched originals) →
  cheap, high-confidence, few escalation gates; its backfill is unattended-by-design; and it
  unblocks **extraction (066-01)**, its real consumer. Its leverage on the playground is small
  (hand-authored middle is the decided primary).

### Recommended order (reasoned on the lens, not on prerequisites)

0. **Trim STEP 3 to the stop-loss.** Author only the minimal REQ-PROC-068 substrate slice needed to
   build the spike+skeleton; **defer the full REQ-PROC-073 oracle AC authoring (and its
   archetype-S sign-off gates) until the spike is green.** Don't spend safety sign-off gates on a
   mechanism the stop-loss might cancel. (Trade-off the developer must OK: this defers recording the
   already-designed oracle as formal ACs.)
1. **Disproof spike + walking skeleton first** — cheap, standalone, stop-loss; run under existing
   autorun (few gates). One go/no-go gate gates everything below.
2. **On green → layer-derivation (071-02 → its emitted chain)** — deterministic verify = cheap
   gates; unblocks extraction; backfill unattended. Run the chain under autorun.
3. **Author full 073 oracle + build oracle/full playground** — premise now validated; layer-deriv
   now exists (enables 071-driven harness-middle generation). Judge calibration (HJR) is the main
   manual cost, incurred only post-green.
4. **Ralph loop (065-06) last** — built once the testing mechanism can advisory-check its autonomous
   output and 041 is solid; turned on, it perpetuates the *maximum* remaining work with a safety net.
   Plain autorun covered build-time gates until here, so nothing earlier needed it.

**Convergence:** this is essentially the developer's own staged instinct — but justified by
quality+gate economics (stop-loss first; ralph last because of quality-risk + redundancy with
autorun), NOT by the (non-existent) circular dependency. The one genuine developer call is step 0:
author-full-oracle-now (design completeness, more sign-off gates pre-stop-loss) vs
author-minimal-now / full-on-green (fewer gates spent on a possibly-cancelled mechanism — recommended).

---

## CORRECTION (developer, 2026-06-26): the testing+fixing TAIL is the dominant cost

The analysis above under-weighted a cost the developer named from experience: **complex mechanisms
never reach desired quality in one run.** The expensive phase is not only design gates — it is the
long iterative **test → find bug / quality-problem / overlooked edge-case → fix → re-test** tail.
The ideation workflow is the standing scar: bugs, result-quality problems, and edge cases keep
surfacing long after "implementation."

This *strengthens* "skill-test first," with a better justification than the bootstrap framing:

- A capability-test mechanism is the **standing instrument that compresses that tail** on every
  complex build after it — layer-derivation, ralph, future skills, and the extraction effort.
  Its cost amortises across all of them; layer-derivation and ralph are just the first beneficiaries.
- "Their own verification" is NOT a substitute: layer-derivation's deterministic diff-oracle and
  ralph's functional tests are exactly the *narrow* checks that let ideation's quality problems
  through. The oracle (REQ-PROC-073) judges process + internal-consistency + authoring-quality and
  catches regressions via old-vs-new A/B — the broad net the narrow checks miss.

**The honest tension (apply the developer's own rule to the tester):** the skill-test mechanism is
*itself* a complex mechanism, so it won't reach quality in one run either. Building it first does not
escape the tail — it moves the FIRST tail onto the tester, paid **manually** (no tool exists yet to
automate it). So the load-bearing question is how the tester bootstraps its OWN quality. The design's
answer: **prove it against KNOWN defects** — planted-defect fixtures carrying expected L1–L4 detection
(`IDEA-SP02-37`), the canary self-test (`IDEA-SP03-51`), discriminating_power as a KNOCKOUT floor
(`CR-08`), and the disproof spike as stop-loss.

**Concrete refinement — use a KNOWN ideation defect as the disproof-spike fixture.** Ideation is the
canonical open-ended skill (this task's subject) and already has real, discovered bugs. A spike on a
known ideation defect tests BOTH premises at once: the *cost* premise (catch it cheaper than the
manual review that originally found it) AND the *discrimination* premise (does the oracle actually
catch a defect known to be there). Ideation's known bugs become the planted-defect calibration set
that bootstraps the tester's own quality.

### Revised order (testing-tail-aware)

1. **Disproof spike on a known ideation defect** — stop-loss + first calibration; tests cost AND
   discrimination premises together.
2. **Grow the tester to *discriminating* maturity** (not merely "running") using ideation's known
   bugs as the planted-defect set — verdicts trustworthy-advisory before anything leans on them.
3. **Build layer-derivation + ralph WITH the matured tester** as the tail-slasher (catches their
   bugs/quality/edge-cases cheaply); each reaches quality with a compressed tail.
4. **Full playground enhancements** (071-driven harness-middle generation; ralph-driven autonomy).

Net: the gate count is no longer the headline metric — the **fix-iteration count on every future
complex mechanism** is, and the tester is the lever that lowers it. The stop-loss (step 1) still
protects the downside: if the spike shows the oracle can't catch a known defect cheaper than manual,
fall back to manual testing for layer-derivation/ralph and skip the rest of the playground build.
