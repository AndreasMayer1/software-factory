# Group 1 Implementation Plan: 7 New Pipeline Scripts
## TASK-PROC-035-08 — Release Pipeline Redesign

**Date**: 2026-04-25
**Author**: Opus (architecture-advisor agent)
**Status**: Ready for implementation

---

## Pre-Implementation Check: `next_tasks.py` target_package → release Resolution

**Verdict: No fix needed in `next_tasks.py` itself.**

Analysis:
- `next_tasks.py` uses `target_package` as a grouping key via `find_next_package()` in `scripts/task_ordering/ranker.py`
- `find_next_package()` resolves package → release by looking up `pkg["version"]` (which is `assigned_release`) from the `backlog_packages` list loaded from `RELEASE_BACKLOG.md` frontmatter (line ~122 in ranker.py)
- `load_backlog_packages()` in `next_tasks.py` reads `packages[].assigned_release` from `RELEASE_BACKLOG.md` frontmatter. This is the correct resolution path.
- The `create_orchestration_task.py` relies on `next_tasks.py` output to detect "UNCOVERED ACs" — this goes through `check_ac_coverage.py`, not a direct package→release join.

**Action for Group 1**: The new `should_use_agents.py` script needs to find requirements for a given release. It should reuse the same `load_backlog_packages()` pattern: load `RELEASE_BACKLOG.md`, filter packages by `assigned_release == version`, then find requirement files by scanning `requirements_tasks/` for `target_package` matching those package IDs. This is consistent with how `next_tasks.py` works. No changes needed to existing scripts before starting Group 1.

**Note**: The package IDs in `RELEASE_BACKLOG.md` are plain strings like `"QR Transfer Send"`, not structured IDs like `PKG-0.0.1-data`. The `should_use_agents.py` script must use exact string matching on `target_package` fields in goal.md/requirements.md files.

---

## Code Style Conventions (from existing scripts)

All 7 scripts must follow the patterns established in `scripts/create_orchestration_task.py`:

1. **Module docstring** with Usage + Exit codes at top
2. **`PROJECT_ROOT = Path(__file__).parent.parent`** — always computed this way
3. **`@dataclass` for Deps** when I/O injection is beneficial (for testability); for simpler scripts, direct Path usage is fine
4. **Pure helper functions** with no I/O (easy to unit-test); I/O-dependent functions clearly separated
5. **`argparse`** for all CLI scripts; `def main()` + `if __name__ == "__main__": main()`
6. **`sys.exit(N)` from `main()`** — never `exit(N)` at module level
7. **Errors to `sys.stderr`**; results to `sys.stdout`
8. **`try yaml.safe_load` with fallback** — import yaml at top with `HAS_YAML = True/False` guard (see `next_tasks.py` pattern)
9. **`Path.read_text(encoding="utf-8")`** for all file reads
10. **`re.MULTILINE` on frontmatter regexes** when needed

---

## Script 1: `scripts/parse_task_creation_plan.py`

**Role**: Shared library. Parses `task_creation_plan.md` → Python dict / JSON. All other scripts import from this module.

### File Path
`/workspaces/private_mood_tracker/flutter_app/scripts/parse_task_creation_plan.py`

### CLI Interface
```
python3 scripts/parse_task_creation_plan.py <plan_path>
```
- Positional argument: `plan_path` — path to `task_creation_plan.md`
- Outputs JSON to stdout (for debugging/inspection)
- `--version-id PLAN-X-vN` — optional, select specific plan version (default: latest non-archived)

### Exit Codes
- `0` — success, JSON written to stdout
- `1` — file not found or unreadable
- `2` — parse error (malformed frontmatter or YAML block)

### Input/Output Contract
- **Reads**: A single `task_creation_plan.md` file (YAML frontmatter + Markdown body)
- **Stdout**: JSON object (when called as CLI):
  ```json
  {
    "frontmatter": { "plan_id": "...", "release": "0.0.1", "status": "approved", ... },
    "packages": [
      {
        "id": "QR Transfer Send",
        "name": "Transfer Data Model",
        "tasks": [
          {
            "task_name": "...",
            "task_type": "implement",
            "target_package": "...",
            "covers_acs": ["AC-01", "AC-02"],
            "effort": "M",
            "layer": "data",
            "after": [],
            "opus_recommended": false,
            "req_path": "...",
            "req_commit": "...",
            "implementation_notes": "...",
            "rationale": "...",
            "_entry_index": 1
          }
        ]
      }
    ]
  }
  ```
- **Stderr**: error messages on parse failure

### Key Implementation Notes

**Multi-version handling**: The plan file may contain multiple versions (`## Plan v2 — [date]` sections). Each version has its own YAML frontmatter block (fenced with ` ```yaml ` ... ` ``` `). The parser must:
1. Find all top-level `## Plan vN` headings (or the implicit v1 if absent)
2. Extract each version's frontmatter block
3. Select the latest non-archived version by `plan_id` suffix (e.g., `PLAN-0.0.1-v2` > `PLAN-0.0.1-v1`)
4. Use that version's task entries

