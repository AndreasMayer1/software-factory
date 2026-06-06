# Plan: generate_status_overview.py — Release Awareness Extension

**Task**: TASK-PROC-034-04
**Date**: 2026-03-04
**Covers**: REQ-PROC-034 SEC-05, SEC-06
**Author**: architecture-advisor agent

---

## 1. Scope of Work

### Files to Modify

1. **`scripts/generate_status_overview.py`** — the only file to change (all logic lives here)

### New Classes to Add (within the same file)

- `ReleaseSummaryReportGenerator` — new report mode class
- `ReleaseConflictDetector` — utility class for SEC-06 conflict detection

### No Other Files Modified

- `requirements_tasks/RELEASES.md` — read-only input
- `scripts/validate_meta.py` — separate task (TASK-PROC-034-03), out of scope
- `.claude/` skills — separate tasks (TASK-PROC-034-05, -06), out of scope

---

## 2. Architecture Strategy

### Principle: Minimal Disruption, Additive Only

The existing code is well-structured. All changes are purely additive:

- Data model fields are added as `Optional[str] = None` (zero breakage to callers)
- New CLI arguments are added alongside existing ones (no mutual exclusivity conflicts)
- New report class follows the exact same pattern as `SummaryReportGenerator`, `PriorityReportGenerator`, etc.
- Existing generators receive `target_release` column via small, isolated additions
- Conflict detection is a self-contained utility class called from `FullReportGenerator` and `ReleaseSummaryReportGenerator`

### Pattern Consistency

All existing report generators follow one of two patterns:

1. **`ReportGeneratorBase` subclass**: `_generate_tasks_report()` + `_generate_requirements_report()` — used for `Priority`, `Blockers`, `Sprint`
2. **Standalone class with `generate()` method**: Used for `Coverage`, `FullReportGenerator`, `DependencyTreeReportGenerator`

The new `ReleaseSummaryReportGenerator` will use pattern 2 (standalone) because release grouping is orthogonal to the tasks/requirements focus axis — it always shows both, grouped by release.

### Semver Comparison

Use tuple comparison on `(major, minor, patch)` parsed from the version string. This avoids a `packaging` dependency (not guaranteed to be installed) while being correct for the strictly `MAJOR.MINOR.PATCH` format used in `RELEASES.md`.

```python
def _parse_semver(version_str: str) -> Tuple[int, int, int]:
    """Parse 'MAJOR.MINOR.PATCH' into a sortable tuple."""
    parts = version_str.split('.')
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (IndexError, ValueError):
        return (0, 0, 0)  # fallback for malformed versions
```

### RELEASES.md Loading

A standalone function `load_releases(project_root: Path) -> List[Dict]` reads and parses `requirements_tasks/RELEASES.md`. It returns the `releases` list from YAML frontmatter, sorted by semver. This function is called once in `main()` and passed down to generators that need it.

```python
def load_releases(project_root: Path) -> List[Dict[str, Any]]:
    """Load and sort release definitions from RELEASES.md."""
    releases_path = project_root / "requirements_tasks" / "RELEASES.md"
    if not releases_path.exists():
        return []
    content = releases_path.read_text(encoding='utf-8')
    parser = YAMLParser()
    meta = parser.parse_frontmatter(content)
    if not meta or 'releases' not in meta:
        return []
    releases = meta.get('releases', [])
    if not isinstance(releases, list):
        return []
    # Sort by semver
    return sorted(releases, key=lambda r: _parse_semver(str(r.get('version', '0.0.0'))))
```

---

## 3. Implementation Steps (Recommended Order)

### Step 1: Data Model Changes

**Why first**: All downstream changes depend on `target_release` being present in the data models. Doing this first makes every subsequent step possible without circular dependencies.

#### 1a. `RequirementData` dataclass (line ~78)

Add after the `blocks` field:

```python
target_release: Optional[str] = None
```

#### 1b. `TaskData` dataclass (line ~110)

Add after the `has_frontmatter` field:

```python
target_release: Optional[str] = None
```

#### 1c. `_requirement_from_frontmatter()` (line ~481)

