# Protocol: execution

## Done

1. `requirements.md`:
   - **AC-03** — added a clause distinguishing a host-side process that
     *executes commands / interprets code* from container-writable files
     (forbidden) from a *fixed, narrow-action* watcher reacting to
     container-produced state (permitted; cross-refs AC-07 + AC-13).
   - **AC-13** (new) — optional Windows-host sleep watcher: action surface
     limited to suspend/hibernate + one fixed-name scheduled wake task
     (`AutorunWakePC`); no command strings/code from container files; only
     container influence is `state.json` timing; elevated run target installed
     outside the repo; `scripts/windows/…` is source of record. Added to YAML
     `trackable_items`.
   - **Key Decision** — "AC-13 sleep watcher is optional narrow-action watcher,
     not a bridge" (mirrors the sync-daemon operational-infra decision).
   - **Common Pitfall** — running the watcher from the Mutagen mirror or
     `\\wsl$\…` is a V7-class regression (elevated `.ps1` becomes LLM-writable
     via normal commits).
   - References — noted sync_setup.md now covers the watcher procedure.

2. `setup_guides/sync_setup.md`:
   - New §13 "Windows-host sleep watcher (optional)": what-it-does/why-not-a-
     bridge, install-outside-repo procedure (copy of `sleep_when_autorun_done.ps1`
     to `%LOCALAPPDATA%\…`), shortcut Target with `-ProjectPath %MUTAGEN_BETA%`,
     admin requirement, wrapper caveat (repo-coupled, doesn't forward
     `-ProjectPath`), log-exclusion note, re-copy-on-update discipline.
   - Cross-references renumbered to §14.

## Verification

- Requirement YAML parses; `status: active` preserved; AC-13 in trackable_items.
- All 5 goal ACs ticked.

## Notes

- No `implements_flows` in YAML → no upstream flow impact.
- Process/dev-infra requirement with no `target_package` on existing ACs →
  package assignment skipped (consistent with siblings).
- Scripts themselves were not modified (out of scope).
