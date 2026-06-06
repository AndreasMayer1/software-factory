---
task_id: TASK-PROC-049-05
type: impl
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T13:30:33Z
effort: M
created: 2026-05-15
after: [TASK-PROC-049-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02]
  sections: []
target_package: ""
scope_description: "Create the ux-write-canon-concept skill that adds, updates, upgrades provenance, and triggers rename cascades on canon concepts"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 5747c0c2
  file: ../../requirements.md
session_id: 3dd5d772-1313-47f6-96ec-b1a3568c7635
session_account: web
---

# Goal: Create ux-write-canon-concept skill

## Objective

Author a new project skill at `.claude/skills/ux-write-canon-concept/skill.md` (≈50 lines) that owns all mutations to `requirements_user_needs/concept_canon/concept_canon.yaml`. The skill covers four operations per design synthesis v3 §5.2:

1. Add a new concept.
2. Update fields on an existing concept.
3. Upgrade provenance level (e.g. `inferred` → `proto-evidenced` → `evidenced`).
4. Trigger a rename cascade.

The skill is the gatekeeper: future caller skills (T6 / TASK-PROC-049-07) invoke this skill rather than touching the YAML directly.

## Background

Skill name matches the existing `ux-write-persona` / `ux-write-scenario` pattern (final_decisions §1.4). Full requirements for the skill come from v3 §5.2 and §9 (mechanics):

- v3 §9.1 — ID generation convention: `CONCEPT-<UPPER-KEBAB>`.
- v3 §9.2 — concurrent-edit lock via `.canon-lock` file.
- v3 §9.8 — duplicate-check heuristic (normalized comparison).
- final_decisions §1.6 v3-7 — rename-cascade safety valve: if a rename touches more than 10 files, the skill creates an impl task instead of editing inline.
- final_decisions §1.3 — audience axis must be explicit in the skill's description.

For complete requirements at task creation time:
```
git show 5747c0c2:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

## Requirements Summary

Covers AC-01 (gatekeeper for canonical-source mutations) and AC-02 (rename-cascade keeps canon-aligned).

## Scope

### In Scope

Use the `claude-create-skill` skill (MANDATORY per CLAUDE.md) to author `.claude/skills/ux-write-canon-concept/skill.md`. Content requirements:

- Skill description (short, token-efficient per CLAUDE.md §7 "Skills"):
  - Must explicitly mention the **audience axis** from final_decisions §1.3 (therapist register vs. lay register).
  - Must state this skill is **REQUIRED** for any new user-facing concept introduction.
- Operations (the four from v3 §5.2): add / update / upgrade-provenance / rename-cascade.
- `.canon-lock` concurrent-edit lock per v3 §9.2.
- ID-generation convention `CONCEPT-<UPPER-KEBAB>` per v3 §9.1.
- Duplicate-check heuristic per v3 §9.8 (normalized name comparison against existing entries before insert).
- Rename-cascade safety valve per final_decisions §1.6 v3-7:
  - Skill must enumerate files touched by the rename before applying it.
  - If the count is >10, the skill MUST NOT edit inline. Instead it creates a new impl task (under REQ-PROC-049 or the closest matching requirement) describing the rename and exits.
  - If the count is ≤10, the skill edits inline.
- After every successful operation, the skill regenerates `concept_canon.md` + `concept_canon.index.yaml` via `scripts/user_needs/generate_concept_canon_md.py`.
- No `///` WHY comments anywhere in the skill (per CLAUDE.md §5). Inline `(reason)` parentheticals only.

### Out of Scope

- Calling the skill from anywhere — wiring into `requ-explore`, `ux-create-flow`, etc. lives in T6 (TASK-PROC-049-07).
- Implementing the check_canon.py audit script (T5).
- README content (T7).

## Acceptance Criteria

- [x] `.claude/skills/ux-write-canon-concept/skill.md` exists, created via `claude-create-skill`.
- [x] Description names the audience axis and the "required for new user-facing concept" rule.
- [x] All four operations (add / update / upgrade-provenance / rename-cascade) are documented.
- [x] `.canon-lock` mechanic is documented.
- [x] `CONCEPT-<UPPER-KEBAB>` ID convention is documented.
- [x] Duplicate-check heuristic is documented.
- [x] Rename-cascade safety valve (>10 files → create task) is documented and enforced.
- [x] Skill regenerates `concept_canon.md` + `concept_canon.index.yaml` after every successful operation.
- [x] No `///` WHY comments in the skill body.

## Implementing Skill

`claude-create-skill` (MANDATORY per CLAUDE.md for new skill creation).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-049-02 | pending | T1 must exist so the skill knows what folder/files to mutate. |

## Notes

- Token efficiency matters per CLAUDE.md §7 — keep description short, body ≈50 lines.
- The skill is read into context every time a caller skill triggers it. Avoid prose; favor instructions.
- Do not over-engineer the rename cascade. The safety valve is the fallback for complex cases; the inline path handles simple cases only.