**Parsing Algorithm** (from protocol §5):
```python
def parse_plan(content: str, version_id: Optional[str] = None) -> dict:
    # Step 1: Parse top-level YAML frontmatter
    frontmatter = parse_frontmatter(content)  # re-use parse_frontmatter() from next_tasks.py pattern

    # Step 2: Handle multi-version — find the correct version section
    # If content has "## Plan v2" headings, split on them and find latest non-archived
    # For single-version plans, use the entire body
    body = extract_version_body(content, version_id)

    # Step 3: Walk Markdown headings
    packages = []
    current_package = None
    current_task = None

    for each heading/block in body:
        if heading matches r'^### (.+)$':
            # Open new package section
            current_package = { "id": heading_text, "name": heading_text, "tasks": [] }
            packages.append(current_package)

        elif heading matches r'^#### Task \d+: (.+)$':
            # Open new task entry
            current_task = { "_entry_index": len(current_package["tasks"]) + 1 }

        elif inside task and next block is fenced YAML:
            # Step 3: Extract fenced YAML block immediately below the task heading
            task_yaml = parse_yaml_block(block_content)
            current_task.update(task_yaml)

        elif inside task after YAML close fence, before next ####/###:
            # Step 4: Capture rationale prose
            current_task["rationale"] = prose.strip()
            current_package["tasks"].append(current_task)
            current_task = None

    # Step 5: Return
    return { "frontmatter": frontmatter, "packages": packages }
```

**`covers_acs` normalization**: Always return as a Python `list` (set-compare semantics for callers). Strip whitespace from each AC ID.

**`after` normalization**: Return as list. Entries may be real TASK-IDs or `#PKG-X:Task N` references. Keep them as-is; resolution is the caller's responsibility.

**`effort` validation**: Must be one of `XS`, `S`, `M`, `L`, `XL`. If invalid, emit a warning to stderr but do not fail — return the raw value so callers can decide.

**Edge cases**:
- Plan file is `archived: true` → raise `PlanArchivedError` (subclass of `ValueError`)
- No tasks found in any package → return `{"frontmatter": fm, "packages": []}` (not an error)
- Fenced YAML block contains invalid YAML → raise `PlanParseError` with line number hint
- `task_name` field missing from YAML block → use the heading text as fallback

### Module API (importable)

```python
# Public API for other scripts to import
from parse_task_creation_plan import parse_plan, PlanParseError, PlanArchivedError

def parse_plan(plan_path: str, version_id: Optional[str] = None) -> dict:
    """Parse task_creation_plan.md and return structured dict.
    Raises: PlanParseError, PlanArchivedError, FileNotFoundError
    """

def get_task_entry(plan: dict, target_package: str, task_name: Optional[str] = None) -> Optional[dict]:
    """Look up a specific task entry from a parsed plan.
    If task_name is None, returns the first task for the package.
    Returns None if not found.
    """

def get_package_tasks(plan: dict, target_package: str) -> list:
    """Return all task entries for a given target_package."""

def get_execution_order(plan: dict) -> list:
    """Return package IDs in execution order from the ## Execution Order section."""
```

### Dependencies
- No imports from other new scripts (this IS the shared library)
- Uses: `pathlib`, `re`, `json`, `sys`, `argparse`
- Optional: `yaml` (with `HAS_YAML` guard, same as `next_tasks.py`)

### Skeleton (~80 lines of core logic)

```python
#!/usr/bin/env python3
"""Parse task_creation_plan.md into a structured dictionary / JSON.

This module is primarily a shared library imported by other pipeline scripts.
A CLI entry point is provided for debugging.

Usage:
    python3 scripts/parse_task_creation_plan.py <plan_path>

Exit codes:
    0  success — JSON written to stdout
    1  file not found or unreadable
    2  parse error (malformed frontmatter or YAML block)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

PROJECT_ROOT = Path(__file__).parent.parent


class PlanParseError(ValueError):
    pass


class PlanArchivedError(ValueError):
    pass


def _parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Extract top-level YAML frontmatter."""
    # [same pattern as next_tasks.py parse_frontmatter()]
    ...


def _parse_yaml_block(block: str) -> Dict[str, Any]:
    """Parse a fenced YAML block (content between ``` fences)."""
    if HAS_YAML:
        try:
            return yaml.safe_load(block) or {}
        except Exception as e:
            raise PlanParseError(f"Invalid YAML in task block: {e}")
    # fallback to simple parser
    ...


def _extract_version_body(content: str, version_id: Optional[str]) -> str:
    """Select the correct version section of the plan body."""
    # If no "## Plan v" headings exist → return full body after frontmatter
    # If version_id given → find that specific section
    # Otherwise → find latest non-archived version
    ...


def _parse_execution_order(body: str) -> List[str]:
    """Extract package IDs from ## Execution Order section."""
    ...


def parse_plan(plan_path: str, version_id: Optional[str] = None) -> Dict[str, Any]:
    """Parse task_creation_plan.md. Returns structured dict."""
    path = Path(plan_path)
    if not path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")
    content = path.read_text(encoding="utf-8")
    frontmatter = _parse_frontmatter(content)
    if frontmatter and frontmatter.get("status") == "archived" and version_id is None:
        raise PlanArchivedError(f"Plan at {plan_path} is archived")
    body = _extract_version_body(content, version_id)
    packages = _walk_headings(body)
    execution_order = _parse_execution_order(body)
    return {
        "frontmatter": frontmatter or {},
        "packages": packages,
        "execution_order": execution_order,
    }


