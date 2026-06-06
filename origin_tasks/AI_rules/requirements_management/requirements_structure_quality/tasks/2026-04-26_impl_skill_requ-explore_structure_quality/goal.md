---
task_id: TASK-PROC-045-04
type: impl
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: pending
effort: S
created: 2026-04-26
after: [TASK-PROC-045-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-08]
  sections: [SEC-01, SEC-02, SEC-03, SEC-05]
scope_description: "Integrate structure quality rules and validation into requ-explore (Phase 2.1 naming guidance + Phase 2.5 validation call) and requ-derive-from-flow (folder path naming guidance)"
release_description: ""
requirements_version:
  commit: ""
  file: ../../requirements.md
---

# Goal: Integrate Structure Quality into requ-explore and requ-derive-from-flow

## Objective

Update two requirement-authoring skills so that REQ-PROC-045 naming conventions and structural rules are actively applied when requirements are created or modified — not just as a post-hoc validation but as embedded guidance during authoring.

Deliverables:
1. **`requ-explore` Phase 2.1** — add explicit structural placement step that references REQ-PROC-045 SEC-01 through SEC-05 and runs the LLM judgment checklist before the author finalises the folder structure.
2. **`requ-explore` Phase 2.5 Quality Check** — add call to the validation script (scoped to the newly written requirement path), blocking task completion on violations (AC-08).
3. **`requ-derive-from-flow`** — add naming convention guidance at the point where the skill suggests target folder paths, referencing REQ-PROC-045 SEC-01 (WHO–WHAT pattern, vocabulary from user flows).

## Scope

### In Scope
- `.claude/skills/requ-explore/skill.md`: Phase 2.1 and Phase 2.5 changes (see detail below)
- `.claude/skills/requ-derive-from-flow/skill.md`: target folder naming guidance
- Both changes must be minimal additions — no restructuring of existing skill steps

### Out of Scope
- Changes to `requ-explore` Phase 1 investigation logic
- Other skills (release-begin-impl handled by TASK-PROC-045-05)
- Fixing pre-existing requirement structural violations

## Exact Changes Required

### requ-explore — Phase 2.1 (Determine Scope and Structure)

After the existing "Epic vs Feature Decision" table, add a new step:

**"Structure Quality Gate (REQ-PROC-045)"**
Before creating any folder, apply the LLM Judgment Checklist from REQ-PROC-045 SEC-05:

Naming questions (answer must be YES):
1. Is the folder name a domain noun from the user's vocabulary? (See `requirements_user_needs/user_flows/` for domain nouns)
2. If epic: name three features expected inside — do they predict the content?
3. Do sibling epic names cluster related and separate unrelated ones visually?

Demarcation questions (for epics only):
4. Independent value test: can users get value from this epic without a sibling?
5. Domain entity test: all features serve the same domain entity or user goal?
6. If same-named epic exists under another grouping: do the user goals match (shared name is correct), or differ (rename needed)?

Hierarchy questions:
7. Sub-grouping needed? (≥4 sibling epics with shared sub-domain)
8. Grouping folder correct (right persona / domain area)?
9. Standalone feature: no plausible second feature that would justify an epic?

Organisational:
10. Any new non-prefixed folder inside epic_* with requirements.md? → must use feat_* prefix (AC-09).

If any answer is NO or uncertain → surface to user before proceeding.

Reference: REQ-PROC-045 at `requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md`

### requ-explore — Phase 2.5 (Quality Check)

Add to the quality checklist:
- [ ] Run `python3 scripts/validate_epic_requirements.py --path [requirement-folder-path]` (scoped to the new/modified requirement's parent folder). If violations reported → fix before proceeding. Pre-existing violations in *other* folders are not blocking.

### requ-derive-from-flow — Target Folder Naming

At the step where the skill selects or proposes target folder paths for gaps, add:

"Apply WHO–WHAT naming (REQ-PROC-045 SEC-01): grouping folder = who benefits (persona or domain area); epic/feature name = domain concept noun from the flow vocabulary. Verify the proposed path against the LLM Judgment Checklist questions 1–3 before writing the goal.md."

## Acceptance Criteria

- [ ] AC-08: `requ-explore` quality check invokes the validation script scoped to the new requirement; task cannot close while violations exist
- [ ] SEC-01 (Naming Conventions): requ-explore Phase 2.1 actively applies the WHO–WHAT naming pattern and user-flow vocabulary before writing folder names
- [ ] SEC-02 (Epic Demarcation): the three boundary tests are applied as explicit checklist questions in Phase 2.1
- [ ] SEC-03 (Organizational Folder Semantics): the AC-09 rule (feat_* prefix inside epic_*) is explicitly checked in Phase 2.1
- [ ] SEC-05 (LLM Judgment Checklist): all 10 questions are answered during Phase 2.1 before folder creation

## Notes

- Depends on TASK-PROC-045-02 (script) being done so the Phase 2.5 call has something to invoke.
- The validation call in Phase 2.5 must use `--path` scoped to the new requirement to avoid blocking on pre-existing violations in unrelated folders.
- Keep skill additions minimal and inline — do not create separate reference files that could get out of sync with REQ-PROC-045.
