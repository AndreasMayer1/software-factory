# Plan: document sleep-watcher scripts under REQ-PROC-054

## Context

Two Windows-host PowerShell scripts already exist:
- `scripts/windows/sleep_when_autorun_done.ps1` — watches `automation/state.json`
  (`is_running`, `rate_limit_reached`, `next_wake_time`, `rate_limited_until`),
  suspends the host, and registers a fixed-name SYSTEM scheduled task
  (`AutorunWakePC`) to wake the PC before the earliest rate-limit reset.
- `scripts/windows/win_sleep_script_wrapper.ps1` — shortcut-friendly wrapper:
  disables console QuickEdit, truncates the log, forwards to the main script.

Their relationship to REQ-PROC-054's no-host-bridge contract was undocumented.

## Threat-model analysis (why this is AC-07-class, not AC-03-forbidden)

- The deleted bridge polled for **commands to execute** (every whitelisted tool
  interpreted container-writable project files on the host → full host privilege
  while watcher online). That is AC-03's forbidden pattern.
- The sleep watcher reads **state to react to** with a fixed, narrow action set:
  suspend, and register a fixed-name wake task at a time derived from
  state.json. A hostile container can influence only *whether/when* the host
  sleeps and wakes — a DoS/convenience surface, not arbitrary execution.
- This is the same security profile as the AC-07 Android-emulator watcher,
  which the requirement already permits.

## V7 consideration → install outside the repository

V7 (from the TASK-PROC-054-01 pen-test) = LLM modifies a repo-tracked file →
user runs it under trust. If the watcher's `.ps1` runs **from the repo or the
Mutagen mirror**, a hostile commit modifies the exact file that later runs as
admin. The mitigation (chosen "Option C") is to install the script outside the
repository, on a Windows path the container cannot write to, and re-copy on
intentional updates. State.json influence remains, but it is bounded to timing.

## Changes

1. `requirements.md`:
   - AC-03: add a clause clarifying command-executing vs. fixed-narrow-action
     state-reactive watchers.
   - New AC-13: the optional sleep watcher, constraints as above.
   - YAML `trackable_items.acceptance_criteria`: add AC-13.
   - Common Pitfalls: add the mirror/UNC warning.
   - Possibly mention the watcher in the integration-test-mechanism / manual-ops
     narrative — keep minimal; AC-13 + pitfall is the core.
2. `setup_guides/sync_setup.md`: add a "Windows-host sleep watcher" section with
   install/operation procedure (copy outside repo, shortcut Target, admin,
   log location, re-copy discipline). Chose sync_setup.md over a new file
   because the watcher is Windows-host operational infra adjacent to the mirror
   topic already covered there.

## Status assessment

Requirement is a living document (`status: active`) → stays `active`.
No `implements_flows` in YAML → no upstream flow impact.
