---
task_id: TASK-PROC-034-10
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-03-26
completed: 2026-03-26
effort: L
created: 2026-03-26
after: [TASK-PROC-034-09]
awaiting: [TASK-PROC-034-09]
awaiting_note: "Needs RELEASE_BACKLOG.md and updated RELEASES.md format to exist first"
covers:
  acceptance_criteria: []
  sections: [SEC-03]
scope_description: "Migration script to replace target_release with target_package in ~137 files"
release_description: ""
requirements_version:
  commit: "b25b8f25"
  file: ../requirements.md
---

# Implementation Task: Migration Script (target_release → target_package)

## Requirement Reference
- **Requirement**: ../requirements.md (REQ-PROC-034)
- **Status**: Not Started

## Goal

Create a Python migration script (`scripts/migrate_target_release_to_package.py`) that replaces all `target_release` fields with `target_package` fields across ~137 files in `requirements_tasks/`. The script reads a version-to-package mapping (derived from RELEASE_BACKLOG.md) and performs the replacement.

## Scope Overview

**Affected files**:
- NEW: `scripts/migrate_target_release_to_package.py`
- UPDATE: ~137 files in `requirements_tasks/` (requirements.md and goal.md files)

### In Scope
- Script reads RELEASE_BACKLOG.md to build version→package mapping (from assigned_release → id)
- Finds all `target_release:` fields in YAML frontmatter of `requirements_tasks/**/*.md`
- Replaces `target_release: "x.y.z"` with `target_package: "Package Name"` using the mapping
- Handles per-AC and per-SEC `target_release` fields in `trackable_items`
- Recalculates top-level `target_package` as the earliest-priority package among items
- Supports `--dry-run` mode (report what would change without writing)
- Outputs a migration report: files changed, values mapped, unmappable entries
- Handles edge cases: absent target_release (skip), unknown version (report as error)

### Out of Scope
- Updating scripts that READ target_release (separate task)
- Updating skills (separate task)
- Creating RELEASE_BACKLOG.md (prerequisite task TASK-PROC-034-09)

## Acceptance Criteria

- [ ] Script runs without errors on the full `requirements_tasks/` tree
- [ ] All `target_release` fields are replaced with `target_package` fields
- [ ] Per-AC and per-SEC `target_release` fields within `trackable_items` are migrated
- [ ] Top-level `target_package` is recalculated correctly using the 3-tier "earliest" logic from SEC-03: (1) semver comparison if both packages are versioned, (2) versioned beats unversioned, (3) backlog position if neither is versioned
- [ ] `--dry-run` mode works and produces accurate report
- [ ] Unmappable entries (version not in RELEASE_BACKLOG.md) are reported, not silently skipped
- [ ] YAML remains valid after migration (no formatting corruption)
- [ ] Migration report shows: total files scanned, files changed, fields migrated, errors

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-034-09 | pending | RELEASE_BACKLOG.md must exist with version→package mappings |

## Notes
- The migration must handle YAML frontmatter correctly — use a YAML parser, not regex, for reading. For writing, preserve existing formatting as much as possible (consider using ruamel.yaml or targeted string replacement).
- Some releases may map to multiple packages. For per-AC mappings where the version maps to multiple packages, the script should use the AC's context (which epic/feature it belongs to) to determine the correct package, or flag for manual review.
- Run `--dry-run` first and have the user review before applying changes.
