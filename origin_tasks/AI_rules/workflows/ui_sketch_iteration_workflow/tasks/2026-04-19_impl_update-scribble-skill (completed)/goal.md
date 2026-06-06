---
task_id: TASK-PROC-032-03
type: impl
parent_requirement: REQ-PROC-032-04
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-04-19
session_completed_at: 2026-04-19T16:52:06Z
effort: L
created: 2026-04-19
started: 2026-04-19
session_id: 78fbebee-bee1-4529-944f-84d7e79ce180
session_account: web
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07]
  sections: [SEC-12, SEC-13, SEC-14]
scope_description: "Implement all 9 changes to ui-create-scribble skill and REQ-PROC-032 recommended by the two evaluation reports (TASK-PROC-032-02): multimodal input, Flutter handoff YAML, draft generators, diff-based regen, Widget Previews, flow-based screen ordering, cross-requirement iteration, flow composite index, component library"
release_description: ""
opus_recommended: false
worktree_path: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
---

# Goal: Update ui-create-scribble Skill — All Evaluation Findings

## Objective

Implement all changes to the `ui-create-scribble` skill and `REQ-PROC-032` as recommended by the two evaluation reports produced by TASK-PROC-032-02. The skill currently lacks multimodal input, has an indirect Flutter handoff, no flow-aware screen ordering, and no shared component library. All 9 changes must be implemented together as they are architecturally interdependent (e.g., `flow_positions` in metadata.yaml is needed by both the composite index generator and the cross-requirement iteration protocol).

## Requirements Summary

REQ-PROC-032 defines the full UI scribble iteration workflow. This task adds AC-12 through AC-19 and SEC-12 through SEC-14 to that requirement, and updates the skill and supporting files to implement them.

