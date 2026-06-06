# Opus Synthesis v2 — Canon Form, Discrepancy Check, and Workflow Embedding

Date: 2026-05-15
Model: Opus 4.7
Inputs:
- v1 synthesis (`2026-05-14_03_opus_synthesis.md`) — superseded by this document
- Parallel session's synthesis (`2026-05-14_04_opus_synthesis.md`) — useful findings folded in
- User feedback (`2026-05-15_05_feedback.md`) — drives the structure of this document
- REQ-PROC-046 / REQ-PROC-052 (back-pressure family) — coordination context

This document supersedes v1 in the areas the user flagged. Confirmed v1 decisions are carried forward unchanged.

---

## 0. Critical correction since v1

**G6 is already taken — Accessibility compliance.** REQ-PROC-046 §Behavior defines:

> G1 Source hygiene · G2 Complexity bounds · G3 Test correctness · G4 Architectural purity · G5 Suppression discipline · **G6 Accessibility compliance** · G7 Performance budget · G8 Bundle size

v1's proposal to "make the canon check G6" was wrong. The actual question is: does the canon-coherence check belong in the *gate set at all*, and if so, under what gate-set extension policy?

Two further corrections from REQ-PROC-046:

1. **REQ-PROC-046 G6 already includes a linguistic-complexity sub-check** on `.arb` strings ("the linguistic-complexity gate (REQ-NFUNC-002 cognitive-accessibility AC) returns no violations on the `.arb` strings shown by the screen"). This is what the user referenced in feedback §3 ("wir haben dort entschieden, dass wir einfache Sprache benutzen wollen"). **Canon-coherence and simple-language are adjacent but distinct concerns**; both walk `.arb`. They should share parsing infrastructure, not gate identity.
2. **"Gates are mandatory, not advisory"** (REQ-PROC-046 Developer Guidelines). A warn-only bootstrap phase for a gate is incompatible with the gate model. If we want bootstrap latitude, the canon check must live *outside* the per-change gate loop (on-demand audit) — or wait for full coverage before becoming a gate.
3. **"The gate set is closed"** (REQ-PROC-046 §Behavior). Adding a new gate requires user approval, a separate task, and updates to `analysis_options.yaml` + this requirement together. v1's casual "add it as G6" assumed too much.

The fix is in §5 below: canon check is an **on-demand audit at REQ-PROC-049-owned-script level**, sibling to but not part of REQ-PROC-046's per-change gates. Promotion to a per-change gate is deferred per the user's §10.4 (acknowledged deferral).

---

## 1. What the user confirmed, deferred, or corrected (v1 → v2 carry-forward)

| v1 § | User decision | v2 status |
|---|---|---|
| §1 Option B (YAML + generated markdown) | Confirmed | Carry forward; location updated per §10.1 |
| §2 Option α (minimal schema) | Confirmed in spirit; **deeper questions raised** about translation workflow | Schema extended in §6 with `provenance:` and reduced workflow ambiguity |
| §3 Option I (single Python script) | Confirmed; coordinate with back-pressure work | Architecture updated in §7 (shared parser with G6 linguistic check) |
| §4 Bottom-up bootstrap | Confirmed; **deeper question raised** about where terms come from | Schema adds `provenance:`; §6.3 establishes the source pipeline |
| §5 G6 gate | **WRONG — G6 is taken** | Replaced by §5 below: on-demand audit, gate promotion deferred |
| §6 Worked example | Read; reduction direction OK; precise number not contested | Carry forward |
| §7 Cost balance | Read; not contested | Carry forward |
| §8 "UX skills not used" | **CORRECTED — they have been used extensively**; UI-scribble / design-system skills are the unused ones (alpha-phase intentional) | §8 below rewritten |
| §10.1 location | **Subfolder requested**: `requirements_user_needs/concept_canon/` | Adopted |
| §10.2 primary language | **English** | Adopted; `aliases.de` for German rendering |
| §10.3 `lib/core/` scope | **Exclude** `lib/core/`; design system has no labels by design | Adopted; lint scope is `lib/features/**/presentation/` only |
| §10.4 warn-only duration | Deferred | Deferred |
| §10.5 code naming | **Code can use different terms**; DDD-style alignment is nice-to-have not enforced | §9 explores what DDD enforcement would mean; recommendation stays "acknowledge in `aliases.code`, no enforcement" |
| §10.6 inline code marker | Deferred | Deferred |
| §10.7 `type: ui_surface` | Deferred | Deferred |

New v2 sections (driven by user feedback):
- **§3**: Coordination with the paused back-pressure work (feedback §3)
- **§4**: Term provenance — where terms come from, how to record evidence, how to upgrade as user research arrives (feedback §4)
- **§6**: Translation workflow — files, references, who-when-how (feedback §2 and §8)
- **§8**: Workflow embedding — which existing skills change, what new skill is added, who maintains the canon (feedback §8)
- **§9**: DDD posture — what enforcing DDD alignment would mean (feedback §10.5)

