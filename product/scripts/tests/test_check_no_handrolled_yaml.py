# tier: B
"""Tests for scripts/quality/check_no_handrolled_yaml.py (REQ-PROC-051 G4).

Tests check_file() directly with synthetic Python source strings.
The two-signature pattern: (1) compare against '---' AND (2) fm-flag variable
or .split(':') call.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_no_handrolled_yaml as cy  # type: ignore[import-not-found]


def _check(source: str, filename: str = "test_file.py") -> list[tuple[int, str]]:
    tmp = Path("/tmp") / filename
    tmp.write_text(textwrap.dedent(source))
    return cy.check_file(tmp)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# True-negatives — check_file() returns []
# ---------------------------------------------------------------------------

def test_clean_module_passes() -> None:
    findings = _check("""\
        def process(data):
            result = {}
            for item in data:
                result[item] = True
            return result
    """)
    assert findings == []


def test_sentinel_alone_passes() -> None:
    """Comparing to '---' without fm-flag or split(':') is not flagged."""
    findings = _check("""\
        def check(line):
            if line == '---':
                return True
            return False
    """)
    assert findings == []


def test_fm_flag_alone_passes() -> None:
    """A boolean fm-flag without '---' comparison is not flagged."""
    findings = _check("""\
        def parse(lines):
            in_frontmatter = False
            for line in lines:
                in_frontmatter = not in_frontmatter
    """)
    assert findings == []


def test_yaml_frontmatter_module_is_in_allowlist(tmp_path: Path) -> None:
    """_is_allowed() returns True for yaml_frontmatter.py (allow-list entry).

    Note: check_file() does NOT apply the allow-list — only main() does.
    This test verifies the allow-list predicate directly.
    """
    # Simulate a path ending with the canonical allow-listed suffix.
    allow_path = tmp_path / "scripts" / "util" / "yaml_frontmatter.py"
    allow_path.parent.mkdir(parents=True)
    allow_path.write_text("")
    assert cy._is_allowed(allow_path) is True


def test_non_allowlisted_file_not_exempted(tmp_path: Path) -> None:
    """_is_allowed() returns False for arbitrary scripts."""
    other = tmp_path / "scripts" / "tasks" / "complete_task.py"
    other.parent.mkdir(parents=True)
    other.write_text("")
    assert cy._is_allowed(other) is False


# ---------------------------------------------------------------------------
# True-positives — check_file() returns findings
# ---------------------------------------------------------------------------

def test_two_signature_pattern_flagged() -> None:
    """Both signatures present in same function → flagged."""
    findings = _check("""\
        def parse_frontmatter(lines):
            in_frontmatter = False
            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                elif in_frontmatter:
                    key, val = line.split(':', 1)
    """)
    assert len(findings) >= 1
    assert "hand-rolled" in findings[0][1]


def test_split_colon_with_sentinel_flagged() -> None:
    """Sentinel compare + split(':') in same scope → flagged."""
    findings = _check("""\
        def load(path):
            for line in open(path):
                if line.strip() == '---':
                    continue
                k, v = line.split(':', 1)
    """)
    assert len(findings) >= 1


def test_fm_started_flag_with_sentinel_flagged() -> None:
    """frontmatter_started flag + '---' compare → flagged."""
    findings = _check("""\
        def read(f):
            frontmatter_started = False
            for line in f:
                if line == '---':
                    frontmatter_started = True
    """)
    assert len(findings) >= 1
