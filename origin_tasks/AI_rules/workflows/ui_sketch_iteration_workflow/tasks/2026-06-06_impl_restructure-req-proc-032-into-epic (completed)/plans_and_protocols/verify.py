#!/usr/bin/env python3
"""
Verification harness for REQ-PROC-032 migration.
Asserts byte-exact fidelity of AC names/descriptions and SEC body prose.

Usage:
    python3 verify.py

Pass condition: exits 0 with "ALL CHECKS PASS" and empty diffs.
Fail condition: exits 1, prints unified diffs for every mismatch.
"""

import sys
import os
import re
import difflib
import yaml
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parents[7]
EPIC_DIR = SCRIPT_DIR.parents[2]
GOLDEN_PATH = Path("/tmp/golden_requirements.md")
CROSSWALK_PATH = SCRIPT_DIR / "crosswalk.yaml"

# ---------------------------------------------------------------------------
# Feature spec (same as migrate.py — must stay in sync)
# ---------------------------------------------------------------------------
FEATURES = [
    {
        "req_id": "REQ-PROC-032-01",
        "folder": "feat_scribble_core_artifact",
        "sections": ["SEC-01", "SEC-02", "SEC-03", "SEC-04", "SEC-05"],
    },
    {
        "req_id": "REQ-PROC-032-02",
        "folder": "feat_iteration_and_rule_protocol",
        "sections": ["SEC-06", "SEC-07", "SEC-08", "SEC-09", "SEC-10"],
    },
    {
        "req_id": "REQ-PROC-032-03",
        "folder": "feat_handoff_skills_and_contract",
        "sections": ["SEC-11", "SEC-15", "SEC-16"],
    },
    {
        "req_id": "REQ-PROC-032-04",
        "folder": "feat_scribble_content_extensions",
        "sections": ["SEC-12", "SEC-13", "SEC-14", "SEC-17"],
    },
    {
        "req_id": "REQ-PROC-032-05",
        "folder": "feat_consistency_sci_layer",
        "sections": ["SEC-18"],
    },
    {
        "req_id": "REQ-PROC-032-06",
        "folder": "feat_carrier_and_auto_review",
        "sections": ["SEC-19", "SEC-20"],
    },
    {
        "req_id": "REQ-PROC-032-07",
        "folder": "feat_embedded_flow_viewer",
        "sections": ["SEC-21"],
    },
]

EMPTY_SECTIONS = {"SEC-12", "SEC-13", "SEC-14"}

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
    "## Scribble–Coder Contract": "SEC-15",
    "## Scribble Review Doctrine": "SEC-16",
    "## Scribble Content Extensions": "SEC-17",
    "## Consistency and Scribble-Layer Model": "SEC-18",
    "## Scribble Carrier Format and Human Review Layer": "SEC-19",
    "## Auto-Review Control Model": "SEC-20",
    "## Embedded Flow-Viewer Sidebar": "SEC-21",
}

# ---------------------------------------------------------------------------
# Parsing helpers (duplicated from migrate.py for self-containedness)
# ---------------------------------------------------------------------------

def split_frontmatter_body(text: str):
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
    body_text = "\n".join(lines[end_idx + 1:])
    return fm_text, body_text


def parse_frontmatter(fm_text: str) -> dict:
    return yaml.safe_load(fm_text)


def extract_acs(fm: dict) -> dict:
    """Returns {ac_id: {id, name, description, ...}}"""
    acs = {}
    for item in fm["trackable_items"]["acceptance_criteria"]:
        acs[item["id"]] = dict(item)
    return acs


def extract_body_sections(body: str) -> dict:
    lines = body.split("\n")
    heading_positions = []
    for i, line in enumerate(lines):
        if re.match(r'^## [^\n]', line):
            heading_positions.append((i, line))

    sections = {}
    if heading_positions:
        intro_lines = lines[:heading_positions[0][0]]
        sections["epic_intro"] = "\n".join(intro_lines)

    for idx, (line_i, heading) in enumerate(heading_positions):
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
            sections[heading_stripped] = section_text

    return sections


def unified_diff(a: str, b: str, fromfile: str = "expected", tofile: str = "actual") -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    diff = list(difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile))
    return "".join(diff)


# ---------------------------------------------------------------------------
# Check 1: AC fidelity
# ---------------------------------------------------------------------------

