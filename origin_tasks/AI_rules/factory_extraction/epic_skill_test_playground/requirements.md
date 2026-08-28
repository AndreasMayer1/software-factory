---
id: REQ-PROC-068
status: active
market_research_refs: [] # No relevant findings identified
trackable_items:
  acceptance_criteria:
    - id: AC-01
      egp: { not_bearing: true, reason: "structural mirror — checkable by inspecting the harness folder for the named subtrees" }
      egp_auto: { archetype: Q }
    - id: AC-02
      egp: { archetype: X, referent: "the emergent cascade relationship across the harness's dependent features when the shared entry surface changes" }
      egp_auto: { archetype: Q }
      consequence: MEDIUM
    - id: AC-03
      egp: { not_bearing: true, reason: "checkable from the harness form artifact and the designated mid-release edit it carries" }
      egp_auto: { archetype: Q }
    - id: AC-04
      egp: { archetype: F, referent: "the emitted probe outputs of a real workflow run on the harness" }
      egp_auto: { archetype: Q }
      consequence: MEDIUM
    - id: AC-05
      egp: { not_bearing: true, reason: "checkable by inspecting the scribble-to-code handoff artifacts for any framework (Flutter) assumption" }
      egp_auto: { archetype: Q }
    - id: AC-06
      egp: { not_bearing: true, reason: "checkable by the location of the product-definition files in the harness project tree" }
      egp_auto: { archetype: Q }
    - id: AC-07
      egp: { archetype: F, referent: "the observed behaviour of a real deploy-run-reset cycle returning the harness to a clean state" }
      egp_auto: { archetype: Q }
      consequence: MEDIUM
    - id: AC-08
      egp: { archetype: C, referent: "the real token consumption + wall-clock duration of the child sessions a test run launches" }
      egp_auto: { archetype: Q }
      consequence: MEDIUM
    - id: AC-09
      egp: { archetype: S, referent: "a real untrusted candidate factory launched as a child session attempting to reach the host factory tree via absolute paths or working-directory escape" }
      egp_auto: { archetype: Q }
      consequence: HIGH
    - id: AC-10
      egp: { archetype: F, referent: "a real workflow run in which a contained child session runs a script-calling factory skill end-to-end inside the harness jail, completing without reaching the host factory tree" }
      egp_auto: { archetype: Q }
      consequence: MEDIUM
    - id: AC-11
      egp: { archetype: F, referent: "a real build/maintain run observed to derive the harness layers in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them; and to retain its own factory-runtime provenance as project data" }
      egp_auto: { archetype: F }
      consequence: MEDIUM
    - id: AC-12
      egp: { archetype: F, referent: "a real contained child launch observed under each ~/.claude and ~/.ccs presence/absence combination — the resulting bind set and the success/error outcome" }
      egp_auto: { archetype: F }
      consequence: MEDIUM
    - id: AC-13
      egp: { archetype: F, referent: "a real build/maintain run observed to create its isolated deployed copy at the configured durable location as its own git repository, not in an OS temp directory" }
      egp_auto: { archetype: F }
      consequence: MEDIUM
    - id: AC-14
      egp: { archetype: F, referent: "a real interrupted build/maintain run observed to preserve the isolated copy and perform no harvest, and a real completed run observed to harvest then discard" }
      egp_auto: { archetype: F }
      consequence: HIGH
    - id: AC-15
      egp: { archetype: F, referent: "a real cold session observed to discover an in-progress run from the run registry and resume the derivation without re-running deploy/seed/snapshot" }
      egp_auto: { archetype: F }
      consequence: MEDIUM
    - id: AC-16
      egp: { archetype: F, referent: "a real build/maintain run interrupted by a usage-limit observed to resume after the shared account window resets with no automation-orchestrator code change" }
      egp_auto: { archetype: F }
      consequence: MEDIUM
    - id: AC-17
      egp: { not_bearing: true, reason: "checkable by inspecting that the resumable-run machinery is parameterized by an injected completion predicate rather than hard-coded to layer-derivation" }
      egp_auto: { archetype: Q }
    - id: AC-18
      egp: { archetype: F, referent: "a real build/maintain run's observed termination mode + acceptance-oracle result + presence/absence of a recorded blocker artifact + per-unit structural degeneracy (which units have real authoring pairs vs zero), checked against the outcome the playground classifies and reports for it" }
      egp_auto: { archetype: F }
      consequence: HIGH
    - id: AC-19
      egp: { archetype: F, referent: "a real build/maintain run observed with no injected acceptance oracle (must not harvest, must not report success), a real run with a degenerate span observed to be counted vacuous-complete by the oracle, and a real run whose child holds an in-flight background agent at -p return (must not be observed as a clean complete exit)" }
      egp_auto: { archetype: F }
      consequence: HIGH
    - id: AC-20
      egp: { archetype: F, referent: "a real sequence of maintenance (build/maintain) runs observed to keep earlier runs' referenced commits reachable in the harness git after restore-from-persisted-history" }
      egp_auto: { archetype: F }
      consequence: HIGH
    - id: AC-21
      egp: { archetype: X, referent: "the absence of harness-specific handling across all non-playground factory mechanisms" }
      egp_auto: { archetype: X }
      consequence: MEDIUM
    - id: AC-22
      egp: { archetype: F, referent: "a real doomed spec (incl. an all-degenerate spec) observed to fail the pre-flight at plan time and consume no deployed run, and a real resume observed to re-validate the pre-flight verdict before reaching harvest, checked against what the deployed run would actually classify" }
      egp_auto: { archetype: F }
      consequence: HIGH
