# Quality Audit Report — TASK-PROC-030-09

**Date**: 2026-04-03
**Files audited**:
1. `scripts/sync_task_packages.py` (new script)
2. `.claude/skills/requ-explore/skill.md` (Phase 2.4 note 5)

---

## Check 1: No Forbidden Imports

**Result**: PASS

Imports used: `argparse`, `os`, `re`, `sys`, `pathlib.Path`, `typing.Optional` — all standard library.
No circular dependencies with other scripts (script does not import from other project scripts).

Minor note: `os` is imported (line 20) but never referenced in the script body. Not a correctness issue — `pathlib` covers all path operations — but it is dead code.

---

## Check 2: Code Style vs Reference Script

**Result**: PASS

Matches `migrate_target_release_to_package.py` style:
- Module docstring with purpose and usage at top: present
- Type hints on all function signatures: present
- Docstrings on all functions: present
- Section dividers (`# ---`) used to separate logical blocks: present
- `split_frontmatter()`, `semver_tuple()`, `earliest_package()`, `parse_release_backlog()`, `build_lookup()` all carried over with equivalent signatures
- CRLF-preservation pattern (detect `\r\n`, write back accordingly): present in `sync_goal_md()`
- BOM-safe reads (`encoding="utf-8-sig"`): present in all read calls
- Argparse `--dry-run` / `--apply` mutual exclusion group with `default=True` / `default=False`: matches reference

---

## Check 3: Correctness of Logic

### 3a: Parse trackable_items from requirements.md

**Result**: PASS

`parse_item_package_map()` uses a state-machine over frontmatter lines:
- Detects `trackable_items:` top-level key
- Detects `acceptance_criteria:` and `sections:` sub-keys within it
- Matches `- id: AC-xx` / `- id: SEC-xx` item ID lines
- Matches `target_package: "..."` lines under the current item
- Exits the block on any top-level (non-indented) key

Logic is correct for the YAML structure used in requirements.md.

### 3b: item_id → target_package map

**Result**: PASS

Map is built as `{item_id: package_name_string}`. Correctly populated from parsed items. Used by `compute_target_package()` via lookup.

### 3c: Skip tasks with empty covers

**Result**: PASS

`sync_goal_md()` checks `if not ac_ids and not sec_ids: return None` — correctly skips tasks with both lists empty.

### 3d: Skip tasks with source_gap

**Result**: PASS (with minor observation)

Check is `re.search(r'^source_gap:\s*\S', fm_body, re.MULTILINE)` — requires at least one non-whitespace character after the key. In practice all actual `source_gap:` values are non-empty text strings, so this works correctly against the real dataset. The edge case of `source_gap: ""` (quoted empty string) would incorrectly trigger the skip because `"` is `\S` — but this format does not appear in the codebase.

### 3e: Earliest-versioned package via semver

**Result**: PASS

`semver_tuple()` and `earliest_package()` are copied faithfully from the reference script. The sort key `(0, semver_tuple(ver), 0)` for versioned packages and `(1, (0,0,0), idx)` for unversioned correctly implements the three priority rules documented in the reference. One behavioral note: synthetic packages (package names found in requirements but absent from RELEASE_BACKLOG.md) are created with `assigned_release: None` and are not in `lookup["ordered"]`, so `lookup["ordered"].index(pkg)` raises `ValueError` which is caught and returns `idx = 999999` — correctly demoting them to lowest priority.

### 3f: Update goal.md frontmatter without corrupting other fields

**Result**: PASS

`update_target_package_in_frontmatter()` uses line-by-line replacement:
- If `target_package:` line already exists: replaces it in place
- If absent: inserts before `covers:` line, or before `scope_description:`, or at end of frontmatter

The insert logic is verified correct by tracing: `insert_idx` starts at `len(new_lines)`, is set to `i` on first pattern match, then the outer loop breaks via `if insert_idx < len(new_lines): break`. All three test cases (has `covers:`, has `scope_description:`, has neither) produce correct output.

The function only modifies the frontmatter body; `split_frontmatter()` + reassembly preserves the rest of the file. No corruption risk for other fields.

### 3g: --dry-run does not write files

**Result**: PASS

