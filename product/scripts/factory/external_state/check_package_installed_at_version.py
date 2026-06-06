#!/usr/bin/env python3
"""Verify an installed tool reports an expected version (external-state vocabulary:
package_installed_at_version). Runs `<tool> --version` and substring-matches.

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
import subprocess


def version_matches(output: str, expected: str) -> bool:
    """Return True if *expected* appears in the tool's --version *output*."""
    return expected in output


def version_output(tool: str, flag: str) -> str:
    """Return combined stdout+stderr of `<tool> <flag>` (empty string if the tool is absent)."""
    try:
        proc = subprocess.run([tool, flag], capture_output=True, text=True, check=False)
    except (FileNotFoundError, OSError):
        return ""
    return proc.stdout + proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool")
    parser.add_argument("expected", help="version substring expected in --version output")
    parser.add_argument("--flag", default="--version")
    args = parser.parse_args()
    ok = version_matches(version_output(args.tool, args.flag), args.expected)
    print(f"{'PASS' if ok else 'FAIL'} — {args.tool} {args.flag} contains '{args.expected}'")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
