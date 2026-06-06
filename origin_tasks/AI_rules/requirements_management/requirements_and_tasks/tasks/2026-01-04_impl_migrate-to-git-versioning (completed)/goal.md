---
task_id: TASK-PROC-009-09
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: L
created: 2026-01-04
completed: 2026-01-04
after:
  - TASK-PROC-009-08
awaiting: []
covers:
  sections:
    - SEC-03  # Requirements Versioning
    - SEC-14  # Migration Strategy
scope_description: "Execute migration from date-prefixed to git-versioned requirements"
requirements_version:
  commit: 7605229
  file: ../requirements.md
---

# Goal: Implement Migration to Git-Versioned Requirements

**Created:** 2026-01-04
**Based on Requirements:** ../2026-01-04_requirement_git_versioning.md
**Plan Reference:** ../2026-01-04_explore_migration-plan/plans_and_protocols/2026-01-04_01_plan_migration.md
**Type:** Implementation
**Status:** Ready to start

## Objective

Execute the migration from date-prefixed requirements files to a single git-versioned `requirements.md` per feature, with git commit hash traceability in all task goal.md files.

## Key Decisions (User-Approved)

1. **No Archive** - Old files are deleted after merge. Git history serves as archive.
2. **Merge Strategy** - One Opus agent per merge operation. Agent consolidates all date-prefixed files in a folder into a single `requirements.md`.
3. **Manual Review** - Agent asks user only when unclear. Use Opus model for quality.
4. **Execution** - Incremental (folder by folder)
5. **Git Hash** - Short format (7 chars)
6. **In goal.md** - Store both git commit hash AND original filename

## Execution Steps

### Step 0: Safety Commit
```bash
git add requirements_tasks/
git commit -m "chore: pre-migration snapshot of requirements_tasks"
```
**Store this commit hash** - it's the reference point for all old requirements.

### Step 1: Inventory
Find all date-prefixed requirements files and group by feature folder.

### Step 2: Consolidation (Per Feature Folder)
For each folder with date-prefixed requirements:
1. Spawn Opus agent with all requirement files as context
2. Agent writes consolidated `requirements.md`
3. Delete old date-prefixed files
4. Commit per folder (for clean git history)

### Step 3: Update Tasks
For each existing task:
1. Find which requirement file(s) it was based on (by date comparison)
2. Add to goal.md:
   - Original requirement filename(s)
   - Git commit hash (from Step 0 snapshot)
   - Command to retrieve historical version

### Step 4: Update Templates & Skills
1. Update goal.md template in setup-task skill
2. Update README.md versioning section

### Step 5: Final Commit
```bash
git add requirements_tasks/
git commit -m "requ: complete migration to git-versioned requirements"
```

## Agent Instructions for Consolidation

When spawning merge agent, provide:

**Prompt:**
```
Consolidate the following date-prefixed requirements files into a single requirements.md.

Files to merge:
{list of files with full content}

Instructions:
1. Analyze all files for overlaps, conflicts, and evolution
2. Create ONE coherent requirements.md that captures:
   - All still-relevant requirements
   - Remove outdated/superseded content
   - Preserve important context and rationale
3. If requirements conflict, ask the user for clarification
4. The result should be a clean, well-structured requirements document
5. Add a "Version History" section at the bottom noting the source files
```

## goal.md Update Format

Add this section at the top of existing goal.md files:

```markdown
---
**Requirements Source (at task creation):**
- Original File: {ORIGINAL_FILENAME, e.g., 2025-08-31_requirement.md}
- Pre-Migration Commit: {SNAPSHOT_COMMIT_HASH}
- Task Date: {DATE_FROM_FOLDER_NAME}

To view original requirements:
`git show {HASH}:path/to/{ORIGINAL_FILENAME}`
---
```

## Success Criteria

- [ ] Pre-migration commit created
- [ ] All date-prefixed requirements consolidated
- [ ] All old files deleted (git history preserved)
- [ ] All existing tasks updated with commit hash + original filename
- [ ] Templates updated
- [ ] README.md updated
- [ ] All commits clean and atomic
- [ ] New workflow tested

## Notes

- Use incremental approach: process/ → non-functional/ → functional/
- Commit after each folder consolidation for clean history
- Opus model required for merge agents (quality)
- Ask user only when truly unclear (not for every merge)
