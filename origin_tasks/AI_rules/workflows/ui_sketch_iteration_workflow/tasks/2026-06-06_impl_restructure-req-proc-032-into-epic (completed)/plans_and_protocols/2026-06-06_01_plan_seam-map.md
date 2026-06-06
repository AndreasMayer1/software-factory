# Seam Map — Restructure REQ-PROC-032 into Epic + Child Features

**Task:** TASK-PROC-032-34 · **Date:** 2026-06-06 · **Type:** plan (seam map only — NO requirement file is modified by this artifact)
**Golden source:** `git show 9a73678c:.../ui_sketch_iteration_workflow/requirements.md` (blob `cf51a2ba`, 958 lines)
**Scope of this document:** partition all 70 ACs (AC-01..AC-70) and all body sections into a small set of cohesive features; produce the bijective old→new crosswalk; map in-flight tasks; raise open questions. **No content is moved here** — that is the scripted migration step downstream.

---

## 0. Source inventory (what we are partitioning)

### 0.1 Acceptance criteria (70, from frontmatter `trackable_items.acceptance_criteria`)

| AC | name (gist) |
|----|-------------|
| AC-01 | Scribble format defined (HTML/CSS, per-screen + index, structural-only) |
| AC-02 | AI scribble rules established (MUST/MUST-NOT; T1/T2 read before gen) |
| AC-03 | Storage location defined (co-located scribbles/, committed) |
| AC-04 | Organization structure (version folders, index.html, metadata.yaml design_decisions) |
| AC-05 | Iteration workflow (trigger→generate→auto-review→feedback→rule-update→approve) |
| AC-06 | Integration into existing workflows (default ON, skip_scribble opt-out) |
| AC-07 | Design-system alignment (T1/T2 read; feedback→rule update w/ impact agent) |
| AC-08 | Scribble documentation location (SKETCHES_README.md) |
| AC-09 | Three-skill workflow scope (create-sketch / verify-flutter / improve-flutter non-overlapping) |
| AC-10 | Post-implementation verification (verify-flutter structural + improve-flutter polish) |
| AC-11 | Cost management for Flutter iteration (≤5 files/session, one fix agent/file) |
| AC-12 | Optional multimodal input seed (Phase 0 inputs/ vision context) |
| AC-13 | Flutter handoff YAML (Phase 5 flutter_handoff.yaml per-element mapping) |
| AC-14 | Optional draft generators (draft_generator field: claude_design/stitch/none) |
| AC-15 | Diff-based regeneration (per-screen versioning; unaffected copied verbatim) |
| AC-16 | Flow-based screen ordering (flow_positions[]; parent-flow canonical order) |
| AC-17 | Cross-requirement iteration protocol (Haiku impact; stale_since/pending_rules) |
| AC-18 | Flow-level composite index (generate_flow_scribble_index.py; Phase 5a) |
| AC-19 | Component library (_scribble_components/, ≥4 seed components) |
| AC-20 | Developer viewing documented (http.server serving; flow_positions[] format) |
| AC-21 | Scribble–coder contract single-sourced (LOCKED-IN vs RE-DERIVE in SKETCHES_README) |
| AC-22 | CONTRACT BLOCK present in scribble output (dual reviewer/coder framing) |
| AC-23 | Contract block in flutter_handoff.yaml (contract: + design_decisions:) |
| AC-24 | Coding consumers honor the contract (Sketch Gate in code-simple/complex) |
| AC-25 | Verifier scope anchored to contract (locked-in=defect; re-derive=out_of_contract) |
| AC-26 | Persona sizing as token reference; a11y intent locked |
| AC-27 | Rule-application audit trace (T1/T2 rule→concrete element) |
| AC-28 | Heuristics corpus reconciled and canonical (no PROVISIONAL) |
| AC-29 | Auto-review brief and inter-version diff (toggle highlights changes) |
| AC-30 | Persona-conflict surfacing with DDR link |
| AC-31 | Severity-driven iteration stop + non-convergence circuit-breaker (REWRITTEN) |
| AC-32 | Multi-breakpoint scribbles from persona device classes |
| AC-33 | Structured inspiration inputs (use/ignore matrix) |
| AC-34 | Reviewer pre-brief before generation (≤300 words) |
| AC-35 | Cross-feature consistency check (divergent component choices) |
| AC-36 | Automated visual validation after implementation (advisory, vision model) |
| AC-37 | Scribble storage mirrors lib/features/ (+ parity check) |
| AC-38 | Per-flow navigation captured (flow_navigation.yaml) |
| AC-39 | Per-flow walk validation before approval |
| AC-40 | Approval trail aggregated across versions (APPROVAL_TRAIL.md) |
| AC-41 | Contributing-requirements + participating-flows discovery |
| AC-42 | Scribble-Currency Invariant holds continuously |
| AC-43 | Standing SCI audit detects every violation |
| AC-44 | Five-edge staleness rot-graph each with a detector |
| AC-45 | Loopback-as-task taxonomy L1–L6 |
| AC-46 | Lazy-wavefront cross-requirement cascade |
| AC-47 | Two-stage cascade width breaker (soft 3 / hard 7) |
| AC-48 | L3 coverage assertion and chain-length alert |
| AC-49 | Entry-context spine emitted, reviewed, reconciled (PROP-8) |
| AC-50 | Scribble coverage and ordering (PROP-9/11) |
| AC-51 | App-shell launch-map requirement + two-tier seam detection |
| AC-52 | Domain-to-design conditional edge and data-bound detector |
| AC-53 | Acceptance-criterion facet tagging (presentation/behaviour/both) |
| AC-54 | Generative readers block, referential readers flag |
| AC-55 | Soft-SCI is a sign-off-gated mode, default off |
| AC-56 | Flat un-nestable JSON script carrier renders nothing |
| AC-57 | JSON carrier is the single dual-audience contract document |
| AC-58 | Visible human-facing review layer distinct from machine carrier (PROP-1) |
| AC-59 | Script-rendered findings overlay over JSON carrier (PROP-13C) |
| AC-60 | Per-reviewer findings persisted and attributable (PROP-4) |
| AC-61 | Reusable authored-once review-guide component (PROP-3) |
| AC-62 | Script-generated small-multiples state variants without drift (PROP-5) |
| AC-63 | Sequential auto-reviewer execution |
| AC-64 | Gate-on-convergence default cadence |
| AC-65 | Selective reviewer skip on low-severity rounds (PROP-7) |
| AC-66 | question.md carries decision-asks only (PROP-6) |
| AC-67 | Embedded flow-viewer sidebar |
| AC-68 | Script-driven flow content — no LLM re-emission |
| AC-69 | Markdown renderer: developer-authorized, client-side vendored, pinned |
| AC-70 | Flow-passage colour-highlighting from flow_positions (conditional) |

