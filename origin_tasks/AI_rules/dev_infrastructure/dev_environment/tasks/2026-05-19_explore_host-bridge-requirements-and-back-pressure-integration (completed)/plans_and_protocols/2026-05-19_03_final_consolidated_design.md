# Final consolidated design — for Phase 4 (requ-explore) input

**Task**: TASK-PROC-054-02
**Date**: 2026-05-19
**Author**: Claude (Opus 4.7), main session
**Status**: APPROVED by user at end of Phase 3
**Supersedes**: 02_design.md (Phase 2 NTFS+bridge design), 02c (WSL exploration), 02d (synthesis), 02e (Option E draft). Those remain on file as the reasoning trail; this doc is the authoritative spec.

This document is the source-of-truth for Phase 4's requirements draft
and Phase 5's implementation. It captures every decision approved
during the user-gate exchange.

---

## 1. Approved architecture in one paragraph

The Flutter project lives on **WSL2 ext4** inside the developer's WSL
distro. The **devcontainer remains at the parent folder level**
(`/workspaces/private_mood_tracker/.devcontainer/devcontainer.json`)
to support git-worktree workflows where Claude Code creates sibling
worktrees that all share one container. The container reads the
project at native ext4 speed; **all daily development — analyze,
dart fix, test, pub get, builds for Linux/Android/Web — runs in the
container with no host-side routing**. A **Mutagen daemon** on the
Windows host continuously syncs WSL ext4 ↔ a local NTFS mirror,
giving Windows-side tools a normal NTFS path for manual release
work. The **host-execution bridge is deleted entirely**; the
pre-push git bundle hook continues to back up to the existing
cloud-synced folder. **Agentic integration testing runs on a new
Linux desktop target with headless Xvfb** in the container — fully
LLM-autonomous. **Android coverage (emulator or physical USB
device) and Windows pre-release smoke testing are deferred to
Phase 7 follow-up tasks.**

---

## 2. The complete set of approved decisions

| # | Decision | Choice | Notes |
|---|---|---|---|
| D0 | Architecture model | **(E) Delete the bridge entirely; WSL ext4 + Mutagen** | Phase 2 §2.3 of 02e doc carries this |
| D1–D6 | Bridge whitelist trim, rename | **moot** — bridge deleted | n/a |
| D7 | Dispatcher facade | **moot** — no bridge to dispatch to | n/a |
| D8 | "Slow" threshold | **moot** | n/a |
| D9 | Auto-detection | **moot** | n/a |
| D10 | Dispatcher config location | **moot** | n/a |
| D11 | Watcher install location | **moot** (no watcher) | n/a |
| D12 | Cheap-wins | **moot** (no watcher to harden) | n/a |
| D13 | Phase 5 scope | §6 below | revised |
| D14 | requirements.md packaging | one doc in renamed `dev_environment/` package | §4 |
| D15 | Sync tool | **Mutagen** | §3.2 |
| D16 | Sync mode | **one-way-safe** (WSL → NTFS); user can flip to two-way-safe if they edit on Windows side | §3.2 |
| D17 | Disaster recovery | **git push + weekly `wsl --export` + Mutagen mirror + pre-push bundle (existing)** | §3.3 |
| D18 | Setup runbook location | `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/` | §4 |
| D19 | Add Linux desktop as Flutter target with Xvfb | **YES** — primary LLM-autonomous integration target | §3.4 |
| D20 | Android emulator narrow-watcher | **YES — design captured here; implementation deferred to Phase 7** | §3.4, §7 |
| D21 | Drop Windows integration tests as daily LLM workflow | **YES — kept as pre-release manual smoke** | §3.4 |
| D22 | Split testing mechanism (this task) vs strategy (Phase 7 task) | **YES** | §7 |
| D23 | UI screenshot mechanism | **widget goldens for single-widget LLM iteration; Xvfb integration screenshots for flows; WSLg/X11 deferred** | §3.5 |
| D24 | Android via physical USB device | **YES — same target shape as emulator (`flutter test integration_test -d <device-id>`); `usbipd attach` or `adb tcpip` from container** | §3.4 |
| D25 | Cloud sync of Mutagen folder | **NO** — git + pre-push bundle is enough | §3.2 |
| D26 | Delete `flutter_app/.vscode/tasks.json` | **YES** | §6 |
| D27 | Keep `.devcontainer/` at parent level | **YES** — required for git-worktree workflow | §3.1, §5 |
| D28 | Parent .vscode/tasks.json (multi-Claude launcher) | **stays in parent**, container-writable accepted as residual risk | §5 |

