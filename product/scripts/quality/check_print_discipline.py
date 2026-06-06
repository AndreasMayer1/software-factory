#!/usr/bin/env python3
"""
scripts/quality/check_print_discipline.py — G5 gate (REQ-PROC-051 AC-09).

Detects undisciplined print() usage in scripts/**/*.py.

Rules:
  - Non-CLI modules: any print() or pprint.pprint() call is a violation.
  - CLI modules (contain top-level `if __name__ == "__main__":` block):
    print() is allowed only if the module docstring (first triple-string at
    module level) contains the literal substring 'Output:' or 'Output contract:'.

A module is CLI iff it has a top-level `if __name__ == "__main__":` block.
sys.stderr.write() and sys.stdout.write() are NOT flagged.

Output contract:
  <path>:<line>: print() in non-CLI module
  <path>:<line>: CLI module uses print() but docstring missing 'Output:' contract
  ...
  G5 PASS — print() discipline satisfied across all scanned files.
  (or)
  G5 FAIL — N violation(s) found.

Exit codes:
  0  no violations
  1  one or more violations
  2  invocation error
"""

# tier: C  # one-shot CLI gate script; no in-tree Python imports

# Why: AST visitor chosen because it can distinguish between top-level
# if __name__ == "__main__": blocks and nested/quoted occurrences of that
# string, which a regex scan cannot reliably do.
# Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#F
# Tests: (smoke: verify against repo scripts/)

import ast
import sys
from pathlib import Path

# Why: 'Output:' substring chosen as the CLI contract marker because it is
# greppable, ruff-style, and forces explicit documentation of what the script
# prints. 'Output contract:' is also accepted as a more descriptive variant.
# The check is case-sensitive to avoid accidental matches on German 'output'
# (Ausgabe) or other partial words. Both variants are checked.
# Source: plans_and_protocols/2026-05-17_01_plan_tooling-mechanism.md#F
_OUTPUT_MARKERS = ("Output:", "Output contract:")

# Names considered equivalent to print() for discipline purposes.
# pprint.pprint produces unstructured output for human consumption, same as print.
_PRINT_LIKE = {"print"}  # pprint.pprint detected separately via attribute check


def _has_main_block(tree: ast.Module) -> bool:
    """Return True if the module has a top-level if __name__ == '__main__': block."""
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        # Pattern: if __name__ == "__main__":
        if (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value == "__main__"
        ):
            return True
    return False


def _get_module_docstring(tree: ast.Module) -> str:
    """Return the first triple-string at module level, or '' if none."""
    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        return tree.body[0].value.value
    return ""


def _has_output_contract(docstring: str) -> bool:
    """Return True if *docstring* contains an 'Output:' or 'Output contract:' marker."""
    return any(marker in docstring for marker in _OUTPUT_MARKERS)


def _is_print_call(node: ast.Call) -> bool:
    """Return True if *node* is a bare print() call."""
    return isinstance(node.func, ast.Name) and node.func.id in _PRINT_LIKE


def _is_pprint_call(node: ast.Call) -> bool:
    """Return True if *node* is pprint.pprint(...) or pprint(...) after 'from pprint import pprint'."""
    func = node.func
    if isinstance(func, ast.Attribute):
        # pprint.pprint(...)
        return (
            isinstance(func.value, ast.Name)
            and func.value.id == "pprint"
            and func.attr == "pprint"
        )
    # Bare pprint(...) — handled by _is_print_call if imported as print alias;
    # the gate flags pprint.pprint attribute calls; bare `pprint()` would only
    # appear if the user does `from pprint import pprint` and then calls it —
    # in that case it appears as a Name node, not an Attribute. We flag it
    # via _PRINT_LIKE by checking func.id == "pprint" too.
    if isinstance(func, ast.Name):
        return func.id == "pprint"
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

    is_cli = _has_main_block(tree)
    docstring = _get_module_docstring(tree)
    has_contract = _has_output_contract(docstring)

    findings: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        is_print = _is_print_call(node) or _is_pprint_call(node)
        if not is_print:
            continue

        line = getattr(node, "lineno", 0)

        if not is_cli:
            findings.append((line, "print() in non-CLI module"))
        elif not has_contract:
            findings.append(
                (
                    line,
                    "CLI module uses print() but docstring missing 'Output:' contract",
                )
            )

    return findings


def main() -> None:
    """Entry point — scan scripts/**/*.py and report findings."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    scripts_dir = repo_root / "scripts"

    if not scripts_dir.is_dir():
        print(f"ERROR: scripts/ directory not found at {scripts_dir}", file=sys.stderr)
        sys.exit(2)

    py_files = sorted(scripts_dir.rglob("*.py"))
    total_violations = 0

    for py_file in py_files:
        if "__pycache__" in py_file.parts or ".venv" in py_file.parts:
            continue

        rel = py_file.relative_to(repo_root)
        findings = check_file(py_file)

        for line_no, message in findings:
            print(f"{rel}:{line_no}: {message}")
            total_violations += 1

    print()
    if total_violations == 0:
        print("G5 PASS — print() discipline satisfied across all scanned files.")
        sys.exit(0)
    else:
        print(f"G5 FAIL — {total_violations} violation(s) found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
