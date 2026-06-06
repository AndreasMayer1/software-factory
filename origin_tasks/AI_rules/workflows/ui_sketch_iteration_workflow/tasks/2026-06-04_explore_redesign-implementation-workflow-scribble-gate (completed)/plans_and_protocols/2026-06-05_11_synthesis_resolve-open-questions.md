# Synthesis iteration 3 — resolving the open questions

Task: TASK-PROC-032-29. Date: 2026-06-05.
Purpose (developer ask): *iterate again — fill open gaps, make recommendations for open questions (pros and
cons), answer as many as possible.* This document walks every open item left by `04`–`10` (and the carried
Round-1 §9/§10 + eval-substrate items) and does one of three things to each: **ANSWERED** (resolved by
inspection or reasoning), **RECOMMENDED** (a call with pros/cons the developer can ratify), or **EMPIRICAL**
(genuinely cannot be settled without a run — stated with its measurement plan). Decisions already made
(Q1 fixture-first, Q2 web, D-2 per-design-unit, D-3 names) are not re-opened.

Scoreboard: of ~18 open items, **6 ANSWERED**, **8 RECOMMENDED**, **4 EMPIRICAL (with a measurement plan)**.

---

## A. Resolved by inspection (new facts, 2026-06-05)

### A1 — 0.0.1 migration is the cheap case, and there is NO holistic plan to reclassify  → **ANSWERED**
Inspection findings (grounded):
- `releases/0.0.1/` holds only `size_analysis/`; **no** activated release manifest, **no** active-release
  marker, **no** live autorun orchestration chain. `RELEASE_BACKLOG.md` lists every 0.0.1 package as
  `status: versioned` (planned, not activated).
- **No `target_package` tags and no holistic/orchestration plan artifact exist.** The 0.0.1 tasks were created
  **organically** by earlier `create-impl-tasks-release-0.0.1` explore tasks (Feb–May 2026,
  `release_preparation/tasks/…`), *not* by a current two-wave `release-begin-impl`. So the premise behind T1
  ("reclassify the existing plan") is itself wrong — **there is no single plan to reclassify.**
- The **bulk of REQ-FUNC-007 is already `completed`** (dozens of impl tasks — working, shipped code). That is
  the brownfield / retro-scribble situation (F10), **not** "blind coding tasks to invalidate." Completed
  working features are never deleted by a migration; if their requirement later changes they enter the normal
  SCI/staleness path.
- The genuinely-affected set is **small and mostly `pending`**: the pre-scribble UI tasks
  `TASK-FUNC-007-12-01..04` (`feat_qr_data_transfer`: client-qr screen, therapist-qr-receive screen, qr
  navigation, foundation) + a few `feat_adaptive_transfer_settings` tasks. The only `in_progress` Presentation
  work is **`TASK-FUNC-007-01-05`** (the pilot — *already* slated for clean re-run by `01_clean-rerun-decision`)
  and **`TASK-FUNC-014-06-01`** (plan-export QR screen — a *different* requirement, REQ-FUNC-014-06).

**Consequence — the migration is even cheaper than `05`/`10` assumed, and "delete-all" is plainly absurd:**
1. The T1 "live-chain mid-flight reconcile" residual **does not apply** (nothing is running).
2. There is **nothing to reclassify** — migration is a **task-set reconcile**, not a plan reclassify:
   run the flow→scribble coverage report (PROP-9) over the 0.0.1 Presentation requirements → it lists the
   missing scribbles; give the ~6–8 affected pre-scribble Presentation tasks (mostly `pending`) a per-task SCI
   verdict (block on a new scribble task); leave all `completed` work and all pure-domain work untouched.
3. The two `in_progress` items already have homes: `007-01-05` → clean re-run (existing decision);
   `014-06-01` → one individual SCI verdict (its own requirement, outside the data-transfer epic).
- **Residual now closed:** the "confirm a derivable plan exists" residual is resolved — *it doesn't*, and that
  makes the answer simpler, not harder. No "fresh Wave-1 decomposition for 0.0.1" is needed either, because the
  non-pilot 0.0.1 work is already implemented; only the handful of un-started pre-scribble UI tasks need the
  SCI-block treatment.

---

## B. Decisions now recommended (pros / cons → a call to ratify)

