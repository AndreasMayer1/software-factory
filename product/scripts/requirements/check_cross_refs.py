#!/usr/bin/env python3
"""
Cross-reference completeness detection for requirements.

Given a target requirement's requirements.md, returns the set of semantically
related requirements not already cross-referenced by that target.

The mechanism derives 2-4 search terms from the requirement's title and first
paragraph (or accepts explicit --terms), greps across requirements_tasks/
subdirectories, and excludes any hit whose REQ-ID already appears in the
target's after:/blocks: chains or ## Related Requirements section.

Output:
    JSON array, one object per cross-reference gap:
      {
        "id":            "REQ-PROC-045",
        "path":          "requirements_tasks/process/.../requirements.md",
        "matched_terms": ["cross", "reference"],
        "snippet":       "first matching line excerpt (≤120 chars)"
      }
    Empty array [] means no unlinked related requirements found.

Usage:
    python3 scripts/requirements/check_cross_refs.py <path-to-requirements.md>
    python3 scripts/requirements/check_cross_refs.py <path> --terms term1 term2

Exit codes:
    0 — ran successfully (gaps found or not)
    1 — script error (missing target, no frontmatter, missing id field, parse failure)
"""

# tier: B  # reusable requirements tool — called by requ-explore (Phase 1.4)
#           # and task-derive-from-requ (Phase 1.5 / TASK-PROC-058-03)

# Why: read_frontmatter is the G4-compliant entrypoint for YAML parsing in this
# project; using it (rather than hand-rolling frontmatter detection) keeps this
# script inside the G4 allow-list boundary defined in yaml_frontmatter.py.
# Source: requirements_tasks/process/AI_rules/coding_standards/python_code_quality/
#         tasks/2026-05-17_impl_python-tooling-config-and-gates/
#         plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#D

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from util.yaml_frontmatter import (  # type: ignore[import-not-found]
    FrontmatterError,
    read_frontmatter,
)

_STOP_WORDS: frozenset[str] = frozenset(
    {
        "the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "for",
        "that", "this", "with", "by", "from", "at", "be", "as", "not", "it",
        "on", "which", "when", "all", "any", "must", "will", "can", "should",
        "have", "has", "been", "its", "via", "into", "per", "each", "every",
        "no", "only", "also", "such", "than", "then", "they", "their", "our",
        "if", "else", "both", "may", "was", "were", "how", "what", "who",
        # User Story boilerplate — match nearly every requirement when used as search terms
        "user", "want", "story", "developer", "stakeholder", "persona", "actor",
    }
)

_MAX_TERM_CANDIDATES: int = 20  # scan this many candidate words for frequency check
_MAX_TERM_FREQ: int = 15        # prefer terms matching ≤ this many requirements.md files
_MIN_GOOD_HITS: int = 10        # good terms must collectively match ≥ this many files

_REQ_ID_RE = re.compile(r"REQ-[A-Z]+-\d+(?:-\d+)*")
_RELATED_HEADER_RE = re.compile(r"^##\s+Related Requirements", re.MULTILINE)
_NEXT_HEADER_RE = re.compile(r"^##\s+", re.MULTILINE)


def _extract_req_id(path: Path) -> str | None:
    """Return the REQ-ID from a requirements.md frontmatter, or None on any failure."""
    try:
        doc = read_frontmatter(path)
    except (OSError, FrontmatterError):
        return None
    if not doc.has_frontmatter:
        return None
    value = doc.metadata.get("id")
    return str(value) if value else None


def _ids_from_yaml_field(value: object) -> set[str]:
    if not value:
        return set()
    if isinstance(value, list):
        return {str(v) for v in value if v}
    return {str(value)}


def _get_excluded_ids(doc: object, body: str, self_id: str) -> set[str]:
    """Collect every REQ-ID the target already cross-references."""
    excluded: set[str] = {self_id}

    for field in ("after", "blocks"):
        excluded |= _ids_from_yaml_field(doc.metadata.get(field))  # type: ignore[attr-defined]

    match = _RELATED_HEADER_RE.search(body)
    if match:
        section_start = match.end()
        next_h = _NEXT_HEADER_RE.search(body[section_start:])
        section_end = section_start + next_h.start() if next_h else len(body)
        excluded |= set(_REQ_ID_RE.findall(body[section_start:section_end]))

    return excluded


