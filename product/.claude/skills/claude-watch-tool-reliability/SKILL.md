---
name: claude-watch-tool-reliability
description: MANDATORY at the start of EVERY Opus session — brief on Claude Code tool-output bug #63966 and run the 7-day upstream-fix check
tools: [Read, Edit, Bash, Agent, Skill]
model: inherit
last_upstream_check: 2026-06-01
---

You brief the current session on the active Claude Code tool-reliability bug and, on a 7-day cadence, check whether it is fixed upstream. Governed by REQ-PROC-067 (Claude Code Usability). Every Opus session MUST invoke this once at start.

## The bug (anthropics/claude-code#63966)

Under Opus 4.x with parallel tool batches, tool-call results (Bash / Read / Edit / MCP) render EMPTY in the live UI, then flush late and out of order. The transcript JSONL keeps the real output — data is NOT lost; only live delivery and ordering break. Long sessions are the most affected.

## How to handle (apply proactively)

1. Empty-looking output ≠ failed command. Do NOT re-run in a probe loop (`echo PROBE`, `printf MARKER`, repeated `echo hello`) — the result exists and flushes late; probing only burns calls.
2. Keep parallel tool-batches small (avoid 10–30 concurrent Bash/Read/MCP calls).
3. Large expected output → redirect to a `/tmp` file, then Read that file.
4. `export FACTORY_DISABLE_READ_LOG=1` to cut per-Read hook overhead in long sessions (the per-Read logging hooks honor this kill-switch).
5. (Separate friction item, NOT the #63966 bug) If repo text reads garbled in your terminal or diffs, that is stray CRLF from the NTFS mirror (REQ-PROC-054); the git index is already LF. Strip working-tree CR:
   `while IFS= read -r -d '' f; do sed -i 's/\r$//' "$f"; done < <(git ls-files -z requirements_tasks/)`

## 7-day upstream check

1. Read `last_upstream_check` from this file's frontmatter. Days since: `echo $(( ( $(date +%s) - $(date -d <last_upstream_check> +%s) ) / 86400 ))`.
2. `< 7` → stop here; the briefing above is done.
3. `>= 7` → spawn a `general-purpose` Agent with `run_in_background: true`: WebFetch `https://github.com/anthropics/claude-code/issues/63966` and WebSearch for a fixed/patched Claude Code version; have it report whether a fix now exists and in which version.
4. Edit this file's `last_upstream_check` to today's date (`YYYY-MM-DD`). (Data-field self-update only — exempt from `claude-modify-skill`; do not change any logic here without it.)

## When the check reports a fix

Create ONE task via the `task-create` skill (type: impl, parent_requirement: REQ-PROC-067) that EITHER:
- after verifying an upgraded CLI fixes the empty-output behavior, removes this skill and the session-level mitigations (the kill-switch / parallel-batch / version guidance; the hook stdin-drain stays — it is harmless); OR
- improves the mitigations per the issue findings (a better workaround or a narrower trigger).

No fix found → only the date update; take no further action.
