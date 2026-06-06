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

# tier: C  # one-shot CLI user-needs tool; no in-tree Python imports

import argparse
import glob
import re
import sys
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

ROOT = Path(__file__).parent.parent.parent


def find_project_root() -> Path:
    return ROOT


def load_yaml_frontmatter(path: Path) -> dict[Any, Any]:
    """Extract YAML frontmatter from a markdown file (between --- delimiters)."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def load_plain_yaml(path: Path) -> dict[Any, Any]:
    """Load a plain YAML file."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def find_all_metadata_yaml(root: Path) -> list[Path]:
    """Find all scribbles/*/metadata.yaml files under requirements_tasks/."""
    pattern = str(root / "requirements_tasks" / "**" / "scribbles" / "*" / "metadata.yaml")
    return [Path(p) for p in glob.glob(pattern, recursive=True)]


def collect_flow_positions(root: Path) -> dict[str, list[dict[Any, Any]]]:
    """
    Returns dict: flow_id -> list of {screen_file, step_number, requirement_id,
                                       scribble_version_path, scribble_status}
    Only includes entries from metadata.yaml files with status: approved.
    """
    result: dict[str, list[dict[Any, Any]]] = {}
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
    return cast("str", fm.get("name", fm.get("title", flow_id)))


def build_composite_html(flow_id: str, title: str, screens: list[dict[Any, Any]]) -> str:
    """Build the scribble_index.html content for a flow."""
    sorted_screens = sorted(screens, key=lambda s: s["step_number"])

    iframe_rows = []
    nav_items = []
    for _i, s in enumerate(sorted_screens):
        scribble_path = s["scribble_version_path"]
        screen_file = s["screen_file"]
        abs_screen = scribble_path / screen_file
        # Make path relative to user_flows/<flow>/ for iframe src
        try:
            # Use absolute path from root for correctness in browser context
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


def generate_for_flow(root: Path, flow_id: str, screens: list[dict[Any, Any]], dry_run: bool) -> None:
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
