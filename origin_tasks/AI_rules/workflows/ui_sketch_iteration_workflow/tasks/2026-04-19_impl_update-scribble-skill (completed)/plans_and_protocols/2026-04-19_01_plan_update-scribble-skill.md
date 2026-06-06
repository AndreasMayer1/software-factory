# Opus Plan: Update ui-create-scribble Skill — All 9 Evaluation Changes

## Objective

Implement AC-12 through AC-19 for REQ-PROC-032 by updating:
- `.claude/skills/ui-create-scribble/skill.md` (new phases + phase modifications)
- `.claude/skills/ui-verify-flutter/skill.md` (consume flutter_handoff.yaml)
- `requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md` (add AC/SEC entries)
- `requirements_tasks/SKETCHES_README.md` (4 new sections)
- `scripts/generate_flow_scribble_index.py` (new script, AC-18)
- `requirements_tasks/_scribble_components/` (new folder, AC-19)

## Analysis Summary

The current `ui-create-scribble` skill (skill.md, ~120 lines) has 5 phases. All 9 changes fall into three buckets:

1. **metadata.yaml schema extensions** (AC-16, AC-17, AC-15): `flow_positions[]`, `stale_since`, `pending_rules[]`, `screen_versions{}` — these are the foundation; skill phases reference them.
2. **New skill phases** (AC-12 Phase 0, AC-14 Phase 1a, AC-18 Phase 5a) and **phase modifications** (Phase 1 flow ordering, Phase 2 diff-regen, Phase 4 expanded impact check, Phase 5 handoff YAML).
3. **New artifacts** (AC-18 script, AC-19 component library) that the skill calls but live outside skill.md.

Token budget constraint: skill.md is loaded into every agent call. Every addition must be as terse as the existing phases — inline parentheticals, no block explanations.

Execution order (per goal.md): AC-16 → AC-17 → AC-12 → AC-13 → AC-18 → AC-19 → AC-14 → AC-15

A single implementation agent can execute all changes sequentially; there are no blocking dependencies between the file-level edits after the metadata schema is established.

---

## Execution Plan

### Single Agent: Implementation Engineer

Execute in this exact order. Read each target file before editing it.

---

### Step 1 — AC-16: Flow-based screen ordering

**Files**: `skill.md` (Phase 1 modification + metadata schema), `SKETCHES_README.md` (flow_positions section), `requirements.md` (AC-16 entry + SEC-12 section entry)

#### 1a. skill.md — Phase 1 modifications

At the top of Phase 1 (before the spawn instruction), insert:

```
Before spawning Phase 1 agent, check whether the requirement references a user flow:
- If `requirements.md` has a `user_needs:` YAML entry linking to a flow, read `requirements_user_needs/user_flows/<flow>/flow.md` to extract step order.
- Pass flow step list to Phase 1 agent as `flow_context` (ordered list of step labels + step numbers).
- Phase 1 agent assigns each screen a `flow_positions` entry: `{screen_file, flow_id, step_number, requirement_id}`.
- Numeric filename prefixes (01_, 02_, …) reflect local sort only; canonical order comes from `flow_positions` in metadata.yaml.
- If no flow reference exists, proceed as today (numeric prefix = canonical order).
```

At the end of the metadata.yaml example block in Phase 1 (or in the Constraints section where metadata format is referenced), append the `flow_positions` field:

```yaml
flow_positions:           # canonical screen order from parent flow (omit if no flow reference)
  - screen_file: 01_home_night_mode.html
    flow_id: FLOW-007
    step_number: 3
    requirement_id: REQ-FUNC-014
```

#### 1b. SKETCHES_README.md — add `flow_positions` section

After the `## \`metadata.yaml\` Format` section, insert:

```markdown
### `flow_positions` Field (optional)

When a requirement is part of a user flow (`requirements_user_needs/user_flows/<flow>/flow.md`), each scribble screen records its canonical position:

```yaml
flow_positions:
  - screen_file: 01_home_night_mode.html
    flow_id: FLOW-007
    step_number: 3
    requirement_id: REQ-FUNC-014
```

- Numeric filename prefixes (01_, 02_) are local sort helpers only.
- Canonical screen order for composite indexes and cross-requirement navigation comes from `flow_positions`.
- Omit this field if the requirement has no parent flow.
```

#### 1c. requirements.md — add AC-16 and SEC-12

In `trackable_items.acceptance_criteria`, append:
```yaml
    - id: AC-16
      name: "Flow-based screen ordering"
      description: "metadata.yaml includes flow_positions[] array; Phase 1 reads parent user flow to determine canonical screen order before numbering; skill.md documents the algorithm"
```

In `trackable_items.sections`, append:
```yaml
    - id: SEC-12
      name: "Flow-Aware Scribble Generation"
      heading: "## Flow-Aware Scribble Generation"
```

