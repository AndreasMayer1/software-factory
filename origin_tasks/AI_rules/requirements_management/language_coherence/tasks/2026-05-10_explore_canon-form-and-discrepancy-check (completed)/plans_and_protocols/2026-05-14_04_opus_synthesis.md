# Opus synthesis — TASK-PROC-049-01

**Date**: 2026-05-14
**Model**: Opus (opus_recommended)
**Inputs**: `2026-05-10_00_user_initial_input.md`, `2026-05-10_01_lib_identifier_walk.md`, `2026-05-10_02_translation_context_shape.md`, `2026-05-10_03_web_research_prior_art.md`
**Output**: Design recommendation sized for a follow-up impl task — canon form, schema, discrepancy check, bootstrap. Honest about what remains for the user to decide.

---

## 1. Problem space — what is now known that was not at task creation

Three findings reframe REQ-PROC-049 from "another markdown artifact" to "the upstream Fluent-Term layer of the repo."

**Finding 1 — The duplication cost is not theoretical, it is measurable.**
On five concrete labels from `feat_therapist_transfer_ui`, **67% of the body of an AC-08 `translation_context` entry is concept-level redescription** if the canon does not exist. Per-label burden drops from ~200 words to ~45 words once concepts are referenced by name — a 77% reduction at the entry level, and an estimated 89% reduction across the projected ~100-entry corpus (45,000 → 5,000 words of concept text). The duplication is invisible today because AC-08 has not been instantiated; it compounds rapidly the moment translation authoring begins. The order-of-arrival matters: the canon must exist before AC-08 is implemented at scale, otherwise the redundant text is written, then has to be unwritten.

**Finding 2 — The cross-artifact check is custom code, not a configured linter.**
Of the obvious off-the-shelf tools (Vale, textlint, RetextJS, glossarify-md), exactly one half of REQ-PROC-049 AC-05 is solvable with Vale-style vocabularies: *"if a canonical name appears anywhere, it must be spelled and capitalized this way."* The other half — *"a concept defined in the canon is missing or named differently in an artifact"* — does not exist as a product. Vale's model is presence-based, not coverage-based; bending it into a coverage checker is wrong-shaped. The cross-artifact discrepancy check must be a small Python script that knows the four artifact types (markdown requirements, ARB JSON, `translation_context` YAML, Dart user-facing identifiers) and reports deltas against the canon.

**Finding 3 — The lib/ side is mostly already coherent; the problems are concentrated.**
The `lib/` walk surfaced 21 user-facing objects, 33 states, 27 operations — fewer than expected. The genuine coherence problems concentrate in three places: (a) **terminology divergence between domain code and UI**, exemplified by `SharePlanTemplateRequested` ↔ "Hand Over Plan" ↔ "Plan aushändigen" naming three different things in three artifact types for one operation; (b) **two `ScannerHardwareTier` and `ScopeVariant` enums that aren't localized**, so German users see English; and (c) **two cases that look like AC-03 verb-decomposition candidates** — `SelectRole` vs. `SwitchProfileRequested`, and `DataBeamDiscarded` vs. `DataBeamUnderDurationExit`. Most of the catalog is fine. The canon should not be drafted as a green-field design exercise; it should be an audit-and-record of what already exists, with delta corrections recorded explicitly.