---

## 2. Subfolder structure (per §10.1)

```
requirements_user_needs/concept_canon/
├── README.md                  # explains the canon, the workflow, the linter
├── concept_canon.yaml         # source of truth — hand-authored
├── concept_canon.md           # generated rendering for humans (read-only)
└── provenance/                # (optional) supporting evidence files
    ├── user_research_2026-XX-XX.md
    └── card_sort_2026-XX-XX.md
```

The `provenance/` subfolder is empty at bootstrap; entries reference it only when their `provenance.level: validated`.

Rationale for subfolder (over single sibling files):
- The canon will accumulate provenance evidence over time (user research notes, card-sort transcripts). Grouping under one folder is cleaner than scattering.
- Matches the existing pattern (`personas/<name>/`, `user_flows/<id>/` are folders, not single files).
- The README inside the folder is the entry-point document — when an LLM agent or a contributor approaches the canon for the first time, that README explains the workflow without requiring them to read this synthesis.

---

## 3. Coordination with the paused back-pressure work (feedback §3)

The user flagged that 26 back-pressure tasks (TASK-PROC-046-*, TASK-PROC-052-*, TASK-PROC-002-*) are paused in the priority-override file. Coordination is required so we do not implement overlapping but inconsistent things.

### Where the overlap lives

| Concern | This task (REQ-PROC-049) | Back-pressure work |
|---|---|---|
| Lint `.arb` string values | Canon-coherence: do strings use canonical names? | G6 linguistic-complexity sub-check: are strings simple enough? |
| Per-change vs. on-demand | On-demand audit (§5) | Per-change gate (mandatory) |
| Pass/fail signal shape | Identical (REQ-PROC-046's binary pattern) | Identical |
| Output format | Exit code + delta list | Exit code + violation report |

Both walk the same files. Both produce binary results. They are not the same check, but their parsers and output infrastructure should be shared.

### Concrete coordination plan

1. **Before any impl task starts**, read these Tier-0 tasks to confirm what they assume about `.arb` parsing:
   - `TASK-PROC-046-01` — root exploration task for the back-pressure design (probably the most context-rich)
   - `TASK-PROC-046-07` — already done (explore, marked `closed` per commit `4ccd0c87`)
   - `TASK-PROC-046-12` — gate-set adjustments
   - `TASK-PROC-046-02` — back-pressure rollout
2. **Identify whether** any of those tasks have already proposed an `.arb` walker module (e.g. `scripts/quality/_arb_parser.py`). If yes, the canon's `check_canon.py` *consumes* that module rather than rolling its own. If no, propose a shared module and let either side create it first.
3. **Place the impl task's `after:` field** with a reference to whichever back-pressure task is upstream of the shared parser. This makes the dependency explicit in `next_tasks.py` ranking.
4. **If a back-pressure task is in flight when the canon impl task is ready**, the canon waits — per the user's note that paused tasks not in-progress may be adjusted, but in-progress ones must not be disturbed.

This is a meta-decision, not part of the canon's design itself. It belongs at the start of the bootstrap-canon impl task, before any code is written.

### Independence claim

Aside from the shared `.arb` parser, the canon-coherence check has zero overlap with the existing gate set:
- G1 (analyzer): different rule space.
- G2 (complexity): different file content.
- G3 (tests): unrelated.
- G4 (architecture): may *consume* the canon's `aliases.code` map to allow named exceptions, but that's a one-way reference.
- G5 (suppressions): unrelated.
- G6 linguistic-complexity sub-check: shares the ARB parser only.
- G7 (perf), G8 (bundle size): unrelated.

So the coordination is bounded: one shared parser module. Everything else is independent.

---

## 4. Term provenance — where terms come from (feedback §4)

The user raised a question v1 did not address: terms are not arbitrary names. They should be derived from the people who will use them (personas), the situations those people are in (scenarios), and the paths they walk (user flows). Good UX writing is user-research-backed and validated. Where validation is not possible (limited access to users), the canon must still record that fact honestly so future work can lift it.

### Provenance levels

Each canon entry carries a `provenance:` block with a level:

| Level | Meaning | Trigger to upgrade |
|---|---|---|
| **inferred** | Term chosen by LLM + app-provider judgement, no user data | Any actual user data |
| **evidenced** | Term grounded in a persona, scenario, or flow that surfaces it; or in published research | User validation (interview, card sort, feedback) |
| **validated** | Term confirmed by direct user contact — interview transcript, card sort result, or user-reported feedback | None — this is the top level |

This mirrors the existing tier system in REQ-NFUNC-013 §12 ("Tier T1: Pre-Framework, Human-Defined", etc.) but is specific to the canon.

### Schema addition (extends §2.2 of v1)

```yaml
- id: CONCEPT-PLAN
  name_canonical: "Plan"
  # … (other fields per v1 §2.2, with refinements per §6 below) …
  provenance:
    level: inferred                     # inferred | evidenced | validated
    sources:                            # always required at level >= evidenced
      - "PERSONA-001 scenarios.md mentions 'mood tracking plan'"
      - "user_flows/FLOW-007/flow.md step 3"
    validated_at: ""                    # ISO date; only when level == validated
    notes: >
      The term "Plan" was chosen for compactness over "Questionnaire Plan"
      because therapist personas already use "Plan" colloquially. No user
      validation yet — flag for first beta interview round.
```

### Bootstrap implication

Almost all bootstrap entries will start at `level: inferred`. That is honest, not embarrassing. The discrepancy check will report distribution:

```
Canon coverage: 28 concepts
  inferred:  24
  evidenced:  4
  validated:  0
```

This is itself a useful signal — it tells the app provider where to focus when user research becomes possible. It also gives REQ-PROC-050 (Artifact Soundness Assessment) a measurable hook into the canon's epistemic state.

### Where the seed terms come from at bootstrap

Concrete sequence for `feat_therapist_transfer_ui`:

1. Read `requirements_user_needs/personas/app_provider/persona.md` (PERSONA-015) and any persona files referenced by REQ-PROC-049 (`personas_served: [PERSONA-015, PERSONA-001]`).
2. Read `requirements_user_needs/user_flows/*/flow.md` for any flow that touches plan handover. Where flows already use a term, that is *evidence* — the canon entry gets `level: evidenced` with the flow ID in `sources`.
3. Read existing requirement bodies that touch this feature area (REQ-FUNC-007 plan transfer, REQ-NFUNC-013 §8.4). Where a requirement chose a term and that choice is explained in the requirement body, that is also evidence.
4. Read `lib/features/therapist/data_transfer/presentation/` — code identifiers and hardcoded UI strings. These are *not* evidence (code is downstream), but they do surface concrete terms that have been used in the product. The canon records the user-facing terms as `name_canonical` and the code-internal terms as `aliases.code`.
5. Everything that does not derive from persona/scenario/flow/requirement is `level: inferred`.

### Adjustment / validation later

When user research arrives — beta-phase feedback, interview transcripts, card sorts — the canon entries are *upgraded*, not rewritten:

```yaml
provenance:
  level: validated
  sources:
    - "interview transcript 2026-09-14 (3/5 participants chose 'Plan')"
    - "card sort 2026-10-02 (Plan grouped with Therapist, Client, Hand Over)"
  validated_at: "2026-10-02"
  notes: >
    Two participants preferred "Programm"; rejected because of conflict with
    PERSONA-002 (Max) tier-1 sensitivity to clinical/institutional terms.
```

Upgrades may flip a canonical name. When that happens, the discrepancy check's job becomes harder for one cycle (all existing references to the old name flag as drift) — manageable, but worth noting.

### Recording disagreement

When validation contradicts inference, the canon records both:

```yaml
rejected_alternatives:
  - term: "Programm"
    reason: >
      Surfaced in interview 2026-09-14 but rejected — conflicts with
      PERSONA-002 sensitivity to clinical/institutional terms.
```

This is the layers-skills "rejected alternatives" discipline plus an evidence trail.

---

## 5. Discrepancy check architecture — on-demand audit, not gate

### What changed from v1

v1 proposed making the check a G6 gate. G6 is taken; gate-set extension is a user decision; and warn-only bootstrap is incompatible with the gate model. v2 places the check **outside the gate set** as an on-demand audit, with explicit user-controlled promotion to a gate later.

### Architecture

`scripts/requirements/check_canon.py` — single Python script. Same shape as v1:

1. Load `concept_canon.yaml` → indexes: canonical names, forbidden synonyms (with `prefer` + `note`), `aliases.de`, `aliases.code`.
2. Walk artifacts:
   - **Requirements markdown** (`requirements_tasks/**/requirements.md`): strip frontmatter, scan bodies for canonical-name violations.
   - **ARB string values** (`lib/l10n/app_*.arb`): scan values (not keys); per-language alias lookup.
   - **`translation_context` entries** (path TBD per AC-08 implementation): scan description text. No-op until AC-08 lands.
   - **Dart user-facing strings** (`lib/features/**/presentation/`): extract literals from `Text(...)`, `Tooltip(...)`, `InputDecoration(labelText:, hintText:)`, `AppBar(title: Text(...))`. **Exclude `lib/core/`** per user §10.3.
3. AC-03 verb-precision check: short list of generic verbs (Add, Create, Edit, Update, Delete, Remove, Save, Submit, Send, Share, Open, Close, Cancel, Discard, Complete). Each occurrence must map to a canon-registered operation; otherwise flag.
4. Output: exit 0/1 + delta list (file:line:found:prefer:note).

### Shared infrastructure with REQ-PROC-046 G6

Both checks walk `.arb` values. Concrete proposal:

```
scripts/quality/_arb_parser.py            # shared parser, public functions
scripts/quality/check_linguistic_complexity.py   # consumes _arb_parser  (G6 sub-check)
scripts/requirements/check_canon.py        # consumes _arb_parser (on-demand audit)
```

`_arb_parser.py` exposes:
```python
def iter_arb_entries(path: pathlib.Path) -> Iterable[ArbEntry]:
    """Yield (key, value, description, placeholders, language_code)."""
```

Either side can create the module first; whichever does it documents the interface so the other consumes it unchanged.

### Per-change vs. on-demand

| Surface | Approach |
|---|---|
| Per-change | NOT a gate during bootstrap. Authoring-time hints in skills (§8) catch the common cases. |
| On-demand | `python3 scripts/requirements/check_canon.py` runs:<br>– Before any requirement-authoring session that creates a new feature<br>– Before each release as part of pre-release checks<br>– Manually by the user whenever they want a coverage snapshot |
| Future promotion to gate | Deferred per user §10.4. When triggered, becomes a new task that updates the canon + REQ-PROC-046 gate set together. |

### Why on-demand, not gate

Three reasons specific to this canon at this moment:

1. **Bootstrap latitude needs warn-only.** Gates are mandatory by design (REQ-PROC-046 Developer Guidelines). Bootstrap inherently has partial coverage. Squaring those two is incoherent unless we pause adoption until coverage is complete — which is the high-cost retrofit path Option B that we rejected in v1 §4.
2. **The 26 paused back-pressure tasks haven't finished.** Adding a new gate before the gate framework itself stabilizes invites churn. On-demand audit is movable; gate identity is not.
3. **User explicitly deferred §10.4** (warn-only duration / promotion trigger). The on-demand audit is the steady state until that decision is taken.

---

## 6. Translation workflow — files, references, who/when/how (feedback §2)

The user's central question: how does the canon fit with the translation pipeline? Which files exist? How do references work? Who maintains what at which stage?

### 6.1 File inventory after AC-08 is implemented

```
requirements_user_needs/concept_canon/concept_canon.yaml       # canon source
requirements_user_needs/concept_canon/concept_canon.md         # generated rendering

lib/l10n/app_en.arb                                            # English UI strings (existing)
lib/l10n/app_de.arb                                            # German UI strings (existing)
lib/l10n/translation_context/<feature>.yaml                    # AC-08 metadata (new, per feature)
lib/generated/l10n/app_localizations*.dart                     # generated (existing)

scripts/requirements/check_canon.py                            # on-demand audit
scripts/quality/_arb_parser.py                                 # shared parser
scripts/requirements/generate_concept_canon_md.py              # canon → markdown
```

The new file family is `lib/l10n/translation_context/<feature>.yaml` — one per feature, parallel to the ARB files. Each entry references canon concepts by ID:

```yaml
# lib/l10n/translation_context/feat_therapist_transfer_ui.yaml
- key: handoverButtonLabel
  references:
    - CONCEPT-HAND-OVER         # the operation
    - CONCEPT-PLAN              # the object
  surface: PrimaryButton.HandOverDialogContent
  audience: Therapist
  rationale: >
    Initiates the hand-over flow from the plan detail screen.
    "Aushändigen" preserves the physical-personal metaphor (see canon
    CONCEPT-HAND-OVER.rejected_alternatives).
```

Note: the keys (`handoverButtonLabel`) match `.arb` keys exactly. The translation tool joins ARB + translation_context on key.

### 6.2 Who does what at which stage

| Stage | Actor | Action | Verification |
|---|---|---|---|
| **A. Requirements authoring** | LLM via `requ-explore` (existing skill) | When the requirement introduces a user-facing noun/verb/state, invoke `canon-add-concept` (new skill, §8) | The skill's quality check runs `check_canon.py --new-concepts-in <req-folder>` and flags concepts present in the requirement body but missing from the canon |
| **B. UI label authoring** | LLM via the impl task that adds the label to ARB (currently no dedicated skill — usually `code-simple` or `code-complex`) | When creating a new ARB entry, also create the matching `translation_context` entry referencing the canon by ID | `check_canon.py` on-demand audit detects ARB entries without a matching `translation_context` entry, and `translation_context` entries that reference unknown canon IDs |
| **C. Code authoring** | LLM via `code-simple` / `code-complex` | When adding hardcoded user-facing strings (`Text('...')`, `labelText: '...'`), the string must use canonical names OR be in the canon's `forbidden_synonyms` deliberate-exception list | `check_canon.py` walks `lib/features/**/presentation/` |
| **D. Translation (future)** | Translation tool (LLM-driven, REQ-NFUNC-013 §8.2) | Tool receives `{key, de, en, translation_context, canon-entries-referenced}` and produces the target language | The translation tool reads the canon for the referenced concepts; canon entries provide the cross-language guidance the tool needs |
| **E. Verification** | `check_canon.py` plus the linting in `quality-checker` | Audit runs before release; LLM-driven session reviews and fixes drift | Pass/fail signal at audit time |
| **F. Canon evolution** | Person + LLM jointly when user research arrives | Upgrade `provenance.level`, possibly flip canonical names | The discrepancy check surfaces the cascade of references that need updating |

### 6.3 The reference syntax — `CONCEPT-*` IDs, not free text

Each `translation_context` entry's `references` is a list of canon IDs, not free-text mentions. The parallel session's synthesis converged on the same shape; I adopt it here. Three reasons:

1. IDs are mechanically resolvable — the linter follows them without prose-parsing.
2. Refactoring the canonical *name* (e.g., "Plan" → "Programme" after user research) does not break references.
3. The LLM author cannot accidentally write `CONCEPT-HANDOVE` instead of `CONCEPT-HAND-OVER` and have it silently pass — the linter resolves IDs and fails on unknown.

### 6.4 Workflow rules ensuring AC-08's translation_context derives from the canon

The user asked: *"welche Regeln stellen wir an welcher Stelle auf, damit sichergestellt wird, dass die KI tatsächlich auch diesen Abgleich vornimmt?"*

Three layered rules:

1. **Skill-level hint** — the skills that touch user-facing language (`requ-explore`, `code-simple`, `code-complex`, future `add-ui-label` if it exists) carry a single-line reminder: *"User-facing nouns/verbs/states must reference `concept_canon/concept_canon.yaml`. If your work introduces a new one, invoke `canon-add-concept`."* This is the cheapest layer — catches the case where the LLM has the discipline in working memory.
2. **Authoring-time check inside `canon-add-concept`** — the new skill (§8) takes a proposed concept addition, validates it against the schema, checks for duplication / synonym conflicts, and writes the entry. The skill's own quality check is local.
3. **On-demand audit** — `check_canon.py`. Catches everything the first two layers missed.

Rules 1 and 2 are mandatory in their respective skills. Rule 3 is mandatory at release time (added to the release pre-flight script).

---

## 7. Schema (final form for v2)

```yaml
version: 1
concepts:
  - id: CONCEPT-PLAN
    type: object                          # object | state | operation | ui_surface (DEFERRED §10.7)
    name_canonical: "Plan"                # English; primary language per §10.2
    aliases:
      de: "Plan"
      code: "QuestionnairePlan"
      legacy: []
    description: >
      A finalized set of questionnaires assigned by a therapist to a client.
      Once finalized, the plan can be handed over to the client's device.
    states: [Draft, Finalized, HandedOver, Received, Accepted, Declined]
    operations: [HandOver, Receive, Accept, Decline, Save]
    forbidden_synonyms:
      - { term: "Programm", note: "rejected for clinical/institutional tone" }
      - { term: "Form", note: "too generic — obscures structured-questionnaire shape" }
    related: [CONCEPT-CLIENT, CONCEPT-HAND-OVER]
    provenance:
      level: inferred
      sources: []
      validated_at: ""
      notes: ""
    introduced_by: REQ-PROC-049
```

### Field decisions versus v1

| Field | v1 | v2 | Reason |
|---|---|---|---|
| `id` | Implicit via name | Explicit `CONCEPT-<NAME>` | Stable referencing per §6.3 |
| `name_canonical` | Mixed EN/DE | EN per §10.2 | User decision |
| `aliases.de` | Optional | Mandatory if user-visible in German | Bilingual app |
| `aliases.code` | Optional | Mandatory if the concept has a code home | DDD posture per §9 — record divergences explicitly |
| `provenance` | absent | present | Feedback §4 |
| `introduced_by` | absent | present | Audit trail; allows the linter to date-stamp entries |
| `forbidden_synonyms[].applies_to` | present | DROPPED | Premature complexity; can be added back when there's a known case it matters |
| `type: ui_surface` | proposed | DEFERRED per §10.7 | Three plain types until proven insufficient |

---

## 8. Workflow embedding — which skills change, what new skill is added (feedback §8)

v1 said "no new skill, edit YAML directly." That was wrong. It left an unanswered question: who maintains the canon, when, where in the workflow. v2 fills the gap.

### 8.1 What v1 got wrong

v1's reasoning was: "ux-create-flow, ux-write-persona, ux-write-scenario have never been used." That premise is false — the user clarified those skills have been used *extensively*. The skills the user has NOT used yet are the *design-system* and *UI-scribble* ones, which are alpha-phase-deferred by design.

So the "do not add UX-shaped machinery" reasoning collapses for the canon. The canon belongs alongside personas/scenarios/flows in the UX-authoring layer.

### 8.2 New skill: `canon-add-concept`

A small, dedicated skill — modeled after `task-create` (referenced from many other skills). Job:

1. Take a proposed concept name + minimum fields.
2. Validate against schema; check duplicates and forbidden-synonym conflicts.
3. Auto-fill `provenance.level: inferred` if no sources supplied; else `evidenced` with the sources.
4. Write the entry into `concept_canon.yaml`.
5. Regenerate `concept_canon.md` via `generate_concept_canon_md.py`.

The skill's body is small (~30 lines, similar weight to `task-create`'s frontmatter validation). Larger skills reference it by name.

