# WSL ext4 ↔ Windows access research

Scope: empirical answers to four questions about moving a Flutter project from
NTFS to a WSL2 ext4 virtual disk, with Windows-side tooling still required.
Research-only; no recommendations.

## Q1. `\\wsl$\<distro>\<path>` performance from Windows

- The Windows→WSL direction is implemented by a 9P client in Windows talking to
  a 9P server inside the WSL2 VM. The reverse direction (`/mnt/c`) uses the
  DrvFs 9P client in the Linux kernel. Both share the same protocol family but
  are independent implementations [1][2].
- Microsoft's open issue #9125 documents a hard cap on the Windows-side 9P
  client: bulk throughput "around 400 Mb/s through 9P" against native Linux
  ext4 in WSL2 measured at "4.5 Gb/s" — i.e. roughly an order of magnitude
  slower than the underlying ext4. The reporter attributes this to a hardcoded
  small `msize` value with no Windows-side knob to tune it [3].
- Issue #5103 ("9p in WSL2 is unusable, please expose ext4 vhdx using Samba
  server instead") reports that running a Samba server inside WSL2 and mapping
  it as `\\127.0.0.1\share` produced "noticeably" higher throughput than the
  built-in `\\wsl$` mount for the same files in the same vhdx [4].
- Issue #13846 reports that simple metadata ops over `\\wsl$\…` (e.g. `ls` of a
  Windows path symlinked into WSL) can take ~30 s on directories that respond
  in milliseconds locally. No formal throughput numbers; qualitative only [5].
- Discussion #9412 references Linux-side 9p kernel patches that gave ~10× wins
  in synthetic Linux→Windows benchmarks; users report the WSL-shipped kernel
  has not consistently picked these up, so the Linux-side improvements have
  not translated reliably into faster `/mnt/c` performance [6].
- Third-party benchmark (Allen Kuo) measured small-file write averages of
  0.019 s on a Samba-in-WSL share vs. 9P baselines that were ~70× slower, and
  observed multi-minute stalls on a 500 MB single-file write over 9P [7].
- WSL 2.0+ release notes record incremental 9P stability fixes (virtio-9p race
  fixes, `cache=mmap` default for dotnet) but no entry advertises a "9P
  server v2" or a protocol-level rewrite for the Windows-side client through
  the dates available [2].
- vxlabs measured WSL2 native ext4 ~9× faster than `/mnt/c` for typical
  development workloads; the inverse direction (`\\wsl$` from Windows) is
  bounded by the same protocol [8].
- No primary source establishes a published per-API-call latency number for
  `\\wsl$` open/stat. The recurring pattern across sources is: large-file
  sequential transfer is the better case (still single-digit × slower than
  native); many-small-file fan-out is the worst case, dominated by per-call
  round-trips on a single Hyper-V socket.

## Q2. Compatibility of Windows toolchains with `\\wsl$\` paths

- **CMD.EXE**: rejects UNC working directories with the long-standing message
  "CMD.EXE was started with the above path as the current directory. UNC paths
  are not supported. Defaulting to the Windows directory." This affects every
  tool that shells out via `cmd /c` from a UNC `cwd` [9][10].
- **CMake + Visual Studio generator**: dotnet/msbuild issue #7001 shows
  MSBuild 17.0.0.51408 (VS 2022) lower-cases UNC components when handling
  CMake-generated `.vcxproj` files, producing path-mismatch warnings MSB8064
  ("custom build succeeded, but specified dependency does not exist") and
  MSB8065. The reporter found no clean workaround other than moving the build
  directory off the UNC path; placing only sources on UNC reduced — but did
  not eliminate — the warnings [11].
- Microsoft Learn's Visual Studio + WSL2 walkthrough does not document running
  with sources on `\\wsl$`; the supported model is sources in Windows
  filesystem, and Visual Studio uses `rsync` to copy them into the WSL distro
  before building. The reverse (sources on WSL, build invoked from Windows
  over `\\wsl$`) is not a documented supported configuration [12].
- **MSBuild generally**: dotnet/sdk #7672 documents that the .NET CLI breaks
  on UNC project paths because relative-path lookup against the project root
  resolves incorrectly. MSBuild itself can *reference* assemblies on UNC
  (`UsingTask AssemblyFile`), but *building a project whose `MSBuildProjectDirectory`
  is UNC* triggers the relative-path bug class [13].
