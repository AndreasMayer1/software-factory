# Opus Synthesis — Canon Form and Discrepancy Check for REQ-PROC-049

Date: 2026-05-14
Model: Opus 4.7 (manual session)
Phase: Phase 2 — synthesis, option-space comparison, recommendation
Companion files:
- `2026-05-14_01_investigation_findings.md` — evidence base
- `2026-05-14_02_web_research_external_knowledge.md` — external prior art

This document is the load-bearing output. A future implementer should be able to start a follow-up `impl` task from this synthesis alone.

---

## 0. Problem reframed in terms not fully known at task creation

Two reframings the investigation surfaced that were not obvious from the goal:

**(a) The duplication-cost clock has not started yet.**
REQ-NFUNC-013 AC-08's `translation_context` field is forward-looking — no entry exists in the repository today. The current `.arb` `description` field is a one-line label hint, not the multi-paragraph context AC-08 calls for. The canon's value therefore accrues at and after AC-08 implementation, not today.

This shifts the bootstrap calculus: there is no large retrofit cost. The canon can be co-introduced with the first feature that adopts the AC-08 schema. The cost balance flips positive *the moment a second feature would otherwise redescribe the same noun/verb/state from scratch*.

**(b) The discrepancy check is genuinely novel territory.**
Web research is unambiguous: no off-the-shelf tool checks the markdown + YAML + Dart triple. Vale handles prose, Spectral handles structured documents, Dart-side checks require custom code. A composite linter that orchestrates three tools is more moving parts than one Python walker. The architectural question is not which tool to adopt — it is how thin the custom check can be while still satisfying AC-05.

The investigation's strongest external signal: **durability correlates with executable enforcement, not artifact richness**. Object maps die after launch; only the lint-enforced glossary file survives. For a solo-developer project with PERSONA-015's longevity constraint, this is the dominant design pressure.

---

## 1. Decision: Canon location and form

### Options compared

| Option | Storage | Pros | Cons |
|---|---|---|---|
| **A** Single hand-authored markdown file | `requirements_user_needs/concept_canon.md` | Maximum simplicity; readable directly; no toolchain | Hard to lint structurally; risks becoming a glossary (downstream of artifacts) rather than canon (upstream); LLM context format unstructured |
| **B** Single YAML file + generated markdown view | `requirements_user_needs/concept_canon.yaml` → `concept_canon.md` | Linter-friendly; LLM-friendly per prior art; humans read rendered markdown; one source of truth; matches existing project pattern (`requirements.md`, `STATUS.md` are generated) | One generated file to keep in sync; needs a tiny generator script |
| **C** Per-concept markdown fragments | `requirements_user_needs/concepts/<name>.md` + index | Locality of edit; per-concept git history; scales to large canons | Overkill at our scale (~30–40 concepts initially); requires an index file anyway; many files to walk for the lint |
| **D** Code-annotated harvest | `@CanonConcept(...)` Dart annotations harvested into canon | Single source for code+canon; physically impossible to drift on code-named concepts | Couples canon to Clean-Architecture domain layer (which REQ-PROC-049 §3 explicitly carves out as separate); not all concepts have a code home (display-only states); fragile across refactor |
| **E** Hybrid YAML+markdown per concept | YAML index + markdown story files | Cheap base, rich where needed | Two artifacts; "when does a concept need its own file" becomes a maintenance question |

### Recommendation: **Option B — Single YAML file with a generated markdown view.**

Justification against PERSONA-015 grounded values:

- **Longevity over velocity**: YAML is mechanically stable; the lint script reads it without parsing markdown ambiguity. Web research shows lint-enforced glossaries outlive richer artifacts.
- **Simplicity as survival strategy**: one source file, one generator, one lint script. The project already operates this pattern for `requirements.md`, `STATUS.md`, and `id_registry.md` — adding `concept_canon.{yaml,md}` is structurally familiar, not a new mechanism.
- **Single-developer maintenance**: per-concept files (Option C) and code annotations (Option D) both create N coordination points where one would do. Option A is simpler still, but loses the executable-enforcement durability signal.

The cost over Option A is one small generator script (~30 lines, modeled on `generate_id_registry.py`). The benefit is mechanical, lintable structure that survives without depending on disciplined human formatting.

### Proposed location