---
# Epic: Skill-Test Playground (Test-Harness Instrument Spec)

## Overview
The **factory-side specification** of the Skill-Test Playground: a small, offline, single-user **personal
media-rating & journaling app** (private notes on movies/books — ratings, tags, a review, a home dashboard)
that the Software Factory *runs on* as its standing test instrument. It defines the app **as a testing
instrument** — why it exists, what it must contain/emit. Process requirement; **not** directly implementable.

## Purpose
Iterating a factory workflow against the real release costs a full release decomposition per loop; a small
consumer makes each loop 10–100× cheaper. This playground is that consumer — kept and grown. Its first job is
to validate the scribble-gate redesign (TASK-PROC-032-29); its standing job is to give *every* factory skill
something real to bite on — a good **factory exerciser**, complexity in its *couplings* not its feature count.

## Scope & the two-tree split (no duplication)
- **This factory tree (instrument spec):** the mirror requirement, the couplings (P-E/P-F/T4), the six probes,
  the deploy/assess/tech-agnostic constraints, build order — framework-agnostic, no product UI detail. It does
  **not** enumerate test cases or define *what integration tests are* (separate, later).
- **`test_harness_app/requirements_user_needs/` + `requirements_tasks/` (product definition):** personas,
  scenarios, flows, screen behaviour, the rating-form data-point table — authored by the **factory skills
  themselves** as the first real exercise. Product detail lives **only** there.

## Real-Project Mirror (hard requirement)
`test_harness_app/` (at the git repo root) MUST mirror the folder structure of a real factory-built *project*
— own `CLAUDE.md`, `requirements_user_needs/`, `requirements_tasks/`, `doc/`, `src/` — so factory skills
resolve their conventional root-relative paths correctly when run with the harness as cwd (see the **Deploy &
isolate** invariant). The harness stays inside `flutter_app/` and is extended together with the factory.

