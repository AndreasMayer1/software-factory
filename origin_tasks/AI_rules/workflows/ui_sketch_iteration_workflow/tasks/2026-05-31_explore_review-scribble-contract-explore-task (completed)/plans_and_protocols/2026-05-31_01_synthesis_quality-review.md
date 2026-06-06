# Quality Review of TASK-PROC-032-10 — Synthesis

**Task:** TASK-PROC-032-16 · **Date:** 2026-05-31 · **Model:** Opus 4.8
**Reviewed corpus:** all 18 files in TASK-PROC-032-10's `plans_and_protocols/` (00–17), TASK-PROC-032-10's `goal.md`, the 8 derived impl `goal.md` files (TASK-PROC-032-11..-19) + the verify task (-20), the encoded ACs in REQ-PROC-032 (AC-21..AC-36), and on-disk ground truth (skills, agents, schemas, scribble location).

> Method: read the corpus in order (the work is cumulative; early synthesis was revised repeatedly), then compared the consolidation (file 16) + task-creation plan (file 17) against the actual ACs and impl tasks, then traced every *adopted* decision (D1–D47) to either an AC, an impl task, an existing artifact, or "nowhere". Verdict is calibrated, not generous.

---

## 0. Bottom line

TASK-PROC-032-10 was an **analytically excellent, executionally leaky** exploration.

- **Q1 and Q2 were answered well** (Section 1). The iteration-1 synthesis alone essentially solved both; the reframe of Q2 from "1:1 vs wireframe" to a **contract-locality problem** is the single most valuable insight and it survived to the shipped ACs.
- **The exploration's reach far exceeded its mandate.** It spawned an entire REQ-PROC-044 program (skill-interface contracts) and the scribble skill/agent split — both genuinely valuable, both now shipped. That is a strength *and* the root of the main weakness.
- **The main weakness is convergence.** Decisions inflated D1→D47 across 6 iterations + 2 analysis docs; the LLM repeatedly recommended *more* (Position C, three agents, seed-all-11-tasks) and the **user**, not the LLM, was the convergence mechanism every time.
- **The most serious defect: the final distillation silently dropped several explicitly user-adopted decisions** (Section 4). The consolidation (file 16) and task plan (file 17) narrowed to the "content bundles" and let go of the scribble-location migration, `flow_navigation.yaml`, per-flow walk validation, `APPROVAL_TRAIL`, the contributing-requirements *discovery mechanism*, and DOMAIN-VOCAB — without flagging the loss, while presenting the plan as the complete remainder.
- **Net for the impl tasks: executing all 8+1 as written will NOT produce the complete workflow the exploration designed** (Section 8). It will deliver the explicit content-contract + 5 feature bundles. It will leave the multi-requirement/multi-flow aggregation problem — the strand the user spent the *most* energy on — unsolved, and it references a skill (`claude-modify-agent`) that does not exist.

---

## 1. Seed 1 — Were Q1 and Q2 fully answered?

**Both: YES, and well-grounded.**

**Q1 (Han UX-review adoption).** Clear answer reached: **inspirational port of protocol seeds, no agent import.** Grounded in (a) reading Han's actual `user-experience-designer.md` verbatim, (b) the prior TASK-PROC-055-01 plugin-level verdict, (c) a concrete overlap matrix showing five genuinely-missing lenses (Critical Inquiry, Nielsen, Affordance/Microinteractions, Dark Patterns, Motion-as-Function). This is the kind of evidence-anchored answer the goal asked for. It shipped: `doc/presentation/heuristics/` exists with exactly those five lenses, consumed by `ui-scribble-heuristics-reviewer`.

**Q2 (scribble–coder contract).** Clear answer reached and it is the exploration's best work: the contract is **not** a "1:1 vs wireframe-only" question but a **contract-locality** problem — the contract was authored but scattered across six artifacts and never reached the coder in one piece. The L1–L15 / D1–D8 split, surfaced at three boundaries (B1–B5), is precise and shipped as AC-21..AC-27. The web-research refinements (L8 named-token reference, L15 a11y-intent-locked) are well-justified and landed in AC-26.

No deferral of either question. The four explore ACs on TASK-PROC-032-10 are genuinely met.

---

