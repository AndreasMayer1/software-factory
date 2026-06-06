# Plan: Scribble Multi-Breakpoint from Persona Device Classes
Date: 2026-06-01
Task: TASK-PROC-032-13
AC: AC-32

## Objective

Implement AC-32: personas declare device classes; a requirement's required breakpoint set = union across served personas; scribbles are generated per required breakpoint with shared-screen deduplication.

## Design Decisions

### D1: device_classes taxonomy

Values: `mobile | tablet | desktop | none`

- `mobile` — phone-sized (up to ~600dp). Renders NavigationBar.
- `tablet` — tablet-sized (600dp–1200dp). Renders NavigationRail or NavigationBar.
- `desktop` — large screen / desktop (1200dp+). Renders NavigationRail or NavigationDrawer.
- `none` — persona uses no digital device in this app context (e.g., Prof. Weber in therapeutic context).

### D2: Where device_classes lives

Added to the `pcd:` block in persona YAML frontmatter as a list:

```yaml
pcd:
  device: "Windows desktop (office), occasional tablet"
  device_classes: [desktop, tablet]
  energy_sensitivity: low
  data_sensitivity: high
```

The free-text `device` field is retained (human-readable description). `device_classes` is the structured field for machine consumption.

### D3: Persona → device_classes mapping (all personas)

| Persona file | device description (existing) | device_classes |
|---|---|---|
| max_client | Budget Android 2020-2022 | [mobile] |
| sophie_structure_seeker | Smartphone 2020-2023 | [mobile] |
| dr_sarah | Windows desktop (office), occasional tablet | [desktop, tablet] |
| lisa_waitlist_bridger | Android 10+ / iOS 14+ student phone | [mobile] |
| app_provider | Development machine (Windows/Mac/Linux) | [desktop] |
| david_structure_seeker | Android 8+ / iOS 13+ mid-range | [mobile] |
| rahel | Mid-range Android 2019-2022 (accessibility) | [mobile] |
| amina | Mid-range Android 2020-2023 | [mobile] |
| dr_med_turan | Windows desktop (clinic KIS) | [desktop] |
| prof_dr_weber | None in therapeutic context | [] |
| michael_high_performer | iPhone 12+ / Android flagship | [mobile] |
| hanna_sleepless | Android 10+ / iOS 14+ mid-range | [mobile] |
| jana_high_strung | Smartphone 2018-2023 | [mobile] |
| elias_skeptical_guardian | Mid-range smartphone 2019-2022 | [mobile] |
| nina_energy_budgeter | iPhone or Android 2020+, Garmin watch | [mobile] |
| lena_depth_seeker | iPhone 2020-2024 mid-range | [mobile] |
| felix | Mid-range Android 2019-2022 | [mobile] |
| system_maintenance | (no pcd block) | (skip) |

Note: `prof_dr_weber` uses `[]` (empty) because the persona uses no digital device in therapeutic context. The device on record is personal and unused professionally.

### D4: How required_breakpoints is derived in ui-scribble-iterate

1. Read requirement frontmatter field `personas_served:` (list of PERSONA-IDs)
2. For each PERSONA-ID, find the persona file in `requirements_user_needs/personas/` using `grep -rl "persona_id: PERSONA-XXX"`
3. Read `pcd.device_classes` from each persona's YAML frontmatter
4. Compute: `required_breakpoints = sorted(unique(all device_classes)) minus {none and empty}`
5. Fallback: if result is empty → use `[mobile]`
6. Store in `scribbles/breakpoints.yaml` alongside pre_brief.md
7. Pass to Phase 1 generator as `required_breakpoints`

Single-breakpoint shortcut: if `required_breakpoints` has exactly one item → no multi-breakpoint overhead; generate normally.

### D5: Per-breakpoint generation logic in ui-scribble-generator

When `required_breakpoints` is provided (multiple values):

**Planning step (step 2)**: For each screen, mark it as:
- `per_breakpoint` — layout changes across breakpoints (navigation pattern shift, column→row reflow, grid changes)
- `shared` — layout is identical across all breakpoints (dialogs, simple overlays, loading states, error states)

Heuristic for "shared": a screen is shared if it meets ALL of:
- No navigation widget in body (dialog/overlay/fullscreen without NavigationBar)
- No grid/layout reflow (same column structure at all widths)
- No secondary content panels that appear at wider breakpoints

**File naming**:
- Single breakpoint: `NN_[screen_name].html` (existing convention, unchanged)
- Multi-breakpoint, per-breakpoint screen: `NN_[screen_name].[breakpoint].html`
- Multi-breakpoint, shared screen: `NN_[screen_name].shared.html`

**index.html for multi-breakpoint**:
- Section per breakpoint listing its screens
- Shared screens section at bottom
- Note: "Shared screens render identically across [mobile, desktop] — generated once"

**metadata.yaml additions**:
```yaml
required_breakpoints: [mobile, desktop]
shared_screens: [03_dialog.shared.html, 06_error.shared.html]
per_breakpoint_screens:
  mobile: [01_home.mobile.html, 02_list.mobile.html]
  desktop: [01_home.desktop.html, 02_list.desktop.html]
```

### D6: Breakpoints file

`scribbles/breakpoints.yaml` stores the derived breakpoints and their source, written by ui-scribble-iterate Phase 0.3 before first generation. This persists across sessions so re-generations don't re-derive.

```yaml
required_breakpoints: [mobile, desktop]
derived_from:
  - persona_id: PERSONA-001
    file: requirements_user_needs/personas/dr_sarah/persona.md
    device_classes: [desktop, tablet]
  - persona_id: PERSONA-002
    file: requirements_user_needs/personas/max_client/persona.md
    device_classes: [mobile]
fallback_used: false
```

Note: `tablet` class from dr_sarah collapses to desktop in the union since mobile+tablet+desktop → we generate mobile and desktop (tablet layout is an intermediate; the RE-DERIVE responsive breakpoint mechanics handle the tablet range between those two anchor layouts).

Actually, revising: `tablet` is a distinct class. Don't collapse it. If personas use tablet, generate a tablet breakpoint. The RE-DERIVE items (exact pixel breakpoints) are handled by the implementation.

Revised: `required_breakpoints = union of all device_classes excluding none/empty`. So if we have `[mobile, desktop, tablet]`, we generate 3 breakpoints.

## Deliverables

1. **README_3_PERSONA_DEFINITION.md** — updated PCD section documenting `device_classes` field + enum values + instructions for filling it in
2. **17 persona files** — `device_classes` added to `pcd:` block per mapping in D3
3. **ui-scribble-generator agent** — MUST-DO steps updated for per-breakpoint generation
4. **ui-scribble-iterate skill** — Phase 0.3 added for breakpoint derivation; Phase 1 passes `required_breakpoints`; Phase 3 mentions breakpoints in user-facing message

## Agent assignments

- **Agent A** (background): README_3_PERSONA_DEFINITION.md + all persona file edits
- **Agent B** (background): ui-scribble-generator + ui-scribble-iterate changes (using claude-modify-agent + claude-modify-skill)

Agents run in parallel (no file overlap).
