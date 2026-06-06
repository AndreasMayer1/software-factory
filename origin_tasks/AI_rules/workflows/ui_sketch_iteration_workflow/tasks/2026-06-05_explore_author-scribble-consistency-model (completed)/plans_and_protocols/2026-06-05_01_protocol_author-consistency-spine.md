# Protocol — Author the Scribble Consistency & Layer Model into REQ-PROC-032 (T-A2)

Task: TASK-PROC-032-30. Date: 2026-06-05. Agent ID: abcbebad43ebf99dc.
Skill: requ-explore (Scenario E — extend REQ-PROC-032, do not restructure).

## 1. Synthesis round — the consistency model in my own words

The scribble is the locked-in design contract a coding task consumes. The whole consistency layer
exists to keep that contract trustworthy across a release's life — through mid-release requirement
edits, cross-feature cascades, and the discrepancy window between a requirement changing and its
scribble catching up. The model is one invariant + a closed set of staleness edges + mechanical
loopback rules.

### Seed 1 — SCI as continuously-enforced invariant (one rule, both times)
The "hard gate" and the "mid-release discrepancy governance" are not two mechanisms; they are the
same invariant observed at two times. I authored AC-42 as: *no coding task is runnable while a
covered scribble is missing/unapproved/stale relative to the requirement's current commit*. At
release start, the scribble gate withholds coding decomposition (temporal establishment); mid-release,
an edit that invalidates a covered scribble keeps dependent coding tasks non-runnable until refresh.
Currency is verifiable identically at t=start and t=mid-release by inspecting each coding task's
covered scribbles. That collapses two sub-problems (P-A hard gate, P-E discrepancy window) into one
standing property — verified by the SCI audit (AC-43).

### Seed 2 — generative-blocks / referential-flags discriminator (which readers block, which flag)
A reader that *generates a downstream artifact* from a stale scribble BLOCKS (ordering edge on the
refresh task; already-running ⇒ SCI violation): the covering coding task (consumes the scribble as UI
contract), a dependent scribble (generates a wireframe from the shared entry surface), and the
verification verdict (produces a pass/fail against the scribble). A reader that merely *references*
the scribble FLAGS it (`stale_since` banner, no block): flow composite index, scribble index, release
notes, approval trail, coverage report. Verification reader blocks by default but has an explicit
advisory override that runs and labels the verdict "against a stale target." Authored as AC-54.

### Seed 3 — facet-tagging accuracy hedge
Tagging accuracy is empirical, so AC-53 hedges: every Presentation requirement's ACs carry a facet
tag {presentation | behaviour | both}; the tag is auto-heuristic THEN human-confirmed; on ambiguity
it FAILS SAFE to `presentation` so an ambiguous AC always passes through the scribble gate (errs
toward more design review, never less). An audit records auto vs confirmed tag per AC. The data-bound
detector (AC-52) reuses these tags: a scribble is data-bound iff its presentation/both ACs reference a
domain value-object that itself has behaviour ACs in the same design-unit; soft ordering edge by
default, hard only for code-first units, human override at the gate.

### Seed 4 — width-breaker thresholds as configurable, measured-on-fixture defaults
AC-47 authors the two-stage breaker: soft threshold annotates the gate while auto-creation continues;
hard threshold stops auto-creation and escalates via back-pressure with the walked sub-graph. Both
configurable; shipped defaults soft=3 / hard=7, explicitly designated *starting values to be tuned
against the first measured fixture cascade*. Recovery stays bounded and human-escalated.

### The five-edge rot-graph (AC-44)
Closed set, each with a detector: (1) requirement→scribble (`stale_since` on LOCKED-IN edit);
(2) scribble→coding (SCI audit); (3) domain-code→data-bound scribble, code-first units only
(domain-commit comparison); (4) scribble→dependent scribble on outward-entry-surface change
(lazy-wavefront detector); (5) scribble→verify verdict (verification currency check). No path outside
these five.

## 2. ACs added (intent, one line each)

