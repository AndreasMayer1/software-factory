# Plan: Package-Based Model Migration — Skills and Scripts

**Task**: TASK-PROC-034-11
**Date**: 2026-03-26
**Goal**: Update all skills and scripts to use `target_package` + RELEASE_BACKLOG.md instead of `target_release` + RELEASES.md versions.

---

## Split Recommendation

This task touches 12+ files and is rated XL. The goal.md itself recommends splitting. The natural split is:

**Recommendation: Split into 5 sub-tasks, implemented sequentially.**

| Sub-task | Scope | Effort | Dependency |
|----------|-------|--------|------------|
| A | Skills: requ-explore, task-create, task-create-impl | M | none |
| B | New skill: release-plan | S | none |
| C | Skills: ux-create-flow, requ-derive-from-flow | S | none |
| D | Scripts: validate_meta.py, generate_status_overview.py, next_tasks.py, generate_technical_release_notes.py | L | none |
| E | Skills: requ-prep-release, release | S | D (requ-prep-release calls generate_status_overview.py with --release flag) |

Sub-tasks A, B, C, and D are independent and can be done in any order. Sub-task E must follow D.

---

## RELEASE_BACKLOG.md Format Reference

RELEASE_BACKLOG.md does not exist yet (created by TASK-PROC-034-09). For all changes below, the implementation must assume this format:

```yaml
---
packages:
  - version: "0.0.1"
    packages:
      - id: "PKG-0.0.1-core"
        name: "Core Data Transfer"
        description: "..."
        status: planned  # planned | active | released
      - id: "PKG-0.0.1-ui"
        name: "UI Polish"
        description: "..."
        status: planned
  - version: "0.1.0"
    packages:
      - id: "PKG-0.1.0-mvp"
        name: "Beta MVP"
        description: "..."
        status: planned
---
```

Key rules derived from acceptance criteria:
1. `target_package` is valid if its value matches any `id` in RELEASE_BACKLOG.md (no backref requirement)
2. The first-listed package per version is the fallback for cross-cutting requirements not covered by any scoped package
3. Skills present the flat list of all package IDs+names to the user when prompting

---

## Sub-task A: Skills — requ-explore, task-create, task-create-impl

### A1. requ-explore/skill.md — Section 2.4

**Current text** (section header + key lines):
```
### 2.4 Release Assignment
**Process**:
1. **Read RELEASES.md**: Parse `releases` list from `requirements_tasks/RELEASES.md` YAML frontmatter...
2. **For each trackable item**...
   - Ask: "Which release should this item target? (or 'unassigned/skip')"
   - Add `target_release: "X.Y.Z"` to that item in YAML
3. **Compute top-level `target_release`**: Set requirement's top-level `target_release`...
**YAML structure**: (shows target_release fields)
**Skip Conditions**:
- `RELEASES.md` not found → warn user and skip release assignment
**Behavior Reference** (from REQ-PROC-034 SEC-04): (shows RELEASES.md lookups)
```

**New text — replace section 2.4 entirely**:

```markdown
### 2.4 Package Assignment

**When**: After requirement document is drafted (Phase 2.3), before quality check.

**Purpose**: Assign each trackable item (acceptance criterion or section) to a target package, then compute top-level `target_package` as the package of the earliest-versioned item.

**Process**:

1. **Read RELEASE_BACKLOG.md**: Parse `packages` from `RELEASE_BACKLOG.md` YAML frontmatter. Build a flat list of all package entries: `(id, name, version)`.

2. **For each trackable item** (AC or section) in the new requirement:
   - If requirement is **new** OR item has no existing `target_package`:
     - Present user with the flat package list grouped by version:
       ```
       Available packages:
       v0.0.1:
         PKG-0.0.1-core  — Core Data Transfer
         PKG-0.0.1-ui    — UI Polish
       v0.1.0:
         PKG-0.1.0-mvp   — Beta MVP
       ```
     - Ask: "Which package should this item target? (or 'unassigned/skip')"
     - Add `target_package: "PKG-x.y.z-name"` to that item in YAML
   - If requirement is **existing** AND item already has `target_package`:
     - Preserve existing value; do not prompt again

3. **Compute top-level `target_package`**: Set requirement's top-level `target_package` to the package whose version is earliest (using semver ordering of the associated version) among all assigned items. If a tie exists (multiple items in the same version), use the one that appears first in RELEASE_BACKLOG.md. If no items assigned, omit top-level field.

   Note: The first-listed package per version in RELEASE_BACKLOG.md serves as the fallback `target_package` for cross-cutting requirements that do not fit any scoped package — assign these to the first-listed package of the relevant version.

**YAML structure**:
```yaml
target_package: "PKG-0.0.1-core"   # top-level: package with earliest version (computed)
trackable_items:
  acceptance_criteria:
    - id: AC-01
      target_package: "PKG-0.0.1-core"  # assigned
    - id: AC-02
      target_package: "PKG-0.1.0-mvp"
    - id: AC-03
                                         # absent = not yet assigned
  sections:
    - id: SEC-01
      target_package: "PKG-0.1.0-mvp"
