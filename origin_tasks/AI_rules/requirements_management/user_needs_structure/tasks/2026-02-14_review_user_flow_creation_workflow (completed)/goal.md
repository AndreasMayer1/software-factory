---
task_id: TASK-PROC-010-16
type: review
parent_requirement: REQ-PROC-010
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
completed: 2026-02-21
effort: M
created: 2026-02-14
after: []
awaiting:
  - TASK-PROC-027-13
covers:
  acceptance_criteria: []
  sections: []
scope_description: >
  After TASK-PROC-027-13 (create user flow for instruct_client_on_protocol) is complete,
  review how the create-user-flow workflow actually performed by comparing protocols and
  outputs against the skill definition and README specifications. Update the skill and/or
  READMEs where gaps, ambiguities, or improvements are identified.
requirements_version:
  commit: a210650
  file: ../requirements.md
---

# Goal: Review User Flow Creation Workflow and Update Skills/READMEs

## Objective

This task performs a retrospective review of the `create-user-flow` skill and associated
READMEs after their **first real-world use** in TASK-PROC-027-13 (creating FLOW-002 for
"Instruct Client on Protocol").

The goal is to identify whether the skill definition, README guidelines, and cross-referencing
rules worked as intended — and to improve them where they didn't.

**Context**: TASK-PROC-027-13 was deliberately chosen as the "first real use" of the new
user flow creation workflow. This review task exists because:
1. The workflow was defined without a concrete test case
2. Real usage reveals ambiguities and missing guidance that theory cannot predict
3. The cross-referencing system (README_8, README_13) was new and untested end-to-end

---

## Mandatory Pre-Work

**BLOCKED**: This task CANNOT start until TASK-PROC-027-13 is completed.

Before starting, verify:
- FLOW-002 exists at `requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md`
- TASK-PROC-027-13 protocols exist in its `plans_and_protocols/` folder

---

## Review Process

### Step 1: Read Task 1 Protocols

Read ALL files in:
`requirements_tasks/process/AI_rules/requirements_management/user_needs_content/tasks/2026-02-14_impl_create_user_flow_instruct_client_on_protocol/plans_and_protocols/`

Read the output:
`requirements_user_needs/user_flows/instruct_client_on_protocol/flow.md`

Extract:
- What steps were hard or ambiguous?
- Where did the agent deviate from the skill definition?
- What did the agent have to figure out that wasn't in the guidelines?
- Did the analysis phase work as intended?
- Did the user review checkpoint happen correctly?
- Were bidirectional references set up correctly?

### Step 2: Read Current Skill and READMEs

Read the skill and all READMEs that govern user flow creation (parallel reads):

**Skill**:
- `.claude/skills/create-user-flow/skill.md`

**READMEs** (in `requirements_user_needs/`):
- `README_5_USER_FLOW_DEFINITION.md` (template, exception model)
- `README_6_PCD_LAYER.md` (resource cost column)
- `README_7_META_INFO_STANDARDS.md` (YAML frontmatter, IDs)
- `README_8_CROSS-REFERENCING_SYSTEMS.md` (bidirectional links)
- `README_10_WRITING_GUIDELINES.md` (language, tone)
- `README_12_REVIEW_STATUS.md` (review workflow)
- `README_13_CROSS_REFERENCE_NOTATION.md` (reference notation)
- `README_14_DEVIATION_DOCUMENTATION.md` (deviation tables)
- `README_15_TECHNOLOGY_NEUTRALITY.md` (technology-agnostic language)

### Step 3: Compare and Identify Issues

Create `plans_and_protocols/2026-02-14_01_review_findings.md` documenting:

For each issue found:
- **What happened**: What the agent did or struggled with
- **What the skill/README says**: The current specification
- **Gap/ambiguity**: What was missing or unclear
- **Proposed fix**: How to update the skill/README
- **Priority**: High (blocks correct execution) / Medium (quality issue) / Low (nice to have)

Categories to review:
1. **Skill workflow steps** — Was the order correct? Were steps missing?
2. **Analysis phase guidance** — Was the pre-creation analysis adequately specified?
   (Note: The analysis phase was added to TASK-PROC-027-13's goal.md as custom guidance
   because it wasn't in the skill. Should it be in the skill?)
3. **Cross-referencing** — Did README_8/README_13 give enough guidance for bidirectional
   epic/feature links?
4. **Scenario status warnings** — Did the skill's handling of non-approved scenarios work?
5. **Multi-perspective flows** — FLOW-002 spans both therapist and client. Does the skill
   handle this case? (Most flows are single-persona)
6. **ID regeneration** — Was the ID registry regeneration step clear enough?
7. **YAML frontmatter completeness** — Were all required fields documented in README_7?
8. **Technology neutrality** — Were there borderline cases where README_15 guidance was
   insufficient?

### Step 4: Update Files

For each identified improvement:
- Update the relevant skill file or README directly
- Keep changes minimal and targeted (do not refactor unrelated content)
- Document each change made in the protocol file

**Files that may be updated**:
- `.claude/skills/create-user-flow/skill.md`
- `requirements_user_needs/README_5_USER_FLOW_DEFINITION.md` (source file, not root)
- `requirements_user_needs/README_8_CROSS-REFERENCING_SYSTEMS.md`
- `requirements_user_needs/README_13_CROSS_REFERENCE_NOTATION.md`
- Other READMEs as needed

**Note on README files**: READMEs under `requirements_user_needs/` are source files
(not auto-generated like `doc/*.md`). Edit them directly.

**Note on skill files**: Skills are in `.claude/skills/[name]/skill.md`. Keep them
token-efficient — every line is loaded into agent context.

### Step 5: Log and Complete

Log findings and changes to `plans_and_protocols/`. Use the `log-protocol` skill
to persist the agent ID for resumability.

---

## Scope

### In Scope
- Review of create-user-flow skill
- Review of all READMEs listed in Step 2
- Updates to skill and READMEs based on findings
- Documenting the review in plans_and_protocols/

### Out of Scope
- Reviewing TASK-PROC-027-13 output for content correctness (flow quality)
- Updating the setup-task skill (unless directly related to user flow creation)
- Adding new READMEs (improve existing ones, do not create new structure)
- Changing the user flow content itself (FLOW-002 may be reviewed separately by user)

---

## Acceptance Criteria

- [ ] All protocols from TASK-PROC-027-13 have been read and analyzed
- [ ] Review findings documented in plans_and_protocols/
- [ ] Each issue has a proposed fix
- [ ] All High-priority fixes have been applied to skill/READMEs
- [ ] Medium-priority fixes applied unless there is a good reason not to
- [ ] Changes are minimal (no unrelated refactoring)
- [ ] Review findings distinguish between skill issues vs README issues

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-027-13 | pending | Must be complete before this task starts |

---

## Notes

- urgency is 3 (not 5 like parent REQ-PROC-010) — this review improves quality but does
  not block any current work
- The review must focus on PROCESS issues, not content quality of FLOW-002 itself
- If the analysis phase from goal.md was very successful and should be formalized into
  the skill, that is a key finding to document

Current requirements:
```
git show a210650:requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/requirements.md
```
