# Opus Synthesis v3 — Multi-language Provenance, Skill Family, Cascade Integration

Date: 2026-05-15
Model: Opus 4.7
Inputs:
- v2 synthesis (`2026-05-15_06_opus_synthesis_v2.md`) — base
- User feedback v2 (`2026-05-15_07_feedback.md`) — drives this iteration
- `.claude/skills/product-intake/skill.md` — cascade-mechanic reference
- `.claude/skills/claude-create-skill/skill.md` — naming convention reference

v3 supersedes v2 in the sections marked **CHANGED** below; confirmed v2 sections carry through unchanged.

---

## 0. What changed from v2 to v3

| Topic | v2 position | v3 position | Driver |
|---|---|---|---|
| Provenance levels | 3 levels (inferred / evidenced / validated) | **4 levels** with `proto-evidenced` inserted | User §4 — most existing personas/scenarios/flows are proto-personas themselves |
| Provenance scope | Single block per concept | **Per-language block** (de / en / ...) | User §4 — evidence is language-specific |
| `sources` field | Free-text strings | **Structured IDs** (`PERSONA-*`, `SCEN-*`, `FLOW-*`, `REQ-*` with optional anchor) | User §7 — machine-readable references |
| Skill name | `canon-add-concept` | **`ux-write-canon-concept`** (verb per project convention) or **`ux-modify-canon-concept`** per user's explicit proposal — both viable, recommendation below | User §8 — UX prefix, covers both add + update |
| Skill scope | Add only | **Add + modify** (single skill, per ux-write-persona / ux-write-scenario pattern) | User §8 — single skill mirrors existing UX skill pattern |
| Scenario skill integration | Always invoke on new concept | **Conditional**: only for *future*-app-usage scenarios, NOT for *as-is* (pre-app) scenarios | User §8 — two scenario types, only one needs canon |
| Persona skill integration | Possibly extend | **Not extended** — personas describe people, not product concepts | User §8 |
| Cascade integration | Not designed | **product-intake gets a Canon step**; canon cascades into UI labels when names change | User §8 + §6 |
| UI-scribble skill integration | Not addressed | **Add canon hint** to scribble skills — labels in scribbles flow downstream | User §6 |
| Translation mechanism | "future AC-08 task" | **Concrete task to spawn** if needed for DE/EN now, else deferred until 3rd language | User §6 — I propose deferral; awaiting confirmation |
| Label-rename cascade | Not designed | **`ux-rename-concept-cascade`** (proposed) or fold into `ux-modify-canon-concept` | User §6 — research updates can flip names, which cascades to ARB + translation_context + code |
| DDD enforcement | "no enforcement" | **Light enforcement via skill instructions** (no linter); `code-simple` / `code-complex` extended | User §9 |
| File splitting | Single file (`concept_canon.yaml`) | **Single file confirmed for bootstrap**; revisit if it grows past ~150 concepts | User §6 — analysis below |
| Check-script location | `scripts/requirements/check_canon.py` | **`scripts/user_needs/check_canon.py`** | User §5 — canon lives in user_needs; this is also where the script's domain lives |
| LLM interpretation step | Implicit | **Explicit**: script produces candidates; LLM session reviews and decides whether each is real drift or acknowledged synonymy | User §5 — pure pattern match isn't enough |

Confirmed unchanged from v2: Subfolder location, English primary, `lib/core/` excluded, on-demand audit not gate, schema field set (with the additions in §4 below), bootstrap impl-task sequencing.

---

## 1. Multi-language provenance — language is the primary axis (user §4)

### 1.1 Why language is its own axis

The user's point: "Plan" being chosen for English does not imply "Plan" is chosen for German, and *certainly* doesn't imply "Plan" is right for Arabic. Each language has its own user research, its own market context, its own register. The target market is currently German; German evidence will accumulate first, English alongside, other languages much later.

Implication: the canon's provenance is per-language, not per-concept.

### 1.2 Four provenance levels (CHANGED from 3)

| Level | Meaning | Trigger to upgrade |
|---|---|---|
| **inferred** | LLM + app-provider judgement only. No user-needs artefact references the term, or the term is novel. | Adding a source-artefact reference |
| **proto-evidenced** | Derived from a persona / scenario / flow / requirement that *itself* has not been validated with users. The user-needs artefact is itself a proto-artefact (LLM-authored, app-provider-reviewed). | The source artefact upgrades its own evidence level, or direct user data arrives |
| **evidenced** | Derived from a user-needs artefact that *has* been validated (interview, beta feedback documented in the artefact). | Direct user research on the term itself |
| **validated** | The term itself was tested with users (card sort, A/B, comprehension test). | None — this is the ceiling |