`requirements_user_needs/concept_canon.yaml` — sibling of `personas/`, `user_flows/`, `scenarios/`, `_meta/`.

Rationale: the canon describes the user-facing surface, which is the same conceptual layer as personas/scenarios/flows. Placing it in `requirements_tasks/` would imply it is a per-feature requirement; placing it in `doc/` would imply it is implementation guidance. It is neither — it is upstream of both.

---

## 2. Decision: Schema per concept

### Options compared

| Option | Shape | Pros | Cons |
|---|---|---|---|
| **α** Minimal: name, description, states, operations, aliases-forbidden | ~5 fields per concept | Lowest authoring cost; clearest pass/fail criterion for the lint | May undersupply AC-08 entries — they may still need to redescribe context |
| **β** Rich: minimal + surface, audience, references (file:line), translation notes | ~10 fields per concept | Each `translation_context` entry shrinks to a near-pointer; per-concept usage trace visible | Authoring cost rises sharply; references rot under refactor; risk of becoming a per-concept duplicate of REQ-NFUNC-013 §4 (tone/voice guidance) |
| **γ** Layered: α base + optional rich extension where AC-08 needs it | α minimum, β fields permitted when present | Cheap base, rich where leverage exists | "When does this need extension" is a judgment call; adds inconsistency |

### Recommendation: **Option α, with explicit option to layer in β fields per concept when AC-08 implementation reveals leverage.**

Concrete proposed schema (illustrated against observed `feat_therapist_transfer_ui` concepts):

```yaml
# concept_canon.yaml
version: 1
concepts:
  - name: Plan
    description: >
      A finalized set of questionnaires assigned by a therapist to a client.
      Once finalized, the plan can be handed over to the client's device.
    states:
      - Draft           # under construction by the therapist
      - Finalized       # complete and ready to be handed over
      - HandedOver      # transferred to a client device but not yet accepted
      - Received        # received on the client device (transient)
      - Accepted        # client confirmed receipt
      - Declined        # client refused receipt
    operations:
      - HandOver        # therapist initiates transfer to a client device
      - Receive         # client device captures the transferred plan
      - Accept          # client confirms the received plan
      - Decline         # client refuses the received plan
      - Save            # therapist persists changes to a Draft
    forbidden_synonyms:
      - { term: Transfer, applies_to: operation, prefer: HandOver, note: "Technical register breaks the personal/physical metaphor" }
      - { term: Send,     applies_to: operation, prefer: HandOver }
      - { term: Upload,   applies_to: operation, prefer: HandOver }
    aliases:
      de:   Plan
      code: QuestionnairePlan        # user-visible? no — code-internal name retained
      legacy: []
    notes:
      - "REQ-NFUNC-013 §8.4 example uses 'Hand Out Plan' / 'Plan aushändigen' for HandOver."

  - name: Client
    description: An individual receiving therapeutic services, to whom a therapist may assign Plans.
    states: [Active, Archived]
    operations:
      - Select          # therapist picks a client from the client list
      - Add             # therapist registers a new client
    forbidden_synonyms:
      - { term: Patient, applies_to: noun, prefer: Client, note: "Reserved register; product chooses Client / Klient" }
    aliases:
      de:   Klient
      code: Client

  - name: HandOverDialog
    type: ui_surface     # not a domain noun — a surface where multiple concepts meet
    description: The therapist-initiated dialog that begins the HandOver of a Plan.
    contains_modes: [InPerson, Remote, Test]
    aliases:
      de: HandoverDialog
      code: HandoverDialogContent

  # … etc
```

Key schema choices:

- **`forbidden_synonyms` carries `prefer` and `note`**: the lint outputs an actionable message, not just "rejected." Per Vale's accept/reject pattern but with structured reasoning.
- **`aliases.de` and `aliases.code` are explicit**: the German term and the code-internal class name are *acknowledged synonymies*, not silent ones. AC-02 is satisfied by acknowledgement, not by uniformity.
- **`states` and `operations` are ordered lists, not enums**: they may grow without breaking existing references; ordering communicates lifecycle.
- **`type: ui_surface`** allows the canon to include surface-level concepts like dialogs and tabs (`Vor Ort` / `In Person`) without forcing them into the object/state/operation taxonomy where they don't fit.
- **No state-transition matrix**: that is BLoC territory, not user-facing canon. Adding it would re-import implementation concerns the requirement explicitly carves out.

