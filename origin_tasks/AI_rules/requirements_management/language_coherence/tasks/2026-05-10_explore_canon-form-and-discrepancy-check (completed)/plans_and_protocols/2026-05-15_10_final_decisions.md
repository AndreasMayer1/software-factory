# Final Decisions — Closing the Design Phase

Date: 2026-05-15
Model: Opus 4.7
Status: Design phase complete. Implementation tasks follow.

This document records the user's final decisions and the resulting closures. Together with v3 (`2026-05-15_08_opus_synthesis_v3.md`) it constitutes the design brief for the bootstrap implementation.

---

## 1. Decisions taken

### 1.1 Shape — Full (v3 as written)

The user picked **Shape F**. Reasons given:
- Implementation by LLM is fast (~3 hours) once the design is settled; the heavy work was the design.
- This project has a dual purpose — building the app AND learning AI-assisted software development. Over-engineering is acceptable when it earns learning value.
- Evidence-level tracking has real future value: when actual user research arrives, the LLM/app-provider must be able to judge whether existing decisions can be overwritten or need careful re-weighing. That judgment depends on knowing each decision's provenance.

The minimal-shape recommendation in the step-back reflection (§5) is recorded but not adopted.

### 1.2 Primary language stays English

Gap 1.9 (English-as-primary lock-in) is closed: the project will not change the primary language. Schema versioning (§9.9) remains as cheap insurance.

### 1.3 Audience axis — new schema dimension

Gap 1.10 (mixed registers) is real and the user confirmed it. The product has two distinct audiences:

- **Therapist audience** — professional users with psychological-studies training and clinical vocabulary. The product surface they use can carry academic terminology.
- **Lay audience** — non-professional users. Two subgroups:
  - *Therapy clients* — clients of a therapist who use the app as part of treatment
  - *Self-users* — people who download the app directly from the app store without a therapist relationship
  Both sub-groups share the same vocabulary register. The distinguishing factor between them is the therapist-relationship (relevant for feature scope, not for language).

Schema extension (additive to v3):

```yaml
- id: CONCEPT-PLAN
  name_canonical: "Plan"           # lay register (default; broader audience)
  aliases:
    de: "Plan"
    code: [...]
    legacy: []
  audience_variants:               # NEW — empty when audiences share the canonical name
    therapist: {}                  # empty → use name_canonical
    self_user: {}                  # empty → use name_canonical (defaults to lay)
  # When a concept's register differs, audience_variants carries the override:
  #
  # audience_variants:
  #   therapist:
  #     en: "Cognitive Distortion"
  #     de: "kognitive Verzerrung"
  #     evidence_level: inferred
  #     sources: []
```

Defaults and conventions:

| Rule | Definition |
|---|---|
| Canonical-name default register | **lay** (broader audience) |
| Audience override | `audience_variants.<audience>` non-empty |
| Audience identifiers | `therapist`, `self_user` (the two non-default registers). `client` is NOT a separate audience axis — therapy clients share the lay register; the distinction between therapy clients and self-users is a feature-scope distinction, not a language distinction. |
| Bootstrap impact | First 6–10 bootstrap concepts (Plan, Client, HandOver, Receive, etc.) are likely register-uniform. `audience_variants` will be empty for all of them. The mechanism is there for future psychological-construct concepts. |

The `provenance.<lang>.level` ladder from v3 §1 stays unchanged. When an audience override exists, it carries its own evidence-level under `audience_variants.<audience>.evidence_level` so that the therapist-register choice can be `proto-evidenced` while the lay choice is `inferred`, or vice versa.

### 1.4 Skill name — `ux-write-canon-concept`

Decision: matches the existing `ux-write-persona` / `ux-write-scenario` pattern. Single skill covers add + modify + provenance-upgrade + rename-trigger.

### 1.5 Translation-mechanism task — created at low priority

Per v3 §15 question 2: I will create the explore task during the bootstrap task-creation step, scheduled at low priority (`urgency: 1`). Parent: REQ-NFUNC-013. It sits in the backlog and surfaces only when a third language gets onto the roadmap.

### 1.6 Smaller defaults adopted

From v3 §12 NEW-* lines:

| Decision | Adopted |
|---|---|
| v3-3 — bidirectional `references: [CONCEPT-*]` in user-needs artefact YAML | DEFERRED to v3.5 (separate cascade-impact change) |
| v3-4 — `constrained_by` field on forbidden_synonyms | Adopted |
| v3-5 — `examples:` per language (optional field) | Adopted as optional |
| v3-6 — `schema_version: 1` | Adopted |
| v3-7 — Cascade A folded into `ux-write-canon-concept` | Adopted with safety valve: if the rename touches >10 files, the skill creates an impl task instead of inline editing |

### 1.7 Self-Users as audience documentation