Why a dedicated skill (not inline in `requ-explore`):
- Token weight: `requ-explore` is already large; adding canon-mechanics inline costs tokens on every requirement-authoring session, even when no new concept is introduced.
- Reusability: code-impl skills also need to invoke canon-add-concept when they introduce a hardcoded label. A standalone skill is the DRY point.
- Single point of authority: changes to canon-authoring rules touch one file.

### 8.3 Extensions to existing skills (one line each)

| Skill | Added line (roughly) |
|---|---|
| `requ-explore` | "When the requirement body introduces a user-facing noun, verb, or state that is not in `requirements_user_needs/concept_canon/concept_canon.yaml`, invoke `canon-add-concept` to record it." |
| `ux-create-flow` | Same line, scoped to flow step labels. |
| `ux-write-scenario` | Same line, scoped to scenario step descriptions. |
| `ux-write-persona` | Probably not needed at bootstrap — persona files describe *people*, not product concepts. Revisit if a concept is first surfaced in a persona file. |
| `code-simple` / `code-complex` | "Hardcoded user-facing strings (`Text('...')`, `labelText: '...'`, ARB values) must use canonical names from the canon. If a new concept is introduced, invoke `canon-add-concept` before completing the task." |

Each is one line of skill body — net effect on token weight is small.

