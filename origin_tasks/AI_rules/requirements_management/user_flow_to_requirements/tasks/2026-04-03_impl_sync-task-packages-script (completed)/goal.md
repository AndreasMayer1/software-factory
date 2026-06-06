---
task_id: TASK-PROC-030-09
type: impl
parent_requirement: REQ-PROC-030
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: Impl tasks created before AC package assignment are permanently orphaned from next_tasks.py package ranking"
impact: 4
impact_reason: "I4-PAIN: Orphaned tasks never surface in the correct package context — developer must manually discover and fix them"
status: completed
completed: 2026-04-03
started: 2026-04-03
effort: S
created: 2026-04-03
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Create scripts/sync_task_packages.py and add one-line call in requ-explore Phase 2.4"
release_description: ""
requirements_version:
  commit: e9382676
  file: ../requirements.md
---

# Implementation Task: sync_task_packages.py + requ-explore hook

## Requirement Reference

- **Requirement**: ../requirements.md (REQ-PROC-030)
- **Status**: Not Started

## Goal

Close the target_package propagation gap identified in TASK-PROC-030-06: when ACs in a
requirement get packages assigned (via `requ-explore` Phase 2.4), covering impl/explore
tasks are not updated. This task delivers the fix.

## Scope Overview

**Affected files**:
1. `scripts/sync_task_packages.py` (new file)
2. `.claude/skills/requ-explore/skill.md` (one-line addition in Phase 2.4)

**Patterns to follow**: `scripts/migrate_target_release_to_package.py` — reuse
`split_frontmatter()`, `semver_tuple()`, frontmatter write pattern.

## Script Design: sync_task_packages.py

**Interface**:
```
python3 scripts/sync_task_packages.py [--requirement PATH] [--dry-run | --apply]
```
- `--requirement PATH`: folder containing requirements.md (scans all requirements_tasks/ if omitted)
- `--dry-run` (default): report what would change without writing
- `--apply`: write changes

**Logic**:
1. For each `requirements.md` under the given path:
   - Parse `trackable_items.acceptance_criteria` and `trackable_items.sections`
   - Build map: `item_id → target_package`
2. For each `tasks/*/goal.md` under the same requirement folder (one level deep):
   - Parse `covers.acceptance_criteria` and `covers.sections`
   - **Skip if both are empty** — task has no concrete AC/section coverage
     (naturally skips flow-derived explore tasks, requirement-writing explore tasks,
     verification tasks — all have empty covers)
   - For each covered item, look up `target_package` from the map
   - Compute task `target_package` as earliest-versioned package (semver)
   - If computed value differs from current (or absent → now set): update goal.md
   - Report: "[path]: [old or absent] → [new]"

**Reuse from migrate_target_release_to_package.py**:
- `split_frontmatter()` — frontmatter parsing and reassembly
- `semver_tuple()` — version comparison
- `earliest_package()` — pick earliest-versioned package among candidates
- `parse_release_backlog()` + `build_lookup()` — for version lookup (needed to compare semver of packages)

## Skill Addition: requ-explore Phase 2.4

**File**: `.claude/skills/requ-explore/skill.md`

**Insert after** note 4 ("Do NOT back-propagate to the originating task"), before the
YAML structure example block. New note 5:

```
5. **Sync covering tasks**: After assigning packages to all items in this requirement, run:
   ```bash
   python3 scripts/sync_task_packages.py --requirement [path-to-requirement-folder] --apply
   ```
   Log the script output to the user. Tasks with empty `covers` are automatically skipped.
```

## Acceptance Criteria

- [ ] `scripts/sync_task_packages.py` exists with `--requirement`, `--dry-run`, `--apply` flags
- [ ] Script skips tasks with empty `covers` (both acceptance_criteria and sections empty)
- [ ] Script correctly computes earliest-versioned package using semver
- [ ] Script updates `target_package` in goal.md frontmatter without touching other fields
- [ ] `--dry-run` reports changes without writing
- [ ] `requ-explore` Phase 2.4 contains the script call (note 5)
- [ ] Manual test: create a requirement with 2 ACs, assign packages, run script → covering task gets correct `target_package`

## References

- Sister exploration: `tasks/2026-04-02_explore_target-package-propagation-gap/plans_and_protocols/2026-04-02_01_protocol_target-package-propagation-gap.md`
- Pattern source: `scripts/migrate_target_release_to_package.py`
