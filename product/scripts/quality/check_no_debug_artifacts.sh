#!/usr/bin/env bash
# REQ-PROC-046 AC-12 — no leftover debug artifacts in lib/.
#
# Greps lib/ for three categories of leftover debug code:
#   1. Bare `print(` calls (Dart's stdout print — never appropriate in lib/).
#   2. `debugPrint(` calls *without* a `[DIAG-*]` bracketed prefix tag in the
#      first string argument, per CLAUDE.md "Bugfix conventions".
#   3. `// TEMPORARY:` markers, which CLAUDE.md requires for any temporary
#      bugfix block — by definition these must not survive task completion.
#
# Bugfix-task allow-listing: this script does NOT consult automation/state.json
# to determine which tasks are mid-flight. Per the task goal note, the
# accepted limitation is that the gate catches violations *outside* active
# bugfix tasks; an in-flight bugfix may legitimately have DIAG- and
# TEMPORARY: lines, and the developer is expected to clean them up in
# task-complete-bugfix. Files can be exempted via scripts/quality/exclusions.txt
# during a bugfix and removed when it lands.
#
# Usage:
#     scripts/quality/check_no_debug_artifacts.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  no leftover debug artifacts
#     1  one or more leftover debug artifacts found
#     2  invocation error

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

parse_exclude_arg "$@"
load_exclude_patterns

LIB_DIR="${PROJECT_ROOT}/lib"
if [[ ! -d "$LIB_DIR" ]]; then
    echo "ERROR: lib/ not found at $LIB_DIR" >&2
    exit 2
fi

violations_print=()
violations_debugprint=()
violations_temporary=()

while IFS= read -r -d '' file; do
    rel="${file#"${PROJECT_ROOT}/"}"
    [[ "$rel" == *".g.dart" ]] && continue
    [[ "$rel" == *".freezed.dart" ]] && continue
    [[ "$rel" == *"/generated/"* ]] && continue
    is_excluded "$rel" && continue

    # Helper: line-is-comment? Drops lines whose first non-space chars are //
    # (covers /// doc comments and // line comments). This avoids flagging
    # mentions of `debugPrint(` or `print(` inside explanatory comments.
    _is_comment_line() {
        local t="$1"
        # Trim leading whitespace
        # shellcheck disable=SC2001
        local stripped
        stripped="$(echo "$t" | sed -e 's/^[[:space:]]*//')"
        [[ "$stripped" == //* ]]
    }

    # 1) Bare print(  — must be word-boundary so we don't catch `imprint(` etc.
    while IFS= read -r m; do
        text="${m#*:}"
        _is_comment_line "$text" && continue
        violations_print+=("$rel:$m")
    done < <(grep -nE '(^|[^A-Za-z0-9_])print\(' "$file" || true)

    # 2) debugPrint( without [DIAG-*] prefix on the same line.
    #    Strategy: list every debugPrint( line, then drop those whose contents
    #    contain "[DIAG-" or are inside a comment.
    while IFS= read -r m; do
        # m = "lineno:text"
        text="${m#*:}"
        _is_comment_line "$text" && continue
        if [[ "$text" == *"[DIAG-"* ]]; then
            continue
        fi
        violations_debugprint+=("$rel:$m")
    done < <(grep -nE '\bdebugPrint\(' "$file" || true)

    # 3) // TEMPORARY: markers (these are *expected* to be in comments — that
    #    IS the marker. So we do NOT skip comment lines here.)
    while IFS= read -r m; do
        violations_temporary+=("$rel:$m")
    done < <(grep -nE '//[[:space:]]*TEMPORARY:' "$file" || true)

done < <(find "$LIB_DIR" -type f -name "*.dart" -print0)

total=$(( ${#violations_print[@]} + ${#violations_debugprint[@]} + ${#violations_temporary[@]} ))

if (( total > 0 )); then
    echo "FAIL: REQ-PROC-046 AC-12 (no leftover debug artifacts) — $total finding(s):"
    if (( ${#violations_print[@]} > 0 )); then
        echo "  --- bare print() (${#violations_print[@]}) ---"
        for v in "${violations_print[@]}"; do echo "    $v"; done
    fi
    if (( ${#violations_debugprint[@]} > 0 )); then
        echo "  --- debugPrint without [DIAG-*] prefix (${#violations_debugprint[@]}) ---"
        for v in "${violations_debugprint[@]}"; do echo "    $v"; done
    fi
    if (( ${#violations_temporary[@]} > 0 )); then
        echo "  --- // TEMPORARY: markers (${#violations_temporary[@]}) ---"
        for v in "${violations_temporary[@]}"; do echo "    $v"; done
    fi
    echo
    echo "If a debugPrint is part of an active bugfix, prefix the message with"
    echo "  '[DIAG-<short-tag>] '   (CLAUDE.md bugfix conventions)"
    echo "and clean it up before task-complete-bugfix. // TEMPORARY: blocks"
    echo "must be deleted before the task is marked done."
    exit 1
fi

echo "PASS: REQ-PROC-046 AC-12 (no leftover debug artifacts) — 0 findings in lib/"
exit 0
