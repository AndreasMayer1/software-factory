# Plan: Coverage Check, release_description Warning, and Smoke Test Gate

_Task: TASK-PROC-036-10_
_Date: 2026-04-19_

---

## Overview

Four files to change, two new files to create:

| File | Action | Type |
|---|---|---|
| `scripts/check_release_preconditions.py` | Add Check 2b (release_description warning) + Check 4b (coverage) | Modify |
| `.claude/skills/release/skill.md` | Insert new Step 2 (smoke gate), renumber old Steps 2–6 → 3–7 | Modify |
| `scripts/smoke_test_windows.ps1` | New script: build Windows release + run integration tests | Create |
| `scripts/smoke_test_llm.py` | New script: launch app + screenshot + Claude API verdict | Create |
| `CLAUDE.md` | Add two new rows to scripts table | Modify |

---

## File 1: `scripts/check_release_preconditions.py`

### Check 2b — release_description warning (non-blocking, after Check 2)

Insert after the existing Check 2 block (around line 95 in current file), before Check 3.

**Logic:**
1. Only run if `release_version` is set.
2. Scan all `goal.md` files under `requirements_tasks/` (use the same pattern as `next_tasks.py`: `find` or `rglob`).
3. For each file with valid frontmatter:
   - `type == "impl"` (case-insensitive)
   - `target_release == release_version` OR `target_package` matches the active release package name (prefer `target_release` match for simplicity — see note)
   - `status` not in terminal set (`completed`, `cancelled`, `superseded`, `deprecated`)
   - `release_description` is missing, empty, or None
4. Collect task IDs + names of matching tasks.
5. Print warning block (non-blocking, does NOT set `failed = True`).

**Note on release matching:** `check_release_preconditions.py` already uses `get_active_release_version()` which returns a version string. Task frontmatter uses `target_release` (version string) OR `target_package` (package name). To avoid the complexity of resolving package names to version, filter by `target_release == release_version`. This covers all tasks explicitly assigned to the version; tasks only assigned via package are out of scope for this check.

