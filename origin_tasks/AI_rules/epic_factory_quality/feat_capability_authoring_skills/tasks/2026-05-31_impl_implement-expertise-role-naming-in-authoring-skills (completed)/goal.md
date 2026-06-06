---
task_id: TASK-PROC-044-01-05
type: impl
parent_requirement: REQ-PROC-044-01
urgency: 3
urgency_reason: U3-ENABLER
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T14:10:18Z
effort: S
created: 2026-05-31
after: [TASK-PROC-044-02-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01]
  sections: []
scope_description: "Enforce the {expertise}-{role} naming constraint (AC-01 amendment post-044-01-01) in claude-create-agent and claude-modify-agent skills"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 4d4b3e26
  file: ../../requirements.md
session_id: dbc949aa-ff8d-46ca-9c56-c06295a588ed
session_account: web
---
# Goal: Implement {expertise}-{role} naming scheme in authoring skills

## Objective

Update `claude-create-agent` and `claude-modify-agent` via `claude-modify-skill` to enforce
the `{expertise}-{role}` naming constraint added to AC-01 after TASK-PROC-044-01-01 shipped.
The skills currently perform collision checking only; the format constraint and the role/expertise
classification logic are absent.

## Requirements Summary

REQ-PROC-044-01 AC-01 was amended (commit `4d4b3e26`) to require that every agent name follows
`{expertise}-{role}` where `role` is drawn from the closed set {writer, transformer, reviewer,
classifier} and `expertise` resolves against the artifact registry (REQ-PROC-044-02).
TASK-PROC-044-01-01 predates this amendment and implements only the older collision-check
sub-rule — it does not enforce the format or the role/expertise semantics.

For complete requirements at task creation time:
```
git show 4d4b3e26:requirements_tasks/process/AI_rules/epic_factory_quality/feat_capability_authoring_skills/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope

- Modify `claude-create-agent/SKILL.md` (via `claude-modify-skill`) to add format enforcement
  to the existing §2 Naming section:
  - The proposed name must match `{expertise}-{role}` (exactly two kebab-case segments; the role
    is always the suffix).
  - The role segment must be in the closed set {writer, transformer, reviewer, classifier}; any
    other value is rejected with an explanation of the 2×2 axis logic.
  - If the agent's function maps to zero roles or two-or-more roles, the skill stops and asks the
    developer to clarify which single output-type axis applies.
  - The expertise segment must resolve against `.factory/registry/artifacts.yaml`; an unresolved
    expertise token delegates to the establishment gate (TASK-PROC-044-01-04 behavior).
  - The existing collision check becomes a sub-rule executed after format validation passes.
- Modify `claude-modify-agent/SKILL.md` (via `claude-modify-skill`) to enforce the same format
  check when a rename is requested (the existing rename path re-runs collision; add format
  validation before the collision sub-check).

### Out of Scope

- The artifact registry file itself (TASK-PROC-044-02-01).
- The establishment gate implementation (TASK-PROC-044-01-04) — this task only triggers it.
- Retrofitting existing `ui-scribble-*` agent names — those are deferred to the REQ-PROC-032 strand.
- Updating contract.yaml sidecar names for already-authored agents (no renames issued).

## Acceptance Criteria

- [x] `claude-create-agent` §2 Naming enforces `{expertise}-{role}` format; rejects non-conforming names before writing
- [x] Role segment validated against closed set {writer, transformer, reviewer, classifier}; zero-or-multi-role case causes skill to stop and ask developer
- [x] Expertise segment resolved against registry; unknown token delegates to establishment gate
- [x] Collision check retained as sub-rule (executed after format validation)
- [x] `claude-modify-agent` rename path applies the same format check
- [x] Both skills modified via `claude-modify-skill` (no direct SKILL.md edits)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-02-01 | pending | Registry must exist before expertise tokens can be validated |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-044-02-01](../../feat_artifact_model/tasks/2026-05-31_impl_create-and-seed-artifact-registry/goal.md) | Predecessor — registry is the source of truth for expertise token resolution |
| [TASK-PROC-044-01-04](../2026-05-31_impl_artifact-establishment-gate-in-authoring-skills/goal.md) | Sibling — establishment gate is triggered when expertise token is unknown |
| [TASK-PROC-044-01-01](../2026-05-31_impl_create-claude-agent-authoring-skills%20(completed)/goal.md) | Predecessor — skills being modified were delivered here; read what was shipped |

## Notes

This task carries only AC-01 because that is the sole AC that was substantively amended after
044-01-01 shipped. The verify task (TASK-PROC-044-01-03) will re-audit AC-01 once this lands.
