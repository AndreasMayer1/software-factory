# Implementation Plan: Git-Versioned Requirements Migration

**Date:** 2026-01-04
**Status:** Ready for execution
**Based on:** ../2026-01-04_explore_migration-plan (refined with user feedback)

---

## Overview

Migrate all date-prefixed requirements files to single git-versioned `requirements.md` files per feature. Use agent-based consolidation with Opus model for quality merges.

---

## Phase 0: Pre-Migration Safety

### 0.1 Create Safety Snapshot

```bash
# Ensure clean working tree
git status

# Commit current state as snapshot
git add requirements_tasks/
git commit -m "chore: pre-migration snapshot of requirements_tasks"

# Store the commit hash
PRE_MIGRATION_COMMIT=$(git rev-parse HEAD)
echo "Pre-migration commit: $PRE_MIGRATION_COMMIT"
```

**This commit hash is critical** - it's the reference point for all historical requirements.

### 0.2 Create Inventory

```bash
# Find all date-prefixed requirements
find requirements_tasks -type f -name "*requirement*.md" \
  | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" \
  | sort > migration_inventory.txt

# Group by parent folder
cat migration_inventory.txt | xargs -I{} dirname {} | sort -u > folders_to_process.txt

# Count files per folder
while read folder; do
  count=$(ls "$folder"/*requirement*.md 2>/dev/null | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" | wc -l)
  echo "$count $folder"
done < folders_to_process.txt > folder_complexity.txt
```

---

## Phase 1: Consolidation (Incremental)

### Execution Order
1. `requirements_tasks/process/` (smallest, lowest risk - pilot)
2. `requirements_tasks/non-functional/`
3. `requirements_tasks/functional/`

### Per-Folder Procedure

For each folder with date-prefixed requirements:

#### Step 1.1: Analyze

```python
# Pseudocode
folder = current_folder
req_files = find_date_prefixed_requirements(folder)
existing_requirements_md = folder / "requirements.md"  # May or may not exist
```

#### Step 1.2: Spawn Merge Agent

```python
# Use Task tool with Opus model
prompt = f"""
You are a requirements consolidation agent.

## Task
Merge the following date-prefixed requirements files into a single requirements.md.

## Source Files
{for each file: filename + full content}

## Target File
{"Overwrite: " + existing_requirements_md if exists else "Create: requirements.md"}

## Instructions
1. Read ALL source files carefully
2. Identify:
   - Core requirements (keep)
   - Evolved/updated requirements (use latest version)
   - Superseded/outdated content (remove)
   - Conflicting requirements (ASK USER)
3. Write a clean, well-structured requirements.md:
   - Clear sections
   - No redundancy
   - Proper markdown formatting
4. Add "Version History" section at the end:
   ```markdown
   ---
   ## Version History
   Consolidated from:
   - 2025-08-31_requirement.md (initial)
   - 2025-09-28_requirement.md (extended scope)
   Consolidation date: 2026-01-04
   ```
5. Only ask the user if there's a genuine conflict or ambiguity

## Output
Write the consolidated content to: {target_path}
"""

# Spawn with Opus model
Task(
    subagent_type="general-purpose",
    model="opus",
    prompt=prompt
)
```

#### Step 1.3: Delete Old Files

After agent completes:

```bash
# Delete all date-prefixed requirements in this folder
cd "$folder"
rm -f *requirement*.md  # Only those matching date pattern, not the new requirements.md

# Or more precisely:
find . -maxdepth 1 -name "*requirement*.md" | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" | xargs rm
```

#### Step 1.4: Commit

```bash
git add "$folder"
git commit -m "requ: consolidate $(basename $folder) requirements to git-versioned"
```

---

## Phase 2: Update Existing Tasks

### 2.1 Find All Tasks

```bash
find requirements_tasks -type d -name "*_impl_*" -o -name "*_explore_*" > all_tasks.txt
```

### 2.2 Per-Task Update

For each task:

```python
def update_task(task_path, pre_migration_commit):
    # Extract task date from folder name
    task_date = extract_date(task_path.name)  # e.g., "2025-10-15"

    # Find parent feature folder
    feature_folder = task_path.parent.parent

    # Find which requirement file(s) existed at task creation
    # Look in pre-migration commit for files in that folder
    old_req_files = git_ls_tree(
        pre_migration_commit,
        feature_folder,
        filter="*requirement*.md"
    )

    # Filter to files that existed at task date
    # (files with date prefix <= task_date)
    relevant_files = [f for f in old_req_files if extract_date(f) <= task_date]

    # If no date-prefixed files, use requirements.md if it existed
    if not relevant_files:
        if "requirements.md" in git_ls_tree(pre_migration_commit, feature_folder):
            relevant_files = ["requirements.md"]

    # Determine primary requirement file (usually the newest one before task date)
    primary_file = max(relevant_files, key=extract_date) if relevant_files else "unknown"

    # Update goal.md
    update_goal_md(task_path, primary_file, pre_migration_commit, task_date)
```

### 2.3 goal.md Update

Prepend to existing goal.md:

```markdown
---
**Requirements Source (at task creation):**
- Original File: 2025-08-31_requirement.md
- Pre-Migration Commit: a3f5b2c
- Task Date: 2025-10-15

To view original requirements:
`git show a3f5b2c:requirements_tasks/.../2025-08-31_requirement.md`

Current requirements: ../requirements.md
---

[... existing goal.md content ...]
```

### 2.4 Commit Task Updates

```bash
# Batch commit all task updates
git add requirements_tasks/
git commit -m "requ: add git commit hashes to existing task goal.md files"
```

---

## Phase 3: Update Templates & Documentation

### 3.1 Update setup-task Skill

Modify to capture git commit hash when creating new tasks:

```python
# In setup-task skill
def create_goal_md(task_path, requirements_path):
    # Capture current git commit
    commit_hash = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True
    ).stdout.strip()

    # Get relative path to requirements
    rel_req_path = os.path.relpath(requirements_path, task_path)

    header = f"""---
**Requirements Source:**
- File: {rel_req_path}
- Git Commit: {commit_hash}
- Date: {datetime.now().strftime("%Y-%m-%d")}

To view requirements at task creation:
`git show {commit_hash}:{requirements_path}`
---

"""
    # ... rest of goal.md template
```

### 3.2 Update README.md

Update `requirements_tasks/README.md` versioning section:

```markdown
## Requirements Versioning

Requirements are versioned using git. Each feature has a single `requirements.md` file.

### Structure
```
feature_folder/
├── requirements.md    # Single source of truth
└── tasks/
    └── YYYY-MM-DD_impl_something/
        └── goal.md    # Contains git commit reference
```

### Viewing Historical Requirements

Each task's `goal.md` contains the git commit hash from when the task was created:

```bash
# View requirements as they were when task was created
git show <commit-hash>:path/to/requirements.md
```

### Updating Requirements

Simply edit and commit:
```bash
# Edit requirements.md
git add requirements.md
git commit -m "requ: update feature X - add requirement Y"
```

All previous versions accessible via `git log requirements.md`.
```

### 3.3 Commit Documentation Updates

```bash
git add requirements_tasks/README.md
git add .claude/  # If skill files are there
git commit -m "docs: update requirements versioning documentation"
```

---

## Phase 4: Validation

### 4.1 Verify Consolidation

```bash
# Should return NO results (no more date-prefixed files)
find requirements_tasks -type f -name "*requirement*.md" | grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}"

# Should return ONE requirements.md per feature
find requirements_tasks -name "requirements.md" | wc -l
```

### 4.2 Verify Task Updates

```bash
# Sample check: all tasks should have "Requirements Source" header
grep -r "Requirements Source" requirements_tasks/*/tasks/*/goal.md | wc -l

# vs total tasks
find requirements_tasks -name "goal.md" | wc -l
```

### 4.3 Verify Git History

```bash
# Test retrieving old requirements
git show $PRE_MIGRATION_COMMIT:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/2025-08-31_requirement.md

# Should show the old file content
```

### 4.4 Test New Workflow

1. Create a test task using setup-task skill
2. Verify goal.md contains git commit hash
3. Modify requirements.md, commit
4. Create another task
5. Verify new task has different commit hash

---

## Execution Checklist

### Phase 0: Safety
- [ ] `git status` is clean
- [ ] Pre-migration commit created
- [ ] PRE_MIGRATION_COMMIT hash saved: `____________`
- [ ] Inventory files created

### Phase 1: Consolidation
- [ ] **process/** folder complete
  - [ ] All merges done (Opus agents)
  - [ ] Old files deleted
  - [ ] Committed
- [ ] **non-functional/** folder complete
  - [ ] All merges done
  - [ ] Old files deleted
  - [ ] Committed
- [ ] **functional/** folder complete
  - [ ] All merges done
  - [ ] Old files deleted
  - [ ] Committed

### Phase 2: Task Updates
- [ ] All existing tasks updated with:
  - [ ] Original filename
  - [ ] Pre-migration commit hash
- [ ] Changes committed

### Phase 3: Templates & Docs
- [ ] setup-task skill updated
- [ ] README.md updated
- [ ] Changes committed

### Phase 4: Validation
- [ ] No date-prefixed requirement files remain
- [ ] All tasks have git references
- [ ] Git history retrieval tested
- [ ] New workflow tested

### Final
- [ ] All validation passed
- [ ] Final commit if needed
- [ ] Task marked complete

---

## Rollback Procedure

If issues arise at any point:

```bash
# Return to pre-migration state
git reset --hard $PRE_MIGRATION_COMMIT

# Or if already pushed, revert
git revert HEAD~N..HEAD  # N = number of migration commits
```

---

## Notes

- Each consolidation uses its own Opus agent for quality
- Agent asks user ONLY for genuine conflicts
- Incremental approach allows pausing/resuming
- Git history preserves everything - no data loss possible
- Short hash (7 chars) is sufficient for our repo size

---

**Ready for execution. Start with Phase 0: Safety Commit.**