### 8.4 Who maintains the canon

| Action | Who | When |
|---|---|---|
| Authoring a new entry | LLM via `canon-add-concept` (invoked by another skill) | Whenever a user-facing concept is introduced |
| Upgrading `provenance.level` | LLM + person jointly | When user research arrives |
| Flipping a canonical name | Person, with LLM cascade-update help | When upgrade decision contradicts inferred choice |
| Deleting a concept | Person | When the product retires the concept; the entry's `legacy` aliases capture historical usage |
| Reviewing distribution / coverage | Person, on demand | Before release; periodic |
| Linting / verification | `check_canon.py` | On demand; mandatory before release |

The person is in the loop for canon-shape decisions (names, validations) but not for routine bookkeeping. The LLM handles bookkeeping under skill guidance.

### 8.5 Embedding into the dev workflow

A typical task that introduces a new user-facing concept (e.g., "we need to surface a 'Reminder' notion in the home screen") now looks like:

1. User invokes `requ-explore` (or `ux-create-flow`, depending on where the concept first surfaces).
2. The skill, while authoring the requirement, sees the word "Reminder" — it's not in the canon. It invokes `canon-add-concept` with `{name: Reminder, sources: [FLOW-007 step 5]}`.
3. `canon-add-concept` validates, writes `CONCEPT-REMINDER` with `provenance.level: evidenced`.
4. The requirement body uses "Reminder" with no further ceremony.
5. Later, a code-impl task adds the UI for it. `code-complex` skill body reminds: "use canonical names." Code uses "Reminder" in `Text('You have a Reminder')`.
6. Later still, the AC-08 implementation adds `translation_context` for the new ARB key, referencing `CONCEPT-REMINDER`.
7. Before release: `check_canon.py` audits; everything resolves.

