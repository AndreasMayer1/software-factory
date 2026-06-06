---
task_id: TASK-PROC-049-02
type: impl
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
effort: S
created: 2026-05-15
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T12:52:36Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01]
  sections: []
target_package: ""
scope_description: "Bootstrap concept_canon/ folder, empty seed files, and the generator that emits concept_canon.md + concept_canon.index.yaml"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 5747c0c2
  file: ../../requirements.md
session_id: 259817ab-ea6d-407f-9df2-967c6e0c9634
session_account: web
---

# Goal: Create concept_canon/ folder structure + seed files + generators

## Objective

Lay the foundation for the canon-coherence bootstrap (REQ-PROC-049):

1. Create the new top-level folder `requirements_user_needs/concept_canon/` with:
   - `README.md` — placeholder (full content authored by T7 / TASK-PROC-049-08).
   - `concept_canon.yaml` — empty seed with frontmatter `schema_version: 1` and an empty `concepts: []` list.
   - `concept_canon.index.yaml` — empty (will be regenerated).
2. Implement `scripts/user_needs/generate_concept_canon_md.py`:
   - Parses `concept_canon.yaml`.
   - Emits the human-readable `concept_canon.md` alongside the lightweight `concept_canon.index.yaml`.
   - Per design synthesis v3 §7.4 (Markdown generator) and §7.5 (index file shape).

This task is the foundation that T3 (canon authoring), T4 (skill creation), and T5 (audit script) all build on.

## Background

REQ-PROC-049 introduces a single canonical source for every user-facing concept the product commits to. The full design is in:

- `requirements_tasks/process/AI_rules/requirements_management/language_coherence/tasks/2026-05-10_explore_canon-form-and-discrepancy-check/plans_and_protocols/2026-05-15_10_final_decisions.md`
- `requirements_tasks/process/AI_rules/requirements_management/language_coherence/tasks/2026-05-10_explore_canon-form-and-discrepancy-check/plans_and_protocols/2026-05-15_08_opus_synthesis_v3.md` (especially §7 generator + §10 schema)

For complete requirements at task creation time:
```
git show 5747c0c2:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

## Requirements Summary

Covers AC-01: "A single canonical source identifies, for every user-facing concept the product commits to, the concept's name, the states it can be in, and the named operations a user can perform on it."

## Scope

### In Scope

- Create `requirements_user_needs/concept_canon/` directory.
- Write placeholder `concept_canon/README.md` (one-line note saying full content lands with TASK-PROC-049-08).
- Write empty seed `concept_canon/concept_canon.yaml` with the v3 §10 frontmatter:
  ```yaml
  schema_version: 1
  concepts: []
  ```
- Write empty seed `concept_canon/concept_canon.index.yaml`.
- Implement `scripts/user_needs/generate_concept_canon_md.py` via the `claude-write-script` skill. The script must:
  - Accept input path `requirements_user_needs/concept_canon/concept_canon.yaml`.
  - Output `concept_canon.md` (human-readable, per v3 §7.4 layout).
  - Output `concept_canon.index.yaml` (lightweight lookup index, per v3 §7.5 shape).
  - Handle the empty-concepts case gracefully (emits a stub message).
  - Register itself in `CLAUDE.md` §11 Generated Files (T7 will do the §11 update; this task only writes the script).
- Run the script once against the empty canon to verify the empty-state path works; commit the generated files alongside the seed.

### Out of Scope

- Authoring actual canon entries (T3 / TASK-PROC-049-04).
- Writing the full README content (T7 / TASK-PROC-049-08).
- Updating CLAUDE.md (T7 / TASK-PROC-049-08).
- The check_canon.py audit script (T5 / TASK-PROC-049-06).

## Acceptance Criteria

- [x] `requirements_user_needs/concept_canon/` exists with README.md, concept_canon.yaml, concept_canon.index.yaml.
- [x] `concept_canon.yaml` parses as valid YAML and contains `schema_version: 1` plus empty `concepts: []`.
- [x] `scripts/user_needs/generate_concept_canon_md.py` exists, follows the project's script conventions, and was created via the `claude-write-script` skill.
- [x] Running the generator against the empty canon produces a valid `concept_canon.md` and `concept_canon.index.yaml` without crashing.
- [x] No edits to skills, requirements files, or CLAUDE.md (those land in later tasks).

## Implementing Skill

Primary: `claude-write-script` for the Python generator. Use `task-resolve` to coordinate the rest of the file creation if needed.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | None; T1 is the foundation task. |

## Notes

- The `concept_canon.yaml` schema is defined in detail in v3 §10. Do NOT redesign — implement as written.
- The empty `concepts: []` seed is intentional. Bootstrap entries are authored in T3 once the generators and folder exist.
- The generator outputs are listed in CLAUDE.md §11 Generated Files but the table update is owned by T7 — do not edit CLAUDE.md here.
