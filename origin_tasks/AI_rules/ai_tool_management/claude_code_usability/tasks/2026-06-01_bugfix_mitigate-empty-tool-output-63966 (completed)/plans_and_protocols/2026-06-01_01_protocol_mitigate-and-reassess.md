---
skills_used:
  - requ-explore
  - task-create
  - code-bugfix
  - claude-write-hook
  - claude-write-script
  - claude-create-skill
  - claude-modify-skill
  - task-complete-bugfix
  - task-complete
  - claude-commit
---

# Protocol — TASK-PROC-067-01 (slim bugfix)

Date: 2026-06-01 · Mode: code-bugfix slim (config/hooks, no Flutter worktree)

## Root cause (confirmed) — upstream, not local
The empty-output symptom is **anthropics/claude-code#63966**: under Opus 4.x + parallel
tool batches, tool-call results are delivered EMPTY to the model in-session and flush
into the transcript late/out-of-order — so the persisted JSONL ends up looking complete.
OPEN upstream, no fix. Env here: CLI 2.1.159 (issue reproduced on 2.1.154/2.1.158).

## Reassessment (2026-06-01) — corrected two earlier overstatements
1. **Filesystem / mount theory: ruled out as a cause.** Verified mounts:
   - project `/workspaces/private_mood_tracker` = **ext4**
   - active Claude runtime `CLAUDE_CONFIG_DIR=/home/vscode/.ccs/instances/gmail2` = **overlayfs**; `/tmp`, `.ccs` logs = overlayfs
   - 9p (v9fs → C:\) mounts exist but are OFF the hot path: default `~/.claude`, `windows_mirror`, `backup`, `.ccs-container`
   → the session did NOT read project files or Claude runtime state over a slow Windows mount.
2. **CRLF was NOT the cause of model-perceived emptiness.** For the model, `\r` bytes are
   just characters, not "empty". CRLF is a readability/friction issue (human terminal/diff
   view + repeated `tr` normalization). The git index is already LF; enforcement was already
   correct. The empty results were genuinely #63966 (real in-session empty delivery), plus
   the session distrusting a legitimate `grep -c → 0`.

## Changes applied
- **Hooks** (via claude-write-hook): `.claude/hooks/post_tool_use_inbox.sh` now drains stdin
  (`cat >/dev/null`) as its first action — the catch-all PostToolUse hook ran after every tool
  and never consumed its stdin payload (EPIPE/SIGPIPE risk under the 2.x hook contract) [AC-02].
  `pre_read_log_event.sh` + `post_read_log_bytes.sh` gained a `FACTORY_DISABLE_READ_LOG=1`
  kill-switch (drain-then-exit) so operators can cut per-Read hook overhead in long sessions.
  All seven hooks now verified to drain stdin [AC-02]. The only every-tool hook is the inbox
  poller; its behavior applies to all tools and it is cheap after draining [AC-03].
- **Tests** (via claude-write-script): added `TestPostToolUseInbox` (200 KB-payload pipe-safety,
  operator-message delivery, empty-inbox silence) + kill-switch tests on the two Read hooks.
  34 hook tests pass; full Python gates G1–G5 PASS (1059 passed).
- **Line endings** [AC-05]: `.gitattributes` already enforces `* text=auto eol=lf` (index = LF) —
  no change needed. One-time working-tree CR strip across 706 tracked files under
  `requirements_tasks/` → now byte-identical to the LF index (zero commit footprint), live reads
  clean. Recurrence is a REQ-PROC-054 environmental residual (NTFS-mirror sync writes CRLF).
- **Version awareness** [partial AC-01/AC-04]: created skill `claude-watch-tool-reliability`
  (MANDATORY each Opus session) — briefs on #63966, lists mitigations, and runs a 7-day
  upstream-fix check (last-check date stored in the skill); on finding a fix it creates a
  follow-up task under REQ-PROC-067 to remove the skill+mitigations or improve them.

## Not done / residual
- Full automated operator-surfacing of known-bad CLi versions (AC-04 in full) → future task.
- Upstream #63966 itself is not fixable here.
- Optional: the default `~/.claude` being on 9p is harmless while `CLAUDE_CONFIG_DIR` overrides
  to overlayfs; noted for awareness, not actioned.
