#!/usr/bin/env python3
"""
Auto-generate ID registry files by scanning YAML frontmatter.
Single-pass version: walks each directory tree exactly once.

Generates:
- requirements_tasks/_meta/id_registry.md   (REQ-* and TASK-* IDs)
- requirements_user_needs/_meta/id_registry.md  (PERSONA-*, SCEN-*, FLOW-* IDs)

Usage:
    python scripts/generate_id_registry_v2.py --requirements
    python scripts/generate_id_registry_v2.py --user-needs
    python scripts/generate_id_registry_v2.py --all

Output:
    Writes id_registry.md file(s) under the relevant _meta/ folders.
    Prints a one-line summary per generated file (path + ID count) to
    stdout; errors go to stderr.
"""

# tier: C  # one-shot CLI artifact generator; no in-tree Python imports

import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional

# Why: this script runs both as `python3 scripts/artifacts/generate_id_registry.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    _parse_yaml_block,
    _split_frontmatter,
)

VTR_BLOCK_PATTERN = re.compile(r'<!--\s*vcd-record\s*\n(.*?)\n\s*-->', re.DOTALL)


# ---------------------------------------------------------------------------
# YAML Frontmatter Parsing \u2014 delegates to the central helper.
# Why: REQ-PROC-051 AC-08 requires a single frontmatter parser (G4 gate).
# ---------------------------------------------------------------------------