Authoring cost estimate at first feature (`feat_therapist_transfer_ui`):
- ~6 concepts × ~12 lines = ~70 lines of canon.
- 30 minutes to draft, 15 minutes to review against existing UI strings.

Total canon cost at full product scale (~30–40 concepts): ~400–500 lines of YAML, ~2–3 hours one-time draft, ongoing growth ~1 concept per feature.

---

## 3. Decision: Discrepancy-check architecture

### Options compared

| Option | Shape | Pros | Cons |
|---|---|---|---|
| **I** Single Python script `scripts/requirements/lint_canon.py` | One walker, four artifact handlers, one pass/fail output | Minimum moving parts; matches existing scripts/ patterns; pass/fail per REQ-PROC-046 trivially expressible | Custom-built; we own all the parsing edge cases |
| **II** Three coordinated tools | Vale + Spectral + custom Dart scanner orchestrated by a runner | Reuses two off-the-shelf tools | Three configurations to maintain; failure aggregation is its own glue layer; Vale rules don't cleanly express the canon's structured constraints (forbidden_synonyms with prefer + note) |
| **III** Composite of (II) + LLM agent for semantic checks | Off-the-shelf linters surface candidates, LLM judges semantic equivalence | Could catch synonyms not in `forbidden_synonyms` list | Non-deterministic; bad fit for AC-05's "repeatable pass/fail" requirement |

### Recommendation: **Option I — Single Python script.**

Web research is decisive: **no off-the-shelf tool handles all three artifact types**, so Option II inherits a custom Dart scanner anyway. Once you have a custom component, the marginal cost of unifying everything in one script is negative — the orchestration glue is more code than the script itself.

### Proposed architecture

`scripts/requirements/lint_canon.py` — pseudocode:

```
1. Load concept_canon.yaml → build:
   - canon_terms:     set of canonical names (Plan, Client, …)
   - canon_states:    map concept → set of states
   - canon_ops:       map concept → set of operations
   - forbidden_map:   forbidden_term → {prefer, note, applies_to, parent_concept}
   - alias_map:       (de|code|legacy) → canonical_name

2. Walk artifact types:

   a) Requirements bodies — requirements_tasks/**/requirements.md
      Strip YAML frontmatter. Tokenize prose. For each canonical noun in the canon,
      check that every occurrence is either the canonical form OR an acknowledged
      alias. Flag forbidden_synonyms.

   b) ARB string values — lib/l10n/app_*.arb
      Walk only the *value* of each entry, not the key. Same lookup as (a).
      Per-language: for app_de.arb, use alias_map.de; for app_en.arb, use canonical.

   c) translation_context entries — once REQ-NFUNC-013 AC-08 is implemented,
      whatever its concrete storage is (proposed YAML), walk the description
      field same as (a). Until then this handler is a no-op.

   d) Dart user-facing identifiers — lib/features/**/presentation/
      Heuristic: extract string literals from Text(…), Tooltip(…),
      InputDecoration(labelText: …, hintText: …), AppBar(title: Text(…)).
      Also extract widget class names that surface verbatim to the user
      (e.g. tab labels in hardcoded TabBar lists).
      Same lookup as (a) against forbidden_synonyms.
      Domain-layer Dart (lib/**/domain/) is EXCLUDED per REQ-PROC-049 §3.

3. AC-03 verb-precision check:
   For each generic verb in a curated short list (Edit, Delete, Update, Add, Create,
   Remove, Save, Submit, Send, Open, Close, Cancel, Discard, Complete) — if the
   verb appears in any artifact and is NOT registered as an operation of some
   canon concept, flag it. The canon authoritatively decomposes generic verbs
   into named operations (HandOver, Discard, Complete, Accept, Decline …) —
   any unregistered occurrence is a candidate flattening.

4. Output:
   - One pass/fail exit code (0 = pass, 1 = fail).
   - JSON report at /tmp/lint_canon_report.json with per-violation:
     { artifact_path, line, found_term, prefer, note }.
   - Stderr human-readable summary with file:line refs.

5. CI integration:
   - Phase 1 (bootstrap): warn-only — exit 0 always, log violations.
   - Phase 2 (steady-state): hard fail — exit 1 on any violation.

Phase 1→Phase 2 transition triggered by user, not automatically.
```

