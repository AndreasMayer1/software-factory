# Synthesis — the shape of the skill-test playground (epic + now-slice)

Task: TASK-PROC-066-03. Date: 2026-06-05. Agent: main session (Opus).
Substrate read: redesign reports `06` (extraction+playground), `08` (T4 domain-before-design),
`10` (next-steps plan, Q1=fixture-first, Q2=web), `12` §"Fixture instrumentation" (the six probes);
the developer's verbatim seed (`00`); sibling tasks TASK-PROC-066-01 (extraction), -04 (web toolchain).

---

## 0. The one move this task has to get right

The hard part is **whole↔slice coherence**: write ONE epic for a *general* skill-test playground (something
the whole factory can eventually be run on) and carve out a NOW-slice of features that is a **strict subset**
of that whole — not a throwaway. If the now-slice is a faithful subset, growing the playground later is pure
addition; nothing built now gets rewritten.

The governing constraint from `06`: **complexity must live in the couplings, not the feature count.** A
"less complicated" app is the *wrong* playground because the redesign exists to handle the hard cases
(P-E, P-F). So the now-slice is sized by *which couplings it must structurally contain*, not by how many
screens feel like a believable product.

## 1. What is the general playground, as a product? (the epic)

**Decision: a personal, offline media-rating & journaling app** — the developer's "movie/book rating" seed,
enriched only as far as needed to make it a good *factory exerciser*. One person's private notes on the
movies and books they have consumed: ratings, tags, a short review, and a home dashboard that summarises
their own activity. Offline, local-only, single-user.

