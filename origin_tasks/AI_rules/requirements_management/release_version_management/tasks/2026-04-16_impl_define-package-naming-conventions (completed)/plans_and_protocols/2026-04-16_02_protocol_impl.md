# Implementation Protocol: Define Package Naming Conventions

**Task**: TASK-PROC-034-12
**Date**: 2026-04-16
**Agent ID**: a5aebf2b7187b1e60
**Plan followed**: 2026-04-16_01_opus_plan.md

## Summary

All planned changes applied successfully. No deviations from the plan.

## Changes Made

### File 1: `requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md`

**SEC-01 — Package Naming Rules** (lines 83-92 replaced with expanded content):

- Replaced the minimal 4-rule table with the full `[Subject] [Capability] [Qualifier?]` structure table
- Added the 9-rule table with rationale column (including the new minimum-2-words rule and similarity check)
- Added Flow-Derived Naming table (happy path / exception bundle / named variant patterns)
- Added User-Facing vs. Technical Packages distinction section
- Added Examples and Anti-Examples table
- Added Grandfathering clause
- Added "How to Derive a Good Package Name" subsection with:
  - 7-step decision process (prose numbered list)
  - Stakeholder Understandability Tests table (U1-U5)
- Added Package Granularity Guidelines section (new/join conditions, oversized package handling, initial sizing philosophy)
- Removed the old standalone sentence "Uniqueness is enforced at creation time..." (subsumed by Rules 6 and 7)

**SEC-05 — Skills and Their Responsibilities** (line ~526):

- Updated `release-plan` row to add: "Validates new package names against naming convention (SEC-01)."

### File 2: `.claude/skills/requ-assign-packages/skill.md`

**Change 1 — New section** (appended after "## Assignment Rules"):

- Added "## Naming Validation (when proposing new packages)" section with:
  - Reference to REQ-PROC-034 SEC-01 convention
  - 4 validation bullet points (structure, timing/jargon, similarity check, demo/boundary tests)
  - Guidance to suggest new package names with `→ Suggested new package: "[Name]"` format in "No match" proposals

**Change 2 — Signal 3 update**:

- Added to the end of Signal 3 description: "If no existing package is a good match, propose a new package name following SEC-01 naming convention and note it as '[NEW — needs release-plan Action 4]'."

### File 3: `.claude/skills/release-plan/skill.md`

**Change 1 — Action 4 naming rules block**:

- Replaced the 2-line minimal name rules ("max 4 words...") with the expanded naming convention block:
  - `[Subject] [Capability] [Qualifier?]` structure reference
  - Forbidden word categories (timing words, implementation jargon)
  - Similarity check instruction (search for 2+ content-word overlaps, ask user to justify or adjust)
  - Good/bad examples

**Change 2 — Action 4b step 5**:

- Added to end of step 5: "Validate the confirmed name against SEC-01 naming convention before writing."

## Deviations from Plan

None. All changes applied verbatim from the plan's exact replacement content.

## Status

All acceptance criteria from goal.md are met:
- SEC-01 updated with comprehensive naming convention
- `requ-assign-packages` skill updated with Naming Validation section and Signal 3 new-package guidance
- `release-plan` skill updated in Action 4 (naming convention block) and Action 4b (validation step)
- TASK-PROC-030-11 is unblocked: the convention confirms all proposed package names for epic_data_transfer are valid