**`proto-evidenced` is new in v3** and addresses the gap the user flagged: most of the current personas/scenarios/flows are themselves proto-artefacts. v2's binary "inferred vs evidenced" let those propagate as full evidence, which would have overstated the canon's credibility.

Source-artefact evidence levels are already tracked in `requirements_user_needs/` artefacts (per REQ-PROC-050 / the SOUNDNESS_REVIEW_CHECKLIST). The canon entry's `evidence_level` derives from its source artefacts' levels: if all referenced sources are themselves proto-evidenced, the canon entry is proto-evidenced; if a referenced source is validated, the canon entry can be evidenced.

### 1.3 Schema — per-language provenance blocks

```yaml
- id: CONCEPT-PLAN
  type: object
  name_canonical: "Plan"          # English; primary language
  aliases:
    de: "Plan"
    code: "QuestionnairePlan"
    legacy: []
  description: >
    A finalized set of questionnaires assigned by a therapist to a client.
  states: [Draft, Finalized, HandedOver, Received, Accepted, Declined]
  operations: [HandOver, Receive, Accept, Decline, Save]
  forbidden_synonyms:
    - { term: "Programm", lang: "de", note: "rejected for clinical/institutional tone" }
  related: [CONCEPT-CLIENT, CONCEPT-HAND-OVER]
  provenance:
    en:
      level: inferred
      sources: []
      validated_at: ""
      notes: ""
    de:
      level: proto-evidenced
      sources:
        - { id: SCEN-001-03,   anchor: "#step-2"  }
        - { id: FLOW-007,      anchor: "#step-5"  }
        - { id: REQ-FUNC-007,  anchor: "#ac-01"   }
      validated_at: ""
      notes: >
        Source artefacts are themselves proto-evidenced (LLM-authored,
        app-provider-reviewed; no user interview yet).
  introduced_by: REQ-PROC-049
  status: active                  # active | archived
```

`forbidden_synonyms` also carries `lang:` — a German user term may be forbidden for register reasons that don't apply to the English term.

### 1.4 What the audit reports per-language

```
Canon coverage: 28 concepts
  en:
    inferred:        24
    proto-evidenced:  3
    evidenced:        1
    validated:        0
  de:
    inferred:        18
    proto-evidenced:  9
    evidenced:        1
    validated:        0
```

This separation makes the German-first reality visible. As beta-phase user research accumulates, DE evidence rises while EN stays largely inferred — that's the honest picture.

---

## 2. Sources as structured IDs (user §7)

### 2.1 Replace free text with IDs everywhere possible

Every place v2 used free-text references, v3 uses structured IDs:

| Field | v2 (free text) | v3 (structured) |
|---|---|---|
| `provenance.sources` | `"PERSONA-015 scenarios.md mentions ..."` | `{ id: PERSONA-015, anchor: "#values" }` |
| `notes` (in concept) | free text | free text PERMITTED but: prefer IDs where applicable |
| `forbidden_synonyms[].note` | free text rationale | free text PERMITTED + optional `evidence: [{id: SCEN-XXX}]` |
| `related` | `[CONCEPT-PLAN, CONCEPT-CLIENT]` | unchanged — already IDs |
| `aliases.code` | string list | `[{ identifier: "DataBeamBloc", artefact: "lib/features/.../bloc.dart", reason: "" }]` — optional structure |

### 2.2 Anchor syntax for in-document position

Anchor formats per artefact type:

| Artefact type | Anchor format | Example |
|---|---|---|
| Persona file | `#values`, `#traits`, `#no-go-rules`, ... | `#values` |
| Scenario file | `#step-N` for step-numbered steps; `#section-N` for §headings | `#step-2` |
| Flow file | `#step-N` | `#step-5` |
| Requirement | `#ac-NN`, `#sec-N.M`, `#purpose` | `#ac-01` |
| Code file | `lib/.../file.dart:LINE` | `lib/features/.../bloc.dart:42` |

For ARB / `translation_context` files (when AC-08 lands), reference by `key`: `{ key: handoverButtonLabel, lang: de }`.

### 2.3 Where this gets enforced

`scripts/user_needs/check_canon.py --validate-references` resolves every `sources[].id` against the registries (`requirements_user_needs/_meta/id_registry.md`, `requirements_tasks/_meta/id_registry.md`). Unknown IDs fail. Anchors are linted only as well-formed strings (loose check) at bootstrap; tight anchor validation deferred.

### 2.4 Other free-text spots reviewed

I scanned v2's schema for remaining free text:

- `description` — stays free text. It's prose-for-humans.
- `notes` fields — stay free text. Notes are the rationale, not the link.
- `validated_at` — ISO date (already structured).
- `forbidden_synonyms[].note` — stays free text but can carry an optional `evidence:` array of IDs.

