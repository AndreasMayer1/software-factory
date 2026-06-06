#!/usr/bin/env python3
"""
Validation script for requirements and task meta information.

Validates:
- YAML frontmatter structure
- ID format and uniqueness
- covers references point to existing trackable_items

Usage:
    python scripts/validate_meta.py [--verbose]

Output:
    Prints one '<path>: <issue>' line per validation failure to stdout, ending with a summary count. --verbose adds per-file pass lines.
"""

# tier: C  # one-shot CLI requirements tool; no in-tree Python imports

import os
import re
import sys
from dataclasses import dataclass, field
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
class ValidationError:
    file_path: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class RequirementMeta:
    id: str
    path: str
    trackable_items: dict[str, list[str]] = field(default_factory=dict)
    # trackable_items = {"acceptance_criteria": ["AC-01", "AC-02"], "sections": ["SEC-01"]}
    target_release: Optional[str] = None


@dataclass
class TaskMeta:
    task_id: str
    path: str
    parent_requirement: str
    covers: dict[str, list[str]] = field(default_factory=dict)
    target_release: Optional[str] = None
    target_package: Optional[str] = None


@dataclass
class UserNeedsMeta:
    """Metadata for user needs documents (personas, scenarios, flows)."""
    id: str  # PERSONA-001, SCEN-001-01, FLOW-001-01-01
    doc_type: str  # persona, scenario, flow
    path: str
    review_status: str  # draft, in_review, approved, deprecated
    parent_id: Optional[str] = None  # For scenarios: persona_id, for flows: scenario_id

    # Flow-specific fields
    implementation_status: Optional[str] = None  # not_started, partial, complete
    implementing_epics: list[str] = field(default_factory=list)  # Epic IDs from flow.md table


