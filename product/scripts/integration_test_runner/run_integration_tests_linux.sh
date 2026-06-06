#!/usr/bin/env bash
# Run integration tests on the Linux desktop target inside the devcontainer,
# headlessly, via the X virtual framebuffer (REQ-PROC-054 AC-06).
#
# This is the LLM-autonomous integration-test path. It replaces the legacy
# Windows-only run_individual_integration_tests.ps1, which is retained only for
# manual Windows-target operations on the developer's host.
#
# Discovery is file-based: every integration test lives in
# integration_test/flows/ as *_test.dart and is invoked one file at a time
# (per-file invocation is the documented-stable pattern; running the whole
# integration_test/ directory in a single dart entry point is the historically
# unstable mode).
#
# Usage (from the flutter_app/ project root):
#     bash scripts/integration_test_runner/run_integration_tests_linux.sh
#     bash scripts/integration_test_runner/run_integration_tests_linux.sh integration_test/flows/onboarding_role_selection_flow_test.dart
#
# Exit codes:
#     0  every discovered test file passed
#     1  at least one test file failed, or no test files found
#
# Note: the first invocation builds the Linux desktop target (a few minutes);
# subsequent runs are cached. If a build fails at the CMake install step with
# "Permission denied" copying to /usr/local/flutter_app, a stale CMakeCache is
# pinning the install prefix — run `rm -rf build/linux` and retry.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/test_outputs"
FLOWS_DIR="integration_test/flows"

mkdir -p "${OUTPUT_DIR}"

if ! command -v xvfb-run >/dev/null 2>&1; then
    echo "ERROR: xvfb-run not found. Run scripts/dev_environment/install_linux_desktop_deps.sh first." >&2
    exit 1
fi

# Collect the test files: either the explicit argument list, or every
# *_test.dart under integration_test/flows/.
if [ "$#" -gt 0 ]; then
    TEST_FILES=("$@")
else
    mapfile -t TEST_FILES < <(find "${FLOWS_DIR}" -maxdepth 1 -name '*_test.dart' -type f 2>/dev/null | sort)
fi

if [ "${#TEST_FILES[@]}" -eq 0 ]; then
    echo "ERROR: no integration test files found under ${FLOWS_DIR}/." >&2
    exit 1
fi

echo "Found ${#TEST_FILES[@]} integration test file(s) to run on the Linux desktop target."

FAILED=0
for test_file in "${TEST_FILES[@]}"; do
    log_name="$(basename "${test_file}" .dart).log"
    log_path="${OUTPUT_DIR}/${log_name}"
    echo "----------------------------------------------------------------------"
    echo "Running: ${test_file}"
    echo "Log:     ${log_path}"
    if xvfb-run -a flutter test "${test_file}" -d linux >"${log_path}" 2>&1; then
        echo "RESULT:  PASS"
    else
        echo "RESULT:  FAIL (see ${log_path})"
        FAILED=1
    fi
done

echo "----------------------------------------------------------------------"
if [ "${FAILED}" -ne 0 ]; then
    echo "One or more integration test files failed."
    exit 1
fi
echo "All integration test files passed."
exit 0
