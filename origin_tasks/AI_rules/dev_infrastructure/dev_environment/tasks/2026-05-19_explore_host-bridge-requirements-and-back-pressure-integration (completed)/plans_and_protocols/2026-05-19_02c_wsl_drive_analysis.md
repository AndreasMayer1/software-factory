# Phase 2 Addendum — WSL-drive architecture analysis

**Task**: TASK-PROC-054-02
**Date**: 2026-05-19
**Author**: Claude (Opus 4.7), main session
**Status**: DRAFT — empirical data placeholders pending Q&A research agent.

This addendum responds to a fourth candidate the user surfaced after
the first design pass: **move the project from Windows NTFS to WSL2
ext4**, so the devcontainer reads natively and Windows tooling
accesses the project via `\\wsl$\<distro>\…` (9P) or via a one-way
mirror to a Windows NTFS folder.

This was NOT in the original Phase 2 candidate set. It changes the
analysis materially. Empirical data from `02b_wsl_drive_research.md`
is needed to confirm.

---

## 1. The proposal restated

| Aspect | Today (NTFS+broker) | Proposed (WSL+thin-broker) |
|---|---|---|
| Project filesystem | Windows NTFS (`~/Projekte/.../flutter_app`) | WSL2 ext4 (`/home/<user>/.../flutter_app` inside `Ubuntu` distro) |
| Devcontainer read path | DrvFs bind-mount of NTFS folder | bind-mount of WSL2 ext4 folder (native to the WSL VM) |
| Container IO speed | **slow** — DrvFs ~10× penalty | native ext4 — **fast** |
| Windows tooling read path | native NTFS | one of: `\\wsl$\<distro>\…` (9P) **or** a Windows mirror folder |
| Windows tooling IO speed | native | **9P: 9P-protocol-bound** **or** mirror: native + mirror-sync overhead |
| Editor (VS Code) | Windows host opening WSL/devcontainer | "Reopen in WSL" / "Reopen in Container" against the WSL folder |
| Broker reason: speed | required for flutter_analyze, dart_fix, pub_get, flutter_test | **gone** — those tools now run in container at ext4 speed |
| Broker reason: toolchain | required for flutter_build_windows, smoke_test | **still required** — those need the Windows toolchain |

The proposal solves the I/O bottleneck at its root rather than
working around it via a broker.

## 2. Why this materially changes the design

### 2.1 The broker shrinks dramatically

If WSL+9P works for Windows-toolchain operations, then the broker
whitelist becomes:

```
flutter_build_windows   # toolchain-only, not speed
(smoke_test)            # toolchain-only — still trimmed per A5
```

That is **one command**, possibly two. Compare today's whitelist of
six. The pen-test attack surface drops correspondingly:

| Vector | Today's bridge | Bridge under WSL-drive |
|---|---|---|
| V1 (flutter_test→Dart on host) | open | **N/A** — flutter_test runs in container, never routed |
| V2 (smoke_test→PS on host) | critical | **N/A** if trimmed (A5) |
| V3 (analyzer plugin) | high | **N/A** — analyze runs in container |
| V4 (CMake execute_process) | high | **still in scope** — flutter_build_windows interprets CMake |
| V5 (pub fetch pivot) | high | **N/A** — pub get runs in container |
| V6 (dart fix backdoor) | medium | **N/A** — dart fix runs in container |
| V7 (watcher restart deception) | medium | **still in scope** — watcher exists |
| V8 (symlink escape) | low-medium | **still in scope** (any whitelisted tool) |

**The vector count goes from 6 in-scope to 2 in-scope.** Several
remaining vectors (V7, V8) are not specific to the whitelist size;
they apply to any broker.

### 2.2 The dispatch problem disappears for most consumers

The Phase 2 design has a §4 dispatch mechanism (Approach A facade
with a config file routing tools through the broker). Most of that
disappears under WSL-drive:

| Consumer | Today | Under WSL-drive |
|---|---|---|
| `verify-quality` Step 3.2 (flutter_analyze) | bridge call | container-local call, no dispatcher needed |
| `check_critical_path_coverage.py` (flutter test) | direct in-container | unchanged — still in-container |
| `check_test_determinism.sh` (flutter test ×10) | direct in-container | unchanged |
| `check_bundle_size.py` (flutter build apk/aab) | direct in-container | unchanged — Linux/Android builds work in container |
| any future flutter_analyze script | dispatcher → bridge | direct in-container |
| Windows build automation | dispatcher → bridge | dispatcher → bridge (only this) |