## 2. Seed 2 — Did the six iterations build on each other?

**Mostly yes, but with a convergence problem the LLM did not own.**

- Each iteration *did* advance: iteration 1 answered Q1/Q2; iteration 2 mapped feedback→proposals; iteration 3 absorbed Position-A reversal + spun off `claude-create-agent`; iteration 4 folded in the skill-interface meta-exploration + scribble-location; iteration 5 *narrowed* (dropped D41/D42 after a real audit, re-parented under existing REQ-PROC-044); iteration 6 reconciled with the shipped REQ-PROC-044 program. There was little gratuitous restatement.
- **But iteration 3 explicitly declared itself the "final pass" with a 9-bundle plan** — then the task ran three more iterations, two analysis documents, and a multi-week block. The expansion was **user-driven** ("another iteration", "still in exploration mood"), which is to the LLM's credit for responsiveness — but it also reveals that the LLM's own convergence signal was unreliable: it declared done while the problem space was still actively growing.
- **Decision inflation is real:** D1→D47. The LLM's *default recommendation was almost always to expand* (adopt Position C tiered locks; build three named agents; seed all 11 tasks immediately; adopt 6 of 8 new ideation candidates). The user reversed the big ones every time (Position A not C; one task not eleven; do infrastructure first). A well-calibrated exploration would have surfaced the expansionary options but defaulted to the minimal one.

Where it gained the most ground: **iteration 1** (the contract-locality reframe) and **iteration 5** (the narrowing — frontmatter audit dropping D41/D42, re-using `requirements_matrix.md`, parenting under existing REQ-PROC-044 instead of inventing a requirement). Those two are the high-water marks.

---

## 3. Seed 3 / Seed 5 — Seven seeds + web-research integration

**Seven seeds (TASK-PROC-032-10 goal):** all explored in iteration 1. Seed 7 ("contract gap as a bug") was answered concretely (F4: the impossible-state-screens bug from TASK-PROC-032-08 *was* a contract-ambiguity failure). Seeds 5–6 ("contract-explicit shape" / "minimum fidelity") produced the L/D lists. No seed was untouched.

