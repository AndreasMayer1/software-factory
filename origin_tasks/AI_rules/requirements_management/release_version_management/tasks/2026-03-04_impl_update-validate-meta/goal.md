---
task_id: TASK-PROC-034-03
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-04
effort: M
created: 2026-03-04
after: [TASK-PROC-034-02]
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-06]
scope_description: "Update scripts/validate_meta.py to recognize and validate the target_release field at both top-level and per-trackable-item level, plus release-dependency constraint validation."
requirements_version:
  commit: c8c9ac7
  file: ../requirements.md
---

# Goal: Update validate_meta.py — target_release Field Recognition & Validation

## What

Extend `scripts/validate_meta.py` (MetaValidator class) to understand `target_release` in requirements.md and goal.md files, and to validate release-dependency consistency.

## Scope

### 1. Field Recognition (SEC-03)

**Top-level field** (both requirements.md and goal.md):
- `target_release` is an optional string field
- When present, must match a version defined in `requirements_tasks/RELEASES.md`
- Format: `MAJOR.MINOR.PATCH` (semver) — validate with regex `^\d+\.\d+\.\d+$`

**Per-trackable-item field** (requirements.md only):
- `target_release` may appear on any AC or section object inside `trackable_items`
- Same validation rules as top-level: must be valid semver and exist in RELEASES.md
- When trackable items have individual releases, top-level `target_release` must equal the earliest among them (computed check)

### 2. Release-Dependency Validation (SEC-06)

For each requirement/task with `target_release` set:
- For each ID in `depends_on` / `blocked_by`: look up that item's `target_release`
- If both sides are assigned: verify `release(self) >= release(dependency)`
- Report as a **warning** (not a hard error) to allow incremental migration
- Skip silently if either side is unassigned

### 3. RELEASES.md Loading

- Load and cache `requirements_tasks/RELEASES.md` once at validation start
- Extract the `releases` list, build a set of known version strings
- If RELEASES.md does not exist yet: skip version-existence checks (not an error)

## Key File

`scripts/validate_meta.py` — read the full file before implementing, especially the `MetaValidator` class and the existing field validation patterns.

## Out of Scope

- Changes to `generate_status_overview.py` (TASK-PROC-034-04)
- Changes to skills (TASK-PROC-034-05, -06)
