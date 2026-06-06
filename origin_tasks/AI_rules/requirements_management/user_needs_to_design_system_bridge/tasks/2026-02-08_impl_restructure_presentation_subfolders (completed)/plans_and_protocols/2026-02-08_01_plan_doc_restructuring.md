# Plan: Restructure doc/presentation/ into Thematic Subfolders

**Task**: TASK-PROC-026-02
**Agent ID**: architecture-advisor-2026-03-01-001
**Status**: PLAN (awaiting user approval before implementation)
**Date**: 2026-03-01

---

## Executive Summary

**What**: Reorganize `doc/presentation/` from 18 flat root files into 7 thematic subfolders, each with a README.md gatekeeper.

**Why it matters**: This is the foundational infrastructure for REQ-PROC-026 (persona-design bridge). Without a clear folder taxonomy, there is nowhere to place the persona-derived design rules (DDRs) that will be created in subsequent tasks (T2/T6). The `design/` subfolder that this task creates is the designated home for those rules. Additionally, the flat structure makes it impossible for AI to selectively read only relevant guidelines — everything is in one large merged file.

**Scope**: Documentation only. Zero changes to `lib/`, `test/`, or `integration_test/`.

---

## Blocker Analysis

### Critical Blocker: TASK-PROC-027-01 (Remove doc merge script)

**Status**: `pending` — has NOT been executed yet.

**Why this is a hard blocker**:
- `doc/presentation.md` currently exists and is a **merged output file** (confirmed: it starts with `# File: accessibility_guidelines.md` — the concatenated content of all source files).
- CLAUDE.md line 21 references `doc/presentation.md` as the live guideline AI reads.
- Skills like `requ-explore/skill.md` reference `doc/presentation.md` directly.
- If we restructure `doc/presentation/` now, the merged `doc/presentation.md` becomes stale and misleading — it would still be read by agents but would not reflect the new subfolder structure.
- TASK-PROC-027-01 is explicitly defined as the prerequisite: it removes the merge script and the merged file, and updates all references. Only then does this restructuring make sense.

**Decision**: This plan documents the COMPLETE restructuring scope (all file moves, README content, reference updates). However, **implementation must NOT begin until TASK-PROC-027-01 is marked complete** (merge script removed, `doc/presentation.md` deleted, CLAUDE.md and skills updated to reference subdirectories).

**Assumption**: When TASK-PROC-027-01 completes, CLAUDE.md will be updated to point agents to `doc/presentation/` subdirectories. This plan does NOT need to update CLAUDE.md or the skills — TASK-PROC-027-01 owns those changes. This task only moves files and creates README.md gatekeepers.

---

## Current State Analysis

### Files in `doc/presentation/` (root level — 16 files to be moved)

| File | Content Summary | Size estimate |
|------|----------------|---------------|
| `accessibility_guidelines.md` | WCAG/ISO9241, screen reader patterns, semantic widgets, BLoC accessibility state | Large |
| `atomic_design.md` | Atomic design (atoms/molecules/organisms), component structure, code examples | Medium |
| `best_practices.md` | Widget composition, BLoC lifecycle, ViewConfig pattern, layout best practices, performance | Large |
| `button_guidelines.md` | Material3 button types (FilledButton, OutlinedButton, TextButton, IconButton), usage rules | Medium |
| `component_api.md` | Custom component API docs: atoms, molecules, organisms with Dart signatures | Large |
| `component_states.md` | M3 state system (enabled/disabled/hover/focused), disabled state pattern, tooltips | Large |
| `design_system.md` | Design system overview, responsive layout system, Figma token setup, component guidelines | Large |
| `folder_structure.md` | `lib/core/` and `lib/features/` directory structure, feature module pattern | Medium |
| `grid_system.md` | Wolt responsive grid, breakpoints, design token integration for grid | Medium |
| `improvements.md` | Adaptive component descriptions (AdaptiveListItem, AdaptiveAppBar) + Role Selection UI updates | Medium |
| `localization.md` | ARB file setup, plurals, placeholders, BLoC integration, team collaboration checklist | Large |
| `navigation_patterns.md` | Three-level navigation hierarchy, Pattern A/B, contextual overlays, decision tree | Large |
| `platform_guidelines.md` | Screen size breakpoints, navigation patterns per platform, component adaptations | Medium |
| `responsive_layout.md` | ResponsiveLayoutBuilder + StatefulShellRoute, orchestrator pattern, master-detail | Large |
| `state_management.md` | BLoC pattern, form lifecycle, singleton vs factory registration, route-BLoC sync | Large |
| `token_system.md` | W3C DTCG token format, token hierarchy, static classes, animation tokens, workflow | Large |

