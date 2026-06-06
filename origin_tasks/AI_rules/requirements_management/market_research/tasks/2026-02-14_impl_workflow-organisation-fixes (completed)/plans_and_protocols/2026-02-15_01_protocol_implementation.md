# Protocol: TASK-PROC-029-06 Workflow & Organisation Fixes

**Date**: 2026-02-15
**Agent ID**: claude-sonnet-4-5-20250929
**Status**: COMPLETED

## Changes Made

### 1. apply-market-research skill — Flow routing fix
**File**: `.claude/skills/apply-market-research/skill.md`
- Mode A step 3 now differentiates: `demand`/`quality` → `requirements_tasks/`, `flow` → `requirements_user_needs/user_flows/`
- Finding MR-2026-02-14-006 (therapist-assigns-homework) now has a clear application pathway

### 2. Conflict Decision Record Template — Created
**File**: `requirements_market_research/_templates/decision_record_template.md`
- Fields: Record ID, date, reviewer, conflicting finding IDs, claims, conflict detection heuristic, resolution, losers update
- Includes heuristic definition for what constitutes a contradiction vs. mere difference in emphasis

### 3. README.md — Handling Conflicts section updated
**File**: `requirements_market_research/README.md`
- "Handling Conflicts" step 2 now references `_templates/decision_record_template.md`

### 4. Folder rename
- `requirements_market_research/2023-11_initial-market-overview/` → `2023-11-01_initial-market-overview/`
- Done via `git mv` to preserve history

### 5. Finding ID updates (MR-2023-11-NNN → MR-2023-11-01-NNN)
Updated in 5 files:
- `requirements_market_research/2023-11-01_initial-market-overview/findings.md` — source batch header + 3 finding headings
- `requirements_tasks/functional/client/epic_data_input/requirements.md` — MR-2023-11-003 → MR-2023-11-01-003
- `requirements_tasks/functional/therapist/epic_plan_management/requirements.md` — MR-2023-11-001 and -003
- `requirements_tasks/functional/shared/epic_security/requirements.md` — MR-2023-11-002
- `requirements_tasks/functional/shared/epic_data_transfer/requirements.md` — MR-2023-11-001 and -002

### 6. findings_template.md — No change needed
Already had the file-level header section (Source batch, Raw data, Extracted, Extracted by). AC already met.

## Acceptance Criteria Verification

- [x] apply-market-research skill routes `flow` findings to `requirements_user_needs/user_flows/`
- [x] Conflict decision record template exists at `_templates/decision_record_template.md`
- [x] README.md "Handling Conflicts" section references the template
- [x] `2023-11_initial-market-overview/` renamed to `2023-11-01_initial-market-overview/`
- [x] Finding IDs updated from `MR-2023-11-*` to `MR-2023-11-01-*` across all active files
- [x] findings_template.md includes file-level header section (was already present)
