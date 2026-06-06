# Plan: target_release Field Recognition & Validation

## Objective
Update `scripts/validate_meta.py` to recognize and validate the `target_release` field across YAML frontmatter, plus validate release-dependency constraints.

## Changes Required

### 1. Add RELEASES.md Loading (Init)
- Add method: `_load_releases()`
- Called once in `__init__()` to cache valid version strings
- Gracefully handle missing RELEASES.md (no error, just skip version checks)
- Extract `releases[].version` field into a set

### 2. Add target_release Validation to Requirements (validate_requirements)
- When parsing requirement metadata:
  - Extract `target_release` if present (optional field)
  - If present, validate format: `^\d+\.\d+\.\d+$`
  - If present, check version exists in cached releases
  - Store `target_release` in RequirementMeta dataclass

- When validating trackable_items:
  - For each AC object: check `target_release` field if present
  - For each SEC object: check `target_release` field if present
  - Same format + existence checks
  - If any trackable items have release, verify top-level release equals earliest

### 3. Add target_release Validation to Tasks (validate_tasks)
- When parsing task metadata:
  - Extract `target_release` if present
  - Validate format and version existence
  - Store in TaskMeta dataclass

### 4. Add Release-Dependency Validation (New Method)
- New method: `validate_release_dependencies()`
- For each requirement/task with `target_release` set:
  - For each ID in `depends_on` / `blocked_by`:
    - Look up that item in requirements or tasks
    - If both sides have `target_release`: verify `release(self) >= release(dependency)`
    - Report as **warning** (not error)
  - Skip silently if either side unassigned

### 5. Call New Validation in run() Method
- Add call to `validate_release_dependencies()` before final summary

## Data Structure Changes
- Add `target_release: Optional[str]` to RequirementMeta
- Add `target_release: Optional[str]` to TaskMeta

## Testing Notes
- Script runs standalone: `python scripts/validate_meta.py [--verbose]`
- No new dependencies required
- Existing validation patterns already present (ID format, etc.)
