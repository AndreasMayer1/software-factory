#!/usr/bin/env bash
# Shared helpers for scripts/quality/ gate scripts.
# Source this file from each gate; do not execute directly.
#
# Provides:
#   parse_exclude_arg "$@"        — sets EXCLUDE_FILE from --exclude-paths flag
#                                    or default scripts/quality/exclusions.txt
#   load_exclude_patterns         — populates global array EXCLUDE_PATTERNS
#                                    from EXCLUDE_FILE (skips comments/blanks)
#   is_excluded <path>            — 0 if path matches any exclusion pattern
#                                    (substring match), 1 otherwise

# Resolve project root (parent of scripts/).
_QUALITY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${_QUALITY_DIR}/../.." && pwd)"

EXCLUDE_FILE="${_QUALITY_DIR}/exclusions.txt"
EXCLUDE_PATTERNS=()

parse_exclude_arg() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --exclude-paths)
                EXCLUDE_FILE="$2"
                shift 2
                ;;
            --exclude-paths=*)
                EXCLUDE_FILE="${1#*=}"
                shift
                ;;
            -h|--help)
                _GATE_HELP=1
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
}

load_exclude_patterns() {
    EXCLUDE_PATTERNS=()
    if [[ ! -f "$EXCLUDE_FILE" ]]; then
        return 0
    fi
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Strip trailing comments, then trim whitespace.
        local trimmed="${line%%#*}"
        # shellcheck disable=SC2001
        trimmed="$(echo "$trimmed" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        [[ -z "$trimmed" ]] && continue
        EXCLUDE_PATTERNS+=("$trimmed")
    done < "$EXCLUDE_FILE"
}

is_excluded() {
    local path="$1"
    local pat
    for pat in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$path" == *"$pat"* ]]; then
            return 0
        fi
    done
    return 1
}