The user's question — *"wer pflegt die [Dateien]"* — has a concrete answer: LLM via skills, person via approvals at canon-shape decisions, audit via the script.

---

## 9. DDD posture — what enforcement would mean (feedback §10.5)

The user confirmed: code can use different terms; DDD-style alignment is desirable but not forced. They also opened the question of what enforcement would look like.

### 9.1 Current state

`lib/features/therapist/data_transfer/` already partly diverges from user-facing language:
- Code: `DataBeamBloc`, `DataBeamScannerScreen`, `TransferChunk`, `SharePlanTemplateRequested` event
- UI: "Hand Over Plan", "Plan aushändigen"
- Canon (proposed): `CONCEPT-HAND-OVER`

`SharePlanTemplateRequested` is a particularly clear example of intentional divergence (called out by both syntheses) — the BLoC event name doesn't have to match the user-facing label.

### 9.2 Three enforcement postures

| Posture | What it would mean | Implication |
|---|---|---|
| **No enforcement** (recommended) | Code may use any name. Canon's `aliases.code` records intentional divergences. Linter does not enforce code↔canon coherence. | Lowest friction. Matches the user's stated preference. |
| **Light enforcement** | Linter walks `lib/features/**/presentation/` for class names containing canon nouns/operations and confirms they appear in `aliases.code`. Unrecorded divergences flag. | Catches drift without forcing renames. |
| **Strict DDD enforcement** | Code identifier names MUST match canonical names (with project naming conventions: `HandOverBloc`, `HandOverEvent`). Any divergence is a violation. | High friction. Forces refactor of `DataBeamBloc`, `SharePlanTemplateRequested`, etc. Conflicts with the user's confirmed "code can use different terms" position. |

