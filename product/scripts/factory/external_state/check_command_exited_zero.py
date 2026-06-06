#!/usr/bin/env python3
"""Verify a bash command exits 0 (external-state vocabulary: command_exited_zero).

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
import subprocess


def exit_code(command: list[str]) -> int:
    """Run *command* and return its process exit code."""
    return subprocess.run(command, capture_output=True, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command + args to run")
    args = parser.parse_args()
    if not args.command:
        print("FAIL — no command given")
        return 1
    code = exit_code(args.command)
    print(f"{'PASS' if code == 0 else 'FAIL'} — `{' '.join(args.command)}` exited {code}")
    return 0 if code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
