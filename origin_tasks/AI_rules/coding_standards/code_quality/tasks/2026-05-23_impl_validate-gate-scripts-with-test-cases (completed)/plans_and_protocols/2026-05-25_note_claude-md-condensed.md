# Note: CLAUDE.md back-pressure section condensed

**Date**: 2026-05-25
**Commit**: 6a7a1084

The quality-gates and back-pressure block in CLAUDE.md was condensed from ~113 lines to ~15 lines (487→425 total). Gate tables (G1-G8, TQ1-TQ4, SP1-SP6), bypass mechanism details, five-cycle protocol steps, supporting-docs list, and the proposals mechanism paragraph were removed — they were duplicated with the `verify-quality` skill, the pre-commit hook, and `task-complete`.

CLAUDE.md now points to the `verify-quality` skill for operational details and retains only behavioral rules (no silent acceptance, manual bypass, authority hierarchy, don't-edit-gates, non-obvious-fix capture).

**Relevance to this task**: when validating gate scripts, note that the gate definitions now live exclusively in:
- `verify-quality` SKILL.md (operational procedure)
- `scripts/quality/check_quality_gates.sh` (entry point)
- REQ-PROC-046 / REQ-PROC-002 / REQ-PROC-052 requirements (contract)
- NOT in CLAUDE.md (which only has behavioral rules)