**Success check**: skill.md Phase 1 mentions flow_context and flow_positions; SKETCHES_README.md has flow_positions section; requirements.md has AC-16 and SEC-12.

---

### Step 2 — AC-17: Cross-requirement iteration protocol

**Files**: `skill.md` (Phase 4 modification), `SKETCHES_README.md` (stale_since section), `requirements.md` (AC-17 entry)

#### 2a. skill.md — Phase 4 impact check extension

Replace the existing impact check step (step 3 in Phase 4):

**Current text**:
> **Impact check** (T1/T2 only): spawn Haiku agent to grep `requirements_tasks/` for already-implemented requirements with Presentation Layer scope

**New text**:
```
**Impact check** (T1/T2 only): spawn Haiku agent to check three categories:
(a) implemented requirements with Presentation Layer scope (grep `requirements_tasks/` for `status: done`)
(b) approved scribbles whose `metadata.yaml` `rules_applied` references the changed rule
(c) approved scribbles whose `metadata.yaml` `flutter_component_mapping` references a component whose `_scribble_components/<c_name>/metadata.yaml` lists the changed rule

For each stale approved scribble found, mark its `metadata.yaml`:
  `stale_since: <date>`
  `pending_rules: [<rule_id>]`
```

#### 2b. metadata.yaml schema — add stale fields

In the metadata.yaml format block (Phase 1 or wherever the canonical schema example lives in skill.md), append:

```yaml
stale_since: ""          # set when an approved scribble is invalidated by a rule change
pending_rules: []        # rule IDs that have changed since this scribble was approved
```

#### 2c. SKETCHES_README.md — add stale_since/pending_rules section

After the `## Version Lifecycle` section, insert:

```markdown
## Stale Scribble Lifecycle

An approved scribble becomes **stale** when a T1/T2 rule it depends on changes after approval.

| Field | Meaning |
|-------|---------|
| `stale_since` | Date the rule change was anchored |
| `pending_rules` | List of rule IDs that changed |

When a scribble is marked stale, the developer is notified by the Rule Update Protocol. The scribble remains `status: approved` (implementation may still reference it) but should be re-reviewed before the next feature iteration that touches those screens.

To clear stale status: re-run `ui-create-scribble` for the requirement; the new version resets `stale_since` and `pending_rules`.
```

#### 2d. requirements.md — add AC-17

```yaml
    - id: AC-17
      name: "Cross-requirement iteration protocol"
      description: "Phase 4 Haiku impact check covers (a) implemented requirements, (b) approved scribbles referencing the changed rule, (c) scribbles using shared components that reference the rule; metadata.yaml stale_since and pending_rules[] fields documented"
```

**Success check**: Phase 4 impact check covers 3 categories; stale_since + pending_rules appear in metadata schema; SKETCHES_README.md has stale section; requirements.md has AC-17.

---

### Step 3 — AC-12: Phase 0 multimodal input

**Files**: `skill.md` (new Phase 0 before Phase 1), `requirements.md` (AC-12 entry)

#### 3a. skill.md — insert Phase 0 before Phase 1

Insert this new section before `## Phase 1`:

```markdown
## Phase 0 — Optional Multimodal Seed

Before spawning Phase 1, check the task/requirement folder for input images:
- `inputs/sketch.{png,jpg,pdf}` — hand-drawn sketch or napkin drawing
- `inputs/reference.{png,jpg}` — screenshot from reference app or competitor

If any `inputs/` files exist: pass them as vision input to the Phase 1 agent alongside `requirements.md` and personas. The Phase 1 agent extracts layout structure from the images to seed the HTML scribble. (Vision capability uses Claude's multimodal input — no external tool needed.)

If no `inputs/` files exist: proceed directly to Phase 1 unchanged.
```

#### 3b. requirements.md — add AC-12

```yaml
    - id: AC-12
      name: "Optional multimodal input seed"
      description: "Phase 0 in skill.md checks inputs/ folder for sketch/reference images before Phase 1; passes them as vision context to Phase 1 agent if present; absent = Phase 1 unchanged"
```

**Success check**: skill.md has `## Phase 0` section with inputs/ logic; requirements.md has AC-12.

---

### Step 4 — AC-13: Flutter handoff YAML

**Files**: `skill.md` (Phase 5 extension), `ui-verify-flutter/skill.md` (Phase 1 modification), `SKETCHES_README.md` (flutter_handoff.yaml section), `requirements.md` (AC-13 entry)

#### 4a. skill.md — extend Phase 5

After step 2 in Phase 5 (`Update previous version's metadata.yaml: status: superseded`), insert step 3:

```
3. Emit `scribbles/v{n}/flutter_handoff.yaml` — spawn a brief agent to read all approved screen HTML files and output structured per-element mapping:

```yaml
screens:
  - screen: 01_home_night_mode
    elements:
      - html_selector: "header.app-bar"
        flutter_widget: AppBar
        material3_variant: "surface tint"
        persona_constraints:
          - "PERSONA-007: dark surface, no tint override"
        rules_applied:
          - t1_dark_mode
      - html_selector: "button.primary"
        flutter_widget: FilledButton
        material3_variant: "filled"
        persona_constraints: []
        rules_applied:
          - t1_touch_targets
