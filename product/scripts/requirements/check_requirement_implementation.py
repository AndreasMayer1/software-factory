#!/usr/bin/env python3
"""Grep lib/ source tree for implementation traces of each AC in a requirement.

Returns per-AC verdicts: likely_implemented, uncertain, or likely_missing.
Used by the Phase 2c Planner to detect already-implemented ACs.

Usage:
    python3 scripts/check_requirement_implementation.py --requirement REQ-FUNC-007 [--verbose] [--json]

Exit codes:
    0  all ACs have verdicts (some may be 'likely_missing')
    1  requirement file not found
    2  no ACs found in requirement file
    3  argument error

Output:
    Prints one '<AC-ID>: <verdict> - <evidence>' line per AC to stdout, followed by a summary count.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Make scripts/util importable when invoked directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from io import StringIO

from ruamel.yaml import YAML
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent

STOP_WORDS = {
    "must", "shall", "when", "with", "from", "that", "this", "have",
    "will", "been", "their", "which", "each", "also", "into", "than",
    "user", "able", "allow", "given", "then", "after", "before",
    "should", "could", "would", "does", "more", "less",
}


# ---------------------------------------------------------------------------
# YAML parsing — delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08)
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Extract and parse YAML frontmatter from markdown content."""
    if content.startswith("﻿"):
        content = content[1:]
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml.strip():
        return None
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
    try:
        result = yaml.load(StringIO(raw_yaml))
    except Exception:
        return None
    if result is None or not isinstance(result, dict) or len(result) == 0:
        return None
    return dict(result)


# ---------------------------------------------------------------------------
# File finding
# ---------------------------------------------------------------------------

def _find_files(root: Path, name: str) -> list[Path]:
    """Locate files by name using native find (faster than rglob on WSL2)."""
    try:
        result = subprocess.run(
            ["find", str(root), "-name", name],
            capture_output=True, text=True,
        )
        return [Path(p) for p in result.stdout.splitlines() if p.strip()]
    except FileNotFoundError:
        return list(root.rglob(name))


def find_requirement_file(req_id: str) -> Optional[Path]:
    """Find requirements.md file with matching id: REQ-ID in frontmatter."""
    root = PROJECT_ROOT / "requirements_tasks"
    for req_file in _find_files(root, "requirements.md"):
        try:
            content = req_file.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = _parse_frontmatter(content)
        if meta and str(meta.get("id", "")).strip() == req_id:
            return req_file
    return None


# ---------------------------------------------------------------------------
# AC extraction
# ---------------------------------------------------------------------------

def extract_acs(content: str) -> list[dict[str, str]]:
    """Extract AC entries from requirements.md body.

    Handles:
    - `- [ ] AC-01: text` or `- [x] AC-01: text`
    - `**AC-01**: text` (bold)
    - `### AC-01` headings
    - `AC-01:` at start of a line
    """
    acs: list[dict[str, str]] = []
    seen: set[Any] = set()

    # Remove frontmatter
    fm_match = re.match(r"^---\n.*?\n---\n?", content, re.DOTALL)
    body = content[fm_match.end():] if fm_match else content

    # Pattern 1: checkbox list items
    for m in re.finditer(
        r"^[-*]\s+\[[ xX]\]\s+(AC-\d+)[:\s]+(.*)$", body, re.MULTILINE
    ):
        ac_id = m.group(1)
        if ac_id not in seen:
            acs.append({"id": ac_id, "text": m.group(2).strip()})
            seen.add(ac_id)

    # Pattern 2: bold AC refs
    for m in re.finditer(r"\*\*(AC-\d+)\*\*[:\s]+(.*?)(?:\n|$)", body):
        ac_id = m.group(1)
        if ac_id not in seen:
            acs.append({"id": ac_id, "text": m.group(2).strip()})
            seen.add(ac_id)

    # Pattern 3: headings ### AC-01
    for m in re.finditer(r"^#{2,4}\s+(AC-\d+)[:\s]*(.*)$", body, re.MULTILINE):
        ac_id = m.group(1)
        if ac_id not in seen:
            acs.append({"id": ac_id, "text": m.group(2).strip()})
            seen.add(ac_id)

    # Pattern 4: bare AC-01: at start of line
    for m in re.finditer(r"^(AC-\d+):\s+(.*)$", body, re.MULTILINE):
        ac_id = m.group(1)
        if ac_id not in seen:
            acs.append({"id": ac_id, "text": m.group(2).strip()})
            seen.add(ac_id)

    # Sort by AC number
    def _ac_num(a: dict[Any, Any]) -> int:
        m_num = re.search(r"\d+", a["id"])
        return int(m_num.group()) if m_num else 0

    acs.sort(key=_ac_num)
    return acs


