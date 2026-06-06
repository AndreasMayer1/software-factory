#!/usr/bin/env python3
"""
Aggregate Value Trade-off Records from across the project.

Scans for <!-- vcd-record ... --> blocks in:
  - requirements_user_needs/
  - doc/presentation/design/

Generates: requirements_user_needs/_meta/value_tradeoff_summary.md

Usage:
    python scripts/aggregate_value_tradeoffs.py

Output:
    Writes the aggregated summary markdown file. Prints progress / error
    diagnostics and a final summary line ("Generated …" or error text)
    to stdout/stderr.

Exit codes:
    0 - success
    1 - validation errors (duplicate IDs, missing required fields)
    2 - no records found (warns, still generates empty summary)
"""

# tier: C  # one-shot CLI artifact generator; no in-tree Python imports

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Why: this script runs both as `python3 scripts/artifacts/aggregate_value_tradeoffs.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
    _parse_yaml_block,
    read_frontmatter,
)

REQUIRED_FIELDS = {'id', 'date', 'artifact', 'personas', 'decision_status'}

SEARCH_DIRS = [
    'requirements_user_needs',
    'doc/presentation/design',
]

# Path fragments that indicate documentation/template files — not real VTR records.
# Any scanned file whose path contains one of these strings is skipped.
EXCLUDE_PATH_FRAGMENTS = [
    '_meta/value_tradeoff_record_template',
    '/plans_and_protocols/',
    '/tasks/',  # task goal.md / protocol.md — VTRs live in artifacts, not task docs
]

OUTPUT_FILE = 'requirements_user_needs/_meta/value_tradeoff_summary.md'

VTR_BLOCK_PATTERN = re.compile(r'<!--\s*vcd-record\s*\n(.*?)\n\s*-->', re.DOTALL)
VTR_ID_PATTERN = re.compile(r'^VTR-\d{3}$')


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_vcd_block(yaml_text: str) -> Optional[dict[str, Any]]:
    """Parse a vcd-record YAML block via the central helper (ruamel.yaml)."""
    try:
        result = _parse_yaml_block(yaml_text)
    except FrontmatterError:
        return None
    # Return as plain dict so downstream isinstance(record, dict) checks
    # and dict-mutation operations (record['_source_file'] = ...) keep working.
    return dict(result) if result else None


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def extract_vtr_records(project_root: Path) -> list[dict[str, Any]]:
    """Scan specified directories for VTR records."""
    records = []

    for dir_name in SEARCH_DIRS:
        search_dir = project_root / dir_name
        if not search_dir.exists():
            continue

        for md_file in sorted(search_dir.rglob('*.md')):
            rel = str(md_file.relative_to(project_root)).replace('\\', '/')
            if any(frag in rel for frag in EXCLUDE_PATH_FRAGMENTS):
                continue
            try:
                content = md_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f'  Warning: Could not read {md_file}: {e}', file=sys.stderr)
                continue

            for match in VTR_BLOCK_PATTERN.finditer(content):
                yaml_text = match.group(1).strip()
                record = parse_vcd_block(yaml_text)
                if record:
                    record['_source_file'] = str(
                        md_file.relative_to(project_root)
                    ).replace('\\', '/')
                    records.append(record)

    return records


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_records(records: list[dict[str, Any]]) -> list[str]:
    """Validate records and return list of error messages."""
    errors = []
    seen_ids: dict[str, str] = {}

    for i, record in enumerate(records):
        src = record.get('_source_file', f'record {i + 1}')
        rec_id = str(record.get('id', ''))

        for field in REQUIRED_FIELDS:
            if field not in record or record[field] is None:
                errors.append(f'[{src}] Missing required field: \'{field}\'')

        if rec_id:
            if not VTR_ID_PATTERN.match(rec_id):
                errors.append(
                    f'[{src}] Invalid VTR ID format: \'{rec_id}\' (expected VTR-NNN)'
                )
            elif rec_id in seen_ids:
                errors.append(
                    f'[{src}] Duplicate VTR ID: \'{rec_id}\' '
                    f'(first seen in {seen_ids[rec_id]})'
                )
            else:
                seen_ids[rec_id] = src

    return errors


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _persona_display(p: Any) -> str:
    if isinstance(p, dict):
        pid = p.get('id', '?')
        val = p.get('value', '?')
        impact = p.get('impact', '?')
        return f'{pid}: {val} [{impact}]'
    return str(p)


def build_conflict_matrix(records: list[dict[str, Any]]) -> dict[tuple[str, str], int]:
    """Count how often persona pairs appear together in VTR records."""
    pair_counts: dict[tuple[str, str], int] = {}

    for record in records:
        personas = record.get('personas', [])
        if not isinstance(personas, list):
            continue
        ids = []
        for p in personas:
            pid = p.get('id', '') if isinstance(p, dict) else str(p)
            if pid:
                ids.append(pid)

        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                sorted_pair = sorted([ids[i], ids[j]])
                pair: tuple[str, str] = (sorted_pair[0], sorted_pair[1])
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

    return pair_counts


def compute_per_persona_impact(
    records: list[dict[str, Any]]
) -> dict[str, dict[str, int]]:
    """Count supported/degraded impacts per persona."""
    impact_map: dict[str, dict[str, int]] = {}

    for record in records:
        personas = record.get('personas', [])
        if not isinstance(personas, list):
            continue
        for p in personas:
            if not isinstance(p, dict):
                continue
            pid = p.get('id', '')
            impact = p.get('impact', '')
            if not pid:
                continue
            if pid not in impact_map:
                impact_map[pid] = {'supported': 0, 'degraded': 0, 'neutral': 0}
            if impact in impact_map[pid]:
                impact_map[pid][impact] += 1

    return impact_map


def scan_persona_vcd_blocks(project_root: Path) -> list[dict[str, str]]:
    """Extract vcd: YAML blocks from persona files."""
    personas_dir = project_root / 'requirements_user_needs' / 'personas'
    if not personas_dir.exists():
        return []

    entries = []
    for persona_dir in sorted(personas_dir.iterdir()):
        if not persona_dir.is_dir():
            continue
        persona_file = persona_dir / 'persona.md'
        if not persona_file.exists():
            continue
        try:
            doc = read_frontmatter(persona_file)
        except (FrontmatterError, OSError):
            continue

        meta = dict(doc.metadata) if doc.has_frontmatter else {}

        persona_id = meta.get('persona_id', '')
        persona_name = meta.get('name', persona_dir.name)
        vcd = meta.get('vcd', {})

        if not persona_id:
            continue

        if isinstance(vcd, dict):
            primary = vcd.get('primary_value', '')
            if isinstance(primary, dict):
                primary = primary.get('name', str(primary))
            secondary = vcd.get('secondary_values', [])
            if isinstance(secondary, list):
                parts = []
                for s in secondary:
                    if isinstance(s, dict):
                        parts.append(s.get('name', str(s)))
                    else:
                        parts.append(str(s))
                secondary_str = ', '.join(parts)
            else:
                secondary_str = str(secondary)
            entries.append({
                'id': str(persona_id),
                'name': str(persona_name),
                'primary_value': str(primary) if primary else '—',
                'secondary_values': secondary_str or '—',
            })

    return entries


# ---------------------------------------------------------------------------
# Output Generation
# ---------------------------------------------------------------------------

def generate_summary(records: list[dict[str, Any]], project_root: Path) -> str:
    """Generate value_tradeoff_summary.md content."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    decided = [r for r in records if r.get('decision_status') == 'decided']
    open_records = [r for r in records if r.get('decision_status') != 'decided']

    lines: list[str] = []
    lines.append('# Value Trade-off Summary')
    lines.append('')
    lines.append(
        '> Do NOT edit this file manually. '
        'Run: `python scripts/aggregate_value_tradeoffs.py`'
    )
    lines.append(f'> Last updated: {now}')
    lines.append(
        f'> Total records: {len(records)} '
        f'({len(decided)} decided, {len(open_records)} open)'
    )
    lines.append('')

    # Open items
    lines.append('## Open Items (requires user decision)')
    lines.append('')
    if open_records:
        lines.append('| ID | Date | Artifact | Personas & Values |')
        lines.append('|---|---|---|---|')
        for r in open_records:
            rid = r.get('id', '?')
            date = r.get('date', '?')
            artifact = r.get('artifact', '?')
            personas = r.get('personas', [])
            persona_str = (
                '; '.join(_persona_display(p) for p in personas)
                if isinstance(personas, list)
                else ''
            )
            lines.append(f'| {rid} | {date} | `{artifact}` | {persona_str} |')
    else:
        lines.append('_No open items._')
    lines.append('')

    # All records chronological
    lines.append('## All Records (chronological)')
    lines.append('')
    if records:
        sorted_records = sorted(records, key=lambda r: str(r.get('date', '')))
        lines.append(
            '| ID | Date | Decision Status | Artifact | Personas | Value Impacts |'
        )
        lines.append('|---|---|---|---|---|---|')
        for r in sorted_records:
            rid = r.get('id', '?')
            date = r.get('date', '?')
            status = r.get('decision_status', '?')
            artifact = r.get('artifact', '?')
            personas = r.get('personas', [])
            if isinstance(personas, list):
                persona_ids = ', '.join(
                    p.get('id', '?') if isinstance(p, dict) else str(p)
                    for p in personas
                )
                impacts = '; '.join(
                    f"{p.get('value', '?')} [{p.get('impact', '?')}]"
                    if isinstance(p, dict)
                    else ''
                    for p in personas
                )
            else:
                persona_ids = ''
                impacts = ''
            lines.append(
                f'| {rid} | {date} | {status} | `{artifact}` | {persona_ids} | {impacts} |'
            )
    else:
        lines.append('_No records found._')
    lines.append('')

    # Conflict frequency matrix
    lines.append('## Conflict Frequency Matrix')
    lines.append('')
    lines.append('How often do persona pairs conflict?')
    lines.append('')
    pair_counts = build_conflict_matrix(records)
    if pair_counts:
        all_personas = sorted({pid for pair in pair_counts for pid in pair})
        header = '| | ' + ' | '.join(all_personas) + ' |'
        separator = '|---|' + '---|' * len(all_personas)
        lines.append(header)
        lines.append(separator)
        for pid in all_personas:
            row = f'| {pid} |'
            for pid2 in all_personas:
                if pid == pid2:
                    row += ' — |'
                else:
                    sorted_pair = sorted([pid, pid2])
                    pair: tuple[str, str] = (sorted_pair[0], sorted_pair[1])
                    count = pair_counts.get(pair, 0)
                    row += f' {count} |' if count else '   |'
            lines.append(row)
    else:
        lines.append('_No conflicts recorded yet._')
    lines.append('')

    # Per-persona impact summary
    lines.append('## Per-Persona Impact Summary')
    lines.append('')
    persona_impact = compute_per_persona_impact(records)
    if persona_impact:
        lines.append('| Persona | Values Supported | Values Degraded | Net Score |')
        lines.append('|---|---|---|---|')
        for pid, impact in sorted(persona_impact.items()):
            supported = impact.get('supported', 0)
            degraded = impact.get('degraded', 0)
            net = supported - degraded
            net_str = f'+{net}' if net > 0 else str(net)
            lines.append(f'| {pid} | {supported} | {degraded} | {net_str} |')
    else:
        lines.append('_No impact data yet._')
    lines.append('')

    # Persona value reference
    lines.append('## Persona Value Reference')
    lines.append('')
    lines.append('Extracted from persona `vcd:` YAML blocks:')
    lines.append('')
    persona_vcd = scan_persona_vcd_blocks(project_root)
    if persona_vcd:
        lines.append('| Persona | Primary Value | Secondary Values |')
        lines.append('|---|---|---|')
        for p in persona_vcd:
            lines.append(
                f"| {p['id']} ({p['name']}) | {p['primary_value']} | {p['secondary_values']} |"
            )
    else:
        lines.append('_No persona VCD data found._')
    lines.append('')

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    print('Scanning for Value Trade-off Records...')
    records = extract_vtr_records(project_root)

    if not records:
        print(
            'Warning: No VTR records found in any search directory.',
            file=sys.stderr,
        )
        print('Generating empty summary...')
        content = generate_summary([], project_root)
        out_file = project_root / OUTPUT_FILE
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content, encoding='utf-8')
        print(f'Written to {out_file}')
        sys.exit(2)

    print(f'Found {len(records)} record(s). Validating...')
    errors = validate_records(records)

    if errors:
        print(f'Validation errors ({len(errors)}):')
        for err in errors:
            print(f'  {err}')
        sys.exit(1)

    print('Generating summary...')
    content = generate_summary(records, project_root)
    out_file = project_root / OUTPUT_FILE
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(content, encoding='utf-8')
    print(f'Written to {out_file}')
    print('Done.')


if __name__ == '__main__':
    main()