```

**Skip Conditions**:
- Requirement is purely internal process tooling AND user indicates "unassigned" → skip without error
- `RELEASE_BACKLOG.md` not found → warn user and skip package assignment

**Behavior Reference** (from REQ-PROC-034 SEC-04):
| Situation | Action |
|-----------|--------|
| New requirement with trackable items | Ask per item |
| Existing requirement, item already has package | Preserve; do not ask |
| Existing requirement, item has no package | Ask |
| RELEASE_BACKLOG.md not found | Warn user; skip |
```

**Also update section 2.5 Quality Check** — replace this checklist item:
- OLD: `- [ ] Release assignment complete: all trackable items have `target_release` or explicitly unassigned`
- NEW: `- [ ] Package assignment complete: all trackable items have `target_package` or explicitly unassigned`

---

### A2. task-create/skill.md — Section "Release Version Inheritance"

**Current section** (lines ~346–375 in skill.md):
```
### Release Version Inheritance (target_release field)
...reads RELEASES.md, inherits target_release, prompts if missing...
```

**Replace entirely with**:

```markdown
### Package Inheritance (target_package field)

**MANDATORY**: After `covers` field is populated, determine `target_package` using these rules:

1. **Read parent requirement's trackable items** — extract `target_package` from each referenced AC/section
2. **All covered items assigned**: Inherit the package of the earliest-versioned item (semver comparison on the associated version). Log the inherited value to the user.
3. **Some items unassigned or `covers` is empty**: Prompt user — "Covered items have mixed/no package assignments. Which package should this task target?" Load available packages from `RELEASE_BACKLOG.md` and present options grouped by version.
4. **RELEASE_BACKLOG.md missing**: Warn and skip (do not fail task creation)
5. **Write `target_package`** to task's YAML frontmatter in goal.md, after the `covers` field:
   ```yaml
   covers:
     acceptance_criteria: [AC-01, AC-02]
     sections: []
   target_package: PKG-0.0.1-core   # omit field entirely if user skipped
   ```

**Example interaction**:
```
Inherited target_package: PKG-0.0.1-core (from AC-01, AC-02)

OR

Covered items have no package assignments.
Available packages from RELEASE_BACKLOG.md:
v0.0.1:
  PKG-0.0.1-core  — Core Data Transfer
  PKG-0.0.1-ui    — UI Polish
v0.1.0:
  PKG-0.1.0-mvp   — Beta MVP

Which package does this task target? (enter package ID or skip)
```
```

Also update **goal.md Template** — replace:
```yaml
target_release: v0.2.0   # omit field entirely if user skipped
```
with:
```yaml
target_package: PKG-0.0.1-core   # omit field entirely if user skipped
```

---

### A3. task-create-impl/skill.md — Section 3.4

**Current section** (lines ~230–244 in skill.md):
```
### 3.4 Release Version Inheritance (target_release field)
...same logic as task-create, reads RELEASES.md...
```

**Replace entirely with**:

