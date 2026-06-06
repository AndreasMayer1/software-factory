# Plan: Automation Scripts (TASK-PROC-036-02)

Date: 2026-03-10
Agent ID: architecture-advisor-20260310-001
Status: Ready for implementation approval

---

## 1. Summary of Findings

### Existing Code That Can Be Reused

- **`scripts/next_tasks.py`**: Contains all the logic for scanning `requirements_tasks/` goal.md files, parsing YAML frontmatter, filtering by `target_release`, and identifying open/pending tasks. The key functions are `load_tasks()`, `rank_tasks()`, and `find_next_release()`. The script supports `--release <version>` and `--count <N>` arguments.
- **`requirements_tasks/RELEASES.md`**: Located at `requirements_tasks/RELEASES.md` (not at project root). Contains YAML frontmatter with a `releases:` list. Each entry has `version:` and `status:` fields. The script must parse this file.
- **`pubspec.yaml`**: Located at project root. Version field currently absent (no `version:` line exists), but the format when present is `X.Y.Z+N` per Flutter convention. The bump logic must handle the case where no version line currently exists.
- **`scripts/complete_task.ps1`**: Style reference for PowerShell scripts in this project — param block at top, `Write-Error`/`Write-Host` for output, `exit 0`/`exit 1` for status codes, try/catch for risky operations.

### Key Observations

1. **pubspec.yaml has no version field currently**: The script must handle this gracefully. When bumping to `X.Y.Z`, if no `version:` line exists, it should insert `version: X.Y.Z+1`. If a version line exists, it should parse the `+N` build number and increment by 1.
2. **RELEASES.md uses YAML frontmatter**: The `releases:` list is inside `---` delimiters at the top of the file. The status field is a simple scalar (`status: planned`, `status: active`, `status: released`). Parsing requires reading within the frontmatter block only.
3. **next_tasks.py --release flag**: The script accepts `--release 0.0.1` to filter tasks for a specific release. The `open_count` computed in `main()` is the number of non-terminal, non-blocked tasks for that release. If `open_count > 0`, pending tasks remain.

---

## 2. RELEASES.md Parsing Approach

The RELEASES.md file has YAML frontmatter (between `---` delimiters) containing a `releases:` list. Each release is a YAML mapping with `version:` and `status:` fields.

**Strategy for PowerShell**: Parse line by line within the frontmatter block. Track which release entry we're currently inside by watching for `- version:` lines. When we find a line matching `status: active` while inside a release entry, capture the version from the previously seen `- version:` line.

**Regex approach**:
1. Read all lines of `requirements_tasks/RELEASES.md`
2. Find the opening `---` and closing `---` to bound the frontmatter
3. Within frontmatter, scan for `^\s*-\s+version:\s+"?([^"]+)"?` to capture version
4. On next `status:` line within the same entry, check if value is `active`
5. When found, return that version; if not found, error out

**Why line-by-line rather than a YAML library**: PowerShell has no built-in YAML parser, and installing modules is not viable in a CI/automation context. The RELEASES.md format is simple and well-structured enough for regex-based line parsing. The pattern has been validated against the actual file structure observed.

**Edge case**: Only one `status: active` entry should exist (enforced by `requ-prep-release`). If zero are found, the script fails with a clear message. If multiple are found (data integrity violation), the script uses the first and warns.

---

## 3. next_tasks.py Reuse Strategy

**Strategy**: Call `next_tasks.py` as a subprocess from PowerShell, passing `--release <version> --count 100` (large count to ensure all open tasks are surfaced). Then check the output for `Open tasks: 0`.

**Approach**:
```powershell
$result = python scripts/next_tasks.py --release $releaseVersion --count 100
# Parse the "Open tasks: N" line
$openTasksLine = $result | Select-String -Pattern "Open tasks: (\d+)"
$openCount = [int]$openTasksLine.Matches[0].Groups[1].Value
if ($openCount -gt 0) { ... fail ... }
```

**Why subprocess over reimplementing**: `next_tasks.py` already has correct frontmatter parsing with BOM handling, blocked-task filtering, terminal-status exclusion, and `--release` filtering. Reimplementing this in PowerShell would duplicate ~200 lines of tested logic and create a maintenance split. The output format (`Open tasks: N`) is stable and machine-readable.

