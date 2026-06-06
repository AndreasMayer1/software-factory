# Web Research — Phase 2 Design Input

Scope: outside facts only. No recommendations.

---

## Q1. Windows Sandbox (`WindowsSandbox.exe`) for per-command isolation

- Microsoft's official description characterises launch as "takes a few seconds" — vendor-level marketing language, not measured numbers. The vendor-claim phrasing comes from the Microsoft Learn overview page [1].
- The first-party docs are explicit that the sandbox is single-instance and non-persistent: "Each launch provides a fresh instance. Host-installed software isn't available in the sandbox." and "Windows Sandbox currently doesn't allow multiple instances to run simultaneously." [1]
- Persistence exception (Windows 11 22H2+): data survives **restarts initiated inside the sandbox**, but a full close/reopen still destroys the VM image and state [1][2].
- Therefore, no parent process "queue" model exists at the OS level — `WindowsSandbox.exe` is one VM at a time, single-shot lifecycle. To pipeline commands you must keep one sandbox alive and push work into it via `LogonCommand` + a mapped folder acting as a message queue. There is no documented IPC primitive for "send another command to the already-running sandbox."
- Cache persistence behaviour follows from this: anything written **inside** the sandbox VM (e.g. `%LOCALAPPDATA%\.dartServer`, `%LOCALAPPDATA%\Pub\Cache`) is discarded when the sandbox closes [1]. Anything written to a `MappedFolder` is host-persistent. The Dart analyzer keeps its driver cache at `%LOCALAPPDATA%\.dartServer` and the pub cache at `%LOCALAPPDATA%\Pub\Cache` by default [9][10] — neither is in the project tree, so a fresh sandbox = cold analyzer cache unless caches are explicitly redirected (e.g. `PUB_CACHE` env var [10]) into a writable mapped folder.
- `MappedFolder` schema supports a `<ReadOnly>true</ReadOnly>` element per folder, with read-only enforced inside the sandbox; default is `false`, and changes to writable mappings persist on the host [3].
- `LogonCommand` runs exactly one command at sandbox start; multi-step orchestration is the user's responsibility (typically a script in a mapped folder) [3].
- Edition support is hard-gated: **Pro, Pro Education/SE, Enterprise, Education**. **Not supported on Windows Home.** License entitlement comes with Windows Pro / Pro Education/SE / Enterprise E3/E5 / Education A3/A5 [1].
- Hardware requirements per Microsoft: 64-bit CPU with SLAT, hardware virtualisation enabled in BIOS/UEFI, ≥ 4 GB RAM (8 GB recommended), ≥ 1 GB free disk (SSD recommended) [1].
- No clear public answer on the specific cold-start floor on consumer hardware. Microsoft's wording is "a few seconds"; the closest community signal is a GitHub issue describing the splash logo as visible for "three or five seconds" under normal conditions, with multi-minute stalls reported as a bug [2]. There appears to be no published, reproducible benchmark of the `WindowsSandbox.exe` cold-start time floor — likely because the single-instance, no-API design discourages programmatic measurement.

---

## Q2. Windows restricted-user / restricted-token / job-object isolation for a long-lived watcher

- The canonical primitive stack is documented by Microsoft Win32 and exemplified by the Chromium sandbox:
  - `CreateRestrictedToken` strips/disables SIDs and privileges on a token; the resulting token cannot regain dropped rights [4][5].
  - `JOBOBJECT_SECURITY_LIMIT_INFORMATION` ties a restricted token to a job so that "all processes in the job are limited to that token or a further restricted token" [4].
  - Job objects propagate to children by default; `ActiveProcessLimit = 1` plus the absence of `JOB_OBJECT_LIMIT_BREAKAWAY_OK` prevents spawning new processes [5][6].
  - Mandatory-integrity-level Low/Untrusted is set on the token; combined with a Low Box (AppContainer) token, this also gives a kernel-enforced no-network capability bit — "Network checks are enforced if the token is a Low Box token and the INTERNET_CLIENT Capability is not present." [5][7].
