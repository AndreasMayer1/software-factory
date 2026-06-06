# WSL + devcontainer setup (supported configuration)

This runbook installs and verifies the supported developer configuration codified by REQ-PROC-054 AC-01: project source-of-truth on WSL2 ext4, VS Code devcontainer placed at the parent-folder level of the `flutter_app/` repository, and (covered in [`sync_setup.md`](sync_setup.md)) a continuous one-way sync to a Windows NTFS mirror.

Reading order for first-time setup: this guide → [`sync_setup.md`](sync_setup.md) → [`backup_and_restore.md`](backup_and_restore.md) → [`android_device_setup.md`](android_device_setup.md) when Android testing is needed.

A developer on macOS, native Linux, or native Windows without WSL follows [`alternative_environment_setup.md`](alternative_environment_setup.md) instead.

---

## 1. Prerequisites

**Operating system.** Windows 10 version 2004 (build 19041) or later, or any Windows 11. Pro / Enterprise / Education editions all work; Home edition works for everything in this guide.

**Hardware virtualization.** Enabled in the firmware (BIOS/UEFI). The setting is typically named "Intel VT-x", "AMD-V", or "SVM Mode". Confirm from Windows by running `systeminfo` in PowerShell and reading the `Hyper-V Requirements` block — every line should report `Yes`.

**RAM.** 16 GB is the practical minimum; the analyzer alone keeps a ~1 GB driver cache resident during a working session, and the WSL VM, Docker Desktop, VS Code, and a browser together comfortably exceed 8 GB.

**Free disk.** 60 GB on the system drive for WSL + Docker Desktop + Flutter SDK + the project's `.dart_tool`, `build/`, and `.pub-cache` directories. The Windows NTFS mirror configured in [`sync_setup.md`](sync_setup.md) adds another 1–5 GB depending on `pubspec.yaml` size.

**Network.** Outbound HTTPS to GitHub, pub.dev, Docker Hub, and `ghcr.io`. Corporate proxies that intercept TLS require Flutter and Dart to trust the proxy's CA bundle; that configuration is out of scope here.

---

## 2. Install WSL2

In an elevated PowerShell:

```powershell
wsl --install -d Ubuntu-22.04
```

WSL is enabled, the kernel is installed, Ubuntu 22.04 LTS is fetched, and the machine restarts once. After the restart, Ubuntu launches a first-run prompt asking for a UNIX username and password — choose a username that matches the Windows login convention you prefer (the username is independent of the Windows account).

After the first-run prompt:

```powershell
wsl --set-default-version 2
wsl --list --verbose
```

`VERSION` for `Ubuntu-22.04` reads `2`. If `1` appears, run `wsl --set-version Ubuntu-22.04 2`.

Update the distro:

```bash
sudo apt-get update && sudo apt-get -y upgrade
```