def _derive_search_terms(title: str, first_paragraph: str, max_terms: int = 4) -> list[str]:
    """Derive up to max_terms search terms; prefer title words, fill from first paragraph."""
    terms: list[str] = []
    seen: set[str] = set()

    for source in (title, first_paragraph):
        for word in re.findall(r"[A-Za-z]{3,}", source):
            low = word.lower()
            if low not in _STOP_WORDS and low not in seen:
                seen.add(low)
                terms.append(word)
            if len(terms) >= max_terms:
                break
        if len(terms) >= max_terms:
            break

    return terms


def _grep_files(term: str, search_dirs: list[Path]) -> list[Path]:
    """Return paths of requirements.md files containing *term* (case-sensitive)."""
    hits: list[Path] = []
    for d in search_dirs:
        if not d.exists():
            continue
        try:
            result = subprocess.run(
                ["grep", "-rl", "--include=requirements.md", term, str(d)],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            continue
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.strip():
                    hits.append(Path(line.strip()))
    return hits


def _get_snippet(term: str, file_path: Path) -> str:
    """Return the first line of file_path matching term (≤120 chars)."""
    try:
        result = subprocess.run(
            ["grep", "-m", "1", term, str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return ""
    return result.stdout.strip()[:120] if result.returncode == 0 else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect cross-reference completeness gaps for a requirement."
    )
    parser.add_argument("requirement", help="Path to the target requirement's requirements.md")
    parser.add_argument(
        "--terms",
        nargs="+",
        metavar="TERM",
        help="Explicit search terms (2-4); derived automatically when omitted",
    )
    args = parser.parse_args(argv)

    req_path = Path(args.requirement).resolve()
    if not req_path.exists():
        print(f"Error: requirements.md not found: {req_path}", file=sys.stderr)
        return 1

    try:
        doc = read_frontmatter(req_path)
    except (OSError, FrontmatterError) as exc:
        print(f"Error: failed to parse {req_path}: {exc}", file=sys.stderr)
        return 1

    if not doc.has_frontmatter:
        print(f"Error: no YAML frontmatter in {req_path}", file=sys.stderr)
        return 1

    self_id = doc.metadata.get("id")
    if not self_id:
        print(f"Error: no 'id' field in frontmatter of {req_path}", file=sys.stderr)
        return 1

    excluded_ids = _get_excluded_ids(doc, doc.body, str(self_id))

    repo_root = Path(__file__).resolve().parent.parent.parent
    search_dirs = [
        repo_root / "requirements_tasks" / "functional",
        repo_root / "requirements_tasks" / "non-functional",
        repo_root / "requirements_tasks" / "process",
    ]

    if args.terms:
        terms = list(args.terms[:4])
    else:
        title = ""
        first_paragraph = ""
        for line in doc.body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# ") and not title:
                title = stripped[2:].strip()
            elif title and stripped and not stripped.startswith("#"):
                first_paragraph = stripped
                break
        candidate_terms = _derive_search_terms(title, first_paragraph, max_terms=_MAX_TERM_CANDIDATES)
        good: list[str] = []
        good_hit_count: int = 0
        for term in candidate_terms:
            n = len(_grep_files(term, search_dirs))
            if n <= _MAX_TERM_FREQ:
                good.append(term)
                good_hit_count += n
        use_good = len(good) >= 2 and good_hit_count >= _MIN_GOOD_HITS
        terms = good[:4] if use_good else candidate_terms[:4]

    # key: resolved path → {terms: set[str], snippet: str}
    candidates: dict[Path, dict[str, object]] = {}
    for term in terms:
        for hit_path in _grep_files(term, search_dirs):
            resolved = hit_path.resolve()
            if resolved == req_path:
                continue
            if resolved not in candidates:
                candidates[resolved] = {
                    "terms": set(),
                    "snippet": _get_snippet(term, resolved),
                }
            cast_terms: set[str] = candidates[resolved]["terms"]  # type: ignore[assignment]
            cast_terms.add(term)

    results: list[dict[str, object]] = []
    for file_path, data in candidates.items():
        req_id = _extract_req_id(file_path)
        if req_id is None or req_id in excluded_ids:
            continue
        try:
            rel_path = str(file_path.relative_to(repo_root))
        except ValueError:
            rel_path = str(file_path)
        matched: set[str] = data["terms"]  # type: ignore[assignment]
        results.append(
            {
                "id": req_id,
                "path": rel_path,
                "matched_terms": sorted(matched),
                "snippet": data["snippet"],
            }
        )

    results.sort(key=lambda x: str(x["id"]))
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
