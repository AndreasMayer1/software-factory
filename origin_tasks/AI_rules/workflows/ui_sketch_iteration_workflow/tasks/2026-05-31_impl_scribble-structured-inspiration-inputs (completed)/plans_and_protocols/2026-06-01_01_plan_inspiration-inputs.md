# Plan: Scribble Structured Inspiration Inputs (TASK-PROC-032-14)

Date: 2026-06-01
AC covered: AC-33

## Objective

Define and implement the `inputs/inspiration.yaml` convention so that
ui-scribble-generator Phase 0 can pattern a scribble after explicitly chosen
aspects of a reference design, while ignoring others in favour of project
conventions.

## Deliverables

1. **SKETCHES_README.md** — new "Structured Inspiration Inputs" section documenting
   the convention: YAML schema, aspect keys, screen_scope, annotation format.
   Also: update folder-structure diagram to include `inputs/` directory.

2. **ui-scribble-generator.md** (via claude-modify-agent) — new step 0b in the
   MUST-DO list that reads `inputs/inspiration.yaml`, applies used aspects to
   screen design, and annotates each affected screen with the inspiration source.

3. **ui-scribble-generator.contract.yaml** — add `inputs/inspiration.yaml` to
   `consumes:`. This requires the Artifact-Establishment Gate; in automated mode
   this triggers a pending_feedback escalation.

## `inputs/inspiration.yaml` Schema

```yaml
references:
  - id: ref_001                          # unique within this file
    source: "inputs/screenshot.png"      # local path or descriptive label
    label: "Short label for annotation"
    note: "Optional free-text explanation"
    screen_scope: []                     # empty/absent = all screens; else list of
                                         # screen-name fragments to limit scope
    use:
      layout: false          # spatial arrangement / column grid
      colors: false          # color palette (usually false → project tokens)
      typography: false      # font-size / weight relationships
      spacing: false         # whitespace proportions
      iconography: false     # icon style / density
      navigation_pattern: false  # nav paradigm (bottom bar, rail, drawer)
      card_structure: false  # list-item / card shape and content layout
      empty_state: false     # empty-state design pattern
      loading_state: false   # loading indicator pattern
      dialog_pattern: false  # dialog / bottom-sheet choice
      form_layout: false     # form-field arrangement
```

## Generator Phase 0b Behaviour

1. Before generating any screen, check for `inputs/inspiration.yaml` alongside
   the requirement (same directory as requirements.md).
2. If present, parse each reference entry.
3. For each aspect with `use: true`:
   - Extract the structural pattern from the source.
   - Pattern the relevant design decision after it (layout grid, spacing ratio,
     nav pattern, etc.).
4. For each aspect with `use: false`:
   - Ignore the reference; apply project conventions from doc/presentation/.
5. Per-screen annotation: add an HTML comment at the top of each affected screen:
   `<!-- inspiration: ref_001 "Label" — used: layout, spacing -->`
6. If `screen_scope` is non-empty, restrict annotation + patterning to screens
   whose filename fragment matches any entry in `screen_scope`.
7. Summarise applied inspiration in `metadata.yaml` under a new
   `inspiration_applied[]` list.

## Execution Steps

1. [x] Create plans_and_protocols/ + this plan
2. [ ] Update SKETCHES_README.md (inline Edit)
3. [ ] Invoke claude-modify-agent for ui-scribble-generator.md
4. [ ] Complete via task-complete skill
