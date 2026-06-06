# ADR: CCS Session State Backup — Periodic Tarball Snapshots

**Date**: 2026-05-23
**Status**: Accepted
**Deciders**: app provider (PERSONA-015)
**Supersedes**: the bind-mount of `%USERPROFILE%\.ccs-container` → `/home/vscode/.ccs` that previously appeared in `devcontainer.json` (now commented-out / removed).

---

## Context

CCS (the Claude Code session/proxy server installed in the devcontainer via `@kaitranntt/ccs`) keeps its full operational state under `~/.ccs/`: account-scoped session logs (`instances/<account>/session-env/<uuid>/`), per-project conversation JSONLs (`shared/context-groups/default/projects/<slug>/<uuid>.jsonl`), the cliproxy auth folder, configuration, caches, logs. Total: ~337 MB, ~1600 files, on the order of dozens of symlinks (each `instances/<account>/{skills,agents,commands,plugins}` is a symlink into `shared/`).

This state lives inside the container filesystem by default. `Dev Containers: Rebuild Container` destroys the container filesystem and creates a new one — session history, agent state, and conversation logs are gone unless they have been moved out of the container before the rebuild. In a prior session this exact failure mode lost the working session that was iterating on this very topic.

The companion `~/.claude/` folder is bind-mounted from `%USERPROFILE%\.claude-container` and persists across rebuilds via the mount itself. The same shortcut was attempted for `~/.ccs/` but was reverted: with `~/.ccs` bind-mounted onto NTFS via DrvFs, CCS's internal symlinks broke (DrvFs has incomplete symlink support — it requires Windows Developer Mode or admin for `mklink`, and even then round-trip semantics differ from Linux ext4). Symptoms ranged from CCS failing to enumerate skills/agents to outright startup failure.

The problem to solve: keep CCS state recoverable across container rebuilds, without bind-mounting `~/.ccs` directly onto NTFS, and without depending on the developer remembering to run a manual backup before each rebuild.

## Decision

**A cron job inside the devcontainer produces a compressed tarball of `~/.ccs` every 30 minutes, writes it atomically to `/home/vscode/.ccs-container/` (a Windows NTFS bind-mount distinct from the OneDrive-backed `~/backup` mount), and retains the newest 3 snapshots. On container creation, when `~/.ccs` is empty, `setup.sh` restores from the newest snapshot in that folder.**

Component summary:

- **`/usr/local/bin/backup-ccs.sh`** — tarball writer. Atomic via `.tmp` → rename. Retention enforced inline.
- **`/usr/local/bin/check-ccs-backup-health.sh`** — health check. Exits 1 if the newest snapshot is older than 35 min (cron interval + 5 min slack).
- **`/etc/cron.d/ccs-backup`** — cron entry, runs as `vscode`, every 30 min, log appended to `/home/vscode/.ccs-container/backup.log`.
- **`setup.sh`** (postCreate) — installs cron, deploys the two scripts and the cron file, restores from the newest snapshot when `~/.ccs` is empty.
- **`postStartCommand`** (devcontainer.json) — starts the cron daemon (cirruslabs image has no systemd) and runs `backup-ccs.sh` once eagerly so the first snapshot of a session exists before the first 30-minute tick.
- **Windows host** — folder `%USERPROFILE%\.ccs-container` (created once, manually); plain local NTFS, not OneDrive-synced.

Size budget: ~100 MB per gzip'd snapshot × 3 retained ≈ 300 MB on Windows.

## Alternatives Considered

### Option A — Bind-mount `%USERPROFILE%\.ccs-container` → `~/.ccs` directly

The shortcut that works for `~/.claude`. **Rejected** because CCS's internal symlinks break on DrvFs/NTFS. The failure is not a slowdown — CCS becomes non-functional. Empirically reproduced in the session that motivated this ADR.

### Option B — Mutagen continuous sync of `~/.ccs` → Windows folder

Mutagen handles small-delta propagation well and is already in use for the project tree. **Rejected** for two reasons:

1. **NTFS symlinks unresolved.** Mutagen's `symlinkMode: portable` translates symlinks whose targets lie within the sync root (CCS's symlinks qualify), but the resulting symlinks on the beta side require `mklink`-capable Windows, and the round-trip behavior on the next reconciliation is not robust enough to bet session integrity on.
2. **Empty-alpha-deletes-beta hazard on rebuild.** In `one-way-safe` mode (container → Windows), if the container is rebuilt and `~/.ccs` starts empty before the restore step, the next sync tick interprets the empty alpha as "delete everything" and wipes the Windows-side copy. Orchestrating "restore first, then start sync" reliably is more fragile than the snapshot/restore split.

