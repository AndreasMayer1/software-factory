# tier: B
"""Tests for scripts/quality/check_type_naming.sh.

Invocation strategy
-------------------
`check_type_naming.sh` derives PROJECT_ROOT from its own location via _lib.sh
and hardcodes ``SCAN_ROOT="${PROJECT_ROOT}/lib"``.  There is no env-var override.

To isolate tests from the live source tree we run the script through a thin
inline wrapper that overrides ``PROJECT_ROOT`` *after* sourcing ``_lib.sh``
(but before SCAN_ROOT is set):

    #!/usr/bin/env bash
    source <real_script>   # not viable — sets PROJECT_ROOT early

Instead, we construct a wrapper that:
  1. sources _lib.sh so all helpers are in scope,
  2. overrides PROJECT_ROOT to point at a temp directory,
  3. then runs the gate logic from the original script verbatim (copy the
     logic, not the file — fragile) … OR

Simpler: source _lib.sh, set PROJECT_ROOT, then inline just the scan block
via a self-contained wrapper that calls the original script with an env
injection hack: set PROJECT_ROOT as an exported variable BEFORE bash sources
_lib.sh.  _lib.sh unconditionally overwrites PROJECT_ROOT from its own
directory — so that does not work either.

Final approach (robust, zero coupling):
  Write a *replacement _lib.sh* inside a temp scripts/quality/ mirror, copy
  (symlink) the real check_type_naming.sh beside it, and run bash from there.
  The replacement _lib.sh sets PROJECT_ROOT to the temp project root.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "quality" / "check_type_naming.sh"
REAL_QUALITY_DIR = Path(__file__).parent.parent / "quality"
PROJECT_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Harness helpers
# ---------------------------------------------------------------------------

def _make_isolated_env(tmp: Path) -> tuple[Path, Path]:
    """
    Build a minimal isolated scripts/quality/ mirror inside *tmp*.

    Returns (script_path, tmp_project_root) where script_path is a copy of
    the real check_type_naming.sh configured to scan tmp_project_root/lib/.
    """
    # Mirror directory: tmp/scripts/quality/
    quality_dir = tmp / "scripts" / "quality"
    quality_dir.mkdir(parents=True)

    # Project root that the script will scan.
    fake_root = tmp / "project"
    fake_root.mkdir()
    (fake_root / "lib").mkdir()

    # Write a replacement _lib.sh that sets PROJECT_ROOT to fake_root.
    fake_lib_sh = quality_dir / "_lib.sh"
    fake_lib_sh.write_text(
        f"""#!/usr/bin/env bash
# Stub _lib.sh for testing — overrides PROJECT_ROOT to the isolated tmp dir.
_QUALITY_DIR="{quality_dir}"
PROJECT_ROOT="{fake_root}"
EXCLUDE_FILE="{quality_dir}/exclusions.txt"
EXCLUDE_PATTERNS=()

parse_exclude_arg() {{
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --exclude-paths)
                EXCLUDE_FILE="$2"; shift 2 ;;
            --exclude-paths=*)
                EXCLUDE_FILE="${{1#*=}}"; shift ;;
            *) shift ;;
        esac
    done
}}

load_exclude_patterns() {{
    EXCLUDE_PATTERNS=()
    [[ ! -f "$EXCLUDE_FILE" ]] && return 0
    while IFS= read -r line || [[ -n "$line" ]]; do
        local trimmed="${{line%%#*}}"
        trimmed="$(echo "$trimmed" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        [[ -z "$trimmed" ]] && continue
        EXCLUDE_PATTERNS+=("$trimmed")
    done < "$EXCLUDE_FILE"
}}

