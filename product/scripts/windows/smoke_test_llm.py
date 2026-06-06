#!/usr/bin/env python3
"""
smoke_test_llm.py — LLM visual smoke test for the Windows release binary.

Launches the Windows release binary, waits for startup, captures a screenshot,
sends it to the Claude API for a visual pass/fail verdict.

Advisory only — exits 0 on PASS, exits 1 on FAIL or error.

Requirements:
  pip install anthropic pillow
  ANTHROPIC_API_KEY environment variable must be set.

Run from the project root on the Windows host (not inside WSL2).

Output:
    Prints the LLM verdict (PASS or FAIL with rationale) to stdout. The captured screenshot path is also reported. Exit 0 on PASS.
"""

# tier: C  # Windows-host smoke-test CLI; no in-tree Python imports

import base64
import io
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import anthropic  # type: ignore[import-not-found]  # anthropic is an optional runtime dep (Windows-only smoke test); not installed in lint env
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    from PIL import (  # type: ignore[import-not-found]  # PIL is an optional runtime dep (Windows-only smoke test); not installed in lint env
        ImageGrab,
    )
except ImportError:
    print("ERROR: pillow package not installed. Run: pip install pillow")
    sys.exit(1)

from find_project_root import find_project_root as _find_project_root  # type: ignore[import-not-found]  # noqa: I001  # resolved at runtime on Windows host via co-located module

PROJECT_ROOT: Path = _find_project_root()
RELEASE_EXE = PROJECT_ROOT / "build" / "windows" / "x64" / "runner" / "Release" / "private_mood_tracker.exe"
STARTUP_WAIT_SECONDS = 6
MODEL = "claude-haiku-4-5-20251001"

VISION_PROMPT = (
    "This is a screenshot of a Flutter mood tracker desktop app after launch on Windows. "
    "The app is called 'Private Mood Tracker'. "
    "Respond with exactly 'PASS' on the first line if:\n"
    "  - The app window is visible and not blank\n"
    "  - No error dialog, crash report, or white/black empty screen is shown\n"
    "  - The app shows either an onboarding screen, a role selection screen, or a main screen\n"
    "Respond with 'FAIL: <reason>' on the first line if:\n"
    "  - The screen is blank or black\n"
    "  - An error dialog or crash report is visible\n"
    "  - The app window is not visible at all\n"
    "  - There is obvious visual corruption (garbled UI, overlapping elements that indicate a render crash)\n"
    "After the first line, optionally add one sentence describing what you see."
)


def find_release_exe() -> Path:
    """Locate the release executable. Searches common name variants."""
    candidates = [
        RELEASE_EXE,
        PROJECT_ROOT / "build" / "windows" / "x64" / "runner" / "Release" / "mood_tracker.exe",
    ]
    # Also search for any .exe in the Release folder
    release_dir = PROJECT_ROOT / "build" / "windows" / "x64" / "runner" / "Release"
    if release_dir.exists():
        for exe in release_dir.glob("*.exe"):
            if exe not in candidates:
                candidates.append(exe)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return RELEASE_EXE  # Return primary path even if missing (error will be reported below)


def take_screenshot() -> str:
    """Capture the primary screen and return as base64-encoded PNG."""
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode()


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    exe_path = find_release_exe()
    if not exe_path.exists():
        print(f"ERROR: Release executable not found: {exe_path}")
        print("       Run smoke_test_windows.ps1 first to build the release binary.")
        sys.exit(1)

    print(f"Launching: {exe_path}")
    proc = subprocess.Popen([str(exe_path)])

    print(f"Waiting {STARTUP_WAIT_SECONDS}s for app to start...")
    time.sleep(STARTUP_WAIT_SECONDS)

    print("Capturing screenshot...")
    screenshot_b64 = take_screenshot()

    print(f"Sending screenshot to Claude API ({MODEL}) for visual review...")
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screenshot_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": VISION_PROMPT,
                    },
                ],
            }
        ],
    )

    verdict = response.content[0].text.strip()
    first_line = verdict.split("\n")[0].strip()

    print("")
    print(f"LLM verdict: {verdict}")
    print("")

    # Terminate the app
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        pass

    if first_line.upper().startswith("PASS"):
        print("=== LLM SMOKE TEST: PASS ===")
        sys.exit(0)
    else:
        print("=== LLM SMOKE TEST: FAIL ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
