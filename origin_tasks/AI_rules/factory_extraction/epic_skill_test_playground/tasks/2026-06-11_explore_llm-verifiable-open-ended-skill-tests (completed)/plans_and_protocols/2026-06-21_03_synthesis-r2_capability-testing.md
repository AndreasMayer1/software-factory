# Synthesis round 2 — Capability-artifact testing (skills AND agents)

Task TASK-PROC-068-01. Supersedes the *scope* of round-1 (`…_01_synthesis_…`) per four
developer directives given interactively on 2026-06-21. Round-1's four-layer rubric still holds;
this round broadens the unit-under-test, makes the playground interface explicit, fixes the
regression baseline, and embeds the whole thing into the capability lifecycle.

Inputs folded in:
- Round-1 synthesis (`…_01_…`) — the four-layer rubric + ideation dimensions + honest limits.
- External prior art (lens reading `…_02_…`; **raw originals** in `sources/`):
  agentskills.io evaluating-skills + Anthropic `skill-creator` plugin (21 files verbatim).
- Developer directives (2026-06-21):
  - **D-i** the concept must make the **interface to the playground** explicit for skills/agents
    that need **project artifacts** to run.
  - **D-ii** it must **embed into the existing skill create/modify workflow**.
  - **D-iii** **agents** also contain rules — they must be testable too.
  - **D-iv** the comparison is **old-version vs new-version A/B**, NOT skill-creator's
    "no-skill vs new-skill" marginal-value baseline.

---

## 1. The unit under test broadens: a "capability artifact" = skill OR agent (D-iii)

Skills and agents are both **governed instruction artifacts**: text that shapes an LLM's
behaviour, authored only through governed meta-skills (REQ-PROC-044-01 owns
`claude-create-skill`/`-modify-skill`/`claude-create-agent`/`-modify-agent`). They are tested by
the **same scaffold**, with two artifact-shaped specialisations:

| | Skill | Agent |
|---|---|---|
| execution | runs *in the calling session* (Skill tool) | *isolated spawn* (Agent tool) — own throwaway context |
| transcript/process capture | interleaved with the session | **clean & discrete** — tool-use + transcript are the agent's alone (≈ skill-creator `execution_metrics`) |
| human gate | some skills run a developer gate (e.g. ideation mid-run gate) | **none** — agents are non-interactive depth-1 leaves |
| deliverable | varies | a persisted file and/or a returned distilled result (persist-before-return is mandatory) |

**Consequence:** the gate layer (L4) applies only to gate-bearing *skills*; agents are tested on
L1–L3 only.

### 1a. Agent role taxonomy → test shape (reuse REQ-PROC-044-01)

REQ-PROC-044-01 already names every agent `{expertise}-{role}` with `role ∈ {writer,
transformer, reviewer, classifier}` (a 2×2 over persist-vs-return × synthesized-vs-mechanical).
That taxonomy **is** the test-shape selector:

- **transformer** (mechanical persist) → almost entirely **L1 deterministic** assertions
  (objectively-verifiable output) — the case skill-creator handles well.
- **classifier** (mechanical return) → an **accuracy eval against a labelled fixture set**: the
  most traditional, most deterministic test (precision/recall against known labels). Closest to a
  classic eval harness; minimal LLM-judge needed.
- **writer** (synthesized persist) → **L1** (artifact present, schema-valid) + **L2** anchored
  rubric on artifact quality + **L3** old-vs-new A/B.