In the return statement, add:

```python
target_release=meta.get('target_release'),
```

Also parse per-trackable-item `target_release` values. These are needed to compute the "earliest" release across all trackable items for the `--release-summary` report. Store them alongside existing `ac_ids` and `sec_ids`:

```python
# Alongside ac_ids, collect per-item release info
trackable_releases = {}  # item_id -> target_release

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
```

Store `trackable_releases` in `RequirementData.trackable_items` dict under a new key:

```python
trackable_items={
    'acceptance_criteria': ac_ids,
    'sections': sec_ids,
    'releases': trackable_releases  # NEW: item_id -> release version
}
```

This is a backwards-compatible extension — existing code only reads `acceptance_criteria` and `sections` keys.

#### 1d. `_task_from_frontmatter()` (line ~595)

In the return statement, add:

```python
target_release=meta.get('target_release'),
```

#### 1e. `_task_from_legacy()` and `_requirement_from_legacy()`

No changes needed — `target_release` defaults to `None`.

---

### Step 2: Semver Utility Function

Add near the top of the file (after the `YAMLParser` class, before `StatusScanner`):

```python
def _parse_semver(version_str: str) -> Tuple[int, int, int]:
    """Parse 'MAJOR.MINOR.PATCH' into a sortable tuple.

    Why: Avoids packaging dependency; correct for our strict MAJOR.MINOR.PATCH format.
    Source: requirements_tasks/.../release_version_management/requirements.md#version-number-system
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
```

---

### Step 3: `load_releases()` Function

Add after `_parse_semver()`:

```python
def load_releases(project_root: Path) -> List[Dict[str, Any]]:
    """Load release definitions from requirements_tasks/RELEASES.md.

    Why: RELEASES.md is the single source of truth (REQ-PROC-034 SEC-01).
         Loading it in the script ensures release names/descriptions match the definition doc.
    Source: requirements_tasks/.../release_version_management/requirements.md#sec-01
    """
    releases_path = project_root / "requirements_tasks" / "RELEASES.md"
    if not releases_path.exists():
        return []
    try:
        content = releases_path.read_text(encoding='utf-8')
    except Exception:
        return []
    parser = YAMLParser()
    meta = parser.parse_frontmatter(content)
    if not meta or not isinstance(meta.get('releases'), list):
        return []
    releases = [r for r in meta['releases'] if isinstance(r, dict) and r.get('version')]
    return sorted(releases, key=lambda r: _parse_semver(str(r.get('version', '0.0.0'))))
```

---

### Step 4: `--release VERSION` Filter (CLI + `main()`)

#### 4a. Argument parser addition (`parse_arguments()`, line ~2006)

Add to the filtering options group (after `--category`):

```python
parser.add_argument('--release', type=str, metavar='VERSION',
                   help='Filter output to items assigned to a specific release version (e.g. 0.1.0)')
```

No mutual exclusivity needed — `--release` is a filter, not a mode.

#### 4b. Apply filter in `main()` (after the `--category` filter block, line ~2120)

```python
if args.release:
    requirements = [r for r in requirements
                    if r.target_release == args.release]
    tasks = [t for t in tasks
             if t.target_release == args.release]
    print(f"  Filtered to release {args.release}: "
          f"{len(requirements)} requirements, {len(tasks)} tasks")
```

This intentionally excludes items with `target_release=None` when a release filter is active, per REQ-PROC-034 SEC-05.

---

### Step 5: `--release-summary` Mode (CLI + new generator class)

#### 5a. Argument parser addition

Add to the `mode_group` mutually exclusive group (after `--critical-path`):

```python
mode_group.add_argument('--release-summary', action='store_true',
                       help='Release-grouped overview: counts and progress per release version')
```

Update the "default to --full" guard:

```python
if not any([args.summary, args.priority, args.coverage,
            args.blockers, args.sprint, args.full,
            args.dependencies, args.dep_graph, args.critical_path,
            args.release_summary]):  # ADD THIS
    args.full = True
```

#### 5b. `ReleaseSummaryReportGenerator` class