---

## 3. Specification

### 3.1 Repository / filesystem topology

```
WSL2 ext4 (~/projects/private_mood_tracker/)
├── .devcontainer/devcontainer.json       (parent-level; supports worktrees)
├── .vscode/tasks.json                    (parent; multi-Claude launcher; personal)
├── flutter_app/                          (THE git repo)
│   ├── .vscode/                          (in git; tasks.json DELETED in Phase 5)
│   ├── .githooks/pre-push                (preserved)
│   ├── mutagen.yml                       (NEW — committed)
│   ├── linux/                            (NEW — Flutter Linux scaffolding)
│   └── ...
└── <sibling worktrees on demand>

Windows NTFS (C:\private_mood_tracker_mirror\flutter_app\)
└── (Mutagen-synced working copy of flutter_app/ for manual Windows builds)

Windows NTFS (~/Projekte/Appentwicklung/private_mood_tracker/flutter_app)
└── (Cloud-synced; receives pre-push bundle from existing hook;
     mounted into container at /home/vscode/backup)
```

The Windows-side live project location (`Projekte Lokaler
Arbeitsbereich/private_mood_tracker/`) is **retired**. WSL ext4 is
source-of-truth. The user moves their checkout to WSL2 once and
never edits on Windows again, except via the Mutagen mirror for
manual builds.

### 3.2 Mutagen sync configuration

**Tool**: Mutagen (`mutagen.io`). Installed once on the Windows host.

**Why Mutagen** (recapping from 02b research):
- Has a documented WSL bridge (`wsl-bridge://...`) that escapes the
  9P bottleneck by using `wsl.exe` shell transport, not `\\wsl$\`.
- Purpose-built for "developer keeps two filesystems in sync".
- Near-realtime propagation; lightweight idle daemon (~50–100 MB
  RAM, ~0 CPU at rest).

**Sync config** (`flutter_app/mutagen.yml`, committed):

```yaml
sync:
  defaults:
    mode: one-way-safe         # WSL → NTFS; NTFS is mirror, not source
    ignore:
      paths:
        - .dart_tool
        - build
        - .git
        - "*.swp"
        - .DS_Store
        - node_modules
        - .pub-cache
        - integration_test/screenshots   # generated locally; LLM-readable but not for mirror

  flutter_app_to_windows:
    alpha: /home/<user>/projects/private_mood_tracker/flutter_app
    beta:  wsl-bridge://Windows/C:/private_mood_tracker_mirror/flutter_app
