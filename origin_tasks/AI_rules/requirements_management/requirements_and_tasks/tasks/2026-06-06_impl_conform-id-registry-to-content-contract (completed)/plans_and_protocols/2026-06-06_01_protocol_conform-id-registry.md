---
skills_used:
  - requ-explore
  - task-create
  - claude-write-script
  - task-complete
  - claude-commit
---

# Protocol: Conform ID Registry Generator to SEC-08 Content Contract

**Task**: TASK-PROC-009-15
**Date**: 2026-06-06
**Agent ID**: a1ea9bdc800d0d0bc

## Summary

Conformed `scripts/artifacts/generate_id_registry.py` to REQ-PROC-009 SEC-08
AC-01/02/03 by expanding the ID scan regex to include hierarchical sub-requirement
IDs and rendering them visually nested in the catalog.

## Changes Made

### 1. `scripts/artifacts/generate_id_registry.py`

**Regex expansion (AC-01/02)** — two scan sites updated:
- `scan_requirements_tree` (~line 207): `^REQ-(FUNC|NFUNC|PROC)-\d{3}$`
  → `^REQ-(FUNC|NFUNC|PROC)-\d{3}(-\d{2})?$`
- `_process_req_files` (~line 447): same change (this is the active scan path
  used by both `--requirements` and `--all` modes)

**Nested rendering helper (AC-01)** — new module-level helpers added before
`generate_requirements_registry`:
- `_HIERARCHICAL_REQ_RE`: compiled regex matching `REQ-CAT-NNN-NN`
- `_req_id_cell(req_id)`: returns `└─ REQ-CAT-NNN-NN` for hierarchical IDs,
  unchanged string for top-level IDs

**Both render loops updated (AC-01)** — `generate_requirements_registry` and
`_build_requirements_content` (used by `--all` mode) now call `_req_id_cell()`
for the ID cell of every catalog table row.

**`compute_next_ids` untouched (AC-03)** — the function's anchored regex
`^REQ-(PROC|NFUNC|FUNC)-(\d{3})$` naturally ignores hierarchical IDs. No change.

### 2. `scripts/tests/test_generate_id_registry.py`

Five new tests covering the AC-01/02/03 requirements:
- `test_hierarchical_id_included_in_req_entries` — `_process_req_files` includes
  `REQ-FUNC-006-07` in `req_entries` (AC-01/02)
- `test_hierarchical_id_rendered_with_tree_marker` — `_req_id_cell` returns the
  `└─` prefix for hierarchical IDs, unchanged for top-level (AC-01)
- `test_per_category_count_includes_hierarchical_ids` — category list contains
  2 entries when one top-level + one hierarchical are present (AC-02)
- `test_compute_next_ids_ignores_hierarchical_ids` — given `REQ-FUNC-023` and
  `REQ-FUNC-023-04`, next FUNC is still `REQ-FUNC-024` (AC-03)

### 3. `requirements_tasks/_meta/id_registry.md`

Regenerated from the corrected generator.

## Before / After Counts

| Category | Before | After |
|----------|--------|-------|
| PROC     | 63     | 96    |
| NFUNC    | 23     | 27    |
| FUNC     | 22     | 67    |
| **Total**| **108**| **190**|

82 hierarchical IDs added (confirmed by pre-run grep count).

## AC-03 Verification — Next Available IDs Unchanged

| Category | Before | After | Match |
|----------|--------|-------|-------|
| PROC     | REQ-PROC-070  | REQ-PROC-070  | YES |
| NFUNC    | REQ-NFUNC-024 | REQ-NFUNC-024 | YES |
| FUNC     | REQ-FUNC-024  | REQ-FUNC-024  | YES |
| VTR      | VTR-008       | VTR-008       | YES |

`compute_next_ids` was not modified and its anchored 3-digit regex continues to
ignore hierarchical IDs — AC-03 confirmed.

## Quality Gates

| Gate | Result | Notes |
|------|--------|-------|
| G1 lint (ruff) | PASS (my files) | Pre-existing F401 in `run_monitors.py` — baseline |
| G2 type (mypy) | PASS | No issues in 189 files |
| G3 tests (pytest) | PASS (my files) | 10/10 pass in `test_generate_id_registry.py`; 1 pre-existing failure in `test_create_optimize_cycle_task.py` — baseline |
| G4 no-handrolled | PASS | |
| G5 print-discip. | PASS | |

All 5 pre-existing tests + 5 new tests in `test_generate_id_registry.py` pass.

## Files Modified

- `scripts/artifacts/generate_id_registry.py`
- `scripts/tests/test_generate_id_registry.py`
- `requirements_tasks/_meta/id_registry.md` (regenerated)