- The Chromium model is the well-known production reference: untrusted renderer = restricted token + Low Box (no INTERNET_CLIENT) + Untrusted integrity + job object with `ActiveProcessLimit=1` + alternate desktop + brokered policy for the few syscalls that need to escape [5][7].
- NCC Group ships `WindowsJobLock` as a reference implementation showing how to apply Job Object UI/process/handle/clipboard restrictions to an arbitrary target process. The README lists Job-Object-only primitives; CreateRestrictedToken is **not** part of that tool [8]. Token shaping is a separate step.
- AppLocker can be configured **per user or group** (Computer Configuration → Windows Settings → Security Settings → Application Control Policies → AppLocker → Executable Rules) and is therefore usable to whitelist a tiny set of binaries for a dedicated local user without affecting the developer's normal account [11]. AppLocker requires the AppIDSvc service running.
- WDAC (App Control for Business) applies device-wide and cannot be scoped per user, so it does not fit a "one restricted local account on a dev box" model unless the whole machine is locked down [11].
- Non-admin setup: NTFS folder ACLs and per-user `runas`/`schtasks /RU` invocation do **not** require admin once set up — but creating a new local user, applying AppLocker policy, or assigning Job-Object security limits **does** require admin once. After the one-time setup the watcher can run under the restricted account without further elevation.
- Flutter / Dart tooling implications for the restricted account:
  - `dart pub get` defaults to **online** behaviour and tries pub.dev; `--offline` makes it use only the local cache [10]. Pub cache default `%LOCALAPPDATA%\Pub\Cache`, overridable via `PUB_CACHE` env var [10] — so the restricted account needs either network egress or a pre-warmed pub cache directory it can read.
  - The Dart analysis server keeps its driver cache at `%LOCALAPPDATA%\.dartServer` (Windows). The cache can reach ~1 GB on real projects [9]. So the restricted account needs write access to its `LOCALAPPDATA` or an explicitly redirected location.
  - Flutter SDK + Dart SDK trees need read+execute; the Flutter tool also writes telemetry/cache to `%APPDATA%\flutter` and `%LOCALAPPDATA%\Pub` by default (Flutter install docs cover this surface area [12]).
  - No clear public answer on a vetted, end-to-end "least-privilege account for Flutter tooling" recipe — vendor docs assume a normal developer account; this configuration appears to be ops-side knowledge not published as a recipe.

---

## Q3. Devcontainer read-only bind mounts and Windows ACL behaviour after `git clone`

- `devcontainer.json` `mounts` and `workspaceMount` accept the exact value space of the Docker CLI `--mount` flag, per the dev-container spec JSON reference; the spec itself does not enumerate options, it delegates to Docker [13].
- `readonly` is a valid `--mount` option in Docker, both as the long form `type=bind,...,readonly` and the `-v ...:ro` short form [14]. Real-world devcontainer use confirms `"mounts": ["source=...,target=...,type=bind,readonly"]` works [15].
- Subpath mounting: bind mounts can target any **host** subpath as their `source`. So mounting `${localWorkspaceFolder}/sub-folder` to `/workspace/sub-folder` is supported; this is shown in the VS Code "change the default source code mount" doc [16]. You can therefore layer one read-only mount on a subpath and a writable mount on a sibling subpath of the same project tree.
- Granularity caveat: **recursive read-only** (`bind-recursive=enabled`) needs Linux kernel ≥ 5.12. On older kernels, sub-mounts of a readonly bind can still be writable [14]. WSL2 kernels are recent enough for current Debian-based containers, but this is the documented limit.
- Recurring spec-level pain point: devcontainer.json `mounts` syntax churn — the structured object form (`{ source, target, type }`) is in flux and may not accept `readonly` cleanly; the comma-separated string form is the established workaround [17]. The issue (`devcontainers/spec#511`) is still open as of late 2024 [17].
- Windows NTFS ACL persistence across `git clone`: **Git does not store NTFS ACLs.** Git's permission model is `core.fileMode` (Unix mode bit), which Git itself probes at clone/init time and silently disables on filesystems that don't support it (FAT, exFAT, NTFS via WSL drvfs) [18]. There is no `core.ntfsACL` or equivalent in upstream Git.
- Consequence: ACLs **never** travel with the repo. On every fresh clone they must be re-applied out-of-band using `icacls.exe` or PowerShell `Set-Acl`; this is the documented standard Windows approach [19]. RoboCopy `/COPY:DATSOU` is the equivalent for moves [19].
- BindFS / AppArmor / overlayfs as in-container enforcement:
  - **AppArmor** is the production-grade choice on Debian/Ubuntu containers; Docker ships a default profile (`docker-default`) and supports per-container profile overrides. It is path-based and can deny writes to specific mount points regardless of the underlying mount's rw flag. Docker docs and SELinux/AppArmor write-ups confirm the model: "If AppArmor's container profile forbids a path, mount, capability, or syscall, you need to fix the profile or switch it." [20].
  - **BindFS** is an LD_PRELOAD/FUSE re-mount that can enforce read-only on a writable bind. No clear public answer on its use as a devcontainer security boundary — write-ups exist for NAS / Synology use, but the VS Code / Codespaces ecosystem does not document it; treat as undocumented.
  - **overlayfs** with a `lowerdir` of the host mount and a tmpfs `upperdir` is a known pattern for making a writable container view of a read-only host source without leaking writes back. This appears in CI runner setups (GitHub Actions, GitLab CI), but again with no first-party devcontainer documentation.

