---
task_id: TASK-PROC-045-01
type: explore
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
started: 2026-04-26
completed: 2026-04-26
effort: M
created: 2026-04-26
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Explore and define requirements structure quality rules; write requirements.md for REQ-PROC-045; draft follow-on impl task for script-based validation and skill integration"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore — must evaluate structure across all requirement categories, define ordering principles, and decide which checks to automate vs. leave to LLM judgment
writes_requirements: true
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Explore Requirements Structure Quality Rules

## Objective

Define a comprehensive set of rules governing how requirements must be structured
in `requirements_tasks/`. The rules should address maintainability, extensibility,
readability, and LLM-processability for both human and AI readers.

Deliverables:
1. Create `requirements.md` for REQ-PROC-045 — the authoritative requirement for requirements structure quality
2. Draft a structure guide / rulebook (can live in `plans_and_protocols/` or inline in requirements.md)
3. Create a follow-on impl task (`TASK-PROC-045-02`) that implements: script-based validation of the rules + integration into existing skills (`requ-explore`, `release-begin-impl`, etc.)

## Context

During a review session the following structural problem was identified:
currently there are no explicit, machine-checkable rules for how requirements must
be organized. The `validate_epic_requirements.py` script checks two things (epic body
length, feat_* folder presence), but larger questions — "is this an epic or a feature?",
"is this in the right category?", "does the folder hierarchy match the semantic level?" —
are unchecked.

The app provider stakeholder (process owner) wants:
- Good requirements structure as a quality property of the factory itself
- Rules that cover: folder hierarchy, naming conventions, metadata completeness,
  semantic level (epic vs. feature vs. requirement), cross-category correctness
- As much script-based enforcement as possible (low LLM overhead for routine checks)
- `requ-explore` must follow these rules when writing new requirements
- Validation integrated at sensible workflow points (not just on-demand)

## Prior Analysis (Session 2026-04-26)

Script-checkable rules already identified:

| Rule | Current state |
|------|--------------|
| `epic_*/` must have ≥1 `feat_*/` child (or draft status) | validate_epic_requirements.py (partial) |
| Every `feat_*/` must have `requirements.md` | not checked |
| No `feat_*` directly under `functional/` (must be under `epic_*/`) | not checked |
| No `epic_*` nested inside another `epic_*/` (max 2 levels) | not checked |
| Requirement IDs in registry must match frontmatter `id:` | partial (registry generation) |
| Category matches content: `functional/` has no architecture requirements | not checked |
| Epic body ≤ 90 lines | validate_epic_requirements.py |
| Listed features in epic have `feat_*/` folders | validate_epic_requirements.py |

LLM-judgment rules (harder to script):
- Is this epic really an epic (or an over-specific feature)?
- Is this feature in the right epic?
- Does the folder name reflect the requirement's content?

Ordering/naming conventions to define:
- What naming scheme for `epic_*` and `feat_*` folders?
- How deep can the hierarchy go?
- When is a standalone requirement (no epic/feat wrapper) acceptable?
- Must requirements use English exclusively? Any exceptions?

## Scope

### In Scope
- Define the complete rules for requirement folder structure (hierarchy, naming, category assignment)
- Define metadata completeness rules (required frontmatter fields, allowed values)
- Identify which rules are script-checkable and which require LLM judgment
- Write `requirements.md` for REQ-PROC-045 covering these rules as trackable ACs
- Create impl task TASK-PROC-045-02 for: extending `validate_epic_requirements.py` + integration into `release-begin-impl` Phase 0 and `requ-explore` completion check

### Out of Scope
- Actual implementation of scripts (that is TASK-PROC-045-02)
- Changes to existing requirements (retrospective validation is a separate decision)
- User needs structure (`requirements_user_needs/`) — covered by REQ-PROC-010

## Acceptance Criteria

- [ ] `requirements.md` for REQ-PROC-045 exists at `requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md`
- [ ] requirements.md contains: complete list of structure rules as trackable ACs, split into "script-checkable" and "convention/LLM" categories
- [ ] A structure rulebook section (can be inline in requirements.md or in plans_and_protocols/) covering ordering principles, folder naming, hierarchy depth, metadata requirements
- [ ] Follow-on impl task `TASK-PROC-045-02` created with concrete AC-level coverage from requirements.md
- [ ] User has approved the requirements.md before closing this task

## Notes

- Stakeholder: app provider / process owner (not end user)
- This requirement is about the factory's internal quality, not the app's features
- The explore task may uncover that existing `validate_epic_requirements.py` needs only minor extension, or it may find larger structural gaps — the impl scope should reflect findings
- Priority U3/I4: important for LLM session quality (unstructured requirements cause navigation errors), but not blocking current release work
