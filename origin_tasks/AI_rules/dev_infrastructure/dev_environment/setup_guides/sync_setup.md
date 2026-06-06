# Mutagen sync setup (devcontainer → Windows NTFS mirror)

This runbook documents the continuous one-way sync that keeps a Windows NTFS folder current with the devcontainer working tree. The NTFS mirror exists so manual Windows-target operations (`flutter build windows`, the Windows desktop smoke test, Windows-target integration tests) have a normal NTFS path to operate on — codified by REQ-PROC-054 AC-05 and AC-09.

This guide assumes [`wsl_devcontainer_setup.md`](wsl_devcontainer_setup.md) has been completed (project source-of-truth is on WSL ext4 at `~/projects/private_mood_tracker/flutter_app/`).

A developer on a configuration that does not build Windows targets locally — macOS, native Linux, native Windows without WSL — does not need Mutagen and skips this guide; see [`alternative_environment_setup.md`](alternative_environment_setup.md).

---

## 1. Purpose

The supported configuration has one source-of-truth (WSL ext4, inside the devcontainer) and one derived Windows-side working copy. The derived copy is needed because:

- `flutter build windows` requires a Windows host and a Windows NTFS working directory. The Windows toolchain — CMD.EXE, MSBuild, the Visual Studio C++ build tools, Flutter's path canonicalization in Dart — is empirically broken against `\\wsl$\…` UNC paths at multiple independent layers (CMD.EXE rejects UNC `cwd`, MSBuild lower-cases UNC components producing `MSB8064`/`MSB8065` warnings, Flutter strips leading backslashes from UNC paths, `flutter pub get` inherits the cmd-shim UNC failure). Using `\\wsl$\…` is not a supported configuration.
- The Windows desktop smoke test (`scripts/windows/smoke_test_windows.ps1`) and the Windows-target integration test runner expect to operate against a normal NTFS path.

The sync's behavior contract: changes in the container propagate to NTFS within seconds; deletions in the container propagate; build artifacts and `.git/` stay out of the mirror; Windows-side accidental writes (typically build outputs) are preserved rather than overwritten.

Mutagen runs inside the devcontainer. Both endpoints are container-local paths: the alpha is the project tree on WSL ext4, the beta is a bind-mounted Windows NTFS folder. This avoids any Windows-side installation (no manual download, no PATH setup, no Task Scheduler). The daemon starts and stops with the container lifecycle.

The committed `mutagen.yml` at the project root drives the sync.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────┐
│  Devcontainer                                       │
│                                                     │
│  /workspaces/private_mood_tracker/flutter_app/      │
│  (WSL ext4 — source-of-truth)                       │
│        │                                            │
│        │  Mutagen daemon (runs in container)         │
│        │  one-way-safe sync                          │
│        ▼                                            │
│  /home/vscode/windows_mirror/                       │
│  (bind-mount → Windows NTFS)                        │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       │ Docker bind-mount
                       ▼
  C:\Users\...\private_mood_tracker\flutter_app\
  (Windows NTFS — derived mirror for manual builds)
