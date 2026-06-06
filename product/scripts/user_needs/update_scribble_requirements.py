#!/usr/bin/env python3
"""
update_scribble_requirements.py

Discovers contributing_requirements (primary + cross-cutting) and
participating_flows for a scribble from its feature_path and the requirements
matrix, then writes them into the scribble's metadata.yaml.

Output:
    Writes contributing_requirements and participating_flows into metadata.yaml,
    normalising the legacy ``requirement:`` scalar key to an array. Prints a
    one-line summary to stdout: "DONE (wrote): primary=... cross_cutting=... flows=... lint=OK"

Usage:
    python3 scripts/user_needs/update_scribble_requirements.py <path/to/metadata.yaml|dir>
    python3 scripts/user_needs/update_scribble_requirements.py --dry-run <path>
    python3 scripts/user_needs/update_scribble_requirements.py --lint-only <path>

Exits:
    0  success — fields written, lint passed
    1  error   — missing feature_path, lint failed, or file not found
    2  ambiguous — partial write done, needs human review
"""

# tier: B  # invoked by ui-scribble-generator; logic exceeds 100-SLOC Tier C limit

from __future__ import annotations

import argparse
import logging
import os
import sys
import tempfile
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.  Same pattern as generate_status_overview.py.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
    read_frontmatter,
)

LOG = logging.getLogger(__name__)

FUNCTIONAL_REQ_ROOT = "requirements_tasks/functional"


@dataclass(frozen=True)
class RequirementFields:
    """Relevant fields extracted from a requirement's YAML frontmatter."""

    req_id: str
    feature_path: str
    flow_ids: tuple[str, ...]  # from user_needs.implements_flows[].id


@dataclass
class DiscoveryResult:
    """Result of the primary-requirement discovery pass."""

    primary: RequirementFields | None
    is_ambiguous: bool = False
    ambiguity_reason: str = ""


def find_project_root(start: Path) -> Path:
    """Walk up from *start* to find the directory containing requirements_tasks/."""
    current = start.resolve()
    while current != current.parent:
        if (current / "requirements_tasks").is_dir():
            return current
        current = current.parent
    raise RuntimeError(f"Could not find project root from {start}")


def load_all_requirements(root: Path) -> list[RequirementFields]:
    """Parse all requirements.md files under requirements_tasks/functional/."""
    functional = root / FUNCTIONAL_REQ_ROOT
    if not functional.is_dir():
        return []
    results: list[RequirementFields] = []
    for path in sorted(functional.rglob("requirements.md")):
        fields = _parse_req_fields(path)
        if fields is not None:
            results.append(fields)
    return results


def _parse_req_fields(path: Path) -> RequirementFields | None:
    """Parse *path* (requirements.md with YAML frontmatter); return fields or None."""
    try:
        doc = read_frontmatter(path)
    except FrontmatterError as exc:
        LOG.warning("Cannot parse frontmatter in %s: %s", path, exc)
        return None
    meta = doc.metadata
    req_id = str(meta.get("id", ""))
    if not req_id:
        return None
    feature_path = str(meta.get("feature_path") or "")
    flow_ids = tuple(_extract_flow_ids(meta))
    return RequirementFields(req_id=req_id, feature_path=feature_path, flow_ids=flow_ids)


def _extract_flow_ids(meta: CommentedMap) -> list[str]:
    """Extract flow IDs from requirement metadata's user_needs.implements_flows."""
    user_needs = meta.get("user_needs") or {}
    if not isinstance(user_needs, dict):
        return []
    implements_flows = user_needs.get("implements_flows") or []
    return [
        str(entry["id"])
        for entry in implements_flows
        if isinstance(entry, dict) and "id" in entry
    ]


def discover_primary(
    feature_path: str,
    reqs: list[RequirementFields],
) -> DiscoveryResult:
    """Find the primary requirement for *feature_path*.

    Returns a DiscoveryResult with the primary candidate and ambiguity information.
    """
    candidates = [r for r in reqs if r.feature_path == feature_path]
    if not candidates:
        return DiscoveryResult(
            primary=None,
            is_ambiguous=True,
            ambiguity_reason=f"No requirement found with feature_path={feature_path!r}",
        )
    if len(candidates) > 1:
        ids = ", ".join(r.req_id for r in candidates)
        return DiscoveryResult(
            primary=candidates[0],
            is_ambiguous=True,
            ambiguity_reason=(
                f"Multiple requirements with feature_path={feature_path!r}:"
                f" {ids} — using first"
            ),
        )
    return DiscoveryResult(primary=candidates[0])


def discover_cross_cutting(
    primary: RequirementFields,
    reqs: list[RequirementFields],
) -> list[str]:
    """Return IDs of requirements sharing ≥1 flow with *primary* (UI-scope heuristic).

    UI-scope heuristic: a candidate requirement must have feature_path set (non-empty),
    indicating it governs a named feature area with Presentation-layer scope.
    """
    primary_flows = set(primary.flow_ids)
    cross_cutting: list[str] = []
    for req in reqs:
        if req.req_id == primary.req_id:
            continue
        if not req.feature_path:  # no feature_path → not UI-scoped
            continue
        if set(req.flow_ids) & primary_flows:
            cross_cutting.append(req.req_id)
    return sorted(set(cross_cutting))


