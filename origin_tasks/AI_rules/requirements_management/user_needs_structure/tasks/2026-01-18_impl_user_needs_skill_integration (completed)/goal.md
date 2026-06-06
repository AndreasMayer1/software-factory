---
task_id: TASK-PROC-010-03
type: impl
parent_requirement: REQ-PROC-010
urgency: 3
urgency_reason: U3-PLANNED
impact: 4
impact_reason: I4-IMPROVEMENT
status: completed
effort: S
created: 2026-01-18
completed: 2026-01-18
after: [TASK-PROC-010-01]
awaiting: []
covers:
  sections: [SEC-05, SEC-06, SEC-07]
scope_description: "Implement validation script enhancements for user needs (skills already completed in Phase 5)"
requirements_version:
  commit: 33cf97e602a35c02b85f57a0c1347a15b7d09758
  file: ../requirements.md
---

# Goal: Implement User Needs Validation Scripts

## Objective

Implement the validation script enhancements defined in Phase 5 planning document.

**IMPORTANT**: Skills were already implemented during Phase 5 execution by Agents 2 and 3. This task only covers the remaining validation script work.

**What's Already Done** ✅:
- New skills created: create-persona, create-scenario, create-user-flow
- Existing skills enhanced: setup-task, verify-quality, explore-requirements
- All skills are functional and ready to use

**What Remains** (this task):
- Enhance validate_meta.py with user needs validation
- Enhance generate_user_needs_status.py with coverage reporting

**Plan Reference**: `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-18_16_opus_plan_phase5.md`

**Specification References**:
- Agent 4: Validation script enhancements (plan lines 595-783)
- Agent 4 Protocol: Detailed implementation specs in `plans_and_protocols/2026-01-18_20_protocol_phase5_agent4.md`

## Scope

### In Scope

**Validation Scripts** (modify `scripts/`):

1. **validate_meta.py** - Add user needs validation
   - Spec: Plan Agent 4, lines 601-653; Protocol Product 1
   - Add UserNeedsMeta dataclass
   - Add validate_user_needs() function
   - Add validate_epic_user_needs_references() function
   - Add validate_cross_reference_symmetry() function
   - Enhance output format with user needs summary

2. **generate_user_needs_status.py** - Add coverage reporting
   - Spec: Plan Agent 4, lines 655-681; Protocol Product 2
   - Add cross-reference validation
   - Add epic coverage report
   - Add orphan flow detection
   - Add implementation progress tracking

### Out of Scope

**Skills** (already completed in Phase 5):
- Creating new skills (create-persona, create-scenario, create-user-flow) - ✅ Done by Agent 2
- Enhancing existing skills (setup-task, verify-quality, explore-requirements) - ✅ Done by Agent 3

**Other**:

- Creating actual user needs documents (completed in Phases 1-4)
- Modifying existing epic/feature requirements.md files (examples only in Phase 5 Agent 1)
- Implementing modify-persona/scenario/flow skills (separate task from CHANGE_PROPAGATION.md)
- Backfilling all epics with user_needs references (separate effort)

## Acceptance Criteria

**Validation Scripts**:
- [ ] `scripts/validate_meta.py` has UserNeedsMeta dataclass
- [ ] `scripts/validate_meta.py` has validate_user_needs() function
- [ ] `scripts/validate_meta.py` has validate_epic_user_needs_references() function
- [ ] `scripts/validate_meta.py` has validate_cross_reference_symmetry() function
- [ ] `scripts/validate_meta.py` output includes user needs summary
- [ ] `scripts/generate_user_needs_status.py` has epic coverage report
- [ ] `scripts/generate_user_needs_status.py` has orphan flow detection
- [ ] `scripts/generate_user_needs_status.py` has implementation progress section
- [ ] Both scripts tested and produce expected output

**Quality**:
- [ ] All code follows existing patterns in respective files
- [ ] No regressions in existing functionality
- [ ] Manual testing confirms all features work
- [ ] CLAUDE.md updated if new skill usage patterns needed

## Implementation Steps

### Phase 1: Enhance Validation Scripts (Agent 4 Specs)