- **reviewer** (synthesized return) → **L2** judgement-quality, testable by a **planted-defect
  fixture**: seed the playground with known defects and measure whether the reviewer catches them
  (and does not hallucinate defects that aren't there) → a *discriminating* test by construction.

This mapping is the agent-side answer to D-iii and is novel relative to the external prior art
(which only covers file/data-output skills).

---

## 2. Explicit playground interface — the Capability-Test Descriptor (D-i)

REQ-PROC-068 AC-04 currently says only "`run_instructions` file + non-boolean rubric." It is
silent on **what playground state the capability needs to run** — yet the open-ended capabilities
(ideation, requ-explore, ux-create-flow, product-intake, quality-checker, architecture-advisor)
are exactly the ones that consume rich project artifacts. Without an explicit interface they
cannot even be run meaningfully on the harness. D-i closes this.

Every capability test carries a **Capability-Test Descriptor** with three explicit parts:

1. **Fixture binding (the explicit interface).** The named, reproducible state of
   `test_harness_app/` the capability binds to. Because AC-07 git-resets the harness between
   runs, a fixture is a **checkpoint to reset *to*** (a git ref/tag/seed-branch of the harness),
   not merely "clean empty":
   - `fixture_ref`: the harness git ref representing the precondition state.
   - `requires_artifacts`: an explicit, human-readable list of the project artifacts the
     capability consumes — e.g. "≥1 approved FLOW with bound personas", "a requirement with
     uncovered ACs", "a prior ideation ledger in the index", "code under `src/` with ≥1 planted
     `doc/` violation" (reviewer fixtures). This list IS the interface contract between the test
     and the playground.
   - Pure mechanical capabilities that need no project context still state `requires_artifacts:
     []` against a `clean` fixture — explicitness is mandatory, emptiness is allowed.
2. **Invocation.** How the candidate capability is run with the harness as cwd: the skill/agent
   name, args, and any fixed `(topic, effort, frames, seed)` for reproducibility.
3. **Artifact collection.** Which outputs to gather as rubric evidence — the **rubric-evidence
   artifacts** (round-1 §8): the produced artifact(s), the gate render (skills), the deterministic
   post-check report, the agent transcript/`execution_metrics` (agents), and the per-dimension
   judge scores with cited evidence.

The fixture set thus becomes a small library of **named seed states** of the harness; each
capability test names the fixture(s) it needs. This is the "make the interface explicit" deliverable.

---

## 3. The regression baseline is OLD-vs-NEW, blind A/B (D-iv)

skill-creator offers two comparison modes (raw originals in `sources/`): (a) **with-skill vs
without-skill** — measures a skill's *marginal value* (is it worth having); (b) **new vs
snapshotted old version** — measures *improvement*. It defaults to (a). The blind **comparator**
agent (`sources/skill-creator/agents/comparator.md`) labels the two outputs A/B and scores six
anchored 1–5 dimensions + a 1–10 holistic score, deliberately **relative**, not equality-to-golden.

**Our model is (b), made the default and made blind:**
- The factory's capabilities are **established**; "does it beat no-skill" is the wrong question.
  The live question on every modification is **"is the new version an improvement and a
  non-regression?"**
- **L3 Regression = old-vs-new blind A/B.** Freeze the currently-approved version's reference run
  on the fixture. On modification, run **old and new on the same fixture-ref**, present outputs
  **blind (A/B)** to a comparator judge that (1) scores each rubric dimension, (2) requires the
  new version to be **non-regressed on every dimension**, and (3) answers **"did the stated
  intended improvement actually appear and get applied?"** (not merely "was a line added").
- Blindness (borrowed from skill-creator) removes "the new one should be better" bias.
- The without-skill baseline survives only as a **one-time** option when a *brand-new* capability
  is created and there is no prior version (then: absolute L1+L2 rubric, optionally vs a naive
  baseline). For every *modification*, it's old-vs-new.

---

## 4. Embedding into the capability lifecycle (D-ii + D-iii)

The test is a **maintained artifact co-located with the capability**, authored/updated only
through the governed meta-skills — mirroring skill-creator's 6-stage workflow (stages 4–5 author
& run evals; stage 6 improve-&-iterate) but bound to *our* meta-skills:

- **`claude-create-skill` / `claude-create-agent`** gain a stage that authors the
  Capability-Test Descriptor: pick the test shape (deterministic-heavy for
  transformer/classifier/objectively-verifiable; L1 process-assertions + L2 anchored rubric +
  golden-trace fixture for writer/reviewer/open-ended), declare the fixture binding (D-i), and
  designate the reference run.
- **`claude-modify-skill` / `claude-modify-agent`** gain a stage that (1) updates the descriptor
  if the capability's contract changed, (2) runs the **old-vs-new blind A/B regression** (D-iv)
  against the frozen reference, requiring non-regression + intended-improvement-present, and
  (3) re-freezes the reference when the change is an accepted improvement.

