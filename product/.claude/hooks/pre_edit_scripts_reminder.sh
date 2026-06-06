#!/usr/bin/env bash
# PreToolUse Edit|Write — reminds Claude to use claude-write-script before editing Python/PS1 scripts.
# Exits 0 always; outputs hookSpecificOutput JSON only when file matches scripts/*.py|.ps1.
F=$(jq -r '.tool_input.file_path // ""')
if printf '%s\n' "$F" | grep -qE "(^|/)scripts/.*\.(py|ps1)$"; then
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"REMINDER: editing scripts/ requires the claude-write-script skill (mandatory per CLAUDE.md §7 / REQ-PROC-051 enforcement). Invoke the skill first; do not Edit/Write directly."}}'
fi
