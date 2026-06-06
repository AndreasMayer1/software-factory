# Plan: Scribble Storage Mirrors lib/features/

**Task**: TASK-PROC-032-22  
**Date**: 2026-06-01  
**Status**: In execution

## Objective

Move the existing scribble from the legacy co-located path to a centralized mirror of `lib/features/`. Update all consuming skills/agents to locate scribbles via `feature_path` mirror, not the hard-coded co-located path.

## Current State

- **Existing scribble** (only one):
  - Location: `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/scribbles/` (v1 + v2)
  - Requirement: REQ-FUNC-007-01
  - Feature in lib: `lib/features/therapist/data_transfer/`
  - `feature_path` NOT in metadata.yaml (schema says it's required but was missing)

- **Schema conflict**: `scribble_metadata.yaml` describes `feature_path` as "relative path to feature's requirements.md folder" — this needs to be updated to reflect lib/features/ mirror semantics per AC-37.

- **Skills using co-located path** (from grep):
  - `ui-scribble-iterate` SKILL.md
  - `ui-scribble-generator` agent
  - `ui-verify-flutter` SKILL.md
  - `code-simple` SKILL.md
  - `code-complex` SKILL.md
  - (ui-visual-validate and ui-scribble-approve-handoff also use it but are OUT OF SCOPE per task)

## Decisions

**D1: feature_path value** = `therapist/data_transfer` (mirrors `lib/features/therapist/data_transfer/`)

**D2: Scribble new base** = `requirements_tasks/scribbles/therapist/data_transfer/`

**D3: Path-discovery algorithm** for consumers:
  1. Read `<req_path>/requirements.md` frontmatter — extract `feature_path` if present
  2. Construct: `requirements_tasks/scribbles/<feature_path>/`
  3. Fallback: `find requirements_tasks/scribbles/ -name "metadata.yaml" | xargs grep -l "<REQ-ID>"`
  4. Legacy fallback: check old co-located path

**D4: Add `feature_path` to requirements.md** for REQ-FUNC-007-01 so generation writes to correct location.

**D5: Requirements frontmatter schema** gets optional `feature_path` field.

**D6: Artifact-Establishment Gate** — NOT triggered. The existing `scribble` and `scribble-metadata` artifact tokens use `requirements_tasks/**/scribbles/v*/` which matches both old and new paths via `**` glob.

## Files to Change

### Schema + Metadata
1. `.claude/schemas/scribble_metadata.yaml` — update `feature_path` description to lib/features/ mirror semantics
2. `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/scribbles/v1/metadata.yaml` — add `feature_path: therapist/data_transfer`
3. `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/scribbles/v2/metadata.yaml` — add `feature_path: therapist/data_transfer`
4. `.claude/schemas/requirements_frontmatter.yaml` — add optional `feature_path` field

### Requirement
5. `requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/requirements.md` — add `feature_path: therapist/data_transfer`

### git mv
6. `git mv requirements_tasks/functional/shared/epic_data_transfer/feat_therapist_transfer_ui/scribbles requirements_tasks/scribbles/therapist/data_transfer`

### Skills + Agents (use claude-modify-skill / claude-modify-agent governance)
7. `.claude/agents/ui-scribble-generator.md` — update Output section paths
8. `.claude/agents/ui-scribble-generator.contract.yaml` — update `produces:` paths
9. `.claude/skills/ui-scribble-iterate/SKILL.md` — add Scribble Base Path Resolution, update all `scribbles/` references
10. `.claude/skills/ui-scribble-iterate/contract.yaml` — update paths
11. `.claude/skills/ui-verify-flutter/SKILL.md` — update entry pre-check + Phase 1 discovery
12. `.claude/skills/ui-verify-flutter/contract.yaml` — update paths
13. `.claude/skills/code-simple/SKILL.md` — update Sketch Gate step 2
14. `.claude/skills/code-simple/contract.yaml` — update path
15. `.claude/skills/code-complex/SKILL.md` — update Sketch Gate step 2
16. `.claude/skills/code-complex/contract.yaml` — update path

### README + Script
17. `requirements_tasks/SKETCHES_README.md` — update Folder Structure section
18. `scripts/quality/check_scribble_parity.py` — NEW via claude-write-script

## Execution Sequence

Phase A (background agent): Items 1–17 (all edits + git mv)
Phase B (main session): Item 18 — invoke `claude-write-script` for parity lint
Phase C (main session): Run parity lint, fix any divergence
Phase D (main session): verify-quality + task-complete

## Parity Lint Spec

Script: `scripts/quality/check_scribble_parity.py`
Purpose: Flag divergence between `requirements_tasks/scribbles/` and `lib/features/`

**Algorithm**:
1. Collect all `feature_path` values from `requirements_tasks/scribbles/**/metadata.yaml` (excluding latest-per-scribble if needed; deduplicate by feature_path)
2. Collect all leaf feature directories from `lib/features/` (directories that contain `presentation/`)
3. For each scribble `feature_path`:
   - Check if `lib/features/<feature_path>/` exists → if not, flag "stale scribble path: <feature_path> has no matching lib/features/ node"
4. For each lib/features leaf `<fp>`:
   - Check if `requirements_tasks/scribbles/<fp>/` has any metadata.yaml → if not, flag "coverage gap: lib/features/<fp> has no scribble"
5. Exit 0 if no violations; exit 1 with violation report

NOTE: Coverage gaps (step 4) are warnings, not errors — many features are pre-scribble. Stale paths (step 3) are errors.
