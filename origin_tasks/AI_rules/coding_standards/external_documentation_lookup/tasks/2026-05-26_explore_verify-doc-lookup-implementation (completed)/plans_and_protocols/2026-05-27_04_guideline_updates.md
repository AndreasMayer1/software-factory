# Guideline Updates — TASK-PROC-053-09

Date: 2026-05-27

## Files Changed

1. `doc/cross_cutting_standards/documentation_lookup.md` — 3 fixes

## Changes Applied

### Fix 1 — §5 Budget band notation (GAP-2)

**Before**: Table used S1 call-count labels (Simple/Standard/Complex with S1 thresholds).  
**After**: Table uses effort labels (XS/S, M, L/XL) matching the `effort:` field the SKILL.md reads from `goal.md` frontmatter. Added note that these correspond to S1 bands from REQ-PROC-001.

### Fix 2 — §6 Privacy script claim (GAP-1)

**Before**: Listed "Project-specific identifiers (class names from private app code)" as stripped.  
**After**: Clarified that only path-separator-containing tokens are stripped. Added explicit note that private class names are NOT stripped (would break query intent).

### Fix 3 — §3 Field reference table: add dedup_key (GAP-3)

**Before**: `dedup_key` was defined only in the "Dedup key" subsection formula, absent from the field reference table.  
**After**: Added `dedup_key` row to the field reference table with its SHA-256 formula and a note that it is precomputed and stored for fast dedup lookups.

## READMEs Synced

None — no files were added or removed from `doc/cross_cutting_standards/`; existing README entry for `documentation_lookup.md` remains accurate.

## Governance

`python3 scripts/artifacts/doc_governance.py` → No violations found.
