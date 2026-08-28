# Synthesis r3 (consolidated) — Capability-Artifact Testing on the Skill-Test Playground

**Status:** single self-contained concept for TASK-PROC-068-01. Supersedes the *scope* of r1
(`…_01_…`) and r2 (`…_03_…`) — read this one; r1/r2 remain as the derivation trail. Awaiting the
developer's requirement-shape decision (§11).

**This document answers, in one place:** the problem's shape, its boundaries (in/out), the unit
under test, the hard constraints, every place it must embed, how it reuses what already exists
(incl. the downloaded skill-creator substrate), the fully-specified four-layer mechanism, a worked
ideation instance, the honest limits, and the requirement architecture + open decisions.

**Inputs folded in:** user initial input (`…_00_…`); external prior art — lens reading (`…_02_…`)
and **raw originals** (`sources/`: agentskills.io page + 21 verbatim skill-creator plugin files);
REQ-PROC-068 (+AC-04) & feat_measurement_instrumentation (068-05); the ideation workflow + its
deterministic post-checks; the EGP system (REQ-PROC-044-04 + `.factory/registry/egp_archetypes.yaml`);
capability-authoring meta-skills (REQ-PROC-044-01); external-plugin adoption (REQ-PROC-055);
TASK-PROC-069-05 (interactive_required sibling); four developer directives (2026-06-21).

---

## 1. Problem shape — stepping back

**The question:** how do we test a capability whose output is *open-ended* — no single correct
result to assert against (ideation: two valid runs on one topic produce different ledgers)? And,
broadened by the developer's directives: how do we do it for **agents** as well as skills, with the
playground interface made **explicit**, **embedded** in the capability lifecycle, and comparing
**old-version vs new-version** (not no-skill-vs-skill)?

**The reframe that unlocks it (the load-bearing move):** a capability test asserts on **(a) the
process the capability ran and (b) the internal consistency + authoring-quality of the artifact it
produced — never on whether the produced answer is "right."** "Is this the right idea/requirement?"
is the human's job at the gate; the test asks "did it explore widely, score coherently, follow its
own stated method, and represent itself honestly?"

**Why this is not ad-hoc:** the factory already has a name for "a property whose faithful check
needs an oracle independent of the artifact itself" — an **externally-grounded property (EGP)**,
with a seven-archetype taxonomy (REQ-PROC-044-04). *A capability test is precisely the EGP oracle
for a governed instruction artifact.* This is the spine the whole concept hangs on (§5.4, §7.2).