# ---------------------------------------------------------------------------
# Search term generation
# ---------------------------------------------------------------------------

def ac_to_search_terms(ac_id: str, ac_text: str) -> list[str]:
    """Generate grep search terms from AC ID and text.

    Strategy:
    1. AC-ID itself (e.g. "AC-01") — search in lib/ comments/strings
    2. Key nouns from AC text (stop-word filtered, >=4 chars)
    3. CamelCase/PascalCase variants of those nouns
    """
    terms = [ac_id]

    # Extract content words
    words = re.findall(r"[A-Za-z]{4,}", ac_text)
    content_words = [
        w for w in words
        if w.lower() not in STOP_WORDS
    ]

    for word in content_words[:3]:
        terms.append(word)
        # PascalCase variant
        pascal = word[0].upper() + word[1:]
        if pascal != word:
            terms.append(pascal)

    return list(dict.fromkeys(terms))  # preserve order, deduplicate


# ---------------------------------------------------------------------------
# Grep execution
# ---------------------------------------------------------------------------

def grep_for_term(term: str, lib_root: Path) -> list[str]:
    """Run grep recursively for term in lib/ and return matching file paths."""
    try:
        result = subprocess.run(
            ["grep", "-rl", "--include=*.dart", term, str(lib_root)],
            capture_output=True, text=True,
        )
        return [p.strip() for p in result.stdout.splitlines() if p.strip()]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------

def compute_verdict(matching_files: list[str]) -> str:
    """Compute verdict from grep match results.

    likely_implemented : >=2 distinct files match, or AC-ID itself found in lib/
    uncertain          : exactly 1 file matches
    likely_missing     : 0 matches
    """
    if not matching_files:
        return "likely_missing"
    unique_files = list(set(matching_files))
    if len(unique_files) >= 2:
        return "likely_implemented"
    return "uncertain"


def analyze_ac(ac: dict[str, str], lib_root: Path) -> dict[str, Any]:
    """Analyze one AC and return verdict dict."""
    terms = ac_to_search_terms(ac["id"], ac["text"])

    all_files: list[str] = []
    ac_id_found_directly = False

    for term in terms:
        files = grep_for_term(term, lib_root)
        all_files.extend(files)
        if term == ac["id"] and files:
            ac_id_found_directly = True

    unique_files = list(set(all_files))

    # Override to likely_implemented if AC-ID found literally in code
    if ac_id_found_directly:
        verdict = "likely_implemented"
    else:
        verdict = compute_verdict(unique_files)

    return {
        "id": ac["id"],
        "verdict": verdict,
        "match_count": len(unique_files),
        "files": sorted(unique_files),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check lib/ for implementation traces of requirement ACs"
    )
    parser.add_argument("--requirement", required=True, metavar="REQ-ID",
                        help="Requirement ID (e.g. REQ-FUNC-007)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show matching file paths per AC")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of human-readable text")
    args = parser.parse_args()

    req_id = args.requirement.strip()

    # Find requirement file
    req_file = find_requirement_file(req_id)
    if req_file is None:
        print(f"ERROR: Requirement file not found for {req_id}", file=sys.stderr)
        sys.exit(1)

    content = req_file.read_text(encoding="utf-8")
    acs = extract_acs(content)

    if not acs:
        print(f"ERROR: No ACs found in {req_file}", file=sys.stderr)
        sys.exit(2)

    lib_root = PROJECT_ROOT / "lib"
    if not lib_root.exists():
        print(f"WARNING: lib/ directory not found at {lib_root}", file=sys.stderr)

    results: list[dict[str, Any]] = []
    for ac in acs:
        result = analyze_ac(ac, lib_root)
        results.append(result)

    # Compute summary
    summary: dict[str, int] = {
        "likely_implemented": 0,
        "uncertain": 0,
        "likely_missing": 0,
    }
    for r in results:
        summary[r["verdict"]] = summary.get(r["verdict"], 0) + 1

    if args.json:
        output = {
            "requirement": req_id,
            "acs": results,
            "summary": summary,
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    # Human-readable output
    print(f"{req_id} — {len(acs)} ACs analyzed\n")

    for r in results:
        verdict_label = r["verdict"].ljust(20)
        print(f"  {r['id']}: {verdict_label} ({r['match_count']} matches in lib/)")
        if args.verbose and r["files"]:
            for f in r["files"]:
                print(f"    {f}")

    print(f"\nSummary: {summary['likely_implemented']} likely_implemented, "
          f"{summary['uncertain']} uncertain, {summary['likely_missing']} likely_missing")

    sys.exit(0)


if __name__ == "__main__":
    main()
