"""Test-smell gate (REQ-PROC-046, DCM-replacement).

Replaces DCM rules `missing-test-assertion`, `avoid-empty-test-groups`, and
`prefer-test-matchers`. Walks `test/unit/`, `test/widget/`, and
`integration_test/`, parses each `*_test.dart` file with a balanced-brace
state machine, and reports three sub-checks:

  1. Missing assertion — a `test(...)` / `testWidgets(...)` body that
     contains no assertion-style call (`expect(`, `expectLater(`,
     `verify(`, `expectAsync*(`, `tester.ensureSemantics(`).
  2. Empty group — a `group(...)` body that contains zero
     `test(` / `testWidgets(` / `group(` calls.
  3. Literal expect — `expect(x.length, N)` flagged in favour of
     `expect(x, hasLength(N))`. Heuristic.

Output:
    Pass — single line "PASS: ..." on stdout, exit 0.
    Fail — one line per finding, then a summary, exit 1.
"""

# tier: B

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXCLUDE_FILE = Path(__file__).resolve().parent / "exclusions.txt"

ASSERTION_RE = re.compile(
    r"(?:^|[^A-Za-z0-9_])"
    r"(?:expect|expectLater|verify|expectAsync[0-9]?)\("
    r"|tester\.ensureSemantics\("
)
TEST_CALL_RE = re.compile(
    r"(?:^|[^A-Za-z0-9_])(?:test|testWidgets|group)\("
)
LITERAL_EXPECT_RE = re.compile(
    r"expect\(\s*[^,]+\.length\s*,\s*[0-9]+"
)

# Three callable names we open a balanced-brace scan for.
OPENER_RES = {
    "test": re.compile(r"(?:^|[^A-Za-z0-9_])test\s*\("),
    "testWidgets": re.compile(r"(?:^|[^A-Za-z0-9_])testWidgets\s*\("),
    "group": re.compile(r"(?:^|[^A-Za-z0-9_])group\s*\("),
}


def load_exclude_patterns(path: Path) -> list[str]:
    if not path.exists():
        return []
    patterns: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    return patterns


def is_excluded(rel_path: str, patterns: list[str]) -> bool:
    return any(p in rel_path for p in patterns)


