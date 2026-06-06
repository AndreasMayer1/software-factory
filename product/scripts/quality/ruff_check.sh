#!/usr/bin/env bash
# G1 — ruff lint gate wrapper (REQ-PROC-051 AC-02).
#
# Runs ruff check over scripts/ using the pyproject.toml config at repo root.
# Uses `uv run` so the pinned venv is used without manual activation.
#
# Exit codes:
#   0  no lint violations
#   1  one or more violations
#   2  invocation error (ruff not found, config missing, etc.)

set -u
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v uv &>/dev/null; then
    # Fallback: try the standard install location
    export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Run: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 2
fi

set +e
uv run --project "$REPO_ROOT" ruff check "$REPO_ROOT/scripts/"
rc=$?
set -e

case $rc in
    0) exit 0 ;;
    1) exit 1 ;;
    *) exit 2 ;;
esac
