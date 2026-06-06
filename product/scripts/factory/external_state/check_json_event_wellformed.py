#!/usr/bin/env python3
"""Verify a JSON event file parses and carries required keys (external-state
vocabulary: json_event_wellformed). Covers the optimize-event channel
(.factory/optimize/events/*.json) and any future structured inbound event.

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
import json
from pathlib import Path


def event_ok(path: Path, required_keys: list[str]) -> tuple[bool, str]:
    """Return (ok, message): the file parses as a JSON object and has every required key."""
    if not path.is_file():
        return False, f"{path} not found"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc.msg}"
    if not isinstance(data, dict):
        return False, "top-level JSON value is not an object"
    missing = [key for key in required_keys if key not in data]
    return (not missing, "well-formed" if not missing else f"missing keys: {', '.join(missing)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--require", nargs="*", default=[], help="required top-level keys")
    args = parser.parse_args()
    ok, message = event_ok(args.path, args.require)
    print(f"{'PASS' if ok else 'FAIL'} — {message}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