is_excluded() {{
    local path="$1"
    local pat
    for pat in "${{EXCLUDE_PATTERNS[@]}}"; do
        [[ "$path" == *"$pat"* ]] && return 0
    done
    return 1
}}
"""
    )

    # Create an empty exclusions.txt so the script does not fail.
    (quality_dir / "exclusions.txt").write_text("")

    # Copy (not symlink) the real script beside the stub _lib.sh.
    script_copy = quality_dir / "check_type_naming.sh"
    shutil.copy2(SCRIPT, script_copy)

    return script_copy, fake_root


def _run(script: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(script), *extra_args],
        capture_output=True,
        text=True,
    )


def _dart_file(fake_root: Path, name: str, content: str) -> Path:
    path = fake_root / "lib" / name
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# True-negative: clean code passes
# ---------------------------------------------------------------------------

def test_valid_pascal_case_passes() -> None:
    """A simple PascalCase class name (no suffix) must pass."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, root = _make_isolated_env(tmp)
        _dart_file(root, "clean.dart", "class MyWidget {}\n")
        result = _run(script)
        assert result.returncode == 0, (
            f"Expected PASS, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "PASS" in result.stdout


def test_approved_suffixes_pass() -> None:
    """Classes with each approved suffix must pass."""
    suffixes = [
        "Event", "Failure", "Bloc", "State", "Repository",
        "Service", "UseCase", "Entity", "ValueObject",
    ]
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, root = _make_isolated_env(tmp)
        content = "\n".join(f"class Foo{s} {{}}" for s in suffixes) + "\n"
        _dart_file(root, "suffixes.dart", content)
        result = _run(script)
        assert result.returncode == 0, (
            f"Expected PASS for approved suffixes, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


def test_generated_files_skipped() -> None:
    """Generated files (*.g.dart, *.freezed.dart) are skipped even with bad names."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, root = _make_isolated_env(tmp)
        _dart_file(root, "foo.g.dart", "class _bad_name {}\n")
        _dart_file(root, "bar.freezed.dart", "class another_bad {}\n")
        result = _run(script)
        assert result.returncode == 0, (
            f"Generated files should be skipped, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


def test_empty_lib_dir_passes() -> None:
    """An empty lib/ directory (no .dart files) must exit 0."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, _root = _make_isolated_env(tmp)
        # lib/ exists but is empty
        result = _run(script)
        assert result.returncode == 0, (
            f"Empty lib/ should pass, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# ---------------------------------------------------------------------------
# True-positive: violation detected
# ---------------------------------------------------------------------------

def test_lowercase_class_name_flagged() -> None:
    """A class starting with lowercase is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, root = _make_isolated_env(tmp)
        _dart_file(root, "bad.dart", "class myBadClass {}\n")
        result = _run(script)
        assert result.returncode == 1, (
            f"Expected FAIL for lowercase class, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "myBadClass" in result.stdout


def test_snake_case_class_name_flagged() -> None:
    """A snake_case class name is a violation."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, root = _make_isolated_env(tmp)
        _dart_file(root, "bad.dart", "class my_class {}\n")
        result = _run(script)
        assert result.returncode == 1, (
            f"Expected FAIL for snake_case class, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


@pytest.mark.xfail(
    strict=False,
    reason=(
        "DESIGN GAP: check_type_naming.sh's NAME_RE allows any PascalCase name "
        "regardless of suffix — 221+ classes in lib/ use non-approved suffixes "
        "(Screen, View, Controller, Impl, …) and are intentionally valid. "
        "Enforcing approved-suffixes-only would require a deliberate rule change "
        "and a TASK-PROC-046-19-scale fix pass. Filed as design note; not a bug."
    ),
)
def test_unapproved_suffix_flagged() -> None:
    """FooHelper currently passes — NAME_RE approves any PascalCase name (xfail)."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, root = _make_isolated_env(tmp)
        _dart_file(root, "bad.dart", "class FooHelper {}\n")
        result = _run(script)
        assert result.returncode == 1, (
            f"Expected FAIL for unapproved suffix, got {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "FooHelper" in result.stdout


# ---------------------------------------------------------------------------
# Private class convention: Flutter's _FooState and similar
# ---------------------------------------------------------------------------

def test_private_state_class_passes() -> None:
    """Flutter's _FooState convention passes — private classes are skipped."""
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        script, root = _make_isolated_env(tmp)
        _dart_file(
            root,
            "my_widget.dart",
            "class MyWidget extends StatefulWidget {}\n"
            "class _MyWidgetState extends State<MyWidget> {}\n",
        )
        result = _run(script)
        assert result.returncode == 0, (
            f"_MyWidgetState should pass but script returned {result.returncode}.\n"
            f"stdout: {result.stdout}"
        )
