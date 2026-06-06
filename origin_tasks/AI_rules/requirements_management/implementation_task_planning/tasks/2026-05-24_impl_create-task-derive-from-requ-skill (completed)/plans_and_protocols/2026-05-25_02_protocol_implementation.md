# Protocol: Create task-derive-from-requ Skill

Date: 2026-05-25
Task: TASK-PROC-058-02
Session: b2120720-0746-49d1-a940-4c2e2f95f890
Automated: yes

## What was done

### 1. Created skill file
- `.claude/skills/task-derive-from-requ/SKILL.md` (9KB, ~150 lines)
- All 6 phases: Gather, Analyze, Plan, Review, Create, Validate
- Phase 1.5 (cross-ref gate) stubbed as deferred to TASK-PROC-058-03
- Mode selection: quick (1-2 tasks) vs full (≥3 uncovered ACs)
- Automated mode table with auto-accept and question.md escalation
- No-duplication enforcement table (AC-15)
- Unified plan format (SEC-04) with YAML example
- Coverage matrix blocking gate (AC-01)
- Verification task mandatory (AC-02)
- Sizing signals S1-S4 (AC-03)
- Enforcement-creates-violations detection (AC-06)
- Cross-package handling (AC-16)
- Covers-field repair (AC-09)
- Orchestration task pattern for >6 tasks or automated mode

### 2. Updated claude-route
- Added detection pattern for "decompose requirement" goal shapes
- Pattern: goal body contains "decompose requirement", "derive tasks from", "plan tasks for", "create tasks for" + references a requirement path or REQ-ID

### 3. Updated INDEX.md
- Added to Quick Reference table
- Added to task-* section

### 4. factory_flows.md
- No change needed — skill wraps existing REQ → TASK paths

## Design decisions

- **No new scripts created**: existing `coverage_report.py`, `create_orchestration_task.py`, `parse_task_creation_plan.py` are sufficient for initial implementation. Script extraction (`plan_validate.py`, `coverage_matrix.py`) deferred to usage experience.
- **Phase 1.5 deferred**: AC-17 cross-reference completeness gate is explicitly out of scope (TASK-PROC-058-03). Stubbed with clear "skip until implemented" note.
- **Plan-driven mode**: Phase 5 passes values to task-create/task-create-code — depends on TASK-PROC-058-04/05 for the receiving side to accept plan-driven inputs.

## AC coverage check

| Goal AC | Status |
|---------|--------|
| Skill file exists with 6 phases | Done |
| Mode selection (quick/full) | Done |
| Unified plan format (SEC-04) | Done |
| Coverage matrix blocking gate | Done |
| Verification task mandatory | Done |
| Enforcement-creates-violations detection | Done |
| No-duplication (AC-15) | Done |
| Phase 5 delegates to task-create/task-create-code | Done |
| Phase 6 invokes coverage_report.py | Done |
| Covers-field repair (AC-09) | Done |
| Cross-package (AC-16) | Done |
| Automated mode documented | Done |
| Orchestration task pattern | Done |
| claude-route detection pattern | Done |
| INDEX.md updated | Done |
