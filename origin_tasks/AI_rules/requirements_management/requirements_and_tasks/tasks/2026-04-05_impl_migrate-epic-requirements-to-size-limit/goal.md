---
task_id: TASK-PROC-009-14
type: impl
parent_requirement: REQ-PROC-009
urgency: 5
urgency_reason: U5-PROC
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-04-05
completed: 2026-04-05
effort: L
created: 2026-04-05
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Trim all 8 bloated epic requirements.md files to comply with the new 90-line body limit"
release_description: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
---

# Goal: Migrate Epic Requirements to 90-Line Size Limit

## Objective

Trim all existing epic-level `requirements.md` files that violate the new 90-line body limit introduced in the `requ-explore` skill (Epic Size Gate). Extract wrong-level content into existing or new `feat_*/requirements.md` files. All 8 violating epics must pass `python3 scripts/validate_epic_requirements.py` when done.

## Scope

### In Scope

8 epic requirements files currently failing validation:

| Epic | Lines | Path |
|---|---|---|
| `epic_plan_management` (therapist) | 761 | `functional/therapist/epic_plan_management/` |
| `epic_data_transfer` | 464 | `functional/shared/epic_data_transfer/` |
| `epic_security` | 369 | `functional/shared/epic_security/` |
| `epic_backup` | 356 | `functional/shared/epic_backup/` |
| `epic_data_input` | 267 | `functional/client/epic_data_input/` |
| `epic_plan_management` (client) | 241 | `functional/client/epic_plan_management/` |
| `epic_onboarding` (shared) | 102 | `functional/shared/epic_onboarding/` |
| `epic_crisis_safety` | 98 | `functional/shared/epic_crisis_safety/` |

Additionally, `epic_crisis_safety` lists 3 features with no corresponding `feat_*/` folder:
- `feat_crisis_message_field`
- `feat_crisis_safety_display`
- `feat_discreet_mode`

### Out of Scope

- The 6 already-compliant epics (must remain untouched)
- Rewriting or expanding feature requirements beyond receiving extracted epic content
- Functional changes to any feature behavior

## Acceptance Criteria

- [ ] `python3 scripts/validate_epic_requirements.py` exits 0 with no violations
- [ ] Each epic body stays within the allowed section whitelist (Overview, Purpose, Scope, Features, User Needs, Dependencies, Cross-Feature Invariants, Glossary, References)
- [ ] Wrong-level content (technical specs, architecture diagrams, testing requirements, platform details, step-by-step scenarios) moved to corresponding `feat_*/requirements.md`
- [ ] For each newly created feature folder: `requirements.md` created with `status: placeholder` + a follow-up explore task created
- [ ] No content is deleted — it must land somewhere (epic or feature)
- [ ] The 6 passing epics remain unchanged and still pass

## Approach

For each violating epic:
1. Read the epic's current content
2. Apply the content-type rule: cross-cutting → keep; feature-specific → extract
3. For each extracted block: find or create the target `feat_*/requirements.md`
4. Trim epic to compliant allowed sections only
5. Run validator after each epic to confirm progress

## Notes

- New rule defined in: `.claude/skills/requ-explore/skill.md` § "Epic Size Gate"
- Validator: `scripts/validate_epic_requirements.py`
- Content-type rule: cross-cutting invariants, grouping rationale, feature index → Epic; technical specs, examples, test requirements, platform details → Feature