### 9.3 Recommendation

Stay at **no enforcement** for bootstrap. Add the `aliases.code` field to the schema to *acknowledge* divergences (so future contributors / LLM agents are not surprised). Light enforcement could be added later as a separate task if drift becomes noisy. Strict DDD enforcement is rejected — the user explicitly said code can use different terms.

But: record the known divergences in the bootstrap canon, so the audit has them as data:

```yaml
- id: CONCEPT-HAND-OVER
  aliases:
    code:
      - "DataBeamBloc"                  # the BLoC that drives the HandOver flow
      - "SharePlanTemplateRequested"   # legacy event name; predates HandOver naming
      - "DataBeamTransferComplete"     # state class for completion
    legacy:
      - "Share"                          # historical UI term (rejected)
      - "Transmit"                       # never reached UI
```

This satisfies AC-02's "the synonymy is acknowledged at the canon" without forcing code renames.

### 9.4 The DDD enforcement question itself

The user asked: *"was es bedeuten würde, wenn wir Domain-Driven Design Enforcen..."*

Concrete answer:
- The `lib/**/domain/` Clean Architecture domain layer would need to align with canon names. That layer is already English (`QuestionnairePlan`, `Client`).
- The `lib/features/**/presentation/` BLoC, event, state classes would need to align. Refactor cost on the existing transfer feature: ~20 class renames, ~50 file-level renames, ~200 reference updates.
- Linter cost: a Dart-AST walker (not just grep) becomes necessary because identifier names need scope-aware matching.
- Discipline benefit: zero divergence; LLM agents stop ever introducing code names that diverge from canon.

