#!/usr/bin/env python3
"""
scripts/quality/check_no_handrolled_yaml.py — G4 gate (REQ-PROC-051 AC-01).

Detects hand-rolled YAML-frontmatter parsers in scripts/**/*.py via AST
inspection and flags them. Every call site should instead import from
scripts/util/yaml_frontmatter.py (the centralized helper).

Output contract:
  <path>:<line>: hand-rolled YAML-frontmatter parser pattern
  ...
  G4 PASS — no hand-rolled YAML frontmatter parsers found.
  (or)
  G4 FAIL — N file(s) contain hand-rolled YAML frontmatter patterns.
  Migrate these to scripts/util/yaml_frontmatter.py (TASK-PROC-051-04).

Exit codes:
  0  no violations
  1  one or more violations
  2  invocation error

NOTE: this gate is EXPECTED to fail on develop until TASK-PROC-051-04 lands
(the compliance / cleanup task). The failing sites are:
  - scripts/automation/orchestrate.py
  - scripts/artifacts/generate_status_overview.py
  - scripts/artifacts/generate_id_registry.py
  - scripts/requirements/reconcile_dependencies.py
"""

# tier: B  # G4 gate script — invoked by scripts/quality/check_python_gates.sh; CI surface, no library callers

# Why: AST visitor chosen over grep/regex because raw string comparisons would
# hit false positives in docstrings and comments that contain '---'. AST
# restricts detection to actual code — string literals in Compare nodes and
# Name nodes for boolean flags — eliminating that entire class of false positives.
# Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#E
# Tests: (smoke: this gate must fail on orchestrate.py and pass on yaml_frontmatter.py)

import ast
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Allow-list — modules exempt from G4.
# Justification: yaml_frontmatter.py IS the central helper; the hand-rolled
# boundary detection inside it IS the implementation, not a violation.
# Using a module-path constant (not inline suppression) so a typo cannot
# silently allow an extra file — a wrong path in this list is simply unused.
# ---------------------------------------------------------------------------
ALLOW_LIST: list[str] = [
    "scripts/util/yaml_frontmatter.py",
]

# ---------------------------------------------------------------------------
# MISSING_TIER_SEVERITY — controls gate behavior for unannotated modules.
# Why: flip to "error" in TASK-PROC-051-04 once all scripts/ modules carry a
# # tier: header. Until then, missing-tier is a WARNING so develop is not
# blocked while annotation rolls out.
# Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#C
# ---------------------------------------------------------------------------
MISSING_TIER_SEVERITY = "warning"

# Names of boolean flag variables that signal hand-rolled frontmatter parsing
_FM_FLAG_NAMES = {"in_frontmatter", "in_fm", "frontmatter_started"}

# The YAML-delimiter sentinel string this gate watches for
_FM_SENTINEL = "---"


class _HandrolledYamlVisitor(ast.NodeVisitor):
    """AST visitor that detects the two-signature hand-rolled YAML pattern.

    A function (or module-level scope) is flagged when it contains BOTH:

    Signature 1 — a string-literal comparison against '---':
        Compare(left=..., ops=[Eq], comparators=[Constant('---')])

    Signature 2 — either:
        (a) a boolean local named in_frontmatter / in_fm / frontmatter_started, or
        (b) a split(":", ...) call on a stripped line within the same scope.

    Why: the two-signature requirement prevents flagging innocuous code that
    happens to compare to '---' (e.g. markdown separator rendering). Both
    signatures must co-occur in the same function scope to constitute the
    classic hand-rolled-frontmatter pattern.
    Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#E
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.findings: list[tuple[int, str]] = []

    # ------------------------------------------------------------------
    # Helpers that analyse a list of statements (function body or module)
    # ------------------------------------------------------------------

    def _has_sentinel_compare(self, nodes: list[ast.stmt]) -> int | None:
        """Return line number of first Compare(... == '---') in *nodes*, or None."""
        for node in ast.walk(ast.Module(body=nodes, type_ignores=[])):
            if isinstance(node, ast.Compare):
                for comp in node.comparators:
                    if isinstance(comp, ast.Constant) and comp.value == _FM_SENTINEL:
                        return getattr(node, "lineno", None)
        return None

    def _has_fm_flag(self, nodes: list[ast.stmt]) -> bool:
        """Return True if any assignment target uses a known FM-flag name."""
        for node in ast.walk(ast.Module(body=nodes, type_ignores=[])):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in _FM_FLAG_NAMES:
                        return True
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in _FM_FLAG_NAMES:
                return True
        return False

    def _has_split_colon(self, nodes: list[ast.stmt]) -> bool:
        """Return True if any Call node is .split(":", ...) in *nodes*."""
        for node in ast.walk(ast.Module(body=nodes, type_ignores=[])):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "split"):
                continue
            if (
                node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.startswith(":")
            ):
                return True
        return False

    def _check_scope(self, body: list[ast.stmt]) -> None:
        """Inspect a function (or module) body for the two-signature pattern."""
        sentinel_line = self._has_sentinel_compare(body)
        if sentinel_line is None:
            return  # signature 1 absent — skip

        sig2 = self._has_fm_flag(body) or self._has_split_colon(body)
        if sig2:
            self.findings.append(
                (sentinel_line, "hand-rolled YAML-frontmatter parser pattern")
            )

    # ------------------------------------------------------------------
    # Visitor entry points
    # ------------------------------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_scope(node.body)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_scope(node.body)
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module) -> None:
        # Also check module-level code (e.g. top-level loops outside functions)
        self._check_scope(node.body)
        self.generic_visit(node)


def _is_allowed(path: Path) -> bool:
    """Return True if *path* is in the G4 allow-list."""
    path_str = str(path)
    for allowed in ALLOW_LIST:
        if path_str.endswith(allowed) or path_str == allowed:
            return True
    return False


def check_file(path: Path) -> list[tuple[int, str]]:
    """Return list of (line, message) findings for *path*."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [(0, f"cannot read file: {exc}")]

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [(getattr(exc, "lineno", 0) or 0, f"syntax error: {exc.msg}")]

    visitor = _HandrolledYamlVisitor(str(path))
    visitor.visit(tree)
    return visitor.findings


def main() -> None:
    """Entry point — scan scripts/**/*.py and report findings."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    scripts_dir = repo_root / "scripts"

    if not scripts_dir.is_dir():
        print(f"ERROR: scripts/ directory not found at {scripts_dir}", file=sys.stderr)
        sys.exit(2)

    py_files = sorted(scripts_dir.rglob("*.py"))
    total_violations = 0
    failing_files = 0

    for py_file in py_files:
        # Skip __pycache__ and .venv
        if "__pycache__" in py_file.parts or ".venv" in py_file.parts:
            continue

        if _is_allowed(py_file):
            continue

        rel = py_file.relative_to(repo_root)
        findings = check_file(py_file)

        if findings:
            failing_files += 1
            for line_no, message in findings:
                print(f"{rel}:{line_no}: {message}")
            total_violations += len(findings)

    print()
    if total_violations == 0:
        print("G4 PASS — no hand-rolled YAML frontmatter parsers found.")
        sys.exit(0)
    else:
        print(
            f"G4 FAIL — {failing_files} file(s) contain hand-rolled YAML frontmatter patterns."
        )
        print("Migrate these to scripts/util/yaml_frontmatter.py (TASK-PROC-051-04).")
        sys.exit(1)


if __name__ == "__main__":
    main()