If only one or two commands are routed, the dispatcher's value is
much weaker — three lines of bash in each Windows-build-related
caller would suffice. The §4 facade can shrink to a thin shim or
be skipped entirely.

### 2.3 What we KEEP from Phase 2's design

- §3 architectural mitigation A1 (restricted Windows user) — still
  needed for the residual `flutter_build_windows` route. Smaller
  attack surface but same defense.
- §6 cheap-wins 6.3 (absolute paths), 6.4 (request size bound),
  6.5+6.6 (watcher out-of-repo + reference-copy check),
  6.7 (audit log) — all still cheap, all still useful.
- §2 rename — still wanted (Windows-centric name is still wrong).

### 2.4 What CHANGES from Phase 2's design

- §4 dispatch facade: massively reduced scope, or skipped.
- §5.1 optionality contract: re-framed — the broker is now optional
  even for the in-container fast-path; only Windows builds need it.
- §6.1 (remove smoke_test): still recommended.
- §3 architecture: A5 reduces to "A1 + remove smoke_test"; flutter_test
  removal is now a non-event (it was never the broker's job to make
  flutter_test fast — the WSL drive does that).
- "Slow threshold" rule (§5.3): no longer the load-bearing reason
  for the broker. The broker is now ONLY a toolchain-routing
  mechanism, never a speed mechanism. This makes the rule simpler.

## 3. The hard problems the proposal introduces

### 3.1 Windows-side filesystem access — three options

#### Option (a): `\\wsl$\<distro>\…` direct via 9P

| Aspect | Status |
|---|---|
| Container side performance | **fast** (native ext4) |
| Windows side read perf | [EMPIRICAL — from 02b research Q1] |
| Windows side write perf | [EMPIRICAL — from 02b research Q1] |
| Single source of truth | **yes** — no copy |
| Compatibility w/ MSBuild | [EMPIRICAL — Q2] |
| Compatibility w/ CMake | [EMPIRICAL — Q2] |
| Compatibility w/ `flutter build windows` | [EMPIRICAL — Q2] |
| Compatibility w/ `.exe` execution from UNC | [EMPIRICAL — Q2] |
| WSL VM lifecycle dependency | yes — WSL must be running |

If 9P direct access works end-to-end for `flutter build windows`
and `.exe` launch, **this is the simplest option** — no mirror, no
sync window.

#### Option (b): One-way mirror script (WSL → Windows NTFS)

| Aspect | Status |
|---|---|
| Container side performance | **fast** (native ext4) |
| Windows side perf | **native NTFS** for the mirrored copy |
| Single source of truth | **no** — two copies; sync window |
| Tools considered | robocopy /MIR, rsync over `/mnt/c/…`, Mutagen, Unison [EMPIRICAL Q3] |
| Mirror sync time | [EMPIRICAL — Q3] |
| Stale-source race during sync | each tool's handling [EMPIRICAL Q3] |
| WSL VM lifecycle dependency | yes — for the source side |

This is the safe fallback if 9P direct doesn't work for Windows
tooling. Bridge invocation pattern: "mirror, then run command on
the mirror".

#### Option (c): Mount WSL ext4 as a Windows drive letter

| Aspect | Status |
|---|---|
| Feasibility via `subst`/`net use` over UNC | [EMPIRICAL Q4] |
| Feasibility via direct ext4 vhdx mount | likely no (Windows has no native ext4 driver) [EMPIRICAL Q4] |
| Persistence across reboots | [EMPIRICAL Q4] |
| Performance vs `\\wsl$\` direct | [EMPIRICAL Q4] |

Mostly listed for completeness; user already suspected this doesn't
work cleanly.

### 3.2 WSL backup / disaster-recovery story

The project lives inside `ext4.vhdx` in the WSL distro. If the WSL
instance corrupts (uncommon but documented), the project is lost.
The mitigations:

- Regular `wsl --export` of the distro → external NTFS backup.
- Git push to a remote repo (already the user's habit).
- Optional: an automated mirror to a Windows NTFS folder serving
  as a passive backup (which is option 3.1(b) rebranded — the
  mirror doubles as backup).

A WSL-drive proposal should ship with a documented backup recipe;
this is a one-section addition to the host_bridge_setup.md doc.

### 3.3 Setup cost (one-time, per Windows machine)

- Install / verify WSL2 distro (already required for the current
  setup).
- Move project: `git clone https://… /home/<user>/projects/…` in
  WSL (or `wsl mv` the existing tree).