def parse_yaml_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Parse YAML frontmatter from a content string.

    Returns dict on success (so existing downstream code keeps working),
    None when the document has no frontmatter or the frontmatter is empty.
    """
    # Strip UTF-8 BOM (some Windows editors add it; central helper does not).
    if content.startswith('﻿'):
        content = content[1:]
    # Use _split_frontmatter + _parse_yaml_block directly to bypass the
    # read_frontmatter() path-vs-text heuristic — callers here always pass
    # in-memory document content, never paths.
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml:
        return None
    try:
        metadata = _parse_yaml_block(raw_yaml)
    except Exception:
        # Why: ruamel raises DuplicateKeyError on repeated mapping keys,
        # while the legacy hand-rolled parser silently accepted the last
        # value. Catching broadly preserves the legacy "skip bad files,
        # do not abort the whole scan" behaviour.
        return None
    if not metadata:
        return None
    return dict(metadata)


# ---------------------------------------------------------------------------
# Name Extraction (unchanged from v1)
# ---------------------------------------------------------------------------

def extract_requirement_name(content: str, folder_path: Path) -> str:
    meta = parse_yaml_frontmatter(content)
    if meta and meta.get('name') and not meta['name'].startswith('['):
        return str(meta['name'])
    match = re.search(r'^# Requirement:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return folder_path.name.replace('_', ' ').title()


def extract_user_needs_name(meta: dict[str, Any], folder_path: Path) -> str:
    name = meta.get('name', '')
    if name and not name.startswith('['):
        return str(name)
    return folder_path.name.replace('_', ' ').title()


# ---------------------------------------------------------------------------
# Filesystem helpers: use native find/grep instead of Python os.walk
#
# On a WSL2-mounted Windows (NTFS) filesystem Python's os.walk takes ~27s to
# traverse 1,100+ files, but native find/grep do the same in 8-14s because
# they avoid Python object-creation overhead and use kernel readdir directly.
# Running find and grep in parallel pins total traversal time to max(8s, 14s).
# ---------------------------------------------------------------------------

def _launch_find(roots: list[str], names: list[str]) -> 'subprocess.Popen[str]':
    """Launch `find` for specific filenames as a background process."""
    name_args: list[str] = []
    for i, name in enumerate(names):
        if i > 0:
            name_args.append('-o')
        name_args += ['-name', name]
    return subprocess.Popen(
        ['find', *roots, '(', *name_args, ')'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )


def _launch_grep(pattern: str, roots: list[str]) -> 'subprocess.Popen[str]':
    """Launch `grep -rl` as a background process."""
    return subprocess.Popen(
        ['grep', '-rl', pattern, *roots],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )


def _collect(proc: 'subprocess.Popen[str]') -> list[str]:
    """Wait for a Popen process and return its stdout lines."""
    stdout, _ = proc.communicate()
    return [p.strip() for p in stdout.splitlines() if p.strip()]


def _find_named_files(roots: list[str], names: list[str]) -> list[str]:
    """Use `find` to locate files with specific names under the given roots."""
    if not roots or not names:
        return []
    try:
        return _collect(_launch_find(roots, names))
    except FileNotFoundError:
        found = []
        name_set = set(names)
        for root in roots:
            for dirpath, _, filenames in os.walk(root):
                for fn in filenames:
                    if fn in name_set:
                        found.append(os.path.join(dirpath, fn))
        return found


def _grep_files(pattern: str, roots: list[str]) -> list[str]:
    """Use `grep -rl` to find files containing pattern."""
    existing = [r for r in roots if os.path.isdir(r)]
    if not existing:
        return []
    try:
        return _collect(_launch_grep(pattern, existing))
    except FileNotFoundError:
        found = []
        for root in existing:
            for dirpath, _, filenames in os.walk(root):
                for fn in filenames:
                    if fn.endswith('.md'):
                        found.append(os.path.join(dirpath, fn))
        return found


# ---------------------------------------------------------------------------
# Requirements scan
# ---------------------------------------------------------------------------

def scan_requirements_tree(base_path: Path) -> tuple[
    list[dict[str, str]],   # req_entries
    list[dict[str, str]],   # task_entries
]:
    """Find and read requirements.md + goal.md files using native find."""
    req_root = base_path / "requirements_tasks"
    req_entries: list[dict[str, str]] = []
    task_entries: list[dict[str, str]] = []

    if not req_root.exists():
        return req_entries, task_entries

    files = _find_named_files([str(req_root)], ['requirements.md', 'goal.md'])

    for file_str in sorted(files):
        file_path = Path(file_str)
        filename = file_path.name
        dir_path = file_path.parent
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            continue

        if filename == 'requirements.md':
            meta = parse_yaml_frontmatter(content)
            if meta:
                req_id = meta.get('id', '')
                # Why: AC-01/02 (REQ-PROC-009 SEC-08) — include hierarchical sub-requirement
                # IDs (REQ-CAT-NNN-NN) alongside top-level IDs (REQ-CAT-NNN) in the catalog.
                if req_id and re.match(r'^REQ-(FUNC|NFUNC|PROC)-\d{3}(-\d{2})?$', str(req_id)):
                    try:
                        rel_path = dir_path.relative_to(req_root)
                    except ValueError:
                        rel_path = dir_path
                    req_entries.append({
                        'id': str(req_id),
                        'path': str(rel_path).replace('\\', '/'),
                        'name': extract_requirement_name(content, dir_path),
                        'status': str(meta.get('status', '')),
                    })

        elif filename == 'goal.md':
            meta = parse_yaml_frontmatter(content)
            if meta:
                task_id = meta.get('task_id', '')
                if task_id and re.match(r'^TASK-(FUNC|NFUNC|PROC)-\d{3}-\d{2}', str(task_id)):
                    task_entries.append({
                        'id': str(task_id),
                        'parent': str(meta.get('parent_requirement', '')),
                        'status': str(meta.get('status', '')),
                    })

    return req_entries, task_entries


# ---------------------------------------------------------------------------
# User needs scan
# ---------------------------------------------------------------------------

def scan_user_needs_tree(base_path: Path) -> tuple[
    list[dict[str, str]],   # personas
    list[dict[str, str]],   # scenarios
    list[dict[str, str]],   # flows
]:
    """Find and read persona/scenario/flow.md files using native find."""
    un_root = base_path / "requirements_user_needs"
    personas: list[dict[str, str]] = []
    scenarios: list[dict[str, str]] = []
    flows: list[dict[str, str]] = []

    if not un_root.exists():
        return personas, scenarios, flows

    files = _find_named_files([str(un_root)], ['persona.md', 'scenario.md', 'flow.md'])

    for file_str in sorted(files):
        file_path = Path(file_str)
        filename = file_path.name
        dir_path = file_path.parent
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            continue

        meta = parse_yaml_frontmatter(content)
        if not meta:
            continue

        if filename == 'persona.md':
            persona_id = meta.get('persona_id', '')
            if persona_id and re.match(r'^PERSONA-\d{3}$', str(persona_id)):
                personas.append({
                    'id': str(persona_id),
                    'folder': dir_path.name,
                    'name': extract_user_needs_name(meta, dir_path),
                    'role': str(meta.get('role', '')),
                    'status': str(meta.get('review_status', '')),
                })

        elif filename == 'scenario.md':
            scenario_id = meta.get('scenario_id', '')
            if scenario_id and re.match(r'^SCEN-\d{3}-\d{2}$', str(scenario_id)):
                try:
                    rel = str(dir_path.relative_to(un_root)).replace('\\', '/')
                except ValueError:
                    rel = str(dir_path)
                scenarios.append({
                    'id': str(scenario_id),
                    'path': rel,
                    'name': extract_user_needs_name(meta, dir_path),
                    'persona_id': str(meta.get('persona_id', '')),
                    'status': str(meta.get('review_status', '')),
                })

        elif filename == 'flow.md':
            flow_id = meta.get('flow_id', '')
            if flow_id and re.match(r'^FLOW-\d{3}$', str(flow_id)):
                flows.append({
                    'id': str(flow_id),
                    'folder': dir_path.name,
                    'name': extract_user_needs_name(meta, dir_path),
                    'status': str(meta.get('review_status', '')),
                    'impl_status': str(meta.get('implementation_status', '')),
                })

    personas.sort(key=lambda e: e['id'])
    scenarios.sort(key=lambda e: e['id'])
    flows.sort(key=lambda e: e['id'])
    return personas, scenarios, flows


# ---------------------------------------------------------------------------
# ID computation helpers (unchanged from v1)
# ---------------------------------------------------------------------------

def compute_next_ids(entries: list[dict[str, str]]) -> dict[str, str]:
    max_nums: dict[str, int] = {'PROC': 0, 'NFUNC': 0, 'FUNC': 0}
    for entry in entries:
        match = re.match(r'^REQ-(PROC|NFUNC|FUNC)-(\d{3})$', entry['id'])
        if match:
            cat = match.group(1)
            num = int(match.group(2))
            max_nums[cat] = max(max_nums[cat], num)
    return {
        cat: f"REQ-{cat}-{(max_num + 1):03d}"
        for cat, max_num in max_nums.items()
    }


def compute_next_user_needs_ids(
    personas: list[dict[str, str]],
    scenarios: list[dict[str, str]],
    flows: list[dict[str, str]],
) -> dict[str, Any]:
    max_persona = 0
    for p in personas:
        match = re.match(r'^PERSONA-(\d{3})$', p['id'])
        if match:
            max_persona = max(max_persona, int(match.group(1)))

    max_flow = 0
    for f in flows:
        match = re.match(r'^FLOW-(\d{3})$', f['id'])
        if match:
            max_flow = max(max_flow, int(match.group(1)))

    persona_max_scen: dict[str, int] = {}
    for s in scenarios:
        match = re.match(r'^SCEN-(\d{3})-(\d{2})$', s['id'])
        if match:
            p_num = match.group(1)
            s_num = int(match.group(2))
            persona_max_scen[p_num] = max(persona_max_scen.get(p_num, 0), s_num)

    return {
        'PERSONA': f"PERSONA-{(max_persona + 1):03d}",
        'FLOW': f"FLOW-{(max_flow + 1):03d}",
        '_scenario_per_persona': {
            f"PERSONA-{k}": f"SCEN-{k}-{(v + 1):02d}"
            for k, v in sorted(persona_max_scen.items())
        },
    }


# ---------------------------------------------------------------------------
# Registry generation (output identical to v1)
# ---------------------------------------------------------------------------

def _parallel_req_scan(base_path: Path) -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    """Launch find (req/task files) and grep (VTR files) in parallel, then process."""
    req_root = str(base_path / "requirements_tasks")

    # Launch find and all three VTR greps before waiting on any of them
    find_proc = _launch_find([req_root], ['requirements.md', 'goal.md']) if os.path.isdir(req_root) else None
    vtr_grep_procs = [
        _launch_grep('vcd-record', [d]) if os.path.isdir(d) else None
        for d in [
            str(base_path / 'requirements_user_needs'),
            req_root,
            str(base_path / 'doc' / 'presentation' / 'design'),
        ]
    ]

    find_files = _collect(find_proc) if find_proc else []
    per_dir_vtr_files = [sorted(_collect(p)) if p else [] for p in vtr_grep_procs]

    req_entries, task_entries = _process_req_files(base_path, find_files)
    vtr_entries = _process_vtr_files(base_path,
        [f for files in per_dir_vtr_files for f in files])
    return req_entries, task_entries, vtr_entries


def _parallel_all_scan(base_path: Path) -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    """Launch all subprocesses in parallel for --all mode."""
    req_root = str(base_path / "requirements_tasks")
    un_root = str(base_path / "requirements_user_needs")
    design_root = str(base_path / 'doc' / 'presentation' / 'design')

    # VTR order must match v1: requirements_user_needs first, then requirements_tasks, then design
    vtr_dirs_ordered = [un_root, req_root, design_root]

    find_req_proc = _launch_find([req_root], ['requirements.md', 'goal.md']) if os.path.isdir(req_root) else None
    find_un_proc = _launch_find([un_root], ['persona.md', 'scenario.md', 'flow.md']) if os.path.isdir(un_root) else None
    vtr_grep_procs = [
        _launch_grep('vcd-record', [d]) if os.path.isdir(d) else None
        for d in vtr_dirs_ordered
    ]

    find_req_files = _collect(find_req_proc) if find_req_proc else []
    find_un_files = _collect(find_un_proc) if find_un_proc else []
    per_dir_vtr_files = [sorted(_collect(p)) if p else [] for p in vtr_grep_procs]

    req_entries, task_entries = _process_req_files(base_path, find_req_files)
    personas, scenarios, flows = _process_un_files(base_path, find_un_files)
    vtr_entries = _process_vtr_files(base_path,
        [f for files in per_dir_vtr_files for f in files])
    return req_entries, task_entries, personas, scenarios, flows, vtr_entries


def _process_req_files(
    base_path: Path, files: list[str]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Parse requirements.md and goal.md files from a file list."""
    req_root = base_path / "requirements_tasks"
    req_entries: list[dict[str, str]] = []
    task_entries: list[dict[str, str]] = []
    for file_str in sorted(files):
        file_path = Path(file_str)
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            continue
        meta = parse_yaml_frontmatter(content)
        if not meta:
            continue
        dir_path = file_path.parent
        if file_path.name == 'requirements.md':
            req_id = meta.get('id', '')
            # Why: AC-01/02 (REQ-PROC-009 SEC-08) — include hierarchical sub-requirement
            # IDs (REQ-CAT-NNN-NN) alongside top-level IDs (REQ-CAT-NNN) in the catalog.
            if req_id and re.match(r'^REQ-(FUNC|NFUNC|PROC)-\d{3}(-\d{2})?$', str(req_id)):
                try:
                    rel_path = dir_path.relative_to(req_root)
                except ValueError:
                    rel_path = dir_path
                req_entries.append({
                    'id': str(req_id),
                    'path': str(rel_path).replace('\\', '/'),
                    'name': extract_requirement_name(content, dir_path),
                    'status': str(meta.get('status', '')),
                })
        elif file_path.name == 'goal.md':
            task_id = meta.get('task_id', '')
            if task_id and re.match(r'^TASK-(FUNC|NFUNC|PROC)-\d{3}-\d{2}', str(task_id)):
                task_entries.append({
                    'id': str(task_id),
                    'parent': str(meta.get('parent_requirement', '')),
                    'status': str(meta.get('status', '')),
                })
    return req_entries, task_entries


