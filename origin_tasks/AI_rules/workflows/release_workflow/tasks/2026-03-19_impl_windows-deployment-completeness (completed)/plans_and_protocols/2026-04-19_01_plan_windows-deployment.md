---
date: 2026-04-19
agent: task-resolve/sonnet
status: approved
---

# Plan: Windows Deployment Completeness (TASK-PROC-036-07)

## Deliverables

1. **NEW** `.github/workflows/release_windows.yml` — tag-triggered Windows release workflow
2. **MODIFY** `scripts/check_release_preconditions.py` — add DLL completeness check (non-blocking warning)

## Execution Phases

### Phase 1 — Create `release_windows.yml`

Pattern sources: `release.yml` (tag trigger + artifact upload), `build_windows.yml` (Windows build steps + long-path fix).

Key steps:
- Trigger: `push: tags: v*.*.*`
- Runner: `windows-latest`
- Enable long paths (PowerShell registry + git config) — copied from `build_windows.yml`
- Flutter stable, cache: true
- `flutter config --enable-windows-desktop`
- `flutter pub get`
- `flutter build windows --release`
- Copy VC++ DLLs: try MSVC Redist dir first (`VC\Redist\MSVC\*\x64\Microsoft.VC143.CRT`), fallback System32; fail step if any DLL not found
  - Required: `vcruntime140.dll`, `vcruntime140_1.dll`, `msvcp140.dll`, `concrt140.dll`
- `Compress-Archive` → `mood_tracker-windows-{tag}.zip`
- `upload-artifact@v4`: name=`mood_tracker-windows-{ref_name}`, path=the zip, retention=30 days

### Phase 2 — Update `check_release_preconditions.py`

Add after Check 4 (tests pass) a new non-blocking warning:

**Check 4b — Windows build DLL completeness**:
- Look for `build/windows/x64/runner/Release/` (relative to PROJECT_ROOT)
- If directory does not exist → print warning and continue (non-blocking)
- If directory exists → check each of the 4 required DLLs; warn about any missing

### Phase 3 — Verify ACs

- [ ] Workflow file exists and has correct trigger, DLL copy step, zip, upload
- [ ] check_release_preconditions.py has the new check
- [ ] Existing tests still pass (script doesn't break anything)

## Success Check

All acceptance criteria in goal.md ticked off.
