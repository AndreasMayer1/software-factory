---
task_id: TASK-PROC-030-01-02
type: impl
parent_requirement: REQ-PROC-030-01
urgency: 3
urgency_reason: "U3-WORKFLOW-GAP: Existing skill can silently write requirements that contradict existing implementations — incident already occurred"
impact: 4
impact_reason: "I4-PAIN: Without these checks, requ-explore can produce requirements that specify work already done or done differently than what exists in lib/"
status: completed
completed: 2026-04-09
effort: M
created: 2026-04-09
started: 2026-04-09
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-02, AC-03, AC-04, AC-05]
  sections: []
scope_description: "Strengthen requ-explore sections 1.4 and 1.5 with keyword-grep, Related Requirements documentation, orphaned-implementation check, and minimum search scope"
release_description: ""
requirements_version:
  commit: 4c028a3b
  file: ../requirements.md
---

# Goal: Strengthen requ-explore Consistency Checks (Sections 1.4 and 1.5)

## Objective

Improve `.claude/skills/requ-explore/skill.md` to add keyword-grep-based overlap detection, persistent Related Requirements documentation, an explicit orphaned-implementation check, and a minimum search scope for section 1.5.

## Requirements Summary

REQ-PROC-030-01 covers four ACs (AC-02 through AC-05) related to requ-explore:

- **AC-02**: Keyword-grep is the primary overlap-detection mechanism in section 1.4, targeting functional/ and non-functional/, in addition to the folder-walk
- **AC-03**: All semantically related requirements found via keyword-grep are listed in `## Related Requirements` of the new requirement document
- **AC-04**: Section 1.5 includes an explicit orphaned-implementation check — code found without a covering requirement is recorded in the protocol, not silently accepted
- **AC-05**: Section 1.5 prescribes a minimum of 2–3 grep passes on `lib/` before concluding no existing implementation exists

Current requirements: ../requirements.md

## Scope

### In Scope
- Section 1.4 in `.claude/skills/requ-explore/skill.md`: add keyword-grep step
- Section 1.5 in `.claude/skills/requ-explore/skill.md`: add orphaned-implementation check and minimum scope rule
- Section 2.3 requirement template: ensure `## Related Requirements` instructions mandate listing keyword-grep hits

### Out of Scope
- Changes to `requ-derive-from-flow`
- Changing the folder-walk behavior (it is preserved as supplementary context)
- Full codebase scans — minimum 2–3 targeted passes is sufficient

## What to Change

### Section 1.4 changes

After the existing folder-walk instruction, add:

Run a keyword-grep across `requirements_tasks/functional/` and `requirements_tasks/non-functional/` using 2–4 terms derived from the requirement topic (domain nouns, action verbs, component names). Read hits to identify semantic overlaps even when folder names or IDs differ. This grep is the primary overlap-detection mechanism; the folder-walk provides supplementary structural context.

### Section 2.3 / Related Requirements

Add to the requirement writing instructions: all related requirements found via the section 1.4 keyword-grep must be listed in the `## Related Requirements` section of the new requirement. An empty `## Related Requirements` is only acceptable if the keyword-grep returned no relevant hits.

### Section 1.5 changes

After the CodeGraph and Glob/Grep steps, add:

**Orphaned-implementation check**: After identifying relevant code in `lib/`, verify that an existing requirement covers the observed behavior. Search `requirements_tasks/functional/` and `requirements_tasks/non-functional/` for the concept. If code implementing the feature is found but no requirement covers it, record this gap explicitly in the protocol before proceeding — do not silently continue.

**Minimum search scope**: At least 2–3 grep passes on `lib/` for key domain terms must be executed before concluding that no existing implementation exists for the requirement topic.

## Acceptance Criteria

- [ ] Section 1.4 prescribes a keyword-grep pass targeting functional/ and non-functional/ as the primary overlap-detection mechanism
- [ ] Section 2.3 (or equivalent writing instructions) requires that keyword-grep hits be listed in `## Related Requirements`
- [ ] Section 1.5 includes an explicit orphaned-implementation check with protocol-recording requirement
- [ ] Section 1.5 prescribes minimum 2–3 grep passes on lib/ before concluding no implementation exists
- [ ] The folder-walk in section 1.4 is preserved (not removed)

## Notes

The orphaned-implementation check does not need to be exhaustive — it needs to be honest. If after 2–3 targeted passes no implementation is found, proceeding is correct. The goal is to prevent the case where an existing implementation is never looked for at all.
