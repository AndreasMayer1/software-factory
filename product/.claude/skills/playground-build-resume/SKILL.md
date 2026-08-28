---
name: playground-build-resume
description: Re-attach an in-progress build-mode run from the run registry without re-running deploy/seed/snapshot.
tools: [Bash, Read]
model: inherit
---

You re-attach a preserved/in-progress build-mode playground run and resume it. Mirrors
`layer-derivation-resume`, but for `scripts/playground/build.py` runs (REQ-PROC-068 AC-15/16).

## Input (all optional)

- `registry_dir` — durable run-registry dir. Default `<worktree_root>/.playground_runs`
  (`python3 scripts/dev_env/worktree_root.py`).

## Steps

1. **Find a resumable run**:
   ```bash
   python3 scripts/playground/build_resume.py list ${REGISTRY_DIR:+--registry-dir "$REGISTRY_DIR"}
   ```
   - No run with status `running` or `preserved` (and an on-disk workspace) → print
     "No resumable build-mode run." and stop.
   - A `complete` run is done — never re-attach it.

2. **Re-attach (resume)** — reuses the preserved workspace + persisted baseline; SKIPS
   deploy/seed/snapshot (AC-15). No human path-threading — the registry record carries the
   workspace path, jsonl dir, prompt, model, and baseline ref:
   ```bash
   python3 scripts/playground/build_resume.py resume ${REGISTRY_DIR:+--registry-dir "$REGISTRY_DIR"}
   ```
   Prints the run manifest JSON (`completed`, `workspace_preserved`, `harvested_paths`, …).

3. **Surface summary**: the resumed run's session_uuid, workspace path, and whether it completed
   (harvested + discarded) or was preserved again for a later resume.

## Notes

- **Usage-limit needs no action here.** A tree-wide usage limit freezes the inner AND outer
  orchestrators together (`orchestrate.py::rate_limit_sleep`, recomputed from the absolute reset
  time) and both resume after the shared window resets — **no orchestrator change** (AC-16). This
  skill is only for re-attaching after autorun has *stopped* (manual stop / session exhausted),
  not mid-run while autorun is active.
- **Explicit pause** is not built (v1, SOL-02 D6). The documented extension point is writing
  `stop_requested` into the inner copy's `automation/state.json`.
- The completion wait uses `scripts/playground/completion_poll.py` (dynamic interval scaled to
  remaining ChainState units, floor/ceiling) — not a fixed 15-minute poll.
