# Protocol: Auto-Update ID Registry Implementation

**Date**: 2026-02-07
**Agent**: architecture-advisor-2026-02-07-001
**Task**: TASK-PROC-009-12

## Work Performed

### 1. Analysis Phase
- Read goal.md and understood requirements
- Read `scripts/validate_meta.py` (reference for YAML parsing pattern)
- Read `scripts/generate_status_overview.py` (reference for folder scanning)
- Read current manual `requirements_tasks/_meta/id_registry.md`
- Read all 4 skills that need updating (setup-task, create-persona, create-scenario, create-user-flow)
- Analyzed YAML frontmatter patterns across:
  - requirements.md files (use `id:` field, inconsistent name extraction)
  - persona.md files (use `persona_id:` and `name:` fields)
  - scenario.md files (use `scenario_id:` and `name:` fields)
  - flow.md files (use `flow_id:` and `name:` fields)

### 2. Key Findings
- Manual registry is already out of sync (REQ-PROC-012 listed as "CodeGraph Integration" but actually maps to "Incrementally Improve Dr. Sarah Persona")
- Some requirements.md files have no YAML frontmatter (e.g., feat_donations, feat_education) - these are legacy
- Name extraction requires 4 fallback levels due to inconsistency
- No `requirements_user_needs/_meta/` directory exists yet - needs creation

### 3. Implementation

#### Created Files
1. **`scripts/generate_id_registry.py`** - Unified registry generation script
   - ~400 lines of Python
   - Supports `--requirements`, `--user-needs`, `--all` flags
   - YAML parsing with PyYAML fallback to simple regex parser
   - 4-level name extraction for requirements
   - Scans personas, scenarios, flows for user needs
   - Generates "Next Available IDs" per category
   - Generates per-persona next scenario IDs

2. **`plans_and_protocols/2026-02-07_01_plan_implementation.md`** - Architecture plan

#### Modified Files
3. **`.claude/skills/setup-task/SKILL.md`** - Added "Regenerate ID Registry" section before "Task ID Generation"
4. **`.claude/skills/create-persona/skill.md`** - Merged step 3 to include registry regeneration
5. **`.claude/skills/create-scenario/skill.md`** - Merged step 3 to include registry regeneration
6. **`.claude/skills/create-user-flow/skill.md`** - Merged step 3 to include registry regeneration

### 4. Testing Status
- Script needs to be run to verify output
- Awaiting execution permission

## Decisions Made
1. **One script, not two**: Both registries share scanning/parsing logic, mode flags are simpler
2. **Overwrite mode**: Registry is fully regenerated each time (git tracks history)
3. **WHY comments**: Added where non-obvious decisions exist (script header, name extraction, skill integration points)
4. **Skill placement**: Registry regeneration added immediately before ID generation step in each skill

## Remaining
- [x] Run script and verify generated registries
- [x] Verify output matches expected format

---

## 2026-02-07 14:35:49 - Verification & Quality Check

**Agent**: simple-implementation-orchestrator (Sonnet 4.5)
**Agent ID**: N/A (orchestrator, not resumable subagent)
**Action**: Verified implementation and ran quality checks

### Testing Performed
1. **Script execution**: Ran `python scripts/generate_id_registry.py --all`
   - ✅ Requirements registry generated: 57 requirements (27 PROC, 14 NFUNC, 16 FUNC)
   - ✅ User needs registry generated: 13 personas, 13 scenarios, 1 flow
   - ✅ Created `requirements_user_needs/_meta/` directory automatically
   - ✅ Both registries have proper headers warning against manual edits

2. **Quality verification**: Spawned quality-checker agent (af6ba9b)
   - ✅ All 7 acceptance criteria met
   - ✅ CLAUDE.md Section 5 compliance (WHY comments for non-obvious decisions only)
   - ✅ Python conventions followed
   - ✅ Cross-platform compatibility (tested on Windows)
   - ✅ All 4 skills correctly integrated with just-in-time regeneration
   - ✅ No blocking violations found

### Outcome
**Status**: PASS - Ready to commit

All deliverables complete:
- Script generates accurate registries from YAML frontmatter
- Next available IDs calculated correctly
- Skills integrated with just-in-time regeneration
- Manual updates eliminated
- Git history tracks changes

### Pre-existing Issues Noted
- Duplicate IDs exist in source files (PERSONA-008, REQ-PROC-010, REQ-PROC-013)
- These are NOT caused by this implementation
- Validation script (`validate_meta.py`) will catch these

### Next Step
Ready for complete-task skill and git commit.
