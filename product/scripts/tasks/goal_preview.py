#!/usr/bin/env python3
"""
Prints the first N lines of a goal.md file, excluding the YAML frontmatter block.

Usage:
    python scripts/goal_preview.py path/to/goal.md
    python scripts/goal_preview.py path/to/goal.md --lines 20

Output:
    First N lines of the goal.md body (frontmatter excluded), printed to stdout.
"""

# tier: C  # one-shot CLI, no imported callers, minimal enforcement required

import argparse
import sys
from pathlib import Path


def extract_body(content: str) -> str:
    """Strip leading YAML frontmatter (--- ... ---) and return the body."""
    if content.startswith("\ufeff"):
        content = content[1:]

    if not content.startswith("---"):
        return content

    lines = content.split("\n")
    end_index = None
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        return content

    body_lines = lines[end_index + 1:]
    # Skip any blank lines immediately after the closing ---
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    return "\n".join(body_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print the first N lines of a goal.md body (frontmatter excluded)."
    )
    parser.add_argument("path", help="Path to the goal.md file")
    parser.add_argument(
        "--lines", type=int, default=20, help="Number of body lines to show (default: 20)"
    )
    args = parser.parse_args()

    goal_file = Path(args.path)
    if not goal_file.exists():
        print(f"Error: file not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    try:
        content = goal_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = goal_file.read_text(encoding="latin-1")

    body = extract_body(content)
    body_lines = body.split("\n")[: args.lines]
    print("\n".join(body_lines))


if __name__ == "__main__":
    main()
