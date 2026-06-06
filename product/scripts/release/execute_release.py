#!/usr/bin/env python3
"""Execute the release: bump pubspec version, merge develop → master, tag, push.
Output:
    Prints each release step (version bump, merge, tag, push) to stdout as it runs. --dry-run prints the planned actions without executing them.
"""

# tier: C  # one-shot CLI release-pipeline script; no in-tree Python imports

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Why: this script runs both as `python3 scripts/release/execute_release.py`
# (standalone, no PYTHONPATH) and via pytest (which adds project root to sys.path).
# Add scripts/ to sys.path so `from util.yaml_frontmatter import ...` resolves
# regardless of invocation path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from util.yaml_frontmatter import (  # type: ignore[import-not-found]  # noqa: E402 -- sys.path mutated above; mypy cannot follow runtime path manipulation
    FrontmatterError,
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


def run_step(label: str, cmd: list[str], remaining_steps: list[str], dry_run: bool) -> None:
    print(f"[Step {label}]", end="")
    if dry_run:
        print(f" (dry-run) {' '.join(cmd)}")
        return

    print()
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\nERROR: Step {label} failed (exit code {result.returncode}).")
        if remaining_steps:
            print("To recover manually, run the remaining steps:")
            for step in remaining_steps:
                print(f"  {step}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute a release.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    args = parser.parse_args()
    dry_run = args.dry_run

    print("execute_release.py — Starting release execution")
    print()

    # Step 0: Determine active release version
    release_version = get_active_release_version()
    if not release_version:
        print("ERROR: No active release found in requirements_tasks/RELEASES.md.")
        print("Run requ-prep-release to activate a release before executing.")
        sys.exit(1)

    print(f"Active release: {release_version}")
    print()

    # Step 1: Bump version in pubspec.yaml
    pubspec_path = PROJECT_ROOT / "pubspec.yaml"
    lines = pubspec_path.read_text(encoding="utf-8").splitlines()

    version_idx = next((i for i, line in enumerate(lines) if re.match(r'^version:\s+', line)), -1)

    if version_idx >= 0:
        existing = re.sub(r'^version:\s+', '', lines[version_idx])
        m = re.match(r'^\d+\.\d+\.\d+\+(\d+)$', existing)
        new_build = (int(m.group(1)) + 1) if m else 1
    else:
        new_build = 1
        desc_idx = next((i for i, line in enumerate(lines) if re.match(r'^description:', line)), -1)
        insert_idx = (desc_idx + 1) if desc_idx >= 0 else 1
        lines.insert(insert_idx, "")  # placeholder, replaced below
        version_idx = insert_idx

    lines[version_idx] = f"version: {release_version}+{new_build}"

    if not dry_run:
        pubspec_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[Step 1] Bumped pubspec.yaml version to {release_version}+{new_build}")

    all_git_steps = [
        "git add pubspec.yaml",
        f'git commit -m "chore: bump version to v{release_version}"',
        "git checkout master",
        f'git merge develop --no-ff -m "release: v{release_version}"',
        f'git tag -a "v{release_version}" -m "Release v{release_version}"',
        "git push origin master",
        f"git push origin v{release_version}",
        "git checkout develop",
    ]

    # Step 2: git add pubspec.yaml
    run_step("2 (git add pubspec.yaml)", ["git", "add", "pubspec.yaml"], all_git_steps[1:], dry_run)

    # Step 3: git commit
    run_step(
        "3 (git commit)",
        ["git", "commit", "-m", f"chore: bump version to v{release_version}"],
        all_git_steps[2:],
        dry_run,
    )

    # Step 4: git checkout master
    run_step("4 (git checkout master)", ["git", "checkout", "master"], all_git_steps[3:], dry_run)

    # Step 5: git merge develop --no-ff
    run_step(
        "5 (git merge develop --no-ff)",
        ["git", "merge", "develop", "--no-ff", "-m", f"release: v{release_version}"],
        all_git_steps[4:],
        dry_run,
    )

    # Step 6: git tag
    run_step(
        f"6 (git tag v{release_version})",
        ["git", "tag", "-a", f"v{release_version}", "-m", f"Release v{release_version}"],
        all_git_steps[5:],
        dry_run,
    )

    # Step 7: git push origin master
    run_step("7 (git push origin master)", ["git", "push", "origin", "master"], all_git_steps[6:], dry_run)

    # Step 8: git push origin tag
    run_step(
        f"8 (git push origin v{release_version})",
        ["git", "push", "origin", f"v{release_version}"],
        all_git_steps[7:],
        dry_run,
    )

    # Step 9: git checkout develop
    run_step("9 (git checkout develop)", ["git", "checkout", "develop"], [], dry_run)

    print()
    print(f"Release v{release_version} complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
