# Alternative Environment Setup

The supported developer configuration for this project is documented in [`wsl_devcontainer_setup.md`](wsl_devcontainer_setup.md): WSL2 ext4 source-of-truth on a Windows host, devcontainer at the parent-folder level, Mutagen continuous sync to a Windows NTFS mirror for manual Windows-target operations. That configuration is what the project's daily development and integration-test loop is benchmarked against.

This guide covers the alternative configurations a contributor may use instead. REQ-PROC-054 AC-02 codifies the contract: each alternative produces identical quality-gate and container-runnable integration-test pass/fail outcomes; the differences from the supported configuration are speed and the availability of Windows-target operations, not correctness.

Three alternatives are documented: macOS, native Linux, and native Windows without WSL. Each section lists what works, what does not, and the substitutes for any Windows-target operations the configuration cannot perform.

---

## 1. macOS

### What is required

- A current macOS release with Apple Silicon or x86_64 hardware sufficient for Flutter development.
- The Flutter SDK installed natively (`brew install --cask flutter` or the standard Flutter installer).
- Xcode and the iOS Simulator, if iOS-target work is anticipated.
- Android Studio (or just the Android command-line tools) for the Android SDK and toolchain.
- A working Docker installation only if the contributor chooses to run the devcontainer; macOS contributors are not required to run the devcontainer at all.

Mutagen is not used. The project lives on the macOS filesystem and is read directly by the locally-installed Flutter SDK. There is no host-side sync, no continuous-sync daemon, and no Windows mirror.

### What works

- Every per-change quality gate defined by REQ-PROC-046, REQ-PROC-002, REQ-PROC-051, and REQ-PROC-052: `flutter analyze`, `dart fix --apply`, `flutter test`, `flutter pub get`, and the gate scripts under `scripts/quality/`. Performance is native (no DrvFs penalty, no 9P penalty).
- `flutter build apk`, `flutter build appbundle`, `flutter build web`, `flutter build macos`, and `flutter build ios` (with the appropriate signing identity).
- Integration tests against the macOS desktop target via `flutter test integration_test -d macos`. The macOS target is not the project's authoritative golden-file platform; goldens regenerated on macOS will not byte-match the committed Linux-rendered goldens, so regenerate-and-commit cycles for goldens are performed on the supported configuration, not on macOS.
- Integration tests against iOS Simulator targets via `flutter test integration_test -d <ios-simulator-id>`.
- Integration tests against Android targets, the same way as the supported configuration: an attached or wireless device, or an emulator launched via the Android SDK's `emulator` command.

### What does not work

- `flutter build windows` and the Windows desktop smoke test require a Windows host. A macOS contributor preparing a Windows-bearing release cannot perform these operations on their own machine.
- Linux desktop integration tests are not the daily LLM-autonomous loop on macOS. They can be run inside a devcontainer if the contributor chooses to run one (the same `xvfb-run flutter test integration_test -d linux` works) but the more natural local choice is macOS-target tests.

### Substitutes for Windows operations

The contract requires that no command silently skips because the alternative environment is detected. A macOS contributor preparing a release that includes the Windows build either:

1. Coordinates with a Windows-equipped contributor to perform the Windows build and smoke test, recording the result on the release notes; or
2. Uses a remote Windows runner (for example a Windows VM, a cloud Windows runner, or a separate Windows machine on the same network) reachable over SSH or RDP, where they perform the Windows operations manually.

If neither is feasible for the release at hand, the release notes state explicitly that the Windows build has not been performed, and the release does not advertise a Windows binary.

---

## 2. Native Linux

### What is required

- A current Linux distribution (Ubuntu 22.04 LTS or similar) on x86_64 or arm64 hardware.
- The Flutter SDK installed natively. Either:
  - via the Snap store (`sudo snap install flutter --classic`), or
  - by unpacking the official tarball and adding it to PATH.
- The Linux desktop runtime dependencies installed system-wide. The same package list used by `scripts/dev_environment/install_linux_desktop_deps.sh` applies; running that script directly on the host installs them.
- The Android SDK and toolchain for Android-target work.

The project lives on a normal Linux filesystem. No Mutagen, no sync.

### What works

- Every per-change quality gate, at native ext4 (or btrfs/xfs) speed.
- Integration tests against the Linux desktop target — the same headless-Xvfb path used in the supported configuration. `xvfb-run -a flutter test integration_test -d linux` works the same way without a devcontainer.
- Integration tests against Android via attached device, wireless `adb`, or emulator.
- `flutter build apk`, `flutter build appbundle`, `flutter build linux`, `flutter build web`.

### What does not work

- `flutter build windows` and the Windows desktop smoke test. Same as macOS: a Windows host is required.
- `flutter build ios` and `flutter build macos`. Same as anywhere outside macOS.

### Substitutes for Windows operations

Identical to the macOS section: coordinate with a Windows-equipped contributor, use a remote Windows runner, or document the Windows build as absent on the release.

### Devcontainer use on native Linux

