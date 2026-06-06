# Implementation Plan: generate_status_overview.py Script

**Agent**: architecture-advisor
**Agent ID**: [To be logged via log-protocol]
**Date**: 2026-01-10
**Task**: TASK-PROC-009-04 (Deliverable #4: Status Overview Script)

## 1. Executive Summary

This plan details the implementation of `scripts/generate_status_overview.py`, a comprehensive status reporting tool that supports 6 different modes of querying requirements and tasks. The script will replace the existing PowerShell script with enhanced YAML frontmatter parsing while maintaining backward compatibility with folder naming conventions.

**Key Design Principles**:
- Parse YAML frontmatter as primary source of truth
- Fall back to folder naming conventions for legacy files
- Modular architecture for each report mode
- Reusable YAML parser from existing scripts
- Windows compatibility guaranteed
- Support both task-focused and requirement-focused reports via `--requirements` flag

**Testing Approach**:
- Create 2 temporary test task files with YAML frontmatter (tasks not migrated yet)
- Remove temporary files after successful testing

---

## 1.1 Plan Updates (User Requested)

**Date**: 2026-01-10

**Updates requested by user**:

1. **Temporary Test Task Files** (Section 5.3)
   - **Why**: Tasks not yet migrated to new meta information structure
   - **Solution**: Create 2 temporary task folders with YAML frontmatter for testing
   - **Location**: `_test_*` prefixed folders in requirements_and_tasks/tasks/
   - **Cleanup**: Delete both folders after Phase 7 validation

2. **Requirements Mode Flag** (`--requirements`) (Section 6.7)
   - **Why**: Need to generate reports focused on requirements, not just tasks
   - **Implementation**: New `--requirements` flag that switches report focus
   - **Affected modes**:
     - ✅ Summary mode (requirements stats instead of task stats)
     - ✅ Priority mode (requirements sorted by priority)
     - ✅ Blockers mode (blocked/critical requirements)
     - ✅ Sprint mode (U3+ requirements)
     - ✅ Full mode (all sections for requirements)
     - ⚠️ Coverage mode (ALWAYS task→requirement, flag ignored with warning)
   - **Implementation**: Base class with `focus` parameter ('tasks' | 'requirements')

**Impact on plan**:
- **File size**: Increased from ~800-1000 lines to ~1000-1200 lines
- **Phases**: Added Phase 0 (test setup) and Phase 7 (cleanup), now 8 phases total
- **Complexity**: Medium → Medium-High (dual mode support)
- **Testing**: Expanded testing checklist to cover both modes

---

## 2. Script Architecture Overview

### 2.1 High-Level Structure

```
generate_status_overview.py
├── YAML Parser (reused from validate_meta.py)
├── Data Models (Requirements, Tasks, Statistics)
├── Scanner Module (find and parse all files)
├── Report Generators (6 modes)
│   ├── SummaryReport
│   ├── PriorityReport
│   ├── CoverageReport
│   ├── BlockersReport
│   ├── SprintReport
│   └── FullReport
├── CLI Argument Handler
└── Main Orchestrator
```

### 2.2 Design Patterns

**Pattern 1: Strategy Pattern for Report Modes**
- Each mode implements a `ReportGenerator` interface
- `generate()` method returns formatted markdown
- Composition in `FullReport` mode

**Pattern 2: Data Collection Phase + Rendering Phase**
- Phase 1: Scan all files, build data structures
- Phase 2: Generate reports from collected data
- Separation of concerns: parsing vs. presentation

**Pattern 3: Backward Compatibility Fallback**
- Try YAML frontmatter first (primary)
- Fall back to folder naming if no frontmatter
- Track which files are legacy for migration reporting

---

## 3. Data Models

### 3.1 Core Data Structures

```python
@dataclass
class RequirementData:
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
    trackable_items: Dict[str, List[str]]  # AC and SEC IDs
    has_frontmatter: bool  # True if YAML found, False if legacy

    @property
    def priority_score(self) -> int:
        return (self.urgency * 10) + self.impact

@dataclass
class TaskData:
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
    depends_on: List[str]
    blocked_by: List[str]
    covers: Dict[str, List[str]]  # AC and SEC IDs
    has_frontmatter: bool

    @property
    def priority_score(self) -> int:
        return (self.urgency * 10) + self.impact

    @property
    def is_blocked(self) -> bool:
        return self.status == 'blocked' or len(self.blocked_by) > 0

    @property
    def is_critical(self) -> bool:
        return self.urgency >= 5

@dataclass
class Statistics:
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
    category_stats: Dict[str, CategoryStats]

@dataclass
class CategoryStats:
    category: str  # FUNC, NFUNC, PROC
    requirement_count: int
    task_count: int
    open_tasks: int
    completed_tasks: int
    coverage_percent: float
```

---

## 4. YAML Frontmatter Parsing

### 4.1 Reuse from validate_meta.py

**Decision**: Reuse the existing YAML parser from `validate_meta.py`.

**Justification**:
- Already tested and working
- Handles BOM characters
- Falls back to simple parser if PyYAML not available
- Supports our specific frontmatter format

**Implementation**:
```python
class YAMLParser:
    """Reusable YAML frontmatter parser."""

    def parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract and parse YAML frontmatter from markdown content."""
        # Copy implementation from validate_meta.py
        # Handle BOM, extract between --- markers, parse YAML
        pass

    def _parse_simple_yaml(self, yaml_text: str) -> Dict[str, Any]:
        """Fallback simple YAML parser."""
        # Copy from validate_meta.py
        pass
```

---

## 5. Backward Compatibility Strategy

### 5.1 Folder Naming Convention Fallback

**When**: No YAML frontmatter found in file
**How**: Parse folder name and structure

#### For Requirements (requirements.md)

```python
def parse_legacy_requirement(path: Path) -> RequirementData:
    """Parse requirement from folder structure (no frontmatter)."""

    # Extract name from parent folder
    name = path.parent.name.replace('_', ' ').title()

    # Determine category from path
    path_str = str(path)
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
        id=f"REQ-{category}-LEGACY",  # Mark as legacy
        path=str(path),
        name=name,
        category=category,
        status='unknown',  # Can't determine without frontmatter
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
```

#### For Tasks (goal.md)

```python
def parse_legacy_task(path: Path) -> TaskData:
    """Parse task from folder structure (no frontmatter)."""

    folder_name = path.parent.name

    # Extract date: YYYY-MM-DD
    date_match = re.match(r'^(\d{4}-\d{2}-\d{2})_', folder_name)
    created = date_match.group(1) if date_match else 'unknown'

    # Extract status from suffix
    if folder_name.endswith('(completed)'):
        status = 'completed'
        name = folder_name.replace('(completed)', '').strip()
    elif folder_name.endswith('(superseded)'):
        status = 'cancelled'
        name = folder_name.replace('(superseded)', '').strip()
    else:
        status = 'in_progress'  # Assume active
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
        depends_on=[],
        blocked_by=[],
        covers={},
        has_frontmatter=False
    )
```

### 5.2 Migration Tracking

Track legacy files to report migration progress:

```python
@dataclass
class MigrationStatus:
    total_requirements: int
    requirements_with_frontmatter: int
    total_tasks: int
    tasks_with_frontmatter: int
    legacy_requirement_paths: List[str]
    legacy_task_paths: List[str]

    @property
    def requirements_migration_percent(self) -> float:
        if self.total_requirements == 0:
            return 100.0
        return (self.requirements_with_frontmatter / self.total_requirements) * 100

    @property
    def tasks_migration_percent(self) -> float:
        if self.total_tasks == 0:
            return 100.0
        return (self.tasks_with_frontmatter / self.total_tasks) * 100
```

### 5.3 Temporary Test Task Files

**Problem**: Tasks are not yet migrated to the new meta information structure, making it impossible to test task parsing.

**Solution**: Create 2 temporary test task folders with complete YAML frontmatter in goal.md files.

#### Test Task 1: High-Priority Completed Task

**Location**: `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/tasks/_test_2026-01-05_impl_test_high_priority_(completed)/`

**goal.md**:
```yaml
---
task_id: TASK-PROC-009-TEST1
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-01-05
completed: 2026-01-08
depends_on: []
blocked_by: []
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-02]
scope_description: "Test task for validating script functionality"
requirements_version:
  commit: f7add7a
  file: ../requirements.md
---

# Goal: Test High Priority Task

This is a temporary test task to validate the status overview script.
\```

#### Test Task 2: Medium-Priority Blocked Task

**Location**: `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/tasks/_test_2026-01-07_explore_test_blocked/`

**goal.md**:
```yaml
---
task_id: TASK-PROC-009-TEST2
type: explore
parent_requirement: REQ-PROC-009
urgency: 3
urgency_reason: U3-SPRINT
impact: 4
impact_reason: I4-DEBT
status: blocked
effort: L
created: 2026-01-07
completed: null
depends_on: [TASK-PROC-009-TEST1]
blocked_by: [TASK-PROC-009-05]
covers:
  acceptance_criteria: []
  sections: [SEC-13]
scope_description: "Test blocked task for script validation"
requirements_version:
  commit: f7add7a
  file: ../requirements.md
---

# Goal: Test Blocked Task

This is a temporary test task to validate blockers reporting.
\```

#### Test File Management

1. **Creation**: Create these folders in Phase 0 (before implementation)
2. **Validation**: Use them to test all report modes during development
3. **Cleanup**: Delete both folders after successful integration testing (Phase 6)

**Naming Convention**: Prefix with `_test_` to clearly mark as temporary test data

---

## 6. Report Modes Implementation

### 6.1 Mode 1: Summary Report (`--summary`)

**Purpose**: Quick overview stats table
**Output Format**: Markdown table

```python
class SummaryReportGenerator:
    """Generates summary statistics table."""

    def generate(self, requirements: List[RequirementData],
                 tasks: List[TaskData],
                 stats: Statistics) -> str:
        """
        Output:
        # Status Summary

        | Category | Requirements | Tasks | Open | Completed | Coverage |
        |----------|--------------|-------|------|-----------|----------|
        | FUNC     | 14           | 25    | 8    | 17        | 45%      |
        | NFUNC    | 14           | 12    | 3    | 9         | 62%      |
        | PROC     | 9            | 15    | 2    | 13        | 78%      |
        | **Total**| **37**       | **52**| **13**| **39**   | **58%**  |
        """

        lines = ["# Status Summary", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Category-wise stats
        lines.append("| Category | Requirements | Tasks | Open | Completed | Coverage |")
        lines.append("|----------|--------------|-------|------|-----------|----------|")

        for cat in ['FUNC', 'NFUNC', 'PROC']:
            cat_stats = stats.category_stats.get(cat)
            if cat_stats:
                lines.append(
                    f"| {cat} | {cat_stats.requirement_count} | "
                    f"{cat_stats.task_count} | {cat_stats.open_tasks} | "
                    f"{cat_stats.completed_tasks} | {cat_stats.coverage_percent:.0f}% |"
                )

        # Total row
        lines.append(
            f"| **Total** | **{stats.total_requirements}** | "
            f"**{stats.total_tasks}** | **{stats.open_tasks}** | "
            f"**{stats.completed_tasks}** | **{stats.overall_coverage:.0f}%** |"
        )

        return '\n'.join(lines)
```

### 6.2 Mode 2: Priority Report (`--priority`)

**Purpose**: Tasks sorted by priority score (urgency × 10 + impact)
**Output Format**: Sorted table

```python
class PriorityReportGenerator:
    """Generates priority-sorted task list."""

    def generate(self, tasks: List[TaskData]) -> str:
        """
        Output:
        # Priority Queue

        | Score | Task ID | Requirement | Status | Urgency | Impact |
        |-------|---------|-------------|--------|---------|--------|
        | 55    | TASK-FUNC-005-01 | Plan Evaluation | in_progress | U5-BLOCK | I5-MVP |
        | 54    | TASK-PROC-009-02 | Meta Migration | pending | U5-PROC | I4-DEBT |
        """

        lines = ["# Priority Queue", ""]
        lines.append("Tasks sorted by priority score (Urgency × 10 + Impact):")
        lines.append("")

        # Filter out completed/cancelled
        active_tasks = [t for t in tasks if t.status not in ['completed', 'cancelled']]

        # Sort by priority score (descending)
        sorted_tasks = sorted(active_tasks, key=lambda t: t.priority_score, reverse=True)

        lines.append("| Score | Task ID | Name | Status | Urgency | Impact |")
        lines.append("|-------|---------|------|--------|---------|--------|")

        for task in sorted_tasks:
            lines.append(
                f"| {task.priority_score} | {task.task_id} | {task.name[:30]} | "
                f"{task.status} | {task.urgency_reason} | {task.impact_reason} |"
            )

        return '\n'.join(lines)
```

### 6.3 Mode 3: Coverage Report (`--coverage`)

**Purpose**: Coverage % per requirement, gaps highlighted
**Output Format**: Detailed coverage breakdown

```python
class CoverageReportGenerator:
    """Generates coverage analysis per requirement."""

    def __init__(self, requirements: List[RequirementData], tasks: List[TaskData]):
        self.requirements = requirements
        self.tasks = tasks
        self.coverage_map = self._build_coverage_map()

    def _build_coverage_map(self) -> Dict[str, Dict[str, List[str]]]:
        """Build map: requirement_id -> {item_id -> [task_ids]}"""
        coverage = {}

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
        """
        Output:
        # Coverage Report

        ## REQ-FUNC-005: Plan Evaluation View
        Coverage: 25% (3/12 AC)
        - [x] AC-01: Displays results - TASK-FUNC-005-01
        - [ ] AC-02: Simple Mode chart - **GAP**
        """

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
                    if isinstance(ac, dict):
                        ac_id = ac['id']
                        ac_text = ac.get('text', 'No description')
                    else:
                        ac_id = ac
                        ac_text = 'No description'

                    if ac_id in req_coverage:
                        covered_items += 1
                        tasks = ', '.join(req_coverage[ac_id])
                        lines.append(f"- [x] `{ac_id}`: {ac_text[:50]} - *{tasks}*")
                    else:
                        lines.append(f"- [ ] `{ac_id}`: {ac_text[:50]} - **GAP**")

            # Sections
            secs = req.trackable_items.get('sections', [])
            if secs:
                lines.append("")
                lines.append("**Sections:**")
                for sec in secs:
                    if isinstance(sec, dict):
                        sec_id = sec['id']
                        sec_name = sec.get('name', 'No name')
                    else:
                        sec_id = sec
                        sec_name = 'No name'

                    if sec_id in req_coverage:
                        covered_items += 1
                        tasks = ', '.join(req_coverage[sec_id])
                        lines.append(f"- [x] `{sec_id}`: {sec_name} - *{tasks}*")
                    else:
                        lines.append(f"- [ ] `{sec_id}`: {sec_name} - **GAP**")

            coverage_percent = (covered_items / total_items * 100) if total_items > 0 else 0
            lines.insert(lines.index(f"## {req.id}: {req.name}") + 1,
                        f"Coverage: **{coverage_percent:.0f}%** ({covered_items}/{total_items} items)")
            lines.append("")
            lines.append("---")
            lines.append("")

        return '\n'.join(lines)
```

### 6.4 Mode 4: Blockers Report (`--blockers`)

**Purpose**: Show blocked tasks and critical (U5) tasks
**Output Format**: Two sections

```python
class BlockersReportGenerator:
    """Generates blockers and critical tasks report."""

    def generate(self, tasks: List[TaskData]) -> str:
        """
        Output:
        # Blockers & Critical Tasks

        ## Blocked Tasks
        | Task | Blocked By | Since |
        |------|------------|-------|
        | TASK-FUNC-007-02 | TASK-FUNC-007-01 | 2026-01-05 |

        ## Critical (U5)
        | Task | Urgency Reason | Status |
        |------|----------------|--------|
        | TASK-PROC-009-01 | U5-PROC | in_progress |
        """

        lines = ["# Blockers & Critical Tasks", ""]

        # Section 1: Blocked tasks
        blocked = [t for t in tasks if t.is_blocked and t.status != 'completed']

        lines.append("## Blocked Tasks")
        lines.append("")
        if blocked:
            lines.append("| Task ID | Name | Blocked By | Created |")
            lines.append("|---------|------|------------|---------|")
            for task in sorted(blocked, key=lambda t: t.created):
                blockers = ', '.join(task.blocked_by) if task.blocked_by else 'Unknown'
                lines.append(f"| {task.task_id} | {task.name[:30]} | {blockers} | {task.created} |")
        else:
            lines.append("*No blocked tasks*")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Section 2: Critical tasks (U5)
        critical = [t for t in tasks if t.is_critical and t.status not in ['completed', 'cancelled']]

        lines.append("## Critical Tasks (Urgency = 5)")
        lines.append("")
        if critical:
            lines.append("| Task ID | Name | Urgency Reason | Status |")
            lines.append("|---------|------|----------------|--------|")
            for task in sorted(critical, key=lambda t: t.priority_score, reverse=True):
                lines.append(f"| {task.task_id} | {task.name[:30]} | {task.urgency_reason} | {task.status} |")
        else:
            lines.append("*No critical tasks*")

        lines.append("")

        return '\n'.join(lines)
```

### 6.5 Mode 5: Sprint Report (`--sprint`)

**Purpose**: Tasks with U3+ urgency (sprint focus)
**Output Format**: Grouped by urgency level

```python
class SprintReportGenerator:
    """Generates sprint planning report (U3+ tasks)."""

    def generate(self, tasks: List[TaskData]) -> str:
        """
        Output:
        # Sprint Focus (U3+)

        ## Must Do (U5)
        - TASK-PROC-009-01: Meta Info Foundation (I5-ENAB) - in_progress

        ## Should Do (U4)
        - TASK-PROC-009-02: Requirements Migration (I4-DEBT) - pending

        ## Nice to Have (U3)
        - TASK-FUNC-005-03: Advanced Features (I3-UX) - pending
        """

        lines = ["# Sprint Focus (Urgency ≥ 3)", ""]
        lines.append("Tasks sorted by urgency level (U5 → U3):")
        lines.append("")

        # Filter active tasks with U3+
        sprint_tasks = [t for t in tasks
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
```

### 6.6 Mode 6: Full Report (`--full`)

**Purpose**: Complete report combining all sections
**Output Format**: All modes concatenated with separators

```python
class FullReportGenerator:
    """Generates complete report with all sections."""

    def __init__(self, requirements: List[RequirementData], tasks: List[TaskData]):
        self.requirements = requirements
        self.tasks = tasks
        self.stats = self._calculate_statistics()

    def _calculate_statistics(self) -> Statistics:
        """Calculate all statistics."""
        # Implementation: compute stats from requirements and tasks
        pass

    def generate(self) -> str:
        """Combine all report modes."""
        sections = []

        # Title
        sections.append("# Complete Status Overview")
        sections.append("")
        sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # 1. Summary
        summary_gen = SummaryReportGenerator()
        sections.append(summary_gen.generate(self.requirements, self.tasks, self.stats))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 2. Priority
        priority_gen = PriorityReportGenerator()
        sections.append(priority_gen.generate(self.tasks))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 3. Sprint
        sprint_gen = SprintReportGenerator()
        sections.append(sprint_gen.generate(self.tasks))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 4. Blockers
        blockers_gen = BlockersReportGenerator()
        sections.append(blockers_gen.generate(self.tasks))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 5. Coverage
        coverage_gen = CoverageReportGenerator(self.requirements, self.tasks)
        sections.append(coverage_gen.generate())
        sections.append("")
        sections.append("---")
        sections.append("")

        # 6. Migration Status (if legacy files exist)
        if self.stats.legacy_requirement_count > 0 or self.stats.legacy_task_count > 0:
            sections.append("## Migration Status")
            sections.append("")
            sections.append(f"Requirements: {self.stats.requirements_with_frontmatter}/{self.stats.total_requirements} migrated")
            sections.append(f"Tasks: {self.stats.tasks_with_frontmatter}/{self.stats.total_tasks} migrated")
            sections.append("")

        return '\n'.join(sections)
```

### 6.7 Requirements Mode (`--requirements` flag)

**Purpose**: Generate reports focused on requirements instead of tasks

**Implementation**: Each report generator accepts a `focus` parameter (`'tasks'` or `'requirements'`)

#### Summary Mode with --requirements

```python
# Output example
# Status Summary - Requirements

| Category | Requirements | Implemented | In Progress | Planned | Blocked |
|----------|--------------|-------------|-------------|---------|---------|
| FUNC     | 14           | 8           | 3           | 2       | 1       |
| NFUNC    | 14           | 10          | 2           | 2       | 0       |
| PROC     | 9            | 7           | 1           | 1       | 0       |
| **Total**| **37**       | **25**      | **6**       | **5**   | **1**   |
```

**Changes from task mode**:
- Columns: Requirements | Implemented | In Progress | Planned | Blocked
- Status counts based on requirement status field
- No coverage column (coverage is task→requirement mapping)

#### Priority Mode with --requirements

```python
# Output example
# Priority Queue - Requirements

| Score | Req ID | Name | Status | Urgency | Impact | Tasks |
|-------|--------|------|--------|---------|--------|-------|
| 55    | REQ-FUNC-005 | Plan Evaluation View | in_progress | U5-BLOCK | I5-MVP | 3 |
| 54    | REQ-PROC-009 | Requirements Structure | implemented | U5-PROC | I4-DEBT | 8 |
```

**Changes from task mode**:
- Added "Tasks" column showing number of tasks per requirement
- Filter: Only active requirements (not implemented/cancelled)

#### Blockers Mode with --requirements

```python
# Output example
# Blockers & Critical Requirements

## Blocked Requirements
| Req ID | Name | Blocked By | Status | Created |
|--------|------|------------|--------|---------|
| REQ-FUNC-007 | Feature X | REQ-FUNC-006 | blocked | 2025-12-01 |

## Critical Requirements (U5)
| Req ID | Name | Urgency Reason | Status | Tasks |
|--------|------|----------------|--------|-------|
| REQ-PROC-009 | Requirements Structure | U5-PROC | implemented | 8 |
```

**Changes from task mode**:
- Same structure, different data source
- Added "Tasks" column showing task count per requirement

#### Sprint Mode with --requirements

```python
# Output example
# Sprint Focus - Requirements (Urgency ≥ 3)

## Must Do (U5)
- `REQ-PROC-009`: **Requirements Structure** (I5-ENAB) - *implemented* - 8 tasks

## Should Do (U4)
- `REQ-FUNC-005`: **Plan Evaluation View** (I4-UX) - *in_progress* - 3 tasks
```

**Changes from task mode**:
- Added task count after status
- Only non-implemented requirements shown

#### Full Mode with --requirements

**Composition**:
1. Summary (requirements)
2. Priority (requirements)
3. Sprint (requirements)
4. Blockers (requirements)
5. **Coverage is ALWAYS task-focused** (shows which tasks cover which requirements)
6. Migration status

**Note**: Coverage mode is ALWAYS about tasks covering requirements, regardless of --requirements flag

#### Implementation Strategy

```python
class ReportGeneratorBase:
    """Base class for report generators."""

    def __init__(self, requirements: List[RequirementData],
                 tasks: List[TaskData],
                 focus: str = 'tasks'):
        self.requirements = requirements
        self.tasks = tasks
        self.focus = focus  # 'tasks' or 'requirements'

    def generate(self) -> str:
        if self.focus == 'requirements':
            return self._generate_requirements_report()
        else:
            return self._generate_tasks_report()

    def _generate_tasks_report(self) -> str:
        """Generate task-focused report (original implementation)."""
        raise NotImplementedError

    def _generate_requirements_report(self) -> str:
        """Generate requirement-focused report (new implementation)."""
        raise NotImplementedError
```

**Coverage Mode Exception**:
- Coverage mode ALWAYS shows task→requirement mapping
- `--requirements` flag is ignored for coverage mode
- Warning printed if both `--coverage` and `--requirements` are used

---

## 7. Command-Line Interface

### 7.1 Argument Structure

```python
import argparse

def parse_arguments():
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
  python scripts/generate_status_overview.py --coverage --format json
        """
    )

    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--summary', action='store_true',
                           help='Quick stats table (tasks or requirements)')
    mode_group.add_argument('--priority', action='store_true',
                           help='Sorted by priority score (tasks or requirements)')
    mode_group.add_argument('--coverage', action='store_true',
                           help='Coverage % per requirement with gaps (task→requirement mapping)')
    mode_group.add_argument('--blockers', action='store_true',
                           help='Blocked and critical items (tasks or requirements)')
    mode_group.add_argument('--sprint', action='store_true',
                           help='Sprint focus - U3+ urgency (tasks or requirements)')
    mode_group.add_argument('--full', action='store_true',
                           help='Complete report with all sections (tasks or requirements)')

    # Output options
    parser.add_argument('--output', '-o', type=str,
                       default='requirements_tasks/STATUS.md',
                       help='Output file path (default: requirements_tasks/STATUS.md)')
    parser.add_argument('--format', '-f', choices=['md', 'json'],
                       default='md',
                       help='Output format: md (markdown) or json')

    # Report focus (tasks vs requirements)
    parser.add_argument('--requirements', '-r', action='store_true',
                       help='Generate report focused on requirements instead of tasks')

    # Filtering options
    parser.add_argument('--category', '-c', choices=['FUNC', 'NFUNC', 'PROC'],
                       help='Filter by category')
    parser.add_argument('--include-legacy', action='store_true',
                       help='Include files without YAML frontmatter')

    # Verbose mode
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Default to --full if no mode specified
    if not any([args.summary, args.priority, args.coverage,
                args.blockers, args.sprint, args.full]):
        args.full = True

    return args
```

### 7.2 Main Orchestrator

```python
def main():
    args = parse_arguments()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

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

    # Apply filters
    if args.category:
        requirements = [r for r in requirements if r.category == args.category]
        tasks = [t for t in tasks if t.parent_requirement.startswith(f"REQ-{args.category}")]

    if not args.include_legacy:
        requirements = [r for r in requirements if r.has_frontmatter]
        tasks = [t for t in tasks if t.has_frontmatter]

    # Generate report
    print("\nGenerating report...")

    if args.summary:
        generator = SummaryReportGenerator()
        stats = calculate_statistics(requirements, tasks)
        report = generator.generate(requirements, tasks, stats)
    elif args.priority:
        generator = PriorityReportGenerator()
        report = generator.generate(tasks)
    elif args.coverage:
        generator = CoverageReportGenerator(requirements, tasks)
        report = generator.generate()
    elif args.blockers:
        generator = BlockersReportGenerator()
        report = generator.generate(tasks)
    elif args.sprint:
        generator = SprintReportGenerator()
        report = generator.generate(tasks)
    else:  # --full
        generator = FullReportGenerator(requirements, tasks)
        report = generator.generate()

    # Output
    if args.format == 'json':
        # Convert to JSON (if applicable)
        print("JSON format not yet implemented for all modes")
        sys.exit(1)

    # Write to file or stdout
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')

    print(f"\nReport written to: {output_path}")
```

---

## 8. File Organization

### 8.1 Module Structure

```
scripts/generate_status_overview.py    (main entry point, ~800 lines)
├── Imports
├── Data Models (RequirementData, TaskData, Statistics)
├── YAMLParser class (reused from validate_meta.py)
├── StatusScanner class
│   ├── scan_requirements()
│   ├── scan_tasks()
│   ├── parse_requirement_frontmatter()
│   ├── parse_task_frontmatter()
│   ├── parse_legacy_requirement()
│   └── parse_legacy_task()
├── Report Generators
│   ├── SummaryReportGenerator
│   ├── PriorityReportGenerator
│   ├── CoverageReportGenerator
│   ├── BlockersReportGenerator
│   ├── SprintReportGenerator
│   └── FullReportGenerator
├── Helper Functions
│   ├── calculate_statistics()
│   └── extract_name_from_path()
├── CLI (parse_arguments)
└── main()
```

### 8.2 Code Organization Principles

1. **Top-Down Readability**: Main function at bottom, supporting code above
2. **Logical Grouping**: Related functions together with section comments
3. **Minimal Dependencies**: Standard library only (pathlib, re, argparse, json, datetime)
4. **Type Hints**: All functions have type annotations
5. **Docstrings**: All classes and complex functions documented

---

## 9. Error Handling Strategy

### 9.1 File Reading Errors

```python
def scan_requirements(self) -> List[RequirementData]:
    """Scan all requirements.md files."""
    requirements = []

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
        requirements.append(req)

    return requirements
```

### 9.2 YAML Parsing Errors

```python
def parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
    """Parse YAML frontmatter, return None if invalid."""
    try:
        # Attempt parsing
        return self._parse_yaml_content(content)
    except Exception as e:
        if self.verbose:
            print(f"  [WARN] YAML parse error: {e}")
        return None  # Fall back to legacy parsing
```

### 9.3 Invalid References

```python
# Validate covers references during scanning
for ac_id in task.covers.get('acceptance_criteria', []):
    if ac_id not in parent_requirement.trackable_items['acceptance_criteria']:
        if self.verbose:
            print(f"  [WARN] {task.task_id} references invalid AC: {ac_id}")
        # Don't crash - just skip invalid reference
```

### 9.4 Missing Required Fields

```python
def _extract_field(meta: Dict, field: str, default: Any) -> Any:
    """Extract field with fallback to default."""
    value = meta.get(field)
    if value is None or value == '':
        return default
    return value

# Usage
urgency = _extract_field(meta, 'urgency', 0)
status = _extract_field(meta, 'status', 'unknown')
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

**Test File**: `tests/test_generate_status_overview.py`

```python
def test_yaml_parser():
    """Test YAML frontmatter parsing."""
    content = """---
id: REQ-FUNC-001
urgency: 5
---
# Content
"""
    parser = YAMLParser()
    meta = parser.parse_frontmatter(content)
    assert meta['id'] == 'REQ-FUNC-001'
    assert meta['urgency'] == 5

def test_legacy_requirement_parsing():
    """Test folder-based requirement parsing."""
    path = Path("requirements_tasks/functional/epic_plan/requirements.md")
    # Mock file without frontmatter
    req = parse_legacy_requirement(path)
    assert req.category == 'FUNC'
    assert req.has_frontmatter == False

def test_priority_score_calculation():
    """Test priority score formula."""
    task = TaskData(urgency=5, impact=4, ...)
    assert task.priority_score == 54
```

### 10.2 Integration Tests

**Test Scenarios**:
1. Run script on actual `requirements_tasks/` folder
2. Verify all 6 modes produce valid markdown
3. Verify `--category` filter works
4. Verify `--include-legacy` flag works
5. Verify JSON output (when implemented)

### 10.3 Manual Testing Checklist

**Task-focused reports (default)**:
- [ ] Run `--summary` mode
- [ ] Run `--priority` mode
- [ ] Run `--coverage` mode
- [ ] Run `--blockers` mode
- [ ] Run `--sprint` mode
- [ ] Run `--full` mode

**Requirement-focused reports**:
- [ ] Run `--requirements --summary` mode
- [ ] Run `--requirements --priority` mode
- [ ] Run `--requirements --blockers` mode
- [ ] Run `--requirements --sprint` mode
- [ ] Run `--requirements --full` mode
- [ ] Verify `--requirements --coverage` shows warning (coverage is always task→requirement)

**Filters and options**:
- [ ] Test `--category FUNC` filter (tasks mode)
- [ ] Test `--requirements --category PROC` filter (requirements mode)
- [ ] Test `--output custom.md` option
- [ ] Test with legacy files (no frontmatter)
- [ ] Test `--include-legacy` flag

**Environment**:
- [ ] Test on Windows (user's environment)
- [ ] Verify temporary test files are detected
- [ ] Verify temporary test files are cleaned up after Phase 7

---

## 11. Performance Considerations

### 11.1 Expected Performance

- **File Count**: ~37 requirements + ~52 tasks = ~89 files
- **Expected Runtime**: < 2 seconds
- **Memory Usage**: Minimal (all data fits in memory)

### 11.2 Optimization Strategy

1. **Single-Pass Scanning**: Read each file once, extract all needed data
2. **Lazy Generation**: Only generate requested report mode
3. **Efficient Data Structures**: Use dictionaries for fast lookups
4. **No External Dependencies**: Avoid heavy libraries like pandas

### 11.3 Scalability

- **Up to 1000 files**: Current design should handle easily
- **Beyond 1000 files**: Consider streaming processing or database

---

## 12. Backward Compatibility Implementation Details

### 12.1 Detection Logic

```python
def _parse_requirement(self, path: Path, content: str) -> RequirementData:
    """Parse requirement with frontmatter or legacy fallback."""

    # Try frontmatter first
    meta = self.yaml_parser.parse_frontmatter(content)

    if meta and 'id' in meta:
        # Modern format with YAML frontmatter
        return self._requirement_from_frontmatter(path, meta)
    else:
        # Legacy format: use folder structure
        return self._requirement_from_legacy(path)
```

### 12.2 Legacy Files Reporting

Add section to `--full` mode:

```markdown
## Migration Status

### Requirements Migration
- **Migrated**: 30/37 (81%)
- **Remaining**: 7 files without frontmatter

Legacy files:
- requirements_tasks/functional/old_feature/requirements.md
- requirements_tasks/process/old_process/requirements.md
...

### Tasks Migration
- **Migrated**: 45/52 (87%)
- **Remaining**: 7 files without frontmatter
```

---

## 13. JSON Output Format (Future Enhancement)

### 13.1 JSON Structure

```json
{
  "generated": "2026-01-10T14:30:00",
  "mode": "full",
  "statistics": {
    "total_requirements": 37,
    "total_tasks": 52,
    "open_tasks": 13,
    "completed_tasks": 39,
    "overall_coverage": 58.5
  },
  "requirements": [
    {
      "id": "REQ-FUNC-001",
      "name": "Plan Evaluation View",
      "status": "in_progress",
      "urgency": 5,
      "impact": 5,
      "coverage_percent": 45.0
    }
  ],
  "tasks": [
    {
      "task_id": "TASK-FUNC-001-01",
      "name": "Phase 1: Domain",
      "status": "in_progress",
      "priority_score": 55
    }
  ]
}
```

**Note**: Implement JSON mode in a future iteration if needed.

---

## 14. Implementation Phases

### Phase 0: Test Environment Setup
- [ ] Create test task 1: `_test_2026-01-05_impl_test_high_priority_(completed)/`
  - [ ] Create folder structure
  - [ ] Create goal.md with YAML frontmatter (completed task)
- [ ] Create test task 2: `_test_2026-01-07_explore_test_blocked/`
  - [ ] Create folder structure
  - [ ] Create goal.md with YAML frontmatter (blocked task)
- [ ] Verify test files are valid (manual inspection)

### Phase 1: Core Infrastructure (Day 1)
- [ ] Set up script file structure
- [ ] Copy YAML parser from validate_meta.py
- [ ] Create data models (RequirementData, TaskData, Statistics)
- [ ] Implement StatusScanner with frontmatter parsing
- [ ] Test on existing requirement files with frontmatter
- [ ] Test on temporary test task files

### Phase 2: Legacy Support (Day 1)
- [ ] Implement legacy requirement parsing
- [ ] Implement legacy task parsing
- [ ] Test on files without frontmatter
- [ ] Verify backward compatibility

### Phase 3: Report Generators - Tasks Mode (Day 2)
- [ ] Implement ReportGeneratorBase with focus parameter
- [ ] Implement SummaryReportGenerator (tasks mode)
- [ ] Implement PriorityReportGenerator (tasks mode)
- [ ] Implement SprintReportGenerator (tasks mode)
- [ ] Implement BlockersReportGenerator (tasks mode)
- [ ] Test each mode individually with temporary test files

### Phase 4: Report Generators - Requirements Mode (Day 2)
- [ ] Implement SummaryReportGenerator (requirements mode)
- [ ] Implement PriorityReportGenerator (requirements mode)
- [ ] Implement SprintReportGenerator (requirements mode)
- [ ] Implement BlockersReportGenerator (requirements mode)
- [ ] Test each mode with --requirements flag

### Phase 5: Coverage & Full Reports (Day 2)
- [ ] Implement CoverageReportGenerator (always task→requirement)
- [ ] Implement FullReportGenerator (tasks mode)
- [ ] Implement FullReportGenerator (requirements mode)
- [ ] Test coverage calculation accuracy
- [ ] Test full report composition

### Phase 6: CLI & Integration (Day 3)
- [ ] Implement argument parsing with --requirements flag
- [ ] Implement main orchestrator
- [ ] Test all command-line options
- [ ] Test --requirements flag with all compatible modes
- [ ] Test on Windows
- [ ] Documentation

### Phase 7: Polish, Validation & Cleanup (Day 3)
- [ ] Add error handling
- [ ] Add verbose logging
- [ ] Performance testing
- [ ] Integration with complete-task skill
- [ ] User acceptance testing
- [ ] **Delete temporary test task files** (both _test_* folders)
- [ ] Final verification on real data only

---

## 15. Integration Points

### 15.1 complete-task Skill Integration

When a task is completed, the skill should:

```bash
# After updating task YAML frontmatter
python scripts/generate_status_overview.py --full
```

This regenerates `requirements_tasks/STATUS.md` automatically.

### 15.2 verify-quality Skill Integration

Before committing, run:

```bash
# Check if STATUS.md is up to date
python scripts/generate_status_overview.py --full --output temp_status.md
diff requirements_tasks/STATUS.md temp_status.md
```

If different, suggest running the script.

---

## 16. Risks & Mitigation

### Risk 1: YAML Parsing Inconsistencies
**Impact**: Medium
**Mitigation**: Reuse proven parser from validate_meta.py, add extensive tests

### Risk 2: Windows Path Handling
**Impact**: High (user's environment is Windows)
**Mitigation**: Use `pathlib.Path` exclusively, test on Windows before delivery

### Risk 3: Large File Performance
**Impact**: Low (only ~89 files currently)
**Mitigation**: Keep design simple, optimize if needed later

### Risk 4: Legacy Format Variations
**Impact**: Medium
**Mitigation**: Test on all existing legacy files, handle edge cases gracefully

### Risk 5: Breaking Changes to Frontmatter Schema
**Impact**: Medium
**Mitigation**: Version the script, document schema assumptions clearly

---

## 17. Success Criteria

1. **Functionality**:
   - [ ] All 6 modes produce valid markdown output
   - [ ] Backward compatibility works with legacy files
   - [ ] --category filter works correctly
   - [ ] All command-line options work as specified

2. **Quality**:
   - [ ] No crashes on malformed input
   - [ ] Graceful error messages for invalid files
   - [ ] Type hints on all functions
   - [ ] Clear docstrings

3. **Performance**:
   - [ ] Runs in < 5 seconds on current file set
   - [ ] Memory usage < 100 MB

4. **Integration**:
   - [ ] Works seamlessly with complete-task skill
   - [ ] Output format matches expectations in goal.md
   - [ ] Runs without errors on Windows

5. **Documentation**:
   - [ ] Usage examples in docstring
   - [ ] README updated with script details
   - [ ] Comments explain non-obvious logic

---

## 18. Follow-Up Tasks

After implementation:
1. Update `complete-task` skill to call this script
2. Update `verify-quality` skill to check STATUS.md freshness
3. Document script usage in `requirements_tasks/README.md`
4. Consider adding `--watch` mode for continuous monitoring (future)
5. Consider JSON output mode for programmatic use (future)

---

## 19. WHY Comments Requirements

The following sections will need WHY comments in the implementation:

### 19.1 Priority Score Calculation
```python
@property
def priority_score(self) -> int:
    """Calculate priority score from urgency and impact.

    Why: Uses formula (urgency × 10) + impact to ensure urgency dominates.
         Example: U5-I1 (score=51) > U4-I9 (score=49)
    Source: requirements.md#priority-system (SEC-07)
    """
    return (self.urgency * 10) + self.impact
```

### 19.2 Legacy Fallback Logic
```python
def _parse_requirement(self, path: Path, content: str) -> RequirementData:
    """Parse requirement with frontmatter or legacy fallback.

    Why: Backward compatibility during migration period (Tasks 2 & 3).
         Files without YAML frontmatter use folder naming conventions.
    Source: goal.md#backward-compatibility
    """
```

### 19.3 BOM Handling
```python
if content.startswith('\ufeff'):
    content = content[1:]

# Why: Windows editors sometimes add UTF-8 BOM marker.
#      Must strip to parse YAML correctly.
# Source: validate_meta.py (proven solution)
```

---

## 20. Deliverable Checklist

**Script Implementation**:
- [ ] `scripts/generate_status_overview.py` created
- [ ] All 6 modes implemented (summary, priority, coverage, blockers, sprint, full)
- [ ] All 6 modes tested in tasks mode (default)
- [ ] All compatible modes tested in requirements mode (--requirements flag)
  - [ ] Summary mode for requirements
  - [ ] Priority mode for requirements
  - [ ] Blockers mode for requirements
  - [ ] Sprint mode for requirements
  - [ ] Full mode for requirements
  - [ ] Coverage mode warning when used with --requirements
- [ ] Backward compatibility with legacy files (folder naming fallback)
- [ ] Command-line arguments working (--requirements, --category, --output, --include-legacy, --verbose)
- [ ] Error handling for edge cases

**Testing**:
- [ ] Temporary test task files created (Phase 0)
- [ ] All modes tested with temporary test files
- [ ] Integration tests passed
- [ ] Windows compatibility verified
- [ ] Temporary test files cleaned up (Phase 7)

**Quality**:
- [ ] WHY comments for non-obvious code
- [ ] Type hints on all functions
- [ ] Docstrings for all classes and complex functions
- [ ] No crashes on malformed input

**Documentation**:
- [ ] Script usage documented
- [ ] requirements_tasks/README.md updated
- [ ] Examples in help text
- [ ] Plan documented with agent ID

---

## Appendix A: Example Output Snippets

### A.1 Summary Mode Output
```markdown
# Status Summary

Generated: 2026-01-10 14:30

| Category | Requirements | Tasks | Open | Completed | Coverage |
|----------|--------------|-------|------|-----------|----------|
| FUNC     | 14           | 25    | 8    | 17        | 45%      |
| NFUNC    | 14           | 12    | 3    | 9         | 62%      |
| PROC     | 9            | 15    | 2    | 13        | 78%      |
| **Total**| **37**       | **52**| **13**| **39**   | **58%**  |
```

### A.2 Priority Mode Output
```markdown
# Priority Queue

Tasks sorted by priority score (Urgency × 10 + Impact):

| Score | Task ID | Name | Status | Urgency | Impact |
|-------|---------|------|--------|---------|--------|
| 55    | TASK-FUNC-005-01 | Plan Evaluation View | in_progress | U5-BLOCK | I5-MVP |
| 54    | TASK-PROC-009-02 | Meta Migration | pending | U5-PROC | I4-DEBT |
| 50    | TASK-PROC-009-04 | Status Script | pending | U5-PROC | I5-ENAB |
```

---

## Appendix B: File Size Estimate

**Total Lines of Code**: ~1000-1200 lines (increased due to --requirements mode)

**Breakdown**:
- Data models: ~100 lines
- YAML parser (reused): ~150 lines
- StatusScanner: ~200 lines
- ReportGeneratorBase: ~50 lines
- Report generators - tasks mode (5 × ~80): ~400 lines
- Report generators - requirements mode (5 × ~60): ~300 lines (sharing logic with base)
- Coverage generator (task→requirement only): ~120 lines
- Full report generator (both modes): ~100 lines
- CLI & main (with --requirements flag): ~120 lines
- Comments & docstrings: ~200 lines

**Similar Scripts**:
- `validate_meta.py`: 473 lines
- `coverage_report.py`: 587 lines

**Complexity**: Medium-High (dual mode support adds complexity, but shared base class keeps it manageable)

**Code Reuse**: ~40% of report generator code shared between tasks and requirements modes via base class

---

## Next Steps

1. **Review this plan** with the user (UPDATED with --requirements mode and test files)
2. **Get approval** before implementation
3. **Execute Phase 0**: Create temporary test task files
4. **Spawn implementation-engineer agent** with reference to this plan
5. **Execute phases 1-7** as outlined in section 14
6. **Delete temporary test files** in Phase 7 cleanup
7. **Log protocol** with agent ID before exiting

---

**END OF PLAN**
