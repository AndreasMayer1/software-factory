---
task_id: TASK-PROC-042-04
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
effort: S
created: 2026-04-22
completed: 2026-04-22
session_completed_at: 2026-04-22T17:38:37Z
started: 2026-04-22
session_id: 57d450dc-ff18-46c3-b73f-fe04c9fb8efd
session_account: gmail
after: [TASK-PROC-042-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-07]
  sections: []
scope_description: "Add scripts/task_ordering/rules.py that loads .claude/task_ordering_rules.yaml; falls back to hardcoded defaults with a visible stderr warning when file is absent or malformed; schema version check included"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Add Rules Loader with Fallback

## Objective

Implement `scripts/task_ordering/rules.py` — the YAML rule file loader. When `.claude/task_ordering_rules.yaml` exists and is valid, the engine uses it. When the file is absent or malformed, the engine falls back to `defaults.py` with a visible stderr warning. This is Phase B of the incremental migration.

## Requirements Summary

AC-07 requires the engine to validate the rule file on load and fall back gracefully. At this phase, the loaded rules are not yet used for ranking (that comes in TASK-PROC-042-05/06) — this task only implements the load/validate/fallback mechanism.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `Rules` dataclass with fields: `schema_version`, `layers`, `special_flags`, `ranking_signals`, `dependency_heuristics`, `fallback`
- `load_rules(path)` function: loads YAML, validates schema version, returns `Rules`
- On parse error or missing file: print warning to stderr, return `hardcoded_rules()` from defaults.py
- Schema version mismatch: warn and fall back (do not crash)
- `_normalize(data)` helper to map raw YAML dict to `Rules` fields

### Out of Scope
- Actually using the loaded rules for classification or ranking (TASK-PROC-042-05)
- `validate_rules.py` CLI (TASK-PROC-042-05)

## Acceptance Criteria

- [ ] `scripts/task_ordering/rules.py` implements `load_rules()` and `Rules` dataclass
- [ ] Missing rule file → falls back silently with stderr warning
- [ ] Malformed YAML → falls back with stderr warning, does not raise exception
- [ ] Wrong `schema_version` → warns and falls back
- [ ] `next_tasks.py` behavior unchanged (rules loaded but not yet used in ranking)

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-03 | Module structure must exist before rules.py can be added |

## Notes

Full design reference: Part 3.3 (Rule file loading and validation pseudocode)
