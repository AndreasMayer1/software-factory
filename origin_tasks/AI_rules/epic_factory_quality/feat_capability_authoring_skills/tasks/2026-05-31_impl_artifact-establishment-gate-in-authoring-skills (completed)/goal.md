---
task_id: TASK-PROC-044-01-04
type: impl
parent_requirement: REQ-PROC-044-01
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-01
completed: 2026-06-01
session_completed_at: 2026-06-01T11:06:07Z
effort: M
created: 2026-05-31
after: [TASK-PROC-044-02-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06]
  sections: []
scope_description: "Implement the eager artifact-establishment gate in the capability-authoring skills"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 4d4b3e26
  file: ../../requirements.md
session_id: 9aa55573-9b2d-420e-a541-dfc65f77631c
session_account: gmail

---
# Goal: Artifact-establishment gate in the authoring skills

## Objective

Implement the eager establishment gate: when an authoring skill would emit a token absent from
the artifact registry, it proposes a registry entry the developer ratifies before authoring
proceeds — establishment of an artifact type becomes a human-authorized act.

## Requirements Summary

REQ-PROC-044-01 AC-06 (artifact establishment). The registry property (open / append /
no-overlap) and the resolve-lint backstop live in REQ-PROC-044-02; this task owns the
*establishment behavior* in the capability-authoring skills, where producers are authored.

Current requirements: ../../requirements.md

## Scope

### In Scope
- Update the capability-authoring skills — `claude-create-agent` / `claude-modify-agent`, and
  `claude-create-skill` / `claude-modify-skill` where they emit `contract.yaml` — via
  `claude-modify-skill`, so that:
  - when authoring would emit a `produces:`/`derived_from:` token, or compose an agent-name
    artifact-or-lens segment, absent from `.factory/registry/artifacts.yaml`, it eagerly
    proposes a registry entry (token + path + definition);
  - the developer ratifies / renames-to-existing / rejects before authoring proceeds;
  - the entry is appended only on ratification; a duplicate or alias is refused;
  - in automated mode the proposal escalates via `pending_feedback` rather than auto-appending.

### Out of Scope
- The registry file itself (TASK-PROC-044-02-01).
- The resolve lint backstop (TASK-PROC-044-02-02).

## Acceptance Criteria

- [x] Authoring an unknown token triggers an eager proposal (token + path + definition) the developer ratifies before authoring proceeds
- [x] Entry appended only on ratification; duplicate/alias refused
- [x] Automated mode escalates the proposal via `pending_feedback` (never auto-appends)
- [x] Initial seeding is recognized as the same gate applied to the proposed initial token set

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-02-01 | pending | Registry must exist for the gate to read/append |

## Notes

Parent is REQ-PROC-044-01 (establishment is an authoring concern), but the gate reads/writes the
044-02 registry — cross-requirement by design. Edit skills via `claude-modify-skill`.
