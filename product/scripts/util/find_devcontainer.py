#!/usr/bin/env python3
"""
find_devcontainer.py — Walk up the directory tree to find a .devcontainer folder.

Usage:
    python scripts/find_devcontainer.py [start_path]

Returns:
    Prints the absolute path to the .devcontainer folder and exits 0 if found.
    Prints nothing and exits 1 if not found.

Use this before installing OS-level tools (e.g. python, node) to check whether
the environment is a VS Code Dev Container. If a .devcontainer folder is found,
the installation should also be recorded in devcontainer.json so it persists
across container rebuilds.

Output:
    Prints the absolute path of the nearest enclosing .devcontainer folder to stdout, or nothing (and exits 1) if none is found.
"""

# tier: C  # one-shot CLI helper; no in-tree Python imports

import sys
from pathlib import Path


def find_devcontainer(start: Path) -> Path | None:
    """Walk up from `start` and return the first .devcontainer directory found."""
    current = start.resolve()
    while True:
        candidate = current / ".devcontainer"
        if candidate.is_dir():
            return candidate
        parent = current.parent
        if parent == current:
            # Reached filesystem root without finding anything.
            return None
        current = parent


def main() -> None:
    start = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    result = find_devcontainer(start)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
