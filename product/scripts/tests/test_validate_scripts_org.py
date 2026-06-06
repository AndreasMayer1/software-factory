"""Tests for scripts/validate_scripts_org.py (REQ-PROC-043 AC-06)."""

import os
import sys
import tempfile
from typing import cast

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import validate_scripts_org as vso  # type: ignore[import-not-found]  # sibling import via sys.path.insert; mypy cannot follow runtime path manipulation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_scripts_dir(tmp: str, files: dict[str, str | None]) -> None:
    """Create script files under tmp/scripts/. files maps rel-path → content (None = empty)."""
    for rel, content in files.items():
        abs_path = os.path.join(tmp, "scripts", rel)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w") as fh:
            fh.write(content or "")


def _make_claude_md(tmp: str, content: str) -> None:
    path = os.path.join(tmp, "CLAUDE.md")
    with open(path, "w") as fh:
        fh.write(content)


def _run(tmp: str, strict: bool = False) -> tuple[list[str], list[str]]:
    """Patch module globals and run validate(), return (errors, warnings)."""
    orig_script_dir = vso.SCRIPT_DIR
    orig_project_root = vso.PROJECT_ROOT
    orig_claude_md = vso.CLAUDE_MD
    try:
        vso.SCRIPT_DIR = os.path.join(tmp, "scripts")
        vso.PROJECT_ROOT = tmp
        vso.CLAUDE_MD = os.path.join(tmp, "CLAUDE.md")
        return cast("tuple[list[str], list[str]]", vso.validate(strict=strict))
    finally:
        vso.SCRIPT_DIR = orig_script_dir
        vso.PROJECT_ROOT = orig_project_root
        vso.CLAUDE_MD = orig_claude_md


# ---------------------------------------------------------------------------
# Tests: default mode passes on empty / clean domain folders
# ---------------------------------------------------------------------------

def test_empty_domain_folders_passes():
    """Default mode exits clean when domain folders are absent (current pre-refactor state)."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "scripts"))
        _make_claude_md(tmp, "No script paths here.\n")
        errors, _warnings = _run(tmp, strict=False)
        assert errors == [], f"Unexpected errors: {errors}"


def test_flat_top_level_scripts_ignored_in_default_mode():
    """Flat top-level .py files are NOT flagged in default mode (only in --strict)."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"next_tasks.py": ""})
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=False)
        assert not any("next_tasks.py" in e for e in errors)


# ---------------------------------------------------------------------------
# Tests: naming format check
# ---------------------------------------------------------------------------

def test_bad_naming_in_domain_folder_fails():
    """A script with an uppercase letter in a domain folder is a naming violation."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"tasks/MyScript.py": ""})
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=False)
        assert any("Naming violation" in e and "MyScript.py" in e for e in errors), errors


def test_valid_naming_in_domain_folder_passes():
    """A script with valid verb_noun naming in a domain folder is accepted."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"tasks/next_tasks.py": ""})
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=False)
        naming_errors = [e for e in errors if "Naming violation" in e]
        assert naming_errors == [], naming_errors


# ---------------------------------------------------------------------------
# Tests: Windows isolation check
# ---------------------------------------------------------------------------

def test_ps1_in_tasks_folder_is_isolation_violation():
    """A .ps1 file in tasks/ violates Windows isolation (only allowed in windows/)."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"tasks/complete_task.ps1": ""})
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=False)
        assert any("Windows isolation" in e and "complete_task.ps1" in e for e in errors), errors


def test_ps1_in_windows_folder_passes_isolation():
    """A .ps1 file in windows/ is correctly allowed."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"windows/complete_task.ps1": ""})
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=False)
        isolation_errors = [e for e in errors if "Windows isolation" in e]
        assert isolation_errors == [], isolation_errors


# ---------------------------------------------------------------------------
# Tests: CLAUDE.md path accuracy
# ---------------------------------------------------------------------------

def test_claude_md_missing_script_path_is_error():
    """A scripts/... path in CLAUDE.md that does not exist on disk is flagged."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "scripts"))
        _make_claude_md(tmp, "Run via `scripts/tasks/nonexistent_script.py`\n")
        errors, _ = _run(tmp, strict=False)
        assert any("nonexistent_script.py" in e for e in errors), errors


def test_claude_md_existing_script_path_passes():
    """A scripts/... path in CLAUDE.md that exists on disk is not flagged."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"tasks/next_tasks.py": ""})
        _make_claude_md(tmp, "Run via `scripts/tasks/next_tasks.py`\n")
        errors, _ = _run(tmp, strict=False)
        path_errors = [e for e in errors if "next_tasks.py" in e]
        assert path_errors == [], path_errors


# ---------------------------------------------------------------------------
# Tests: --strict mode
# ---------------------------------------------------------------------------

def test_strict_flags_flat_top_level_script():
    """--strict mode flags flat top-level scripts (except validate_scripts_org.py itself)."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"next_tasks.py": ""})
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=True)
        assert any("Flat top-level" in e and "next_tasks.py" in e for e in errors), errors


def test_strict_flags_missing_domain_folder():
    """--strict mode flags absent required domain folders."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "scripts"))
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=True)
        assert any("Required domain folder missing" in e for e in errors), errors


def test_strict_passes_when_structure_compliant():
    """--strict mode exits clean when domain folders exist and no flat scripts."""
    with tempfile.TemporaryDirectory() as tmp:
        scripts_dir = os.path.join(tmp, "scripts")
        for folder in vso.DOMAIN_FOLDERS:
            os.makedirs(os.path.join(scripts_dir, folder))
        # Add validate_scripts_org.py itself (the sole allowed top-level exception)
        open(os.path.join(scripts_dir, "validate_scripts_org.py"), "w").close()
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=True)
        assert errors == [], errors


# ---------------------------------------------------------------------------
# Tests: util/ size gate
# ---------------------------------------------------------------------------

def test_util_size_warning_when_over_five():
    """util/ with >5 scripts produces a warning (not an error)."""
    with tempfile.TemporaryDirectory() as tmp:
        files = {f"util/should_use_{i}.py": "" for i in range(6)}
        _make_scripts_dir(tmp, files)
        _make_claude_md(tmp, "")
        errors, warnings = _run(tmp, strict=False)
        assert any(("util/" in w and ">5" in w) or "6" in w for w in warnings), warnings
        assert errors == [], errors


# ---------------------------------------------------------------------------
# Tests: unknown verb prefix
# ---------------------------------------------------------------------------

def test_unknown_verb_prefix_flagged():
    """A script in a domain folder with an unclassified verb prefix is an error."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_scripts_dir(tmp, {"tasks/bloop_something.py": ""})
        _make_claude_md(tmp, "")
        errors, _ = _run(tmp, strict=False)
        assert any("Unknown verb prefix" in e and "bloop_something.py" in e for e in errors), errors


# ---------------------------------------------------------------------------
# Tests: CLI surface
# ---------------------------------------------------------------------------

def test_cli_help_runs_without_error():
    """python3 scripts/validate_scripts_org.py --help exits 0."""
    import subprocess
    script = os.path.join(os.path.dirname(__file__), "..", "validate_scripts_org.py")
    result = subprocess.run(
        [sys.executable, script, "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_cli_check_flag_runs_without_error():
    """python3 scripts/validate_scripts_org.py --check exits 0 on the real working tree."""
    import subprocess
    script = os.path.join(os.path.dirname(__file__), "..", "validate_scripts_org.py")
    result = subprocess.run(
        [sys.executable, script, "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
