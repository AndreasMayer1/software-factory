---
task_id: TASK-PROC-045-12
type: impl
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: pending
effort: S
created: 2026-06-01
after: [TASK-PROC-045-09, TASK-PROC-045-11]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-18]
  sections: [SEC-09]
scope_description: "Add Phase 2.1b (reactive restructuring analysis) to requ-explore SKILL.md — checks sibling bundling, feature oversize (>10 ACs), and obsolescence after location approval, before writing"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
---

# Goal: Implement Reactive Restructuring Analysis in requ-explore (Phase 2.1b)

## Objective

Add Phase 2.1b to `.claude/skills/requ-explore/SKILL.md`. This phase runs after Phase 2.1a (location approval) and before Phase 2.2 (write requirements). It analyses the requirement's neighbourhood for three structural problems and presents each finding to the user in a separate approval gate before any files are written.

## Requirements Summary

REQ-PROC-045 AC-18 and SEC-09 (added by TASK-PROC-045-11) specify the mechanism. Read them before starting:

```
git show 6ece1dc7:requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md
```

Current requirements: ../requirements.md

**Three cases to detect (from SEC-09):**

| Case | Trigger | Detection | Resolution |
|------|---------|-----------|------------|
| A — Sibling bundling | Existing `feat_*` siblings in the same grouping share the new requirement's primary domain concept | LLM judgment: read each sibling's `requirements.md` and compare domain concepts | Propose a new `epic_*` enclosing both; Path B under SEC-06; requires user approval |
| B — Feature oversize | Authored or extended `feat_*` has > 10 acceptance criteria | Count `trackable_items.acceptance_criteria` entries; script-checkable | Propose splitting into multiple `feat_*` under a new `epic_*`; Path B; requires user approval |
| C — Obsolescence | An existing requirement's full scope is subsumed by the new content | Review Phase 1.4 cross-reference candidates; compare their ACs to new content | Propose marking it `deprecated` with `superseded_by: [new-REQ-ID]` in frontmatter; requires user approval |

Phase 2.1a already tells the user the analysis is coming (updated in TASK-PROC-045-11 session). Phase 2.1b delivers the findings.

## Scope

### In Scope
- `.claude/skills/requ-explore/SKILL.md`: insert new `### 2.1b Reactive Restructuring Analysis` section immediately after the existing `### 2.1a Location Approval Gate` section
- Phase 2.5 quality checklist: add one item — "Reactive restructuring: any detected case was either applied (with user approval) or explicitly deferred; none silently skipped"
- Use `claude-modify-skill` for all skill edits (mandatory per CLAUDE.md)

### Out of Scope
- Changes to the structural validation script (TASK-PROC-045-02/03)
- REQ-PROC-045 requirements.md content (already updated by TASK-PROC-045-11)
- TASK-PROC-045-04's scope: AC-08 (validation script call), SEC-01-05 (naming/demarcation guidance in Phase 2.1)
- Automated detection without user gate — every case requires explicit user approval before applying

## Acceptance Criteria

- [ ] `requ-explore` SKILL.md contains a `### 2.1b Reactive Restructuring Analysis` section placed between `### 2.1a` and `### 2.2`
- [ ] Phase 2.1b specifies all three cases (A sibling bundling, B feature oversize >10 ACs, C obsolescence) with their detection method and resolution path
- [ ] Phase 2.1b specifies that findings are presented in a separate user approval gate, one finding per approval, before any files are written
- [ ] Phase 2.1b specifies that no finding is silently skipped — the user must approve or explicitly defer each one
- [ ] Phase 2.5 quality checklist contains the reactive restructuring verification item
- [ ] `claude-modify-skill` was used for all skill edits

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-045-09 | pending | Migration roadmap — exec must not precede the restructuring; the skill should reflect the settled folder structure |
| TASK-PROC-045-11 | pending | Explore task that defined AC-18 / SEC-09 and updated Phase 2.1a; read its protocol before starting |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-045-11](../2026-06-01_explore_reactive-restructuring-analysis/goal.md) | Predecessor — defines the mechanism; read plans_and_protocols/ before implementing |
| [TASK-PROC-045-09](../2026-05-28_define_migration-roadmap-process-and-non-functional/goal.md) | Predecessor — migration roadmap; skill changes should align with settled structure |
| [TASK-PROC-045-04](../2026-04-26_impl_skill_requ-explore_structure_quality/goal.md) | Scope boundary — covers AC-08/SEC-01-05 (Phase 2.1 naming guidance + Phase 2.5 validation call); this task covers AC-18/SEC-09 (Phase 2.1b reactive analysis) |
