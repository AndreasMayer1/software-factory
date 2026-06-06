#!/usr/bin/env python3
"""Canon-coherence audit script (REQ-PROC-049 AC-03, AC-05).

Walks requirements, ARB strings, translation_context (stub), and Dart
presentation files to detect drift from the concept canon.

Usage:
    python3 scripts/user_needs/check_canon.py [options]

Exit codes:
    0  pass — no drift candidates found
    1  fail — candidates found (for LLM review) or reference errors

Output:
    Prints one '<file>:<line>: <issue>' line per drift candidate or reference error to stdout, ending with a summary count.
"""

# tier: C  # one-shot CLI user-needs tool; no in-tree Python imports

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
CANON_PATH = REPO_ROOT / "requirements_user_needs" / "concept_canon" / "concept_canon.yaml"
USER_NEEDS_REGISTRY = REPO_ROOT / "requirements_user_needs" / "_meta" / "id_registry.md"
REQUIREMENTS_REGISTRY = REPO_ROOT / "requirements_tasks" / "_meta" / "id_registry.md"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "quality"))

GENERIC_VERBS = frozenset({"edit", "delete", "update", "add", "create", "remove", "save", "submit"})

_candidate_counter = 0


def _next_id() -> str:
    global _candidate_counter
    _candidate_counter += 1
    return f"C-{_candidate_counter:03d}"


# ── Data structures ──────────────────────────────────────────────────────────


@dataclass
class Candidate:
    id: str
    walker: str
    artefact: str
    line: int
    found_term: str
    matched_rule: str
    prefer: str
    canon_concept: str
    note: str
    context_snippet: str


@dataclass
class CanonConcept:
    id: str
    name_canonical: str
    status: str
    aliases_de: list[str]
    aliases_code: list[str]
    forbidden_synonyms: list[dict[Any, Any]]
    audience_variants: dict[Any, Any]
    provenance: dict[Any, Any]
    related: list[str]
    all_sources: list[dict[Any, Any]]


# ── Canon loading ────────────────────────────────────────────────────────────


def load_canon() -> tuple[list[CanonConcept], dict[Any, Any]]:
    if not CANON_PATH.exists():
        return [], {}
    try:
        raw: dict[Any, Any] = yaml.safe_load(CANON_PATH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"ERROR: Failed to parse {CANON_PATH}: {exc}", file=sys.stderr)
        sys.exit(2)

    concepts: list[CanonConcept] = []
    for entry in raw.get("concepts", []):
        aliases = entry.get("aliases", {}) or {}
        code_block = aliases.get("code", []) or []
        code_names = [
            c["identifier"] if isinstance(c, dict) else str(c)
            for c in code_block
        ]
        de_alias = aliases.get("de", "") or ""
        aliases_de = [de_alias] if de_alias else []

        all_sources: list[dict[Any, Any]] = []
        for lang_prov in (entry.get("provenance") or {}).values():
            if isinstance(lang_prov, dict):
                for src in lang_prov.get("sources", []) or []:
                    if isinstance(src, dict) and src.get("id"):
                        all_sources.append(src)

        concepts.append(CanonConcept(
            id=entry.get("id", ""),
            name_canonical=entry.get("name_canonical", ""),
            status=entry.get("status", "active"),
            aliases_de=aliases_de,
            aliases_code=code_names,
            forbidden_synonyms=entry.get("forbidden_synonyms", []) or [],
            audience_variants=entry.get("audience_variants", {}) or {},
            provenance=entry.get("provenance", {}) or {},
            related=entry.get("related", []) or [],
            all_sources=all_sources,
        ))
    return concepts, raw


def build_forbidden_index(
    concepts: list[CanonConcept],
) -> dict[tuple[str, str], CanonConcept]:
    """Map (lower_term, lang) → concept. lang='' means language-agnostic."""
    index: dict[tuple[str, str], CanonConcept] = {}
    for concept in concepts:
        if concept.status != "active":
            continue
        for syn in concept.forbidden_synonyms:
            term = (syn.get("term") or "").strip()
            lang = syn.get("lang") or ""
            if term:
                index[(term.lower(), lang)] = concept
    return index


