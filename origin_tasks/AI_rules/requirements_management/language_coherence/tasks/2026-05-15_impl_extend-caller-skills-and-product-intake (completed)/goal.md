---
task_id: TASK-PROC-049-07
type: impl
parent_requirement: REQ-PROC-049
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-05-16
completed: 2026-05-16
session_completed_at: 2026-05-16T14:16:23Z
effort: M
created: 2026-05-15
after: [TASK-PROC-049-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-04]
  sections: []
target_package: ""
scope_description: "Extend requ-explore, ux-create-flow, ux-write-scenario, code-simple, code-complex, ui-create-scribble, ui-create-scribble-improve, and product-intake to invoke ux-write-canon-concept where appropriate"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 5747c0c2
  file: ../../requirements.md
session_id: d21d0913-6d70-4214-a95a-d5af499098ae
session_account: gmail
---

# Goal: Extend caller skills + product-intake

## Objective

Wire `ux-write-canon-concept` (from T4 / TASK-PROC-049-05) into all skills that introduce or reference user-facing concepts. Per design synthesis v3 §5.3 and §6.1 (Cascade C). After this task, no caller skill can introduce a user-facing noun/verb/state without consulting or extending the canon.

## Background

Design references:

- `2026-05-15_08_opus_synthesis_v3.md` §5.3 (per-skill instructions) and §6.1 (Cascade C / product-intake insertion).
- `2026-05-15_10_final_decisions.md` §1.4 (skill name) and §2 row T6 (this task's scope).
- v2 §8 feedback: `ux-write-scenario` must distinguish AS-IS (pre-app) scenarios from FUTURE-state scenarios.

For complete requirements at task creation time:
```
git show 5747c0c2:requirements_tasks/process/AI_rules/requirements_management/language_coherence/requirements.md
```

Current requirements: ../../requirements.md

## Requirements Summary

- AC-01 — caller skills route through the canon's gatekeeper.
- AC-02 — every artefact creation hooks into canon-alignment.
- AC-04 — `translation_context` entries (touched via `ui-create-scribble`) reference canonical concepts.

## Scope

### In Scope

Use the `claude-modify-skill` skill (MANDATORY per CLAUDE.md) once per affected skill. Add to each:

1. **`requ-explore`** — add: "When the requirement body introduces a user-facing noun/verb/state not in `concept_canon.yaml`, invoke `ux-write-canon-concept`."

2. **`ux-create-flow`** — same line, scoped to flow step labels.

3. **`ux-write-scenario`** — CONDITIONAL. Description must explicitly state:
   > "Invoke `ux-write-canon-concept` ONLY for FUTURE-state scenarios (App-Nutzung). NEVER for AS-IS (pre-app) scenarios."
   (Per v2 §8 feedback. AS-IS scenarios describe pre-product user behaviour and do not commit the product to vocabulary.)

4. **`code-simple`** — DDD-light enforcement per v3 §8.2: prefer canonical names for classes, methods, BLoC events/states, user-facing strings. Invoke `ux-write-canon-concept` when a new user-facing concept is introduced.

5. **`code-complex`** — same as `code-simple`.

6. **`ui-create-scribble`** — when generating labels, consult canon. Add HTML-comment markers `<!-- canon: CONCEPT-X -->` per v3 §4 (so the audit script and reviewers can trace label → canon).

7. **`ui-create-scribble-improve`** — same as `ui-create-scribble`.

8. **`product-intake`** — insert a "Canon impact" step between current Step 4 (User Flows) and Step 5 (Requirements), per v3 §6.1 Cascade C. Step content: check whether the proposed change introduces or renames any user-facing concept; if yes, route through `ux-write-canon-concept`.

### Out of Scope

- README.md (T7 / TASK-PROC-049-08).
- CLAUDE.md edits (T7).
- Cross-reference updates to other requirements (T7).
- Authoring new canon entries — the skills now know to invoke `ux-write-canon-concept`, but the actual concept-creation happens when those skills are next used.

## Acceptance Criteria

- [x] All 8 skill files have been modified via `claude-modify-skill`.
- [x] Each modification is the minimum content needed (no gratuitous changes).
- [x] `ux-write-scenario` modification explicitly excludes AS-IS scenarios.
- [x] `ui-create-scribble*` modifications include the `<!-- canon: CONCEPT-X -->` marker convention.
- [x] `product-intake` has a "Canon impact" step between current Step 4 and Step 5.
- [x] `.claude/skills/INDEX.md` and `.claude/skills/factory_flows.md` are synced (handled by `claude-modify-skill`).

## Implementing Skill

`claude-modify-skill` (MANDATORY per CLAUDE.md for any skill modification) — invoked once per affected skill (8 invocations total).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-049-05 | pending | `ux-write-canon-concept` must exist before callers reference it. |

## Notes

- Skill descriptions are token-sensitive (CLAUDE.md §7). Keep each added line short.
- No `///` WHY comments anywhere in skill bodies.
- The eight skill files are independent; `claude-modify-skill` invocations can be batched logically but each is its own operation.
