#!/usr/bin/env python3
"""Check all preconditions before running execute_release.py.
Output:
    Prints a section per check (canon coherence, pending tasks, branch state, tests, version) to stdout with [PASS]/[FAIL]/[WARN] markers, ending with an overall summary line.
"""

# tier: C  # one-shot CLI release-pipeline script; no in-tree Python imports

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Why: this script runs both as `python3 scripts/release/check_release_preconditions.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
    _parse_yaml_block,
    _split_frontmatter,
    read_frontmatter,
)

PROJECT_ROOT = Path(__file__).parent.parent


def get_active_release_version() -> str | None:
    """Return the version string of the release whose status is 'active', or None."""
    releases_path = PROJECT_ROOT / "requirements_tasks" / "RELEASES.md"
    if not releases_path.exists():
        return None
    try:
        doc = read_frontmatter(releases_path)
    except (FrontmatterError, OSError):
        return None
    if not doc.has_frontmatter:
        return None
    releases = doc.metadata.get("releases")
    if not isinstance(releases, list):
        return None
    for entry in releases:
        if isinstance(entry, dict) and str(entry.get("status", "")).strip() == "active":
            version = entry.get("version")
            if version is not None:
                return str(version).strip().strip("\"'")
    return None


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, (result.stdout + result.stderr).strip()


def find_goal_files(root: Path) -> list[Path]:
    """Find all goal.md files under requirements_tasks/."""
    try:
        result = subprocess.run(
            ["find", str(root), "-name", "goal.md"],
            capture_output=True, text=True
        )
        return [Path(p) for p in result.stdout.splitlines() if p.strip()]
    except FileNotFoundError:
        return list(root.rglob("goal.md"))


def parse_frontmatter(content: str) -> dict[Any, Any] | None:
    """Extract YAML frontmatter from markdown content. Returns dict or None.

    Delegates to scripts.util.yaml_frontmatter (REQ-PROC-051 AC-08).
    """
    # Strip UTF-8 BOM (central helper does not).
    if content.startswith("\ufeff"):
        content = content[1:]
    raw_yaml, _body = _split_frontmatter(content)
    if not raw_yaml:
        return None
    try:
        metadata = _parse_yaml_block(raw_yaml)
    except Exception:
        return None
    if not metadata:
        return None
    return dict(metadata)


COVERAGE_THRESHOLD = 75.0


def check_line_coverage() -> tuple[bool, float]:
    """
    Parse coverage/lcov.info and compute line coverage across all tracked source files.
    Returns (passed: bool, coverage_pct: float).
    Fails hard (returns False) if lcov.info is missing or unparseable.
    """
    lcov_path = PROJECT_ROOT / "coverage" / "lcov.info"
    if not lcov_path.exists():
        print("ERROR: coverage/lcov.info not found after flutter test --coverage.")
        return False, 0.0

    total_lines = 0
    hit_lines = 0
    covered_files: set[str] = set()

    current_sf: str | None = None
    cur_total = 0
    cur_hit = 0

    for line in lcov_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("SF:"):
            current_sf = line[3:].strip()
            cur_total = 0
            cur_hit = 0
        elif line.startswith("DA:") and current_sf:
            parts = line[3:].split(",")
            if len(parts) >= 2:
                cur_total += 1
                if int(parts[1]) > 0:
                    cur_hit += 1
        elif line == "end_of_record" and current_sf:
            total_lines += cur_total
            hit_lines += cur_hit
            covered_files.add(current_sf)
            current_sf = None
            cur_total = 0
            cur_hit = 0

    # Account for tracked source files not imported by any test
    lib_dir = PROJECT_ROOT / "lib"
    for dart_file in lib_dir.rglob("*.dart"):
        # Skip generated files — they skew coverage and can't be unit-tested
        if dart_file.name.endswith(".g.dart") or dart_file.name.endswith(".freezed.dart"):
            continue
        abs_str = str(dart_file.resolve())
        if abs_str not in covered_files:
            # Count non-blank, non-comment lines as a rough proxy for instrumentable lines
            try:
                src_lines = [
                    line for line in dart_file.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.strip().startswith("//")
                ]
                file_lines = max(len(src_lines), 1)
            except Exception:
                file_lines = 1
            total_lines += file_lines
            # hit_lines += 0  (zero covered)

    if total_lines == 0:
        print("[WARN] No instrumentable lines found in coverage report.")
        return True, 100.0

    pct = hit_lines / total_lines * 100
    return pct >= COVERAGE_THRESHOLD, pct


def main() -> None:
    failed = False

    print("Checking preconditions for release...")
    print()

    # Check 0: Must be on develop branch
    code, output = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=PROJECT_ROOT)
    if code != 0:
        print("ERROR: Could not determine current git branch. Are you in a git repository?")
        failed = True
    elif output != "develop":
        print(f"ERROR: Must be on branch 'develop' to run a release. Current branch: {output}")
        failed = True
    else:
        print("[OK] On branch: develop")

    # Check 1: Active release exists in RELEASES.md
    release_version = get_active_release_version()
    if not release_version:
        print("ERROR: No active release found in requirements_tasks/RELEASES.md. Run requ-prep-release first.")
        failed = True
    else:
        print(f"[OK] Active release: {release_version}")

    # Check 2: No pending/open tasks for the active release
    if release_version:
        next_tasks_script = PROJECT_ROOT / "scripts" / "next_tasks.py"
        try:
            code, output = run(
                [sys.executable, str(next_tasks_script), "--release", release_version, "--count", "100"],  # sys.executable = current python3 interpreter
                cwd=PROJECT_ROOT,
            )
            m = re.search(r"Open tasks:\s*(\d+)", output)
            if m:
                open_count = int(m.group(1))
                if open_count > 0:
                    print(f"ERROR: {open_count} open task(s) remain for release {release_version}. Complete all tasks before releasing.")
                    failed = True
                else:
                    print(f"[OK] No pending tasks for release {release_version}")
            else:
                print("ERROR: Could not parse open task count from next_tasks.py output. Output was:")
                print(output)
                failed = True
        except Exception as e:
            print(f"ERROR: Failed to run next_tasks.py: {e}")
            failed = True

    # Check 2b: impl tasks assigned to active release without release_description (non-blocking warning)
    TERMINAL_STATUSES = {"completed", "cancelled", "superseded", "deprecated"}
    if release_version:
        req_root = PROJECT_ROOT / "requirements_tasks"
        missing_desc: list[tuple[str, str]] = []
        for goal_file in find_goal_files(req_root):
            try:
                content = goal_file.read_text(encoding="utf-8")
            except Exception:
                continue
            meta = parse_frontmatter(content)
            if not meta or not meta.get("task_id"):
                continue
            if str(meta.get("type", "impl")).lower() != "impl":
                continue
            if str(meta.get("target_release", "")).strip().strip("\"'") != release_version:
                continue
            if str(meta.get("status", "unknown")).lower() in TERMINAL_STATUSES:
                continue
            rd = meta.get("release_description")
            if not rd or not str(rd).strip():
                task_id = str(meta.get("task_id", "unknown"))
                folder = goal_file.parent.name
                name = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", folder)
                name = re.sub(r"^(impl|explore|analyze|fix|create|update)_", "", name, flags=re.IGNORECASE)
                for suffix in ("_(completed)", "_(superseded)", "_(cancelled)", "_(paused)"):
                    name = name.replace(suffix, "")
                name = name.replace("_", " ").strip()
                missing_desc.append((task_id, name))
        if missing_desc:
            print(f"[WARN] {len(missing_desc)} impl task(s) assigned to release {release_version} have no release_description:")
            for tid, tname in sorted(missing_desc):
                print(f"       - {tid}: {tname}")
            print("       Set release_description in each task's goal.md or confirm omission is intentional.")
        else:
            print(f"[OK] All impl tasks for release {release_version} have a release_description set")

    # Check 3: develop branch is clean
    code, output = run(["git", "status", "--porcelain"], cwd=PROJECT_ROOT)
    if code != 0:
        print("ERROR: git status failed. Are you in a git repository?")
        failed = True
    elif output:
        print("ERROR: Develop branch has uncommitted changes. Commit or stash all changes before releasing.")
        failed = True
    else:
        print("[OK] Develop branch is clean")

    # Check 4: Local tests pass + coverage threshold
    code, output = run(["flutter", "test", "--coverage"], cwd=PROJECT_ROOT)
    if code != 0:
        print("ERROR: Flutter tests failed. Fix all test failures before releasing.")
        print(output)
        failed = True
    else:
        print("[OK] All tests pass")
        passed_cov, coverage_pct = check_line_coverage()
        if not passed_cov:
            print(f"ERROR: Line coverage {coverage_pct:.1f}% is below threshold {COVERAGE_THRESHOLD:.0f}%.")
            print("       Run 'flutter test --coverage' and check coverage/lcov.info.")
            failed = True
        else:
            print(f"[OK] Line coverage: {coverage_pct:.1f}% (threshold: {COVERAGE_THRESHOLD:.0f}%)")

    # Check 4c: Windows build output contains required VC++ runtime DLLs (non-blocking)
    windows_build_dir = PROJECT_ROOT / "build" / "windows" / "x64" / "runner" / "Release"
    required_dlls = ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll", "concrt140.dll"]
    if not windows_build_dir.exists():
        print("[WARN] Windows build output not found locally — confirm GitHub Actions artifact is complete after release.")
    else:
        missing_dlls = [dll for dll in required_dlls if not (windows_build_dir / dll).exists()]
        if missing_dlls:
            print(f"[WARN] Windows build output is missing required DLLs: {', '.join(missing_dlls)}")
            print("       Run the release_windows.yml workflow on GitHub Actions to produce a complete artifact.")
        else:
            print("[OK] Windows build output contains all required VC++ runtime DLLs")

    # Check 4d: Concept-canon coherence (REQ-PROC-049 AC-05)
    canon_script = PROJECT_ROOT / "scripts" / "user_needs" / "check_canon.py"
    if not canon_script.exists():
        print("ERROR: scripts/user_needs/check_canon.py not found — canon coherence cannot be verified.")
        print("canon coherence: FAIL")
        failed = True
    else:
        code, output = run([sys.executable, str(canon_script)], cwd=PROJECT_ROOT)
        if code != 0:
            print("canon coherence: FAIL")
            if output:
                print(output)
            print("       Resolve canon drift before releasing (see scripts/user_needs/check_canon.py output).")
            failed = True
        else:
            print("canon coherence: PASS")

    # Check 4e: Dependency advisory sweep (REQ-PROC-061 AC-03)
    sweep_script = PROJECT_ROOT / "scripts" / "release" / "check_dependency_sweep.py"
    if not sweep_script.exists():
        print("ERROR: scripts/release/check_dependency_sweep.py not found — dependency sweep cannot run.")
        print("dependency sweep: FAIL")
        failed = True
    else:
        code, output = run([sys.executable, str(sweep_script)], cwd=PROJECT_ROOT)
        if code != 0:
            print("dependency sweep: FAIL")
            if output:
                print(output)
            print("       Resolve all advisories before releasing (see check_dependency_sweep.py output).")
            failed = True
        else:
            print("dependency sweep: PASS")

    # Check 5: pubspec.yaml version not yet bumped to release version
    if release_version:
        pubspec_path = PROJECT_ROOT / "pubspec.yaml"
        version_line = next(
            (line for line in pubspec_path.read_text(encoding="utf-8").splitlines() if re.match(r'^version:\s+', line)),
            None,
        )
        if version_line:
            m = re.match(r'^version:\s+(\d+\.\d+\.\d+)', version_line)
            if m and m.group(1) == release_version:
                print(f"ERROR: pubspec.yaml version already matches {release_version}. The version was already bumped — execute_release.py may have been run already.")
                failed = True
            else:
                print("[OK] pubspec.yaml version not yet bumped")
        else:
            print("[OK] pubspec.yaml version not yet bumped")

    print()
    if failed:
        print("One or more preconditions failed. Fix the errors above before running execute_release.py.")
        sys.exit(1)

    print("All preconditions met. Safe to run execute_release.py.")
    sys.exit(0)


if __name__ == "__main__":
    main()