```

The I/O path for sync writes is: Mutagen → Docker → WSL → 9P → NTFS. This path is fine for incremental sync (a few changed files at a time). The 9P throughput cap that makes `flutter analyze` slow over DrvFs is irrelevant here — the sync writes individual files, not thousands of random reads during a build.

---

## 3. Prerequisites (already in place)

The devcontainer configuration handles Mutagen installation and lifecycle automatically:

- **`setup.sh`** (`postCreateCommand`) installs the Mutagen binary into `/home/vscode/.local/bin/` on container creation.
- **`postStartCommand`** in `devcontainer.json` starts the Mutagen daemon and the sync session on every container start, before `flutter pub get`.
- **`devcontainer.json`** mounts the Windows NTFS mirror folder at `/home/vscode/windows_mirror`.
- **`mutagen.yml`** in the project root declares the sync session with container-local paths.

No Windows-side installation, PATH configuration, environment variables, or Task Scheduler entry is needed.

### DrvFs metadata prerequisite

The WSL host distro's `/etc/wsl.conf` must have the `metadata` option enabled on the automount:

```ini
[automount]
options = "metadata,umask=22,fmask=11"
```

Without `metadata`, the DrvFs mount does not support `chmod`. Docker bind-mounts to NTFS inherit this limitation, and Mutagen's file-write path calls `chmod` on every staged file — every write fails with `operation not permitted` if `metadata` is absent. This is configured once during initial WSL setup (see [`wsl_devcontainer_setup.md`](wsl_devcontainer_setup.md) §3).

After enabling `metadata` on an existing mirror that was previously written without it, all files default to `uid=1000` (the DrvFs mount default). The container's `vscode` user is `uid=1001`. Run a one-time ownership fix from inside the container:

```bash
sudo chown -R vscode:vscode /home/vscode/windows_mirror/
```

New files written by Mutagen after this fix are created as `vscode` (uid 1001) and do not need further chown.

### Per-developer configuration

The mount source in `devcontainer.json` is the only per-developer value. It points to the developer's Windows NTFS folder via the WSL `/mnt/c/…` path:

```json
"source=/mnt/c/Users/<windows-user>/<path-to>/private_mood_tracker/flutter_app,target=/home/vscode/windows_mirror,type=bind,consistency=cached"
```

Adjust this path once to match the local Windows folder. The target folder must exist before the container starts — Docker bind mounts fail if the source path does not exist.

---

## 4. Pre-seeding the mirror (first time only)

If a Windows-side copy of the project already exists (e.g., from a prior Windows-only checkout), use it as the mirror target folder. Mutagen with `one-way-safe` mode handles a pre-populated beta cleanly:

- Files that match the container tree → skipped (no transfer)
- Files that are older or different → overwritten with the container version
- Files that exist only on the Windows side → preserved (the "safe" in `one-way-safe`)

This makes the initial sync a fast delta rather than a full copy.

Optionally clean up `.git/`, `.dart_tool/`, and `build/` from the Windows-side copy before the first sync — they are in the `mutagen.yml` ignore list and won't be synced, but they take disk space.

If no Windows-side copy exists, create the empty target folder once from PowerShell:

```powershell
mkdir "C:\Users\<windows-user>\<path-to>\private_mood_tracker\flutter_app"
```

---

## 5. Verify the sync

After the container starts (or after a container rebuild), verify the sync session:

```bash
mutagen sync list
```

The output lists `flutter-app-to-windows` with `Status: Watching for changes` (or `Reconciling…` during the first pass). Both `Connection state` lines report `Connected`.

After the first reconciliation completes, the Windows mirror folder contains the project tree. Confirm visually from Windows Explorer: `lib/`, `test/`, `pubspec.yaml`, `mutagen.yml`, and other top-level entries match the container tree.

---

## 6. The pre-build flush — `Build-Win`

Mutagen propagation is near-realtime but not instant. Before invoking a Windows build, an explicit flush guarantees that whatever was just edited in the container has reached the NTFS mirror. The convention is a PowerShell function named `Build-Win`.

Add to the PowerShell `$PROFILE` (run `code $PROFILE` from PowerShell to open the profile file in VS Code; if the profile file does not exist, PowerShell prompts to create it):

```powershell
function Build-Win {
    [CmdletBinding()]
    param(
        [string]$Target = 'windows'
    )
    Write-Host "[Build-Win] Flushing Mutagen…" -ForegroundColor Cyan
    # Flush runs from inside the container where Mutagen is installed.
    # Use wsl to invoke it from Windows PowerShell.
    wsl -d Ubuntu-22.04 -e bash -c 'mutagen sync flush flutter-app-to-windows'
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[Build-Win] Mutagen flush failed; aborting build."
        return
    }
    Set-Location "$env:MUTAGEN_BETA"
    Write-Host "[Build-Win] Running flutter build $Target…" -ForegroundColor Cyan
    flutter build $Target
}
```

**Note**: Because Mutagen runs in the container (not on Windows), the flush command must reach the container. The `wsl -e bash -c '…'` invocation runs the flush inside the WSL distro. Alternatively, run the flush directly from a terminal inside the container before switching to the Windows PowerShell session for the build.

For the `Set-Location` line, either set `MUTAGEN_BETA` as a Windows environment variable pointing to the mirror folder, or replace `$env:MUTAGEN_BETA` with the literal path (e.g., `"C:\Users\am-ur\Projekte Lokaler Arbeitsbereich\private_mood_tracker\flutter_app"`).

Reload the profile in the current session: `. $PROFILE`.

Usage: from any PowerShell prompt, `Build-Win`. The function flushes the mirror, changes directory into it, and runs `flutter build windows`.

A standalone flush (without building) is: run `mutagen sync flush flutter-app-to-windows` from a terminal inside the container. Useful before running the smoke test or a Windows-target integration test.

---

## 7. Daily workflow

The developer edits files inside the container against the WSL ext4 working tree. Mutagen detects changes and propagates them to the NTFS mirror within seconds. No explicit action is required for sync in the normal loop.

Three points call for an explicit flush:

- **Before `flutter build windows`.** `Build-Win` handles it.
- **Before running the Windows desktop smoke test.** Flush first (`mutagen sync flush flutter-app-to-windows` from a container terminal), then invoke the smoke test from a Windows session.
- **Before running a Windows-target integration test.** Same — explicit flush first.

Between these moments, the sync runs continuously and silently.

A flush is fast (one to a few seconds on a clean tree); it is safe to run repeatedly.

---

## 8. Healthcheck and recovery

**Healthcheck.** `mutagen sync list` (from inside the container) returns exit 0 and reports `Status: Watching for changes` for the `flutter-app-to-windows` session. Both `Connection state` lines report `Connected`. If any of these conditions fails, the daemon or the session is not healthy.

**Common failure modes and recovery:**

| Symptom | Likely cause | Recovery |
|---|---|---|
| `mutagen sync list` reports `Error: unable to connect to daemon` | Daemon is not running (container restarted without postStartCommand firing) | `mutagen daemon start && mutagen project start` from the project root |
| `Connection state (beta): Disconnected` | The bind-mount target folder was deleted or moved on Windows | Recreate the folder on Windows; restart the container or run `mutagen daemon restart` |
| The session reports `Status: Halted on root deletion` | The beta mount point disappeared (Docker mount issue) | Verify the mount exists: `ls /home/vscode/windows_mirror/`; if missing, restart the container |
| Propagation takes minutes rather than seconds | Extremely large change set (e.g., `flutter pub get` writing 10k files to `.pub-cache`) | The `.pub-cache` and `.dart_tool` exclusions in `mutagen.yml` should prevent this; confirm `mutagen sync list` shows the configured ignores |
| `mutagen project start` fails with "session already exists" | Stale session from a previous container lifecycle | `mutagen project terminate 2>/dev/null; mutagen project start` |

**Restart the daemon if anything is stuck:** `mutagen daemon restart`. Sessions resume automatically.

**Hard reset if something is wrong with the session state:** `mutagen sync terminate flutter-app-to-windows`, then `mutagen project start` from the project root. The next sync is a full reconciliation, which can take 1–5 minutes.

---

## 9. Container rebuild

When the container is rebuilt (`Dev Containers: Rebuild Container`), Mutagen is reinstalled by `setup.sh` and the sync session is recreated by `postStartCommand`. No manual intervention is needed. The first sync after a rebuild is a full reconciliation against the existing NTFS mirror — since most files match, this completes quickly.

---

## 10. Conflict resolution under one-way-safe

The configured sync mode is `one-way-safe`. The semantics are:

- Changes on the container (`alpha`) side propagate to NTFS (`beta`).
- Deletions on the container side propagate to NTFS.
- Changes on the NTFS side that conflict with the container side are preserved on the NTFS side as `.conflict` files; they are not overwritten and they do not propagate back.
- Files on the NTFS side that do not exist on the container side and are listed in the ignore list (e.g., `build/`, `.dart_tool/`) are left alone.
- Files on the NTFS side that do not exist on the container side and are *not* in the ignore list (e.g., a stray PowerShell script the developer put there) are preserved.

This mode protects against losing Windows-side work by mistake. The trade is that Windows-side edits to source files do not automatically reach the container tree.

### How to detect a conflict

`mutagen sync list` reports `Conflicts: N` for the affected session. The conflicting files are listed with two paths and a brief reason.

### How to resolve a conflict

Three approaches, depending on intent:

1. **Discard the Windows-side change.** Delete the `.conflict` file (and the original Windows-side file if needed). On the next sync tick, the container-side version is mirrored over.
2. **Keep the Windows-side change.** Copy the resolved content back to the container tree by hand (open the file in the container, paste the desired content, save). The next sync propagates it to NTFS and the `.conflict` file disappears on the following reconciliation.
3. **Resolve manually and resume.** Edit both sides to converge, then `mutagen sync flush flutter-app-to-windows`.

Conflicts are uncommon on this configuration because the developer's edit path is "container only". They arise typically from inadvertent Windows-side touches (e.g., a Windows tool created a build output that the ignore list didn't catch).

---

## 11. When to flip to two-way-safe

The default `one-way-safe` mode is correct as long as the developer only edits source from inside the container. If the workflow changes — for example the developer starts editing Windows-side native runner code (`windows/runner/*.cpp`) from a Windows editor regularly, or uses Visual Studio to debug a Windows build interactively — `two-way-safe` is the appropriate mode.

To switch:

1. Edit `mutagen.yml` and change `mode: one-way-safe` to `mode: two-way-safe`.
2. From inside the container: `mutagen sync terminate flutter-app-to-windows`, then `mutagen project start` from the project root.

Under `two-way-safe`:

- Changes on either side propagate to the other.
- Bidirectional deletions propagate.
- Concurrent changes to the same file produce a `.conflict` file containing both versions, marked with `.conflict-alpha` and `.conflict-beta` suffixes. The developer resolves manually.

The trade is symmetric protection (no side silently overwrites the other) at the cost of more frequent conflict files when both sides edit. For a single-developer setup where the LLM is the dominant editor, `one-way-safe` remains the safer default; `two-way-safe` is the appropriate choice once Windows-side editing is a routine activity rather than an occasional incident.

The mirror folder itself stays on plain local NTFS — never a cloud-synced folder (OneDrive, Dropbox, Google Drive). Cloud-sync clients interact poorly with Flutter build artifacts (the cloud client tries to rehydrate placeholders during `flutter build`), with the `.git/` directory's lock files (the cloud client opens files Git is in the middle of writing), and with Mutagen's own state. Off-machine backup duty is carried by the GitHub remote and by the pre-push `git bundle --all` that `.githooks/pre-push` writes into the cloud-synced backup folder — both of which are already part of the supported configuration (REQ-PROC-054 AC-09).

The same pre-push hook also snapshots the workspace-parent `.devcontainer/` and `.vscode/` folders (at `/workspaces/private_mood_tracker/`) to the cloud-synced backup folder as `_parent_.devcontainer/` and `_parent_.vscode/`. Those folders sit outside the git repo (the repo root is `flutter_app/`) and outside the Mutagen alpha (also `flutter_app/`), so without this step they would have no off-machine copy. The snapshot is staged to a `*.new` path and atomic-swapped to avoid the `cp -r` nesting trap.

---

## 12. Mutagen version updates

Mutagen is pinned in `setup.sh` at a specific version (currently v0.18.1). To update:

1. Check the latest release at `https://github.com/mutagen-io/mutagen/releases`.
2. Update the `MUTAGEN_VERSION` variable in `setup.sh`.
3. Rebuild the container.

The sync configuration in `mutagen.yml` is version-independent; updates do not require reconfiguration.

---

## 13. Windows-host scripts (optional)

Windows scripts that run on the host — the sleep watcher, the smoke test, the LLM smoke test — live in `scripts/windows/` inside the repository. They are **never run from the mirror or the repo directly when elevated**; instead they are installed to an out-of-repo location via the install tool (`sync_windows_scripts.ps1`). This section covers the full mechanism.

### What the scripts do and why they are not a bridge

The scripts read the orchestrator's `automation/state.json` and the project's build outputs. They react with a fixed, narrow action set: suspend/wake the host (sleep watcher), build and run integration tests (smoke test), capture a screenshot and call an external API (LLM smoke test). They execute no command strings and interpret no code from container-writable files. The only thing a container-side process can influence is *whether and when* the host sleeps and wakes — a DoS/convenience surface, not arbitrary execution. This is the same security profile as the AC-07 Android-emulator watcher, which is why they are a permitted class and not a host-execution bridge (REQ-PROC-054 AC-03).

### Project root resolution

All scripts use a shared resolution helper (`find_project_root.ps1` for PowerShell, `find_project_root.py` for Python) with 3-level precedence:

1. **Explicit parameter** (`-ProjectPath` / `explicit=` argument) — highest priority.
2. **`windows_scripts.config.json`** next to the script — written by the install tool at the out-of-repo install location, containing `{ "project_root": "<mirror path>" }`.
3. **Auto-derive** from script location — `scripts/windows/` is two levels below the project root; used when running in-repo.

This means scripts work both in-repo (development/testing) and out-of-repo (installed copy) without manual path configuration.

### Install tool (`sync_windows_scripts.ps1`)

The install tool replaces the previous manual `Copy-Item` step. It copies all scripts from `scripts/windows/` (excluding the `tests/` subfolder) to an out-of-repo target directory and writes the config + manifest files.

**First-time install** from a Windows PowerShell prompt:

```powershell
# From the mirror or a full checkout:
.\scripts\windows\sync_windows_scripts.ps1
```

Default target: `$HOME\projects\private_mood_tracker\windows-scripts`. Override with `-TargetDir`. The `-MirrorPath` parameter defaults to the project root auto-derived from the tool's own location.

**What it does:**

1. Computes SHA-256 hashes of every file under `scripts\windows\` (excluding `tests\`).
2. If the target already has a `_manifest.json` from a previous install, diffs against it and shows added/removed/changed files with per-file old-to-new hashes.
3. Prints the full manifest.
4. Prompts `Confirm install? [y/N]` — aborts on non-y.
5. Copies all scripts to the target directory.
6. Writes `windows_scripts.config.json` with `project_root` pointing to the mirror.
7. Writes `_manifest.json` for the next diff.

**On update:** when scripts change intentionally, re-run `sync_windows_scripts.ps1` from the updated mirror. The review gate shows exactly what changed (file-level SHA-256 diff) before any files are overwritten. This replaces the previous manual re-copy step with a verifiable, auditable process.

### Denylist checker (`check_windows_scripts.ps1`)

A deterministic, LLM-free scanner that checks all `.ps1` and `.py` files under `scripts/windows/` (excluding `tests/`) for dangerous patterns:

- `Invoke-Expression` / `IEX` (code injection)
- `DownloadString` / `DownloadFile` / `Invoke-WebRequest` / `Invoke-RestMethod` (network download)
- `-EncodedCommand` / `FromBase64String` (obfuscated payloads)
- `Register-ScheduledTask` outside the known `AutorunWakePC` usage (unexpected task registration)
- `Set-ItemProperty` on `HKLM` / `HKCU` (registry writes)
- `net user` / `Add-LocalGroupMember` (user account manipulation)
- `Remove-Item -Recurse` (mass deletion — warning severity)
- `Start-Process` with URLs (external content execution)

Known-safe instances are allow-listed by file name or by a `# safety: known-safe <reason>` inline annotation. Exit 0 on clean, exit 1 on any error-severity match.

Run before and after modifying any Windows script:

```powershell
.\scripts\windows\check_windows_scripts.ps1
```

### Windows Sandbox (`dev_sandbox.wsb`)

A Windows Sandbox configuration that maps `scripts/windows/` read-only into the sandbox and runs the test suite on logon. Use it to test script changes in isolation without affecting the host:

1. Update the `<HostFolder>` path in `dev_sandbox.wsb` to match your local project location.
2. Double-click `dev_sandbox.wsb` — the sandbox boots, installs Pester, and runs all tests.

### Test runner (`scripts/windows/tests/run_all_windows_tests.ps1`)

Discovers and runs all `*.Tests.ps1` Pester test files in `scripts/windows/tests/`. Installs Pester v5+ if not present. Prints a summary and exits nonzero on any failure.

```powershell
.\scripts\windows\tests\run_all_windows_tests.ps1
```

### Sleep watcher shortcut (elevated)

The watcher runs **as Administrator** (it registers a SYSTEM scheduled task and calls the Win32 suspend API). For that reason the installed copy must live **outside** the repository and the Mutagen mirror, on a Windows path the container cannot write to. The install tool handles this — the installed copy at the target directory reads `windows_scripts.config.json` for the mirror path automatically.

Create a desktop shortcut, **Run as administrator** (Shortcut > Properties > Advanced > Run as administrator), with a Target such as:

```
powershell.exe -ExecutionPolicy Bypass -File "%LOCALAPPDATA%\PrivateMoodTracker\sleep_watcher\sleep_when_autorun_done.ps1"
```

No `-ProjectPath` is needed — the installed copy reads the project root from its co-located `windows_scripts.config.json`. The main script throws a clear error if it is not elevated and wake-up is enabled (the default). Use `-NoWake` to sleep without scheduling a wake, or `-TestMode` to verify the suspend+wake plumbing on the host without the orchestrator.

### About the wrapper

`win_sleep_script_wrapper.ps1` is a convenience layer: it disables console QuickEdit (so a stray click cannot freeze the poll loop) and truncates its log before forwarding to the main script. It resolves the project root via the shared helper. For the out-of-repo install, invoke `sleep_when_autorun_done.ps1` directly (as in the shortcut above).

The wrapper writes its log to `<ProjectRoot>\automation\win_sleep_script.log`. If the project root resolves to the mirror, exclude that log from the sync — add `automation/win_sleep_script.log` to the `mutagen.yml` ignore list.

---

## 14. Cross-references

- [`wsl_devcontainer_setup.md`](wsl_devcontainer_setup.md) — prerequisite for this guide; WSL2, Docker Desktop, VS Code, the parent-level devcontainer, the WSL ext4 project clone, and the DrvFs `metadata` prerequisite.
- [`backup_and_restore.md`](backup_and_restore.md) — backup inventory, verification, and restore procedures (container rebuild, WSL reset, machine swap).
- [`android_device_setup.md`](android_device_setup.md) — Android USB / wireless attachment for Flutter Android integration tests from inside the container (independent of Mutagen).
- [`alternative_environment_setup.md`](alternative_environment_setup.md) — macOS, native Linux, native Windows without WSL. Mutagen is not used in any of these configurations.
- [`../decisions/2026-05-19_no-host-bridge.md`](../decisions/2026-05-19_no-host-bridge.md) — the ADR that explains why Mutagen exists in this architecture (the bridge-less response to the speed problem) and why `\\wsl$\…` direct access is not a supported alternative.
- `flutter_app/mutagen.yml` — the committed sync configuration. The ignore list, mode, and endpoints are there.
- `/workspaces/private_mood_tracker/.devcontainer/setup.sh` (workspace-parent level, not inside `flutter_app/`) — Mutagen binary installation.
- `/workspaces/private_mood_tracker/.devcontainer/devcontainer.json` (workspace-parent level) — the NTFS mirror bind-mount and the `postStartCommand` that starts the daemon.
