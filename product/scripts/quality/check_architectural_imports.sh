#!/usr/bin/env bash
# REQ-PROC-046 AC-05 — architectural-import gate.
#
# Replaces DCM's `avoid-banned-imports`. Reads
# `scripts/quality/architectural_imports_policy.yaml` and, for each policy
# entry, ensures no file under the entry's path glob imports anything
# matching one of the entry's deny regexes.
#
# Usage:
#     scripts/quality/check_architectural_imports.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  every architectural import is allowed
#     1  one or more imports violate the policy
#     2  invocation error (policy file missing or unparseable)
set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

parse_exclude_arg "$@"
load_exclude_patterns

POLICY="${SCRIPT_DIR}/architectural_imports_policy.yaml"
if [[ ! -f "$POLICY" ]]; then
    echo "ERROR: architectural imports policy missing: $POLICY" >&2
    exit 2
fi

# Tiny purpose-built parser. The policy file has a fixed shape:
#
#   - path: "lib/core/domain/**"
#     deny:
#       - "^package:flutter/"
#       - "^package:flutter_bloc/"
#
# We extract one PATH plus its DENY regex list per block. Comments and
# blank lines are skipped. Quoted strings unquoted via sed.
PATHS=()
DENIES=()  # parallel array; entries separated by ASCII RS (\x1e)

current_path=""
current_denies=""
in_deny=0

flush_block() {
    if [[ -n "$current_path" ]]; then
        PATHS+=("$current_path")
        DENIES+=("$current_denies")
    fi
    current_path=""
    current_denies=""
    in_deny=0
}

unquote() {
    local s="$1"
    s="${s#\"}"; s="${s%\"}"
    s="${s#\'}"; s="${s%\'}"
    echo "$s"
}

while IFS= read -r line || [[ -n "$line" ]]; do
    # Strip line comments and trailing whitespace.
    stripped="${line%%#*}"
    stripped="$(echo "$stripped" | sed -e 's/[[:space:]]*$//')"
    [[ -z "$stripped" ]] && continue

    if [[ "$stripped" =~ ^-[[:space:]]+path:[[:space:]]+(.+)$ ]]; then
        flush_block
        current_path="$(unquote "${BASH_REMATCH[1]}")"
        in_deny=0
    elif [[ "$stripped" =~ ^[[:space:]]+deny:[[:space:]]*$ ]]; then
        in_deny=1
    elif (( in_deny )) && [[ "$stripped" =~ ^[[:space:]]+-[[:space:]]+(.+)$ ]]; then
        regex="$(unquote "${BASH_REMATCH[1]}")"
        if [[ -z "$current_denies" ]]; then
            current_denies="$regex"
        else
            current_denies="${current_denies}"$'\x1e'"${regex}"
        fi
    fi
done < "$POLICY"
flush_block

if [[ ${#PATHS[@]} -eq 0 ]]; then
    echo "ERROR: no policy entries parsed from $POLICY" >&2
    exit 2
fi

# Convert an ant-style glob into a bash-extended-regex. We do this in awk
# rather than a chain of bash substitutions for clarity.
glob_to_regex() {
    local g="$1"
    awk -v g="$g" 'BEGIN {
        out = "^"
        i = 1
        n = length(g)
        while (i <= n) {
            c = substr(g, i, 1)
            d = (i < n) ? substr(g, i + 1, 1) : ""
            if (c == "*" && d == "*") {
                out = out ".*"
                i += 2
                # Consume an optional following slash so "**/" matches "".
                if (substr(g, i, 1) == "/") { i++ }
            } else if (c == "*") {
                out = out "[^/]*"
                i += 1
            } else if (c == "." || c == "+" || c == "(" || c == ")" \
                    || c == "|" || c == "^" || c == "$" || c == "[" \
                    || c == "]" || c == "{" || c == "}" || c == "?" \
                    || c == "\\") {
                out = out "\\" c
                i += 1
            } else {
                out = out c
                i += 1
            }
        }
        out = out "$"
        print out
    }'
}

violations=0

for idx in "${!PATHS[@]}"; do
    path_glob="${PATHS[$idx]}"
    deny_blob="${DENIES[$idx]}"
    path_regex="$(glob_to_regex "$path_glob")"

    # Walk lib/ once per policy block; matching files only.
    while IFS= read -r -d '' file; do
        rel="${file#${PROJECT_ROOT}/}"
        if ! [[ "$rel" =~ $path_regex ]]; then
            continue
        fi
        if is_excluded "$rel"; then
            continue
        fi
        # Iterate import lines.
        line_no=0
        while IFS= read -r src_line || [[ -n "$src_line" ]]; do
            ((line_no++))
            if [[ "$src_line" =~ ^[[:space:]]*import[[:space:]]+\'([^\']+)\' ]] \
                || [[ "$src_line" =~ ^[[:space:]]*import[[:space:]]+\"([^\"]+)\" ]]; then
                uri="${BASH_REMATCH[1]}"
                # Test against each deny regex.
                IFS=$'\x1e' read -r -a denies <<< "$deny_blob"
                for d in "${denies[@]}"; do
                    if [[ "$uri" =~ $d ]]; then
                        echo "$rel:$line_no: import '$uri' violates policy for $path_glob"
                        ((violations++))
                        break
                    fi
                done
            fi
        done < "$file"
    done < <(find "${PROJECT_ROOT}/lib" -type f -name '*.dart' -print0 2>/dev/null || true)
done

if (( violations > 0 )); then
    echo
    echo "FAIL: $violations architectural-import violation(s)."
    echo "Update scripts/quality/architectural_imports_policy.yaml if the rule"
    echo "needs revisiting; do not silence violations in code."
    exit 1
fi

echo "PASS: every import respects the architectural-imports policy."
exit 0
