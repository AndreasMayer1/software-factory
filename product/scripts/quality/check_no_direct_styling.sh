#!/usr/bin/env bash
# REQ-PROC-046 AC-02 / 2026-05-13 K.1 — direct-styling gate.
#
# Forbids direct instantiation of low-level Material styling classes inside
# `lib/features/`. The design system (`lib/core/design_system/`) is the
# permitted home for these constructions; feature code consumes design-system
# components, never the underlying Material primitives.
#
# Replaces the previous DCM `ban-name` rule for ButtonStyle / TextStyle /
# Color / Colors / ThemeData.
#
# Usage:
#     scripts/quality/check_no_direct_styling.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  no violations
#     1  one or more violations (file:line:match)
#     2  invocation error
set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

parse_exclude_arg "$@"
load_exclude_patterns

SCAN_ROOT="${PROJECT_ROOT}/lib/features"
if [[ ! -d "$SCAN_ROOT" ]]; then
    echo "NOTICE: $SCAN_ROOT does not exist; nothing to scan." >&2
    exit 0
fi

# Match constructions / member accesses of low-level styling primitives.
# Word-boundary anchored; class names followed by '(' (constructor call)
# or '.' (member access) only.
PATTERN='\b(ButtonStyle|TextStyle|Color|ThemeData)\s*\(|\bColors\.'

violations=0
while IFS= read -r -d '' file; do
    rel="${file#${PROJECT_ROOT}/}"
    if is_excluded "$rel"; then
        continue
    fi
    # Each match emitted with file:line:content.
    while IFS=: read -r line content; do
        [[ -z "$line" ]] && continue
        # Skip comment-only lines.
        stripped="$(echo "$content" | sed -e 's/^[[:space:]]*//')"
        if [[ "$stripped" == //* ]]; then
            continue
        fi
        echo "$rel:$line:$stripped"
        ((violations++))
    done < <(grep -nE "$PATTERN" "$file" 2>/dev/null || true)
done < <(find "$SCAN_ROOT" -type f -name '*.dart' -print0)

if (( violations > 0 )); then
    echo
    echo "FAIL: $violations direct-styling violation(s) under lib/features/."
    echo "Use design-system components from lib/core/design_system/ instead."
    exit 1
fi

echo "PASS: no direct-styling primitives under lib/features/."
exit 0