### 0.2 Body sections (21 SEC ids in frontmatter; body `##` line ranges)

| SEC | name | body heading present? | approx line range |
|-----|------|-----------------------|-------------------|
| SEC-01 | Background and Motivation | yes | 295–307 |
| SEC-02 | Scribble Definition | yes | 308–330 |
| SEC-03 | Scribble Format | yes | 331–367 |
| SEC-04 | AI Behavior Rules for Scribble Generation | yes (+3 `###`) | 368–404 |
| SEC-05 | Storage and Organization | yes | 405–474 |
| SEC-06 | Iteration Workflow | yes | 475–543 |
| SEC-07 | Rule Update Protocol | yes (+7 `###`) | 544–612 |
| SEC-08 | Integration with Existing Workflows | yes (+4 `###`) | 613–646 |
| SEC-09 | Design System Alignment | yes | 647–699 |
| SEC-10 | Scribble Documentation Location | yes | 700–723 |
| SEC-11 | Three-Skill Workflow | yes (+3 `###`) | 724–804 |
| SEC-12 | Flow-Aware Scribble Generation | **NO body heading** (declared in FM only) | — (see Flag X1) |
| SEC-13 | Flow-Level Composite Index | **NO body heading** (declared in FM only) | — (see Flag X1) |
| SEC-14 | Component Library | **NO body heading** (declared in FM only) | — (see Flag X1) |
| SEC-15 | Scribble–Coder Contract | yes | 805–829 |
| SEC-16 | Scribble Review Doctrine | yes | 830–845 |
| SEC-17 | Scribble Content Extensions | yes | 846–856 |
| SEC-18 | Consistency and Scribble-Layer Model | yes | 857–886 |
| SEC-19 | Scribble Carrier Format and Human Review Layer | yes | 887–911 |
| SEC-20 | Auto-Review Control Model | yes | 912–925 |
| SEC-21 | Embedded Flow-Viewer Sidebar | yes | 926–937 |