---

## Q4. Prior art on host-execution proxies / dev-container façades

- **VS Code devcontainer `initializeCommand` is the only first-class host-side hook in the spec.** Per containers.dev and Ken Muse's write-up, `initializeCommand` "runs on the host machine before the container is created … may run more than once during a given session" [21][22]. There is no `hostExec` / `hostBridge` / `runOnHost` step **during normal container life** — only at create/start.
- Security model around `initializeCommand` is "the user already trusts this repo." Public security research (Jamie McCrindle, GitHub blog on devcontainer prompt-injection, danieldemmel write-up) all flag `initializeCommand` as the standard exfiltration vector and recommend Workspace Trust + manual config inspection — there is no sandbox around host-side commands [23][24][25].
- **GitHub Codespaces** has no published "back to host" hook — Codespaces *is* the host. Prebuild lifecycle runs `onCreateCommand` and `updateContentCommand` only; `postCreateCommand` / `postStartCommand` run later in the dev environment [26]. So Codespaces has no analogue to this pattern; it sidesteps it by making the container the only machine.
- **JetBrains Gateway** uses an explicit thin-client / backend split — the IDE backend runs on the dev-host (remote VM or container) and the local thin client only renders UI. Communication is via TLS-over-SSH; the host is the heavyweight, the local machine is the light client [27]. This is the inverse of "container is slow, run on host."
- **`devcontainer-bridge` (dbr)** is the closest in-the-wild instance of the "broker on host, polled by container" pattern. The Bradley Beddoes write-up describes it as a reverse-connection daemon (container → host) for port forwarding and `$BROWSER` URL opening, with the host daemon as the only authority for binding listeners and invoking host tools [28]. Naming convention used: **"bridge"** + **"daemon"**.
- **BuildKit / Buildx remote builder** uses the same vocabulary: "frontend" (definition) + "worker" / "remote builder" (execution). Buildx connects to a remote `buildkitd` over TCP; the container build is dispatched to the remote node, results streamed back [29]. Naming convention: **"worker"**, **"remote driver"**.
- **Dagger / Earthly / Skaffold** all support local-host execution as a first-class option, not a fallback. Skaffold's "local build" environment uses the developer's installed Docker/Bazel/Maven; "lifecycle hooks" run shell on the host before/after [30][31]. Dagger frames host dependencies as explicit, strictly-typed inputs to a sandboxed function — the host capability is opt-in per call [32].
- **gVisor "OCI host-bridge"** — no clear public answer. gVisor has a `runsc` "sentinel" / "gofer" split where the gofer mediates host filesystem access, but Google's docs do not use the term "host-bridge" and the pattern is a syscall filter, not a command-dispatch broker. Treat the phrasing as unattested.
- Optionality contract — "tool on host but not container":
  - VS Code / devcontainers: pure config-time hooks. If the host command fails, the container still starts unless you exit non-zero from `initializeCommand`, which aborts attach. No silent fall-back.
  - Buildx: explicit driver selection; if the remote driver is unreachable, the user sees the connection error. No silent local fallback.
  - Skaffold: explicit `build.local` vs `build.googleCloudBuild` etc. — chosen in config, not auto-fallback [30].
  - Dagger: each capability is a typed input; missing on host → typed error to the calling function [32].
  - The general pattern is **explicit declaration, hard error on absence**, not silent fallback. Silent fallback is uncommon in this design space.
- How they prevent the container injecting code into the host tool:
  - Chromium-style brokering is the canonical defence: the broker validates **policy-allowed call signatures**, not opaque payloads. "The policy interface allows the broker to specify exceptions, which is a way to take a specific Windows API call issued in the target and proxy it over to the broker." [7] The container side cannot ask for arbitrary execution — only for pre-declared, parameter-validated operations.
  - `devcontainer-bridge` constrains the surface to "open a URL" and "forward a TCP port" — both narrow, parseable contracts [28].
  - BuildKit / Buildx achieve safety by treating the container build as data (LLB) sent to the remote worker — the worker executes its own runtime, not a script the client sent verbatim [29].
  - **The unsolved class** is what your pen-test surfaced: when the "tool" is `flutter analyze` or `dart fix` and the tool itself interprets project files (build scripts, codegen, custom lints), the broker has no way to validate the payload without re-implementing the tool. No published OSS project appears to solve this for Flutter/Dart specifically. The Chromium-style answer would be "don't let the tool interpret arbitrary code from inside the sandbox" — i.e. drop privileges on the host-side runner, not on the dispatcher.