This is ~200–300 lines of Python. Manageable for solo maintenance, modeled on existing `scripts/artifacts/generate_id_registry.py` patterns.

---

## 4. Decision: Bootstrap strategy

### Options compared

| Option | Shape | Pros | Cons |
|---|---|---|---|
| **X** Top-down audit | Harvest all artifacts → reverse-engineer canon | Comprehensive | Reproduces drift problem; canon becomes a glossary downstream of artifacts; high one-time effort |
| **Y** Bottom-up per feature | Start with `feat_therapist_transfer_ui`, expand feature-by-feature | Concrete worked example; canon stays small until proven useful | Incomplete coverage during expansion; partial-state lint must be tolerant |
| **Z** Just-in-time | Add canon entries only when new labels are added | Zero retrofit cost | Existing drift (e.g. "Plan empfangen" vs "Plan erhalten") remains undetected indefinitely |

### Recommendation: **Option Y — bottom-up per feature, starting with `feat_therapist_transfer_ui`.**

Reasoning:

- `feat_therapist_transfer_ui` is the most fleshed-out feature area and is exactly the area REQ-NFUNC-013 §8.4 uses as its worked example (`plan_handout_button`). The canon's first concrete contribution is to that documented example.
- Per the strangler-pattern signal from web research, lint runs warn-only during Phase 1 — partial coverage is acceptable because nothing is gated yet.
- The maintenance-vs-duplication cost balance flips positive only with the *second* feature adopting AC-08. Building the canon ahead of that second feature is wasted work; building it concurrently with the first AC-08 feature is the natural moment.

Concrete bootstrap sequence:

1. **Implementation task A (small)**: write `lint_canon.py` as a no-op (loads canon, exits 0). Add it as a CI step in warn-only mode. Cost: ~1 hour.
2. **Implementation task B (medium)**: author the first canon — `feat_therapist_transfer_ui` concepts (~6 concepts, ~70 lines). Generator script for `concept_canon.md`. Cost: ~3 hours.
3. **Implementation task C (medium)**: implement the four artifact walkers in `lint_canon.py`. Run against current repo, document violations as known-debt. Cost: ~4 hours.
4. **Implementation task D (small)**: AC-03 verb-decomposition check. Cost: ~1 hour.
5. **Concurrent**: REQ-NFUNC-013 AC-08 implementation co-references the canon for the first feature area. The worked-example transformation in §6 below is performed as part of that task.
6. **Per future feature**: extending the canon becomes a step in feature implementation, not a separate task.
7. **Phase 2 transition** (later, user-triggered): flip the lint to hard-fail. Coincides with REQ-PROC-046 G6 integration (see §5).

---

## 5. REQ-PROC-046 integration: G6 gate or separate process gate?

REQ-PROC-046 defines binary pass/fail back-pressure gates G1–G5 for code quality. AC-05 names a similar pass/fail signal.

### Options

- **G6 gate** alongside G1–G5: `lint_canon.py` runs after code quality checks; failure blocks the same way G1–G5 do.
- **Separate process gate**: runs in a different CI lane (e.g. pre-merge linting), not coupled to code-quality gates.
- **Both**: G6 in code-quality lane *for code-touching changes*, separate lane *for requirements-only changes*.

### Recommendation: **G6 alongside G1–G5, with the warn-only bootstrap phase explicitly recorded in REQ-PROC-046.**

Reasoning:
- AC-05 already names "the back-pressure pattern established by REQ-PROC-046" (REQ-PROC-049 Developer Guidelines §6) — making it a sibling gate honours that explicit alignment.
- Requirements-only changes (no `lib/` touch) still affect the canon — those changes are exactly where new concepts get introduced, so excluding them creates an enforcement gap.
- Two CI lanes is two configurations to maintain. PERSONA-015 simplicity argument wins.
- The bootstrap phase (warn-only) is a feature of G6's introduction, not a separate gate. When `lint_canon.py` flips to hard-fail, G6 becomes binding without changing the gate's identity.

What the LLM agent sees when G6 fails:

```
G6 (concept canon coherence) — FAIL
  artifact: lib/features/therapist/data_transfer/presentation/widgets/in_person_tab_content.dart:178
  found:    Discard Transfer
  prefer:   Discard HandOver
  note:     "Transfer" breaks the personal/physical metaphor used by HandOver.
            Either rename to "Discard HandOver", or register "Transfer" as an
            acknowledged synonym of HandOver in concept_canon.yaml.

  artifact: lib/features/client/data_receive/presentation/screens/plan_receipt_confirm_screen.dart:28
  found:    Plan erhalten
  prefer:   Plan empfangen  (canonical DE alias for Receive)
  note:     Use one DE term per canon operation. If the post-scan phase needs a
            distinct user-facing label, decompose Receive into RecordReceipt
            (active) + ConfirmReceipt (post-scan) at the canon and update both
            screen titles accordingly.
```

This is actionable — the LLM agent has a deterministic next move per violation.

---

## 6. Worked example: `translation_context` before vs after the canon

Feature area: `feat_therapist_transfer_ui` (HandOver dialog).

### Before the canon — five entries drafted by hand

Each entry redescribes Plan, Therapist, Client, and HandOver from scratch.

```yaml
- key: handover_dialog_title
  de: "Plan aushändigen"
  en: "Hand Over Plan"
  translation_context: >
    Shown to the therapist as the title of a modal dialog that begins
    the process of transferring a finalized plan to the client's device.
    A "Plan" is a set of questionnaires the therapist has assigned to a
    "Klient" (Client) — an individual receiving therapeutic services.
    The dialog opens after the therapist taps the "Plan aushändigen" button
    on the plan detail screen. "Aushändigen" evokes a physical, personal
    hand-over (as in handing a document to someone), which matches the
    therapeutic relationship. Avoid technical-register translations.
    DialogContent.

- key: tab_label_vor_ort
  de: "Vor Ort"
  en: "In Person"
  translation_context: >
    Tab label inside the "Plan aushändigen" dialog. The dialog presents
    the therapist with three modes for handing over a plan: in-person
    QR transfer, remote transfer (future), and test mode. "Vor Ort" is
    the in-person mode where the therapist and client are physically
    co-located and the plan is transferred via QR-code scanning from the
    therapist's device to the client's device. A "Klient" is an individual
    receiving therapeutic services. TabLabel within DialogContent.

- key: discard_transfer_button
  de: "Übertragung verwerfen"   # hypothetical — currently hardcoded EN only
  en: "Discard Transfer"
  translation_context: >
    Secondary button on the in-person transfer screen inside the "Plan
    aushändigen" dialog. Tapping this button cancels the in-progress
    transfer of the plan to the client's device. A "Plan" is a finalized
    set of questionnaires the therapist has assigned to a "Klient" — an
    individual receiving therapeutic services. The transfer is mid-flight
    when this button appears. "Verwerfen" is non-blaming language —
    abandoning the attempt is normal and not a failure.
    SecondaryButton.

- key: complete_transfer_button
  de: "Übertragung abschließen"
  en: "Complete Transfer"
  translation_context: >
    Primary button on the in-person transfer screen inside the "Plan
    aushändigen" dialog. The therapist taps this button to explicitly
    end the QR-stream transfer of the plan to the client's device after
    confirming visually that the client has captured the sequence. A
    "Plan" is a finalized set of questionnaires the therapist has assigned
    to a "Klient" — an individual receiving therapeutic services.
    PrimaryButton.

- key: client_name_label
  de: "Name des Klienten"
  en: "Client Name"
  translation_context: >
    Form-field label for entering the name of the client to whom the
    plan is being handed over. A "Klient" is an individual receiving
    therapeutic services from the therapist. This name is used only to
    label the transfer locally — no client identifier is persisted across
    the handover. FormFieldLabel.
```

**Pre-canon line count**: ~50 lines of `translation_context` prose across five entries. Of that, ~25 lines redescribe Plan, Klient/Client, the relationship between them, and the personal-hand-over metaphor — repeated four to five times.

### After the canon

Each entry references concepts by canonical name and adds only label-specific context.