def _process_un_files(
    base_path: Path, files: list[str]
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Parse persona/scenario/flow.md files from a file list."""
    un_root = base_path / "requirements_user_needs"
    personas: list[dict[str, str]] = []
    scenarios: list[dict[str, str]] = []
    flows: list[dict[str, str]] = []
    for file_str in sorted(files):
        file_path = Path(file_str)
        dir_path = file_path.parent
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            continue
        meta = parse_yaml_frontmatter(content)
        if not meta:
            continue
        if file_path.name == 'persona.md':
            persona_id = meta.get('persona_id', '')
            if persona_id and re.match(r'^PERSONA-\d{3}$', str(persona_id)):
                personas.append({
                    'id': str(persona_id),
                    'folder': dir_path.name,
                    'name': extract_user_needs_name(meta, dir_path),
                    'role': str(meta.get('role', '')),
                    'status': str(meta.get('review_status', '')),
                })
        elif file_path.name == 'scenario.md':
            scenario_id = meta.get('scenario_id', '')
            if scenario_id and re.match(r'^SCEN-\d{3}-\d{2}$', str(scenario_id)):
                try:
                    rel = str(dir_path.relative_to(un_root)).replace('\\', '/')
                except ValueError:
                    rel = str(dir_path)
                scenarios.append({
                    'id': str(scenario_id),
                    'path': rel,
                    'name': extract_user_needs_name(meta, dir_path),
                    'persona_id': str(meta.get('persona_id', '')),
                    'status': str(meta.get('review_status', '')),
                })
        elif file_path.name == 'flow.md':
            flow_id = meta.get('flow_id', '')
            if flow_id and re.match(r'^FLOW-\d{3}$', str(flow_id)):
                flows.append({
                    'id': str(flow_id),
                    'folder': dir_path.name,
                    'name': extract_user_needs_name(meta, dir_path),
                    'status': str(meta.get('review_status', '')),
                    'impl_status': str(meta.get('implementation_status', '')),
                })
    personas.sort(key=lambda e: e['id'])
    scenarios.sort(key=lambda e: e['id'])
    flows.sort(key=lambda e: e['id'])
    return personas, scenarios, flows


def scan_vtr_records(base_path: Path) -> list[dict[str, str]]:
    """Find VTR records using grep per directory (preserving v1 search order).

    Searches requirements_user_needs/ first, then requirements_tasks/, then
    doc/presentation/design/ — matching v1's order so that when the same VTR
    ID appears in multiple files the first-seen source file is consistent.
    Launches all three greps in parallel, then merges in order.
    """
    ordered_dirs = [
        str(base_path / 'requirements_user_needs'),
        str(base_path / 'requirements_tasks'),
        str(base_path / 'doc' / 'presentation' / 'design'),
    ]

    # Launch one grep per directory in parallel
    procs = [
        _launch_grep('vcd-record', [d]) if os.path.isdir(d) else None
        for d in ordered_dirs
    ]
    per_dir_files = [
        sorted(_collect(p)) if p else []
        for p in procs
    ]

    entries: list[dict[str, str]] = []
    seen_ids: set[Any] = set()

    for files in per_dir_files:
        for file_str in files:
            file_path = Path(file_str)
            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception:
                continue
            for m in VTR_BLOCK_PATTERN.finditer(content):
                id_m = re.search(r'^\s*id:\s*(VTR-\d{3})\s*$', m.group(1), re.MULTILINE)
                if id_m:
                    vtr_id = id_m.group(1)
                    if vtr_id not in seen_ids:
                        seen_ids.add(vtr_id)
                        rel = str(file_path.relative_to(base_path)).replace('\\', '/')
                        entries.append({'id': vtr_id, 'source_file': rel})

    entries.sort(key=lambda e: e['id'])
    return entries


def _process_vtr_files(base_path: Path, files: list[str]) -> list[dict[str, str]]:
    """Extract VTR records from a list of files (used when files already ordered)."""
    entries: list[dict[str, str]] = []
    seen_ids: set[Any] = set()
    for file_str in files:
        file_path = Path(file_str)
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            continue
        for m in VTR_BLOCK_PATTERN.finditer(content):
            id_m = re.search(r'^\s*id:\s*(VTR-\d{3})\s*$', m.group(1), re.MULTILINE)
            if id_m:
                vtr_id = id_m.group(1)
                if vtr_id not in seen_ids:
                    seen_ids.add(vtr_id)
                    rel = str(file_path.relative_to(base_path)).replace('\\', '/')
                    entries.append({'id': vtr_id, 'source_file': rel})
    entries.sort(key=lambda e: e['id'])
    return entries


_HIERARCHICAL_REQ_RE = re.compile(r'^REQ-(FUNC|NFUNC|PROC)-\d{3}-\d{2}$')


def _req_id_cell(req_id: str) -> str:
    """Return the ID cell content for a requirement table row.

    Hierarchical sub-requirement IDs (REQ-CAT-NNN-NN) are prefixed with a
    tree marker so they render visually nested under their parent epic entry.

    Why: AC-01 (REQ-PROC-009 SEC-08) requires hierarchical IDs to be listed
    "nested under their parent epic's top-level ID".
    """
    if _HIERARCHICAL_REQ_RE.match(req_id):
        return f"└─ {req_id}"
    return req_id


def generate_requirements_registry(base_path: Path) -> str:
    req_entries, task_entries, vtr_entries = _parallel_req_scan(base_path)

    # Next VTR ID
    max_vtr = 0
    for vtr in vtr_entries:
        match = re.match(r'^VTR-(\d{3})$', vtr['id'])
        if match:
            max_vtr = max(max_vtr, int(match.group(1)))
    next_vtr_id = f'VTR-{(max_vtr + 1):03d}'
    vtr_range = f"{vtr_entries[0]['id']} to {vtr_entries[-1]['id']}" if vtr_entries else '--'

    # Group requirements by category
    categories: dict[str, list[dict[str, str]]] = {'PROC': [], 'NFUNC': [], 'FUNC': []}
    for entry in req_entries:
        match = re.match(r'^REQ-(PROC|NFUNC|FUNC)-', entry['id'])
        if match:
            categories[match.group(1)].append(entry)
    for cat in categories:
        categories[cat].sort(key=lambda e: e['id'])

    # Task counts per requirement
    task_counts: dict[str, int] = {}
    for task in task_entries:
        parent = task['parent']
        task_counts[parent] = task_counts.get(parent, 0) + 1

    next_ids = compute_next_ids(req_entries)
    total = sum(len(v) for v in categories.values())

    lines = []
    lines.append("# Requirements ID Registry")
    lines.append("")
    lines.append(f"**Auto-generated**: {date.today().isoformat()} by `scripts/generate_id_registry.py`")
    lines.append("")
    lines.append("> Do NOT edit this file manually. It is regenerated on demand.")
    lines.append("> Run: `python scripts/generate_id_registry.py --requirements`")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append("| Category | ID Range | Count |")
    lines.append("|----------|----------|-------|")
    for cat_key, cat_label in [('PROC', 'PROC (Process)'), ('NFUNC', 'NFUNC (Non-Functional)'), ('FUNC', 'FUNC (Functional)')]:
        cat_entries = categories[cat_key]
        if cat_entries:
            lines.append(f"| {cat_label} | {cat_entries[0]['id']} to {cat_entries[-1]['id']} | {len(cat_entries)} |")
        else:
            lines.append(f"| {cat_label} | -- | 0 |")
    lines.append(f"| **Total** | | **{total}** |")
    lines.append(f"| VTR (Value Trade-off Records) | {vtr_range} | {len(vtr_entries)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    cat_descriptions = {
        'PROC': ('PROC - Process Requirements',
                 'Process requirements define HOW we work, document, communicate, or how the AI should behave.'),
        'NFUNC': ('NFUNC - Non-Functional Requirements',
                  'Non-functional requirements define technical specs, quality requirements, and design system rules.'),
        'FUNC': ('FUNC - Functional Requirements',
                 'Functional requirements define features from the end-user\'s perspective.'),
    }

    for cat_key in ['PROC', 'NFUNC', 'FUNC']:
        title, description = cat_descriptions[cat_key]
        lines.append(f"## {title}")
        lines.append("")
        lines.append(description)
        lines.append("")
        lines.append("| ID | Path | Name |")
        lines.append("|----|------|------|")
        for entry in categories[cat_key]:
            lines.append(f"| {_req_id_cell(entry['id'])} | `{entry['path']}` | {entry['name']} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Next Available IDs")
    lines.append("")
    lines.append("| Category | Next ID |")
    lines.append("|----------|---------|")
    for cat_key in ['PROC', 'NFUNC', 'FUNC']:
        lines.append(f"| {cat_key} | {next_ids[cat_key]} |")
    lines.append(f"| VTR | {next_vtr_id} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Task Summary")
    lines.append("")
    lines.append(f"Total tasks found: {len(task_entries)}")
    lines.append("")
    if task_entries:
        status_counts: dict[str, int] = {}
        for task in task_entries:
            s = task['status']
            status_counts[s] = status_counts.get(s, 0) + 1
        lines.append("| Status | Count |")
        lines.append("|--------|-------|")
        for status, count in sorted(status_counts.items()):
            lines.append(f"| {status} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## VTR - Value Trade-off Records")
    lines.append("")
    lines.append("Value Trade-off Records document design decisions where persona values conflict.")
    lines.append("")
    lines.append("| ID | Source File |")
    lines.append("|----|-------------|")
    if vtr_entries:
        for vtr in vtr_entries:
            lines.append(f"| {vtr['id']} | `{vtr['source_file']}` |")
    else:
        lines.append("| — | _No VTR records found_ |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Usage Notes")
    lines.append("")
    lines.append("1. **ID Assignment**: When creating new requirements, use the \"Next Available ID\" for the appropriate category")
    lines.append("2. **ID Immutability**: Once assigned, IDs NEVER change (even if the requirement is renamed/moved)")
    lines.append("3. **Path Changes**: If a requirement moves, the ID stays the same")
    lines.append("4. **Deprecation**: Deprecated requirements keep their ID (marked as deprecated, not reused)")
    lines.append("")
    lines.append("## Scripts")
    lines.append("")
    lines.append("- `scripts/generate_id_registry.py` - Auto-generates this registry")
    lines.append("- `scripts/validate_meta.py` - Validates YAML frontmatter and ID uniqueness")
    lines.append("- `scripts/generate_status_overview.py` - Generates coverage reports")
    lines.append("")

    return '\n'.join(lines)


def generate_user_needs_registry(base_path: Path) -> str:
    un_root = str(base_path / "requirements_user_needs")
    files = _find_named_files([un_root], ['persona.md', 'scenario.md', 'flow.md'])
    personas, scenarios, flows = _process_un_files(base_path, files)
    next_ids = compute_next_user_needs_ids(personas, scenarios, flows)

    lines = []
    lines.append("# User Needs ID Registry")
    lines.append("")
    lines.append(f"**Auto-generated**: {date.today().isoformat()} by `scripts/generate_id_registry.py`")
    lines.append("")
    lines.append("> Do NOT edit this file manually. It is regenerated on demand.")
    lines.append("> Run: `python scripts/generate_id_registry.py --user-needs`")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    lines.append(f"| Personas | {len(personas)} |")
    lines.append(f"| Scenarios | {len(scenarios)} |")
    lines.append(f"| Flows | {len(flows)} |")
    lines.append(f"| **Total** | **{len(personas) + len(scenarios) + len(flows)}** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Personas")
    lines.append("")
    lines.append("| ID | Folder | Name | Role | Status |")
    lines.append("|----|--------|------|------|--------|")
    for p in personas:
        lines.append(f"| {p['id']} | `{p['folder']}` | {p['name']} | {p['role']} | {p['status']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Scenarios")
    lines.append("")
    lines.append("| ID | Path | Name | Persona | Status |")
    lines.append("|----|------|------|---------|--------|")
    for s in scenarios:
        lines.append(f"| {s['id']} | `{s['path']}` | {s['name']} | {s['persona_id']} | {s['status']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Flows")
    lines.append("")
    lines.append("| ID | Folder | Name | Review Status | Impl Status |")
    lines.append("|----|--------|------|---------------|-------------|")
    for f in flows:
        lines.append(f"| {f['id']} | `{f['folder']}` | {f['name']} | {f['status']} | {f['impl_status']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Next Available IDs")
    lines.append("")
    lines.append("| Type | Next ID |")
    lines.append("|------|---------|")
    lines.append(f"| Persona | {next_ids['PERSONA']} |")
    lines.append(f"| Flow | {next_ids['FLOW']} |")
    lines.append("")

    scen_per_persona = next_ids.get('_scenario_per_persona', {})
    if scen_per_persona:
        lines.append("### Next Scenario ID per Persona")
        lines.append("")
        lines.append("| Persona | Next Scenario ID |")
        lines.append("|---------|------------------|")
        for persona_id, next_scen in sorted(scen_per_persona.items()):
            lines.append(f"| {persona_id} | {next_scen} |")
        lines.append("")

    lines.append("---")
    lines.append("")

    lines.append("## Usage Notes")
    lines.append("")
    lines.append("1. **Persona IDs**: Sequential globally (PERSONA-001, PERSONA-002, ...)")
    lines.append("2. **Scenario IDs**: Per-persona sequential (SCEN-001-01, SCEN-001-02, SCEN-002-01, ...)")
    lines.append("3. **Flow IDs**: Sequential globally (FLOW-001, FLOW-002, ...)")
    lines.append("4. **ID Immutability**: Once assigned, IDs NEVER change")
    lines.append("")
    lines.append("## Scripts")
    lines.append("")
    lines.append("- `scripts/generate_id_registry.py` - Auto-generates this registry")
    lines.append("- `scripts/validate_meta.py` - Validates YAML frontmatter and ID uniqueness")
    lines.append("")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    args = set(sys.argv[1:])

    if not args or '--help' in args or '-h' in args:
        print("Usage: python scripts/generate_id_registry_v2.py [--requirements] [--user-needs] [--all]")
        print("")
        print("Modes:")
        print("  --requirements  Generate requirements_tasks/_meta/id_registry.md")
        print("  --user-needs    Generate requirements_user_needs/_meta/id_registry.md")
        print("  --all           Generate both registries")
        sys.exit(0)

    do_requirements = '--requirements' in args or '--all' in args
    do_user_needs = '--user-needs' in args or '--all' in args

    if not do_requirements and not do_user_needs:
        print("Error: Specify --requirements, --user-needs, or --all")
        sys.exit(1)

    if do_requirements and do_user_needs:
        # --all: launch all subprocesses in parallel, then process results
        print("Generating both registries...")
        req_entries, task_entries, personas, scenarios, flows, vtr_entries = \
            _parallel_all_scan(project_root)

        # Requirements registry
        content = _build_requirements_content(req_entries, task_entries, vtr_entries)
        out_dir = project_root / "requirements_tasks" / "_meta"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "id_registry.md").write_text(content, encoding='utf-8')
        print(f"  Written to {out_dir / 'id_registry.md'}")

        # User needs registry
        content = _build_user_needs_content(personas, scenarios, flows)
        out_dir = project_root / "requirements_user_needs" / "_meta"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "id_registry.md").write_text(content, encoding='utf-8')
        print(f"  Written to {out_dir / 'id_registry.md'}")

    elif do_requirements:
        print("Generating requirements ID registry...")
        content = generate_requirements_registry(project_root)
        out_dir = project_root / "requirements_tasks" / "_meta"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "id_registry.md").write_text(content, encoding='utf-8')
        print(f"  Written to {out_dir / 'id_registry.md'}")

    elif do_user_needs:
        print("Generating user needs ID registry...")
        content = generate_user_needs_registry(project_root)
        out_dir = project_root / "requirements_user_needs" / "_meta"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "id_registry.md").write_text(content, encoding='utf-8')
        print(f"  Written to {out_dir / 'id_registry.md'}")

    print("Done.")


def _build_requirements_content(
    req_entries: list[dict[str, str]],
    task_entries: list[dict[str, str]],
    vtr_entries: list[dict[str, str]],
) -> str:
    """Build requirements registry markdown from pre-scanned data."""
    max_vtr = 0
    for vtr in vtr_entries:
        match = re.match(r'^VTR-(\d{3})$', vtr['id'])
        if match:
            max_vtr = max(max_vtr, int(match.group(1)))
    next_vtr_id = f'VTR-{(max_vtr + 1):03d}'
    vtr_range = f"{vtr_entries[0]['id']} to {vtr_entries[-1]['id']}" if vtr_entries else '--'

    categories: dict[str, list[dict[str, str]]] = {'PROC': [], 'NFUNC': [], 'FUNC': []}
    for entry in req_entries:
        match = re.match(r'^REQ-(PROC|NFUNC|FUNC)-', entry['id'])
        if match:
            categories[match.group(1)].append(entry)
    for cat in categories:
        categories[cat].sort(key=lambda e: e['id'])

    task_counts: dict[str, int] = {}
    for task in task_entries:
        parent = task['parent']
        task_counts[parent] = task_counts.get(parent, 0) + 1

    next_ids = compute_next_ids(req_entries)
    total = sum(len(v) for v in categories.values())

    lines = []
    lines.append("# Requirements ID Registry")
    lines.append("")
    lines.append(f"**Auto-generated**: {date.today().isoformat()} by `scripts/generate_id_registry.py`")
    lines.append("")
    lines.append("> Do NOT edit this file manually. It is regenerated on demand.")
    lines.append("> Run: `python scripts/generate_id_registry.py --requirements`")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append("| Category | ID Range | Count |")
    lines.append("|----------|----------|-------|")
    for cat_key, cat_label in [('PROC', 'PROC (Process)'), ('NFUNC', 'NFUNC (Non-Functional)'), ('FUNC', 'FUNC (Functional)')]:
        cat_entries = categories[cat_key]
        if cat_entries:
            lines.append(f"| {cat_label} | {cat_entries[0]['id']} to {cat_entries[-1]['id']} | {len(cat_entries)} |")
        else:
            lines.append(f"| {cat_label} | -- | 0 |")
    lines.append(f"| **Total** | | **{total}** |")
    lines.append(f"| VTR (Value Trade-off Records) | {vtr_range} | {len(vtr_entries)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    cat_descriptions = {
        'PROC': ('PROC - Process Requirements',
                 'Process requirements define HOW we work, document, communicate, or how the AI should behave.'),
        'NFUNC': ('NFUNC - Non-Functional Requirements',
                  'Non-functional requirements define technical specs, quality requirements, and design system rules.'),
        'FUNC': ('FUNC - Functional Requirements',
                 'Functional requirements define features from the end-user\'s perspective.'),
    }
    for cat_key in ['PROC', 'NFUNC', 'FUNC']:
        title, description = cat_descriptions[cat_key]
        lines.append(f"## {title}")
        lines.append("")
        lines.append(description)
        lines.append("")
        lines.append("| ID | Path | Name |")
        lines.append("|----|------|------|")
        for entry in categories[cat_key]:
            lines.append(f"| {_req_id_cell(entry['id'])} | `{entry['path']}` | {entry['name']} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Next Available IDs")
    lines.append("")
    lines.append("| Category | Next ID |")
    lines.append("|----------|---------|")
    for cat_key in ['PROC', 'NFUNC', 'FUNC']:
        lines.append(f"| {cat_key} | {next_ids[cat_key]} |")
    lines.append(f"| VTR | {next_vtr_id} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Task Summary")
    lines.append("")
    lines.append(f"Total tasks found: {len(task_entries)}")
    lines.append("")
    if task_entries:
        status_counts: dict[str, int] = {}
        for task in task_entries:
            s = task['status']
            status_counts[s] = status_counts.get(s, 0) + 1
        lines.append("| Status | Count |")
        lines.append("|--------|-------|")
        for status, count in sorted(status_counts.items()):
            lines.append(f"| {status} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## VTR - Value Trade-off Records")
    lines.append("")
    lines.append("Value Trade-off Records document design decisions where persona values conflict.")
    lines.append("")
    lines.append("| ID | Source File |")
    lines.append("|----|-------------|")
    if vtr_entries:
        for vtr in vtr_entries:
            lines.append(f"| {vtr['id']} | `{vtr['source_file']}` |")
    else:
        lines.append("| — | _No VTR records found_ |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Usage Notes")
    lines.append("")
    lines.append("1. **ID Assignment**: When creating new requirements, use the \"Next Available ID\" for the appropriate category")
    lines.append("2. **ID Immutability**: Once assigned, IDs NEVER change (even if the requirement is renamed/moved)")
    lines.append("3. **Path Changes**: If a requirement moves, the ID stays the same")
    lines.append("4. **Deprecation**: Deprecated requirements keep their ID (marked as deprecated, not reused)")
    lines.append("")
    lines.append("## Scripts")
    lines.append("")
    lines.append("- `scripts/generate_id_registry.py` - Auto-generates this registry")
    lines.append("- `scripts/validate_meta.py` - Validates YAML frontmatter and ID uniqueness")
    lines.append("- `scripts/generate_status_overview.py` - Generates coverage reports")
    lines.append("")

    return '\n'.join(lines)


def _build_user_needs_content(
    personas: list[dict[str, str]],
    scenarios: list[dict[str, str]],
    flows: list[dict[str, str]],
) -> str:
    """Build user needs registry markdown from pre-scanned data."""
    next_ids = compute_next_user_needs_ids(personas, scenarios, flows)

    lines = []
    lines.append("# User Needs ID Registry")
    lines.append("")
    lines.append(f"**Auto-generated**: {date.today().isoformat()} by `scripts/generate_id_registry.py`")
    lines.append("")
    lines.append("> Do NOT edit this file manually. It is regenerated on demand.")
    lines.append("> Run: `python scripts/generate_id_registry.py --user-needs`")
    lines.append("")

    lines.append("## Overview")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    lines.append(f"| Personas | {len(personas)} |")
    lines.append(f"| Scenarios | {len(scenarios)} |")
    lines.append(f"| Flows | {len(flows)} |")
    lines.append(f"| **Total** | **{len(personas) + len(scenarios) + len(flows)}** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Personas")
    lines.append("")
    lines.append("| ID | Folder | Name | Role | Status |")
    lines.append("|----|--------|------|------|--------|")
    for p in personas:
        lines.append(f"| {p['id']} | `{p['folder']}` | {p['name']} | {p['role']} | {p['status']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Scenarios")
    lines.append("")
    lines.append("| ID | Path | Name | Persona | Status |")
    lines.append("|----|------|------|---------|--------|")
    for s in scenarios:
        lines.append(f"| {s['id']} | `{s['path']}` | {s['name']} | {s['persona_id']} | {s['status']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Flows")
    lines.append("")
    lines.append("| ID | Folder | Name | Review Status | Impl Status |")
    lines.append("|----|--------|------|---------------|-------------|")
    for f in flows:
        lines.append(f"| {f['id']} | `{f['folder']}` | {f['name']} | {f['status']} | {f['impl_status']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Next Available IDs")
    lines.append("")
    lines.append("| Type | Next ID |")
    lines.append("|------|---------|")
    lines.append(f"| Persona | {next_ids['PERSONA']} |")
    lines.append(f"| Flow | {next_ids['FLOW']} |")
    lines.append("")

    scen_per_persona = next_ids.get('_scenario_per_persona', {})
    if scen_per_persona:
        lines.append("### Next Scenario ID per Persona")
        lines.append("")
        lines.append("| Persona | Next Scenario ID |")
        lines.append("|---------|------------------|")
        for persona_id, next_scen in sorted(scen_per_persona.items()):
            lines.append(f"| {persona_id} | {next_scen} |")
        lines.append("")

    lines.append("---")
    lines.append("")

    lines.append("## Usage Notes")
    lines.append("")
    lines.append("1. **Persona IDs**: Sequential globally (PERSONA-001, PERSONA-002, ...)")
    lines.append("2. **Scenario IDs**: Per-persona sequential (SCEN-001-01, SCEN-001-02, SCEN-002-01, ...)")
    lines.append("3. **Flow IDs**: Sequential globally (FLOW-001, FLOW-002, ...)")
    lines.append("4. **ID Immutability**: Once assigned, IDs NEVER change")
    lines.append("")
    lines.append("## Scripts")
    lines.append("")
    lines.append("- `scripts/generate_id_registry.py` - Auto-generates this registry")
    lines.append("- `scripts/validate_meta.py` - Validates YAML frontmatter and ID uniqueness")
    lines.append("")

    return '\n'.join(lines)


if __name__ == "__main__":
    main()
