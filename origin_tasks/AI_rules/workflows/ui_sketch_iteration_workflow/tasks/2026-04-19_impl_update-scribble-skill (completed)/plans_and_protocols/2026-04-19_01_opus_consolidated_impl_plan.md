---
agent: claude-opus-4-7
date: 2026-04-19
task: TASK-PROC-032-03
based_on:
  - 2026-04-18_01_protocol_evaluation_findings.md
  - 2026-04-19_02_opus_screen_ordering_and_components.md
status: complete
---

# Consolidated Implementation Plan: Update ui-create-scribble Skill (All 9 Changes)

This document is the authoritative retrospective reconciliation of two independently-authored Opus evaluation reports (TASK-PROC-032-02) and explains how their 9 combined proposals were merged into a single coherent implementation. Read this file alongside the current `skill.md`, `requirements.md`, and `SKETCHES_README.md` to understand every design decision made.

---

## 1. Reconciliation Summary

Two reports were produced by separate Opus sessions before this implementation task began. They were architecturally compatible but contained naming inconsistencies and one path disagreement that required resolution.

### 1.1 Items with NO conflict

| Topic | Report 1 | Report 2 | Outcome |
|---|---|---|---|
| metadata.yaml `screen_versions` | AC-15: diff-based regen counter | (not mentioned) | Implemented as specified |
| metadata.yaml `flow_positions[]` | (not mentioned) | AC-16: flow+step anchoring | Implemented as specified |
| metadata.yaml `stale_since` + `pending_rules[]` | (not mentioned) | AC-17: staleness lifecycle | Implemented as specified |
| Phase 0 multimodal input | AC-12 | (not mentioned) | Implemented as specified |
| Component library | (not mentioned) | AC-19 | Implemented as specified |

All metadata.yaml fields from both reports use distinct names and serve distinct purposes. They were merged into a single canonical schema with no field collisions.

### 1.2 Phase numbering inconsistency — RESOLVED

Report 1 proposed a "Phase 6 — Emit Flutter Handoff" for the `flutter_handoff.yaml` step. Report 2 proposed "Phase 5a" for composite index generation, also placed after Phase 5.

Resolution: The flutter handoff was absorbed into Phase 5 as step 3 (it is a completion action on approval, not a standalone phase). The composite index became Phase 5a (a conditional post-approval script invocation). "Phase 6" numbering was dropped. The skill now reads Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 5a, with no gap.

### 1.3 Diff-based regen vs. per-screen versioning — NOT the same thing

Report 1's `screen_versions{}` (AC-15) tracks how many times each screen file has been regenerated within a single requirement's scribble cycle. Report 2's `flow_positions[]` (AC-16) tracks which flow step each screen maps to. The names and the data are completely different. There was no reconciliation needed — both fields were implemented.

### 1.4 Composite index path — MINOR INCONSISTENCY RESOLVED

Report 2 §3 specified the composite index path as `requirements_user_needs/user_flows/<flow>/scribbles/index.html`. The implementation plan chose `requirements_user_needs/user_flows/<flow>/scribble_index.html` (flat path at the flow directory root).

Rationale for the flat path: creating a `scribbles/` subdirectory inside a flow folder would be an empty folder until the first scribble is approved. The flat `scribble_index.html` file is created on demand by the script with no orphaned directories. Both paths were functionally equivalent; the flat path was simpler. The script and Phase 5a both use the flat path consistently.

### 1.5 flutter_handoff.yaml and component library — ADDITIVE, not conflicting

Report 2 §8 raised the open question of whether `flutter_handoff.yaml` should list `component_library_entry` IDs per element. This was not implemented: the flutter_handoff.yaml format covers `html_selector → flutter_widget → material3_variant → persona_constraints[] → rules_applied[]` but does not include a `component_id` back-reference. This is a known gap (see §8 below).

### 1.6 Phase 4 impact check — Report 2 is a superset of Report 1