The user introduced **Self-User** as a distinct user category (downloads app without therapist). This is a *persona-shaped* distinction. Two follow-up actions:

1. Check whether a `PERSONA-self-user` (or similar) already exists in `requirements_user_needs/personas/`. If not, flag for `ux-write-persona` follow-up.
2. The canon's audience axis (§1.3) does NOT include `self_user` as a register-distinct audience — both therapy clients and self-users share lay register. The persona-level distinction is about feature scope and user goals, not language. Recorded in canon `README.md`.

---

## 2. Bootstrap implementation task list (finalized)

Carry-forward from v3 §11 with §1.3 audience and §1.6 adopted defaults applied:

| # | Task title | Type | Effort | Skill to use during impl | After |
|---|---|---|---|---|---|
| **T1** | Create `concept_canon/` folder structure + empty seeds + `generate_concept_canon_md.py` (also generates `concept_canon.index.yaml`) | impl | S | `claude-write-script` + `task-resolve` | — |
| **T2** | Coordination read of TASK-PROC-046 Tier-0 (`-01`, `-02`, `-08`, `-14`); document or create shared `scripts/quality/_arb_parser.py` | analyze | S | `task-resolve` | — (parallel with T1) |
| **T3** | Author bootstrap canon for `feat_therapist_transfer_ui` — 6–10 concepts with multi-language provenance, recorded `aliases.code` divergences (incl. SharePlanTemplateRequested ↔ HandOver, SelectRole ↔ SwitchProfileRequested, DataBeamDiscarded ↔ DataBeamUnderDurationExit), `audience_variants` blocks present (mostly empty for this feature) | impl | M | `task-resolve` | T1 |
| **T4** | Create `ux-write-canon-concept` skill (~50 lines; add/modify/upgrade-provenance/rename-trigger; concurrent-edit lock; ID generation convention `CONCEPT-<UPPER-KEBAB>`; duplicate-check heuristic; rename cascade with >10-files safety valve) | impl | M | `claude-create-skill` | T1 |
| **T5** | Implement `scripts/user_needs/check_canon.py` — 4 walkers (requirements md, ARB, translation_context placeholder, Dart presentation), AC-03 verb-precision check, `--json`, `--validate-references`, `--code-coverage`, audience-aware lookups | impl | M | `claude-write-script` | T1, T2, T3 |
| **T6** | Extend caller skills: `requ-explore`, `ux-create-flow`, `ux-write-scenario` (conditional — future-state scenarios only; explicit note in skill description excludes as-is scenarios), `code-simple`, `code-complex`, `ui-create-scribble`, `ui-create-scribble-improve`. Plus add canon-impact step to `product-intake` between Step 4 (User Flows) and Step 5 (Requirements). | impl | M | `claude-modify-skill` (per skill; batchable) | T4 |
| **T7** | Document workflow in `concept_canon/README.md` (incl. audience axis, self-user note, bootstrap graceful-degradation rule, extension ladder); one-line entry in `CLAUDE.md` §10 | impl | S | `task-resolve` | T1–T6 |
| **T8** | Wire `check_canon.py` into release pre-flight (`scripts/release/check_release_preconditions.py`) | impl | S | `claude-write-script` | T5 |
| **T9 (low-priority, optional)** | Explore task: LLM-driven translation skill consuming canon + translation_context (deferred until 3rd language is on the roadmap; urgency: 1) | explore | M | `task-resolve` | — (independent backlog item) |

---

## 3. What remains uncertain (carried unchanged)

From v3 §13:

- Provenance-level transitions in practice (frequency of upgrades unknown until beta)
- Cross-language canon flips (audit messaging must be language-aware)
- `ui-create-scribble` integration cost (alpha-phase skill, first real exercise)
- Cascade A complexity (placeholders, ICU plurals, format strings may need extra logic)
- `_arb_parser.py` ownership (resolved at T2)
- AC-03 verb-precision false-positive rate (empirical; tuned over time)
- Schema migration cost when versioning increments (first migration years away)

From this iteration:

- Audience-variant adoption rate (most bootstrap concepts will not exercise the dimension; the mechanism is forward-looking)
- Self-user persona — whether one already exists or needs to be authored

---

## 4. Honest note on the iteration cycle

Three full synthesis rounds plus a step-back reflection plus this addendum is heavier than typical. The user's grounding (§3 of their last feedback): defining things completely up-front is faster overall than iterating impl, because LLM impl is fast but rework across many files is slow. The over-engineering is also intentional — the project doubles as an AI-assisted-development learning exercise.

Both reasons are sound. The reflection in `2026-05-15_09_step_back_reflection.md` §8 stands as a process note for future explore tasks: explicit cost/value re-checks between synthesis rounds would help, but they are not always the right gate. In this case, the user's stated goals (learning + completeness) shift the optimal point of the cost/value curve toward more apparatus than my reflection assumed.

Proceeding to task creation.
