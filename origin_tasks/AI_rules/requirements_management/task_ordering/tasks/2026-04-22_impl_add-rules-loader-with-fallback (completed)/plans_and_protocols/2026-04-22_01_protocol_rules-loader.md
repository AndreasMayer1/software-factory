# Protocol: Add Rules Loader with Fallback

## Task
TASK-PROC-042-04 — implement `scripts/task_ordering/rules.py`

## Approach
Inline implementation. Single file. No agents.

## Design
- `Rules` dataclass: schema_version, layers, special_flags, ranking_signals, dependency_heuristics, fallback
- `hardcoded_rules()`: returns minimal valid `Rules` (empty lists, fallback defaults)
- `_normalize(data)`: maps raw YAML dict → Rules
- `load_rules(path=None)`: defaults to `.claude/task_ordering_rules.yaml`; falls back to hardcoded_rules() with stderr warning on any error
- SUPPORTED_SCHEMA_VERSION = "1.0"
- Rules are NOT yet used for ranking (that's TASK-PROC-042-05/06)

## Status
- [x] rules.py implemented
- [x] smoke test passed
- [x] next_tasks.py behavior unchanged

## 2026-04-22T17:37:13Z
**Agent**: Main conversation (task-resolve inline)
**Agent ID**: a5bd528bdd0432b96
**Action**: Implemented scripts/task_ordering/rules.py — Rules dataclass, load_rules(), _normalize(), hardcoded_rules(). All 4 ACs verified via smoke tests.
**Outcome**: Pass — valid file loads correctly, missing file warns+falls back, malformed YAML warns+falls back, wrong schema_version warns+falls back. next_tasks.py output unchanged.
**Next Step**: Run task-complete to mark TASK-PROC-042-04 done and commit.