This embedding lands in REQ-PROC-044-01's territory (it owns those four meta-skills), so the
requirement work spans **two** existing requirements (see §6).

---

## 5. The tiered rubric, restated with the prior-art reinforcements

L1 **Deterministic** (scripts; "scripts are more reliable than LLM judgment for mechanical
checks"). Includes **process assertions** — skill-creator's `expectations` schema explicitly
allows "The skill used script Y"; our factory capabilities are *method-defined*, so
process-conformance ("ideation ran Phase 0 + emitted the criteria panel"; "requ-explore ran the
Phase-0 eligibility + four tripwires") is a first-class L1 family the external sources only touch
opportunistically — a genuine extension.

L2 **Anchored rubric (LLM judge).** The round-1 ideation dimensions (D1 frame-lens fidelity … D5
gate honesty), each **1–5 with concrete per-level anchors** (extension: skill-creator's 1–5 are
*unanchored*), **citing ledger/artifact evidence per score** (skill-creator's evidence rule), and
governed by two reinforcements from the prior art:
- **Discriminating-check rule** (grader/analyzer): every L1/L2 check must be one a worse baseline
  would actually fail; checks that pass regardless are pruned. Antidote to vacuous open-ended tests.
- **False-confidence is the named primary failure mode**: "a passing grade on a weak assertion is
  worse than useless." Mitigation: concrete cited evidence + grade the checks themselves.

L3 **Old-vs-new blind A/B regression** (§3).

L4 **Gate persona-walk** — gate-bearing skills only (not agents). Bridge to TASK-PROC-069-05.

Honest limits (unchanged from round-1 §9): judge variance (mitigated by anchors + evidence
citation + bands + inter-judge spot-checks); seed is best-effort under LLM nondeterminism;
**content correctness stays unmeasurable by design**; the persona-judge approximates, not
replaces, a developer.

---

## 6. Requirement architecture — proposal + the open decisions

The concept now spans two homes:
- **REQ-PROC-068 (playground/instrument):** owns the **Capability-Test Descriptor** (fixture
  interface + tiered rubric + role→test-shape map + old-vs-new A/B). This is the refinement AC-04
  was always pointing at — now big enough to be a **feature**, not an inline AC tweak.
- **REQ-PROC-044-01 (capability-authoring meta-skills):** owns the **lifecycle embedding** — the
  four meta-skills author/update the descriptor and run the regression.

**Proposed shape (recommended):**
1. New feature under REQ-PROC-068: `feat_capability_testing` (working name) — status `defined` —
   specifying the descriptor, the tiered rubric L1–L4, the agent role→test-shape map, the
   old-vs-new blind A/B regression, and the discriminating/evidence/false-confidence rules.
2. Refine epic AC-04 to reference the new feature + add the **probe-family distinction** note
   (round-1 §8: the six REQ-PROC-068-05 probes are release-cascade probes, distinct from
   capability-test rubric-evidence artifacts; only #6 graph-stats feeds a capability rubric).
3. Extend REQ-PROC-044-01 with one AC: the four meta-skills author/update a Capability-Test
   Descriptor and run the old-vs-new regression on modify.
4. Follow-up **impl tasks** (NOT done in this explore): edit the four meta-skills (via
   `claude-modify-skill`); author the first descriptor (ideation) on the harness.

**Open decisions for the developer (genuine forks):**
- **Q-A — Home/scope:** the recommended split above (feature under 068 + AC on 044-01) vs. a
  single standalone requirement spanning both vs. fold-into-AC-04-only (now too small).
- **Q-B — Feature name & breadth:** `feat_capability_testing` (skills+agents, the unified frame)
  vs. a narrower `feat_open_ended_skill_testing` (skills only; agents handled later).
- **Q-C — Now vs. defer the 044-01 embedding:** specify the lifecycle embedding now (one AC on
  044-01 + follow-up impl tasks) vs. land the 068 feature first and open the embedding as its own
  task.
- **Q-D — Next action after approval:** author the requirement(s) now in this task, and/or create
  the follow-up impl tasks, and/or stop at synthesis.