**Frontmatter parsing:** Reuse the same minimal YAML parser already in the script (the `run()` helper already exists; add a new helper `parse_frontmatter()` modeled after `next_tasks.py`'s version — simple, no PyYAML dependency).

**Output format:**
```
[WARN] 2 impl task(s) assigned to release 0.0.3 have no release_description:
       - TASK-FUNC-012-04: qr-scan-improvements
       - TASK-FUNC-015-02: onboarding-animation
       Set release_description in each task's goal.md or confirm omission is intentional.
```
or:
```
[OK] All impl tasks for release 0.0.3 have a release_description set
```

**Insertion point:** After the `# Check 2` block closes (around line 95), before `# Check 3`.

**Helper function to add (before `main()`):**
```python
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


def parse_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content. Returns dict or None."""
    if content.startswith("\ufeff"):
        content = content[1:]
    if not content.startswith("---"):
        return None
    lines = content.split("\n")
    yaml_lines: list[str] = []
    in_fm = False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_fm = True
            continue
        if in_fm:
            if line.strip() == "---":
                break
            yaml_lines.append(line)
    if not yaml_lines:
        return None
    result: dict = {}
    current_list_key: str | None = None
    for line in yaml_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0 and ":" in stripped:
            parts = stripped.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            if value in ("[]", ""):
                result[key] = [] if value == "[]" else None
                current_list_key = key
            elif value.startswith("[") and value.endswith("]"):
                items = value[1:-1].split(",")
                result[key] = [i.strip().strip("\"'") for i in items if i.strip()]
                current_list_key = None
            else:
                v = value.strip("\"'")
                result[key] = v
                current_list_key = None
        elif stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip("\"'")
            if not isinstance(result.get(current_list_key), list):
                result[current_list_key] = []
            result[current_list_key].append(item)
    return result
```

**Check 2b code block (insert in `main()` after Check 2):**
```python
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
                import re as _re
                name = _re.sub(r"^\d{4}-\d{2}-\d{2}_", "", folder)
                name = _re.sub(r"^(impl|explore|analyze|fix|create|update)_", "", name, flags=_re.IGNORECASE)
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
```

**Note on `import re`:** The script already has `import re` at top level, so inline `import re as _re` is redundant. In the actual implementation just use the module-level `re` directly.

---

### Check 4b — Flutter test coverage threshold (blocking, replaces Check 4)

**Replace Check 4** (current lines 108–115) with an expanded version that:
1. Runs `flutter test --coverage` (same command but different args).
2. If exit code != 0: print ERROR and set `failed = True` (same as now).
3. If exit code == 0:
   a. Print `[OK] All tests pass`.
   b. Run coverage threshold check using `lcov --summary coverage/lcov.info`.
   c. Also list all tracked `.dart` source files in `lib/` and cross-check against the lcov report to ensure untested files are counted (push their line rate to 0%).
   d. Compute overall line coverage across all tracked files.
   e. If coverage < 75%: print ERROR and set `failed = True`.
   f. Else: print `[OK] Line coverage: X.X% (threshold: 75%)`.

**Coverage measurement approach (from research):**

Option A: Use `lcov --summary` (requires `lcov` installed). Shell-based but needs external tool.
Option B: Parse `coverage/lcov.info` directly in Python (no external dependency). This is preferable for portability in WSL2/Linux container.

**Chosen approach: Parse `coverage/lcov.info` directly in Python.**

The lcov.info format is:
```
SF:<source_file>
DA:<line_number>,<hit_count>
...
end_of_record
```

Algorithm:
1. Read `coverage/lcov.info`.
2. For each `SF:` record, accumulate `total_lines` and `hit_lines` (hit_count > 0).
3. Also collect all `SF:` paths present in the report.
4. Scan all `.dart` files under `lib/` (excluding generated files like `*.g.dart`, `*.freezed.dart`).
5. For each `.dart` file NOT in the lcov report: add 0 hit_lines, some estimated total_lines (use 1 to ensure it counts but not dominate; or read and count non-blank non-comment lines). Conservative approach: use 1 line for each untracked file — it penalizes untested files but doesn't require parsing Dart.
6. Compute: `coverage = sum(hit_lines) / sum(total_lines) * 100`.
7. Compare against threshold 75.0.

**Helper function:**
```python
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
                    l for l in dart_file.read_text(encoding="utf-8").splitlines()
                    if l.strip() and not l.strip().startswith("//")
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
```

**Replacement for Check 4 in `main()`:**
```python
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
```

**Positioning in `main()`:** Replace the current `# Check 4` block (lines 108–115). The existing `# Check 4b` (DLL check, lines 117–128) remains and is renumbered to `# Check 4c` in comments for clarity (no functional change needed since it's already non-blocking).

---

## File 2: `.claude/skills/release/skill.md`

### Step insertions and renumbering

**Current structure:**
- Step 1 — Pre-flight check
- Step 2 — Execute release
- Step 3 — Technical release notes
- Step 4 — Marketing release notes
- Step 5 — Mark released
- Step 6 — Commit

**New structure:**
- Step 1 — Pre-flight check (unchanged)
- **Step 2 — Smoke test gate (NEW)**
- Step 3 — Execute release (was Step 2)
- Step 4 — Technical release notes (was Step 3)
- Step 5 — Marketing release notes (was Step 4)
- Step 6 — Mark released (was Step 5)
- Step 7 — Commit (was Step 6)

### New Step 2 text (to insert between current Step 1 and Step 2):

```markdown
---

## Step 2 — Smoke test gate

Before executing the release, the Windows release candidate must be smoke-tested on the Windows host.

Instruct the developer:

> Run both smoke test scripts on your Windows machine (not inside WSL2):
>
> **Script 1 — Integration test:**
> ```powershell
> cd <project root>
> .\scripts\smoke_test_windows.ps1
> ```
> This builds the Windows release binary and runs critical integration tests.
> Exit code 0 = pass. Report the exit code and any test failures.
>
> **Script 2 — LLM visual review (advisory):**
> ```powershell
> cd <project root>
> python scripts\smoke_test_llm.py
> ```
> This launches the release binary, captures a screenshot, and sends it to the Claude API for a visual pass/fail verdict. Requires `ANTHROPIC_API_KEY` in your environment.
> Report the PASS/FAIL verdict and reason printed by the script.
>
> Type **proceed** when both scripts have been run and the integration test passed (the LLM verdict is advisory only). Type anything else to abort the release.

Wait for the developer's response.

- If the developer types "proceed" (case-insensitive): confirm "Smoke gate passed. Continuing to release execution." and continue to Step 3.
- If exit code of `smoke_test_windows.ps1` was non-zero and the developer did not explicitly override: tell the developer to fix the failing integration tests before releasing. Stop.
- If the developer types anything other than "proceed": stop and report what was not done.

---
```

### Renumbering changes (exact string replacements):

- `## Step 2 — Execute release` → `## Step 3 — Execute release`
- `## Step 3 — Technical release notes` → `## Step 4 — Technical release notes`
- `## Step 4 — Marketing release notes` → `## Step 5 — Marketing release notes`
- `### 4.1 Read active release` → `### 5.1 Read active release`
- `### 4.2 Create output directory` → `### 5.2 Create output directory`
- `### 4.3 Generate German draft` → `### 5.3 Generate German draft`
- `### 4.4 Generate English draft` → `### 5.4 Generate English draft`
- `### 4.5 Present drafts for review` → `### 5.5 Present drafts for review`
- `### 4.6 Revisions` → `### 5.6 Revisions`
- `### 4.7 Write approved files` → `### 5.7 Write approved files`
- References to `Step 4.1`, `Step 4.6`, `Step 5` within text bodies also updated
- `## Step 5 — Mark released` → `## Step 6 — Mark released`
  - `Step 4.1` references inside Step 5 → `Step 5.1`
- `## Step 6 — Commit` → `## Step 7 — Commit`

**Key body text updates in renumbered steps:**
- Step 5 (was 4), section 5.1: "If no active package found in `RELEASE_BACKLOG.md`, fall back:" — no change needed.
- Step 5.5 (was 4.5): `*Drafts follow REQ-PROC-037 (Marketing Writing Rules). Type **approve** to write and continue, or describe what to change.*` — update: "to write and continue, or describe what to change." → reference is unchanged, just in step 5 now.
- Step 5.7 (was 4.7): `"Marketing release notes written to \`releases/[version]/\`."` — unchanged.
- Step 6 (was 5) "active package was found from RELEASE_BACKLOG.md in Step 4.1" → update to "Step 5.1".
- Step 7 (was 6): `Use the \`claude-commit\` skill` — unchanged.

---

## File 3: `scripts/smoke_test_windows.ps1`

### Full script structure

```powershell
# smoke_test_windows.ps1
# Builds the Windows release candidate and runs smoke integration tests.
# Run this script from the project root on the Windows host (not inside WSL2).
# Exit code 0 = all tests passed. Exit code 1 = build or test failure.

param(
    [string]$ProjectRoot = $PSScriptRoot + "\.."
)

$ErrorActionPreference = "Stop"

Write-Host "=== Smoke Test: Windows Release Candidate ==="
Write-Host ""

# Step 1: Build Windows release
Write-Host "Step 1: Building Windows release..."
Push-Location $ProjectRoot
try {
    flutter build windows --release
    if ($LASTEXITCODE -ne 0) {
        Write-Host -ForegroundColor Red "ERROR: flutter build windows --release failed (exit code: $LASTEXITCODE)."
        exit 1
    }
    Write-Host -ForegroundColor Green "Build succeeded."
} finally {
    Pop-Location
}

Write-Host ""

# Step 2: Run smoke integration tests
# Uses the individual test runner pattern from scripts/integration_test_runner/
# Only runs tests covering critical end-to-end flows for smoke validation.
Write-Host "Step 2: Running smoke integration tests..."

$testSuiteFile = "integration_test\integration_suite_test.dart"

# Smoke-relevant test names — critical end-to-end flows only.
# These cover: app launch, role selection, navigation to main screens.
# Update this list when new smoke-critical tests are added.
$smokeTests = @(
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow First Launch - Shows Onboarding Screen and Dialog",
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow Select Therapist Role - Navigates to PlansScreen",
    "Role Selection Flow Role Selection Flow Tests Onboarding Flow Select Client Role - Navigates to DataInputScreen",
    "Role Selection Flow Role Selection Flow Tests Post-Onboarding Flow (Client) App Launch - Client Role Already Selected - Navigates to DataInputScreen",
    "Role Selection Flow Role Selection Flow Tests Post-Onboarding Flow (Therapist) App Launch - Therapist Role Already Selected - Navigates to PlansScreen",
    "Simple Launch Simple App Launch Test with Mock Bloc (pumpWidget, Set Size) App pumps MyApp and finds DataInputScreen after pumps"
)

$allPassed = $true
$failedTests = @()

Push-Location $ProjectRoot
try {
    foreach ($testName in $smokeTests) {
        Write-Host "  Running: $testName"
        $output = flutter test $testSuiteFile --plain-name "$testName" -d windows *>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            Write-Host -ForegroundColor Red "  FAILED: $testName"
            $allPassed = $false
            $failedTests += $testName
        } else {
            Write-Host -ForegroundColor Green "  PASSED: $testName"
        }
    }
} finally {
    Pop-Location
}

Write-Host ""
if ($allPassed) {
    Write-Host -ForegroundColor Green "=== SMOKE TEST RESULT: PASS ==="
    Write-Host "All $($smokeTests.Count) smoke tests passed."
    exit 0
} else {
    Write-Host -ForegroundColor Red "=== SMOKE TEST RESULT: FAIL ==="
    Write-Host "$($failedTests.Count) of $($smokeTests.Count) smoke tests failed:"
    foreach ($t in $failedTests) {
        Write-Host "  - $t"
    }
    exit 1
}
```

---

## File 4: `scripts/smoke_test_llm.py`

### Full script structure

Uses the Claude API (claude-haiku-4-5-20251001 for cost efficiency; image input only — no computer use).
Requires `ANTHROPIC_API_KEY` in environment.
Runs on Windows (not inside WSL2); uses PIL for screenshot capture.

```python
#!/usr/bin/env python3
"""
smoke_test_llm.py — LLM visual smoke test for the Windows release binary.

Launches the Windows release binary, waits for startup, captures a screenshot,
sends it to the Claude API for a visual pass/fail verdict.

Advisory only — exits 0 on PASS, exits 1 on FAIL or error.

Requirements:
  pip install anthropic pillow
  ANTHROPIC_API_KEY environment variable must be set.

Run from the project root on the Windows host (not inside WSL2).
"""

import base64
import io
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    from PIL import ImageGrab
except ImportError:
    print("ERROR: pillow package not installed. Run: pip install pillow")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
RELEASE_EXE = PROJECT_ROOT / "build" / "windows" / "x64" / "runner" / "Release" / "private_mood_tracker.exe"
STARTUP_WAIT_SECONDS = 6
MODEL = "claude-haiku-4-5-20251001"

VISION_PROMPT = (
    "This is a screenshot of a Flutter mood tracker desktop app after launch on Windows. "
    "The app is called 'Private Mood Tracker'. "
    "Respond with exactly 'PASS' on the first line if:\n"
    "  - The app window is visible and not blank\n"
    "  - No error dialog, crash report, or white/black empty screen is shown\n"
    "  - The app shows either an onboarding screen, a role selection screen, or a main screen\n"
    "Respond with 'FAIL: <reason>' on the first line if:\n"
    "  - The screen is blank or black\n"
    "  - An error dialog or crash report is visible\n"
    "  - The app window is not visible at all\n"
    "  - There is obvious visual corruption (garbled UI, overlapping elements that indicate a render crash)\n"
    "After the first line, optionally add one sentence describing what you see."
)


def find_release_exe() -> Path:
    """Locate the release executable. Searches common name variants."""
    candidates = [
        RELEASE_EXE,
        PROJECT_ROOT / "build" / "windows" / "x64" / "runner" / "Release" / "mood_tracker.exe",
    ]
    # Also search for any .exe in the Release folder
    release_dir = PROJECT_ROOT / "build" / "windows" / "x64" / "runner" / "Release"
    if release_dir.exists():
        for exe in release_dir.glob("*.exe"):
            if exe not in candidates:
                candidates.append(exe)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return RELEASE_EXE  # Return primary path even if missing (error will be reported below)


def take_screenshot() -> str:
    """Capture the primary screen and return as base64-encoded PNG."""
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    exe_path = find_release_exe()
    if not exe_path.exists():
        print(f"ERROR: Release executable not found: {exe_path}")
        print("       Run smoke_test_windows.ps1 first to build the release binary.")
        sys.exit(1)

    print(f"Launching: {exe_path}")
    proc = subprocess.Popen([str(exe_path)])

    print(f"Waiting {STARTUP_WAIT_SECONDS}s for app to start...")
    time.sleep(STARTUP_WAIT_SECONDS)

    print("Capturing screenshot...")
    screenshot_b64 = take_screenshot()

    print(f"Sending screenshot to Claude API ({MODEL}) for visual review...")
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screenshot_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": VISION_PROMPT,
                    },
                ],
            }
        ],
    )

    verdict = response.content[0].text.strip()
    first_line = verdict.split("\n")[0].strip()

    print("")
    print(f"LLM verdict: {verdict}")
    print("")

    # Terminate the app
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        pass

    if first_line.upper().startswith("PASS"):
        print("=== LLM SMOKE TEST: PASS ===")
        sys.exit(0)
    else:
        print("=== LLM SMOKE TEST: FAIL ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## File 5: `CLAUDE.md` — Scripts table addition

In the `## 10. Generated Files (Scripts Reference)` section, under `**Scripts that modify (not create) files:**`, add two new entries under the existing list (or in a new subsection).

The two new scripts are **not** generated files and **not** query-only scripts — they are operation scripts run by the developer on Windows. Add a new subsection:

**New subsection to add after the existing "Scripts that modify (not create) files:" list:**

```
**Windows release scripts (run on Windows host, not in WSL2):**
- `scripts/smoke_test_windows.ps1` — builds Windows release candidate and runs smoke integration tests; exits 0 on pass
- `scripts/smoke_test_llm.py` — launches release binary, captures screenshot, calls Claude API for visual pass/fail verdict; exits 0 on PASS (requires `ANTHROPIC_API_KEY`)
```

---

## Implementation Order

1. Add `parse_frontmatter()` and `find_goal_files()` helpers to `check_release_preconditions.py`
2. Add Check 2b (release_description warning) in `main()`
3. Replace Check 4 with the coverage-extended version (keep `--coverage` flag, add `check_line_coverage()`)
4. Add `check_line_coverage()` helper + `COVERAGE_THRESHOLD` constant
5. Update `.claude/skills/release/skill.md`: insert Step 2, renumber Steps 2–6 → 3–7, update cross-references
6. Create `scripts/smoke_test_windows.ps1`
7. Create `scripts/smoke_test_llm.py`
8. Update `CLAUDE.md` scripts table

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `coverage/lcov.info` missing (tests never ran `--coverage` before) | `check_line_coverage()` handles missing file: prints ERROR and returns `(False, 0.0)` |
| Generated `.dart` files inflate untested-file penalty | Skip `*.g.dart` and `*.freezed.dart` in lib scan |
| `target_release` field not set on older tasks | Check 2b only fires for tasks where `target_release == release_version`; tasks without the field are silently skipped (they won't match) |
| Windows exe name differs from `private_mood_tracker.exe` | `find_release_exe()` falls back to any `.exe` in the Release directory |
| PIL / anthropic not installed on Windows machine | Script prints clear installation instructions and exits 1 |
| Step renumbering breaks inline cross-references in skill.md | All `Step 4.x` → `Step 5.x`, `Step 4.1` → `Step 5.1` in Step 6 body text — must be audited carefully |

---

## Test Plan

After implementation:
1. Run `python scripts/check_release_preconditions.py` (dry run in container — will fail on `flutter test` unless test suite passes, which is expected).
2. Manually verify that `check_release_preconditions.py` prints Check 2b and Check 4b output in the correct positions.
3. Read `skill.md` and verify step numbers are sequential 1–7 with no gaps.
4. Verify `smoke_test_windows.ps1` has correct syntax (PowerShell syntax check: `pwsh -Command "Get-Content scripts/smoke_test_windows.ps1 | Out-Null"` — checks for parse errors).
5. Verify `smoke_test_llm.py` imports are correct and script is parseable (`python3 -m py_compile scripts/smoke_test_llm.py`).
6. Confirm CLAUDE.md table has both new script entries.
7. Run `flutter test` (existing tests) to confirm nothing is broken.
