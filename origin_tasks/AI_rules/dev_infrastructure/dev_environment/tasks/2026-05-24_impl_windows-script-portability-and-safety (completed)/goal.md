---
task_id: TASK-PROC-054-07
type: impl
parent_requirement: REQ-PROC-054
urgency: 3
urgency_reason: U3-DEBT
impact: 4
impact_reason: I4-RISK
status: completed
effort: L
created: 2026-05-24
completed: 2026-05-24
after: [TASK-PROC-054-06, TASK-PROC-043-06]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-14, AC-15, AC-16, AC-17, AC-18]
  sections: []
scope_description: "Implement the windows-script portability mechanism (resolution helper + config), the install tool (with review gate + denylist checker), test runner, Windows Sandbox config, migrate existing scripts, move tests to scripts/windows/tests/, rewrite setup-guide §13."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 30ea8ea0
  file: ../../requirements.md
---

# Goal: Implement windows-script portability, install tool, and safety controls

## Objective

Build the full mechanism defined by REQ-PROC-054 AC-14 through AC-18 and
REQ-PROC-043 AC-08: resolution helper, install tool with review gate,
deterministic safety checker, test runner, Windows Sandbox config, and migrate
the existing windows scripts to use the mechanism.

## Implementation Spec

### 1. Config schema (shared contract)

File: `windows_scripts.config.json` (co-located with installed scripts at
the out-of-repo install location; NOT committed in-repo — the install tool
writes it).

```json
{
  "project_root": "C:\\Users\\am-ur\\Projekte Lokaler Arbeitsbereich\\private_mood_tracker\\flutter_app"
}
```

Single key `project_root`: the path to the synced project tree (the Mutagen
NTFS mirror). Used by every windows script to find `automation/state.json`,
build outputs, etc.

### 2. Resolution helper (AC-14)

**PowerShell** — `scripts/windows/find_project_root.ps1`:
- Exports a function `Find-ProjectRoot` (dot-sourced by other scripts).
- Precedence: (1) explicit `-ProjectPath` param → (2) `windows_scripts.config.json`
  in `$PSScriptRoot` → (3) auto-derive: `Split-Path (Split-Path $PSScriptRoot -Parent) -Parent`
  (the in-repo two-levels-up case).
- Returns the resolved path; throws if none resolves or path doesn't exist.
- Small, pure, no side effects, hash-pinnable.

**Python** — `scripts/windows/find_project_root.py`:
- Exports a function `find_project_root(explicit: str | None = None) -> Path`.
- Same precedence: explicit arg → `windows_scripts.config.json` next to the
  calling script (use `__file__` of the importer to find the dir) → auto-derive.
- Used by `smoke_test_llm.py`.

**Naming**: `find_` prefix is in the known verb list (read-only). Passes lint.

### 3. Install tool (AC-15 + AC-17 review gate)

`scripts/windows/sync_windows_scripts.ps1`:
- `sync_` prefix (state-modifying, in the known verb list). Passes lint.
- Reads its own config for: `target_dir` (default:
  `$HOME\projects\private_mood_tracker\windows-scripts`), `project_root`
  (the mirror path to write into the deployed config).
- The tool's own config: `scripts/windows/sync_config.json` (committed,
  per-developer; `.gitignore`'d or treated as a template).
  Actually, simpler: use parameters with sensible defaults; no extra config file.
  `-TargetDir` (default `$HOME\projects\private_mood_tracker\windows-scripts`),
  `-MirrorPath` (default: auto-detect from the tool's own location being inside
  the repo/mirror → `Split-Path ... -Parent -Parent`).