def get_task_entry(plan: Dict, target_package: str,
                   task_name: Optional[str] = None) -> Optional[Dict]:
    for pkg in plan.get("packages", []):
        if pkg["id"] == target_package:
            if task_name is None:
                return pkg["tasks"][0] if pkg["tasks"] else None
            for task in pkg["tasks"]:
                if task.get("task_name") == task_name:
                    return task
    return None


def get_package_tasks(plan: Dict, target_package: str) -> List[Dict]:
    for pkg in plan.get("packages", []):
        if pkg["id"] == target_package:
            return pkg["tasks"]
    return []


def get_execution_order(plan: Dict) -> List[str]:
    return plan.get("execution_order", [])


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse task_creation_plan.md → JSON")
    parser.add_argument("plan_path", help="Path to task_creation_plan.md")
    parser.add_argument("--version-id", help="Specific plan version to extract (e.g. PLAN-0.0.1-v2)")
    args = parser.parse_args()
    try:
        result = parse_plan(args.plan_path, args.version_id)
        print(json.dumps(result, indent=2, default=str))
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except (PlanParseError, PlanArchivedError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
```

---

## Script 2: `scripts/check_task_against_plan.py`

**Role**: Compare a created task's `goal.md` against its plan entry. Called by `task-create-code` Phase 6 and `release-begin-impl-finalize` Phase 1.

### File Path
`/workspaces/private_mood_tracker/flutter_app/scripts/check_task_against_plan.py`

### CLI Interface
```
python3 scripts/check_task_against_plan.py --task TASK-ID --plan PLAN_PATH [--verbose]
```

Arguments:
- `--task TASK-ID` (required) — the task ID to look up (e.g. `TASK-FUNC-007-12`)
- `--plan PLAN_PATH` (required) — path to `task_creation_plan.md`
- `--verbose` — print full diff of all fields

### Exit Codes
- `0` — task matches plan entry (all required fields conform)
- `1` — mismatch found (at least one conformance rule violated, excluding effort ±1)
- `2` — no plan entry found for this task (task has no `target_package` in plan; skip silently)
- `3` — argument error or file not found

### Input/Output Contract
- **Reads**:
  - Goal.md of the task (found by scanning `requirements_tasks/**/goal.md` for `task_id: TASK-ID`)
  - `task_creation_plan.md` at the given plan path
- **Stdout**: conformance report (one line per field, PASS/FAIL/WARN):
  ```
  TASK-FUNC-007-12 vs plan entry "Implement TransferSession entity"
  target_package : PASS  (QR Transfer Send)
  covers_acs     : PASS  ({AC-01, AC-02, AC-03})
  effort         : WARN  goal=L plan=M (±1 allowed)
  layer          : PASS  (data)
  Overall        : PASS (1 warning)
  ```
- **Stderr**: error messages only

### Key Implementation Notes

**Finding the goal.md**: Scan `requirements_tasks/**/goal.md` for a file whose frontmatter contains `task_id: TASK-ID`. Use `subprocess.run(["find", ...])` pattern from `next_tasks.py` for speed.

**Finding the plan entry**: Use `parse_task_creation_plan.get_package_tasks(plan, target_package)` where `target_package` comes from the goal.md frontmatter. If the target_package is not in the plan at all → exit 2.

**If multiple tasks exist for the same package**: match by `task_name` similarity. If no match → exit 2.

**Conformance rules** (from protocol §2c):
```python
EFFORT_ORDER = ["XS", "S", "M", "L", "XL"]

def effort_conformant(goal_effort: str, plan_effort: str) -> tuple[bool, bool]:
    """Returns (passes, is_warning). ±1 is a WARN, not a FAIL."""
    try:
        gi = EFFORT_ORDER.index(goal_effort)
        pi = EFFORT_ORDER.index(plan_effort)
        diff = abs(gi - pi)
        if diff == 0: return True, False    # exact match
        if diff == 1: return True, True     # ±1: pass with warning
        return False, False                 # >±1: fail
    except ValueError:
        return False, False  # unknown effort value

def check_conformance(goal_meta: dict, plan_entry: dict) -> list[dict]:
    """Returns list of check results: {field, status, goal_val, plan_val, message}"""
    results = []

    # target_package: exact match
    goal_pkg = goal_meta.get("target_package", "")
    plan_pkg = plan_entry.get("target_package", "")
    results.append({
        "field": "target_package",
        "status": "PASS" if goal_pkg == plan_pkg else "FAIL",
        "goal_val": goal_pkg, "plan_val": plan_pkg,
    })

    # covers_acs: set equality
    goal_acs = set(goal_meta.get("covers", {}).get("acceptance_criteria", []))
    plan_acs = set(plan_entry.get("covers_acs", []))
    results.append({
        "field": "covers_acs",
        "status": "PASS" if goal_acs == plan_acs else "FAIL",
        "goal_val": sorted(goal_acs), "plan_val": sorted(plan_acs),
    })

    # effort: ±1 allowed
    passes, is_warn = effort_conformant(goal_meta.get("effort", ""), plan_entry.get("effort", ""))
    results.append({
        "field": "effort",
        "status": "WARN" if (passes and is_warn) else ("PASS" if passes else "FAIL"),
        "goal_val": goal_meta.get("effort"), "plan_val": plan_entry.get("effort"),
    })

    # layer: exact match (from goal.md scope_description or layer field)
    goal_layer = goal_meta.get("layer", "")
    plan_layer = plan_entry.get("layer", "")
    results.append({
        "field": "layer",
        "status": "PASS" if goal_layer == plan_layer else "FAIL",
        "goal_val": goal_layer, "plan_val": plan_layer,
    })

    return results
```

**Overall exit code logic**:
```python
has_fail = any(r["status"] == "FAIL" for r in results)
exit_code = 1 if has_fail else 0
```

**Note on `layer` field**: Goal.md frontmatter may not have an explicit `layer:` field in current templates. The implementation should check `scope_description` for layer hints as a fallback, or accept that `layer` is an optional check (SKIP if not present in goal.md, rather than FAIL).

### Dependencies
- Imports `parse_task_creation_plan` (Script 1)

---

## Script 3: `scripts/reconcile_after_chains.py`

**Role**: Find missing `after:` entries across all impl tasks for a release. With `--apply`, edits goal.md files in-place.

### File Path
`/workspaces/private_mood_tracker/flutter_app/scripts/reconcile_after_chains.py`

### CLI Interface
```
python3 scripts/reconcile_after_chains.py --release VERSION [--plan PLAN_PATH] [--apply] [--verbose]
```

Arguments:
- `--release VERSION` (required) — e.g. `0.0.1`
- `--plan PLAN_PATH` (optional) — path to `task_creation_plan.md`; if omitted, detects automatically
- `--apply` — edit goal.md files in-place to add missing after entries
- `--verbose` — print full detail per task

### Exit Codes
- `0` — all after-chains valid (or `--apply` completed successfully)
- `1` — missing after-entries found (without `--apply`); or apply failed for ≥1 task
- `3` — no active release found or argument error

### Input/Output Contract
- **Reads**: All `goal.md` files for tasks whose `target_release == VERSION` (or whose `target_package` is assigned to that release)
- **Reads**: `task_creation_plan.md` (if provided) for authoritative `after:` entries
- **Stdout** (without `--apply`):
  ```
  After-chain reconciliation for release 0.0.1
  TASK-FUNC-007-12 (QR Transfer Send): missing after: [TASK-FUNC-007-11]
    Plan says: after: [TASK-FUNC-007-11]
    Goal has:  after: []

  Total: 2 tasks with missing after-entries.
  Run with --apply to fix.
  ```
- **Stdout** (with `--apply`):
  ```
  TASK-FUNC-007-12: added after: [TASK-FUNC-007-11] — DONE
  Total: 2 tasks updated.
  ```
- **Stderr**: file I/O errors only

### Key Implementation Notes

**Step 1 — Load all release tasks**: Scan all `goal.md` files, filter by `target_release == VERSION` or by `target_package` belonging to the release (via `RELEASE_BACKLOG.md`).

**Step 2 — Load plan** (if provided): Use `parse_task_creation_plan.parse_plan()`. Build a dict: `target_package → [list of after-entries per task]`. Note: plan `after:` entries may use `#PKG-X:Task N` references — resolve these to real TASK-IDs by looking up committed tasks with matching `target_package` and `_entry_index` (or task name). If resolution fails, skip that reference with a warning.

**Step 3 — Compare**: For each task in the release, check if its `after:` list contains all entries that the plan specifies. Missing entries = entries in plan's `after:` that are not in goal.md's `after:`.

**Step 4 — Report or apply**:
- Without `--apply`: print missing entries list
- With `--apply`: edit each goal.md's `after:` field in-place

**In-place edit algorithm** (critical — must not corrupt frontmatter):
```python
def add_after_entries(goal_path: str, new_entries: list[str]) -> None:
    content = Path(goal_path).read_text(encoding="utf-8")
    # Find the after: line in frontmatter
    # Pattern: after: [] or after: [TASK-X, TASK-Y] or after: followed by list items
    # Strategy: parse frontmatter, update the after list, serialize back
    fm_match = re.search(r'^(---\n)(.*?)(^---)', content, re.DOTALL | re.MULTILINE)
    if not fm_match:
        raise ValueError(f"No frontmatter in {goal_path}")
    yaml_text = fm_match.group(2)
    # Update after: field
    updated_yaml = update_after_field(yaml_text, new_entries)
    new_content = f"---\n{updated_yaml}---" + content[fm_match.end():]
    Path(goal_path).write_text(new_content, encoding="utf-8")
```

**`update_after_field` strategy**: Use regex to find and replace the `after:` value in the YAML text. Handle both inline (`after: [A, B]`) and block list forms:
```python
def update_after_field(yaml_text: str, new_entries: list[str]) -> str:
    # Merge existing + new entries (deduplicate)
    # existing: parse from yaml_text
    existing = parse_after_from_yaml(yaml_text)
    merged = list(dict.fromkeys(existing + new_entries))  # preserve order, deduplicate
    # Replace inline form: after: [...]
    inline_pattern = r'^(after:\s*)\[.*?\]'
    inline_replacement = f'after: [{", ".join(merged)}]'
    if re.search(inline_pattern, yaml_text, re.MULTILINE):
        return re.sub(inline_pattern, inline_replacement, yaml_text, flags=re.MULTILINE)
    # Replace block form: after:\n  - X
    # ... handle multi-line list
    return yaml_text  # fallback: no change (with warning)
```

**`#PKG-X:Task N` reference resolution**: When plan has intra-plan references, resolve by:
1. Parse the package name from `#PKG-X:` prefix (it's the package heading text)
2. Find the Nth task entry for that package in the plan
3. Look up which real TASK-ID was created for that entry by scanning all `goal.md` files for matching `target_package` + similar task name
4. If not found → emit a warning and skip (do not add unresolved reference)

**Auto-detect plan path**: If `--plan` not given, look for `task_creation_plan.md` in the same explore task folder that is linked from the first orchestration task's `plan_path` frontmatter field. Fallback: scan `requirements_tasks/process/AI_rules/requirements_management/release_preparation/tasks/` for a completed explore task with matching `target_release`.

### Dependencies
- Imports `parse_task_creation_plan` (Script 1)

---

## Script 4: `scripts/summarize_plan.py`

**Role**: Produce a 1-page statistics summary of a `task_creation_plan.md` for the user gate in `release-begin-impl` Phase 5.

### File Path
`/workspaces/private_mood_tracker/flutter_app/scripts/summarize_plan.py`

### CLI Interface
```
python3 scripts/summarize_plan.py --plan PLAN_PATH [--format md|text]
```

Arguments:
- `--plan PLAN_PATH` (required) — path to `task_creation_plan.md`
- `--format md|text` — output format (default: `md`)

### Exit Codes
- `0` — success, summary written to stdout
- `1` — file not found or parse error

### Input/Output Contract
- **Reads**: `task_creation_plan.md`
- **Stdout**: 1-page markdown or text summary:
  ```markdown
  # Task Creation Plan Summary: Release 0.0.1
  Plan ID: PLAN-0.0.1-v1 | Status: approved | Created: 2026-04-25

  ## Coverage
  - Packages covered: 4
  - Total tasks: 12
  - Task types: implement=9, verify=2, scribble=1

  ## Effort Distribution
  | Effort | Count | Tasks |
  |--------|-------|-------|
  | XS     | 1     | ... |
  | S      | 4     | ... |
  | M      | 5     | ... |
  | L      | 2     | ... |

  ## By Layer
  - data: 3 tasks
  - domain: 3 tasks
  - presentation: 4 tasks
  - test: 2 tasks

  ## Packages (Execution Order)
  1. QR Transfer Send — 3 tasks (S, M, M)
  2. Transfer Pairing — 2 tasks (M, L)
  ...

  ## Flags
  - opus_recommended: 2 tasks (TASK names listed)
  - verify tasks: 2 (already-implemented ACs)

  ## After-Chain Density
  - Tasks with after dependencies: 7 / 12 (58%)
  - Max chain depth: 3
  ```

### Key Implementation Notes

**After-chain depth calculation**: Build a DAG from `after:` references within the plan (using `#PKG-X:Task N` intra-plan refs and resolved real IDs). Compute longest path via topological sort. Handle cycles (warn, skip).

**Effort total computation**:
```python
EFFORT_DAYS = {"XS": 0.5, "S": 1, "M": 2, "L": 4, "XL": 8}
```
Include estimated total days in the summary.

**Task listing in effort table**: List task names truncated to 40 chars for readability.

**No I/O side effects**: Only reads the plan file, writes to stdout. No file writes.

### Dependencies
- Imports `parse_task_creation_plan` (Script 1)

---

## Script 5: `scripts/check_requirement_implementation.py`

**Role**: Grep `lib/` source tree for implementation traces of each AC in a requirement, returning per-AC verdicts. Used by Phase 2c Planner to detect already-implemented ACs.

### File Path
`/workspaces/private_mood_tracker/flutter_app/scripts/check_requirement_implementation.py`

### CLI Interface
```
python3 scripts/check_requirement_implementation.py --requirement REQ-FUNC-007 [--verbose] [--json]
```

Arguments:
- `--requirement REQ-ID` (required) — e.g. `REQ-FUNC-007`
- `--verbose` — show matching file paths per AC
- `--json` — output JSON instead of human-readable text

### Exit Codes
- `0` — all ACs have verdicts (some may be `likely_missing`)
- `1` — requirement file not found
- `2` — no ACs found in requirement file
- `3` — argument error

### Input/Output Contract
- **Reads**: `requirements_tasks/**/requirements.md` with `id: REQ-ID` in frontmatter
- **Reads**: `lib/**/*.dart` files via grep
- **Stdout** (human-readable):
  ```
  REQ-FUNC-007 — 12 ACs analyzed

  AC-01: likely_implemented   (3 matches in lib/)
    lib/features/data_transfer/domain/entities/transfer_session.dart
  AC-02: likely_implemented   (2 matches)
  AC-03: uncertain            (1 weak match)
  AC-04: likely_missing       (0 matches)
  ...

  Summary: 8 likely_implemented, 2 uncertain, 2 likely_missing
  ```
- **Stdout** (JSON with `--json`):
  ```json
  {
    "requirement": "REQ-FUNC-007",
    "acs": [
      {"id": "AC-01", "verdict": "likely_implemented", "match_count": 3, "files": [...]},
      {"id": "AC-04", "verdict": "likely_missing", "match_count": 0, "files": []}
    ],
    "summary": {"likely_implemented": 8, "uncertain": 2, "likely_missing": 2}
  }
  ```

### Key Implementation Notes

**Finding the requirement file**: Scan all `requirements.md` files for `id: REQ-ID` in frontmatter. Use `find` subprocess for speed.

**Extracting ACs from requirements.md**: Parse the markdown body for AC entries. ACs typically appear as:
- `- [ ] AC-01:` or `- [x] AC-01:` at the start of a list item
- Also scan for `**AC-01**` or `### AC-01` headings

Extract the AC ID and its description text (used to generate search terms).

**Search term generation** (this is the core heuristic):
```python
def ac_to_search_terms(ac_id: str, ac_text: str) -> list[str]:
    """Generate grep search terms from AC text.

    Strategy:
    1. AC-ID itself (e.g. "AC-01") → search for it in comments/strings in lib/
    2. Key nouns from AC text (stop-word filtered, ≥4 chars, CamelCase variants)
    3. Domain-specific terms: entity names, method names inferred from AC text
    """
    terms = [ac_id]  # always search for the AC-ID itself
    # Extract nouns: split on whitespace, filter stop words, convert to camelCase/PascalCase
    words = [w for w in re.findall(r'[A-Za-z]{4,}', ac_text) if w.lower() not in STOP_WORDS]
    for word in words[:3]:  # top 3 content words
        terms.append(word)
        terms.append(word[0].upper() + word[1:])  # PascalCase variant
    return terms
```

**Verdict logic**:
```python
def compute_verdict(matches: list[str]) -> str:
    """
    likely_implemented : ≥2 distinct files match, or AC-ID itself found in lib/
    uncertain          : exactly 1 file matches
    likely_missing     : 0 matches
    """
    if not matches:
        return "likely_missing"
    ac_id_in_matches = any(re.search(r'\bAC-\d+\b', m) for m in matches)  # AC-ID literal
    if len(set(matches)) >= 2 or ac_id_in_matches:
        return "likely_implemented"
    return "uncertain"
```

**Grep execution**:
```python
result = subprocess.run(
    ["grep", "-rl", "--include=*.dart", term, str(PROJECT_ROOT / "lib")],
    capture_output=True, text=True
)
```

**Performance**: Run grep once per search term, collect unique files. For large `lib/` trees this is fast (grep is OS-level). Do NOT read Dart files into Python — use grep only.

**Stop words** (class-level constant):
```python
STOP_WORDS = {"must", "shall", "when", "with", "from", "that", "this", "have",
              "will", "been", "their", "which", "each", "also", "into", "than"}
```

### Dependencies
- No imports from other new scripts (standalone)

---

## Script 6: `scripts/find_orchestration_tasks.py`

**Role**: Detect orchestration tasks by structural signature. Used by `create_orchestration_task.py` for duplicate-check, and potentially by `claude-automated-mode`.

### File Path
`/workspaces/private_mood_tracker/flutter_app/scripts/find_orchestration_tasks.py`

### CLI Interface
```
python3 scripts/find_orchestration_tasks.py [--status STATUS] [--release VERSION] [--json]
```

Arguments:
- `--status STATUS` — filter by status: `pending`, `in_progress`, `completed`, `any` (default: `any`)
- `--release VERSION` — filter by `target_release` value
- `--json` — output JSON instead of human-readable lines

### Exit Codes
- `0` — found ≥1 orchestration task matching filters (or 0 with `--json`)
- `1` — no orchestration tasks found matching filters
- `3` — argument error

**Note**: Exit 0 when found, exit 1 when not found — callers use this as a boolean check.

### Input/Output Contract
- **Reads**: All `goal.md` files in `requirements_tasks/`
- **Stdout** (human-readable):
  ```
  TASK-PROC-035-08 pending  target_release=0.0.1
    path: requirements_tasks/.../goal.md
  ```
- **Stdout** (JSON with `--json`):
  ```json
  [
    {
      "task_id": "TASK-PROC-035-08",
      "status": "pending",
      "target_release": "0.0.1",
      "scope_description": "Orchestration: ...",
      "path": "requirements_tasks/.../goal.md"
    }
  ]
  ```
- **Stderr**: file I/O warnings only (non-fatal)

### Key Implementation Notes

**Structural signature** (from protocol §4):
An orchestration task MUST satisfy BOTH conditions:
1. `target_release` is set (non-empty string in frontmatter)
2. `scope_description` starts with `"Orchestration:"` (case-sensitive, colon required)

```python
def is_orchestration_task(meta: dict) -> bool:
    target_release = str(meta.get("target_release", "") or "").strip()
    scope_desc = str(meta.get("scope_description", "") or "").strip()
    return bool(target_release) and scope_desc.startswith("Orchestration:")
```

**Why this approach**: Avoids grep on content (fragile) and avoids path-name assumptions. The two frontmatter fields together uniquely identify orchestration tasks vs. regular impl/explore tasks.

**Scanning**: Use the same `find` subprocess pattern from `next_tasks.py` for speed:
```python
def _find_files(root: Path, name: str) -> list[Path]:
    result = subprocess.run(["find", str(root), "-name", name], capture_output=True, text=True)
    return [Path(p) for p in result.stdout.splitlines() if p.strip()]
```

**Status filter**: `--status any` returns all statuses. Other values filter to exact match.

**Release filter**: exact string match on `target_release` frontmatter field.

**Exit code for `--json`**: Always exit 0 when JSON output (empty array `[]` is a valid result). Exit 1 only for non-JSON mode when 0 tasks found.

**Performance note**: This replaces the fragile `grep` in `create_orchestration_task.py`'s `find_existing_orchestration_task()`. The new script is importable:
```python
from find_orchestration_tasks import find_orchestration_tasks
tasks = find_orchestration_tasks(status="pending", release="0.0.1")
```

### Module API (importable)

```python
def find_orchestration_tasks(
    status: Optional[str] = None,
    release: Optional[str] = None,
    root: Optional[Path] = None,
) -> list[dict]:
    """Return list of orchestration task dicts matching filters."""
```

### Dependencies
- No imports from other new scripts (standalone, uses only stdlib)

---

## Script 7: `scripts/should_use_agents.py`

**Role**: Compute total size of requirement files for a release. Output JSON verdict (`orchestrator_direct` vs `agents_required`) based on 30KB/5-file threshold. Used by `release-begin-impl` Phase 1 and `task-create-code` Phase 1.

### File Path
`/workspaces/private_mood_tracker/flutter_app/scripts/should_use_agents.py`

### CLI Interface
```
python3 scripts/should_use_agents.py --release VERSION [--single-file FILE_PATH] [--verbose]
```

Arguments:
- `--release VERSION` — find all requirement files for this release (uses `RELEASE_BACKLOG.md` + `target_package` field)
- `--single-file FILE_PATH` — check just one file (for `task-create-code` single-requirement use case)
- `--verbose` — include per-file sizes in output

Either `--release` or `--single-file` is required (mutually exclusive).

### Exit Codes
- `0` — always (JSON output; exit code does not indicate verdict — read the JSON)
- `1` — release not found or file not readable

### Input/Output Contract
- **Reads**: `RELEASE_BACKLOG.md` (to find packages for the release), then `requirements_tasks/**/requirements.md` files with matching `target_package`
- **Stdout**: JSON:
  ```json
  {
    "release": "0.0.1",
    "verdict": "agents_required",
    "total_bytes": 87432,
    "file_count": 7,
    "threshold_bytes": 30720,
    "threshold_files": 5,
    "files": [
      {"path": "requirements_tasks/.../requirements.md", "package": "QR Transfer Send", "bytes": 12500},
      {"path": "requirements_tasks/.../requirements.md", "package": "Transfer Pairing", "bytes": 8200}
    ]
  }
  ```
- **Stderr**: warnings for files that could not be read

### Key Implementation Notes

**Step 1 — Find packages for release**: Load `RELEASE_BACKLOG.md` frontmatter. Filter packages where `assigned_release == VERSION`. Collect package IDs.

```python
def find_packages_for_release(version: str) -> list[str]:
    content = RELEASE_BACKLOG_FILE.read_text(encoding="utf-8")
    meta = parse_frontmatter(content)  # reuse parse_frontmatter from this script
    if not meta or "packages" not in meta:
        return []
    return [
        str(pkg["id"])
        for pkg in meta.get("packages", [])
        if isinstance(pkg, dict) and str(pkg.get("assigned_release", "")) == version
    ]
```

**Step 2 — Find requirement files**: For each package ID, scan all `requirements.md` files in `requirements_tasks/` for `target_package: "<package_id>"` in frontmatter. This is the same resolution path used by `next_tasks.py`.

**Important**: Packages in `RELEASE_BACKLOG.md` have `source.ref` pointing to a requirement ID (e.g., `REQ-FUNC-007`). Use BOTH strategies:
1. Find `requirements.md` files with `target_package` matching the package ID
2. Also find `requirements.md` files with `id: <source.ref>` (the parent requirement)
Deduplicate by path.

**Step 3 — Compute sizes**: `os.path.getsize()` for each requirements.md file.

**Step 4 — Apply thresholds**:
```python
THRESHOLD_BYTES = 30 * 1024  # 30KB
THRESHOLD_FILES = 5

def compute_verdict(total_bytes: int, file_count: int) -> str:
    if total_bytes <= THRESHOLD_BYTES and file_count <= THRESHOLD_FILES:
        return "orchestrator_direct"
    return "agents_required"
```

**For `--single-file`**: Skip release/package lookup. Just compute size of the single file.
```json
{
  "verdict": "orchestrator_direct",
  "total_bytes": 8200,
  "file_count": 1,
  "threshold_bytes": 30720,
  "threshold_files": 5,
  "files": [{"path": "...", "bytes": 8200}]
}
```

**`parse_frontmatter` reuse**: Do NOT import from `next_tasks.py` (circular/fragile). Copy the minimal `parse_frontmatter` function into this script (or extract to a shared `scripts/_utils.py` if preferred — but given project conventions, copy is simpler and avoids import complexity).

**Finding `target_package` in requirements.md**: The `target_package` field is in the frontmatter of `requirements.md` files at the feature level (e.g., `feat_qr_data_transfer/requirements.md`). These are different from task `goal.md` files.

### Dependencies
- No imports from other new scripts (standalone)
- Uses `subprocess.run(["find", ...])` for file discovery

---

## Shared Utilities Note

The `parse_frontmatter()` function appears in both `next_tasks.py` and `generate_status_overview.py` with slightly different implementations. For the 7 new scripts:

**Recommendation**: Copy the `parse_frontmatter` + `_parse_simple_yaml` functions from `next_tasks.py` directly into scripts that need them (`should_use_agents.py`, `reconcile_after_chains.py`, `find_orchestration_tasks.py`, `check_task_against_plan.py`). Do NOT create a shared `_utils.py` module — the existing project does not have one, and introducing a new internal module would require all callers to manage the `sys.path.insert` pattern. Keep each script self-contained.

**Exception**: `parse_task_creation_plan.py` IS the shared library. Scripts 2, 3, and 4 import from it. They use `sys.path.insert(0, str(Path(__file__).parent))` before the import (same pattern as `next_tasks.py` uses for `task_ordering`).

---

## Implementation Order Within Group 1

```
Step 1: parse_task_creation_plan.py           (no deps — implement first)
Step 2: find_orchestration_tasks.py           (no deps — can be parallel with step 1)
        should_use_agents.py                  (no deps — can be parallel)
        check_requirement_implementation.py   (no deps — can be parallel)
Step 3: check_task_against_plan.py            (depends on parse_task_creation_plan.py)
        reconcile_after_chains.py             (depends on parse_task_creation_plan.py)
        summarize_plan.py                     (depends on parse_task_creation_plan.py)
```

All 7 scripts must be implemented before the Group 1 commit. They form a coherent set that subsequent groups depend on.

---

## Quality Criteria

- [ ] All 7 scripts have correct shebang and module docstring with Usage + Exit codes
- [ ] All exit codes match the spec exactly
- [ ] `parse_task_creation_plan.py` correctly handles multi-version plans (v1/v2)
- [ ] `parse_task_creation_plan.py` correctly normalizes `covers_acs` as a list
- [ ] `check_task_against_plan.py` exits 2 (not 1) when no plan entry exists
- [ ] `reconcile_after_chains.py --apply` does not corrupt frontmatter YAML
- [ ] `reconcile_after_chains.py` handles `#PKG-X:Task N` references gracefully (warning, not crash)
- [ ] `summarize_plan.py` output fits on one screen (≤50 lines for typical plan)
- [ ] `check_requirement_implementation.py` runs in <5s for a typical requirement (grep-based, no full file reads)
- [ ] `find_orchestration_tasks.py` correctly identifies tasks by structural signature only
- [ ] `should_use_agents.py` JSON output always includes `verdict`, `total_bytes`, `file_count`, `files` keys
- [ ] All scripts print errors to stderr, results to stdout
- [ ] `parse_task_creation_plan.py` is importable without side effects (no module-level code that does I/O)
- [ ] Scripts 2, 3, 4 use `sys.path.insert(0, str(Path(__file__).parent))` before importing parse_task_creation_plan
- [ ] No script imports from `next_tasks.py` or `generate_status_overview.py` (fragile — those are CLI scripts)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| `task_creation_plan.md` schema may evolve mid-implementation | Parser is designed to be lenient — missing optional fields return None, not errors |
| `covers_acs` set equality check may fail on whitespace differences | Normalize: `set(ac.strip() for ac in acs_list)` |
| Frontmatter YAML corruption in `reconcile_after_chains --apply` | Write to a temp file first, then `os.replace()` for atomic swap |
| `find_orchestration_tasks.py` may be slow on large `requirements_tasks/` trees | Use `subprocess.run(["find", ...])` — same pattern as `next_tasks.py`, fast even in WSL2 |
| `check_requirement_implementation.py` false positives (AC-01 text matches unrelated code) | Verdict threshold is conservative: `uncertain` at 1 match, only `likely_implemented` at ≥2 distinct files |
| Multi-line YAML block form in `after:` field breaks `reconcile_after_chains` regex | Handle both inline `after: [A, B]` and block list forms explicitly |
| `should_use_agents.py` may not find feature-level `requirements.md` files if `target_package` naming differs | Use BOTH `target_package` field match AND `source.ref` requirement-ID match as fallback |

---

## Notes for Implementation Agent

1. **Do not change existing scripts** in Group 1. Only create the 7 new files.
2. **The `_walk_headings` function** in `parse_task_creation_plan.py` is the most complex piece — allocate 30-40 lines for it. Use a state machine (enum or string state variable).
3. **For `reconcile_after_chains.py --apply`**: use `os.replace(tmp_path, goal_path)` for atomic writes to avoid partial writes on crash.
4. **Test each script manually** after writing by running it against real files in the repo (e.g., `python3 scripts/summarize_plan.py --plan [any test plan file]`).
5. **The `task_creation_plan.md` file does not exist yet** in the repo — the parsing scripts will be tested against a hand-crafted example or against the plan created by `release-begin-impl` Phase 2c in a later task. Scripts must handle `FileNotFoundError` gracefully.
6. **Run `dart fix --apply`** does not apply to Python scripts — run `python3 -m py_compile scripts/<file>.py` to check syntax after writing each file.
7. **Commit message format**: reference the task folder path as per CLAUDE.md conventions.
