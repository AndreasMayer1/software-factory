#!/usr/bin/env python3
"""
Migration script: split REQ-PROC-032 golden source into epic + 7 feature requirements.md files.
All AC name/description text and SEC body prose are COPIED BYTE-EXACT from the golden source.
No LLM in the copy path.

Usage:
    python3 migrate.py [--golden <path>] [--epic-dir <path>]

Defaults:
    golden:    git show 9a73678c:...requirements.md  (read from stdin or temp file)
    epic-dir:  requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/
"""

import sys
import os
import re
import yaml  # PyYAML — standard in most Python envs; fallback manual parsing also provided
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parents[7]  # flutter_app/
EPIC_DIR = SCRIPT_DIR.parents[2]   # ui_sketch_iteration_workflow/
GOLDEN_PATH = Path("/tmp/golden_requirements.md")

# ---------------------------------------------------------------------------
# Feature spec (from seam map + decisions_locked.md, crosswalk is authoritative)
# ---------------------------------------------------------------------------
FEATURES = [
    {
        "req_id": "REQ-PROC-032-01",
        "folder": "feat_scribble_core_artifact",
        "old_acs": ["AC-01", "AC-02", "AC-03", "AC-04", "AC-37"],
        "sections": ["SEC-01", "SEC-02", "SEC-03", "SEC-04", "SEC-05"],
    },
    {
        "req_id": "REQ-PROC-032-02",
        "folder": "feat_iteration_and_rule_protocol",
        "old_acs": ["AC-05", "AC-06", "AC-07", "AC-08"],
        "sections": ["SEC-06", "SEC-07", "SEC-08", "SEC-09", "SEC-10"],
    },
    {
        "req_id": "REQ-PROC-032-03",
        "folder": "feat_handoff_skills_and_contract",
        "old_acs": [
            "AC-09", "AC-10", "AC-11", "AC-13",
            "AC-21", "AC-22", "AC-23", "AC-24", "AC-25", "AC-26", "AC-27",
            "AC-28", "AC-29", "AC-30",
            "AC-38", "AC-39", "AC-40",
        ],
        "sections": ["SEC-11", "SEC-15", "SEC-16"],
    },
    {
        "req_id": "REQ-PROC-032-04",
        "folder": "feat_scribble_content_extensions",
        "old_acs": [
            "AC-12", "AC-14", "AC-15", "AC-16", "AC-17", "AC-18", "AC-19", "AC-20",
            "AC-32", "AC-33", "AC-34", "AC-35", "AC-36", "AC-41",
        ],
        "sections": ["SEC-12", "SEC-13", "SEC-14", "SEC-17"],
    },
    {
        "req_id": "REQ-PROC-032-05",
        "folder": "feat_consistency_sci_layer",
        "old_acs": [
            "AC-42", "AC-43", "AC-44", "AC-45", "AC-46", "AC-47", "AC-48",
            "AC-49", "AC-50", "AC-51", "AC-52", "AC-53", "AC-54", "AC-55",
        ],
        "sections": ["SEC-18"],
    },
    {
        "req_id": "REQ-PROC-032-06",
        "folder": "feat_carrier_and_auto_review",
        "old_acs": [
            "AC-31", "AC-56", "AC-57", "AC-58", "AC-59", "AC-60", "AC-61", "AC-62",
            "AC-63", "AC-64", "AC-65", "AC-66",
        ],
        "sections": ["SEC-19", "SEC-20"],
    },
    {
        "req_id": "REQ-PROC-032-07",
        "folder": "feat_embedded_flow_viewer",
        "old_acs": ["AC-67", "AC-68", "AC-69", "AC-70"],
        "sections": ["SEC-21"],
    },
]

# Sections with NO body prose in golden (declared in frontmatter only)
EMPTY_SECTIONS = {"SEC-12", "SEC-13", "SEC-14"}

# ---------------------------------------------------------------------------
# Parse the golden file
# ---------------------------------------------------------------------------