Install basic tooling inside WSL (the devcontainer carries the Flutter SDK; the WSL distro itself only needs git, build essentials, and the unzip tools that `wsl --install`'s base image sometimes omits):

```bash
sudo apt-get install -y git curl unzip ca-certificates build-essential
```

Set git identity inside WSL (this is the identity the devcontainer will use, since the container mounts the WSL home):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### GitHub authentication

GitHub deprecated password authentication for git operations in August 2021. `git clone`, `git pull`, and `git push` over HTTPS now require either a Personal Access Token in place of a password or an SSH key. Configure one of the two options below inside WSL before reaching §5 — both options survive WSL reboots and devcontainer rebuilds because the credential state lives in the WSL home, which is the same home the container mounts.

**Option 1 — GitHub CLI (recommended).** Handles HTTPS git auth and the `gh` command in a single OAuth flow, no manual token management:

```bash
sudo apt-get install -y gh
gh auth login
```

Pick **GitHub.com → HTTPS → Login with a web browser**. The terminal prints a one-time code and a URL; paste the code into your browser, approve in your GitHub account, and `gh` registers itself as the git credential helper. From then on, HTTPS `git clone`, `git pull`, and `git push` work without further prompts.

**Option 2 — SSH key.** Generate inside WSL, upload the public key to GitHub:

```bash
ssh-keygen -t ed25519 -C "you@example.com"     # press Enter at every prompt to accept defaults
cat ~/.ssh/id_ed25519.pub
```

In a browser, go to GitHub → **Settings → SSH and GPG keys → New SSH key**; paste the public-key contents. Test:

```bash
ssh -T git@github.com
```

A successful first connection prints `Hi <user>! You've successfully authenticated…`. With SSH set up, use SSH-style remote URLs (`git@github.com:<user>/<repo>.git`) when cloning in §5. If you arrived via Option B (copy of an existing Windows checkout) and the copied tree has an HTTPS remote URL, switch it once:

```bash
cd ~/projects/private_mood_tracker/flutter_app
git remote set-url origin git@github.com:<user>/<repo>.git
```

---

## 3. Install Docker Desktop with the WSL2 backend

Download Docker Desktop for Windows from `docker.com` and run the installer. During first launch the WSL2 backend toggle appears under **Settings → General → Use the WSL 2 based engine**; it is enabled by default on recent installs.

Under **Settings → Resources → WSL Integration**, enable integration with the `Ubuntu-22.04` distro. Apply and restart Docker Desktop.

Verify from inside WSL:

```bash
docker version
docker info | grep "Operating System"
```

`docker version` reports a working client and server. `docker info | grep "Operating System"` reports `Docker Desktop`. Both confirm the integration is live.

Allocate Docker resources. The defaults (CPUs/RAM/disk) are set by Docker Desktop based on the host. On a 16 GB machine, raising the WSL VM's memory cap helps the analyzer:

Create `C:\Users\<your-windows-user>\.wslconfig`:

```ini
[wsl2]
memory=8GB
processors=4
swap=4GB
```

Enable POSIX metadata on DrvFs. Inside the WSL distro, edit `/etc/wsl.conf`:

```bash
sudo nano /etc/wsl.conf
```

Add (or merge into the existing `[automount]` section):

```ini
[automount]
options = "metadata,umask=22,fmask=11"
```

Without `metadata`, the DrvFs mount on `/mnt/c` does not support `chmod` — Docker bind-mounts that go through DrvFs to NTFS inherit this limitation. Mutagen (configured in [`sync_setup.md`](sync_setup.md)) needs `chmod` to write files to the NTFS mirror; without `metadata` every write fails with `operation not permitted`. The `umask=22` / `fmask=11` values produce conventional defaults (directories 755, files 644) for files that have no stored POSIX metadata.

Restart WSL from PowerShell to apply both `.wslconfig` and `wsl.conf`: `wsl --shutdown`, then reopen the WSL terminal.

---

## 4. Install VS Code and the Dev Containers extension

Download VS Code from `code.visualstudio.com` and run the installer.

Install the Dev Containers extension. From an elevated or normal PowerShell:

```powershell
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-vscode-remote.remote-wsl
```

The Remote-WSL extension is helpful for inspecting WSL paths from VS Code's host-side window before reopening in the container.

---

## 5. Move the project onto WSL ext4

The project source-of-truth lives on the WSL distro's ext4 filesystem. The rationale is performance: `flutter analyze` and `dart fix` over the full source tree read every Dart file in `lib/ + test/ + integration_test/`; reading those files through DrvFs (WSL's 9P client onto NTFS) or `\\wsl$\…` (Windows's 9P client onto WSL) is bounded by a single Hyper-V socket and capped at roughly an order of magnitude slower than native ext4. On ext4 the analyzer completes in under two minutes; on DrvFs it ran 10–17 minutes on the same tree. REQ-PROC-054 AC-04 codifies the under-2-minute contract.

Two options for getting the source tree onto ext4: a fresh `git clone` (Option A — clean baseline), or copying an existing Windows-side checkout across (Option B — keeps uncommitted work and local config). Pick one. Either option leaves `~/projects/private_mood_tracker/flutter_app/` as the git repository root, with the parent directory `~/projects/private_mood_tracker/` available to hold the devcontainer config in the next step.

**Do not** keep using a Windows-side checkout as the working tree (Git for Windows / GitHub Desktop into NTFS, then accessed from WSL via `/mnt/c/…`). The supported topology has the working tree on ext4; reading the project through DrvFs reintroduces the performance penalty this configuration exists to avoid. An existing Windows checkout is fine as the Mutagen mirror target (it gets reused in [`sync_setup.md`](sync_setup.md)); it is not fine as the daily-development working tree.

### Option A — Fresh clone

Choose this when there is no prior Windows-side checkout, or when the existing checkout is clean (all commits pushed, no untracked configuration worth preserving).

Inside the WSL terminal:

```bash
mkdir -p ~/projects
cd ~/projects
git clone <your-fork-or-the-canonical-remote> private_mood_tracker
cd private_mood_tracker
ls -la
```

The clone places the `flutter_app/` subdirectory at `~/projects/private_mood_tracker/flutter_app/`.

If you previously kept a Windows-side checkout of the project, you can either delete it (the WSL ext4 clone is the new source-of-truth), or keep it as the NTFS mirror target — [`sync_setup.md`](sync_setup.md) reuses an existing Windows-side checkout as the Mutagen `beta` endpoint, which means your existing Windows path stays valid without manual relocation.

### Option B — Copy an existing Windows checkout

Choose this when you already have the project checked out under `C:\…` with uncommitted work, local untracked configuration, or unpushed branches you do not want to recreate. Copying preserves the full working-tree state; the only things that must NOT come along are platform-specific build caches that bake in absolute Windows paths.

From the WSL terminal:

```bash
mkdir -p ~/projects
rsync -a --info=progress2 \
  --exclude='.dart_tool/' \
  --exclude='build/' \
  --exclude='flutter_app/.dart_tool/' \
  --exclude='flutter_app/build/' \
  --exclude='flutter_app/android/.gradle/' \
  --exclude='flutter_app/android/app/build/' \
  --exclude='flutter_app/ios/Pods/' \
  --exclude='flutter_app/ios/.symlinks/' \
  --exclude='flutter_app/macos/Pods/' \
  --exclude='flutter_app/.flutter-plugins' \
  --exclude='flutter_app/.flutter-plugins-dependencies' \
  /mnt/c/path/to/private_mood_tracker/ \
  ~/projects/private_mood_tracker/
```

Substitute the actual Windows path of your existing checkout for `/mnt/c/path/to/private_mood_tracker/`. The trailing slashes matter — they tell rsync to copy the *contents* of the source folder into the destination folder rather than nesting another level deep.

Before starting the copy, make sure no Windows-side git, editor, or build process is actively writing into the source tree. A `.git/index.lock` present at the moment of copy can produce a broken clone; close any open VS Code window on the Windows side and let any background pub-get / gradle process finish first.

**Post-copy fixups.** Files coming off NTFS lose POSIX execute bits and may carry CRLF endings. From inside `~/projects/private_mood_tracker/`:

```bash
cd ~/projects/private_mood_tracker/flutter_app

# Restore execute bits on the scripts and git hooks.
find scripts -type f -name '*.sh' -exec chmod +x {} +
chmod +x .githooks/* 2>/dev/null || true

# Tell git to renormalize line endings to whatever .gitattributes says.
git config core.autocrlf input
git add --renormalize . 2>/dev/null || true

# Sanity check — should match what git status showed on Windows.
git status
```

If `git status` shows a flood of modified files that you do not recognise, almost all of them are line-ending changes — `git checkout -- <path>` on a sample file should make it disappear, confirming the renormalization is the only difference. Run `git checkout -- .` to discard those line-ending-only deltas; real uncommitted work you wrote remains.

The Flutter build cache rebuilds itself when you run `flutter pub get` (which the devcontainer's `postStartCommand` does on every container open, per §6's `devcontainer.json`); you do not need to re-run anything manually at this stage.

If your previous Windows checkout had remote-tracking branches you did not have pushed (for example, a personal `wip/…` branch), `git branch -vv` after the copy confirms they came along. The remote URL is preserved as well — `git remote -v` lists the same URL the Windows checkout had.

**Sections §6 and §7 are pre-populated by the copy.** The rsync source is the parent folder `private_mood_tracker/`, which already contains `.devcontainer/devcontainer.json` and `.devcontainer/setup.sh` at the parent level — that is the layout §6 and §7 describe. After the copy:

- Confirm `~/projects/private_mood_tracker/.devcontainer/devcontainer.json` exists and the bind-mount paths inside it still resolve on your Windows host (they reference `${localEnv:USERPROFILE}\…` paths that Docker Desktop resolves to your Windows user profile — unchanged by the WSL move).
- Confirm the `mounts` block targets `${localEnv:USERPROFILE}/.claude-container` and `${localEnv:USERPROFILE}/.ccs-container`, not `${localEnv:USERPROFILE}/.claude` and `${localEnv:USERPROFILE}/.ccs`. The older layout (mounting `.claude` / `.ccs` directly) shares config folders with a Windows-native Claude Code or CCS installation and breaks both sides; if you see the older layout, update the `mounts` block to match §6 and create the `*-container` folders on Windows via the PowerShell `mkdir` command in §6.
- Confirm `~/projects/private_mood_tracker/.devcontainer/setup.sh` exists and is executable: `ls -la ~/projects/private_mood_tracker/.devcontainer/setup.sh` shows the `x` bit. If not, `chmod +x ~/projects/private_mood_tracker/.devcontainer/setup.sh`.

With all three checks passing, skip §6 and §7 entirely and proceed to §8 (First container open). If `devcontainer.json` or `setup.sh` is missing — for example, your Windows checkout predates the parent-folder devcontainer layout — fall back to §6 and §7 and create them by hand.

---

## 6. Place the devcontainer at the parent-folder level

The `.devcontainer/` folder lives at `~/projects/private_mood_tracker/.devcontainer/`, one directory above the git repository root, **not** inside `flutter_app/`. The rationale is git-worktree compatibility: a Claude Code session frequently spawns a sibling worktree alongside the main repo (for example `~/projects/private_mood_tracker/flutter_app-task-PROC-054-03/`), and the parent-level devcontainer means all siblings open in the same container instance — the analyzer's `.dartServer` cache, the pub cache, and the Docker layer cache are shared across worktrees, which is materially faster than running one container per worktree.

The parent folder `~/projects/private_mood_tracker/` is the developer's personal workspace. It is not in git (the `flutter_app/` subdirectory is the only git tree). Create the parent's `.devcontainer/` manually on first setup.

Create the directory and two files:

```bash
mkdir -p ~/projects/private_mood_tracker/.devcontainer
```

Before creating `devcontainer.json`, create the two Windows-side folders that will hold (a) Claude Code's bind-mounted config and (b) the snapshot folder for CCS session state. From PowerShell:

```powershell
mkdir $env:USERPROFILE\.claude-container, $env:USERPROFILE\.ccs-container
```

The names are deliberately distinct from `%USERPROFILE%\.claude` and `%USERPROFILE%\.ccs`. The latter pair is used by Claude Code and CCS when those tools are installed natively on Windows; pointing the container's bind mounts at the same folders causes the two installations to overwrite each other's state, which broke the Windows-native installation during prior iterations of this setup. Keeping the container artefacts in dedicated `*-container` folders eliminates the clash. The folders must exist before the first `Reopen in Container` — Docker Desktop creates missing bind-mount sources as root-owned directories that the container cannot write to.

Note on the asymmetry between the two folders:

- **`.claude-container`** is bind-mounted directly onto `~/.claude` inside the container. `~/.claude` has no internal symlinks, so DrvFs is happy with it.
- **`.ccs-container`** is **not** mounted onto `~/.ccs`. CCS uses internal symlinks (`instances/<account>/skills` → `shared/skills` and similar) that DrvFs cannot represent reliably; a direct mount broke CCS empirically. Instead, the folder receives periodic gzip'd tarball snapshots of `~/.ccs/` written by a cron job inside the container; on container creation, `setup.sh` restores from the newest snapshot when `~/.ccs/` is empty. See [`../decisions/2026-05-23_ccs-session-state-backup.md`](../decisions/2026-05-23_ccs-session-state-backup.md) for the rationale.

Now create `~/projects/private_mood_tracker/.devcontainer/devcontainer.json` with the following contents. The `mounts` block binds the two `*-container` folders and a cloud-synced backup folder into the container; adjust the host-side paths under `${localEnv:USERPROFILE}` to match your Windows layout:

```jsonc
{
  "name": "Flutter",
  "image": "ghcr.io/cirruslabs/flutter:latest",
  "remoteUser": "vscode",
  "features": {
    "ghcr.io/devcontainers-extra/features/claude-code:1": {},
    "ghcr.io/devcontainers/features/node:1": {
      "version": "lts",
      "nodeGypDependencies": true
    },
    "ghcr.io/devcontainers/features/common-utils:2": {
      "username": "vscode",
      "installZsh": true
    }
  },
  "postCreateCommand": "bash ./.devcontainer/setup.sh",
  "postStartCommand": "cd /workspaces/private_mood_tracker/flutter_app && (sudo service cron start 2>/dev/null || true) && (/usr/local/bin/backup-ccs.sh >> /home/vscode/.ccs-container/backup.log 2>&1 || true) && (mutagen daemon start 2>/dev/null || true) && (mutagen project start 2>/dev/null || true) && flutter pub get",
  "mounts": [
    "source=${localEnv:USERPROFILE}/.claude-container,target=/home/vscode/.claude,type=bind,consistency=cached",
    "source=${localEnv:USERPROFILE}/.ccs-container,target=/home/vscode/.ccs-container,type=bind,consistency=cached",
    "source=${localEnv:USERPROFILE}/Projekte/Appentwicklung/private_mood_tracker/flutter_app,target=/home/vscode/backup,type=bind,consistency=cached"
  ]
}
```

Notes on the bind mounts:

- `%USERPROFILE%\.claude-container\` → `/home/vscode/.claude` carries Claude Code's configuration (settings, memory, agents, plugins) across container rebuilds. NTFS persists, so a `Dev Containers: Rebuild Container` does not destroy it.
- `%USERPROFILE%\.ccs-container\` → `/home/vscode/.ccs-container` is the snapshot folder for CCS session state. **It is not mounted onto `~/.ccs`** — see [`../decisions/2026-05-23_ccs-session-state-backup.md`](../decisions/2026-05-23_ccs-session-state-backup.md) for why a direct mount fails (DrvFs vs. CCS's internal symlinks). Instead, a cron job (see §7) writes gzip'd snapshots of `~/.ccs/` into this folder every 30 minutes with retention of the newest 3. On a fresh container start with `~/.ccs/` empty, `setup.sh` restores from the newest snapshot.
- Claude Code's standalone-mode account/OAuth file `~/.claude.json` is intentionally not mounted: in this container Claude Code is driven through the CCS proxy (installed by §7 below), and account state lives in `~/.ccs/cliproxy/auth/` rather than in `~/.claude.json`. The CCS snapshot mechanism therefore covers it transitively.
- On the first container start with empty `*-container` folders, `setup.sh` (§7) bootstraps `~/.claude` from a `claude-backup-*.tar.gz` in `~/backup` if one exists (migration path from an older layout). On a fresh setup with no backup tarballs and no CCS snapshots, the bootstrap is a no-op; Claude Code and CCS initialize themselves into the empty folders on first launch.

A 4th mount — the Windows NTFS mirror for Mutagen sync — is added when following [`sync_setup.md`](sync_setup.md). It is not shown here because Mutagen is optional (skip it entirely if you don't build Windows targets locally). See `sync_setup.md` §3 for the mount line to add.
- `/home/vscode/backup` is the cloud-synced Windows folder that receives the pre-push git bundle from `.githooks/pre-push`. **It is intentionally distinct from `~/.ccs-container/`**: the OneDrive sync that backs up the git bundle is poorly suited to many small files written every 30 minutes, so the CCS snapshot folder lives on plain local NTFS instead. Adjust the source path of `~/backup` to the cloud-synced folder you actually use (OneDrive, Dropbox, Google Drive — the bundle is small and the cloud sync is the off-machine backup layer of REQ-PROC-054 AC-09 layer 2).

Notes on the image tag: `ghcr.io/cirruslabs/flutter:latest` tracks the latest stable Flutter release. Pin the tag to a specific Flutter version (e.g. `ghcr.io/cirruslabs/flutter:3.27.1`) when the project's `pubspec.yaml` Flutter constraint requires it, or when a stable-image break is observed.

---

## 7. Configure the postCreate setup script

The authoritative `setup.sh` lives at `~/projects/private_mood_tracker/.devcontainer/setup.sh` (workspace-parent level, alongside `devcontainer.json`). It runs once per container creation via the `postCreateCommand`. Each section has inline comments explaining its purpose.

If you arrived via Option B in §5 (copy from Windows), `setup.sh` was already copied as part of the parent folder. Confirm it exists and is executable:

```bash
ls -la ~/projects/private_mood_tracker/.devcontainer/setup.sh
# Should show the x bit. If not:
chmod +x ~/projects/private_mood_tracker/.devcontainer/setup.sh
```

If you arrived via Option A in §5 (fresh clone) and the parent folder does not yet contain `setup.sh`, copy it from the backup or create it by following the inline structure documented below. The script is not duplicated here in full — the file is the single source of truth — but its key sections are:

1. **NVM + apt cache refresh.** Sources NVM, runs `sudo apt-get update` to fix the stale package index in the base image.
2. **CCS session state restore.** If `~/.ccs` is empty (fresh rebuild), restores from the newest tarball in `~/.ccs-container/` (Windows NTFS bind-mount).
3. **CCS npm package install.** `npm install -g @kaitranntt/ccs` (Claude Code session server).
4. **CCS backup mechanism.** Installs `cron`, copies `backup-ccs.sh`, `check-ccs-backup-health.sh`, and the cron schedule file into system paths. See [`../decisions/2026-05-23_ccs-session-state-backup.md`](../decisions/2026-05-23_ccs-session-state-backup.md) for the design rationale.
5. **Claude Code config restore.** Fallback bootstrap of `~/.claude` from a `claude-backup-*.tar.gz` in `~/backup` if the bind-mount is empty (migration path from older layout).
6. **Python tooling.** `python3-pip`, `python3-yaml`, `tmux`, plus pip packages for quality gates (`pytest`, `plotly`, `kaleido`, `weasyprint`, `jinja2`, `ruamel.yaml`).
7. **Google Chrome.** Installed from Google's official `.deb` (the `chromium` apt package on Ubuntu Noble is a snap-wrapper stub that fails inside containers). Used by kaleido for chart-to-PNG export and discovered by `flutter doctor` as the Web toolchain Chrome.
8. **uv.** Python dev-deps lock and sync (REQ-PROC-051).
9. **Mutagen.** Continuous one-way sync to the Windows NTFS mirror. Binary installed to `~/.local/bin/mutagen`. See [`sync_setup.md`](sync_setup.md).
10. **Git hooks.** Sets `core.hooksPath` to `.githooks/` inside the `flutter_app/` repo.
11. **Flutter SDK ownership.** `chown` to `vscode` inside the cirruslabs image.
12. **Linux desktop runtime dependencies.** Delegates to `flutter_app/scripts/dev_environment/install_linux_desktop_deps.sh` (REQ-PROC-054 AC-06).
13. **Timezone.** Defaults to `Europe/Berlin`; adjust to your locale.
14. **Claude diagnostics fix.** Symlinks the `claude` binary into `~/.local/bin/`.

The script does not add any host-side automation. There is no PowerShell launch, no `wsl.exe` shell-out, no scheduled-task creation. The pen-test (TASK-PROC-054-01) found that host-side auto-launch from a repository-tracked or repository-adjacent file is the V7 attack-vector class; the setup script restricts itself to in-container, container-installed tooling.

---

## 8. First container open

In Windows, open VS Code. The fastest path:

```bash
# From a WSL terminal in the parent folder:
cd ~/projects/private_mood_tracker
code .
```

The first `code .` invocation from inside WSL bootstraps the VS Code Server inside the WSL distro and opens a window connected to WSL. From there:

1. Click the green Remote indicator at the bottom-left of the VS Code window.
2. Choose **Reopen in Container**.
3. The container builds (first build ≈ 5–10 minutes; subsequent reopens are cached and complete in seconds).

The container is now running. The terminal inside VS Code opens at `/workspaces/private_mood_tracker/` by default. The `flutter_app/` subdirectory is the git repository.

If `code .` is not on the WSL PATH, install it once from VS Code's command palette: **Remote-WSL: Install VS Code Server in WSL**, then close and reopen the WSL terminal.

---

## 9. Verify the environment

From a terminal inside the container (VS Code: **Terminal → New Terminal**, or any external terminal attached to the running container):

```bash
cd /workspaces/private_mood_tracker/flutter_app
flutter doctor -v
```

`flutter doctor` reports a working Flutter installation. The Android toolchain, Chrome, and Linux desktop entries are expected to report `[✓]`; the Windows toolchain entry is expected to report `[!]` or `[✗]` and is correct on a Linux container — Windows builds are not performed from inside the container (see [`sync_setup.md`](sync_setup.md) for the Windows-target operations procedure).

Pull dependencies:

```bash
flutter pub get
```

Time the analyzer against the full source tree:

```bash
time flutter analyze
```

Expected: under 2 minutes (REQ-PROC-054 AC-04 contract). If the analyzer takes substantially longer, the project tree is not on ext4 — confirm with `df -T .` inside the container; the filesystem type should report `ext4` (the container's view of the WSL ext4 filesystem). If it reports `9p` or `drvfs`, the project is being read through the 9P frontier; re-do step 5 and ensure the clone lives under `~/projects/` on the WSL distro, not under `/mnt/c/…` or `~/projects/…/` symlinked back to NTFS.

Time `dart fix --apply`:

```bash
time dart fix --apply
```

Expected: under 1 minute on a clean tree.

Run the test suite:

```bash
flutter test
```

Expected: the per-change `flutter test` portion of the back-pressure gates passes. If individual tests fail because of environment-specific assertions, [`alternative_environment_setup.md`](alternative_environment_setup.md) discusses platform-sensitive test patterns; on the supported configuration the suite is expected GREEN on a clean checkout.

Run a Linux-desktop integration test (the LLM-autonomous integration target per REQ-PROC-054 AC-06):

```bash
xvfb-run -a flutter test integration_test -d linux
```

The headless framebuffer provides a display; the Flutter Linux desktop binary renders into it; the integration test exercises the application and reports pass/fail. The first invocation builds the Linux desktop target (a few minutes); subsequent invocations are cached.

---

## 10. Configure Claude Code

The factory's AI sessions run through [Claude Code](https://claude.ai/code). Install it on the host (Windows or WSL) following the official docs, then verify the project-level setting is in effect.

**Context compression** (auto-compact) is disabled in `.claude/settings.json` (version-controlled). You do not need to set this manually — cloning the repository is sufficient. The factory is designed for short sessions with file-based cross-session memory (`plans_and_protocols/`); automatic context compression adds input-token cost on resumption without benefit and can silently summarize active context mid-session (REQ-PROC-067 AC-06).

To confirm the setting is active, run from inside the container:

```bash
grep -r "autoCompactEnabled" /workspaces/private_mood_tracker/flutter_app/.claude/settings.json
```

Expected output: `"autoCompactEnabled": false`

If you manage a personal `~/.claude/settings.json`, add the same key there so it is also off for any project opened outside this devcontainer:

```json
"autoCompactEnabled": false
```

---

## 11. Next steps

- **[`sync_setup.md`](sync_setup.md)** — install and configure the Mutagen continuous sync from the WSL ext4 working tree to a Windows NTFS mirror, so manual Windows-target operations (`flutter build windows`, the Windows desktop smoke test, Windows-target integration tests) have a normal NTFS path to operate on. Required if the developer ever builds the Windows desktop target locally; optional otherwise.
- **[`backup_and_restore.md`](backup_and_restore.md)** — what is backed up, where it lives, how to verify, and step-by-step restore procedures for container rebuild, WSL reset, and machine swap.
- **[`android_device_setup.md`](android_device_setup.md)** — USB-via-WSL (`usbipd`) and wireless (`adb tcpip`) attachment paths for running Flutter Android integration tests from inside the container.
- **[`alternative_environment_setup.md`](alternative_environment_setup.md)** — macOS, native Linux, and native-Windows-without-WSL configurations. Useful when a contributor joins on a non-Windows machine or when the developer occasionally works from a different host.

REQ-PROC-054 *Developer Environment Contract (No Host-Execution Bridge)* is the contract these guides realize; the contract is the source of truth for what counts as conformant. The decision rationale is recorded in [`../decisions/2026-05-19_no-host-bridge.md`](../decisions/2026-05-19_no-host-bridge.md).