- **Flutter on UNC**: flutter/flutter #43594 is the canonical issue — Flutter
  build on a project root accessed via a Samba-style UNC path fails because
  Dart's path canonicalization strips leading backslashes, producing
  `UNC\server\share\…` instead of `\\server\share\…`, which is then declared
  as a build input and not found. dart-lang/sdk #52309 is the matching Dart
  SDK bug for `Platform.resolvedExecutable` on UNC [14][15].
- **`flutter pub get` and downstream tools**: npm/cli #6280 and yarnpkg/yarn
  #8715 reproduce the same UNC-cwd failure mode under PowerShell launched in
  a `\\wsl$\…` directory; the failure is at the `cmd /c` shim layer, so any
  tool that invokes a child process via cmd inherits it. `pub` shells out
  during `flutter pub get`, and Flutter docs warn against putting projects
  under WSL paths when using the Windows Flutter SDK [16][17][18].
- **PowerShell ExecutionPolicy on UNC**: Microsoft Learn (PowerShell 7.5
  `about_Execution_Policies`) states explicitly: "On systems that do not
  distinguish Universal Naming Convention (UNC) paths from internet paths,
  scripts that are identified by a UNC path might not be permitted to run
  with the **RemoteSigned** execution policy." Behaviour also changed between
  Windows PowerShell 5.1 (consulted the Local Intranet zone) and PowerShell
  7 (no longer consults Local Intranet, treats FQDN-like UNCs as Internet);
  `-ExecutionPolicy Bypass` is the documented workaround [19].
- **Launching `.exe` from UNC**: Win32 `GetCurrentDirectory` works on UNC,
  but `CreateProcess` with a UNC `lpCurrentDirectory` still triggers the
  CMD.EXE shim warning for any cmd-based child; `SetCurrentDirectory` to a
  UNC path succeeds at the API level. Native-only EXEs that do not shell out
  generally launch and run from `\\wsl$\…`; the failures are in tooling that
  *shells out via cmd.exe or assumes a drive-letter cwd* [9][20].
- **`net use X: \\wsl$\Ubuntu\home\u\proj`**: assigns a drive letter; the
  underlying transport is still 9P. Microsoft Q&A discussions note that the
  WSL UNC namespace's lifetime is bound to the WSL VM (it disappears when
  WSL shuts down), so `/PERSISTENT:Yes` mappings re-fail after reboot until
  WSL is restarted [21][22]. `subst` does not persist across reboot by
  design [21].

## Q3. Real-world WSL ↔ Windows mirror tools

- **`robocopy /MIR` from PowerShell, source `\\wsl$\…`, target `C:\…`**:
  works at the file-content level; `/MT:N` parallelism helps. Two caveats
  surface in the primary sources: (a) Windows lacks Linux mode bits and
  symlinks-to-Linux-targets, so executable bits and Linux symlinks degrade —
  symlinks become reparse points or copies of the symlink target depending
  on flags [23][24]. (b) `/MIR` deletes anything in the destination missing
  from source, which makes "build outputs left in destination by Windows
  tools then mirrored back" a hazard requiring an explicit exclude list.
- **`rsync` inside WSL, target `/mnt/c/…`**: microsoft/WSL #5087 documents
  rsync failing on non-writable NTFS targets because rsync's "temporarily
  override target attributes" path is a no-op when chmod is forced to 0777
  by the DrvFs mount. microsoft/WSL #5299 reports 20-minute rsync runs over
  `/mnt/c` for what took 30 s under WSL1, attributed to per-file 9P
  round-trips. Mode bits do not survive the trip [25][26].
- **Mutagen** (`mutagen.io`): documented as a fast bidirectional sync; the
  WSL Counter-Strike walkthrough and the takken.io WSL→Linux dev guide both
  use Mutagen specifically to escape the 9P boundary, keeping native-speed
  access on each side. Reported first-sync ≤30 s for typical projects;
  steady-state propagation "near real-time" — but reports are anecdotal,
  not formal benchmarks. Mutagen runs Watchers on both sides and resolves
  conflicts with a configurable policy [27][28].
- **Unison**: vxlabs documents running Unison "directly via the WSL bridge"
  (a shim that invokes `wsl.exe` instead of `ssh`) to avoid 9P. Two-way
  reconciliation works but is interactive on conflict by default. Open
  bug bcpierce00/unison #264 reports the file watcher locking child
  directories on WSL during repeat syncs, blocking renames [29][30].