Report 1 preserved the existing single-category impact check (implemented requirements only). Report 2 expanded it to three categories. The implementation uses Report 2's three-category version, which fully subsumes Report 1's intent. No content from Report 1's impact check description was lost.

---

## 2. Unified metadata.yaml Schema

The canonical schema after all 9 changes, with annotations showing which AC introduced each new field:

```yaml
version: v2
date: 2026-04-19
status: approved            # draft | superseded | approved
requirement: REQ-[ID]
screens_covered:
  - 01_home_night_mode: "Home screen with night mode active"
  - 02_quick_entry: "Quick entry screen for voice input trigger"
personas_applied:
  - PERSONA-002 (Max): blank-field paralysis → structured prompts used
  - PERSONA-007 (Hanna): dark mode → true black backgrounds
rules_applied:
  - T1: touch targets ≥ 48dp (doc/presentation/design/t1_touch_targets.md)
  - T1: dark mode backgrounds (doc/presentation/design/t1_dark_mode.md)
flutter_component_mapping:
  button.primary: FilledButton (M3)
  text_input: TextField with OutlineInputBorder
  card: Card with Material3 surfaceVariant
  bottom_nav: NavigationBar (M3)
  app_bar: AppBar with Material3 surface tint
new_rules_anchored: []
design_decisions:
  - decision: "Mood input uses slider, not discrete buttons"
    reason: "Continuous assessment; reduces anchoring bias"
    applies_to: [01_mood_entry.html]

# --- AC-16: Flow-based screen ordering ---
flow_positions:             # omit if requirement has no parent flow
  - screen_file: 01_home_night_mode.html
    flow_id: FLOW-007
    step_number: 3
    requirement_id: REQ-FUNC-014

# --- AC-15: Diff-based regeneration ---
screen_versions:            # omit until first targeted regeneration occurs
  01_home_night_mode.html: 1
  02_quick_entry.html: 2    # regenerated once for targeted feedback

# --- AC-17: Staleness lifecycle ---
stale_since: ""             # YYYY-MM-DD; set when a post-approval rule change invalidates this scribble
pending_rules: []           # rule IDs that changed after approval
```

Fields `reuses_screen`, `variant_of`, and `component_library_entry` (proposed in Report 2 for cross-requirement screen reuse and chrome-role components) were documented in Report 2 but not added to the canonical skill.md schema in this task. They remain available as optional extensions for future use when cross-requirement screen reuse is first needed in practice.

---

## 3. Skill.md Changes

The pre-task skill had Phase 1 through Phase 5 (approximately 80 lines). The post-task skill has Phase 0 through Phase 5a (approximately 190 lines). Changes by phase:

### Phase 0 — NEW (AC-12)

Did not exist before this task. Added before Phase 1. The skill checks `inputs/sketch.{png,jpg,pdf}` and `inputs/reference.{png,jpg}` in the task/requirement folder. If any files exist, they are passed as vision input to the Phase 1 agent to seed the HTML scribble. If absent, Phase 1 proceeds unchanged. No external tool required — uses Claude's native multimodal capability.

### Phase 1 — MODIFIED (AC-14, AC-16)

Two additions at the top of Phase 1, before the agent spawn instruction:

**AC-14 draft_generator check**: Reads `draft_generator` field from goal.md YAML. Values: `none` (default, unchanged behavior), `claude_design` (invokes Claude Design for first-draft HTML, then second agent annotates with personas/rules), `stitch` (documented but unsupported until Stitch MCP is configured — a separate task). In all cases, output is the standard `scribbles/v{n}/` format.

**AC-16 flow_context**: Before spawning the Phase 1 agent, checks whether `requirements.md` has a `user_needs:` YAML entry linking to a flow. If yes, reads `requirements_user_needs/user_flows/<flow>/flow.md` to extract step order and passes a `flow_context` (ordered list of step labels + step numbers) to the Phase 1 agent. The agent assigns each screen a `flow_positions` entry: `{screen_file, flow_id, step_number, requirement_id}`. Numeric filename prefixes (01_, 02_, …) reflect local sort only; canonical order comes from `flow_positions` in metadata.yaml. If no flow reference exists, the pre-task behavior is unchanged.