The principle: **anywhere a reference would be more useful than prose, use a reference; keep prose only for the rationale**.

---

## 3. Discrepancy-check architecture refinements (user §5)

### 3.1 Location: move to `scripts/user_needs/` (CHANGED)

The user is right that script location should match domain. The canon source lives in `requirements_user_needs/concept_canon/`; the script that audits canonical-name usage is most naturally a user-needs concern. v3 places it at:

```
scripts/user_needs/check_canon.py
scripts/user_needs/generate_concept_canon_md.py
```

The fact that the script *also walks `requirements_tasks/` and `lib/`* doesn't change its primary domain — those are downstream artefacts the canon governs. By comparison `scripts/requirements/coverage_report.py` walks across both areas but is named for its primary domain.

`scripts/quality/_arb_parser.py` (the shared parser with G6 linguistic-complexity) stays under `scripts/quality/` — it's a shared util both sides import.

### 3.2 Python script + LLM interpretation — explicit two-stage flow (user §5)

The user's concern: a Python script can only match strings; it can't decide whether a found mismatch is real drift, intentional synonymy, or false-positive context. Only an LLM can. So **the check_canon.py output is structured candidates, and the LLM session that ran it does the disposition step**.

Concrete flow:

```
[1] LLM session invokes:
    $ python3 scripts/user_needs/check_canon.py --json > report.json

[2] check_canon.py produces report.json:
    {
      "summary": { "candidates": 12, "files": 5 },
      "candidates": [
        {
          "id": "C-001",
          "artefact": "lib/features/.../in_person_tab_content.dart",
          "line": 178,
          "found_term": "Discard Transfer",
          "matched_rule": "forbidden_synonym",
          "prefer": "Discard HandOver",
          "canon_concept": "CONCEPT-HAND-OVER",
          "note": "Transfer breaks the personal/physical metaphor.",
          "context_snippet": "child: const Text('Discard Transfer'),"
        },
        ...
      ]
    }

[3] LLM reads the JSON, for each candidate decides:
    - real drift -> fix in place (or queue fix as a task)
    - acknowledged synonymy -> add to canon's `aliases.code` / `forbidden_synonyms.allow`
    - false positive (e.g. matched inside a comment or code-internal context) -> add an
      exclusion line to the script's config

[4] LLM re-runs the script -> ideally exit 0.
```

The script's job ends at "produce candidates"; disposition is an LLM concern. This makes pure pattern-matching adequate.

### 3.3 What happens if this becomes a gate later

The user asked: "wenn wir das später zu einem Gate machen, dann wird es ja nicht mehr so einfach funktionieren, oder?"

Right — gates run automatically with no LLM session present. Two responses:

1. **The script's pass criterion becomes stricter at gate-promotion time.** Pre-gate, candidates need LLM disposition. As-gate, candidates either are auto-resolved (look up in the canon's `aliases.code` / allowed-synonym lists which by then must be comprehensive) or fail.
2. **The disposition workflow stays available** — when a gate failure occurs in a per-change task, that task's LLM session runs the same disposition step and either fixes the code or adds the allowed-synonym to the canon (and explicitly justifies it).

In short: the gate promotion moves the disposition from "every audit run" to "only when a gate fails." The script doesn't need a complete rewrite, but its data files (`aliases.code`, allowed-synonyms) need to be much more complete at gate-promotion time. This is in line with the deferred §10.4 decision.

---

## 4. UI-scribble skills (user §6 — new lacuna)

The user flagged a real gap: UI-scribble skills (`ui-create-scribble`, `ui-create-scribble-improve`) generate HTML wireframes that include button labels and other text. These labels can be carried into Flutter implementation 1:1 — meaning canonical-name violations get baked in *before* code is written.

### 4.1 Extension to scribble skills

The scribble skills must:

1. **Before generating** any label-bearing element (button, tab, form label, section heading): read `concept_canon/concept_canon.yaml` and use canonical names where the concept exists.
2. **When generating a label for a concept that does not exist in the canon**: invoke `ux-write-canon-concept` (the new skill, §5) to add it, with `provenance.level: inferred` (or `proto-evidenced` if the scribble derives from a flow/scenario that referenced the concept).
3. **In the scribble's output** (HTML), mark each canonical-name-derived label with an HTML comment containing the canon ID:
   ```html
   <!-- canon: CONCEPT-HAND-OVER -->
   <button>Plan aushändigen</button>
   ```
   This is for downstream Flutter implementation: the impl skill reads the canon ID and knows the label is canonical.

### 4.2 Why this matters before AC-08

Scribbles → Flutter → ARB → translation_context. If scribbles use non-canonical terms, they propagate three steps before the canon catches them. Catching at scribble-time is the cheapest fix.

### 4.3 Update for `ui-improve-flutter`, `ui-verify-flutter`

