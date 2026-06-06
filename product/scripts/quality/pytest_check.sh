#!/usr/bin/env bash
# G3 — pytest test runner gate wrapper (REQ-PROC-051 AC-02).
#
# Runs pytest with the collection roots defined in pyproject.toml:
#   scripts/automation/tests  and  scripts/tests
# Uses `uv run` so the pinned venv is used without manual activation.
#
# Exit codes:
#   0  all tests passed
#   1  one or more tests failed
#   2  invocation error (pytest not found, config missing, etc.)

set -u
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v uv &>/dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Run: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 2
fi

set +e
uv run --project "$REPO_ROOT" pytest -q
rc=$?
set -e

case $rc in
    0) exit 0 ;;
    1) exit 1 ;;
    *) exit 2 ;;
esac
