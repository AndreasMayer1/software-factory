# Protocol: Verify Backup and Sync Mechanisms

Task: TASK-PROC-054-03
Date: 2026-05-26
Agent: a4ea88a3-9cdf-47ff-b228-b040b45ab6fb

## Root Cause Found: DrvFs Bind-Mount Ownership Mismatch

Two bind-mount directories were owned by `ubuntu` (uid=1000) instead of `vscode` (uid=1001):
- `~/.ccs-container/` (CCS tarball store)
- `~/.claude/` (Claude config bind-mount)

The DrvFs mounts have `uid=1000;gid=1000` as the default in mount options (`/proc/mounts`),
but `~/backup/` and `~/windows_mirror/` carry NTFS extended attributes (metadata mount option)
that override to uid=1001. The two failing directories lacked those EAs — they fell back to
the mount default (ubuntu). This blocked the backup cron (runs as vscode) and broke write
access to the Claude config mount.

**Fix applied:**
```bash
sudo chown -R vscode:vscode ~/.ccs-container ~/.claude
```

This writes uid=1001 into the NTFS EAs on both directories. The change persists across
container restarts (as long as the Windows files are not recreated from scratch).

---

## Check Results

### 1. CCS Backup Mechanism — PASS (after fix)

| Check | Result |
|---|---|
| `sudo service cron status` | cron is running |
| `/etc/cron.d/ccs-backup` | Present — runs every 30 min as vscode |
| `check-ccs-backup-health.sh` | OK: newest backup 0 min old |
| `backup-ccs.sh` (manual) | Success — ccs-backup-20260526-012748.tar.gz (101M) |
| Tarballs in `~/.ccs-container/` | 3 tarballs (retention policy satisfied) |
| Tarball ownership | vscode:vscode (after fix) |

**Pre-fix state:** STALE — 3295 min old, manual backup failed with `Permission denied`.
**Cause:** `~/.ccs-container/` owned by ubuntu, vscode could not write.
**Fix:** `sudo chown -R vscode:vscode ~/.ccs-container`

---

### 2. Git Bundle Backup — PASS

| Check | Result |
|---|---|
| `.githooks/pre-push` exists | Yes (`-rwxr-xr-x`) |
| `git config core.hooksPath` | `.githooks` |
| `~/backup/flutter_app.bundle` | Present (20M, May 23 19:27) |
| `git bundle verify` | OK — complete history, 7 refs |

Bundle is from May 23 (last push date). The hook fires on each push, so the bundle
age reflects the last push, not a failure. Mechanism is healthy.

---

### 3. Parent-Config Backup — PASS

| Check | Result |
|---|---|
| `~/backup/_parent_.devcontainer/` | Present, contains `setup.sh` |
| `~/backup/_parent_.vscode/` | Present, contains `tasks.json` |
| Diff vs live `.devcontainer/` | Identical (no diff) |
| Diff vs live `.vscode/` | Identical (no diff) |

---

### 4. Claude Config Bind-Mount — PASS (after fix)

| Check | Result |
|---|---|
| `~/.claude/settings.json` exists | Yes (`-rwxr--r--`) |
| Readable | Yes |
| Write test (`touch ~/.claude/.write_test_marker`) | OK (after fix) |
| Mount is live | Confirmed — write succeeded and file was removed |

**Pre-fix state:** Write failed — `Permission denied`. 
**Cause:** `~/.claude/` owned by ubuntu, vscode could not write.
**Fix:** `sudo chown -R vscode:vscode ~/.claude` (applied together with `~/.ccs-container/`)

---

### 5. Mutagen Sync — PASS

| Check | Result |
|---|---|
| Daemon running | Yes (sync list returns results) |
| Session `flutter-app-to-windows` | Present |
| Alpha (container) | Connected |
| Beta (windows_mirror) | Connected |
| Status | Watching for changes |
| Conflicts | 0 |
| Transition problems | 0 |
| Propagation test | OK — file appeared in `~/windows_mirror/` within 5s |

---

### 6. DrvFs Ownership — PASS (after fix)

| Directory | Pre-fix | Post-fix |
|---|---|---|
| `~/backup/` | vscode:vscode | vscode:vscode |
| `~/windows_mirror/` | vscode:vscode | vscode:vscode |
| `~/.claude/` | ubuntu:ubuntu | vscode:vscode |
| `~/.ccs-container/` | ubuntu:ubuntu | vscode:vscode |

---

## Overall Health Status

**All 7 acceptance criteria: PASS**

- [x] CCS backup cron is running and healthcheck reports OK
- [x] Git bundle exists, is recent, and passes `git bundle verify`
- [x] Parent-config backup matches live `.devcontainer/` and `.vscode/`
- [x] Claude config bind-mount is live and writable
- [x] Mutagen sync session is healthy (Watching, Connected, 0 conflicts)
- [x] DrvFs ownership is correct (vscode:vscode) on all bind-mount roots
- [x] All results documented in protocol with pass/fail per mechanism

## Session Log

## 2026-05-26T01:30Z
**Agent**: Claude (main session)
**Agent ID**: a4ea88a3-9cdf-47ff-b228-b040b45ab6fb
**Action**: Ran all 7 verification checks inline; fixed DrvFs ownership mismatch on `~/.ccs-container` and `~/.claude`; re-verified all mechanisms post-fix
**Outcome**: PASS — all 7 acceptance criteria satisfied
**Next Step**: doc-update-guidelines → task-complete

## Recommendation

If the devcontainer is ever rebuilt from scratch, re-run `sudo chown -R vscode:vscode ~/.ccs-container ~/.claude` immediately after startup to restore the correct NTFS EAs. This could be automated in the `postStartCommand` or `postCreateCommand` in `devcontainer.json`.