```markdown
### 3.4 Package Inheritance (target_package field)

**MANDATORY**: After populating `covers` field in goal.md YAML, determine `target_package` using these rules:

1. **Read parent requirement's trackable items** — extract `target_package` from each referenced AC/section
2. **All covered items assigned**: Inherit the package of the earliest-versioned item (semver comparison on the associated version). Log the inherited value to the user.
3. **Some items unassigned or `covers` is empty**: Prompt user — "Covered items have mixed/no package assignments. Which package should this task target?" Load available packages from `RELEASE_BACKLOG.md` and present options grouped by version.
4. **RELEASE_BACKLOG.md missing**: Warn and skip (do not fail task creation)
5. **Write `target_package`** to task's YAML frontmatter in goal.md, after the `covers` field:
   ```yaml
   covers:
     acceptance_criteria: [AC-01, AC-02]
     sections: []
   target_package: PKG-0.0.1-core   # omit field entirely if user skipped
   ```
```

Also update the **goal.md Template** in Phase 3 — replace `target_release` reference with `target_package`.

---

## Sub-task B: New Skill — release-plan

**File**: `.claude/skills/release-plan/skill.md` (new file)

**INDEX.md entry** to add under `### release (Release Execution)`:
```
| **release-plan** | Assign packages to versions in RELEASE_BACKLOG.md |
```

**Quick reference table** entry:
```
| Plan a release (assign packages to versions) | `release-plan` | `/release-plan` |
```

### Full Workflow

```markdown
---
name: release-plan
description: Assign packages to versions in RELEASE_BACKLOG.md; update status and version assignments
tools: Read, Write, Bash
model: inherit
---

You manage the release backlog: assign packages to versions and update their statuses.

## Step 1 — Read Current Backlog

Read `RELEASE_BACKLOG.md`. Display the current state:

```
Current RELEASE_BACKLOG.md:

v0.0.1 (2 packages):
  [active]  PKG-0.0.1-core — Core Data Transfer
  [planned] PKG-0.0.1-ui   — UI Polish

v0.1.0 (1 package):
  [planned] PKG-0.1.0-mvp  — Beta MVP

Unassigned packages (id set, no version): none
```

## Step 2 — Determine Action

Ask user what they want to do:

```
What would you like to do?
  1. Assign a new package to a version
  2. Move a package to a different version
  3. Change a package's status (planned → active → released)
  4. Add a new package entry
  5. Done
```

## Step 3 — Execute Action

### Action 1: Assign new package to version
- Ask: "Package ID? (e.g. PKG-0.0.2-feature)"
- Ask: "Package name?"
- Ask: "Which version? (existing or new)"
- Ask: "Initial status? (planned/active)"
- Add entry to the correct version block in RELEASE_BACKLOG.md

### Action 2: Move package to different version
- Show current assignment
- Ask: "Move to which version?"
- Update the package entry's version grouping in RELEASE_BACKLOG.md

### Action 3: Change package status
- Show current packages with statuses
- Ask: "Which package? Which new status? (planned/active/released)"
- Constraint: Only one package may have `status: active` at a time (warn if another is already active)
- Update status in RELEASE_BACKLOG.md

### Action 4: Add new package entry
- Ask for: id, name, description, version, status
- ID format convention: `PKG-[VERSION]-[short-name]` (e.g. `PKG-0.2.0-analytics`)
- Add to RELEASE_BACKLOG.md in the correct version block
- Note: The first-listed package per version is the fallback for cross-cutting requirements

### Action 5: Done
- Proceed to Step 4

After each action (except Done), return to Step 2 to allow chaining.

## Step 4 — Write and Commit

Write the updated RELEASE_BACKLOG.md.

Use the `claude-commit` skill to commit:
```
chore(backlog): update RELEASE_BACKLOG.md — [brief summary of changes]
```

## Key Principle

The first-listed package per version in RELEASE_BACKLOG.md serves as the fallback `target_package`
for requirements that do not fit any scoped package. Keep this in mind when ordering packages.
```

---

## Sub-task C: Skills — ux-create-flow and requ-derive-from-flow

### C1. ux-create-flow/skill.md

**Step 2 — Gather Additional Metadata**: Add a new question for Release Scope:

After the existing questions (evidence level, implementation status), add:

```markdown
**Release Scope** (optional — skip if unknown):
- Ask: "Which package(s) in RELEASE_BACKLOG.md does this flow target?"
- Read `RELEASE_BACKLOG.md` and present the flat list of package IDs + names grouped by version
- User may select one or more package IDs, or skip
- Store selection as `target_packages: [PKG-x.y.z-name, ...]` in flow.md YAML frontmatter (omit field if skipped)
```

