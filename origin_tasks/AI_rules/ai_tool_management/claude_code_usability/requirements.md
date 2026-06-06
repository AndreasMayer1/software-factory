---
id: REQ-PROC-067
status: active
tool_dependency: claude_code
urgency: 4
urgency_reason: U4-BLOCK
impact: 4
impact_reason: I4-QUAL
effort: M
stakeholder: developer
created: 2026-06-01
after: []
blocks: []
trackable_items:
  acceptance_criteria:
    - id: AC-01
      text: "Tool-call results (Bash, Read, Edit/Write, MCP) produced during a session are delivered to the model complete and in correct order; when an active platform regression prevents this, a documented mitigation (CLI version pin and/or reduced parallel tool-batch size) is in effect and recorded."
    - id: AC-02
      text: "Every hook command registered in .claude/settings.json reads and discards its stdin before exiting, so no hook can break the harness-to-hook pipe (EPIPE/SIGPIPE) under the Claude Code stdin-payload contract."
    - id: AC-03
      text: "No hook runs on a broader tool-event scope than its function requires: a hook that fires on every tool call exists only when its behavior genuinely applies to all tools."
    - id: AC-04
      text: "The Claude Code CLI version in use is known, and active versions carrying a documented tool-reliability regression are surfaced to the operator with the matching upstream issue reference."
    - id: AC-05
      text: "All version-controlled text files use LF line endings enforced by .gitattributes, so tools reading repository text files produce un-garbled output regardless of the host (container ext4 or synced Windows/NTFS mirror)."
    - id: AC-06
      text: "Claude Code's automatic context compression is disabled in the project .claude/settings.json (`\"autoCompactEnabled\": false`), ensuring no in-session compaction summarizes active context without developer awareness. The factory's file-based memory system (protocol.md / plans_and_protocols/) is the sole cross-session persistence mechanism."
---

# Claude Code Usability

## Overview

The entire software factory runs on a single AI coding tool: Claude Code. This requirement asserts that Claude Code must remain **reliably usable** as a hard dependency of the factory — its tool calls must deliver their results correctly to the session, and the project's own configuration (hooks, line endings, CLI version) must not silently degrade that reliability.

## Purpose

The factory's orchestrate → delegate → verify model assumes that when an agent runs a tool, it sees the tool's real result. When that assumption breaks, sessions waste calls re-probing the shell, fall back to brittle workarounds, and can act on output they never actually received.

This was triggered by a concrete incident (2026-06-01 investigation): on Claude Code 2.1.159, long-running Opus 4.8 sessions with parallel tool batches hit [anthropics/claude-code#63966](https://github.com/anthropics/claude-code/issues/63966) — tool-call results are delivered empty to the model in-session and only flush into the transcript late and out of order, so the persisted JSONL ends up looking complete. The session affected (`5b7178b8`) spent ~30 extra calls on liveness probes and `/tmp`-redirect + Python workarounds. The empty delivery is an upstream harness bug, independent of this project's filesystem: the project source is on ext4 and the active Claude runtime on overlayfs — not the 9p Windows mounts present elsewhere in the container. Two local factors are worth controlling because the bug is load-sensitive and the working tree is noisy: per-tool hook overhead (a catch-all `PostToolUse` hook that never drained stdin; per-`Read` logging hooks), and repo-wide CRLF line endings in the working tree (from the synced NTFS mirror, REQ-PROC-054). The CRLF is a readability/friction cost that forces repeated `tr` normalization and garbles the human-facing terminal/diff view — it is **not** a cause of the empty-output behavior.

It matters now because the factory cannot self-improve or ship reliably on top of a tool whose results it cannot trust, and because the failure mode is silent — the model perceives "empty" output and may fabricate or retry rather than surface the problem.

## Behavior

- When tool results are delivered correctly, agents act on real output with no shell-liveness probing or output-forcing markers (`echo PROBE`, `printf MARKER`, redirect-to-`/tmp`-then-Read).
- When a known platform regression is active, the operator is informed of the affected CLI version and the upstream issue, and the in-effect mitigation is recorded rather than silently tolerated.
- Project configuration (hooks, `.gitattributes`) never introduces a new way for tool output to be lost or garbled.

## Developer Guidelines

### Key Decisions
- **Hooks are on the hot path of every tool call.** Each registered hook adds process spawn + I/O to the tool round-trip. Hook count and scope are kept minimal because the platform's result-delivery reliability degrades under parallel-tool load.
- **Stdin is part of the hook contract.** Claude Code (2.x) delivers the hook payload as JSON on stdin; a hook that exits without consuming stdin risks a broken pipe. Draining stdin is mandatory, not optional.
- **The CLI version is a reliability variable.** Tool-result delivery is a property of the harness version, not just of the commands run. A version with a known regression is treated as a known-bad input until pinned or worked around.
- **Line endings are a readability/friction concern.** CRLF in working-tree text files garbles the human-facing terminal/diff view and forces repeated `tr` normalization; the git index is already LF, and keeping the working tree LF removes that friction. This is independent of the #63966 empty-output behavior — LF does not fix or cause it.
- **Auto-compact is disabled project-wide.** The factory is designed for short sessions with file-based cross-session memory (protocol.md / plans_and_protocols/). Auto-compact would silently summarize active context mid-session and add input-token cost on resumption; it provides no benefit the factory's own mechanisms don't already cover. The setting is enforced via `.claude/settings.json` in version control so every session opened against this project inherits it without manual configuration.

### Common Pitfalls
- A `PostToolUse`/`PreToolUse` hook registered with no (or an over-broad) matcher so it fires on every tool call for a purpose that applies to only some tools.
- A hook script that reads its payload via a single `jq` but has a code path that exits before `jq` runs, leaving stdin undrained.
- Assuming "the tool returned nothing" means the command produced no output — under #63966 the result exists in the transcript but rendered empty live; re-probing burns calls without fixing anything.
- Editing files on the Windows host of the NTFS mirror without LF enforcement, re-introducing CRLF.

## Related Requirements
- REQ-PROC-011 — Roo Code Deprecation and Archival (origin of the `tool_dependency` metadata convention)
- REQ-PROC-054 — Developer environment / no-host-bridge (source of the synced NTFS mirror that introduces CRLF)
- REQ-PROC-046 — Quality gate enforcement (the pre-commit Bash gate is itself a hook on the tool hot path)

## References
- [anthropics/claude-code#63966](https://github.com/anthropics/claude-code/issues/63966) — tool results empty in live UI, flush late (Opus 4.8, parallel batches)
- Claude Code hooks reference — https://code.claude.com/docs/en/hooks (stdin payload contract)
- `.claude/settings.json` — registered hooks
- `.claude/hooks/` — hook scripts