```

(Agent reads component mapping block from each HTML file to extract selectors; reads metadata.yaml for personas and rules applied.)
```

#### 4b. ui-verify-flutter/skill.md — Phase 1 modification

In Phase 1 (Locate Approved Scribble), after step 2 (list screen files), add:

```
2b. Check for `flutter_handoff.yaml` in the approved version folder. If present, use it as the primary component mapping source (more precise than parsing HTML comments). If absent, fall back to parsing component mapping blocks in each HTML file.
```

#### 4c. SKETCHES_README.md — add flutter_handoff.yaml section

After the `## Component Mapping Block` section, insert:

```markdown
## `flutter_handoff.yaml` (generated after approval)

After scribble approval, `ui-create-scribble` emits `scribbles/v{n}/flutter_handoff.yaml` — a machine-readable per-element mapping used by `ui-verify-flutter` and implementation agents:

```yaml
screens:
  - screen: 01_home_night_mode
    elements:
      - html_selector: "header.app-bar"
        flutter_widget: AppBar
        material3_variant: "surface tint"
        persona_constraints:
          - "PERSONA-007: dark surface, no tint override"
        rules_applied:
          - t1_dark_mode
```

`ui-verify-flutter` reads this file first (if present) instead of parsing HTML comments.
```

#### 4d. requirements.md — add AC-13

```yaml
    - id: AC-13
      name: "Flutter handoff YAML"
      description: "Phase 5 emits scribbles/v{n}/flutter_handoff.yaml with per-element html_selector→flutter_widget→material3_variant→persona_constraints[]→rules_applied[]; ui-verify-flutter updated to consume it as primary source"
```

**Success check**: skill.md Phase 5 has handoff YAML step; ui-verify-flutter.md Phase 1 checks for flutter_handoff.yaml; SKETCHES_README.md has the format section; requirements.md has AC-13.

---

### Step 5 — AC-18: Flow-level composite index script

**Files**: `scripts/generate_flow_scribble_index.py` (new), `skill.md` (new Phase 5a), `requirements.md` (AC-18 entry + SEC-13 entry)

#### 5a. Create `scripts/generate_flow_scribble_index.py`

Full script:

```python
#!/usr/bin/env python3
"""
generate_flow_scribble_index.py

Generates requirements_user_needs/user_flows/<flow>/scribble_index.html
for each flow that has scribble screens registered in metadata.yaml flow_positions.

Usage:
  python scripts/generate_flow_scribble_index.py [--flow FLOW-ID] [--dry-run]

Output:
  requirements_user_needs/user_flows/<flow>/scribble_index.html
  (one per flow; overwrites if exists)

No build system required. Reads:
  - requirements_user_needs/user_flows/<flow>/flow.md (step order)
  - requirements_tasks/**/scribbles/*/metadata.yaml (flow_positions entries)
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent


def find_project_root() -> Path:
    return ROOT


def load_yaml_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file (between --- delimiters)."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def load_plain_yaml(path: Path) -> dict:
    """Load a plain YAML file."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def find_all_metadata_yaml(root: Path) -> list[Path]:
    """Find all scribbles/*/metadata.yaml files under requirements_tasks/."""
    pattern = str(root / "requirements_tasks" / "**" / "scribbles" / "*" / "metadata.yaml")
    return [Path(p) for p in glob.glob(pattern, recursive=True)]


def collect_flow_positions(root: Path) -> dict[str, list[dict]]:
    """
    Returns dict: flow_id -> list of {screen_file, step_number, requirement_id,
                                       scribble_version_path, scribble_status}
    Only includes entries from metadata.yaml files with status: approved.
    """
    result: dict[str, list[dict]] = {}
    for meta_path in find_all_metadata_yaml(root):
        data = load_plain_yaml(meta_path)
        if data.get("status") != "approved":
            continue
        positions = data.get("flow_positions", [])
        if not positions:
            continue
        scribble_version_dir = meta_path.parent
        for pos in positions:
            flow_id = pos.get("flow_id")
            if not flow_id:
                continue
            result.setdefault(flow_id, []).append({
                "screen_file": pos.get("screen_file", ""),
                "step_number": pos.get("step_number", 0),
                "requirement_id": pos.get("requirement_id", ""),
                "scribble_version_path": scribble_version_dir,
                "status": data.get("status", ""),
            })
    return result


def get_flow_dir(root: Path, flow_id: str) -> Path | None:
    """Find the directory for a flow by ID (searches user_flows/ by flow.md frontmatter)."""
    pattern = str(root / "requirements_user_needs" / "user_flows" / "**" / "flow.md")
    for p in glob.glob(pattern, recursive=True):
        fm = load_yaml_frontmatter(Path(p))
        if fm.get("id") == flow_id:
            return Path(p).parent
    return None


def get_flow_title(root: Path, flow_id: str) -> str:
    """Read flow title from flow.md frontmatter."""
    flow_dir = get_flow_dir(root, flow_id)
    if not flow_dir:
        return flow_id
    flow_md = flow_dir / "flow.md"
    if not flow_md.exists():
        return flow_id
    fm = load_yaml_frontmatter(flow_md)
    return fm.get("name", fm.get("title", flow_id))


def build_composite_html(flow_id: str, title: str, screens: list[dict]) -> str:
    """Build the scribble_index.html content for a flow."""
    sorted_screens = sorted(screens, key=lambda s: s["step_number"])

    iframe_rows = []
    nav_items = []
    for i, s in enumerate(sorted_screens):
        scribble_path = s["scribble_version_path"]
        screen_file = s["screen_file"]
        abs_screen = scribble_path / screen_file
        # Make path relative to user_flows/<flow>/ for iframe src
        try:
            rel = os.path.relpath(abs_screen, start=scribble_path.parent.parent.parent)
            # Actually, relative from user_flows/<flow_dir>/
            # We'll use absolute path from root for correctness in browser context
            src = "/" + str(abs_screen.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            src = str(abs_screen)

        step = s["step_number"]
        req = s["requirement_id"]
        anchor = f"step-{step}"
        nav_items.append(f'<li><a href="#{anchor}">Step {step} — {screen_file} ({req})</a></li>')
        iframe_rows.append(
            f'<section id="{anchor}" class="screen-frame">\n'
            f'  <h2>Step {step}: {screen_file}</h2>\n'
            f'  <p class="req-badge">{req}</p>\n'
            f'  <iframe src="{src}" width="390" height="844" loading="lazy" '
            f'title="Step {step}: {screen_file}"></iframe>\n'
            f'</section>'
        )

    nav_html = "\n".join(nav_items)
    frames_html = "\n\n".join(iframe_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Scribble Index — {title} ({flow_id})</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; padding: 16px; background: #f5f5f5; }}
    h1 {{ font-size: 1.25rem; margin-bottom: 8px; }}
    .subtitle {{ color: #666; font-size: 0.875rem; margin-bottom: 24px; }}
    nav ol {{ padding-left: 1.5rem; margin-bottom: 32px; }}
    nav a {{ color: #1565c0; text-decoration: none; }}
    nav a:hover {{ text-decoration: underline; }}
    .screen-frame {{ background: white; border: 1px solid #ddd; border-radius: 4px;
                     padding: 16px; margin-bottom: 24px; }}
    .screen-frame h2 {{ font-size: 1rem; margin: 0 0 4px; }}
    .req-badge {{ font-size: 0.75rem; color: #555; margin: 0 0 12px; }}
    iframe {{ border: 1px solid #ccc; border-radius: 2px; display: block; }}
  </style>
</head>
<body>
  <h1>Scribble Index — {title}</h1>
  <p class="subtitle">{flow_id} · Auto-generated by scripts/generate_flow_scribble_index.py · Only approved scribbles included</p>
  <nav>
    <ol>
{nav_html}
    </ol>
  </nav>

{frames_html}

</body>
</html>
"""


def generate_for_flow(root: Path, flow_id: str, screens: list[dict], dry_run: bool) -> None:
    flow_dir = get_flow_dir(root, flow_id)
    if flow_dir is None:
        print(f"  WARNING: Flow directory not found for {flow_id} — skipping", file=sys.stderr)
        return

    title = get_flow_title(root, flow_id)
    html = build_composite_html(flow_id, title, screens)
    out_path = flow_dir / "scribble_index.html"

    if dry_run:
        print(f"  [dry-run] Would write {out_path} ({len(html)} bytes, {len(screens)} screens)")
        return

    out_path.write_text(html, encoding="utf-8")
    print(f"  Written: {out_path} ({len(screens)} screens)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate flow scribble composite index HTML files.")
    parser.add_argument("--flow", metavar="FLOW-ID", help="Generate only for this flow ID")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written; do not write")
    args = parser.parse_args()

    root = find_project_root()
    all_positions = collect_flow_positions(root)

    if not all_positions:
        print("No flow_positions found in any approved scribble metadata.yaml. Nothing to generate.")
        return

    if args.flow:
        if args.flow not in all_positions:
            print(f"No approved scribbles with flow_positions for {args.flow}.")
            sys.exit(1)
        items = {args.flow: all_positions[args.flow]}
    else:
        items = all_positions

    print(f"Generating scribble indexes for {len(items)} flow(s)...")
    for flow_id, screens in sorted(items.items()):
        print(f"  {flow_id}: {len(screens)} screen(s)")
        generate_for_flow(root, flow_id, screens, dry_run=args.dry_run)

    print("Done.")


if __name__ == "__main__":
    main()
```

