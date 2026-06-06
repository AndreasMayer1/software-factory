#!/usr/bin/env python3
"""Verify a URL responds 2xx (external-state vocabulary: url_returned_2xx).

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
import urllib.error
import urllib.request

_HTTP_OK_MIN = 200
_HTTP_OK_MAX = 299
_TIMEOUT_SECONDS = 15


def is_2xx(status: int) -> bool:
    """Return True if *status* is in the HTTP 2xx success range."""
    return _HTTP_OK_MIN <= status <= _HTTP_OK_MAX


def fetch_status(url: str) -> int:
    """Return the HTTP status code for *url* (urllib error codes mapped to their status)."""
    try:
        with urllib.request.urlopen(url, timeout=_TIMEOUT_SECONDS) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    status = fetch_status(parser.parse_args().url)
    print(f"{'PASS' if is_2xx(status) else 'FAIL'} — HTTP {status}")
    return 0 if is_2xx(status) else 1


if __name__ == "__main__":
    raise SystemExit(main())