**Web research (file 02):** **genuinely integrated, not collected-and-shelved.** Two concrete refinements — R1 (L8: literal `48px` → named token reference) and R2 (split accessibility: intent locked, implementation deferred → L15) — came directly from the survey and **both shipped in AC-26**. Confidence was honestly graded (high on the locked/deferred core, medium on inline-vs-sibling token catalogues) and the one outlier (Stitch's inline hex) was named and rejected with reason. This is exemplary research integration.

Contrast: the *skill-interface* web research (file 08 §2, ≤6 fetches) was thinner. The LLM's own §6 and the user both flagged it as incomplete; the correct move (taken) was to de-weight it and require NEW-EXPLORATION to validate via prototype. Good handling of a weak input.

---

## 4. Seed 4 — Lost material (the most important finding)

Tracing every *adopted* decision to an AC / task / artifact / nowhere reveals that the requ-explore→derive pass (commit `6886298f`) encoded the **content** decisions (Q1/Q2 + 5 features = AC-21..AC-36) but **dropped a coherent strand of explicitly-adopted, user-prioritised decisions**. Verified on disk (grep returns zero footprint unless noted):

| Lost / orphaned decision | Source | User stance | On disk today |
|---|---|---|---|
| **Scribble location → `requirements_tasks/scribbles/` mirroring `lib/features/`** (D33–D36) | file 07 (explicit), iteration 4 §2 | **Strong explicit directive** ("I'd prefer… enforce it to a *must*") | **NOT done** — scribbles still at old `…/feat_therapist_transfer_ui/scribbles/`; `requirements_tasks/scribbles/` does not exist. No AC, no task. |
| **`flow_navigation.yaml`** per-flow nav graph (D20) | iteration 3 §4.4 | Adopted ("Q2-CONTRACT deliverable") | **Zero references** anywhere. No AC, no task. |
| **Per-flow walk validation + human walk instructions** (D39, iter4 §5.2, iter5 §5.1) | file 07 (explicit) | Adopted | **Zero references** in any `ui-scribble-*` skill/agent. No AC. |
| **`APPROVAL_TRAIL.md`** approval-decision aggregator (D43 / 6.1) | iteration 3 §6.1 | **"yes, do it"** (twice; "proved very helpful" for flows) | **Zero references.** No AC, no task. |
| **contributing_requirements / participating_flows *discovery mechanism*** (D29, D30, D40) — the multi-requirement aggregation problem | files 05+07 (most-discussed strand) | Adopted; auto-discovery script + parity lint | **Partial:** fields exist in `.claude/schemas/scribble_metadata.yaml`, but **no discovery script, no parity lint, no skill wiring, no AC.** |
| **DOMAIN-VOCAB** — Domain Vocabulary + Anti-Patterns on the 6 existing agents (D9) | iteration 1 §8.2 | "Adopt as standalone" | **Not done** — none of the 6 agents has a `## Domain Vocabulary`. Legitimately outside REQ-PROC-032, but **homed in no task anywhere** (status untracked). |

**Why this matters:** the multi-requirement / multi-flow / scribble-location strand is the work the **user invested the most feedback energy in** (two long rounds, files 05 and 07 — "who decides the main use case?", "is the skill able to find ALL relevant requirements?", "place scribbles mirroring lib/features"). It addresses a real, named risk (a screen embodies several requirements; the generator must see all of them). The consolidation quietly let it go. The verify task (032-20) audits only AC-21..36, so **the lost material is invisible to the verification gate too** — nothing in the plan will detect that it's missing.

This is not "the plan is wrong"; it is "the plan is presented as complete and is not." That gap between confidence and completeness is the defect to fix before implementation begins.

---

## 5. Seed 6 — Honest quality assessment (where the reasoning was strong vs weak)

**Strong / well-grounded:**
- The contract-locality reframe (iteration 1 §2) — earned, not asserted.
- Honest-uncertainty sections in every iteration; the frontmatter audit that *dropped* D41/D42 rather than adding fields (iteration 5 §3) — exactly the discipline the user asked for.
- Re-parenting under the existing REQ-PROC-044 instead of minting REQ-PROC-TBD (iteration 5 §2) — avoided duplicate-requirement sprawl.
- Web-research integration (Section 3 above).
- The PROVISIONAL flag deliberately left in the heuristics corpus as a tripwire pointing back at the needed reconciliation — a nice "the code points at its own missing step" move.

**Weak / should be questioned:**
- **Expansionary default (Section 2).** The LLM's recommendations skewed consistently toward more scope; the user was the brake. An exploration should be its own brake.
- **No YAGNI re-check of the plan.** The redundancy check (file 10) is honest that it *only* asked "do any two items overlap?" and explicitly **did not** ask "should each item exist at all?" (file 10 §12). Across 10 redundancy candidates it found exactly **one** real collapse and zero drops — a suspiciously self-validating result for a 47-decision plan. A genuine adversarial pass would likely have collapsed or cut more.
- **High confidence in a flagged-incomplete input.** The meta-exploration agent's thin findings (file 08) were strong enough to *launch an entire REQ-PROC-044 program* — which did ship well, so this paid off, but the bet was larger than the evidence at the time warranted.
- **The consolidation over-claimed completeness** (Section 4) — the deepest reasoning failure: confident framing ("Path 1 keeps the Q1/Q2 substance"; "All 16 ACs covered… No circular dependencies") masking a silent scope contraction.

---

## 6. Seed 7 — What the ideal version would have done

1. **Closed Q1/Q2 in ~2 iterations** (iteration 1 nearly did) and stopped, since both were answered.
2. **Maintained one authoritative decision ledger that tracked every adopted decision to a destination** (AC / task / existing artifact / explicitly-deferred-with-trigger). Then nothing could silently vanish between iteration 4 and file 17. This single discipline would have prevented the Section-4 loss.
3. **Split the spun-off mega-threads cleanly at birth.** Three distinct problems got tangled: (a) the scribble *content* contract (the actual question), (b) skill-interface contracts (→ REQ-PROC-044, correctly spun off), and (c) scribble *location* + `lib/features` structure policy (left dangling). Thread (c) deserved its own scoped task with an explicit owner; instead it evaporated.
4. **Run a YAGNI/adversarial cut before seeding**, not only an overlap check.

Is the current output sufficient to build on? **For the core Q1/Q2 content contract: yes** — AC-21..AC-27 are clean and shippable. **For "the complete scribble workflow the exploration designed": no** — the Section-4 strand must be recovered first (or consciously killed), and the `claude-modify-agent` reference must be fixed.

---

## 7. Seed 8 — Will the impl tasks, executed as written, deliver a correct & complete workflow?

**No — improved, but neither complete nor fully executable as written.** Two classes of problem:

**(A) Broken reference — will stall execution.**
- 5 derived goal.md files (TASK-PROC-032-11, -12, -13, -14, -19) instruct agent edits "through `claude-modify-agent`"; -19 also references `claude-create-agent`. **Neither skill exists.** Agent-creation/modification guidance was folded into `claude-create-skill`/`claude-modify-skill` (REQ-PROC-044 FU-6 / 044-08) — which *contradicts* the user's explicit approval of standalone `claude-create-agent`+`claude-modify-agent` (file 14, "Option B… yes"). So: a user-approved deliverable was silently replaced by a fold-in, **and** the downstream tasks still point at the non-existent standalone skill. An implementer will hit a dead reference.

**(B) Missing scope — will leave designed gaps.** Even if all 8 impl + 1 verify run perfectly, the workflow will lack: scribble-location migration (D33-36), `flow_navigation.yaml` (D20), per-flow walk validation (D39), `APPROVAL_TRAIL` (D43), the contributing-requirements *discovery mechanism* (D29/D30/D40), and DOMAIN-VOCAB (D9). The multi-requirement/multi-flow aggregation problem — the user's most-emphasised concern — remains unsolved.

**What is genuinely good about the tasks:** the AC-21..AC-27 content contract is precisely specified (CONTRACT BLOCK dual framing, L8 token-reference fix, a11y intent, rule-audit trace, Sketch-Gate + verifier anchoring); dependency ordering is correct (consumers after doctrine; visual-validate after doctrine; verify after all); the R3 collapse (verification_seeds inside flutter_handoff) is honored in AC-36. The five feature tasks (breakpoints, inspiration, pre-brief, cross-feature, visual-validate) faithfully carry file 17's notes.

---

## 8. Recommendation (for the pending-feedback decision)

The exploration's *analysis* is sound and the *content* tasks are largely shippable. The required corrections before implementation are bounded:

1. **Recover or consciously kill the lost strand** (Section 4). Either (a) a short `requ-explore` top-up on REQ-PROC-032 that adds ACs for scribble-location migration, `flow_navigation.yaml`, per-flow walk validation, contributing-requirements discovery, and `APPROVAL_TRAIL`, then derives the matching tasks — or (b) an explicit decision to defer/drop each, recorded with a trigger, so nothing is *silently* missing.
2. **Fix the `claude-modify-agent` / `claude-create-agent` references** in the 5 tasks → point at the actual `claude-modify-skill`/`claude-create-skill` (whichever the 044-08 fold made canonical), OR create the standalone skills the user approved. Decide which, then make the tasks consistent.
3. **Home DOMAIN-VOCAB (D9)** in a task somewhere (it belongs outside REQ-PROC-032 — likely under the agent-infrastructure requirement), or record it as dropped.
4. **Widen the verify task (032-20)** so it also checks for the recovered strand, not just AC-21..36 — otherwise the verification cannot catch the very gaps identified here.

If the user prefers, the minimal path is: accept AC-21..AC-36 tasks as-is for the core contract, fix (2), and treat (1)/(3) as a separate explicitly-scoped follow-up rather than blocking the content work.

---

## 9. What remains uncertain

- Whether the scribble-location migration and `flow_navigation.yaml` were *intentionally* dropped (a judgment that they're lower priority than the content contract) or *accidentally* lost. The corpus shows them adopted and then never mentioned again after iteration 4 — which reads as accidental, but only the developer can confirm intent.
- Whether `claude-create-agent`/`claude-modify-agent` were deliberately superseded by the 044-08 fold (in which case the user's file-14 approval was overridden — possibly with the user's later assent that isn't in this corpus) or simply never built.
- Whether DOMAIN-VOCAB was tasked under another requirement outside the slice I inspected.
