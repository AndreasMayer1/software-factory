#!/usr/bin/env bash
# PreToolUse Bash — blocks git commit when quality gates are RED (REQ-PROC-046).
# Always exits 0; uses deny JSON to block the tool call on gate failure.
CMD=$(jq -r '.tool_input.command // ""')
printf '%s\n' "$CMD" | grep -qE '^[[:space:]]*git[[:space:]]+commit' || exit 0

if [ "${SKIP_QUALITY_GATES:-0}" = "1" ]; then
    echo '[verify-quality] SKIPPED for git commit (SKIP_QUALITY_GATES=1)' >&2
    exit 0
fi

STAGED=$(git diff --name-only --cached 2>/dev/null)
printf '%s\n' "$STAGED" | grep -qE '^(lib|test|integration_test)/' || {
    echo '[verify-quality] SKIPPED for git commit (no staged files under lib/, test/, or integration_test/ — auto-bypass per REQ-PROC-046 scope)' >&2
    exit 0
}

if [ -f .git/quality_green_hash ]; then
    CUR_HASH=$(git stash create -u 2>/dev/null)
    [ -z "$CUR_HASH" ] && CUR_HASH=$(git rev-parse HEAD 2>/dev/null)
    STORED_HASH=$(cat .git/quality_green_hash 2>/dev/null)
    if [ -n "$CUR_HASH" ] && [ "$CUR_HASH" = "$STORED_HASH" ]; then
        echo "[verify-quality] SKIPPED for git commit (tree hash $CUR_HASH already GREEN — fast-skip per .git/quality_green_hash)" >&2
        exit 0
    fi
fi

bash scripts/quality/check_quality_gates.sh >/tmp/verify_quality_commit.log 2>&1
rc=$?
if [ $rc -ne 0 ]; then
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"verify-quality: RED — commit blocked. Quality gates failed. See /tmp/verify_quality_commit.log. Fix the violations and try again, or invoke the verify-quality skill to enter the back-pressure protocol. Override (only with explicit user authorization): set SKIP_QUALITY_GATES=1 and note the bypass in the commit message."}}'
fi
exit 0
