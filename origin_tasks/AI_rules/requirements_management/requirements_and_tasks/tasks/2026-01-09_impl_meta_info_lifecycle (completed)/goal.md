---
task_id: TASK-PROC-009-04
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
effort: M
created: 2026-01-09
completed: 2026-01-10
after: [TASK-PROC-009-01]
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-13]
scope_description: "Implement lifecycle processes in skills and create enhanced status overview script"
requirements_version:
  commit: f7add7a
  file: ../requirements.md
---

# Goal: Meta Information Lifecycle Processes

## Objective

Implement the meta information lifecycle processes defined in `requirements.md` by:
1. Updating relevant skills to enforce lifecycle rules
2. Creating an enhanced status overview script with multiple modes
3. Ensuring all processes are integrated and validated
Bonus: Update documentation in requirements_tasks\README.md.

## Requirements Summary

The parent requirement now defines (SEC-LIFECYCLE):
- **Creating New Requirements**: Priority decision trees, effort estimation, trackable_items
- **Creating New Tasks**: ID generation, priority inheritance, covers prompting
- **Completing Tasks**: Status updates, requirement status propagation
- **Quality Gates**: Meta information validation
- **When Requirements Change**: ID immutability, change management
- **Status Overview Reports**: Multiple modes (summary, priority, coverage, blockers, sprint, full)

For complete requirements:
```
git show f7add7a:requirements_tasks/process/AI_rules/requirements_management/requirements_and_tasks/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

#### 1. Update `setup-task` Skill

Add to `.claude/skills/setup-task/skill.md`:
- [ ] Reference to priority decision trees in requirements.md
- [ ] Guidance: "Read SEC-LIFECYCLE in parent requirements for priority determination"
- [ ] Effort estimation guidance
- [ ] Prompt sequence for covers selection

#### 2. Update `complete-task` Skill

Add to `.claude/skills/complete-task/skill.md`:
- [ ] Update YAML frontmatter in goal.md:
  - Set `status: completed`
  - Set `completed: YYYY-MM-DD`
- [ ] Check if all tasks for requirement are completed → update requirement status
- [ ] Run validation script after completion
- [ ] Trigger status overview regeneration

#### 3. Update `verify-quality` Skill

Add to `.claude/skills/verify-quality/SKILL.md`:
- [ ] Check YAML frontmatter exists in goal.md
- [ ] Validate required fields present (task_id, parent_requirement, status, covers)
- [ ] Validate covers references point to existing trackable_items
- [ ] Report meta information issues in audit report

#### 4. Create Enhanced Status Overview Script

Create `scripts/generate_status_overview.py`:
- [ ] Parse YAML frontmatter from requirements.md and goal.md files
- [ ] Support multiple modes via command-line arguments:

| Mode | Flag | Output |
|------|------|--------|
| Summary | `--summary` | Quick stats table: counts, coverage % |
| Priority | `--priority` | Tasks sorted by priority score (urgency×10+impact) |
| Coverage | `--coverage` | Coverage % per requirement, gaps highlighted |
| Blockers | `--blockers` | Tasks with status=blocked or U5 urgency |
| Sprint | `--sprint` | Tasks with U3-SPRINT or higher urgency |
| Full | `--full` | Complete report combining all sections |

- [ ] Additional options:
  - `--output PATH` - Custom output file (default: requirements_tasks/STATUS.md)
  - `--format md|json` - Output format
  - `--category FUNC|NFUNC|PROC` - Filter by category
  - `--include-legacy` - Include files without YAML frontmatter (folder-based status)

- [ ] Backward compatibility: Fall back to folder naming conventions if no YAML

#### 5. Update requirements_tasks\README.md

- [ ] Readme reflects the additions and changes to how requirements and tasks are structured and managed. 

#### 6. Integration Testing

- [ ] Test setup-task with new priority guidance
- [ ] Test complete-task updates YAML correctly
- [ ] Test verify-quality catches missing/invalid meta info
- [ ] Test all status overview modes produce valid output
- [ ] Verify scripts work on Windows

### Out of Scope

- Actual migration of files (Tasks 2 & 3)
- Changing the meta information schema
- Modifying existing requirements content

## Deliverables

1. Updated `.claude/skills/setup-task/skill.md`
2. Updated `.claude/skills/complete-task/skill.md`
3. Updated `.claude/skills/verify-quality/SKILL.md`
4. New `scripts/generate_status_overview.py`
5. Updated `requirements_tasks\README.md`
6. Integration tests documentation

## Acceptance Criteria

- [ ] setup-task skill references priority decision trees
- [ ] complete-task skill updates YAML frontmatter status
- [ ] complete-task skill checks/updates requirement status when all tasks complete
- [ ] verify-quality skill validates meta information
- [ ] Status overview script supports all 6 modes
- [ ] Status overview script has backward compatibility with folder naming
- [ ] All scripts run without errors on Windows
- [ ] Documentation updated for new script usage

## Implementation Notes

### Status Overview Script Modes - Detailed

**`--summary` Mode**:
```markdown
# Status Summary

