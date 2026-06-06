---
task_id: TASK-PROC-036-07
type: impl
parent_requirement: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-04-19
completed: 2026-04-19
session_completed_at: 2026-04-19T17:05:08Z
session_id: b32f6c8c-6c09-4683-a2eb-9332a9c891db
session_account: gmail
effort: M
created: 2026-03-19
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-09]
target_package: "Transfer Data Model"
scope_description: "Add a Windows release GitHub Actions workflow that bundles VC++ runtime DLLs alongside the executable and uploads a self-contained ZIP artifact. Update check_release_preconditions.py to verify the artifact is deployment-complete."
release_description: "Windows release package runs on any machine without extra installation steps."
requirements_version:
  commit: af5994e
  file: ../requirements.md
---

# Implementation Task: Windows Deployment Completeness

## Requirement Reference
- **Requirement**: `requirements_tasks/process/AI_rules/workflows/release_workflow/requirements.md`
- **Section**: SEC-09 — Windows Deployment Completeness
- **Status**: Not Started

## Goal

Ensure that every Windows release artifact produced by GitHub Actions is self-contained and runs correctly on a clean Windows machine — one with no development tools or pre-installed Visual C++ Redistributables.

Background: A concrete crash was confirmed on a second laptop (`MSVCP140.dll` version mismatch, exception code `0xc0000005`, Windows Event Log). The root cause is that the current CI workflow (`build_windows.yml`) builds but does not produce a release artifact, and no Windows release workflow exists.

## Scope Overview

**Affected areas**:
- `.github/workflows/` — new `release_windows.yml` workflow (tag-triggered, produces artifact)
- `scripts/check_release_preconditions.py` — add Windows artifact completeness check

**Estimated files**: ~2 files (new workflow + script update)

**Patterns to follow**:
- `release.yml` — Android release workflow structure (tag trigger, artifact upload)
- `build_windows.yml` — Flutter Windows build steps

## What to Implement

### 1. New workflow: `.github/workflows/release_windows.yml`

Triggers on version tags (`v*.*.*`), same as the Android release workflow. Steps:
1. Checkout repository
2. Set up Flutter (stable)
3. Enable Windows desktop
4. `flutter pub get`
5. `flutter build windows --release`
6. Copy VC++ runtime DLLs from the GitHub Actions runner into the build output folder alongside `mood_tracker.exe`:
   - `vcruntime140.dll`
   - `vcruntime140_1.dll`
   - `msvcp140.dll`
   - `concrt140.dll`
   These DLLs are available on `windows-latest` runners under the Visual C++ Redistributable path.
7. ZIP the entire `build\windows\x64\runner\Release\` folder
8. Upload ZIP as a GitHub Actions artifact (retention: 30 days), named `mood_tracker-windows-{tag}`

### 2. Update `scripts/check_release_preconditions.py`

Add a check that verifies the Windows build output (if present locally) contains the required DLLs. If the build output is not present locally, the check passes with a warning: "Windows artifact not verified locally — confirm GitHub Actions artifact is complete after release."

## Acceptance Criteria

- [ ] A ZIP artifact named `mood_tracker-windows-{tag}` is produced by GitHub Actions on every version tag push
- [ ] The ZIP contains `vcruntime140.dll`, `vcruntime140_1.dll`, `msvcp140.dll`, `concrt140.dll` alongside `mood_tracker.exe`
- [ ] The app launches and the camera screen does not crash on a clean Windows machine (no Visual Studio installed) when installed from the artifact
- [ ] `check_release_preconditions.py` warns if local Windows build output is missing the required DLLs

## Dependencies

None — `release.yml` (Android) provides the structural pattern.

---

**Note**: This task describes WHAT to implement, not HOW.
The implementation plan will be created when this task is executed,
based on the current state of the codebase at that time.