**Step 6 — Template**: Ensure `target_packages` is included in the flow.md YAML template when creating a new flow (omit if not selected in Step 2).

**Step 10 — Validate checklist**: Add item:
```
- [ ] If target_packages was set: each package ID exists in RELEASE_BACKLOG.md
```

**Step 12 — Output, New mode**: Add note after "Next steps":
```
Package scope: [PKG-IDs if set, or "not assigned — run /release-plan to assign packages"]
Note: If this flow targets a specific package, the package helps link flow → requirement → task automatically.
```

---

### C2. requ-derive-from-flow/skill.md

**Phase 1.1 — Read the primary flow**: Add to the extraction list:

```
**F. Release Scope** (if `target_packages` YAML field present):
Package IDs from the flow that inform which package the derived requirements should target.
```

**Phase 2 — Build Requirements Matrix**: Update the Opus instruction to include a "Suggested Package" column in the matrix format:

In the matrix table header, add column:
```
| # | Source in Flow | Gap Description | Existing Req | Status | Foundations | Cross-Flow | Suggested Package | Suggested Action / Target |
```

The Suggested Package column should contain the package ID from the flow's `target_packages` (if a single package is set) or "see flow" (if multiple). Leave blank if flow has no `target_packages`.

**Phase 4.2 — Write goal.md**: Add to the goal.md template YAML frontmatter:

```yaml
suggested_package: "PKG-x.y.z-name"  # from flow's target_packages; omit if flow has none
```

And add to the goal.md body under `## References`:
```
- Suggested package: `PKG-x.y.z-name` (from flow's target_packages field)
```

---

## Sub-task D: Scripts

### D1. validate_meta.py — Four changes

#### Change 1: Add `_load_packages()` method alongside `_load_releases()`

New method:
```python
def _load_packages(self):
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
```

Also add `self.known_packages: Set[str] = set()` to `__init__` and call `self._load_packages()` in `__init__`.

#### Change 2: Add `_validate_target_package()` method

```python
def _validate_target_package(self, file_path: str, target_package: Any) -> bool:
    """Validate target_package field. Returns True if valid."""
    if not target_package or target_package == '':
        return True  # Optional field

    if not isinstance(target_package, str):
        self.add_error(file_path, f"target_package must be a string, got {type(target_package).__name__}")
        return False

    # Check if package ID exists in RELEASE_BACKLOG.md (if loaded)
    if self.known_packages and target_package not in self.known_packages:
        self.add_error(file_path, f"target_package '{target_package}' not found in RELEASE_BACKLOG.md")
        return False

    return True
```

#### Change 3: Update `validate_requirements()` — accept both fields during transition

In `validate_requirements()`, after the existing `target_release` validation block:
```python
# Validate target_release if present (transition period: both fields accepted)
target_release = meta.get('target_release')
if target_release:
    self._validate_target_release(str(req_file), target_release)

# Validate target_package if present
target_package = meta.get('target_package')
if target_package:
    self._validate_target_package(str(req_file), target_package)
```

Also validate `target_package` on trackable items (AC and SEC objects), mirroring the existing `target_release` validation on those objects.

#### Change 4: Update `validate_tasks()` — same dual validation

In `validate_tasks()`:
```python
# Validate target_release if present (transition period)
target_release = meta.get('target_release')
if target_release:
    self._validate_target_release(str(goal_file), target_release)

# Validate target_package if present
target_package = meta.get('target_package')
if target_package:
    self._validate_target_package(str(goal_file), target_package)
```

Also update `TaskMeta` dataclass to add `target_package: Optional[str] = None` field.

---

### D2. generate_status_overview.py — Five changes

#### Change 1: Add `target_package` to `RequirementData` and `TaskData` dataclasses

```python
target_package: Optional[str] = None
```
(alongside existing `target_release: Optional[str] = None`)

#### Change 2: Update data loading to extract `target_package`

In `load_requirements()` (around line 639):
```python
target_package=meta.get('target_package'),
```

In `load_tasks()` (around line 730):
```python
target_package=meta.get('target_package'),
```

#### Change 3: Add `--package` flag to argument parser

```python
parser.add_argument('--package', type=str, metavar='PKG_ID',
                   help='Filter output to items assigned to a specific package ID (e.g. PKG-0.0.1-core)')
```