```yaml
- key: handover_dialog_title
  de: "Plan aushändigen"
  en: "Hand Over Plan"
  translation_context: >
    @canon:HandOver → @canon:Plan
    Surface: DialogTitle of the HandOverDialog.
    Audience: Therapist.
    Rationale: Personal-hand-over metaphor (see @canon:HandOver.notes).

- key: tab_label_vor_ort
  de: "Vor Ort"
  en: "In Person"
  translation_context: >
    @canon:HandOverDialog.modes.InPerson
    Surface: TabLabel within HandOverDialog.
    Audience: Therapist.
    Rationale: In-person mode = co-located QR transfer. Tab label
    must read as a *mode name*, not an action.

- key: discard_transfer_button
  de: "HandOver verwerfen"        # canonical form
  en: "Discard HandOver"
  translation_context: >
    @canon:HandOver.operations.Discard
    Surface: SecondaryButton on the InPerson sub-screen.
    Audience: Therapist (mid-flight).
    Rationale: Non-blaming — abandoning the attempt is normal.

- key: complete_transfer_button
  de: "HandOver abschließen"
  en: "Complete HandOver"
  translation_context: >
    @canon:HandOver.operations.Complete
    Surface: PrimaryButton on the InPerson sub-screen.
    Audience: Therapist (after visual confirmation of client capture).

- key: client_name_label
  de: "Name des Klienten"
  en: "Client Name"
  translation_context: >
    @canon:Client.name
    Surface: FormFieldLabel.
    Audience: Therapist (before HandOver starts).
    Rationale: Name is local-only to the HandOver context — not persisted.
```

**Post-canon line count**: ~20 lines of `translation_context` prose across five entries. **Reduction: ~60%.**

Where duplication concentrates pre-canon (and what disappears post-canon):

| Repeated concept | Pre-canon repeats | Post-canon |
|---|---|---|
| "Plan is a finalized set of questionnaires" | 4× | 0× (lives at @canon:Plan.description) |
| "Klient is an individual receiving therapeutic services" | 4× | 0× (lives at @canon:Client.description) |
| "Aushändigen evokes a physical hand-over" | 1× (full), 3× (implicit) | 1× (lives at @canon:HandOver.notes) |
| Label-specific context (surface, audience, rationale) | 5× | 5× (irreducible — this is what stays) |

**The reduction is concept-level, not label-level.** Label-specific context cannot and should not be removed — it is precisely what `translation_context` exists for. The win is removing the redundant per-entry redescription of nouns/verbs/states.

### Discrepancies the canon would catch on this feature today

1. Hardcoded `'Discard Transfer'` and `'Complete Transfer'` (lines 178, 189 of `in_person_tab_content.dart`) — `Transfer` is a forbidden synonym of `HandOver`. **G6 FAIL**, with the rewrite "Discard HandOver" / "Complete HandOver" suggested.
2. Client-side "Plan empfangen" (scanner title) vs "Plan erhalten" (receipt confirm title) — two DE forms for one canon operation. **G6 FAIL**, suggesting either canonical alignment to one form, or decomposition into RecordReceipt + ConfirmReceipt at the canon.
3. EN cluster "Receive Plan" / "Receive Data" / "Plan empfangen" — three forms for Receive. **G6 FAIL**, suggesting canonical alignment to "Receive Plan" + alias entries for the historical forms.

These are real, in the codebase, today.

---

## 7. Maintenance cost vs. duplication cost balance

### Maintenance cost of the canon

| Item | One-time | Recurring |
|---|---|---|
| `concept_canon.yaml` initial author (1 feature) | ~3 hours | ~30 min per new feature |
| `lint_canon.py` (initial + 4 walkers + verb check) | ~6 hours | rare maintenance |
| `generate_concept_canon_md.py` | ~1 hour | rare maintenance |
| CI integration (G6 gate) | ~30 min | rare maintenance |
| **Total bootstrap** | **~10–11 hours** | **~30 min per new feature** |

### Duplication cost without the canon

Estimating at full product scale:
- ~200–400 `translation_context` entries when AC-08 is fully implemented.
- Per-entry redescription cost: ~3–5 lines of redundant prose for shared concepts.
- Lower bound: 200 × 3 = 600 lines of duplicated description.
- Upper bound: 400 × 5 = 2000 lines.

### Where the balance flips

Crossover point: the moment the *second* feature would otherwise redescribe a shared concept. At ~5–10 shared concepts × 2 features = ~10–20 entries of duplication, the per-feature canon authoring cost (~30 min) is recovered, and every subsequent feature reduces total prose.