Why this product is a good factory exerciser (the test is "does it give every skill something real to bite
on", not "is it a believable app"):

| Factory capability | What the media-rating app naturally provides |
|---|---|
| personas with conflicting values (ux-write-persona, VCD) | the meticulous **Archivist** (values completeness/data integrity) vs the **Quick-Logger** (values low-friction speed) — a real value conflict on the entry form |
| flows sharing an entry surface (ux-create-flow, requ-derive-from-flow) | a **home dashboard** every feature is reached from / surfaces onto |
| cross-feature UI cascade — **P-F** | the dashboard is a genuine hub: change its interaction model and the ripple hits Library + Insights + the quick-add entry |
| validation-heavy data-bound form — **T4** | **add/edit a rating**: title, type, rating scale, date consumed, tags, review — many fields, many formats, real validation |
| mid-stream requirement edit — **P-E** | the rating-scale requirement is *designed to be edited* mid-release (e.g. 1–10 → half-star), invalidating an approved scribble |
| domain model / value objects / data layer | Rating entity + validated value objects; local persistence |
| design system / shared components (ui-scribble-*) | dashboard cards, list rows, the form's field components are reused across features |
| privacy/security surface (SP gates, eventually) | local-only personal data — an eventual hook, not now-slice |

This is the developer's seed, not a replacement for it — enriched exactly enough that the dashboard is a real
hub and the form is genuinely hard.

## 2. The now-slice — smallest set that *structurally* contains P-E, P-F, T4

**Five features** (`06`'s "~4–5 requirements, not a product"):

1. **`feat_home_dashboard`** — the shared entry/hub surface. **Origin of P-F.** Composes summary cards +
   entry points for the other features. Its interaction-model change is the scripted cascade origin.
2. **`feat_rating_entry_form`** — the validation-heavy add/edit form. **Carries T4** (multi-field, multi-format,
   validated; backed by a domain Rating value-object) **and is the P-E target** (its rating-scale requirement
   is the one edited mid-release).
3. **`feat_library_browse`** — list/filter/search over rated items. **P-F dependent #1** — draws an entry
   summary/tile from the dashboard; its scribble goes stale when the dashboard interaction model changes even
   though its own requirement is unchanged.
4. **`feat_collection_insights`** — derived stats (counts, distribution) surfaced as a dashboard card and a
   detail view. **P-F dependent #2** — depends on the dashboard surface contract.
5. **`feat_measurement_instrumentation`** — the cross-cutting requirement that the fixture + the workflow run
   against it **emit the six measurement probes** (§4). The fixture is an *instrumented* app, not just an app.

Why this is the minimal structural set:
- **P-F needs a hub + 2–3 dependents** → dashboard (hub) + Library + Insights (dependents) + the quick-add
  entry point. That is the minimum that makes the cascade *cross-feature* rather than intra-feature.
- **P-E needs one edit-designated requirement on an approved scribble** → the rating-scale AC in the form.
- **T4 needs one genuinely hard data-bound form** → the rating form.
- Drop any of the four product features and one coupling stops firing. So 4 product features + instrumentation
  is the floor, not a comfortable middle.

**Subset property (whole↔slice):** every now-slice feature is a feature the *general* playground would host
anyway. Growing the playground = adding more features around the same dashboard (search, recommendations,
import/export, multi-list, social-free sharing-by-file…), more personas, a richer design system — never
rewriting the five built now. The epic's `## Features` index lists the now-slice as built and names the
growth features as not-yet.

## 3. Engineering the couplings on purpose

**P-F (cross-feature cascade).** Specify the dashboard as a *shared entry surface with a published
composition contract*: dependent features (Library, Insights, quick-add) register a card/entry on it. The
scripted change is to the **dashboard's interaction model** (e.g. cards become tap-to-expand / reorderable),
which moves the outward surface the dependents render into — firing the lazy-wavefront cascade into 2–3
dependent scribbles whose *own* requirements never changed. The instrumentation's **cascade log** records
dependents-touched-per-hop so the L5 width-breaker threshold **N** can be *measured*, not guessed (redesign
Q5).

**P-E (mid-release staleness).** Designate the **rating-scale AC** of `feat_rating_entry_form` as the
*scripted mid-release edit*: after its scribble is approved, the requirement is edited (rating granularity
changes), which staleness-invalidates the approved scribble via SCI. The **stall report** records which
coding tasks block and their design-units, so the E1 stall fraction + cross-unit leak are measurable.

**T4 (domain→design ordering).** The rating form is data-bound to a Rating value-object that carries its own
(non-Presentation) validation ACs. This is exactly the case where the floor (a precise **data-point table in
the requirement**) is tested, and — because the rating/tag normalisation has genuine discovery risk — the
conditional domain-before-scribble edge can be observed too.

## 4. The six measurement probes (mandatory output — `12` §Fixture instrumentation)

The now-slice instrumentation feature requires that running the workflow on the fixture emits:

| # | Probe | Emitted by |
|---|---|---|
| 1 | **stall report** — blocked coding tasks + each task's design-unit, on the scripted mid-release edit | SCI audit / release-finalize-impl |
| 2 | **cascade log** — per origin: dependents touched per hop, visited-set, per-refresh "did outward surface move?" | lazy-wavefront detector |
| 3 | **salvage diff** — quarantine→re-derive diff persisted per re-derived task | release-derive-code |
| 4 | **fixture↔release behaviour log** — which cascade/staleness behaviours were/weren't seen on the fixture vs 0.0.1 | STEP-D reconcile |
| 5 | **facet-tag audit** — auto-tag vs human-confirmed tag per AC | requ-explore / decomposition |
| 6 | **graph-stats dump** — per-unit coding-task count, entry-graph hub in-degree, `both`-tag share | computed from design-unit map + entry-reference graph |

These make the redesign's empirical questions answerable *by construction*.

## 5. Web target & tech-agnosticism (what choosing React/Angular forces now)

- The scribble→code hand-off contract must split **design-intent (tech-neutral)** from **target-binding
  (web component framework)**. The web fixture is the forcing function that prevents the contract staying
  Flutter-shaped. → captured as an epic Cross-Feature Invariant + a now-slice constraint on the handoff.
- The factory/project **boundary labelling** (which skills are factory vs project) becomes a deliverable as
  skills are exercised on a *second* consumer — coordinate with TASK-PROC-066-01, don't duplicate.
- **In scope now (this task):** the *requirements* — that the handoff be tech-agnostic, that web gates/`doc/`
  surface must exist. **Deferred to TASK-PROC-066-04** (already created, `after` this task): actually standing
  up the React/Angular toolchain, web `doc/` guidelines, and web quality gates.
- **Framework recommendation: React** (largest model-training corpus → cheapest codegen per loop, which is
  the fixture's whole point; lighter scaffold than Angular for a tiny offline app). Final pick is confirmed in
  TASK-PROC-066-04 — this is a recommendation, not a lock.

## 6. Where do the playground's product requirements live? (Seed 7 — a developer decision)

Co-located under `process/AI_rules/factory_extraction/epic_skill_test_playground/` for now (developer
decision). Trade-off, surfaced for the developer:
- The playground is a **product**, but a *fixture* product — not the mood-tracker. Putting its
  personas/scenarios/flows into the real `requirements_user_needs/` tree would **pollute** the mood-tracker's
  user-needs with fixture artifacts.
- Therefore the playground's personas/flows are **described inside the epic** for now, not minted as real
  PERSONA-*/FLOW-* artifacts in the product tree. Formalising them (own user-needs sub-tree under the epic,
  or a dedicated playground tree) is a developer decision that interacts with the factory/project boundary
  TASK-PROC-066-01 will draw. Flagged as deferred + a framed question.

## 7. "All skills in mind" — per-skill epic hooks (so the whole factory can run on it eventually)

Authored as epic-level hooks (NOT pulled into the now-slice):

| Skill family | Hook the playground provides |
|---|---|
| ux-write-persona / -scenario | Archivist & Quick-Logger personas; scenarios on the entry form & dashboard |
| ux-create-flow / requ-derive-from-flow | add-rating flow, browse flow, review-insights flow — all sharing the dashboard |
| requ-explore / task-derive-from-requ | the epic + features themselves; data-point tables |
| ui-scribble-iterate / -auto-review / -approve-handoff | every screen scribbled; the tech-agnostic handoff |
| ui-verify-flutter (→ web analogue) | verify implemented web screens vs approved scribble (forces a web verifier) |
| code-simple / -complex / -test | domain value objects, data layer, web components, tests |
| verify-quality (→ web gates) | web lint/test/build gates (stood up by 066-04) |
| release-* (begin-impl / derive-code / finalize) | a real two-wave release decomposition over the fixture |
| doc-* | a web `doc/` surface (stood up by 066-04) |
| product-intake / vcd-log-tradeoff | the Archivist↔Quick-Logger value conflict |

Growth features (deferred): search, recommendations-from-own-data, import/export, multi-collection, themes.

## 8. Honest residual uncertainty (AC4)

- **Fixture fidelity** (the redesign's own biggest risk): a minimal fixture may under-represent the real 0.0.1
  cascade and give false confidence. Mitigation baked in: model the dashboard→feature dependency on the actual
  0.0.1 dashboard shape; the probe #4 behaviour-log surfaces what the fixture missed at STEP D.
- **Playground user-needs home** (Seed 7) — unresolved; described-in-epic for now, framed for the developer.
- **React vs Angular** — recommended React; final lock in 066-04.
- **Whether the data-point-table floor suffices or the form needs domain-code-first** — the form is built to
  test exactly this; unresolved until run.
- **Package assignment**: the playground is internal factory test-tooling, carries **no `target_package`**
  (release 0.0.1 packages are the mood-tracker's); its tasks go on `task_ordering_priority_override.txt`.

## 9. Decisions framed for the developer (AC3 / AC5)

1. **Approve the product shape** — personal offline media-rating app as the general playground vehicle?
2. **Approve the now-slice = 5 features** (dashboard + rating-form + library + insights + instrumentation) as
   the minimal coupling-complete subset?
3. **Playground user-needs home** (Seed 7): described-in-epic now, or mint a dedicated playground user-needs
   sub-tree (and when)?
4. **Framework**: confirm React (vs Angular) — or defer the lock entirely to 066-04?
5. **Next step**: after approval, what to run — `task-derive-from-requ` on the now-slice features to create the
   build tasks (appended to the ordering override), or hold?
