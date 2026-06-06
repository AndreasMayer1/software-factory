#!/usr/bin/env bash
# PostToolUse Edit|Write — runs dart analyze and surfaces errors/warnings for .dart files.
F=$(jq -r '.tool_input.file_path // ""')
[[ "$F" == *.dart ]] && dart analyze "$F" 2>&1 | grep -E 'error|warning' || true