Add corresponding filter in main() after the existing `--release` filter:
```python
if args.package:
    requirements = [r for r in requirements if r.target_package == args.package]
    tasks = [t for t in tasks if t.target_package == args.package]
    print(f"  Filtered to package {args.package}: "
          f"{len(requirements)} requirements, {len(tasks)} tasks")
```

#### Change 4: Add `--package-summary` mode (new `PackageSummaryReportGenerator` class)

New class modeled after `ReleaseSummaryReportGenerator` but grouping by package ID:

```python
class PackageSummaryReportGenerator:
    """Generates package-grouped overview.

    Groups requirements and tasks by target_package.
    Reads RELEASE_BACKLOG.md for package metadata (name, version, status).
    """

    def __init__(self, requirements, tasks, backlog_packages):
        # backlog_packages: list of dicts with id, name, version, status
        ...

    def generate(self) -> str:
        # For each known package ID (sorted by version then position):
        #   Show: package ID, name, version, status
        #   Requirements count by status
        #   Tasks count by status
        #   Progress bar (completed / total tasks)
        # Then: Unassigned section (items with no target_package)
        # Then: Dependency conflicts (same logic as release summary)
        ...
```

Add to argument parser:
```python
mode_group.add_argument('--package-summary', action='store_true',
                       help='Package-grouped overview: counts and progress per package')
```

#### Change 5: Update `ReleaseSummaryReportGenerator` — show `target_package` column

In the `ReleaseSummaryReportGenerator.generate()` method, when listing tasks/requirements per release, also show the `target_package` value to make the transition visible. This is a display-only change — no logic change.

Also update the "Unassigned" section heading:
```python
# Show items with neither target_release nor target_package
lines.append("### Unassigned (no target_release or target_package)")
```

---

### D3. next_tasks.py — Four changes

#### Change 1: Add `target_package` to task dict in `load_tasks()`

```python
target_package = meta.get("target_package")
if target_package is not None:
    target_package = str(target_package).strip().strip("\"'") or None

tasks.append({
    ...
    "target_release": target_release,
    "target_package": target_package,  # NEW
    ...
})
```

#### Change 2: Add `find_next_package()` function

```python
def find_next_package(tasks: List[Dict], completed_ids: set, backlog_packages: List[Dict]) -> Optional[str]:
    """Lowest-versioned package that still has at least one open, non-blocked task.

    backlog_packages: list of dicts with 'id', 'version' keys, in order from RELEASE_BACKLOG.md.
    Returns the package id, not the version.
    """
    packages_with_open = set()
    for t in tasks:
        if t["status"] not in TERMINAL_STATUSES and not _is_blocked(t, completed_ids):
            if t.get("target_package"):
                packages_with_open.add(t["target_package"])

    if not packages_with_open:
        return None

    # Sort by version (semver) then by position within version (from backlog order)
    def pkg_sort_key(pkg_id: str) -> Tuple:
        for pkg in backlog_packages:
            if pkg['id'] == pkg_id:
                return (_parse_semver(str(pkg.get('version', '999.999.999'))),
                        backlog_packages.index(pkg))
        return ((999, 999, 999), 9999)

    candidates = [p for p in packages_with_open]
    return min(candidates, key=pkg_sort_key)
```

#### Change 3: Add `load_backlog_packages()` function

```python
RELEASE_BACKLOG_FILE = PROJECT_ROOT / "RELEASE_BACKLOG.md"

def load_backlog_packages() -> List[Dict]:
    """Parse RELEASE_BACKLOG.md and return flat list of packages with version info."""
    if not RELEASE_BACKLOG_FILE.exists():
        return []
    try:
        content = RELEASE_BACKLOG_FILE.read_text(encoding="utf-8")
    except Exception:
        return []
    meta = parse_frontmatter(content)
    if not meta or 'packages' not in meta:
        return []
    result = []
    for version_block in meta.get('packages', []):
        if isinstance(version_block, dict):
            version = str(version_block.get('version', ''))
            for pkg in version_block.get('packages', []):
                if isinstance(pkg, dict) and 'id' in pkg:
                    result.append({
                        'id': pkg['id'],
                        'name': pkg.get('name', ''),
                        'version': version,
                        'status': pkg.get('status', 'planned'),
                    })
    return result
```

