---
task_id: TASK-PROC-036-04
type: impl
parent_requirement: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 4
impact_reason: I4-UX
status: completed
completed: 2026-03-11
effort: M
created: 2026-03-10
after: []
release_description: "Generate AI-drafted marketing release notes with user review step"
covers:
  acceptance_criteria: []
  sections: [SEC-04]
target_package: "Transfer Data Model"
scope_description: "Implement marketing release notes generation (DE+EN) with mandatory user review step in the release skill."
requirements_version:
  commit: 8aeefd9
  file: ../requirements.md
---

# Goal: Marketing Release Notes Generation

## Objective

Implement the AI-assisted generation of user-facing marketing release notes in German and English, with a mandatory user review step before the release completes. The notes are generated from the active release's definition in RELEASES.md and follow the style rules in REQ-PROC-037.

## Requirements Summary

Covers SEC-04 (Marketing Release Notes) of REQ-PROC-036.

**BLOCKED**: REQ-PROC-037 (Marketing Writing Rules) must be defined first. The AI cannot write marketing notes without an agreed style and structure.

Current requirements: ../requirements.md

## Scope

### In Scope
- Logic in the `/release` skill to:
  - Read `description`, `goals`, and `scope_boundaries.includes` from the active release in RELEASES.md
  - Generate draft `releases/[version]/release_notes_marketing_de.md` (German, `du` form)
  - Generate draft `releases/[version]/release_notes_marketing_en.md` (English)
  - Present both drafts to the user for review
  - Allow the user to edit inline or request AI revision
  - Proceed only after explicit user approval

### Out of Scope
- Style rules themselves (REQ-PROC-037)
- Technical release notes (TASK-PROC-036-03)
- In-app Release Notes UI (SEC-08, deferred to 0.1.0)

## Acceptance Criteria

- [ ] `releases/[version]/release_notes_marketing_de.md` generated in German (`du` form, per REQ-NFUNC-013 and REQ-PROC-037)
- [ ] `releases/[version]/release_notes_marketing_en.md` generated in English
- [ ] Skill presents both drafts and waits for user approval — does NOT auto-proceed
- [ ] User can request revisions; skill regenerates on request
- [ ] Release only marked `released` after user explicitly approves

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-037-01 | pending | Explore persona rules + identify gaps |
| TASK-PROC-037-02 | pending | Update all personas with communication preferences |
| TASK-PROC-037-03 | pending | Define REQ-PROC-037 from updated personas (requ-explore) |

## Notes

- Before starting implementation, verify REQ-PROC-037 exists and its requirements.md is written.
- German version must be written naturally — not translated from English.
