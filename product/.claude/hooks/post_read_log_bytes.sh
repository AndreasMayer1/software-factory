#!/usr/bin/env bash
# PostToolUse Read — appends byte-count entry to an already-open session read_events.jsonl.
# Only writes if the log file exists (session must have been started by pre_read_log_event.sh).
INPUT=$(cat)
# Operator kill-switch: disable per-Read logging overhead in long Opus sessions
# (REQ-PROC-067 — reduces per-tool hook load that aggravates #63966). Stdin is
# already drained above, so exiting here is pipe-safe.
[ "${FACTORY_DISABLE_READ_LOG:-0}" = "1" ] && exit 0
F=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // ""')
[ -n "$F" ] && [ -n "${CLAUDE_SESSION_ID}" ] || exit 0
B=$([ -f "$F" ] && wc -c < "$F" 2>/dev/null || echo 0)
LOG=".factory/session_logs/${CLAUDE_SESSION_ID}/read_events.jsonl"
[ -f "$LOG" ] || exit 0
jq -cn \
    --arg fp "$F" \
    --arg sid "${CLAUDE_SESSION_ID}" \
    --argjson b "${B}" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{"type":"read_bytes","file_path":$fp,"session_id":$sid,"bytes":$b,"timestamp":$ts}' \
    >> "$LOG" 2>/dev/null
exit 0
