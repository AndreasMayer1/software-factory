#!/usr/bin/env python3
"""
User Needs Status Report Generator.

Generates status reports by parsing YAML frontmatter from persona, scenario,
and user flow files in the requirements_user_needs/ folder.

Usage:
    python scripts/generate_user_needs_status.py
    python scripts/generate_user_needs_status.py --output requirements_user_needs/STATUS.md

Output:
    requirements_user_needs/STATUS.md (default)
"""

# tier: C  # one-shot CLI artifact generator; no in-tree Python imports

import argparse
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]  # PyYAML lacks bundled stubs; types-PyYAML not in dev deps per TASK-PROC-051-04 scope

# Constants
DEFAULT_OUTPUT = "requirements_user_needs/STATUS.md"
USER_NEEDS_ROOT = "requirements_user_needs"

class UserNeedsStatusGenerator:
    """Generate status reports for user needs documents."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.personas: list[Any] = []
        self.scenarios: list[Any] = []
        self.flows: list[Any] = []
        self.scenario_index: Any = None
        self.scenario_ideas: list[Any] = []
        self.flow_ideas: list[Any] = []

    def scan_documents(self) -> None:
        """Scan all persona, scenario, and flow documents."""
        # Parse SCENARIO_INDEX.md first (also populates self.scenario_ideas)
        self._parse_scenario_index()
        # Parse FLOW_INDEX.md for flow ideas
        self._parse_flow_index()

        personas_dir = self.root_dir / "personas"

        if not personas_dir.exists():
            print(f"Warning: {personas_dir} does not exist", file=sys.stderr)
            return

        # Scan each persona folder
        for persona_dir in personas_dir.iterdir():
            if not persona_dir.is_dir():
                continue

            # Parse persona.md
            persona_file = persona_dir / "persona.md"
            if persona_file.exists():
                persona_data = self._parse_document(persona_file, "persona")
                if persona_data:
                    persona_data['folder'] = persona_dir.name
                    self.personas.append(persona_data)

            # Scan scenarios
            scenarios_dir = persona_dir / "scenarios"
            if not scenarios_dir.exists():
                continue

            for scenario_dir in scenarios_dir.iterdir():
                if not scenario_dir.is_dir():
                    continue

                # Parse scenario.md
                scenario_file = scenario_dir / "scenario.md"
                if scenario_file.exists():
                    scenario_data = self._parse_document(scenario_file, "scenario")
                    if scenario_data:
                        scenario_data['folder'] = f"{persona_dir.name}/{scenario_dir.name}"
                        self.scenarios.append(scenario_data)

        # Scan user flows (now at root level under user_flows/)
        flows_root = self.root_dir / "user_flows"
        if flows_root.exists():
            for flow_dir in flows_root.iterdir():
                if not flow_dir.is_dir():
                    continue

                # Parse flow.md
                flow_file = flow_dir / "flow.md"
                if flow_file.exists():
                    flow_data = self._parse_document(flow_file, "flow")
                    if flow_data:
                        flow_data['folder'] = flow_dir.name
                        self.flows.append(flow_data)

    def _parse_scenario_index(self) -> None:
        """Parse SCENARIO_INDEX.md file."""
        index_file = self.root_dir / "SCENARIO_INDEX.md"

        if not index_file.exists():
            print(f"Warning: {index_file} does not exist", file=sys.stderr)
            return

        try:
            with open(index_file, encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter — split on '---' only at line boundaries
            # to avoid false matches inside YAML comments (e.g. "# --- comment ---")
            import re
            parts = re.split(r'(?m)^---\s*$', content, maxsplit=2)
            if len(parts) < 2:
                return

            self.scenario_index = yaml.safe_load(parts[1])
            if self.scenario_index:
                self.scenario_ideas = self.scenario_index.get('ideas', [])

        except Exception as e:
            print(f"Error parsing SCENARIO_INDEX.md: {e}", file=sys.stderr)

    def _parse_flow_index(self) -> None:
        """Parse FLOW_INDEX.md to extract flow ideas from the '## Flow Ideas' section."""
        import re
        index_file = self.root_dir / "user_flows" / "FLOW_INDEX.md"

        if not index_file.exists():
            print(f"Warning: {index_file} does not exist", file=sys.stderr)
            return

        try:
            with open(index_file, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading FLOW_INDEX.md: {e}", file=sys.stderr)
            return

        # Find the "## Flow Ideas" section
        ideas_start = content.find('\n## Flow Ideas\n')
        if ideas_start == -1:
            return

        ideas_section = content[ideas_start:]

        # Trim to next ## section if any
        next_h2 = ideas_section.find('\n## ', 1)
        if next_h2 != -1:
            ideas_section = ideas_section[:next_h2]

        current_phase = None
        current_idea = None

        for line in ideas_section.split('\n'):
            phase_match = re.match(r'^### (Phase .+)', line)
            if phase_match:
                current_phase = phase_match.group(1).strip()
                continue

            idea_match = re.match(r'^#### Idea: (.+)', line)
            if idea_match:
                if current_idea:
                    self.flow_ideas.append(current_idea)
                current_idea = {
                    'name': idea_match.group(1).strip(),
                    'phase': current_phase or 'Unknown',
                    'brainstorm_ref': '',
                    'purpose': '',
                    'personas': '',
                    'evaluation_notes': '',
                    'high_priority': False,
                }
                continue

            if current_idea is None:
                continue

            m = re.match(r'^- \*\*Brainstorm ref\*\*: (.+)', line)
            if m:
                current_idea['brainstorm_ref'] = m.group(1).strip()
                continue

            m = re.match(r'^- \*\*Purpose\*\*: (.+)', line)
            if m:
                current_idea['purpose'] = m.group(1).strip()
                continue

            m = re.match(r'^- \*\*Personas\*\*: (.+)', line)
            if m:
                current_idea['personas'] = m.group(1).strip()
                continue

            m = re.match(r'^- \*\*Evaluation notes\*\*: (.+)', line)
            if m:
                current_idea['evaluation_notes'] = m.group(1).strip()
                if '**HIGH PRIORITY**' in str(current_idea['evaluation_notes']):
                    current_idea['high_priority'] = True
                continue

        if current_idea:
            self.flow_ideas.append(current_idea)

    def _parse_document(self, file_path: Path, doc_type: str) -> dict[Any, Any] | None:
        """Parse YAML frontmatter from a document."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter — split on '---' only at line boundaries
            # to avoid false matches inside YAML comments (e.g. "# --- comment ---")
            import re
            parts = re.split(r'(?m)^---\s*$', content, maxsplit=2)
            if len(parts) < 3:
                return None

            frontmatter = yaml.safe_load(parts[1])
            if not frontmatter:
                return None

            # Add file info
            frontmatter['_file_path'] = str(file_path.relative_to(self.root_dir))
            frontmatter['_doc_type'] = doc_type
            frontmatter['_modified'] = datetime.fromtimestamp(file_path.stat().st_mtime)

            return cast("dict[Any, Any]", frontmatter)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}", file=sys.stderr)
            return None

    def _extract_epic_references(self, content: str) -> list[Any]:
        """Extract epic IDs from flow content."""
        import re
        matches = re.findall(r'(REQ-[A-Z]+-\d{3}|EPIC-[A-Z]+-\d{3})', content)
        return list(set(matches))

    def _find_epic_path(self, epic_id: str) -> Any:
        """Find path to epic requirements.md file."""
        req_root = self.root_dir.parent / "requirements_tasks"
        if not req_root.exists():
            return None

        for req_file in req_root.rglob("requirements.md"):
            try:
                with open(req_file, encoding='utf-8') as f:
                    content = f.read()
                if f"id: {epic_id}" in content or f"id: '{epic_id}'" in content:
                    return req_file
            except Exception:
                continue
        return None

    def _epic_references_flow(self, epic_path: Path, flow_id: str) -> bool:
        """Check if epic references the given flow in user_needs field."""
        try:
            with open(epic_path, encoding='utf-8') as f:
                content = f.read()
            return flow_id in content
        except Exception:
            return False

    def validate_cross_references(self) -> Any:
        """Validate all cross-references in user needs documents."""
        issues = []

        # Validate flow → epic references
        for flow in self.flows:
            flow_id = flow.get('flow_id', 'UNKNOWN')

            # Parse implementing epics from flow content
            flow_file = self.root_dir / flow['_file_path']
            try:
                with open(flow_file, encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            # Extract epic references
            epic_refs = self._extract_epic_references(content)

            # Check if epic files exist
            for epic_id in epic_refs:
                epic_path = self._find_epic_path(epic_id)
                if not epic_path:
                    issues.append({
                        'type': 'flow_to_epic',
                        'source': flow_id,
                        'issue': f"References non-existent epic: {epic_id}",
                        'severity': 'error'
                    })
                else:
                    # Check if epic references flow back
                    if not self._epic_references_flow(epic_path, flow_id):
                        issues.append({
                            'type': 'flow_to_epic',
                            'source': flow_id,
                            'issue': f"Epic {epic_id} doesn't reference flow back (asymmetric)",
                            'severity': 'warning'
                        })

        # Validate bidirectional scenario ↔ flow references
        bidirectional_issues = self._validate_bidirectional_flow_scenario()
        issues.extend(bidirectional_issues)

        return issues

    def _validate_bidirectional_flow_scenario(self) -> Any:
        """Check scenario ↔ flow bidirectional consistency."""
        issues = []

        # Build lookup maps
        flows_by_id = {f.get('flow_id'): f for f in self.flows if f.get('flow_id')}
        scenarios_by_id = {s.get('scenario_id'): s for s in self.scenarios if s.get('scenario_id')}

        # Check scenarios → flows
        for scenario in self.scenarios:
            scenario_id = scenario.get('scenario_id', 'UNKNOWN')
            implements_flows = scenario.get('implements_flows', [])

            if not implements_flows:
                # Warning: scenario has no flows
                issues.append({
                    'type': 'orphan_scenario',
                    'source': scenario_id,
                    'issue': "Scenario has no flows (implements_flows is empty)",
                    'severity': 'warning'
                })

            for flow_ref in implements_flows:
                flow_id = flow_ref.get('flow_id') if isinstance(flow_ref, dict) else flow_ref
                if not flow_id:
                    continue

                # Check if flow exists
                flow = flows_by_id.get(flow_id)
                if not flow:
                    issues.append({
                        'type': 'scenario_to_flow',
                        'source': scenario_id,
                        'issue': f"References non-existent flow: {flow_id}",
                        'severity': 'error'
                    })
                else:
                    # Check if flow references scenario back
                    serves_scenarios = flow.get('serves_scenarios', [])
                    scenario_referenced = any(
                        s.get('scenario_id') == scenario_id if isinstance(s, dict) else s == scenario_id
                        for s in serves_scenarios
                    )

                    if not scenario_referenced:
                        issues.append({
                            'type': 'scenario_to_flow',
                            'source': scenario_id,
                            'issue': f"Flow {flow_id} doesn't reference scenario back (asymmetric)",
                            'severity': 'warning'
                        })

        # Check flows → scenarios
        for flow in self.flows:
            flow_id = flow.get('flow_id', 'UNKNOWN')
            serves_scenarios = flow.get('serves_scenarios', [])

            if not serves_scenarios:
                # Warning: orphan flow (not serving any scenario)
                issues.append({
                    'type': 'orphan_flow',
                    'source': flow_id,
                    'issue': "Flow not serving any scenario (serves_scenarios is empty)",
                    'severity': 'warning'
                })

            for scenario_ref in serves_scenarios:
                scenario_id = scenario_ref.get('scenario_id') if isinstance(scenario_ref, dict) else scenario_ref
                if not scenario_id:
                    continue

                # Check if scenario exists
                scenario = scenarios_by_id.get(scenario_id)
                if not scenario:
                    issues.append({
                        'type': 'flow_to_scenario',
                        'source': flow_id,
                        'issue': f"References non-existent scenario: {scenario_id}",
                        'severity': 'error'
                    })
                else:
                    # Check if scenario references flow back
                    implements_flows = scenario.get('implements_flows', [])
                    flow_referenced = any(
                        f.get('flow_id') == flow_id if isinstance(f, dict) else f == flow_id
                        for f in implements_flows
                    )

                    if not flow_referenced:
                        issues.append({
                            'type': 'flow_to_scenario',
                            'source': flow_id,
                            'issue': f"Scenario {scenario_id} doesn't reference flow back (asymmetric)",
                            'severity': 'warning'
                        })

        return issues

    def generate_report(self) -> str:
        """Generate the status report."""
        lines = []
        lines.append("# User Needs Status Report")
        lines.append("")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Summary statistics
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Personas**: {len(self.personas)}")
        lines.append(f"- **Total Scenarios**: {len(self.scenarios)}")
        lines.append(f"- **Total User Flows**: {len(self.flows)}")
        high_scen_ideas = sum(1 for i in self.scenario_ideas if i.get('priority') == 'high')
        lines.append(f"- **Scenario Ideas**: {len(self.scenario_ideas)} ({high_scen_ideas} high priority)")
        high_flow_ideas = sum(1 for i in self.flow_ideas if i.get('high_priority'))
        lines.append(f"- **Flow Ideas**: {len(self.flow_ideas)} ({high_flow_ideas} high priority)")
        lines.append("")

        # Scenario + flow ideas sections
        lines.extend(self._generate_scenario_ideas())
        lines.extend(self._generate_flow_ideas())

        # NEW: Scenario Category Coverage
        lines.extend(self._generate_scenario_category_coverage())

        # NEW: Implementation progress
        lines.extend(self._generate_implementation_progress())

        # Review status breakdown
        lines.extend(self._generate_status_summary())

        # NEW: Epic coverage
        lines.extend(self._generate_epic_coverage())

        # NEW: Orphan flows
        lines.extend(self._generate_orphan_flows())

        # NEW: Cross-reference warnings
        issues = self.validate_cross_references()
        if issues:
            lines.append("## Cross-Reference Warnings")
            lines.append("")

            # Group issues by type
            flow_to_epic = [i for i in issues if i.get('type') == 'flow_to_epic']
            scenario_to_flow = [i for i in issues if i.get('type') == 'scenario_to_flow']
            flow_to_scenario = [i for i in issues if i.get('type') == 'flow_to_scenario']
            orphan_flows = [i for i in issues if i.get('type') == 'orphan_flow']
            orphan_scenarios = [i for i in issues if i.get('type') == 'orphan_scenario']

            # Bidirectional Reference Warnings (Scenario ↔ Flow)
            if scenario_to_flow or flow_to_scenario or orphan_flows or orphan_scenarios:
                lines.append("### Bidirectional Reference Warnings (Scenario ↔ Flow)")
                lines.append("")

                if orphan_scenarios:
                    lines.append("**Orphan Scenarios** (no flows):")
                    for issue in orphan_scenarios:
                        lines.append(f"- ⚠️ {issue['source']}: {issue['issue']}")
                    lines.append("")

                if orphan_flows:
                    lines.append("**Orphan Flows** (not serving any scenario):")
                    for issue in orphan_flows:
                        lines.append(f"- ⚠️ {issue['source']}: {issue['issue']}")
                    lines.append("")

                if scenario_to_flow:
                    lines.append("**Scenario → Flow Issues:**")
                    for issue in scenario_to_flow:
                        severity_marker = "⚠️" if issue['severity'] == 'warning' else "❌"
                        lines.append(f"- {severity_marker} {issue['source']}: {issue['issue']}")
                    lines.append("")

                if flow_to_scenario:
                    lines.append("**Flow → Scenario Issues:**")
                    for issue in flow_to_scenario:
                        severity_marker = "⚠️" if issue['severity'] == 'warning' else "❌"
                        lines.append(f"- {severity_marker} {issue['source']}: {issue['issue']}")
                    lines.append("")

            # Flow → Epic Warnings
            if flow_to_epic:
                lines.append("### Flow → Epic Reference Warnings")
                lines.append("")
                for issue in flow_to_epic:
                    severity_marker = "⚠️" if issue['severity'] == 'warning' else "❌"
                    lines.append(f"- {severity_marker} {issue['source']}: {issue['issue']}")
                lines.append("")

        # Documents by status
        lines.extend(self._generate_documents_by_status())

        # Recently modified
        lines.extend(self._generate_recently_modified())

        # Pending review
        lines.extend(self._generate_pending_review())

        return "\n".join(lines)

    def _generate_scenario_ideas(self) -> list[Any]:
        """Generate scenario ideas evaluation queue section."""
        lines = []
        lines.append("## Scenario Ideas (Evaluation Queue)")
        lines.append("")

        if not self.scenario_ideas:
            lines.append("*No scenario ideas in queue*")
            lines.append("")
            return lines

        by_status = defaultdict(list)
        for idea in self.scenario_ideas:
            by_status[idea.get('status', 'proposed')].append(idea)

        by_priority = defaultdict(list)
        for idea in by_status.get('proposed', []):
            by_priority[idea.get('priority', 'medium')].append(idea)

        if by_priority:
            lines.append("### Proposed")
            lines.append("")
            for priority in ['high', 'medium', 'low']:
                ideas = by_priority.get(priority, [])
                if not ideas:
                    continue
                lines.append(f"**{priority.title()} Priority** ({len(ideas)}):")
                for idea in ideas:
                    name = idea.get('idea', 'Unnamed')
                    category = idea.get('category', 'unknown')
                    personas = idea.get('suggested_personas', [])
                    persona_str = ", ".join(str(p) for p in personas) if personas else "—"
                    related = idea.get('related_flow_idea', '')
                    lines.append(f"- **{name}** `[{category}]`")
                    lines.append(f"  - Personas: {persona_str}")
                    if related:
                        lines.append(f"  - Related flow: {related}")
                lines.append("")

        accepted = by_status.get('accepted', [])
        if accepted:
            lines.append(f"### Accepted ({len(accepted)}) → ready for `create-scenario`")
            lines.append("")
            for idea in accepted:
                lines.append(f"- {idea.get('idea', 'Unnamed')}")
            lines.append("")

        declined = by_status.get('declined', [])
        if declined:
            lines.append(f"### Declined ({len(declined)})")
            lines.append("")
            for idea in declined:
                lines.append(f"- ~~{idea.get('idea', 'Unnamed')}~~")
            lines.append("")

        return lines

    def _generate_flow_ideas(self) -> list[Any]:
        """Generate flow ideas brainstorming section."""
        lines = []
        lines.append("## Flow Ideas (Brainstorming)")
        lines.append("")

        if not self.flow_ideas:
            lines.append("*No flow ideas found in FLOW_INDEX.md*")
            lines.append("")
            return lines

        high_count = sum(1 for i in self.flow_ideas if i.get('high_priority'))
        lines.append(f"**Total**: {len(self.flow_ideas)} ideas | **High Priority**: {high_count}")
        lines.append("")

        by_phase = defaultdict(list)
        for idea in self.flow_ideas:
            by_phase[idea.get('phase', 'Unknown')].append(idea)

        for phase in sorted(by_phase.keys()):
            ideas = by_phase[phase]
            lines.append(f"### {phase}")
            lines.append("")
            for idea in ideas:
                priority_marker = " ⚡" if idea.get('high_priority') else ""
                ref = idea.get('brainstorm_ref', '')
                ref_str = f" ({ref})" if ref else ""
                lines.append(f"- **{idea['name']}**{priority_marker}{ref_str}")
                if idea.get('personas'):
                    lines.append(f"  - Personas: {idea['personas']}")
            lines.append("")

        return lines

    def _generate_status_summary(self) -> list[Any]:
        """Generate review status summary."""
        lines = []
        lines.append("## Review Status Summary")
        lines.append("")

        # Count by status
        status_counts: dict[Any, dict[str, int]] = defaultdict(lambda: {'personas': 0, 'scenarios': 0, 'flows': 0})

        for persona in self.personas:
            status = persona.get('review_status', 'unknown')
            status_counts[status]['personas'] += 1

        for scenario in self.scenarios:
            status = scenario.get('review_status', 'unknown')
            status_counts[status]['scenarios'] += 1

        for flow in self.flows:
            status = flow.get('review_status', 'unknown')
            status_counts[status]['flows'] += 1

        # Table
        lines.append("| Status | Personas | Scenarios | Flows | Total |")
        lines.append("|--------|----------|-----------|-------|-------|")

        for status in ['draft', 'in_review', 'pending_alignment', 'approved', 'deprecated', 'unknown']:
            counts = status_counts[status]
            total = counts['personas'] + counts['scenarios'] + counts['flows']
            if total > 0:
                lines.append(f"| {status} | {counts['personas']} | {counts['scenarios']} | {counts['flows']} | {total} |")

        lines.append("")
        return lines

    def _generate_documents_by_status(self) -> list[Any]:
        """Generate lists of documents grouped by status."""
        lines = []
        lines.append("## Documents by Status")
        lines.append("")

        all_docs = []
        all_docs.extend([(d, 'Persona') for d in self.personas])
        all_docs.extend([(d, 'Scenario') for d in self.scenarios])
        all_docs.extend([(d, 'Flow') for d in self.flows])

        # Group by status
        by_status = defaultdict(list)
        for doc, doc_label in all_docs:
            status = doc.get('review_status', 'unknown')
            by_status[status].append((doc, doc_label))

        # Output each status group
        for status in ['draft', 'in_review', 'pending_alignment', 'approved', 'deprecated', 'unknown']:
            docs = by_status[status]
            if not docs:
                continue

            lines.append(f"### {status.replace('_', ' ').title()}")
            lines.append("")

            for doc, doc_label in sorted(docs, key=lambda x: x[0].get('_file_path', '')):
                doc_id = self._get_doc_id(doc)
                name = doc.get('name', 'Unnamed')
                lines.append(f"- **{doc_id}** ({doc_label}): {name}")
                lines.append(f"  - Path: `{doc['_file_path']}`")
                lines.append(f"  - Last modified: {doc['_modified'].strftime('%Y-%m-%d')}")
                lines.append("")

        return lines

    def _generate_recently_modified(self) -> list[Any]:
        """Generate list of recently modified documents."""
        lines = []
        lines.append("## Recently Modified (Last 7 Days)")
        lines.append("")

        all_docs = []
        all_docs.extend([(d, 'Persona') for d in self.personas])
        all_docs.extend([(d, 'Scenario') for d in self.scenarios])
        all_docs.extend([(d, 'Flow') for d in self.flows])

        # Filter and sort by modification time
        now = datetime.now()
        recent_docs = [
            (doc, doc_label)
            for doc, doc_label in all_docs
            if (now - doc['_modified']).days <= 7
        ]
        recent_docs.sort(key=lambda x: x[0]['_modified'], reverse=True)

        if not recent_docs:
            lines.append("*No documents modified in the last 7 days*")
            lines.append("")
        else:
            for doc, doc_label in recent_docs:
                doc_id = self._get_doc_id(doc)
                name = doc.get('name', 'Unnamed')
                status = doc.get('review_status', 'unknown')
                lines.append(f"- **{doc_id}** ({doc_label}): {name}")
                lines.append(f"  - Status: {status}")
                lines.append(f"  - Modified: {doc['_modified'].strftime('%Y-%m-%d %H:%M')}")
                lines.append(f"  - Path: `{doc['_file_path']}`")
                lines.append("")

        return lines

    def _generate_pending_review(self) -> list[Any]:
        """Generate list of documents pending review."""
        lines = []
        lines.append("## Pending Review")
        lines.append("")

        all_docs = []
        all_docs.extend([(d, 'Persona') for d in self.personas])
        all_docs.extend([(d, 'Scenario') for d in self.scenarios])
        all_docs.extend([(d, 'Flow') for d in self.flows])

        # Filter in_review status
        pending = [
            (doc, doc_label)
            for doc, doc_label in all_docs
            if doc.get('review_status') == 'in_review'
        ]

        if not pending:
            lines.append("*No documents pending review*")
            lines.append("")
        else:
            for doc, doc_label in sorted(pending, key=lambda x: x[0].get('_file_path', '')):
                doc_id = self._get_doc_id(doc)
                name = doc.get('name', 'Unnamed')

                # Get last review history entry
                review_history = doc.get('review_history', [])
                if review_history:
                    last_review = review_history[-1]
                    reviewer = last_review.get('reviewer', 'unknown')
                    date = last_review.get('date', 'unknown')
                    notes = last_review.get('notes', '')
                else:
                    reviewer = 'unknown'
                    date = 'unknown'
                    notes = ''

                lines.append(f"- **{doc_id}** ({doc_label}): {name}")
                lines.append(f"  - Submitted by: {reviewer} on {date}")
                if notes:
                    lines.append(f"  - Notes: {notes}")
                lines.append(f"  - Path: `{doc['_file_path']}`")
                lines.append("")

        return lines

    def _generate_scenario_category_coverage(self) -> list[Any]:
        """Generate scenario category coverage tables by stage."""
        lines = []
        lines.append("## Scenario Category Coverage")
        lines.append("")

        if not self.scenario_index:
            lines.append("*SCENARIO_INDEX.md not found or could not be parsed*")
            lines.append("")
            return lines

        # Build persona_id → role mapping
        persona_roles = {}
        for persona in self.personas:
            persona_id = persona.get('persona_id')
            role = persona.get('role', 'unknown')
            if persona_id:
                persona_roles[persona_id] = role

        # Sort personas for consistent column order
        sorted_personas = sorted(self.personas, key=lambda p: p.get('persona_id', ''))

        stages = self.scenario_index.get('stages', [])

        for stage in stages:
            stage_display = stage.get('display_name', 'Unknown Stage')
            categories = stage.get('categories', [])

            if not categories:
                continue

            lines.append(f"### {stage_display}")
            lines.append("")

            # Table header
            header_row = "| Category |"
            separator_row = "|----------|"

            for persona in sorted_personas:
                persona_name = persona.get('name', 'Unknown')
                persona_id = persona.get('persona_id', '')

                # Remove archetype suffix in parentheses (e.g., "(The Rapid Monitor)")
                if '(' in persona_name:
                    persona_name = persona_name.split('(')[0].strip()

                # Create readable short name
                # Special handling for titles (Dr., Prof.)
                if persona_name.startswith('Prof. Dr. '):
                    # Extract last name after "Prof. Dr. "
                    parts = persona_name.split()
                    if len(parts) >= 3:
                        short_name = f"Prof. {parts[2]}"
                    else:
                        short_name = persona_name
                elif persona_name.startswith('Dr. med. '):
                    # Extract last name after "Dr. med. "
                    parts = persona_name.split()
                    short_name = f"Dr. {parts[2]}" if len(parts) >= 3 else persona_name
                elif persona_name.startswith('Dr. '):
                    # Extract last name after "Dr. "
                    parts = persona_name.split()
                    short_name = f"Dr. {parts[1]}" if len(parts) >= 2 else persona_name
                else:
                    # Use first name for clients
                    short_name = persona_name.split()[0] if persona_name else 'Unknown'

                header_row += f" {short_name} |"
                separator_row += "------|"

            lines.append(header_row)
            lines.append(separator_row)

            # Table rows (one per category)
            for category in categories:
                category_display = category.get('display_name', 'Unknown')
                applicable_roles = [r.get('role') for r in category.get('applicable_roles', [])]
                instances = category.get('instances', [])

                row = f"| {category_display} |"

                for persona in sorted_personas:
                    persona_id = persona.get('persona_id')
                    persona_role = persona_roles.get(persona_id, 'unknown')

                    # Find instance for this persona in this category
                    persona_instances = [
                        inst for inst in instances
                        if inst.get('persona_id') == persona_id
                    ]

                    if persona_instances:
                        # Persona has scenario(s) in this category
                        # Show all scenarios (may be multiple)
                        scenario_labels = []
                        for inst in persona_instances:
                            scenario_id = inst.get('scenario_id', 'SCEN-???')
                            is_gold = inst.get('gold_status', False)
                            if is_gold:
                                scenario_labels.append(f"⭐ {scenario_id}")
                            else:
                                scenario_labels.append(f"✓ {scenario_id}")
                        cell_value = "<br>".join(scenario_labels)
                    else:
                        # No scenario for this persona
                        # Check if category is applicable for this persona's role
                        cell_value = "🔲" if persona_role in applicable_roles else "—"

                    row += f" {cell_value} |"

                lines.append(row)

            lines.append("")
            lines.append("**Legend**: ⭐ = Gold standard | ✓ = Exists | 🔲 = Applicable (missing) | — = Not applicable")
            lines.append("")

        return lines

    def _generate_implementation_progress(self) -> list[Any]:
        """Generate implementation progress report."""
        lines = []
        lines.append("## Implementation Progress")
        lines.append("")

        if not self.flows:
            lines.append("*No flows found*")
            lines.append("")
            return lines

        # Count by implementation_status
        status_counts: dict[Any, int] = defaultdict(int)
        for flow in self.flows:
            status = flow.get('implementation_status', 'unknown')
            status_counts[status] += 1

        total = len(self.flows)
        complete = status_counts.get('complete', 0)
        partial = status_counts.get('partial', 0)
        not_started = status_counts.get('not_started', 0)

        complete_pct = (complete / total * 100) if total > 0 else 0
        partial_pct = (partial / total * 100) if total > 0 else 0
        not_started_pct = (not_started / total * 100) if total > 0 else 0

        lines.append(f"**Total Flows**: {total}")
        lines.append("")
        lines.append(f"- Complete: {complete} ({complete_pct:.1f}%)")
        lines.append(f"- Partial: {partial} ({partial_pct:.1f}%)")
        lines.append(f"- Not Started: {not_started} ({not_started_pct:.1f}%)")
        lines.append("")

        # Progress bar (ASCII)
        bar_width = 50
        complete_width = int(complete_pct / 100 * bar_width)
        partial_width = int(partial_pct / 100 * bar_width)

        bar = "█" * complete_width + "▓" * partial_width + "░" * (bar_width - complete_width - partial_width)
        lines.append(f"```\n{bar}\n```")
        lines.append("")

        return lines

    def _generate_epic_coverage(self) -> list[Any]:
        """Generate epic/feature coverage report."""
        lines = []
        lines.append("## Epic/Feature Coverage")
        lines.append("")

        # Build mapping: epic_id -> flows it implements
        epic_to_flows = defaultdict(list)

        for flow in self.flows:
            flow_id = flow.get('flow_id', 'UNKNOWN')
            flow_name = flow.get('name', 'Unnamed')
            impl_status = flow.get('implementation_status', 'unknown')

            # Extract epic references from flow
            flow_file = self.root_dir / flow['_file_path']
            try:
                with open(flow_file, encoding='utf-8') as f:
                    content = f.read()
                epic_refs = self._extract_epic_references(content)

                for epic_id in epic_refs:
                    epic_to_flows[epic_id].append({
                        'flow_id': flow_id,
                        'flow_name': flow_name,
                        'impl_status': impl_status
                    })
            except Exception:
                continue

        if not epic_to_flows:
            lines.append("*No epic/feature coverage mappings found*")
            lines.append("")
            return lines

        # Generate table
        lines.append("| Epic/Feature | Flows Implemented | Implementation Status |")
        lines.append("|--------------|-------------------|----------------------|")

        for epic_id in sorted(epic_to_flows.keys()):
            flows = epic_to_flows[epic_id]
            flow_list = ", ".join([f"{f['flow_id']}" for f in flows])

            # Calculate aggregate status
            statuses = [f['impl_status'] for f in flows]
            if all(s == 'complete' for s in statuses):
                agg_status = "complete"
            elif all(s == 'not_started' for s in statuses):
                agg_status = "not_started"
            else:
                agg_status = "partial"

            lines.append(f"| {epic_id} | {flow_list} | {agg_status} |")

        lines.append("")
        return lines

    def _generate_orphan_flows(self) -> list[Any]:
        """Generate list of flows not referenced by any epic (implementation gap)."""
        import re
        lines = []
        lines.append("## Implementation Gaps (Flows Not Referenced by Any Epic)")
        lines.append("")

        orphans = []

        # Build set of all epics that reference flows
        referenced_flows = set()

        req_root = self.root_dir.parent / "requirements_tasks"
        if req_root.exists():
            for req_file in req_root.rglob("requirements.md"):
                try:
                    with open(req_file, encoding='utf-8') as f:
                        content = f.read()

                    # Extract FLOW-XXX references (new format) and FLOW-XXX-XX-XX (old format)
                    flow_refs = re.findall(r'FLOW-\d{3}(?:-\d{2}-\d{2})?', content)
                    referenced_flows.update(flow_refs)
                except Exception:
                    continue

        # Find flows with no epic references
        for flow in self.flows:
            flow_id = flow.get('flow_id', 'UNKNOWN')
            if flow_id not in referenced_flows:
                orphans.append({
                    'flow_id': flow_id,
                    'flow_name': flow.get('name', 'Unnamed'),
                    'impl_status': flow.get('implementation_status', 'unknown')
                })

        if not orphans:
            lines.append("*All flows have at least one epic implementing them*")
            lines.append("")
        else:
            lines.append("**Note**: These flows serve scenarios but don't have implementation epics yet.")
            lines.append("")
            for orphan in sorted(orphans, key=lambda x: x['flow_id']):
                lines.append(f"- **{orphan['flow_id']}** ({orphan['flow_name']}) - Status: {orphan['impl_status']}")
            lines.append("")

        return lines

    def _get_doc_id(self, doc: dict[Any, Any]) -> str:
        """Extract document ID based on type."""
        doc_type = doc['_doc_type']

        if doc_type == 'persona':
            return cast("str", doc.get('persona_id', 'UNKNOWN'))
        if doc_type == 'scenario':
            return cast("str", doc.get('scenario_id', 'UNKNOWN'))
        if doc_type == 'flow':
            return cast("str", doc.get('flow_id', 'UNKNOWN'))
        return 'UNKNOWN'


def git_commit(output_path: Path) -> None:
    project_root = output_path.parent
    while project_root != project_root.parent:
        if (project_root / ".git").exists():
            break
        project_root = project_root.parent

    rel = str(output_path.relative_to(project_root))
    subprocess.run(["git", "add", rel], cwd=project_root, check=True)

    status = subprocess.run(
        ["git", "status", "--porcelain", rel],
        cwd=project_root, check=True, capture_output=True, text=True,
    ).stdout

    if status.strip():
        message = (
            f"docs: Update {rel}\n\n"
            "Generated by scripts/artifacts/generate_user_needs_status.py"
        )
        subprocess.run(["git", "commit", "-m", message], cwd=project_root, check=True)
        print(f"Committed {rel}")
    else:
        print(f"No changes to commit ({rel} is up to date)")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate status report for user needs documents'
    )
    parser.add_argument(
        '--output',
        default=DEFAULT_OUTPUT,
        help=f'Output file path (default: {DEFAULT_OUTPUT})'
    )
    parser.add_argument(
        '--no-commit',
        action='store_true',
        help='Skip git commit (useful for testing).',
    )

    args = parser.parse_args()

    # Find project root (where requirements_user_needs/ exists)
    current = Path.cwd()
    root = None

    for path in [current, *list(current.parents)]:
        if (path / USER_NEEDS_ROOT).exists():
            root = path
            break

    if not root:
        print(f"Error: Could not find {USER_NEEDS_ROOT}/ folder", file=sys.stderr)
        sys.exit(1)

    # Generate report
    generator = UserNeedsStatusGenerator(str(root / USER_NEEDS_ROOT))
    generator.scan_documents()
    report = generator.generate_report()

    # Write output
    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Status report generated: {output_path}")
    print(f"  Personas: {len(generator.personas)}")
    print(f"  Scenarios: {len(generator.scenarios)}")
    print(f"  Flows: {len(generator.flows)}")
    print(f"  Scenario ideas: {len(generator.scenario_ideas)}")
    print(f"  Flow ideas: {len(generator.flow_ideas)}")

    if not args.no_commit:
        git_commit(output_path)


if __name__ == '__main__':
    main()