### Existing subdirectory (already correctly placed)

| Directory | Files | Action |
|-----------|-------|--------|
| `libs/` | `material_component_api.md`, `wolt_responsive_layout_grid.md` | Keep as-is (already correct) |

### Special case: `improvements.md`

This file has a mixed nature:
- Part 1: "Design System Components" — describes `AdaptiveListItem`, `AdaptiveAppBar`, `StandardIconButton` — these are **custom component implementations**, fitting `coding/`
- Part 2: "Role Selection Feature Updates" — describes feature-specific UI changes, NOT a general guideline
- Part 3: "Implementation Guidelines" — screen size handling, touch targets, accessibility basics

**Decision**: Move to `coding/improvements.md`. The file is dated 2025-01-30 and describes adaptive component patterns. It is a guideline document about custom component patterns, which belongs in `coding/`. The "Role Selection Feature Updates" section is historical context within the file — acceptable to move as-is. (If it needs cleanup, that is a separate task.)

---

## Target Structure

```
doc/presentation/
├── README.md                          (new — top-level index)
├── coding/
│   ├── README.md                      (new — gatekeeper)
│   ├── atomic_design.md               (moved)
│   ├── best_practices.md              (moved)
│   ├── button_guidelines.md           (moved)
│   ├── component_api.md               (moved)
│   ├── component_states.md            (moved)
│   ├── design_system.md               (moved)
│   ├── folder_structure.md            (moved)
│   ├── improvements.md                (moved)
│   └── state_management.md            (moved)
├── design/
│   └── README.md                      (new — gatekeeper, empty subfolder)
├── navigation/
│   ├── README.md                      (new — gatekeeper)
│   ├── navigation_patterns.md         (moved)
│   └── responsive_layout.md           (moved)
├── platform/
│   ├── README.md                      (new — gatekeeper)
│   ├── grid_system.md                 (moved)
│   ├── localization.md                (moved)
│   └── platform_guidelines.md         (moved)
├── tokens/
│   ├── README.md                      (new — gatekeeper)
│   └── token_system.md               (moved)
├── accessibility/
│   ├── README.md                      (new — gatekeeper)
│   └── accessibility_guidelines.md   (moved)
└── libs/
    ├── README.md                      (new — gatekeeper for existing subfolder)
    ├── material_component_api.md      (already here)
    └── wolt_responsive_layout_grid.md (already here)
```

**File count**: 16 files moved + 8 README.md files created = 24 file operations

---

## Detailed File Mapping Table

