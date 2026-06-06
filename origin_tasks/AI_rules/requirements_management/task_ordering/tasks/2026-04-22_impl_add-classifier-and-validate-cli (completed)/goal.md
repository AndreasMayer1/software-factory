---
task_id: TASK-PROC-042-05
type: impl
parent_requirement: REQ-PROC-042
urgency: 3
urgency_reason: U3-CTX
impact: 4
impact_reason: I4-QUAL
status: completed
effort: M
created: 2026-04-22
started: 2026-04-22
completed: 2026-04-22
session_completed_at: 2026-04-22T17:51:44Z
session_id: 6cff4323-1011-4892-a25c-7d258731c65d
session_account: web
after: [TASK-PROC-042-02, TASK-PROC-042-04]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05, AC-07]
  sections: []
scope_description: "Add scripts/task_ordering/classifier.py implementing classify_layer() — path-glob + frontmatter matching in declaration order, first match wins; add scripts/task_ordering/validate_rules.py CLI that schema-checks the rule file and exits non-zero on errors"
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: f65d3fca
  file: ../requirements.md
---

# Goal: Add Layer Classifier and Validate CLI

## Objective

Implement `scripts/task_ordering/classifier.py` with the `classify_layer()` function that maps a task (path + frontmatter) to its layer using the rule file. Also add the `scripts/task_ordering/validate_rules.py` CLI for schema-checking the rule file. This is Phase C preparation — the classifier is wired but the ranking signal is not yet active (that is TASK-PROC-042-06).

## Requirements Summary

AC-05 requires layer inference from folder path without LLM at ordering time. AC-07 requires schema validation with visible warning on failure.

For complete requirements at task creation time:
```
git show f65d3fca:requirements_tasks/process/AI_rules/requirements_management/task_ordering/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- `classifier.py`: `classify_layer(task, rules)` — iterates layers in declaration order, applies path_glob + frontmatter predicates, returns first matching layer or fallback sentinel
- Path normalization: always use forward slashes (Windows compatibility)
- `_matches(task, rule)` helper: handles `path_glob`, `frontmatter`, `scope_description_contains` predicates
- `validate_rules.py` CLI: loads rule file via `rules.py`, checks schema constraints (layer order uniqueness, no duplicate names, glob sanity check), exits 0 on pass / non-zero on failure with clear error messages
- Validation rules from Part 5.4 of the design: schema version, layer order uniqueness, sparsity recommendation, dependency cycle check

### Out of Scope
- Wiring `classify_layer()` into the ranker (TASK-PROC-042-06)
- `simulate.py` (TASK-PROC-042-07)

## Acceptance Criteria

- [ ] `classify_layer()` correctly classifies all current open tasks when run manually
- [ ] First-match-wins order matches layer declaration order in rule file
- [ ] `validate_rules.py` exits 0 on the current rule file
- [ ] `validate_rules.py` exits non-zero with clear error for: duplicate layer order, missing required fields, invalid path_glob (matches zero folders)
- [ ] Path separators normalized to forward slashes

## Dependencies

| Dependency | Notes |
|---|---|
| TASK-PROC-042-02 | Rule file must exist for classification to work |
| TASK-PROC-042-04 | Rules loader must exist |

## Notes

Full design reference:
- Part 3.2: `classifier.py` pseudocode
- Part 5.4: Validation rules (for validate_rules.py)