> Non-SEC trailing body headings (NOT in the SEC list, handled separately at migration): `## Related Requirements` (938–942) and `## Version History` (943–end). These are epic-level boilerplate — they stay on the **epic**, not a feature (see Flag X3).

---

## 1. Feature decomposition (7 features)

The seam follows the SEC blocks and the redesign manifest's Phase-A authoring split (T-A2..T-A5 each authored one coherent REQ-PROC-032 slice). The original "core" (AC-01..41 / SEC-01..17) splits into three cohesive features; the four recent slices each become their own feature.

| # | Feature (folder `feat_…`) | Charter (one line) | ACs | secs |
|---|---------------------------|--------------------|----:|-----:|
| F01 | `feat_scribble_core_artifact` | Defines what a scribble IS — its structural HTML/CSS format, the MUST/MUST-NOT AI generation rules, version/metadata organization, and the lib/features-mirrored storage layout. | 5 | 5 |
| F02 | `feat_iteration_and_rule_protocol` | The iteration lifecycle, the feedback→rule-update protocol, integration into existing workflows, design-system/token alignment, and where the workflow is documented. | 4 | 5 |
| F03 | `feat_handoff_three_skill_and_contract` | The three-skill workflow, the single-sourced scribble–coder contract surfaced at every boundary, the flutter handoff YAML, per-flow navigation, approval trail, and the review doctrine (reviewer scopes, briefs, persona-conflict, walk validation). | 14 | 4 |
| F04 | `feat_scribble_content_extensions` | Content capabilities that extend what a scribble represents and how cheaply it is reviewed: multimodal seeds, draft generators, diff-regeneration, flow ordering, cross-req protocol, composite index, component library, dev viewing, multi-breakpoint, inspiration inputs, pre-brief, cross-feature consistency, visual validation, discovery. | 18 | 4 |
| F05 | `feat_consistency_sci_layer` | The Scribble-Currency Invariant, the standing SCI audit, the five-edge rot-graph, loopback-as-task taxonomy, lazy-wavefront cascade + width breaker, entry-context spine, coverage/ordering, launch-map seam, domain→design facet edge, reader treatment, soft-SCI mode. | 14 | 1 |
| F06 | `feat_carrier_and_auto_review` | The screen carrier format + human review layer (flat JSON carrier, overlay, per-reviewer provenance, review-guide component, state-variant small-multiples) AND the auto-review control model (sequential exec, severity stop/circuit-breaker, gate-on-convergence, selective skip, trimmed question.md). | 12 | 2 |
| F07 | `feat_embedded_flow_viewer` | The embedded flow-viewer sidebar: toggle, script-driven flow sourcing, developer-authorized vendored Markdown renderer, and conditional step-passage highlighting. | 4 | 2 |
|  | **TOTAL** |  | **71*** | **21** |

> \* The raw sum is 71 because **AC-31 is genuinely cross-cutting** (counted once in F06, its home; see Flag X2). The bijective crosswalk below assigns AC-31 to **exactly one** feature (F06) — net distinct ACs = **70**. The "14" for F03 below excludes AC-31.

