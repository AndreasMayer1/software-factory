# Migration Plan: Date-Prefixed Requirements → Git-Versioned Requirements

**Date:** 2026-01-04
**Status:** Draft (awaiting user approval)
**Effort Estimate:** Medium (4-6 hours)
**Risk Level:** Low-Medium (reversible, no code changes)

---

## Executive Summary

### Overview
Migrate from multiple date-prefixed requirements files per feature to a single git-versioned `requirements.md` per feature, while maintaining full traceability for existing tasks via git commit hashes.

### Expected Benefits
1. **Reduced maintenance:** Single file to edit per feature
2. **Better tooling:** Use standard git diff, blame, history
3. **Cleaner structure:** Less file clutter
4. **Full traceability:** Git commit hash in each task's `goal.md`
5. **Better diffs:** See exactly what changed between versions

### Risk Assessment
- **Overall Risk:** Low-Medium
- **Reversibility:** High (can restore from git/backups)
- **Breaking Changes:** None (backwards compatible)
- **Data Loss Risk:** Very Low (archival strategy + git history)

---

## 1. Current State Analysis

### Inventory Script
```bash
# Find all date-prefixed requirements
find requirements_tasks -type f -name "*requirement*.md" \
  | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" \
  | sort

# Count by feature
find requirements_tasks -type f -name "*requirement*.md" \
  | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" \
  | xargs dirname \
  | sort | uniq -c
```

### Expected Findings
Based on earlier search, we found:
- `requirements_tasks/process/AI_rules/coding_standards/testing/2025-10-02_requirements.md`
- `requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/2025-08-31_requirement.md`
- `requirements_tasks/non-functional/architecture/2025-10-01_requirement_data_model_versioning.md`
- Multiple requirements in navigation/responsive_layout tasks

### Consolidation Complexity
**Simple cases (1 file):** Just rename to `requirements.md`
**Complex cases (2+ files):** Need merge strategy (see Section 3)

---

## 2. Migration Strategy

### Phase 1: Preparation & Backup
**Objective:** Ensure safe rollback capability

**Steps:**
1. **Create git branch** for migration
   ```bash
   git checkout -b migration/git-versioned-requirements
   ```

2. **Create backup archive**
   ```bash
   timestamp=$(date +%Y%m%d_%H%M%S)
   tar -czf "requirements_backup_${timestamp}.tar.gz" requirements_tasks/
   ```

3. **Document current state**
   ```bash
   # Save file inventory
   find requirements_tasks -name "*requirement*.md" > migration_inventory_before.txt

   # Save current git commit
   git rev-parse HEAD > migration_base_commit.txt
   ```

**Acceptance Criteria:**
- [ ] Git branch created
- [ ] Backup archive created and verified
- [ ] Inventory files created

---

### Phase 2: Requirements Consolidation
**Objective:** Merge date-prefixed files into single `requirements.md` per feature

#### 2.1 Consolidation Logic

**For features with 1 requirements file:**
```bash
# Simple rename
cd feature_folder/
git mv 2025-XX-XX_requirement.md requirements.md
git commit -m "requ: consolidate to git-versioned requirements.md"
```

**For features with 2+ requirements files:**

**Decision Tree:**
```
Are requirements incremental (newer extends older)?
├─ YES: Use newest as base, add "Historical Versions" section
│   └─ Action: Merge strategy A (see below)
└─ NO: Requirements conflict or replace each other?
    ├─ YES: Use newest only, archive older versions
    │   └─ Action: Merge strategy B (see below)
    └─ UNCLEAR: Manual review required
        └─ Action: Flag for manual merge
```

**Merge Strategy A: Incremental Requirements**
```markdown
# requirements.md

[Content from newest requirement file]

---

## Historical Context

### Version: 2025-08-31
[Summary or relevant excerpts from older version]

**Changes in later versions:**
- Added feature X (2025-09-28)
- Clarified requirement Y (2025-10-15)

**Full history:** See git log for this file
```

**Merge Strategy B: Superseding Requirements**
```markdown
# requirements.md

[Content from newest requirement file only]

---

## Superseded Versions

This requirement supersedes:
- `2025-08-31_requirement.md` - archived in `archive/requirements_history/`

For historical context, see archived files or git history before consolidation:
`git show migration_base_commit:path/to/old_requirement.md`
```

#### 2.2 Automation Script (Pseudocode)

