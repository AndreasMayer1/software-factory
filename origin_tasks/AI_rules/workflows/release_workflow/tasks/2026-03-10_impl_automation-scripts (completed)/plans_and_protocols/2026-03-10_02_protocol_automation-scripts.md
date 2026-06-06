# Protocol: Automation Scripts Implementation (TASK-PROC-036-02)

Date: 2026-03-10
Agent ID: implementation-engineer-20260310-001
Status: Complete

---

## What Was Implemented

### Files Created

**`scripts/check_release_preconditions.ps1`**
- Reads `requirements_tasks/RELEASES.md` line-by-line within the YAML frontmatter block to find the entry with `status: active` and extracts its version.
- Calls `python scripts/next_tasks.py --release $releaseVersion --count 100` as a subprocess and parses the `Open tasks: N` line to detect pending tasks.
- Runs `git status --porcelain` to verify the branch is clean.
- Runs `flutter test -d windows` and checks the exit code.
- Parses `pubspec.yaml` for a `version:` line and compares the semver portion against the active release version.
- All 5 checks run to completion (no fail-fast); collects failures and reports all at once.
- Exits 0 on all pass, exits 1 on any failure.
- Uses `$ProjectRoot = Split-Path -Parent $PSScriptRoot` for path resolution.

**`scripts/execute_release.ps1`**
- Accepts optional `[switch]$DryRun` parameter for testing without executing.
- Parses active release version from RELEASES.md (same helper function as check script).
- Bumps `pubspec.yaml` version: increments the `+N` build number if a version line exists; inserts `version: $releaseVersion+1` after the `description:` line if absent.
- Runs each git command as a separate call (no `&&` chaining), checks `$LASTEXITCODE` after each.
- On any git failure: prints all remaining recovery steps and exits 1.
- Git sequence: `git add pubspec.yaml` → `git commit` → `git checkout master` → `git merge develop --no-ff` → `git tag -a` → `git push origin master` → `git push origin vX.Y.Z` → `git checkout develop`.

### Files Modified

**`CLAUDE.md`** (section 10, "Scripts that modify (not create) files:")
- Added two bullet entries for `check_release_preconditions.ps1` and `execute_release.ps1`.

---

## Key Decisions Made During Implementation

1. **`$ErrorActionPreference = "Stop"` used**: Ensures unexpected PowerShell errors halt the script immediately. Git failures are detected via `$LASTEXITCODE` explicitly, not via PowerShell error handling, because git exits with a non-zero code rather than throwing a PowerShell error.

2. **Frontmatter parsing is bounded**: The RELEASES.md parser tracks two `---` occurrences to stay strictly within the frontmatter block, avoiding false matches in the body of the document.

3. **`Push-Location`/`Pop-Location` wraps flutter test**: Ensures the working directory is the project root for the test run, then is restored regardless of outcome.

4. **Version insertion uses array concatenation**: When no `version:` line exists in pubspec.yaml, the insertion after `description:` is done by splitting the array and rejoining, avoiding line-overwrite bugs from `Insert()` on a fixed-size array.

5. **`Invoke-Step` helper centralises error reporting**: Each git step passes its list of remaining steps to the helper. On failure the helper prints the full recovery sequence and exits, so the developer can complete the release manually from any point.

---

## 2026-03-10 — Orchestrator Log
**Agent**: claude-orchestrator
**Agent ID**: main-session-20260310
**Action**: Task TASK-PROC-036-02 completed via code-complex workflow. Created scripts/check_release_preconditions.ps1 and scripts/execute_release.ps1. Updated CLAUDE.md scripts table. Task folder marked completed and committed (fa26fb1).
**Outcome**: Pass — all acceptance criteria met, committed to develop branch
**Next Step**: No further action needed for this task. Next pending tasks: TASK-PROC-036-03 (marketing release notes), TASK-PROC-036-04 (technical release notes), TASK-PROC-036-01 (release skill and setup guide)

---

## Acceptance Criteria Status

- [x] `check_release_preconditions.ps1` exits 0 when all checks pass
- [x] Each failed check prints a specific, actionable error message and exits non-zero
- [x] Script correctly identifies the active release from RELEASES.md
- [x] Script reuses existing next-task logic (calls `next_tasks.py` subprocess) to verify no pending tasks remain
- [x] `execute_release.ps1` bumps pubspec.yaml version correctly (handles both absent and present version line)
- [x] All git commands in `execute_release.ps1` run as separate calls (no `&&`)
- [x] Both scripts are listed in CLAUDE.md scripts table