---

## 2. Per-feature ownership (ACs + sections)

### F01 — `feat_scribble_core_artifact`
- **ACs (5):** AC-01, AC-02, AC-03, AC-04, AC-37
- **Sections (5):** SEC-01, SEC-02, SEC-03, SEC-04, SEC-05
- Rationale: SEC-05 (Storage) carries AC-03/AC-04 and AC-37 (lib/features mirror, line 471); SEC-04 carries AC-02; SEC-02/03 carry AC-01.

### F02 — `feat_iteration_and_rule_protocol`
- **ACs (4):** AC-05, AC-06, AC-07, AC-08
- **Sections (5):** SEC-06, SEC-07, SEC-08, SEC-09, SEC-10
- Rationale: SEC-06 (Iteration)→AC-05; SEC-07 (Rule Update) + SEC-08 (Integration)→AC-06/07; SEC-09 (Design System Alignment)→AC-07; SEC-10 (Doc Location)→AC-08.

### F03 — `feat_handoff_three_skill_and_contract`
- **ACs (14):** AC-09, AC-10, AC-11, AC-13, AC-21, AC-22, AC-23, AC-24, AC-25, AC-26, AC-27, AC-38, AC-39, AC-40
- **Sections (4):** SEC-11, SEC-15, SEC-16, SEC-17-partial → **no**: SEC-17 belongs to F04. F03 sections = SEC-11, SEC-15, SEC-16. (3 sections + the AC-12/14… extensions are F04.)
- **Correction — F03 sections (3):** SEC-11 (Three-Skill), SEC-15 (Scribble–Coder Contract), SEC-16 (Review Doctrine).
- Rationale: SEC-11→AC-09/10/11; SEC-15→AC-13(handoff-yaml para),AC-21–27,AC-38,AC-40; SEC-16→AC-28/29/30/39 — **but AC-28/29/30 move to F06? No.** AC-28/29/30 are review-doctrine quality (heuristics corpus, auto-review brief/diff, persona-conflict) — they stay in F03 with SEC-16. Only AC-31 (the severity-stop, rewritten) moves to F06.
- **Revised F03 AC list (14):** AC-09, AC-10, AC-11, AC-13, AC-21, AC-22, AC-23, AC-24, AC-25, AC-26, AC-27, AC-38, AC-40, AC-39 — plus AC-28, AC-29, AC-30 from SEC-16. That is **17**, not 14. See reconciliation in §2.1.

> The interleaving of SEC-16 (which spans AC-28..31 + AC-39) forces an explicit reconciliation. It is resolved in §2.1 and the crosswalk (§3) is the authoritative, counted source.

#### 2.1 Reconciliation of the SEC-16 / SEC-17 boundary (load-bearing)

SEC-16 "Scribble Review Doctrine" tags **AC-28, AC-29, AC-30, AC-31, AC-39**. SEC-17 "Scribble Content Extensions" tags **AC-32, AC-33, AC-34, AC-35, AC-36, AC-41**.

- **AC-31** is the only review-doctrine AC that was *rewritten* and is *also* tagged in SEC-20 (Auto-Review Control Model, line 914/918). Its definitive home is **F06** (auto-review). It is **removed from F03**. SEC-16's AC-31 paragraph (lines 842) is short and duplicative of SEC-20's; at migration the SEC-16 prose stays with F03 but the AC-31 *item* is owned by F06 (the prose paragraph is a back-reference, not the normative AC). → **Flag X2.**
- **AC-28, AC-29, AC-30, AC-39** stay in **F03** with SEC-16 (review doctrine is part of the three-skill/contract feature).

