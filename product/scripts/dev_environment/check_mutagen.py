#!/usr/bin/env python3
"""Check mutagen sync by writing a probe file and verifying it appears on the beta side.

Output: PASS/FAIL lines to stdout, exits 0 on success, 1 on failure.
"""

# tier: C  # one-shot CLI, no imported callers

import sys
import time
from pathlib import Path

ALPHA = Path("/workspaces/private_mood_tracker/flutter_app")
BETA = Path("/home/vscode/windows_mirror")
PROBE_NAME = ".mutagen_probe_check"
TIMEOUT_SECONDS = 60


def main() -> int:
    alpha_probe = ALPHA / PROBE_NAME
    beta_probe = BETA / PROBE_NAME

    try:
        alpha_probe.write_text("mutagen-check")
    except OSError as e:
        print(f"FAIL  could not write probe file: {e}")
        return 1

    print(f"Wrote probe to {alpha_probe}, waiting up to {TIMEOUT_SECONDS}s...")

    deadline = time.monotonic() + TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if beta_probe.exists():
            elapsed = TIMEOUT_SECONDS - (deadline - time.monotonic())
            print(f"PASS  probe appeared on beta side in ~{elapsed:.1f}s")
            alpha_probe.unlink(missing_ok=True)
            beta_probe.unlink(missing_ok=True)
            return 0
        time.sleep(0.5)

    alpha_probe.unlink(missing_ok=True)
    print(f"FAIL  probe did not appear on beta side within {TIMEOUT_SECONDS}s")
    return 1


if __name__ == "__main__":
    sys.exit(main())