This is a **separate, larger initiative** — appropriate as a future requirement (REQ-PROC-???) once the canon stabilizes. Not in scope here. Just flagged so the user knows the cost shape if they choose to revisit.

---

## 10. Worked example — carry-forward from v1 §6

The worked example (5 `translation_context` entries before/after the canon, ~60% prose reduction, concept-level redundancy concentrated on Plan + Client + Hand-Over descriptions) is unchanged from v1 §6. Reference syntax updated to `CONCEPT-*` IDs per §6.3:

```yaml
- key: handoverButtonLabel
  references: [CONCEPT-HAND-OVER, CONCEPT-PLAN]
  surface: PrimaryButton.HandOverDialogContent
  audience: Therapist
  rationale: >
    Primary action on the handover dialog. "Aushändigen" preserves the
    physical-personal metaphor (see CONCEPT-HAND-OVER.rejected_alternatives).
```

The parallel session's quantification (76% reduction at the entry level, 89% across a projected 100-entry corpus) is consistent with v1's estimate and reflects a more aggressive accounting of which prose belongs to the concept vs. the entry. The exact percentage is not material; both syntheses converge on "the win is concept-level and large."

---

## 11. Bootstrap impl-task sequence (revised)

Each task below targets REQ-PROC-049 as `parent_requirement`, has `target_package: ""` (process tooling).

| # | Task | Type | Effort | Skill | Depends on |
|---|---|---|---|---|---|
| 1 | Create `requirements_user_needs/concept_canon/{README.md, concept_canon.yaml (empty seed)}` and `scripts/requirements/generate_concept_canon_md.py` | impl | S | `claude-write-script` + `task-resolve` | none |
| 2 | Author the bootstrap canon for `feat_therapist_transfer_ui` (~6–10 concepts incl. Plan, Client, Therapist, HandOver, Receive, HandOverDialog) with `provenance.level: inferred` and known `aliases.code` divergences recorded | impl | S | `task-resolve` | 1 |
| 3 | Read `TASK-PROC-046-01`, `-02`, `-12` for `.arb` parser status; create `scripts/quality/_arb_parser.py` if not already proposed, or document the dependency | analyze | S | `task-resolve` | none (can run in parallel with 1 + 2) |
| 4 | Implement `scripts/requirements/check_canon.py` with the four artifact walkers and AC-03 verb check | impl | M | `claude-write-script` | 1, 2, 3 |
| 5 | Add `canon-add-concept` skill (~30-line skill, modeled on `task-create`) | impl | S | `claude-create-skill` | 1 |
| 6 | Extend `requ-explore`, `ux-create-flow`, `ux-write-scenario`, `code-simple`, `code-complex` with the one-line canon hint | impl | S | `claude-modify-skill` (one per skill, may batch) | 5 |
| 7 | Document the workflow embedding in `concept_canon/README.md` and add a one-line entry to `CLAUDE.md` §10 (information map) | impl | S | `task-resolve` | 1–6 |
| 8 | Add `check_canon.py` to the release pre-flight script (`scripts/release/check_release_preconditions.py`) | impl | S | `claude-write-script` | 4 |

