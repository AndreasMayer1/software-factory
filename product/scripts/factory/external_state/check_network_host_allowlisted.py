#!/usr/bin/env python3
"""Verify a URL's host is allowlisted (external-state vocabulary:
network_host_allowlisted). Governs web-research / OS-fetch destinations. A host
matches an allowlist entry on exact equality or as a dotted suffix (sub.x.com ⊆ x.com).

Output: 'PASS — ...' / 'FAIL — ...' on stdout; exit 0 pass, 1 fail.
"""

# tier: B  # external-state postcondition validator; referenced by contract quality_criteria

from __future__ import annotations

import argparse
from urllib.parse import urlparse


def host_allowed(url: str, allowlist: list[str]) -> bool:
    """Return True if *url*'s host equals or is a dotted subdomain of an allowlist entry."""
    host = (urlparse(url).hostname or "").lower()
    return any(host == entry.lower() or host.endswith("." + entry.lower()) for entry in allowlist)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("allowlist", nargs="+", help="allowed host(s), e.g. flutter.dev pub.dev")
    args = parser.parse_args()
    ok = host_allowed(args.url, args.allowlist)
    print(f"{'PASS' if ok else 'FAIL'} — host of {args.url} {'in' if ok else 'not in'} allowlist")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