Add between `CoverageReportGenerator` and `FullReportGenerator`:

```python
class ReleaseSummaryReportGenerator:
    """Generates release-grouped overview (SEC-05).

    Why: Groups items by release to answer "what's in release X?" and
         "how much progress has been made on each release?"
         One-stop view for release planning decisions.
    Source: requirements_tasks/.../release_version_management/requirements.md#sec-05
    """

    def __init__(self, requirements: List[RequirementData],
                 tasks: List[TaskData],
                 releases: List[Dict[str, Any]]):
        self.requirements = requirements
        self.tasks = tasks
        self.releases = releases  # Sorted by semver, from load_releases()

    def generate(self) -> str:
        lines = ["# Release Overview", ""]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

        # Build lookup: version -> list of requirements/tasks
        known_versions = {str(r.get('version', '')): r for r in self.releases}

        # Collect all versions present in requirements/tasks (may not be in RELEASES.md yet)
        data_versions = set()
        for req in self.requirements:
            if req.target_release:
                data_versions.add(req.target_release)
        for task in self.tasks:
            if task.target_release:
                data_versions.add(task.target_release)

        # Merge and sort: known releases first (in semver order), then any unknown
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

            # Per-category breakdown
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

        # Unassigned section
        unassigned_reqs = [r for r in self.requirements if not r.target_release]
        unassigned_tasks = [t for t in self.tasks if not t.target_release]

        lines.append("### Unassigned (no target_release)")
        lines.append("")
        lines.append("| Category | Requirements | Tasks |")
        lines.append("|----------|-------------|-------|")

        for cat in ['FUNC', 'NFUNC', 'PROC']:
            cat_reqs = sum(1 for r in unassigned_reqs if r.category == cat)
            cat_tasks = sum(1 for t in unassigned_tasks
                            if t.parent_requirement.startswith(f'REQ-{cat}'))
            lines.append(f"| {cat} | {cat_reqs} | {cat_tasks} |")

        lines.append(
            f"| **Total** | **{len(unassigned_reqs)}** | **{len(unassigned_tasks)}** |"
        )
        lines.append("")

        return '\n'.join(lines)
```

---

### Step 6: Release-Dependency Conflict Detection (SEC-06)

#### 6a. `ReleaseConflictDetector` utility class

Add between `ReleaseSummaryReportGenerator` and `FullReportGenerator`:

```python
class ReleaseConflictDetector:
    """Detects release-dependency ordering conflicts (SEC-06).

    Why: Enforces invariant release(X) >= release(Y) for X depends_on Y.
         Items assigned to an earlier release than their dependencies would
         be logically impossible to ship (dependency isn't done yet).
    Source: requirements_tasks/.../release_version_management/requirements.md#sec-06
    """

    def __init__(self, requirements: List[RequirementData], tasks: List[TaskData]):
        self.requirements = requirements
        self.tasks = tasks
        # Build lookup maps by ID for O(1) access
        self._req_map: Dict[str, RequirementData] = {r.id: r for r in requirements}
        self._task_map: Dict[str, TaskData] = {t.task_id: t for t in tasks}

    def find_conflicts(self) -> List[Dict[str, str]]:
        """Return list of conflict dicts with keys: item, release, dep, dep_release, message."""
        conflicts = []

        # Check tasks
        for task in self.tasks:
            if not task.target_release:
                continue
            for dep_id in task.depends_on + task.blocked_by:
                dep_release = self._get_release_for_id(dep_id)
                if dep_release is None:
                    continue  # Skip unassigned deps
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
            for dep_id in req.depends_on:
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
        """Look up target_release for a task or requirement ID."""
        if item_id in self._task_map:
            return self._task_map[item_id].target_release
        if item_id in self._req_map:
            return self._req_map[item_id].target_release
        return None

    def format_conflicts_section(self, conflicts: List[Dict[str, str]]) -> List[str]:
        """Format conflicts as markdown section lines."""
        if not conflicts:
            return []

        lines = ["## ⚠ Release-Dependency Conflicts", ""]
        lines.append("| Item | Release | Depends On | Dep Release | Conflict |")
        lines.append("|------|---------|------------|-------------|----------|")

        for c in conflicts:
            lines.append(
                f"| {c['item']} | {c['release']} | {c['dep']} | "
                f"{c['dep_release']} | {c['message']} |"
            )

        lines.append("")
        return lines
```

