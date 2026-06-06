#!/usr/bin/env bash
# PreToolUse Read — logs file-path + timestamp to the session's read_events.jsonl.
# No-ops when CLAUDE_SESSION_ID is unset; always exits 0.
INPUT=$(cat)
# Operator kill-switch: disable per-Read logging overhead in long Opus sessions
# (REQ-PROC-067 — reduces per-tool hook load that aggravates #63966). Stdin is
# already drained above, so exiting here is pipe-safe.
[ "${FACTORY_DISABLE_READ_LOG:-0}" = "1" ] && exit 0
F=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // ""')
[ -n "$F" ] && [ -n "${CLAUDE_SESSION_ID}" ] || exit 0
mkdir -p ".factory/session_logs/${CLAUDE_SESSION_ID}"
jq -cn \
    --arg fp "$F" \
    --arg sid "${CLAUDE_SESSION_ID}" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{"tool":"Read","file_path":$fp,"session_id":$sid,"timestamp":$ts}' \
    >> ".factory/session_logs/${CLAUDE_SESSION_ID}/read_events.jsonl" 2>/dev/null
exit 0
