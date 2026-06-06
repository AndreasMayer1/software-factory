---
task_id: TASK-PROC-049-04
type: impl
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T13:22:16Z
effort: M
created: 2026-05-15
after: [TASK-PROC-049-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: []
target_package: ""
scope_description: "Author 6-10 bootstrap canon entries for feat_therapist_transfer_ui with multi-language provenance and recorded alias divergences"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 5747c0c2
  file: ../../requirements.md
session_id: 2d8512f3-9328-4e5d-92ed-ec6ca672fd89
session_account: gmail
---

# Goal: Bootstrap canon for feat_therapist_transfer_ui

## Objective

Author the first 6–10 entries in `requirements_user_needs/concept_canon/concept_canon.yaml`. The bootstrap covers the `feat_therapist_transfer_ui` feature surface — the cleanest end-to-end test case for the canon mechanism because it spans:

- A clearly-defined user-facing object set (Plan, Client, Therapist, HandOver, Receive).
- An interaction object (HandOverDialog).
- Multiple known code-level alias divergences that the canon must record.

This task proves the schema works in practice and produces enough material for T5's `check_canon.py` audit script to detect real drift.

## Background

The canon's schema is fully specified in design synthesis v3 §10. The audience axis (`audience_variants`) and the v3-4 (`constrained_by` on `forbidden_synonyms`) / v3-5 (`examples:` per language) / v3-6 (`schema_version: 1`) additions are confirmed in:

- `2026-05-15_10_final_decisions.md` §1.3 (audience), §1.6 (adopted defaults).
- `2026-05-15_08_opus_synthesis_v3.md` §10 (full schema).

For complete requirements at task creation time:
```
git show 5747c0c2:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

## Requirements Summary

Covers:
- AC-01 — by populating the canonical source for the bootstrap feature.
- AC-02 — by recording `aliases.code` for every known code-level divergence so the canon is the single authoritative naming source.

## Scope

### In Scope

Author at minimum these concepts (more allowed up to ~10):

| Canonical name (lay register, EN) | Type | Notes |
|---|---|---|
| Plan | object | core therapy plan artefact |
| Client | object | the person receiving therapy |
| Therapist | object | the professional user |
| HandOver | operation | therapist initiates plan handover to client |
| Receive | operation | client receives the handover |
| HandOverDialog | object | the modal dialog used for handover |

For each entry, follow v3 §10 schema with ALL fields:

- `id`: `CONCEPT-<UPPER-KEBAB>` per v3 §9.1 (e.g. `CONCEPT-HAND-OVER`).
- `type`: `object` / `operation` / `state`.
- `status: active`.
- `name_canonical`: lay register, English (per final_decisions §1.2 / §1.3).
- `aliases.de`: German equivalent.
- `aliases.code`: record ALL known divergences. Must at minimum include:
  - `SharePlanTemplateRequested` (event name diverging from HandOver)
  - `DataBeamBloc`, `DataBeamScannerScreen`, `DataBeamDiscarded`, `DataBeamUnderDurationExit`
  - `SelectRole` / `SwitchProfileRequested`
  - `TransferChunk`
  (The agent must walk `lib/features/therapist/data_transfer/` and `lib/features/client/data_receive/` to confirm these and discover any others.)
- `description`.
- `states`: enumerated user-visible states (if any).
- `operations`: enumerated named operations (if any).
- `forbidden_synonyms`: per v3-4 with `lang`, `note`, and optional `constrained_by`.
- `related`: list of CONCEPT-* IDs (cross-links inside the canon).
- `audience_variants`: empty for register-uniform entries; the mechanism must be present per final_decisions §1.3 (i.e. the key exists with `therapist: {}` and `self_user: {}` even when empty).
- `examples`: optional per v3-5.
- `provenance`: per-language. Mostly `inferred` for EN, `proto-evidenced` for DE where source IDs exist. Record `sources: []` lists explicitly.
- `introduced_by: REQ-PROC-049`.

Process:
1. Walk `lib/features/therapist/data_transfer/` and `lib/features/client/data_receive/` thoroughly to identify all aliasable identifiers.
2. Author entries in `requirements_user_needs/concept_canon/concept_canon.yaml`.
3. Run `python3 scripts/user_needs/generate_concept_canon_md.py` (created in T1) to regenerate `concept_canon.md` and `concept_canon.index.yaml`.
4. Sanity-check that no two entries collide and that all `related` IDs resolve.

### Out of Scope

- Building the audit check (T5 / TASK-PROC-049-06).
- Updating downstream skills (T6 / TASK-PROC-049-07).
- Authoring concepts for other features.
- Rename cascades — no production code is renamed in this task. Divergences are recorded as `aliases.code`, not eliminated.

## Acceptance Criteria

- [x] 6–10 entries authored in `concept_canon.yaml`, all valid per v3 §10 schema.
- [x] Every entry has `audience_variants` block (possibly empty per audience).
- [x] Every required alias divergence (SharePlanTemplateRequested, DataBeam*, SelectRole/SwitchProfileRequested, TransferChunk) is recorded under the appropriate concept's `aliases.code`.
- [x] All `related` cross-references resolve to existing canon IDs.
- [x] `concept_canon.md` and `concept_canon.index.yaml` regenerated via the T1 generator.
- [x] `lib/features/therapist/data_transfer/` and `lib/features/client/data_receive/` have been walked (note in a brief `plans_and_protocols/` log if useful).

## Implementing Skill

`task-resolve` — the work is authoring per a fully-specified schema. No new design is needed.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-049-02 | pending | T1 creates the folder + generators consumed here. |

## Notes

- Lay register is the default canonical register per final_decisions §1.3. Most or all bootstrap entries will be register-uniform (no therapist-specific overrides needed). The empty `audience_variants` blocks document that the mechanism exists.
- Do NOT redesign the schema. v3 §10 is the source of truth.
- If a divergence cannot be classified (e.g. it might be a separate concept rather than an alias), record it as a candidate in `plans_and_protocols/` and proceed with best judgment.
