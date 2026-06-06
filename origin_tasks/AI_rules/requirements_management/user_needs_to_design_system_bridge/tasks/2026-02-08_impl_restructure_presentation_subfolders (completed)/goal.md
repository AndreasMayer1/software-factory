---
task_id: TASK-PROC-026-02
type: impl
parent_requirement: REQ-PROC-026
urgency: 3
urgency_reason: U3-CTX
impact: 3
impact_reason: I3-INFRA
status: completed
completed: 2026-03-01
effort: S
created: 2026-02-08
after:
  - TASK-PROC-027-01
awaiting:
  - TASK-PROC-027-01
covers:
  acceptance_criteria:
    - AC-13
    - AC-16
  sections:
    - "4.5"
scope_description: "Restructure doc/presentation/ into subfolders and create README.md gatekeepers for each"
requirements_version:
  commit: null
  file: ../../../requirements.md
  note: "REQ-PROC-026 section 4.5 defines the subfolder structure"
---

# Implementation Task: Restructure doc/presentation/ Subfolders

## Requirement Reference
- **Requirement**: [REQ-PROC-026](../../../requirements.md) — Section 4.5 "Where Design-as-Code Rules Live"
- **Roadmap Position**: T1 (first implementation task after T0 merge script removal)

## Goal

Reorganize `doc/presentation/` from a flat file structure into thematic subfolders, and create a README.md for each subfolder that defines what content is allowed there. This is the foundational task — all subsequent persona-design bridge work depends on this structure being in place.

## Scope Overview

**Current state**: 18 files in `doc/presentation/` root (plus `libs/` subdirectory with 2 files). All files are flat — coding conventions mixed with design tokens mixed with navigation patterns.

**Target state**: Files organized into 7 subfolders, each with a README.md gatekeeper:

| Subfolder | Purpose | Approx. files to move |
|-----------|---------|----------------------|
| `coding/` | Flutter coding conventions, widget patterns, state management | ~8 files |
| `design/` | Persona-derived design rules, DDRs (empty initially, populated by T2/T6) | 0 (new) |
| `navigation/` | Navigation architecture, routing patterns | ~2 files |
| `platform/` | Platform-specific adaptations, responsive, localization | ~3 files |
| `tokens/` | Design token definitions, theme configuration | ~2 files |
| `accessibility/` | WCAG compliance, screen reader patterns | ~1 file |
| `libs/` | Third-party library references (already exists) | 0 (already there) |

**Affected Layers**: Documentation only (no code changes in `lib/`, `test/`)
**Estimated Files**: ~18 files moved + 7 README.md files created = ~25 file operations
**Patterns to Follow**: The `libs/` subfolder already exists as a precedent

## What Each README.md Must Contain

Per REQ-PROC-026 section 4.5 "Subfolder README Requirements":

1. **Purpose**: What kind of content belongs in this folder
2. **Allowed content**: What types of files may be added here (with examples)
3. **Forbidden content**: What does NOT belong here (to prevent misplacement)
4. **Naming conventions**: File naming rules specific to this subfolder (if any)

The `design/` subfolder README is especially important — it must document the `t1_`, `t2_`, `ddr_`, `persona_` file naming prefixes.

## Additional Context

- After T0 (TASK-PROC-027-01) removes the merge script, `doc/presentation.md` (the merged output) will no longer exist. AI reads individual source files directly via Glob/Grep.
- References to `doc/presentation.md` in CLAUDE.md and skills need to be updated to point to the subfolder structure.
- The `improvements.md` file in the current root may need to be assessed — it might be a temporary file that doesn't belong in the new structure.

## Acceptance Criteria

- [ ] AC-13: `doc/presentation/` restructured into subfolders (`coding/`, `design/`, `navigation/`, `platform/`, `tokens/`, `accessibility/`, `libs/`)
- [ ] AC-16: Every subfolder has a README.md defining allowed content, forbidden content, and naming conventions
- [ ] All existing files moved to appropriate subfolders (no files left in root except possibly a top-level README.md)
- [ ] References in CLAUDE.md updated to reflect new structure
- [ ] References in skills updated if they point to specific `doc/presentation/` files
- [ ] Git history preserved (use `git mv` for moves)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-027-01 (Remove doc merge script) | pending | **BLOCKER** — must complete first. Merge script and merged output must be gone before restructuring. |

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
