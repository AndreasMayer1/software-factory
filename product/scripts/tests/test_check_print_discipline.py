# tier: B
"""Tests for scripts/quality/check_print_discipline.py (REQ-PROC-051 G5).

Tests check_file() directly with synthetic Python source.
Rules: non-CLI modules may not print(); CLI modules (have __main__ block)
must document their output via 'Output:' in the docstring.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "quality"))
import check_print_discipline as cpd  # type: ignore[import-not-found]


def _check(source: str) -> list[tuple[int, str]]:
    tmp = Path("/tmp") / "test_print_discipline_sample.py"
    tmp.write_text(textwrap.dedent(source))
    return cpd.check_file(tmp)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# True-negatives — check_file() returns []
# ---------------------------------------------------------------------------

def test_non_cli_no_print_passes() -> None:
    """Pure library module with no print() passes."""
    findings = _check("""\
        def compute(x):
            return x * 2
    """)
    assert findings == []


def test_cli_with_output_contract_and_print_passes() -> None:
    """CLI module with 'Output:' docstring + print() passes."""
    findings = _check("""\
        \"\"\"My CLI tool.

        Output:
          One line per result.
        \"\"\"

        def run():
            print('result')

        if __name__ == '__main__':
            run()
    """)
    assert findings == []


def test_cli_with_output_contract_variant_passes() -> None:
    """'Output contract:' is also an accepted marker."""
    findings = _check("""\
        \"\"\"Tool.

        Output contract:
          Prints PASS or FAIL on stdout.
        \"\"\"

        if __name__ == '__main__':
            print('PASS')
    """)
    assert findings == []


def test_sys_stderr_write_not_flagged() -> None:
    """sys.stderr.write() is never flagged."""
    findings = _check("""\
        import sys

        def warn(msg):
            sys.stderr.write(msg + '\\n')
    """)
    assert findings == []


def test_sys_stdout_write_not_flagged() -> None:
    """sys.stdout.write() is never flagged."""
    findings = _check("""\
        import sys

        def emit(line):
            sys.stdout.write(line)
    """)
    assert findings == []


# ---------------------------------------------------------------------------
# True-positives — check_file() returns findings
# ---------------------------------------------------------------------------

def test_print_in_non_cli_module_flagged() -> None:
    """print() in a non-CLI module (no __main__ block) is a violation."""
    findings = _check("""\
        def process(data):
            print(f'Processing {data}')
            return data
    """)
    assert len(findings) >= 1
    assert "non-CLI" in findings[0][1]


def test_cli_without_output_contract_flagged() -> None:
    """CLI module with print() but no 'Output:' in docstring is a violation."""
    findings = _check("""\
        \"\"\"My tool — does things.\"\"\"

        def run():
            print('done')

        if __name__ == '__main__':
            run()
    """)
    assert len(findings) >= 1
    assert "Output:" in findings[0][1] or "contract" in findings[0][1]


def test_pprint_in_non_cli_flagged() -> None:
    """pprint.pprint() in a non-CLI module is a violation."""
    findings = _check("""\
        import pprint

        def debug(data):
            pprint.pprint(data)
    """)
    assert len(findings) >= 1


# ---------------------------------------------------------------------------
# main() smoke
# ---------------------------------------------------------------------------

def test_main_exits_without_crash() -> None:
    """main() can run against the real scripts/ without raising."""
    import subprocess
    import sys as _sys
    result = subprocess.run(
        [_sys.executable,
         str(Path(__file__).parent.parent / "quality" / "check_print_discipline.py")],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent.parent),
    )
    assert result.returncode in (0, 1), f"Unexpected exit: {result.returncode}\n{result.stderr}"