def get_preferred_term(concept: CanonConcept, lang: str) -> str:
    """Return canonical or audience-variant name for the given lang."""
    for _audience, variant in (concept.audience_variants or {}).items():
        if isinstance(variant, dict) and variant.get(lang):
            return cast("str", variant[lang])
    if lang == "de" and concept.aliases_de:
        return concept.aliases_de[0]
    return concept.name_canonical


def get_synonym_note(concept: CanonConcept, term_lower: str) -> str:
    for syn in concept.forbidden_synonyms:
        if (syn.get("term") or "").lower() == term_lower:
            return syn.get("note") or ""
    return ""


# ── Text utilities ───────────────────────────────────────────────────────────


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def find_term_occurrences(term: str, text: str) -> list[tuple[int, str]]:
    """Return (1-based line_number, stripped_line) for each word-boundary match."""
    pat = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
    results: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if pat.search(line):
            results.append((lineno, line.strip()))
    return results


# Simple Dart string-literal extractor (single + double quoted, non-greedy).
# Handles common cases; intentionally approximate for V1.
_DART_STR_PAT = re.compile(
    r"'''(.*?)'''|\"\"\"(.*?)\"\"\"|'([^'\\]*(?:\\.[^'\\]*)*)'|\"([^\"\\]*(?:\\.[^\"\\]*)*)\"",
    re.DOTALL,
)


def extract_dart_strings(text: str) -> list[tuple[int, str]]:
    """Return (1-based line_number, value) for user-visible string literals."""
    line_starts: list[int] = [0]
    for m in re.finditer(r"\n", text):
        line_starts.append(m.end())

    results: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()

    for m in _DART_STR_PAT.finditer(text):
        value: str = (m.group(1) or m.group(2) or m.group(3) or m.group(4) or "").strip()
        if len(value) < 3:
            continue
        # Keep only strings that look user-facing (contain space or mixed case)
        if " " not in value and not any(c.isupper() for c in value):
            continue
        pos = m.start()
        lineno = next(
            (i for i, s in enumerate(line_starts, 1) if s > pos),
            len(line_starts),
        ) - 1
        key = (lineno, value[:80])
        if key not in seen:
            seen.add(key)
            results.append((lineno, value))
    return results


# ── Walker 1: requirements markdown ─────────────────────────────────────────


def walk_requirements(forbidden_index: dict[tuple[str, str], CanonConcept]) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[tuple[str, int, str]] = set()

    req_files = list((REPO_ROOT / "requirements_tasks").rglob("requirements.md"))
    for req_file in req_files:
        try:
            body = strip_frontmatter(req_file.read_text(encoding="utf-8"))
        except OSError:
            continue
        rel = str(req_file.relative_to(REPO_ROOT))

        for (term, lang), concept in forbidden_index.items():
            if lang and lang != "en":
                # Requirements files are English; skip DE-only synonyms
                continue
            for lineno, snippet in find_term_occurrences(term, body):
                dedup = (rel, lineno, term)
                if dedup in seen:
                    continue
                seen.add(dedup)
                candidates.append(Candidate(
                    id=_next_id(),
                    walker="requirements",
                    artefact=rel,
                    line=lineno,
                    found_term=term,
                    matched_rule="forbidden_synonym",
                    prefer=get_preferred_term(concept, "en"),
                    canon_concept=concept.id,
                    note=get_synonym_note(concept, term),
                    context_snippet=snippet[:120],
                ))
    return candidates


# ── Walker 2: ARB strings ────────────────────────────────────────────────────


def walk_arb(forbidden_index: dict[tuple[str, str], CanonConcept]) -> list[Candidate]:
    try:
        from _arb_parser import (  # type: ignore[import-not-found]  # sibling import via sys.path manipulation in walker setup; mypy cannot resolve
            iter_arb_entries,
        )
    except ImportError:
        print("WARNING: _arb_parser not found in scripts/quality/; skipping ARB walker.", file=sys.stderr)
        return []

    candidates: list[Candidate] = []
    seen: set[tuple[str, str, str]] = set()

    for arb_file in (REPO_ROOT / "lib").rglob("*.arb"):
        try:
            entries = list(iter_arb_entries(arb_file))
        except Exception as exc:
            print(f"WARNING: Could not parse {arb_file}: {exc}", file=sys.stderr)
            continue
        rel = str(arb_file.relative_to(REPO_ROOT))

        for entry in entries:
            lang = entry.language_code or ""
            for (term, syn_lang), concept in forbidden_index.items():
                if syn_lang and syn_lang != lang:
                    continue
                pat = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
                if pat.search(entry.value):
                    dedup = (rel, entry.key, term)
                    if dedup in seen:
                        continue
                    seen.add(dedup)
                    candidates.append(Candidate(
                        id=_next_id(),
                        walker="arb",
                        artefact=rel,
                        line=0,
                        found_term=term,
                        matched_rule="forbidden_synonym",
                        prefer=get_preferred_term(concept, lang or "en"),
                        canon_concept=concept.id,
                        note=get_synonym_note(concept, term),
                        context_snippet=f"key={entry.key}: {entry.value[:80]}",
                    ))
    return candidates


