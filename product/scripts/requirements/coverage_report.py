#!/usr/bin/env python3
"""
Coverage report generator for requirements and tasks.

Generates a markdown report showing:
- Coverage percentage per requirement
- Gaps (uncovered acceptance criteria/sections)
- Task-to-item mapping

Usage:
    python scripts/coverage_report.py [--output FILE] [--format md|json]

Output:
    Prints (or writes via --output) the coverage report in the requested format (md/json), covering progress per requirement, gaps, and task mapping.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Make scripts/util importable when invoked directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from io import StringIO

from ruamel.yaml import YAML
from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)


@dataclass
class TrackableItem:
    id: str
    text: str = ""
    covered_by: list[str] = field(default_factory=list)  # task_ids


@dataclass
class RequirementCoverage:
    id: str
    name: str
    path: str
    status: str
    acceptance_criteria: dict[str, TrackableItem] = field(default_factory=dict)
    sections: dict[str, TrackableItem] = field(default_factory=dict)

    @property
    def total_items(self) -> int:
        return len(self.acceptance_criteria) + len(self.sections)

    @property
    def covered_items(self) -> int:
        ac_covered = sum(1 for ac in self.acceptance_criteria.values() if ac.covered_by)
        sec_covered = sum(1 for sec in self.sections.values() if sec.covered_by)
        return ac_covered + sec_covered

    @property
    def coverage_percent(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.covered_items / self.total_items) * 100


@dataclass
class TaskInfo:
    task_id: str
    path: str
    parent_requirement: str
    status: str
    covers_ac: list[str] = field(default_factory=list)
    covers_sec: list[str] = field(default_factory=list)


class CoverageReporter:
    """Generates coverage reports for requirements."""

    REQUIREMENTS_ROOT = "requirements_tasks"

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.requirements: dict[str, RequirementCoverage] = {}
        self.tasks: dict[str, TaskInfo] = {}
        self.orphan_tasks: list[TaskInfo] = []  # Tasks without valid parent

    def parse_yaml_frontmatter(self, content: str) -> Optional[dict[str, Any]]:
        """Extract and parse YAML frontmatter from markdown content.

        Delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08).
        """
        if content.startswith('﻿'):
            content = content[1:]
        raw_yaml, _body = _split_frontmatter(content)
        if not raw_yaml.strip():
            return None
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.allow_duplicate_keys = True
        try:
            result = yaml.load(StringIO(raw_yaml))
        except Exception:
            return None
        if result is None or not isinstance(result, dict) or len(result) == 0:
            return None
        return dict(result)

    def _parse_value(self, value: str) -> Any:
        """Parse a YAML value string."""
        if not value:
            return ''
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        if value.isdigit():
            return int(value)
        if value.lower() in ('true', 'yes'):
            return True
        if value.lower() in ('false', 'no'):
            return False
        return value

    def extract_name_from_path(self, path: Path) -> str:
        """Extract a human-readable name from the requirement path."""
        # Get the parent folder name (e.g., "plan_evaluation_view")
        parent = path.parent.name
        # Convert snake_case to Title Case
        return parent.replace('_', ' ').title()

    def scan_requirements(self) -> None:
        """Scan all requirements.md files."""
        req_root = self.base_path / self.REQUIREMENTS_ROOT
        if not req_root.exists():
            return

        for req_file in req_root.rglob("requirements.md"):
            try:
                content = req_file.read_text(encoding='utf-8')
            except Exception:
                continue

            meta = self.parse_yaml_frontmatter(content)
            if meta is None:
                continue

            req_id = meta.get('id')
            if not req_id:
                continue

            # Extract trackable items
            trackable = meta.get('trackable_items', {})
            ac_items = {}
            sec_items = {}

            if isinstance(trackable, dict):
                for ac in trackable.get('acceptance_criteria', []):
                    if isinstance(ac, dict):
                        ac_id = ac.get('id', '')
                        ac_text = ac.get('text', '')
                        if ac_id:
                            ac_items[ac_id] = TrackableItem(id=ac_id, text=ac_text)
                    elif isinstance(ac, str):
                        ac_items[ac] = TrackableItem(id=ac)

                for sec in trackable.get('sections', []):
                    if isinstance(sec, dict):
                        sec_id = sec.get('id', '')
                        sec_name = sec.get('name', '')
                        if sec_id:
                            sec_items[sec_id] = TrackableItem(id=sec_id, text=sec_name)
                    elif isinstance(sec, str):
                        sec_items[sec] = TrackableItem(id=sec)

            self.requirements[req_id] = RequirementCoverage(
                id=req_id,
                name=self.extract_name_from_path(req_file),
                path=str(req_file),
                status=meta.get('status', 'unknown'),
                acceptance_criteria=ac_items,
                sections=sec_items
            )

    def scan_tasks(self) -> None:
        """Scan all goal.md files and link to requirements."""
        req_root = self.base_path / self.REQUIREMENTS_ROOT
        if not req_root.exists():
            return

        for goal_file in req_root.rglob("goal.md"):
            try:
                content = goal_file.read_text(encoding='utf-8')
            except Exception:
                continue

            meta = self.parse_yaml_frontmatter(content)
            if meta is None:
                continue

            task_id = meta.get('task_id')
            if not task_id:
                continue

            parent_req = meta.get('parent_requirement', '')
            covers = meta.get('covers', {})
            status = meta.get('status', 'unknown')

            covers_ac = covers.get('acceptance_criteria', []) if isinstance(covers, dict) else []
            covers_sec = covers.get('sections', []) if isinstance(covers, dict) else []

            task = TaskInfo(
                task_id=task_id,
                path=str(goal_file),
                parent_requirement=parent_req,
                status=status,
                covers_ac=covers_ac,
                covers_sec=covers_sec
            )

            self.tasks[task_id] = task

            # Link task to requirement's trackable items
            if parent_req in self.requirements:
                req = self.requirements[parent_req]
                for ac_id in covers_ac:
                    if ac_id in req.acceptance_criteria:
                        req.acceptance_criteria[ac_id].covered_by.append(task_id)
                for sec_id in covers_sec:
                    if sec_id in req.sections:
                        req.sections[sec_id].covered_by.append(task_id)
            elif parent_req:
                self.orphan_tasks.append(task)

    def generate_markdown_report(self) -> str:
        """Generate a markdown coverage report."""
        lines = [
            "# Requirements Coverage Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Summary",
            "",
        ]

        # Calculate overall stats
        total_reqs = len(self.requirements)
        total_items = sum(r.total_items for r in self.requirements.values())
        covered_items = sum(r.covered_items for r in self.requirements.values())
        overall_coverage = (covered_items / total_items * 100) if total_items > 0 else 0

        lines.extend([
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Requirements | {total_reqs} |",
            f"| Total Trackable Items | {total_items} |",
            f"| Covered Items | {covered_items} |",
            f"| Overall Coverage | {overall_coverage:.1f}% |",
            f"| Total Tasks | {len(self.tasks)} |",
            "",
            "---",
            "",
        ])

        # Coverage by category
        categories: dict[str, list[Any]] = {'FUNC': [], 'NFUNC': [], 'PROC': []}
        for req in self.requirements.values():
            if 'FUNC' in req.id and 'NFUNC' not in req.id:
                categories['FUNC'].append(req)
            elif 'NFUNC' in req.id:
                categories['NFUNC'].append(req)
            elif 'PROC' in req.id:
                categories['PROC'].append(req)

        for cat_name, cat_label in [('FUNC', 'Functional'), ('NFUNC', 'Non-Functional'), ('PROC', 'Process')]:
            reqs = categories[cat_name]
            if not reqs:
                continue

            cat_total = sum(r.total_items for r in reqs)
            cat_covered = sum(r.covered_items for r in reqs)
            cat_coverage = (cat_covered / cat_total * 100) if cat_total > 0 else 0

            lines.extend([
                f"## {cat_label} Requirements ({cat_name})",
                "",
                f"Category Coverage: **{cat_coverage:.1f}%** ({cat_covered}/{cat_total} items)",
                "",
                "| ID | Name | Status | Coverage | Items |",
                "|----|------|--------|----------|-------|",
            ])

            for req in sorted(reqs, key=lambda r: r.id):
                status_icon = self._get_status_icon(req.status)
                coverage_bar = self._get_coverage_bar(req.coverage_percent)
                lines.append(
                    f"| {req.id} | {req.name} | {status_icon} {req.status} | "
                    f"{coverage_bar} {req.coverage_percent:.0f}% | {req.covered_items}/{req.total_items} |"
                )

            lines.extend(["", ""])

        # Detailed coverage per requirement
        lines.extend([
            "---",
            "",
            "## Detailed Coverage by Requirement",
            "",
        ])

        for req in sorted(self.requirements.values(), key=lambda r: r.id):
            lines.extend([
                f"### {req.id}: {req.name}",
                "",
                f"- **Status**: {req.status}",
                f"- **Coverage**: {req.coverage_percent:.0f}% ({req.covered_items}/{req.total_items})",
                f"- **Path**: `{os.path.relpath(req.path, self.base_path)}`",
                "",
            ])

            # Acceptance criteria
            if req.acceptance_criteria:
                lines.append("**Acceptance Criteria:**")
                for ac_id, ac in sorted(req.acceptance_criteria.items()):
                    if ac.covered_by:
                        tasks = ", ".join(ac.covered_by)
                        lines.append(f"- [x] `{ac_id}`: {ac.text or '(no description)'} - *{tasks}*")
                    else:
                        lines.append(f"- [ ] `{ac_id}`: {ac.text or '(no description)'} - **GAP**")
                lines.append("")

            # Sections
            if req.sections:
                lines.append("**Sections:**")
                for sec_id, sec in sorted(req.sections.items()):
                    if sec.covered_by:
                        tasks = ", ".join(sec.covered_by)
                        lines.append(f"- [x] `{sec_id}`: {sec.text or '(no description)'} - *{tasks}*")
                    else:
                        lines.append(f"- [ ] `{sec_id}`: {sec.text or '(no description)'} - **GAP**")
                lines.append("")

            if not req.acceptance_criteria and not req.sections:
                lines.append("*No trackable items defined*")
                lines.append("")

            lines.append("")

        # Gaps summary
        gaps = []
        for req in self.requirements.values():
            for ac_id, ac in req.acceptance_criteria.items():
                if not ac.covered_by:
                    gaps.append((req.id, 'AC', ac_id, ac.text))
            for sec_id, sec in req.sections.items():
                if not sec.covered_by:
                    gaps.append((req.id, 'SEC', sec_id, sec.text))

        if gaps:
            lines.extend([
                "---",
                "",
                "## Coverage Gaps",
                "",
                f"Total gaps: **{len(gaps)}** items without task coverage",
                "",
                "| Requirement | Type | Item ID | Description |",
                "|-------------|------|---------|-------------|",
            ])
            for req_id, item_type, item_id, text in sorted(gaps):
                lines.append(f"| {req_id} | {item_type} | {item_id} | {text[:50]}{'...' if len(text) > 50 else ''} |")
            lines.append("")

        # Orphan tasks
        if self.orphan_tasks:
            lines.extend([
                "---",
                "",
                "## Orphan Tasks",
                "",
                "Tasks with invalid or missing parent_requirement:",
                "",
            ])
            for task in self.orphan_tasks:
                lines.append(f"- `{task.task_id}` -> `{task.parent_requirement}` (not found)")
            lines.append("")

        return '\n'.join(lines)

    def _get_status_icon(self, status: str) -> str:
        icons = {
            'draft': 'pencil2',
            'defined': 'clipboard',
            'in_progress': 'arrows_counterclockwise',
            'implemented': 'white_check_mark',
            'deprecated': 'wastebasket',
        }
        return icons.get(status, 'question')

    def _get_coverage_bar(self, percent: float) -> str:
        """Generate a simple text coverage bar."""
        filled = int(percent / 10)
        empty = 10 - filled
        return f"[{'#' * filled}{'-' * empty}]"

    def generate_json_report(self) -> str:
        """Generate a JSON coverage report."""
        data: dict[str, Any] = {
            'generated': datetime.now().isoformat(),
            'summary': {
                'total_requirements': len(self.requirements),
                'total_tasks': len(self.tasks),
                'total_items': sum(r.total_items for r in self.requirements.values()),
                'covered_items': sum(r.covered_items for r in self.requirements.values()),
            },
            'requirements': {},
            'tasks': {},
        }

        for req_id, req in self.requirements.items():
            data['requirements'][req_id] = {
                'name': req.name,
                'path': req.path,
                'status': req.status,
                'coverage_percent': req.coverage_percent,
                'total_items': req.total_items,
                'covered_items': req.covered_items,
                'acceptance_criteria': {
                    ac_id: {'text': ac.text, 'covered_by': ac.covered_by}
                    for ac_id, ac in req.acceptance_criteria.items()
                },
                'sections': {
                    sec_id: {'text': sec.text, 'covered_by': sec.covered_by}
                    for sec_id, sec in req.sections.items()
                },
            }

        for task_id, task in self.tasks.items():
            data['tasks'][task_id] = {
                'path': task.path,
                'parent_requirement': task.parent_requirement,
                'status': task.status,
                'covers_ac': task.covers_ac,
                'covers_sec': task.covers_sec,
            }

        return json.dumps(data, indent=2)

    def run(self, output_format: str = 'md', output_file: Optional[str] = None) -> None:
        """Run the coverage report generation."""
        print("Scanning requirements...")
        self.scan_requirements()
        print(f"  Found {len(self.requirements)} requirements with meta information")

        print("Scanning tasks...")
        self.scan_tasks()
        print(f"  Found {len(self.tasks)} tasks with meta information")

        print("\nGenerating report...")

        if output_format == 'json':
            report = self.generate_json_report()
        else:
            report = self.generate_markdown_report()

        if output_file:
            Path(output_file).write_text(report, encoding='utf-8')
            print(f"\nReport written to: {output_file}")
        else:
            print("\n" + report)


def main() -> None:
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    if not (project_root / "requirements_tasks").exists():
        print(f"Error: requirements_tasks/ not found in {project_root}")
        sys.exit(1)

    # Parse arguments
    output_format = 'md'
    output_file = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ('--output', '-o') and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] in ('--format', '-f') and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        else:
            i += 1

    reporter = CoverageReporter(project_root)
    reporter.run(output_format=output_format, output_file=output_file)


if __name__ == "__main__":
    main()