1. **Enhance validate_meta.py**:
   - Read current `scripts/validate_meta.py`
   - Read detailed specification from protocol Product 1
   - Add UserNeedsMeta dataclass
   - Add validate_user_needs() function
   - Add validate_epic_user_needs_references() function
   - Add validate_cross_reference_symmetry() function
   - Update run() method with new validation calls
   - Update output format
   - Test: Run script and verify output

2. **Enhance generate_user_needs_status.py**:
   - Read current `scripts/generate_user_needs_status.py`
   - Read detailed specification from protocol Product 2
   - Add cross-reference validation methods
   - Add epic coverage report generation
   - Add orphan flow detection
   - Add implementation progress tracking
   - Update generate_report() method
   - Test: Run script and verify output

### Phase 2: Testing & Documentation

3. **Test all changes**:
   - Run validate_meta.py on current codebase
   - Run generate_user_needs_status.py
   - Verify no regressions in existing functionality
   - Check that both scripts handle edge cases gracefully

4. **Update documentation**:
   - Document any new script features in script docstrings
   - Update README.md if validation rules changed

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-010-01 | complete | Phase 5 fully executed (all 4 agents) |
| Phase 5 Agent 1 | complete | Cross-reference documentation in README.md |
| Phase 5 Agent 2 | complete | New skills CREATED (not just specified) |
| Phase 5 Agent 3 | complete | Existing skills ENHANCED (not just specified) |
| Phase 5 Agent 4 | complete | Validation script specifications created |

## References

### Plan Documents
- **Opus Plan**: `../2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-18_16_opus_plan_phase5.md`
- **Agent 1 Protocol**: `../2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-18_17_protocol_phase5_agent1.md`
- **Agent 2 Protocol**: `../2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-18_18_protocol_phase5_agent2.md`
- **Agent 3 Protocol**: `../2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-18_19_protocol_phase5_agent3.md`
- **Agent 4 Protocol**: `../2026-01-17_explore_implement_user_needs_structure/plans_and_protocols/2026-01-18_20_protocol_phase5_agent4.md` (this task's specifications)

### Completed Work (Reference Only)

**New Skills** (✅ Already created by Agent 2):
- `.claude/skills/create-persona/skill.md`
- `.claude/skills/create-scenario/skill.md`
- `.claude/skills/create-user-flow/skill.md`

**Skill Enhancements** (✅ Already done by Agent 3):
- `.claude/skills/setup-task/skill.md` - has User Needs Reference Check section
- `.claude/skills/verify-quality/skill.md` - has user needs verification
- `.claude/skills/explore-requirements/skill.md` - has User Needs Analysis section

**Validation Script Specifications** (this task implements these):
- validate_meta.py: Plan lines 601-653 + Agent 4 Protocol Product 1
- generate_user_needs_status.py: Plan lines 655-681 + Agent 4 Protocol Product 2

### Existing Patterns
- Skill structure: `.claude/skills/setup-task/skill.md`
- Validation script: `scripts/validate_meta.py`
- Status generator: `scripts/generate_user_needs_status.py`

## Notes

### Implementation Focus

**This task only implements validation scripts**. All skills were already created/enhanced during Phase 5 execution.

### Testing Strategy

**Script testing**:
```bash
# Test validate_meta.py
python scripts/validate_meta.py --verbose

# Test generate_user_needs_status.py
python scripts/generate_user_needs_status.py
cat requirements_user_needs/STATUS.md
```

### Quality Checks

**Before completion**:
- [ ] All acceptance criteria met
- [ ] No Python syntax errors in scripts
- [ ] No broken references in skill.md files
- [ ] Existing skills still work
- [ ] Existing scripts still work
- [ ] Manual testing confirms new features work
- [ ] Protocol.md logged with implementation notes

---

**Task Status**: PENDING
**Created By**: Agent 4 (validation-enhancement-agent-2026-01-18-004)
**Modified By**: Factory Orchestrator (corrected scope - skills already implemented)
**Created Date**: 2026-01-18
**Parent Task**: TASK-PROC-010-01