## Features (instrument-feature specs — coupling intent only; product detail lives in the project tree)
Now-slice (the minimal subset that structurally contains the redesign's hard cases):
- [feat_home_dashboard](feat_home_dashboard/requirements.md) — shared entry/hub surface; origin of the
  cross-feature UI cascade (P-F).
- [feat_rating_entry_form](feat_rating_entry_form/requirements.md) — validation-heavy data-bound form (T4);
  target of the scripted mid-release edit (P-E).
- [feat_library_browse](feat_library_browse/requirements.md) — cascade dependent #1.
- [feat_collection_insights](feat_collection_insights/requirements.md) — cascade dependent #2.
- [feat_measurement_instrumentation](feat_measurement_instrumentation/requirements.md) — the six measurement
  probes the fixture + workflow must emit.

Growth (not built now; added around the same dashboard without rewriting the now-slice): **persona-conditional
rating facets** (film-studies craftsmanship vs. sociology facets; genre-triggered + user-defined fields),
search, recommendations, import/export.

## Build / Derivation order (run the real factory chain on the harness)
(1) structural mirror → (2) personas → (3) scenarios → (4) flows → (5) requirements
(`requ-derive-from-flow`/`requ-explore`) → (6) tasks (`task-derive-from-requ`) → (7) scribble gate + code (the
validation, emitting the six probes). Steps 2–4 author the **minimum** personas/scenarios/flows the test case
needs (enough to fire P-E/P-F/T4), not a believable product's worth. Where a skill assumes Flutter or a single
project root, that is a **finding** to improve the skill — not a special case.

## User Needs (described here; formalised in the project tree)
Personas: **Archivist** (completeness) vs **Quick-Logger** (speed) — a real value conflict on the entry form.
Flows (add a rating, browse, review insights) all pass through the dashboard. Minted as real PERSONA-*/FLOW-*
artifacts in `test_harness_app/requirements_user_needs/`, not in the mood-tracker's tree.

## Cross-Feature Invariants
- **Shared entry surface:** the dashboard publishes a composition contract; dependents register a card/entry,
  so a dashboard interaction-model change ripples into dependents whose own requirements are unchanged (P-F).
- **Tech-agnostic hand-off:** the scribble→code hand-off separates tech-neutral **design-intent** from
  **target-binding** (web framework); no artifact may assume Flutter. (Full tech-agnostic architecture is a
  dedicated work item — see Dependencies.)
- **Deploy & isolate:** the candidate factory is deployed into the harness and run with the harness as cwd,
  then git-reset between runs — each run repeatable from a clean state.
- **Instrumented & assessed:** a run emits the six probes; each factory-skill/workflow test carries a
  `run_instructions` file + a **non-boolean quality-scale outcome rubric** (in the harness) the probes feed —
  capturing quality improvement, not only completeness.

## Dependencies
- **Web toolchain & gates** — TASK-PROC-066-04 stands up the React (confirmed) toolchain + web quality gates.
- **Structural mirror** — a corrective task makes `test_harness_app` mirror a real project + relocates web `doc/`.
- **Test-harness execution & assessment protocol** — a dedicated exploration designs the deploy/run/git-reset
  mechanism + the run-instructions/outcome-rubric format.
- **Factory technology-agnosticism architecture** — a dedicated exploration (with TASK-PROC-066-01) designs the
  techstack config + routing/facade for tech-dependent scripts and skill/agent calls.
- **Factory extraction** — TASK-PROC-066-01 (sibling); the deploy boundary this epic adopts interacts with it.

## References
- Synthesis: this task's `plans_and_protocols/` (`…_01_shape`, `…_02_two-tree-reframe`, `…_03_deploy-assess`);
  redesign substrate reports `06`, `08`, `10`, `12`.
- AC-10 grounding: `…/2026-06-11_explore_llm-verifiable-open-ended-skill-tests (completed)/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`
  §"Revision (2026-07-01, developer)" — whole-factory-deploy decoupled from REQ-PROC-066; T-B impl is a
  separate downstream task; the coarse exclude-set is impl guidance, not part of this AC.
- AC-13..AC-17 grounding (build-mode resumability): `tasks/2026-07-08_explore_build-mode-resumability/plans_and_protocols/2026-07-09_006_synthesis_v2.md`
  (developer-approved SOL-02) — durable out-of-project git-backed copy, completion-gated harvest, run
  registry + cold re-attach, usage-limit-as-freeze with no orchestrator change, injected-completion-predicate seam.
- AC-18/AC-19 clarification + AC-22 (harvestability pre-flight) grounding: `tasks/2026-07-14_explore_fix-degenerate-span-harvest-and-spec-authoring/plans_and_protocols/2026-07-15_004_synthesis.md`
  (developer-approved SOL-01, IDEATION-023) — the degenerate zero-authoring-pair span is a vacuous-complete
  terminal, not an unfinished one; "abandoned" is narrowed to a real-authoring under-finish; a plan-time
  pre-flight predicts the oracle verdict (rejecting all-degenerate specs) before any deployed run is spent.
  The complementary mechanism disposition is REQ-PROC-071-06 AC-09/AC-10.

## Deferred (YAGNI)
### Hard cost cap + circuit-breaker (`max_budget_usd`)
**Why deferred:** the disproof spike is a one-shot, single-pair run with inherently bounded cost; the hard `max_budget_usd` cap and clean-abort circuit-breaker (SOL-01's co-essential "cap + ledger + clean-abort") are needed only once the walking-skeleton runs repeatedly and could accumulate unbounded spend. AC-08 commits to cost *measurement*, not yet enforcement.
**Reopen when:** the walking-skeleton runs more than the one-shot spike (the full SP-03 cost-model authoring at T-orch1).
**Source:** SOL-01 SP-03.

## Acceptance Criteria
- [ ] AC-01: `test_harness_app/` mirrors a real factory-built project's structure (own `CLAUDE.md`, `requirements_user_needs/`, `requirements_tasks/`, `doc/`, `src/`).
- [ ] AC-02: The harness contains a shared entry-surface feature whose interaction-model change cascades into ≥2 dependent features whose own requirements are unchanged (P-F).
- [ ] AC-03: The harness contains a validation-heavy data-bound form whose one isolated rule is the scripted mid-release edit that invalidates an approved scribble (T4 + P-E).
- [ ] AC-04: A workflow run emits the six probes (see feat_measurement_instrumentation) and the test carries a `run_instructions` file + a non-boolean quality-scale outcome rubric (in the harness) the probes feed.
- [ ] AC-05: The scribble→code hand-off separates tech-neutral design-intent from web target-binding (no Flutter assumption).
- [ ] AC-06: The app's product definition (personas, flows, feature requirements) lives in `test_harness_app/requirements_*`, authored via the factory skill chain — not in this factory tree.
- [ ] AC-07: A test run deploys the candidate factory into the harness, runs with the harness as cwd, and git-resets the harness between runs (repeatable from a clean state).
- [ ] AC-08: A test run records the real token consumption and wall-clock duration of every child session it launches, attributed to that run.
- [ ] AC-09: A candidate factory deployed into the harness executes as an isolated child session whose reads and writes cannot reach any factory tree outside the harness working tree — including via absolute paths or working-directory escape (CON-04); an untrusted candidate has no path to read or modify the host factory tree. This isolation guarantee covers the host *factory tree*; the host Claude/CCS auth-config directories named in AC-12 are the sole intentional exception.
- [ ] AC-10: A deploy places the *whole* factory into the harness so a contained child session can invoke any factory skill end-to-end using only the deployed contents, with no reach-back to the host factory tree. ("Whole factory" means everything the factory provides — defined by the factory itself, never by a file/artifact enumeration in this requirement. AC-09 guarantees the child *cannot* reach out; AC-10 guarantees it *need not*, because the deploy is complete — a skills-only deploy fails it, a whole-factory deploy passes it.)
- [ ] AC-11: A build/maintain run derives the harness's own product-definition layers inside an isolated deployed copy of the whole factory (so the derivation runs as its own project), then places the resulting product-definition artifacts — the categories the factory artifact registry (`.factory/registry/artifacts.yaml`) designates as product definition: user-needs (personas/scenarios/flows), requirements, scribbles, and app source — into the persistent `test_harness_app/` tree. A build/maintain run retains the derived layers (distinct from a test run's clean reset, AC-07); the transient deployed factory machinery — the skills, scripts, and registries copied in to run the derivation — is absent from `test_harness_app/`, while the harness retains its own factory-runtime provenance grounding its product definition (the ideation index and ledger backing a derived decision) as project data of the standalone harness. — EGP: F (a real build/maintain run observed to derive in an isolated deployed copy and deposit the registry-classified product-definition artifacts into test_harness_app/, retaining them); consequence: MEDIUM
- [ ] AC-12: The contained child session is granted read-write access to the host Claude auth-config directory (`~/.claude`) and, when present, the host CCS multi-account directory (`~/.ccs`), each bound into the jail at its real absolute path so that `claude` and `ccs` invoked inside the jail authenticate and operate. `~/.claude` is mandatory; `~/.ccs` is optional: with both present, both are bound; with `~/.claude` present and `~/.ccs` absent, only `~/.claude` is bound and no error or warning is emitted (a host that does not use CCS is fully supported); with `~/.claude` absent, the launch fails with an error (no authentication is possible, and CCS cannot operate without Claude). These auth-config directories are the only host paths outside the harness workspace present in the jail — the host factory tree remains absent (AC-09). The exposure is scoped to the trusted skill-under-test use case; a genuinely untrusted candidate factory could read the bound credentials, so this binding is not a safe boundary against an untrusted candidate. — EGP: F (a real contained child launch observed under each `~/.claude` and `~/.ccs` presence/absence combination — the resulting bind set and success/error outcome); consequence: MEDIUM
- [ ] AC-13: A build/maintain run's isolated deployed copy resides at a durable location resolved by the same worktree-root convention the factory's worktree-creating skills use (`<repo root>/.worktree` by default, overridable by the per-developer project-environment config), gitignored and excluded from the deploy's own copy so the copy is never self-referential, and is its own git repository so per-unit commits accrue inside it. The copy is never placed in an ephemeral OS temp directory. — EGP: F; consequence: MEDIUM
- [ ] AC-14: A build/maintain run deposits product-definition artifacts into `test_harness_app/` and discards the isolated copy only once an explicit completion signal confirms the derivation finished. On any non-complete termination — usage-limit, timeout, hung session, or crash — the isolated copy is preserved and no harvest occurs, so a partial or incoherent deposit into `test_harness_app/` cannot happen (preserve-by-default, discard-only-on-verified-complete, skip-harvest-on-incomplete). — EGP: F; consequence: HIGH
- [ ] AC-15: A host-side run registry records each in-progress build/maintain run's resumable state — its durable copy location, the derivation session identity, and completion status — so that a later cold session discovers the in-progress run and re-attaches to resume the derivation from its preserved state, without re-running deploy/seed/snapshot and without a human supplying paths by hand. Safe cold re-attach assumes a single active runner — no other live process holds the same run — which the serialized orchestrator provides by running one session at a time; concurrent build/maintain execution of the same run lies outside this assumption and requires a liveness or lease check before re-attach to prevent two child sessions operating on one copy. — EGP: F; consequence: MEDIUM
- [ ] AC-16: A usage-limit hit during a build/maintain run is a planned pause requiring no modification to the automation orchestrator: the shared account window freezes the nested outer and inner orchestrators together and each resumes after the window resets, and the outer run learns of derivation completion by polling the completion signal at an interval that scales with the estimated remaining work rather than a fixed period. Under automated orchestration the run is a resumable task so the orchestrator's existing resume path carries it across the pause; no explicit external pause mechanism exists (the orchestrator stop signal is the documented extension point should a preemptive-pause need ever arise). — EGP: F; consequence: MEDIUM
- [ ] AC-17: The resumable build/maintain machinery (durable copy, run registry, completion-gated harvest) is parameterized by an injected completion predicate, so any long deployed run reuses it and layer-derivation is one instance rather than the hard-coded case. — EGP: not-bearing (self-certifiable — checkable from the wrapper's parameterization)
- [ ] AC-18: Every build/maintain run resolves to exactly one classified outcome that determines its disposition: **complete** (clean child exit and the injected acceptance oracle confirms the derivation finished — every unit at a completion-satisfying terminal, where a structurally degenerate zero-authoring-pair unit is vacuously complete rather than unfinished) is the only outcome whose deposit is harvested; **interrupted** (non-clean termination — usage-limit, timeout, hung session, or crash) preserves the copy for resume (AC-14/15/16); **blocked** (clean child exit with an explicit blocker or escalation artifact recorded) is a developer-facing pause that is neither harvested nor treated as a failure of the skill under test; **abandoned** (clean child exit with the acceptance oracle reporting not-finished, no blocker or escalation artifact recorded, and at least one unit that has real authoring pairs left non-terminal) is reported as a run failure attributable to the completion guidance of the skill under test, and is neither harvested nor auto-resumed. A run whose only units short of an authored terminal are structurally degenerate no-op spans is **complete**, never abandoned, and is never blamed on the skill under test — a mandatory no-op span the spec structure forced is not a completion failure of the skill. — EGP: F; consequence: HIGH
- [ ] AC-19: The completion gate never certifies a run complete without a positive result from an injected acceptance oracle — an absent oracle yields "cannot certify complete", so the run is neither harvested nor reported as successful. "The derivation finished" means every unit with real authoring pairs reached its authored terminal and every structurally degenerate zero-authoring-pair unit reached its vacuous-complete terminal; the oracle counts a vacuous-complete unit as satisfying completion exactly as an authored terminal does, and cannot be satisfied by a unit that has real authoring pairs but no authored terminal. A clean child process-exit reflects the child session's own completion decision: a background agent still working inside the child cannot cause the run to be observed as a clean, complete exit. — EGP: F; consequence: HIGH
- [ ] AC-20: A maintenance (build/maintain) run's deployed copy initializes its git repository by restoring the harness's persisted history rather than a fresh empty repository, and on harvest the copy's advanced history is persisted back with the harness in the container project, so a commit reference a run records (a materialization artifact's provenance commit, a task's pinned requirements version) stays reachable in every later run. The persisted history retains every commit a harvested artifact references and omits unreferenced intermediate commits; commits persisted by prior runs are immutable. A test-mode run, which resets to a clean baseline after each run, carries no persisted history. — EGP: F (a real sequence of maintenance runs observed to keep earlier runs' referenced commits reachable in the harness git after restore); consequence: HIGH
- [ ] AC-21: The harness's presentation as an ordinary standalone project is established entirely within the playground deploy/harvest mechanism: durable git history and the harness's own factory-runtime provenance are provided by the playground, so no other factory mechanism contains handling specific to the harness being a test fixture — every other mechanism operates on the harness exactly as on any real project. — EGP: X (the absence of harness-specific handling across all non-playground factory mechanisms); consequence: MEDIUM
- [ ] AC-22: A build/maintain spec is screened by a harvestability pre-flight before any isolated copy is deployed. Reusing the same span resolution, per-span disposition typing, and injected acceptance-oracle predicate the run itself would use, the pre-flight predicts — over the best-case terminal state in which every real-authoring span reaches its authored terminal and every structurally degenerate span reaches its vacuous-complete terminal — whether the run could ever be certified complete and harvested. A spec that cannot be harvested even under that best case fails the pre-flight at plan time with a distinct doomed-spec outcome and consumes no deployed run; an all-degenerate spec (every span a zero-authoring-pair no-op, so nothing would be authored) is one such doomed spec and is rejected at plan time rather than deployed. The pre-flight verdict is persisted and re-validated on every resume, so no start or resume path reaches harvest without a current positive pre-flight. — EGP: F; consequence: HIGH
