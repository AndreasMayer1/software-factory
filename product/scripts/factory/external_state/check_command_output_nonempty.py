#!/usr/bin/env python3
"""Verify a command produces non-empty stdout (external-state vocabulary:
command_output_nonempty). Covers structured-doc fetches such as `ctx7 docs ...`.

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
import subprocess


def stdout_nonempty(command: list[str]) -> bool:
    """Run *command* and return True if its stdout has non-whitespace content."""
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    return bool(proc.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command + args to run")
    args = parser.parse_args()
    if not args.command:
        print("FAIL — no command given")
        return 1
    ok = stdout_nonempty(args.command)
    print(f"{'PASS' if ok else 'FAIL'} — `{' '.join(args.command)}` stdout {'has' if ok else 'no'} content")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