### B1 — D-0: the `ui-create-scribble` routing bug  → **ANSWERED (no decision, just sequencing)**
`create_orchestration_task.py` L276 routes `task_type: scribble` to a non-existent skill string. Fix it as the
**very first concrete change in STEP C**, before any scribble task can run. Map `scribble → ui-scribble-iterate`.
No trade-off; it is a prerequisite. (Folds into the B8 registry-routing-contract check so it can't recur.)

### B2 — D-1: make the bisection a hard requirement?  → **RECOMMENDED: yes**
"Begin Implementation decomposes only scribble + pure-domain tasks; Presentation coding tasks are decomposed
only post-approval by `release-derive-code`."
- **Pro:** it is the structural spine; SCI, the gate, and the two-wave model all hang off it. Ambiguity here
  re-admits the exact defect (coding decomposed blind) the redesign exists to remove.
- **Con:** none material — it is the developer's stated intent. The only nuance is the per-design-unit escape
  (pure-domain units get code in Wave 1), which is already in D-2.
- **Recommendation:** ratify as a hard AC in REQ-PROC-035, with the per-design-unit escape written in.

### B3 — Q3 / T4: where does the data-point definition live?  → **RECOMMENDED: requirement (default), code-first only for discovery-heavy domains**
- **Requirement-home (recommended).** *Pro:* preserves the RE-DERIVE separation (the scribble derives from the
  requirement, not from `lib/`); the scribble keeps a single upstream source; no new staleness coupling. *Con:*
  forces `requ-explore` to author a precise data-point table (name/type/format/validation/optional/enum) up
  front; mild duplication with the eventual value-object.
- **Code-first.** *Pro:* surfaces constraints only discovered at implementation. *Con:* adds a domain-code →
  scribble staleness edge (see B9), serialises, erodes RE-DERIVE.
- **Recommendation:** requirement-home as the floor (always); code-first as an explicit **per-design-unit
  exception** flagged at `requ-explore` time when the data model is genuinely undecidable pre-implementation.
  When code-first is used, the domain-code→scribble edge of B9 is activated for that unit.

### B4 — Q4 / T5: scope of the skill-design trade-off record  → **RECOMMENDED: fused-responsibility skills only, with an objective trigger**
- **Trigger rule (makes "fused" objective):** a skill needs the full trade-off record iff it has **>1
  artifact-in→artifact-out pair** OR carries a **mode flag** (`--scope`-style). Single-responsibility skills
  carry only the one-sentence responsibility.
- **Pro:** no boilerplate on simple skills; attention focuses on the genuine drift-risk seams (in this whole
  redesign, essentially just `task-derive-from-requ --scope`). *Con:* needs the artifact registry to express
  in/out pairs (B8) for the trigger to be checkable.
- **Recommendation:** adopt fused-only with the objective trigger; AC in REQ-PROC-035/058.

### B5 — D-4: SCI reader table; does `ui-verify-flutter` hard-block on a stale scribble?  → **RECOMMENDED: hard-block, with an explicit advisory override**
The generative-blocks / referential-flags discriminator (Round-1 §4.1) stands. The only contested row is
`ui-verify-flutter` / `ui-visual-validate`.
- **Hard-block (recommended).** *Pro:* it generates a pass/fail *verdict against the scribble* — a stale
  scribble makes that verdict meaningless or misleading. *Con:* you lose the ability to catch gross impl
  regressions during the staleness window.
- **Advisory-flag.** *Pro:* still runs a sanity check. *Con:* risks acting on a verdict against the wrong
  target.
- **Recommendation:** **hard-block by default** (it is a generative reader), but expose an explicit
  `--verify-against-stale` advisory override that runs and labels the verdict "advisory: target stale." Best of
  both: safe default, escape hatch when a human wants a gross-regression sanity check.

### B6 — Q5 / T3: the L5 cascade width-breaker value N  → **RECOMMENDED mechanism + starting value; EMPIRICAL final value**
- **Mechanism (ANSWERED):** two-stage breaker. *Soft* — at N1 cumulative dependents, log + annotate the gate
  ("wide cascade in progress"). *Hard* — at N2, stop auto-creating refresh tasks and escalate to the developer
  via `pending_feedback` with the dependency sub-graph walked so far (honouring PROP-10 "bounded recovery;
  never unbounded auto-create").
- **Starting values:** N1 = 3, N2 = 7 (7 echoes the doc-lookup M-band feel; both configurable). The *value* is
  EMPIRICAL — measured on the fixture cascade (TASK-PROC-066-03 Seed 3 is built to produce one).
- **Recommendation:** ship the two-stage breaker with N1=3/N2=7 as defaults; tune after the first fixture
  cascade.

### B7 — D-5: PROP-14 Markdown→HTML technology  → **RECOMMENDED: client-side vendored renderer (pinned), REQ-PROC-060 authorization still required**
- **Client-side vendored (recommended).** A single pinned static JS lib (e.g. a `marked.min.js`-class
  renderer) in the scribble artifact. *Pro:* keeps the scribble self-contained and zero-build; matches the
  hard constraint "a script *copies* the flow files in, the LLM does not re-emit them"; aligns with the
  web/static-HTML direction the fixture decision (Q2) just set. *Con:* ships one JS dependency inside the
  artifact; needs REQ-PROC-060 admission for that one pinned file.
- **Build-step.** *Pro:* no shipped JS dep. *Con:* adds a build step to scribble generation; the rendered flow
  is baked (less live), and a build step is exactly what the self-contained-artifact goal avoids.
- **Recommendation:** client-side vendored, pinned, single file — still a developer-authorized REQ-PROC-060
  call (cannot self-add), so it stays a developer decision but with a clear recommendation.

### B8 — D-6: accept the S1→S4 staging?  → **RECOMMENDED: yes, with the T3/T4/T5 ACs folded in as already mapped**
S1 (REQ-PROC-035/058 spine) → S2 (REQ-PROC-032 consistency) → S3 (generator carrier-format, parallel) → S4
(PROP-14, last). *Pro:* dependency-correct (S2's SCI edges need S1's two-wave model). *Con:* none surfaced.
- **Recommendation:** ratify. Fold: B2/B4 → S1; B3/B5/B6/B9 + L3 coverage-assertion → S2; comment-leak →
  S3; B7 → S4.

---

## C. Uncertainties now answered or bounded by reasoning

### C1 — The complete SCI rot-graph edge set  → **ANSWERED**
The "SCI rot-graph completeness" worry (`10` §5) is closed by enumerating every staleness edge and its
detector. There are **five**:
| # | Edge (upstream → dependent) | Trigger | Detector |
|---|------------------------------|---------|----------|
| 1 | requirement → scribble | requirement LOCKED-IN edit (P-E) | `stale_since` set by `requ-explore`/`task-derive-from-requ` (PROP-12) |
| 2 | scribble → coding task | scribble re-approved / superseded | SCI audit (`§4.2`); `check_scribble_currency.py` |
| 3 | domain-code → data-bound scribble | domain value-object edit, *only* for code-first units (B3) | extend SCI audit with a domain-commit comparison (new, conditional) |
| 4 | scribble → dependent scribble | outward entry surface changed on approval (P-F) | lazy-wavefront detector + visited-set + width breaker (B6) |
| 5 | scribble → `ui-verify-flutter` verdict | scribble stale at verify time | hard-block reader (B5) |
Edges 1/2/4/5 were in Round-1; **edge 3 is new** (introduced by T4) and is the one previously unmodelled. With
it enumerated, the rot-graph is closed for the current design.

### C2 — `--scope presentation/code` clean separability  → **ANSWERED (mechanism), EMPIRICAL (tagging accuracy)**
The tie-break for ACs that are *both* Presentation and behaviour (Round-1 §10): give **every AC a facet tag
`{presentation | behaviour | both}`**, authored at `requ-explore` time.
- `presentation` → Wave 1 (locked by the scribble).
- `behaviour` → Wave 2 coding task.
- `both` → appears in **both** waves: the Presentation facet is locked by the scribble (Wave 1), the behaviour
  facet becomes a Wave-2 coding task `after` that scribble.
So separability reduces to "can we tag AC facets?" — yes, with a heuristic + human confirm. The L3
coverage-assertion (T3) keys off this exact tag: "every AC tagged `presentation` or `both` must have a
scribble/source-check." *Accuracy of the tagging* is EMPIRICAL (mis-tags over/under-serialise) but the
mechanism is settled.

### C3 — `flutter_handoff.yaml` sufficiency, under a web target  → **ANSWERED**
The Q2 web decision forces the handoff to split anyway, which *also* answers the sufficiency worry:
- **design-intent layer** (tech-neutral: layout, component roles, copy, states — the LOCKED-IN set) — Wave-2
  reads this **fully**; it is the distillation that realises "read twice rarely."
- **target-binding layer** (Flutter widgets *or* React/Angular components) — produced per consumer.
- **behaviour facet** (C2's `behaviour`/`both`-tagged ACs the scribble doesn't depict) — Wave-2 reads a
  **narrow** slice of these, *not* the whole raw requirement. The earlier "may be thin for cross-persona
  constraints" worry is bounded to exactly the facet-tagged behaviour ACs.
- **Verdict:** handoff is sufficient for the Presentation facet; Wave-2's only re-read is the bounded,
  facet-tagged behaviour ACs. The unbounded "re-read the raw requirement" fear is retired.

### C4 — The "data-bound" detector (T4)  → **ANSWERED**
Concrete rule: a scribble is **data-bound** iff its requirement's `presentation`/`both`-tagged ACs reference a
domain value-object/entity that itself has `behaviour`-tagged ACs in the same design-unit. Default action = a
**soft-pref** ordering edge (scribble after that domain task); hardened to a blocking `after` only for the
code-first exception units (B3). Human can override at the gate. Reuses the facet tags (C2) and the
design-unit map — no new metadata beyond the tag.

### C5 — Registry expressiveness for routing contracts (T5 / D-0)  → **RECOMMENDED extension**
For the artifact-registry encapsulation test (B4) to also catch D-0-class bugs, extend
`.factory/registry/artifacts.yaml` so a plan-entry `task_type` value is a **registered routing contract**:
every `task_type` must name a registered consumer skill. The encapsulation check then asserts
"every emitted `task_type` resolves to a registered skill" — which *is* the D-0 detector. *Pro:* one check
catches the whole class. *Con:* a small registry-schema extension is needed first. **Recommendation:** add it
in S1 (it is the contract that makes B1/B4 enforceable).

### C6 — Deep L3 source-gap chains (T3)  → **ANSWERED**
Even with each step depth-1, an A→B→C→… chain of source-gaps is theoretically unbounded. Add a **soft alert at
chain length > 3** (log + surface, do not block) so a degenerate requirement graph is visible. Rare in
practice; the alert is cheap insurance, not a hard bound.

---

## D. What genuinely remains EMPIRICAL (with its measurement plan)

These cannot be settled by reasoning; each has a concrete way to be measured — and the fixture
(TASK-PROC-066-03) is being built precisely to measure most of them.

| Item | Why empirical | Measurement plan |
|------|---------------|------------------|
| **Liveness/throughput under SCI** | depends on real cross-unit edit fan-out | per-design-unit (D-2) + facet split (C2) bound the stall to the affected unit; measure stall width on the first real mid-release edit (fixture P-E scenario) |
| **Cascade width / breaker N value** (B6) | depends on real shared-surface topology | fixture Seed 3 produces a dashboard cascade on purpose → observe wavefront width → set N1/N2 |
| **Presentation-code salvage rate** (T1) | depends on how much scribbles restructure screens | run the quarantine→re-derive→diff on the ≤2 started 0.0.1 tasks; safe regardless (no valid work destroyed) |
| **Fixture fidelity to the real P-F** (T2) | a minimal fixture may under-represent the real cascade | model the fixture's dashboard→feature dependency on the *actual* 0.0.1 dashboard case (fixture Seed 3) — minimal but representative; STEP D still backstops anything missed |
| **AC facet-tagging accuracy** (C2) | heuristic over AC prose | measure mis-tag rate on the fixture's ACs; human-confirm at the gate until trusted |

Note these are now **narrower** than in `10` §5: liveness is bounded to a unit, handoff sufficiency (C3) and
the rot-graph (C1) are no longer open, and the 0.0.1 live-chain risk (A1) is gone.

---

## E. Updated decision ledger — what is actually left for the developer

Everything below is a **ratify-or-adjust**, not an open design problem:

1. **Ratify the recommendations** B2 (bisection hard), B3 (requirement-home + code-first exception), B4
   (fused-only trade-off record), B5 (verify hard-block + override), B6 (two-stage breaker N1=3/N2=7), B7
   (client-side vendored MD renderer — the one true REQ-PROC-060 authorization still required), B8 (S1→S4
   staging), C5 (registry routing-contract extension).
2. **0.0.1 migration scope is now settled by inspection (A1)** — no confirmation needed. It is a small
   **task-set reconcile**: coverage-report the missing 0.0.1 scribbles, SCI-block the ~6–8 un-started
   pre-scribble UI tasks (notably `TASK-FUNC-007-12-01..04`), give `TASK-FUNC-014-06-01` one verdict, and let
   the pilot (`007-01-05`) follow its existing clean-re-run decision. All `completed` and pure-domain work is
   untouched. The only thing to *accept* is that this reconcile runs at STEP D (after the workflow is validated
   on the fixture), not now.
3. **Accept** that five items (D) stay empirical and will be measured on the fixture — i.e. the plan does not
   stall waiting for them; it measures them in flight.

If all of E1 are ratified, **STEP A (the `requ-explore` requirements authoring) has no unresolved design
inputs left** — it can author REQ-PROC-035/058 (S1) and REQ-PROC-032 (S2) directly from this document.

## F. Acceptance-criteria status (this task's goal.md) — unchanged from `10`
- [x] synthesis round produced (this is the third)
- [x] problem space defined in new terms (facet tags; the five-edge SCI rot-graph; the two-stage width breaker)
- [x] decisions framed to decide (§E)
- [x] honest about what remains uncertain (§D — now narrowed)
- [x] user approved + stated next step (Q1/Q2 decided 2026-06-05; STEP A is next)
- [ ] next step performed — STEP A not yet kicked off (awaiting ratification of §E)