- **NTFS junction (`mklink /J`) pointing to `\\wsl$\…`**: NTFS junctions
  are stored as reparse points containing absolute *NT object paths*; the
  Mount Manager only resolves them for paths backed by a `\Device\HarddiskVolume…`
  device. The `\\wsl$` namespace is a network redirector (`p9rdr.sys`),
  not a volume, so `mklink /J` either refuses creation or yields a junction
  the kernel will not follow. microsoft/WSL #559 + the Trail of Bits post
  document the related fact that NTFS junctions are not transparently
  visible to WSL, and SMB/UNC targets are not valid junction destinations
  in general [31][32].
- **Race conditions / "source changed during sync"**: robocopy retries
  per-file and does not represent a consistent snapshot; Mutagen and Unison
  both checkpoint per-file and re-reconcile on the next tick. None of the
  primary sources claim a cross-file consistent snapshot — that would
  require freezing writers (e.g. shutting the devcontainer) for the
  duration of the mirror pass.

## Q4. Mounting WSL ext4 as a Windows drive letter / regular path

- **`wsl --mount`**: Microsoft Learn confirms this command mounts a Linux
  disk *into the WSL VM*, not the reverse. With `--vhd` you can attach a
  separate `ext4.vhdx` into WSL; you cannot use it to attach the distro's
  vhdx as a Windows drive [33]. Microsoft Learn states: "If you have an
  Ext4-formatted drive, you cannot mount it on your Windows file system"
  via this path [33].
- **`subst X: \\wsl$\<distro>\<path>`**: works in the current session; the
  drive letter resolves through the same 9P redirector, so performance is
  identical to direct `\\wsl$\…` access. ss64.com (vendor reference) and
  Microsoft Q&A both note `subst` does not persist across reboot; users
  bridge that with a startup script or registry `DOS Devices` entry [21][34].
- **`net use X: \\wsl$\<distro>\<path> /PERSISTENT:Yes`**: assigns a drive
  letter persistently in the user's NetUse registry, but the underlying
  `\\wsl$` namespace is only present while WSL is running, so the mapping
  is "persistent" in Windows but not in availability — it re-resolves after
  WSL starts. Performance equals direct `\\wsl$` access (no separate
  caching layer) [22].
- **Direct ext4.vhdx access from Windows**: Windows has no in-box ext4
  driver. Third-party kernel-mode drivers exist:
  - Paragon Linux File Systems for Windows ("extFS for Windows"): commercial,
    user-mode via Dokan (not kernel-mode in current builds); read/write
    ext2/3/4 with documented support up to 2 TB volumes; 10-day trial then
    throttled [35][36].
  - Ext2Fsd / Ext4Fsd: open-source, last meaningful ext4 work years stale;
    documented to risk corruption in read-write mode against modern ext4
    feature sets; safe only read-only on legacy volumes [37].
  - DiskInternals Linux Reader: read-only, file-extraction UI, not a
    filesystem mount [37].
  None of these is documented to be safe against a *live* WSL distro vhdx
  (concurrent writes from inside WSL while Windows holds the vhdx open).
  Microsoft Learn explicitly recommends WSL's own kernel as the safer
  read/write surface for ext4 [33][37].
- **"Plan 9 client for Windows" / `wsl-mount` community projects**: no
  primary-source project found that surfaces WSL ext4 as a Windows volume
  with a drive letter independent of the `\\wsl$` redirector. The 9p
  redirector (`p9rdr.sys`) Microsoft ships *is* the Plan 9 client for
  Windows; there is no public alternative implementation cited in the
  sources reviewed.
- **Net result for "drive letter that performs better than `\\wsl$`"**:
  no clear public answer that a Windows-side drive letter *bypassing* the
  9P redirector exists for a live WSL distro. The vhdx-driver route exists
  only for *offline* ext4 volumes; the `subst` / `net use` route uses the
  same 9P path under the hood.

## Sources

1. Microsoft Learn — WSL file systems overview:
   <https://learn.microsoft.com/en-us/windows/wsl/filesystems>
2. Microsoft Learn — WSL release notes:
   <https://learn.microsoft.com/en-us/windows/wsl/release-notes>
3. microsoft/WSL #9125 — Add msize configuration for windows-side 9P client:
   <https://github.com/microsoft/WSL/issues/9125>
4. microsoft/WSL #5103 — 9p in WSL2 is unusable, expose ext4 via Samba:
   <https://github.com/microsoft/WSL/issues/5103>
5. microsoft/WSL #13846 — WSL2 extremely slow at file system frontier:
   <https://github.com/microsoft/WSL/issues/13846>
6. microsoft/WSL discussion #9412 — 9p performance increase ~10x:
   <https://github.com/microsoft/WSL/discussions/9412>
