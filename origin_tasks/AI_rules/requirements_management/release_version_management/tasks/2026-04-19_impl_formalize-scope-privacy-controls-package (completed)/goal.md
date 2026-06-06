---
task_id: TASK-PROC-034-16
type: impl
parent_requirement: REQ-PROC-034
urgency: 5
urgency_reason: U5-BLOCK
impact: 5
impact_reason: I5-ENAB
status: completed
effort: XS
created: 2026-04-19
started: 2026-04-20
completed: 2026-04-20
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-04]
scope_description: "Add a new RELEASE_BACKLOG.md package entry for FLOW-003 'Scope & Privacy Controls' chunk via release-plan Action 4b"
release_description: "Formalizes client data scope selection and exclusion marker feature as a release package."
opus_recommended: false
worktree_path: ""
requirements_version:
  commit: 3e9fba52
  file: ../requirements.md
---

# Goal: Formalize FLOW-003 "Scope & Privacy Controls" as a Backlog Package

## Objective

Run `release-plan → Action 4b` to create a new `RELEASE_BACKLOG.md` package entry for the unformalized FLOW-003 chunk **"Scope & Privacy Controls"**.

This chunk was detected as unformalized during `requ-assign-packages` — no matching backlog package exists for it.

## Scope

### In Scope
- Run `release-plan → Action 4b`
- Create a new package entry in `RELEASE_BACKLOG.md` for FLOW-003 "Scope & Privacy Controls"
- Follow SEC-01 package naming rules (max 4 words, role-subject convention, 5 stakeholder tests)

### Out of Scope
- Assigning requirements to the new package (that is handled by `requ-assign-packages` after this task)
- Changes to any flow or requirement files

## Chunk Details

**Flow**: FLOW-003 (session_start_data_transfer)
**Chunk label**: "Scope & Privacy Controls"
**Covers** (from flow.md release_scope):
- Exception 3.1 (client decline / mid-transfer exit)
- Exception 3.2 (scope narrowing + exclusion marker)
- All Adaptive UI Rules

**Why no existing package matched**: The RELEASE_BACKLOG.md has no package sourced from FLOW-003 covering scope control / exclusion markers during QR transfer. "Privacy Controls" (REQ-FUNC-006) is about GDPR/data deletion, not transfer scope. "Transfer Content Selection" is FLOW-004 (file transfer), not FLOW-003 (QR transfer).

## Acceptance Criteria

- [ ] A new package entry exists in RELEASE_BACKLOG.md with source: flow, ref: FLOW-003, scope: "Scope & Privacy Controls"
- [ ] Package name passes the 5 stakeholder tests from `package_assignment_rules.md`
- [ ] Package is positioned correctly relative to other FLOW-003 packages

## Notes

After this task is complete, re-run `requ-assign-packages` so the package can be used for assignment.