# ── Walker 3: translation_context (stub) ─────────────────────────────────────


def walk_translation_context(*, code_coverage: bool = False) -> list[Candidate]:
    if code_coverage:
        print("[translation_context walker] deferred — REQ-NFUNC-013 AC-08 not yet implemented")
    return []


# ── Walker 4: Dart presentation files ───────────────────────────────────────


def walk_dart(forbidden_index: dict[tuple[str, str], CanonConcept]) -> list[Candidate]:
    candidates: list[Candidate] = []
    seen: set[tuple[str, int, str]] = set()

    features_root = REPO_ROOT / "lib" / "features"
    dart_files = [
        f for f in features_root.rglob("*.dart")
        if "presentation" in f.parts
    ]

    for dart_file in dart_files:
        try:
            text = dart_file.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(dart_file.relative_to(REPO_ROOT))
        strings = extract_dart_strings(text)

        for lineno, value in strings:
            for (term, _lang), concept in forbidden_index.items():
                pat = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
                if pat.search(value):
                    dedup = (rel, lineno, term)
                    if dedup in seen:
                        continue
                    seen.add(dedup)
                    lang_guess = "de" if re.search(r"[äöüÄÖÜß]", value) else "en"
                    candidates.append(Candidate(
                        id=_next_id(),
                        walker="dart",
                        artefact=rel,
                        line=lineno,
                        found_term=term,
                        matched_rule="forbidden_synonym",
                        prefer=get_preferred_term(concept, lang_guess),
                        canon_concept=concept.id,
                        note=get_synonym_note(concept, term),
                        context_snippet=value[:120],
                    ))
    return candidates


# ── AC-03: generic-verb precision check ──────────────────────────────────────


def check_verb_precision() -> list[Candidate]:
    """Detect generic verbs in user-facing ARB and Dart strings (AC-03)."""
    try:
        from _arb_parser import iter_arb_entries
        arb_ok = True
    except ImportError:
        arb_ok = False

    # Collect all user-facing text with provenance
    texts: list[tuple[str, str, int]] = []  # (value, artefact_rel, line)

    if arb_ok:
        for arb_file in (REPO_ROOT / "lib").rglob("*.arb"):
            try:
                for entry in iter_arb_entries(arb_file):
                    texts.append((entry.value, str(arb_file.relative_to(REPO_ROOT)), 0))
            except Exception:
                pass

    features_root = REPO_ROOT / "lib" / "features"
    for dart_file in features_root.rglob("*.dart"):
        if "presentation" not in dart_file.parts:
            continue
        try:
            dart_text = dart_file.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(dart_file.relative_to(REPO_ROOT))
        for lineno, val in extract_dart_strings(dart_text):
            texts.append((val, rel, lineno))

    # Group occurrences by verb
    verb_hits: dict[str, list[tuple[str, str, int]]] = {v: [] for v in GENERIC_VERBS}
    for value, artefact, lineno in texts:
        for verb in GENERIC_VERBS:
            if re.search(r"\b" + verb + r"\b", value, re.IGNORECASE):
                verb_hits[verb].append((value, artefact, lineno))

    candidates: list[Candidate] = []
    seen: set[tuple[str, str, int]] = set()
    for verb, hits in verb_hits.items():
        if len(hits) < 2:
            # Single occurrence — no divergence risk; skip
            continue
        for value, artefact, lineno in hits:
            dedup = (verb, artefact, lineno)
            if dedup in seen:
                continue
            seen.add(dedup)
            candidates.append(Candidate(
                id=_next_id(),
                walker="verb_precision",
                artefact=artefact,
                line=lineno,
                found_term=verb,
                matched_rule="generic_verb",
                prefer="(review: name each operation if downstream consequences differ)",
                canon_concept="",
                note=(
                    f"Generic verb '{verb}' appears in {len(hits)} place(s). "
                    "Verify AC-03 condition (b): if consequences differ by object, "
                    "decompose into separately named operations."
                ),
                context_snippet=value[:120],
            ))
    return candidates