#### 5b. skill.md — add Phase 5a after Phase 5

Insert after Phase 5:

```markdown
## Phase 5a — Flow Composite Index

After emitting `flutter_handoff.yaml` (Phase 5 step 3), if the requirement references a user flow:

```
python scripts/generate_flow_scribble_index.py --flow <flow_id>
```

(Reads all approved scribble `flow_positions` for this flow; writes `requirements_user_needs/user_flows/<flow>/scribble_index.html`.)

Skip Phase 5a if the requirement has no parent flow.
```

#### 5c. requirements.md — add AC-18 and SEC-13

```yaml
    - id: AC-18
      name: "Flow-level composite index"
      description: "scripts/generate_flow_scribble_index.py generates requirements_user_needs/user_flows/<flow>/scribble_index.html by iframing approved scribble screens in flow-step order; Phase 5a in skill.md triggers it after approval when a flow reference exists"
```

```yaml
    - id: SEC-13
      name: "Flow-Level Composite Index"
      heading: "## Flow-Level Composite Index"
```

**Success check**: script file exists and is syntactically valid; skill.md has `## Phase 5a`; requirements.md has AC-18 and SEC-13.

---

### Step 6 — AC-19: Component library

**Files**: Create `requirements_tasks/_scribble_components/` folder structure, `SKETCHES_README.md` (component library section), `requirements.md` (AC-19 entry + SEC-14 entry)

#### 6a. Create `requirements_tasks/_scribble_components/components.js`

```javascript
/**
 * Scribble Component Loader — wireframe-quality only, no production use.
 * Resolves <div data-component="c_xxx"> by fetching /_scribble_components/c_xxx/template.html
 * at page load. Falls back gracefully (empty div) if JS disabled or fetch fails.
 *
 * Usage in scribble HTML: <div data-component="c_navigation_bar"></div>
 * Base path resolved relative to this script's location.
 */
(function () {
  const BASE = (function () {
    const scripts = document.querySelectorAll('script[src]');
    for (const s of scripts) {
      if (s.src.includes('components.js')) {
        return s.src.replace(/components\.js.*$/, '');
      }
    }
    return '/_scribble_components/';
  })();

  function resolveComponent(el) {
    const name = el.dataset.component;
    if (!name) return;
    fetch(BASE + name + '/template.html')
      .then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); })
      .then(function (html) {
        const tpl = document.createElement('template');
        tpl.innerHTML = html;
        const clone = tpl.content.cloneNode(true);
        el.replaceWith(clone);
      })
      .catch(function () {
        el.setAttribute('data-component-error', name);
        el.style.cssText = 'border:1px dashed #bbb;padding:8px;color:#999;font-size:12px;';
        el.textContent = '[Component: ' + name + ']';
      });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-component]').forEach(resolveComponent);
  });
})();
```

#### 6b. Create `requirements_tasks/_scribble_components/c_navigation_bar/template.html`

```html
<!-- c_navigation_bar: NavigationBar (M3) — T1: touch targets ≥ 48dp -->
<nav class="scribble-nav-bar" style="display:flex;background:#e8e8e8;border-top:1px solid #ccc;height:80px;align-items:center;justify-content:space-around;padding:0 8px;" aria-label="Bottom navigation">
  <div class="nav-item" style="display:flex;flex-direction:column;align-items:center;min-width:48px;min-height:48px;justify-content:center;gap:4px;cursor:pointer;">
    <div style="width:24px;height:24px;background:#aaa;border-radius:12px;" aria-hidden="true"></div>
    <span style="font-size:11px;color:#555;">[Nav 1]</span>
  </div>
  <div class="nav-item" style="display:flex;flex-direction:column;align-items:center;min-width:48px;min-height:48px;justify-content:center;gap:4px;cursor:pointer;">
    <div style="width:24px;height:24px;background:#aaa;border-radius:12px;" aria-hidden="true"></div>
    <span style="font-size:11px;color:#555;">[Nav 2]</span>
  </div>
  <div class="nav-item" style="display:flex;flex-direction:column;align-items:center;min-width:48px;min-height:48px;justify-content:center;gap:4px;cursor:pointer;">
    <div style="width:24px;height:24px;background:#aaa;border-radius:12px;" aria-hidden="true"></div>
    <span style="font-size:11px;color:#555;">[Nav 3]</span>
  </div>
</nav>
<!-- Flutter: NavigationBar (M3) with NavigationDestination items -->
```

#### 6c. Create `requirements_tasks/_scribble_components/c_navigation_bar/metadata.yaml`

```yaml
component: c_navigation_bar
flutter_widget: NavigationBar
material3_variant: "M3 NavigationBar"
tier: T1
rules_applied:
  - T1: Touch targets ≥ 48dp (doc/presentation/design/t1_touch_targets.md)
last_updated: 2026-04-19
description: "Bottom navigation bar with 3 destinations. Wireframe-quality placeholder."
```