**The deeper purpose — the validation asymmetry (extraction-confirmed).** Today the factory tests
the *app's* code rigorously (Dart unit/integration tests + per-commit gates) but does **not** test
its *own* instruction artifacts with anything equivalent. The factory-extraction exploration
(TASK-PROC-066-01) names this the **validation-asymmetry concern** and designates **this task
(068-01) as the factory's "testing oracle"** — one of three quality loops the extracted factory must
self-apply (completeness = REQ-PROC-071; **testing = 068-01**; fix-scheduling = claude-optimize).
So: **capability tests are, for the factory's instruction artifacts, what unit/integration tests are
for Dart code** (the developer's framing). The concept is built to that bar — and to be portable so
the extracted factory carries it (§13).

---

## 2. Boundaries — what is IN and OUT of scope

**IN scope:**
- The unit under test is a **governed instruction artifact** — a **skill**, an **agent**, or a
  **behavioural-contract** artifact (`CLAUDE.md`, `task_ordering_rules.yaml`, the orchestrator
  contract). See §3 for the three-tier unit. All are instruction text that shapes LLM behaviour.
- Testing of **process**, **artifact internal consistency**, and **authoring/output quality**
  (the EGP-bearing properties) via a tiered deterministic+judged mechanism on the playground.
- **Old-vs-new** regression: is a *changed* capability an improvement and a non-regression?
- The **explicit interface** to the playground (which project artifacts a capability binds to).
- The **embedding** of test authoring/running into the capability create/modify lifecycle.

**OUT of scope (and where it lives instead):**
- **App/product code quality** (`lib/`, `test/`, Python `scripts/`) → the existing per-commit gates
  (REQ-PROC-046 / 002 / 051 / 052). Capability tests are a *capability-lifecycle* gate, not a
  per-commit code gate. (Note: the *orchestrator's Python implementation* keeps its unit tests; what
  this concept adds is a test of its **behavioural contract** — §3, §7.8.)
- **Content correctness** — whether the produced idea/requirement is *the right one*. Unmeasurable
  by design; it is the human's call at the gate (§9).
- **The human's decision itself** — we test whether the gate *discloses enough to decide well*
  (L4), not whether the human decided well.
- **The six release-cascade probes** (068-05): stall/cascade/salvage/fidelity/facet/graph — these
  measure the *release/scribble-cascade* workflow, not a capability's quality. Only #6 graph-stats
  feeds a capability rubric. AC-04 conflates the two families (§5.3).
- **Supply-chain safety of external packages** → REQ-PROC-056. **Adoption *method*** for external
  tooling → REQ-PROC-055 (we *use* it, §6).
- **Tech-agnostic hand-off / the app's own UI** → other REQ-PROC-068 features.

---

## 3. The unit under test: any governed instruction artifact

**Boundary (developer decision, 2026-06-21): the unit is *any governed instruction artifact*** —
not just skills/agents. Three tiers, all on one mechanism:

| Tier | Artifacts | Governance | Test shape |
|---|---|---|---|
| **Output-level** | skills, agents | `claude-create/modify-skill`/`-agent` | run on a fixture, judge the produced/modified artifact (§3 role axis, §7.7 modify axis) |
| **Behavioural-contract** | `CLAUDE.md`, `task_ordering_rules.yaml`, the orchestrator's behavioural contract | direct edit / `claude-modify-ordering-rules` / orchestrator | run a **representative task battery** on the harness, judge end-to-end *behaviour* conformance + invariance (§7.8) |

The behavioural-contract tier is what makes **CLAUDE.md** (the highest-leverage instruction artifact,
previously untested) testable — and it is the **chain-level test** the concept previously lacked
(blindspot G1): you cannot judge a CLAUDE.md/ordering/orchestrator change except by running
capability *chains* and watching the seams. **G2 (broaden the boundary) and G1 (test the seams)
collapse into one mechanism.**

### 3.1 Output-level: skill | agent
Skills and agents are both governed instruction artifacts, tested by the **same scaffold** with two
specialisations:

| | Skill | Agent |
|---|---|---|
| execution | runs in the *calling session* (Skill tool) | *isolated spawn* (Agent tool), throwaway context |
| process capture | interleaved with the session | **clean & discrete** — its own transcript + tool-use (≈ skill-creator `metrics.json`/`execution_metrics`) |
| human gate | some skills run a developer gate | **none** — agents are non-interactive depth-1 leaves |
| → L4 (gate persona-walk) | applies to gate-bearing skills | **N/A** |

**Agent role taxonomy → test shape (reuse REQ-PROC-044-01's `{expertise}-{role}`):** the role
*is* the test-shape selector —
- **transformer** (mechanical persist) → almost all **L1 deterministic** (objectively-verifiable).
- **classifier** (mechanical return) → **accuracy against a labelled fixture set** (precision/recall
  vs known labels) — the most traditional, most deterministic eval.
- **writer** (synthesized persist) → L1 + **L2** anchored quality rubric + **L3** old-vs-new A/B.
- **reviewer** (synthesized return) → **L2** judgement quality, testable by a **planted-defect
  fixture** (did it catch the seeded defects, without hallucinating absent ones?) — discriminating
  by construction; also an **S (adversarial safety)** EGP probe.

**Second axis — produce vs. modify (developer directive, 2026-06-21).** Orthogonal to role: a
capability either **produces** a new artifact from a fixture (ideation → a fresh ledger) or
**modifies** an existing one (requ-explore extending a requirement, `claude-modify-skill/-agent`,
`ux-write-persona` with cascade, `doc-update-guidelines`, the scribble-feedback loop, `task-repair-meta`).
The modifying case is **the same mechanism with more meat** (§7.7) — it judges the *delta*, not just
the output, and is where the highest-value factory skills live. It is the capability-level analogue
of the playground's own reason for existing (the scripted mid-release edit P-E + cascade P-F).

---

## 4. Constraints (these shape every design choice)

1. **Harness is deploy → run-as-cwd → git-reset between runs** (REQ-PROC-068 AC-07). A test is
   *repeatable from a clean state*; a fixture is therefore a **named git ref/seed-branch to reset
   *to***, not merely "empty".
2. **Two-tree split** (REQ-PROC-068): the *capability tree* (`flutter_app/.claude/…` + `CLAUDE.md`)
   holds the **capabilities under test**; the *product tree* (`test_harness_app/`) holds **both the
   test definitions** (`factory_tests/<capability>/`, §7.2) **and the fixtures** (`requirements_*`,
   `src/`, `doc/`) the capability runs against. Capabilities never leak product detail and
   vice-versa.
3. **Depth-1 spawn topology** (CLAUDE.md): an agent cannot spawn agents. So the **orchestrator
   session owns the whole test run** — deploy, reset, invoke the capability-under-test, collect
   artifacts, spawn judge leaves, aggregate. Judges are leaves; the session is the conductor.
4. **Judges are search/judgement leaves with an explicit model** — never inherit the reasoning
   tier silently (CLAUDE.md delegation economics + ideation AC-18; now nudged by the
   `pre_agent_model_reminder` hook). Reasoning-class judging may be Opus *by explicit choice*.
5. **Automated-mode unattended** — tests must run without a human in the loop; the L4 human-gate
   layer is therefore played by an LLM developer-persona (bridge to TASK-PROC-069-05).
6. **Sequential-on-tight-tier parallelism** — on `pro`/`free`, judge/run leaves spawn sequentially
   (a usage-limit mid-run loses only the in-flight leaf). Each leaf persists before returning.
7. **LLM nondeterminism + judge variance** — even an unchanged capability produces a different run;
   the seed is a best-effort anchor. Mitigated by anchored levels, evidence-citation, score-bands,
   and inter-judge spot-checks (§9).
8. **Cost is measured in net human time saved — not apparatus size** (developer directive,
   2026-06-21). The design goal is **maximal automated catching**: the LLM + scripts catch
   *everything they can*, so the human's residual is only the irreducible judgment of skill
   performance (§2 "OUT: content correctness"). For PERSONA-015 (minimum-effective-dose), the
   *effective* dose is the one that **minimizes the developer's manual review effort**; a broad
   mechanism that saves more developer time than it costs to maintain IS the minimum dose — breadth
   is justified by time saved, not penalized by size. The remaining discipline is per-component:
   every check must be **discriminating** (catch a real failure a baseline would exhibit), else it
   is pruned. Token/duration cost is still recorded as the **C (real cost/performance) EGP
   measurement**; tests run on a **lifecycle trigger** (create/modify), not per-commit, to spend
   that cost where it buys signal.
9. **Tech-agnostic** — no artifact may assume Flutter (REQ-PROC-068); the test substrate is the
   web/React harness, the rubric is framework-neutral.

---

## 5. Where it embeds (all touch points)

### 5.1 Capability lifecycle — REQ-PROC-044-01 (the create/modify embedding, directive D-ii/D-iii)
The four meta-skills own the **lifecycle triggers** (§7.10): `claude-create-skill`/`-agent` **author
the Capability-Test Descriptor inline** (§7.2) + create the baseline/improve test-task;
`claude-modify-skill`/`-agent`,
on a change to a *tested* capability, fire the **ASK-the-developer gate** (run the regression now /
defer to a test-task / skip-with-justification — `pending_feedback` in automated mode), and on an
accepted improvement **re-baseline** `current_best`. (One new AC on REQ-PROC-044-01; the meta-skill
edits are follow-up impl tasks.)

### 5.2 The playground venue — REQ-PROC-068 (directive D-i)
Owns the **fixture library** (named seed-states of `test_harness_app/`) and the run/reset mechanism
(AC-07). AC-04's "`run_instructions` + non-boolean rubric" is *specified* by this concept's
descriptor + tiered rubric.

### 5.3 Measurement instrumentation — REQ-PROC-068-05 (probe-family finding)
The six probes are **release-cascade** probes, not capability-quality probes. A capability test
emits its own **rubric-evidence artifacts** (the produced artifact, the gate render, the L1
post-check report, the judge `comparison`/`grading` outputs, the `timing` cost). Recommend a note
on 068-05 distinguishing the two families. The bridge is **per-capability**: for the *ideation*
rubric only #6 graph-stats feeds a dimension; for *other* capabilities other probes feed theirs —
e.g. #5 facet-tag audit (auto vs human-confirmed tag) feeds a **requ-explore** test's **F-archetype**
dimension (validator m3). So "only #6" holds for ideation, not for the general mechanism.

### 5.4 The EGP quality-property spine — REQ-PROC-044-04 (the deepest connection)
The factory already requires HIGH-consequence skills/agents to declare an **EGP disposition** in
their `contract.yaml` (archetype + external referent), enforced by
`check_egp_floor_contracts.py`. **A capability test is the oracle that those declarations promise.**
The mapping (rubric dimension ⇒ archetype):

| EGP archetype | external referent | capability-test instantiation |
|---|---|---|
| **Q** authoring/output quality | a human quality rubric | the core L2 anchored rubric (e.g. ideation D1 frame-lens, D2 non-redundancy, D3 criteria soundness) |
| **I** stated-intention fidelity | the plain-language goal | "did the capability fulfil its *stated* purpose, not a silently narrowed sub-goal?" — L1 process-conformance + L2 D4 synthesis fidelity |
| **F** empirical fidelity | real artifacts/behaviour | for capabilities making claims about real artifacts (requ-explore: requirement vs real code/personas) |
| **V** persona/user value | the real persona | product/UX capabilities: does the output serve the real persona? (persona-walk) |
| **C** real cost/performance | a real measurement | the `timing` token/duration capture |
| **S** adversarial safety | real adversarial input | reviewer planted-defect / malformed-fixture robustness |
| **X** cross-artifact coherence | other artifacts' emergent state | does the produced artifact stay coherent with the rest of the harness project? |

So: **the playground IS the external-referent substrate** (real artifacts, real persona-fixtures,
real measurements) that EGP archetypes demand, and the **four-layer test is the oracle mechanism**;
the L2 dimensions are *instances of the archetypes the capability's contract declares*. This unifies
the concept with the factory's existing quality spine instead of bolting on a parallel one.

### 5.5 External-tooling adoption — REQ-PROC-055 (governed reuse, §6)
The skill-creator substrate is adopted through REQ-PROC-055's framework, not re-derived.

### 5.6 First instance + reusable parts — REQ-PROC-004 ideation
Ideation is the first capability tested; it already supplies L1 post-checks, an HTML gate render,
and cross-run memory we reuse (§6.2).

### 5.7 Continuous improvement — REQ-PROC-006 optimizer
A regression `lost`/`tie` or a recurring judge finding writes a `.factory/optimize/events/*` event,
so `claude-optimize` folds the lesson back into the capability — closing the improve loop
(mirrors skill-creator stage 6, but through *our* optimizer).

### 5.8 The interactive-required sibling — TASK-PROC-069-05
L4's persona-judge is the automated stand-in for the human venue 069-05 routes genuinely-interactive
runs to. They meet exactly at "test the gate."

---

## 6. Utilize what already exists (concrete reuse map)

### 6.1 The skill-creator substrate (MIT) — adopt via REQ-PROC-055
Capability testing is **band G (governance/quality gates) — the factory moat**, so per REQ-PROC-055
OR-2 we **never Full-adopt**. The governed split:
- **Selective-adopt (copy + adapt + freeze, attribute in `THIRD_PARTY_NOTICES.md`)** — the **data
  schemas**, adapted JSON→YAML for factory consistency:
  - `evals.json` ⇒ the **Capability-Test Descriptor** (`prompt`/`expected_output`/`files`/
    **`expectations`** — note `expectations` already supports *process* assertions like "The skill
    used script Y").
  - **`history.json` ⇒ the old-vs-new regression ledger** — `current_best`, `iterations[]` with
    `parent` + `grading_result: won|lost|tie`. *This is exactly directive D-iv's version lineage.*
  - `grading.json` ⇒ the L1+judge result (graded `expectations` + `execution_metrics` + `claims` +
    **`eval_feedback`** = grade-the-checks-themselves) — carries the discriminating-check + evidence
    discipline.
  - `comparison.json` ⇒ the **blind A/B** judge output (winner, per-output anchored sub-scores,
    1–10 holistic, strengths/weaknesses, `expectation_results`).
  - `metrics.json` / `timing.json` ⇒ process + cost capture (the C-archetype measurement).
- **Inspirational-port the *dispatcher*** — the orchestration *flow* (`run_eval.py`, `run_loop.py`)
  and the `comparator`/`grader`/`analyzer` agent *prompts*: re-express the *ideas* (clean-context per
  run, same-turn baseline, discriminating pruning, false-confidence guard) inside our own meta-skills
  + judge agents, under our depth-1 topology and model-tier rules. The Band-G *dispatch spine* is
  never replaced. **But the blanket ruling is too coarse (validator m1):** individual **pure
  utilities** (e.g. `aggregate_benchmark.py` — statistics, no dispatch) MAY qualify for
  **Selective-adopt** if a per-script read shows they carry no Band-G dispatch logic. All scripts are
  in `sources/skill-creator/.../scripts/` (fully fetched, not listing-only); the read + the
  per-script adopt/port decision belongs to the REQ-PROC-055 adoption task, not pre-decided here.
- **Reuse the idea of** the `eval-viewer` HTML as a review surface — but we already have
  `render_ideation_ledger.py` (§6.2); prefer ours.

### 6.2 Factory-native parts we already own
- **Ideation deterministic post-checks** = ready-made **L1** for the ideation instance:
  `diverge_postcheck` (quota/frame/technique), `recompose_postcheck` (integration/goal/dedup),
  `soundness` (constraint/answers/stability), `decomposition.validate_tree`.
- **`render_ideation_ledger.py --serve`** = the **L4** review surface the persona-judge walks.
- **`index_session.py`** = cross-run memory; a capability's reference runs + regression history can
  index alongside, so prior test runs are retrievable.
- **EGP archetype taxonomy** = the L2 **dimension vocabulary** (§5.4) — no new taxonomy invented.
- **The `pre_agent_model_reminder` hook** (added this session) = an **advisory nudge** for
  constraint #4 on judge/run leaf spawns (it exits 0, never blocks — enforcement is *social, not
  mechanical*; validator m4).

---

## 7. The concept, fully specified

### 7.1 Four layers
- **L1 — Deterministic** (scripts; "scripts are more reliable than LLM judgment"). Two families:
  (a) **structural invariants** (artifact present, schema-valid, counts, structural links, dedup,
  capped-gaps-surfaced); (b) **process-conformance assertions** — the capability ran its own stated
  method ("ideation ran Phase 0 + emitted the criteria panel"; "requ-explore ran Phase-0 eligibility
  + the four tripwires"). Process assertions are the **I-archetype** backbone and are first-class in
  skill-creator's `expectations` schema. The LLM starts only where L1 stops.
- **L2 — Anchored rubric (LLM judge).** Dimensions = the **EGP archetypes the capability's
  contract declares**, made concrete per capability with **1–5 per-level anchors** (extension beyond
  skill-creator's unanchored 1–5) and a hard rule: **every score cites specific artifact/ledger
  rows**. Two prior-art reinforcements: the **discriminating-check rule** — at authoring time an
  *intent* (the author believes each check would catch a real failure); **confirmed or pruned
  *retroactively*** by the analyzer's `eval_feedback` once old-vs-new runs reveal checks that pass
  in both arms (a maintenance signal, not a build-time gate — validator M4) — and the
  **false-confidence guard** ("a passing grade on a weak assertion is worse than useless" → grade
  the checks themselves, via `eval_feedback`).
- **L3 — Old-vs-new blind A/B regression** (directive D-iv). **Compare *versions*, not stored runs**
  (resolves G3 model-drift): on modify, execute **both the old and the new capability version fresh,
  now, under the same current executor+judge model**, on the same fixture-ref, then present outputs
  **blind (A/B)** to the comparator: (1) score each dimension, (2) apply the regression gate (§7.6
  — a weighted/threshold gate with a recorded-tradeoff override, *not* a hard every-dimension floor),
  (3) answer **"did the stated intended improvement appear *and get applied*?"**. Because both arms
  share the model *version*, the dominant G3 confound (version drift) is removed; on tight tiers the
  two runs are **sequential, not literally same-turn**, so residual sampling variance remains —
  bounded by the variance controls (multi-run, score-bands, §9), not eliminated (validator M1). The
  stored reference run is kept only as a **model-pinned cache**. **Schema note (validator C2):**
  upstream `history.json` carries **no** model field (`executor_model` exists only in
  `benchmark.json.metadata`); model-pinning therefore **adds** an `executor_model`/`judge_model`
  field to our *adapted* history schema — a deliberate Selective-**adapt** addition (within
  copy+adapt+freeze), ours, not reused-verbatim. Cache valid while the model is unchanged; a model
  upgrade invalidates it and the old version is re-run fresh to restore a model-matched baseline
  (**the re-baseline policy**); re-running old-vs-its-own-cache is the **model-drift detector**.
  Recorded in the adapted `history` ledger (`won|lost|tie`, `current_best`, `parent`, + our
  `executor_model`/`judge_model`). Brand-new capability (no prior version) → absolute L1+L2.
- **L4 — Gate persona-walk** (skills with a human gate only). An LLM developer-persona walks the
  rendered gate and scores **interaction quality** ("could I decide well from what's shown? is
  anything buried/missing/misrepresented?") — the **V**-archetype probe and the 069-05 bridge.
  Distinct from L2's **gate-honesty** dimension ("does the gate tell the truth about the ledger?");
  L4 = "is the truth it tells *enough* to decide?".

### 7.2 The Capability-Test Descriptor (the explicit interface, directive D-i)
**Location (corrected to fit the established deploy/assess design, TASK-PROC-066-03):** the
descriptor lives in the **product tree** at `test_harness_app/factory_tests/<capability>/` —
co-located with the fixtures, as `run_instructions.md` + `expected_outcome.md` (the rubric), the
structure that synthesis already fixed. The capability-authoring meta-skills (factory tree)
*author/update* it there; it is *not* under `.claude/`. A YAML descriptor (adapted from `evals.json`)
backs `expected_outcome.md`. Parts:
1. **`capability`**: name + kind (`skill | agent | behavioural-contract`) + (agent) `role`.
2. **`egp_dimensions`**: the archetypes from the capability's `contract.yaml`, each with its 1–5
   anchors → drives L2.
3. **`fixture` (the explicit playground interface)**:
   - `fixture_ref`: the `test_harness_app/` git ref/seed-branch to reset to.
   - `requires_artifacts`: explicit list of project artifacts the capability consumes (e.g. "≥1
     approved FLOW with bound personas", "a requirement with uncovered ACs", "a prior ideation
     ledger in the index", "code with ≥1 planted `doc/` violation"). *This list is the interface
     contract between test and playground.* Mechanical capabilities state `requires_artifacts: []`
     against a `clean` fixture — emptiness allowed, explicitness mandatory.
4. **`invocation`**: how to run with harness as cwd — name, args, fixed `(topic, effort, frames,
   seed)` for reproducibility.
5. **`collect`**: which rubric-evidence artifacts to gather.
6. **`expectations`**: L1 deterministic + process assertions.
7. **`reference`**: pointer to the reference *version* + its model-pinned cached run (the L3
   baseline, re-run fresh on a model change — §7.1) + the `history` ledger path.

### 7.3 The fixture library
Named seed-states of `test_harness_app/` (git refs/branches), authored once and maintained; each
`requires_artifacts` resolves to a fixture. Fixtures live in the **product tree**; descriptors
reference them by ref. A planted-defect fixture (for reviewer agents) is a seed-state with known,
catalogued defects so the test is discriminating by construction.

### 7.4 The run model (depth-1, orchestrator-owned)
The session (not an agent) does: **deploy** candidate capability into the harness → **reset** harness
to `fixture_ref` → **invoke** the capability (collect produced artifact + transcript + `timing`) →
run **L1** scripts → spawn **L2/L4 judge leaves** (model set explicitly; sequential on tight tiers;
each persists before returning) → for L3, repeat old+new and spawn the **blind comparator** leaf →
**aggregate** into `grading`/`comparison`/`history`. Triggered on create (baseline) / modify
(regression); never per-commit.

### 7.5 Judge calibration & governance — the oracle for the oracle (resolves B1)
The judges (L2/L3/L4) are themselves open-ended capabilities, so they need their *own* external
referent. The factory already built it: the **Human-Judgment Register** (REQ-PROC-044-05) — a
developer-ratified catalog of judgment *kinds* mapped to EGP archetypes (the **types** layer), over
a captured corpus of real human gate-decisions (the **instances** layer = the feedback-checkpoint
corpus), with a generated decision index and a token-efficient **query interface** (AC-04) that
returns distilled capsules without reading the raw corpus. Wiring:
- **Calibration:** for each L2 dimension, the matching Register decision-kind (same EGP archetype)
  supplies **gold human judgments** as the judge's calibration set. The judge is periodically scored
  against a held-out slice of those captured human decisions; large judge↔human divergence on a
  dimension means the anchor is mis-set → re-author it (and the divergence is itself a Register-query
  signal, not a fresh corpus read — honors the depth-1/context-economy constraint).
- **Anchor provenance (resolves D2):** the 1–5 anchors are not free-authored per descriptor — each
  is an instance of a **ratified Register judgment-kind**; adding/altering a dimension's standard of
  good is a developer-ratification act (Register AC-05: tooling may only *surface* a candidate kind,
  never add/edit one during a run).
- **Honest residual (Register AC-06 pattern):** a dimension whose archetype maps to *no* captured
  decision-kind is **uncalibrated** — flagged as the irreducible residual blind spot, never silently
  treated as validated. Two dispositions: add a capture point so future gate-decisions populate it,
  or accept it as a stated limit.
- **Inter-judge variance** (a different failure than bias) stays a within-test check: run the judge
  ≥2× on the reference; high disagreement ⇒ tighten the anchor.

This closes the regress *one bounded level*: the judge is grounded in real human decisions, and the
fact that the human corpus is itself finite/imperfect is the acknowledged terminal residual — the
same place every EGP oracle in the factory bottoms out.

**Implementation status (validator M2) — B1 is resolved *in design*, activation is a prerequisite.**
The Register's **types** layer exists (`.factory/registry/human_judgment_register.yaml`), but the
**decision index** (REQ-PROC-044-05 AC-03) and the **query interface** (AC-04) are **not yet
implemented** (no query script in `scripts/`), so the calibration corpus is not yet
machine-retrievable. Until AC-04 lands: anchors are **author-declared inline** at create (the §7.10
decision), and calibration runs **deferred**. So D2 (anchor provenance) and B1 (judge oracle) are
resolved as a *target*; their *activation* depends on the Register query interface — a named
prerequisite (§14), not a current capability.

### 7.6 The regression gate — weighted, with knockouts + recorded tradeoffs (resolves D1)
"Non-regression on every dimension" is wrong: it blocks legitimate tradeoffs (improve D1, slightly
cost D2) and floods neutral changes (refactors) with no-signal **ties**. The gate reuses three
existing factory patterns instead of inventing one:
- **Knockout floor** on the dimensions whose archetype is *always high-consequence* — **S
  (adversarial safety)** by EGP identity, and any dimension the capability's contract marks
  high-floor: these may **never** regress (= ideation's `kind_of_criterion: knockout`).
- **Weighted aggregate** over the remaining (Q/I/F/V/X) dimensions, each carrying a
  `weight` + `weight_rationale` (= ideation's weighted criteria): the gate passes when the
  **weighted aggregate is non-regressed**, even if an individual weighted dimension dips.
- **Recorded-tradeoff override**: an individual weighted-dimension drop beyond a tolerance is
  admissible **only** with a **Value-Trade-off Record** (`vcd-log-tradeoff`) naming what was traded
  for what — turning a silent regression into an auditable, deliberate decision.
- A **tie** (no aggregate movement, no knockout breach) is a **pass with no re-baseline** — it does
  not block a neutral change, and `history` records it as `tie` without churning `current_best`.

This makes the gate discriminating *and* permissive of good tradeoffs, and it inherits the
governance of patterns the factory already trusts (knockout/weighted criteria + VTR).

### 7.7 Artifact-modifying capabilities — the same mechanism, more meat (developer directive)
A *producing* capability is judged on its output; a *modifying* capability must be judged on its
**delta** over a pre-existing artifact-state. Same four layers, three additions:
1. **The fixture is the *before*-state** — already expressible as `fixture_ref` (the existing
   interface, §7.2), now naming the artifact(s) that must already exist and their pre-edit content.
   The descriptor additionally declares the **change request** (the edit the skill is asked to make)
   so the test has the *intent* to judge the delta against.
2. **Delta-scoped assertions over `(before → after)`** — partition the diff into:
   - **intended-change set** (must move, and move correctly) → **I (stated-intention fidelity)**:
     did the requested change land *and get applied*, not a narrowed sub-edit?
   - **invariant set** (must NOT move) → **X (cross-artifact coherence)** + a deterministic L1
     "blast-radius" check: *only* the artifacts that should change did; nothing unrelated was
     silently rewritten, no sibling/cross-reference was corrupted, the edit cascaded where it
     should (P-F) and stopped where it shouldn't.
   - **schema/structure preserved** → L1 (still valid after the edit).
   X is the load-bearing dimension here — exactly the archetype already in §5.4 ("stays coherent
   with the emergent state of *other* artifacts"). For a modifying capability, X moves from a
   nice-to-have to a primary gate.
3. **Idempotence / over-reach probes where applicable** — re-running the modify on an
   already-satisfied fixture should be a no-op (catches skills that rewrite needlessly); a
   minimal-change fixture should produce a minimal diff (catches over-eager rewriting — a real
   failure mode of LLM edit skills).
The L3 regression (old-vs-new of the *modifying skill itself*) and L4 (its gates, e.g.
requ-explore's location/synthesis-approval, the scribble feedback gate) are unchanged. So the
mechanism is **one mechanism**: producing is the degenerate case where the before-state is empty
and the invariant set is "everything outside the new artifact"; modifying just makes the delta and
the X-coherence dimension explicit and primary. This is also why the playground's P-E/P-F couplings
matter for *capability* testing, not only product testing — they are the fixtures a modifying-skill
test needs.

### 7.8 Behavioural-contract artifacts & chain-level testing (resolves G1 + G2)
`CLAUDE.md`, `task_ordering_rules.yaml`, and the orchestrator behavioural contract do not *produce*
an artifact you can judge in isolation — their effect is on **how capability chains behave**. So
they are tested at the **chain/battery level**:
- **Fixture = a representative task battery** on the harness (e.g. "do this code task", "do this
  requ-explore", "resume after a simulated rate-limit") chosen to exercise the rules the artifact
  governs — the capability analogue of the playground's P-E/P-F couplings.
- **Judge the run, not an output:** **I** — did agents *follow* the changed rule across the battery?
  **X** — did unrelated behaviour stay invariant (no rule silently broke elsewhere)? **S** — for the
  orchestrator, adversarial scenarios (rate-limit, lock contention, malformed answer.md) behave per
  contract. The process-capture (`metrics`/transcripts) is the evidence.
- **Modify framing applies** (§7.7): a CLAUDE.md edit is a *modification*, judged on its delta —
  intended rule-change present, blast-radius bounded — via old-vs-new battery A/B.
- This is the **single highest-value tier for time-saved** (developer aim, §4 #8): a constitution or
  ordering-rule regression is exactly the kind of silent, cross-cutting damage a human cannot
  cheaply catch by eye. It is also the costliest (a battery per change) → reserved for
  behavioural-contract edits, on the lifecycle trigger.
- **Topology clarification (validator M3).** A battery runs each chain as a **scoped child
  Claude-Code *session*** on the harness (the deploy/run mechanism, `cd test_harness_app && ccs …`),
  driven by the **test orchestrator**. This is a *different layer* from the **depth-1 *agent* rule**
  (which forbids an Agent-tool *leaf* from spawning agents *within* a session, and forbids normal
  task-work shelling out to nested `claude`): the test runner launching scoped child sessions is the
  **sanctioned deploy/assess mechanism**, not the forbidden pattern. But because that child-session
  orchestration is the **undesigned** part of TASK-PROC-066-03, this tier **depends on the execution
  substrate prerequisite (§14)** and cannot be built before it.

### 7.9 Test-time isolation — the candidate is untrusted (resolves D4)
Isolation reuses the deploy/assess **constraints** recorded by TASK-PROC-066-03 — but the *mechanism*
itself is an **explicitly-deferred** dedicated exploration ("the task designs the mechanism"), and
`test_harness_app/` is **not yet structured as a factory project** (no `CLAUDE.md`/`.claude/`/
`requirements_*`; REQ-PROC-068 AC-01 unchecked). Both are **hard prerequisites** (§14, validator C3).
As constrained: a run **deploys** the candidate (skills/agents + `CLAUDE.md`) into
`test_harness_app/`, launches Claude Code **scoped with the harness as cwd** (loads only that
project's `.claude/`+`CLAUDE.md`), and **git-resets** the harness after, splitting durable fixtures
from disposable run-outputs. Treated as **untrusted**: the candidate acts only within the harness
cwd; git-reset wipes its effects; nothing it writes persists into the factory tree. This matters
most for **externally-adopted candidates** (REQ-PROC-055) — they run under the same untrusted
boundary. **Residual risk** (flagged to the dedicated execution-protocol task): a candidate using
absolute paths or escaping cwd scoping could touch the factory tree — the scoping mechanism, not
this concept, must guarantee containment.

### 7.10 Testability definition + execution lifecycle (developer directive, 2026-06-21)
**What is "testable"?** A governed instruction artifact is **testable by this mechanism** iff it is
(a) **exercisable on a reproducible fixture** AND (b) **bears ≥1 externally-grounded property**
(Q/F/I/V/C/S/X). Condition (b) IS the EGP membership test (REQ-PROC-044-04): an EGP-bearing property
*cannot* be self-certified, so it needs the fixture+oracle test; a purely self-certifiable
capability is *checkable* by deterministic L1 / existing script unit tests and needs no judged test.
**Derivable from the contract's EGP disposition *where one is declared*** — a non-`not_bearing`
archetype ⇒ testable ⇒ a test is *owed*. **But (validator C1) most capabilities do not declare one
today**: the EGP floor only *requires* a disposition on HIGH-floor contracts, and many capabilities
— including the primary example `ideation-start` — **have no `contract.yaml` at all**, so the
derivation is not yet mechanical in production. Where no declaration exists, the **test author
declares the bearing archetypes inline** at authoring time (consistent with author-knows-intent,
§7.10.1) — which doubles as the trigger to backfill the contract's EGP disposition (a §14
prerequisite). A capability that bears an EGP property but is **not fixture-exercisable** (needs
unbounded external state) is flagged as the honest residual (Register AC-06 pattern), not silently
passed.

**Execution lifecycle (the "when") — three triggers:**
1. **On create of a testable capability →** the create meta-skill **authors the descriptor inline**
   — fixture binding + EGP dimensions + anchors + L1/process `expectations` — **because the author
   has the freshest, most complete knowledge of what the capability should do, so the test cases are
   cheapest and highest-fidelity to write right then** (and it captures the *stated intention* — the
   I-archetype — while it is still explicit; developer-confirmed 2026-06-21). Only the
   execution-heavy remainder — the **baseline run + judge calibration + improve loop** — is deferred
   to a **created task** (it needs execution and benefits from iteration). So *"tests must always be
   created when something testable is created"* = the **inline-authored descriptor**; the task only
   *runs and improves* it.
2. **On modify of a capability that HAS a test → ASK the developer** (a declared **user-input
   gate**): run the regression now / defer to a test-improve task / skip-with-justification. This is
   the developer's explicit rule — a tested-capability change always surfaces to the human (cost +
   keep-the-human-in-the-loop). In **automated mode** the ask becomes a `pending_feedback`
   escalation (the factory's standard gate handling).
3. **On modify of a testable capability with NO test yet →** create the backfill test-task.

Execution is thus **decoupled from authoring**: tests run on their task and re-run on the gated
modify, never as an inline per-edit blocker — matching the cost constraint (§4 #8) and feeding the
fix-scheduling loop (claude-optimize). The triggers are owned by the capability-authoring meta-skills
(§5.1) and registered in the user-input-gate inventory (`render_user_input_gates.py`).

---

## 8. Worked instance — ideation (the first capability test)
- **Fixture**: a harness seed-state with a fixed topic + an index containing ≥1 prior ledger;
  `invocation`: `ideation-start "<fixed topic>" effort=Standard` with pinned frames+seed.
- **L1**: the four existing post-checks + process assertions (Phase-0 recorded; criteria panel
  emitted; mid-run gate rendered; index appended; capped gaps surfaced).
- **L2 (Q + I)**: D1 frame-lens fidelity, D2 semantic non-redundancy, D3 criteria soundness,
  D4 synthesis fidelity (= I), D5 gate honesty — each 1–5 anchored, citing ledger rows. **D6 recovery
  honesty is *conditional*** — scored **only when the recovery ladder actually ran** (viable-set
  collapse); on a non-collapse run it is *not applicable*, not a vacuous pass (validator m2). The
  descriptor schema therefore supports **conditional dimensions** (a `when:` guard).
- **L3**: on an ideation-skill change, **both versions run fresh under one model** on the fixed
  topic+seed, blind A/B + "did the intended improvement appear?" (the cached prior run is a
  model-pinned baseline, §7.1).
- **L4 (V)**: persona-judge walks the `render_ideation_ledger --serve` mid-run gate, scores
  decide-ability.
- **Cost (C)**: `timing` tokens/duration recorded.

---

## 9. Honest limits & what stays unmeasurable
- **Judge variance & bias** — anchors + evidence-citation + score-bands + inter-judge spot-checks
  reduce *variance*; *systematic* bias is caught only by calibration against the Human-Judgment
  Register corpus (§7.5). The terminal residual is that the human corpus is itself finite — the
  factory's universal EGP bottom (Register AC-06).
- **Seed is best-effort** under LLM nondeterminism; the comparator must separate "different but
  equally good" from "regressed".
- **Content correctness is unmeasurable by design** — the human's call at the gate.
- **The persona-judge approximates, not replaces, a developer** — it scores disclosure quality,
  not whether a real human would actually decide well.
- **Conformance ≠ good method (B2, largely inherent)** — the test certifies that a capability
  *faithfully ran its stated method* and produced an *internally-consistent* artifact; it cannot
  certify the **method itself is sound** (a faithfully-executed bad method scores well). Method
  soundness stays a human-authoring judgment — but not a *lost* one: it is explicitly a
  Human-Judgment-Register kind raised at create/modify time (§7.5), so it is captured and surfaced,
  not silently assumed. Old-vs-new A/B catches a method *regression* only once a human proposes the
  better method.
- **Construct validity (B3, partly inherent)** — passing on a deliberately-small fixture is a
  *hypothesis* that the capability is good in production, not proof. Mitigation: keep fixtures as
  realistic as the coupling-signal allows, and over time **correlate test verdicts against real-run
  outcomes** (a `lost`/`tie` that real use contradicts is a fixture-realism defect to fix). The gap
  between toy-pass and real-good never fully closes — stated, not hidden.
- **The EGP *declaration* itself has no oracle (validator C1)** — the L2 dimension set is derived
  from the capability's declared archetypes (or author-declared inline), but **nothing checks the
  author declared the *right* archetypes**. A capability that should bear S (safety) but declares
  only Q is under-tested, and the test cannot detect the omission. This is the same class as B2
  (authoring judgment with no external check); mitigation is the same — surface the declaration as a
  Human-Judgment-Register kind so it is reviewed, not silently trusted.
- **Cost vs coverage** — full runs are expensive, so the fixture set stays **small and
  high-signal** (skill-creator: "start with 2–3") for *signal density*, not to cap scope: the aim
  is to catch everything mechanically/LLM-catchable so the developer's manual time shrinks (§4 #8).

---

## 10. Generality
The four-layer scaffold + descriptor + fixture-interface + old-vs-new A/B is **capability-generic**
across **both** axes (role §3, and produce-vs-modify §7.7); only the L2 dimensions (= the
capability's declared EGP archetypes) are per-capability. Confirmed mappings: requ-explore
(*modifying* when it extends a requirement → L1 blast-radius + end-state gate; L2 = I/X/F; L4 = its
approval gates), product-intake (L1 routing-artifact present; L2 = I/V routing justification), the
reviewer agents (L2 = S/Q via planted defects), the `claude-modify-skill/-agent` meta-skills
(modifying, with X-coherence over `INDEX.md`/`factory_flows.md` as a primary dimension). The two
axes select the shape.

---

## 11. Requirement architecture & the open decisions (the action this task needs)

**Proposed shape (recommended):**
1. **New feature under REQ-PROC-068** — `feat_capability_testing` (working name): the
   Capability-Test Descriptor, the fixture interface, the tiered rubric L1–L4 with EGP-archetype
   dimensions, the agent role→test-shape map, the old-vs-new blind A/B regression, and the
   discriminating/evidence/false-confidence rules. Status `defined`.
2. **Refine epic AC-04** to reference the feature + add the **probe-family** distinction (068-05).
3. **One AC on REQ-PROC-044-01** — the four meta-skills author/update a descriptor and run the
   old-vs-new regression on modify.
4. **Cross-reference on REQ-PROC-044-04** — a capability test is the EGP oracle for a capability's
   declared archetypes (no new EGP mechanism; this is the oracle the floor-contract promises).
4b. **Cross-reference on REQ-PROC-044-05 (Human-Judgment Register)** — the Register corpus is the
   judges' calibration oracle and the home of the rubric anchors (ratified judgment-kinds); the test
   *consumes* the Register, it does not duplicate it.
5. **An adoption task under REQ-PROC-055** — Selective-adopt the skill-creator schemas
   (evals/grading/comparison/history, JSON→YAML) + `THIRD_PARTY_NOTICES.md`; Inspirational-port the
   orchestration.
6. **Alignment with the deploy/assess execution-protocol task** (TASK-PROC-066-03 line) — this
   concept records the *constraints* (deploy/scoped-cwd/git-reset, descriptors in
   `test_harness_app/factory_tests/`, untrusted candidate); that task designs the *mechanism*.
7. **Scope note:** the unit is *any governed instruction artifact* (skills, agents, CLAUDE.md,
   ordering-rules, orchestrator contract) across two tiers (output-level, behavioural-contract) —
   the feature name should reflect that (e.g. `feat_capability_testing`, "capability" = governed
   instruction artifact). Q-B reframed accordingly.
8. **Follow-up impl tasks** (NOT this explore): edit the meta-skills; author the first (ideation)
   descriptor + fixture; check whether ideation gate-decisions are already in the feedback corpus
   (Iteration 1 residual).

**Open forks for the developer (the requirement-shape decision):**
- **Q-A Home/scope:** the multi-home split above *(recommended)* vs. a single standalone requirement
  spanning 068 / 044-01 / 044-04 / 044-05 vs. fold-into-AC-04-only (too small now).
- **Q-B Name:** breadth is **decided** (any governed instruction artifact — Iteration 6); only the
  name remains — `feat_capability_testing` *(recommended)* vs. an alternative.
- **Q-C EGP coupling:** make the EGP-archetype mapping **binding** (L2 dimensions MUST be the
  contract's declared archetypes) vs. a *recommended* alignment.
- **Q-D Adoption depth:** Selective-adopt the skill-creator schemas as proposed vs. Inspirational-only
  (re-author our own YAML formats, zero attribution burden).
- **Q-E Next action:** author the requirement(s) now in this task, and/or create the follow-up impl +
  adoption tasks, and/or stop at synthesis.

---

## 12. Iterative design resolutions (questioning each solution)

Each entry: the solution/problem questioned · does it fit the rest of the concept · was there a
better alternative · open questions + how resolved (reason / read / websearch / experiment) ·
what changed in the concept above. Blindspot ids reference `…_05_blindspots_…`.

### Iteration 1 — B1: the judge has no oracle → calibrate against the Human-Judgment Register
- **Questioned:** L2/L3/L4 are open-ended LLM judgments with nothing checking them; the concept's
  confidence outran its foundation.
- **Open question, resolved by reading a file:** *does the factory already have a human-judgment
  oracle to calibrate against?* — Read REQ-PROC-044-05. **Yes:** a ratified catalog of judgment
  *kinds* (mapped to EGP archetypes) over a captured corpus of real human gate-decisions, with a
  token-efficient query interface (AC-04) and an explicit "judgment captured nowhere = residual
  blind spot" honesty rule (AC-06).
- **Fit:** strong — it *deepens* the EGP spine (§5.4) and reuses an existing factory capability
  (§6.2) rather than adding a parallel one; the query interface respects the depth-1/context budget.
- **Better alternative considered & rejected:** a bespoke per-capability gold-judgment set —
  duplicates the Register, adds maintenance, violates minimum-effective-dose. Using the Register is
  strictly better.
- **Resolution folded in:** new **§7.5** (calibration against the Register by decision-kind; anchors
  become ratified Register kinds — this also resolves **D2**; uncovered dimensions are flagged
  uncalibrated per AC-06); §9 judge-limit rewritten to separate *variance* from *bias*.
- **Residual open question (cheap, deferred):** *are ideation mid-run gate APPROVE/ITERATE
  decisions actually captured in the feedback-checkpoint corpus today?* If yes, the ideation
  D5/L4 judge has a live calibration oracle immediately; if no, that capture point is the first
  follow-up. Checkable by querying the corpus — noted for the ideation-instance impl task.

### Iteration 2 — G3: model drift confounds the regression → compare versions, not stored runs
- **Questioned:** L3 "freeze the reference *run*" silently assumed a constant model; a frozen run is
  produced under an old executor+judge model, so new-vs-frozen conflates *version* change with
  *model* change.
- **Resolved by reasoning** (+ the already-read skill-creator schema): the fix is latent in
  skill-creator's own same-turn-baseline discipline — **execute both versions fresh, now, under the
  same current model**; the difference is then attributable to the version alone. The stored run is
  demoted to a **model-pinned cache** (`benchmark.metadata.executor_model` already carries the model
  id), valid only while the model is unchanged; a model upgrade triggers a **re-baseline** (re-run
  the old version fresh), and re-running old-vs-its-own-cache *is* the drift detector.
- **Fit:** strengthens L3, reuses the `history`/`benchmark` schema (now carrying `model`), no new
  machinery. **Better alternative rejected:** keep frozen runs + statistically "subtract" model
  drift — unidentifiable from one sample, fragile. Folded into **§7.1 L3**.

### Iteration 3 — D1: every-dimension non-regression too strict → weighted gate + knockouts + VTR
- **Questioned:** a hard per-dimension floor blocks legitimate tradeoffs and floods neutral changes
  with no-signal ties.
- **Resolved by reasoning** (reuse existing factory patterns): **knockout** floor on always-high
  archetypes (S, + contract-marked high-floor) that may never regress; **weighted aggregate**
  (weight + weight_rationale) over the rest; an individual dip admissible only with a **VTR**
  (`vcd-log-tradeoff`); a tie is a pass with no re-baseline. Reuses ideation's
  `kind_of_criterion: weighted|knockout`, the EGP "S always high" rule, and the VTR mechanism.
- **Fit:** inherits trusted governance; makes the gate discriminating yet tradeoff-permissive.
  Folded into new **§7.6**; L3 now points at it.

### Iteration 4 — R1 reframe: cost = net human time saved, not apparatus size (developer correction)
- **Questioned (and refuted):** my blindspot R1 ("the mechanism is too large for the project /
  minimum-effective-dose"). The developer corrected: he will judge skill *performance*, but expects
  the LLM + scripts to **catch everything they can** so he saves time.
- **Resolution:** for PERSONA-015 the *effective* dose minimizes the developer's **residual manual
  effort**; a broad mechanism that nets time-saved IS minimum-dose. The discipline stays
  per-component (every check must be discriminating), but breadth is no longer penalized by size.
  Folded into **§4 #8** and **§9** (cost bullet). Supersedes blindspot R1; **R2 (altitude)** stays
  open only as the produce-vs-modify/where-to-bound question (now partly answered by Iteration 5).

### Iteration 5 — artifact-modifying capabilities: one mechanism, more meat (developer directive)
- **Questioned:** the concept implicitly tested *producing* capabilities; the highest-value factory
  skills *modify* artifacts (requ-explore extend, modify-skill/-agent, persona cascade, scribble
  loop).
- **Resolved by reasoning:** the modifying case is the *same* four layers judging the **delta** —
  intended-change set (I), invariant/blast-radius set (X, now primary), schema preserved (L1), plus
  idempotence/over-reach probes. Producing is the degenerate case (empty before-state). This makes
  the EGP **X** archetype load-bearing and explains why the playground's P-E/P-F couplings are the
  fixtures a modifying-skill test needs. Folded into **§3** (second axis), new **§7.7**, **§10**.
- **Fit:** unifies the mechanism instead of forking it; aligns capability testing with the
  playground's original P-E/P-F design intent.

### Iteration 6 — G2+G1: broaden the unit to *any governed instruction artifact* (developer decision)
- **Questioned:** the boundary at skills+agents excluded the highest-leverage artifact (CLAUDE.md)
  and tested only isolated units, never the seams (G1).
- **Developer decision:** include **all** governed instruction artifacts (skills, agents, CLAUDE.md,
  ordering-rules, orchestrator behavioural contract).
- **Resolved by reasoning — the elegant collapse:** behavioural-contract artifacts can *only* be
  tested by running capability **chains** (a task battery) and judging behaviour — so **G2 (broaden)
  and G1 (test the seams) are one mechanism.** Folded into **§2**, **§3** (three-tier unit table +
  §3.1), new **§7.8** (chain-level battery, I/X/S judged), **§10**. Highest time-saved tier (§4 #8):
  a constitution/ordering regression is exactly the silent cross-cutting damage a human can't catch
  by eye.

### Iteration 7 — D4: candidate isolation → reuse the deploy/scoped-cwd/git-reset model (read a file)
- **Resolved by reading** TASK-PROC-066-03 (deploy/assess synthesis): isolation already designed —
  deploy candidate into `test_harness_app/`, run **scoped with harness as cwd**, **git-reset** after,
  durable-fixtures vs disposable-outputs split. **Fit-fix discovered:** test definitions live in the
  **product tree** at `test_harness_app/factory_tests/<capability>/` (`run_instructions.md` +
  `expected_outcome.md`), NOT my invented `.claude/capability_tests/` — **§7.2 corrected.** Candidate
  treated as **untrusted** (esp. REQ-PROC-055 external adoptions); residual cwd-escape risk flagged
  to the dedicated execution-protocol task. New **§7.9**.

### Iteration 8 — B2: conformance ≠ good method (inherent → stated, not lost)
- **Resolved:** the test raises the floor (no *unfaithful* execution, no *self-inconsistent* output)
  but cannot certify the method is *right*; that stays human-authoring judgment — routed explicitly
  to a Register judgment-kind at create/modify time so it is **captured and surfaced**, not silently
  assumed. Stated in **§9**. Honest terminal limit per the goal's AC.

### Iteration 9 — B3: construct validity (partly inherent → hypothesis + correlate over time)
- **Resolved:** toy-fixture pass is a *hypothesis* of real-world good, not proof; mitigate by fixture
  realism + **correlating test verdicts against real-run outcomes** over time (a verdict real use
  contradicts = a fixture-realism defect). Gap never fully closes; stated in **§9**.

### Still open (genuinely, for the requirement to record honestly)
- **D3** — the L1/L2 line is a gradient, not a crisp line (deterministic proxies can give false
  confidence). Acknowledged; mitigated by the discriminating-check + evidence-citation rules. Minor;
  no further mechanism proposed.
- **R2 (altitude)** — substantially resolved: the unit is now principled ("governed instruction
  artifact", three tiers) rather than arbitrary.
- The **requirement-shape decision** (§11 Q-A..Q-E) remains the developer's to make.

### Iteration 10 — execution lifecycle & testability definition (developer directive)
- **Questioned:** the concept said *what* and *how* but not *when* tests are created/run, and never
  defined "testable".
- **Resolved by reasoning, grounded in EGP + the user's rules:** **testable ≡ fixture-exercisable
  AND EGP-bearing** (mechanically derivable from `contract.yaml`'s EGP disposition). Triggers:
  create → descriptor **authored inline** + a mandatory **test-task** (deferred run/improve, feeds the
  improve loop); modify-with-test → **ASK the developer** (declared user-input gate; `pending_feedback`
  in automated mode); modify-without-test → backfill task. Execution decoupled from authoring. New
  **§7.10**; §5.1 triggers + `render_user_input_gates.py` registration.
- **Fit:** uses the EGP disposition already on every contract (no new metadata), reuses the factory's
  user-input-gate + task-scheduling + claude-optimize machinery. **Sub-question resolved (developer,
  2026-06-21):** the descriptor is **authored inline at create** — the author knows the intent best,
  so the test cases are cheapest + highest-fidelity there; only the baseline run + improve loop defers
  to the task (§7.10 trigger 1, §5.1).

### Iteration 11 — extraction alignment: this IS the factory's testing oracle (read a file)
- **Questioned:** does the concept respect the factory-extraction plan, or contradict it?
- **Resolved by reading** TASK-PROC-066-01 goal: it **names 068-01 as the factory's "testing
  oracle"**, one of three self-applied quality loops, and ties it to the **validation-asymmetry
  concern** (factory tests app code, not its own artifacts). The developer's framing — "these tests
  are the factory's unit/integration tests" — is the official one. Folded into **§1 purpose** and new
  **§13**: portability/extractability + self-application are first-class requirements, not
  afterthoughts.

### Iteration 12 — adversarial validation incorporation (han-adversarial-validator, file `…_06_…`)
External adversarial pass (verdict: HOLDS WITH RESERVATIONS). I re-verified its load-bearing claims
against the live codebase — **all true** — and accepted every finding:
- **C1** (EGP floor: 90 violations; `ideation-start` has no `contract.yaml`) → §7.10 softened
  ("derivable *where declared*; else author-declares inline"); §9 new limit (the declaration has no
  oracle); §14 prerequisite.
- **C2** (`history.json` has no `model` field — only `benchmark.metadata.executor_model`) → §7.1 L3
  now labels model-pinning as **our Selective-*adapt* addition**, not upstream-reused.
- **C3** (execution substrate undesigned + harness not a factory project; AC-01 unchecked) → §7.9
  de-overclaimed; §14 prerequisite.
- **M1** (sequential tier ≠ same-turn) → §7.1 L3 caveat: version-match holds, residual sampling
  variance bounded by §9 controls.
- **M2** (HJR query interface AC-04 unimplemented) → §7.5 "resolved *in design*, activation is a
  prerequisite"; §14.
- **M3** (behavioural battery vs depth-1) → §7.8: child *sessions* (sanctioned deploy mechanism) ≠
  the depth-1 *agent* rule; still gated on the §14 substrate.
- **M4** (discriminating-check is retroactive) → §7.1 L2 reframed as authoring-*intent* confirmed by
  `eval_feedback`.
- **m1/m2/m3/m4** → §6.1 (per-script adopt deferred), §8 (D6 conditional), §5.3 ("only #6" is
  ideation-only), §6.2 (hook advisory, not enforcing).
- **Survived attacks** (no change): assert-on-process reframe, `factory_tests/` location, the EGP
  table, the weighted-gate/VTR reuse, the prior-art provenance — all confirmed grounded.
- **Disagreement recorded:** the validator's bottom line ("close the three gaps *before* the
  requirement-shape decision") conflates *assumes-them-done* with *must-wait-for-them*. A design task
  names prerequisites as **dependencies**; it does not build them first (§14). The fix was to make
  the requirement honest about the dependency ordering — not to invert requirements-before-impl.

---

## 13. Extraction alignment — capability tests as the factory's own test suite

This concept is **named infrastructure** in the factory-extraction plan (TASK-PROC-066-01), not a
standalone playground feature. Three obligations follow:

1. **It is one of the three self-applied quality loops.** The extracted factory must run, on its own
   artifacts: **completeness** (REQ-PROC-071 layer-derivation), **testing** (this concept), and
   **fix-scheduling** (claude-optimize / REQ-PROC-006). The three compose: completeness finds *what's
   missing*, testing finds *what's wrong*, fix-scheduling *schedules the repair*. A failing
   capability test (`lost`/knockout-breach) emits a claude-optimize event → a fix task — the loop
   closes without a human chasing it (the time-saving aim, §4 #8).
2. **It is the cure for the validation asymmetry.** App code has unit/integration tests + gates; the
   factory's instruction artifacts had nothing equivalent. Capability testing is that equivalent —
   "what unit/integration tests are for Dart code, capability tests are for skills/agents/CLAUDE.md".
   The requirement should state this as the *purpose*, so the extracted factory's own process
   **mandates** self-testing (extraction AC: "the factory's own process mandates them").
3. **It must be portable (the boundary question).** Per the extraction boundary map and the
   REQ-PROC-070 "same mechanism, language/project-parameterised" precedent (extraction seed 8):
   - **Factory-general (travels with the extracted factory):** the four-layer mechanism, the
     descriptor/`history`/`comparison` schemas, the rubric→EGP-archetype taxonomy, the run/reset
     protocol, the lifecycle triggers.
   - **Factory's own self-test fixtures:** `test_harness_app/` is the factory's *own* unit-test
     fixture (a tiny app it tests itself on) — it travels with the factory.
   - **Project-supplied (a consuming project configures):** any project-specific capability a
     consumer adds supplies its own descriptors + fixtures, without inheriting the factory's — the
     mechanism is parameterised, exactly like REQ-PROC-070's registry/gate.
   The requirement classifies the mechanism as **factory** in the extraction boundary map.

**Chain ordering (extraction AC):** extraction implementation tasks set `after` the oracle-verify
task; i.e. the oracle (this concept, proven on the ideation instance) is an *input* the extraction
consumes, not something it re-derives. So this concept should be specified to a *provable* bar (the
ideation instance is the proof) before extraction relies on it.

---

## 14. Prerequisites — current state vs. target state (validator C1/C2/C3/M2)

The adversarial pass established that several foundations the mechanism relies on **do not exist in
the codebase today**. They are real, and they gate **implementation** — not the **design**. The
distinction is load-bearing:

> A **requirement/design** (this task's deliverable) *names* its prerequisites as `after:`
> dependencies; it does **not** require them built first. Building the substrate before writing the
> requirement would invert the factory's requirements-drive-tasks order. So this task can complete;
> the prerequisites become `after:` edges on the **first impl + the ideation "proving" task**.

**The four prerequisites (each a dependency of the first capability-test impl, not of this design):**

| # | Gap (current state) | Needed for | Owner task |
|---|---|---|---|
| **P1** | `test_harness_app/` is a bare React app — **no** `CLAUDE.md`/`.claude/`/`requirements_*`/`factory_tests/` (REQ-PROC-068 AC-01 unchecked) | every fixture/descriptor path; deploy target | the structural-mirror corrective task (REQ-PROC-068 dep) |
| **P2** | The deploy / scoped-run / git-reset **mechanism** is only *constraints*, explicitly deferred | L3, L4, chain-battery — all runs | the dedicated **execution & reset protocol** exploration (TASK-PROC-066-03 names it) |
| **P3** | Tested capabilities lack an **EGP disposition** (90 floor violations; `ideation-start` has no `contract.yaml`) | L2 dimension derivation | an EGP-backfill step on the capabilities to be tested (folds into their contracts) |
| **P4** | The Human-Judgment-Register **query interface** (REQ-PROC-044-05 AC-04) is unimplemented (types layer exists; corpus unreachable) | live judge **calibration** (B1/D2 *activation*) | REQ-PROC-044-05 AC-03/AC-04 impl |

Also **P5 (schema):** model-pinning *adapts* `history.json` (adds `executor_model`/`judge_model`) —
a Selective-**adapt** decision for the REQ-PROC-055 adoption task (not a verbatim reuse).

**What is *not* blocked:** the conceptual architecture (the four layers, the EGP spine, the
produce/modify axis, the descriptor *contract*, the lifecycle triggers, the testability definition)
is stable and substrate-independent — it is the WHAT the requirement states. The substrate-dependent
HOW (run model §7.4, child-session battery §7.8, isolation §7.9) is correctly deferred to P1/P2,
which is where the factory's requirements-vs-tasks separation already puts it.

**Net (answers "finish other tasks first?"):** *No* to gating the **requirement** on P1–P4 — write
it now, naming them as dependencies. *Yes* to gating the **first implementation** (and the ideation
"proving" run the extraction consumes) on P1–P4. The recommended order: **P3 + P1 first** (cheap,
unblock everything), **P2** (the substrate exploration — the long pole), **P4** in parallel
(calibration can activate late), then the ideation-instance proof, then extraction.