**Fallback**: If `python` is not available or the script errors, the subprocess call will fail with a non-zero exit code, which the PowerShell script will detect and surface as a clear error.

---

## 4. check_release_preconditions.ps1 Design

**File**: `scripts/check_release_preconditions.ps1`
**Location**: Project root via `scripts/` (same as all other scripts)
**Exit codes**: 0 = all pass, 1 = one or more checks failed

### Checks (in order)

**Check 1: Active release exists in RELEASES.md**
- Parse `requirements_tasks/RELEASES.md` for `status: active`
- On failure: `"ERROR: No active release found in requirements_tasks/RELEASES.md. Run requ-prep-release first."`
- On success: extract `$releaseVersion`

**Check 2: No pending/open tasks for the active release**
- Run: `python scripts/next_tasks.py --release $releaseVersion --count 100`
- Parse output line `Open tasks: N`
- On failure (N > 0): `"ERROR: $N open task(s) remain for release $releaseVersion. Complete all tasks before releasing."`
- On success: continue

**Check 3: develop branch is clean**
- Run: `git status --porcelain`
- On failure (output non-empty): `"ERROR: Develop branch has uncommitted changes. Commit or stash all changes before releasing."`
- On success: continue

**Check 4: Local tests pass**
- Run: `flutter test -d windows`
- On failure (exit code non-zero): `"ERROR: Flutter tests failed. Fix all test failures before releasing."`
- On success: continue

**Check 5: pubspec.yaml version does not match release version**
- Parse `pubspec.yaml` for `version:` line, extract `X.Y.Z` part (strip `+N` build)
- If version line absent: check passes (not yet bumped, safe to proceed)
- If version matches `$releaseVersion`: `"ERROR: pubspec.yaml version already matches $releaseVersion. The version was already bumped — execute_release.ps1 may have been run already."`
- On success: continue

### Output on all-pass
```
[OK] Active release: 0.0.1
[OK] No pending tasks for release 0.0.1
[OK] Develop branch is clean
[OK] All tests pass
[OK] pubspec.yaml version not yet bumped
All preconditions met. Safe to run execute_release.ps1.
```

### Script skeleton
```powershell
param()
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$failed = $false

# --- Check 1: Active release ---
# ... parse RELEASES.md ...
if (-not $releaseVersion) {
    Write-Host "ERROR: ..."
    $failed = $true
}

# --- Check 2: No pending tasks ---
# ... call next_tasks.py ...

# --- Check 3: Clean branch ---
# ... git status --porcelain ...

# --- Check 4: Tests pass ---
# ... flutter test -d windows ...

# --- Check 5: Version not bumped ---
# ... parse pubspec.yaml ...

if ($failed) { exit 1 }
Write-Host "All preconditions met. Safe to run execute_release.ps1."
exit 0
```

**Important**: All checks run to completion even if earlier ones fail (collect all errors), then exit 1 if any failed. This gives the developer the full picture in one run.

---

## 5. execute_release.ps1 Design

**File**: `scripts/execute_release.ps1`
**Precondition**: Must be run after `check_release_preconditions.ps1` exits 0
**Exit codes**: 0 = success, 1 = failure (with recovery instructions)

### Parameters
```powershell
param(
    [switch]$DryRun  # Optional: print commands without executing (for testing)
)
```

### Step sequence

**Step 0: Determine active release version**
- Parse `requirements_tasks/RELEASES.md` for `status: active` (same logic as check script)
- Fail immediately if not found

**Step 1: Bump version in pubspec.yaml**
- Read all lines of `pubspec.yaml`
- Find line matching `^version:\s+`
- If found: parse `X.Y.Z+N`, replace with `$releaseVersion+($N+1)`
- If not found: insert `version: $releaseVersion+1` after the `description:` line
- Write all lines back to `pubspec.yaml`
- Print: `[Step 1] Bumped pubspec.yaml version to $releaseVersion+$newBuildNumber`

**Step 2: git add pubspec.yaml**
```powershell
git add pubspec.yaml
```