- Update devcontainer.json `mounts:` to point at the WSL path
  rather than `${localEnv:USERPROFILE}/Projekte/...`.
- VS Code: "Reopen in Container" against the WSL folder.
- Optional: configure mirror tool if going with option (b).

This is comparable to the existing one-time setup. Lower friction
than A2 (Sandbox) or A3 (VM).

### 3.4 Per-contributor friction

Each contributor that wants the speedup must move their checkout
to WSL2 ext4. Contributors who don't (Mac, native Linux, native
Windows without WSL) work as today. The optionality contract from
Phase 2 §5.1 still applies cleanly — the WSL-drive setup is a
*performance choice*, not a correctness requirement.

### 3.5 IDE friction

VS Code's "Reopen in WSL" + "Reopen in Container" is established
and well-supported. Editor cwd, terminal cwd, debugger cwd all work
on WSL paths. Git integration works via the WSL git. No new IDE
plumbing.

External tools (Sourcetree, GitHub Desktop) running on Windows would
have to access the repo via `\\wsl$\` UNC — depending on the tool,
this is either fine or sluggish. Most professional users use git
from the terminal in VS Code, where this is non-issue.

## 4. Security re-analysis under WSL-drive

### 4.1 What gets BETTER

- **The LLM sandbox is preserved by default.** The container runs
  on WSL2 ext4 with the project; the rest of the Windows host is
  unreachable. Even without the broker, the LLM cannot escape to
  Windows.
- **The broker's whitelist shrinks from 6 → 1–2 commands.**
- **V1, V3, V5, V6 evaporate** (tools run in container, never
  routed; container has no path to Windows).
- **Watcher's idle attack surface shrinks** — most of the time it
  has nothing to do.

### 4.2 What gets WORSE (or stays the same)

- **V4 (CMake execute_process via flutter_build_windows) is
  unchanged.** A1's restricted account still needed for that route.
- **V7 (watcher restart deception) is unchanged.** Cheap-win 6.5
  (watcher out-of-repo) still applies.
- **9P direct-access opens a new "Windows reads container-writable
  files" surface for any Windows tooling that interprets project
  files outside the broker.** If a Windows developer opens
  `\\wsl$\…\windows\CMakeLists.txt` in a Visual Studio that
  auto-runs CMake on load, that load is interpreting a
  container-writable file. **This is the SAME class as V4** — it
  was already in scope when the project lived on NTFS. Not new,
  not worse.
- **The mirror script (option (b))** is a confused-deputy candidate
  if the bridge invokes it on the container's behalf. Design
  carefully: mirror is one-way (WSL → NTFS), runs under the
  restricted account on the Windows side, target is read-only to
  the developer's normal account where appropriate.

### 4.3 Net security verdict

**Strictly better than the Phase 2 design.** Most of A5's complexity
exists to manage a large whitelist; under WSL-drive, the whitelist
is so small that the residual A1 work covers it comfortably. We
keep A1 (restricted user) and the §6 cheap-wins; we drop almost
everything in §4 (dispatcher).

## 5. Performance verdict

[EMPIRICAL — to be confirmed by 02b research, but rough expectations:]

| Workload | Today | WSL-drive + 9P | WSL-drive + mirror |
|---|---|---|---|
| `flutter analyze` (container) | 10–17 min | ~1 min | ~1 min |
| `dart fix --apply` (container) | >10 min (TIMES OUT) | ~30 s | ~30 s |
| `flutter pub get` (container, cold) | minutes | ~10 s | ~10 s |
| `flutter test` (container) | slow but works | fast | fast |
| `flutter build windows` (Windows host) | native | depends on 9P perf | mirror time + native |
| Smoke test `.exe` launch (Windows host) | native | depends on 9P perf | mirror time + native |
| Daily editor responsiveness | mixed | should improve | should improve |

The win on the container side is unambiguous: ext4 native >> DrvFs.
The cost on the Windows side depends on which option (a/b) and the
empirical numbers from 02b.

## 6. Updated user-gate decision matrix

If WSL-drive is adopted, the Phase 3 user-gate from Phase 2 §9
changes substantively. Updated rows:

| # | Decision | Phase 2 reco | Under WSL-drive |
|---|---|---|---|
| D4 | Trust architecture | A5 (A1 + trim flutter_test, smoke_test) | **A1' = A1 + trim smoke_test only** (flutter_test is moot — not on whitelist) |
| D5 | Remove `flutter_test` from whitelist | yes | **moot** — was never routed in this model |
| D6 | Remove `smoke_test` from whitelist | yes | yes (unchanged) |
| D7 | Dispatch approach | A (facade) + slim B | **drop the facade**; one or two callers add a 3-line wrapper. Keep slim B (read-only `scripts/host-bridge/`) |
| D8 | "Slow" threshold | 1 min advisory at admission | **gone** — broker is no longer a speed mechanism, only a toolchain mechanism |
| D10 | Config location | yaml in repo + local override | broker config in `scripts/host-bridge/`; no dispatcher config |
| D13 | Phase 5 scope | rename + A5 + dispatcher + 3 consumer migrations + mount + CLAUDE.md | rename + A1' + 0–1 consumer migration + WSL setup doc + mount + CLAUDE.md |

Three new rows specific to WSL-drive:

| # | Decision | Recommendation [if data confirms] |
|---|---|---|
| **D15** | Adopt WSL-drive architecture? | **YES** if research confirms `flutter build windows` works on `\\wsl$\…` or via a reasonable mirror; **NO** if both fail |
| **D16** | Windows-side filesystem access | **9P direct** if Q2 says Flutter Windows build works; **mirror** (robocopy /MIR via the broker) otherwise |
| **D17** | Backup strategy | `wsl --export` to a Windows folder, weekly + on demand; git push covers the rest |

## 7. What this analysis is HONEST about

- 9P from Windows is slower than native NTFS. **How much slower for
  Flutter's specific build pipeline is empirical** — research Q1/Q2
  will tell. If it's 2×, fine. If it's 10× and rivals today's DrvFs
  problem, we go with the mirror.
- The mirror introduces a 2-source-of-truth window. Tool selection
  matters; Mutagen has the cleanest reputation but I have not used
  it in this configuration personally. Research Q3.
- The WSL-drive proposal eliminates most of the broker's
  speed-driven justification. If we adopt it, the document we
  produce for `requirements.md` reflects this shift — the broker
  is a toolchain bridge, not a performance bridge. The honesty about
  this matters: if someone reads the requirement in 6 months and
  sees "broker for speed", they'll be confused.
- Disaster recovery for the WSL distro becomes a first-class
  concern. We add a backup recipe to the setup doc.
- The slim-B defense-in-depth (`scripts/host-bridge/` read-only in
  container) still applies and is still cheap.

## 8. Empirical-questions pending

Filled in by `02b_wsl_drive_research.md`. Updates to this doc when
it returns:

1. `\\wsl$\` perf vs native NTFS vs DrvFs (Q1)
2. CMake / MSBuild / `flutter build windows` / `.exe` launch over
   UNC (Q2)
3. Mirror tool comparison: robocopy /MIR, rsync, Mutagen, Unison (Q3)
4. Drive-letter mount feasibility (Q4)

If Q2 is "works fine", recommendation = WSL-drive + 9P direct.
If Q2 is "works partly", recommendation = WSL-drive + mirror.
If Q2 is "broken", recommendation = stay with Phase 2's NTFS+broker
A5 design.

## 9. What to do with `02_design.md`

Hold its decisions in suspense pending §8. The user gate (Phase 3)
should evaluate Phase 2's A5 design **and** this WSL-drive option
side by side, then commit to one. The requirements draft (Phase 4
via requ-explore) reflects whichever wins.

If WSL-drive wins, large parts of `02_design.md` §4 (dispatcher),
§5 (policy) become smaller / simpler / dropped. §2 (naming), §3
(A1 reduced to A1'), §6 (cheap-wins) carry forward intact.

If WSL-drive doesn't pan out (research returns red on Q2 and Q3),
we go with `02_design.md` as-is.
