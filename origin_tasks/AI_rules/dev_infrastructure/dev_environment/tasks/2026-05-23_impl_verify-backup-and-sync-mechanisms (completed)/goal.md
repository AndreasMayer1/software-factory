---
task_id: TASK-PROC-054-03
type: impl
parent_requirement: REQ-PROC-054
urgency: 4
urgency_reason: U4-FAIL
impact: 5
impact_reason: I5-ENAB
status: completed
effort: S
created: 2026-05-23
started: 2026-05-26
completed: 2026-05-26
session_completed_at: 2026-05-25T23:31:17Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-09, AC-05, AC-01]
  sections: []
scope_description: "Verify that all backup and syncing mechanisms documented in the setup guides work correctly in the current devcontainer environment"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 0724300a
  file: ../requirements.md
session_id: a4ea88a3-9cdf-47ff-b228-b040b45ab6fb
session_account: gmail
---
# Goal: Verify backup and sync mechanisms

## Objective

Confirm that every backup and syncing mechanism documented in the setup guides (`backup_and_restore.md`, `sync_setup.md`, `wsl_devcontainer_setup.md`) is operational in the current devcontainer environment. Document pass/fail for each mechanism and fix any that are broken.

## Requirements Summary

REQ-PROC-054 AC-09 requires three independent recovery layers (GitHub remote, git bundle to cloud-synced backup, NTFS mirror). AC-05 requires the Mutagen sync to NTFS. AC-01 defines the supported configuration including bind-mounts for Claude config and CCS state.

For complete requirements at task creation time:
```
git show 0724300a:requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

1. **CCS backup mechanism**
   - Verify cron is running: `sudo service cron status`
   - Verify cron job is installed: `cat /etc/cron.d/ccs-backup`
   - Run healthcheck: `check-ccs-backup-health.sh` — should print OK, < 35 min old
   - Run a manual backup: `backup-ccs.sh` — should succeed without errors
   - Verify tarball exists and is recent in `~/.ccs-container/`
   - Verify 3-copy retention policy (at most 3 tarballs)

2. **Git bundle backup (pre-push hook)**
   - Verify `.githooks/pre-push` exists and is executable
   - Verify `git config core.hooksPath` points to `.githooks/`
   - Verify `~/backup/flutter_app.bundle` exists — check `ls -lh ~/backup/flutter_app.bundle`
   - Verify the bundle is valid: `git bundle verify ~/backup/flutter_app.bundle`

3. **Parent-config backup (pre-push hook)**
   - Verify `~/backup/_parent_.devcontainer/` exists and contains `setup.sh`
   - Verify `~/backup/_parent_.vscode/` exists and contains `tasks.json`
   - Compare contents with `/workspaces/private_mood_tracker/.devcontainer/` and `/workspaces/private_mood_tracker/.vscode/`

4. **Claude config bind-mount**
   - Verify `~/.claude/settings.json` exists and is readable/writable
   - Verify the mount is live (not a stale copy): write a temporary marker, confirm it persists

5. **Mutagen sync**
   - Verify Mutagen daemon is running
   - Run `mutagen sync list` — should show `flutter-app-to-windows` session
   - Verify status: `Watching for changes`, both endpoints `Connected`, 0 conflicts, 0 transition problems
   - Test propagation: create a temporary file in the container tree, verify it appears in `~/windows_mirror/`, then delete it

6. **DrvFs ownership**
   - Verify bind-mount directories are owned by vscode: `ls -ld ~/backup/ ~/windows_mirror/ ~/.claude/ ~/.ccs-container/`
   - All should show `vscode vscode` ownership

7. **Document results**
   - Log each check's pass/fail status in the protocol
   - If any mechanism is broken, document the failure and fix it
   - Final protocol entry summarizes overall health status

### Out of Scope
- Implementing new backup mechanisms
- Changing the sync configuration
- Windows-side verification (smoke tests, Build-Win)
- Android device setup verification

## Acceptance Criteria

- [x] CCS backup cron is running and healthcheck reports OK
- [x] Git bundle exists, is recent, and passes `git bundle verify`
- [x] Parent-config backup matches live `.devcontainer/` and `.vscode/`
- [x] Claude config bind-mount is live and writable
- [x] Mutagen sync session is healthy (Watching, Connected, 0 conflicts)
- [x] DrvFs ownership is correct (vscode:vscode) on all bind-mount roots
- [x] All results documented in protocol with pass/fail per mechanism

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

Reference docs:
- `setup_guides/backup_and_restore.md` §3 (Quick healthcheck)
- `setup_guides/sync_setup.md` §5, §8 (Verify sync, Healthcheck and recovery)
- `setup_guides/wsl_devcontainer_setup.md` §9 (Verify the environment)