7. Allen Kuo, "WSL2 I/O Performance Benchmarking: 9P vs Samba":
   <https://allenkuo.medium.com/windows-wsl2-i-o-performance-benchmarking-9p-vs-samba-file-systems-cf2559be41ac>
8. vxlabs — WSL1 vs WSL2 filesystem I/O measurements:
   <https://vxlabs.com/2019/12/06/wsl2-io-measurements/>
9. desktop/desktop #14181 — CMD.EXE does not support UNC paths:
   <https://github.com/desktop/desktop/issues/14181>
10. Microsoft Learn — GetCurrentDirectory:
    <https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getcurrentdirectory>
11. dotnet/msbuild #7001 — MSBuild + CMake + WSL2 UNC path warnings:
    <https://github.com/dotnet/msbuild/issues/7001>
12. Microsoft Learn — Walkthrough: Build and Debug C++ with WSL 2 and VS 2022:
    <https://learn.microsoft.com/en-us/cpp/build/walkthrough-build-debug-wsl2?view=msvc-170>
13. dotnet/sdk #7672 — Can't build project located on UNC path:
    <https://github.com/dotnet/sdk/issues/7672>
14. flutter/flutter #43594 — Flutter build fails on mapped Samba share:
    <https://github.com/flutter/flutter/issues/43594>
15. dart-lang/sdk #52309 — Platform.resolvedExecutable invalid path on UNC:
    <https://github.com/dart-lang/sdk/issues/52309>
16. npm/cli #6280 — npm on WSL mount path UNC failure:
    <https://github.com/npm/cli/issues/6280>
17. yarnpkg/yarn #8715 — UNC not working for yarn install on WSL2:
    <https://github.com/yarnpkg/yarn/issues/8715>
18. Flutter docs — Troubleshooting installation:
    <https://docs.flutter.dev/install/troubleshoot>
19. Microsoft Learn — about_Execution_Policies (PowerShell 7.5):
    <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.5>
20. Microsoft Q&A — PowerShell 7.2 script need to run via UNC path:
    <https://learn.microsoft.com/en-us/answers/questions/1078473/powershell-7-2-script-need-to-run-via-unc-path>
21. ss64 — `subst` reference:
    <https://ss64.com/nt/subst.html>
22. microsoft/WSL #10311 — WSL does not automount drive letters from subst:
    <https://github.com/microsoft/WSL/issues/10311>
23. Microsoft TechCommunity — Robocopy /MIR mirroring file permissions:
    <https://techcommunity.microsoft.com/t5/storage-at-microsoft/robocopy-mir-switch-8211-mirroring-file-permissions/ba-p/423662>
24. Microsoft Learn — Robocopy reference:
    <https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy>
25. microsoft/WSL #5087 — rsync fails on non-writable NTFS mounts:
    <https://github.com/microsoft/WSL/issues/5087>
26. microsoft/WSL #5299 — rsync to mounted external drive unbearably slow:
    <https://github.com/microsoft/WSL/issues/5299>
27. takken.io — Seamless Windows-Linux development with Mutagen:
    <https://takken.io/blog/seamless-windows-linux-development>
28. Mutagen project documentation:
    <https://mutagen.io/documentation/introduction>
29. vxlabs — Unison file sync via the WSL bridge:
    <https://vxlabs.com/2022/10/22/unison-file-synchronization-directly-via-the-wsl-bridge/>
30. bcpierce00/unison #264 — Watcher locking directories on WSL:
    <https://github.com/bcpierce00/unison/issues/264>
31. microsoft/WSL #559 — NTFS junctions not seen in DriveFS:
    <https://github.com/Microsoft/WSL/issues/559>
32. Trail of Bits — Why Windows can't follow WSL symlinks:
    <https://blog.trailofbits.com/2024/02/12/why-windows-cant-follow-wsl-symlinks/>
33. Microsoft Learn — Get started mounting a Linux disk in WSL 2:
    <https://learn.microsoft.com/en-us/windows/wsl/wsl2-mount-disk>
34. kjctech — Persistent SUBST virtual drive:
    <https://www.kjctech.net/how-to-make-an-old-school-subst-virtual-drive-persistent/>
35. Paragon — Linux File Systems for Windows:
    <https://www.paragon-drivers.com/en/lfswin/>
36. Phoronix — Commercial EXT4 File-System Driver for Windows (Paragon):
    <https://www.phoronix.com/news/Paragon-EXT4-Windows-Update>
37. MacMyths — How to Mount/Read/Format EXT4 on Windows 11 (2025):
    <https://macmyths.com/how-to-mount-read-or-format-ext4-on-windows-11-2025-guide/>
