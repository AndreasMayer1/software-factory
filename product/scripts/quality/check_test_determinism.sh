#!/usr/bin/env bash
# REQ-PROC-002 AC-04 (TQ4) — test suite passes under random ordering AND on
# 10 consecutive identical runs. Detects two orthogonal flake classes:
#
#   1. Order-dependent flakes (Phase 1): one run of `flutter test` with
#      `--test-randomize-ordering-seed=<seed>`. The seed is generated locally
#      and printed so any failure is exactly reproducible.
#   2. Non-deterministic flakes (Phase 2): 10 consecutive default-order runs.
#      A test that passes on some runs and fails on others reveals clock /
#      race / shared-state dependence even when the order is fixed.
#
# Cadence: per-release-candidate (not per-change). Per-change would cost
# roughly 11× a normal test run; the release pre-flight is the right
# checkpoint.
#
# Usage:
#     scripts/quality/check_test_determinism.sh
#
# Environment:
#     LOG_DIR        Output directory for per-run logs.
#                    Default: /tmp/check_test_determinism
#     CONSECUTIVE    Number of consecutive default-order runs (Phase 2).
#                    Default: 10 (the value mandated by REQ-PROC-002 AC-04).
#     SEED           Optional fixed seed for Phase 1. If unset, a random
#                    32-bit value is generated. Set this to reproduce a
#                    prior Phase-1 failure.
#
# Exit codes:
#     0  all 1+CONSECUTIVE runs passed
#     1  one or more runs failed (suite is not deterministic)
#     2  invocation error (flutter missing, lib/ tree missing, etc.)

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

LOG_DIR="${LOG_DIR:-/tmp/check_test_determinism}"
CONSECUTIVE="${CONSECUTIVE:-10}"

if ! command -v flutter >/dev/null 2>&1; then
    echo "ERROR: 'flutter' not on PATH" >&2
    exit 2
fi
if [[ ! -d "${PROJECT_ROOT}/test" ]]; then
    echo "ERROR: ${PROJECT_ROOT}/test not found" >&2
    exit 2
fi

mkdir -p "$LOG_DIR"

# Phase-1 seed: prefer a caller-supplied SEED for reproduction; otherwise
# generate a 30-bit value by combining two $RANDOM draws (each is 15-bit).
if [[ -z "${SEED:-}" ]]; then
    SEED=$(( (RANDOM << 15) | RANDOM ))
fi

_extract_failure_lines() {
    local log="$1"
    # `flutter test` failure markers: lines starting with NN:NN +P -F (the -F
    # is the loss counter), `Some tests failed.`, and `Expected:`/`Actual:`
    # diff blocks. We cap to 80 lines so one runaway test doesn't drown out
    # the summary.
    grep -nE '(^[0-9]+:[0-9]+ .* -[1-9])|(^Some tests failed\.)|(^Expected:)|(^Actual:)|(^  Which:)|(EXCEPTION CAUGHT BY)|(FAILED:)' "$log" \
        | head -80 || true
}

overall_rc=0
phase1_log="${LOG_DIR}/phase1_random_seed_${SEED}.log"

echo "==================================================================="
echo "Phase 1/2 — random order, seed=${SEED}"
echo "==================================================================="
echo "  log: ${phase1_log}"
set +e
( cd "$PROJECT_ROOT" && flutter test --test-randomize-ordering-seed="$SEED" ) \
    >"$phase1_log" 2>&1
phase1_rc=$?
set -e

if (( phase1_rc != 0 )); then
    echo "FAIL: Phase 1 — random-order run exited ${phase1_rc} (seed=${SEED})"
    echo "  --- failure excerpt (${phase1_log}) ---"
    _extract_failure_lines "$phase1_log" | sed 's/^/    /'
    echo
    echo "  Reproduce:"
    echo "    cd ${PROJECT_ROOT} && flutter test --test-randomize-ordering-seed=${SEED}"
    echo
    overall_rc=1
else
    echo "PASS: Phase 1 — random-order run (seed=${SEED})"
fi

echo
echo "==================================================================="
echo "Phase 2/2 — ${CONSECUTIVE} consecutive default-order runs"
echo "==================================================================="

phase2_failures=()
for ((i = 1; i <= CONSECUTIVE; i++)); do
    log="${LOG_DIR}/phase2_consec_$(printf '%02d' "$i").log"
    echo "  [${i}/${CONSECUTIVE}] flutter test"
    set +e
    ( cd "$PROJECT_ROOT" && flutter test ) >"$log" 2>&1
    rc=$?
    set -e
    if (( rc != 0 )); then
        echo "    FAIL — exit ${rc}; log: ${log}"
        phase2_failures+=("$i:$log")
    fi
done

if (( ${#phase2_failures[@]} > 0 )); then
    overall_rc=1
    echo
    echo "FAIL: Phase 2 — ${#phase2_failures[@]}/${CONSECUTIVE} run(s) failed"
    for entry in "${phase2_failures[@]}"; do
        idx="${entry%%:*}"
        log="${entry#*:}"
        echo "  --- run ${idx} failure excerpt (${log}) ---"
        _extract_failure_lines "$log" | sed 's/^/    /'
        echo
    done
    echo "  A flake that appears on only some of N identical runs indicates"
    echo "  non-determinism (clock/race/shared-state). The order is fixed in"
    echo "  Phase 2; investigate the named test for state that leaks across"
    echo "  runs or for wall-clock / random dependence."
else
    echo "PASS: Phase 2 — ${CONSECUTIVE}/${CONSECUTIVE} consecutive runs"
fi

echo
echo "==================================================================="
echo "SUMMARY"
echo "==================================================================="
total=$(( 1 + CONSECUTIVE ))
if (( overall_rc == 0 )); then
    passed=$total
else
    p1=$(( phase1_rc == 0 ? 1 : 0 ))
    p2=$(( CONSECUTIVE - ${#phase2_failures[@]} ))
    passed=$(( p1 + p2 ))
fi
echo "  ${passed}/${total} runs passed (1 random seed=${SEED} + ${CONSECUTIVE} consecutive)"
echo "  logs: ${LOG_DIR}/"

exit "$overall_rc"