```python
# migration_script.py (pseudocode)

for each feature_folder in requirements_tasks:
    req_files = find_date_prefixed_requirements(feature_folder)

    if len(req_files) == 0:
        continue  # No requirements to migrate

    elif len(req_files) == 1:
        # Simple case: just rename
        git_mv(req_files[0], "requirements.md")
        git_commit(f"requ: consolidate {feature_folder} to git-versioned")

    else:  # len(req_files) > 1
        # Complex case: needs merge strategy
        newest = max(req_files, key=extract_date)
        older = [f for f in req_files if f != newest]

        # Analyze if incremental
        is_incremental = analyze_requirements_relationship(newest, older)

        if is_incremental:
            merged_content = merge_strategy_A(newest, older)
        else:
            merged_content = merge_strategy_B(newest, older)
            # Move old files to archive
            for old_file in older:
                archive_file(old_file)

        write_file("requirements.md", merged_content)
        git_add("requirements.md")
        if not is_incremental:
            git_add("archive/")
        git_commit(f"requ: consolidate {feature_folder} (merged {len(req_files)} versions)")
```

**Manual Review Required:**
- Features with conflicting (non-incremental, non-superseding) requirements
- Features where relationship between versions is unclear
- Create checklist: `migration_manual_review.md`

---

### Phase 3: Task Update Strategy
**Objective:** Add git commit hash references to existing tasks

#### 3.1 Determine Requirements Version for Each Task

**Logic:**
```python
for each task in all_tasks:
    task_date = extract_date_from_task_folder(task)  # e.g., "2025-10-15"
    feature_folder = get_parent_feature(task)
    requirements_file = feature_folder + "/requirements.md"

    # Find git commit of requirements.md at task creation date
    # This assumes we've already consolidated and committed
    commit_hash = git_find_commit_before_date(
        file=requirements_file,
        date=task_date
    )

    if commit_hash is None:
        # Requirements didn't exist yet or task predates git migration
        # Use the consolidation commit as reference
        commit_hash = git_show_first_commit(requirements_file)

    # Update task's goal.md
    update_goal_with_commit_hash(task, commit_hash, task_date)
```

#### 3.2 goal.md Update Template

**Add at the top of existing goal.md:**
```markdown
---
**MIGRATION NOTE (2026-01-04):**
**Requirements Version:**
- Git Commit: {COMMIT_HASH}
- Date: {TASK_DATE}
- File: ../requirements.md

To view requirements as they were when this task was created:
`git show {COMMIT_HASH}:path/to/requirements.md`
---

[Existing goal.md content below...]
```

**Script:**
```python
def update_goal_with_commit_hash(task_path, commit_hash, task_date):
    goal_file = task_path + "/goal.md"
    existing_content = read_file(goal_file)

    header = f"""---
**MIGRATION NOTE (2026-01-04):**
**Requirements Version:**
- Git Commit: {commit_hash[:7]}
- Date: {task_date}
- File: ../requirements.md

To view requirements as they were when this task was created:
`git show {commit_hash}:requirements_tasks/.../requirements.md`
---

"""

    new_content = header + existing_content
    write_file(goal_file, new_content)
    git_add(goal_file)
```

#### 3.3 Edge Cases

**Case 1: Task predates all requirements**
- Use oldest available commit of requirements.md
- Add note: "Note: Task may predate formal requirements documentation"

**Case 2: Multiple requirements files existed at task creation**
- List all relevant commits
- Note which one was likely used (by proximity/naming)

**Case 3: Requirements file was deleted/moved**
- Use git history to find it
- Add note with historical path

---

### Phase 4: Template & Tooling Updates
**Objective:** Update templates and skills for future tasks

#### 4.1 Update goal.md Template

**New section in all task templates:**
```markdown
**Requirements Version:**
- Git Commit: {auto-filled by setup-task}
- Date: {auto-filled by setup-task}
- File: ../requirements.md

## Requirements Summary
{Brief summary - to be filled manually or extracted}

## Full Requirements
For complete requirements at task creation:
`git show {COMMIT_HASH}:path/to/requirements.md`
```

#### 4.2 Update setup-task Skill