class MetaValidator:
    """Validates meta information across requirements and tasks."""

    REQUIREMENTS_ROOT = "requirements_tasks"

    # Regex patterns for ID validation
    REQ_ID_PATTERN = re.compile(r'^REQ-(FUNC|NFUNC|PROC)-\d{3}(-\d{2})?$')
    TASK_ID_PATTERN = re.compile(r'^TASK-(FUNC|NFUNC|PROC)-\d{3}-\d{2}(-\d{2})?$')
    AC_ID_PATTERN = re.compile(r'^AC-\d{2}$')
    SEC_ID_PATTERN = re.compile(r'^SEC-\d{2}$')
    PERSONA_ID_PATTERN = re.compile(r'^PERSONA-\d{3}$')
    SCENARIO_ID_PATTERN = re.compile(r'^SCEN-\d{3}-\d{2}$')
    FLOW_ID_PATTERN = re.compile(r'^FLOW-\d{3}(-\d{2}(-\d{2})?)?$')
    SEMVER_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')

    def __init__(self, base_path: Path, verbose: bool = False):
        self.base_path = base_path
        self.verbose = verbose
        self.errors: list[ValidationError] = []
        self.requirements: dict[str, RequirementMeta] = {}  # id -> RequirementMeta
        self.tasks: dict[str, TaskMeta] = {}  # task_id -> TaskMeta
        self.user_needs: dict[str, UserNeedsMeta] = {}  # id -> UserNeedsMeta
        self.known_releases: set[str] = set()  # Known version strings from RELEASES.md
        self.known_packages: set[str] = set()  # Known package IDs from RELEASE_BACKLOG.md
        self._load_releases()
        self._load_packages()

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"  [INFO] {message}")

    def _load_releases(self) -> None:
        """Load and cache known version strings from RELEASES.md."""
        releases_file = self.base_path / "requirements_tasks" / "RELEASES.md"
        if not releases_file.exists():
            self.log("RELEASES.md not found, skipping version-existence checks")
            return

        try:
            content = releases_file.read_text(encoding='utf-8')
            meta = self.parse_yaml_frontmatter(content)
            if meta and 'releases' in meta:
                releases = meta['releases']
                if isinstance(releases, list):
                    for release in releases:
                        if isinstance(release, dict) and 'version' in release:
                            version = release['version']
                            if isinstance(version, str):
                                self.known_releases.add(version)
                    self.log(f"Loaded {len(self.known_releases)} known releases from RELEASES.md")
        except Exception as e:
            self.log(f"Error loading RELEASES.md: {e}")

    def _load_packages(self) -> None:
        """Load and cache known package IDs from RELEASE_BACKLOG.md."""
        backlog_file = self.base_path / "RELEASE_BACKLOG.md"
        if not backlog_file.exists():
            self.log("RELEASE_BACKLOG.md not found, skipping package-existence checks")
            return
        try:
            content = backlog_file.read_text(encoding='utf-8')
            meta = self.parse_yaml_frontmatter(content)
            if meta and 'packages' in meta:
                for version_block in meta['packages']:
                    if isinstance(version_block, dict):
                        for pkg in version_block.get('packages', []):
                            if isinstance(pkg, dict) and 'id' in pkg:
                                self.known_packages.add(pkg['id'])
                self.log(f"Loaded {len(self.known_packages)} known packages from RELEASE_BACKLOG.md")
        except Exception as e:
            self.log(f"Error loading RELEASE_BACKLOG.md: {e}")

    def add_error(self, file_path: str, message: str, severity: str = "error") -> None:
        self.errors.append(ValidationError(file_path, message, severity))

    def parse_yaml_frontmatter(self, content: str) -> Optional[dict[str, Any]]:
        """Extract and parse YAML frontmatter from markdown content.

        Delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08).
        """
        if content.startswith('\ufeff'):
            content = content[1:]
        raw_yaml, _body = _split_frontmatter(content)
        if not raw_yaml.strip():
            return None
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.allow_duplicate_keys = True
        try:
            result = yaml.load(StringIO(raw_yaml))
        except Exception as e:
            self.log(f"YAML parse error: {e}")
            return None
        if result is None or not isinstance(result, dict) or len(result) == 0:
            return None
        return dict(result)

    def _parse_value(self, value: str) -> Any:
        """Parse a YAML value string."""
        if not value:
            return ''
        # Remove quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        # Check for numbers
        if value.isdigit():
            return int(value)
        # Check for booleans
        if value.lower() in ('true', 'yes'):
            return True
        if value.lower() in ('false', 'no'):
            return False
        return value

    def _validate_target_release(self, file_path: str, target_release: Any) -> bool:
        """Validate target_release field. Returns True if valid."""
        if not target_release or target_release == '':
            return True  # Optional field

        if not isinstance(target_release, str):
            self.add_error(file_path, f"target_release must be a string, got {type(target_release).__name__}")
            return False

        # Validate semver format
        if not self.SEMVER_PATTERN.match(target_release):
            self.add_error(file_path, f"Invalid target_release format: {target_release} (must be MAJOR.MINOR.PATCH)")
            return False

        # Check if version exists in RELEASES.md (if known releases are loaded)
        if self.known_releases and target_release not in self.known_releases:
            self.add_error(file_path, f"target_release '{target_release}' not found in RELEASES.md")
            return False

        return True

    def _validate_target_package(self, file_path: str, target_package: Any) -> bool:
        """Validate target_package field. Returns True if valid.

        Why: Package IDs are free-form strings — no fixed format to regex-validate.
        Existence in RELEASE_BACKLOG.md is the only valid check. If backlog is absent,
        we skip the check (transition period: backlog may not exist yet).
        Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/tasks/2026-03-26_impl_update-skills-and-scripts/plans_and_protocols/2026-03-26_01_plan_package-model-migration.md#d1-validatemetapy
        """
        if not target_package or target_package == '':
            return True  # Optional field
        if not isinstance(target_package, str):
            self.add_error(file_path, f"target_package must be a string, got {type(target_package).__name__}")
            return False
        if self.known_packages and target_package not in self.known_packages:
            self.add_error(file_path, f"target_package '{target_package}' not found in RELEASE_BACKLOG.md")
            return False
        return True

    def validate_requirements(self) -> None:
        """Find and validate all requirements.md files."""
        req_root = self.base_path / self.REQUIREMENTS_ROOT
        if not req_root.exists():
            self.add_error(str(req_root), "requirements_tasks folder not found")
            return

        for req_file in req_root.rglob("requirements.md"):
            self.log(f"Checking {req_file}")

            try:
                content = req_file.read_text(encoding='utf-8')
            except Exception as e:
                self.add_error(str(req_file), f"Could not read file: {e}")
                continue

            # Check for YAML frontmatter
            meta = self.parse_yaml_frontmatter(content)

            if meta is None:
                self.add_error(str(req_file), "No YAML frontmatter found", "warning")
                continue

            # Validate required fields
            req_id = meta.get('id')
            if not req_id:
                self.add_error(str(req_file), "Missing 'id' field in frontmatter")
                continue

            # Validate ID format
            if not self.REQ_ID_PATTERN.match(req_id):
                self.add_error(str(req_file), f"Invalid requirement ID format: {req_id}")

            # Validate top-level target_release if present (transition period: both fields accepted)
            target_release = meta.get('target_release')
            if target_release:
                self._validate_target_release(str(req_file), target_release)

            # Validate top-level target_package if present
            target_package = meta.get('target_package')
            if target_package:
                self._validate_target_package(str(req_file), target_package)

            # Check for duplicate IDs
            if req_id in self.requirements:
                self.add_error(str(req_file),
                    f"Duplicate requirement ID: {req_id} (also in {self.requirements[req_id].path})")
            else:
                # Extract trackable items
                trackable = meta.get('trackable_items', {})
                ac_ids = []
                sec_ids = []
                trackable_releases = []  # Collect releases from trackable items

                if isinstance(trackable, dict):
                    ac_list = trackable.get('acceptance_criteria', [])
                    for ac in ac_list:
                        if isinstance(ac, dict):
                            ac_id = ac.get('id')
                            if ac_id:
                                if not self.AC_ID_PATTERN.match(ac_id):
                                    self.add_error(str(req_file), f"Invalid AC ID format: {ac_id}")
                                ac_ids.append(ac_id)
                            # Validate target_release on AC object (transition period)
                            ac_target_release = ac.get('target_release')
                            if ac_target_release:
                                self._validate_target_release(str(req_file), ac_target_release)
                                trackable_releases.append(ac_target_release)
                            # Validate target_package on AC object
                            ac_target_package = ac.get('target_package')
                            if ac_target_package:
                                self._validate_target_package(str(req_file), ac_target_package)
                        elif isinstance(ac, str):
                            ac_ids.append(ac)

                    sec_list = trackable.get('sections', [])
                    for sec in sec_list:
                        if isinstance(sec, dict):
                            sec_id = sec.get('id')
                            if sec_id:
                                if not self.SEC_ID_PATTERN.match(sec_id):
                                    self.add_error(str(req_file), f"Invalid SEC ID format: {sec_id}")
                                sec_ids.append(sec_id)
                            # Validate target_release on SEC object (transition period)
                            sec_target_release = sec.get('target_release')
                            if sec_target_release:
                                self._validate_target_release(str(req_file), sec_target_release)
                                trackable_releases.append(sec_target_release)
                            # Validate target_package on SEC object
                            sec_target_package = sec.get('target_package')
                            if sec_target_package:
                                self._validate_target_package(str(req_file), sec_target_package)
                        elif isinstance(sec, str):
                            sec_ids.append(sec)

                # Check top-level release matches earliest trackable item release
                if trackable_releases and target_release:
                    earliest = min(trackable_releases)  # Simple string comparison (semver sorted)
                    if target_release != earliest:
                        self.add_error(str(req_file),
                            f"top-level target_release '{target_release}' must equal earliest trackable item release '{earliest}'",
                            "warning")

                self.requirements[req_id] = RequirementMeta(
                    id=req_id,
                    path=str(req_file),
                    trackable_items={
                        'acceptance_criteria': ac_ids,
                        'sections': sec_ids
                    },
                    target_release=target_release if isinstance(target_release, str) else None
                )

            # Validate other required fields
            required_fields = ['urgency', 'impact', 'status', 'effort', 'created']
            for field_name in required_fields:
                if field_name not in meta:
                    self.add_error(str(req_file), f"Missing required field: {field_name}", "warning")

            # Validate allowed status values for requirements
            valid_req_statuses = ['draft', 'defined', 'in_progress', 'implemented', 'active', 'deprecated']
            req_status = meta.get('status', '')
            if req_status and req_status not in valid_req_statuses:
                self.add_error(str(req_file),
                               f"Invalid status: '{req_status}' (must be one of {valid_req_statuses})",
                               "error")

    def validate_tasks(self) -> None:
        """Find and validate all goal.md files."""
        req_root = self.base_path / self.REQUIREMENTS_ROOT
        if not req_root.exists():
            return

        for goal_file in req_root.rglob("goal.md"):
            self.log(f"Checking {goal_file}")

            try:
                content = goal_file.read_text(encoding='utf-8')
            except Exception as e:
                self.add_error(str(goal_file), f"Could not read file: {e}")
                continue

            # Check for YAML frontmatter
            meta = self.parse_yaml_frontmatter(content)

            if meta is None:
                self.add_error(str(goal_file), "No YAML frontmatter found", "warning")
                continue

            # Validate required fields
            task_id = meta.get('task_id')
            if not task_id:
                # Old-style frontmatter without proper meta info - treat as warning
                # These are legacy tasks that haven't been migrated yet (Task 3 scope)
                self.add_error(str(goal_file), "No YAML frontmatter found", "warning")
                continue

            # Validate ID format
            if not self.TASK_ID_PATTERN.match(task_id):
                self.add_error(str(goal_file), f"Invalid task ID format: {task_id}")

            # Validate target_release if present (transition period: both fields accepted)
            target_release = meta.get('target_release')
            self._validate_target_release(str(goal_file), target_release)

            # Validate target_package if present
            target_package = meta.get('target_package')
            if target_package:
                self._validate_target_package(str(goal_file), target_package)

            # Check for duplicate IDs
            if task_id in self.tasks:
                self.add_error(str(goal_file),
                    f"Duplicate task ID: {task_id} (also in {self.tasks[task_id].path})")
            else:
                parent_req = meta.get('parent_requirement', '')
                covers = meta.get('covers', {})

                self.tasks[task_id] = TaskMeta(
                    task_id=task_id,
                    path=str(goal_file),
                    parent_requirement=parent_req,
                    covers=covers if isinstance(covers, dict) else {},
                    target_release=target_release if isinstance(target_release, str) else None,
                    target_package=target_package if isinstance(target_package, str) else None
                )

            # Validate other required fields
            required_fields = ['type', 'parent_requirement', 'urgency', 'impact', 'status', 'effort', 'created']
            for field_name in required_fields:
                if field_name not in meta:
                    self.add_error(str(goal_file), f"Missing required field: {field_name}", "warning")

            # Validate allowed status values for tasks
            valid_task_statuses = ['pending', 'ready', 'in_progress', 'blocked', 'review', 'completed', 'cancelled']
            task_status = meta.get('status', '')
            if task_status and task_status not in valid_task_statuses:
                self.add_error(str(goal_file),
                               f"Invalid status: '{task_status}' (must be one of {valid_task_statuses})",
                               "error")

            # Validate that blocked tasks have a reason (awaiting list or awaiting_note string)
            if task_status == 'blocked':
                awaiting = meta.get('awaiting', [])
                awaiting_note = meta.get('awaiting_note', '')
                has_awaiting = isinstance(awaiting, list) and len(awaiting) > 0
                has_awaiting_note = isinstance(awaiting_note, str) and awaiting_note.strip() != ''
                if not has_awaiting and not has_awaiting_note:
                    self.add_error(str(goal_file),
                                   "Task status is 'blocked' but neither awaiting nor awaiting_note is populated",
                                   "error")

            # Validate writes_requirements flag (optional boolean; only meaningful on explore tasks)
            writes_requirements = meta.get('writes_requirements')
            if writes_requirements is not None:
                if not isinstance(writes_requirements, bool):
                    self.add_error(str(goal_file),
                                   f"writes_requirements must be a boolean (true/false), got: {writes_requirements!r}",
                                   "error")
                elif writes_requirements is True and str(meta.get('type', '')).lower() != 'explore':
                    # writes_requirements: true only makes sense on explore tasks — impl tasks never
                    # write requirements, so this flag on an impl task is a semantic mismatch.
                    self.add_error(str(goal_file),
                                   "writes_requirements: true is set on a non-explore task "
                                   f"(type: {str(meta.get('type', ''))!r}); this flag is only valid on explore tasks",
                                   "warning")

    def validate_coverage_references(self) -> None:
        """Validate that covers references point to existing trackable_items."""
        for _task_id, task in self.tasks.items():
            if not task.parent_requirement:
                continue

            # Find the parent requirement
            req = self.requirements.get(task.parent_requirement)
            if not req:
                self.add_error(task.path,
                    f"parent_requirement '{task.parent_requirement}' not found in any requirements.md")
                continue

            # Validate AC references
            covered_acs = task.covers.get('acceptance_criteria', [])
            valid_acs = set(req.trackable_items.get('acceptance_criteria', []))

            for ac_id in covered_acs:
                if ac_id not in valid_acs:
                    self.add_error(task.path,
                        f"covers.acceptance_criteria references '{ac_id}' which doesn't exist in {req.id}")

            # Validate SEC references
            covered_secs = task.covers.get('sections', [])
            valid_secs = set(req.trackable_items.get('sections', []))

            for sec_id in covered_secs:
                if sec_id not in valid_secs:
                    self.add_error(task.path,
                        f"covers.sections references '{sec_id}' which doesn't exist in {req.id}")

    def _validate_user_needs_file(self, file_path: Path, doc_type: str, id_pattern: Any) -> Optional[UserNeedsMeta]:
        """Validate a single user needs file and extract metadata."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.add_error(str(file_path), f"Could not read file: {e}")
            return None

        # Parse YAML frontmatter
        meta = self.parse_yaml_frontmatter(content)
        if meta is None:
            self.add_error(str(file_path), "No YAML frontmatter found", "warning")
            return None

        # Extract ID based on doc type
        id_field = f"{doc_type}_id"
        doc_id = meta.get(id_field)

        if not doc_id:
            self.add_error(str(file_path), f"Missing '{id_field}' field in frontmatter")
            return None

        # Validate ID format
        if not id_pattern.match(doc_id):
            self.add_error(str(file_path), f"Invalid {doc_type} ID format: {doc_id}")

        # Check for duplicate IDs
        if doc_id in self.user_needs:
            self.add_error(str(file_path),
                          f"Duplicate {doc_type} ID: {doc_id} (also in {self.user_needs[doc_id].path})")

        # Validate review_status
        review_status = meta.get('review_status', '')
        valid_statuses = ['draft', 'in_review', 'pending_alignment', 'approved', 'deprecated']
        if review_status not in valid_statuses:
            self.add_error(str(file_path),
                          f"Invalid review_status: {review_status} (must be one of {valid_statuses})",
                          "warning")

        # Extract parent reference (for scenarios and flows)
        parent_id = None
        if doc_type == 'scenario':
            parent_id = meta.get('persona_id')
            if not parent_id:
                self.add_error(str(file_path), "Missing 'persona_id' field in scenario")
        elif doc_type == 'flow':
            parent_id = meta.get('scenario_id')  # optional for top-level flows

            # Validate implementation_status for flows
            impl_status = meta.get('implementation_status', '')
            valid_impl_statuses = ['not_started', 'partial', 'complete']
            if impl_status not in valid_impl_statuses:
                self.add_error(str(file_path),
                              f"Invalid implementation_status: {impl_status} (must be one of {valid_impl_statuses})",
                              "warning")

        return UserNeedsMeta(
            id=doc_id,
            doc_type=doc_type,
            path=str(file_path),
            review_status=review_status,
            parent_id=parent_id,
            implementation_status=meta.get('implementation_status') if doc_type == 'flow' else None
        )

    def _extract_implementing_epics(self, flow_file: Path) -> list[str]:
        """Extract epic/feature IDs from flow.md 'Implementing Epics/Features' table."""
        try:
            content = flow_file.read_text(encoding='utf-8')
        except Exception:
            return []

        # Look for "Implementing Epics/Features" section
        # Parse markdown table to extract epic IDs
        epic_ids = []
        in_table = False

        for line in content.split('\n'):
            if '## Implementing Epics/Features' in line or '## Related Epic/Feature' in line:
                in_table = True
                continue
            if in_table:
                if line.startswith('##'):  # Next section
                    break
                # Look for epic references like EPIC-THER-001 or REQ-FUNC-001
                matches = re.findall(r'(REQ-[A-Z]+-\d{3}|EPIC-[A-Z]+-\d{3})', line)
                epic_ids.extend(matches)

        return list(set(epic_ids))  # Remove duplicates

    def validate_user_needs(self) -> None:
        """Find and validate all persona, scenario, flow files."""
        user_needs_root = self.base_path / "requirements_user_needs" / "personas"

        if not user_needs_root.exists():
            self.add_error(str(user_needs_root),
                          "requirements_user_needs/personas/ folder not found",
                          "warning")
            return

        # Scan persona directories
        for persona_dir in user_needs_root.iterdir():
            if not persona_dir.is_dir():
                continue

            # Validate persona.md
            persona_file = persona_dir / "persona.md"
            if not persona_file.exists():
                self.add_error(str(persona_dir),
                              "Missing persona.md file", "warning")
                continue

            persona_meta = self._validate_user_needs_file(
                persona_file, "persona", self.PERSONA_ID_PATTERN
            )
            if persona_meta:
                self.user_needs[persona_meta.id] = persona_meta

            # Scan scenarios
            scenarios_dir = persona_dir / "scenarios"
            if not scenarios_dir.exists():
                continue

            for scenario_dir in scenarios_dir.iterdir():
                if not scenario_dir.is_dir():
                    continue

                # Validate scenario.md
                scenario_file = scenario_dir / "scenario.md"
                if not scenario_file.exists():
                    self.add_error(str(scenario_dir),
                                  "Missing scenario.md file", "warning")
                    continue

                scenario_meta = self._validate_user_needs_file(
                    scenario_file, "scenario", self.SCENARIO_ID_PATTERN
                )
                if scenario_meta:
                    # Verify parent persona reference
                    expected_persona = f"PERSONA-{scenario_meta.id.split('-')[1]}"
                    if scenario_meta.parent_id != expected_persona:
                        self.add_error(str(scenario_file),
                                      f"Scenario parent_id mismatch: expected {expected_persona}, got {scenario_meta.parent_id}")
                    elif expected_persona not in self.user_needs:
                        self.add_error(str(scenario_file),
                                      f"Parent persona {expected_persona} not found")

                    self.user_needs[scenario_meta.id] = scenario_meta

                # Scan user flows
                flows_dir = scenario_dir / "user_flows"
                if not flows_dir.exists():
                    continue

                for flow_dir in flows_dir.iterdir():
                    if not flow_dir.is_dir():
                        continue

                    # Validate flow.md
                    flow_file = flow_dir / "flow.md"
                    if not flow_file.exists():
                        self.add_error(str(flow_dir),
                                      "Missing flow.md file", "warning")
                        continue

                    flow_meta = self._validate_user_needs_file(
                        flow_file, "flow", self.FLOW_ID_PATTERN
                    )
                    if flow_meta:
                        # Verify parent scenario reference
                        expected_scenario = f"SCEN-{'-'.join(flow_meta.id.split('-')[1:3])}"
                        if flow_meta.parent_id != expected_scenario:
                            self.add_error(str(flow_file),
                                          f"Flow parent_id mismatch: expected {expected_scenario}, got {flow_meta.parent_id}")
                        elif expected_scenario not in self.user_needs:
                            self.add_error(str(flow_file),
                                          f"Parent scenario {expected_scenario} not found")

                        # Extract implementing epics from flow.md content
                        flow_meta.implementing_epics = self._extract_implementing_epics(flow_file)

                        self.user_needs[flow_meta.id] = flow_meta

        # Scan top-level user_flows directory
        top_flows_root = self.base_path / "requirements_user_needs" / "user_flows"
        if top_flows_root.exists():
            for flow_dir in top_flows_root.iterdir():
                if not flow_dir.is_dir() or flow_dir.name.startswith('_'):
                    continue
                flow_file = flow_dir / "flow.md"
                if not flow_file.exists():
                    self.add_error(str(flow_dir), "Missing flow.md file", "warning")
                    continue
                flow_meta = self._validate_user_needs_file(
                    flow_file, "flow", self.FLOW_ID_PATTERN
                )
                if flow_meta:
                    flow_meta.implementing_epics = self._extract_implementing_epics(flow_file)
                    self.user_needs[flow_meta.id] = flow_meta

    def validate_epic_user_needs_references(self) -> None:
        """Validate user_needs field in epic/feature requirements.md."""
        for _req_id, req in self.requirements.items():
            # Read requirements.md to check for user_needs field
            try:
                with open(req.path, encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            meta = self.parse_yaml_frontmatter(content)
            if not meta or 'user_needs' not in meta:
                continue  # user_needs is optional

            user_needs = meta['user_needs']

            # Validate implements_flows
            implements_flows = user_needs.get('implements_flows', [])
            for flow_ref in implements_flows:
                if isinstance(flow_ref, dict):
                    flow_id = flow_ref.get('id', '')
                else:
                    flow_id = flow_ref

                if not flow_id:
                    self.add_error(req.path, "Empty flow ID in user_needs.implements_flows")
                    continue

                # Check flow exists
                if flow_id not in self.user_needs:
                    self.add_error(req.path,
                                  f"user_needs.implements_flows references non-existent flow: {flow_id}")
                else:
                    flow_meta = self.user_needs[flow_id]

                    # Warn if flow not approved
                    if flow_meta.review_status != 'approved':
                        self.add_error(req.path,
                                      f"Epic references flow {flow_id} which has review_status: {flow_meta.review_status}",
                                      "warning")

                    # Validate coverage vs implementation_status
                    if isinstance(flow_ref, dict):
                        claimed_coverage = flow_ref.get('coverage', 'not_started')
                        actual_impl = flow_meta.implementation_status or 'not_started'

                        # Consistency check (not strict, just warning)
                        if claimed_coverage == 'complete' and actual_impl != 'complete':
                            self.add_error(req.path,
                                          f"Epic claims complete coverage of {flow_id} but flow has implementation_status: {actual_impl}",
                                          "warning")

            # Validate addresses_scenarios
            addresses_scenarios = user_needs.get('addresses_scenarios', [])
            for scenario_id in addresses_scenarios:
                if scenario_id not in self.user_needs:
                    self.add_error(req.path,
                                  f"user_needs.addresses_scenarios references non-existent scenario: {scenario_id}")
                else:
                    scenario_meta = self.user_needs[scenario_id]
                    if scenario_meta.review_status != 'approved':
                        self.add_error(req.path,
                                      f"Epic references scenario {scenario_id} which has review_status: {scenario_meta.review_status}",
                                      "warning")

            # Validate personas_served
            personas_served = user_needs.get('personas_served', [])
            for persona_id in personas_served:
                if persona_id not in self.user_needs:
                    self.add_error(req.path,
                                  f"user_needs.personas_served references non-existent persona: {persona_id}")
                else:
                    persona_meta = self.user_needs[persona_id]
                    if persona_meta.review_status != 'approved':
                        self.add_error(req.path,
                                      f"Epic references persona {persona_id} which has review_status: {persona_meta.review_status}",
                                      "warning")

    def validate_release_dependencies(self) -> None:
        """Validate release-dependency consistency for items with target_release."""
        for task_id, task in self.tasks.items():
            if not task.target_release:
                continue

            # Check after
            after = getattr(task, 'after', [])
            if not after:
                # Try to read from file to get after field
                try:
                    with open(task.path, encoding='utf-8') as f:
                        content = f.read()
                    meta = self.parse_yaml_frontmatter(content)
                    after = meta.get('after', []) if meta else []
                except Exception:
                    after = []

            if isinstance(after, list):
                for dep_id in after:
                    if not dep_id:
                        continue
                    dep_task = self.tasks.get(dep_id)
                    dep_req = self.requirements.get(dep_id)
                    dep_item = dep_task or dep_req

                    if not dep_item:
                        continue

                    dep_release = getattr(dep_item, 'target_release', None)
                    # Both sides assigned: verify constraint
                    if dep_release and task.target_release < dep_release:
                        self.add_error(task.path,
                            f"task {task_id} (release {task.target_release}) depends on {dep_id} (release {dep_release}), "
                            f"but should have release >= dependency",
                            "warning")

            # Check awaiting
            awaiting: list[Any] = []
            try:
                with open(task.path, encoding='utf-8') as f:
                    content = f.read()
                meta = self.parse_yaml_frontmatter(content)
                awaiting = meta.get('awaiting', []) if meta else []
            except Exception:
                awaiting = []

            if isinstance(awaiting, list):
                for blocker_id in awaiting:
                    if not blocker_id:
                        continue
                    blocker_task = self.tasks.get(blocker_id)
                    blocker_req = self.requirements.get(blocker_id)
                    blocker_item = blocker_task or blocker_req

                    if not blocker_item:
                        continue

                    blocker_release = getattr(blocker_item, 'target_release', None)
                    # Both sides assigned: verify constraint
                    if blocker_release and task.target_release < blocker_release:
                        self.add_error(task.path,
                            f"task {task_id} (release {task.target_release}) is blocked by {blocker_id} (release {blocker_release}), "
                            f"but should have release >= blocker",
                            "warning")

    def validate_cross_reference_symmetry(self) -> None:
        """Check bidirectional references are symmetric."""
        # For each flow that lists implementing epics
        for flow_id, flow_meta in self.user_needs.items():
            if flow_meta.doc_type != 'flow':
                continue

            for epic_id in flow_meta.implementing_epics:
                # Check if epic exists
                if epic_id not in self.requirements:
                    self.add_error(flow_meta.path,
                                  f"Flow references epic {epic_id} which doesn't exist in requirements")
                    continue

                # Check if epic references this flow back
                epic = self.requirements[epic_id]
                try:
                    with open(epic.path, encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    continue

                meta = self.parse_yaml_frontmatter(content)
                if not meta or 'user_needs' not in meta:
                    self.add_error(flow_meta.path,
                                  f"Flow {flow_id} lists epic {epic_id} but epic doesn't have user_needs field",
                                  "warning")
                    continue

                # Check if flow_id is in implements_flows
                user_needs = meta['user_needs']
                implements_flows = user_needs.get('implements_flows', [])

                flow_referenced = False
                for flow_ref in implements_flows:
                    ref_id = flow_ref.get('id') if isinstance(flow_ref, dict) else flow_ref
                    if ref_id == flow_id:
                        flow_referenced = True
                        break

                if not flow_referenced:
                    self.add_error(flow_meta.path,
                                  f"Flow {flow_id} lists epic {epic_id} but epic doesn't reference flow back (asymmetric reference)",
                                  "warning")

    def run(self) -> tuple[int, int]:
        """Run all validations. Returns (error_count, warning_count)."""
        print("=" * 60)
        print("META INFORMATION VALIDATION")
        print("=" * 60)
        print()

        # NEW: Validate user needs first
        print("Scanning user needs documents...")
        self.validate_user_needs()

        persona_count = len([m for m in self.user_needs.values() if m.doc_type == 'persona'])
        scenario_count = len([m for m in self.user_needs.values() if m.doc_type == 'scenario'])
        flow_count = len([m for m in self.user_needs.values() if m.doc_type == 'flow'])

        print(f"  Found {persona_count} personas")
        print(f"  Found {scenario_count} scenarios")
        print(f"  Found {flow_count} flows")

        print("\nScanning requirements.md files...")
        self.validate_requirements()
        print(f"  Found {len(self.requirements)} requirements with valid frontmatter")

        print("\nScanning goal.md files...")
        self.validate_tasks()
        print(f"  Found {len(self.tasks)} tasks with valid frontmatter")

        print("\nValidating coverage references...")
        self.validate_coverage_references()

        # NEW: Validate user needs references
        print("\nValidating user needs references...")
        self.validate_epic_user_needs_references()

        print("\nValidating cross-reference symmetry...")
        self.validate_cross_reference_symmetry()

        print("\nValidating release dependencies...")
        self.validate_release_dependencies()

        # Count errors and warnings
        errors = [e for e in self.errors if e.severity == "error"]
        warnings = [e for e in self.errors if e.severity == "warning"]

        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)

        if errors:
            print(f"\nERRORS ({len(errors)}):")
            for err in errors:
                rel_path = os.path.relpath(err.file_path, self.base_path)
                print(f"  [ERROR] {rel_path}")
                print(f"          {err.message}")

        if warnings:
            print(f"\nWARNINGS ({len(warnings)}):")
            for warn in warnings:
                rel_path = os.path.relpath(warn.file_path, self.base_path)
                print(f"  [WARN]  {rel_path}")
                print(f"          {warn.message}")

        if not errors and not warnings:
            print("\nAll validations passed!")

        # NEW: Add user needs summary before final summary
        if self.user_needs:
            print("\n=== USER NEEDS SUMMARY ===")

            # Status breakdown
            status_counts = {'draft': 0, 'in_review': 0, 'pending_alignment': 0, 'approved': 0, 'deprecated': 0}
            for meta in self.user_needs.values():
                status = meta.review_status
                if status in status_counts:
                    status_counts[status] += 1

            approved_personas = len([m for m in self.user_needs.values() if m.doc_type == 'persona' and m.review_status == 'approved'])
            approved_scenarios = len([m for m in self.user_needs.values() if m.doc_type == 'scenario' and m.review_status == 'approved'])
            approved_flows = len([m for m in self.user_needs.values() if m.doc_type == 'flow' and m.review_status == 'approved'])

            print(f"Personas: {persona_count} (approved: {approved_personas})")
            print(f"Scenarios: {scenario_count} (approved: {approved_scenarios})")
            print(f"Flows: {flow_count} (approved: {approved_flows})")
            print()

        print()
        print(f"Summary: {len(errors)} errors, {len(warnings)} warnings")

        return len(errors), len(warnings)


def main() -> None:
    # Find project root (directory containing requirements_tasks/)
    # Script is at scripts/requirements/, so project root is two levels up
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Check if requirements_tasks exists
    if not (project_root / "requirements_tasks").exists():
        print(f"Error: requirements_tasks/ not found in {project_root}")
        sys.exit(1)

    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    validator = MetaValidator(project_root, verbose=verbose)
    errors, _warnings = validator.run()

    # Exit with error code if there are errors
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
