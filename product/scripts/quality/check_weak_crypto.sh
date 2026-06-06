#!/usr/bin/env bash
# REQ-PROC-052 SP4 — no weak crypto in security paths.
#
# Greps lib/ for SHA-1 and MD5 usage from package:crypto. For each match, the
# script verifies that an *adjacent* comment line (within 2 lines above or on
# the same line) names a non-security purpose. Per AC-04, SHA-1 / MD5 are
# permitted only with that justification (e.g. cache key, file checksum).
#
# Usage:
#     scripts/quality/check_weak_crypto.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  no unjustified weak-crypto uses
#     1  one or more uses without adjacent justification
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

# Patterns chosen to match `package:crypto`'s public surface.
# The `\b` word-boundary on the regex side keeps `sha1` from matching `sha1024`
# or similar identifiers that an LLM might invent.
WEAK_CRYPTO_REGEX='\b(sha1|md5)\b\.(convert|bind)|\b(Sha1|Md5)\b\(|\b(sha1|md5)\b *= *[A-Z]'

# Heuristic: an "adjacent justification" is a comment line within
# JUSTIFICATION_RADIUS lines above the match (or trailing on the same line)
# that contains at least one of the keywords below. Tuned to be permissive
# of common phrasings; precision can be raised later if false negatives bite.
JUSTIFICATION_RADIUS=2
JUSTIFICATION_KEYWORDS_RE='(non-security|non security|cache key|cache-key|checksum|content hash|integrity|deterministic id|fingerprint|stable id|legacy compat)'

violations=()

while IFS= read -r -d '' file; do
    rel="${file#"${PROJECT_ROOT}/"}"
    [[ "$rel" == *".g.dart" ]] && continue
    [[ "$rel" == *".freezed.dart" ]] && continue
    [[ "$rel" == *"/generated/"* ]] && continue
    is_excluded "$rel" && continue

    # Find candidate lines (line-number prefixed).
    while IFS= read -r match_line; do
        lineno="${match_line%%:*}"
        text="${match_line#*:}"

        justified=0
        # Trailing same-line comment?
        if [[ "$text" =~ //.*$JUSTIFICATION_KEYWORDS_RE ]]; then
            justified=1
        fi
        # Preceding comment lines within radius?
        if [[ $justified -eq 0 ]]; then
            start=$(( lineno - JUSTIFICATION_RADIUS ))
            (( start < 1 )) && start=1
            end=$(( lineno - 1 ))
            if (( end >= start )); then
                preceding="$(sed -n "${start},${end}p" "$file" || true)"
                if echo "$preceding" | grep -qE "//.*$JUSTIFICATION_KEYWORDS_RE"; then
                    justified=1
                fi
            fi
        fi

        if [[ $justified -eq 0 ]]; then
            violations+=("$rel:$lineno: $text")
        fi
    done < <(grep -nE "$WEAK_CRYPTO_REGEX" "$file" || true)

done < <(find "$LIB_DIR" -type f -name "*.dart" -print0)

if [[ ${#violations[@]} -gt 0 ]]; then
    echo "FAIL: SP4 (no weak crypto in security paths) — ${#violations[@]} unjustified use(s):"
    for v in "${violations[@]}"; do
        echo "  $v"
    done
    echo
    echo "Each weak-crypto call (SHA-1 / MD5) must carry an adjacent comment"
    echo "naming a non-security purpose, e.g.:"
    echo "    // Non-security: cache key only (collision resistance not required)"
    echo "    final key = sha1.convert(utf8.encode(query)).toString();"
    exit 1
fi

echo "PASS: SP4 (no weak crypto in security paths) — 0 unjustified uses in lib/"
exit 0
