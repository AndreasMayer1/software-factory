# Plan: Add Layer Classifier and Validate CLI

## Approach
Inline implementation — two Python files, mechanical spec-to-code.

## Phase 1: classifier.py

Replace stub. Signature: `classify_layer(task, rules)` where:
- `task` is a dict with at least `path` (str) and optionally frontmatter fields
- `rules` is a `Rules` object from `rules.py`

Algorithm (first-match-wins, declaration order):
1. Normalize path separators to forward slashes
2. For each layer in `rules.layers` (ordered by their position, not by `order` field — YAML preserves insertion order):
   - For each match-rule in `layer["match"]`:
     - If `_matches(task, match_rule)` → return `layer["name"]`
3. Return fallback sentinel (e.g. `"__unclassified__"`)

`_matches(task, rule)` checks:
- `path_glob` — fnmatch against task path (normalized)
- `frontmatter` — dict subset check against task frontmatter fields
- `scope_description_contains` — list of strings, any must be in `scope_description`

## Phase 2: validate_rules.py

CLI: `python3 scripts/task_ordering/validate_rules.py [--rules PATH]`

Checks (Part 5.4 of design):
1. Schema version present and == "1.0"
2. Each layer has required fields: `name`, `order`, `match`
3. Layer `order` values are unique (no duplicates)
4. Layer `name` values are unique
5. Each `path_glob` in match rules matches at least one folder in requirements_tasks/
6. No dependency cycles in `consumes` references (layers referencing non-existent layer names)

Exit 0 on all pass. Exit 1 with clear error messages on any failure.

## Smoke Test
- `python3 -c "from scripts.task_ordering.classifier import classify_layer; print('ok')"` — import check
- `python3 scripts/task_ordering/validate_rules.py` — must exit 0 on current rule file
- Quick classify check on a known task path

## Session
agent: 6cff4323-1011-4892-a25c-7d258731c65d
