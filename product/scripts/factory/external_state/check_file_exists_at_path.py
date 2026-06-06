#!/usr/bin/env python3
"""Verify a file exists, optionally with a minimum size (external-state vocabulary:
file_exists_at_path — also covers build_artifact_exists via --min-bytes).

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
from pathlib import Path


def file_ok(path: Path, min_bytes: int) -> bool:
    """Return True if *path* is a file of at least *min_bytes* bytes."""
    return path.is_file() and path.stat().st_size >= min_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--min-bytes", type=int, default=0)
    args = parser.parse_args()
    ok = file_ok(args.path, args.min_bytes)
    print(f"{'PASS' if ok else 'FAIL'} — {args.path} (min {args.min_bytes} bytes)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