#### Change 4: Update `main()` to support `--package` flag and dual-mode ranking

```python
parser.add_argument(
    "--package", help="Override the auto-detected next package ID"
)
```

In `main()`:
```python
backlog_packages = load_backlog_packages()
next_package = args.package if args.package else find_next_package(tasks, completed_ids, backlog_packages)

# Fall back to release-based ranking if no target_package data exists
next_release = args.release if args.release else find_next_release(tasks, completed_ids)

# Primary: use package if available, else fall back to release
if next_package:
    display_next = f"Next package: {next_package}"
    ranked = rank_tasks_by_package(tasks, next_package, completed_ids)
elif next_release:
    display_next = f"Next release: {next_release} (no package data — falling back to release)"
    ranked = rank_tasks(tasks, next_release, completed_ids)
else:
    print("No open tasks with a target_package or target_release found.")
    sys.exit(0)
```

Add `rank_tasks_by_package()` function (analogous to `rank_tasks()` but using `target_package` instead of `target_release`):

```python
def rank_tasks_by_package(
    tasks: List[Dict], next_package: Optional[str], completed_ids: set
) -> List[Dict]:
    """Return eligible tasks sorted by priority rules (package-based)."""
    reqs_active = _requirements_in_progress_by_package(tasks, next_package)

    eligible = [
        t for t in tasks
        if t["status"] not in TERMINAL_STATUSES and not _is_blocked(t, completed_ids)
    ]

    def sort_key(t: Dict):
        is_next = 0 if (next_package and t.get("target_package") == next_package) else 1
        type_rank = 0 if t["type"] == "explore" else 1
        req_not_active = 0 if t["parent_requirement"] in reqs_active else 1
        return (is_next, type_rank, req_not_active, -_priority_score(t))

    return sorted(eligible, key=sort_key)
```

Also update the release boundary warnings to check `RELEASE_BACKLOG.md` active package instead of (or in addition to) `RELEASES.md` active release.

---

### D4. generate_technical_release_notes.py — Three changes

#### Change 1: Add `find_active_package()` function

```python
RELEASE_BACKLOG_MD = PROJECT_ROOT / "RELEASE_BACKLOG.md"

def find_active_package() -> Optional[str]:
    """Read RELEASE_BACKLOG.md and return the package id with status: active."""
    if not RELEASE_BACKLOG_MD.exists():
        return None
    try:
        content = RELEASE_BACKLOG_MD.read_text(encoding="utf-8")
    except Exception:
        return None

    fm = parse_frontmatter(content)
    if fm and isinstance(fm.get("packages"), list):
        for version_block in fm["packages"]:
            if isinstance(version_block, dict):
                for pkg in version_block.get("packages", []):
                    if isinstance(pkg, dict) and str(pkg.get("status", "")).strip() == "active":
                        return str(pkg.get("id", "")).strip()
    return None
```

#### Change 2: Update `load_release_tasks()` to accept both `target_release` and `target_package`

Rename to `load_release_tasks(version_or_package: str, by_package: bool = False)`:

```python
def load_release_tasks(version_or_package: str, by_package: bool = False) -> Dict[str, List[Dict]]:
    """Scan functional/ and non-functional/ for completed tasks matching version or package.

    by_package=True: match tasks where target_package == version_or_package
    by_package=False: match tasks where target_release == version_or_package (legacy)
    Tasks with target_package set take precedence over target_release.
    """
    ...
    for goal_file in scan_root.rglob("goal.md"):
        ...
        if by_package:
            # Match by target_package
            task_target_pkg = meta.get("target_package")
            if task_target_pkg:
                task_target_pkg = str(task_target_pkg).strip().strip("\"'")
            if task_target_pkg != version_or_package:
                continue
        else:
            # Match by target_release (transition period fallback)
            target_release = meta.get("target_release")
            # Also check target_package if no target_release
            if not target_release:
                target_package = meta.get("target_package")
                if target_package:
                    continue  # Has package, not release — skip in release mode
            if target_release is not None:
                target_release = str(target_release).strip().strip("\"'")
            if target_release != version_or_package:
                continue
```

#### Change 3: Update `main()` to support `--package` flag

```python
parser.add_argument(
    "--package",
    help="Target package ID (default: read active package from RELEASE_BACKLOG.md)",
)
```

