"""Shared ARB file parser consumed by check_canon.py and check_linguistic_complexity.py.

Provides ArbEntry and iter_arb_entries — the single source of ARB parsing logic
so both the canon-coherence check (REQ-PROC-049) and the G6 linguistic-complexity
check (REQ-PROC-046) read .arb files identically.

>>> import pathlib, tempfile, json, os
>>> tmp = tempfile.NamedTemporaryFile(suffix='_app_en.arb', mode='w', delete=False)
>>> _ = tmp.write(json.dumps({"greeting": "Hello {name}!", "@greeting": {"description": "Welcome greeting", "placeholders": {"name": {"type": "String"}}}, "title": "Mood Tracker", "@title": {"description": "App title"}}))
>>> tmp.close()
>>> entries = list(iter_arb_entries(pathlib.Path(tmp.name)))
>>> len(entries)
2
>>> entries[0].key
'greeting'
>>> entries[0].language_code
'en'
>>> entries[0].placeholders
{'name': {'type': 'String'}}
>>> os.unlink(tmp.name)
"""

# tier: C  # one-shot CLI gate script; no in-tree Python imports

from __future__ import annotations

import json
import pathlib
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


@dataclass
class ArbEntry:
    key: str
    value: str
    description: str
    placeholders: dict[str, dict[Any, Any]]
    language_code: str
    source_path: pathlib.Path


def _extract_language_code(path: pathlib.Path) -> str:
    """Extract locale code from ARB filename (e.g. app_en.arb → 'en', app_de.arb → 'de')."""
    m = re.search(r"_([a-z]{2}(?:_[A-Z]{2})?)\.arb$", path.name)
    return m.group(1) if m else ""


def iter_arb_entries(path: pathlib.Path) -> Iterable[ArbEntry]:
    """Yield one ArbEntry per translatable key in the given .arb file."""
    language_code = _extract_language_code(path)
    data: dict[Any, Any] = json.loads(path.read_text(encoding="utf-8"))
    for key, value in data.items():
        if key.startswith("@") or not isinstance(value, str):
            continue
        meta: dict[Any, Any] = data.get(f"@{key}", {})
        yield ArbEntry(
            key=key,
            value=value,
            description=meta.get("description", ""),
            placeholders=meta.get("placeholders", {}),
            language_code=language_code,
            source_path=path,
        )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