The spawned agent instructions (the indented prose block with MUST/MUST-NOT rules) were not changed.

### Phase 2 — MODIFIED (AC-15)

One clause added after the existing auto-review checks list:

"If the triggering feedback classified specific screens (screen scope from Phase 4): regenerate only those screens; copy the rest from v{n}. Update `screen_versions` for regenerated files only."

This makes Phase 2 aware of the diff-based regen path introduced in Phase 4. When feedback is targeted (not structural), Phase 2 performs a partial regeneration rather than a full one.

### Phase 4 — MODIFIED (AC-15, AC-17)

Two additions:

**AC-15 screen scope classification**: After the existing tier classification step, a new sub-step classifies whether the feedback affects specific screens or all screens. Specific-screen feedback triggers the diff-based path (regenerate only affected files, copy others, update `screen_versions` for changed screens). All-screens feedback triggers full regeneration as before.

**AC-17 expanded impact check**: Replaced the single-category Haiku impact check with a three-category check:
- (a) Implemented requirements with Presentation Layer scope (grep `requirements_tasks/` for `status: done`) — unchanged from before
- (b) Approved scribbles whose `metadata.yaml` `rules_applied` references the changed rule — new
- (c) Approved scribbles whose `metadata.yaml` `flutter_component_mapping` references a component whose `_scribble_components/<c_name>/metadata.yaml` lists the changed rule — new, depends on AC-19 component library

For each stale approved scribble found (categories b/c), the skill marks its `metadata.yaml` with `stale_since: <date>` and `pending_rules: [<rule_id>]`.

### Phase 5 — MODIFIED (AC-13)