A native-Linux contributor may choose to run the devcontainer for parity with the supported configuration. In that case the parent-folder-for-worktrees layout becomes optional: native Linux's git-worktree workflow does not face the per-worktree-container overhead that motivates the parent-level placement on Windows. Either layout is correct on native Linux. The devcontainer reads the project at native speed (no DrvFs intermediary), so the speed benefit of WSL ext4 over Windows NTFS does not apply.

---

## 3. Native Windows without WSL

### What is required

- A current Windows release (Windows 10 21H2 or later, Windows 11 any version).
- The Flutter SDK installed natively on Windows (via the official installer or `winget install Flutter.Flutter`).
- Visual Studio Build Tools or Visual Studio 2022 with the C++ desktop workload for `flutter build windows`.
- The Android SDK and toolchain.

The project lives on a normal Windows NTFS path. No WSL, no devcontainer, no Mutagen, no sync. This is the simplest configuration topologically — one host, one toolchain, one filesystem.

### What works

- Every per-change quality gate runs natively on Windows. The 10–17-minute `flutter analyze` problem that motivated the supported configuration is a WSL-DrvFs phenomenon; running the analyzer natively on Windows is fast.
- `flutter build windows`, the Windows desktop smoke test, and Windows-target integration tests run locally without any sync or mirroring step.
- `flutter build apk`, `flutter build appbundle`, `flutter build web`.
- Integration tests against the Windows desktop target via `flutter test integration_test -d windows`.
- Integration tests against Android via an attached device or emulator.

### What does not work

- The Linux desktop target is not natively buildable on Windows; `flutter build linux` requires a Linux host or container. Consequently the LLM-autonomous headless-Xvfb integration-test loop does not exist on this configuration in the form the supported configuration uses it. The substitute is direct Windows-target integration tests, which are not headless but are the canonical target for this configuration.
- `flutter build ios` and `flutter build macos`. Same as Linux: a macOS host is required.

### Differences from the supported configuration

A native-Windows contributor's LLM-autonomous loop runs against the Windows desktop target rather than the Linux desktop target. This is acceptable under the configuration-agnostic-correctness contract: the same set of pass/fail outcomes is produced; the differences are platform-rendering pixel-level (which is the same reason Linux is designated as the canonical golden platform regardless of who runs the tests).

If the contributor wants Linux-target tests for parity with committed CI / committed goldens, the options are:
- Set up WSL2 and use the supported configuration. (At that point this section no longer applies.)
- Run a separate Linux machine or cloud Linux runner for the Linux-target tests.

---

## 4. Cross-cutting notes

### Golden files

REQ-PROC-054 AC-08 designates Linux as the authoritative platform for committed widget goldens. A contributor on any non-Linux configuration who is asked to update goldens performs the regenerate-and-commit cycle from the supported configuration (or from a native-Linux environment). Goldens regenerated on macOS or Windows are not byte-identical to Linux-rendered goldens and overwriting committed goldens with non-Linux-rendered versions causes CI mismatches for every other contributor.

### Quality-gate parity

The gate scripts under `scripts/quality/` are written in Bash and Python and assume a POSIX shell. On macOS and Linux this is native. On native Windows the scripts run under WSL's Bash, Git Bash, or PowerShell's WSL invocation; pure-Python gate scripts (`*.py`) run under Windows Python directly. The supported configuration is also POSIX (Linux-in-container), so day-to-day gate parity is straightforward. Native-Windows contributors using PowerShell may want to set up Bash availability (`winget install Git.Git` brings Git Bash; or use the Windows Subsystem for Linux for the gate scripts only).

### The pre-push backup bundle

`.githooks/pre-push` writes a `git bundle --all` to `/home/vscode/backup` — a container-internal path. On non-container configurations the hook silently skips because the backup directory does not exist (the hook's first check is `if [ ! -d "$BACKUP_DIR" ]`). The contributor is expected to maintain their own backup discipline: routine `git push`, plus a personal periodic backup of the working tree if desired. The supported configuration's three-backup-layers contract (REQ-PROC-054 AC-09) is a property of the supported configuration; alternative configurations rely on git push plus the contributor's own habits.

### Reporting an alternative-configuration release

When a release is built on an alternative configuration, the release notes record:

- Which configuration was used (macOS / native Linux / native Windows without WSL).
- Which build targets were produced locally and which were skipped or delegated.
- Any deviation from the integration-test cadence required by REQ-PROC-053 *verification_strategy* (when that requirement is in force).

This keeps the release's provenance traceable for the duration of the project.

---

## 5. Related material

- [`wsl_devcontainer_setup.md`](wsl_devcontainer_setup.md) — the supported configuration.
- [`sync_setup.md`](sync_setup.md) — Mutagen; not used in any alternative configuration.
- [`android_device_setup.md`](android_device_setup.md) — Android device attachment; the same procedures apply on macOS and Linux (using `usbipd` is Windows-specific, but a directly-connected device on macOS or Linux is recognized by `adb` without any forwarding step).
- REQ-PROC-054 *Developer Environment Contract (No Host-Execution Bridge)* — AC-02 is the contract this guide realizes.
- [`../decisions/2026-05-19_no-host-bridge.md`](../decisions/2026-05-19_no-host-bridge.md) — the ADR explaining why no automated host-side path exists in any configuration.
