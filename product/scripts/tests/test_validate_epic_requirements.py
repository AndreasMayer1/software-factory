#!/usr/bin/env python3
"""Regression tests for scripts/requirements/validate_epic_requirements.py.

Pins observable behaviour of count_body_lines before swapping the hand-rolled
parser to scripts.util.yaml_frontmatter (TASK-PROC-051-04 / G4).
"""

from scripts.requirements import validate_epic_requirements as v


def test_count_body_lines_with_frontmatter() -> None:
    content = (
        "---\n"
        "id: REQ-001\n"
        "---\n"
        "# Title\n"
        "\n"
        "body line\n"
    )
    # Lines after closing '---' are 3: "# Title", "", "body line"
    assert v.count_body_lines(content) == 3


def test_count_body_lines_without_frontmatter_returns_full_length() -> None:
    content = "# Title\n\nbody\n"
    # 3 lines (splitlines does not count trailing newline as a line)
    assert v.count_body_lines(content) == 3


def test_count_body_lines_empty_body() -> None:
    content = "---\nid: REQ-001\n---\n"
    assert v.count_body_lines(content) == 0


def test_count_body_lines_with_empty_lines_in_body() -> None:
    content = "---\nid: REQ-001\n---\n\n\n\n"
    # 3 trailing empty lines after closing '---'
    assert v.count_body_lines(content) == 3