**Modifications needed:**
```python
# In setup-task skill

def create_goal_md(task_path, requirement_path):
    # ... existing logic ...

    # NEW: Capture git commit hash
    commit_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True
    ).stdout.strip()

    task_date = datetime.now().strftime("%Y-%m-%d")

    # Add to goal.md
    requirements_section = f"""
**Requirements Version:**
- Git Commit: {commit_hash[:7]}
- Date: {task_date}
- File: {relative_path_to_requirements}

## Requirements Summary
[To be filled: Brief summary of relevant requirements]

## Full Requirements
For complete requirements at task creation:
`git show {commit_hash}:{requirement_path}`
"""

    # ... insert into goal.md template ...
```

#### 4.3 Update README.md

**Section to update:**
```markdown
## Requirements Versioning

Requirements are versioned using git. Each feature has a single `requirements.md` file.

### For New Tasks
When creating a task, the `setup-task` skill automatically captures:
- Current git commit hash of requirements.md
- Task creation date
- Relative path to requirements

This ensures full traceability even as requirements evolve.

### Viewing Historical Requirements
To see requirements as they were for a specific task:
```bash
# Find commit hash in task's goal.md, then:
git show <commit-hash>:path/to/requirements.md
```

### Updating Requirements
Simply edit `requirements.md` and commit:
```bash
git add requirements.md
git commit -m "requ: update feature X requirements - add Y"
```

All previous versions remain accessible via git history.
```

---

## 3. Migration Script Specification

### 3.1 Main Script Structure

```bash
#!/bin/bash
# migrate_to_git_versioning.sh

set -e  # Exit on error

# Configuration
BACKUP_DIR="migration_backups"
ARCHIVE_DIR="archive/requirements_history"
LOG_FILE="migration_log_$(date +%Y%m%d_%H%M%S).txt"

# Phase 1: Preparation
echo "Phase 1: Preparation" | tee -a $LOG_FILE
create_backup
create_git_branch
save_inventory

# Phase 2: Consolidate requirements
echo "Phase 2: Consolidating requirements" | tee -a $LOG_FILE
consolidate_requirements

# Phase 3: Update tasks
echo "Phase 3: Updating tasks" | tee -a $LOG_FILE
update_all_tasks

# Phase 4: Update templates
echo "Phase 4: Updating templates and docs" | tee -a $LOG_FILE
update_templates
update_readme

# Final: Commit and summary
git commit -m "requ: migrate to git-versioned requirements [migration]"
print_summary
```

### 3.2 Detailed Functions

**consolidate_requirements():**
```bash
consolidate_requirements() {
    # Find all features with date-prefixed requirements
    while IFS= read -r feature_dir; do
        cd "$feature_dir"

        req_files=($(ls -1 *requirement*.md 2>/dev/null | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" || true))

        if [ ${#req_files[@]} -eq 0 ]; then
            continue
        elif [ ${#req_files[@]} -eq 1 ]; then
            # Simple rename
            git mv "${req_files[0]}" requirements.md
        else
            # Complex merge - flag for manual review
            echo "MANUAL_REVIEW: $feature_dir (${#req_files[@]} files)" | tee -a $LOG_FILE
            echo "$feature_dir" >> manual_review_list.txt
        fi

        cd -
    done < <(find requirements_tasks -type d -name "tasks" | xargs dirname)
}
```

**update_all_tasks():**
```python
# update_tasks.py
import os
import subprocess
from datetime import datetime
from pathlib import Path

def get_commit_hash_at_date(file_path, date):
    """Get git commit hash of file at or before given date."""
    result = subprocess.run(
        ["git", "log", "--until=" + date, "--format=%H", "-1", "--", file_path],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def update_task_goal(task_path):
    task_date = extract_task_date(task_path)  # from folder name
    feature_path = Path(task_path).parent.parent
    req_file = feature_path / "requirements.md"

    if not req_file.exists():
        print(f"Warning: No requirements.md for {task_path}")
        return

    commit_hash = get_commit_hash_at_date(str(req_file), task_date)

    if not commit_hash:
        # Use first commit of requirements.md
        result = subprocess.run(
            ["git", "log", "--format=%H", "--reverse", "--", str(req_file)],
            capture_output=True, text=True
        )
        commit_hash = result.stdout.split('\n')[0] if result.stdout else "unknown"

    # Update goal.md
    goal_path = Path(task_path) / "goal.md"
    if goal_path.exists():
        prepend_requirements_section(goal_path, commit_hash, task_date, req_file)

def prepend_requirements_section(goal_path, commit_hash, task_date, req_file):
    with open(goal_path, 'r', encoding='utf-8') as f:
        existing = f.read()

    header = f"""---
**MIGRATION NOTE (2026-01-04):**
**Requirements Version:**
- Git Commit: {commit_hash[:7]}
- Date: {task_date}
- File: {os.path.relpath(req_file, goal_path.parent.parent)}

To view requirements at task creation:
`git show {commit_hash[:7]}:requirements_tasks/.../requirements.md`
---

"""

    with open(goal_path, 'w', encoding='utf-8') as f:
        f.write(header + existing)

# Main execution
for task_dir in find_all_task_directories():
    update_task_goal(task_dir)
```

