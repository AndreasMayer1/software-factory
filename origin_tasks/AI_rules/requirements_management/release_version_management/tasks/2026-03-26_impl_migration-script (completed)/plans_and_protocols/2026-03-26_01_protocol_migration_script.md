# Protocol: Migration Script (target_release → target_package)

## 2026-03-26 14:19
**Agent**: Claude (Sonnet 4.6)
**Agent ID**: main-conversation
**Action**: Implemented `scripts/migrate_target_release_to_package.py` — Python migration script that replaces `target_release` fields with `target_package` fields across `requirements_tasks/`.
**Outcome**: Pass — script created and dry-run tested.

### Implementation Summary
- Parses `requirements_tasks/RELEASE_BACKLOG.md` YAML frontmatter to build version→package mapping
- Handles BOM (`utf-8-sig`) and CRLF line endings (normalizes internally, restores on write)
- Resolution order: (1) exact ref+version match, (2) parent req ID fallback (strips `-04`/`-F6` suffixes), (3) scope-based AC disambiguation using AC ranges in package scope strings (e.g. `"(AC-06–17)"`), (4) version-only fallback
- Top-level `target_package` recalculated as earliest-priority package among trackable items
- `--dry-run` (default) / `--apply` modes
- Migration report: files scanned, changed, fields migrated, errors/warnings

### Dry-Run Results (2026-03-26)
- Files scanned: 310
- Files would change: 41
- Fields would migrate: 283
- Issues: 284 total
  - 178 UNRESOLVABLE: requirements not in RELEASE_BACKLOG.md at that version (legitimate gaps — no package defined yet)
  - 68 AMBIGUOUS: multi-package same ref+version, scope doesn't have AC ranges (e.g. Transfer Encryption vs Storage Security for REQ-FUNC-006 at 0.0.2) — flagged for manual review
  - 38 WARNING: version-only match used (acceptable fallback, single candidate)

### Correctness Verified
- `REQ-FUNC-002 @ 0.0.3` → `"Client Data Entry"` ✓
- `REQ-FUNC-002 @ 0.1.0` → `"Client Input Complete"` ✓
- `REQ-FUNC-007-04 @ 0.0.1 AC-06` → `"Adaptive Scanner Settings"` ✓
- `REQ-FUNC-007-04 @ 0.0.1 AC-18` → `"Reverse DataBeam Spike"` ✓

**Next Step**: User reviews dry-run output, resolves AMBIGUOUS/UNRESOLVABLE cases manually or accepts, then runs `python3 scripts/migrate_target_release_to_package.py --apply`.
