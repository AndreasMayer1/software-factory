---
task_id: TASK-PROC-034-12
type: impl
parent_requirement: REQ-PROC-034
urgency: 4
urgency_reason: U4-PLAN
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-04-16
effort: M
created: 2026-04-16
started: 2026-04-16
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: [SEC-01, SEC-05]
scope_description: "Define package naming conventions (what is a package, naming rules, categories/prefixes) and update skills to document and enforce them"
release_description: ""
requirements_version:
  commit: fadfd042
  file: ../requirements.md
---

# Goal: Define Package Naming Conventions and Update Skills

## Objective

The current `REQ-PROC-034` package naming rules are minimal (max 4 words, human-readable, globally unique, content-descriptive). In practice, ambiguous names arise when similar functionality exists in different contexts — e.g., a hypothetical "Print" package that could apply to multiple unrelated features across different epics and user flows.

This task defines comprehensive naming conventions for release packages and updates the relevant skills to document and enforce them.

## Requirements Summary

Relevant sections in `REQ-PROC-034`:

- **SEC-01 (Package Definition)**: What is a package, sources (flow-based, requirement-based, standalone), current naming rules (4 words, human-readable, unique, content-descriptive)
- **SEC-05 (AI Skill Behavior)**: Skill responsibilities for package assignment, creation, and validation

For complete requirements at task creation time:
```
git show fadfd042:requirements_tasks/process/AI_rules/requirements_management/release_version_management/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope

1. **Investigate what constitutes a package** — answer these open questions:
   - Should packages be cross-cutting (user-perspective, feature-agnostic) or scope-specific (per epic/flow)?
   - How do we prevent packages from becoming too large?
   - When does a set of ACs warrant a new package vs. joining an existing one?
   - User-perspective packages vs. technical/enabler packages — are these different categories?

2. **Define naming convention** — produce concrete rules for:
   - Naming pattern (structure, allowed words, forbidden words)
   - Category system (if any): prefixes, suffixes, or explicit category fields
   - Uniqueness guarantee: how to name scope-specific packages so similar names don't collide (e.g., "Print Client Data" vs. "Print Path Report")
   - How to derive a name from a user flow's happy path vs. exception bundle

3. **Document the rules** — update `SEC-01` of `REQ-PROC-034` (the Package Naming Rules subsection) with the new conventions

4. **Update skills** — ensure the following skills reference/enforce the new conventions:
   - `requ-assign-packages` — mention naming rules when prompting for new package names
   - `release-plan` — validate or remind when creating new packages
   - Any other skill that creates or names packages

### Out of Scope

- Renaming existing packages in `RELEASE_BACKLOG.md` (this task defines future rules; existing packages are grandfathered unless explicitly flagged)
- Assigning packages to `epic_data_transfer` requirements (that is TASK-PROC-030-11, which is blocked on this task)
- Creating new releases or reorganizing the backlog

## Acceptance Criteria

- [ ] Written analysis of the "what is a package" question — granularity, scope, user vs. technical perspective
- [ ] Concrete naming convention documented (rules, examples, anti-examples)
- [ ] `SEC-01` of `REQ-PROC-034` updated with the new naming rules
- [ ] `requ-assign-packages` skill updated to reference/enforce naming rules
- [ ] `release-plan` skill updated to reference/enforce naming rules
- [ ] TASK-PROC-030-11 unblocked: naming conventions are clear enough that the epic_data_transfer package assignments can proceed

## Context: Why This Was Created

TASK-PROC-030-11 (assign packages to `epic_data_transfer` requirements) is blocked on this task. The proposed package names in that task may need revision once naming conventions exist. The user identified this gap when reviewing the pending question for TASK-PROC-030-11 on 2026-04-15.

## Notes

- Use `opus-advisor` agent for the investigation phase (question 1 above) — this requires architectural reasoning
- The naming rules should be pragmatic: a developer looking at a package name in `RELEASE_BACKLOG.md` should immediately understand its scope without looking up the source requirement/flow
- Check existing package names in `RELEASE_BACKLOG.md` as examples — they should inform (but not necessarily constrain) the new rules