`ui-verify-flutter` already verifies scribble→Flutter conformance. It should also verify that canonical-name comments in the scribble correspond to canonical-name strings in the Dart code.

---

## 5. Skill family — final naming and scoping (user §8)

### 5.1 Single skill, name decision

The user proposed `ux-modify-canon-concept`. Checking `claude-create-skill` naming conventions: `ux-` prefix is correct; verbs in active use are `create`, `write`, `update`, `approve`, `complete`, `draft`, `validate`. "modify" is not in the list. The existing UX skills that handle both create + update use the verb `write` (e.g. `ux-write-persona`, `ux-write-scenario`) or `create` (e.g. `ux-create-flow`).

Two viable names:
- **Recommended: `ux-write-canon-concept`** — mirrors `ux-write-persona` / `ux-write-scenario`, both of which create-or-update existing artefacts. Lowest cognitive load.
- Alternative: `ux-modify-canon-concept` — the user's proposal. Distinguishes "modify-not-create" but breaks the existing UX-skill verb pattern.

Going forward I'll use `ux-write-canon-concept` and note the alternative — but it's a small naming call; either works.

### 5.2 Scope (covers add + modify + provenance-upgrade + rename)

The skill handles four operations on canon entries:

| Operation | Trigger | What the skill does |
|---|---|---|
| **Add new concept** | Calling skill encountered a user-facing concept not in canon | Validate uniqueness, fill provenance (inferred or proto-evidenced from caller's context), write entry, regenerate `concept_canon.md` |
| **Update fields** | E.g. adding a new state, a new alias, a new related concept | Edit entry in place; update `concept_canon.md` |
| **Upgrade provenance** | New source artefact validated, or user research arrives | Move `provenance.<lang>.level` upward; add IDs to `sources`; optionally fill `validated_at` |
| **Rename canonical name** (cascade-triggering) | User research reveals a better term | Trigger the cascade — see §6 below |

### 5.3 Caller-skill integration matrix (CHANGED from v2)

| Caller skill | Invokes `ux-write-canon-concept`? | Condition |
|---|---|---|
| `requ-explore` | Yes | When body introduces a user-facing noun/verb/state |
| `ux-create-flow` | Yes | When flow step labels introduce a user-facing concept |
| `ux-write-scenario` | **Conditional** — only when scenario is *future-state* (app-usage) | NOT for as-is (pre-app) scenarios. Skill description must state this explicitly. |
| `ux-write-persona` | **No** | Personas describe people, not product concepts |
| `code-simple` / `code-complex` | Yes (DDD light enforcement, §8) | When introducing hardcoded user-facing strings or feature-level identifiers that surface to users |
| `ui-create-scribble` | Yes (§4) | When generating labels |
| `ui-create-scribble-improve` | Yes (§4) | Same |
| `product-intake` | Yes (§6) | When intake produces user-facing concept changes (e.g., new feature naming) |

### 5.4 Skill body sketch (canonical structure)

The skill itself is small. Its body needs:

1. **Inputs**: `name` (string), `lang_evidence` (map lang→{level, sources}), optional `aliases`, optional `description`, optional `states`/`operations`, optional `forbidden_synonyms`.
2. **Check first**: read `concept_canon.yaml`; case-insensitive search for `name` and its near-variants; if found → propose to update existing entry instead, ask user/caller.
3. **ID generation**: `CONCEPT-<UPPER-KEBAB>` from the canonical English name. Multi-word: hyphenate. Example: "Hand Over" → `CONCEPT-HAND-OVER`. Document this convention in `concept_canon/README.md` for stability.
4. **Concurrent edits**: use a marker file lock (`.canon-lock`) similar to the REQ-ID-allocation pattern (`allocate_req_id.py`) to prevent two parallel sessions from creating duplicates.
5. **Write**: append entry to `concept_canon.yaml`, regenerate `concept_canon.md`.
6. **Verify**: invoke `check_canon.py --concept CONCEPT-X` to spot-check the new entry resolves correctly.

---

## 6. Cascade integration (user §8 — significant new section)

### 6.1 The four cascade flows

Three cascades involve the canon:

**Cascade A: Canonical-name flip changes UI labels and code (forward).**
When `ux-write-canon-concept` renames a concept (e.g., user research says "Programme" beats "Plan"):

1. Audit: `check_canon.py --references-to CONCEPT-PLAN` — list all files that reference the old canonical name.
2. For each ARB file with the term: update value, update key if appropriate.
3. For each Dart user-facing string: update via Edit tool.
4. For each `translation_context` entry: update both the English text and the per-locale text where applicable.
5. Re-run audit; expect exit 0.

This cascade is large enough to be its own concern. Two options:
- **A1**: Fold into `ux-write-canon-concept` — the skill itself orchestrates the cascade.
- **A2**: Separate skill `ux-cascade-canon-rename` invoked by `ux-write-canon-concept` when a rename is detected.

Recommendation: **A1 — fold into the single skill**. The user's note about existing UX skills folding create + update into one supports the same folding here. The rename branch becomes a section of the skill's body.

**Cascade B: User-needs artefact updates name → canon needs update (reverse).**
When `ux-write-persona`, `ux-create-flow`, `ux-write-scenario` change a term that the canon references:

1. The calling skill must detect the rename (string comparison before/after).
2. If the renamed term resolves to a canon entry via `aliases` or appears in any `sources` reference: trigger `ux-write-canon-concept` to handle the canon side (and then forward Cascade A from there).

This is a *less common* path. Most user-needs edits do not affect canonical names. The skill extensions need a "did your edit rename a canonized term?" check before completing.

**Cascade C: `product-intake` introduces new concepts.**
`product-intake` is the top-down intake skill. It already cascades persona → scenario → flow → requirement. The canon now joins this chain:

```
product-intake step N+1: Canon impact
1. Identify any new user-facing concepts introduced by this intake
2. For each: invoke `ux-write-canon-concept`
3. If a concept name changed: run Cascade A from `ux-write-canon-concept`
```

I propose inserting this between Step 4 (User Flows) and Step 5 (Requirements) in `product-intake/skill.md`. The canon entry must exist before the requirement is written, so requirements can reference canon IDs.

### 6.2 The translation mechanism — proposing a task

The user asked whether a translation-mechanism task exists, and if needed for DE/EN now.

**My assessment**:
- DE/EN translations are currently authored by the LLM/app-provider via ARB editing. AC-08's `translation_context` adds a structured field that helps but doesn't *require* a new translation tool.
- A dedicated translation skill becomes useful when:
  - A third language is added (then the LLM-driven translation pipeline gets exercised), OR
  - Volume exceeds what manual ARB editing handles comfortably (~200+ entries).
- Neither trigger is acute right now.

**Recommendation**: create the task at **low priority**, queued for when a third language gets added. I will spawn the task-create agent for this as the user authorized — but flag the priority is `urgency: 1` (defer).

Title proposal: *Design and implement LLM-driven translation skill consuming concept_canon + translation_context*. Parent: REQ-NFUNC-013 (ux_writing). Type: `explore` then `impl`.

### 6.3 The label-rename cascade skill — already in §6.1

Cascade A handles the user's specific concern ("Wenn neue User Research dazu führt, dass UI-Labels angepasst werden müssen — wäre gut, einen Skill dafür zu haben"). Folded into `ux-write-canon-concept` per §6.1 A1.

---

## 7. File-splitting decision (user §6)

### 7.1 The question

If `concept_canon.yaml` reaches 50–200 concepts, every skill that consults it pays a read cost. Splitting into multiple files reduces the per-read footprint at the cost of more complex lookup.

### 7.2 Sizing the file

Conservative estimate per concept:
- Minimal entry (inferred, EN only): ~10 lines.
- Rich entry (multi-language proto-evidenced + aliases.code + forbidden synonyms): ~25 lines.
- Average: ~15 lines.

At 150 concepts × 15 lines = **~2,250 lines** of YAML. That's ~80 KB. Smaller than `requirements.md` (the merged one) and well within practical LLM-read budget. Plus YAML is highly compressible in LLM context (lots of repeated keys).

### 7.3 Counter-argument: LLM doesn't need the whole file

When a skill needs to check "does CONCEPT-PLAN exist?", it needs the IDs and names only. Full bodies aren't required for the lookup. Options:

- **Generated lightweight index**: alongside the full `concept_canon.yaml`, a generated `concept_canon.index.yaml` carrying only `[id, name_canonical, aliases.de, related]` per concept. ~5 lines per concept = ~750 lines at 150 concepts (~25 KB). Skills consult the index for "does this exist"; only `ux-write-canon-concept` reads the full file when actually editing.
- **Splitting by bounded context**: `concept_canon/canon-therapist.yaml`, `canon-client.yaml`, etc. — but this hits the fan-out failure mode flagged in web research and v1 §1.

### 7.4 Recommendation

**Single file + generated index** (option above).

- `concept_canon.yaml` stays canonical.
- `concept_canon.index.yaml` is generated by `generate_concept_canon_md.py` (same generator step). Skills consult the index.
- This stays cheap until ~500 concepts, far beyond plausible product scale.
- The user's point that "spätestens, wenn man einen neuen Begriff hinzufügen möchte, wird dir auffallen, dass es den schon gibt" — the index makes that check cheap.

If/when the index also outgrows comfort, splitting it by context becomes the next move. But that's a v4-or-later concern.

### 7.5 Schema for index

```yaml
# concept_canon.index.yaml (generated; do not edit)
version: 1
generated_from: concept_canon.yaml
generated_at: 2026-MM-DD
concepts:
  - id: CONCEPT-PLAN
    name: Plan
    aliases_de: [Plan]
    type: object
  - id: CONCEPT-HAND-OVER
    name: "Hand Over"
    aliases_de: [Aushändigen]
    type: operation
  ...
```

---

## 8. Light DDD enforcement via skills (user §9 — CHANGED from v2)

### 8.1 What "light enforcement" means here

The user moved from v2's "no enforcement" to "light enforcement — but not via linter; via skill instructions so the LLM naturally uses canonical names." Occasional slip-ups are acceptable.

### 8.2 Code-skill extensions

| Skill | Extension |
|---|---|
| `code-simple` | "When introducing classes, methods, enums, BLoC events/states, or hardcoded user-facing strings, prefer names that match canon's canonical name or one of its `aliases.code`. If you introduce a new user-facing concept in code, invoke `ux-write-canon-concept` to register it before completing the task." |
| `code-complex` | Same extension. |
| `code-test` | Test class names mirror the classes under test — no separate canon directive needed. |
| `code-bugfix` | Bug-fix scope is narrow; no canon directive needed unless the bug fix renames a class with user-facing surface (rare). |

### 8.3 Recording what already diverges

The existing divergences (`SharePlanTemplateRequested`, `DataBeamBloc`, etc.) get recorded in the bootstrap canon's `aliases.code` field. They are NOT refactored — they are acknowledged. Future code authored under the light enforcement directive will gravitate toward canonical names without forcing the existing code to change.

### 8.4 Audit signal for code-side divergence

`check_canon.py` includes a `--code-coverage` mode that reports:
- Percent of feature-presentation BLoCs/screens whose names match a canon concept directly.
- List of unacknowledged divergences (BLoCs/screens whose names *contain* a forbidden synonym not in `aliases.code`).

This is signal, not gate. Useful for periodic review.

---

## 9. New gaps I identified that the user didn't raise

The user invited me to surface gaps beyond their feedback. Below are nine I see; each is followed by a recommendation.

### 9.1 Concept-ID naming convention

Multi-word concept names need a stable ID convention. v3 proposes: `CONCEPT-<UPPER-KEBAB>` from the English canonical name. "Hand Over" → `CONCEPT-HAND-OVER`. "Plan Template" → `CONCEPT-PLAN-TEMPLATE`. Document this rule in `concept_canon/README.md` so the convention isn't reinvented per session.

### 9.2 Concurrent canon edits — lock mechanism

Two parallel sessions both invoking `ux-write-canon-concept` could create duplicate entries or race on file writes. The project already has a precedent: `allocate_req_id.py` uses a file lock to atomically reserve REQ-IDs. The canon skill should use the same pattern — a `.canon-lock` marker file with a brief lifetime during the write step.

### 9.3 Concept lifecycle — archive when retired

When a concept is removed from the product, the entry should not be deleted (history loss). Schema field `status: active | archived` plus an `archived_reason` field. Archived entries are skipped by the audit's forbidden-synonym detection (so deprecated code can still reference the historical name) but flagged if appearing in new artefacts.

### 9.4 Bidirectional links — back from source artefacts to canon

The canon entries link *down* to source artefacts via `provenance.sources`. The reverse link (a scenario file or flow file linking *up* to the canon ID it uses) is not enforced. Adding `references: [CONCEPT-PLAN, CONCEPT-HAND-OVER]` to the YAML of personas/scenarios/flows would make Cascade B (above) automatic.

Recommendation: defer until v3.5 — extending the existing YAML schemas in `requirements_user_needs/` is its own change with cascade. Note it in the deferred list.

### 9.5 REQ-PROC-050 (Artifact Soundness) integration

The provenance levels match REQ-PROC-050's spirit perfectly. The canon's `provenance.<lang>.level` becomes a signal REQ-PROC-050's soundness checklist can consume. Concretely: REQ-PROC-050 already mandates each user-needs artefact carry an evidence level — the canon now does too, and REQ-PROC-050's aggregator can include canon distribution in its report.

Recommendation: flag this in the bootstrap-canon impl task's "Related" section; the actual integration is a follow-up task under REQ-PROC-050.

### 9.6 Persona-driven constraints on canon terms

PERSONA-002 (Max) has tier-1 sensitivity to shame language; PERSONA-014 (Jana) has trauma-related triggers. Some terms aren't *technically wrong* but are persona-forbidden. The canon should be able to express this:

```yaml
forbidden_synonyms:
  - term: "Failed"
    lang: en
    note: "Persona-driven exclusion"
    constrained_by: [PERSONA-002, PERSONA-014]
```

This makes the canon a more honest record of why certain words are out of bounds.

### 9.7 Localized example sentences (translator aid)

Adding `examples:` per language to each entry:

```yaml
examples:
  en:
    - "The therapist hands over a Plan to a Client."
  de:
    - "Die Therapeutin händigt einen Plan dem Klienten aus."
```

Helps the translation tool (Cascade B / future translation skill) by showing the term in context. Optional field; not required at bootstrap.

### 9.8 Search heuristic for "does this concept exist already?"

When `ux-write-canon-concept` checks for duplicates before adding, the comparison can't be exact-only — "HandOver", "Hand Over", "Hand-Over" are all candidates. Recommendation: normalize (lowercase, strip whitespace and hyphens) for the duplicate check; if the normalized form matches an existing concept, prompt the caller "Did you mean CONCEPT-HAND-OVER?"

### 9.9 Canon entry schema versioning

If the schema changes (e.g., adding `examples`), entries written under the old schema may be missing fields. Adding `schema_version: 1` to the top of `concept_canon.yaml` lets future migrations be explicit. Cheap insurance.

---

## 10. Final schema (consolidated v3)

```yaml
schema_version: 1
concepts:
  - id: CONCEPT-PLAN
    type: object                           # object | state | operation | ui_surface(DEFERRED §10.7)
    status: active                         # active | archived  (NEW §9.3)
    archived_reason: ""                    # only when status==archived
    name_canonical: "Plan"                 # English; primary per §10.2
    aliases:
      de: "Plan"
      code:
        - identifier: "QuestionnairePlan"
          artefact: "lib/core/domain/entities/questionnaire_plan_entities/"
          reason: ""
      legacy: []
    description: >
      A finalized set of questionnaires assigned by a therapist to a client.
    states: [Draft, Finalized, HandedOver, Received, Accepted, Declined]
    operations: [HandOver, Receive, Accept, Decline, Save]
    forbidden_synonyms:
      - term: "Programm"
        lang: "de"
        note: "Rejected for clinical/institutional tone."
        constrained_by: []                 # optional persona IDs
        evidence: []                       # optional source IDs
    related: [CONCEPT-CLIENT, CONCEPT-HAND-OVER]
    examples:                              # optional (§9.7)
      en: []
      de: []
    provenance:
      en:
        level: inferred                    # 4 levels per §1.2
        sources: []                        # structured IDs per §2
        validated_at: ""
        notes: ""
      de:
        level: proto-evidenced
        sources:
          - { id: SCEN-001-03, anchor: "#step-2" }
          - { id: FLOW-007,    anchor: "#step-5" }
        validated_at: ""
        notes: ""
    introduced_by: REQ-PROC-049
```

---

## 11. Updated bootstrap impl-task sequence

| # | Task | Type | Effort | Skill | Depends on |
|---|---|---|---|---|---|
| 1 | Create `requirements_user_needs/concept_canon/{README.md, concept_canon.yaml (empty seed), concept_canon.index.yaml (empty seed)}` + `scripts/user_needs/generate_concept_canon_md.py` (also generates the index) | impl | S | `claude-write-script` + `task-resolve` | none |
| 2 | Author bootstrap canon for `feat_therapist_transfer_ui` (~6–10 concepts incl. Plan, Client, Therapist, HandOver, Receive, HandOverDialog) — provenance per language; known `aliases.code` divergences recorded | impl | M | `task-resolve` | 1 |
| 3 | Coordination read of TASK-PROC-046 Tier-0 tasks; create `scripts/quality/_arb_parser.py` if not already proposed | analyze | S | `task-resolve` | none (parallel with 1+2) |
| 4 | Implement `scripts/user_needs/check_canon.py` — 4 walkers + AC-03 verb check + `--json` output + `--validate-references` + `--code-coverage` | impl | M | `claude-write-script` | 1, 2, 3 |
| 5 | Add `ux-write-canon-concept` skill (~50-line skill, with concurrent-edit lock, search heuristic, all 4 operations from §5.2) | impl | M | `claude-create-skill` | 1 |
| 6 | Extend caller skills: `requ-explore`, `ux-create-flow`, `ux-write-scenario` (conditional — future scenarios only), `code-simple`, `code-complex`, `ui-create-scribble`, `ui-create-scribble-improve`, `product-intake` (new step) | impl | M | `claude-modify-skill` (per skill; batchable) | 5 |
| 7 | Document workflow in `concept_canon/README.md`; one-line entry in `CLAUDE.md` §10 | impl | S | `task-resolve` | 1–6 |
| 8 | Add `check_canon.py` to release pre-flight script | impl | S | `claude-write-script` | 4 |
| 9 | **(new, low-priority, optional)** Translation-mechanism design task — `explore` task under REQ-NFUNC-013 — design LLM-driven translation skill consuming canon + translation_context | explore | M | `task-create` (this task creates it) | none — sits in backlog |

Tasks 1 and 3 parallelizable; 5 and 4 parallelizable after 1; 6 follows 5; 7 cleans up; 8 wires to release; 9 is a deferred backlog item.

---

## 12. Open / deferred decisions (carried + new)

| # | Decision | Status |
|---|---|---|
| §10.1 (v1) | Subfolder location | RESOLVED — `requirements_user_needs/concept_canon/` |
| §10.2 (v1) | Primary language | RESOLVED — English |
| §10.3 (v1) | `lib/core/` scope | RESOLVED — excluded |
| §10.4 (v1) | Gate promotion trigger | DEFERRED |
| §10.5 (v1) | DDD enforcement | RESOLVED — light enforcement via skill instructions, no linter |
| §10.6 (v1) | Inline code marker | DEFERRED |
| §10.7 (v1) | `type: ui_surface` | DEFERRED |
| v3-1 | Skill name (`ux-write-canon-concept` recommended vs user's `ux-modify-canon-concept`) | OPEN — please pick |
| v3-2 | Translation-mechanism task — spawn now (low priority) or defer entirely? | OPEN — awaiting your call |
| v3-3 | Bidirectional `references: [CONCEPT-*]` in user-needs artefact YAML (§9.4) | DEFERRED to v3.5 |
| v3-4 | Persona-driven `constrained_by` field for forbidden_synonyms (§9.6) | RECOMMEND adopt; awaiting your nod |
| v3-5 | `examples` field per language (§9.7) | RECOMMEND adopt as optional; awaiting your nod |
| v3-6 | Schema versioning (`schema_version: 1`) (§9.9) | RECOMMEND adopt; cheap insurance |
| v3-7 | Cascade A folded into `ux-write-canon-concept` (vs separate skill) — §6.1 | RECOMMEND fold; awaiting your nod |

---

## 13. What remains uncertain

- **Provenance-level transitions in practice**: how often does `inferred` upgrade to `proto-evidenced`? Hard to know until beta-phase research arrives. The schema accommodates either pace.
- **Cross-language canon flips**: if user research validates "Plan" for DE but rejects "Plan" for EN, the canon would have a name-divergence across `name_canonical` (EN) and `aliases.de`. The current schema handles this — `name_canonical` is just one language's canonical choice — but the audit messaging needs to be language-aware.
- **`ui-create-scribble` integration cost** (§4) — adding canon awareness to a skill that currently runs in alpha phase is more invasive than expected. Worth measuring on the first integration.
- **Cascade A complexity** (§6.1) — renaming a canonical name with cascade through ARB + Dart + translation_context is non-trivial. The first time it runs in anger we may discover edge cases (placeholders, ICU plurals, format strings) that need additional logic.
- **The shared `_arb_parser.py` ownership** — same coordination point as v2, unchanged.
- **Discrepancy-check false-positive rate** — the AC-03 verb-precision check will likely produce many candidates on first run. Tuning empirical.
- **Schema migration cost when `schema_version` increments** — first migration is years away; the field is insurance.

---

## 14. Acceptance criteria check

- [x] User §4 (provenance, multi-language, proto-evidenced) — §1
- [x] User §5 (script location, LLM-interpretation, gate-future shape) — §3
- [x] User §6 (UI-scribble, translation-task, label-rename-cascade, file-splitting) — §4 + §6 + §7
- [x] User §7 (IDs everywhere, anchors, free-text audit) — §2
- [x] User §8 (skill name, scope, scenario conditional, persona exclusion, cascade integration) — §5 + §6
- [x] User §9 (light DDD enforcement via skills) — §8
- [x] Additional gaps surfaced — §9 (9 new gaps)
- [x] Honest about remaining uncertainty — §13
- [x] Updated bootstrap sequence — §11
- [x] Open decisions explicitly framed — §12

---

## 15. Action proposal

Before kicking off the bootstrap impl-task sequence, two things need your decision:

1. **Skill name**: `ux-write-canon-concept` (my recommendation, matches `ux-write-persona` / `ux-write-scenario`) **or** `ux-modify-canon-concept` (your earlier proposal).
2. **Translation-mechanism task** (§6.2): spawn it now as low-priority backlog, or defer until a third language is on the roadmap?

Plus four lighter calls (§12 v3-3 through v3-7) where I've made a recommendation and a yes/no from you closes them out.

Once those are answered, we're ready for the impl tasks. I can spawn `task-create` agents in parallel for the eight bootstrap tasks (§11) plus the optional translation task (§11 #9).
