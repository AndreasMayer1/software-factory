---
task_id: TASK-PROC-054-04
type: explore
parent_requirement: REQ-PROC-054
urgency: 3
urgency_reason: U3-DEBT
impact: 3
impact_reason: I3-INCR
status: completed
effort: S
created: 2026-05-24
completed: 2026-05-24
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Document the relationship of the Windows-host sleep-watcher scripts (scripts/windows/sleep_when_autorun_done.ps1 + win_sleep_script_wrapper.ps1) to REQ-PROC-054's no-host-bridge contract, and the install/operation procedure."
release_description: ""
opus_recommended: false
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 4920c1d2
  file: ../../requirements.md
---

# Goal: Document the Windows-host sleep-watcher scripts under REQ-PROC-054

## Objective

The scripts `scripts/windows/sleep_when_autorun_done.ps1` and
`scripts/windows/win_sleep_script_wrapper.ps1` already exist. They run on the
Windows host, observe the orchestrator's `automation/state.json`, and suspend
the PC (registering a fixed-name scheduled wake task when the orchestrator is
rate-limited). Their relationship to REQ-PROC-054's no-host-bridge contract was
never documented, and there is no install/operation runbook.

Bring these scripts under the requirement's contract using the AC-07
Android-emulator-watcher precedent: a narrow host-side watcher that reads a
container-produced state file, takes a fixed and narrow set of actions, executes
no commands originating from container files, and is installed **outside** the
repository so the script that runs as admin is not LLM-writable through normal
commits.

## Requirements Summary

REQ-PROC-054 (`status: active`, living document). Relevant ACs:
- AC-03 forbids a host-execution bridge that polls for and executes whitelisted
  commands from container-controlled files.
- AC-07 already permits a narrow Windows-host watcher (Android emulator) that
  reads a sentinel file, reads no project files, and takes no parameters from
  the container — installed outside the repository.

## Scope

### In Scope
1. New **AC-13**: permit an optional Windows-host sleep watcher under
   AC-07-style constraints (installed outside the repo; action surface limited
   to OS suspend + registration of a fixed-name scheduled wake task; no command
   execution from container files; container influence bounded to state.json
   timing values).
2. New **Common Pitfall**: warn against pointing the sleep-watcher shortcut at
   the Mutagen mirror or `\\wsl$\…` — that makes the admin-run script
   LLM-writable through normal commits (V7-class regression).
3. **AC-03 clarification**: distinguish a watcher that *executes commands* from
   container files (forbidden) from a watcher with a *fixed, narrow action
   surface reacting to container state files* (permitted under AC-07 / AC-13).
4. Add the sleep-watcher install/operation procedure to a setup guide.

### Out of Scope
- Changing the scripts themselves.
- Implementing any new automation.

## Acceptance Criteria

- [x] REQ-PROC-054 has a new AC-13 covering the optional sleep watcher with the
      install-outside-repo constraint and the narrow action surface.
- [x] REQ-PROC-054 Common Pitfalls includes a warning against running the
      watcher from the Mutagen mirror or `\\wsl$\…` (V7-class regression).
- [x] AC-03 wording distinguishes command-executing watchers (forbidden) from
      fixed-narrow-action state-reactive watchers (permitted under AC-07/AC-13).
- [x] A setup guide documents the install (copy from `scripts/windows/`),
      re-copy-on-update discipline, shortcut Target example, admin requirement,
      and log location for the sleep watcher.
- [x] Requirement stays `status: active`; YAML `trackable_items` lists AC-13.