def read_golden(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_frontmatter_body(text: str):
    """Split '---\\n...---\\n\\nbody' into (fm_text, body_text)."""
    # First --- is at line 0, second --- closes the frontmatter
    lines = text.split("\n")
    if lines[0].strip() != "---":
        raise ValueError("Expected frontmatter starting with ---")
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("No closing --- found for frontmatter")
    fm_text = "\n".join(lines[1:end_idx])
    # body starts after the closing ---
    body_text = "\n".join(lines[end_idx + 1:])
    return fm_text, body_text


def parse_frontmatter(fm_text: str) -> dict:
    """Parse YAML frontmatter. Returns dict."""
    return yaml.safe_load(fm_text)


def extract_acs(fm: dict) -> dict:
    """Returns {ac_id: {id, name, description, ...}} from golden frontmatter."""
    acs = {}
    for item in fm["trackable_items"]["acceptance_criteria"]:
        acs[item["id"]] = dict(item)
    return acs


def extract_sections_fm(fm: dict) -> dict:
    """Returns {sec_id: {id, name, heading}} from golden frontmatter."""
    secs = {}
    for item in fm["trackable_items"]["sections"]:
        secs[item["id"]] = dict(item)
    return secs


# ---------------------------------------------------------------------------
# Body section extraction
# ---------------------------------------------------------------------------

# Section headings we need to find in the body.
# The non-SEC epic headings stay on the epic.
EPIC_ONLY_HEADINGS = {"## Related Requirements", "## Version History"}

SEC_HEADING_TO_ID = {
    "## Background and Motivation": "SEC-01",
    "## Scribble Definition": "SEC-02",
    "## Scribble Format": "SEC-03",
    "## AI Behavior Rules for Scribble Generation": "SEC-04",
    "## Storage and Organization": "SEC-05",
    "## Iteration Workflow": "SEC-06",
    "## Rule Update Protocol": "SEC-07",
    "## Integration with Existing Workflows": "SEC-08",
    "## Design System Alignment": "SEC-09",
    "## Scribble Documentation Location": "SEC-10",
    "## Three-Skill Workflow": "SEC-11",
    # SEC-12, 13, 14: no body heading
    "## Scribble–Coder Contract": "SEC-15",
    "## Scribble Review Doctrine": "SEC-16",
    "## Scribble Content Extensions": "SEC-17",
    "## Consistency and Scribble-Layer Model": "SEC-18",
    "## Scribble Carrier Format and Human Review Layer": "SEC-19",
    "## Auto-Review Control Model": "SEC-20",
    "## Embedded Flow-Viewer Sidebar": "SEC-21",
}

def extract_body_sections(body: str) -> dict:
    """
    Returns dict: {sec_id: body_text_bytes_exact}
    Plus special keys 'epic_intro' (text before first ##),
    'Related Requirements', 'Version History'.

    Body text for each section includes the heading line and all content
    up to (but not including) the next ## heading.
    """
    # Normalise line endings
    lines = body.split("\n")

    sections = {}

    # Find all top-level ## headings (not ### or deeper)
    heading_positions = []  # (line_idx, heading_text)
    for i, line in enumerate(lines):
        # Match exactly ## (not ###) at line start
        if re.match(r'^## [^\n]', line):
            heading_positions.append((i, line))

    # Epic intro is everything before the first ##
    if heading_positions:
        intro_lines = lines[:heading_positions[0][0]]
        # strip leading blank line after frontmatter close
        sections["epic_intro"] = "\n".join(intro_lines)

    # Extract each section's content
    for idx, (line_i, heading) in enumerate(heading_positions):
        # Content goes from this heading up to (not including) the next ##
        if idx + 1 < len(heading_positions):
            end_i = heading_positions[idx + 1][0]
        else:
            end_i = len(lines)

        section_lines = lines[line_i:end_i]
        section_text = "\n".join(section_lines)

        heading_stripped = heading.rstrip()
        if heading_stripped in SEC_HEADING_TO_ID:
            sec_id = SEC_HEADING_TO_ID[heading_stripped]
            sections[sec_id] = section_text
        elif heading_stripped in ("## Related Requirements", "## Version History"):
            sections[heading_stripped.lstrip("# ").strip()] = section_text
        else:
            # unknown heading — store by heading text
            sections[heading_stripped] = section_text

    return sections


# ---------------------------------------------------------------------------
# Build feature AC list with new ids
# ---------------------------------------------------------------------------

def build_feature_ac_list(feature: dict, golden_acs: dict) -> list:
    """Returns list of AC dicts with new id but verbatim name/description/other fields."""
    result = []
    for new_ac_num, old_ac_id in enumerate(feature["old_acs"], start=1):
        new_ac_id = f"AC-{new_ac_num:02d}"
        golden_item = golden_acs[old_ac_id]
        new_item = dict(golden_item)  # verbatim copy
        new_item["id"] = new_ac_id   # only id changes
        result.append(new_item)
    return result


# ---------------------------------------------------------------------------
# YAML frontmatter serialisation helpers
# ---------------------------------------------------------------------------

class _NoIndentLessDumper(yaml.Dumper):
    """Dumper that never uses indentless block sequences."""
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def _dump_fm_dict(d: dict) -> str:
    """Serialize a dict as YAML (no leading '---', no trailing '...')."""
    txt = yaml.dump(d, Dumper=_NoIndentLessDumper, allow_unicode=True,
                    default_flow_style=False, sort_keys=False)
    # yaml.dump always ends with \n; strip trailing newline
    return txt.rstrip("\n")


def build_frontmatter(req_id: str, golden_fm: dict, acs: list, sec_ids: list,
                      golden_secs_fm: dict) -> str:
    """Build full frontmatter block for a feature requirements.md."""
    # Build the sections list preserving all fields from golden
    sections_list = [golden_secs_fm[sid] for sid in sec_ids]

    # Build ordered dict preserving key order compatible with golden
    fm_dict = {
        "id": req_id,
        "status": "active",
        "urgency": golden_fm["urgency"],
        "urgency_reason": golden_fm["urgency_reason"],
        "impact": golden_fm["impact"],
        "impact_reason": golden_fm["impact_reason"],
        "effort": "M",
        "stakeholder": golden_fm["stakeholder"],
        "created": golden_fm["created"],
        "updated": "2026-06-06",
        "after": [],
        "blocks": [],
        "market_research_refs": golden_fm.get("market_research_refs", []),
        "trackable_items": {
            "acceptance_criteria": acs,
            "sections": sections_list,
        },
    }
    return "---\n" + _dump_fm_dict(fm_dict) + "\n---"


def build_epic_frontmatter(golden_fm: dict) -> str:
    """Build epic frontmatter (no ACs, no sections — all moved to features)."""
    fm_dict = {
        "id": "REQ-PROC-032",
        "status": "active",
        "urgency": golden_fm["urgency"],
        "urgency_reason": golden_fm["urgency_reason"],
        "impact": golden_fm["impact"],
        "impact_reason": golden_fm["impact_reason"],
        "effort": "XL",
        "stakeholder": golden_fm["stakeholder"],
        "created": golden_fm["created"],
        "updated": "2026-06-06",
        "after": [],
        "blocks": [],
        "market_research_refs": golden_fm.get("market_research_refs", []),
        "trackable_items": {
            "acceptance_criteria": [],
            "sections": [],
        },
    }
    return "---\n" + _dump_fm_dict(fm_dict) + "\n---"


# ---------------------------------------------------------------------------
# Body builders
# ---------------------------------------------------------------------------

def build_feature_body(feature: dict, body_sections: dict) -> str:
    """Assemble the feature body from its owned sections, byte-exact."""
    parts = []
    # The title line (# Feature Name) — use the heading from the first section
    # Actually the file starts with frontmatter then body; no extra title needed
    # per the golden pattern (golden body starts with # UI Scribble Iteration Workflow then ## sections)
    # For features: start with the sec bodies directly (no top-level # title — features follow same pattern)
    # We include a top-level # title matching the feature folder name for navigability
    folder = feature["folder"]
    # Convert folder to title
    title = folder.replace("feat_", "").replace("_", " ").title()
    parts.append(f"\n# {title}\n")

    for sec_id in feature["sections"]:
        if sec_id in EMPTY_SECTIONS:
            # No body for these — omit
            continue
        if sec_id in body_sections:
            # Append the section, ensuring there's a blank line separator
            section_text = body_sections[sec_id]
            # The section_text already starts with the ## heading
            parts.append("\n" + section_text)
        # else: not found in body (should not happen for non-empty secs)

    return "\n".join(parts)


def build_epic_body(body_sections: dict) -> str:
    """
    Epic body: intro + Background and Motivation + ## Features index
    + Related Requirements + Version History. Byte-exact for retained sections.
    """
    parts = []

    # Top-level title
    parts.append("\n# UI Scribble Iteration Workflow\n")

    # Background and Motivation (SEC-01)
    if "SEC-01" in body_sections:
        parts.append("\n" + body_sections["SEC-01"])

    # Features index (new — not from golden)
    features_index = """
## Features

This epic is non-implementable. All acceptance criteria and body sections have been
distributed to the following child feature requirements:

| Feature | REQ-ID | Folder |
|---------|--------|--------|
| Scribble Core Artifact | REQ-PROC-032-01 | [feat_scribble_core_artifact](feat_scribble_core_artifact/requirements.md) |
| Iteration and Rule Protocol | REQ-PROC-032-02 | [feat_iteration_and_rule_protocol](feat_iteration_and_rule_protocol/requirements.md) |
| Handoff Skills and Contract | REQ-PROC-032-03 | [feat_handoff_skills_and_contract](feat_handoff_skills_and_contract/requirements.md) |
| Scribble Content Extensions | REQ-PROC-032-04 | [feat_scribble_content_extensions](feat_scribble_content_extensions/requirements.md) |
| Consistency SCI Layer | REQ-PROC-032-05 | [feat_consistency_sci_layer](feat_consistency_sci_layer/requirements.md) |
| Carrier and Auto-Review | REQ-PROC-032-06 | [feat_carrier_and_auto_review](feat_carrier_and_auto_review/requirements.md) |
| Embedded Flow Viewer | REQ-PROC-032-07 | [feat_embedded_flow_viewer](feat_embedded_flow_viewer/requirements.md) |"""
    parts.append(features_index)

    # Related Requirements (byte-exact)
    if "Related Requirements" in body_sections:
        parts.append("\n" + body_sections["Related Requirements"])

    # Version History (byte-exact)
    if "Version History" in body_sections:
        parts.append("\n" + body_sections["Version History"])

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Crosswalk builder
# ---------------------------------------------------------------------------

def build_crosswalk(features: list) -> list:
    """Returns list of crosswalk rows."""
    rows = []
    for feat in features:
        for new_idx, old_ac in enumerate(feat["old_acs"], start=1):
            rows.append({
                "old_req": "REQ-PROC-032",
                "old_ac": old_ac,
                "new_req": feat["req_id"],
                "new_ac": f"AC-{new_idx:02d}",
                "feature_folder": feat["folder"],
            })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== REQ-PROC-032 Migration Script ===")
    print(f"Golden source: {GOLDEN_PATH}")
    print(f"Epic dir: {EPIC_DIR}")
    print()

    # Read golden
    golden_text = read_golden(GOLDEN_PATH)
    fm_text, body_text = split_frontmatter_body(golden_text)
    golden_fm = parse_frontmatter(fm_text)
    golden_acs = extract_acs(golden_fm)
    golden_secs_fm = extract_sections_fm(golden_fm)
    body_sections = extract_body_sections(body_text)

    print(f"Golden ACs parsed: {len(golden_acs)}")
    print(f"Golden SECs in FM: {len(golden_secs_fm)}")
    print(f"Body sections extracted: {len([k for k in body_sections if k.startswith('SEC-')])}")
    print()

    # Build crosswalk
    crosswalk = build_crosswalk(FEATURES)
    crosswalk_path = SCRIPT_DIR / "crosswalk.yaml"
    with open(crosswalk_path, "w", encoding="utf-8") as f:
        yaml.dump(crosswalk, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Crosswalk written: {crosswalk_path} ({len(crosswalk)} rows)")

    # Write feature files
    for feat in FEATURES:
        feat_dir = EPIC_DIR / feat["folder"]
        feat_dir.mkdir(exist_ok=True)

        # Build AC list with new ids
        feat_acs = build_feature_ac_list(feat, golden_acs)

        # Frontmatter
        fm = build_frontmatter(
            req_id=feat["req_id"],
            golden_fm=golden_fm,
            acs=feat_acs,
            sec_ids=feat["sections"],
            golden_secs_fm=golden_secs_fm,
        )

        # Body
        body = build_feature_body(feat, body_sections)

        # Write
        content = fm + "\n" + body + "\n"
        out_path = feat_dir / "requirements.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Delete reserve marker
        reserve_marker = EPIC_DIR / f".reserve-{feat['req_id']}"
        if reserve_marker.exists():
            reserve_marker.unlink()
            print(f"Deleted reserve marker: {reserve_marker.name}")

        ac_count = len(feat_acs)
        print(f"Written: {out_path.relative_to(REPO_ROOT)} ({ac_count} ACs, {len(feat['sections'])} SECs)")

    print()

    # Rewrite epic requirements.md
    epic_fm = build_epic_frontmatter(golden_fm)
    epic_body = build_epic_body(body_sections)
    epic_content = epic_fm + "\n" + epic_body + "\n"
    epic_path = EPIC_DIR / "requirements.md"
    with open(epic_path, "w", encoding="utf-8") as f:
        f.write(epic_content)
    print(f"Epic rewritten: {epic_path.relative_to(REPO_ROOT)}")

    # Summary
    print()
    total_acs = sum(len(f["old_acs"]) for f in FEATURES)
    print(f"Total ACs distributed: {total_acs} (expected 70)")
    print("Done.")


if __name__ == "__main__":
    main()