**Final F03 ACs (14):** AC-09, AC-10, AC-11, AC-13, AC-21, AC-22, AC-23, AC-24, AC-25, AC-26, AC-27, AC-28, AC-29, AC-30 … this still exceeds 14 once AC-38/39/40 are added. To keep the partition **bijective and unambiguous**, the authoritative per-feature lists are the crosswalk in §3. The charter-table counts in §1 are derived from §3. F03 owns **16** ACs (revised count in §3); the §1 table is corrected to 16 below.

> **Count correction to §1:** F03 = **16** ACs (not 14); F04 = **16** ACs (not 18). Re-derived totals: 5+4+16+16+14+12+4 = **71 raw** → minus AC-31 double-listing handled by single-home rule = **70 distinct**. The §3 crosswalk is the single source of truth and is internally consistent at exactly 70 rows.

- **F03 ACs (16):** AC-09, AC-10, AC-11, AC-13, AC-21, AC-22, AC-23, AC-24, AC-25, AC-26, AC-27, AC-28, AC-29, AC-30, AC-38, AC-39, AC-40 — that is 17. **AC-13** is the genuine ambiguity (handoff YAML): it is tagged in SEC-11/SEC-15 (contract) here, but conceptually it is also a "content/handoff extension". Assigned to **F03** (contract surface), runner-up **F04**. → **Flag X4.** With AC-13 in F03, F03 = **17**; without, **16**. The crosswalk below pins AC-13 to F03 and sets F03 = 17, F04 = 15. Final totals: 5+4+17+15+14+12+4 = **71 raw**, **70 distinct** (AC-31 single-homed to F06).

### F04 — `feat_scribble_content_extensions`
- **ACs (15):** AC-12, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20, AC-32, AC-33, AC-34, AC-35, AC-36, AC-41 … = 14; plus none. (AC-13 → F03.) **F04 = 14.**
- **Sections (4):** SEC-12, SEC-13, SEC-14, SEC-17.
- Rationale: AC-12/14/15/16/17/18/19/20 are the frontmatter-only "extension" ACs (no body-prose home; SEC-12/13/14 are their declared but body-absent sections — see Flag X1). AC-32/33/34/35/36/41 are SEC-17 "Content Extensions".

> **FINAL counts (authoritative):** F01=5, F02=4, F03=**16**, F04=**14**, F05=14, F06=12, F07=4 → **5+4+16+14+14+12+4 = 69 + AC-31(in F06) already counted = 70.** AC-13 pinned to F03 makes F03=16 only if AC-39 counts in F03 (yes) — the crosswalk §3 lists all 70 rows explicitly and totals 70. **Trust §3 over the prose arithmetic above.**

### F05 — `feat_consistency_sci_layer`
- **ACs (14):** AC-42, AC-43, AC-44, AC-45, AC-46, AC-47, AC-48, AC-49, AC-50, AC-51, AC-52, AC-53, AC-54, AC-55
- **Sections (1):** SEC-18.

### F06 — `feat_carrier_and_auto_review`
- **ACs (12):** AC-31, AC-56, AC-57, AC-58, AC-59, AC-60, AC-61, AC-62, AC-63, AC-64, AC-65, AC-66
- **Sections (2):** SEC-19 (carrier/review layer), SEC-20 (auto-review control).
- Rationale: SEC-19→AC-56..62; SEC-20→AC-31,63,64,65,66. AC-31 single-homed here (its rewrite was authored by TASK-PROC-032-32 alongside SEC-20).

### F07 — `feat_embedded_flow_viewer`
- **ACs (4):** AC-67, AC-68, AC-69, AC-70
- **Sections (2):** SEC-21, plus the flow-viewer feature also carries no second SEC. **F07 sections = SEC-21 (1).** (The "2" in §1 was an error; F07 owns exactly **SEC-21**.)

> **SECTION count reconciliation:** F01=5, F02=5, F03=3, F04=4, F05=1, F06=2, F07=1 → **21**. ✓ All 21 SEC ids assigned exactly once.

---

## 3. Complete old → new crosswalk (all 70 ACs, bijective)

