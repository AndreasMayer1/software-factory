#!/usr/bin/env bash
# G2 — mypy type-check gate wrapper (REQ-PROC-051 AC-02).
#
# Runs mypy over scripts/ using the pyproject.toml config at repo root.
# TIER A modules (scripts.automation.orchestrate) are checked with strict=true;
# TIER B/C use the lenient baseline. See pyproject.toml [[tool.mypy.overrides]].
# Uses `uv run` so the pinned venv is used without manual activation.
#
# Exit codes:
#   0  no type errors
#   1  one or more type errors
#   2  invocation error (mypy not found, config missing, etc.)

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
uv run --project "$REPO_ROOT" mypy --config-file "$REPO_ROOT/pyproject.toml" "$REPO_ROOT/scripts/"
rc=$?
set -e

case $rc in
    0) exit 0 ;;
    1) exit 1 ;;
    *) exit 2 ;;
esac