**Step 3: git commit**
```powershell
git commit -m "chore: bump version to v$releaseVersion"
```

**Step 4: git checkout master**
```powershell
git checkout master
```

**Step 5: git merge develop --no-ff**
```powershell
git merge develop --no-ff -m "release: v$releaseVersion"
```

**Step 6: git tag**
```powershell
git tag -a "v$releaseVersion" -m "Release v$releaseVersion"
```

**Step 7: git push origin master**
```powershell
git push origin master
```

**Step 8: git push origin tag**
```powershell
git push origin "v$releaseVersion"
```

**Step 9: git checkout develop**
```powershell
git checkout develop
```

### Error handling
Each git command is wrapped in a check: if the command exits non-zero, the script prints:
```
ERROR: Step N (git <command>) failed.
To recover manually, run:
  <remaining commands listed>
```
Then exits 1. No retry loops. Developer follows the printed recovery steps.

### Version bump logic details
- Input: current `version:` line value (e.g., `1.2.3+7`) or absent
- Output: `$releaseVersion+$nextBuild` (e.g., `0.0.1+1`)
- If current line is `0.0.1+3` and release is `0.0.1`: result is `0.0.1+4`
- If current line is `0.0.0+99` and release is `0.0.1`: result is `0.0.1+100` (build always increments)
- If version line absent: insert `version: 0.0.1+1`

---

## 6. CLAUDE.md Update

The scripts table in CLAUDE.md section 10 needs two new rows added to the "Scripts that modify (not create) files" section, since both scripts modify `pubspec.yaml` and the git state respectively but do not generate a dedicated output file.

Actually, reviewing more carefully: these scripts are operational tools (not file generators), so they belong under a new subsection or in the existing "Scripts that modify" bullet list.

**Proposed addition** — add two new bullets under "Scripts that modify (not create) files:":
```
- `scripts/check_release_preconditions.ps1` — validates release preconditions (active release in RELEASES.md, no pending tasks, clean branch, tests pass, version not yet bumped); exits 0 on pass
- `scripts/execute_release.ps1` — bumps `version:` in `pubspec.yaml`, then merges develop → master, creates annotated tag, and pushes; run only after check script exits 0
```

---

## 7. File List

### Files to Create

| File | Type | Description |
|------|------|-------------|
| `scripts/check_release_preconditions.ps1` | New | Pre-flight check script |
| `scripts/execute_release.ps1` | New | Release execution script |

### Files to Modify

| File | Change |
|------|--------|
| `CLAUDE.md` | Add two bullet entries under "Scripts that modify (not create) files" in section 10 |

### Files NOT to Touch
- `scripts/next_tasks.py` — used as-is via subprocess call
- `requirements_tasks/RELEASES.md` — read-only by these scripts (setting `status: released` is done by the `/release` skill, not by `execute_release.ps1`)
- `pubspec.yaml` — modified by `execute_release.ps1` at runtime (not modified here)

---

## 8. Open Questions / Risks

1. **Python availability**: `check_release_preconditions.ps1` calls `python scripts/next_tasks.py`. If `python` is not on PATH (e.g., `python3` alias), the script will fail. Mitigation: try `python` first, fall back to `python3`, error with clear message if neither works.

2. **Git remote not configured**: `execute_release.ps1` pushes to `origin`. If the remote is not set up, git push will fail. The error message should direct the developer to `releases/SETUP_GUIDE.md` (created by TASK-PROC-036-01).

3. **pubspec.yaml version line position**: The version line insertion (when absent) targets "after the description line". The actual pubspec.yaml currently has `name:` then `description:` then `environment:`. Inserting after `description:` is safe and follows Flutter convention.

4. **`$ErrorActionPreference = "Stop"` scope**: Using Stop mode in PowerShell means any non-terminating error becomes terminating. This is appropriate for these scripts — any unexpected failure should halt execution. However, `git` commands return non-zero via exit code, not PowerShell errors. We must explicitly check `$LASTEXITCODE` after each git command.

5. **No tests for scripts**: PowerShell scripts in this project have no test suite (no Pester tests). The acceptance criteria do not require automated tests for the scripts themselves. Manual testing against a dry-run flag covers the execution path.
