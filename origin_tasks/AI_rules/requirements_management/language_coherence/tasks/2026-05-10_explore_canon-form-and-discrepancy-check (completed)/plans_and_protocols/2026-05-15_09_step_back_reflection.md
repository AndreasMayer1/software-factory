# Step-Back Reflection — Are We Building the Right Thing?

Date: 2026-05-15
Model: Opus 4.7
Purpose: Surface additional gaps; then step back from v3 and ask whether the cumulative design is well-sized for this project's actual situation.

This document is a reflection, not a design. It complements v3, doesn't replace it. Sections 1 and 2 list new gaps; sections 3–6 are the step-back analysis the user asked for.

---

## 1. Additional gaps (beyond v3 §9)

I scanned v3 for things I had not yet surfaced. Eleven more gaps, organized by where they bite:

### 1.1 Bootstrap fragility — skills must handle "canon doesn't exist yet"
Every skill that consults the canon must degrade gracefully during the first few minutes of bootstrap (between Task 1 creating the empty file and Task 2 populating it). v3 didn't define that fallback: if `concept_canon.yaml` exists but is empty, do skills proceed silently? Warn? Block? Recommendation: silent proceed; an empty canon is the natural state at start.

### 1.2 The 26 paused back-pressure tasks may have already decided things
v3 §3 said "coordination needed" but didn't actually verify what those tasks decided. Some of them — particularly `TASK-PROC-046-01` (explore root), `TASK-PROC-046-08`, `TASK-PROC-046-14` — may have produced design artefacts that contradict v3's choices (e.g., a different `.arb` parser shape, a different gate-promotion policy). Before any impl task starts, those task plans must be read. This is not a one-line "coordination read" — it could surface real conflicts requiring re-design.

### 1.3 User vocabulary that the product does NOT model
The canon currently captures concepts the product commits to. It does not capture user vocabulary that users use but the product doesn't model — e.g., users say "mood swings," but the product's `MoodEntry` doesn't have a "swing" state. This is exactly the class of mismatch user research is most likely to surface ("you have no word for the thing I'm trying to do"). The canon as designed cannot record these gaps.

Possible extension: an `external_vocabulary:` section in the canon listing terms users use that the product does not model, with `notes` for product-design follow-up. This is a soft signal for REQ-PROC-050 soundness.

### 1.4 Error-message and disabled-state copy is outside the canon's scope
REQ-NFUNC-013 §5 defines a two-part error pattern; §6 defines a two-part disabled-state pattern. These produce copy ("Please try again," "Save your plan first to enable Hand Over"). The patterns reference concepts (the disabled action references HandOver) but the canon does not model the patterns themselves. Result: an LLM authoring an error message must consult the canon for concept names AND REQ-NFUNC-013 §5 for the error pattern. Two places to check.

This is probably fine — the canon does not need to subsume all UX writing — but the boundary should be explicit.

### 1.5 Translations that already exist become stale on canon-rename
Cascade A (rename) updates ARB string values when a canonical name flips. But the *German translation* of a renamed English term may not be a 1:1 substitution. E.g., if `HandOver` becomes `Transfer`, the German alias `Aushändigen` may stay valid — or it may need to flip to `Übertragen`. Currently the skill cannot make this judgment automatically. The cascade must pause for per-language human review.

### 1.6 Deprecation horizon for legacy canonical names
When `Plan` becomes `Programme`, `Plan` lives in `legacy`. For how long? Forever (history)? Until next release (cleanup)? Until no artefact references it anymore (automatic decay)? The schema permits any policy; v3 didn't pick one.

### 1.7 No automated detection that the LLM is *introducing* a new concept
The skill extensions say "if you introduce a new concept, invoke `ux-write-canon-concept`." But the LLM has to *notice*. A heuristic: any noun-phrase appearing in a UI string that doesn't tokenize to a canon name should auto-flag. But pure NLP can't distinguish "I'm naming a new feature" from "I'm using a generic word." This is the kind of thing only LLM judgment can do — but the LLM has to know to ask itself.

A skill-level reminder is the only practical mechanism. We've already proposed that in v3 §5.3 / §8.2. The gap is honest: the mechanism is hint-based, not enforcement-based. Will the LLM actually catch every case? Probably not. Most cases, yes.

