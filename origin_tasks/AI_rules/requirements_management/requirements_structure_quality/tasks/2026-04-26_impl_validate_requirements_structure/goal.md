---
task_id: TASK-PROC-045-02
type: impl
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: pending
effort: M
created: 2026-04-26
after: [TASK-PROC-045-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-06]
  sections: []
scope_description: "Extend structural validation script to enforce AC-01 through AC-05, AC-09, AC-10 — the foundation that TASK-PROC-045-04 and TASK-PROC-045-05 depend on"
release_description: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
---

# Goal: Extend Structural Validation Script

## Objective

Extend `scripts/validate_epic_requirements.py` to enforce all script-checkable rules defined in REQ-PROC-045 (AC-01 through AC-05, AC-09, AC-10). This script is the shared foundation that the skill-integration tasks (TASK-PROC-045-04, TASK-PROC-045-05) depend on.

## Scope

### In Scope
- Extend `scripts/validate_epic_requirements.py` with checks for AC-01 through AC-05, AC-09, and AC-10 (the two existing checks for epic body length and feat_* folder presence remain)
- Clear, actionable error messages that name the violating folder and the rule violated
- Handle the AC-01 grandfathering clause correctly: epics whose only requirement-bearing children are non-prefixed folders pre-dating 2026-04-26 must not be flagged as AC-01 violations
- Smoke verification: run the script against the current `requirements_tasks/` corpus and document all violations found as known pre-existing structural debt (do not fix them — record them)
- If the script is renamed (e.g., to `validate_requirements_structure.py`), update CLAUDE.md "Generated Files" table and all referencing skills

### Out of Scope
- Fixing pre-existing violations surfaced by the new checks — record only
- Skill integration (handled by TASK-PROC-045-04 and TASK-PROC-045-05)
- Performance optimization

## New Checks to Implement

| AC | Check | Grandfathering |
|---|---|---|
| AC-01 | epic_* without feat_* children (and not all children are grandfathered non-prefixed) | Yes — see scope |
| AC-02 | feat_* without requirements.md | None |
| AC-03 | feat_* as direct child of category root | None |
| AC-04 | epic_* nested inside epic_* | None |
| AC-05 | id: value in requirements.md not in _meta/id_registry.md | None |
| AC-09 | non-prefixed folder inside epic_* with requirements.md, created after 2026-04-26 | Folders pre-dating 2026-04-26 are exempt |
| AC-10 | epic_* without requirements.md | None |

## Acceptance Criteria

- [ ] AC-06: Script enforces all checks listed above; existing checks (body ≤ 90 lines, feat_* folders listed in ## Features) are preserved
- [ ] Script exits 0 when no violations found, non-zero otherwise
- [ ] Output clearly identifies: violation type, folder path, applicable rule (AC-ID)
- [ ] Smoke run output documented in `plans_and_protocols/` showing known pre-existing violations

## Notes

- Depends on TASK-PROC-045-01 being completed and requirements.md approved.
- Prefer additive check functions (one function per rule) so a bug in one check cannot silence others.
- The grandfathering date for AC-09 is 2026-04-26 — use folder creation date heuristic (git log --follow or fall back to current date comparison if git history unavailable).
