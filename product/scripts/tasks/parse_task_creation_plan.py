#!/usr/bin/env python3
"""Parse task_creation_plan.md into a structured dictionary / JSON.

This module is primarily a shared library imported by other pipeline scripts.
A CLI entry point is provided for debugging.

Usage:
    python3 scripts/parse_task_creation_plan.py <plan_path>
    python3 scripts/parse_task_creation_plan.py --plan <plan_path> [--version-id PLAN-X-vN]
    python3 scripts/parse_task_creation_plan.py <plan_path> --package "QR Transfer Send"
    python3 scripts/parse_task_creation_plan.py <plan_path> --next-uncreated --field task_type

Exit codes:
    0  success — JSON written to stdout
    1  file not found or unreadable
    2  parse error (malformed frontmatter or YAML block)
    3  --next-uncreated: all tasks have been created

Output:
    Prints a JSON document describing the parsed plan to stdout. --next-uncreated prints the next batch of uncreated tasks as JSON; exit 3 if all tasks have been created.
"""

# tier: C  # one-shot CLI task tool; no in-tree Python imports

import argparse
import json
import re
import sys
from io import StringIO
from pathlib import Path
from typing import Any, Optional, cast

from ruamel.yaml import YAML

# Make scripts/util importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation
    _split_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent.parent

VALID_EFFORTS = {"XS", "S", "M", "L", "XL"}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PlanParseError(ValueError):
    pass


class PlanArchivedError(ValueError):
    pass


# ---------------------------------------------------------------------------
# YAML parsing — delegates to scripts/util/yaml_frontmatter (REQ-PROC-051 AC-08)
# ---------------------------------------------------------------------------


def _fix_orphan_list_items(yaml_text: str) -> str:
    """Re-indent col-0 list items under their last-seen nested-key parent.

    Why: textwrap.dedent inside triple-quoted f-strings with embedded list
    items can produce frontmatter where list items sit at col 0 instead of
    under their parent key. This is invalid YAML per ruamel but historically
    accepted by the lenient hand-rolled parser. We restore a valid form by
    detecting the parent's last column and re-indenting orphan items.
    """
    lines = yaml_text.split("\n")
    out: list[str] = []
    last_key_indent = -1
    for raw in lines:
        stripped = raw.strip()
        # Track the most-recent key-with-empty-value (likely a list parent)
        ind = len(raw) - len(raw.lstrip())
        if stripped and not stripped.startswith("- ") and stripped.endswith(":"):
            last_key_indent = ind
        if raw.startswith("- ") and last_key_indent >= 0:
            # Orphan item at col 0 — re-indent under last parent (+2)
            out.append(" " * (last_key_indent + 2) + raw)
        else:
            out.append(raw)
    return "\n".join(out)


def _load_yaml_text(yaml_text: str) -> Optional[dict[str, Any]]:
    """Parse a YAML string into a dict, tolerating duplicate keys."""
    if not yaml_text.strip():
        return None
    # Pre-process: fix textwrap-dedent-broken orphan list items
    yaml_text = _fix_orphan_list_items(yaml_text)
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
    try:
        result = yaml.load(StringIO(yaml_text))
    except Exception:
        return None
    if result is None or not isinstance(result, dict):
        return None
    return dict(result)


def _parse_frontmatter(content: str) -> Optional[dict[str, Any]]:
    """Extract top-level YAML frontmatter from markdown content.

    Pre-step: strip common indent from the document so docs produced by
    textwrap.dedent inside triple-quoted f-strings (where an embedded list item
    reduces dedent's common-indent to 0) still parse correctly. Then delegate
    YAML parsing to ruamel via _load_yaml_text.
    """
    if content.startswith("﻿"):
        content = content[1:]

    lines = content.split("\n")
    first_line = lines[0] if lines else ""

    # If the first non-empty line is an indented '---', dedent the whole doc by
    # that indent so the central splitter can recognise the boundary line.
    if first_line.strip() == "---" and first_line != "---":
        open_indent = len(first_line) - len(first_line.lstrip())
        prefix = " " * open_indent
        dedented: list[str] = []
        for line in lines:
            if line.startswith(prefix):
                dedented.append(line[open_indent:])
            else:
                # Preserve as-is (likely already at column 0 due to an embedded
                # list item that broke dedent's common-prefix detection).
                dedented.append(line)
        content = "\n".join(dedented)

    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml.strip():
        return None
    return _load_yaml_text(raw_yaml)


# ---------------------------------------------------------------------------
# Task YAML block parser
# ---------------------------------------------------------------------------