def check_ac_fidelity(golden_acs: dict, crosswalk: list) -> list:
    """
    For every golden AC, find its migrated AC via crosswalk in the feature files.
    Assert name and description are BYTE-IDENTICAL to golden.
    Returns list of failure messages.
    """
    failures = []

    # Load all feature ACs
    feature_acs = {}  # (req_id, new_ac_id) -> {id, name, description}
    for feat in FEATURES:
        feat_path = EPIC_DIR / feat["folder"] / "requirements.md"
        if not feat_path.exists():
            failures.append(f"MISSING: {feat_path}")
            continue
        with open(feat_path, "r", encoding="utf-8") as f:
            text = f.read()
        try:
            fm_text, _ = split_frontmatter_body(text)
            fm = parse_frontmatter(fm_text)
            acs = extract_acs(fm)
            for ac_id, ac in acs.items():
                feature_acs[(feat["req_id"], ac_id)] = ac
        except Exception as e:
            failures.append(f"PARSE ERROR {feat_path}: {e}")

    # Check each crosswalk row
    for row in crosswalk:
        old_req = row["old_req"]
        old_ac = row["old_ac"]
        new_req = row["new_req"]
        new_ac = row["new_ac"]

        golden_item = golden_acs.get(old_ac)
        if golden_item is None:
            failures.append(f"GOLDEN MISSING: {old_ac}")
            continue

        migrated_item = feature_acs.get((new_req, new_ac))
        if migrated_item is None:
            failures.append(f"MIGRATED MISSING: {new_req}/{new_ac} (from {old_ac})")
            continue

        # Check name byte-exact
        if migrated_item["name"] != golden_item["name"]:
            diff = unified_diff(
                golden_item["name"],
                migrated_item["name"],
                fromfile=f"golden/{old_ac}/name",
                tofile=f"migrated/{new_req}/{new_ac}/name",
            )
            failures.append(f"NAME MISMATCH {old_ac} -> {new_req}/{new_ac}:\n{diff}")

        # Check description byte-exact
        if migrated_item["description"] != golden_item["description"]:
            diff = unified_diff(
                golden_item["description"],
                migrated_item["description"],
                fromfile=f"golden/{old_ac}/description",
                tofile=f"migrated/{new_req}/{new_ac}/description",
            )
            failures.append(f"DESCRIPTION MISMATCH {old_ac} -> {new_req}/{new_ac}:\n{diff}")

    return failures


# ---------------------------------------------------------------------------
# Check 2: Bijective crosswalk
# ---------------------------------------------------------------------------

def check_bijective(crosswalk: list, golden_acs: dict) -> list:
    """
    Each old AC appears exactly once; new ids restart per feature with no gaps.
    """
    failures = []

    old_ac_set = set(golden_acs.keys())  # AC-01..AC-70
    seen_old = {}
    seen_new = {}  # (new_req, new_ac) -> old_ac

    for row in crosswalk:
        old_ac = row["old_ac"]
        new_req = row["new_req"]
        new_ac = row["new_ac"]

        if old_ac in seen_old:
            failures.append(f"DUPLICATE old AC: {old_ac} appears in both {seen_old[old_ac]} and {(new_req, new_ac)}")
        seen_old[old_ac] = (new_req, new_ac)

        key = (new_req, new_ac)
        if key in seen_new:
            failures.append(f"DUPLICATE new AC: {key} assigned to both {seen_new[key]} and {old_ac}")
        seen_new[key] = old_ac

    # Check all golden ACs covered
    for ac in sorted(old_ac_set, key=lambda x: int(x.split("-")[1])):
        if ac not in seen_old:
            failures.append(f"MISSING from crosswalk: {ac}")

    # Check no extra ACs
    for old_ac in seen_old:
        if old_ac not in old_ac_set:
            failures.append(f"SPURIOUS in crosswalk: {old_ac}")

    # Check per-feature new ids restart at AC-01 with no gaps
    feat_acs = {}
    for row in crosswalk:
        feat_acs.setdefault(row["new_req"], []).append(row["new_ac"])

    for req_id, ac_ids in feat_acs.items():
        nums = sorted(int(a.split("-")[1]) for a in ac_ids)
        expected = list(range(1, len(nums) + 1))
        if nums != expected:
            failures.append(f"GAPS in {req_id} new AC ids: {ac_ids} (expected 01..{len(nums):02d})")

    if not failures:
        total = len(crosswalk)
        if total != 70:
            failures.append(f"CROSSWALK ROW COUNT: {total} (expected 70)")

    return failures


# ---------------------------------------------------------------------------
# Check 3: Section fidelity
# ---------------------------------------------------------------------------

