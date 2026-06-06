#!/usr/bin/env bash
# PostToolUse Edit|Write — runs dart fix --apply on .dart files; no-ops for all others.
F=$(jq -r '.tool_input.file_path // ""')
[[ "$F" == *.dart ]] && dart fix --apply "$F" 2>/dev/null || true