**Review gate (AC-17)**:
1. Computes SHA-256 of each file in `scripts/windows/` (excluding `tests/`
   subfolder and the tool's own lockfile).
2. If `-TargetDir` already has installed scripts, reads the previously-written
   manifest (`_manifest.json`) and computes a diff: added / removed / changed
   files (with per-file old→new hash for changed ones).
3. Prints the diff summary + full manifest.
4. Prompts `Confirm install? [y/N]`; aborts on non-y.
5. Copies all scripts (EXCLUDING `scripts/windows/tests/`) to `$TargetDir`.
6. Writes `windows_scripts.config.json` with `project_root = $MirrorPath`.
7. Writes `_manifest.json` with the new file hashes (for next diff).
8. Prints summary.

### 4. Deterministic denylist checker (AC-17)

`scripts/windows/check_windows_scripts.ps1`:
- `check_` prefix (read-only, in known verb list). Passes lint.
- Scans all `.ps1` and `.py` under `scripts/windows/` (excluding tests/) for
  a fixed set of dangerous constructs:
  - `Invoke-Expression` / `IEX` (PowerShell code injection)
  - `DownloadString` / `DownloadFile` / `Invoke-WebRequest` / `Invoke-RestMethod`
    / `wget` / `curl` (network download in host scripts)
  - `-EncodedCommand` / `[Convert]::FromBase64String` (encoded payloads)
  - `New-ScheduledTask` / `Register-ScheduledTask` outside the one known
    `AutorunWakePC` task name (unexpected task registration)
  - `Set-ItemProperty.*HKLM` / `Set-ItemProperty.*HKCU` (registry writes)
  - `net user` / `Add-LocalGroupMember` (user account manipulation)
  - `Remove-Item -Recurse` / `rm -rf` / `del /s /q` (mass deletion)
  - `Start-Process` of external URLs or network content
- Each pattern: regex, description, severity (error vs warning). Known safe
  instances (e.g. `AutorunWakePC` in sleep_when_autorun_done.ps1) are
  allow-listed by file+line or by a `# safety: known-safe <reason>` inline
  annotation.
- Exit 0 on clean, exit 1 on any error-severity match.
- Small, deterministic, no LLM. Designed to be reviewed once and pinned by hash.

### 5. Test runner (AC-18)

`scripts/windows/tests/run_all_windows_tests.ps1`:
- Located in tests/ subfolder (not scanned by lint — correct).
- Discovers and runs all `*.Tests.ps1` Pester test files in the same folder.
- Requires Pester module (`Install-Module Pester -Force` if missing).
- Prints summary; exits nonzero on any failure.

### 6. Move existing tests

- `scripts/windows/sleep_when_autorun_done.Tests.ps1`
  → `scripts/windows/tests/sleep_when_autorun_done.Tests.ps1` (`git mv`).

### 7. Migrate existing scripts to use the helper

Each script that currently derives `$ProjectPath` from its own location:

**`sleep_when_autorun_done.ps1`**: Replace the block at lines ~134-139
(`$scriptDir = ...; $ProjectPath = Split-Path (Split-Path ...)`) with:
```powershell
. "$PSScriptRoot\find_project_root.ps1"
if (-not $ProjectPath) { $ProjectPath = Find-ProjectRoot }
```
Keep the explicit `-ProjectPath` param (the helper's precedence-1).

**`win_sleep_script_wrapper.ps1`**: Replace `$projectRoot = Split-Path
(Split-Path $PSScriptRoot -Parent) -Parent` with the helper call. It
currently derives root for its log path + main script path — adapt.

**`smoke_test_windows.ps1`**: Same pattern — dot-source the helper, use
`Find-ProjectRoot` for the project root.

**`smoke_test_llm.py`**: Import `find_project_root` from the Python helper,
use it to resolve the project directory.

### 8. Windows Sandbox config

`scripts/windows/dev_sandbox.wsb`:
- Maps `scripts/windows/` read-only into the sandbox.
- LogonCommand: `Install-Module Pester -Force; & \\path\tests\run_all_windows_tests.ps1`.
- Documentation comment at the top explaining purpose.

### 9. Setup guide §13 rewrite

`requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/sync_setup.md`
section 13 (Windows-host sleep watcher): rewrite to cover the full mechanism
(install tool replaces manual copy, review gate, denylist checker, Sandbox).
The current §13 describes manual copy + `-ProjectPath`; the new version uses
`sync_windows_scripts.ps1`.

## Important constraints

- **No pwsh in container**: PowerShell scripts are static-reviewed only here.
  Verify on Windows / in Windows Sandbox.
- **claude-write-script skill MANDATORY** for every new script under
  `scripts/windows/` or `scripts/windows/tests/`.
- **Naming**: all scripts use known verb prefixes to pass
  `validate_scripts_org.py` (find_, sync_, check_). The runner in tests/
  is exempt (subfolder, not scanned).
- **Do not change `validate_scripts_org.py`** — current non-recursive scan
  already handles the structure.
- After implementation, `validate_scripts_org.py` must still exit 0.
- The Python gates (`check_python_gates.sh`) must pass for the `.py` helper.

## Acceptance Criteria

- [x] `scripts/windows/find_project_root.ps1` exists and exports Find-ProjectRoot
      with the 3-level precedence.
- [x] `scripts/windows/find_project_root.py` exists with equivalent Python function.
- [x] `scripts/windows/sync_windows_scripts.ps1` exists: copies scripts (excl tests/),
      writes config + manifest, has the diff+hash review gate with confirmation.
- [x] `scripts/windows/check_windows_scripts.ps1` exists: deterministic denylist scan,
      allow-list for known-safe patterns, exit 0/1.
- [x] `scripts/windows/tests/run_all_windows_tests.ps1` exists: discovers + runs Pester.
- [x] `scripts/windows/tests/sleep_when_autorun_done.Tests.ps1` moved from parent dir.
- [x] `scripts/windows/dev_sandbox.wsb` exists.
- [x] All 4 existing scripts migrated to dot-source/import the helper.
- [x] Setup guide §13 rewritten to use the install tool + mechanism.
- [x] `validate_scripts_org.py` exits 0.
- [x] Python gates pass for `find_project_root.py`.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-054-06 | completed | AC-17/AC-18 safety + test-location ACs |
| TASK-PROC-043-06 | completed | Scripts-org AC-08 windows test placement |