For the requirements state at task creation time:
```
git show fadfd042:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Must Read Before Implementing

1. **Evaluation report (5 changes)**: `tasks/2026-04-18_explore_scribble_skill_evaluation (completed)/plans_and_protocols/2026-04-18_01_protocol_evaluation_findings.md`
2. **Opus report (4 changes + tooling)**: `tasks/2026-04-18_explore_scribble_skill_evaluation (completed)/plans_and_protocols/2026-04-19_02_opus_screen_ordering_and_components.md`
3. **Current skill**: `.claude/skills/ui-create-scribble/skill.md`
4. **Current requirement**: `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md`
5. **Current README**: `requirements_tasks/SKETCHES_README.md`

## Scope

### In Scope

**From Report 1 (evaluation findings):**

1. **Phase 0 — Multimodal input** (AC-12): Before Phase 1 HTML generation, the skill checks for `inputs/sketch.{png,jpg,pdf}` or `inputs/reference.{png,jpg}` in the task/requirement folder. If present, the Phase 1 agent receives them as vision input to seed the HTML scribble structure. If absent, Phase 1 proceeds unchanged.

2. **Flutter handoff YAML** (AC-13): After approval (Phase 5), the skill emits `scribbles/v{n}/flutter_handoff.yaml` with per-element structured mapping: `html_selector → flutter_widget → material3_variant → persona_constraints[] → rules_applied[]`. The `ui-verify-flutter` skill is updated to consume this file instead of parsing HTML comments.

3. **Optional draft generators** (AC-14): New `draft_generator: claude_design | stitch | none` field in goal.md YAML. When set to `claude_design` or `stitch`, Phase 1 invokes the external tool to generate a first draft, then a second agent annotates it with personas and T1/T2 rules. Output is always a scribble (HTML + component mapping + metadata.yaml). Default is `none` (current behavior).

4. **Diff-based regeneration** (AC-15): When user feedback targets specific screens, the auto-review and next-version agents regen only affected screen files. metadata.yaml gains a `screen_versions: {}` map tracking per-screen version numbers. Unaffected screens are copied verbatim.

5. **Flutter Widget Previews** (AC-15 supplement, ui-verify-flutter): After implementation, the verification agent runs `flutter widget-previews` on new widgets and includes captured screenshots in `scribbles/flutter_review/comparison.md`.

**From Report 2 (Opus screen ordering + components):**

6. **Flow-based screen ordering** (AC-16): metadata.yaml gains a `flow_positions[]` array. Each screen entry has `{screen_file, flow_id, step_number, requirement_id}` coordinates read from the relevant `user_flows/<flow>/flow.md`. Numeric filename prefixes remain local-sort-only; canonical order comes from flow_positions. Phase 1 agents read the parent user flow to determine where new screens fit before numbering them.

7. **Cross-requirement iteration protocol** (AC-17): Haiku impact check in Phase 4 (Rule Update Protocol) is extended to cover three categories: (a) implemented requirements, (b) approved scribbles directly referencing the changed rule, (c) scribbles using shared components that reference the changed rule. metadata.yaml gains `stale_since` and `pending_rules[]` fields for approved-but-obsoleted scribbles.

8. **Flow-level composite index** (AC-18): New script `scripts/generate_flow_scribble_index.py` generates `requirements_user_needs/user_flows/<flow>/scribble_index.html` — a cross-requirement composite that iframes canonical scribble screens in flow-step order. The skill calls this script in a new Phase 5a after approval. Script reads flow.md steps + all requirement metadata.yaml `flow_positions` entries; no build system required.

9. **Component library** (AC-19): New folder `requirements_tasks/_scribble_components/` with:
   - `c_<name>/template.html` — HTML5 `<template>` fragment
   - `c_<name>/metadata.yaml` — component name, tier (T1/T2), rules applied, last updated
   - `components.js` — 40-line vanilla JS that resolves `<div data-component="c_xxx">` at page load
   - Seed components: `c_navigation_bar`, `c_app_bar`, `c_filled_button`, `c_mood_entry_card`
   - Component promotion follows T2/T3 tier process: T2 rule → corresponding component added/updated

### Out of Scope

- Changes to `ui-verify-flutter` or `ui-improve-flutter` beyond flutter_handoff.yaml consumption
- Actual integration with Google Stitch API (draft_generator: stitch is documented but requires Stitch MCP setup, which is a separate task)
- Changes to Flutter lib/ code or test/
- Visual design of seed components (wireframe quality only — grey/white placeholders)

## Acceptance Criteria

- [ ] **AC-12**: Phase 0 in skill.md — skill checks `inputs/` folder for sketch/reference images before Phase 1; passes them as vision context to Phase 1 agent if present
- [ ] **AC-13**: Flutter handoff YAML emitted after approval; `ui-verify-flutter` updated to consume it
- [ ] **AC-14**: `draft_generator` field documented in goal.md schema; Phase 1 conditionally delegates to Claude Design or Stitch; output is always scribble format
- [ ] **AC-15**: Diff-based regeneration — Phase 4 feedback classification includes "affects screen X" vs "affects all"; metadata.yaml `screen_versions` map implemented
- [ ] **AC-16**: `flow_positions[]` in metadata.yaml; Phase 1 reads parent flow to determine screen ordering; skill.md documents the algorithm
- [ ] **AC-17**: Expanded Haiku impact check in Phase 4 covers approved scribbles and shared components; `stale_since` + `pending_rules[]` lifecycle documented in skill.md and SKETCHES_README.md
- [ ] **AC-18**: `scripts/generate_flow_scribble_index.py` exists and generates correct composite HTML; Phase 5a in skill.md triggers it after approval
- [ ] **AC-19**: `requirements_tasks/_scribble_components/` exists with `components.js` and ≥4 seed components (c_navigation_bar, c_app_bar, c_filled_button, c_mood_entry_card); maintenance protocol documented in SKETCHES_README.md
- [ ] **REQ-PROC-032 updated**: AC-12..AC-19 and SEC-12..SEC-14 added to requirements.md with correct trackable_items entries
- [ ] **SKETCHES_README.md updated**: flow_positions schema, flutter_handoff.yaml format, component library usage, stale_since lifecycle
- [ ] No regressions to existing skill phases (Phase 1–5 behavior unchanged for `draft_generator: none` and no `inputs/` folder)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-032-02 | completed | Evaluation reports that define all 9 changes |

## Notes

- Implement changes in this order to minimize rework: AC-16 (flow_positions schema) → AC-17 (expanded impact check) → AC-12 (Phase 0) → AC-13 (handoff YAML) → AC-18 (composite script) → AC-19 (component library) → AC-14 (draft generators) → AC-15 (diff-based regen)
- The `flow_positions` metadata.yaml field is the foundation — AC-17 and AC-18 both depend on it
- `components.js` must be JavaScript-free fallback compatible (components render as empty divs if JS is disabled) — wireframe-level only
- The skill.md is token-sensitive context loaded into every agent; keep changes concise; prefer inline parentheticals over block comments