#### 6d. Create `requirements_tasks/_scribble_components/c_app_bar/template.html`

```html
<!-- c_app_bar: AppBar (M3 surface tint) — T1: touch targets ≥ 48dp -->
<header class="scribble-app-bar" style="display:flex;background:#e0e0e0;height:64px;align-items:center;padding:0 16px;gap:8px;" role="banner">
  <button style="min-width:48px;min-height:48px;background:none;border:1px dashed #aaa;border-radius:4px;cursor:pointer;" aria-label="Back">[Back]</button>
  <span style="flex:1;font-size:14px;font-weight:600;color:#333;">[Screen Title]</span>
  <button style="min-width:48px;min-height:48px;background:none;border:1px dashed #aaa;border-radius:4px;cursor:pointer;" aria-label="Action">[Action]</button>
</header>
<!-- Flutter: AppBar with Material3 surface tint; leading/actions as IconButton -->
```

#### 6e. Create `requirements_tasks/_scribble_components/c_app_bar/metadata.yaml`

```yaml
component: c_app_bar
flutter_widget: AppBar
material3_variant: "surface tint"
tier: T1
rules_applied:
  - T1: Touch targets ≥ 48dp (doc/presentation/design/t1_touch_targets.md)
last_updated: 2026-04-19
description: "Top app bar with leading back button, title, and trailing action. Wireframe-quality."
```

#### 6f. Create `requirements_tasks/_scribble_components/c_filled_button/template.html`

```html
<!-- c_filled_button: FilledButton (M3) — T1: touch targets ≥ 48dp -->
<button class="scribble-filled-btn" style="min-height:48px;min-width:64px;padding:0 24px;background:#9e9e9e;border:none;border-radius:12px;font-size:14px;font-weight:600;color:#fff;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;">[Label]</button>
<!-- Flutter: FilledButton (M3) -->
```

#### 6g. Create `requirements_tasks/_scribble_components/c_filled_button/metadata.yaml`

```yaml
component: c_filled_button
flutter_widget: FilledButton
material3_variant: "filled"
tier: T1
rules_applied:
  - T1: Touch targets ≥ 48dp (doc/presentation/design/t1_touch_targets.md)
last_updated: 2026-04-19
description: "Primary filled button. Replace [Label] with action text. Wireframe-quality."
```

#### 6h. Create `requirements_tasks/_scribble_components/c_mood_entry_card/template.html`

```html
<!-- c_mood_entry_card: Card (M3 surfaceVariant) — mood entry pattern -->
<!-- PERSONA-002 (Max): blank-field paralysis → structured prompt, no empty free-text -->
<div class="scribble-mood-card" style="background:#f0f0f0;border:1px solid #ccc;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:12px;" role="region" aria-label="Mood entry">
  <div style="font-size:13px;font-weight:600;color:#555;">[Structured prompt: How are you feeling?]</div>
  <!-- Slider replaces free-text (Max: reduces blank-field paralysis) -->
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="font-size:11px;color:#888;">Low</span>
    <div style="flex:1;height:8px;background:#ccc;border-radius:4px;position:relative;">
      <div style="width:60%;height:100%;background:#888;border-radius:4px;"></div>
      <div style="position:absolute;top:-8px;left:60%;width:24px;height:24px;background:#666;border-radius:12px;transform:translateX(-50%);"></div>
    </div>
    <span style="font-size:11px;color:#888;">High</span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:8px;">
    <span style="padding:6px 12px;background:#ddd;border-radius:16px;font-size:12px;">[Tag 1]</span>
    <span style="padding:6px 12px;background:#ddd;border-radius:16px;font-size:12px;">[Tag 2]</span>
    <span style="padding:6px 12px;border:1px dashed #aaa;border-radius:16px;font-size:12px;">+ Add tag</span>
  </div>
</div>
<!-- Flutter: Card (surfaceVariant) > Column > [prompt text, Slider, Wrap(FilterChip)] -->
```

#### 6i. Create `requirements_tasks/_scribble_components/c_mood_entry_card/metadata.yaml`

```yaml
component: c_mood_entry_card
flutter_widget: Card
material3_variant: "surfaceVariant"
tier: T2
rules_applied:
  - T1: Touch targets ≥ 48dp (doc/presentation/design/t1_touch_targets.md)
  - T2: Mood input uses slider (not free-text) — reduces blank-field paralysis (PERSONA-002)
last_updated: 2026-04-19
description: "Mood entry card with structured prompt, slider, and tag chips. Wireframe-quality."
personas_applied:
  - PERSONA-002 (Max): blank-field paralysis → structured prompt + slider, no empty free-text fields
```

#### 6j. SKETCHES_README.md — add component library section

After the `## After Implementation` section, insert:

```markdown
## Component Library (`_scribble_components/`)

Reusable wireframe-quality HTML5 template fragments live in `requirements_tasks/_scribble_components/`.

### Using a component in a scribble

```html
<!-- At the top of your screen HTML, load the component loader: -->
<script src="/requirements_tasks/_scribble_components/components.js"></script>

<!-- Then use anywhere in the body: -->
<div data-component="c_navigation_bar"></div>
<div data-component="c_app_bar"></div>
<div data-component="c_filled_button"></div>
<div data-component="c_mood_entry_card"></div>
```

If JavaScript is disabled, the div renders as an empty placeholder (JS-free fallback).

### Seed components

| Component | Flutter widget | Tier |
|-----------|---------------|------|
| `c_navigation_bar` | NavigationBar (M3) | T1 |
| `c_app_bar` | AppBar (M3 surface tint) | T1 |
| `c_filled_button` | FilledButton (M3) | T1 |
| `c_mood_entry_card` | Card (surfaceVariant) | T2 |

### Maintenance protocol

- When a T2/T1 rule is approved that affects an existing component, update the component's `template.html` and bump `last_updated` in `metadata.yaml`.
- When a new T2/T1 rule introduces a new reusable pattern, create a new `c_<name>/` folder following the same structure.
- Components are wireframe-quality only — no brand colors, no production styling.
- Do NOT add JavaScript logic to template.html fragments (they are passive HTML only).
```

#### 6k. requirements.md — add AC-19 and SEC-14

```yaml
    - id: AC-19
      name: "Component library"
      description: "requirements_tasks/_scribble_components/ exists with components.js and ≥4 seed components (c_navigation_bar, c_app_bar, c_filled_button, c_mood_entry_card); maintenance protocol documented in SKETCHES_README.md"
```

```yaml
    - id: SEC-14
      name: "Component Library"
      heading: "## Component Library"
```

**Success check**: `_scribble_components/components.js` exists; 4 seed component folders each with `template.html` and `metadata.yaml`; SKETCHES_README.md has component library section; requirements.md has AC-19 and SEC-14.

---

### Step 7 — AC-14: Optional draft generators

**Files**: `skill.md` (Phase 1 modification), `requirements.md` (AC-14 entry)

#### 7a. skill.md — Phase 1 modification (draft_generator check)

At the start of Phase 1 (before the spawn instruction), insert:

```
**Optional draft generator**: Check `draft_generator` field in goal.md YAML.
- `none` (default) — proceed as today (generate HTML from scratch).
- `claude_design` — invoke Claude Design with requirements summary to produce a first-draft HTML wireframe; then spawn a second agent to annotate it with personas, T1/T2 rules, and component mapping block. Output is still a scribble.
- `stitch` — if Stitch MCP is configured, invoke it; convert Flutter widget output to HTML scribble format; annotate with personas and rules. (Note: Stitch MCP setup is a separate task; document as unsupported until configured.)

In all cases, output is `scribbles/v{n}/` in standard scribble format (index.html, per-screen HTML files, metadata.yaml, feedback.md).
```

#### 7b. requirements.md — add AC-14

```yaml
    - id: AC-14
      name: "Optional draft generators"
      description: "draft_generator field in goal.md YAML (claude_design | stitch | none); Phase 1 conditionally delegates to external tool for first-draft HTML; output is always standard scribble format; default none = current behavior"
```

**Success check**: skill.md Phase 1 checks `draft_generator`; `claude_design` and `stitch` paths documented; `none` = unchanged behavior; requirements.md has AC-14.

---

### Step 8 — AC-15: Diff-based regeneration

**Files**: `skill.md` (Phase 2 + Phase 4 modifications + metadata schema), `SKETCHES_README.md` (screen_versions section), `requirements.md` (AC-15 entry)

#### 8a. skill.md — Phase 4 modification (feedback classification)

In Phase 4, after step 1 (classify: missing rule | requirement gap | existing rule not applied), add a classification sub-step:

```
**Screen scope classification**: Determine whether the feedback affects:
- **Specific screen(s)**: "the dark mode contrast on screen 03" → regenerate only affected files; copy unaffected screens verbatim from previous version; update `screen_versions` map for changed screens only.
- **All screens** (structural change, new T1 rule, index change): full regeneration as today.
```

#### 8b. skill.md — Phase 2 modification (auto-review diff awareness)

In Phase 2, after the existing "checks" list, add:

```
If the triggering feedback classified specific screens (screen scope from Phase 4): regenerate only those screens; copy the rest from v{n}. Update `screen_versions` for regenerated files only.
```

#### 8c. metadata.yaml schema — add screen_versions

In the metadata.yaml format block, append:

```yaml
screen_versions:          # per-screen version tracking (incremented on each targeted regen)
  01_home_night_mode.html: 1
  02_quick_entry.html: 2  # regenerated once for targeted feedback
```

#### 8d. SKETCHES_README.md — add screen_versions section

After the `## Version Lifecycle` section, insert (or extend if stale section already added in step 2):