Tarballs sidestep both: tar preserves symlinks bit-exact, and a snapshot is a self-contained file that has no notion of "the source is empty so delete me."

### Option C — Manual pre-rebuild backup script triggered by the developer

A `backup-ccs.sh` invoked by hand before each `Rebuild Container`. **Rejected** because the failure mode it must prevent — forgetting to run the backup — is exactly the human-disciplined path. The whole point of the mechanism is that the developer should not have to remember anything.

### Option D — SIGTERM trap in the container (Pre-Stop hook)

Docker delivers SIGTERM to PID 1 before `docker rm`. A trap handler could fire a final backup on the way out. **Rejected** for two reasons:

1. Docker's grace period (default ~10 s) is tight for a 337 MB tar to NTFS via DrvFs; partial-write risk is non-trivial.
2. VS Code's `Rebuild Container` likely uses `docker rm -f`, which skips the SIGTERM path entirely. The mechanism would not fire in the case it most needs to.

### Option E — Claude Code `Stop` hook for per-response backups

Claude Code's `Stop` event fires after every assistant turn. **Rejected** as too frequent — a 337 MB tar after every message adds noticeable latency and produces enormous churn on the Windows folder.

### Option F — Claude Code `SessionEnd` hook for per-session backups

`SessionEnd` is per-session, not per-message, so the frequency is right. **Considered as a complement, not an alternative.** If a session ends cleanly, `SessionEnd` would catch the freshest possible state. But a session that ends because VS Code was abruptly closed, the container was killed, or the user clicked Rebuild without exiting Claude Code first does not fire `SessionEnd` reliably. The cron path is the load-bearing mechanism; a `SessionEnd` hook can be added later as a freshness booster without changing this decision.

## Consequences

### Positive

- **Survives Rebuild Container.** Newest snapshot is at most 30 min old; restore from `~/.ccs-container/ccs-backup-*.tar.gz` runs in `setup.sh` before the new session starts.
- **Symlinks intact.** Tar preserves them; the restore re-materializes the original symlink graph.
- **No bind-mount of `~/.ccs` onto NTFS.** CCS sees a normal ext4 filesystem at runtime; no DrvFs in the hot path.
- **Operational visibility.** `backup.log` lives on the Windows-side folder so it survives rebuild; `check-ccs-backup-health.sh` is a one-shot diagnostic.
- **Disk budget bounded.** Retention=3 caps the Windows-side footprint at ~300 MB.

### Negative / Accepted Risks

- **Up to 30 min of session loss in the gap between snapshots.** A manual `backup-ccs.sh` before a deliberate Rebuild closes this gap when remembered.
- **No host-execution bridge or external watcher.** Consistent with REQ-PROC-054 and its ADR (`2026-05-19_no-host-bridge.md`) — the backup mechanism runs entirely inside the container and writes to a passive Windows folder. No host-side automation is introduced.
- **Snapshot consistency under active writes.** CCS writes to JSONLs as append-only. A tar that races a write at most truncates the final line of a single session log, which standard JSONL parsing skips. No corruption of the broader state.
- **Cron daemon could die silently.** Mitigated by `check-ccs-backup-health.sh` (manual invocation) — could be elevated to a `SessionStart` hook if a stale snapshot ever escapes notice.
- **Cron interval is hardcoded at 30 min.** Changing it requires editing `.devcontainer/ccs-backup.cron` and rebuilding the container. Acceptable — the value is not expected to need frequent tuning.

## References

- `.devcontainer/backup-ccs.sh` — the snapshot writer.
- `.devcontainer/check-ccs-backup-health.sh` — staleness probe.
- `.devcontainer/ccs-backup.cron` — cron entry (deployed to `/etc/cron.d/ccs-backup`).
- `.devcontainer/setup.sh` — installer + restore.
- `.devcontainer/devcontainer.json` — bind-mount + `postStartCommand` that starts cron and runs the eager initial snapshot.
- `setup_guides/wsl_devcontainer_setup.md` §6 and §7 — the developer-facing setup instructions that reflect the mechanism.
- `decisions/2026-05-19_no-host-bridge.md` — the contract this mechanism stays within (no host-side automation; everything in-container).