def check_section_fidelity(golden_body_sections: dict, golden_secs_fm: dict) -> list:
    """
    For every golden SEC body, find it in a feature (or epic) file.
    Assert heading+prose BYTE-IDENTICAL.
    All 21 SEC ids appear in exactly one trackable_items.sections.
    The 18 with bodies match byte-exact; the 3 empty stay empty.
    """
    failures = []

    # Build map of sec_id -> owning feature folder
    sec_to_feat = {}
    for feat in FEATURES:
        for sec_id in feat["sections"]:
            sec_to_feat[sec_id] = feat

    # Load all feature file body sections
    all_feat_body_sections = {}  # (folder, sec_id) -> body_text
    feat_sec_ids_in_fm = {}  # folder -> [sec_id, ...]

    for feat in FEATURES:
        feat_path = EPIC_DIR / feat["folder"] / "requirements.md"
        if not feat_path.exists():
            failures.append(f"MISSING: {feat_path}")
            continue
        with open(feat_path, "r", encoding="utf-8") as f:
            text = f.read()
        try:
            fm_text, body_text = split_frontmatter_body(text)
            fm = parse_frontmatter(fm_text)
            secs_in_fm = [s["id"] for s in fm["trackable_items"]["sections"]]
            feat_sec_ids_in_fm[feat["folder"]] = secs_in_fm
            body_secs = extract_body_sections(body_text)
            for sec_id, content in body_secs.items():
                if sec_id.startswith("SEC-"):
                    all_feat_body_sections[(feat["folder"], sec_id)] = content
        except Exception as e:
            failures.append(f"PARSE ERROR {feat_path}: {e}")

    # Check: all 21 SEC ids appear in exactly one trackable_items.sections
    sec_assignments = {}  # sec_id -> [folder, ...]
    for folder, sec_ids in feat_sec_ids_in_fm.items():
        for sid in sec_ids:
            sec_assignments.setdefault(sid, []).append(folder)

    for sec_id in golden_secs_fm:
        assigned = sec_assignments.get(sec_id, [])
        if len(assigned) == 0:
            failures.append(f"SEC NOT IN ANY FEATURE FM: {sec_id}")
        elif len(assigned) > 1:
            failures.append(f"SEC IN MULTIPLE FEATURE FMs: {sec_id} in {assigned}")

    for sec_id in sec_assignments:
        if sec_id not in golden_secs_fm:
            failures.append(f"SPURIOUS SEC IN FEATURE FM: {sec_id}")

    # Check body fidelity for sections that have body in golden
    for sec_id, golden_body in golden_body_sections.items():
        if not sec_id.startswith("SEC-"):
            continue
        if sec_id in EMPTY_SECTIONS:
            # Should NOT have body in any feature
            owning_feat = sec_to_feat.get(sec_id)
            if owning_feat:
                feat_body = all_feat_body_sections.get((owning_feat["folder"], sec_id))
                if feat_body is not None:
                    failures.append(f"EMPTY SEC {sec_id} unexpectedly has body in {owning_feat['folder']}")
            continue

        owning_feat = sec_to_feat.get(sec_id)
        if owning_feat is None:
            failures.append(f"SEC {sec_id} has no owning feature in FEATURES spec")
            continue

        feat_body = all_feat_body_sections.get((owning_feat["folder"], sec_id))
        if feat_body is None:
            failures.append(f"SEC {sec_id} body NOT FOUND in {owning_feat['folder']}")
            continue

        # Strip trailing whitespace on each line for comparison, but preserve structure
        # Actually we want byte-exact on the content. Compare after stripping trailing
        # whitespace from lines (the file writer may add a trailing newline).
        # We compare the section text itself (heading line + prose).
        golden_norm = golden_body.rstrip()
        feat_norm = feat_body.rstrip()

        if golden_norm != feat_norm:
            diff = unified_diff(
                golden_norm + "\n",
                feat_norm + "\n",
                fromfile=f"golden/{sec_id}",
                tofile=f"{owning_feat['folder']}/{sec_id}",
            )
            failures.append(f"SEC BODY MISMATCH {sec_id} in {owning_feat['folder']}:\n{diff}")

    return failures


# ---------------------------------------------------------------------------
# Check 4: Epic body fidelity
# ---------------------------------------------------------------------------

