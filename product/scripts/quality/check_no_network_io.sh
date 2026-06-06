#!/usr/bin/env bash
# REQ-PROC-052 SP1 — no direct network I/O in lib/.
#
# Greps lib/ for forbidden network primitives (HTTP clients, raw sockets,
# WebSockets). Inter-device transfer in this project is QR-only (REQ-FUNC-007),
# so any match in lib/ is a gate failure unless the path is on the exclusion
# list at scripts/quality/exclusions.txt (or a file passed via --exclude-paths).
#
# Usage:
#     scripts/quality/check_no_network_io.sh [--exclude-paths <file>]
#
# Exit codes:
#     0  no matches
#     1  one or more forbidden network-I/O patterns found
#     2  invocation error (lib/ missing, etc.)

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

# Forbidden patterns. Each entry is a fixed string we grep for in *.dart files.
# Patterns chosen to match the import / usage forms an LLM is most likely to
# introduce; tightened over time as false positives surface.
#
# Note: we deliberately do NOT flag bare `import 'dart:io';` — that import
# also brings File, Directory, Platform, stdout, exit, etc., which are all
# legitimate. The gate targets specific *network* surfaces of dart:io.
PATTERNS=(
    "package:http/"
    "package:dio/"
    "package:web_socket_channel"
    "HttpClient("
    "HttpClient.new"
    "HttpServer.bind"
    "HttpServer.bindSecure"
    "Socket.connect"
    "Socket.startConnect"
    "ServerSocket.bind"
    "RawSocket.connect"
    "RawServerSocket.bind"
    "RawDatagramSocket.bind"
    "WebSocket.connect"
    "SecureSocket.connect"
)

violations=()

# Scan only *.dart files, skip generated and exclusion-listed paths.
while IFS= read -r -d '' file; do
    rel="${file#"${PROJECT_ROOT}/"}"
    # Skip generated code by default; if intentional, override via exclusions.txt.
    [[ "$rel" == *".g.dart" ]] && continue
    [[ "$rel" == *".freezed.dart" ]] && continue
    [[ "$rel" == *"/generated/"* ]] && continue
    is_excluded "$rel" && continue

    for pat in "${PATTERNS[@]}"; do
        # -F fixed-string, -n line numbers; suppress no-match exit
        matches=$(grep -nF "$pat" "$file" || true)
        if [[ -n "$matches" ]]; then
            while IFS= read -r m; do
                violations+=("$rel: $m  [pattern: $pat]")
            done <<< "$matches"
        fi
    done
done < <(find "$LIB_DIR" -type f -name "*.dart" -print0)

if [[ ${#violations[@]} -gt 0 ]]; then
    echo "FAIL: SP1 (no network I/O) — ${#violations[@]} match(es) in lib/:"
    for v in "${violations[@]}"; do
        echo "  $v"
    done
    echo
    echo "Either remove the network code or, if the use is legitimate, update"
    echo "REQ-PROC-052 SP1's allow-list and add the path to scripts/quality/exclusions.txt."
    exit 1
fi

echo "PASS: SP1 (no network I/O) — 0 matches in lib/"
exit 0