### 1.8 The canon doesn't model object-state cardinality or transitions
A Plan can move from Finalized → HandedOver → Received. The canon lists the states but does not encode the transitions. AC-03's verb-precision check needs *some* notion of "which operations apply to which states" to detect, e.g., "you can't HandOver a Draft plan." Without that, the check is purely lexical.

This is *probably fine* — state-machine modeling is implementation concern, and the canon's job is naming. But it limits what AC-03 can detect.

### 1.9 No mechanism for the canon to evolve away from English-as-primary
If the product later goes Arabic-first, the canon's `name_canonical` is the wrong axis. Migrating requires touching every entry. Schema versioning (v3 §9.9) helps but doesn't solve. The current shape is locked to English-as-primary as long as it lives.

### 1.10 Mixed registers within one concept
The same operation may need formal vs. informal variants in one language — "Plan aushändigen" (therapist→client, formal) vs. some hypothetical client-side variant (more casual). The canon entry is single-register per language. This breaks for products with strong audience-segmentation needs. Less acute here than for, say, a banking app, but worth noting.

### 1.11 What if two valid English terms exist for genuinely-different reasons?
"Account" vs. "Profile" — both valid, distinguishing user identity vs. settings. The canon currently treats one as canonical and one as forbidden/rejected. But sometimes both legitimately co-exist. The schema can express this (different `CONCEPT-*` entries), but the AC-03 verb-precision check would need to disambiguate which one a given label references — and lexical patterns alone can't.

---

## 2. Quick verdict on the eleven new gaps

| # | Severity | Resolve now? |
|---|---|---|
| 1.1 | Low | Yes — one-line graceful-degradation in the README |
| 1.2 | **High** | Yes — must read before impl |
| 1.3 | Medium | Defer — add `external_vocabulary:` section if user research surfaces real need |
| 1.4 | Low | Document the boundary in `concept_canon/README.md` |
| 1.5 | Medium | Document: rename cascade requires per-language human review |
| 1.6 | Low | Pick a default (recommended: legacy stays in canon for one major release, then archived) |
| 1.7 | Medium | Accept it's hint-based; document the limitation honestly |
| 1.8 | Low | Document scope: canon names; state-transition modeling stays in code |
| 1.9 | Low | Schema versioning already covers it |
| 1.10 | Low | Out of scope until product needs it |
| 1.11 | Low | Schema supports separate CONCEPT entries; LLM-disposition handles ambiguity |

---

## 3. Step back — what have we actually been designing?

Across three iterations the design has accumulated:

- 1 source YAML (`concept_canon.yaml`)
- 1 generated index YAML (`concept_canon.index.yaml`)
- 1 generated markdown view (`concept_canon.md`)
- 1 README explaining the workflow
- 1 new skill (`ux-write-canon-concept`, ~50 lines)
- 1 audit script (`check_canon.py`) with 4 artefact walkers, JSON output, reference validation, code-coverage mode
- 1 shared parser module (`_arb_parser.py`) with REQ-PROC-046 G6
- 1 generator script
- 1 lock mechanism
- 1 schema with: 4-level multi-language provenance, structured ID references with anchors, lifecycle status, persona-driven constraints, examples, schema versioning
- Extensions to 7+ existing skills (requ-explore, ux-create-flow, ux-write-scenario [conditional], code-simple, code-complex, ui-create-scribble, ui-create-scribble-improve, product-intake)
- 9 bootstrap implementation tasks

This is a lot. The user's recurring grounding — PERSONA-015's "longevity over velocity, simplicity as survival strategy for one-person maintenance over years" — is the lens I want to re-apply now, honestly.

### 3.1 The core tension I missed earlier

The canon framework (Layers-skills OOUX, DDD ubiquitous language, Fluent terms) was designed for teams that have:

- Multiple authors who would otherwise drift apart;
- User research feeding term decisions;
- Designers and engineers needing a shared reference;
- A delivery cadence where naming gets settled and stays settled.

This project has:

- One author (the app provider) plus LLM agents that read everything before they write;
- Almost no user research yet — current evidence base is proto-personas;
- Designers and engineers are the same person + LLM;
- Pre-beta, where naming is provisional and will likely flip when research starts.