| Category | Requirements | Tasks | Open | Completed | Coverage |
|----------|--------------|-------|------|-----------|----------|
| FUNC     | 14           | 25    | 8    | 17        | 45%      |
| NFUNC    | 14           | 12    | 3    | 9         | 62%      |
| PROC     | 9            | 15    | 2    | 13        | 78%      |
| **Total**| **37**       | **52**| **13**| **39**   | **58%**  |
```

**`--priority` Mode**:
```markdown
# Priority Queue

| Score | Task ID | Requirement | Status | Urgency | Impact |
|-------|---------|-------------|--------|---------|--------|
| 55    | TASK-FUNC-005-01 | Plan Evaluation View | in_progress | U5-BLOCK | I5-MVP |
| 54    | TASK-PROC-009-02 | Meta Migration | pending | U5-PROC | I4-DEBT |
...
```

**`--coverage` Mode**:
```markdown
# Coverage Report

## REQ-FUNC-005: Plan Evaluation View
Coverage: 25% (3/12 AC)
- [x] AC-01: Displays questionnaire results - TASK-FUNC-005-01
- [ ] AC-02: Simple Mode shows basic charts - **GAP**
...
```

**`--blockers` Mode**:
```markdown
# Blockers & Critical Tasks

## Blocked Tasks
| Task | Blocked By | Since |
|------|------------|-------|
| TASK-FUNC-007-02 | TASK-FUNC-007-01 | 2026-01-05 |

## Critical (U5)
| Task | Urgency Reason | Status |
|------|----------------|--------|
| TASK-PROC-009-01 | U5-PROC | in_progress |
```

**`--sprint` Mode**:
```markdown
# Sprint Focus (U3+)

## Must Do (U5)
- TASK-PROC-009-01: Meta Info Foundation

## Should Do (U4)
- TASK-PROC-009-02: Requirements Migration

## Nice to Have (U3)
- TASK-FUNC-005-03: Advanced Features
```

### Backward Compatibility

The script should work even if files don't have YAML frontmatter:
1. First try to parse YAML frontmatter
2. If no frontmatter, fall back to folder naming:
   - `_(completed)` suffix → status: completed
   - `_(superseded)` suffix → status: cancelled
   - No suffix → status: in_progress or pending
3. Report which files are missing frontmatter (for migration tracking)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-009-01 | completed | Foundation (scripts, registry) |
| requirements.md update | completed | Lifecycle section added |

## Notes

- The new Python script will eventually replace the PowerShell script
- Keep PowerShell script for backward compatibility during migration
- Python chosen for cross-platform compatibility and YAML parsing
- Consider adding `--watch` mode for continuous monitoring in future

---

## Process Flow After Implementation

```
NEW TASK CREATION                    TASK COMPLETION
─────────────────                    ───────────────

User: "Create task"                  User: "Complete task"
        │                                    │
        ▼                                    ▼
┌───────────────┐                   ┌───────────────┐
│  setup-task   │                   │ complete-task │
│    skill      │                   │    skill      │
└───────┬───────┘                   └───────┬───────┘
        │                                    │
        ▼                                    ▼
1. Read parent req ID              1. Update goal.md YAML
2. Show priority decision trees       - status: completed
3. Ask for urgency/impact             - completed: date
4. Ask for covers selection        2. Check all tasks done?
5. Generate goal.md with YAML         - Yes → update req status
6. Run validate_meta.py            3. Run validate_meta.py
        │                          4. Run generate_status_overview.py
        ▼                                    │
    ✓ Ready                                  ▼
                                        ✓ Complete

QUALITY CHECK
─────────────

Before any commit:
        │
        ▼
┌───────────────┐
│verify-quality │
│    skill      │
└───────┬───────┘
        │
        ▼
1. Check code guidelines
2. Check tests exist
3. Check WHY comments
4. **Check meta info:**           ← NEW
   - YAML frontmatter exists
   - Required fields present
   - covers references valid
        │
        ▼
    ✓ GREEN or ✗ RED
```
