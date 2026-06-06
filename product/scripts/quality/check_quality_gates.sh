#!/usr/bin/env bash
# Aggregate runner for REQ-PROC-052 / REQ-PROC-046 quality gates.
#
# Runs each gate in sequence, collects pass/fail per gate, prints a summary,
# and exits non-zero if any gate failed. Each gate's full output is streamed
# live so the developer can see the violations as they appear.
#
# Fifteen gates:
#   G1  flutter analyze   (source hygiene — analyzer + lint rules)
#   G3  flutter test      (test correctness — skipped with --quick)
#   AC-06 error-handling  (bare catch, non-Error throws)
#   SP1–SP4               (privacy/security: no-network-io, no-telemetry,
#                          no-hardcoded-secrets, no-weak-crypto)
#   AC-11, AC-12          (suppression-justification, no-debug-artifacts)
#   AC-02, type-naming, arch-imports, no-direct-styling, test-smells,
#   folder-taxonomy       (DCM-replacement gates from TASK-PROC-046-14)
#
# Usage:
#     scripts/quality/check_quality_gates.sh [--exclude-paths <file>] [--quick]
#
# Flags:
#     --exclude-paths <file>   Path to exclusions file (forwarded to each gate)
#     --quick                  Skip flutter test (G3) for fast local runs
#
# Exit codes:
#     0  all gates passed
#     1  one or more gates failed
#     2  invocation error (a gate script is missing or unexpected rc)

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect --quick locally; strip it from ARGS so gate scripts don't receive it.
# (Python gates use argparse and would error on an unknown flag.)
QUICK=0
ARGS=()
for _arg in "$@"; do
    if [[ "$_arg" == "--quick" ]]; then
        QUICK=1
    else
        ARGS+=("$_arg")
    fi
done

GATES=(
    "SP1 no-network-io      | check_no_network_io.sh"
    "SP2 no-telemetry-sdks  | check_no_telemetry_sdks.py"
    "SP3 no-hardcoded-secret| check_no_hardcoded_secrets.sh"
    "SP4 no-weak-crypto     | check_weak_crypto.sh"
    "AC11 suppression-just. | check_suppression_justification.sh"
    "AC12 no-debug-artifacts| check_no_debug_artifacts.sh"
    "AC06 error-handling    | check_ac06_error_handling.py"
    "AC02 complexity        | check_complexity.py"
    "type-naming            | check_type_naming.sh"
    "arch-imports           | check_architectural_imports.sh"
    "no-direct-styling      | check_no_direct_styling.sh"
    "test-smells            | check_test_smells.py"
    "folder-taxonomy        | check_folder_taxonomy.sh"
    "artifact-token-resolve | check_artifact_token_resolve.py"
)

# Per-gate extra arguments appended after the common ARGS.
# Used for flags that only certain gates understand (e.g. --baseline for AC-06).
declare -A GATE_EXTRA_ARGS
GATE_EXTRA_ARGS["check_ac06_error_handling.py"]="--baseline ${SCRIPT_DIR}/ac06_violations_baseline.txt"
GATE_EXTRA_ARGS["check_artifact_token_resolve.py"]="--baseline ${SCRIPT_DIR}/artifact_token_baseline.txt"

results=()
overall=0

# ── G1: flutter analyze ────────────────────────────────────────────────────
# REQ-PROC-046 pass condition is "zero errors / warnings" — info-level issues
# (line length, eol, lint hints) do not constitute a gate failure.
# flutter analyze exits 1 for any issue; we check the output instead.
echo
echo "==================================================================="
echo "GATE: G1 flutter-analyze  (flutter analyze)"
echo "==================================================================="
set +e
_g1_out=$(flutter analyze 2>&1)
_g1_exitcode=$?
set -e
echo "$_g1_out"
# Count lines that are genuine errors or warnings (not info).
_g1_issues=$(echo "$_g1_out" | grep -cE "^  (error|warning) " || true)
if [[ $_g1_issues -gt 0 ]]; then
    results+=("FAIL   G1 flutter-analyze  ($_g1_issues error/warning(s))")
    (( overall < 1 )) && overall=1
elif [[ $_g1_exitcode -ne 0 ]]; then
    # Exit non-zero but no errors/warnings — only infos. Still a pass per REQ-PROC-046.
    results+=("PASS   G1 flutter-analyze  (info-only, no errors/warnings)")
else
    results+=("PASS   G1 flutter-analyze")
fi

# ── Script-based gates ─────────────────────────────────────────────────────
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
        runner=(python3 "$script_path")
    else
        runner=(bash "$script_path")
    fi

    extra_str="${GATE_EXTRA_ARGS[$script_name]:-}"
    if [[ -n "$extra_str" ]]; then
        read -ra extra_arr <<< "$extra_str"
        set +e
        "${runner[@]}" "${ARGS[@]}" "${extra_arr[@]}"
        rc=$?
        set -e
    else
        set +e
        "${runner[@]}" "${ARGS[@]}"
        rc=$?
        set -e
    fi

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

# ── G3: flutter test ──────────────────────────────────────────────────────
echo
echo "==================================================================="
if [[ $QUICK -eq 1 ]]; then
    echo "GATE: G3 flutter-test  (flutter test) [SKIPPED — --quick]"
    echo "==================================================================="
    echo "[quick mode] flutter test skipped. Run without --quick for full gate enforcement."
    results+=("SKIP   G3 flutter-test")
else
    echo "GATE: G3 flutter-test  (flutter test)"
    echo "==================================================================="
    set +e
    flutter test
    _rc=$?
    set -e
    case $_rc in
        0)
            results+=("PASS   G3 flutter-test")
            ;;
        1)
            results+=("FAIL   G3 flutter-test")
            (( overall < 1 )) && overall=1
            ;;
        *)
            results+=("ERR${_rc}  G3 flutter-test")
            overall=2
            ;;
    esac
fi

echo
echo "==================================================================="
echo "QUALITY GATES SUMMARY"
echo "==================================================================="
for r in "${results[@]}"; do
    echo "  $r"
done
echo

if (( overall == 0 )); then
    echo "All quality gates PASSED."
elif (( overall == 1 )); then
    echo "One or more quality gates FAILED. See per-gate output above."
else
    echo "Quality-gate runner encountered an ERROR (missing script or unexpected rc)."
fi

exit $overall
