#!/usr/bin/env python3
"""REQ-PROC-052 SP2 — no telemetry / analytics / crash-reporting SDKs.

Parses pubspec.yaml (dependencies, dev_dependencies, dependency_overrides) and
asserts that no entry matches any package on the FORBIDDEN_SDKS list. The list
is the verbatim AC-02 enumeration from REQ-PROC-052 plus their canonical pub.dev
package names so the check is robust against renames.

Usage:
    scripts/quality/check_no_telemetry_sdks.py [--exclude-paths <file>]

The --exclude-paths flag is accepted for symmetry with the other gates; it
loads patterns from scripts/quality/exclusions.txt (or the given file) and
skips any pubspec.yaml whose path matches an exclusion. In practice there is
only one pubspec.yaml at the project root, so the flag rarely matters here.

Exit codes:
    0  no forbidden SDKs found
    1  one or more forbidden SDKs found
    2  invocation error (pubspec.yaml missing, parse error)

Output:
    On fail: prints one '<path>:<line>: <sdk>' per occurrence to stdout, followed by a FAIL summary.
    On pass: prints a PASS summary line.
"""

# tier: C  # one-shot CLI gate script; no in-tree Python imports

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PUBSPEC = PROJECT_ROOT / "pubspec.yaml"
DEFAULT_EXCLUDE_FILE = Path(__file__).resolve().parent / "exclusions.txt"

# AC-02 verbatim list:
#   Firebase Analytics, Firebase Crashlytics, Sentry, Mixpanel, Amplitude,
#   Adjust, AppsFlyer, OneSignal, Bugsnag.
#
# Each human-named SDK maps to one or more pub.dev package names that an
# LLM might add. The matching rule is:
#   any dependency key that *equals* one of these names, or starts with one
#   followed by '_' (covers companion packages like firebase_analytics_web).
FORBIDDEN_SDKS: dict[str, list[str]] = {
    "Firebase Analytics":   ["firebase_analytics"],
    "Firebase Crashlytics": ["firebase_crashlytics"],
    "Sentry":               ["sentry", "sentry_flutter", "sentry_dart"],
    "Mixpanel":             ["mixpanel_flutter", "mixpanel_analytics"],
    "Amplitude":            ["amplitude_flutter", "amplitude_analytics"],
    "Adjust":               ["adjust_sdk"],
    "AppsFlyer":            ["appsflyer_sdk"],
    "OneSignal":            ["onesignal_flutter"],
    "Bugsnag":              ["bugsnag_flutter"],
}


def _flatten() -> list[tuple[str, list[str]]]:
    """Return [(human_name, [package_names]), ...] preserving order."""
    return list(FORBIDDEN_SDKS.items())


def _load_exclude_patterns(path: Path) -> list[str]:
    if not path.is_file():
        return []
    patterns: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    return patterns


def _is_excluded(rel_path: str, patterns: list[str]) -> bool:
    return any(pat in rel_path for pat in patterns)


# Parse top-level dependency map keys from a pubspec.yaml. We avoid pulling in
# PyYAML because the rest of the script set is pure-stdlib; the structure we
# need is small and the regex is sufficient for any well-formed pubspec.
_SECTION_RE = re.compile(r"^(dependencies|dev_dependencies|dependency_overrides):\s*$")
_KEY_RE = re.compile(r"^  ([A-Za-z_][A-Za-z0-9_]*)\s*:")


def parse_dependency_keys(pubspec_text: str) -> dict[str, list[str]]:
    """Return {section_name: [package_keys]} for the three dep sections."""
    sections: dict[str, list[str]] = {
        "dependencies": [],
        "dev_dependencies": [],
        "dependency_overrides": [],
    }
    current: str | None = None
    for line in pubspec_text.splitlines():
        # Skip comment-only lines
        if line.lstrip().startswith("#"):
            continue
        section_match = _SECTION_RE.match(line)
        if section_match:
            current = section_match.group(1)
            continue
        # Top-level key (no indent) — leaves any dependency section.
        if line and not line.startswith(" ") and not line.startswith("\t"):
            current = None
            continue
        if current is None:
            continue
        key_match = _KEY_RE.match(line)
        if key_match:
            sections[current].append(key_match.group(1))
    return sections


def find_violations(deps: dict[str, list[str]]) -> list[tuple[str, str, str]]:
    """Return [(section, package_key, human_sdk_name), ...]."""
    violations: list[tuple[str, str, str]] = []
    for section, keys in deps.items():
        for key in keys:
            for human, names in _flatten():
                for name in names:
                    if key == name or key.startswith(name + "_"):
                        violations.append((section, key, human))
                        break
                else:
                    continue
                break
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exclude-paths", type=Path, default=DEFAULT_EXCLUDE_FILE)
    args = parser.parse_args()

    if not PUBSPEC.is_file():
        print(f"ERROR: pubspec.yaml not found at {PUBSPEC}", file=sys.stderr)
        return 2

    rel = str(PUBSPEC.relative_to(PROJECT_ROOT))
    patterns = _load_exclude_patterns(args.exclude_paths)
    if _is_excluded(rel, patterns):
        print("PASS: SP2 (no telemetry SDKs) — pubspec.yaml is on the exclusion list (skipped).")
        return 0

    try:
        text = PUBSPEC.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read pubspec.yaml: {exc}", file=sys.stderr)
        return 2

    deps = parse_dependency_keys(text)
    violations = find_violations(deps)

    if violations:
        print(f"FAIL: SP2 (no telemetry SDKs) — {len(violations)} forbidden dependency match(es):")
        for section, key, human in violations:
            print(f"  {section}: {key}   (matches forbidden SDK: {human})")
        print()
        print("Forbidden-SDK list (REQ-PROC-052 AC-02):")
        for human, names in _flatten():
            print(f"  - {human}: {', '.join(names)}")
        print()
        print("If a listed package is being added intentionally, REQ-PROC-052")
        print("AC-02 must be updated first; SP2 has no per-path exception.")
        return 1

    print("PASS: SP2 (no telemetry SDKs) — pubspec.yaml clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