**The cost balance is already positive once a single shared concept (e.g. Plan, Client, HandOver) is used across two features.** This is true for `feat_therapist_transfer_ui` and `feat_client_receive_data` *today* — Plan and HandOver concepts span both.

Hidden gain beyond line-count: translation consistency, drift detection, and the LLM agent's ability to query the canon as authoritative context when authoring new `translation_context` entries. These are not directly measurable in lines but compound over time.

---

## 8. Relationship to existing UX infrastructure

The user explicitly flagged that `ux-create-flow`, `ux-write-persona`, `ux-write-scenario` exist but have never been used in practice. The canon should not become a fourth under-used UX-shaped artifact.

### Posture taken in this synthesis

The canon **sits adjacent to**, but does not consume or extend, the existing UX skills. Specifically:

- It does not require a new authoring skill at bootstrap time. Direct YAML editing — guided by a worked schema — is sufficient. A skill can be added later if and only if the pattern stabilizes.
- It does not duplicate persona or scenario content. Personas describe *who*; scenarios describe *situations*; flows describe *paths*; the canon describes *the things, states, and operations those flows act on*. The four artifact types describe a complete cross-section.
- The canon is *referenced from* personas/scenarios/flows where they introduce a new concept (e.g. when a flow first mentions HandOver, it can reference @canon:HandOver). Bidirectional links are added incrementally, not retrofitted.

### Decision: do not create a `canon-add-concept` skill at bootstrap.

Rationale: the user's explicit feedback notes that adding more UX skill machinery without proven need is risky. The pattern of editing YAML directly is well-understood across the team (single developer); a skill becomes warranted only if the editing pattern reveals enough complexity to justify the abstraction. For now, the cost of a skill exceeds its value.

---

## 9. What the layers-skills framework gets right and wrong here

The `/layers-conceptual-model` skill (Sophia Prater OOUX, Daniel Rosenberg semantic IxD) inspired this requirement. Where its prescription continues to apply, and where it stops:

**What translates:**
- The object/state/operation taxonomy is durable and applies cleanly. The canon schema's `name`, `states`, `operations` fields are direct lifts.
- The verb-precision discipline (synonym drift + semantic flattening tests) translates verbatim. AC-03 is precisely the layers-skills "ubiquitous language check."
- The framing of *upstream-of-artifacts* (the canon is the source, artifacts derive from it) translates and is the requirement's core stance.

**What does not translate:**
- The framework's output format (Mermaid object maps + state diagrams + markdown narrative) is **designer-facing**. Our consumers are also LLM tooling and Dart code. A markdown narrative is not a queryable canon. Hence YAML.
- The framework's delivery model (workshop → artifact → handoff) assumes a multi-disciplinary team and a delivery phase. Solo developer with long-term maintenance constraints needs an artifact that survives without ceremony — hence executable enforcement, not workshop facilitation.
- The framework treats the conceptual model as a complete deliverable. Bottom-up per-feature bootstrap diverges from this — the canon is incomplete until the product is, and that is fine.

**Net**: the framework supplies the discipline (object/state/operation precision, verb-decomposition) but not the artifact format. Take the discipline, reject the format.

---

## 10. Open decisions requiring user input

These cannot be resolved by exploration alone. The follow-up `impl` task should not start until they are answered.

1. **Canon location confirmation.** Proposed: `requirements_user_needs/concept_canon.yaml` + generated `concept_canon.md`. Acceptable, or different?

2. **Language scope.** Proposed: the canon stores English canonical names, and `aliases.de` (and any future locale) records the corresponding term. The lint walks both `.arb` files using the alias map. **Question**: is English the canon's "primary" language, or should the canon be locale-agnostic with both DE and EN as equal aliases of an abstract concept name (e.g. `HandOver` is the concept, `Hand Out` / `aushändigen` are both aliases)?

3. **Scope of code-side check.** Proposed: lint only `lib/features/**/presentation/` Dart files, excluding `lib/**/domain/` per REQ-PROC-049 §3. **Question**: include or exclude `lib/core/presentation/`? It contains shared user-facing widgets but is structurally distinct from feature presentation.

4. **Bootstrap-phase warn-only duration.** Proposed: stays warn-only until the user explicitly flips to hard-fail (no automatic transition). **Question**: is there a target trigger event? E.g. "flip when first AC-08 feature lands" or "flip when canon covers ≥ 50% of features"?