### 3.3 Manual Steps

**Cannot be automated - require human judgment:**

1. **Merging conflicting requirements** (Strategy A vs B decision)
2. **Writing requirements summaries** for complex merges
3. **Resolving unclear version relationships**
4. **Reviewing migration log** for anomalies

**Estimated manual effort:** 1-2 hours

---

## 4. Rollback Plan

### 4.1 Immediate Rollback (During Migration)

**If issues discovered during migration:**
```bash
# 1. Abort and return to main branch
git checkout main
git branch -D migration/git-versioned-requirements

# 2. Restore from backup if needed
tar -xzf requirements_backup_TIMESTAMP.tar.gz
```

### 4.2 Post-Migration Rollback

**If issues discovered after merge to main:**
```bash
# 1. Find migration commit
git log --grep="migrate to git-versioned" --format="%H" -1

# 2. Revert the migration
git revert <commit-hash>

# OR reset to before migration
git reset --hard <commit-before-migration>

# 3. Restore from backup archive
tar -xzf requirements_backup_TIMESTAMP.tar.gz
```

### 4.3 Data Recovery

**All data remains recoverable:**
- Git history preserves all commits
- Backup archive has pre-migration state
- Archived files in `archive/requirements_history/`

---

## 5. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|------------|---------|------------|
| **Merge conflicts** (complex requirements) | Medium | Medium | Manual review list + clear decision tree |
| **Wrong commit hash** for tasks | Low | Low | Can be corrected post-migration |
| **Lost requirements context** | Low | Medium | Archive old files instead of deleting |
| **Script errors** | Medium | Low | Dry-run mode + extensive logging |
| **Git history confusion** | Low | Low | Clear commit messages + migration notes |
| **Breaking existing workflows** | Very Low | High | Backwards compatible (old tasks still work) |
| **User resistance to git** | Low | Medium | Good documentation + examples |

### Risk Mitigation Summary
- ✅ All changes in feature branch first
- ✅ Complete backup before starting
- ✅ Extensive logging for audit trail
- ✅ Manual review list for complex cases
- ✅ Reversible at any point
- ✅ No code changes (only documentation)

---

## 6. Testing & Validation

### 6.1 Pre-Migration Tests

**Checklist:**
- [ ] Git repository is clean (no uncommitted changes)
- [ ] All tests pass
- [ ] Backup created and verified (can extract)
- [ ] Migration branch created
- [ ] Inventory files generated

### 6.2 Post-Consolidation Tests

**For each consolidated requirement:**
- [ ] `requirements.md` exists and is valid markdown
- [ ] Git history shows consolidation commit
- [ ] Old files archived (if multiple versions)
- [ ] No duplicate requirements files remain

**Script:**
```bash
# Validation script
find requirements_tasks -name "*requirement*.md" | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}"
# Should return empty or only archived files
```

### 6.3 Post-Task-Update Tests

**Sample task checks:**
- [ ] goal.md contains git commit hash
- [ ] Commit hash is valid (git show <hash> works)
- [ ] Commit hash corresponds to correct date
- [ ] Can retrieve requirements using documented command

**Script:**
```bash
# Test random sample of tasks
for task in $(find requirements_tasks -type d -name "*_impl_*" | shuf -n 5); do
    goal="$task/goal.md"
    if grep -q "Git Commit:" "$goal"; then
        hash=$(grep "Git Commit:" "$goal" | awk '{print $3}')
        git show "$hash" > /dev/null 2>&1 && echo "✓ $task" || echo "✗ $task"
    else
        echo "⚠ No commit hash: $task"
    fi
done
```

### 6.4 Integration Tests

**Test new workflow:**
1. Create a new test task using `setup-task` skill
2. Verify goal.md contains commit hash
3. Modify requirements.md
4. Create another task
5. Verify new task has different commit hash
6. Use `git show` to verify both tasks can retrieve their respective requirements versions

