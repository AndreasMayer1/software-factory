# Protocol: add-simulate-cli

## Execution Log

**2026-04-23** — Inline implementation.

### Files read
- `scripts/task_ordering/ranker.py` — `rank_tasks`, `_enrich_tasks` (mutates in-place)
- `scripts/task_ordering/rules.py` — `load_rules`, `DEFAULT_RULES_PATH`, `Rules`
- `scripts/task_ordering/classifier.py` — `classify_layer`, `UNCLASSIFIED`
- `scripts/task_ordering/defaults.py` — `EXCLUDED_STATUSES`
- `scripts/task_ordering/__init__.py` — public API
- `scripts/next_tasks.py` — `load_tasks` (task scanning), `parse_frontmatter`
- `scripts/task_ordering/validate_rules.py` — CLI pattern reference

### Key design decisions
- `_rank()` deep-copies input before ranking to avoid `_enrich_tasks` mutating shared task dicts
- `next_tasks.load_tasks()` imported at runtime (not part of `task_ordering` package); `_SCRIPTS_DIR` added to `sys.path`
- Exits 0 always (informational, not a gate) per AC spec

### Deliverable
`scripts/task_ordering/simulate.py` — created and smoke tested (same-rules run: 0 shifts, 0 unclassified; exit 0 confirmed).

## 2026-04-23T00:00Z
**Agent**: Main conversation (claude-sonnet-4-6)
**Agent ID**: a12885217c1ff74a2
**Action**: Created `scripts/task_ordering/simulate.py` — dry-run CLI for comparing backlog rankings under old vs proposed rule files
**Outcome**: Pass — smoke test passed (exit 0, correct output, --verbose flag works, missing file falls back gracefully)
**Next Step**: task-complete
