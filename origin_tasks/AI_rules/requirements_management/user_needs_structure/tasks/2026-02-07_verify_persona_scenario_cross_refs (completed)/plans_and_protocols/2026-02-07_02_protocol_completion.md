# Protocol: Persona-Scenario Cross-Reference Verification - COMPLETE

**Date**: 2026-02-07
**Task**: TASK-PROC-010-14
**Agent**: modify-user-needs skill (direct execution mode)
**Status**: ✅ COMPLETE

## Summary

Verified all 13 personas for scenario cross-references and fixed all inconsistencies.

**Result**:
- ✅ Fixed 5 personas with missing scenario links
- ✅ Updated `create-scenario` skill to enforce bidirectional linking
- ✅ All personas now correctly reference their scenarios

## Changes Made

### 1. Persona.md Files Updated (5 files)

| Persona | File | Scenarios Added |
|---------|------|-----------------|
| Dr. med. Turan (PERSONA-012) | `personas/dr_med_turan/persona.md` | 2 scenarios |
| Prof. Dr. Weber (PERSONA-011) | `personas/prof_dr_weber/persona.md` | 2 scenarios |
| Max (PERSONA-002) | `personas/max_client/persona.md` | 3 scenarios |
| Sophie (PERSONA-010) | `personas/sophie_structure_seeker/persona.md` | 2 scenarios |
| Jana (PERSONA-014) | `personas/jana_high_strung/persona.md` | 2 scenarios |

**Total**: 11 scenario links added

### 2. Skill Updated

**File**: `.claude/skills/create-scenario/skill.md`

**Change**: Added new step 7 "Update Parent Persona's Related Scenarios"

**What it does**:
- After creating a scenario, automatically updates parent persona.md
- Adds scenario link to "Related Scenarios" section
- Replaces placeholder text or appends to existing list

**Format**:
```markdown
### 7. Update Parent Persona's Related Scenarios

Add scenario link to parent persona.md:

1. Read persona.md
2. Find "## Related Scenarios" section
3. Replace placeholder ("*To be created*") or append to list:
   ```markdown
   - [Scenario Name](scenarios/[folder]/scenario.md)
   ```
4. Write back persona.md
```

### 3. Final Verification

All 13 personas checked:

**With scenarios (6 personas)** - All correctly linked:
- ✅ PERSONA-001 (Dr. Sarah): 2 scenarios
- ✅ PERSONA-012 (Dr. med. Turan): 2 scenarios [FIXED]
- ✅ PERSONA-011 (Prof. Dr. Weber): 2 scenarios [FIXED]
- ✅ PERSONA-002 (Max): 3 scenarios [FIXED]
- ✅ PERSONA-010 (Sophie): 2 scenarios [FIXED]
- ✅ PERSONA-014 (Jana): 2 scenarios [FIXED]

**Without scenarios (7 personas)** - Correct placeholder:
- ✅ PERSONA-003 (David Structure Seeker)
- ✅ PERSONA-004 (Elias Skeptical Guardian)
- ✅ PERSONA-005 (Hanna Sleepless)
- ✅ PERSONA-007 (Lisa Waitlist Bridger)
- ✅ PERSONA-009 (Michael High Performer)
- ✅ PERSONA-006 (Nina Energy Budgeter)
- ✅ PERSONA-013 (System Maintenance) - no section, acceptable

## Acceptance Criteria Status

From goal.md:

- [x] Alle Personas durchgegangen und Scenario-Links überprüft
- [x] Fehlende Links in persona.md ergänzt
- [x] `create-scenario` Skill auf Persona-Update-Anweisung geprüft
- [x] Falls fehlend: Anweisung in Skill ergänzt
- [x] Weitere relevante Skills identifiziert und aktualisiert (only create-scenario needs update)
- [x] Dokumentation der Änderungen in protocol.md
- [ ] Git commit mit allen Änderungen (pending user action)

## Files Modified

1. `personas/dr_med_turan/persona.md`
2. `personas/prof_dr_weber/persona.md`
3. `personas/max_client/persona.md`
4. `personas/sophie_structure_seeker/persona.md`
5. `personas/jana_high_strung/persona.md`
6. `.claude/skills/create-scenario/skill.md`
7. `requirements_tasks/.../2026-02-07_verify_persona_scenario_cross_refs/plans_and_protocols/2026-02-07_01_analysis.md` (analysis doc)
8. `requirements_tasks/.../2026-02-07_verify_persona_scenario_cross_refs/plans_and_protocols/2026-02-07_02_protocol_completion.md` (this file)

## Next Steps

1. User reviews changes
2. Git commit with task reference: `git commit -m "task: Verify and fix persona-scenario cross-references (TASK-PROC-010-14)"`
3. Mark task as complete via `complete-task` skill

## Notes

- No review_status changes were made to persona.md files (these are simple link additions, not content modifications)
- The `modify-user-needs` skill itself was not modified (it handles more complex content changes; simple cross-reference additions don't need the full cascade workflow)
- Future scenario creations will automatically maintain bidirectional links via updated `create-scenario` skill
