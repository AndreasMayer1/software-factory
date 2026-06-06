---
name: release-status
description: Show where you are in the release workflow
tools: "*"
model: inherit
---

Run `python3 scripts/release/release_readiness.py` from the project root and show the output to the user.

That is all this skill does. The script detects the current release stage (0–5) and recommends the next step.