---

## Sources

[1] Microsoft Learn — Windows Sandbox overview: https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/
[2] microsoft/Windows-Sandbox issues (launch-time behaviour reports): https://github.com/microsoft/Windows-Sandbox/issues/101
[3] Microsoft Learn — Configure Windows Sandbox with .wsb files: https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file
[4] Microsoft Learn — JOBOBJECT_SECURITY_LIMIT_INFORMATION: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_security_limit_information
[5] Microsoft Learn — Job Objects (Win32): https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
[6] Google Project Zero — Chrome sandbox token write-up: https://googleprojectzero.blogspot.com/2020/04/you-wont-believe-what-this-one-line.html
[7] Chromium Sandbox design doc: https://chromium.googlesource.com/chromium/src/+/main/docs/design/sandbox.md
[8] NCC Group WindowsJobLock: https://github.com/nccgroup/WindowsJobLock
[9] dart-lang/sdk issue 29648 — analysis driver cache size and `.dartServer` location: https://github.com/dart-lang/sdk/issues/29648
[10] Dart docs — pub environment variables (`PUB_CACHE`) and `pub get --offline`: https://dart.dev/tools/pub/environment-variables — https://dart.dev/tools/pub/cmd/pub-get
[11] Microsoft Learn — App Control and AppLocker overview: https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control/wdac-and-applocker-overview
[12] Flutter install troubleshooting / environment: https://docs.flutter.dev/install/troubleshoot
[13] Dev Containers spec — JSON reference for `mounts` / `workspaceMount`: https://containers.dev/implementors/json_reference/
[14] Docker docs — Bind mounts (readonly, recursive RO, subpaths): https://docs.docker.com/engine/storage/bind-mounts/
[15] VS Code remote docs — Add another local file mount: https://code.visualstudio.com/remote/advancedcontainers/add-local-file-mount
[16] VS Code remote docs — Change the default source-code mount (subpath): https://code.visualstudio.com/remote/advancedcontainers/change-default-source-mount
[17] devcontainers/spec issue 511 — readonly mount status: https://github.com/devcontainers/spec/issues/511
[18] Git docs — `core.fileMode` behaviour: https://git-scm.com/docs/git-config#Documentation/git-config.txt-corefileMode
[19] Windows OS Hub — backup/restore NTFS ACLs with `icacls` / RoboCopy: https://woshub.com/how-to-backup-and-restore-ntfs-permissions-using-icacls/
[20] Docker / SELinux / AppArmor permission model write-up: https://cr0x.net/en/docker-selinux-apparmor-permission-errors/
[21] Dev Containers spec — metadata JSON reference (`initializeCommand`): https://containers.dev/implementors/json_reference/
[22] Ken Muse — DevContainer `initializeCommand` behaviour: https://www.kenmuse.com/blog/new-devcontainer-initializecommand/
[23] Jamie McCrindle — Exploiting Visual Studio Code Devcontainers: https://foldr.uk/exploiting-visual-studio-code-devcontainers/
[24] GitHub Blog — Safeguarding VS Code against prompt injections: https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/
[25] Daniel Demmel — Coding agents in secured VS Code dev containers: https://www.danieldemmel.me/blog/coding-agents-in-secured-vscode-dev-containers
[26] GitHub Docs — Codespaces prebuilds and lifecycle: https://docs.github.com/en/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds
[27] JetBrains Blog — Deep dive into JetBrains Gateway: https://blog.jetbrains.com/blog/2021/12/03/dive-into-jetbrains-gateway/
[28] Bradley Beddoes — devcontainer-bridge (dbr): https://bradleybeddoes.com/writing/making-devcontainers-even-better-in-the-terminal
[29] Docker docs — BuildKit + remote drivers: https://docs.docker.com/build/buildkit/
[30] Skaffold docs — local build environment: https://skaffold.dev/docs/builders/build-environments/local/
[31] Skaffold docs — lifecycle hooks: https://skaffold.dev/docs/lifecycle-hooks/
[32] Dagger.io — host inputs are explicit and typed: https://dagger.io/
