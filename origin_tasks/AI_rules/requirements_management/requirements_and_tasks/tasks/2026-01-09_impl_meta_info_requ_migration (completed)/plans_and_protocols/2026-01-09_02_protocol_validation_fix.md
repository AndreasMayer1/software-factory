# Validation Fix Protocol

**Date**: 2026-01-09
**Task**: TASK-PROC-009-02
**Agent**: opus-4.5

## Summary

Fixed 9 validation errors that were caused by the simple YAML parser in `scripts/validate_meta.py` not correctly parsing nested list structures in trackable_items.

## Problem Analysis

### Initial State
- Validation showed: 9 errors, 49 warnings
- All 9 errors were about section IDs (SEC-06 through SEC-14) not existing in REQ-PROC-009
- However, REQ-PROC-009's requirements.md clearly defined SEC-01 through SEC-14 in its trackable_items

### Root Cause Investigation

Debugged the YAML parser output for REQ-PROC-009:
```
trackable_items: {'sections': [], '- id': 'SEC-14', 'name': 'Migration Strategy', ...}
```

The custom `_parse_simple_yaml()` function could not correctly parse nested list structures like:
```yaml
trackable_items:
  sections:
    - id: SEC-01
      name: "Overview"
      heading: "## Overview"
    - id: SEC-02
      ...
```

It was:
1. Returning `sections: []` (empty list)
2. Incorrectly extracting only the last entry's fields as top-level keys

## Solution

### Fix 1: Add PyYAML for Proper YAML Parsing

Modified `scripts/validate_meta.py` to:

1. **Import PyYAML conditionally**:
```python
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
```

2. **Use PyYAML when available**:
```python
if HAS_YAML:
    try:
        return yaml.safe_load(yaml_text)
    except yaml.YAMLError:
        return self._parse_simple_yaml(yaml_text)
```

3. **Handle BOM encoding**:
```python
if content.startswith('\ufeff'):
    content = content[1:]
```

### Fix 2: Handle Legacy Task Files

After PyYAML was enabled, it correctly parsed more files, which revealed that many old task files have `---` markers but not proper YAML frontmatter (old-style requirements source blocks).

Modified `validate_tasks()` to treat files without `task_id` as "no frontmatter" (warning instead of error):
```python
task_id = meta.get('task_id')
if not task_id:
    # Old-style frontmatter without proper meta info - treat as warning
    # These are legacy tasks that haven't been migrated yet (Task 3 scope)
    self.add_error(str(goal_file), "No YAML frontmatter found", "warning")
    continue
```

## Verification

After fixes:
```
============================================================
META INFORMATION VALIDATION
============================================================

Scanning requirements.md files...
  Found 37 requirements with valid frontmatter

Scanning goal.md files...
  Found 4 tasks with valid frontmatter

Validating coverage references...

============================================================
RESULTS
============================================================

Summary: 0 errors, 49 warnings
```

### Results Analysis

- **0 errors**: All 37 requirements.md files validated correctly
- **4 tasks with valid frontmatter**: The 4 tasks created for TASK-PROC-009-0x have proper frontmatter
- **49 warnings**: Expected - these are legacy task files without frontmatter (migrating them is Task 3's scope)

## Files Modified

1. `scripts/validate_meta.py`
   - Added PyYAML import (with fallback)
   - Updated `parse_yaml_frontmatter()` to use PyYAML and handle BOM
   - Updated `validate_tasks()` to treat missing task_id as warning

## Dependencies Added

- **PyYAML** (`pyyaml`): Required for correct nested YAML parsing
  - Installed via: `pip install pyyaml`
  - Version: 6.0.3

## Task Status

- **Migration Status**: COMPLETE (37/37 requirements migrated)
- **Validation Status**: PASSING (0 errors)
- **Next Step**: Task 3 (TASK-PROC-009-03) will migrate the 49 task goal.md files
