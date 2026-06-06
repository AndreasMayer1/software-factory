#!/usr/bin/env python3
# ruff: noqa: RUF001, RUF002, RUF100
# RUF001 / RUF002: docstrings and report strings use the MULTIPLICATION SIGN intentionally
# in priority formulas like "Urgency x 10 + Impact" rendered for human readability.
# RUF100: false-positive on file-level noqa for codes ruff cannot introspect into the file body.
"""
Status Overview Report Generator for Requirements and Tasks.

Generates various status reports by parsing YAML frontmatter from requirements.md
and goal.md files, with backward compatibility for legacy folder naming conventions.

Usage:
    python scripts/generate_status_overview.py --summary
    python scripts/generate_status_overview.py --priority
    python scripts/generate_status_overview.py --coverage
    python scripts/generate_status_overview.py --blockers
    python scripts/generate_status_overview.py --sprint
    python scripts/generate_status_overview.py --full
    python scripts/generate_status_overview.py --dependencies
    python scripts/generate_status_overview.py --critical-path
    python scripts/generate_status_overview.py --dep-graph --graph-format mermaid
    python scripts/generate_status_overview.py --requirements --summary
    python scripts/generate_status_overview.py --release-summary
    python scripts/generate_status_overview.py --release 0.1.0 --priority
    python scripts/generate_status_overview.py --package-summary
    python scripts/generate_status_overview.py --package PKG-0.0.1-core --priority

Modes:
    --summary         Quick stats table (tasks or requirements)
    --priority        Sorted by priority score (tasks or requirements)
    --coverage        Coverage % per requirement with gaps (task→requirement mapping)
    --blockers        Blocked and critical items (tasks or requirements)
    --sprint          Sprint focus - U3+ urgency (tasks or requirements)
    --full            Complete report with all sections (tasks or requirements)
    --dependencies    Dependency tree visualization (ASCII art)
    --critical-path   Critical path analysis (bottlenecks and chains)
    --dep-graph       Export dependency graph (DOT/Mermaid format)
    --release-summary Release-grouped overview: counts and progress per release version
    --package-summary Package-grouped overview: counts and progress per package

Output:
    Prints the selected human-readable report (summary table, priority
    list, coverage matrix, dependency graph, etc.) to stdout. Mode-specific
    formatting; no files are written.

Options:
    --requirements     Generate requirement-focused reports instead of task-focused
    --output PATH      Output file path (default: requirements_tasks/STATUS.md)
    --format md|json   Output format (default: md)
    --graph-format dot|mermaid  Graph export format for --dep-graph (default: dot)
    --category FUNC|NFUNC|PROC  Filter by category
    --release VERSION  Filter output to items assigned to a specific release version
    --package PKG_ID   Filter output to items assigned to a specific package ID
    --include-legacy   Include files without YAML frontmatter
    --verbose         Verbose output
"""