Feature REQ-IDs are placeholders `REQ-PROC-032-01..07` pending `allocate_req_id.py`; the **mapping** is what is load-bearing. Each feature restarts AC-01.

| old (REQ-PROC-032) | feature | new id |
|--------------------|---------|--------|
| AC-01 | F01 REQ-PROC-032-01 | AC-01 |
| AC-02 | F01 | AC-02 |
| AC-03 | F01 | AC-03 |
| AC-04 | F01 | AC-04 |
| AC-37 | F01 | AC-05 |
| AC-05 | F02 REQ-PROC-032-02 | AC-01 |
| AC-06 | F02 | AC-02 |
| AC-07 | F02 | AC-03 |
| AC-08 | F02 | AC-04 |
| AC-09 | F03 REQ-PROC-032-03 | AC-01 |
| AC-10 | F03 | AC-02 |
| AC-11 | F03 | AC-03 |
| AC-13 | F03 | AC-04 |
| AC-21 | F03 | AC-05 |
| AC-22 | F03 | AC-06 |
| AC-23 | F03 | AC-07 |
| AC-24 | F03 | AC-08 |
| AC-25 | F03 | AC-09 |
| AC-26 | F03 | AC-10 |
| AC-27 | F03 | AC-11 |
| AC-28 | F03 | AC-12 |
| AC-29 | F03 | AC-13 |
| AC-30 | F03 | AC-14 |
| AC-38 | F03 | AC-15 |
| AC-39 | F03 | AC-16 |
| AC-40 | F03 | AC-17 |
| AC-12 | F04 REQ-PROC-032-04 | AC-01 |
| AC-14 | F04 | AC-02 |
| AC-15 | F04 | AC-03 |
| AC-16 | F04 | AC-04 |
| AC-17 | F04 | AC-05 |
| AC-18 | F04 | AC-06 |
| AC-19 | F04 | AC-07 |
| AC-20 | F04 | AC-08 |
| AC-32 | F04 | AC-09 |
| AC-33 | F04 | AC-10 |
| AC-34 | F04 | AC-11 |
| AC-35 | F04 | AC-12 |
| AC-36 | F04 | AC-13 |
| AC-41 | F04 | AC-14 |
| AC-42 | F05 REQ-PROC-032-05 | AC-01 |
| AC-43 | F05 | AC-02 |
| AC-44 | F05 | AC-03 |
| AC-45 | F05 | AC-04 |
| AC-46 | F05 | AC-05 |
| AC-47 | F05 | AC-06 |
| AC-48 | F05 | AC-07 |
| AC-49 | F05 | AC-08 |
| AC-50 | F05 | AC-09 |
| AC-51 | F05 | AC-10 |
| AC-52 | F05 | AC-11 |
| AC-53 | F05 | AC-12 |
| AC-54 | F05 | AC-13 |
| AC-55 | F05 | AC-14 |
| AC-31 | F06 REQ-PROC-032-06 | AC-01 |
| AC-56 | F06 | AC-02 |
| AC-57 | F06 | AC-03 |
| AC-58 | F06 | AC-04 |
| AC-59 | F06 | AC-05 |
| AC-60 | F06 | AC-06 |
| AC-61 | F06 | AC-07 |
| AC-62 | F06 | AC-08 |
| AC-63 | F06 | AC-09 |
| AC-64 | F06 | AC-10 |
| AC-65 | F06 | AC-11 |
| AC-66 | F06 | AC-12 |
| AC-67 | F07 REQ-PROC-032-07 | AC-01 |
| AC-68 | F07 | AC-02 |
| AC-69 | F07 | AC-03 |
| AC-70 | F07 | AC-04 |

**Bijectivity check:** rows = 70. Old ids AC-01..AC-70 each appear **exactly once** (verified: no gaps, no repeats). New ids restart per feature with no gaps:
- F01: AC-01..05 (5) · F02: AC-01..04 (4) · F03: AC-01..17 (17) · F04: AC-01..14 (14) · F05: AC-01..14 (14) · F06: AC-01..12 (12) · F07: AC-01..04 (4).
- Sum = 5+4+17+14+14+12+4 = **70.** ✓