def check_consistency(scribble_fp: str, primary: RequirementFields | None) -> bool:
    """Check that the primary requirement's feature_path matches the scribble's.

    Returns True if consistent; prints an error to stderr and returns False on mismatch.
    """
    if primary is None:
        return False
    if primary.feature_path != scribble_fp:
        print(
            f"LINT ERROR: primary requirement {primary.req_id} has"
            f" feature_path={primary.feature_path!r}"
            f" but scribble has feature_path={scribble_fp!r}",
            file=sys.stderr,
        )
        return False
    return True


def read_plain_yaml(path: Path) -> CommentedMap:
    """Read a pure-YAML file (no '---' frontmatter markers) into a CommentedMap.

    Uses ruamel.yaml for round-trip comment preservation. This is NOT a
    hand-rolled YAML parser — the G4 restriction targets frontmatter boundary
    detection; plain-YAML files like scribble metadata.yaml use the ruamel API.
    """
    yaml = _make_yaml()
    text = path.read_text(encoding="utf-8")
    result = yaml.load(StringIO(text))
    if not isinstance(result, CommentedMap):
        return CommentedMap()
    return result


def write_plain_yaml(path: Path, data: CommentedMap) -> None:
    """Write *data* to *path* as plain YAML, atomically (tmp → fsync → rename)."""
    yaml = _make_yaml()
    buf = StringIO()
    yaml.dump(data, buf)
    content = buf.getvalue()

    dir_ = path.parent
    fd, tmp_str = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    tmp = Path(tmp_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        tmp.rename(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _make_yaml() -> YAML:
    """Return a ruamel YAML instance configured for round-trip with comment preservation."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    return yaml


def apply_updates(
    path: Path,
    contributing: list[str],
    flows: list[str],
    is_ambiguous: bool,
    ambiguity_reason: str,
    *,
    dry_run: bool,
) -> None:
    """Write *contributing* and *flows* into the scribble metadata at *path*.

    Normalises the legacy ``requirement:`` scalar key to ``contributing_requirements``.
    On dry_run=True, parses and validates but does not write.
    """
    data = read_plain_yaml(path)

    if "requirement" in data:
        data.pop("requirement")

    contrib_seq = CommentedSeq(contributing)
    contrib_seq.fa.set_flow_style()
    data["contributing_requirements"] = contrib_seq

    flows_seq = CommentedSeq(flows)
    flows_seq.fa.set_flow_style()
    data["participating_flows"] = flows_seq

    if is_ambiguous:
        data.yaml_set_comment_before_after_key(
            "contributing_requirements",
            before=f"AMBIGUOUS: {ambiguity_reason} — needs human review",
        )

    if not dry_run:
        write_plain_yaml(path, data)


def resolve_metadata_path(arg: str) -> Path:
    """Return the metadata.yaml path from a file or directory argument."""
    p = Path(arg)
    return p / "metadata.yaml" if p.is_dir() else p


def main() -> int:
    """CLI entry point; returns exit code (0 OK, 1 error, 2 ambiguous)."""
    parser = argparse.ArgumentParser(
        description=(
            "Discover contributing_requirements and participating_flows "
            "for a scribble metadata.yaml."
        )
    )
    parser.add_argument(
        "metadata",
        help="Path to scribble metadata.yaml or a scribble directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without modifying the file",
    )
    parser.add_argument(
        "--lint-only",
        action="store_true",
        help="Only check consistency; do not write any fields",
    )
    args = parser.parse_args()

    metadata_path = resolve_metadata_path(args.metadata)
    if not metadata_path.exists():
        print(f"ERROR: {metadata_path} not found", file=sys.stderr)
        return 1

    try:
        root = find_project_root(metadata_path)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    scribble_data = read_plain_yaml(metadata_path)
    feature_path = str(scribble_data.get("feature_path") or "")
    if not feature_path:
        print(f"ERROR: No feature_path field in {metadata_path}", file=sys.stderr)
        return 1

    all_reqs = load_all_requirements(root)
    discovery = discover_primary(feature_path, all_reqs)

    if not check_consistency(feature_path, discovery.primary):
        return 1

    participating_flows: list[str] = []
    cross_cutting: list[str] = []
    if discovery.primary is not None:
        participating_flows = sorted(set(discovery.primary.flow_ids))
        cross_cutting = discover_cross_cutting(discovery.primary, all_reqs)

    contributing = (
        [discovery.primary.req_id, *cross_cutting]
        if discovery.primary is not None
        else []
    )

    if not args.lint_only:
        apply_updates(
            metadata_path,
            contributing,
            participating_flows,
            discovery.is_ambiguous,
            discovery.ambiguity_reason,
            dry_run=args.dry_run,
        )

    action = "dry-run" if args.dry_run else "lint-only" if args.lint_only else "wrote"
    primary_id = discovery.primary.req_id if discovery.primary else "None"
    print(
        f"DONE ({action}): primary={primary_id}"
        f" cross_cutting={cross_cutting}"
        f" flows={participating_flows}"
        f" lint=OK"
    )

    if discovery.is_ambiguous:
        print(f"AMBIGUOUS: {discovery.ambiguity_reason}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