# ── --validate-references ────────────────────────────────────────────────────


_ID_PATTERN = re.compile(
    r"\b(CONCEPT|PERSONA|SCEN|FLOW|REQ|TASK|VTR)-[\w-]+\b"
)


def load_known_ids() -> set[str]:
    known: set[str] = set()
    for registry in [USER_NEEDS_REGISTRY, REQUIREMENTS_REGISTRY]:
        if registry.exists():
            for m in _ID_PATTERN.finditer(registry.read_text(encoding="utf-8")):
                known.add(m.group(0))
    # Also treat all CONCEPT-* IDs in the canon itself as known
    if CANON_PATH.exists():
        for m in _ID_PATTERN.finditer(CANON_PATH.read_text(encoding="utf-8")):
            if m.group(0).startswith("CONCEPT-"):
                known.add(m.group(0))
    return known


def validate_references(concepts: list[CanonConcept]) -> list[str]:
    known = load_known_ids()
    errors: list[str] = []
    for concept in concepts:
        for src in concept.all_sources:
            ref_id = src.get("id", "")
            if ref_id and ref_id not in known:
                errors.append(f"{concept.id}: unknown source ID '{ref_id}'")
        for rel_id in concept.related:
            if rel_id and not rel_id.startswith("CONCEPT-"):
                errors.append(f"{concept.id}: related '{rel_id}' is not a CONCEPT-* ID")
    return errors


# ── --code-coverage ──────────────────────────────────────────────────────────


def code_coverage_report(concepts: list[CanonConcept]) -> None:
    active = [c for c in concepts if c.status == "active"]
    total = len(active)
    with_alias = [c for c in active if c.aliases_code]
    without_alias = [c for c in active if not c.aliases_code]
    pct = (len(with_alias) / total * 100) if total else 0.0

    print("=== Code Coverage Report ===")
    print(f"Active concepts : {total}")
    print(f"With code alias : {len(with_alias)} ({pct:.0f}%)")
    print(f"Without alias   : {len(without_alias)}")

    if with_alias:
        print("\nConcepts with code alias:")
        for c in with_alias:
            print(f"  {c.id}: {c.name_canonical} → {', '.join(c.aliases_code)}")

    if without_alias:
        print("\nConcepts without code alias:")
        for c in without_alias:
            print(f"  {c.id}: {c.name_canonical}")

    # Unacknowledged divergences: forbidden synonym appears in a Dart filename
    # but is NOT listed in aliases.code for the concept that forbids it
    forbidden_index = build_forbidden_index(concepts)
    if not forbidden_index:
        walk_translation_context(code_coverage=True)
        return

    unacknowledged: list[tuple[str, str, str]] = []
    for dart_file in (REPO_ROOT / "lib" / "features").rglob("*.dart"):
        stem = dart_file.stem
        for (term, _lang), concept in forbidden_index.items():
            if (
                re.search(r"\b" + re.escape(term) + r"\b", stem, re.IGNORECASE)
                and term.lower() not in [a.lower() for a in concept.aliases_code]
            ):
                unacknowledged.append((
                    str(dart_file.relative_to(REPO_ROOT)), term, concept.id,
                ))
    if unacknowledged:
        print("\nUnacknowledged divergences (forbidden synonym in filename, missing from aliases.code):")
        for path, term, concept_id in unacknowledged:
            print(f"  {path}: '{term}' (see {concept_id})")

    walk_translation_context(code_coverage=True)


# ── Provenance summary ───────────────────────────────────────────────────────