```

**Mode rationale**: `one-way-safe` because the developer edits in
the container (LLM) and at most reviews/runs builds on Windows.
Windows-side accidental writes (e.g., build outputs) are preserved,
not overwritten by sync. If the user later edits source on Windows
side, flip to `two-way-safe` — conflicts surface as `.conflict`
files for manual resolution.

**Lifecycle**: Windows Task Scheduler entry starts the Mutagen
daemon at user logon with restart-on-failure. `mutagen sync list`
exit code is the healthcheck.

**Pre-build flush**: a one-line PowerShell alias
`Build-Win = { mutagen sync flush flutter_app_to_windows; flutter
build windows }` documented in the setup guide. User uses this
before manual Windows builds to guarantee freshness.

### 3.3 Backup strategy

Three independent layers:

1. **Git push to remote** — every push goes to the GitHub remote.
   Standard offsite copy.
2. **Pre-push bundle** — existing `.githooks/pre-push` creates
   `git bundle --all` → writes to `/home/vscode/backup` → mounts to
   the cloud-synced `~/Projekte/Appentwicklung/...` folder. Captures
   full git state (branches, stashes, reflog) that a working-tree
   mirror does not. **Preserved unchanged.**
3. **Mutagen NTFS mirror** — continuous, current working tree on
   NTFS. Useful for "I accidentally `rm -rf`'d something in WSL"
   recovery within the sync window.

Optional fourth layer: weekly `wsl --export` to capture the entire
ext4.vhdx. Documented in setup guide as user-discretionary.

### 3.4 Integration test architecture

**Three target types, three different lifecycles:**

| Target | Where it runs | LLM-triggerable? | Cadence | Status in Phase 5 |
|---|---|---|---|---|
| **Linux desktop** | container, headless Xvfb | **yes** | every change | **implement** |
| **Android emulator** | Windows host, emulator | yes via narrow watcher | LLM-triggered when designing Android-specific features | **design, defer impl to Phase 7** |
| **Android physical device** | USB-connected device | yes via `usbipd attach` or `adb tcpip` | when physically plugged in | **document as supported path** |
| **Windows desktop** | Windows host | no — manual only | pre-release smoke | **kept as manual; Phase 7 verifies** |

**Linux desktop target — the daily LLM loop:**

- `flutter config --enable-linux-desktop` (one-time, recorded in
  flutter SDK config; committed via setup script or documented).
- `flutter create --platforms=linux .` to scaffold `linux/`. Commit
  the scaffolding.
- `apt install xvfb libgtk-3-dev libblkid-dev liblzma-dev` etc. in
  `.devcontainer`'s `postCreateCommand`. Cirruslabs flutter image
  may already include some; verify and add what's missing.
- Tests run via `xvfb-run -a flutter test integration_test -d
  linux` from the container.

**Android emulator narrow watcher — design captured, deferred:**

When the user wants Android coverage in agentic mode:
- A Windows-side script (installed once at `~/host-tools/android-emulator-watcher.ps1`,
  out-of-repo) polls for a sentinel file like
  `~/projects/private_mood_tracker/flutter_app/.devtools/request-android-emulator-start`.
- LLM creates the sentinel → watcher detects → starts the emulator
  via `emulator -avd <name>`.
- LLM then runs `flutter test integration_test -d <emulator-ip>:5555`.
- Watcher does NOT read project files, does NOT take container-supplied
  parameters. Security profile: V1–V6 closed by construction; V7
  mitigated by out-of-repo install (cheap-win 6.5 pattern).

**Android physical device path:**

- USB-connected: `usbipd list` from Windows admin shell to get
  `BUSID`; `usbipd attach --wsl --busid <id>` to forward into WSL2.
  Container's `adb devices` then sees it.
- Wireless: on the device once, `adb tcpip 5555`; from container
  `adb connect <device-ip>:5555`. Persists until device reboots.

Both paths are documented in the setup guide; the LLM can invoke
either when a device is connected.

**Windows desktop target:**

The existing `scripts/integration_test_runner/run_individual_integration_tests.ps1`
is preserved unchanged. Developer runs it manually on the Mutagen
NTFS mirror before release. Tests today are broken (user note);
their repair is out of scope of this task.

### 3.5 UI screenshot mechanism (for LLM-iterated widget work)

**Single-widget iteration** — golden tests:

```dart
testWidgets('NewWidget renders correctly', (tester) async {
  await tester.pumpWidget(const NewWidget());
  await expectLater(
    find.byType(NewWidget),
    matchesGoldenFile('new_widget.png'),
  );
});
```

LLM workflow:
1. Write/modify widget.
2. Run test with `flutter test --update-goldens path/to/test.dart`.
3. Read the generated PNG via the Read tool.
4. Iterate.

Runs in container with no display server. The PNG goes into the
repo as a golden if the LLM wants regression coverage, or stays
local if it's just a "what does it look like" artifact.

**Flow-level screenshots** — integration tests with Xvfb:

```dart
final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
await binding.takeScreenshot('after_login');
```

Same `xvfb-run` setup as integration tests. Screenshots land in
`integration_test/screenshots/` (gitignored, ephemeral). LLM reads
them.

**Golden discipline note**: goldens are platform-rendering-sensitive
(font metrics, anti-aliasing). Linux-generated goldens won't byte-
match Windows-generated goldens. The committed goldens are
**Linux-platform truth**. The Phase 7 verification_strategy task
will codify this.

**WSLg / X11 forwarding**: deferred. Not needed for LLM iteration
(LLM reads images, not live windows). Trivially addable later via
devcontainer.json mounts.

---

## 4. Documentation package layout

Rename:
```
requirements_tasks/process/AI_rules/dev_infrastructure/host_bridge/
                    ↓
requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/
```

Final contents:

```
dev_environment/
├── requirements.md                              ← Phase 4 produces this via requ-explore
├── decisions/
│   └── 2026-05-19_no-host-bridge.md            ← ADR; references pen-test report + this task's plans_and_protocols
└── setup_guides/
    ├── wsl_devcontainer_setup.md               ← blessed config
    ├── mutagen_setup.md                        ← Mutagen install + mutagen.yml + Task Scheduler entry
    ├── android_device_setup.md                 ← usbipd / adb tcpip walkthrough
    └── non_windows_setup.md                    ← best-effort: Mac, native Linux (no WSL, no Mutagen)

tasks/
└── 2026-05-19_explore_host-bridge-requirements-and-back-pressure-integration/
    └── (this task; renamed-or-not depending on Phase 5 choice; the historical name is fine)
