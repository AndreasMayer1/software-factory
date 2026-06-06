---
name: ui-scribble-cross-feature-checker
description: Check component consistency across sibling-feature scribbles sharing a user flow
tools: Read, Glob, Grep, Bash
model: haiku
---

Check whether the current scribble uses the same Flutter components for the same UI roles as
sibling features that share the same user flow. Flag divergences for human resolution.

Spawned by `ui-scribble-auto-review` (Phase 2) when the current scribble has `flow_positions`.

## Inputs

Caller passes:
- `scribble_path`: path to `scribbles/v{n}/` for the current feature (e.g. `requirements_tasks/scribbles/mood_entry/v3/`)
- `feature_path`: the current feature's path (from `metadata.yaml feature_path`)

## Steps

### 1. Read current scribble metadata

Read `{scribble_path}/metadata.yaml`.
- Extract `flow_positions` → list of `flow_id` values.
- Extract `flutter_component_mapping` (keys = HTML element names/classes, values = Flutter widget names).

If `flow_positions` is empty or absent: output `NO_FLOW_POSITIONS — cross-feature check skipped.` and stop.

### 2. Find sibling scribbles

For each `flow_id` in `flow_positions`:
- Find all `metadata.yaml` files under `requirements_tasks/scribbles/` recursively using Bash:
  ```bash
  grep -rl "flow_id: <flow_id>" requirements_tasks/scribbles/ 2>/dev/null
  ```
- Include a file if: (a) the flow_id appears in its `flow_positions`, AND (b) its `feature_path` differs from the current feature's `feature_path`.
- For each sibling feature: use only its highest-version scribble with `status` in `[draft, reviewed, approved]` (skip `superseded` / `stale`).

If no siblings found: output `NO_SIBLINGS_FOUND — cross-feature check skipped.` and stop.

### 3. Compare component mappings

For each sibling, compare its `flutter_component_mapping` against the current scribble's:
- **Shared key (same HTML element name/class)**: if the Flutter widget value differs → divergence.
- **Key present in one only**: gap — note but do not flag as divergence.

### 4. HTML fallback when mapping metadata absent

If the current scribble or a sibling lacks `flutter_component_mapping` (the field is absent or empty), read the HTML screens (index.html or individual screen files) and extract component usage:
- Look for `data-flutter-widget` attributes.
- Look for `class` values that appear in a `<!-- flutter-component-mapping: ... -->` comment block.
- Look for button/interactive element patterns annotated with Flutter widget names.
Compare extracted values as in step 3.

### 5. Output

Emit a structured report:

```
## Cross-Feature Consistency Check

Current feature: {feature_path}
Flows checked: {flow_id1}, {flow_id2}, …
Siblings compared: {sibling_feature_path1} (v{n}), {sibling_feature_path2} (v{n}), …

### Divergences — Human Resolution Needed
| UI Role / Element | Current Feature | Sibling Feature | Flow |
|---|---|---|---|
| {element_name} | {widget_a} | {widget_b} | {flow_id} |

### Gaps (element present in one feature only — informational)
{element_name}: present in {feature_path}, absent in {sibling_path}

### Consistent (no action needed)
{element_name}: {widget} — matches across all siblings checked
```

If there are no divergences, replace the divergences table with:
`No divergences found across {n} sibling(s).`