def check_epic_body_fidelity(golden_body_sections: dict) -> list:
    """
    Epic's retained Background/Related Requirements/Version History spans
    are byte-identical to golden.
    """
    failures = []

    epic_path = EPIC_DIR / "requirements.md"
    if not epic_path.exists():
        return [f"MISSING: {epic_path}"]

    with open(epic_path, "r", encoding="utf-8") as f:
        epic_text = f.read()

    try:
        fm_text, epic_body = split_frontmatter_body(epic_text)
        epic_sections = extract_body_sections(epic_body)
    except Exception as e:
        return [f"PARSE ERROR epic requirements.md: {e}"]

    # Check Background and Motivation (SEC-01)
    golden_bg = golden_body_sections.get("SEC-01", "")
    epic_bg = epic_sections.get("SEC-01", "")
    if golden_bg.rstrip() != epic_bg.rstrip():
        diff = unified_diff(
            golden_bg.rstrip() + "\n",
            epic_bg.rstrip() + "\n",
            fromfile="golden/SEC-01",
            tofile="epic/SEC-01",
        )
        failures.append(f"EPIC SEC-01 MISMATCH:\n{diff}")

    # Check Related Requirements
    golden_rr = golden_body_sections.get("Related Requirements", "")
    epic_rr = epic_sections.get("Related Requirements", "")
    if golden_rr.rstrip() != epic_rr.rstrip():
        diff = unified_diff(
            golden_rr.rstrip() + "\n",
            epic_rr.rstrip() + "\n",
            fromfile="golden/Related Requirements",
            tofile="epic/Related Requirements",
        )
        failures.append(f"EPIC Related Requirements MISMATCH:\n{diff}")

    # Check Version History
    golden_vh = golden_body_sections.get("Version History", "")
    epic_vh = epic_sections.get("Version History", "")
    if golden_vh.rstrip() != epic_vh.rstrip():
        diff = unified_diff(
            golden_vh.rstrip() + "\n",
            epic_vh.rstrip() + "\n",
            fromfile="golden/Version History",
            tofile="epic/Version History",
        )
        failures.append(f"EPIC Version History MISMATCH:\n{diff}")

    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== REQ-PROC-032 Migration Verification Harness ===")
    print()

    # Load golden
    if not GOLDEN_PATH.exists():
        print(f"FATAL: golden file not found at {GOLDEN_PATH}")
        sys.exit(1)

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        golden_text = f.read()

    fm_text, body_text = split_frontmatter_body(golden_text)
    golden_fm = parse_frontmatter(fm_text)
    golden_acs = extract_acs(golden_fm)
    golden_secs_fm = {s["id"]: s for s in golden_fm["trackable_items"]["sections"]}
    golden_body_sections = extract_body_sections(body_text)

    print(f"Golden ACs: {len(golden_acs)}")
    print(f"Golden SECs in FM: {len(golden_secs_fm)}")
    print(f"Golden body sections: {len([k for k in golden_body_sections if k.startswith('SEC-')])}")
    print()

    # Load crosswalk
    if not CROSSWALK_PATH.exists():
        print(f"FATAL: crosswalk not found at {CROSSWALK_PATH}")
        sys.exit(1)
    with open(CROSSWALK_PATH, "r", encoding="utf-8") as f:
        crosswalk = yaml.safe_load(f)
    print(f"Crosswalk rows: {len(crosswalk)}")
    print()

    all_failures = []

    # Check 1: AC fidelity
    print("--- Check 1: AC fidelity ---")
    f1 = check_ac_fidelity(golden_acs, crosswalk)
    if f1:
        for msg in f1:
            print(f"  FAIL: {msg}")
        all_failures.extend(f1)
    else:
        print("  PASS: all 70 AC names and descriptions are byte-identical to golden")
    print()

    # Check 2: Bijective
    print("--- Check 2: Bijective crosswalk ---")
    f2 = check_bijective(crosswalk, golden_acs)
    if f2:
        for msg in f2:
            print(f"  FAIL: {msg}")
        all_failures.extend(f2)
    else:
        print("  PASS: crosswalk is bijective (70 rows, each old AC exactly once, new ids gapless)")
    print()

    # Check 3: Section fidelity
    print("--- Check 3: Section fidelity ---")
    f3 = check_section_fidelity(golden_body_sections, golden_secs_fm)
    if f3:
        for msg in f3:
            print(f"  FAIL: {msg}")
        all_failures.extend(f3)
    else:
        print("  PASS: all 18 body sections are byte-identical; 3 empty sections present in FM only")
    print()

    # Check 4: Epic body fidelity
    print("--- Check 4: Epic body fidelity ---")
    f4 = check_epic_body_fidelity(golden_body_sections)
    if f4:
        for msg in f4:
            print(f"  FAIL: {msg}")
        all_failures.extend(f4)
    else:
        print("  PASS: epic Background, Related Requirements, Version History are byte-identical to golden")
    print()

    # Summary
    if all_failures:
        print(f"=== RESULT: FAIL — {len(all_failures)} issue(s) found ===")
        sys.exit(1)
    else:
        print("=== RESULT: ALL CHECKS PASS — empty diff on all four checks ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