```

**Top-level README.md** at repo root: add a "Getting Started"
section with one paragraph + link to
`requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/setup_guides/wsl_devcontainer_setup.md`.

---

## 5. Accepted residual risks (must be documented in the requirement)

1. **Parent folder `.devcontainer/devcontainer.json` and
   `.vscode/tasks.json` are LLM-writable.** Required for the
   git-worktree workflow. Mitigated by VS Code Workspace Trust
   discipline + occasional human inspection of those two files.
2. **WSL ext4.vhdx corruption** is rare but possible. Mitigated by
   the three-layer backup strategy.
3. **Mutagen daemon silently stops** is possible. Mitigated by
   Task Scheduler restart-on-failure + manual `mutagen sync flush`
   before Windows builds.
4. **Linux-target tests catch fewer platform-specific bugs than
   Windows-target tests.** Mitigated by pre-release manual Windows
   smoke check (Phase 7 verification_strategy).
5. **Golden tests are platform-rendering-sensitive.** Linux is the
   authoritative golden platform; goldens regenerated on other
   platforms won't match. Codified in Phase 7
   verification_strategy.
6. **Camera platform code is untested on Linux.** Camera tests can't
   be automated anyway (require human QR-code holding). No new
   automation gap — manual smoke check covers this.

---

## 6. Phase 5 implementation roadmap (final)

Group A — deletions (small, mechanical):

1. Delete `scripts/win-command-bridge/` (whole folder, including
   tests, watcher, signal files).
2. Delete `flutter_app/.vscode/tasks.json` (only the bridge auto-launch task lives there).
3. Remove all bridge references from `.claude/skills/verify-quality/skill.md`
   (Step 3.2 becomes direct `flutter analyze` invocation).
4. Remove bridge references from `doc/linter/linter_setup_and_guidelines.md`.
5. Remove bridge references from any other in-repo doc.

Group B — CLAUDE.md surgery:

6. Rewrite CLAUDE.md §7 entirely. Old "Windows command bridge" section
   becomes "Developer environment" section: brief paragraph stating
   WSL ext4 + Mutagen + Linux integration tests; pointer to
   `dev_environment/setup_guides/wsl_devcontainer_setup.md` for
   actionable steps.
7. CLAUDE.md cleanup: any other reference to the bridge throughout
   the file.

Group C — Mutagen + WSL setup (no code; new config + docs):

8. Author `flutter_app/mutagen.yml` per §3.2.
9. `.gitignore`: add Mutagen state file patterns.
10. Author `dev_environment/setup_guides/wsl_devcontainer_setup.md`.
11. Author `dev_environment/setup_guides/mutagen_setup.md`.

Group D — Linux desktop integration test capability:

12. `flutter config --enable-linux-desktop` documented in setup
    guide (one-time per developer machine).
13. `flutter create --platforms=linux .` to scaffold `linux/`;
    commit the scaffolding (small files, all auto-generated by
    Flutter).
14. Update `.devcontainer/devcontainer.json` `postCreateCommand`
    (or new `postCreate.sh`) to `apt install xvfb libgtk-3-dev
    libblkid-dev liblzma-dev` (verify which are needed against
    cirruslabs/flutter base).
15. Optional: a small wrapper script
    `scripts/quality/run_integration_tests_linux.sh` that wraps
    `xvfb-run -a flutter test integration_test -d linux`; or
    document the invocation in the setup guide and let `verify-quality`
    or future gates call it directly.

Group E — Android device documentation:

16. Author `dev_environment/setup_guides/android_device_setup.md`
    (usbipd + adb tcpip walkthrough).

Group F — Non-Windows developers:

17. Author `dev_environment/setup_guides/non_windows_setup.md`
    (Mac, native Linux: no Mutagen, project lives on local FS,
    container reads it normally; manual Windows builds via cloud-
    based Windows runner or skipped).

Group G — Requirements + ADR (Phase 4 actually writes these):

18. `requirements.md` for `dev_environment/` (via `requ-explore`).
19. `decisions/2026-05-19_no-host-bridge.md` (ADR).

Group H — README:

20. Add "Getting Started" section to top-level README.md with
    pointer to setup_guides/.

Group I — Verification (Phase 6):

21. Time `flutter analyze` in WSL ext4 container — assert ~1 min.
22. Time `dart fix --apply` — assert ~30 s.
23. Run `verify-quality` end-to-end in container, confirm no
    bridge reference fires.
24. Confirm `flutter build windows` succeeds against the Mutagen
    NTFS mirror.
25. Smoke check: write a tiny golden test for an existing widget,
    confirm Claude can read the generated PNG via the Read tool.
26. Smoke check: run `xvfb-run flutter test integration_test -d
    linux` against a trivial example test; confirm pass/fail
    reaches stdout cleanly.

Effort estimate: ~1 working day for Groups A–H, ~half day for
Group I.

---

## 7. Phase 7 follow-up tasks (to be created at end of Phase 5)

These are intentionally bounded OUT of this task. Each gets its own
goal.md via `task-create`:

**F1 — Implement Android emulator narrow-watcher.**
Goal: install-once watcher at `~/host-tools/android-emulator-watcher.ps1`;
poll for sentinel file; start AVD on request; produce result file
that container can read for emulator IP/port. Watcher script itself
out-of-repo (cheap-win 6.5 pattern). Setup guide entry +
verification PoC.

**F2 — Write verification_strategy requirement (new REQ).**
Covers: which test types are required when, coverage targets per
test type, golden-file discipline and platform-truth, pre-release
manual Windows smoke checklist, cadence rules
(per-change vs release-cadence), camera-code manual smoke procedure.
Seeds from this task's exploration captured in the goal.md.

**F3 — Repair / rewrite the existing integration tests targeting
Linux desktop.**
User notes the existing tests are broken. Out of scope of this
task. New task: bring them up to date, target Linux desktop as the
primary platform per §3.4. Camera-related tests stay manual.

**F4 — (Optional, low priority) WSLg / X11 forwarding in
devcontainer for visible Linux app runs during interactive dev.**
Trivial config addition; deferred until user actually wants it.

---

## 8. What Phase 4 produces (input for requ-explore)

The `requ-explore` skill is invoked next with the following framing:

> Create requirements.md for the new package
> `requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/`.
> Source-of-truth for content: `2026-05-19_03_final_consolidated_design.md`
> in this task's plans_and_protocols folder (§3 spec + §5 residual
> risks + §6 implementation roadmap).
>
> The requirement codifies the **supported developer environment
> contract** and the **decision against having a host-execution
> bridge**. Audience: future developers / future LLM sessions
> reading the repo cold who need to understand "how does
> development actually happen on this project?"
>
> Forward-references to be left as TBD pointers:
> - REQ-PROC-053 (verification_strategy) — to be written in
>   Phase 7 F2 follow-up task.
>
> Coverage required (acceptance criteria):
> 1. Supported config (WSL2 ext4 + devcontainer + Mutagen).
> 2. Optionality contract for Mac / native Linux / Windows-without-WSL.
> 3. Bridge-deleted decision recorded; reference to decisions/
>    ADR and to TASK-PROC-054-01 pen-test report.
> 4. Daily-development model: 100% in-container; no host-side
>    routing; quality gates run in-container.
> 5. Manual Windows operations model: developer runs
>    `flutter build windows` and integration tests on the Mutagen
>    NTFS mirror.
> 6. Integration test mechanism per target (Linux/Android/Windows).
> 7. Screenshot mechanism for LLM-iterated UI work.
> 8. Backup strategy (three layers).
> 9. Accepted residual risks (parent-folder writability,
>    ext4.vhdx, Mutagen failure mode, golden-platform-truth,
>    camera coverage gap).

---

## 9. Provenance trail

For the future reader who lands on this doc: the reasoning chain
that produced these decisions lives in this task's
`plans_and_protocols/` folder in numbered order:

- `2026-05-19_00_user_initial_input.md` — verbatim brainstorm seed
- `2026-05-19_01_gather.md` — Phase 1 inventory
- `2026-05-19_02a_web_research.md` — Sandbox / restricted-user /
  devcontainer-mount / prior-art research
- `2026-05-19_02_design.md` — original Phase 2 NTFS+bridge design
  (Option A); superseded
- `2026-05-19_02b_wsl_drive_research.md` — `\\wsl$\` perf + UNC
  toolchain compatibility research
- `2026-05-19_02c_wsl_drive_analysis.md` — exploration of WSL-drive
  models; superseded
- `2026-05-19_02d_final_synthesis.md` — option C synthesis;
  superseded
- `2026-05-19_02e_option_e_delete_bridge.md` — Option E first
  draft; superseded
- `2026-05-19_03_final_consolidated_design.md` — **THIS DOC; the
  authoritative spec**

The pen-test report from TASK-PROC-054-01 (in that completed task's
plans_and_protocols folder) is the load-bearing input that made
the bridge's threat surface concrete and forced the rethink.

End of consolidated design.
