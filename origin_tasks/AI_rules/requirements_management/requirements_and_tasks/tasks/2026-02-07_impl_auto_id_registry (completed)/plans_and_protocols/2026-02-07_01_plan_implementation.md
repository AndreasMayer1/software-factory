# Implementation Plan: Auto-Update ID Registry Scripts

**Date**: 2026-02-07
**Task**: TASK-PROC-009-12
**Agent**: architecture-advisor-2026-02-07-001

## 1. Scope of Work

### Files to Create
1. `scripts/generate_id_registry.py` - Unified script generating both registries

### Files to Modify
2. `.claude/skills/setup-task/SKILL.md` - Add registry regeneration step
3. `.claude/skills/create-persona/skill.md` - Add registry regeneration step
4. `.claude/skills/create-scenario/skill.md` - Add registry regeneration step
5. `.claude/skills/create-user-flow/skill.md` - Add registry regeneration step

### Files to Generate (output)
6. `requirements_tasks/_meta/id_registry.md` - Requirements registry (overwritten)
7. `requirements_user_needs/_meta/id_registry.md` - User needs registry (new)

## 2. Architecture Strategy

### Decision: One Unified Script

**Choice**: Single `scripts/generate_id_registry.py` with `--requirements` and `--user-needs` flags.

**Why**: Both registries share 80% of the logic (YAML parsing, file scanning, markdown generation). A unified script with mode flags is simpler to maintain and call from skills. Each skill calls the appropriate mode.

### Script Architecture

```
generate_id_registry.py
├── parse_yaml_frontmatter()    # Reuse pattern from validate_meta.py
├── extract_name()              # Name from: YAML name > # Requirement: heading > folder path
├── scan_requirements()         # Scan requirements_tasks/**/requirements.md
├── scan_user_needs()           # Scan personas, scenarios, flows
├── generate_requirements_registry()  # Write requirements_tasks/_meta/id_registry.md
├── generate_user_needs_registry()    # Write requirements_user_needs/_meta/id_registry.md
└── main()                      # CLI: --requirements, --user-needs, --all
```

### YAML Parsing

Reuse the fallback approach from validate_meta.py:
- Try `yaml.safe_load()` if PyYAML available
- Fall back to simple regex-based parser for our specific format
- Handle BOM, missing frontmatter gracefully

### Name Extraction Priority
For requirements:
1. YAML `name:` field (if present)
2. First `# Requirement: [Name]` heading
3. First `# [Name]` heading (e.g., "# Requirements and Tasks Structure")
4. Folder name converted to Title Case

For user needs:
1. YAML `name:` field (always present in our format)
2. Folder name as fallback

### Registry Format

**Requirements registry** (matches current format):
- Overview table with category counts
- Per-category tables (PROC, NFUNC, FUNC) with ID, Path, Name
- Next Available IDs section
- Usage notes (static text)

**User needs registry** (new):
- Overview table with type counts
- Personas table: ID, Path, Name, Role, Status
- Scenarios table: ID, Path, Name, Persona, Status
- Flows table: ID, Path, Name, Status
- Next Available IDs section

## 3. Skill Integration Strategy

Each of the 4 skills will get a single instruction block added:

```
### N. Regenerate ID Registry (Just-in-Time)
Before reading the registry, regenerate it:
python scripts/generate_id_registry.py --[mode]
```

- `setup-task` -> `--requirements` (needs REQ-* IDs)
- `create-persona` -> `--user-needs` (needs PERSONA-* IDs)
- `create-scenario` -> `--user-needs` (needs SCEN-* IDs)
- `create-user-flow` -> `--user-needs` (needs FLOW-* IDs)

**Placement**: Right before the step that reads/generates IDs.

## 4. WHY Comments Requirements

1. **Script**: Why single script vs two - maintenance simplicity
2. **Script**: Why regex fallback for YAML - no PyYAML dependency guarantee
3. **Script**: Why name extraction has 4 fallback levels - inconsistent naming in codebase
4. **Skills**: Why regenerate before reading - just-in-time freshness guarantee

## 5. Testing Strategy

- Run script and verify output matches expected format
- Compare generated registry with current manual registry (should be superset)
- Verify next available IDs are correct
- Verify user needs registry includes all personas/scenarios/flows

## 6. Risks

1. **YAML parsing edge cases**: Mitigated by reusing proven pattern from validate_meta.py
2. **Name extraction inconsistency**: Mitigated by 4-level fallback with folder name as last resort
3. **Windows path handling**: Use pathlib for cross-platform compatibility
4. **Requirements without frontmatter**: Skip with warning (old/legacy files like feat_education)