The canon framework's authority comes from research-backed deliberate naming decisions. **In our context, the canon's authority is largely "this is what the LLM and the app provider agreed last."** That is a weaker form of authority than the framework was designed for. It does not justify the same apparatus.

### 3.2 Where the apparatus pays off, and where it doesn't

What pays off:
- **AC-08 duplication removal**: real win at scale. The canon lets `translation_context` reference concepts by ID instead of redescribing them. Direct savings of hundreds of lines once AC-08 lands at scale.
- **Concrete drift catches (AC-02)**: real win even today. `Transfer` vs. `HandOver` on the same dialog is a genuine bug the audit would have caught.
- **A reference for the LLM**: real win. LLM sessions can read one file and know the names. This is mostly what the framework is doing in our context — providing LLM context.

What doesn't pay off proportionally:
- **Multi-language provenance with 4 levels**: this is bookkeeping for evidence we mostly do not have. At bootstrap, ~100% will be `inferred` for EN and `proto-evidenced` for DE. We are encoding the absence of evidence with high fidelity.
- **Cascade A (rename with multi-file edits)**: this is heavy machinery for an event that will happen, optimistically, ~5–10 times across the project's life until product-market fit.
- **The product-intake step + 7 skill extensions**: this is a lot of touch points for a discipline whose value materializes mostly at AC-08 time and at release time.
- **The audit script's `--code-coverage` mode + reference validation + JSON output**: features that pay off only at scale we haven't reached.

### 3.3 The deeper question

If the canon is largely an LLM context aid plus a release-time drift detector, the apparatus around it is over-built.

Two thoughts:

**Thought 1**: The canon's primary value at this stage is *as LLM context*, not as a refereed authority. The simplest thing that delivers that value is a markdown file the LLM reads, plus a release-time grep. Everything else is preparing for a future scale that may not arrive in this form.

**Thought 2**: PERSONA-015's "simplicity is a survival strategy" reads in the strongest sense as: *don't build the apparatus for the team you don't have.* A solo developer's canon should be small enough to read in two minutes, edit without ceremony, and grep without a script. Everything beyond that has to earn its place by removing more friction than it adds.

### 3.4 Where I think v3 over-engineers

I'll be concrete:

| v3 feature | What it costs | What it buys | Verdict |
|---|---|---|---|
| Multi-language 4-level provenance per concept | ~10 lines per entry × 30+ entries = ~300 lines of structured bookkeeping at bootstrap | Records absence-of-evidence with fidelity | Probably too much; one block per concept with a single level field is enough |
| `concept_canon.index.yaml` generated alongside | Generator + format + sync issue | Cheaper LLM reads | Skip until file exceeds 80 KB (currently zero need) |
| `--code-coverage` audit mode | ~30 lines of script | Signal for periodic review | Skip until used in earnest |
| `--validate-references` audit mode | ~20 lines | Catches typo'd IDs | Catch with manual review at bootstrap; add later |
| `--json` audit output + LLM disposition workflow | ~40 lines of script + disposition rules | Structured audit | Pretty stderr text is enough until the audit produces enough findings to warrant JSON |
| Persona-driven `constrained_by` on forbidden synonyms | Field + lookup logic | Rich rationale | Defer — write in `note` until the field carries weight |
| `examples:` per language | Field | Translation aid | Defer; not needed until 3rd language |
| Concurrent-edit lock | Lock file + retry logic | Prevents rare collisions | Skip — solo dev rarely has two parallel sessions on canon |
| Cascade A (in-skill rename cascade) | Significant skill body | Automates a rare event | Replace with: skill creates an impl task to handle the cascade |
| Product-intake step insertion | Skill modification | Top-down consistency | Worthwhile, but place it cautiously — product-intake is already heavy |
| 7 skill extensions | 7 places to keep in sync | LLM hints | Reduce to: 1 CLAUDE.md paragraph + 1 explicit invocation in `requ-explore` |

### 3.5 What I would keep

