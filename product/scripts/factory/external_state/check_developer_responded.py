#!/usr/bin/env python3
"""Verify a developer answered a pending question (external-state vocabulary:
developer_responded). An answer.md still identical to TEMPLATE_answer.md counts as
unanswered — the orchestrator's own convention.

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
from pathlib import Path


def answered(answer: Path, template: Path | None) -> bool:
    """Return True if *answer* exists, is non-empty, and differs from *template* (if given)."""
    if not answer.is_file():
        return False
    text = answer.read_text(encoding="utf-8").strip()
    if not text:
        return False
    return template is None or text != template.read_text(encoding="utf-8").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answer", type=Path)
    parser.add_argument("--template", type=Path, default=None)
    args = parser.parse_args()
    ok = answered(args.answer, args.template)
    print(f"{'PASS' if ok else 'FAIL'} — {args.answer} {'answered' if ok else 'not answered'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
