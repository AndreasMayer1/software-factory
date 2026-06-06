---
task_id: TASK-PROC-061-03
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-27
completed: 2026-05-27
session_completed_at: 2026-05-27T08:14:13Z
effort: S
created: 2026-05-26
after: [TASK-PROC-061-01]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Integrate the mandatory per-release dependency sweep into the release workflow"
release_description: "Release workflow now blocks on dependency advisory sweep before any candidate ships."
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 3cbd51ab
  file: ../requirements.md
session_id: f9e542d4-ec73-4f4b-906a-b5dbf56c9508
session_account: gmail
---
# Goal: Release Sweep Integration

## Objective

Add the mandatory per-release dependency sweep (AC-03) as a gate in the release workflow (REQ-PROC-036). No release candidate may be approved while a known, unresolved security advisory exists for any pinned dependency. The sweep runs `flutter pub outdated` plus `osv-scanner` (or equivalent advisory scanner) over all in-scope manifests.

## Requirements Summary

AC-03: "Before any release candidate is approved, a mandatory dependency sweep runs: flutter pub outdated + osv-scanner (or equivalent advisory scanner) over all in-scope manifests. No release candidate ships with a dependency version for which a known, unresolved security advisory exists at the time of the sweep. This sweep is a gate on the release workflow (integration point with REQ-PROC-036)."

For complete requirements at task creation time:
```
git show 3cbd51ab:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

- Read the current release workflow (`release` skill and/or `release-begin-impl` / `release-status` skills) to identify where the dependency sweep gate should be inserted
- Check whether `osv-scanner` is installed in the devcontainer; if not, use `claude-install-os-tool` to add it, or identify an equivalent (pub.dev advisory warnings from `dart pub get` output, or `dart pub audit` if available)
- Add the sweep step to the release checklist / release skill at the correct gate point (before release candidate approval)
- The sweep step must: run the tools, capture output, fail the gate if any unresolved advisory is found, and escalate to the developer with findings
- Update the authoritative lifecycle doc (TASK-PROC-061-01 output) or release skill to document this gate

### Out of Scope

- Monthly cadence setup (TASK-PROC-061-02)
- Resolving any advisories found during this task (that is release-time work)
- Any changes to `lib/`, `test/`, or `integration_test/`

## Acceptance Criteria

- [x] `osv-scanner` (or equivalent) is available in the devcontainer and confirmed working
- [x] The release workflow has a dependency sweep step before release candidate approval
- [x] The sweep runs `flutter pub outdated` + advisory scanner over pub, Python scripts/, and any npm manifests
- [x] The sweep fails (blocks release) if an unresolved advisory is found for any pinned version
- [x] The gate is documented in the release skill or release checklist

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-061-01 | pending | Authoritative doc must exist to reference from release workflow |

## Notes

`osv-scanner` is Google's open-source vulnerability scanner for lock files — supports `pubspec.lock`, `requirements.txt`, and npm `package-lock.json`. Install via `osv-scanner` binary from GitHub releases or `go install github.com/google/osv-scanner/cmd/osv-scanner@latest`. Check the devcontainer first: `which osv-scanner`. The release skill is at `.claude/skills/release/SKILL.md`.