`dry_run` flag propagates from `main()` → `sync_requirement_folder()` → `sync_goal_md()`. The write statement `goal_path.write_text(...)` is guarded by `if not dry_run:`. Mode correctly defaults to dry-run when `--apply` is not passed.

---

## Check 4: BUG — parse_covers does not handle multi-line YAML list format

**Result**: FAIL — Logic gap

**Description**: `parse_covers()` states in its docstring "Handles both inline list format: [AC-01, AC-02] and multi-line format." However, the implementation only handles the inline bracket format via `re.search(r'covers:.*?acceptance_criteria:\s*\[([^\]]*)\]', ...)`. It has no code path for the multi-line YAML bullet-list format:

```yaml
covers:
  acceptance_criteria:
    - AC-01
    - AC-02
```

**Impact**: Three existing goal.md files in the repository use the multi-line format with non-empty acceptance_criteria lists. For these files, `parse_covers()` returns empty lists, causing `sync_goal_md()` to silently skip them (the `if not ac_ids and not sec_ids: return None` guard fires). These tasks will never be synced regardless of what packages are assigned to their covered ACs.

Files affected:
- `requirements_tasks/functional/shared/epic_data_transfer/tasks/2026-02-22_explore_create_impl_tasks_feat_transfer/goal.md` (AC-01 through AC-05)
- `requirements_tasks/functional/shared/epic_security/tasks/2026-03-29_explore_privacy_boundary_architecture/goal.md` (AC-09, AC-12)
- `requirements_tasks/non-functional/branding/app_naming/tasks/2026-02-08_explore_app_naming/goal.md` (AC-01 through AC-05)

**Severity**: Medium — the script is functionally incomplete for a minority of files. New tasks created by `task-create` likely use the inline format (majority: 48 files use inline vs 3 multi-line), so the primary use-case is unaffected. However, the docstring claim of multi-line support is incorrect.

---

## Check 5: Minor — Unused import

**Result**: WARNING (cosmetic)

`import os` on line 20 is never used. All path operations use `pathlib.Path`. This is dead code but has no functional impact.

---

## Check 6: Skill Edit — Note 5 placement and content

**Result**: PASS

Note 5 is correctly placed in `.claude/skills/requ-explore/skill.md` Phase 2.4:
- Follows note 4 ("Do NOT back-propagate to the originating task") on line 400
- Precedes the "**YAML structure**" example block on line 408
- Separation is clean (blank line before and after note 5 block)
- The bash command is syntactically correct
- Placeholder `[path-to-requirement-folder]` is consistent with the skill's existing placeholder convention (e.g., `[parent-path]` in Phase 2.0)
- The trailing note "Tasks with empty `covers` are automatically skipped" is accurate

---

## Check 7: Documentation

**Result**: PASS

Module docstring (lines 2–17) explains:
- Purpose of the script
- When it is used (after requ-explore Phase 2.4)
- Full CLI usage with all flags
- Working directory requirement

All functions have docstrings describing parameters and return values.

---

## Check 8: CLAUDE.md scripts table

**Result**: OBSERVATION (out of scope for this task, but noted)

`scripts/sync_task_packages.py` is not listed in the "Scripts that modify (not create) files" section of CLAUDE.md. The reference script `migrate_target_release_to_package.py` is also not listed there, suggesting this section only covers scripts run automatically by the system. The sync script is invoked explicitly from the skill, so omission is likely intentional and consistent.

---

## Summary

| Check | Result |
|-------|--------|
| No forbidden imports | PASS |
| Code style matches reference | PASS |
| Parse trackable_items correctly | PASS |
| item_id → target_package map | PASS |
| Skip tasks with empty covers | PASS |
| Skip tasks with source_gap | PASS |
| Earliest-versioned package (semver) | PASS |
| Update frontmatter without corruption | PASS |
| --dry-run does not write | PASS |
| parse_covers multi-line format | FAIL (bug) |
| Unused import (os) | WARNING |
| Skill note 5 placement | PASS |
| Skill placeholder makes sense | PASS |
| Script has module docstring | PASS |

**Overall status**: RED — Fix parse_covers multi-line format before release (or explicitly restrict the docstring to inline-only and accept the current behavior as a known limitation).