5. **Forbidden-synonym ergonomics.** Some terms (e.g. "Transfer" as forbidden synonym of HandOver) appear frequently in code as legitimate technical names (`TransferChunk`, `DataBeamTransferComplete`). **Question**: does the lint distinguish user-facing strings from code identifier names, with code-internal `Transfer` allowed but user-facing string `'Discard Transfer'` rejected? Proposed yes — that is the heuristic in §3 — but worth explicit user sign-off.

6. **Acknowledged-synonym annotation in code.** When a code identifier intentionally diverges (e.g. `DataBeamBloc` is the code name for what the user sees as the HandOver flow), the canon's `aliases.code` records that. **Question**: does the lint require an inline marker in code (`// canon-alias: DataBeam → HandOver`) to validate the divergence, or is the canon's `aliases.code` field alone authoritative? Proposed: canon-only — the inline marker is duplication PERSONA-015 would resent.

7. **`type: ui_surface` legitimacy.** The proposed schema introduces a `type` field that distinguishes domain concepts (Plan, Client) from UI surfaces (HandOverDialog, tab labels). **Question**: is "ui_surface" too implementation-shaped for a canon that is meant to be upstream of UI? Alternative: drop `type`, treat all entries uniformly, accept that some concepts have empty `states`/`operations`.

---

## 11. What remains uncertain

- **AC-08 entry shape is not finalized.** REQ-NFUNC-013 §8.4 specifies the conceptual fields but not the concrete storage. The worked example in §6 assumes a YAML form parallel to ARB, but the actual implementation could use ARB `description` extended, a separate sidecar file, or a generated artifact. The canon's interface to AC-08 is robust to all three (it just walks whatever field carries the description), but exact integration syntax (`@canon:HandOver → @canon:Plan`) is a proposal, not a settled convention.
- **AC-03 verb-precision check false-positive rate is unknown** until the lint runs against the full repository. The curated short list of generic verbs is a starting point; tuning is empirical.
- **Translation tooling's behaviour with `@canon:...` references is unverified.** If translators use a tool that strips comments or references, the post-canon translation_context entries lose their reference power. Worth a small spike before committing to that syntax.
- **The cost balance estimate is back-of-envelope.** First-feature bootstrap will produce the real number. The synthesis treats the estimate as directionally correct, not precise.
- **`lib/core/presentation/` scope question (#3 above)** is genuinely open — could go either way pending user judgment.

---

## 12. Sizing the follow-up implementation tasks

Based on §4's sequence, the follow-up tasks would be:

| Task | Type | Effort | Skill | Notes |
|---|---|---|---|---|
| Write canon YAML for `feat_therapist_transfer_ui` (6 concepts) | impl (process artifact) | S | `task-resolve` | Authoring; not code |
| Write `generate_concept_canon_md.py` | impl (script) | S | `claude-write-script` | ~30-line generator |
| Write `lint_canon.py` skeleton (load canon, no walkers, exit 0) | impl (script) | S | `claude-write-script` | CI-wires the warn-only gate |
| Implement four artifact walkers in `lint_canon.py` | impl (script) | M | `claude-write-script` | Most substantive task |
| Implement AC-03 verb-precision check | impl (script) | S | `claude-write-script` | Extends `lint_canon.py` |
| Integrate G6 into REQ-PROC-046 documentation | impl (process) | S | `task-resolve` | Documentation only |

All tasks have `target_package: ""` (process tooling, unassigned). All sit under `parent_requirement: REQ-PROC-049`. None of them require Opus.

---

## 13. Acceptance criteria check (from goal.md)

- [x] At least one Opus synthesis round — this document.
- [x] Synthesis defines problem space in terms not fully known at task creation — §0 reframes (duplication clock not started; cross-artifact check is novel territory).
- [x] At least two viable options compared for each major decision — §1 (5 options), §2 (3 options), §3 (3 options), §4 (3 options), §5 (3 options).
- [x] Recommendations justified against PERSONA-015 grounded values — explicit in each §.
- [x] Concrete worked example showing translation_context before/after, with duplication reduction estimated — §6, ~60% reduction.
- [x] Decisions requiring user input identified and framed clearly — §10 (7 decisions).
- [x] Output honest about what remains uncertain — §11.
- [x] Sized for follow-up implementation — §12.