| Element | Keep | Why |
|---|---|---|
| `concept_canon.yaml` source | Yes | Core artefact |
| `concept_canon.md` rendered view | Yes | Human read path |
| `ux-write-canon-concept` skill | Yes | Single discipline anchor |
| `check_canon.py` audit script (minimal) | Yes | AC-05 satisfaction |
| Schema with id, name_canonical, aliases, description, states, operations, forbidden_synonyms, related, code-side aliases | Yes | Minimal useful payload |
| Single provenance field (level + sources) without per-language split | Yes | Acceptable simplification |
| Bootstrap from feat_therapist_transfer_ui | Yes | Concrete entry point |
| Co-design with REQ-PROC-046 work | Yes | Genuine coordination need |
| Shared `_arb_parser.py` | Yes (or thinner) | Real shared infra |
| Light DDD via code-skill hint | Yes (one-line) | Cheap win |
| CLAUDE.md mention | Yes | One place for the directive |

### 3.6 What I would defer or remove

| Element | Action |
|---|---|
| Multi-language provenance split | Defer until both EN and DE evidence diverge in practice |
| 4-level provenance ladder | Reduce to 2 levels initially (inferred / evidenced); add proto-evidenced and validated when needed |
| `concept_canon.index.yaml` | Defer until file exceeds practical-read threshold |
| `--code-coverage` mode | Defer until canon is mature |
| `--validate-references` mode | Defer; bootstrap canon is small enough for manual review |
| JSON output + disposition workflow | Defer; text output adequate at small scale |
| Concurrent-edit lock | Skip |
| `examples` field | Defer to 3rd-language work |
| `constrained_by` field | Defer; use `note` |
| Cascade A in-skill | Replace with: skill creates an impl task |
| Skill extensions × 7 | Reduce to: CLAUDE.md paragraph + `requ-explore` explicit invocation |
| `ui-create-scribble` integration | Defer — alpha phase, not yet exercised |
| `product-intake` step | Add as note in skill body; lighter than full step |
| 9 bootstrap tasks | Reduce to 3–4 tasks (see §5) |

---

## 4. Three viable shapes — pick one

Given the analysis, three sizings are coherent. The user picks based on their cost/value judgment.

### 4.1 Shape M — Minimal (recommended for current context)

The smallest thing that earns AC-01..AC-05.

**Deliverables (3 tasks):**
1. `requirements_user_needs/concept_canon/concept_canon.yaml` — hand-authored, ~6 concepts seeding `feat_therapist_transfer_ui`. Schema: `id, name_canonical, name_de, description, states, operations, forbidden_synonyms, aliases_code, related, evidence_level (inferred|evidenced), introduced_by`. No multi-language provenance blocks; one `evidence_level` field. `concept_canon.md` is auto-generated on commit (or by a tiny script run on demand).
2. `scripts/user_needs/check_canon.py` — ~100 lines, single mode, text output. Walks `.arb` + `lib/features/**/presentation/*.dart` + `requirements_tasks/**/requirements.md`. Lists candidates; exit 0/1.
3. `ux-write-canon-concept` skill — ~40 lines. Add or update entry. No cascade — if a rename is needed, the skill creates an impl task instead.

**CLAUDE.md addition** — one paragraph:
> When authoring user-facing language (requirements bodies, ARB values, UI strings, scribble labels), consult `requirements_user_needs/concept_canon/concept_canon.yaml` for canonical names. If you introduce a new user-facing object/state/operation, invoke `ux-write-canon-concept`. Before release, run `python3 scripts/user_needs/check_canon.py`.

**Skill extensions** — exactly one: `requ-explore` mentions "consult canon and invoke `ux-write-canon-concept` when introducing concepts." Other skills inherit via CLAUDE.md.

**What's deferred**: per-language provenance, proto-evidenced and validated levels, index, JSON output, all advanced audit modes, scribble integration, cascade A, product-intake integration, examples, constrained_by.

**Effort**: ~1 day to bootstrap end-to-end. Maintenance cost approaches zero.

**Risk**: drift detection is coarser; the canon's authority is informal. Acceptable trade in solo/alpha phase.

### 4.2 Shape M+ — Medium (v2 baseline, lightly cleaned up)

What v2 was, with the v3 corrections.

