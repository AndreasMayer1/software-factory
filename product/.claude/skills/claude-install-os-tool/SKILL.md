---
name: claude-install-os-tool
description: Install OS-level tool (apt/brew/npm -g); devcontainer-aware
tools: [Bash, Read, Edit]
model: inherit
---

You install an OS-level package (apt, pip --system, brew, npm -g, etc.) safely in any environment.

## Steps

1. **Detect environment**
   ```bash
   python scripts/util/find_devcontainer.py
   ```
   - Exit 0 → prints `.devcontainer/` path → **devcontainer step required** (continue to step 2)
   - Exit 1 → no devcontainer → skip to step 3

2. **Update devcontainer.json** (only if step 1 found a devcontainer)
   - Read the `devcontainer.json` at the path returned above
   - Add the tool installation to **one** of:
     - `features` — preferred for standard tools (e.g. Python, Node, Docker CLI)
     - `postCreateCommand` — for custom/non-feature installs
   - Do **not** add to both; features take priority
   - Tell the user: "Added to devcontainer.json — rebuild the container to make this permanent."

3. **Install the tool**
   Run the installation command provided by the user.

4. **Verify**
   Run a version check (e.g. `python --version`, `node --version`) to confirm success.

## Decision: features vs postCreateCommand

| Situation | Use |
|-----------|-----|
| Tool exists in [Dev Container Features catalog](https://containers.dev/features) | `features` |
| Custom script or multi-step install | `postCreateCommand` |
| Already in `postCreateCommand` (append, don't duplicate) | `postCreateCommand` |
