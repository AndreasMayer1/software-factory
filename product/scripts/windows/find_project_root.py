"""Resolution helper for Windows scripts — Python equivalent of find_project_root.ps1.

Exports ``find_project_root`` with the same 3-level precedence used by the
PowerShell helper:

1. Explicit *explicit* argument passed by the caller.
2. ``windows_scripts.config.json`` next to **this file** (the installed
   out-of-repo location written by ``sync_windows_scripts.ps1``).
3. Auto-derive from this file's location (in-repo layout:
   ``scripts/windows/ → scripts/ → <project root>``).

The function returns a ``pathlib.Path``; it raises ``FileNotFoundError`` when
no candidate resolves to an existing directory.
"""

# tier: C  # Windows-host resolution helper; no in-tree Python imports

from __future__ import annotations

import json
import sys
from pathlib import Path


def find_project_root(explicit: str | None = None) -> Path:
    """Resolve the project root with 3-level precedence.

    Args:
        explicit: If given, used as-is (precedence 1).

    Returns:
        Resolved project root as an absolute ``Path``.

    Raises:
        FileNotFoundError: When none of the three levels yields an existing
            directory.
    """
    # Precedence 1: explicit argument
    if explicit:
        resolved = Path(explicit)
        if not resolved.is_dir():
            msg = f"find_project_root: explicit path does not exist: {explicit}"
            raise FileNotFoundError(msg)
        return resolved.resolve()

    # Precedence 2: windows_scripts.config.json next to this file
    config_path = Path(__file__).parent / "windows_scripts.config.json"
    if config_path.is_file():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        project_root = data.get("project_root")
        if project_root:
            resolved = Path(project_root)
            if not resolved.is_dir():
                msg = f"find_project_root: config project_root does not exist: {project_root}"
                raise FileNotFoundError(msg)
            return resolved.resolve()

    # Precedence 3: auto-derive from script location
    # scripts/windows/ -> scripts/ -> <project root>
    derived = Path(__file__).resolve().parent.parent.parent
    if derived.is_dir():
        return derived

    msg = "find_project_root: cannot determine project root. Pass explicit path."
    raise FileNotFoundError(msg)


if __name__ == "__main__":
    try:
        root = find_project_root(sys.argv[1] if len(sys.argv) > 1 else None)
        sys.stdout.write(f"{root}\n")
    except FileNotFoundError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)