**Deliverables (~5–6 tasks):**
- Shape M, plus:
- `concept_canon.index.yaml` (generated)
- The provenance field becomes a block with `level` + `sources` (single-language, both EN and DE go through one field) — no per-language split
- `check_canon.py` gains `--json` output and AC-03 verb check
- Add `ui-create-scribble` extension as a one-line hint
- Add `product-intake` note (not full step)
- Cascade A still in an impl task spawned by the skill, not inline

**What's still deferred**: 4-level provenance, multi-language split, `--code-coverage`, `--validate-references`, examples, constrained_by, concurrent-edit lock.

**Effort**: ~3–5 days to bootstrap. Maintenance cost low.

**Risk**: less coverage than full; but probably aligned with current value extraction.

### 4.3 Shape F — Full (v3 as written)

Everything v3 spelled out.

**Effort**: ~7–10 days to bootstrap. Maintenance cost moderate (the provenance/cascade machinery needs ongoing attention).

**Risk**: over-built for current research evidence base; the apparatus could ossify before it's earned.

---

## 5. My recommendation

**Shape M (minimal)**, scheduled for bootstrap.

Reasons:
1. PERSONA-015's grounded values are the dominant constraint. Shape M is the smallest thing that satisfies AC-01..AC-05.
2. The audit-and-LLM-disposition loop is *easier* to operate with a small canon than a rich one. Patterns we discover at small scale inform what to add. Building the rich one first is speculation.
3. Shape M is *strictly extensible* to Shape M+ or F. Nothing in Shape M closes future doors. Adding provenance per language, an index, JSON output, etc. is a follow-up task whenever the evidence demands.
4. The user's previous feedback ("project already creates a lot of markdown documents") is best honored by adding the least, not the most.
5. Beta phase will surface what we actually need. Bootstrapping at scale now means we ship a lot of machinery that may not survive beta-phase reality.

What I would explicitly include in Shape M's README is the *path to extension*: "When a third language is added, the provenance field splits per-language. When the file exceeds X KB, generate the index. When forbidden-synonym findings exceed Y per audit, add `--json` output." The README is the upgrade ladder.

## 6. Other framings I considered and rejected

For honesty: I considered three reframings during this reflection and rejected them. Listing for completeness:

**(a) Drop the canon, just enforce REQ-NFUNC-013 §8.4 case-by-case.** Rejected: AC-08's duplication problem is real and scales. Without a canon, every translation_context entry redescribes shared concepts. The savings are too large to skip.

**(b) Use a database (SQLite) instead of YAML.** Rejected: overkill; YAML round-trips with git better; LLMs read YAML naturally. SQLite would help only at >1000 concepts.

**(c) Pure code-driven canon (Dart annotations harvested).** Rejected for the reasons already noted in v1/v2: the canon must precede code authoring (for requirements and flows), and code-name divergences from user-facing names are intentional.

The framework framings (Shape M / M+ / F) are the live options. Pick.

---

## 7. Decisions you'd be making

If you pick Shape M:
- The schema in v3 §10 simplifies (single provenance field, fewer slots).
- The bootstrap task list in v3 §11 reduces from 9 to 3.
- The skill family in v3 §5 reduces to one new skill plus minimal `requ-explore` extension + CLAUDE.md paragraph.
- Most v3 §12 open decisions become "deferred" rather than "decide now."

If you pick Shape M+:
- Most of v3's structure stays.
- Provenance simplifies to one block per concept.
- A handful of advanced modes get deferred.

If you pick Shape F:
- v3 as written is the plan; impl tasks proceed.

Pick. Then we proceed.

---

## 8. Honest reflection on the iteration itself

Three iterations of synthesis is a useful sign. Each iteration added detail in response to specific feedback — and the cumulative effect is more apparatus than the use case demands. This is a common AI-assisted-design pitfall: each round answers each question well, but the rounds compound into something heavier than any single round would have produced.

The user's question — "should we approach some things completely differently?" — is the right counter to that drift. The answer is: yes, by deciding upfront how much apparatus the *current* state of evidence and team size justifies, then sizing accordingly. Shape M is what that sizing produces; M+ and F are honest options if the user disagrees with my read of the cost/value balance.

I should have surfaced this tension earlier — probably at v2. Future synthesis iterations will benefit from an explicit cost/value re-check between rounds.