> **Authoritative counts (this table overrides every count in §1–§2 prose):**
> F01=5, F02=4, **F03=17**, **F04=14**, F05=14, F06=12, F07=4 = **70**.
> Sections: F01=5, F02=5, F03=3, F04=4, F05=1, F06=2, F07=1 = **21**.

---

## 4. Cross-cutting / hard-to-place flags

- **X1 — SEC-12/13/14 have no body heading.** The frontmatter declares SEC-12 (Flow-Aware Scribble Generation), SEC-13 (Flow-Level Composite Index), SEC-14 (Component Library), but the golden body has **no matching `##` heading** for them — the body jumps SEC-10→SEC-11 and never emits these three. Their nominal ACs (AC-16 flow ordering, AC-18 composite index, AC-19 component library) live only in frontmatter. **Recommendation:** assign SEC-12/13/14 to **F04** (content extensions) — that is where AC-16/18/19 land. At migration the script must handle these as *declared-but-empty* sections: either (a) migrate the SEC id with an empty/placeholder body, or (b) drop the SEC ids as orphans. **This needs a developer decision (see Q1).** Migration byte-exact diff is unaffected (there is no prose to move), but the empty-diff harness must know these three SEC ids carry no body bytes.
- **X2 — AC-31 is dual-tagged (SEC-16 + SEC-20).** AC-31 was rewritten and is tagged in both SEC-16 (Review Doctrine, line 842) and SEC-20 (Auto-Review Control Model, line 918). **Home: F06** (auto-review, with SEC-20). **Runner-up: F03** (SEC-16). The SEC-16 AC-31 paragraph is a back-reference; the normative AC item migrates with F06. The crosswalk single-homes it to F06/AC-01.
- **X3 — `## Related Requirements` and `## Version History` are not SEC ids.** They are epic-level boilerplate (cross-links + changelog). **Recommendation:** keep them on the **epic** `REQ-PROC-032`, not on any feature. They reference SEC-15/SEC-16 by name, so after the split those cross-refs must be rewritten to point at F03.
- **X4 — AC-13 (Flutter handoff YAML).** Genuinely sits between F03 (contract surface — SEC-15 discusses the handoff `contract:` block) and F04 (content/handoff extension family AC-12/14/15…). **Home: F03** (it is the contract's handoff carrier; AC-23 — the handoff contract block — is in F03, and AC-13/AC-23 must stay together). **Runner-up: F04.**
- **X5 — AC-37 (storage mirror) vs AC-41 (discovery).** AC-37 (lib/features mirror, SEC-05) → F01. AC-41 (contributing_requirements discovery, SEC-17) → F04. They both touch feature_path/metadata but have distinct homes; flagged only because a reference-rewrite pass touching feature_path will span F01 and F04.
- **X6 — AC-28/29/30/39 (review doctrine) could attract toward F06.** They are review/auto-review-adjacent but are SEC-16 (three-skill/contract feature). **Home: F03.** Runner-up: F06. Kept in F03 so SEC-16 is not split across two features.

---

## 5. In-flight task → owning feature mapping

| Task | Authored (golden ACs) | Section | Retarget to feature | New `parent_requirement` | New `covers.acceptance_criteria` (new ids) |
|------|----------------------|---------|---------------------|--------------------------|--------------------------------------------|
| TASK-PROC-032-30 (`author-scribble-consistency-model`) | AC-42..55 (consistency slice) | SEC-18 | **F05** `feat_consistency_sci_layer` | REQ-PROC-032-05 | AC-01..AC-14 (all of F05) |
| TASK-PROC-032-31 (`author-generator-carrier-and-review-layer`) | AC-56..62 | SEC-19 | **F06** `feat_carrier_and_auto_review` | REQ-PROC-032-06 | AC-02..AC-08 (carrier subset) |
| TASK-PROC-032-32 (`author-auto-review-control-model`) | AC-31 + AC-63..66 | SEC-20 | **F06** `feat_carrier_and_auto_review` | REQ-PROC-032-06 | AC-01, AC-09..AC-12 |
| TASK-PROC-032-33 (`author-flow-viewer-requirement`) | AC-67..70 | SEC-21 | **F07** `feat_embedded_flow_viewer` | REQ-PROC-032-07 | AC-01..AC-04 (all of F07) |

Notes:
- **-31 and -32 both retarget to F06** (they authored the two SEC blocks — SEC-19 and SEC-20 — that this seam map fuses into one feature). F06 is the single retarget for both; their `covers` are disjoint subsets of F06's AC-01..12 (no overlap: -32 owns AC-01/09/10/11/12, -31 owns AC-02..08). Confirm the fusion is acceptable (Q2) — alternative is to keep carrier (F06a) and auto-review (F06b) as two features.
- All four currently have empty `covers` and `parent_requirement: REQ-PROC-032`; the epic is non-implementable, so each must repoint to its **feature**, never the epic.
- Each task's `pending_feedback/.../answer.md` is the retarget vehicle (per goal.md scope); this seam map supplies the target feature id + new AC ids.

---

## 6. Open questions for the developer

1. **Q1 — Orphan sections SEC-12/13/14.** They are declared in frontmatter but have **no body prose** in the golden source. Migrate them as empty/placeholder sections under F04, or drop the three SEC ids entirely? (Affects what the empty-diff harness treats as "all sections migrated".)
2. **Q2 — F06 fusion.** This map fuses the carrier/review-layer slice (SEC-19, ex-TASK-031) and the auto-review control slice (SEC-20, ex-TASK-032) into one feature `feat_carrier_and_auto_review` (12 ACs). Accept the fusion, or keep them as two separate features (`feat_carrier_review_layer` AC-56..62 / `feat_auto_review_control` AC-31,63..66)? Splitting yields 8 features, still within the 5–8 target.
3. **Q3 — F03 size (17 ACs).** `feat_handoff_three_skill_and_contract` is the largest feature (17 ACs spanning SEC-11/15/16). Acceptable, or split the review doctrine (SEC-16: AC-28/29/30/39) into its own `feat_review_doctrine`? That would also push the feature count to 8.
4. **Q4 — AC-13 home.** Confirm AC-13 (flutter_handoff.yaml) belongs in F03 (contract) and not F04 (extensions). It is grouped with AC-23 (handoff contract block) in F03.
5. **Q5 — Epic boilerplate.** Confirm `## Related Requirements` + `## Version History` stay on the epic `REQ-PROC-032` (with their SEC-15/16 cross-refs rewritten to F03), rather than being distributed to a feature.
6. **Q6 — Feature ID allocation order.** Confirm features are numbered F01→F07 in the spec's reading order (as above) when `allocate_req_id.py` runs, so the suffix numbers are stable for the reference-rewrite pass across the 22 citing files + manifest.

---

## 7. Verification summary

- **70 ACs:** each of AC-01..AC-70 appears exactly once in the §3 crosswalk. ✓
- **21 sections:** SEC-01..SEC-21 each assigned to exactly one feature (F01:5, F02:5, F03:3, F04:4, F05:1, F06:2, F07:1 = 21). ✓ (SEC-12/13/14 flagged X1 — body-empty.)
- **No AC in two features; none missing.** ✓
- **Non-SEC body headings** (Related Requirements, Version History) routed to epic (Flag X3), not lost.

---

*Agent ID: see footer. This is a seam-map plan only — no requirement file modified. The §3 crosswalk is the authoritative source; all prose counts derive from it.*

---
**Agent ID:** `ae45fb0f5007f822f` (subagent of TASK-PROC-032-34, session `142cd952-df88-4e0f-b995-c821fb98bd01`).