# tier: C  # one-shot CLI artifact generator; no in-tree Python imports

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Why: this script runs both as `python3 scripts/artifacts/generate_status_overview.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
    _parse_yaml_block,
    _split_frontmatter,
    read_frontmatter,
)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RequirementData:
    """Represents a requirement with all metadata."""
    id: str
    path: str
    name: str  # Extracted from folder structure
    category: str  # FUNC, NFUNC, PROC
    status: str
    urgency: int
    urgency_reason: str
    impact: int
    impact_reason: str
    effort: str
    created: str
    updated: Optional[str]
    trackable_items: dict[str, Any] = field(default_factory=dict)
    has_frontmatter: bool = True
    after: list[str] = field(default_factory=list)  # NEW: Dependency fields
    blocks: list[str] = field(default_factory=list)      # NEW: Dependency fields
    target_release: Optional[str] = None
    target_package: Optional[str] = None

    @property
    def priority_score(self) -> int:
        """Calculate priority score from urgency and impact.

        Why: Uses formula (urgency × 10) + impact to ensure urgency dominates.
             Example: U5-I1 (score=51) > U4-I9 (score=49)
        Source: requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/plans_and_protocols/2026-01-09_01_plan_status_overview_script.md#priority-score-calculation
        """
        return (self.urgency * 10) + self.impact


@dataclass
class TaskData:
    """Represents a task with all metadata."""
    task_id: str
    path: str
    name: str  # Folder name without date/status
    parent_requirement: str
    type: str  # impl, explore
    status: str
    urgency: int
    urgency_reason: str
    impact: int
    impact_reason: str
    effort: str
    created: str
    completed: Optional[str]
    after: list[str] = field(default_factory=list)
    awaiting: list[str] = field(default_factory=list)
    awaiting_note: str = ''
    covers: dict[str, list[str]] = field(default_factory=dict)
    has_frontmatter: bool = True
    target_release: Optional[str] = None
    target_package: Optional[str] = None

    @property
    def priority_score(self) -> int:
        """Calculate priority score from urgency and impact.

        Why: Uses formula (urgency × 10) + impact to ensure urgency dominates.
             Example: U5-I1 (score=51) > U4-I9 (score=49)
        Source: requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/plans_and_protocols/2026-01-09_01_plan_status_overview_script.md#priority-score-calculation
        """
        return (self.urgency * 10) + self.impact

    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked."""
        return self.status == 'blocked' or len(self.awaiting) > 0

    @property
    def is_critical(self) -> bool:
        """Check if task is critical (urgency >= 5)."""
        return self.urgency >= 5


@dataclass
class CategoryStats:
    """Statistics for a single category."""
    category: str  # FUNC, NFUNC, PROC
    requirement_count: int
    task_count: int
    open_tasks: int
    completed_tasks: int
    coverage_percent: float


@dataclass
class Statistics:
    """Overall statistics."""
    total_requirements: int
    total_tasks: int
    open_tasks: int
    completed_tasks: int
    blocked_tasks: int
    critical_tasks: int
    sprint_tasks: int  # U3+
    overall_coverage: float  # Percentage
    legacy_requirement_count: int
    legacy_task_count: int
    category_stats: dict[str, CategoryStats] = field(default_factory=dict)

    @property
    def requirements_with_frontmatter(self) -> int:
        return self.total_requirements - self.legacy_requirement_count

    @property
    def tasks_with_frontmatter(self) -> int:
        return self.total_tasks - self.legacy_task_count


# ============================================================================
# DEPENDENCY GRAPH DATA STRUCTURES
# ============================================================================

@dataclass
class DependencyNode:
    """Represents a node in the dependency graph."""
    id: str
    name: str
    type: str  # 'task' or 'requirement'
    status: str
    after: list[str]  # IDs this item depends on
    blocks: list[str]      # IDs this item blocks (computed)
    depth: int = 0         # Distance from root in tree

    @property
    def is_root(self) -> bool:
        """Node with no dependencies."""
        return len(self.after) == 0

    @property
    def is_leaf(self) -> bool:
        """Node that blocks nothing."""
        return len(self.blocks) == 0


@dataclass
class DependencyGraph:
    """Complete dependency graph with analysis."""
    nodes: dict[str, DependencyNode] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)

    # Analysis results
    circular_dependencies: list[list[str]] = field(default_factory=list)
    orphaned_nodes: list[str] = field(default_factory=list)
    critical_path: list[str] = field(default_factory=list)
    blocking_scores: dict[str, int] = field(default_factory=dict)


# ============================================================================
# YAML PARSER (Reused from validate_meta.py)
# ============================================================================

class YAMLParser:
    """Thin wrapper around scripts.util.yaml_frontmatter for backward compatibility.

    Why: callers throughout this module previously instantiated YAMLParser and
    called .parse_frontmatter(content_string). Preserving the class shape keeps
    the diff localized while routing the actual parsing through the central
    helper (REQ-PROC-051 AC-08).
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def parse_frontmatter(self, content: str) -> Optional[dict[str, Any]]:
        """Parse YAML frontmatter from a content string.

        Returns dict on success, None when frontmatter is absent/empty/malformed.
        """
        # Strip UTF-8 BOM (some Windows editors add it; central helper does not).
        if content.startswith('\ufeff'):
            content = content[1:]
        raw_yaml, _body = _split_frontmatter(content)
        if not raw_yaml:
            return None
        try:
            metadata = _parse_yaml_block(raw_yaml)
        except Exception as exc:
            if self.verbose:
                print(f"  [WARN] YAML parse error: {exc}")
            return None
        if not metadata:
            return None
        return dict(metadata)

# ============================================================================
# SEMVER UTILITIES
# ============================================================================

def _parse_semver(version_str: str) -> tuple[int, int, int]:
    """Parse 'MAJOR.MINOR.PATCH' into a sortable tuple.

    # Why: Avoids the `packaging` dependency which is not guaranteed to be installed
    #      in all environments (not part of stdlib). Tuple comparison is correct for
    #      our strict MAJOR.MINOR.PATCH format used in RELEASES.md.
    # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md#version-number-system
    """
    if not version_str:
        return (0, 0, 0)
    parts = str(version_str).split('.')
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        return (0, 0, 0)


def load_releases(project_root: Path) -> list[dict[str, Any]]:
    """Load release definitions from requirements_tasks/RELEASES.md.

    # Why: RELEASES.md is the single source of truth for all planned releases
    #      (REQ-PROC-034 SEC-01). Loading it here ensures release names and
    #      descriptions shown in reports always match the definition document.
    #      Convention-over-configuration: file is at a known path so callers
    #      don't need to pass it as an argument.
    # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md#sec-01
    """
    releases_path = project_root / "requirements_tasks" / "RELEASES.md"
    if not releases_path.exists():
        return []
    try:
        doc = read_frontmatter(releases_path)
    except (FrontmatterError, OSError):
        return []
    meta = dict(doc.metadata) if doc.has_frontmatter else {}
    releases_raw = meta.get('releases')
    if not isinstance(releases_raw, list):
        return []
    releases = [
        dict(r) for r in releases_raw if isinstance(r, dict) and r.get('version')
    ]
    return sorted(releases, key=lambda r: _parse_semver(str(r.get('version', '0.0.0'))))


def load_backlog_packages(project_root: Path) -> list[dict[str, Any]]:
    """Load flat list of packages (with version info) from RELEASE_BACKLOG.md.

    Returns list of dicts with keys: id, name, version, status.
    Returns empty list if file is missing or malformed — callers degrade gracefully.
    """
    backlog_path = project_root / "requirements_tasks" / "RELEASE_BACKLOG.md"
    if not backlog_path.exists():
        return []
    try:
        doc = read_frontmatter(backlog_path)
    except (FrontmatterError, OSError):
        return []
    meta = dict(doc.metadata) if doc.has_frontmatter else {}
    packages_raw = meta.get('packages')
    if not isinstance(packages_raw, list):
        return []
    result: list[dict[str, Any]] = []
    for pkg in packages_raw:
        if not isinstance(pkg, dict) or not pkg.get('id'):
            continue
        version = str(pkg.get('assigned_release', '') or '')
        result.append({
            'id': str(pkg['id']),
            'name': str(pkg.get('name', pkg['id'])),
            'version': version,
            'status': str(pkg.get('status', 'planned')),
        })
    return result


# ============================================================================
# STATUS SCANNER
# ============================================================================

class StatusScanner:
    """Scans and parses all requirements and tasks."""

    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.requirements_root = project_root / "requirements_tasks"
        self.verbose = verbose
        self.yaml_parser = YAMLParser(verbose=verbose)

    def log(self, message: str) -> None:
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"  [INFO] {message}")

    def scan_requirements(self) -> list[RequirementData]:
        """Scan all requirements.md files."""
        requirements: list[Any] = []

        if not self.requirements_root.exists():
            print(f"Error: {self.requirements_root} not found")
            return requirements

        for req_file in self.requirements_root.rglob("requirements.md"):
            try:
                content = req_file.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try alternative encoding
                try:
                    content = req_file.read_text(encoding='latin-1')
                    self.log(f"Warning: {req_file} used latin-1 encoding")
                except Exception as e:
                    self.log(f"Error reading {req_file}: {e}")
                    continue
            except Exception as e:
                self.log(f"Error reading {req_file}: {e}")
                continue

            # Parse content
            req = self._parse_requirement(req_file, content)
            if req:
                requirements.append(req)

        return requirements

    def scan_tasks(self) -> list[TaskData]:
        """Scan all goal.md files."""
        tasks: list[Any] = []

        if not self.requirements_root.exists():
            return tasks

        for goal_file in self.requirements_root.rglob("goal.md"):
            try:
                content = goal_file.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = goal_file.read_text(encoding='latin-1')
                    self.log(f"Warning: {goal_file} used latin-1 encoding")
                except Exception as e:
                    self.log(f"Error reading {goal_file}: {e}")
                    continue
            except Exception as e:
                self.log(f"Error reading {goal_file}: {e}")
                continue

            # Parse content
            task = self._parse_task(goal_file, content)
            if task:
                tasks.append(task)

        return tasks

    def _parse_requirement(self, path: Path, content: str) -> Optional[RequirementData]:
        """Parse requirement with frontmatter or legacy fallback.

        Why: Backward compatibility during migration period (Tasks 2 & 3).
             Files without YAML frontmatter use folder naming conventions.
        Source: requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/plans_and_protocols/2026-01-09_01_plan_status_overview_script.md#backward-compatibility
        """
        # Try frontmatter first
        meta = self.yaml_parser.parse_frontmatter(content)

        if meta and 'id' in meta:
            # Modern format with YAML frontmatter
            return self._requirement_from_frontmatter(path, meta)
        # Legacy format: use folder structure
        return self._requirement_from_legacy(path)

    def _requirement_from_frontmatter(self, path: Path, meta: dict[str, Any]) -> RequirementData:
        """Create RequirementData from YAML frontmatter."""
        # Extract name from parent folder
        name = path.parent.name.replace('_', ' ').title()

        # Extract trackable items
        trackable = meta.get('trackable_items', {})
        ac_ids = []
        sec_ids = []
        # Why: Per-item releases stored alongside ac_ids/sec_ids so ReleaseSummaryReportGenerator
        #      can read them from trackable_items['releases'] without re-parsing frontmatter.
        #      Note: 'releases' is a special dict key (item_id -> release), not a list like
        #      'acceptance_criteria'/'sections'. Existing code only reads by name so no collision.
        trackable_releases: dict[str, str] = {}

        if isinstance(trackable, dict):
            ac_list = trackable.get('acceptance_criteria', [])
            for ac in ac_list:
                if isinstance(ac, dict):
                    ac_id = ac.get('id')
                    if ac_id:
                        ac_ids.append(ac_id)
                        if ac.get('target_release'):
                            trackable_releases[ac_id] = ac['target_release']
                elif isinstance(ac, str):
                    ac_ids.append(ac)

            sec_list = trackable.get('sections', [])
            for sec in sec_list:
                if isinstance(sec, dict):
                    sec_id = sec.get('id')
                    if sec_id:
                        sec_ids.append(sec_id)
                        if sec.get('target_release'):
                            trackable_releases[sec_id] = sec['target_release']
                elif isinstance(sec, str):
                    sec_ids.append(sec)

        # Extract category from ID
        req_id = meta.get('id', '')
        category = 'UNKNOWN'
        if req_id.startswith('REQ-'):
            parts = req_id.split('-')
            if len(parts) >= 2:
                category = parts[1]

        # Extract dependency fields (NEW)
        after = meta.get('after', [])
        if not isinstance(after, list):
            after = [after] if after else []

        blocks = meta.get('blocks', [])
        if not isinstance(blocks, list):
            blocks = [blocks] if blocks else []

        return RequirementData(
            id=req_id,
            path=str(path),
            name=name,
            category=category,
            status=meta.get('status', 'unknown'),
            urgency=meta.get('urgency', 0),
            urgency_reason=meta.get('urgency_reason', 'U0-UNKNOWN'),
            impact=meta.get('impact', 0),
            impact_reason=meta.get('impact_reason', 'I0-UNKNOWN'),
            effort=meta.get('effort', 'M'),
            created=str(meta.get('created', 'unknown')),
            updated=str(meta.get('updated')) if meta.get('updated') else None,
            trackable_items={
                'acceptance_criteria': ac_ids,
                'sections': sec_ids,
                'releases': trackable_releases  # item_id -> release version
            },
            after=after,  # NEW
            blocks=blocks,          # NEW
            target_release=meta.get('target_release'),
            target_package=meta.get('target_package'),
            has_frontmatter=True
        )

    def _requirement_from_legacy(self, path: Path) -> RequirementData:
        """Parse requirement from folder structure (no frontmatter)."""
        # Extract name from parent folder
        name = path.parent.name.replace('_', ' ').title()

        # Determine category from path
        path_str = str(path).lower()
        if 'functional' in path_str or 'features' in path_str:
            category = 'FUNC'
        elif 'non-functional' in path_str or 'non_functional' in path_str:
            category = 'NFUNC'
        elif 'process' in path_str:
            category = 'PROC'
        else:
            category = 'UNKNOWN'

        # Default values for missing frontmatter
        return RequirementData(
            id=f"REQ-{category}-LEGACY",
            path=str(path),
            name=name,
            category=category,
            status='unknown',
            urgency=0,
            urgency_reason='U0-UNKNOWN',
            impact=0,
            impact_reason='I0-UNKNOWN',
            effort='M',
            created='unknown',
            updated=None,
            trackable_items={},
            has_frontmatter=False
        )

    def _parse_task(self, path: Path, content: str) -> Optional[TaskData]:
        """Parse task with frontmatter or legacy fallback."""
        # Try frontmatter first
        meta = self.yaml_parser.parse_frontmatter(content)

        if meta and 'task_id' in meta:
            # Modern format with YAML frontmatter
            return self._task_from_frontmatter(path, meta)
        # Legacy format: use folder structure
        return self._task_from_legacy(path)

    def _task_from_frontmatter(self, path: Path, meta: dict[str, Any]) -> TaskData:
        """Create TaskData from YAML frontmatter."""
        # Extract name from folder
        folder_name = path.parent.name
        # Remove date prefix and status suffix
        name = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', folder_name)
        name = re.sub(r'_(impl|explore)_', ' ', name)
        name = name.replace('_(completed)', '').replace('_(superseded)', '')
        name = name.replace('_', ' ').strip().title()

        # Extract after and awaiting
        after = meta.get('after', [])
        if not isinstance(after, list):
            after = [after] if after else []

        awaiting = meta.get('awaiting', [])
        if not isinstance(awaiting, list):
            awaiting = [awaiting] if awaiting else []

        awaiting_note = str(meta.get('awaiting_note', '') or '')

        # Extract covers
        covers = meta.get('covers', {})
        if not isinstance(covers, dict):
            covers = {}

        return TaskData(
            task_id=meta.get('task_id', ''),
            path=str(path),
            name=name,
            parent_requirement=meta.get('parent_requirement', 'UNKNOWN'),
            type=meta.get('type', 'impl'),
            status=meta.get('status', 'unknown'),
            urgency=meta.get('urgency', 0),
            urgency_reason=meta.get('urgency_reason', 'U0-UNKNOWN'),
            impact=meta.get('impact', 0),
            impact_reason=meta.get('impact_reason', 'I0-UNKNOWN'),
            effort=meta.get('effort', 'M'),
            created=str(meta.get('created', 'unknown')),
            completed=str(meta.get('completed')) if meta.get('completed') else None,
            after=after,
            awaiting=awaiting,
            awaiting_note=awaiting_note,
            covers=covers,
            target_release=meta.get('target_release'),
            target_package=meta.get('target_package'),
            has_frontmatter=True
        )

    def _task_from_legacy(self, path: Path) -> TaskData:
        """Parse task from folder structure (no frontmatter)."""
        folder_name = path.parent.name

        # Extract date: YYYY-MM-DD
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2})_', folder_name)
        created = date_match.group(1) if date_match else 'unknown'

        # Extract status from suffix
        if folder_name.endswith('_(completed)'):
            status = 'completed'
            name = folder_name.replace('_(completed)', '').strip()
        elif folder_name.endswith('_(superseded)'):
            status = 'cancelled'
            name = folder_name.replace('_(superseded)', '').strip()
        else:
            status = 'in_progress'
            name = folder_name

        # Extract type: impl or explore
        type_match = re.search(r'_(impl|explore)_', folder_name)
        task_type = type_match.group(1) if type_match else 'impl'

        # Clean name (remove date and type prefix)
        name = re.sub(r'^\d{4}-\d{2}-\d{2}_(impl|explore)_', '', name)
        name = name.replace('_', ' ').title()

        return TaskData(
            task_id=f"TASK-LEGACY-{created}",
            path=str(path),
            name=name,
            parent_requirement='UNKNOWN',
            type=task_type,
            status=status,
            urgency=0,
            urgency_reason='U0-UNKNOWN',
            impact=0,
            impact_reason='I0-UNKNOWN',
            effort='M',
            created=created,
            completed=created if status == 'completed' else None,
            after=[],
            awaiting=[],
            covers={},
            has_frontmatter=False
        )


# ============================================================================
# DEPENDENCY GRAPH BUILDER
# ============================================================================

class DependencyGraphBuilder:
    """Builds dependency graph from requirements and tasks."""

    def __init__(self, requirements: list[RequirementData], tasks: list[TaskData]):
        self.requirements = requirements
        self.tasks = tasks

    def build(self, focus: str = 'tasks') -> DependencyGraph:
        """Build dependency graph.

        Args:
            focus: 'tasks' or 'requirements' or 'both'

        Returns:
            Complete dependency graph with analysis
        """
        nodes: dict[Any, Any] = {}
        edges: list[Any] = []

        if focus in ['tasks', 'both']:
            self._add_task_dependencies(nodes, edges)

        if focus in ['requirements', 'both']:
            self._add_requirement_dependencies(nodes, edges)

        # Build graph
        graph = DependencyGraph(nodes=nodes, edges=edges)

        # Run analysis
        graph.circular_dependencies = self._find_cycles(graph)
        graph.orphaned_nodes = [n.id for n in nodes.values() if n.is_root and n.is_leaf]
        graph.critical_path = self._find_longest_chain(graph)
        graph.blocking_scores = self._compute_blocking_scores(graph)

        return graph

    def _add_task_dependencies(self, nodes: dict[str, DependencyNode], edges: list[tuple[str, str]]) -> None:
        """Add task nodes and edges."""
        for task in self.tasks:
            # Create node
            node = DependencyNode(
                id=task.task_id,
                name=task.name,
                type='task',
                status=task.status,
                after=task.after[:],  # Copy list
                blocks=[]  # Computed later
            )
            nodes[task.task_id] = node

            # Add edges (dependency → task that depends on it)
            for dep_id in task.after:
                edges.append((dep_id, task.task_id))

            # Add edges from awaiting (inverse relationship)
            for blocker_id in task.awaiting:
                edges.append((blocker_id, task.task_id))

        # Compute 'blocks' lists from edges
        for from_id, to_id in edges:
            if from_id in nodes and to_id not in nodes[from_id].blocks:
                nodes[from_id].blocks.append(to_id)

    def _add_requirement_dependencies(self, nodes: dict[str, DependencyNode], edges: list[tuple[str, str]]) -> None:
        """Add requirement nodes and edges."""
        for req in self.requirements:
            node = DependencyNode(
                id=req.id,
                name=req.name,
                type='requirement',
                status=req.status,
                after=req.after[:],  # Copy list
                blocks=req.blocks[:]           # Copy list
            )
            nodes[req.id] = node

            # Add edges (dependency → requirement that depends on it)
            for dep_id in req.after:
                edges.append((dep_id, req.id))

            # Add edges for blocks relationship
            for blocked_id in req.blocks:
                edges.append((req.id, blocked_id))

    def _find_cycles(self, graph: DependencyGraph) -> list[list[str]]:
        """Detect circular dependencies using depth-first search.

        Why: Uses DFS with visited set to detect cycles in directed graph.
             Tarjan's algorithm is more efficient for large graphs, but simpler
             DFS is adequate for our use case (<100 nodes typically).
        Source: requirements_tasks/.../2026-01-10_03_plan_dependency_visualization.md#4.3
        """
        cycles: list[Any] = []
        visited = set()
        rec_stack = set()

        def dfs(node_id: str, path: list[str]) -> None:
            if node_id in rec_stack:
                # Found cycle
                cycle_start = path.index(node_id)
                cycle = path[cycle_start:]
                if len(cycle) > 1:  # Ignore self-loops
                    # Normalize cycle (avoid duplicates)
                    cycle_tuple = tuple(sorted(cycle))
                    if cycle_tuple not in [tuple(sorted(c)) for c in cycles]:
                        cycles.append(cycle)
                return

            if node_id in visited:
                return

            visited.add(node_id)
            rec_stack.add(node_id)

            # Visit dependencies
            node = graph.nodes.get(node_id)
            if node:
                for dep_id in node.after:
                    dfs(dep_id, [*path, node_id])

            rec_stack.discard(node_id)

        # Start DFS from each unvisited node
        for node_id in graph.nodes:
            if node_id not in visited:
                dfs(node_id, [])

        return cycles

    def _compute_blocking_scores(self, graph: DependencyGraph) -> dict[str, int]:
        """Count how many items each node blocks (recursively).

        Why: Identifies bottlenecks - items blocking the most downstream work.
             Uses memoization to avoid redundant traversals.
             Without this, complexity is O(2^n) for tree structures.
             With memoization, complexity is O(n + e) for n nodes, e edges.
        Source: requirements_tasks/.../2026-01-10_03_plan_dependency_visualization.md#4.4
        """
        scores = {}
        memo: dict[Any, int] = {}  # Memoization cache

        def count_descendants(node_id: str, visiting: Optional[set[Any]] = None) -> int:
            if visiting is None:
                visiting = set()

            # Avoid infinite recursion on cycles
            if node_id in visiting:
                return 0

            if node_id in memo:
                return memo[node_id]

            node = graph.nodes.get(node_id)
            if not node:
                return 0

            visiting.add(node_id)

            # Direct blocks + recursive descendants
            count = len(node.blocks)
            for blocked_id in node.blocks:
                count += count_descendants(blocked_id, visiting)

            visiting.discard(node_id)
            memo[node_id] = count
            return count

        for node_id in graph.nodes:
            scores[node_id] = count_descendants(node_id)

        return scores

    def _find_longest_chain(self, graph: DependencyGraph) -> list[str]:
        """Find the longest dependency chain in the graph.

        Why: Identifies the critical path - longest sequence of dependencies.
             Useful for understanding minimum project completion time.
        Source: requirements_tasks/.../2026-01-10_03_plan_dependency_visualization.md#4.4
        """
        longest: list[Any] = []

        def dfs_longest(node_id: str, path: list[str], visited: set[Any]) -> None:
            nonlocal longest

            if node_id in visited:
                return  # Avoid cycles

            visited_copy = visited.copy()
            visited_copy.add(node_id)
            current_path = [*path, node_id]

            node = graph.nodes.get(node_id)
            if not node or len(node.blocks) == 0:
                # Leaf node - check if this is longest path
                if len(current_path) > len(longest):
                    longest = current_path[:]
            else:
                # Continue DFS on blocked items
                for blocked_id in node.blocks:
                    dfs_longest(blocked_id, current_path, visited_copy)

        # Start from root nodes (no dependencies)
        for node_id, node in graph.nodes.items():
            if node.is_root:
                dfs_longest(node_id, [], set())

        return longest


# ============================================================================
# STATISTICS CALCULATION
# ============================================================================

def calculate_statistics(requirements: list[RequirementData],
                        tasks: list[TaskData]) -> Statistics:
    """Calculate overall statistics."""
    # Count tasks by status
    open_tasks = sum(1 for t in tasks if t.status not in ['completed', 'cancelled'])
    completed_tasks = sum(1 for t in tasks if t.status == 'completed')
    blocked_tasks = sum(1 for t in tasks if t.is_blocked and t.status not in ['completed', 'cancelled'])
    critical_tasks = sum(1 for t in tasks if t.is_critical and t.status not in ['completed', 'cancelled'])
    sprint_tasks = sum(1 for t in tasks if t.urgency >= 3 and t.status not in ['completed', 'cancelled'])

    # Count legacy files
    legacy_reqs = sum(1 for r in requirements if not r.has_frontmatter)
    legacy_tasks = sum(1 for t in tasks if not t.has_frontmatter)

    # Calculate category stats
    category_stats = {}
    for category in ['FUNC', 'NFUNC', 'PROC']:
        cat_reqs = [r for r in requirements if r.category == category]
        cat_tasks = [t for t in tasks if t.parent_requirement.startswith(f'REQ-{category}')]

        cat_open = sum(1 for t in cat_tasks if t.status not in ['completed', 'cancelled'])
        cat_completed = sum(1 for t in cat_tasks if t.status == 'completed')

        # Calculate coverage: tasks that cover at least one item / total trackable items
        total_items = 0
        covered_items = 0

        for req in cat_reqs:
            req_items = len(req.trackable_items.get('acceptance_criteria', [])) + \
                       len(req.trackable_items.get('sections', []))
            total_items += req_items

            # Count covered items
            req_tasks = [t for t in cat_tasks if t.parent_requirement == req.id]
            covered_acs = set()
            covered_secs = set()
            for task in req_tasks:
                covered_acs.update(task.covers.get('acceptance_criteria', []))
                covered_secs.update(task.covers.get('sections', []))

            covered_items += len(covered_acs & set(req.trackable_items.get('acceptance_criteria', [])))
            covered_items += len(covered_secs & set(req.trackable_items.get('sections', [])))

        coverage = (covered_items / total_items * 100) if total_items > 0 else 0

        category_stats[category] = CategoryStats(
            category=category,
            requirement_count=len(cat_reqs),
            task_count=len(cat_tasks),
            open_tasks=cat_open,
            completed_tasks=cat_completed,
            coverage_percent=coverage
        )

    # Calculate overall coverage
    total_items = sum(
        len(r.trackable_items.get('acceptance_criteria', [])) +
        len(r.trackable_items.get('sections', []))
        for r in requirements
    )
    total_covered = 0
    for req in requirements:
        req_tasks = [t for t in tasks if t.parent_requirement == req.id]
        covered_acs = set()
        covered_secs = set()
        for task in req_tasks:
            covered_acs.update(task.covers.get('acceptance_criteria', []))
            covered_secs.update(task.covers.get('sections', []))

        total_covered += len(covered_acs & set(req.trackable_items.get('acceptance_criteria', [])))
        total_covered += len(covered_secs & set(req.trackable_items.get('sections', [])))

    overall_coverage = (total_covered / total_items * 100) if total_items > 0 else 0

    return Statistics(
        total_requirements=len(requirements),
        total_tasks=len(tasks),
        open_tasks=open_tasks,
        completed_tasks=completed_tasks,
        blocked_tasks=blocked_tasks,
        critical_tasks=critical_tasks,
        sprint_tasks=sprint_tasks,
        overall_coverage=overall_coverage,
        legacy_requirement_count=legacy_reqs,
        legacy_task_count=legacy_tasks,
        category_stats=category_stats
    )


# ============================================================================
# REPORT GENERATORS BASE CLASS
# ============================================================================

class ReportGeneratorBase:
    """Base class for report generators."""

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 focus: str = 'tasks'):
        self.requirements = requirements
        self.tasks = tasks
        self.focus = focus  # 'tasks' or 'requirements'

    def generate(self) -> str:
        """Generate report based on focus."""
        if self.focus == 'requirements':
            return self._generate_requirements_report()
        return self._generate_tasks_report()

    def _generate_tasks_report(self) -> str:
        """Generate task-focused report (original implementation)."""
        raise NotImplementedError

    def _generate_requirements_report(self) -> str:
        """Generate requirement-focused report (new implementation)."""
        raise NotImplementedError


# ============================================================================
# SUMMARY REPORT GENERATOR
# ============================================================================

class SummaryReportGenerator(ReportGeneratorBase):
    """Generates summary statistics table."""

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 stats: Statistics,
                 focus: str = 'tasks'):
        super().__init__(requirements, tasks, focus)
        self.stats = stats

    def _generate_tasks_report(self) -> str:
        """Generate task-focused summary."""
        lines = ["# Status Summary - Tasks", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Category-wise stats
        lines.append("| Category | Requirements | Tasks | Open | Completed | Coverage |")
        lines.append("|----------|--------------|-------|------|-----------|----------|")

        for cat in ['FUNC', 'NFUNC', 'PROC']:
            cat_stats = self.stats.category_stats.get(cat)
            if cat_stats:
                lines.append(
                    f"| {cat} | {cat_stats.requirement_count} | "
                    f"{cat_stats.task_count} | {cat_stats.open_tasks} | "
                    f"{cat_stats.completed_tasks} | {cat_stats.coverage_percent:.0f}% |"
                )

        # Total row
        lines.append(
            f"| **Total** | **{self.stats.total_requirements}** | "
            f"**{self.stats.total_tasks}** | **{self.stats.open_tasks}** | "
            f"**{self.stats.completed_tasks}** | **{self.stats.overall_coverage:.0f}%** |"
        )

        return '\n'.join(lines)

    def _generate_requirements_report(self) -> str:
        """Generate requirement-focused summary."""
        lines = ["# Status Summary - Requirements", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Count requirements by status
        lines.append("| Category | Requirements | Implemented | Active 🔄 | In Progress | Planned | Blocked |")
        lines.append("|----------|--------------|-------------|-----------|-------------|---------|---------|")

        for cat in ['FUNC', 'NFUNC', 'PROC']:
            cat_reqs = [r for r in self.requirements if r.category == cat]
            implemented = sum(1 for r in cat_reqs if r.status == 'implemented')
            active = sum(1 for r in cat_reqs if r.status == 'active')
            in_progress = sum(1 for r in cat_reqs if r.status == 'in_progress')
            planned = sum(1 for r in cat_reqs if r.status == 'planned')
            blocked = sum(1 for r in cat_reqs if r.status == 'blocked')

            lines.append(
                f"| {cat} | {len(cat_reqs)} | {implemented} | {active} | {in_progress} | {planned} | {blocked} |"
            )

        # Total row
        total_reqs = len(self.requirements)
        total_implemented = sum(1 for r in self.requirements if r.status == 'implemented')
        total_active = sum(1 for r in self.requirements if r.status == 'active')
        total_in_progress = sum(1 for r in self.requirements if r.status == 'in_progress')
        total_planned = sum(1 for r in self.requirements if r.status == 'planned')
        total_blocked = sum(1 for r in self.requirements if r.status == 'blocked')

        lines.append(
            f"| **Total** | **{total_reqs}** | **{total_implemented}** | "
            f"**{total_active}** | **{total_in_progress}** | **{total_planned}** | **{total_blocked}** |"
        )

        return '\n'.join(lines)


# ============================================================================
# PRIORITY REPORT GENERATOR
# ============================================================================

class PriorityReportGenerator(ReportGeneratorBase):
    """Generates priority-sorted list."""

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 focus: str = 'tasks',
                 package_release_map: Optional[dict[str, str]] = None):
        super().__init__(requirements, tasks, focus)
        self.package_release_map: dict[str, str] = package_release_map or {}

    def _generate_tasks_report(self) -> str:
        """Generate task-focused priority report."""
        lines = ["# Priority Queue - Tasks", ""]
        lines.append("Tasks sorted by priority score (Urgency × 10 + Impact):")
        lines.append("")

        # Filter out completed/cancelled
        active_tasks = [t for t in self.tasks if t.status not in ['completed', 'cancelled']]

        # Sort by priority score (descending)
        sorted_tasks = sorted(active_tasks, key=lambda t: t.priority_score, reverse=True)

        lines.append("| Score | Task ID | Name | Status | Urgency | Impact | Package | Release |")
        lines.append("|-------|---------|------|--------|---------|--------|---------|---------|")

        for task in sorted_tasks:
            name = task.name[:30] if len(task.name) > 30 else task.name
            package = task.target_package or '—'
            release = task.target_release or (
                self.package_release_map.get(task.target_package, '—')
                if task.target_package else '—'
            )
            lines.append(
                f"| {task.priority_score} | {task.task_id} | {name} | "
                f"{task.status} | {task.urgency_reason} | {task.impact_reason} | {package} | {release} |"
            )

        if not sorted_tasks:
            lines.append("| - | - | *No active tasks* | - | - | - | - | - |")

        return '\n'.join(lines)

    def _generate_requirements_report(self) -> str:
        """Generate requirement-focused priority report."""
        lines = ["# Priority Queue - Requirements", ""]
        lines.append("Requirements sorted by priority score (Urgency × 10 + Impact):")
        lines.append("")

        # Filter out implemented/cancelled requirements
        active_reqs = [r for r in self.requirements if r.status not in ['implemented', 'cancelled']]

        # Sort by priority score (descending)
        sorted_reqs = sorted(active_reqs, key=lambda r: r.priority_score, reverse=True)

        lines.append("| Score | Req ID | Name | Status | Urgency | Impact | Tasks | Package | Release |")
        lines.append("|-------|--------|------|--------|---------|--------|-------|---------|---------|")

        for req in sorted_reqs:
            name = req.name[:30] if len(req.name) > 30 else req.name
            task_count = sum(1 for t in self.tasks if t.parent_requirement == req.id)
            package = req.target_package or '—'
            release = req.target_release or (
                self.package_release_map.get(req.target_package, '—')
                if req.target_package else '—'
            )
            lines.append(
                f"| {req.priority_score} | {req.id} | {name} | "
                f"{req.status} | {req.urgency_reason} | {req.impact_reason} | {task_count} | {package} | {release} |"
            )

        if not sorted_reqs:
            lines.append("| - | - | *No active requirements* | - | - | - | - | - | - |")

        return '\n'.join(lines)


# ============================================================================
# BLOCKERS REPORT GENERATOR
# ============================================================================

class BlockersReportGenerator(ReportGeneratorBase):
    """Generates blockers and critical items report."""

    def _generate_tasks_report(self) -> str:
        """Generate task-focused blockers report."""
        lines = ["# Blockers & Critical Tasks", ""]

        # Section 1: Blocked tasks
        blocked = [t for t in self.tasks if t.is_blocked and t.status != 'completed']

        lines.append("## Blocked Tasks")
        lines.append("")
        if blocked:
            lines.append("| Task ID | Name | Blocked By | Note | Created |")
            lines.append("|---------|------|------------|------|---------|")
            for task in sorted(blocked, key=lambda t: t.created):
                name = task.name[:30] if len(task.name) > 30 else task.name
                blockers = ', '.join(task.awaiting) if task.awaiting else 'Status: blocked'
                note = task.awaiting_note[:60] if len(task.awaiting_note) > 60 else task.awaiting_note
                lines.append(f"| {task.task_id} | {name} | {blockers} | {note} | {task.created} |")
        else:
            lines.append("*No blocked tasks*")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Section 2: Critical tasks (U5)
        critical = [t for t in self.tasks if t.is_critical and t.status not in ['completed', 'cancelled']]

        lines.append("## Critical Tasks (Urgency = 5)")
        lines.append("")
        if critical:
            lines.append("| Task ID | Name | Urgency Reason | Status |")
            lines.append("|---------|------|----------------|--------|")
            for task in sorted(critical, key=lambda t: t.priority_score, reverse=True):
                name = task.name[:30] if len(task.name) > 30 else task.name
                lines.append(f"| {task.task_id} | {name} | {task.urgency_reason} | {task.status} |")
        else:
            lines.append("*No critical tasks*")

        lines.append("")

        # Why: Release-dependency conflicts are a special category of blocker (an item is
        #      logically unshippable if its dependency ships in a later release). Appending
        #      the conflict section here avoids duplicating it in a separate mode — users
        #      running --blockers get all blocker types in one view.
        # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md#sec-06
        detector = ReleaseConflictDetector(self.requirements, self.tasks)
        conflicts = detector.find_conflicts()
        conflict_lines = detector.format_conflicts_section(conflicts)
        if conflict_lines:
            lines.append("---")
            lines.append("")
            lines.extend(conflict_lines)

        return '\n'.join(lines)

    def _generate_requirements_report(self) -> str:
        """Generate requirement-focused blockers report."""
        lines = ["# Blockers & Critical Requirements", ""]

        # Section 1: Blocked requirements
        blocked = [r for r in self.requirements if r.status == 'blocked']

        lines.append("## Blocked Requirements")
        lines.append("")
        if blocked:
            lines.append("| Req ID | Name | Status | Created | Tasks |")
            lines.append("|--------|------|--------|---------|-------|")
            for req in sorted(blocked, key=lambda r: r.created):
                name = req.name[:30] if len(req.name) > 30 else req.name
                task_count = sum(1 for t in self.tasks if t.parent_requirement == req.id)
                lines.append(f"| {req.id} | {name} | {req.status} | {req.created} | {task_count} |")
        else:
            lines.append("*No blocked requirements*")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Section 2: Critical requirements (U5)
        critical = [r for r in self.requirements if r.urgency >= 5 and r.status not in ['implemented', 'cancelled']]

        lines.append("## Critical Requirements (Urgency = 5)")
        lines.append("")
        if critical:
            lines.append("| Req ID | Name | Urgency Reason | Status | Tasks |")
            lines.append("|--------|------|----------------|--------|-------|")
            for req in sorted(critical, key=lambda r: r.priority_score, reverse=True):
                name = req.name[:30] if len(req.name) > 30 else req.name
                task_count = sum(1 for t in self.tasks if t.parent_requirement == req.id)
                lines.append(f"| {req.id} | {name} | {req.urgency_reason} | {req.status} | {task_count} |")
        else:
            lines.append("*No critical requirements*")

        lines.append("")

        return '\n'.join(lines)


# ============================================================================
# SPRINT REPORT GENERATOR
# ============================================================================

class SprintReportGenerator(ReportGeneratorBase):
    """Generates sprint planning report (U3+ items)."""

    def _generate_tasks_report(self) -> str:
        """Generate task-focused sprint report."""
        lines = ["# Sprint Focus - Tasks (Urgency ≥ 3)", ""]
        lines.append("Tasks sorted by urgency level (U5 → U3):")
        lines.append("")

        # Filter active tasks with U3+
        sprint_tasks = [t for t in self.tasks
                       if t.urgency >= 3 and t.status not in ['completed', 'cancelled']]

        # Group by urgency
        u5_tasks = [t for t in sprint_tasks if t.urgency == 5]
        u4_tasks = [t for t in sprint_tasks if t.urgency == 4]
        u3_tasks = [t for t in sprint_tasks if t.urgency == 3]

        # U5: Must Do
        lines.append("## Must Do (U5 - Critical)")
        lines.append("")
        if u5_tasks:
            for task in sorted(u5_tasks, key=lambda t: t.priority_score, reverse=True):
                lines.append(
                    f"- `{task.task_id}`: **{task.name}** "
                    f"({task.impact_reason}) - *{task.status}*"
                )
        else:
            lines.append("*No U5 tasks*")

        lines.append("")

        # U4: Should Do
        lines.append("## Should Do (U4 - High)")
        lines.append("")
        if u4_tasks:
            for task in sorted(u4_tasks, key=lambda t: t.priority_score, reverse=True):
                lines.append(
                    f"- `{task.task_id}`: **{task.name}** "
                    f"({task.impact_reason}) - *{task.status}*"
                )
        else:
            lines.append("*No U4 tasks*")

        lines.append("")

        # U3: Nice to Have
        lines.append("## Nice to Have (U3 - Sprint Focus)")
        lines.append("")
        if u3_tasks:
            for task in sorted(u3_tasks, key=lambda t: t.priority_score, reverse=True):
                lines.append(
                    f"- `{task.task_id}`: **{task.name}** "
                    f"({task.impact_reason}) - *{task.status}*"
                )
        else:
            lines.append("*No U3 tasks*")

        lines.append("")

        return '\n'.join(lines)

    def _generate_requirements_report(self) -> str:
        """Generate requirement-focused sprint report."""
        lines = ["# Sprint Focus - Requirements (Urgency ≥ 3)", ""]
        lines.append("Requirements sorted by urgency level (U5 → U3):")
        lines.append("")

        # Filter non-implemented requirements with U3+
        sprint_reqs = [r for r in self.requirements
                      if r.urgency >= 3 and r.status not in ['implemented', 'cancelled']]

        # Group by urgency
        u5_reqs = [r for r in sprint_reqs if r.urgency == 5]
        u4_reqs = [r for r in sprint_reqs if r.urgency == 4]
        u3_reqs = [r for r in sprint_reqs if r.urgency == 3]

        # U5: Must Do
        lines.append("## Must Do (U5 - Critical)")
        lines.append("")
        if u5_reqs:
            for req in sorted(u5_reqs, key=lambda r: r.priority_score, reverse=True):
                task_count = sum(1 for t in self.tasks if t.parent_requirement == req.id)
                lines.append(
                    f"- `{req.id}`: **{req.name}** "
                    f"({req.impact_reason}) - *{req.status}* - {task_count} tasks"
                )
        else:
            lines.append("*No U5 requirements*")

        lines.append("")

        # U4: Should Do
        lines.append("## Should Do (U4 - High)")
        lines.append("")
        if u4_reqs:
            for req in sorted(u4_reqs, key=lambda r: r.priority_score, reverse=True):
                task_count = sum(1 for t in self.tasks if t.parent_requirement == req.id)
                lines.append(
                    f"- `{req.id}`: **{req.name}** "
                    f"({req.impact_reason}) - *{req.status}* - {task_count} tasks"
                )
        else:
            lines.append("*No U4 requirements*")

        lines.append("")

        # U3: Nice to Have
        lines.append("## Nice to Have (U3 - Sprint Focus)")
        lines.append("")
        if u3_reqs:
            for req in sorted(u3_reqs, key=lambda r: r.priority_score, reverse=True):
                task_count = sum(1 for t in self.tasks if t.parent_requirement == req.id)
                lines.append(
                    f"- `{req.id}`: **{req.name}** "
                    f"({req.impact_reason}) - *{req.status}* - {task_count} tasks"
                )
        else:
            lines.append("*No U3 requirements*")

        lines.append("")

        return '\n'.join(lines)


# ============================================================================
# COVERAGE REPORT GENERATOR
# ============================================================================

class CoverageReportGenerator:
    """Generates coverage analysis per requirement.

    Note: Coverage is ALWAYS task→requirement mapping, regardless of --requirements flag.
    """

    def __init__(self, requirements: list[RequirementData], tasks: list[TaskData]):
        self.requirements = requirements
        self.tasks = tasks
        self.coverage_map = self._build_coverage_map()

    def _build_coverage_map(self) -> dict[str, dict[str, list[str]]]:
        """Build map: requirement_id -> {item_id -> [task_ids]}"""
        coverage: dict[Any, Any] = {}

        for task in self.tasks:
            req_id = task.parent_requirement
            if req_id not in coverage:
                coverage[req_id] = {}

            # Map AC coverage
            for ac_id in task.covers.get('acceptance_criteria', []):
                if ac_id not in coverage[req_id]:
                    coverage[req_id][ac_id] = []
                coverage[req_id][ac_id].append(task.task_id)

            # Map section coverage
            for sec_id in task.covers.get('sections', []):
                if sec_id not in coverage[req_id]:
                    coverage[req_id][sec_id] = []
                coverage[req_id][sec_id].append(task.task_id)

        return coverage

    def generate(self) -> str:
        """Generate coverage report."""
        lines = ["# Coverage Report", ""]
        lines.append("Coverage analysis for all requirements:")
        lines.append("")

        for req in sorted(self.requirements, key=lambda r: r.id):
            # Calculate coverage for this requirement
            total_items = len(req.trackable_items.get('acceptance_criteria', [])) + \
                         len(req.trackable_items.get('sections', []))

            if total_items == 0:
                continue  # Skip requirements without trackable items

            covered_items = 0
            req_coverage = self.coverage_map.get(req.id, {})

            lines.append(f"## {req.id}: {req.name}")

            # Acceptance Criteria
            acs = req.trackable_items.get('acceptance_criteria', [])
            if acs:
                lines.append("")
                lines.append("**Acceptance Criteria:**")
                for ac in acs:
                    ac_id = ac

                    if ac_id in req_coverage:
                        covered_items += 1
                        tasks = ', '.join(req_coverage[ac_id])
                        lines.append(f"- [x] `{ac_id}` - *{tasks}*")
                    else:
                        lines.append(f"- [ ] `{ac_id}` - **GAP**")

            # Sections
            secs = req.trackable_items.get('sections', [])
            if secs:
                lines.append("")
                lines.append("**Sections:**")
                for sec in secs:
                    sec_id = sec

                    if sec_id in req_coverage:
                        covered_items += 1
                        tasks = ', '.join(req_coverage[sec_id])
                        lines.append(f"- [x] `{sec_id}` - *{tasks}*")
                    else:
                        lines.append(f"- [ ] `{sec_id}` - **GAP**")

            coverage_percent = (covered_items / total_items * 100) if total_items > 0 else 0

            # Insert coverage line after heading
            heading_idx = lines.index(f"## {req.id}: {req.name}")
            lines.insert(heading_idx + 1, f"Coverage: **{coverage_percent:.0f}%** ({covered_items}/{total_items} items)")

            lines.append("")
            lines.append("---")
            lines.append("")

        return '\n'.join(lines)


# ============================================================================
# RELEASE SUMMARY REPORT GENERATOR
# ============================================================================

class ReleaseSummaryReportGenerator:
    """Generates release-grouped overview (SEC-05).

    # Why: Groups items by release to answer "what's in release X?" and
    #      "how much progress has been made on each release?"
    #      This is orthogonal to the tasks/requirements focus axis — a release
    #      view always shows both, so it does not subclass ReportGeneratorBase.
    # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md#sec-05
    """

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 releases: list[dict[str, Any]]):
        self.requirements = requirements
        self.tasks = tasks
        self.releases = releases  # Sorted by semver, from load_releases()

    def generate(self) -> str:
        lines = ["# Release Overview", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Build lookup: version -> release metadata dict
        known_versions = {str(r.get('version', '')): r for r in self.releases}

        # Collect all versions referenced in requirements/tasks (may not exist in RELEASES.md yet)
        data_versions: set[Any] = set()
        for req in self.requirements:
            if req.target_release:
                data_versions.add(req.target_release)
        for task in self.tasks:
            if task.target_release:
                data_versions.add(task.target_release)

        # Why: Two-set merge ensures versions in data but missing from RELEASES.md are still
        #      shown (rather than silently dropped). known_versions come first (in semver
        #      order from load_releases()), then any unknown versions sorted by semver.
        #      This handles the case where someone adds target_release to a task before
        #      updating RELEASES.md.
        # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md#sec-05
        sorted_versions = [str(r.get('version', '')) for r in self.releases]
        unknown_versions = sorted(
            data_versions - set(sorted_versions),
            key=_parse_semver
        )
        all_versions = sorted_versions + unknown_versions

        for version in all_versions:
            release_meta = known_versions.get(version, {})
            release_reqs = [r for r in self.requirements if r.target_release == version]
            release_tasks = [t for t in self.tasks if t.target_release == version]

            if not release_reqs and not release_tasks:
                continue  # Skip releases with no assigned items

            name = release_meta.get('name', version)
            status = release_meta.get('status', 'unknown')
            description = release_meta.get('description', '')

            lines.append(f"### {version} {name} ({status})")
            if description:
                lines.append(description)
            lines.append("")

            # Per-category breakdown table
            lines.append("| Category | Requirements | Tasks Open | Tasks Done | Coverage |")
            lines.append("|----------|-------------|------------|------------|----------|")

            total_reqs = 0
            total_open = 0
            total_done = 0

            for cat in ['FUNC', 'NFUNC', 'PROC']:
                cat_reqs = [r for r in release_reqs if r.category == cat]
                cat_tasks = [t for t in release_tasks
                             if t.parent_requirement.startswith(f'REQ-{cat}')]
                open_t = sum(1 for t in cat_tasks if t.status not in ['completed', 'cancelled'])
                done_t = sum(1 for t in cat_tasks if t.status == 'completed')
                total_t = open_t + done_t
                coverage = f"{done_t / total_t * 100:.0f}%" if total_t > 0 else "—"

                if cat_reqs or cat_tasks:
                    lines.append(
                        f"| {cat} | {len(cat_reqs)} | {open_t} | {done_t} | {coverage} |"
                    )
                    total_reqs += len(cat_reqs)
                    total_open += open_t
                    total_done += done_t

            total_t = total_open + total_done
            total_coverage = f"{total_done / total_t * 100:.0f}%" if total_t > 0 else "—"
            lines.append(
                f"| **Total** | **{total_reqs}** | **{total_open}** | "
                f"**{total_done}** | **{total_coverage}** |"
            )
            lines.append("")

        # Unassigned section — always shown so users can see what still needs assignment
        unassigned_reqs = [r for r in self.requirements if not r.target_release and not r.target_package]
        unassigned_tasks = [t for t in self.tasks if not t.target_release and not t.target_package]

        lines.append("### Unassigned (no target_release or target_package)")
        lines.append("")
        lines.append("| Category | Requirements | Tasks |")
        lines.append("|----------|-------------|-------|")

        for cat in ['FUNC', 'NFUNC', 'PROC']:
            cat_reqs_count = sum(1 for r in unassigned_reqs if r.category == cat)
            cat_tasks_count = sum(1 for t in unassigned_tasks
                                  if t.parent_requirement.startswith(f'REQ-{cat}'))
            lines.append(f"| {cat} | {cat_reqs_count} | {cat_tasks_count} |")

        lines.append(
            f"| **Total** | **{len(unassigned_reqs)}** | **{len(unassigned_tasks)}** |"
        )
        lines.append("")

        return '\n'.join(lines)


class PackageSummaryReportGenerator:
    """Generates package-grouped overview.

    # Why: Mirrors ReleaseSummaryReportGenerator but groups by target_package instead of
    #      target_release. Needed for the package-based release model (REQ-PROC-034 SEC-05)
    #      where work is tracked against packages (PKG-x.y.z-name) not raw version strings.
    #      Reads RELEASE_BACKLOG.md for package metadata (name, version, status).
    # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/tasks/2026-03-26_impl_update-skills-and-scripts/plans_and_protocols/2026-03-26_01_plan_package-model-migration.md
    """

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 backlog_packages: list[dict[str, Any]]):
        self.requirements = requirements
        self.tasks = tasks
        # backlog_packages: list of dicts with id, name, version, status (from load_backlog_packages)
        self.backlog_packages = backlog_packages

    def generate(self) -> str:
        lines = ["# Package Overview", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Build lookup: package id -> metadata dict
        known_ids = {pkg['id']: pkg for pkg in self.backlog_packages}

        # Collect all package IDs referenced in requirements/tasks (may not be in backlog yet)
        data_ids: set[Any] = set()
        for req in self.requirements:
            if req.target_package:
                data_ids.add(req.target_package)
        for task in self.tasks:
            if task.target_package:
                data_ids.add(task.target_package)

        # Sort known packages by version then position; append unknown IDs sorted alphabetically
        backlog_order = [pkg['id'] for pkg in self.backlog_packages]
        unknown_ids = sorted(data_ids - set(backlog_order))
        all_ids = backlog_order + unknown_ids

        for pkg_id in all_ids:
            pkg_meta = known_ids.get(pkg_id, {})
            pkg_reqs = [r for r in self.requirements if r.target_package == pkg_id]
            pkg_tasks = [t for t in self.tasks if t.target_package == pkg_id]

            if not pkg_reqs and not pkg_tasks:
                continue  # Skip packages with no assigned items

            name = pkg_meta.get('name', pkg_id)
            version = pkg_meta.get('version', '?')
            status = pkg_meta.get('status', 'unknown')

            lines.append(f"### {pkg_id} — {name} (v{version}, {status})")
            lines.append("")

            lines.append("| Category | Requirements | Tasks Open | Tasks Done | Coverage |")
            lines.append("|----------|-------------|------------|------------|----------|")

            total_reqs = 0
            total_open = 0
            total_done = 0

            for cat in ['FUNC', 'NFUNC', 'PROC']:
                cat_reqs = [r for r in pkg_reqs if r.category == cat]
                cat_tasks = [t for t in pkg_tasks
                             if t.parent_requirement.startswith(f'REQ-{cat}')]
                open_t = sum(1 for t in cat_tasks if t.status not in ['completed', 'cancelled'])
                done_t = sum(1 for t in cat_tasks if t.status == 'completed')
                total_t = open_t + done_t
                coverage = f"{done_t / total_t * 100:.0f}%" if total_t > 0 else "—"

                if cat_reqs or cat_tasks:
                    lines.append(
                        f"| {cat} | {len(cat_reqs)} | {open_t} | {done_t} | {coverage} |"
                    )
                    total_reqs += len(cat_reqs)
                    total_open += open_t
                    total_done += done_t

            total_t = total_open + total_done
            total_coverage = f"{total_done / total_t * 100:.0f}%" if total_t > 0 else "—"
            lines.append(
                f"| **Total** | **{total_reqs}** | **{total_open}** | "
                f"**{total_done}** | **{total_coverage}** |"
            )
            lines.append("")

        # Unassigned section
        unassigned_reqs = [r for r in self.requirements if not r.target_package]
        unassigned_tasks = [t for t in self.tasks if not t.target_package]

        lines.append("### Unassigned (no target_package)")
        lines.append("")
        lines.append("| Category | Requirements | Tasks |")
        lines.append("|----------|-------------|-------|")

        for cat in ['FUNC', 'NFUNC', 'PROC']:
            cat_reqs_count = sum(1 for r in unassigned_reqs if r.category == cat)
            cat_tasks_count = sum(1 for t in unassigned_tasks
                                  if t.parent_requirement.startswith(f'REQ-{cat}'))
            lines.append(f"| {cat} | {cat_reqs_count} | {cat_tasks_count} |")

        lines.append(
            f"| **Total** | **{len(unassigned_reqs)}** | **{len(unassigned_tasks)}** |"
        )
        lines.append("")

        return '\n'.join(lines)


# ============================================================================
# RELEASE CONFLICT DETECTOR
# ============================================================================

class ReleaseConflictDetector:
    """Detects release-dependency ordering conflicts (SEC-06).

    # Why: Enforces the invariant release(X) >= release(Y) for all X after Y.
    #      An item assigned to an earlier release than its dependency is logically
    #      unshippable (the dependency won't be done yet). Detecting this early
    #      prevents impossible sprint plans.
    # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md#sec-06
    """

    def __init__(self, requirements: list[RequirementData], tasks: list[TaskData]):
        self.requirements = requirements
        self.tasks = tasks
        # Build lookup maps by ID for O(1) access
        self._req_map: dict[str, RequirementData] = {r.id: r for r in requirements}
        self._task_map: dict[str, TaskData] = {t.task_id: t for t in tasks}

    def find_conflicts(self) -> list[dict[str, str]]:
        """Return list of conflict dicts with keys: item, release, dep, dep_release, message."""
        conflicts = []

        # Check tasks
        for task in self.tasks:
            if not task.target_release:
                continue
            for dep_id in task.after + task.awaiting:
                dep_release = self._get_release_for_id(dep_id)
                if dep_release is None:
                    continue  # Skip unassigned deps — no constraint to violate
                if _parse_semver(task.target_release) < _parse_semver(dep_release):
                    conflicts.append({
                        'item': task.task_id,
                        'release': task.target_release,
                        'dep': dep_id,
                        'dep_release': dep_release,
                        'message': 'Dependency ships later'
                    })

        # Check requirements
        for req in self.requirements:
            if not req.target_release:
                continue
            for dep_id in req.after:
                dep_release = self._get_release_for_id(dep_id)
                if dep_release is None:
                    continue  # Skip unassigned deps
                if _parse_semver(req.target_release) < _parse_semver(dep_release):
                    conflicts.append({
                        'item': req.id,
                        'release': req.target_release,
                        'dep': dep_id,
                        'dep_release': dep_release,
                        'message': 'Dependency ships later'
                    })

        return conflicts

    def _get_release_for_id(self, item_id: str) -> Optional[str]:
        """Look up target_release for a task or requirement ID.

        # Why: Dependencies can point to either task IDs (TASK-*) or requirement IDs
        #      (REQ-*). Both maps must be checked because there is no naming convention
        #      that guarantees which type a dep_id refers to without a lookup.
        # Source: requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md#sec-06
        """
        if item_id in self._task_map:
            return self._task_map[item_id].target_release
        if item_id in self._req_map:
            return self._req_map[item_id].target_release
        return None

    def format_conflicts_section(self, conflicts: list[dict[str, str]]) -> list[str]:
        """Format conflicts as markdown section lines. Returns [] when no conflicts.

        # Why: Returning empty list (not an empty section heading) prevents noise
        #      in reports when there are no conflicts — callers check truthiness
        #      before extending the output.
        """
        if not conflicts:
            return []

        lines = ["## Release-Dependency Conflicts", ""]
        lines.append("| Item | Release | Depends On | Dep Release | Conflict |")
        lines.append("|------|---------|------------|-------------|----------|")

        for c in conflicts:
            lines.append(
                f"| {c['item']} | {c['release']} | {c['dep']} | "
                f"{c['dep_release']} | {c['message']} |"
            )

        lines.append("")
        return lines


# ============================================================================
# FULL REPORT GENERATOR
# ============================================================================

class FullReportGenerator:
    """Generates complete report with all sections."""

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 focus: str = 'tasks',
                 releases: Optional[list[dict[str, Any]]] = None,
                 package_release_map: Optional[dict[str, str]] = None):
        self.requirements = requirements
        self.tasks = tasks
        self.focus = focus
        self.releases = releases or []
        self.package_release_map: dict[str, str] = package_release_map or {}
        self.stats = calculate_statistics(requirements, tasks)

    def generate(self) -> str:
        """Combine all report modes."""
        sections = []

        # Title
        focus_label = "Requirements" if self.focus == 'requirements' else "Tasks"
        sections.append(f"# Complete Status Overview - {focus_label}")
        sections.append("")
        sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # 1. Summary
        summary_gen = SummaryReportGenerator(self.requirements, self.tasks, self.stats, self.focus)
        sections.append(summary_gen.generate())
        sections.append("")
        sections.append("---")
        sections.append("")

        # 2. Priority
        priority_gen = PriorityReportGenerator(self.requirements, self.tasks, self.focus,
                                               self.package_release_map)
        sections.append(priority_gen.generate())
        sections.append("")
        sections.append("---")
        sections.append("")

        # 3. Sprint
        sprint_gen = SprintReportGenerator(self.requirements, self.tasks, self.focus)
        sections.append(sprint_gen.generate())
        sections.append("")
        sections.append("---")
        sections.append("")

        # 4. Blockers
        blockers_gen = BlockersReportGenerator(self.requirements, self.tasks, self.focus)
        sections.append(blockers_gen.generate())
        sections.append("")
        sections.append("---")
        sections.append("")

        # 5. Coverage (always task→requirement)
        coverage_gen = CoverageReportGenerator(self.requirements, self.tasks)
        sections.append(coverage_gen.generate())
        sections.append("")
        sections.append("---")
        sections.append("")

        # 5b. Release Conflict Warnings (only shown when conflicts exist)
        conflict_detector = ReleaseConflictDetector(self.requirements, self.tasks)
        conflicts = conflict_detector.find_conflicts()
        if conflicts:
            sections.extend(conflict_detector.format_conflicts_section(conflicts))
            sections.append("---")
            sections.append("")

        # 5c. Release Summary (only shown when RELEASES.md was loaded)
        if self.releases:
            release_gen = ReleaseSummaryReportGenerator(
                self.requirements, self.tasks, self.releases
            )
            sections.append(release_gen.generate())
            sections.append("---")
            sections.append("")

        # 6. Tasks Needing Metadata (Priority: Add metadata first!)
        tasks_without_meta = [t for t in self.tasks if not t.has_frontmatter]
        if tasks_without_meta:
            sections.append("## ⚠️ Tasks Needing Metadata (Add metadata FIRST!)")
            sections.append("")
            sections.append("These tasks were manually created and need YAML frontmatter added:")
            sections.append("")
            sections.append("| Path | Name | Created | Status |")
            sections.append("|------|------|---------|--------|")

            for task in sorted(tasks_without_meta, key=lambda t: t.created, reverse=True):
                # Make path relative to project root and use forward slashes
                full_path = task.path.replace('\\', '/')
                # Find requirements_tasks/ in the path and show from there
                if 'requirements_tasks/' in full_path:
                    rel_path = 'requirements_tasks/' + full_path.split('requirements_tasks/')[1]
                else:
                    rel_path = full_path

                sections.append(
                    f"| {rel_path} | {task.name} | {task.created} | {task.status} |"
                )

            sections.append("")
            sections.append("---")
            sections.append("")

        # 7. Migration Status (if legacy files exist)
        if self.stats.legacy_requirement_count > 0 or self.stats.legacy_task_count > 0:
            sections.append("## Migration Status")
            sections.append("")

            req_migrated = self.stats.requirements_with_frontmatter
            req_total = self.stats.total_requirements
            req_percent = (req_migrated / req_total * 100) if req_total > 0 else 100

            task_migrated = self.stats.tasks_with_frontmatter
            task_total = self.stats.total_tasks
            task_percent = (task_migrated / task_total * 100) if task_total > 0 else 100

            sections.append(f"Requirements: {req_migrated}/{req_total} migrated ({req_percent:.0f}%)")
            sections.append(f"Tasks: {task_migrated}/{task_total} migrated ({task_percent:.0f}%)")
            sections.append("")

        return '\n'.join(sections)


# ============================================================================
# DEPENDENCY TREE REPORT GENERATOR
# ============================================================================

class DependencyTreeReportGenerator(ReportGeneratorBase):
    """Generates ASCII dependency tree visualization.

    Why: Uses box-drawing characters (U+251x range) for clean tree structure.
         Windows Terminal and most modern terminals support these.
    Source: requirements_tasks/.../2026-01-10_03_plan_dependency_visualization.md#5.1
    """

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 focus: str = 'tasks'):
        super().__init__(requirements, tasks, focus)
        self.builder = DependencyGraphBuilder(requirements, tasks)
        self.graph = self.builder.build(focus)

    def generate(self) -> str:
        """Generate dependency tree report."""
        lines = [f"# Dependency Tree - {self.focus.title()}", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Section 1: Active Dependencies (tree structure)
        lines.append("## Active Dependencies")
        lines.append("")

        if self.focus == 'requirements':
            lines.extend(self._render_requirement_tree())
        else:
            lines.extend(self._render_task_tree())

        lines.append("")

        # Section 2: Orphaned Items
        if self.graph.orphaned_nodes:
            lines.append("## Orphaned Items (No Dependencies)")
            lines.append("")
            for node_id in self.graph.orphaned_nodes:
                node = self.graph.nodes[node_id]
                status_icon = self._get_status_icon(node.status)
                lines.append(f"- {node.id}: {node.name} [{node.status}] {status_icon}")
            lines.append("")

        # Section 3: Circular Dependencies
        if self.graph.circular_dependencies:
            lines.append("## Circular Dependencies Detected")
            lines.append("")
            for cycle in self.graph.circular_dependencies:
                cycle_str = " -> ".join([*cycle, cycle[0]])
                lines.append(f"- CYCLE: {cycle_str}")
            lines.append("")

        return '\n'.join(lines)

    def _render_task_tree(self) -> list[str]:
        """Render tasks grouped by parent requirement."""
        lines = []

        # Group tasks by parent requirement
        by_requirement: dict[Any, Any] = {}
        for task in self.tasks:
            if task.status in ['completed', 'cancelled']:
                continue  # Skip completed tasks

            req_id = task.parent_requirement
            if req_id not in by_requirement:
                by_requirement[req_id] = []
            by_requirement[req_id].append(task)

        if not by_requirement:
            lines.append("*No active tasks with dependencies*")
            return lines

        # Render each requirement's tasks
        for req_id in sorted(by_requirement.keys()):
            # Find requirement name
            req = next((r for r in self.requirements if r.id == req_id), None)
            req_name = req.name if req else "Unknown"

            lines.append(f"{req_id} ({req_name})")

            tasks = by_requirement[req_id]
            for i, task in enumerate(tasks):
                is_last = (i == len(tasks) - 1)
                prefix = "└─" if is_last else "├─"
                status_icon = self._get_status_icon(task.status)
                blocked_warning = " [BLOCKED]" if task.is_blocked else ""

                lines.append(f"{prefix} {task.task_id}: {task.name} [{task.status}] {status_icon}{blocked_warning}")

                # Show dependencies
                if task.after:
                    dep_prefix = "   " if is_last else "│  "
                    deps_str = ", ".join(task.after)
                    lines.append(f"{dep_prefix}(depends on: {deps_str})")

            lines.append("")  # Blank line between requirements

        return lines

    def _render_requirement_tree(self) -> list[str]:
        """Render requirements as dependency tree."""
        lines = []
        visited: set[Any] = set()

        # Start from root nodes (no dependencies)
        roots = [n for n in self.graph.nodes.values() if n.is_root and n.type == 'requirement']

        if not roots:
            lines.append("*No requirements with dependencies found*")
            return lines

        for i, root in enumerate(roots):
            is_last_root = (i == len(roots) - 1)
            lines.extend(self._render_subtree(root.id, 0, visited, is_last_root))
            if not is_last_root:
                lines.append("")

        return lines

    def _render_subtree(self, node_id: str, depth: int, visited: set[Any], is_last: bool) -> list[str]:
        """Recursively render dependency subtree.

        Args:
            node_id: Current node
            depth: Indentation depth
            visited: Set of already rendered nodes (avoid cycles)
            is_last: Whether this is the last child of parent
        """
        lines = []

        if node_id in visited:
            return [f"{'  ' * depth}(already shown: {node_id})"]

        visited.add(node_id)
        node = self.graph.nodes.get(node_id)
        if not node:
            return [f"{'  ' * depth}(missing: {node_id})"]

        # Render current node
        indent = "  " * depth
        prefix = "└─" if is_last else "├─"
        status_icon = self._get_status_icon(node.status)

        if depth == 0:
            lines.append(f"{node.id} ({node.name}) [{node.status}] {status_icon}")
        else:
            lines.append(f"{indent}{prefix} {node.id} ({node.name}) [{node.status}] {status_icon}")

        # Render blocked items (children)
        if node.blocks:
            for i, blocked_id in enumerate(node.blocks):
                child_is_last = (i == len(node.blocks) - 1)
                lines.extend(self._render_subtree(blocked_id, depth + 1, visited, child_is_last))

        return lines

    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        icons = {
            'completed': '✓',
            'in_progress': '⏳',
            'pending': '⏸',
            'planned': '⏸',
            'blocked': '🚫',
            'cancelled': '❌',
            'implemented': '✓',
            'active': '🔄'
        }
        return icons.get(status, '')

    def _generate_tasks_report(self) -> str:
        """Override base class method."""
        return self.generate()

    def _generate_requirements_report(self) -> str:
        """Override base class method."""
        return self.generate()


# ============================================================================
# CRITICAL PATH REPORT GENERATOR
# ============================================================================

class CriticalPathReportGenerator(ReportGeneratorBase):
    """Generates critical path analysis report."""

    def __init__(self, requirements: list[RequirementData],
                 tasks: list[TaskData],
                 focus: str = 'tasks'):
        super().__init__(requirements, tasks, focus)
        self.builder = DependencyGraphBuilder(requirements, tasks)
        self.graph = self.builder.build(focus)

    def generate(self) -> str:
        """Generate critical path report."""
        lines = ["# Critical Path Analysis", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Section 1: Most Blocking Items
        lines.append("## Most Blocking Items (items that block the most work)")
        lines.append("")
        lines.append("| Item | Type | Blocks Count | Downstream Impact | Status |")
        lines.append("|------|------|--------------|-------------------|--------|")

        # Sort by blocking score
        sorted_nodes = sorted(
            self.graph.nodes.values(),
            key=lambda n: self.graph.blocking_scores.get(n.id, 0),
            reverse=True
        )

        for node in sorted_nodes[:10]:  # Top 10
            direct_blocks = len(node.blocks)
            total_impact = self.graph.blocking_scores.get(node.id, 0)
            status_icon = self._get_status_icon(node.status)

            lines.append(
                f"| {node.id} | {node.type} | "
                f"{direct_blocks} direct, {total_impact} total | "
                f"{total_impact} items | {node.status} {status_icon} |"
            )

        lines.append("")

        # Section 2: Longest Dependency Chains
        lines.append("## Longest Dependency Chains")
        lines.append("")

        longest = self.graph.critical_path
        if longest:
            chain_str = " -> ".join(longest)
            lines.append(f"**Critical Path (depth: {len(longest)}):**")
            lines.append(chain_str)
        else:
            lines.append("*No dependency chains found*")

        lines.append("")

        # Section 3: Bottleneck Warnings
        lines.append("## Bottleneck Warnings")
        lines.append("")

        # Find in-progress items blocking multiple items
        bottlenecks = [
            n for n in sorted_nodes
            if n.status in ['in_progress', 'planned'] and len(n.blocks) > 0
        ]

        if bottlenecks:
            for node in bottlenecks[:5]:  # Top 5
                blocked_items = ", ".join(node.blocks[:3])  # Show first 3
                if len(node.blocks) > 3:
                    blocked_items += f", ... ({len(node.blocks) - 3} more)"

                lines.append(f"- **{node.id}** ({node.status}) blocks {len(node.blocks)} items")
                lines.append("  - Consider prioritizing completion")
                lines.append(f"  - Blocked items: {blocked_items}")
                lines.append("")
        else:
            lines.append("*No bottlenecks detected*")

        return '\n'.join(lines)

    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        icons = {
            'completed': '✓',
            'in_progress': '⏳',
            'pending': '⏸',
            'planned': '⏸',
            'blocked': '🚫',
            'cancelled': '❌',
            'implemented': '✓',
            'active': '🔄'
        }
        return icons.get(status, '')

    def _generate_tasks_report(self) -> str:
        """Override base class method."""
        return self.generate()

    def _generate_requirements_report(self) -> str:
        """Override base class method."""
        return self.generate()


# ============================================================================
# DEPENDENCY GRAPH EXPORTER
# ============================================================================

class DependencyGraphExporter:
    """Exports dependency graph to external formats.

    Why: DOT format for generating SVG/PNG visualizations with Graphviz.
         Mermaid format for embedding in markdown/documentation.
    Source: requirements_tasks/.../2026-01-10_03_plan_dependency_visualization.md#5.3
    """

    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def export_dot(self) -> str:
        """Export to Graphviz DOT format."""
        lines = ["digraph dependencies {"]
        lines.append("    rankdir=TB;")
        lines.append("    node [shape=box];")
        lines.append("")

        # Add nodes
        lines.append("    // Nodes")
        for node_id, node in self.graph.nodes.items():
            color = self._get_dot_color(node.status)
            label = f"{node.id}\\n{node.name[:20]}"
            safe_id = node_id.replace('-', '_')
            lines.append(f'    "{safe_id}" [label="{label}" fillcolor={color} style=filled];')

        lines.append("")
        lines.append("    // Edges")

        # Add edges
        circular_edges = set()
        for cycle in self.graph.circular_dependencies:
            for i in range(len(cycle)):
                next_i = (i + 1) % len(cycle)
                circular_edges.add((cycle[i], cycle[next_i]))

        for from_id, to_id in self.graph.edges:
            safe_from = from_id.replace('-', '_')
            safe_to = to_id.replace('-', '_')
            is_circular = (from_id, to_id) in circular_edges
            color = "red" if is_circular else "black"
            label = "circular" if is_circular else "blocks"
            lines.append(f'    "{safe_from}" -> "{safe_to}" [color={color} label="{label}"];')

        lines.append("}")
        return '\n'.join(lines)

    def export_mermaid(self) -> str:
        """Export to Mermaid diagram format."""
        lines = ["graph TB"]

        # Add nodes with styling
        for node_id, node in self.graph.nodes.items():
            safe_id = node_id.replace('-', '_')
            label = f"{node.id}: {node.name[:20]}"
            style_class = self._get_mermaid_class(node.status)
            lines.append(f'    {safe_id}["{label}"]:::{style_class}')

        # Add edges
        circular_edges = set()
        for cycle in self.graph.circular_dependencies:
            for i in range(len(cycle)):
                next_i = (i + 1) % len(cycle)
                circular_edges.add((cycle[i], cycle[next_i]))

        for from_id, to_id in self.graph.edges:
            safe_from = from_id.replace('-', '_')
            safe_to = to_id.replace('-', '_')

            is_circular = (from_id, to_id) in circular_edges
            if is_circular:
                lines.append(f'    {safe_from} -.->|circular| {safe_to}')
            else:
                lines.append(f'    {safe_from} --> {safe_to}')

        # Add style definitions
        lines.append("")
        lines.append("    classDef inprogress fill:#ffd700")
        lines.append("    classDef pending fill:#f0f0f0")
        lines.append("    classDef planned fill:#f0f0f0")
        lines.append("    classDef completed fill:#90ee90")
        lines.append("    classDef implemented fill:#90ee90")
        lines.append("    classDef active fill:#add8e6")
        lines.append("    classDef blocked fill:#ff6b6b")
        lines.append("    classDef cancelled fill:#d3d3d3")

        return '\n'.join(lines)

    def _get_dot_color(self, status: str) -> str:
        """Get Graphviz color for status."""
        colors = {
            'completed': 'lightgreen',
            'implemented': 'lightgreen',
            'active': 'lightblue',
            'in_progress': 'gold',
            'pending': 'white',
            'planned': 'white',
            'blocked': 'lightcoral',
            'cancelled': 'lightgray'
        }
        return colors.get(status, 'white')

    def _get_mermaid_class(self, status: str) -> str:
        """Get Mermaid CSS class for status."""
        classes = {
            'completed': 'completed',
            'implemented': 'implemented',
            'active': 'active',
            'in_progress': 'inprogress',
            'pending': 'pending',
            'planned': 'planned',
            'blocked': 'blocked',
            'cancelled': 'cancelled'
        }
        return classes.get(status, 'pending')


# ============================================================================
# GIT HELPERS
# ============================================================================

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
            "Generated by scripts/artifacts/generate_status_overview.py"
        )
        subprocess.run(["git", "commit", "-m", message], cwd=project_root, check=True)
        print(f"Committed {rel}")
    else:
        print(f"No changes to commit ({rel} is up to date)")


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def parse_arguments() -> Any:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate status overview reports for requirements and tasks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Task-focused reports (default)
  python scripts/generate_status_overview.py --summary
  python scripts/generate_status_overview.py --priority --output sprint.md
  python scripts/generate_status_overview.py --full --category FUNC

  # Requirement-focused reports
  python scripts/generate_status_overview.py --requirements --summary
  python scripts/generate_status_overview.py --requirements --priority
  python scripts/generate_status_overview.py --requirements --sprint --category PROC

  # Coverage report (tasks covering requirements)
  python scripts/generate_status_overview.py --coverage --format md
        """
    )

    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--summary', action='store_true',
                           help='Quick stats table (tasks or requirements)')
    mode_group.add_argument('--priority', action='store_true',
                           help='Sorted by priority score (tasks or requirements)')
    mode_group.add_argument('--coverage', action='store_true',
                           help='Coverage %% per requirement with gaps (task->requirement mapping)')
    mode_group.add_argument('--blockers', action='store_true',
                           help='Blocked and critical items (tasks or requirements)')
    mode_group.add_argument('--sprint', action='store_true',
                           help='Sprint focus - U3+ urgency (tasks or requirements)')
    mode_group.add_argument('--full', action='store_true',
                           help='Complete report with all sections (tasks or requirements)')
    mode_group.add_argument('--dependencies', action='store_true',
                           help='Dependency tree visualization (ASCII art)')
    mode_group.add_argument('--dep-graph', action='store_true',
                           help='Export dependency graph (DOT/Mermaid format)')
    mode_group.add_argument('--critical-path', action='store_true',
                           help='Critical path analysis (bottlenecks and chains)')
    mode_group.add_argument('--release-summary', action='store_true',
                           help='Release-grouped overview: counts and progress per release version')
    mode_group.add_argument('--package-summary', action='store_true',
                           help='Package-grouped overview: counts and progress per package')

    # Output options
    parser.add_argument('--output', '-o', type=str,
                       default='requirements_tasks/STATUS.md',
                       help='Output file path (default: requirements_tasks/STATUS.md)')
    parser.add_argument('--format', '-f', choices=['md', 'json'],
                       default='md',
                       help='Output format: md (markdown) or json')
    parser.add_argument('--graph-format', choices=['dot', 'mermaid'],
                       default='dot',
                       help='Graph export format for --dep-graph (default: dot)')

    # Report focus (tasks vs requirements)
    parser.add_argument('--requirements', '-r', action='store_true',
                       help='Generate report focused on requirements instead of tasks')

    # Filtering options
    parser.add_argument('--category', '-c', choices=['FUNC', 'NFUNC', 'PROC'],
                       help='Filter by category')
    parser.add_argument('--release', type=str, metavar='VERSION',
                       help='Filter output to items assigned to a specific release version (e.g. 0.1.0)')
    parser.add_argument('--package', type=str, metavar='PKG_ID',
                       help='Filter output to items assigned to a specific package ID (e.g. PKG-0.0.1-core)')
    parser.add_argument('--include-legacy', action='store_true',
                       help='Include files without YAML frontmatter')

    # Verbose mode
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--no-commit', action='store_true',
                       help='Skip git commit (useful for testing).')

    args = parser.parse_args()

    # Default to --full if no mode specified
    if not any([args.summary, args.priority, args.coverage,
                args.blockers, args.sprint, args.full,
                args.dependencies, args.dep_graph, args.critical_path,
                args.release_summary, args.package_summary]):
        args.full = True

    # Warn if --requirements used with --coverage
    if args.requirements and args.coverage:
        print("Warning: --requirements flag ignored for coverage mode.")
        print("Coverage mode always shows task->requirement mapping.")
        print()

    return args


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main() -> None:
    """Main entry point."""
    args = parse_arguments()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    if not (project_root / "requirements_tasks").exists():
        print(f"Error: requirements_tasks/ not found in {project_root}")
        sys.exit(1)

    # Initialize scanner
    scanner = StatusScanner(project_root, verbose=args.verbose)

    # Scan all files
    print("Scanning requirements...")
    requirements = scanner.scan_requirements()
    print(f"  Found {len(requirements)} requirements")

    print("Scanning tasks...")
    tasks = scanner.scan_tasks()
    print(f"  Found {len(tasks)} tasks")

    # Load release definitions from RELEASES.md
    releases = load_releases(project_root)
    if releases:
        print(f"  Found {len(releases)} releases in RELEASES.md")
    else:
        print("  No RELEASES.md found — release features disabled")

    # Apply filters
    if args.category:
        requirements = [r for r in requirements if r.category == args.category]
        tasks = [t for t in tasks if t.parent_requirement.startswith(f"REQ-{args.category}")]

    # Build package → release lookup from RELEASE_BACKLOG.md early so the
    # --release filter below can use it.
    backlog_packages = load_backlog_packages(project_root)
    package_release_map: dict[str, str] = {
        pkg['id']: pkg['version'] for pkg in backlog_packages if pkg.get('id') and pkg.get('version')
    }

    if args.release:
        # Why: requirements/tasks use target_package (e.g. "QR Transfer Send") rather than
        # target_release directly. The package-to-release mapping lives in RELEASE_BACKLOG.md
        # (loaded above). We include an item if its target_release matches OR if its
        # target_package maps to the requested release via that backlog.
        release_packages = {pkg_id for pkg_id, ver in package_release_map.items() if ver == args.release}
        requirements = [r for r in requirements
                        if r.target_release == args.release
                        or r.target_package in release_packages]
        tasks = [t for t in tasks
                 if t.target_release == args.release
                 or t.target_package in release_packages]
        print(f"  Filtered to release {args.release}: "
              f"{len(requirements)} requirements, {len(tasks)} tasks")

    if args.package:
        requirements = [r for r in requirements if r.target_package == args.package]
        tasks = [t for t in tasks if t.target_package == args.package]
        print(f"  Filtered to package {args.package}: "
              f"{len(requirements)} requirements, {len(tasks)} tasks")

    if not args.include_legacy:
        requirements = [r for r in requirements if r.has_frontmatter]
        # Always include all tasks (even without frontmatter) so manually created tasks are visible
        # tasks = [t for t in tasks if t.has_frontmatter]

    # Determine focus
    focus = 'requirements' if args.requirements else 'tasks'

    # Generate report
    print("\nGenerating report...")

    generator: Any
    if args.summary:
        stats = calculate_statistics(requirements, tasks)
        generator = SummaryReportGenerator(requirements, tasks, stats, focus)
        report = generator.generate()
    elif args.priority:
        generator = PriorityReportGenerator(requirements, tasks, focus, package_release_map)
        report = generator.generate()
    elif args.coverage:
        generator = CoverageReportGenerator(requirements, tasks)
        report = generator.generate()
    elif args.blockers:
        generator = BlockersReportGenerator(requirements, tasks, focus)
        report = generator.generate()
    elif args.sprint:
        generator = SprintReportGenerator(requirements, tasks, focus)
        report = generator.generate()
    elif args.dependencies:
        generator = DependencyTreeReportGenerator(requirements, tasks, focus)
        report = generator.generate()
    elif args.dep_graph:
        builder = DependencyGraphBuilder(requirements, tasks)
        graph = builder.build(focus)
        exporter = DependencyGraphExporter(graph)

        if args.graph_format == 'mermaid':
            report = exporter.export_mermaid()
        else:
            report = exporter.export_dot()
    elif args.critical_path:
        generator = CriticalPathReportGenerator(requirements, tasks, focus)
        report = generator.generate()
    elif args.release_summary:
        generator = ReleaseSummaryReportGenerator(requirements, tasks, releases)
        report = generator.generate()
    elif args.package_summary:
        generator = PackageSummaryReportGenerator(requirements, tasks, backlog_packages)
        report = generator.generate()
    else:  # --full
        generator = FullReportGenerator(requirements, tasks, focus, releases=releases,
                                        package_release_map=package_release_map)
        report = generator.generate()

    # Output
    if args.format == 'json':
        print("JSON format not yet implemented")
        sys.exit(1)

    # Write to file or stdout
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')

    print(f"\nReport written to: {output_path}")

    if not args.no_commit:
        git_commit(output_path)


if __name__ == "__main__":
    main()
