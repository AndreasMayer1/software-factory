#!/usr/bin/env bash
# REQ-PROC-046 (DCM replacement) — type-naming gate.
#
# Replaces DCM's `prefer-correct-type-name`. Every `class Foo` declaration
# under `lib/` must satisfy:
#
#   ^[A-Z][a-zA-Z0-9]*((Event)|(Failure)|(Bloc)|(State)|(Repository)|
#                      (Service)|(UseCase)|(Entity)|(ValueObject))?$
#
# Generated files (*.g.dart, *.freezed.dart) are skipped. Enum and mixin
# declarations are NOT flagged (their declaration keywords differ).
#
# Usage:
#     scripts/quality/check_type_naming.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  every class name conforms
#     1  one or more class names violate the regex
#     2  invocation error
set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

parse_exclude_arg "$@"
load_exclude_patterns

SCAN_ROOT="${PROJECT_ROOT}/lib"
if [[ ! -d "$SCAN_ROOT" ]]; then
    echo "NOTICE: $SCAN_ROOT does not exist; nothing to scan." >&2
    exit 0
fi

# Acceptable name shape (with or without an approved suffix).
NAME_RE='^[A-Z][a-zA-Z0-9]*((Event)|(Failure)|(Bloc)|(State)|(Repository)|(Service)|(UseCase)|(Entity)|(ValueObject))?$'

# Match the start of a class declaration. Handles optional modifiers
# (abstract / sealed / final / base / interface / mixin-class). The first
# capture group is the class name.
DECL_RE='^[[:space:]]*(abstract |sealed |final |base |interface )?(mixin )?class[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)'

violations=0
while IFS= read -r -d '' file; do
    rel="${file#${PROJECT_ROOT}/}"
    if [[ "$file" == *.g.dart || "$file" == *.freezed.dart || "$file" == *.config.dart ]]; then
        continue
    fi
    if is_excluded "$rel"; then
        continue
    fi
    line_no=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        ((line_no++))
        if [[ "$line" =~ $DECL_RE ]]; then
            name="${BASH_REMATCH[3]}"
            # Private classes (underscore prefix) are standard Dart convention — skip.
            [[ "$name" == _* ]] && continue
            if ! [[ "$name" =~ $NAME_RE ]]; then
                echo "$rel:$line_no: class name '$name' violates type-name regex"
                ((violations++))
            fi
        fi
    done < "$file"
done < <(find "$SCAN_ROOT" -type f -name '*.dart' -print0)

if (( violations > 0 )); then
    echo
    echo "FAIL: $violations type-name violation(s)."
    echo "Accepted suffixes: Event, Failure, Bloc, State, Repository, Service,"
    echo "UseCase, Entity, ValueObject (or no suffix; PascalCase mandatory)."
    exit 1
fi

echo "PASS: every class name matches the type-name regex."
exit 0
