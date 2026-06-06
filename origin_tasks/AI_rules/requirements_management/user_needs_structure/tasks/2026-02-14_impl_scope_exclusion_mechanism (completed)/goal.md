---
task_id: TASK-PROC-010-15
type: impl
parent_requirement: REQ-PROC-010
urgency: 5
urgency_reason: U5-PROC
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-02-14
effort: M
created: 2026-02-14
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: [SEC-03, SEC-04, SEC-08]
scope_description: "Add scope_exclusions mechanism to persona and scenario documents + update relevant skills"
requirements_version:
  commit: a210650
  file: ../requirements.md
---

# Goal: Scope Exclusion Mechanism for Personas and Scenarios

## Objective

Add a standardized "Won't Support (for now)" mechanism at the persona and scenario level in `requirements_user_needs/`. Currently, intentional scope decisions can only be documented at the epic/feature/flow level via Deviation Documentation (README_14). This gap means there is no way to record early-stage decisions like "this persona use case is explicitly out of scope" before any epic or scenario is written.

## Scope Overview

**Affected Layers**: Process documentation + Claude Code skills (no Flutter code)
**Estimated Files**: ~6-8 files
**Patterns to Follow**: Existing `scope_exclusions` concept from README_14_DEVIATION_DOCUMENTATION.md; YAML frontmatter conventions from existing persona.md and scenario.md files

## Background & Motivation

When defining personas and scenarios, it is often clear that certain use cases or behaviors will NOT be supported in the app — at least for the current version. Without a formal mechanism:
- These decisions are undocumented and easily forgotten
- Scenarios might be written unnecessarily for excluded use cases
- AI agents might flag "missing scenarios" for intentionally excluded areas

**Primary exclusion level**: Persona (preferred — exclude early, before scenarios are created)
**Secondary level**: Scenario (when an exclusion only becomes apparent while writing the scenario)

## What to Implement

### 1. README Guideline (new file)
Create `requirements_user_needs/README_15_SCOPE_EXCLUSIONS.md` (or next available number) documenting:
- The concept and when to use it
- Difference between persona-level vs. scenario-level exclusions
- YAML schema for `scope_exclusions` field
- Reason taxonomy: `technical` | `effort` | `business` | `strategic`
- Optional `reconsider_in` field (e.g., `"v2.0"`, `"post-MVP"`)
- Examples for both persona and scenario
- Relationship to existing Deviation Documentation (README_14) — exclusions are upstream of deviations

### 2. Persona Template Update
Add `scope_exclusions` section to persona YAML frontmatter schema:
```yaml
scope_exclusions:
  - area: "Brief description of the excluded use case"
    reason: technical | effort | business | strategic
    reason_detail: "Optional explanation"
    reconsider_in: "v2.0"  # optional
```
If a persona has `scope_exclusions`, scenarios for those areas MUST NOT be created.

### 3. Scenario Template Update
Add `scope_exclusions` section to scenario YAML frontmatter schema (same structure as persona level).
Use case: A specific behavior within a scenario is excluded, but the scenario itself exists.

### 4. Skill Updates
Update the following Claude Code skills to:
- **create-persona**: Include `scope_exclusions: []` in generated persona template; mention in instructions that exclusions can be added during creation
- **create-scenario**: Before creating a scenario, check the parent persona's `scope_exclusions` — warn/block if the scenario would cover an excluded area. Include `scope_exclusions: []` in generated scenario template
- **modify-user-needs**: Support adding/modifying `scope_exclusions` entries as a modification type

## Acceptance Criteria

- [ ] `README_15_SCOPE_EXCLUSIONS.md` exists with complete documentation
- [ ] Persona YAML schema includes `scope_exclusions` field (documented + in template)
- [ ] Scenario YAML schema includes `scope_exclusions` field (documented + in template)
- [ ] `create-persona` skill generates `scope_exclusions: []` in new personas
- [ ] `create-scenario` skill checks parent persona exclusions before proceeding
- [ ] `modify-user-needs` skill supports modifying `scope_exclusions`
- [ ] The README clearly explains when to use persona-level vs. scenario-level exclusions
- [ ] At least one example each for persona-level and scenario-level exclusion is documented

## Out of Scope

- Retroactively adding `scope_exclusions` to existing personas/scenarios (separate task if needed)
- Changes to epic/feature/flow Deviation Documentation (README_14) — this is upstream, not a replacement
- Flutter app code changes

## Dependencies

None — this is a standalone process/documentation task.

## Notes

- Check current README numbering in `requirements_user_needs/` before creating README_15 (verify the next available number)
- The `create-scenario` skill guard against excluded areas should be a soft warning (inform + ask to proceed), not a hard block — the user may intentionally override
- Skill files are in `.claude/skills/[name]/skill.md` directories
```
git show a210650:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```

Current requirements: ../requirements.md