---

### Step 7: Integrate `target_release` Column into Existing Generators

#### 7a. `PriorityReportGenerator._generate_tasks_report()` (line ~1109)

Add `Target Release` column to the table header and rows:

```python
# Header change:
lines.append("| Score | Task ID | Name | Status | Urgency | Impact | Release |")
lines.append("|-------|---------|------|--------|---------|--------|---------|")

# Row change:
release = task.target_release or '—'
lines.append(
    f"| {task.priority_score} | {task.task_id} | {name} | "
    f"{task.status} | {task.urgency_reason} | {task.impact_reason} | {release} |"
)
```

#### 7b. `PriorityReportGenerator._generate_requirements_report()` (line ~1136)

Same pattern — add `Release` column:

```python
# Header change:
lines.append("| Score | Req ID | Name | Status | Urgency | Impact | Tasks | Release |")
lines.append("|-------|--------|------|--------|---------|--------|-------|---------|")

# Row change:
release = req.target_release or '—'
lines.append(
    f"| {req.priority_score} | {req.id} | {name} | "
    f"{req.status} | {req.urgency_reason} | {req.impact_reason} | {task_count} | {release} |"
)
```

#### 7c. `BlockersReportGenerator._generate_tasks_report()` (line ~1172)

The blockers generator already shows `Blocked By`. We add a call to `ReleaseConflictDetector` and append the conflicts section after the Critical Tasks section. This requires passing `requirements` to the generator — which it already has via `self.requirements`.

```python
# At the end of _generate_tasks_report(), before return:
detector = ReleaseConflictDetector(self.requirements, self.tasks)
conflicts = detector.find_conflicts()
conflict_lines = detector.format_conflicts_section(conflicts)
if conflict_lines:
    lines.append("---")
    lines.append("")
    lines.extend(conflict_lines)
```

---

### Step 8: Integrate New Sections into `FullReportGenerator`

#### 8a. Pass `releases` to `FullReportGenerator`

`FullReportGenerator.__init__()` currently takes `requirements`, `tasks`, `focus`. Add `releases`:

```python
def __init__(self, requirements, tasks, focus='tasks', releases=None):
    ...
    self.releases = releases or []
```

#### 8b. Add sections in `FullReportGenerator.generate()`

After section 5 (Coverage), before section 6 (Tasks Needing Metadata), add:

```python
# 5b. Release Conflict Warnings
conflict_detector = ReleaseConflictDetector(self.requirements, self.tasks)
conflicts = conflict_detector.find_conflicts()
if conflicts:
    sections.extend(conflict_detector.format_conflicts_section(conflicts))
    sections.append("---")
    sections.append("")

# 5c. Release Summary (if releases loaded)
if self.releases:
    release_gen = ReleaseSummaryReportGenerator(
        self.requirements, self.tasks, self.releases
    )
    sections.append(release_gen.generate())
    sections.append("---")
    sections.append("")
```

---

### Step 9: Wire Everything in `main()`

#### 9a. Load releases after scanning

```python
# After scanning tasks:
releases = load_releases(project_root)
if releases:
    print(f"  Found {len(releases)} releases in RELEASES.md")
else:
    print("  No RELEASES.md found — release features disabled")
```

#### 9b. Add `--release` filter (already specified in Step 4b)

#### 9c. Add `--release-summary` dispatch

```python
elif args.release_summary:
    generator = ReleaseSummaryReportGenerator(requirements, tasks, releases)
    report = generator.generate()
```

#### 9d. Pass `releases` to `FullReportGenerator`

```python
else:  # --full
    generator = FullReportGenerator(requirements, tasks, focus, releases=releases)
    report = generator.generate()
```

#### 9e. Update docstring at top of file