```markdown
### `screen_versions` Map (optional)

When diff-based regeneration is active, each screen file tracks its own version number in `metadata.yaml`:

```yaml
screen_versions:
  01_home_night_mode.html: 1
  02_quick_entry.html: 2
```

Screens not mentioned in user feedback are copied verbatim from the previous version (same content, unchanged `screen_versions` count). Only feedback-affected screens are regenerated and incremented.
```

#### 8e. requirements.md — add AC-15

```yaml
    - id: AC-15
      name: "Diff-based regeneration"
      description: "Phase 4 feedback classification includes 'affects screen X' vs 'affects all'; metadata.yaml screen_versions map tracks per-screen version numbers; unaffected screens copied verbatim on targeted regeneration"
```

**Success check**: skill.md Phase 4 has screen scope classification; Phase 2 references diff-based path; metadata.yaml schema shows `screen_versions`; SKETCHES_README.md documents it; requirements.md has AC-15.

---

### Step 9 — Final: verify all ACs met

Run through the verification checklist below. No additional file changes in this step — just read and confirm.

---

## Metadata.yaml Canonical Schema (complete, after all changes)

For reference — the full metadata.yaml format the skill should document:

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
    reason: "Feels more natural for continuous mood assessment"
    applies_to: [01_mood_entry.html]
# --- new fields (AC-16, AC-17, AC-15) ---
flow_positions:             # canonical screen order from parent flow (omit if no flow)
  - screen_file: 01_home_night_mode.html
    flow_id: FLOW-007
    step_number: 3
    requirement_id: REQ-FUNC-014
screen_versions:            # per-screen regen counters (omit if no targeted regen yet)
  01_home_night_mode.html: 1
  02_quick_entry.html: 1
stale_since: ""             # date if rule change invalidates this scribble post-approval
pending_rules: []           # rule IDs changed since approval
```

---

## Quality Criteria (Verification Checklist)

- [ ] **AC-12**: `## Phase 0` in skill.md; inputs/ folder check present; Phase 1 mentions vision context
- [ ] **AC-13**: Phase 5 step 3 emits `flutter_handoff.yaml`; ui-verify-flutter Phase 1 step 2b checks for it; SKETCHES_README.md has format example
- [ ] **AC-14**: Phase 1 checks `draft_generator`; `claude_design`, `stitch`, `none` paths documented; none = current behavior
- [ ] **AC-15**: Phase 4 has screen scope classification step; Phase 2 references diff path; metadata.yaml shows `screen_versions`; SKETCHES_README.md documents it
- [ ] **AC-16**: Phase 1 reads parent flow before numbering; metadata.yaml shows `flow_positions`; algorithm documented; SKETCHES_README.md has flow_positions section
- [ ] **AC-17**: Phase 4 impact check has 3 categories (a/b/c); metadata.yaml shows `stale_since` + `pending_rules`; SKETCHES_README.md has stale lifecycle section
- [ ] **AC-18**: `scripts/generate_flow_scribble_index.py` exists and is syntactically valid; `## Phase 5a` in skill.md; requirements.md has AC-18 + SEC-13
- [ ] **AC-19**: `requirements_tasks/_scribble_components/components.js` exists; 4 seed folders each with `template.html` + `metadata.yaml`; SKETCHES_README.md has component library section; requirements.md has AC-19 + SEC-14
- [ ] **REQ-PROC-032**: `trackable_items.acceptance_criteria` has AC-12 through AC-19; `trackable_items.sections` has SEC-12 through SEC-14
- [ ] **SKETCHES_README.md**: 4 new sections present (flow_positions, flutter_handoff.yaml, stale lifecycle, component library); existing content unchanged
- [ ] **No regressions**: Phase 1–5 behavior unchanged for `draft_generator: none` and no `inputs/` folder; existing phases preserved

---

## Risks

- **Token budget**: skill.md additions must be terse. Each new phase/modification: write 3-8 lines max. Use inline parentheticals. Check total skill.md line count after edits — target <200 lines.
- **metadata.yaml schema drift**: The schema is documented in two places (skill.md example block + SKETCHES_README.md). Keep them in sync — update both when adding fields.
- **Script path assumptions**: `generate_flow_scribble_index.py` uses `Path(__file__).parent.parent` to find root. Verify this resolves correctly from `scripts/` folder.
- **components.js relative path**: Uses `script[src]` inspection to find BASE path. Works for file:// served locally. If scribbles are served from a non-root path, the BASE resolution may need adjustment. Acceptable for wireframe-only use.
- **AC-14 stitch path**: Document as "requires Stitch MCP setup (separate task)" to avoid implying it works today.

---

## Execution: Single Agent

All changes are sequential file edits with no blocking dependencies after step 1 establishes the metadata schema. A single implementation agent executes steps 1–8 in order, then runs the verification checklist.

Agent reads each file before editing. Uses Edit tool for existing files, Write tool for new files.
