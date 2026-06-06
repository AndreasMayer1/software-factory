---
task_id: TASK-PROC-036-02
type: impl
parent_requirement: REQ-PROC-036
urgency: 3
urgency_reason: U3-PROC
impact: 4
impact_reason: I4-ENAB
status: completed
completed: 2026-03-10
effort: M
created: 2026-03-10
after: [TASK-PROC-036-05, TASK-PROC-036-06]
awaiting: []
awaiting_note: ""
release_description: "Add pre-flight check and release execution scripts"
covers:
  acceptance_criteria: []
  sections: [SEC-02]
target_package: "Transfer Data Model"
scope_description: "Create check_release_preconditions.ps1 and execute_release.ps1."
requirements_version:
  commit: 8aeefd9
  file: ../requirements.md
---

# Goal: Automation Scripts

## Objective

Create two PowerShell scripts that handle the deterministic parts of the release:
- `scripts/check_release_preconditions.ps1`: validates all preconditions
- `scripts/execute_release.ps1`: bumps pubspec.yaml version, merges, tags, pushes

## Requirements Summary

Covers SEC-02 (Automation Scripts) of REQ-PROC-036.

Current requirements: ../requirements.md

## Scope

### In Scope
- `scripts/check_release_preconditions.ps1`
  - Reads active release from RELEASES.md (`status: active`)
  - Calls existing "next task" script logic to check no pending tasks remain for the active release
  - Verifies develop branch is clean
  - Runs `flutter test -d windows`
  - Verifies pubspec.yaml version does not yet match release version
  - Exits 0 on pass, non-zero with clear per-check error message on failure
- `scripts/execute_release.ps1`
  - Bumps `version:` in pubspec.yaml (format: `X.Y.Z+[build]`, build +1)
  - Separate `git add pubspec.yaml`, then `git commit`
  - `git checkout master`, `git merge develop --no-ff`, `git tag -a`, `git push origin master`, `git push origin vX.Y.Z`, `git checkout develop`
  - Each git command runs separately (no `&&` chaining)

### Out of Scope
- GitHub Actions workflow file (documented in SETUP_GUIDE, set up manually by developer)
- Release notes generation (TASK-PROC-036-03 and -04)

## Acceptance Criteria

- [ ] `check_release_preconditions.ps1` exits 0 when all checks pass
- [ ] Each failed check prints a specific, actionable error message and exits non-zero
- [ ] Script correctly identifies the active release from RELEASES.md
- [ ] Script reuses existing next-task logic to verify no pending tasks remain
- [ ] `execute_release.ps1` bumps pubspec.yaml version correctly
- [ ] All git commands in `execute_release.ps1` run as separate calls (no `&&`)
- [ ] Both scripts are listed in CLAUDE.md scripts table

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-036-06 | pending | requ-prep-release must set status: active so the script can find the active release |

## Notes

- Check what "next task" script already exists before writing new logic — reuse or call it directly.
- The build number in pubspec.yaml (`X.Y.Z+N`) should increment by 1 from the current value.
