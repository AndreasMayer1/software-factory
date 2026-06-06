# Plan: Cross-Reference Detection Mechanism

**Task**: TASK-PROC-045-07
**Date**: 2026-05-25
**Agent**: session e28d42b1

## Approach: Inline with mandatory skill invocations

All deliverables produced in the main session via required skill calls:
- `claude-write-script` for script + tests
- `claude-modify-skill` for requ-explore update

## Deliverables

### 1. `scripts/requirements/check_cross_refs.py` (tier B)

**Input**: `<path-to-requirements.md>` + optional `--terms TERM1 TERM2 ...`

**Process**:
1. Parse YAML frontmatter → `id`, `after:`, `blocks:`
2. Parse `## Related Requirements` body section → additional REQ-IDs to exclude
3. Collect excluded IDs = self + after + blocks + related
4. Derive 2-4 search terms from requirement title + first paragraph (or use `--terms`)
5. `grep -rl --include=requirements.md <term> requirements_tasks/{functional,non-functional,process}/`
6. For each hit: extract REQ-ID from frontmatter; skip if in excluded set or is self
7. Output: `JSON [{id, path, matched_terms, snippet}]`

**Exit codes**: 0 = success (including zero gaps), 1 = script error

**Tier**: B (reusable — called by requ-explore and task-derive-from-requ)

### 2. `scripts/tests/test_check_cross_refs.py`

Coverage:
- `_extract_req_id`: valid file, missing file, no id field, malformed YAML
- `_get_excluded_ids`: self excluded, after chain, blocks chain, Related Requirements section
- `_derive_search_terms`: title words, fallback to paragraph, max 4, stop word filtering
- `main()` integration: missing target (exit 1), malformed YAML (exit 1), no id (exit 1), explicit --terms, zero matches, matches with exclusion

### 3. requ-explore Phase 1.4 update (via `claude-modify-skill`)

Replace the inline keyword-grep prose in Phase 1.4 with:
```
Run: python3 scripts/requirements/check_cross_refs.py <path-to-requirements.md>
```
Preserve user-facing behavior (surface gaps for user to decide).

### 4. Output format documentation

Documented in script docstring for TASK-PROC-058-03 consumer.

## JSON Output Schema

```json
[
  {
    "id": "REQ-FUNC-001",
    "path": "requirements_tasks/functional/.../requirements.md",
    "matched_terms": ["term1", "term2"],
    "snippet": "first matching line excerpt (max 120 chars)"
  }
]
```

Empty list `[]` = no unlinked related requirements found.

## Notes

- Use `read_frontmatter` from `scripts/util/yaml_frontmatter.py` (G4 compliant)
- grep uses `--include=requirements.md` to scope to requirement files only
- `subprocess.run` with `capture_output=True, timeout=30`
- CLAUDE.md Section 11: Rule 2 applies — general-purpose analytical capability → add row