def _parse_yaml_block(block: str) -> dict[str, Any]:
    """Parse a fenced YAML block (content between ``` fences)."""
    if not block.strip():
        return {}
    yaml_inst = YAML()
    yaml_inst.preserve_quotes = True
    yaml_inst.allow_duplicate_keys = True
    try:
        result = yaml_inst.load(StringIO(block))
    except Exception as e:
        raise PlanParseError(f"Invalid YAML in task block: {e}") from e
    if result is None:
        return {}
    if not isinstance(result, dict):
        return {}
    return dict(result)


def _normalize_list_field(value: Any) -> list[str]:
    """Normalize a value that should be a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if item is not None]
    if isinstance(value, str):
        # May be inline list like "[A, B]"
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1]
            return [i.strip().strip("\"'") for i in inner.split(",") if i.strip()]
        if s:
            return [s]
    return []


# ---------------------------------------------------------------------------
# Version body extractor
# ---------------------------------------------------------------------------

def _extract_version_body(content: str, version_id: Optional[str]) -> str:
    """Select the correct version section of the plan body.

    If no '## Plan v' headings exist, returns the full body after frontmatter.
    If version_id given, finds that specific section.
    Otherwise, finds the latest non-archived version.
    """
    # Remove frontmatter block
    body = content
    fm_match = re.match(r"^---\n.*?\n---\n?", content, re.DOTALL)
    if fm_match:
        body = content[fm_match.end():]

    # Check if multi-version plan
    version_headings = re.findall(r"^## Plan v(\d+)", body, re.MULTILINE)
    if not version_headings:
        return body

    # Split into version sections
    parts = re.split(r"^(## Plan v\d+.*?)$", body, flags=re.MULTILINE)
    # parts: [pre, heading1, section1, heading2, section2, ...]
    versions: list[dict[str, Any]] = []
    i = 1
    while i + 1 < len(parts):
        heading = parts[i]
        section_body = parts[i + 1]
        v_match = re.search(r"v(\d+)", heading)
        v_num = int(v_match.group(1)) if v_match else 0

        # Extract plan_id from this section's fenced yaml block if present
        plan_id_match = re.search(r"```ya?ml\n(.*?)```", section_body, re.DOTALL)
        archived = False
        section_plan_id = ""
        if plan_id_match:
            try:
                section_fm = _parse_yaml_block(plan_id_match.group(1))
                archived = bool(section_fm.get("archived", False))
                section_plan_id = str(section_fm.get("plan_id", ""))
            except PlanParseError:
                pass

        versions.append({
            "v_num": v_num,
            "plan_id": section_plan_id,
            "body": heading + "\n" + section_body,
            "archived": archived,
        })
        i += 2

    if not versions:
        return body

    if version_id:
        for v in versions:
            if v["plan_id"] == version_id:
                return cast("str", v["body"])
        # Try matching by v_num suffix
        v_suffix = re.search(r"v(\d+)$", version_id)
        if v_suffix:
            v_num_target = int(v_suffix.group(1))
            for v in versions:
                if v["v_num"] == v_num_target:
                    return cast("str", v["body"])

    # Return latest non-archived version
    non_archived = [v for v in versions if not v["archived"]]
    if not non_archived:
        non_archived = versions  # fallback: use all if all archived

    latest = max(non_archived, key=lambda v: v["v_num"])
    return cast("str", latest["body"])


# ---------------------------------------------------------------------------
# Execution order parser
# ---------------------------------------------------------------------------

def _parse_execution_order(body: str) -> list[str]:
    """Extract package IDs from ## Execution Order section."""
    order_match = re.search(r"## Execution Order.*?\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
    if not order_match:
        return []

    section = order_match.group(1)
    # Match lines like: "1. Package Name" or "- Package Name"
    items = re.findall(r"^\s*(?:\d+\.|-)\s+(.+)$", section, re.MULTILINE)
    return [item.strip() for item in items if item.strip()]


# ---------------------------------------------------------------------------
# Heading walker — state machine
# ---------------------------------------------------------------------------

def _walk_headings(body: str) -> list[dict[str, Any]]:
    """Walk markdown headings to extract packages and tasks.

    State machine states:
      - 'root': outside any package section
      - 'package': inside a ### Package heading
      - 'task_open': inside a #### Task heading, before YAML block
      - 'task_yaml': collecting fenced YAML block lines
      - 'task_rationale': after YAML block, collecting prose
    """
    packages: list[dict[str, Any]] = []
    current_package: Optional[dict[str, Any]] = None
    current_task: Optional[dict[str, Any]] = None
    state = "root"
    yaml_lines: list[str] = []
    rationale_lines: list[str] = []

    lines = body.split("\n")

    def _finalize_task() -> None:
        nonlocal current_task, rationale_lines
        if current_task is not None and current_package is not None:
            if rationale_lines:
                current_task["rationale"] = "\n".join(rationale_lines).strip()
            current_package["tasks"].append(current_task)
            current_task = None
            rationale_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect fenced code blocks (``` or ```)
        if state == "task_yaml":
            # We're collecting the YAML fence — check for closing
            if stripped.startswith("```") or stripped.startswith("~~~"):
                # End of YAML fence
                yaml_content = "\n".join(yaml_lines)
                try:
                    task_data = _parse_yaml_block(yaml_content)
                except PlanParseError as e:
                    print(f"WARNING: {e}", file=sys.stderr)
                    task_data = {}

                if current_task is not None:
                    # Merge YAML data into task, preserving _entry_index
                    entry_index = current_task.get("_entry_index", 1)
                    heading_name = current_task.get("task_name", "")
                    current_task.update(task_data)
                    current_task["_entry_index"] = entry_index
                    # Use heading text as fallback for task_name
                    if not current_task.get("task_name"):
                        current_task["task_name"] = heading_name
                    # Normalize list fields
                    current_task["covers_acs"] = _normalize_list_field(
                        current_task.get("covers_acs")
                    )
                    current_task["after"] = _normalize_list_field(
                        current_task.get("after")
                    )
                    # Validate effort
                    effort = current_task.get("effort", "")
                    if effort and str(effort) not in VALID_EFFORTS:
                        print(
                            f"WARNING: Invalid effort '{effort}' in task "
                            f"'{current_task.get('task_name')}' — expected one of "
                            f"{sorted(VALID_EFFORTS)}",
                            file=sys.stderr,
                        )
                    # Normalize opus_recommended
                    current_task["opus_recommended"] = bool(
                        current_task.get("opus_recommended", False)
                    )

                yaml_lines = []
                state = "task_rationale"
            else:
                yaml_lines.append(line)
            continue

        # Check for package heading (###)
        pkg_match = re.match(r"^### (.+)$", stripped)
        task_match = re.match(r"^#### Task \d+[.:]\s*(.+)$", stripped)
        task_match_alt = re.match(r"^#### Task \d+$", stripped)

        # Higher-level headings close current task/package context
        if re.match(r"^## ", stripped) and not re.match(r"^### ", stripped):
            _finalize_task()
            current_package = None
            state = "root"
            continue

        if pkg_match:
            _finalize_task()
            pkg_name = pkg_match.group(1).strip()
            current_package = {"id": pkg_name, "name": pkg_name, "tasks": []}
            packages.append(current_package)
            state = "package"
            continue

        if task_match or task_match_alt:
            _finalize_task()
            if current_package is None:
                # Create implicit package
                current_package = {"id": "_ungrouped", "name": "_ungrouped", "tasks": []}
                packages.append(current_package)

            heading_text = (task_match.group(1).strip() if task_match else "")
            current_task = {
                "_entry_index": len(current_package["tasks"]) + 1,
                "task_name": heading_text,
                "covers_acs": [],
                "after": [],
                "opus_recommended": False,
            }
            state = "task_open"
            rationale_lines = []
            continue

        if state == "task_open":
            # Look for opening fenced YAML block
            if stripped.startswith("```yaml") or stripped.startswith("```yml"):
                yaml_lines = []
                state = "task_yaml"
                continue
            # Non-fence content while waiting for yaml — skip blank lines
            if stripped:
                # Could be rationale before yaml — treat as rationale
                rationale_lines.append(line)

        elif state == "task_rationale":
            # Collect rationale prose until next task/package/section heading
            if not (re.match(r"^#+\s", stripped)):
                rationale_lines.append(line)

    # Finalize last task
    _finalize_task()

    return packages


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_plan(plan_path: str, version_id: Optional[str] = None) -> dict[str, Any]:
    """Parse task_creation_plan.md and return structured dict.

    Raises:
        FileNotFoundError: if plan_path does not exist
        PlanArchivedError: if the plan is archived (and no version_id given)
        PlanParseError: if the file has malformed YAML
    """
    path = Path(plan_path)
    if not path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileNotFoundError(f"Cannot read plan file: {e}") from e

    frontmatter = _parse_frontmatter(content)
    if frontmatter is None:
        frontmatter = {}

    if frontmatter.get("status") == "archived" and version_id is None:
        raise PlanArchivedError(f"Plan at {plan_path} is archived")

    body = _extract_version_body(content, version_id)
    packages = _walk_headings(body)
    execution_order = _parse_execution_order(body)

    return {
        "frontmatter": frontmatter,
        "packages": packages,
        "execution_order": execution_order,
    }


def get_task_entry(
    plan: dict[str, Any],
    target_package: str,
    task_name: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Look up a specific task entry from a parsed plan.

    If task_name is None, returns the first task for the package.
    Returns None if not found.
    """
    for pkg in plan.get("packages", []):
        if pkg["id"] == target_package:
            if task_name is None:
                return pkg["tasks"][0] if pkg["tasks"] else None
            for task in pkg["tasks"]:
                if task.get("task_name") == task_name:
                    return cast("dict[str, Any] | None", task)
    return None


def get_package_tasks(plan: dict[str, Any], target_package: str) -> list[dict[str, Any]]:
    """Return all task entries for a given target_package."""
    for pkg in plan.get("packages", []):
        if pkg["id"] == target_package:
            return cast("list[dict[str, Any]]", pkg["tasks"])
    return []


def get_execution_order(plan: dict[str, Any]) -> list[str]:
    """Return package IDs in execution order from the ## Execution Order section."""
    return cast("list[str]", plan.get("execution_order", []))


# ---------------------------------------------------------------------------
# --next-uncreated helper
# ---------------------------------------------------------------------------

def _find_next_uncreated(plan: dict[str, Any], root: Path) -> Optional[dict[str, Any]]:
    """Find the first plan task not yet covered by a matching goal.md.

    Uses the same (target_package, parent_requirement, covers_acs) tuple match as
    _find_next_uncreated_package so that legacy tasks for the same package cannot
    produce false positives.

    Why: The previous package-name heuristic suppressed an entire package whenever any
    existing goal.md shared its target_package — legacy tasks completed before the plan
    was written triggered this false positive for Adaptive Scanner Settings and would have
    repeated for every subsequent package that had pre-existing tasks.
    Source: automation/pending_feedback/TASK-PROC-035-17/question.md
    """
    created_tasks = _load_all_created_tasks(root)

    for pkg in plan.get("packages", []):
        if pkg.get("id") == "_ungrouped" or not pkg.get("tasks"):
            continue
        for task in pkg["tasks"]:
            if not _is_task_created(task, created_tasks):
                return cast("dict[str, Any]", task)
    return None


# ---------------------------------------------------------------------------
# --next-uncreated-package helpers
# ---------------------------------------------------------------------------

def _load_all_created_tasks(root: Path) -> list[dict[str, Any]]:
    """Walk root for goal.md files and return list of parsed frontmatter dicts.

    Why: The --next-uncreated-package mode needs fine-grained matching by
    (target_package, parent_requirement, covers_acs) rather than package name
    alone. Loading all goal.md frontmatter once per invocation lets
    _is_task_created do exact tuple matching without repeated filesystem walks.
    Source: requirements_tasks/.../plans_and_protocols/2026-04-27_01_opus_impl_plan.md#agent-a
    """
    results: list[dict[str, Any]] = []
    for goal_path in root.rglob("goal.md"):
        try:
            content = goal_path.read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            if fm and isinstance(fm, dict):
                results.append(fm)
        except Exception:
            # Skip files that fail to parse — non-fatal
            continue
    return results


def _is_task_created(task_entry: dict[str, Any], created_tasks: list[dict[str, Any]]) -> bool:
    """Check if a plan task entry matches any created goal.md by exact tuple.

    Match tuple: (target_package, req_id/parent_requirement, set(covers_acs)).
    - Plan entry uses `req_id`; goal.md uses `parent_requirement` — both handled.
    - `covers_acs` in plan vs `covers.acceptance_criteria` in goal.md (nested dict).

    Why: Counting goal.md files by target_package alone causes false positives —
    unrelated test/bugfix tasks for the same package would be counted as coverage.
    The three-field tuple uniquely identifies a planned impl task.
    Source: requirements_tasks/.../plans_and_protocols/2026-04-27_01_opus_impl_plan.md#already-created-matching-strategy
    """
    plan_package = str(task_entry.get("target_package", "")).strip()
    # req_id in plan entries; parent_requirement in goal.md frontmatter
    plan_req = str(task_entry.get("req_id", "")).strip()
    plan_acs = set(_normalize_list_field(task_entry.get("covers_acs")))

    for fm in created_tasks:
        created_package = str(fm.get("target_package", "")).strip()
        created_req = str(fm.get("parent_requirement", fm.get("req_id", ""))).strip()

        # covers.acceptance_criteria is nested in goal.md frontmatter
        covers_raw = fm.get("covers")
        if isinstance(covers_raw, dict):
            created_acs = set(_normalize_list_field(covers_raw.get("acceptance_criteria")))
        else:
            created_acs = set()

        if (created_package == plan_package
                and created_req == plan_req
                and created_acs == plan_acs):
            return True
    return False


def _find_next_uncreated_package(
    plan: dict[str, Any],
    root: Path,
    max_tasks: int = 6,
) -> Optional[list[dict[str, Any]]]:
    """Return up to max_tasks uncreated tasks from the first uncreated package.

    Algorithm:
    1. Load all created task frontmatter from goal.md files under root.
    2. Walk plan["packages"] in document order.
    3. For each pkg_block (skip empty or _ungrouped):
       - Collect tasks where _is_task_created returns False.
       - If any uncreated: return up to max_tasks of them (preserve plan order).
    4. Return None when all packages are fully created.

    Why: Batch creation — one full package per orch session — keeps context
    focused while surfacing all pending tasks for a package up-front.
    Cap at max_tasks (default 6) prevents context blowup.
    Source: requirements_tasks/.../plans_and_protocols/2026-04-27_01_opus_impl_plan.md#agent-a
    """
    created_tasks = _load_all_created_tasks(root)

    for pkg_block in plan.get("packages", []):
        if not pkg_block.get("tasks"):
            continue
        if pkg_block.get("id") == "_ungrouped":
            continue

        uncreated = [
            t for t in pkg_block["tasks"]
            if not _is_task_created(t, created_tasks)
        ]
        if uncreated:
            return uncreated[:max_tasks]

    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Parse task_creation_plan.md -> JSON")
    parser.add_argument("plan_path", nargs="?", help="Path to task_creation_plan.md")
    parser.add_argument("--plan", dest="plan_path_flag", metavar="PATH",
                        help="Alternative to positional argument")
    parser.add_argument("--version-id", metavar="PLAN-X-vN",
                        help="Specific plan version to extract")
    parser.add_argument("--package", metavar="PKG-ID",
                        help="Filter output to one package's tasks")
    parser.add_argument("--next-uncreated", action="store_true",
                        help="Return first task entry with no matching goal.md yet")
    parser.add_argument("--next-uncreated-package", action="store_true",
                        help=(
                            "Return all uncreated tasks for the first uncreated package "
                            "as a JSON array (capped at 6). Exit 0 with JSON array; "
                            "exit 3 when all packages created. Ignores --field and --format."
                        ))
    parser.add_argument("--field", metavar="FIELD_NAME",
                        help="Print just one field value from the task entry")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="Output format (default: json)")
    args = parser.parse_args()

    # Resolve plan path from positional or --plan
    plan_path = args.plan_path or args.plan_path_flag
    if not plan_path:
        print("ERROR: plan_path is required (positional or --plan)", file=sys.stderr)
        sys.exit(1)

    try:
        result = parse_plan(plan_path, args.version_id)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except (PlanParseError, PlanArchivedError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    # --next-uncreated-package mode (takes precedence over --next-uncreated)
    if args.next_uncreated_package:
        batch = _find_next_uncreated_package(
            result, PROJECT_ROOT / "requirements_tasks"
        )
        if batch is None:
            # All packages already created
            sys.exit(3)
        print(json.dumps(batch, indent=2, default=str))
        sys.exit(0)

    # --next-uncreated mode
    if args.next_uncreated:
        task_entry = _find_next_uncreated(
            result, PROJECT_ROOT / "requirements_tasks"
        )
        if task_entry is None:
            # All tasks have been created
            sys.exit(3)
        if args.field:
            val = task_entry.get(args.field)
            if val is None:
                print("", end="")
            elif isinstance(val, (list, dict)):
                print(json.dumps(val))
            else:
                print(str(val))
        else:
            if args.format == "json":
                print(json.dumps(task_entry, indent=2, default=str))
            else:
                for k, v in task_entry.items():
                    print(f"{k}: {v}")
        sys.exit(0)

    # --package filter
    if args.package:
        tasks = get_package_tasks(result, args.package)
        output: Any = {"package": args.package, "tasks": tasks}
    else:
        output = result

    if args.format == "json":
        print(json.dumps(output, indent=2, default=str))
    else:
        # Text format: simple key: value per task
        for pkg in output.get("packages", [output] if "tasks" in output else []):
            print(f"Package: {pkg.get('id', '')}")
            for task in pkg.get("tasks", []):
                for k, v in task.items():
                    print(f"  {k}: {v}")
            print()

    sys.exit(0)


if __name__ == "__main__":
    main()