In `main()`:
```python
if args.package:
    package_id = args.package.strip()
    tasks = load_release_tasks(package_id, by_package=True)
    version_label = package_id
    by_package = True
elif args.release:
    version_label = args.release.strip()
    tasks = load_release_tasks(version_label, by_package=False)
    by_package = False
else:
    # Try package first, fall back to release
    package_id = find_active_package()
    if package_id:
        version_label = package_id
        tasks = load_release_tasks(package_id, by_package=True)
        by_package = True
    else:
        version_label = find_active_release()
        if not version_label:
            print("ERROR: No active package or release found.", file=sys.stderr)
            sys.exit(1)
        tasks = load_release_tasks(version_label, by_package=False)
        by_package = False
```

Output file path: when using package ID, write to `releases/[version_from_backlog]/release_notes_technical.md` by looking up the version for the package in RELEASE_BACKLOG.md, or fall back to `releases/[package_id]/release_notes_technical.md`.

---

## Sub-task E: Skills — requ-prep-release and release

### E1. requ-prep-release/skill.md

#### Phase 0 — Bootstrap changes

**Current**:
```
1. Run `python scripts/generate_status_overview.py --release [release_version] --output ...`
2. Read `requirements_tasks/RELEASES.md` — extract `scope_boundaries.includes`
3. Read STATUS_NEXT_RELEASE.md — extract all requirements with `target_release: [version]`
```

**New**:
```
1. Ask user: "Are you preparing by package ID or by release version?"
   - By package: ask for package ID (e.g. PKG-0.0.1-core)
   - By release: ask for release version (legacy mode, e.g. 0.0.1)

2. **If by package**:
   Run `python scripts/generate_status_overview.py --package [pkg_id] --output requirements_tasks/STATUS_NEXT_RELEASE.md`
   Read `RELEASE_BACKLOG.md` — extract the package's `name`, `description`, and associated version's scope

3. **If by release** (legacy):
   Run `python scripts/generate_status_overview.py --release [release_version] --output requirements_tasks/STATUS_NEXT_RELEASE.md`
   Read `requirements_tasks/RELEASES.md` — extract `scope_boundaries.includes` for the target release
```

Subsequent phases use the status file identically — no further changes needed in Phases 1–5.

#### Phase 6 — Activate: update for package model

**Current**:
```
3. update `status: planned` → `status: active` for the target release in RELEASES.md
```

**New**:
```
3. If operating by package:
   - Read `RELEASE_BACKLOG.md`
   - Warn if another package already has `status: active`
   - Update `status: planned` → `status: active` for the target package in RELEASE_BACKLOG.md
   - Confirm: "Package [pkg_id] is now active in RELEASE_BACKLOG.md."

   If operating by release (legacy):
   - Existing behavior: update RELEASES.md
```

---

### E2. release/skill.md

#### Step 4.1 — Read active release: update to check both files

**Current**:
```
Read `requirements_tasks/RELEASES.md`. Find the entry with `status: active`.
```

**New**:
```
Read `RELEASE_BACKLOG.md`. Find the package with `status: active`. Extract:
- `id` (package ID), `name`, `description`, version (from parent version block)

If no active package found in RELEASE_BACKLOG.md, fall back:
Read `requirements_tasks/RELEASES.md`. Find the entry with `status: active`.
If neither found: stop — "No active package or release found."
```

#### Step 5 — Mark released: update for both files

**Current**:
```
Read `requirements_tasks/RELEASES.md`. Find the entry with `status: active`. Change `status: active` to `status: released`.
```

**New**:
```
If active package was found in Step 4.1 from RELEASE_BACKLOG.md:
  - Update that package's status: active → released in RELEASE_BACKLOG.md
  - Also update RELEASES.md if the corresponding version entry has status: active → released

If active release was found in Step 4.1 from RELEASES.md (legacy fallback):
  - Update that release's status: active → released in RELEASES.md
```

---

## Transition Period Rules (All Changes)

All scripts must implement graceful dual-field handling until migration is confirmed complete:

1. **For filtering**: Accept `target_package` preferentially; fall back to `target_release` if `target_package` is absent
2. **For validation**: Validate whichever field is present; neither is required (both are optional during transition)
3. **For display**: Show both fields when both are present (no hiding of `target_release` data)
4. **RELEASE_BACKLOG.md missing**: All scripts degrade gracefully — warn but do not fail

