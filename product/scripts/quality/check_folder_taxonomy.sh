#!/usr/bin/env bash
# REQ-PROC-046 K.2 (user 2026-05-13) — domain folder-taxonomy gate.
#
# Every .dart file inside `lib/core/domain/` or `lib/features/*/domain/`
# MUST live in one of the allow-listed sub-folders. Bare-`domain/` files and
# files in unexpected sub-folder names are flagged.
#
# Allow-listed sub-folder names live in
# `scripts/quality/folder_taxonomy_allowlist.txt`. Adding a new taxonomy
# category is a documented design decision; the gate stays stable across
# such additions.
#
# Usage:
#     scripts/quality/check_folder_taxonomy.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  no violations
#     1  one or more violations
#     2  invocation error (allowlist missing)
set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

parse_exclude_arg "$@"
load_exclude_patterns

ALLOWLIST="${SCRIPT_DIR}/folder_taxonomy_allowlist.txt"
if [[ ! -f "$ALLOWLIST" ]]; then
    echo "ERROR: folder taxonomy allowlist missing: $ALLOWLIST" >&2
    exit 2
fi

# Load allow-listed names (one per line, '#' comments stripped).
ALLOWED=()
while IFS= read -r line || [[ -n "$line" ]]; do
    trimmed="${line%%#*}"
    trimmed="$(echo "$trimmed" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [[ -z "$trimmed" ]] && continue
    ALLOWED+=("$trimmed")
done < "$ALLOWLIST"

is_allowed() {
    local name="$1"
    local a
    for a in "${ALLOWED[@]}"; do
        if [[ "$a" == "$name" ]]; then
            return 0
        fi
    done
    return 1
}

# Discover domain roots.
ROOTS=()
[[ -d "${PROJECT_ROOT}/lib/core/domain" ]] && ROOTS+=("${PROJECT_ROOT}/lib/core/domain")
while IFS= read -r -d '' dir; do
    ROOTS+=("$dir")
done < <(find "${PROJECT_ROOT}/lib/features" -mindepth 2 -maxdepth 2 -type d -name domain -print0 2>/dev/null || true)

if [[ ${#ROOTS[@]} -eq 0 ]]; then
    echo "NOTICE: no */domain/ directories found; nothing to scan." >&2
    exit 0
fi

violations=0
for root in "${ROOTS[@]}"; do
    # Files directly in `root/` (no sub-folder) — flag.
    while IFS= read -r -d '' file; do
        rel="${file#${PROJECT_ROOT}/}"
        is_excluded "$rel" && continue
        echo "$rel: domain file is not inside an allow-listed sub-folder"
        ((violations++))
    done < <(find "$root" -mindepth 1 -maxdepth 1 -type f -name '*.dart' -print0)

    # Files in `root/<sub>/...` where <sub> is not allow-listed — flag.
    while IFS= read -r -d '' dir; do
        sub="$(basename "$dir")"
        if is_allowed "$sub"; then
            continue
        fi
        # Walk and flag every .dart file beneath this disallowed sub-folder.
        while IFS= read -r -d '' file; do
            rel="${file#${PROJECT_ROOT}/}"
            is_excluded "$rel" && continue
            echo "$rel: sub-folder '$sub' is not in folder_taxonomy_allowlist.txt"
            ((violations++))
        done < <(find "$dir" -type f -name '*.dart' -print0)
    done < <(find "$root" -mindepth 1 -maxdepth 1 -type d -print0)
done

if (( violations > 0 )); then
    echo
    echo "FAIL: $violations folder-taxonomy violation(s)."
    echo "Either move the file into an allow-listed sub-folder, or add the"
    echo "category to scripts/quality/folder_taxonomy_allowlist.txt with a"
    echo "short justification."
    exit 1
fi

echo "PASS: every domain file lives in an allow-listed sub-folder."
exit 0
