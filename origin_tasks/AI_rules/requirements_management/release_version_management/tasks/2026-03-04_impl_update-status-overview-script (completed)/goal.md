---
task_id: TASK-PROC-034-04
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-03-04
effort: L
created: 2026-03-04
after: [TASK-PROC-034-02]
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-05, SEC-06]
scope_description: "Update scripts/generate_status_overview.py to add target_release to data models, new --release filter, new --release-summary report mode, and release-dependency conflict reporting."
requirements_version:
  commit: c8c9ac7
  file: ../requirements.md
---

# Goal: Update generate_status_overview.py — Release Grouping & Validation

## What

Extend `scripts/generate_status_overview.py` with release version awareness: data model changes, a new `--release-summary` report mode, a `--release VERSION` filter, and release-dependency conflict detection.

## Scope

### 1. Data Model Changes

**`RequirementData` dataclass** (line ~60):
- Add `target_release: Optional[str] = None`
- Parse from frontmatter: `meta.get('target_release')`
- Also parse per-trackable-item releases from `trackable_items.acceptance_criteria[].target_release` and `trackable_items.sections[].target_release`

**`TaskData` dataclass** (line ~92):
- Add `target_release: Optional[str] = None`
- Parse from frontmatter: `meta.get('target_release')`

### 2. New Command-Line Option: `--release VERSION`

- Filters all existing report modes to only items with `target_release == VERSION`
- Works with all existing modes: `--summary`, `--priority`, `--full`, etc.
- Items with no `target_release` are excluded from filtered output

### 3. New Report Mode: `--release-summary`

Generates a release-grouped overview (see REQ-PROC-034 SEC-05 for the exact format):
- One section per release version from RELEASES.md, sorted by semver
- Per release: requirements count, open tasks, completed tasks, coverage %
- Plus an "Unassigned" section at the end for items with no `target_release`
- Load RELEASES.md to show release name and description in section headers

### 4. Release-Dependency Conflict Reporting (SEC-06)

In `--full` mode and `--release-summary` mode, add a "⚠ Release-Dependency Conflicts" section:
- For every item with `target_release` set, check all `depends_on` / `blocked_by` items
- If dependency has a later release: report as a conflict row in the table
- Format per REQ-PROC-034 SEC-06 conflict output format
- Use `packaging.version.Version` for semver comparison (or implement simple tuple comparison as fallback)

### 5. Existing Report Integration

- `--priority` mode: add `target_release` column to priority tables
- `--blockers` mode: list release conflicts alongside other blockers

## Key Files

- `scripts/generate_status_overview.py` — read the full file first; understand RequirementData, TaskData, all ReportGenerator subclasses, and the argument parser
- `requirements_tasks/RELEASES.md` — must exist before this task (blocked by TASK-PROC-034-02)

## Out of Scope

- Changes to `validate_meta.py` (TASK-PROC-034-03)
- Changes to skills (TASK-PROC-034-05, -06)