The `--package` flag in scripts is always preferred over `--release` flag when both are provided (or error and ask user to use one).

---

## Files to Change

| File | Sub-task | Change Type |
|------|----------|-------------|
| `.claude/skills/requ-explore/skill.md` | A | Rewrite section 2.4, update 2.5 checklist |
| `.claude/skills/task-create/skill.md` | A | Rewrite "Release Version Inheritance" section, update YAML template |
| `.claude/skills/task-create-impl/skill.md` | A | Rewrite section 3.4, update YAML template |
| `.claude/skills/release-plan/skill.md` | B | Create new file |
| `.claude/skills/INDEX.md` | B | Add release-plan entry |
| `.claude/skills/ux-create-flow/skill.md` | C | Update Steps 2, 10, 12 |
| `.claude/skills/requ-derive-from-flow/skill.md` | C | Update Phase 1.1, Phase 2 matrix, Phase 4.2 template |
| `scripts/validate_meta.py` | D | Add package loading, add `_validate_target_package()`, dual validation in req/task validators |
| `scripts/generate_status_overview.py` | D | Add `target_package` to data models, add `--package` flag, add `PackageSummaryReportGenerator` |
| `scripts/next_tasks.py` | D | Add `target_package` to task dict, add `find_next_package()`, add `--package` flag, add `rank_tasks_by_package()` |
| `scripts/generate_technical_release_notes.py` | D | Add `find_active_package()`, update `load_release_tasks()` for dual mode, add `--package` flag |
| `.claude/skills/requ-prep-release/skill.md` | E | Update Phase 0 Bootstrap and Phase 6 Activate |
| `.claude/skills/release/skill.md` | E | Update Steps 4.1 and 5 |

**Total: 14 file changes (1 new file)**

---

## WHY Comments Required

These code changes in scripts require WHY comments (non-obvious decisions):

1. **`validate_meta.py` — `_validate_target_package()`**: WHY no format-regex validation (unlike `target_release` which validates semver). Reason: package IDs are free-form strings in RELEASE_BACKLOG.md, not a fixed format — the only valid check is existence in the backlog.

2. **`next_tasks.py` — `rank_tasks_by_package()` dual-mode fallback**: WHY the function falls back to release-based ranking when no `target_package` data exists. Reason: transition period — tasks migrated at different times, mixed-field state is normal.

3. **`generate_technical_release_notes.py` — `load_release_tasks()` precedence logic**: WHY `target_package` takes precedence over `target_release` when a task has both. Reason: a task that has been migrated should not appear in both package-mode and release-mode outputs.

---

## Testing Strategy

No automated tests exist for these scripts or skills. Manual verification steps:

1. After Sub-task D: Run `python scripts/validate_meta.py --verbose` against existing task files — should pass without new errors (both `target_release` and `target_package` accepted).
2. After Sub-task D: Run `python scripts/next_tasks.py` — should behave identically to before (no `target_package` data yet, falls back to `target_release`).
3. After Sub-task D: Add a test goal.md with `target_package: PKG-0.0.1-test` and run `validate_meta.py` — should warn "not found in RELEASE_BACKLOG.md" if RELEASE_BACKLOG.md is missing or warn "invalid package" if it exists but does not contain that ID.

---

## Risks

1. **RELEASE_BACKLOG.md not yet created**: All scripts and skills must degrade gracefully when the file is absent. This is covered by "warn and skip" behavior throughout.

2. **YAML parser limitations**: The simple fallback YAML parsers in `next_tasks.py` and `generate_technical_release_notes.py` do not parse nested objects. The RELEASE_BACKLOG.md format uses nested `packages` lists. Since PyYAML is available in the container, this is not a problem in practice — but the fallback parser will need an update for the nested structure. If PyYAML is unavailable, these scripts should warn and skip package loading.

3. **Two `--package` flags** in `requ-prep-release` and the scripts have different semantics: the skill asks for a full package ID, while `generate_status_overview.py --package` filters by that ID. These must be consistent — verify the same ID string is passed through.

4. **Skill token length**: Adding new sections to skills increases their token cost. Minimize wording — the new sections are concise replacements of existing text, not additions.
