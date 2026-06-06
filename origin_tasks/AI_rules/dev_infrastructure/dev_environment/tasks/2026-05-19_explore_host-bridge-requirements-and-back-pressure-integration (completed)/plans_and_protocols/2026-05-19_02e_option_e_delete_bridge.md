# Phase 2 — Option E: Delete the bridge entirely

**Task**: TASK-PROC-054-02
**Date**: 2026-05-19
**Author**: Claude (Opus 4.7), main session
**Status**: DRAFT — supersedes the recommendation in `02d_final_synthesis.md`.

This option emerged from user feedback after `02d` ("can we even remove
the bridge altogether?"). It is the simplest architecture in the
option set and — given the empirical data from `02a` and `02b` — also
the strongest on every axis: security, simplicity, and daily speed.

---

## 1. The model in one paragraph

The Flutter project lives on WSL2 ext4. The devcontainer reads it
natively (fast). Every daily-development command — `flutter analyze`,
`dart fix`, `flutter test`, `flutter pub get`, `flutter build apk`,
`flutter build linux`, integration tests against Android/Linux —
runs in the container. **No bridge.** A continuous sync daemon
(Mutagen) running on the Windows host keeps an NTFS mirror of the
project current. Windows-targeted operations (`flutter build
windows`, smoke test, Windows integration tests, release packaging)
are **user-triggered, manual**, run from a Windows PowerShell session
against the NTFS mirror. The bridge is deleted entirely.

---

## 2. What this trades away

Honest cost accounting:

1. **Manual discipline for Windows-target operations.** The user
   remembers to run `flutter build windows` and the smoke test on
   the Windows side before release. There is no automated
   container-to-Windows trigger.
2. **No automation of Windows integration tests.** Today's
   integration_test_runner already lives in `scripts/windows/` and
   is run on Windows. That stays manual.
3. **A continuous-sync daemon to install and supervise.** Mutagen
   (or equivalent). New per-Windows-machine setup step.
4. **WSL ext4 as the primary source-of-truth.** Disaster recovery
   relies on Mutagen-mirrored NTFS + git push + periodic
   `wsl --export`.

---

## 3. What this buys

Big wins on every axis:

### 3.1 Speed (the original problem)

| Command | Today | Option E |
|---|---|---|
| `flutter analyze` | 10–17 min via bridge | **~1 min in container** |
| `dart fix --apply` | bridge (>10 min, times out) | **~30 s in container** |
| `flutter pub get` cold | minutes via bridge | **~10 s in container** |
| `flutter test` | slow but works | **fast in container** |
| `flutter build apk` | container | container |
| `flutter build linux` | n/a | container |
| `flutter build windows` | bridge → host | manual on host (no bridge) |
| Smoke test | bridge → host | manual on host (no bridge) |

The container hot loop becomes ~10× faster.

### 3.2 Security

| Pen-test vector | Today | Option E |
|---|---|---|
| V1 (flutter_test → Dart on host) | critical | **moot — no bridge** |
| V2 (smoke_test → PS on host) | critical | **moot — no bridge** |
| V3 (analyzer plugin on host) | high | **moot — analyze runs in container only** |
| V4 (CMake execute_process on host) | high | **moot — no automated build path** |
| V5 (pub fetch pivot via host) | high | **moot — pub get runs in container only** |
| V6 (dart fix backdoor) | medium | **moot — dart fix runs in container only** |
| V7 (watcher restart deception) | medium | **moot — no watcher exists** |
| V8 (WSL→NTFS symlink) | low-med | low (no symlink follows host since no host-side automation reads them) |

**The entire pen-test threat model evaporates.** When the user runs
`flutter build windows` manually, they own the trust decision the
way they own any "I'm running a command on my own machine"
decision. There is no automated path from a compromised LLM to host
code execution.

### 3.3 Operational complexity

- No watcher PowerShell to install, supervise, audit-log, or
  reference-copy-check.
- No restricted Windows user account, AppLocker rules, firewall
  outbound rules, scheduled tasks.
- No `icacls` post-clone step (no scripts to ACL).
- No dispatcher facade, no config file, no per-tool routing rules.
- No bridge tests to maintain (`test_win_bridge.sh` deleted).
- One new thing: Mutagen daemon. Mature, well-documented.

### 3.4 Disaster recovery

Mutagen keeps NTFS in sync with WSL. If the WSL `ext4.vhdx`
corrupts, the NTFS mirror is the latest known-good copy. If NTFS
corrupts, the WSL ext4 is the latest known-good copy. Either side
recovers from the other. Add `wsl --export` weekly and git push
always = three layers of redundancy.

---

## 4. The Mutagen setup

### 4.1 Tool choice

Mutagen wins because:
- Purpose-built for "developer keeps two filesystems in sync"
- Has a documented WSL bridge that escapes the 9P bottleneck (uses
  `wsl.exe` shell transport, not `\\wsl$\` 9P) — see
  research `02b` source [27] and [28]
- Cross-platform; consistent CLI; near-realtime propagation
- One config file (`mutagen.yml`) per project — checked into the
  repo as the documented configuration

Alternatives considered and rejected (full table in section 4 of
`02d`):
- **Unison**: open watcher bug on WSL (bcpierce00/unison #264)
- **inotifywait + rsync to `/mnt/c/`**: rsync to `/mnt/c/` is
  *documented slow* (microsoft/WSL #5299)
- **robocopy on Task Scheduler**: not real-time; bursty I/O;
  carries the deletion-semantics hazard of `/MIR`
- **PowerShell FileSystemWatcher on `\\wsl$\`**: change events on
  network shares unreliable

### 4.2 `mutagen.yml` shape (sketch)

```yaml
sync:
  defaults:
    mode: one-way-safe         # WSL is source-of-truth; NTFS mirrors
    ignore:
      paths:
        - .dart_tool
        - build/linux
        - build/android
        - build/ios
        - build/web
        - .git              # git lives on WSL side; Windows builds
                            # do not need the .git directory
        - "*.swp"
        - .DS_Store
        - node_modules
        - .pub-cache

  flutter_app_to_windows:
    alpha: /home/<user>/projects/private_mood_tracker/flutter_app
    beta:  "wsl-bridge://Windows/C:/private_mood_tracker_mirror/flutter_app"
```

Note `mode: one-way-safe`:
- "one-way" means changes propagate WSL → NTFS only (the user's
  default workflow edits files in the container).
- "safe" means deletions on the source side propagate, but
  conflicts on the destination side (e.g. Windows build outputs)
  are preserved and surfaced rather than overwritten.

If the user also edits files on Windows side (e.g. opens
`windows/runner/main.cpp` in Visual Studio), flip to `two-way-safe`.

### 4.3 Mutagen lifecycle

- Windows Task Scheduler entry: starts Mutagen daemon at user
  logon; restart on failure.
- `mutagen sync list` exit code = healthcheck.
- `mutagen sync flush flutter_app_to_windows` = force up-to-date
  before invoking a Windows build. (Optional manual checkpoint;
  the user runs it if they just made a change in the container
  and want to switch over to Windows immediately.)

### 4.4 Daily workflow

| Activity | Where | How |
|---|---|---|
| Code edit (LLM / human) | Container (VS Code Remote) | `code .` in WSL via VS Code's Remote-Containers; edits land on WSL ext4 |
| Run quality gates | Container | `verify-quality` skill calls `flutter analyze` directly (no bridge) |
| Run tests | Container | `flutter test` etc. |
| Commit | Container | `git commit` in WSL |
| Build Windows .exe | Windows | open PowerShell, `cd C:\private_mood_tracker_mirror\flutter_app`, `flutter build windows` |
| Smoke test | Windows | run the resulting `.exe`, or `scripts/windows/smoke_test_windows.ps1` |
| Mutagen | always running | invisible; auto-syncs |

The user only switches to the Windows side when they want to test
the Windows variant. Day to day, they don't leave the container.

---

## 5. Migration plan (Phase 5 under Option E)

Effort estimate: ~0.5–1 working day. Smaller than Phase 2's plan
because deletion is cheaper than refactoring.

### 5.1 Setup runbook (new doc)

`doc/dev_infrastructure/wsl_setup.md` — one-page instructions:

1. Confirm WSL2 distro is installed.
2. `git clone` into `~/projects/private_mood_tracker` inside WSL.
3. Install Mutagen on Windows: `winget install mutagen-io.mutagen`.
4. Copy the repo-tracked `mutagen.yml` into use:
   `mutagen project start` from the project root.
5. Create Task Scheduler entry for Mutagen daemon at logon.
6. Open VS Code, "Reopen in Container" against the WSL path.
7. Done. Daily work happens here.
8. For Windows builds: open PowerShell on Windows, `cd
   C:\private_mood_tracker_mirror\flutter_app`, run `flutter
   build windows`.

### 5.2 Deletion list

- `scripts/win-command-bridge/` (entire folder)
- All references in CLAUDE.md §7 (rewrite as a short paragraph
  pointing at `doc/dev_infrastructure/wsl_setup.md`)
- All references in `.claude/skills/verify-quality/skill.md` (Step
  3.2 simplifies — direct `flutter analyze` instead of bridge call)
- All references in `doc/linter/linter_setup_and_guidelines.md`
- `.vscode/tasks.json` line that auto-starts the watcher

### 5.3 Repo additions

- `mutagen.yml` — committed
- `.gitignore` — add Mutagen state files / OS lock files
- `doc/dev_infrastructure/wsl_setup.md` — new
- `.devcontainer/devcontainer.json` — update workspace folder
  source to point at WSL ext4 path (was `~/Projekte/.../flutter_app`,
  becomes `~/projects/.../flutter_app`); slim B mount is moot
  (no scripts/host-bridge/ folder to mount read-only)

### 5.4 `requirements.md` for the new package

A short doc, not the lengthy one Phase 2 envisioned. Topics:
- Project source-of-truth is on WSL2 ext4 in the supported config.
- Daily development runs in-container at native ext4 speed.
- Continuous WSL → NTFS sync via Mutagen for ergonomic Windows-side
  access; manual Windows builds are the supported model.
- Quality gates run in-container; no bridge dependency.
- Optionality contract: Mac, native Linux, native Windows
  developers work without WSL — they just use the project's NTFS
  copy directly and pay today's slow-analyze cost in-container, or
  run gates on the host. Mutagen and the WSL move are
  Windows-developer accelerations, not correctness requirements.

### 5.5 Verification (Phase 6)

There are no PoCs to demonstrate because there are no bridge
vectors. The verification step is empirical:

- Time `flutter analyze` in container under WSL ext4 — expect ~1 min.
- Time `dart fix --apply` — expect ~30 s.
- Verify the existing test suite + gates run end-to-end without
  bridge invocation.
- Run `flutter build windows` manually on Windows against the
  Mutagen mirror — verify it succeeds and the produced `.exe`
  runs.
- (Optional) `wsl --export` and `wsl --import` round-trip — verify
  the backup workflow.

---

## 6. Updated Phase 3 decision matrix

Replaces both Phase 2 §9 and `02d` §5. The decision space collapses
dramatically.

| # | Decision | Recommendation |
|---|---|---|
| **D0** | **Architecture model** | **(E) Delete the bridge entirely; WSL ext4 + Mutagen continuous sync + manual Windows builds** |
| **D1–D6** | (bridge whitelist trim, rename) | **moot** under E |
| **D7** | (dispatcher facade) | **moot** under E |
| **D8** | ("slow" threshold) | **moot** under E |
| **D9** | (auto-detection) | **moot** under E |
| **D10** | (config location for dispatcher) | **moot** under E |
| **D11** | (watcher install location) | **moot** under E |
| **D12** | (cheap-wins) | **moot** under E |
| **D13** | Phase 5 scope | **deletion + Mutagen setup + WSL setup doc + requirements.md + CLAUDE.md rewrite** |
| **D14** | `requirements.md` packaging | one short doc for `host_bridge/` package (despite the name, it documents the no-bridge architecture and the WSL setup) |
| **D15** | Sync tool | **Mutagen** |
| **D16** | Sync mode | **one-way-safe** (WSL → NTFS); flip to two-way-safe only if user edits on Windows side |
| **D17** | Disaster recovery | git push + weekly `wsl --export` + the Mutagen NTFS mirror itself |
| **D18** | Setup runbook location | `doc/dev_infrastructure/wsl_setup.md` |

---

## 7. Folder rename consideration

The package today is at
`requirements_tasks/process/AI_rules/dev_infrastructure/host_bridge/`.
Under Option E, "host bridge" is misleading — there is no bridge.

Recommendation: rename the package folder during Phase 5 to
`dev_infrastructure/dev_environment/` or similar, and the
requirement document covers "the supported developer environment"
(WSL config + Mutagen + manual Windows operations) rather than
"the bridge". This is a Phase 5 rename, mechanical.

Acceptable alternative: keep the `host_bridge/` folder name out of
inertia and rename only the requirement doc inside it. Less
disruption.

---

## 8. Risks specific to Option E

Honest list, in order of likelihood:

1. **Mutagen daemon silently stops** — user finds out only when
   the Windows build is stale. Mitigation: Task Scheduler restart-
   on-failure + a daily `mutagen sync list` healthcheck.
2. **WSL `ext4.vhdx` corruption** — rare but real. Mitigation:
   three-layer backup (NTFS mirror + `wsl --export` + git push).
3. **User forgets `mutagen sync flush` before a Windows build** —
   builds from stale source. Mitigation: a one-line PowerShell
   alias `Build-Win` that runs `mutagen sync flush; flutter build
   windows`. Document in the setup runbook.
4. **Mutagen version drift between contributors** — if multiple
   developers, they may have different Mutagen versions producing
   different conflict behaviour. Mitigation: pin Mutagen version
   in `mutagen.yml` (Mutagen supports `minimumVersion`).
5. **The user occasionally edits files on Windows side** — needs
   two-way sync. Mitigation: `mode: two-way-safe`; conflicts
   surface as `.conflict` files.
6. **Mutagen on Windows has a memory leak / bug** — rare. Workaround:
   restart the daemon. Mature tool, low risk.

These are operational risks, not architectural risks. No
architectural risk in the security sense remains because there is
no bridge attack surface.

---

## 9. Comparison: where Option E sits among A–E

| Option | Container speed | Windows automation | Bridge surface | Setup cost | Sim­plicity |
|---|---|---|---|---|---|
| (A) Phase 2 (NTFS + bridge + A1) | slow | full | 4 commands | medium | medium |
| (B) WSL + Mutagen continuous + bridge | fast | full | 1–2 commands | high | low |
| (C) WSL + on-demand mirror + bridge | fast | full | 1–2 commands | medium | medium |
| (D) WSL + 9P direct | (broken) | n/a | n/a | n/a | n/a |
| **(E) Delete bridge + WSL + Mutagen** | **fast** | **manual** | **zero** | **low** | **high** |

The only column where E is *not* strictly best is "Windows
automation" — and that's the explicit trade. If you accept
"Windows is a release-time manual operation, not a daily-test
operation", E wins on every other dimension.

---

## 10. The question for your gate

**One decision: do you accept manual Windows builds?**

- Yes → Option E. Everything else falls out of that choice.
- No → fall back to Option C from `02d` (WSL + on-demand mirror
  + bridge for Windows commands only).
- Want to keep automation but stay on NTFS → fall back to
  Option A from Phase 2 (`02_design.md`).

I am recommending Option E because:
- The pen-test attack surface goes to zero, not partial.
- The daily speed win is identical to (B) and (C).
- The implementation is *deletion*, not refactor — usually the
  cheapest change to make.
- Windows builds for a Flutter app are inherently a less-frequent
  activity than the daily code loop. Pushing them to manual aligns
  effort with frequency.

If you say "yes" to the gate question, Phase 4 starts: I invoke
`requ-explore` to produce a short requirements.md for the WSL
developer-environment package, and Phase 5 begins the deletion +
Mutagen setup.