| Source (current) | Destination | git mv command |
|-----------------|-------------|----------------|
| `doc/presentation/atomic_design.md` | `doc/presentation/coding/atomic_design.md` | `git mv doc/presentation/atomic_design.md doc/presentation/coding/atomic_design.md` |
| `doc/presentation/best_practices.md` | `doc/presentation/coding/best_practices.md` | `git mv doc/presentation/best_practices.md doc/presentation/coding/best_practices.md` |
| `doc/presentation/button_guidelines.md` | `doc/presentation/coding/button_guidelines.md` | `git mv doc/presentation/button_guidelines.md doc/presentation/coding/button_guidelines.md` |
| `doc/presentation/component_api.md` | `doc/presentation/coding/component_api.md` | `git mv doc/presentation/component_api.md doc/presentation/coding/component_api.md` |
| `doc/presentation/component_states.md` | `doc/presentation/coding/component_states.md` | `git mv doc/presentation/component_states.md doc/presentation/coding/component_states.md` |
| `doc/presentation/design_system.md` | `doc/presentation/coding/design_system.md` | `git mv doc/presentation/design_system.md doc/presentation/coding/design_system.md` |
| `doc/presentation/folder_structure.md` | `doc/presentation/coding/folder_structure.md` | `git mv doc/presentation/folder_structure.md doc/presentation/coding/folder_structure.md` |
| `doc/presentation/improvements.md` | `doc/presentation/coding/improvements.md` | `git mv doc/presentation/improvements.md doc/presentation/coding/improvements.md` |
| `doc/presentation/state_management.md` | `doc/presentation/coding/state_management.md` | `git mv doc/presentation/state_management.md doc/presentation/coding/state_management.md` |
| `doc/presentation/navigation_patterns.md` | `doc/presentation/navigation/navigation_patterns.md` | `git mv doc/presentation/navigation_patterns.md doc/presentation/navigation/navigation_patterns.md` |
| `doc/presentation/responsive_layout.md` | `doc/presentation/navigation/responsive_layout.md` | `git mv doc/presentation/responsive_layout.md doc/presentation/navigation/responsive_layout.md` |
| `doc/presentation/grid_system.md` | `doc/presentation/platform/grid_system.md` | `git mv doc/presentation/grid_system.md doc/presentation/platform/grid_system.md` |
| `doc/presentation/localization.md` | `doc/presentation/platform/localization.md` | `git mv doc/presentation/localization.md doc/presentation/platform/localization.md` |
| `doc/presentation/platform_guidelines.md` | `doc/presentation/platform/platform_guidelines.md` | `git mv doc/presentation/platform_guidelines.md doc/presentation/platform/platform_guidelines.md` |
| `doc/presentation/token_system.md` | `doc/presentation/tokens/token_system.md` | `git mv doc/presentation/token_system.md doc/presentation/tokens/token_system.md` |
| `doc/presentation/accessibility_guidelines.md` | `doc/presentation/accessibility/accessibility_guidelines.md` | `git mv doc/presentation/accessibility_guidelines.md doc/presentation/accessibility/accessibility_guidelines.md` |

**libs/ files**: No move needed — already in correct location.

---

## Internal Link Updates Required

After moving files, several internal cross-references break. These MUST be updated:

