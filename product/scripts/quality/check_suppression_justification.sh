#!/usr/bin/env bash
# REQ-PROC-046 AC-11 — suppression-justification gate.
#
# Greps lib/, test/, integration_test/ for `// ignore:` and
# `// ignore_for_file:` directives. Each must have an adjacent justification
# comment (within 2 lines above) of non-trivial length, or a justification
# appended on the same line after the directive.
#
# Usage:
#     scripts/quality/check_suppression_justification.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  no unjustified suppressions
#     1  one or more unjustified suppressions
#     2  invocation error

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

parse_exclude_arg "$@"
load_exclude_patterns

cd "$PROJECT_ROOT"

TARGETS=()
[[ -d lib ]] && TARGETS+=("lib")
[[ -d test ]] && TARGETS+=("test")
[[ -d integration_test ]] && TARGETS+=("integration_test")

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    echo "ERROR: no scan targets (lib/, test/, integration_test/)" >&2
    exit 2
fi

JUSTIFICATION_RADIUS=2
# A "non-trivial" justification has at least 12 characters of content beyond
# the comment marker — long enough to convey *why*, short enough not to be
# overly fussy. Tune by raising if junk-comments slip through.
MIN_JUSTIFICATION_LEN=12

violations=()

# Collect all `// ignore:` / `// ignore_for_file:` lines across targets.
while IFS= read -r raw; do
    # raw format: "path:lineno:matched-text"
    path="${raw%%:*}"
    rest="${raw#*:}"
    lineno="${rest%%:*}"
    text="${rest#*:}"

    is_excluded "$path" && continue
    [[ "$path" == *".g.dart" ]] && continue
    [[ "$path" == *".freezed.dart" ]] && continue
    [[ "$path" == *"/generated/"* ]] && continue

    # 1) Same-line trailing justification: anything after the ignore directive.
    #    The directive itself includes the rule list, so we look for content
    #    AFTER the rule-list segment.
    same_line_justified=0
    # Strip everything up to and including `ignore:` or `ignore_for_file:` and
    # then up to the next whitespace-separated end of the rule list.
    # Pragmatic check: if the line contains another `//` AFTER the directive,
    # treat that as the justification.
    after_directive="${text#*ignore}"
    if [[ "$after_directive" == *"//"* ]]; then
        tail_comment="${after_directive#*//}"
        # Trim whitespace
        # shellcheck disable=SC2001
        trimmed="$(echo "$tail_comment" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        if (( ${#trimmed} >= MIN_JUSTIFICATION_LEN )); then
            same_line_justified=1
        fi
    fi

    if [[ $same_line_justified -eq 1 ]]; then
        continue
    fi

    # 2) Preceding comment lines within radius.
    start=$(( lineno - JUSTIFICATION_RADIUS ))
    (( start < 1 )) && start=1
    end=$(( lineno - 1 ))
    preceding_justified=0
    if (( end >= start )); then
        # Read each preceding line; check it is a comment with enough content.
        while IFS= read -r pre_line; do
            stripped="$(echo "$pre_line" | sed -e 's/^[[:space:]]*//')"
            if [[ "$stripped" == //* ]]; then
                content="${stripped#//}"
                # shellcheck disable=SC2001
                content_trim="$(echo "$content" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
                # Skip another suppression directive — that doesn't justify.
                if [[ "$content_trim" == ignore:* || "$content_trim" == ignore_for_file:* ]]; then
                    continue
                fi
                if (( ${#content_trim} >= MIN_JUSTIFICATION_LEN )); then
                    preceding_justified=1
                    break
                fi
            fi
        done < <(sed -n "${start},${end}p" "$path" || true)
    fi

    if [[ $preceding_justified -eq 0 ]]; then
        violations+=("$path:$lineno: $text")
    fi

done < <(grep -rEn -I \
            --include="*.dart" \
            '// *ignore(_for_file)?:' "${TARGETS[@]}" 2>/dev/null || true)

if [[ ${#violations[@]} -gt 0 ]]; then
    echo "FAIL: REQ-PROC-046 AC-11 (suppression justification) — ${#violations[@]} unjustified suppression(s):"
    for v in "${violations[@]}"; do
        echo "  $v"
    done
    echo
    echo "Each // ignore: or // ignore_for_file: directive must be preceded"
    echo "by (or trailed by, on the same line) a comment naming WHY the"
    echo "suppression is correct. Minimum ${MIN_JUSTIFICATION_LEN} characters of content."
    exit 1
fi

echo "PASS: REQ-PROC-046 AC-11 (suppression justification) — 0 unjustified suppressions"
exit 0
