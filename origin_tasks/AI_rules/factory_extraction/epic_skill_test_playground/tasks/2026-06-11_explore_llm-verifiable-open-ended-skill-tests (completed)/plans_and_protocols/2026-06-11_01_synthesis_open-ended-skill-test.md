# Synthesis — An LLM-verifiable test for open-ended skills

Task: TASK-PROC-068-01 · refines REQ-PROC-068 **AC-04** for the no-golden-answer case.
Session: ecaffbbb (Opus, automated). Status: synthesis round 1 complete; awaiting developer
approval of the requirement-shaping decision (see §10).

> Read alongside `2026-06-11_00_user_initial_input.md`. This is round-1 synthesis; it defines
> the problem space in terms not fully known at task creation and frames the decisions the
> developer must make.

---

## 0. Material read (audit trail)

- Epic REQ-PROC-068 + its AC-04 ("run_instructions file + non-boolean quality-scale outcome
  rubric the six probes feed").
- feat_measurement_instrumentation REQ-PROC-068-05 — the **six probes** (stall report, cascade
  log, salvage diff, fixture↔release behaviour log, facet-tag audit, graph-stats dump).
- ideation-start SKILL.md (5 phases: GATHER → ANALYZE → IDEATE/diverge → SYNTHESIZE → REPORT;
  mid-run + end-of-run gates; ledger YAML; criteria/topic-class/persona-binding/phase-tiers;
  recovery ladder; index_session).
- Deterministic post-checks: `scripts/ideation/diverge_postcheck.py`,
  `recompose_postcheck.py`, `soundness.py`, `decomposition.validate_tree`.
- Two live ideation test-run ledgers (the goal's material):
  - `…/2026-06-09_explore_skill-test-playground-full-scope/…_001_ideation_ledger.yaml` (~109 ideas, 6 frames)
  - `…/2026-06-09_explore_brownfield-layer-derivation-mechanism/…_001_ideation_ledger.yaml` (~167 ideas, 6 frames)

---

## 1. Core principle — assert on process & internal consistency, never on content correctness

The wall: open-ended skills (ideation, requ-explore, product-intake) produce outputs with **no
single correct answer**. Two valid ideation runs on one topic produce different ledgers;
output-equality is meaningless.

**Resolution:** an open-ended-skill test asserts on (a) **the process the skill ran** and
(b) **the internal consistency of the artifact it produced** — never on whether the produced
idea/answer is "right." *"Is this the right idea?"* is the human's job at the gate; the test asks
*"did the skill explore widely, score coherently, and represent itself honestly?"* Any candidate
criterion that secretly asserts content correctness is rejected.

This reframes "test a skill" from "verify the output" to "verify the skill did its job well,
whatever output it reached."

---

## 2. Four-layer test architecture (generalises beyond ideation)

| Layer | What | Mechanism | Cost |
|---|---|---|---|
| **L1 Structural invariants** | did the skill emit the artifacts it must, with valid structure? | deterministic scripts (no LLM) | cheap; hard pass/fail; runs first as a precondition gate |
| **L2 Quality rubric** | are the topic-invariant quality dimensions met? | LLM-as-judge, 1–5 anchored | medium; result is "quality ≥ threshold", not correct/incorrect |
| **L3 Golden-trace regression** | is a changed skill at least as good as a frozen reference, and did the intended improvement appear? | LLM judge new-vs-reference | medium; runs on skill change |
| **L4 Gate persona-walk** | is the human-in-the-loop gate good enough to decide from? | LLM developer-persona judge | medium; bridges to TASK-PROC-069-05 |

The LLM judge (L2–L4) **starts only where the deterministic checks (L1) stop.**

---

## 3. L1 — deterministic structural invariants for ideation (already exist)

Inventory of what the ideation post-checks already decide with no LLM — the test reuses these
as a boolean precondition gate:

- `diverge_postcheck`: `min_ideas` quota met; every declared frame covered; all 6 canonical
  divergence techniques present.
- `recompose_postcheck`: integration guard, original-goal guard, de-duplication guard (exact/
  near-exact text).
- `soundness`: no forbidden-pair constraint violations; every solution links to an answered
  (sub)problem; soundness stable (0 ripples).
- `decomposition.validate_tree`: interface contracts present, parents resolve, acyclic.
- Presence checks: criteria panel present with `weight` + `weight_rationale` each;
  `topic_class` + rationale recorded; `persona_frame_binding` recorded; gate render produced;
  index appended; capped-exit gaps surfaced (not silently dropped).

**Line rule:** if a script can decide it from the ledger, it is L1. The LLM is used only where
judgment is irreducible.

---

## 4. L2 — the rubric dimensions for ideation (anchored 1–5, judged)

Each dimension is (a) invariant across topics, (b) grounded in a concrete failure a real run
could exhibit, (c) not a content-correctness assertion, (d) starts where L1 stops. The judge
**must cite specific ledger rows** for every score (grounding requirement).

**D1 — Frame-lens fidelity.** L1 counts ideas per frame; D1 judges whether ideas under each
frame are *genuinely expressed through that frame's lens* or generic ideas tagged to fill quota.
- 1: frame-labeled but no frame-specific lens (quota gaming).
- 3: most frames show their lens; 1–2 thin/generic.
- 5: every frame visibly shapes its ideas; the non-obvious + cross-domain frames yield ideas the
  role frames could not have.
- Catches: 6 frames "covered" by count while the cross-domain frame shows no analogical distance.

**D2 — Divergent non-redundancy (semantic).** L1 dedups exact text; D2 judges semantic
clustering across the pool.
- 1: large redundant clusters; effective diversity ≪ raw count.
- 3: some clustering; most ideas distinct.
- 5: ideas mutually distinct; high effective diversity relative to count.
- Catches: 109/167 ideas collapsing to ~20 distinct ideas — high count masking low diversity.

**D3 — Criteria soundness.** L1 checks criteria present with weight+rationale; D3 judges whether
they discriminate the problem, are non-overlapping, and weights are justified by the rationale.
- 1: generic/overlapping criteria; weights unjustified.
- 3: criteria fit the problem; most weights justified; minor overlap.
- 5: criteria discriminate cleanly, non-overlapping, each weight traceable to a problem-grounded
  rationale.
- Catches: every criterion weighted 0.5 "because important"; two criteria measuring one thing.

**D4 — Synthesis fidelity.** L1 checks structural links exist; D4 judges whether the viable set
traces to *high-scoring* ideas under the stated criteria and the winner rationale is faithful to
the scores (no cherry-picking).
- 1: viable set does not follow from scores; rationale contradicts ledger.
- 3: broadly follows; rationale mostly faithful.
- 5: viable set is exactly the high-scoring criteria-justified subset; rationale traceable
  line-by-line to ledger scores.

**D5 — Gate honesty (load-bearing).** Judges whether the mid-run gate render (the HTML the
developer sees) *faithfully represents the ledger* — surfacing viable-set collapse, low
diversity, capped gaps, and weak criteria rather than flattering itself.
- 1: gate misrepresents ledger (hides collapse/gaps/weakness).
- 3: represents main state; weaknesses understated.
- 5: faithfully surfaces every weakness the ledger contains, actionably.
- This is self-representation honesty — distinct from L4 (sufficiency).

**D6 (optional) — Recovery honesty.** Did the skill run the recovery ladder on viable-set
collapse and report the disposition honestly rather than reporting a lone winner?

---

## 5. Deterministic vs judged — the clean cut

| Property | Mechanism |
|---|---|
| artifacts present (ledger, criteria, gate render, index) | **deterministic** |
| frame × technique × quota counts | **deterministic** |
| structural links (solution→answer, tree contracts) | **deterministic** |
| exact/near-exact dedup | **deterministic** |
| capped-exit gaps surfaced | **deterministic** |
| frame-lens fidelity (D1) | judged |
| semantic non-redundancy (D2) | judged |
| criteria discrimination & weight justification (D3) | judged |
| score→selection fidelity (D4) | judged |
| gate self-representation honesty (D5) | judged |

---

## 6. L3 — golden-trace regression without a golden answer

Freeze a reference run for fixed `(topic, effort, frame set, model id, seed/temperature)`. The
seed is a **best-effort anchor, not a guarantee** — LLM nondeterminism means even an unchanged
skill produces a slightly different run (stated limit §9).

The reference is **never asserted on by equality.** It is a **quality floor.** On a skill change
the harness re-runs and gives an LLM judge `(reference ledger+gate, new ledger+gate, the
intended-improvement text from the change's task)` and asks two questions:
1. **Non-regression:** is the new run at least as good as the reference on each of D1–D5?
   (per-dimension; a drop is a *flag for human review*, not an auto-fail.)
2. **Intended-improvement presence:** does the stated improvement actually appear *and get
   applied*, not merely added? (e.g. "added connotation-safety criterion for naming topics" →
   judge checks it is present **and meaningfully applied**.)

This catches regressions with no correct answer: the reference bounds quality, not output.

---

## 7. L4 — testing the human gate via a persona judge (bridge to TASK-PROC-069-05)

Part of an open-ended skill's value IS the gate. For an automated test, an LLM plays a developer
persona walking the **mid-run gate** and scores **interaction quality**, not the final artifact:
given the rendered gate (HTML ledger + criteria/scope panels + enumerated options), it asks
*"could I, as this developer, make a good APPROVE/ITERATE decision from what's shown? Is anything
I'd need buried, missing, or misrepresented?"* → interaction-quality 1–5 + the specific
decision-relevant info missing/surfaced.

**Relation to the two gate dimensions:** D5 = "does the gate tell the truth about the ledger?";
L4 persona-walk = "is the truth it tells *enough* to decide?". Complementary.

**Bridge:** TASK-PROC-069-05 (interactive_required venue axis) routes *genuinely* interactive
runs to a human venue. 068-01's persona-judge is the **automated stand-in** for that human,
scoring the gate's quality of disclosure. The two meet exactly at "test the gate."

---

## 8. Feeding the six probes & AC-04's run_instructions+rubric format — KEY FINDING

AC-04 says the test carries a `run_instructions` file + a non-boolean rubric "the six probes
feed." Mapping the six probes (REQ-PROC-068-05) onto an open-ended-skill rubric:

- **#6 graph-stats dump** (per-frame idea counts) → feeds D1/D2 inputs. ✅ direct.
- **#1 stall report, #2 cascade log, #3 salvage diff, #4 fixture↔release log, #5 facet-tag
  audit** → these are about the **release / scribble-cascade workflow**, *not* about an
  open-ended skill's quality. They do not feed an ideation rubric.

**Finding: AC-04 conflates two probe families.** The six probes were designed for the
scribble-gate / release-cascade validation. An open-ended-skill test needs its **own** small
evidence set — call them **rubric-evidence artifacts**, emitted by the skill run:
(a) ledger snapshot at the gate, (b) the gate render, (c) the deterministic post-check report
(L1), (d) per-dimension judge scores with cited ledger rows (L2). These are NOT the six
release-cascade probes.

run_instructions for an open-ended skill = fixed `(topic, effort, frames, seed)` + the invoke
command on the harness + the expected artifacts to collect. outcome rubric = L1 boolean gate +
L2 anchored D1–D5(+D6) + L3 golden-trace comparison (when a reference exists) + L4 persona-gate
score.

---

## 9. Judge-reliability limits & what stays unmeasurable (honest)

- LLM-judge scores have variance; anchored levels reduce but don't eliminate inter-judge
  disagreement. Mitigations: concrete anchors; require the judge to **cite ledger rows** per
  score; treat scores as **bands/thresholds**, not exact values; spot-check inter-judge stability
  (run the judge ≥2× on the reference — large disagreement ⇒ the anchor is too vague ⇒ tighten).
- Golden-trace seed is best-effort; the judge must distinguish "different but equally good" from
  "regressed."
- **Content correctness is unmeasurable by design** — whether the idea/requirement is *the right
  one* is the human's call at the gate; the test deliberately does not touch it.
- The persona-judge **approximates** a developer; it scores disclosure quality, not whether a
  real human would actually decide well.

---

## 10. Generality & the requirement-shaping DECISION (needs developer input)

**Generality:** the four-layer scaffold (L1 deterministic → L2 anchored rubric → L3 golden-trace
→ L4 persona-gate) is **reusable for other open-ended skills**; only the L2 *dimensions* are
skill-specific.
- requ-explore: L1 = schema-valid requirement, ACs present, end-state-language gate; L2 = are
  ACs genuinely end-state & non-overlapping? does the requirement trace to the goal?; L4 = the
  location-approval + synthesis-approval gates.
- product-intake: L1 = routing artifact present; L2 = is the routing justified by the
  persona/scenario/flow chain?

**Decisions for the developer (the action this task's ACs require approval on):**

1. **Requirement shape** — Refine **AC-04 in place** to (a) name the four-layer open-ended-skill
   test scaffold, (b) distinguish release-cascade probes (the six) from open-ended-skill
   *rubric-evidence artifacts*, (c) reference the assert-on-process principle —
   **vs.** mint a dedicated **new feature** `feat_open_ended_skill_testing` under REQ-PROC-068
   holding the scaffold + ideation dimension set, with AC-04 cross-referencing it.
   *Recommendation:* refine AC-04 in place **and** add one new sub-AC for the probe-family
   distinction — lightest change consistent with the goal's "refinement, not competing mechanism."
2. **Probe-family distinction** — confirm the §8 finding (six probes ≠ open-ended rubric
   evidence) and whether REQ-PROC-068-05 should note it.
3. **Scaffold documentation** — record the four-layer scaffold as the canonical open-ended-skill
   test pattern (per-skill dimension sets) now, or defer until a second open-ended skill is
   tested.
4. **Next action** — what to perform after approval (e.g. "edit AC-04 + add sub-AC now",
   "create a follow-up impl task to author the ideation rubric file", or "defer").

> This session is automated and cannot edit the requirement before approval (the requirement
> shape is itself decision #1). On approval it performs the stated next action.
