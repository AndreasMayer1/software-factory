#!/usr/bin/env python3
"""
generate_concept_canon_md.py

Parses requirements_user_needs/concept_canon/concept_canon.yaml and emits:
  - concept_canon.md          human-readable reference (v3 §7.4)
  - concept_canon.index.yaml  lightweight lookup index (v3 §7.5)

Usage:
  python3 scripts/user_needs/generate_concept_canon_md.py [--input PATH] [--dry-run]

Outputs are written alongside the input file unless overridden.

Output:
    Writes concept_canon.md and concept_canon.index.yaml alongside the input (unless --dry-run). Prints a one-line per-output summary to stdout.
"""

# tier: C  # one-shot CLI user-needs tool; no in-tree Python imports

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

ROOT = Path(__file__).parent.parent.parent
DEFAULT_INPUT = ROOT / "requirements_user_needs" / "concept_canon" / "concept_canon.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_canon(input_path: Path) -> dict[Any, Any]:
    try:
        data = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: Failed to parse {input_path}: {exc}", file=sys.stderr)
        sys.exit(1)
    return data


def _now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def _now_date() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# concept_canon.md builder (v3 §7.4)
# ---------------------------------------------------------------------------

def _build_md(data: dict[Any, Any], input_path: Path) -> str:
    concepts = data.get("concepts") or []
    schema_version = data.get("schema_version", "?")
    generated_at = _now_local()
    script_path = "scripts/user_needs/generate_concept_canon_md.py"

    lines: list[str] = []
    lines.append("# Concept Canon\n")
    lines.append(f"> Generated from `{input_path.name}` — do not edit directly.  ")
    lines.append(f"> Run `{script_path}` to regenerate.\n")
    lines.append(f"Schema version: {schema_version}  \nGenerated: {generated_at}\n")
    lines.append("---\n")

    if not concepts:
        lines.append("## No concepts defined yet\n")
        lines.append(
            "The canon is empty. Add entries by running the `ux-write-canon-concept` skill.\n"
        )
        return "\n".join(lines)

    # Table of contents
    lines.append("## Table of Contents\n")
    for c in concepts:
        cid = c.get("id", "UNKNOWN")
        name = c.get("name_canonical", cid)
        anchor = cid.lower().replace("-", "-")
        lines.append(f"- [{cid}](#{anchor}) — {name}")
    lines.append("")
    lines.append("---\n")

    # Per-concept sections
    for c in concepts:
        cid = c.get("id", "UNKNOWN")
        name = c.get("name_canonical", "")
        ctype = c.get("type", "")
        status = c.get("status", "active")
        description = c.get("description", "").strip()
        states = c.get("states") or []
        operations = c.get("operations") or []
        related = c.get("related") or []
        aliases = c.get("aliases") or {}
        forbidden = c.get("forbidden_synonyms") or []
        provenance = c.get("provenance") or {}
        introduced_by = c.get("introduced_by", "")
        archived_reason = c.get("archived_reason", "")

        lines.append(f"## {cid} — {name}\n")

        meta_parts = []
        if ctype:
            meta_parts.append(f"**Type:** {ctype}")
        meta_parts.append(f"**Status:** {status}")
        if introduced_by:
            meta_parts.append(f"**Introduced by:** {introduced_by}")
        lines.append(" | ".join(meta_parts))
        lines.append("")

        if archived_reason:
            lines.append(f"> **Archived:** {archived_reason}\n")

        if description:
            lines.append(f"**Description:** {description}\n")

        if states:
            lines.append(f"**States:** {', '.join(states)}\n")

        if operations:
            lines.append(f"**Operations:** {', '.join(operations)}\n")

        if related:
            lines.append(f"**Related:** {', '.join(related)}\n")

        # Aliases
        alias_parts = []
        alias_de = aliases.get("de")
        if alias_de:
            alias_parts.append(f"DE: {alias_de}")
        alias_code = aliases.get("code") or []
        if alias_code:
            code_ids = [
                (a.get("identifier", a) if isinstance(a, dict) else a)
                for a in alias_code
            ]
            alias_parts.append(f"code: {', '.join(code_ids)}")
        alias_legacy = aliases.get("legacy") or []
        if alias_legacy:
            alias_parts.append(f"legacy: {', '.join(alias_legacy)}")
        if alias_parts:
            lines.append(f"**Aliases:** {' | '.join(alias_parts)}\n")

        # Forbidden synonyms
        if forbidden:
            lines.append("**Forbidden synonyms:**")
            for fs in forbidden:
                term = fs.get("term", "")
                lang = fs.get("lang", "")
                note = fs.get("note", "")
                line = f"- `{term}` ({lang})"
                if note:
                    line += f" — {note}"
                lines.append(line)
            lines.append("")

        # Provenance
        if provenance:
            lines.append("**Provenance:**")
            for lang, prov in provenance.items():
                level = prov.get("level", "?")
                sources = prov.get("sources") or []
                notes = prov.get("notes", "").strip()
                validated_at = prov.get("validated_at", "")
                src_str = ", ".join(
                    (s.get("id", "") + (f"#{s['anchor']}" if s.get("anchor") else ""))
                    if isinstance(s, dict) else str(s)
                    for s in sources
                ) if sources else "none"
                prov_line = f"- **{lang}**: {level}"
                if src_str != "none":
                    prov_line += f" | sources: {src_str}"
                if validated_at:
                    prov_line += f" | validated: {validated_at}"
                if notes:
                    prov_line += f" | {notes}"
                lines.append(prov_line)
            lines.append("")

        lines.append("---\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# concept_canon.index.yaml builder (v3 §7.5)
# ---------------------------------------------------------------------------

def _build_index(data: dict[Any, Any], input_path: Path) -> str:
    concepts = data.get("concepts") or []
    generated_at = _now_date()

    header = (
        f"# concept_canon.index.yaml (generated; do not edit)\n"
        f"version: 1\n"
        f"generated_from: {input_path.name}\n"
        f"generated_at: {generated_at}\n"
        f"concepts:\n"
    )

    if not concepts:
        return header + "  []  # no concepts yet\n"

    entries: list[str] = []
    for c in concepts:
        cid = c.get("id", "UNKNOWN")
        name = c.get("name_canonical", "")
        ctype = c.get("type", "")
        aliases = c.get("aliases") or {}
        alias_de_raw = aliases.get("de")

        if isinstance(alias_de_raw, list):
            alias_de = alias_de_raw
        elif alias_de_raw:
            alias_de = [alias_de_raw]
        else:
            alias_de = []

        entry = f"  - id: {cid}\n    name: {name}\n"
        if alias_de:
            entry += f"    aliases_de: [{', '.join(alias_de)}]\n"
        else:
            entry += "    aliases_de: []\n"
        if ctype:
            entry += f"    type: {ctype}\n"
        entries.append(entry)

    return header + "\n".join(entries)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate concept_canon.md and concept_canon.index.yaml from concept_canon.yaml."
    )
    parser.add_argument(
        "--input",
        metavar="PATH",
        default=str(DEFAULT_INPUT),
        help="Path to concept_canon.yaml (default: requirements_user_needs/concept_canon/concept_canon.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing files.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    data = _load_canon(input_path)
    canon_dir = input_path.parent

    md_content = _build_md(data, input_path)
    index_content = _build_index(data, input_path)

    md_path = canon_dir / "concept_canon.md"
    index_path = canon_dir / "concept_canon.index.yaml"

    if args.dry_run:
        print(f"[dry-run] Would write {md_path} ({len(md_content)} bytes)")
        print(f"[dry-run] Would write {index_path} ({len(index_content)} bytes)")
        return

    md_path.write_text(md_content, encoding="utf-8")
    index_path.write_text(index_content, encoding="utf-8")

    concept_count = len(data.get("concepts") or [])
    print(f"Written: {md_path} ({concept_count} concept(s))")
    print(f"Written: {index_path} ({concept_count} concept(s))")


if __name__ == "__main__":
    main()