Add new entries to the `Usage:` and `Modes:` sections:

```
    python scripts/generate_status_overview.py --release-summary
    python scripts/generate_status_overview.py --release 0.1.0 --priority

Modes:
    --release-summary  Release-grouped overview: counts and progress per release

Options:
    --release VERSION  Filter output to items assigned to a specific release
```

---

## 4. WHY Comments Required

The following locations require WHY comments per coding standards:

| Location | Code | Reason |
|----------|------|--------|
| `_parse_semver()` | Tuple comparison instead of `packaging.version` | Non-obvious why stdlib is preferred over a standard semver library |
| `load_releases()` | Reads from conventional path rather than passing as arg | Explains the "convention over configuration" decision |
| `ReleaseConflictDetector._get_release_for_id()` | Checks both `_task_map` and `_req_map` | Non-obvious that dependencies can point to either tasks or requirements |
| `ReleaseSummaryReportGenerator.generate()` | The `known_versions` + `unknown_versions` merge logic | Non-obvious why we need two sets merged; explains graceful handling of versions in data but missing from RELEASES.md |
| `BlockersReportGenerator` conflict injection | `ReleaseConflictDetector` called inside the blockers generator | Non-obvious coupling between conflict detection and blockers report |
| `_requirement_from_frontmatter()` `trackable_releases` | Stores per-item releases in `trackable_items['releases']` | Non-obvious that `trackable_items` dict is being extended with a new key |

---

## 5. Testing Strategy

This is a Python script, not Flutter code. Testing is done by:

1. **Manual smoke tests** (run script with new flags, verify output format):
   ```
   python scripts/generate_status_overview.py --release-summary
   python scripts/generate_status_overview.py --release 0.1.0 --summary
   python scripts/generate_status_overview.py --priority
   python scripts/generate_status_overview.py --full
   ```

2. **Edge case manual testing**:
   - Run `--release-summary` with no items assigned to any release (should show only "Unassigned" section)
   - Run `--release 0.0.1` where no items match (should produce empty tables gracefully)
   - Artificially create a conflict (manually set `target_release` to an earlier release than a dependency) and verify the conflict section appears in `--full` and `--release-summary`

3. **No existing tests to break**: The script has no automated test suite. The implementation must not break any of the existing modes (`--summary`, `--priority`, `--coverage`, `--blockers`, `--sprint`, `--dependencies`, `--critical-path`, `--dep-graph`).

4. **Backward compatibility check**: Run `python scripts/generate_status_overview.py --full` on the current codebase (before any items have `target_release` assigned) — should produce identical output to the current version, except for the new empty "Release Summary" section (or it should be omitted when empty).

---

## 6. Implementation Order Summary

```
Step 1: Data model (RequirementData, TaskData)  — foundation
Step 2: _parse_semver() utility function         — needed by steps 3, 5, 6
Step 3: load_releases() function                 — needed by steps 5, 8, 9
Step 4: --release filter (CLI + main())          — isolated, safe
Step 5: ReleaseSummaryReportGenerator            — new class, no conflicts
Step 6: ReleaseConflictDetector                  — new class, no conflicts
Step 7: --priority and --blockers integration    — small column/section additions
Step 8: FullReportGenerator integration          — orchestrates 5+6
Step 9: Wire main()                              — final hookup
```

Each step is independently testable. Steps 1-3 can be implemented and verified (via data parsing smoke test) before any generator work begins.

---

## 7. Risk Areas

### Risk 1: RELEASES.md YAML Parsing Complexity

**Issue**: The `YAMLParser._parse_simple_yaml()` fallback parser handles simple flat and nested structures but may struggle with deeply nested `scope_boundaries.includes/excludes` lists in `RELEASES.md`.

**Mitigation**: `load_releases()` only needs `version`, `name`, `status`, `description` from each release entry. The `scope_boundaries` field is ignored. With PyYAML installed (standard in CI), this is a non-issue. The fallback parser handles our requirements structure but `RELEASES.md` is more complex — if the fallback fails, `load_releases()` returns `[]` gracefully.

