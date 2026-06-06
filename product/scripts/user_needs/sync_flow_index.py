#!/usr/bin/env python3
"""
Sync FLOW_INDEX.md Status lines from authoritative flow.md YAML frontmatter.

Each flow.md's review_status is the source of truth. This script reads every
flow.md, extracts flow_id + review_status, and updates the matching
- **Status**: line under the ### FLOW-NNN: heading in FLOW_INDEX.md.

The parenthetical annotation (anything after the status keyword) is preserved
so that human context notes are not lost — only the leading keyword is updated.

Usage:
    python scripts/sync_flow_index.py            # update in place
    python scripts/sync_flow_index.py --dry-run  # show changes, no writes

Exit codes:
    0 — success (even if nothing changed)
    1 — error (file not found, YAML parse failure, etc.)

Output:
    Prints one '<FLOW-ID> <OLD> -> <NEW>' line per change to stdout. --dry-run reports planned changes without writing.
"""

# tier: C  # one-shot CLI user-needs tool; no in-tree Python imports

import re
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

FLOW_INDEX_PATH = Path("requirements_user_needs/user_flows/FLOW_INDEX.md")
FLOWS_ROOT = Path("requirements_user_needs/user_flows")

STATUS_DISPLAY = {
    "draft": "Draft",
    "in_review": "In Review",
    "pending_alignment": "Pending Alignment",
    "aligned": "Aligned",
    "approved": "Approved",
    "deprecated": "Deprecated",
}


def extract_flow_statuses() -> dict[str, str]:
    """Return {flow_id: review_status} for every flow.md found under FLOWS_ROOT."""
    statuses: dict[str, str] = {}
    for flow_md in FLOWS_ROOT.rglob("flow.md"):
        content = flow_md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not m:
            print(f"  [warn] no YAML frontmatter in {flow_md}", file=sys.stderr)
            continue
        try:
            data = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            print(f"  [warn] YAML parse error in {flow_md}: {e}", file=sys.stderr)
            continue
        flow_id = data.get("flow_id")
        review_status = data.get("review_status")
        if flow_id and review_status:
            statuses[flow_id] = review_status
        else:
            print(f"  [warn] missing flow_id or review_status in {flow_md}", file=sys.stderr)
    return statuses


def sync(dry_run: bool = False) -> int:
    """
    Update Status lines in FLOW_INDEX.md.
    Returns the number of lines changed (0 = already in sync).
    """
    if not FLOW_INDEX_PATH.exists():
        print(f"ERROR: {FLOW_INDEX_PATH} not found", file=sys.stderr)
        sys.exit(1)

    statuses = extract_flow_statuses()
    if not statuses:
        print("No flow.md files found — nothing to sync.", file=sys.stderr)
        sys.exit(1)

    lines = FLOW_INDEX_PATH.read_text(encoding="utf-8").split("\n")
    current_flow_id: str | None = None
    changed = 0

    for i, line in enumerate(lines):
        # Any heading resets the tracker; only FLOW-NNN headings set it
        if re.match(r"^#{1,6} ", line):
            m = re.match(r"^### (FLOW-\d+):", line)
            current_flow_id = m.group(1) if m else None
            continue

        # Update the Status line for the current flow
        if current_flow_id and re.match(r"^- \*\*Status\*\*:", line):
            if current_flow_id not in statuses:
                continue  # flow in index but no flow.md found — leave as-is

            display = STATUS_DISPLAY.get(statuses[current_flow_id], statuses[current_flow_id])

            # Preserve any parenthetical annotation after the status keyword
            # e.g. "In Review (was Approved; ...)" → keep the "(was Approved; ...)" part
            annotation_match = re.match(r"^- \*\*Status\*\*:\s*\S.*?\s*(\(.*)", line)
            annotation = f" {annotation_match.group(1)}" if annotation_match else ""

            new_line = f"- **Status**: {display}{annotation}"

            if lines[i] != new_line:
                print(f"  {current_flow_id}: {lines[i].strip()!r}")
                print(f"           → {new_line.strip()!r}")
                if not dry_run:
                    lines[i] = new_line
                changed += 1

    if not dry_run and changed > 0:
        FLOW_INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
        print(f"\nSynced {changed} status line(s) in FLOW_INDEX.md")
    elif dry_run:
        print(f"\n[dry-run] Would update {changed} status line(s)")
    else:
        print("FLOW_INDEX.md already in sync — no changes needed.")

    return changed


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sync(dry_run=dry_run)