def strip_comments_and_strings(src: str) -> str:
    """Return `src` with comments and string literals replaced by spaces so
    brace counting is not fooled by `{` inside strings.

    Length is preserved so byte offsets remain valid against the original.
    """
    out = []
    i = 0
    n = len(src)
    in_line_comment = False
    in_block_comment = False
    in_string: str | None = None  # quote character that opened the string
    while i < n:
        ch = src[i]
        nxt = src[i + 1] if i + 1 < n else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append(ch)
            else:
                out.append(" ")
            i += 1
            continue
        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                out.append("  ")
                i += 2
                continue
            out.append(" " if ch != "\n" else "\n")
            i += 1
            continue
        if in_string is not None:
            if ch == "\\" and nxt:
                out.append("  ")
                i += 2
                continue
            if ch == in_string:
                in_string = None
                out.append(" ")
                i += 1
                continue
            out.append(" " if ch != "\n" else "\n")
            i += 1
            continue

        if ch == "/" and nxt == "/":
            in_line_comment = True
            out.append("  ")
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            out.append("  ")
            i += 2
            continue
        if ch in ("'", '"'):
            in_string = ch
            out.append(" ")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def find_block_end(stripped: str, start: int) -> int:
    """Given a position `start` at an opening `{`, return the index of the
    matching close brace. Returns -1 if unbalanced.
    """
    depth = 0
    n = len(stripped)
    i = start
    while i < n:
        ch = stripped[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def line_of(offset: int, line_starts: list[int]) -> int:
    # Binary search the line index.
    lo, hi = 0, len(line_starts) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if line_starts[mid] <= offset:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi + 1  # 1-indexed


def compute_line_starts(src: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(src):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def scan_blocks(
    raw: str, opener_name: str
) -> list[tuple[int, str]]:
    """Return a list of (start_line, body_text) for each balanced block
    opened by `opener_name(...) { ... }`. Bodies use the *stripped* source
    (comments/strings replaced) so downstream regex scans are safe.

    Arrow-bodies (`=> ...;`) are returned with an empty body string so the
    assertion check fires correctly on them.
    """
    stripped = strip_comments_and_strings(raw)
    line_starts = compute_line_starts(raw)
    opener_re = OPENER_RES[opener_name]
    results: list[tuple[int, str]] = []
    pos = 0
    while pos < len(stripped):
        m = opener_re.search(stripped, pos)
        if not m:
            break
        # The match's first character may be a preceding non-identifier;
        # locate the opener-name start.
        name_start = stripped.find(opener_name, m.start(), m.end())
        if name_start == -1:
            name_start = m.start()
        # Find the matching close-paren of the call.
        paren_open = stripped.find("(", name_start)
        if paren_open == -1:
            pos = m.end()
            continue
        depth = 0
        i = paren_open
        while i < len(stripped):
            c = stripped[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        if i >= len(stripped):
            break
        after_paren = i + 1
        # Skip whitespace.
        j = after_paren
        while j < len(stripped) and stripped[j] in " \t\n\r":
            j += 1
        if j >= len(stripped):
            break
        if stripped[j] == "{":
            block_end = find_block_end(stripped, j)
            if block_end == -1:
                break
            body = stripped[j + 1 : block_end]
            results.append((line_of(name_start, line_starts), body))
            pos = block_end + 1
        elif stripped[j : j + 2] == "=>":
            # Arrow body — find terminating ';' at the same nesting level.
            k = j + 2
            depth = 0
            while k < len(stripped):
                c = stripped[k]
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                elif c == ";" and depth == 0:
                    break
                k += 1
            body = stripped[j + 2 : k]
            results.append((line_of(name_start, line_starts), body))
            pos = k + 1
        else:
            pos = j
    return results


def check_file(
    file_path: Path, rel_path: str
) -> int:
    raw = file_path.read_text(encoding="utf-8", errors="replace")
    findings = 0

    # Sub-check 1: missing assertion.
    for opener in ("test", "testWidgets"):
        for line_no, body in scan_blocks(raw, opener):
            if ASSERTION_RE.search(body):
                continue
            sys.stdout.write(
                f"{rel_path}:{line_no}: {opener}() body has no "
                f"assertion-style call\n"
            )
            findings += 1

    # Sub-check 2: empty group.
    for line_no, body in scan_blocks(raw, "group"):
        if TEST_CALL_RE.search(body):
            continue
        sys.stdout.write(
            f"{rel_path}:{line_no}: empty group() (no test / "
            f"testWidgets / group call inside)\n"
        )
        findings += 1

    # Sub-check 3: literal expect(...length, N).
    stripped = strip_comments_and_strings(raw)
    line_starts = compute_line_starts(raw)
    for m in LITERAL_EXPECT_RE.finditer(stripped):
        line_no = line_of(m.start(), line_starts)
        sys.stdout.write(
            f"{rel_path}:{line_no}: prefer expect(x, hasLength(N)) "
            f"over expect(x.length, N)\n"
        )
        findings += 1

    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Test-smell gate for Dart test files."
    )
    parser.add_argument(
        "--exclude-paths",
        type=Path,
        default=DEFAULT_EXCLUDE_FILE,
    )
    args = parser.parse_args(argv)

    excluded = load_exclude_patterns(args.exclude_paths)

    roots = [
        PROJECT_ROOT / "test" / "unit",
        PROJECT_ROOT / "test" / "widget",
        PROJECT_ROOT / "integration_test",
    ]
    roots = [r for r in roots if r.exists()]
    if not roots:
        sys.stderr.write("NOTICE: no test roots found; nothing to scan.\n")
        return 0

    total = 0
    for root in roots:
        for file_path in sorted(root.rglob("*_test.dart")):
            try:
                rel = str(file_path.resolve().relative_to(PROJECT_ROOT))
            except ValueError:
                rel = str(file_path)
            if is_excluded(rel, excluded):
                continue
            total += check_file(file_path, rel)

    if total > 0:
        sys.stdout.write(f"\nFAIL: {total} test-smell finding(s).\n")
        return 1
    sys.stdout.write("PASS: no test smells detected.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