**Decision**: Test explicitly with `HAS_YAML = False` to verify the fallback handles `RELEASES.md`'s format. If it doesn't, consider a direct `yaml.safe_load` call in `load_releases()` with a clear fallback message.

### Risk 2: `trackable_items['releases']` Key Collision

**Issue**: Adding a new `'releases'` key to the `trackable_items` dict could confuse code that iterates over all keys in `trackable_items`.

**Mitigation**: Scan the entire codebase for all usages of `trackable_items`. Currently `CoverageReportGenerator._build_coverage_map()` reads `acceptance_criteria` and `sections` keys by name — it never iterates over all keys. The `calculate_statistics()` function does the same. No code treats `trackable_items` as a dict of lists to iterate over blindly.

**Action**: Add a comment in `_requirement_from_frontmatter()` noting the special `releases` key.

### Risk 3: `FullReportGenerator` constructor signature change

**Issue**: Adding `releases=None` to `FullReportGenerator.__init__()` changes the constructor signature. Any code calling `FullReportGenerator(requirements, tasks, focus)` without the `releases` keyword arg will still work because it defaults to `None`.

**Mitigation**: The only call site is in `main()` (line ~2167). One change required. No external callers.

### Risk 4: `--release-summary` + `--requirements` interaction

**Issue**: `ReleaseSummaryReportGenerator` always shows both requirements and tasks (it doesn't respect the `--requirements` focus flag). This is intentional — release overview is about the whole release, not just one perspective.

**Decision**: Add a note in the argparse help text: "`--release-summary` shows both requirements and tasks regardless of `--requirements` flag." Document this as intentional in the WHY comment.

### Risk 5: Empty conflict section noise

**Issue**: If no items have `target_release` set (current state — no items assigned yet), the conflict detector finds zero conflicts. The `--full` report should not show an empty conflict section.

**Mitigation**: `format_conflicts_section()` returns `[]` when there are no conflicts. The `FullReportGenerator` checks `if conflicts:` before appending the section. No empty section noise.

---

## 8. Dependency Analysis

- **TASK-PROC-034-02** (create RELEASES.md) — marked completed in commit `3585606`. RELEASES.md exists at `requirements_tasks/RELEASES.md`. This task can proceed.
- **TASK-PROC-034-03** (update validate_meta.py) — parallel, no dependency either direction.
- **TASK-PROC-034-05, -06** (skill updates) — after this task; skills will read `target_release` fields that this script now parses.

---

## 9. Complete Change Summary Table

| Location | Line(s) | Type | Description |
|----------|---------|------|-------------|
| `RequirementData` | ~78 | Add field | `target_release: Optional[str] = None` |
| `TaskData` | ~110 | Add field | `target_release: Optional[str] = None` |
| `_requirement_from_frontmatter()` | ~527 | Extend | Parse `target_release` + per-item releases |
| `_task_from_frontmatter()` | ~619 | Extend | Parse `target_release` |
| After `YAMLParser` class | ~387 | Add function | `_parse_semver()` |
| After `_parse_semver()` | ~395 | Add function | `load_releases()` |
| `parse_arguments()` | ~2065 | Extend | Add `--release VERSION` filter option |
| `parse_arguments()` mode group | ~2047 | Extend | Add `--release-summary` mode |
| Before `FullReportGenerator` | ~1485 | Add class | `ReleaseSummaryReportGenerator` |
| Before `FullReportGenerator` | ~1487 | Add class | `ReleaseConflictDetector` |
| `PriorityReportGenerator` | ~1122 | Extend | Add `Release` column to both tables |
| `BlockersReportGenerator` | ~1210 | Extend | Append conflict section if conflicts exist |
| `FullReportGenerator.__init__()` | ~1492 | Extend | Add `releases=None` parameter |
| `FullReportGenerator.generate()` | ~1545 | Extend | Add conflict + release summary sections |
| `main()` | ~2110 | Extend | Load releases; apply `--release` filter; dispatch `--release-summary` |
| Module docstring | lines 1-38 | Update | Document new modes and options |
