# Phase 2 — Final Synthesis (for Phase 3 user gate)

**Task**: TASK-PROC-054-02
**Date**: 2026-05-19
**Author**: Claude (Opus 4.7), main session
**Reading order**: this doc → `02_design.md` (full Phase 2 spec for option A) → `02c_wsl_drive_analysis.md` (full WSL exploration) → research reports `02a_web_research.md` / `02b_wsl_drive_research.md` for backup.

This is the single doc you read for the Phase 3 user-gate decision. It
collapses the four architectural options into a head-to-head and ends
with the decision matrix you act on.

---

## 1. What the empirical research established

### 1.1 The "WSL + 9P direct" model is dead

`\\wsl$\<distro>\…` from Windows is broken for Flutter's Windows
build chain at multiple independent layers (all primary-source
documented):

- CMD.EXE refuses UNC `cwd` (the root failure)
- MSBuild 17 lowercase-bugs UNC components → `MSB8064` / `MSB8065`
  warnings; CMake-generated `.vcxproj` triggers them (dotnet/msbuild #7001)
- Flutter strips leading backslashes from UNC paths → "build input
  not found" (flutter/flutter #43594, dart-lang/sdk #52309)
- `flutter pub get` inherits the cmd.exe shim failure (same class as
  npm #6280, yarn #8715)
- PowerShell `RemoteSigned` may refuse UNC scripts; `-ExecutionPolicy
  Bypass` is the documented workaround
- **Microsoft's own supported VS+WSL model goes the opposite direction**
  — sources on Windows, rsync'd INTO WSL

**Verdict: cannot put source-of-truth on WSL ext4 with Windows
tooling reaching it directly via `\\wsl$\`.**

### 1.2 The drive-letter mount path is dead

`subst` and `net use` resolve through the same 9P redirector — same
performance, same UNC bugs. Third-party ext4 drivers (Paragon,
Ext2Fsd) only work on *offline* ext4 volumes — concurrent access
with a live WSL distro is undocumented and risky.

### 1.3 The "WSL + mirror" model is viable

- Mutagen and Unison both have working WSL bridges that "explicitly
  exist to escape 9P" (research's framing).
- Robocopy /MIR works at content level but mangles Linux mode bits
  and Linux symlinks; deletion semantics need explicit excludes.
- rsync from inside WSL → `/mnt/c/…` is documented slow (20-min
  runs for what was 30 s on WSL1) and breaks on NTFS mode-bit
  semantics.
- No tool claims a cross-file consistent snapshot — short race
  windows during sync are unavoidable. Mutagen's `mutagen sync
  flush` command can block until sync is up-to-date, which closes
  the race for explicit synchronization points.

### 1.4 Bidirectional rather than one-way is the practical reality

Microsoft's own VS+WSL walkthrough syncs **into** WSL (sources on
NTFS, copy on WSL). The user's workflow puts the source-of-truth in
the container (where the LLM works). That implies sync goes WSL →
NTFS so Windows tools can use the NTFS copy. But the developer also
edits files in Windows-side tools (VS, GitHub Desktop, code editor
on Windows). So **bidirectional** is the realistic configuration
unless the user is willing to confine all edits to the
container side.

---

## 2. The four options, side by side

| Aspect | (A) Phase 2 design — NTFS + bridge | (B) WSL + Mutagen continuous bidi sync | (C) WSL + bridge-mediated on-demand mirror | (D) WSL + 9P direct (DEAD) |
|---|---|---|---|---|
| Source-of-truth | NTFS only | shared NTFS+WSL (Mutagen-synced) | WSL only | WSL only |
| Container IO speed | **slow** (DrvFs ~10×) | **fast** (native ext4) | **fast** (native ext4) | fast |
| Windows-tool IO speed | native | native (on NTFS copy) | native (on NTFS copy after mirror) | broken |
| `flutter analyze` daily speed | 10–17 min via bridge | **~1 min in container** | **~1 min in container** | n/a |
| `dart fix` daily speed | >10 min, times out via bridge | **~30 s in container** | **~30 s in container** | n/a |
| `flutter test` daily speed | slow in container | **fast in container** | **fast in container** | n/a |
| `flutter build windows` | bridge → native NTFS build | bridge → native NTFS build (on synced copy) | bridge → mirror + native NTFS build | broken |
| Bridge whitelist size | 4 (after A5 trim) | 1–2 (toolchain only) | 1–2 (toolchain only) | n/a |
| Pen-test V1, V3, V5, V6 | partially closed by A1 | **closed** (never routed) | **closed** (never routed) | n/a |
| Pen-test V2, V4 | A1 + whitelist trim | A1 + restricted-account build | A1 + restricted-account mirror+build | n/a |
| Continuous background daemon | none new | **Mutagen on Windows** | none new | n/a |
| Sync race window | n/a | <1 s typical, flush available | only at command time, mirror is sync | n/a |
| Setup steps (one-time per machine) | restricted user + AppLocker + firewall + watcher install | restricted user + Mutagen install + sync config + watcher install | restricted user + watcher install + mirror config | n/a |
| Per-clone setup | icacls post-clone (Git stores no ACLs) | icacls post-clone + initial Mutagen sync | icacls post-clone | n/a |
| Disaster recovery (WSL vhdx corrupts) | n/a | source still on NTFS — fine | source on WSL only — must restore from git/backup | n/a |
| Per-contributor friction | medium (A1 setup) | medium-high (A1 + Mutagen) | medium (A1 + mirror) | n/a |
| LLM sandbox preserved? | yes (when watcher offline) | yes (when watcher offline) | yes (when watcher offline) | n/a |
| Ops complexity | moderate | **highest** (sync daemon) | low (sync inside bridge) | n/a |
| Dispatcher facade (Phase 2 §4) | needed | unneeded (only 1 routed cmd) | unneeded | n/a |

### 2.1 Headline trade-offs

**A vs. B/C**: A is what we have today made safer. B and C are 10×
faster on the developer's hottest loop (`flutter analyze`,
`dart fix`) and have a strictly smaller attack surface (fewer routed
commands). The cost is an additional component: a sync mechanism.

**B vs. C**: B keeps a daemon running; C does sync on-demand inside
the bridge. B has zero per-command latency for Windows builds
(sync is already current). C has mirror-time latency on every
Windows build. For a workflow where Windows builds are episodic
(release-time) and container work is continuous, **C costs less
operational complexity** with comparable speed wins on the daily
loop.

**Setup cost difference between B and C**:
- B adds: Mutagen install + sync config + daemon supervision.
- C adds: mirror tool (robocopy or rsync wrapper) invoked inside the
  watcher.

B's setup is more involved but the daemon is "set and forget";
C's setup is simpler but the mirror logic lives inside the bridge
code (which we control).

---

## 3. Security analysis: are B/C actually safer than A?

### 3.1 Pen-test vectors under each model

| Vector | (A) Phase 2 A5 | (B) WSL + Mutagen | (C) WSL + on-demand mirror |
|---|---|---|---|
| V1 (flutter_test → Dart on host) | closed (trim) | **closed** (never routed) | **closed** (never routed) |
| V2 (smoke_test → PS on host) | closed (trim) | closed (trim still applies) | closed (trim still applies) |
| V3 (analyzer plugins) | partial (A1) | **closed** (never routed) | **closed** (never routed) |
| V4 (CMake execute_process) | partial (A1) | partial (A1) | partial (A1) |
| V5 (pub fetch pivot) | partial (firewall) | **closed** (never routed) | **closed** (never routed) |
| V6 (dart fix backdoor) | open | **closed** (never routed) | **closed** (never routed) |
| V7 (watcher restart deception) | mitigated (cheap-win 6.5) | mitigated (cheap-win 6.5) | mitigated (cheap-win 6.5) |
| V8 (symlink escape) | low | low | low |

B and C convert **four "partial" or "open" vectors into "closed"**
(V3, V5, V6, and V1 is closed under A too but trivially). The only
remaining vector that needs A1 restricted-user mitigation is V4
(CMake), and that's the irreducible cost of having any Windows
build pathway at all.

### 3.2 New surfaces introduced by sync

**B**: the Mutagen daemon runs under the developer's account with
full read of WSL files and full write to NTFS. A compromised LLM in
the container writes a malicious file to WSL → Mutagen propagates
to NTFS → restricted-account watcher reads it via the bridge → V4
fires. Net effect: V4 reaches the watcher as before, A1 still does
its job. **No new vectors of consequence.**

**C**: the bridge invokes the mirror under the restricted account
itself; the dev user has no sync daemon. Trust boundary is tighter
than B by a small margin (one fewer process under dev user with
WSL-read + NTFS-write).

### 3.3 Disaster-recovery posture

**A**: NTFS is the only copy. Risk: NTFS disk failure / accidental
delete. Mitigated by git push.

**B**: both NTFS and WSL hold copies, kept in sync. Either one
surviving = recovery. WSL ext4.vhdx corruption is not catastrophic
because NTFS is still there. **Best DR posture of the three.**

**C**: WSL is the source-of-truth. NTFS holds derived build copies
or the latest mirror snapshot. WSL ext4.vhdx corruption is more
serious; mitigated by `wsl --export` weekly and git push. Worse
than B, comparable to A.

---

## 4. Recommendation

**Adopt option (C) — WSL + bridge-mediated on-demand mirror.**

Reasoning:

1. **It gets the speed win.** The hot loop (`flutter analyze`,
   `dart fix`, `flutter test`, `pub get`) becomes 10× faster — a
   real, daily, every-edit improvement.
2. **It gets the security win.** Four pen-test vectors transition
   from "partial" / "open" to "closed". The remaining V4 has the
   same A1 mitigation it would have under any model.
3. **It minimizes operational complexity.** No always-on sync
   daemon. Sync is a function the bridge invokes; same lifecycle as
   any bridge command.
4. **It keeps the dispatcher trivial.** With only 1–2 routed
   commands, the Phase 2 §4 facade is unnecessary — those callers
   can include a 3-line wrapper. Less code, less surface.

When to prefer (B) instead:

- If the user does substantial editing on the Windows side outside
  the container (VS for native Windows code, Photoshop, etc.) and
  wants those edits visible in the container with sub-second
  latency.
- If the user prefers continuous sync and is comfortable with the
  Mutagen daemon.

When to prefer (A) instead:

- If the user is unwilling to accept *any* sync mechanism — wants
  one filesystem, period.
- If WSL ext4 reliability concerns dominate (rare but cited).

When to prefer (D) — never. Empirically broken.

---

## 5. Updated Phase 3 decision matrix

Replaces Phase 2 §9. Each row is a decision; recommendation shown.

| # | Decision | Recommendation | Alternatives |
|---|---|---|---|
| **D0** | **Architecture model** | **(C) WSL + on-demand mirror** | (A) NTFS + bridge (Phase 2), (B) WSL + Mutagen continuous |
| **D1** | Long name | `host-execution bridge` | other variants in `02_design.md` §2.2 |
| **D2** | Short name | `host bridge` | other variants |
| **D3** | Folder rename | `scripts/host-bridge/` | other variants |
| **D4** | Trust architecture (within model) | **A1'** = A1 restricted Windows user + `smoke_test` removed; `flutter_test`/`flutter_analyze`/`dart_fix`/`flutter_pub_get` not on whitelist (run in container fast) | A1 without removal, A4 (accept openly) |
| **D5** | Remove `flutter_test` from broker whitelist | **moot under (C)** — flutter_test runs in container at fast speed; never routed | n/a |
| **D6** | Remove `smoke_test` from broker whitelist | **Yes** | hash-pin instead |
| **D7** | Dispatcher facade (Phase 2 §4) | **drop** — only 1–2 routed commands; callers use a 3-line wrapper | keep facade |
| **D8** | "Slow" threshold | **drop** — broker is no longer a speed mechanism, only a toolchain mechanism | keep |
| **D9** | Auto-detection | No env sniffing; broker `probe` is sufficient | yes |
| **D10** | Config location | broker config in `scripts/host-bridge/`; no dispatcher config | yaml in repo |
| **D11** | Watcher install location | `~/host-bridge-watcher/` on Windows, outside repo | keep in repo |
| **D12** | Cheap-wins kept | 6.3 (absolute paths), 6.4 (request size bound), 6.5+6.6 (watcher out-of-repo + reference-copy check), 6.7 (audit log) | drop any subset |
| **D13** | Phase 5 scope | rename + A1' + on-demand mirror in watcher + WSL setup doc + slim B mount + CLAUDE.md update + `requirements.md` | broader |
| **D14** | `requirements.md` packaging | one consolidated doc covering broker + mirror + WSL workflow | split |
| **D15** | Mirror tool inside bridge | **robocopy /MIR with explicit excludes** for the WSL→NTFS direction (simple, ships with Windows, well-understood deletion semantics) | Mutagen one-way, rsync from PowerShell, custom |
| **D16** | NTFS mirror destination | A dedicated folder under restricted account, e.g. `C:\host-bridge\mirror\private_mood_tracker\` | overwrite original location |
| **D17** | Backup strategy | git push (already habit) + weekly `wsl --export` of distro | full machine backup |
| **D18** | New per-contributor setup doc | `doc/dev_infrastructure/host_bridge_setup.md` covering WSL ext4 move, watcher install, mirror config, backup | inline in CLAUDE.md |

---

## 6. New Phase 5 implementation roadmap (replaces Phase 2 §8)

Smaller scope than Phase 2's roadmap because the dispatcher drops out.

1. **Setup doc** — `doc/dev_infrastructure/host_bridge_setup.md`:
   - Move project from `~/Projekte/.../flutter_app` (NTFS) to
     `~/projects/.../flutter_app` (WSL ext4)
   - Update `.devcontainer/devcontainer.json` mount source
   - Install restricted Windows user, AppLocker, firewall
   - Install watcher to `~/host-bridge-watcher/`
   - Configure mirror destination
   - Set up `wsl --export` backup task

2. **Rename pass** — `scripts/win-command-bridge/` → `scripts/host-bridge/`
   + all file/env-var renames per Phase 2 §2.3.

3. **Updated watcher** — `host_bridge_watcher.ps1`:
   - Absolute-path resolution at startup (cheap-win 6.3)
   - Request-file size bound (6.4)
   - Reference-copy startup check vs. in-repo source (6.5+6.6)
   - Audit log to `~/host-bridge-watcher/audit.log` (6.7)
   - Mirror invocation before each whitelisted command
   - Trimmed whitelist: `flutter_build_windows` only (or +
     `flutter_test_windows_integration` if user wants Windows
     integration tests routed)

4. **Mirror script** — `scripts/host-bridge/mirror_wsl_to_ntfs.ps1`:
   - One-way WSL → NTFS robocopy with explicit excludes
     (`.dart_tool/`, `build/linux/`, `build/android/`, `.git/` —
     git remains in the WSL-side source-of-truth)
   - Idempotent; called by the watcher pre-command
   - Logs to the audit log

5. **Container-side configuration**:
   - `.devcontainer/devcontainer.json` — point mount source at WSL
     ext4 path; add `scripts/host-bridge/` read-only subpath mount
     (slim B)
   - Existing `~/.claude`, `~/.ccs` etc. mounts unchanged

6. **CLAUDE.md §7 update** — rewrite to:
   - Reflect new name
   - Explain the WSL-drive setup as the supported configuration
   - Restate the optionality contract (Mac / native Linux work
     without bridge, no WSL drive needed)
   - List the trimmed whitelist
   - Document the mirror behavior

7. **`requirements.md`** for `host_bridge/` (Phase 4 via `requ-explore`).

8. **Verification PoCs (Phase 6)** — adapted V1 and V4 PoCs:
   - V1 (flutter_test → host): since flutter_test never routes,
     PoC must instead try to invoke it via the bridge — bridge
     rejects (not on whitelist). Inert.
   - V4 (CMake): demonstrate that `flutter_build_windows` runs
     under the restricted account; payload in CMakeLists.txt
     achieves only restricted-account privileges, not developer-
     account.

Estimated effort: ~1 working day for the code; the developer's WSL
move is a one-off ~30 min activity using a clear runbook.

---

## 7. Open questions still parked for Phase 5

- Empirical measurement: actual robocopy mirror time for
  `flutter_app` from `\\wsl$\…` to `C:\…`. If it's >30 s on a
  typical machine, the user feels it on every Windows build. We
  may want to keep an exclude list large enough that the mirror is
  effectively small.
- Whether `flutter build windows` actually succeeds against the
  mirror copy with the user's specific Visual Studio configuration.
  Worth a 10-minute Phase-5 smoke test.
- AppLocker policy testing on a non-AD-joined home machine — works
  in principle per research, untested in this setup.
- Outbound Firewall rule scoped to a single Windows user account —
  same.
- VS Code's behaviour with the project on WSL ext4 and the
  devcontainer mount pointing at the WSL path. Likely works
  trivially (it's the default "Open Folder in WSL" + "Reopen in
  Container" flow), but worth confirming.

These are Phase 5 smoke-tests, not architecture-altering
uncertainties.

---

## 8. What I'm recommending you say "no" to

Three things you should explicitly veto if you disagree:

- **(D0)**: WSL + on-demand mirror as the model. If you want to
  stay on NTFS for any reason — disaster recovery comfort, dislike
  of WSL ext4 reliability — say so now. Phase 2 design (A) is the
  fallback.
- **(D7)**: dropping the dispatcher. The dispatcher had value if
  we expected the broker to grow many tools. Under (C), the broker
  shrinks instead. The 3-line wrapper in 1–2 call sites is enough.
  But if you want the dispatcher as future-proofing, we keep it.
- **(D15)**: robocopy as mirror tool. Mutagen is a stronger tool
  but adds an external dependency. If you prefer Mutagen — fine.

Everything else is mechanical from the design.

---

## 9. What this final synthesis is HONEST about

- The mirror tool's reliability under sustained dev pace is
  empirical. Robocopy is well-understood for one-way mirror, but
  symlinks and mode-bits degrade. We exclude `.dart_tool/` and
  build outputs from the mirror to keep the source set small.
- WSL ext4.vhdx corruption is a real risk class (rare, documented).
  Backup discipline (`wsl --export` weekly, git push always)
  bounds it.
- We are still in V4-vulnerable territory (CMake execute_process
  in `windows/CMakeLists.txt` runs under restricted account but
  still runs container-controlled code). A1 reduces blast radius;
  it does not eliminate.
- The new setup doc is longer than the current "start the watcher
  on Windows" instruction. The investment is justified by the daily
  10× speedup on `flutter analyze` — but it IS an investment.
- If the user later decides Mutagen is worth the complexity, the
  bridge code in (C) is forward-compatible: replace the robocopy
  invocation with a `mutagen sync flush` call; the rest stays.

If any of these surprises you, push back before Phase 4 locks the
requirements.
