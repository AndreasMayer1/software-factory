#!/usr/bin/env bash
# REQ-PROC-052 SP3 — no hardcoded credentials, API keys, or private keys.
#
# Pattern-scans lib/, test/, integration_test/, pubspec.yaml, and
# analysis_options.yaml for common secret shapes. If `gitleaks` is on PATH it
# is preferred; otherwise a regex set tuned to the most common formats is
# used. False positives are expected; the cost is paid via exclusions.txt.
#
# Usage:
#     scripts/quality/check_no_hardcoded_secrets.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  no matches
#     1  one or more candidate-secret patterns found
#     2  invocation error

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

parse_exclude_arg "$@"
load_exclude_patterns

cd "$PROJECT_ROOT"

# Gitleaks path: if available, defer to it. We still apply our exclusion list
# by passing --no-banner and filtering output afterward.
if command -v gitleaks >/dev/null 2>&1; then
    echo "INFO: using gitleaks for SP3 scan"
    tmp_out="$(mktemp)"
    set +e
    gitleaks detect --no-banner --redact --source "$PROJECT_ROOT" \
        --report-format json --report-path "$tmp_out" >/dev/null 2>&1
    rc=$?
    set -e
    if [[ $rc -eq 0 ]]; then
        echo "PASS: SP3 (no hardcoded secrets) — gitleaks reported 0 findings"
        rm -f "$tmp_out"
        exit 0
    fi
    echo "FAIL: SP3 (no hardcoded secrets) — gitleaks findings:"
    cat "$tmp_out" || true
    rm -f "$tmp_out"
    exit 1
fi

# Fallback: regex set. Each entry is (label | extended-regex). We use grep -E
# with -P-free patterns so it works on busybox/macOS/Linux alike.
PATTERNS=(
    "AWS_ACCESS_KEY|(^|[^A-Z0-9])(AKIA|ASIA)[A-Z0-9]{16}([^A-Z0-9]|\$)"
    "PRIVATE_KEY_PEM|-----BEGIN ((RSA|DSA|EC|OPENSSH|PGP) )?PRIVATE KEY-----"
    "SSH_PRIVATE_KEY|-----BEGIN OPENSSH PRIVATE KEY-----"
    "JWT|eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}"
    "GENERIC_API_KEY|(api[_-]?key|apikey|secret[_-]?key|access[_-]?token)[\"' ]*[:=][\"' ]*[A-Za-z0-9_\\-]{20,}"
    "OAUTH_CLIENT_SECRET|(client[_-]?secret)[\"' ]*[:=][\"' ]*[A-Za-z0-9_\\-]{16,}"
    "GOOGLE_API_KEY|AIza[0-9A-Za-z_\\-]{35}"
    "STRIPE_SECRET|sk_live_[0-9a-zA-Z]{24,}"
    "SLACK_TOKEN|xox[baprs]-[0-9A-Za-z\\-]{10,}"
    "GITHUB_PAT|gh[pousr]_[A-Za-z0-9]{36,}"
)

# Scan targets.
TARGETS=()
[[ -d lib ]] && TARGETS+=("lib")
[[ -d test ]] && TARGETS+=("test")
[[ -d integration_test ]] && TARGETS+=("integration_test")
[[ -f pubspec.yaml ]] && TARGETS+=("pubspec.yaml")
[[ -f analysis_options.yaml ]] && TARGETS+=("analysis_options.yaml")

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    echo "ERROR: no scan targets found (lib/, test/, integration_test/, pubspec.yaml)" >&2
    exit 2
fi

violations=()

for entry in "${PATTERNS[@]}"; do
    label="${entry%%|*}"
    regex="${entry#*|}"

    # grep -rEn: recursive, extended regex, line numbers.
    # Use -I to skip binary files; --include limits to text-y files.
    while IFS= read -r line; do
        # line is "path:lineno:matched-text"
        path="${line%%:*}"
        rest="${line#*:}"
        is_excluded "$path" && continue
        # Skip generated files.
        [[ "$path" == *".g.dart" ]] && continue
        [[ "$path" == *".freezed.dart" ]] && continue
        [[ "$path" == *"/generated/"* ]] && continue
        violations+=("[$label] $path:$rest")
    done < <(grep -rEnI \
                --include="*.dart" --include="*.yaml" --include="*.yml" \
                --include="*.json" --include="*.txt" \
                "$regex" "${TARGETS[@]}" 2>/dev/null || true)
done

if [[ ${#violations[@]} -gt 0 ]]; then
    echo "FAIL: SP3 (no hardcoded secrets) — ${#violations[@]} candidate match(es):"
    for v in "${violations[@]}"; do
        echo "  $v"
    done
    echo
    echo "Each match is a *candidate*; review each one. If it is a fixture"
    echo "string that resembles a credential but is obviously synthetic"
    echo "(e.g. 'sk-test-XXXXXXXX'), add the file path to scripts/quality/exclusions.txt."
    exit 1
fi

echo "PASS: SP3 (no hardcoded secrets) — 0 candidate matches"
exit 0