- **AC-42** — Scribble-Currency Invariant holds continuously (Seed 1; one rule covering t=start and t=mid-release).
- **AC-43** — Standing script-driven SCI audit; blocking gate at finalization; additive to parity check.
- **AC-44** — The five-edge staleness rot-graph, each edge with its named detector.
- **AC-45** — Loopback-as-task taxonomy L1–L6 (normative-upstream ⇒ new task; un-approved scribble ⇒ same task, new version).
- **AC-46** — Lazy-wavefront depth-1 cross-requirement cascade; live `flow_positions`; visited-set termination.
- **AC-47** — Two-stage width breaker, configurable, soft=3/hard=7 measured-on-fixture defaults (Seed 4).
- **AC-48** — L3 coverage assertion (source-check sound iff every Presentation req has scribble/source-check) + chain-length alert.
- **AC-49** — Entry-context spine (PROP-8): emit + reviewer check + bounded reconciliation + container dimension.
- **AC-50** — Coverage/ordering (PROP-9/11 R1–R3 + G1–G4): coverage report, auto scribble task, primary-path depth-1 ordering, basis resolution.
- **AC-51** — App-shell/launch-map requirement (R4) + two-tier seam detection — authored as a constraint (skill change lands in T-C17).
- **AC-52** — Domain→design conditional edge + data-bound detector (reuses facet tags + design-unit map).
- **AC-53** — AC facet-tagging {presentation|behaviour|both}: auto + human confirm, fail-safe to presentation (Seed 3).
- **AC-54** — Generative readers block / referential readers flag (Seed 2); verify hard-block + advisory override.
- **AC-55** — Soft-SCI as configurable, sign-off-gated mode, default OFF (authoring decision a).

Plus body section **SEC-18 "Consistency and Scribble-Layer Model"** prose-anchoring [AC-42..AC-55].
Existing ACs (AC-01..AC-41) and sections (SEC-01..SEC-17) untouched. Status left `active`. No
`target_package` on new ACs (internal factory-process tooling — matches all existing ACs in the file).

## 3. The two authoring decisions (recommendation made; developer sign-off requested)

**(a) Soft-SCI mode** — authored as AC-55: an explicit configurable, sign-off-gated mode, **default OFF**.
Recommendation X = "mode, default OFF." *Sign-off requested.* Overriding to "documented pivot only"
(no mode at all) would remove the liveness escape hatch the contingency plan (E1-B2) keeps available
for densely-coupled releases; the near-one-way-door reversibility analysis (`12` §Branch reversibility)
is why it must exist but stay gated rather than be a silent default.

**(b) Width-breaker / §0.6 thresholds** — authored into AC-47 as configurable with measured-on-fixture
defaults (soft=3 / hard=7), and the validation task (T-CV) is where these defaults are accepted/tuned
against the §0.6 pre-registered thresholds. Recommendation X = "bake thresholds into T-CV's acceptance,
phrased configurable." *Sign-off requested.* Overriding to "hard-code in REQ-PROC-032" would freeze the
numbers before any fixture measurement, contradicting Seed 4 and §0.6's pre-registration discipline.

## 4. What remains uncertain (honest)

- **Facet-tag accuracy (E5)** — AC-53's heuristic mis-tag rate is unmeasured; the fail-safe-to-presentation
  hedge bounds the *direction* of error but not the over-serialization cost until measured on the fixture.
- **Cascade width / breaker N (E2)** — AC-47 ships 3/7 as guesses; the real wavefront width is unmeasured.
  The fixture's deliberate dashboard hub is the highest-likelihood place this goes red (risk register).
- **Liveness under hard SCI (E1)** — AC-42 guarantees correctness, not liveness; a wide mid-release edit
  can serialize. Per-design-unit scoping (authored in the T-A1 spine, not here) mitigates; AC-55 soft-SCI
  is the escape hatch. No throughput model exists yet.
- **`both`-facet ACs in both waves (AC-53)** — the mechanism is settled; whether the `both` share is small
  enough that human-confirm stays cheap is empirical.
- **Edge 3 (domain-code→scribble)** — only active for code-first design-units (a per-unit exception from
  the redesign's B3 decision); how often code-first is actually invoked is unknown until real releases.

## 5. Cross-reference to manifest

This is T-A2 (`13_implementation-task-manifest.md`). It feeds [DERIVED] impl tasks T-C8 (SCI/stale_since/
audit), T-C9 (verify hard-block), T-C10 (loopback-as-task), T-C11 (cascade+breaker+PROP-10), T-C12
(entry-context spine), T-C13 (coverage/ordering + L3 assertion/alert), T-C14 (domain→design + facet
tags), and the R4 constraint consumed by T-C17. `task-derive-from-requ` generates those after this lands.

Agent ID: abcbebad43ebf99dc.