A new step 3 was inserted between the existing step 2 (update previous version's metadata to `status: superseded`) and the existing report step:

"3. Emit `scribbles/v{n}/flutter_handoff.yaml` — spawn a brief agent to read all approved screen HTML files and output structured per-element mapping."

The handoff format: `screens[] → elements[] → {html_selector, flutter_widget, material3_variant, persona_constraints[], rules_applied[]}`. The agent reads component mapping blocks from each HTML file for selectors; reads metadata.yaml for personas and rules.

The `ui-verify-flutter` skill was updated to check for `flutter_handoff.yaml` in Phase 1 (step 2b: if present, use it as primary component mapping source; if absent, fall back to parsing HTML comment blocks).

### Phase 5a — NEW (AC-18)

Did not exist before this task. Added after Phase 5. Conditional on whether the requirement references a user flow. If yes:

```
python scripts/generate_flow_scribble_index.py --flow <flow_id>
```

This regenerates `requirements_user_needs/user_flows/<flow>/scribble_index.html` — a composite view of all approved scribbles serving that flow, in flow-step order. Deterministic; no agent involved. Skip if the requirement has no parent flow.

---

## 4. New Files Created

### `scripts/generate_flow_scribble_index.py`

Purpose: Deterministically generates `requirements_user_needs/user_flows/<flow>/scribble_index.html` for one or all flows that have approved scribbles with `flow_positions` entries.

CLI: `python scripts/generate_flow_scribble_index.py [--flow FLOW-ID] [--dry-run]`

Algorithm:
1. Scans `requirements_tasks/**/scribbles/*/metadata.yaml` for `status: approved` files with `flow_positions[]`.
2. Groups screens by `flow_id`.
3. For each flow, locates the flow directory by grepping `requirements_user_needs/user_flows/**/flow.md` for `id: <flow_id>` in frontmatter.
4. Sorts screens by `step_number`.
5. Emits an HTML file with `<iframe>` per screen (absolute paths from project root), step labels, and requirement badge.

Output path: `<flow_dir>/scribble_index.html` (flat, at the flow directory root — not in a `scribbles/` subfolder).

Parallel to existing scripts like `generate_status_overview.py` in style (Python, no dependencies beyond PyYAML, plain string concatenation for HTML).

Added to CLAUDE.md Section 10 "Generated Files" table: "`scripts/generate_flow_scribble_index.py` → `requirements_user_needs/user_flows/<flow>/scribble_index.html`".

### `requirements_tasks/_scribble_components/` directory

Purpose: Shared wireframe-quality HTML5 template fragments reused across per-requirement scribbles. Prevents duplication of common chrome elements; enables single-point updates when a T1/T2 rule affects a shared component.

Files created:

| Path | Purpose |
|---|---|
| `_scribble_components/components.js` | ~50-line vanilla JS that resolves `<div data-component="c_xxx">` by fetching and inserting `c_xxx/template.html` at page load. Degrades gracefully (renders placeholder text) if JS disabled or fetch fails. |
| `_scribble_components/c_navigation_bar/template.html` | NavigationBar (M3) with 3 destinations, inline styles, 48dp minimum height |
| `_scribble_components/c_navigation_bar/metadata.yaml` | `flutter_widget: NavigationBar`, `tier: T1`, `rules_applied: [T1 touch targets]` |
| `_scribble_components/c_app_bar/template.html` | AppBar with back button, title, trailing action — all 48dp minimum |
| `_scribble_components/c_app_bar/metadata.yaml` | `flutter_widget: AppBar`, `tier: T1`, `rules_applied: [T1 touch targets]` |
| `_scribble_components/c_filled_button/template.html` | FilledButton (M3) with 48dp minimum height and 12dp radius |
| `_scribble_components/c_filled_button/metadata.yaml` | `flutter_widget: FilledButton`, `tier: T1`, `rules_applied: [T1 touch targets]` |
| `_scribble_components/c_mood_entry_card/template.html` | Card with structured prompt, slider, and tag chips — PERSONA-002 (Max) blank-field paralysis constraint applied |
| `_scribble_components/c_mood_entry_card/metadata.yaml` | `flutter_widget: Card`, `tier: T2`, `rules_applied: [T1 touch targets, T2 mood input uses slider]`, `personas_applied: [PERSONA-002]` |

Usage in scribble HTML:
```html
<script src="/requirements_tasks/_scribble_components/components.js"></script>
<div data-component="c_navigation_bar"></div>
```

The `components.js` resolves the script's own src attribute to compute the base path, making it work from any depth in the filesystem under `requirements_tasks/`.

---

## 5. requirements.md Additions

Added to `trackable_items.acceptance_criteria`:

| AC | Name | One-line description |
|---|---|---|
| AC-12 | Optional multimodal input seed | Phase 0 checks `inputs/` folder for sketch/reference images; passes as vision context to Phase 1 if present |
| AC-13 | Flutter handoff YAML | Phase 5 emits `scribbles/v{n}/flutter_handoff.yaml` with per-element `html_selector → flutter_widget → material3_variant → persona_constraints[] → rules_applied[]`; `ui-verify-flutter` consumes it as primary source |
| AC-14 | Optional draft generators | `draft_generator` field in goal.md YAML (`claude_design \| stitch \| none`); Phase 1 delegates to external tool for first draft; output always standard scribble format; default `none` = unchanged behavior |
| AC-15 | Diff-based regeneration | Phase 4 classifies feedback as screen-specific or all-screens; `screen_versions{}` map in metadata.yaml tracks per-screen regen counters; unaffected screens copied verbatim |
| AC-16 | Flow-based screen ordering | `flow_positions[]` in metadata.yaml; Phase 1 reads parent flow to determine canonical screen order; numeric prefixes are local sort only |
| AC-17 | Cross-requirement iteration protocol | Phase 4 Haiku impact check covers (a) implemented requirements, (b) approved scribbles referencing the changed rule, (c) scribbles using shared components referencing the rule; `stale_since` + `pending_rules[]` lifecycle |
| AC-18 | Flow-level composite index | `scripts/generate_flow_scribble_index.py` generates `user_flows/<flow>/scribble_index.html`; Phase 5a triggers it after approval when a flow reference exists |
| AC-19 | Component library | `requirements_tasks/_scribble_components/` with `components.js` and 4 seed components; maintenance protocol in SKETCHES_README.md |

Added to `trackable_items.sections`:

| SEC | Name | Heading |
|---|---|---|
| SEC-12 | Flow-Aware Scribble Generation | `## Flow-Aware Scribble Generation` |
| SEC-13 | Flow-Level Composite Index | `## Flow-Level Composite Index` |
| SEC-14 | Component Library | `## Component Library` |

---

## 6. SKETCHES_README.md Additions

Four new sections were added to `requirements_tasks/SKETCHES_README.md`. All were inserted into the existing document without altering prior content:

### Section: `flow_positions` Field (optional)

Inserted after the `## metadata.yaml Format` section. Documents the `flow_positions[]` field with a YAML example (`screen_file`, `flow_id`, `step_number`, `requirement_id`). States: numeric prefixes are local sort helpers only; canonical screen order comes from `flow_positions`; omit if no parent flow.

### Section: Stale Scribble Lifecycle

Inserted after the `## Version Lifecycle` section. Documents the `stale_since` and `pending_rules` fields — what each means, when the Rule Update Protocol sets them, that `status: approved` is preserved (implementation can still reference the scribble), and how to clear stale status (re-run `ui-create-scribble`). Also documents the `screen_versions{}` map sub-section: explains diff-based regen, that unaffected screens are copied verbatim, only feedback-affected screens are incremented.

### Section: `flutter_handoff.yaml` (generated after approval)

Inserted after the `## Component Mapping Block` section. Documents the full YAML format of the handoff file (`screens[] → elements[] → {html_selector, flutter_widget, material3_variant, persona_constraints[], rules_applied[]}`). States that `ui-verify-flutter` reads this file first if present.

### Section: Component Library (`_scribble_components/`)

Inserted after the `## After Implementation` section. Documents: location (`requirements_tasks/_scribble_components/`), how to use a component in a scribble HTML file (script tag + `<div data-component="...">`), JS-disabled fallback behavior, seed component table (4 entries with Flutter widget and tier), and maintenance protocol (when to update vs. create components; wireframe-quality only; no JS in template.html fragments).

---

## 7. Implementation Order Used

The implementation followed the order: **AC-16 → AC-17 → AC-12 → AC-13 → AC-18 → AC-19 → AC-14 → AC-15**

Rationale for each dependency:

| Step | AC | Why this position |
|---|---|---|
| 1 | AC-16 (flow_positions schema) | Foundation. AC-17's impact check queries `flow_positions`; AC-18's script reads `flow_positions`. Both depend on the field existing. Must go first. |
| 2 | AC-17 (expanded impact check + stale fields) | Extends Phase 4 and defines `stale_since`/`pending_rules`. Placed before Phase 0–Phase 5 additions so the full impact protocol is in place before adding new phases. |
| 3 | AC-12 (Phase 0 multimodal) | Adds a new phase before Phase 1. No dependencies on AC-13–AC-19. Early placement keeps the phase-by-phase skill changes sequential. |
| 4 | AC-13 (flutter_handoff.yaml) | Extends Phase 5 with a new step. No dependency on AC-18 (Phase 5a) but must be added before Phase 5a so Phase 5 step numbering is stable. |
| 5 | AC-18 (composite script + Phase 5a) | Creates the new Python script and Phase 5a, which calls it. Depends on AC-16 (`flow_positions` fields) having been defined. Adds Phase 5a after the now-finalized Phase 5. |
| 6 | AC-19 (component library) | Creates `_scribble_components/` folder structure. No dependency on AC-14 or AC-15; placed here to establish the library before Phase 4's impact check (category c) references it in skill behavior. |
| 7 | AC-14 (draft generators) | Extends Phase 1 with the `draft_generator` check. Placed late because it is an optional input-side feature with no structural dependencies on earlier ACs. |
| 8 | AC-15 (diff-based regen) | Extends Phase 2 and Phase 4. Placed last because it references Phase 4's "screen scope classification" (added in this same step) and Phase 2's regen path. No other ACs depend on it. |

---

## 8. What Was NOT Implemented

### Widget Previews integration in `ui-verify-flutter` (deferred)

Report 1 §6.5 proposed that after Flutter implementation, the verification agent runs `flutter widget-previews` on new widgets and captures screenshots for inclusion in `scribbles/flutter_review/comparison.md`. This was listed in goal.md's scope but placed in "Out of Scope" as "Changes to `ui-verify-flutter` or `ui-improve-flutter` beyond flutter_handoff.yaml consumption." Flutter Widget Previews (Flutter 3.35, August 2025) are available and supported; this integration is a future task for the `ui-verify-flutter` skill specifically.

### Stitch MCP integration (placeholder only)

Report 1 AC-14 described `draft_generator: stitch` as a viable path if Stitch MCP is configured. The `stitch` option is documented in Phase 1 of skill.md with a note: "Stitch MCP setup is a separate task; document as unsupported until configured." No actual Stitch API calls or MCP wiring were implemented. This is an explicit out-of-scope deferral, not an oversight.

### Component backrefs script (`scripts/update_component_backrefs.py`)

Report 2 §8 raised as an open question whether the `used_by_requirements:` field in component metadata.yaml should be script-maintained rather than hand-maintained. No such script was created. The field is absent from the seed component metadata.yaml files in `_scribble_components/`. If component reuse tracking becomes important in practice, a small script analogous to `generate_flow_scribble_index.py` could populate this field by scanning all metadata.yaml files for component references.

### `flutter_handoff.yaml` component_library_entry enrichment

Report 2 §8 suggested that `flutter_handoff.yaml` could list the component IDs (e.g., `c_navigation_bar`) used per screen, making the handoff mapping richer for `ui-verify-flutter`. The implemented `flutter_handoff.yaml` format does not include this field. The flutter_handoff.yaml agent reads component mapping comment blocks from HTML files; those blocks do not currently record `<div data-component="...">` references. Closing this gap would require the Phase 1 generation agent to record component usage in each screen's HTML comment block AND the flutter_handoff.yaml agent to extract and forward it.

### `reuses_screen`, `variant_of`, `components_used[]`, `component_library_entry` metadata fields

Report 2 §1.3 and §1.6 proposed these additional metadata.yaml fields for cross-requirement screen reuse (`reuses_screen`, `variant_of`) and chrome-role component tracking (`component_library_entry`). None were added to the canonical metadata.yaml schema in skill.md or SKETCHES_README.md. They are available to add when the first real cross-requirement screen reuse situation occurs — there are no existing scribbles yet, so adding these fields now would be premature. The field names are reserved in this document to prevent future naming collisions.

### Composite index at `scribbles/index.html` vs `scribble_index.html` (path decision)

Report 2 §3 specified the path as `requirements_user_needs/user_flows/<flow>/scribbles/index.html`. The implemented script writes to `requirements_user_needs/user_flows/<flow>/scribble_index.html` (flow directory root, no `scribbles/` subfolder). The rationale: the `scribbles/` subfolder would need to be created as an empty directory until the first composite index is generated, adding filesystem noise with no benefit. The flat path `scribble_index.html` is self-describing and matches the naming pattern already used by `scribble_index` concepts elsewhere. The script and Phase 5a are internally consistent on this path.