| File (new path) | Current reference | Updated reference |
|-----------------|------------------|-------------------|
| `coding/design_system.md` | `./button_guidelines.md` | `./button_guidelines.md` (same folder, no change needed) |
| `coding/design_system.md` | `./atomic_design.md` | `./atomic_design.md` (same folder, no change needed) |
| `coding/design_system.md` | `./from_figma/component_transformation_guide.md` | unchanged (not moving from_figma) |
| `coding/design_system.md` | `./token_system.md` → now in `tokens/` | `../tokens/token_system.md` |
| `coding/best_practices.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `coding/component_api.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `coding/component_states.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `coding/atomic_design.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `coding/button_guidelines.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `coding/folder_structure.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `coding/improvements.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `navigation/navigation_patterns.md` | `responsive_layout.md` | `./responsive_layout.md` (same folder, no change) |
| `navigation/navigation_patterns.md` | `state_management.md` → now in `coding/` | `../coding/state_management.md` |
| `navigation/navigation_patterns.md` | `../architecture/routing.md` | `../../architecture/routing.md` |
| `navigation/responsive_layout.md` | `navigation_patterns.md` | `./navigation_patterns.md` (same folder, no change) |
| `platform/accessibility_guidelines.md` | moved — see `accessibility/` folder | N/A |
| `accessibility/accessibility_guidelines.md` | `platform_guidelines.md` → now in `platform/` | `../platform/platform_guidelines.md` |
| `platform/grid_system.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `platform/platform_guidelines.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `platform/localization.md` | `libs/material_component_api.md` | `../libs/material_component_api.md` |
| `tokens/token_system.md` | No internal presentation/ links | No change needed |

**Implementation note**: The implementer MUST run a search for all `libs/` references (currently `libs/material_component_api.md`) across moved files and update to `../libs/` after moving one level deeper.

---

## README.md Content Strategy

### Top-Level: `doc/presentation/README.md`

Purpose: Entry-point index for the entire presentation layer documentation.

Content outline:
- What this directory contains (presentation layer guidelines for `lib/`, `test/`)
- Directory map with one-line description per subfolder
- How AI should navigate: "Use Glob on subdirectories to find relevant guidelines"
- Cross-reference to `doc/architecture.md` for layer boundaries

### `coding/README.md`

**Purpose**: Flutter coding conventions, widget patterns, component architecture, state management for the presentation layer.

**Allowed content**:
- Widget composition rules and patterns
- Component API documentation (atoms/molecules/organisms)
- State management patterns (BLoC usage in presentation)
- Button, form, and UI component guidelines
- Folder structure and code organization
- Custom component implementations and improvements

**Forbidden content**:
- Persona-derived design rules (those go in `design/`)
- Navigation architecture (goes in `navigation/`)
- Design token definitions (goes in `tokens/`)
- Accessibility-specific guidelines (goes in `accessibility/`)
- Platform/responsive breakpoint specs (goes in `platform/`)

**Naming convention**: `[component_name]_guidelines.md` or `[topic]_patterns.md` or `[topic].md`.

### `design/README.md`

**Purpose**: Persona-derived design rules — the bridge between user research and code decisions. This is the home for all DDRs (Design Decision Records) derived from persona analysis.

**Allowed content**:
- `t1_*.md` — Tier-1 rules: apply to ALL screens universally (e.g., `t1_touch_targets.md`)
- `t2_*.md` — Tier-2 rules: apply to 2+ screens but not all (e.g., `t2_form_layout.md`)
- `ddr_*.md` — Design Decision Records: explicit persona-to-rule traceability
- `persona_*.md` — Persona summaries or design constraints derived from user research

**Forbidden content**:
- Technical Flutter implementation patterns (goes in `coding/`)
- Navigation architecture rules (goes in `navigation/`)
- Pure token definitions (goes in `tokens/`)

**Naming convention** (mandatory):
- `t1_[descriptive_name].md` — universal screen rules
- `t2_[descriptive_name].md` — multi-screen rules
- `ddr_[descriptive_name].md` — design decision records
- `persona_[name_or_type].md` — persona documents

**Initially empty**: This folder starts with only the README.md. Content is added by T2 (persona bridge file) and T6 (retroactive annotation tasks).

### `navigation/README.md`

**Purpose**: Navigation architecture, routing patterns, and layout pattern decisions.

**Allowed content**:
- Navigation pattern definitions (Pattern A Master-Detail, Pattern B Detail-Only)
- Responsive layout rules and `ResponsiveLayoutBuilder` usage
- GoRouter and `StatefulShellRoute` patterns
- Back navigation conventions
- Layout state documentation

**Forbidden content**:
- Platform-specific breakpoint numbers (goes in `platform/`)
- Generic widget composition (goes in `coding/`)

**Naming convention**: `[pattern_name]_patterns.md` or `[component]_layout.md`.

### `platform/README.md`

**Purpose**: Platform-specific adaptations, responsive breakpoints, grid system, and localization.

**Allowed content**:
- Screen size breakpoints and responsive behavior specs
- Grid system (columns, margins, gutters)
- Platform-specific component adaptations (mobile vs. desktop vs. medium)
- Localization (ARB files, `flutter_localizations` setup, i18n patterns)
- Input handling differences per platform (touch vs. mouse)

**Forbidden content**:
- Navigation patterns (goes in `navigation/`)
- General accessibility rules (goes in `accessibility/`)

**Naming convention**: `[platform_or_topic]_guidelines.md`.

### `tokens/README.md`

**Purpose**: Design token definitions, token hierarchy, and token usage patterns.

**Allowed content**:
- Token system documentation (W3C DTCG format)
- Token hierarchy explanation (primitives → semantic → component)
- How to access tokens in code (SpacingTokens, ColorTokens, etc.)
- How to add new tokens (workflow)
- Animation token documentation

**Forbidden content**:
- Persona-derived design constraints (goes in `design/`)
- Component-specific usage examples beyond token access patterns (goes in `coding/`)

**Naming convention**: `token_[category].md` or `[token_type]_system.md`.

### `accessibility/README.md`

**Purpose**: WCAG compliance, screen reader support, focus management, and accessibility testing patterns.

**Allowed content**:
- WCAG/ISO 9241 compliance guidelines
- Screen reader support patterns (semantic widgets, labels)
- Focus management and keyboard navigation
- Accessibility testing (automated and manual)
- Disabled state patterns and tooltip requirements

**Forbidden content**:
- General platform adaptations (goes in `platform/`)
- Component implementation details beyond accessibility aspects (goes in `coding/`)

**Naming convention**: `[topic]_accessibility.md` or `accessibility_[category].md`.

### `libs/README.md`

**Purpose**: Reference documentation for third-party libraries used in the presentation layer.

**Allowed content**:
- Third-party library API references that AI needs to consult during development
- Library-specific usage notes or constraints

**Forbidden content**:
- Internal custom component documentation (goes in `coding/`)
- App-specific patterns built on top of libraries (goes in relevant subfolder)

**Naming convention**: `[library_name].md`.

---

## Implementation Order and Sequencing

### Pre-condition (MUST be verified before Step 1)
- [ ] TASK-PROC-027-01 status is `completed`
- [ ] `doc/presentation.md` no longer exists
- [ ] `CLAUDE.md` has been updated to reference `doc/presentation/` subdirectories (not merged file)

### Step 1: Create subfolder directories

Create the following new directories (empty, ready for moves):
```
doc/presentation/coding/
doc/presentation/design/
doc/presentation/navigation/
doc/presentation/platform/
doc/presentation/tokens/
doc/presentation/accessibility/
```
`doc/presentation/libs/` already exists.

### Step 2: Move files using `git mv`

Execute all 16 `git mv` commands from the file mapping table above. Run them as individual commands (not chained). Example:
```bash
git mv "doc/presentation/atomic_design.md" "doc/presentation/coding/atomic_design.md"
git mv "doc/presentation/best_practices.md" "doc/presentation/coding/best_practices.md"
# ... (all 16 moves)
```

### Step 3: Fix internal cross-references

After all moves, update the relative links inside moved files as specified in the "Internal Link Updates Required" table above. Key pattern to find:
- `libs/material_component_api.md` → `../libs/material_component_api.md` (in all `coding/`, `platform/`, `accessibility/` files)
- `token_system.md` in `coding/design_system.md` → `../tokens/token_system.md`
- `state_management.md` in `coding/best_practices.md` and `navigation/navigation_patterns.md` → adjust path

### Step 4: Create README.md files

Create 8 README.md files using the content strategy above:
1. `doc/presentation/README.md` (top-level index)
2. `doc/presentation/coding/README.md`
3. `doc/presentation/design/README.md`
4. `doc/presentation/navigation/README.md`
5. `doc/presentation/platform/README.md`
6. `doc/presentation/tokens/README.md`
7. `doc/presentation/accessibility/README.md`
8. `doc/presentation/libs/README.md`

### Step 5: Verify no broken links

Search for any remaining references to now-moved files using their old root paths:
```bash
rg "presentation/atomic_design|presentation/best_practices|presentation/button_guidelines" --type md
```
Also verify that cross-links to `doc/presentation/` from `navigation_patterns.md` etc. pointing to `../architecture/routing.md` still resolve correctly (they should, as architecture files did not move).

### Step 6: Git commit

```bash
git add doc/presentation/
git commit -m "docs: restructure doc/presentation/ into thematic subfolders (TASK-PROC-026-02)"
```

---

## CLAUDE.md and Skills Updates

**This task does NOT update CLAUDE.md or skills** — that is owned by TASK-PROC-027-01.

However, after TASK-PROC-027-01 completes, the following references will exist and this task's structure must be compatible:

| File | Current reference (post-027-01) | Must resolve to |
|------|--------------------------------|-----------------|
| `CLAUDE.md` | `doc/presentation/` subdirectory | Agents use Glob on subfolders |
| `.claude/agents/architecture-advisor.md` | `doc/presentation.md` | Will be updated by 027-01 to `doc/presentation/` |
| `.claude/skills/requ-explore/skill.md` | `doc/presentation.md` | Will be updated by 027-01 |
| `.claude/skills/ui-create-sketch/skill.md` | `doc/presentation/design/` | Already correct — references `design/` subfolder |

**The `ui-create-sketch` skill already anticipates this structure** — it references `doc/presentation/design/t1_*.md` and `doc/presentation/design/t2_*.md` directly. This plan's structure is compatible.

---

## Categorization Rationale (Ambiguous Cases)

### Why `responsive_layout.md` → `navigation/` (not `platform/`)

`responsive_layout.md` is primarily about `ResponsiveLayoutBuilder` architecture — the orchestrator + StatefulShellRoute pattern for master-detail navigation. It is a navigation ARCHITECTURE document, not a breakpoint specification document. `platform_guidelines.md` handles the breakpoint numbers and platform-specific component adaptations. The cross-reference in `navigation_patterns.md` itself links to `responsive_layout.md` as a sibling document, confirming they belong together.

### Why `grid_system.md` → `platform/` (not `tokens/`)

The grid system uses design tokens (SpacingTokens) but its primary concern is responsive columns/gutters/margins across screen sizes — a platform adaptation concern. The token system document (`tokens/`) documents how tokens are defined and accessed; the grid document documents how to use them in a specific responsive context.

### Why `design_system.md` → `coding/` (not a standalone or `design/`)

Despite its name, `design_system.md` is a coding guidelines document about component organization, responsive layout implementation, and Figma token integration workflow. It is NOT a persona-derived design rule. It belongs in `coding/` alongside `atomic_design.md` which it references.

### Why `state_management.md` → `coding/` (not a separate `state/` subfolder)

State management in the presentation layer is a coding pattern, not a navigation or design concern. The goal limits subfolders to 7 specifically defined ones; no `state/` subfolder is defined in the requirement. `coding/` is the correct home.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| TASK-PROC-027-01 not completed before this task executes | High (it's still pending) | High — creates stale merged file alongside new structure | Plan includes explicit pre-condition check; implementer must verify |
| Internal links break after moves | Medium | Medium — agents follow broken references | Step 3 and Step 5 explicitly address link fixing |
| Skills referencing specific files by old paths | Low | Low — only `ui-create-sketch` references `design/` explicitly (and that's correct) | Verified: skills reference `doc/presentation/` at directory level, not individual files, except `requ-explore` which will be fixed by 027-01 |
| Future DDR files placed in wrong subfolder | Medium | Low | `design/README.md` with explicit `t1_/t2_/ddr_/persona_` naming conventions mitigates this |
| `improvements.md` content mismatch in `coding/` | Low | Low | File is dated 2025-01-30; its content (adaptive components + implementation patterns) fits `coding/`; no risk of misattribution |

---

## Scope Assessment

**Is splitting needed?** No. This task is appropriately scoped:
- 16 file moves (all `git mv`, no content editing)
- 8 README.md files created (new content, but templated)
- 0 code changes (documentation only)
- Estimated effort: Small (confirmed in goal.md frontmatter as `S`)
- All operations are mechanical once the plan is approved

---

## Summary of Deliverables

After implementation:

1. `doc/presentation/` root contains ONLY: `README.md`, and 7 subdirectory folders
2. All 16 source files moved to appropriate subfolders, git history preserved
3. 8 README.md gatekeeper files created (one per subfolder + top-level)
4. All internal cross-references updated to reflect new relative paths
5. AC-13 satisfied: subfolders `coding/`, `design/`, `navigation/`, `platform/`, `tokens/`, `accessibility/`, `libs/` all exist
6. AC-16 satisfied: every subfolder has a README.md with purpose, allowed content, forbidden content, and naming conventions

---

*Plan created by architecture-advisor-2026-03-01-001. Implementation may begin only after TASK-PROC-027-01 is complete and user approves this plan.*
