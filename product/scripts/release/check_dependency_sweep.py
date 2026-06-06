#!/usr/bin/env python3
"""Run a pre-release dependency advisory sweep (REQ-PROC-061 AC-03).

Scans pubspec.lock and requirements-dev.txt with osv-scanner.
Also runs flutter pub outdated for informational output.

Output:
    Section per lockfile with [PASS]/[FAIL] markers, advisory details,
    and flutter pub outdated output (informational only).
    Final line: [PASS] or [FAIL] sweep summary.
    Exit 0 = clean sweep; Exit 1 = advisory found or tool unavailable.
"""

# tier: C  # one-shot CLI release-pipeline script; no in-tree Python imports

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command; return (exit_code, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _scan_lockfile(lockfile: Path) -> tuple[int, dict[str, Any]]:
    """Run osv-scanner over one lockfile. Returns (exit_code, parsed_json_or_empty)."""
    rc, stdout, _stderr = run(
        ["osv-scanner", "scan", "source", "-L", str(lockfile), "-f", "json"]
    )
    if stdout:
        try:
            return rc, json.loads(stdout)
        except json.JSONDecodeError:
            pass
    return rc, {}


def _count_advisories(scan_data: dict[str, Any]) -> list[str]:
    """Return a list of human-readable advisory strings from osv-scanner JSON output."""
    lines: list[str] = []
    for result in scan_data.get("results", []):
        for pkg in result.get("packages", []):
            vulns = pkg.get("vulnerabilities", [])
            if not vulns:
                continue
            pkg_info = pkg.get("package", {})
            name = pkg_info.get("name", "unknown")
            version = pkg_info.get("version", "unknown")
            for vuln in vulns:
                vuln_id = vuln.get("id", "unknown")
                summary = vuln.get("summary", "")
                aliases = vuln.get("aliases", [])
                alias_str = f" ({', '.join(aliases)})" if aliases else ""
                entry = f"  [ADVISORY] {name}@{version}: {vuln_id}{alias_str}"
                if summary:
                    entry += f"\n             {summary}"
                lines.append(entry)
    return lines


def main() -> None:
    failed = False

    print("Dependency advisory sweep (REQ-PROC-061 AC-03)")
    print("=" * 50)
    print()

    if not shutil.which("osv-scanner"):
        print("[FAIL] osv-scanner not installed.")
        print("       See .devcontainer/setup.sh — it is installed at container build time.")
        sys.exit(1)

    _rc, stdout, _ = run(["osv-scanner", "--version"])
    version_line = stdout.splitlines()[0] if stdout else "unknown"
    print(f"Tool: {version_line}")
    print()

    # --- Advisory scan per lockfile ---
    manifests = [
        PROJECT_ROOT / "pubspec.lock",
        PROJECT_ROOT / "requirements-dev.txt",
    ]

    total_advisory_count = 0

    for manifest in manifests:
        rel = manifest.relative_to(PROJECT_ROOT)
        if not manifest.exists():
            print(f"[SKIP] {rel} not found")
            continue

        print(f"Scanning {rel} ...")
        _rc2, data = _scan_lockfile(manifest)
        advisories = _count_advisories(data)

        if advisories:
            total_advisory_count += len(advisories)
            failed = True
            for line in advisories:
                print(line)
            print(f"  [FAIL] {len(advisories)} advisory/advisories in {manifest.name}")
        else:
            print(f"  [PASS] No advisories in {manifest.name}")
        print()

    # --- flutter pub outdated (informational) ---
    print("flutter pub outdated (informational — not a gate):")
    _flutter_rc, flutter_out, flutter_err = run(["flutter", "pub", "outdated"], cwd=PROJECT_ROOT)
    output_text = (flutter_out or flutter_err or "").strip()
    if output_text:
        for line in output_text.splitlines():
            print(f"  {line}")
    else:
        print("  (no output)")
    print()

    # --- Summary ---
    print("=" * 50)
    if failed:
        print(
            f"[FAIL] {total_advisory_count} unresolved advisory/advisories found.\n"
            "       No release candidate may ship with a known vulnerable dependency.\n"
            "       Resolve the findings above before approving this release."
        )
        sys.exit(1)

    print("[PASS] No security advisories found. Sweep complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
