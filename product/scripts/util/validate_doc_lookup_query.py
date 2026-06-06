#!/usr/bin/env python3
"""Sanitize ctx7 query strings before forwarding to external AI services.

ctx7 forwards queries to third-party LLMs (OpenAI, Anthropic, Gemini) for
reranking and stores them anonymized for 30 days.  This script strips file
paths and path-like tokens so no private project structure leaks out.

Usage:
    python3 scripts/util/validate_doc_lookup_query.py "<query>"
    python3 scripts/util/validate_doc_lookup_query.py flutter ListView.builder "itemBuilder signature"

Output:
    Sanitized query string printed to stdout (exit 0).
    Error message printed to stderr (exit 1).

Exit codes:
    0  sanitized query printed to stdout
    1  query empty after sanitization, or no arguments given

tier: B
"""

import re
import sys

# ---------------------------------------------------------------------------
# Patterns that identify tokens to STRIP
# ---------------------------------------------------------------------------

# Anything containing a forward- or back-slash is a path fragment.
_HAS_PATH_SEP = re.compile(r"[/\\]")

# Tokens that start with / ~ . are path roots.
_IS_PATH_ROOT = re.compile(r"^[/~.]")


def sanitize(query: str) -> str:
    """Return *query* with path-like tokens removed.

    Kept tokens: library ids (``package:flutter``, ``dart:async``),
    dotted API paths (``ListView.builder.itemBuilder``), version strings,
    and plain words.  Stripped tokens: anything containing ``/`` or ``\\``
    and anything starting with ``/``, ``~``, or ``.``.
    """
    clean: list[str] = []
    for token in query.split():
        if _HAS_PATH_SEP.search(token):
            continue
        if _IS_PATH_ROOT.match(token):
            continue
        clean.append(token)
    return " ".join(clean)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(
            "Usage: validate_doc_lookup_query.py <query> [more words ...]",
            file=sys.stderr,
        )
        return 1

    raw = " ".join(args)
    clean = sanitize(raw)

    if not clean.strip():
        print(
            "Error: query is empty after sanitization — "
            "avoid embedding file paths in ctx7 queries.",
            file=sys.stderr,
        )
        return 1

    print(clean)
    return 0


if __name__ == "__main__":
    sys.exit(main())
