#!/usr/bin/env bash
# Delivers any pending operator message to the running session.
# Drain stdin first: Claude Code 2.x pipes the tool-event JSON payload to every
# hook; a catch-all PostToolUse hook that exits without consuming it can break
# the pipe (EPIPE/SIGPIPE) on large tool results (REQ-PROC-067 AC-02, #63966).
cat >/dev/null 2>&1 || true
INBOX="automation/inbox.md"
if [ -s "$INBOX" ]; then
  echo ""
  echo "=== OPERATOR MESSAGE ==="
  cat "$INBOX"
  echo "========================"
  # Atomically clear
  > "$INBOX"
fi