def provenance_summary(concepts: list[CanonConcept]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for concept in concepts:
        if concept.status != "active":
            continue
        for lang, prov in concept.provenance.items():
            if isinstance(prov, dict):
                level = prov.get("level") or "unknown"
                summary.setdefault(lang, {})
                summary[lang][level] = summary[lang].get(level, 0) + 1
    return summary


# ── Output ───────────────────────────────────────────────────────────────────


def _now_str() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def print_human(
    candidates: list[Candidate],
    ref_errors: list[str],
    prov: dict[Any, Any],
) -> None:
    print(f"\n{'='*60}")
    print(f"Canon Coherence Audit — {_now_str()}")
    print(f"{'='*60}")

    if prov:
        print("\nProvenance coverage:")
        for lang in sorted(prov):
            print(f"  {lang}:")
            for level, count in sorted(prov[lang].items()):
                print(f"    {level:<20} {count}")

    if not candidates and not ref_errors:
        print("\n✓ No drift candidates found. Canon is coherent.")
        return

    print(f"\nDrift candidates: {len(candidates)}")
    for c in candidates:
        loc = f":{c.line}" if c.line else ""
        print(f"\n  [{c.id}] {c.walker} — {c.artefact}{loc}")
        print(f"    Found    : '{c.found_term}'  rule={c.matched_rule}")
        if c.prefer and "review:" not in c.prefer:
            print(f"    Prefer   : '{c.prefer}' ({c.canon_concept})")
        if c.note:
            print(f"    Note     : {c.note}")
        if c.context_snippet:
            print(f"    Snippet  : {c.context_snippet}")

    if ref_errors:
        print(f"\nReference errors: {len(ref_errors)}")
        for err in ref_errors:
            print(f"  ✗ {err}")


def print_json(
    candidates: list[Candidate],
    ref_errors: list[str],
    prov: dict[Any, Any],
) -> None:
    out = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "summary": {
            "candidates": len(candidates),
            "reference_errors": len(ref_errors),
        },
        "provenance": prov,
        "candidates": [
            {
                "id": c.id,
                "walker": c.walker,
                "artefact": c.artefact,
                "line": c.line,
                "found_term": c.found_term,
                "matched_rule": c.matched_rule,
                "prefer": c.prefer,
                "canon_concept": c.canon_concept,
                "note": c.note,
                "context_snippet": c.context_snippet,
            }
            for c in candidates
        ],
        "reference_errors": ref_errors,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect drift between concept canon and requirements/ARB/Dart artefacts.",
    )
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output.")
    parser.add_argument(
        "--validate-references",
        action="store_true",
        help="Resolve source IDs (CONCEPT-*, PERSONA-*, SCEN-*, FLOW-*, REQ-*) against registries.",
    )
    parser.add_argument(
        "--code-coverage",
        action="store_true",
        help="Report code-alias coverage and unacknowledged divergences.",
    )
    parser.add_argument(
        "--concept",
        metavar="CONCEPT_ID",
        help="Spot-check: exit 0 if CONCEPT_ID exists in canon, 1 if absent.",
    )
    args = parser.parse_args()

    concepts, _raw = load_canon()

    # Spot-check mode (used by ux-write-canon-concept)
    if args.concept:
        known = {c.id for c in concepts}
        if args.concept in known:
            print(f"✓ {args.concept} found in canon.")
            return 0
        print(f"✗ {args.concept} NOT found in canon.")
        return 1

    # Code-coverage report (printed before drift section)
    if args.code_coverage:
        code_coverage_report(concepts)
        print()

    # Empty canon — graceful no-op
    if not concepts:
        empty_out = {
            "summary": {"candidates": 0, "reference_errors": 0},
            "candidates": [],
            "reference_errors": [],
        }
        if args.json:
            print(json.dumps(empty_out, indent=2))
        else:
            print("Canon is empty — no drift check performed.")
        return 0

    forbidden_index = build_forbidden_index(concepts)

    candidates: list[Candidate] = []
    candidates.extend(walk_requirements(forbidden_index))
    candidates.extend(walk_arb(forbidden_index))
    walk_translation_context()  # stub — always empty; runs for side-effects in --code-coverage
    candidates.extend(walk_dart(forbidden_index))
    candidates.extend(check_verb_precision())

    ref_errors: list[str] = []
    if args.validate_references:
        ref_errors = validate_references(concepts)

    prov = provenance_summary(concepts)

    if args.json:
        print_json(candidates, ref_errors, prov)
    else:
        print_human(candidates, ref_errors, prov)

    return 1 if (candidates or ref_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
