# Guideline updates from TASK-PROC-068-36

Added one new anti-pattern entry to `doc/python/anti_patterns.md`:

**"Auto-deriving 'one level above my own root' without checking for a nested repo"** — documents the
`scripts/dev_env/worktree_root.py` nested-repo escape found by `scripts/util/path_anchor_audit.py`
during this task (see `2026-07-21_01_plan_audit-findings-and-guard-design.md` for the full incident).
Follows the file's existing incident → rule → cost structure.

No README sync needed — `anti_patterns.md` is an existing file already listed in `doc/python/README.md`;
no new file was added, no folder was added/removed.

`path_anchor_audit.py` itself was NOT documented as a new "Use Scripts, Not Grep" entry in CLAUDE.md
Section 11 (per `claude-write-script`'s Rule 5 litmus test) — it's a fixed compliance check invoked via
pytest, not something an LLM would reach for ad-hoc via grep in place of.
