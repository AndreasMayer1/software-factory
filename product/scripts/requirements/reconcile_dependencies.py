#!/usr/bin/env python3
"""
Reconcile dependency metadata across all requirements.md files.

Ensures after ↔ blocks are mutually consistent:
  If A.after contains B → B.blocks must contain A.

Also detects circular dependencies (fails with report if any found).

Usage:
    python scripts/reconcile_dependencies.py           # apply changes
    python scripts/reconcile_dependencies.py --dry-run # report only, no writes

Output:
    Prints a per-requirement change summary to stdout (and, by default, writes 'blocks:' updates into requirements.md files). --dry-run reports only, no writes. Cycle detections are reported with the offending chain.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import io
import re
import sys
from pathlib import Path
from typing import Any, Optional

# Ensure UTF-8 output on Windows (avoids cp1252 encode errors for box-drawing chars)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT = Path(__file__).parent.parent.parent / "requirements_tasks"


# ---------------------------------------------------------------------------
# Frontmatter parsing (same dual-strategy as generate_id_registry.py)
# ---------------------------------------------------------------------------

def parse_frontmatter_text(content: str) -> tuple[Optional[str], Optional[dict[Any, Any]]]:
    """Return (yaml_text, parsed_dict) or (None, None) if no frontmatter."""
    if content.startswith('\ufeff'):
        content = content[1:]
    if not content.startswith('---'):
        return None, None

    lines = content.split('\n')
    yaml_lines: list[str] = []
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if line.strip() == '---':
            break
        yaml_lines.append(line)

    if not yaml_lines:
        return None, None

    yaml_text = '\n'.join(yaml_lines)
    if HAS_YAML:
        try:
            return yaml_text, yaml.safe_load(yaml_text)
        except Exception:
            pass
    return yaml_text, None


def extract_id_list(value: Any) -> list[str]:
    """Extract clean REQ-* IDs from a YAML field (handles lists, strings, None)."""
    if value is None:
        return []
    if isinstance(value, list):
        result = []
        for item in value:
            if item is None:
                continue
            s = str(item).split('#')[0].strip()
            if s:
                result.append(s)
        return result
    if isinstance(value, str):
        return [v.strip() for v in value.split(',') if v.strip()]
    return []


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------

def detect_cycle(
    node: str,
    graph: dict[str, list[str]],
    visited: set[str],
    in_stack: set[str],
    path: list[str],
) -> Optional[list[str]]:
    visited.add(node)
    in_stack.add(node)
    path.append(node)

    for neighbour in graph.get(node, []):
        if neighbour not in graph:
            continue
        if neighbour not in visited:
            result = detect_cycle(neighbour, graph, visited, in_stack, path)
            if result is not None:
                return result
        elif neighbour in in_stack:
            # Found cycle — return the cycle portion
            idx = path.index(neighbour)
            return path[idx:]

    path.pop()
    in_stack.discard(node)
    return None


# ---------------------------------------------------------------------------
# Safe list append in raw YAML text (preserves inline comments)
# ---------------------------------------------------------------------------

def append_to_yaml_list(content: str, field: str, new_id: str) -> str:
    """
    Add new_id to a YAML list field inside frontmatter without destroying comments.
    Handles three cases: missing field, `field: []`, and `field:` with existing items.
    """
    # Locate frontmatter boundaries in raw content
    bom = ''
    if content.startswith('\ufeff'):
        bom = '\ufeff'
        content = content[1:]

    if not content.startswith('---'):
        return bom + content

    # Find end of frontmatter
    second_sep = content.find('\n---', 3)
    if second_sep == -1:
        return bom + content

    fm = content[4:second_sep]        # text between the two `---` delimiters
    rest = content[second_sep:]       # from closing `---` onwards

    # Case 1: field is absent → append before closing ---
    field_re = re.compile(rf'^{re.escape(field)}\s*:', re.MULTILINE)
    if not field_re.search(fm):
        new_block = f'\n{field}:\n  - {new_id}'
        return bom + '---\n' + fm + new_block + rest

    # Case 2: inline empty list  →  field: []
    inline_re = re.compile(rf'^({re.escape(field)}\s*:)\s*\[\s*\]\s*$', re.MULTILINE)
    m = inline_re.search(fm)
    if m:
        replacement = f'{m.group(1)}\n  - {new_id}'
        fm = fm[:m.start()] + replacement + fm[m.end():]
        return bom + '---\n' + fm + rest

    # Case 3: multi-line list  →  find insertion point after last list item
    # Locate the field line
    field_m = field_re.search(fm)
    assert field_m is not None, "field_re must match; caller handles the no-match case earlier"
    field_line_end = fm.index('\n', field_m.end()) if '\n' in fm[field_m.end():] else len(fm)

    # Walk subsequent lines to find the last list item
    lines_after = fm[field_line_end + 1:].split('\n')
    insert_offset = field_line_end + 1
    last_item_end = insert_offset  # where to insert the new entry

    for line in lines_after:
        stripped = line.lstrip()
        if stripped.startswith('- ') or stripped.startswith('-\t'):
            last_item_end = insert_offset + len(line) + 1  # +1 for the \n
        elif line == '' or line.startswith(' ') or line.startswith('\t'):
            # Empty or indented continuation — keep scanning
            pass
        else:
            break  # non-indented line = end of list
        insert_offset += len(line) + 1

    new_entry = f'  - {new_id}\n'
    fm = fm[:last_item_end] + new_entry + fm[last_item_end:]
    return bom + '---\n' + fm + rest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    dry_run = '--dry-run' in sys.argv

    print(f"Scanning {ROOT} ...")
    req_files = sorted(ROOT.rglob('requirements.md'))
    print(f"Found {len(req_files)} requirements.md files\n")

    # Build registry: id → {path, after, blocks}
    registry: dict[str, dict[Any, Any]] = {}

    for req_file in req_files:
        content = req_file.read_text(encoding='utf-8')
        _, fm = parse_frontmatter_text(content)
        if not fm:
            print(f"  SKIP (no frontmatter): {req_file.relative_to(ROOT.parent)}")
            continue

        req_id = fm.get('id')
        if not req_id:
            print(f"  SKIP (no id):          {req_file.relative_to(ROOT.parent)}")
            continue

        if req_id in registry:
            print(f"  WARN (duplicate id {req_id}): {req_file.relative_to(ROOT.parent)}")
            continue

        registry[req_id] = {
            'path': req_file,
            'after': extract_id_list(fm.get('after')),
            'blocks': extract_id_list(fm.get('blocks')),
            'status': fm.get('status', ''),
        }

    print(f"Loaded {len(registry)} requirements with valid IDs\n")

    # --- Cycle detection ---
    print("Checking for circular dependencies ...")
    graph: dict[str, list[str]] = {
        rid: [d for d in data['after'] if d in registry]
        for rid, data in registry.items()
    }

    cycles: list[list[str]] = []
    visited: set[str] = set()
    for rid in registry:
        if rid not in visited:
            cycle = detect_cycle(rid, graph, visited, set(), [])
            if cycle:
                cycles.append(cycle)

    if cycles:
        print("\n❌  CIRCULAR DEPENDENCIES DETECTED — fix these before proceeding:\n")
        for cycle in cycles:
            print(f"   {' → '.join(cycle)} → {cycle[0]}")
        return 1
    print("✓  No circular dependencies\n")

    # --- Reciprocity check & fix ---
    print("Reconciling after ↔ blocks ...")
    changes: dict[str, list[str]] = {}  # req_id → list of IDs to append to blocks

    for rid, data in registry.items():
        for dep_id in data['after']:
            if dep_id not in registry:
                print(f"  WARN: {rid}.after references unknown ID: {dep_id}")
                continue
            if rid not in registry[dep_id]['blocks']:
                changes.setdefault(dep_id, [])
                if rid not in changes[dep_id]:
                    changes[dep_id].append(rid)
                    print(f"  + {dep_id}.blocks ← {rid}")

    if not changes:
        print("✓  All after ↔ blocks pairs are already consistent\n")
    else:
        print(f"\n{len(changes)} file(s) need blocks updates")
        if dry_run:
            print("  (dry-run: no files written)")
        else:
            for req_id, new_ids in changes.items():
                file_path: Path = registry[req_id]['path']
                content = file_path.read_text(encoding='utf-8')
                for new_id in new_ids:
                    content = append_to_yaml_list(content, 'blocks', new_id)
                file_path.write_text(content, encoding='utf-8')
                print(f"  ✓  Updated {file_path.relative_to(ROOT.parent)}")
        print()

    print("Reconciliation complete.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
