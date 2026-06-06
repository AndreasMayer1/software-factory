#!/usr/bin/env bash
# Aggregate runner for REQ-PROC-051 Python quality gates.
#
# Mirrors the shape of check_quality_gates.sh (Dart-side) — one pattern for
# both language stacks. Runs each gate as a subprocess, collects per-gate exit
# codes, prints a summary, and exits with the union.
#
# Usage:
#     scripts/quality/check_python_gates.sh
#
# Exit codes:
#     0  all gates passed
#     1  one or more gates failed
#     2  invocation error (a gate script is missing or non-executable)

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v uv &>/dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
fi

GATES=(
    "G1 lint           | ruff_check.sh"
    "G2 type           | mypy_check.sh"
    "G3 tests          | pytest_check.sh"
    "G4 no-handrolled  | check_no_handrolled_yaml.py"
    "G5 print-discip.  | check_print_discipline.py"
)

results=()
overall=0

for entry in "${GATES[@]}"; do
    label="${entry%%|*}"
    label="${label%"${label##*[![:space:]]}"}"  # rtrim
    script_name="${entry##*|}"
    script_name="${script_name#"${script_name%%[![:space:]]*}"}"  # ltrim
    script_path="${SCRIPT_DIR}/${script_name}"

    echo
    echo "==================================================================="
    echo "GATE: $label  ($script_name)"
    echo "==================================================================="

    if [[ ! -f "$script_path" ]]; then
        echo "ERROR: gate script missing: $script_path" >&2
        results+=("ERROR  $label")
        overall=2
        continue
    fi

    if [[ "$script_path" == *.py ]]; then
        runner=(uv run --project "${SCRIPT_DIR}/../.." python3 "$script_path")
    else
        runner=(bash "$script_path")
    fi

    set +e
    "${runner[@]}"
    rc=$?
    set -e

    case $rc in
        0)
            results+=("PASS   $label")
            ;;
        1)
            results+=("FAIL   $label")
            (( overall < 1 )) && overall=1
            ;;
        *)
            results+=("ERR$rc  $label")
            overall=2
            ;;
    esac
done

echo
echo "==================================================================="
echo "PYTHON GATES SUMMARY"
echo "==================================================================="
for r in "${results[@]}"; do
    echo "  $r"
done
echo

if (( overall == 0 )); then
    echo "All Python quality gates PASSED."
elif (( overall == 1 )); then
    echo "One or more Python quality gates FAILED. See per-gate output above."
else
    echo "Python gate runner encountered an ERROR (missing script or unexpected rc)."
fi

exit $overall