### 6.5 Acceptance Criteria

**Migration is complete when:**
- [ ] All date-prefixed requirements consolidated
- [ ] All tasks have commit hash references
- [ ] Templates updated with new format
- [ ] Documentation (README.md) updated
- [ ] All validation tests pass
- [ ] Manual review items resolved
- [ ] Migration log reviewed and clean
- [ ] New workflow tested successfully
- [ ] User approval obtained

---

## 7. Execution Timeline

### Recommended Approach: Phased Migration

**Option A: Big Bang (All at once)**
- Pros: Done quickly, consistent state
- Cons: Higher risk, more manual work at once
- Time: 4-6 hours continuous

**Option B: Incremental (Folder by folder)** ⭐ **RECOMMENDED**
- Pros: Lower risk, can pause/resume, learn as you go
- Cons: Takes longer, mixed state during migration
- Time: 1-2 hours per session, multiple sessions

**Recommended Order (Option B):**
1. **Pilot:** Start with `process/` folder (smaller, lower risk)
2. **Validate:** Test workflow, fix any issues
3. **Continue:** `non-functional/` folder
4. **Final:** `functional/` folder (largest, highest impact)

---

## 8. Post-Migration Actions

### 8.1 Immediate (Same Session)
- [ ] Run all validation tests
- [ ] Review migration log for errors
- [ ] Test new task creation workflow
- [ ] Commit migration changes
- [ ] Create git tag: `migration-requirements-versioning-complete`

### 8.2 Short-term (Within 1 week)
- [ ] Update CLAUDE.md if needed
- [ ] Update skill documentation
- [ ] Create user guide for new workflow
- [ ] Monitor for issues in daily use

### 8.3 Long-term (Within 1 month)
- [ ] Remove migration notes from goal.md (optional)
- [ ] Clean up migration logs and scripts
- [ ] Archive backup files (keep for 3 months minimum)

---

## 9. Open Questions for User Approval

Before proceeding, please confirm:

1. **Merge Strategy:**
   - For incremental requirements: Strategy A (merge with history section)?
   - For superseding requirements: Strategy B (newest only + archive)?

2. **Manual Review Threshold:**
   - Should ALL multi-file consolidations be manually reviewed?
   - Or only those flagged as "unclear relationship"?

3. **Execution Timing:**
   - Big Bang approach (all at once)?
   - Or incremental (folder by folder)?

4. **Archive Location:**
   - Keep archived files in `archive/requirements_history/`?
   - Or different location?

5. **Commit Hash Format:**
   - Short hash (7 chars): `a3f5b2c`?
   - Or full hash (40 chars)?

6. **Migration Notes:**
   - Keep migration notes in goal.md permanently?
   - Or remove after verification period?

---

## 10. Approval Checklist

Before executing this migration, confirm:

- [ ] I understand the changes being made
- [ ] I approve the consolidation strategies (A & B)
- [ ] I approve the task update approach (commit hash in goal.md)
- [ ] I approve the execution approach (Big Bang vs Incremental)
- [ ] I understand the rollback procedure
- [ ] I accept the risk level (Low-Medium)
- [ ] I have reviewed the manual review list (will be generated)
- [ ] I approve proceeding with Phase 1 (Preparation)

**User Signature:** _______________
**Date:** _______________

---

## Appendix A: Example Consolidation

**Before:**
```
feature_X/
├── 2025-08-31_requirement.md
├── 2025-09-28_detailed_requirement.md
└── tasks/
    └── 2025-10-15_impl_something/
        └── goal.md
```

**After:**
```
feature_X/
├── requirements.md                    # Consolidated
├── archive/
│   └── requirements_history/
│       ├── 2025-08-31_requirement.md  # Archived
│       └── 2025-09-28_detailed_requirement.md
└── tasks/
    └── 2025-10-15_impl_something/
        └── goal.md                     # Updated with commit hash
```

**goal.md update:**
```markdown
---
**MIGRATION NOTE (2026-01-04):**
**Requirements Version:**
- Git Commit: b7f3a1c
- Date: 2025-10-15
- File: ../requirements.md

To view requirements at task creation:
`git show b7f3a1c:requirements_tasks/.../requirements.md`
---

# Goal: Implement Something
[... rest of original goal.md ...]
```

---

**END OF MIGRATION PLAN**

**Status:** Ready for user review and approval
**Next Step:** User approval → Create implementation task