The bootstrap canon (Task 2) is hand-authored, not generated. The web research is clear that durability correlates with *executable enforcement* on a small honest canon; harvesting from code (Option D in v1) reproduces drift, and starts the canon downstream of artifacts.

Tasks 1, 3 can run in parallel. Tasks 4, 5 can run in parallel after their prereqs. Task 6 is the cleanup that wires everything together. Task 8 is the on-demand → release-gate hand-off.

---

## 12. Open / deferred decisions (carried + new)

| # | Decision | Status |
|---|---|---|
| §10.1 | Subfolder location | RESOLVED — `requirements_user_needs/concept_canon/` |
| §10.2 | Primary language | RESOLVED — English |
| §10.3 | `lib/core/` scope | RESOLVED — excluded |
| §10.4 | Warn-only duration / gate promotion trigger | DEFERRED |
| §10.5 | DDD enforcement posture | RESOLVED — no enforcement, record divergences in `aliases.code` |
| §10.6 | Inline code marker for synonyms | DEFERRED |
| §10.7 | `type: ui_surface` legitimacy | DEFERRED — three types until proven insufficient |
| NEW-1 | `canon-add-concept` skill — confirm scope before bootstrap impl-task 5 | OPEN |
| NEW-2 | Coordination with paused back-pressure work — confirm `_arb_parser.py` ownership (canon side or G6 side) | OPEN — first action of bootstrap impl-task 3 |
| NEW-3 | DDD enforcement as a future REQ-PROC | DEFERRED — flagged but out of scope |

---

## 13. What remains uncertain

- **The exact pace at which `provenance.level: validated` will become populated** depends on beta-phase user research, which is not scheduled. Bootstrap canon will be ~100% inferred, which is honest but means the canon's epistemic credibility is wholly LLM+app-provider until then.
- **The interaction between canon flips (validated overrides inferred) and the cascade through artifacts** has not been worked out concretely. When user research says "users prefer Programme over Plan," the audit will produce N findings and the LLM must walk them; that workflow is not designed yet. Manageable, but un-rehearsed.
- **Whether `translation_context` files end up under `lib/l10n/translation_context/` or somewhere else** is conjectural — AC-08's implementation task will choose. The canon's interface (`references: [CONCEPT-*]`) is robust to that choice.
- **The shared `_arb_parser.py` ownership** (REQ-PROC-046 G6 side or REQ-PROC-049 side) is open until the coordination review in bootstrap impl-task 3. If both sides build their own, the duplication is small (~50 lines) but worth avoiding.
- **DDD posture stays at "acknowledge, do not enforce."** If the user later wants strict DDD, the canon's `aliases.code` data is already there as the migration starting point — but the cost shape is large (§9.4).

---

## 14. Acceptance criteria check

- [x] **Synthesis updated** to address every feedback point in `2026-05-15_05_feedback.md`.
- [x] **G6 correction** acknowledged (§0); replacement (§5) is on-demand audit, not a new gate.
- [x] **Coordination plan** with paused back-pressure work documented (§3).
- [x] **Term provenance** mechanism designed (§4) with three levels and upgrade path.
- [x] **Translation workflow** detailed: files, references, who/when/how (§6).
- [x] **Workflow embedding** in skills explicit (§8): one new skill, five lines added to existing skills.
- [x] **DDD posture** clarified (§9) with cost shape for future strict-enforcement scenario.
- [x] **Subfolder structure** (§10.1), **English primary** (§10.2), **`lib/core/` excluded** (§10.3) — all adopted.
- [x] **Deferrals** (§10.4, §10.6, §10.7) explicitly carried, not silently dropped.
- [x] **Bootstrap impl-task sequence** revised (§11) with explicit dependencies and coordination steps.
- [x] **Honest about uncertainty** (§13) — five named soft spots.
- [x] **Parallel session findings** folded in (§9.3 known code divergences; §6.3 reference syntax via IDs; quantification cross-validated).