**The reframing**: REQ-PROC-049 is the **Fluent-Term layer** of this repo — a registry of definitions that downstream artifacts reference by name. The strongest prior art (Mozilla Fluent's `-Term` mechanism, Lokalise/Crowdin glossary triads, Anthropic Skill reference files) all converge on the same pattern: *centralize the definition, accept duplication of local context*. That pattern, plus a script-substituted audit (because there is no runtime to catch drift the way OpenAPI does), is the shape the implementation should take.

---

## 2. Option space and recommendations

### 2.1 Canon location and form

| Option | Description | PERSONA-015 fit |
|---|---|---|
| **A. Single `canon.md` with markdown headings + YAML frontmatter per concept** | One file at `requirements_user_needs/CONCEPT_CANON.md`. One `## ConceptName` per concept, alphabetical. YAML block under each heading carries machine-readable fields. | **Best.** Flutter docs, Dart docs, OpenProject glossary all prove this scales. One mental index. No fan-out failure mode. Human-editable, machine-parseable, no daemon, no DSL. Maps onto the `glossarify-md` shape. |
| B. Per-bounded-context `canon/<context>.md` files | One file per bounded context (therapist, client, transfer, plans). | Fan-out failure mode for solo dev — exactly the case the web research flagged. Each new feature tempts a new file. Synonym tracking across contexts fragments. |
| C. YAML/JSON registry (`canon.yaml`) consumed by tooling | A pure data file. Human reading requires a viewer. | Tooling is easier; reading is harder. The canon is *read by humans authoring requirements and labels far more often than it is consumed by tooling*. Wrong audience optimization. |
| D. Generated from `lib/` annotations | Each user-facing class/enum carries a `@CanonName('...')` annotation; the canon is harvested. | Misses the upstream artifacts (requirements, scenarios, flows) where most authoring happens *before* code exists. Code-first canon leaves the bulk of the repo un-canonized. |
| E. Hybrid: A + harvested supplement from `lib/` | Authored `CONCEPT_CANON.md` is canonical; the check script harvests `lib/` identifiers as *evidence of consumption*, not as canon entries. | Acceptable, but the harvesting is the discrepancy-check's job, not the canon's. Folding it into the canon couples them unnecessarily. |

**Recommendation: Option A — single `CONCEPT_CANON.md` at `requirements_user_needs/`**.

- Lives next to `SCENARIO_INDEX.md` because both are user-facing-language registries; this is the right neighborhood.
- Single file, alphabetical, markdown headings, YAML block per heading.
- Machine-parseable: a 30-line Python parser can extract every concept's structured fields.
- Resists the fan-out failure mode that has historically killed solo glossaries.
- Matches the strongest external prior art (Fluent Terms, Lokalise glossaries, Skill reference files).

Why not B (per-context files): the failure mode for solo developers is "too many files," not "one large file." A 200-term `canon.md` is ~2000 lines; that is still indexable. Splitting it costs more than it saves until the canon is much larger than this app will plausibly grow.

Why not C (pure YAML): the primary reader is a human authoring a requirement or label, and an LLM agent helping them. Both prefer markdown with embedded YAML over pure YAML.

### 2.2 Canon schema per concept

The schema must satisfy the four reference points (requirements bodies, UI labels, `translation_context` entries, user-facing `lib/` identifiers) without becoming a maintenance sink. The Layers-skills `term / rejected alternatives / decision` triple combined with Fluent's "definition referenced by name" model gives the minimum useful payload:

```yaml
---
id: CONCEPT-PLAN
type: object              # object | state | operation
name_canonical: "Plan"    # the canonical English name
name_de: "Plan"           # canonical German name (or "" if not user-visible in de)
scope: [therapist, client]   # bounded contexts where this concept surfaces
states: [draft, published, assigned, completed]    # only for type=object
operations: [create, edit, publish, assign, hand-over, withdraw]
rejected_alternatives:
  - term: "Questionnaire"
    reason: "Used internally as Questionnaire (sub-component of Plan); the user-facing whole is Plan"
  - term: "Form"
    reason: "Too generic; doesn't capture the structured-questionnaire shape"
synonyms_in_artifacts: []    # legacy/intentional divergences acknowledged (per AC-02)
see_also: [CONCEPT-QUESTIONNAIRE, CONCEPT-HAND-OVER]
vtr_refs: []    # link to Value Trade-off Records when the naming choice encoded a value conflict
---
A structured questionnaire containing multiple Questions arranged in order.
Therapists create Plans and Hand Over Plans to Clients; Clients complete Plans
by answering each Question.
```

**Field-by-field rationale**:

- `id` — stable identifier `CONCEPT-<NAME>`; referenced by other artifacts via `[[CONCEPT-NAME]]`-style or plain text where the canonical name suffices.
- `type` — three values only. `object` (a noun a user encounters), `state` (a status the user sees), `operation` (a named verb).
- `name_canonical` / `name_de` — the canonical names. Per-locale because translation is in scope (REQ-NFUNC-013).
- `scope` — bounded context tags so that `Mood` in one context and `Mood` in another can be distinguished if needed. For this app, scopes are coarse: `therapist`, `client`, `transfer`, `core`.
- `states` / `operations` — only for `type=object`. Lists existing state values and named operations. Each one referenced should be itself a `CONCEPT-*` of type `state` or `operation` — but for the bootstrap, plain string entries are acceptable.
- `rejected_alternatives` — the Layers-skills lesson. Without this, the next AI session "fixes" deliberate choices.
- `synonyms_in_artifacts` — AC-02's escape valve. Where a legacy or role-specific term cannot be removed (e.g. `SharePlanTemplateRequested` event in `lib/` for the "Hand Over" operation), the synonymy is acknowledged here rather than silently elsewhere.
- `see_also` — cross-link to related concepts (closes the `[[X]]` pattern in canon entries).
- `vtr_refs` — link to Value Trade-off Records when naming encodes a value conflict between personas. Almost always empty; non-empty cases are rare and important.

**The body text** under each heading is the human-readable definition: 1–3 sentences. Definitions are *upstream of artifacts*: a label's `translation_context` references this concept by name and adds only label-specific context, never repeating the definition.

### 2.3 Discrepancy check architecture

**Recommendation: two narrow tools, neither a CI gate, both on-demand.**

| Sub-problem | Tool | Form |
|---|---|---|
| "If a canonical name appears, it must be spelled exactly this way" | Vale with a generated `accept.txt` vocabulary | Generated from `CONCEPT_CANON.md` by a small script; runs as `vale requirements_tasks/ requirements_user_needs/ lib/l10n/`. |
| "A concept is in the canon but missing/divergent in artifact X" (and inverse) | Custom Python script `scripts/requirements/check_canon.py` | On-demand audit. Parses the canon. Greps each of the four artifact types for canonical names and known divergences. Produces a single pass/fail line plus a delta list. |

**What the custom script knows**:

1. **Markdown requirements** — greps `requirements_tasks/**/*.md` for canonical names; flags any artifact that uses a `rejected_alternative` term without it being in `synonyms_in_artifacts`.
2. **ARB JSON UI labels** — parses `lib/l10n/app_*.arb`; same name-coverage check on the English string values. (German is checked against `name_de` if present.)
3. **`translation_context` entries** — once they exist (REQ-NFUNC-013 AC-08 downstream), parses them and checks that each entry references at least one canonical concept by ID.
4. **Dart user-facing identifiers** — greps `lib/features/**/presentation/` for class names, BLoC event names, BLoC state names; matches against canon `operations`/`states`/`name_canonical`. Flags divergences.

**Pass/fail signal** (per AC-05): the script exits 0 (pass) when zero unacknowledged divergences are found, exits 1 (fail) otherwise. The output format is deliberately small: one line summary plus a delta list. This matches REQ-PROC-046's binary back-pressure pattern.

**Why not a G6 gate today**: a CI-blocking gate is the wrong cost-benefit shape at this stage. The canon is still being bootstrapped; gates against a half-bootstrapped canon would block all work. Run on demand before releases and before requirement-authoring sessions. *Whether to promote it to a G6 gate later is a user decision (see §5.1)*.

**Why not embedding-based fuzzy matching**: at ~50–200 terms, exact-name lookup is sufficient. RAG/embedding infrastructure for canonical-name resolution is premature at this scale (web research §6).

**Why not save-time hooks**: the audit's cost-benefit only works as on-demand; save-time linters fight back when authoring across multiple artifacts in one session.

### 2.4 Bootstrap strategy

| Option | Description | PERSONA-015 fit |
|---|---|---|
| **A. Seed the canon from `feat_therapist_transfer_ui` (covered in lib walk)** | Use the ~30 concepts already inventoried (Plan, Client, Hand Over, Scan, Scanner Hardware Tier, etc.) as the initial canon. | **Best.** Concrete, scoped, fast. Provides immediate working material for the AC-08 worked example. Discrepancy check can be exercised against a small canon. |
| B. Full-app retrofit before turning on the check | Inventory every user-facing concept across all features, populate the canon, then run the check. | High upfront cost; defers AC-08 value. Solo-dev failure mode: large all-at-once project that never finishes. |
| C. Bootstrap from `lib/` automatically | Generate canon stubs from `presentation/bloc/*_event.dart`, `*_state.dart`, and entity classes. | Misses the upstream-artifact concepts not yet in code (e.g. flow-level concepts). Generates noise. |

**Recommendation: Option A**. Seed with `feat_therapist_transfer_ui`'s ~30 concepts (already inventoried in `2026-05-10_01_lib_identifier_walk.md`). Implementation tasks add new concepts incrementally as new features or labels are authored. The check script's scope grows with the canon — it ignores artifacts that mention no canonical concepts (so an un-canonized feature does not block).

**Bootstrap deliverables** (for the impl task):

1. `requirements_user_needs/CONCEPT_CANON.md` with ~30 entries covering `feat_therapist_transfer_ui` concepts.
2. `scripts/requirements/check_canon.py` (custom audit script).
3. Generated `.vale/styles/Canon/accept.txt` from the canon (script also outputs this).
4. Five reauthored `translation_context` entries (the five from `2026-05-10_02`) using the canon — demonstrates the post-canon shape.
5. AC-02 synonym acknowledgement entries for the three known divergences from the lib walk: `SharePlanTemplateRequested` ↔ Hand Over, `SelectRole`/`SwitchProfileRequested` ↔ Set Role, `DataBeamDiscarded`/`DataBeamUnderDurationExit` ↔ Transfer Cancelled.

---

## 3. Worked example — before-canon vs. after-canon, one label

This consolidates the worked example from `2026-05-10_02_translation_context_shape.md` §§ 5–6 and pins down the canon entries that make it work.

### 3.1 The canon entries (excerpt)

```yaml
## Plan
---
id: CONCEPT-PLAN
type: object
name_canonical: "Plan"
name_de: "Plan"
scope: [therapist, client]
states: [draft, published, assigned, completed]
operations: [create, edit, publish, assign, hand-over, withdraw]
rejected_alternatives:
  - term: "Questionnaire"
    reason: "Questionnaire is a sub-component of Plan; the user-facing whole is Plan"
  - term: "Form"
    reason: "Too generic; obscures the structured-questionnaire shape"
synonyms_in_artifacts: []
see_also: [CONCEPT-QUESTIONNAIRE, CONCEPT-HAND-OVER, CONCEPT-CLIENT]
---
A structured questionnaire containing multiple Questions arranged in order.
Therapists create Plans and Hand Over Plans to Clients; Clients complete Plans
by answering each Question.

## Hand Over (operation)
---
id: CONCEPT-HAND-OVER
type: operation
name_canonical: "Hand Over"
name_de: "Aushändigen"
scope: [therapist]
rejected_alternatives:
  - term: "Send"
    reason: "Technical/digital connotation; loses the personal/physical metaphor"
  - term: "Transmit"
    reason: "Engineering term; clinical context wants warmer language"
  - term: "Share"
    reason: "Implies permission/access; this is a one-shot transfer to one client"
synonyms_in_artifacts:
  - artifact: "lib/features/therapist/plan_templates/presentation/bloc/plan_templates_event.dart"
    term: "SharePlanTemplateRequested"
    reason: "Domain code retained 'Share' from an earlier design; user-facing label is Hand Over. Refactor pending; meanwhile, the synonymy is acknowledged here."
see_also: [CONCEPT-PLAN, CONCEPT-SCAN]
---
Therapist-initiated transfer of an assigned Plan from the therapist device
to a Client device via QR code scanning. The client completes the operation
by performing a Scan. Inverse: Withdraw.
```

### 3.2 The label, before and after the canon

**Before (~210 words, 71% concept-level burden)** — full text in `2026-05-10_02_translation_context_shape.md` §5 Label 1.

**After (~50 words, 0% concept-level burden, 76% reduction)**:

```yaml
key: handoverButtonLabel
de: "Plan aushändigen"
en: "Hand Over Plan"
translation_context: >
  Therapist handover dialog, primary action button. Initiates CONCEPT-HAND-OVER
  of a CONCEPT-PLAN.

  User situation: Therapist has selected a plan and opened the handover dialog.
  The therapist now initiates the plan transfer.

  Tone: "Aushändigen" preserves the physical-personal metaphor (see canon
  rejected_alternatives: "Senden", "Übertragen"). Same metaphor in English:
  "Hand Over", not "transmit" or "send."
```

The translator can now read `CONCEPT-PLAN` and `CONCEPT-HAND-OVER` in `CONCEPT_CANON.md` once, then translate every label that references them with only the label-specific context (which screen, which audience, which moment of use).

---

## 4. Where this lands relative to REQ-PROC-049's AC-01..AC-05

| AC | How the recommendation satisfies it |
|----|-------------------------------------|
| AC-01 | `CONCEPT_CANON.md` is the single canonical source. Each concept appears once. |
| AC-02 | Discrepancy check parses each artifact type and matches against canon; unacknowledged uses of `rejected_alternatives` or undeclared synonyms fail the check. `synonyms_in_artifacts` is the explicit escape valve. |
| AC-03 | Generic-verb detection: the check has a list of generic verbs (Add, Create, Edit, Update, Delete, Remove, Save, Submit, Send, Share); when one appears in a user-facing artifact, the script flags it if the operation it names is not in the canon's `operations` field for the affected object. Two known cases (Hand Over vs. Share, Set Role vs. Select/Switch) are bootstrap synonyms; new cases surface in the check output. |
| AC-04 | The worked example demonstrates the post-canon `translation_context` shape. The check verifies that every `translation_context` entry references at least one canonical concept ID. |
| AC-05 | The custom `check_canon.py` script produces a binary pass/fail signal, deterministically, from the current repo state. No reviewer memory required. |

---

## 5. Decisions requiring user input (framed for decision)

### 5.1 Should the discrepancy check become a G6 back-pressure gate eventually?

REQ-PROC-046 establishes G1–G5 as binary pass/fail code-quality gates. AC-05 of REQ-PROC-049 specifies a pass/fail signal in the same shape, but does not say it must run in CI. Two stances:

- **(a) Stay on-demand.** Run before releases and before requirement-authoring sessions. Cost: human discipline to run it. Benefit: zero friction during normal work.
- **(b) Promote to G6 once the canon is mature.** A future task adds it as a release-precondition (similar to existing pre-release checks). Cost: any unacknowledged drift blocks release. Benefit: zero reliance on memory.

**Recommend**: start with (a). Re-evaluate after the canon has been authored for two or three feature areas; once it stabilizes, the cost-benefit of promoting to G6 should be revisited. The decision is reversible.

### 5.2 Authoring workflow: extend `requ-explore` or add a new `canon-add-concept` skill?

When a new feature introduces a new concept, where does the canon get updated?

- **(a) Extend `requ-explore`** to add a "canon impact" step: any new user-facing noun/verb/state in a feature must be reflected in the canon. The skill calls `check_canon.py` after writing the requirement and fails closed if the new concept is not in the canon.
- **(b) Add a dedicated `canon-add-concept` skill** invoked explicitly when concept changes are needed.

**Recommend (a)**, with a fallback to (b) only if (a)'s skill text grows past the token budget. Existing UX infrastructure (`ux-create-flow`, `ux-write-persona`, `ux-write-scenario`) has been authored but never used; *adding another UX-shaped skill before the existing ones are used would be the failure mode flagged in §2 of the user's initial input.* `requ-explore` extension keeps the canon embedded in the authoring path that *is* already used.

### 5.3 Canonical language for `name_canonical` — English, German, or both?

Today the app is bilingual (en + de). The canon's `name_canonical` field is currently English in the proposal. Three stances:

- **(a) English is the canonical name; `name_de` is the German rendering.** Engineering convention. But the app is German-first (the user's prior memory: "User's German UI labels are primary, English follows from them").
- **(b) German is the canonical name.** Matches the app's primary audience.
- **(c) Both are equal; the canon is bilingual at the name level.** No primary language; downstream consumers pick.

**Recommend (a)** for tooling reasons (Dart class names are English; requirements are English; the check script's regex matching is simpler against English). The `name_de` field is a first-class rendering, not an afterthought. *But this is a user judgment call about product identity, not an engineering question.*

### 5.4 Scope of canon coverage — user-facing only, or also flow concepts?

The lib walk inventoried code identifiers. The web research suggested that the canon should also include concepts that surface in `user_flows/` and `scenarios/` *before* they appear in code. Two stances:

- **(a) User-facing only (per AC-02 wording).** Concepts visible to end users. Implementation-internal types stay out.
- **(b) Include flow-level concepts.** Names that appear in `requirements_user_needs/user_flows/*.md` step descriptions but not yet in code.

**Recommend (a)**, with the understanding that flow-level concept names *that will appear in user-facing artifacts* should be canonized when the flow is authored, before code exists. This is the natural workflow extension in §5.2.

---

## 6. What remains uncertain

- **Total canon size**: estimated 50–200 entries at maturity. The bootstrap covers ~30. Whether the upper bound is closer to 100 or 200 depends on how many state values and named operations become user-visible. The single-file approach holds at either end.
- **Auto-harvesting Dart identifiers**: the discrepancy check parses Dart user-facing identifiers (state class names, BLoC event names) by name. Whether this needs a structured Dart parser (analyzer package) or grep-based extraction is sufficient is unknown; grep should work for the patterns this codebase actually uses (BLoC events end in `Event`, BLoC states end in `State`). Revisit if false positives become noisy.
- **Synonym detection of variant casing/whitespace**: e.g. "Hand Over" vs. "Hand-over" vs. "Handover" — the check should normalize these before matching, but the normalization rules will need iteration.
- **Whether AC-03 verb-precision can be fully automated**: detecting "this generic verb hides two different operations" requires either an authored list of generic verbs plus a per-object operations list (mechanical, achievable) or semantic reasoning over user intent (LLM-assisted, fuzzier). The recommendation goes mechanical first; LLM-assisted review is a deferred option.
- **What happens when the discrepancy check runs at the same time as a refactor**: a refactor that renames a concept produces churn in artifacts; running the check mid-refactor produces false-positives. Mitigation: the check has a `--baseline` flag that records the current state as "acknowledged"; subsequent runs only flag *new* drift. Whether this baseline mechanism is worth building immediately or deferred is open.
- **Bilingual canon maintenance load**: if German strings drift from English (e.g., a new German label is added without an English equivalent), the canon's `name_de` lookup falls back to the canonical name. This is a known soft spot — a translator who only authors German would not surface the gap. Not a blocker for the bootstrap.

---

## 7. Sized for follow-up implementation

A follow-up `impl` task derived from this plan would cover:

1. **Create `requirements_user_needs/CONCEPT_CANON.md`** with the ~30 entries from `feat_therapist_transfer_ui` (Plan, Client, Question, Questionnaire, Hand Over, Scan, Scanner Hardware Tier, Data Beam, Transfer Bundle, Therapist, Set Role, Switch Profile, Edit Client, …). Each entry follows the schema in §2.2.
2. **Acknowledge the three known synonymies** from the lib walk in `synonyms_in_artifacts`: `SharePlanTemplateRequested` → Hand Over; `SelectRole` / `SwitchProfileRequested` → Set Role; `DataBeamDiscarded` / `DataBeamUnderDurationExit` → Transfer Cancelled.
3. **Write `scripts/requirements/check_canon.py`** — single-file Python script. Parses the canon. Greps each of the four artifact types. Produces a single pass/fail line plus a delta list. Exits 0 on pass, 1 on fail.
4. **Write the Vale `accept.txt` generator** — same script, `--emit-vale` flag. Writes `.vale/styles/Canon/accept.txt` from the canon.
5. **Reauthor the five `translation_context` entries** from `2026-05-10_02_translation_context_shape.md` §6 as the worked example demonstrating the post-canon shape. Live in a draft location (not yet committed to ARB) so that AC-08's downstream impl task can adopt them when it lands.
6. **Update `requ-explore` skill** to run `check_canon.py` after writing or modifying a requirement; fail-closed if new user-facing concepts are missing from the canon. (This is the §5.2 recommendation; if the user prefers a separate `canon-add-concept` skill, the impl task is scoped accordingly.)
7. **Update `CLAUDE.md`** with a one-line reference to the canon as the source of truth for user-facing concept names. Do NOT inline the canon into CLAUDE.md (per the web research §6 lesson).

The impl task is approximately M-sized (single feature area, single script, one skill update, one document creation). It is well-defined enough that an implementer can begin without redoing design work.

---

## 8. Coverage of goal.md acceptance criteria

| Goal AC | Status |
|---------|--------|
| Exploration produced at least one Opus synthesis round | ✓ (this document) |
| Synthesis defines the problem space in terms not fully known at task creation | ✓ §1 (duplication cost quantified at 67% concept-level burden; cross-artifact check is custom code, not a configured linter; lib/ is mostly already coherent with three named coherence problems) |
| At least two viable options compared for each major decision, with recommendation justified against PERSONA-015 grounded values | ✓ §2.1 (canon form), §2.3 (discrepancy check), §2.4 (bootstrap); schema in §2.2 derived from prior art |
| A concrete worked example showing one feature's `translation_context` entries before and after the canon | ✓ §3 with full canon entries and 76% reduction quantified; full five-label expansion in `2026-05-10_02_translation_context_shape.md` §§ 5–6 |
| Decisions requiring user input are identified and framed clearly | ✓ §5 (four open decisions) |
| The output is honest about what remains uncertain | ✓ §6 (five known soft spots) |
| Sized for follow-up implementation: an impl task can be derived without further design work | ✓ §7 (seven concrete deliverables) |

---

## 9. Recommended next steps

1. The user reviews §5 (four open decisions). Default recommendations are documented; explicit overrides are recorded as decisions.
2. A follow-up `impl` task is created from §7. The task workspace folder name suggestion: `2026-05-XX_impl_bootstrap-concept-canon`.
3. The discrepancy check's promotion to a G6 gate is deferred — re-evaluated after two or three feature areas have been canonized.
