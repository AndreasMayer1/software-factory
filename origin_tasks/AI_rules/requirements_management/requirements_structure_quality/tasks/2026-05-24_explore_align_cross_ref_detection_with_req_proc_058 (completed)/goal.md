---
task_id: TASK-PROC-045-06
type: explore
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
effort: S
created: 2026-05-24
completed: 2026-05-24
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add an acceptance criterion to REQ-PROC-045 defining the keyword-grep mechanism for cross-reference completeness detection (used by requ-explore Phase 1.4 and task-derive-from-requ Phase 1.5 per REQ-PROC-058 AC-17)"
release_description: ""
opus_recommended: false
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 0ea59bdb
  file: ../requirements.md
---

# Goal: Add Keyword-Grep Cross-Reference Detection AC to REQ-PROC-045

## Objective

Update REQ-PROC-045 to add a new acceptance criterion defining the keyword-grep
mechanism for cross-reference completeness detection in requirements.md files.
This mechanism is invoked by `requ-explore` Phase 1.4 (already exists) and by
`task-derive-from-requ` Phase 1.5 (new per REQ-PROC-058 AC-17). REQ-PROC-058
points at REQ-PROC-045 as the authoritative definition of the detection
mechanism — currently REQ-PROC-045 has no AC that covers it, so the pointer
dangles.

## Background

REQ-PROC-058 (Implementation Task Planning Quality) AC-17 introduces a
cross-reference completeness gate in `task-derive-from-requ` Phase 1.5 and
explicitly defers the detection mechanism to REQ-PROC-045: *"It checks the
`after:` chain, `blocks:` chain, and `## Related Requirements` body section
against a keyword-grep across `requirements_tasks/` (detection mechanism
defined by REQ-PROC-045)."*

The same mechanism is already used informally in `requ-explore` Phase 1.4
(see `.claude/skills/requ-explore/SKILL.md`):
> "Keyword-grep for overlap — Run a keyword-grep across
> `requirements_tasks/functional/` and `requirements_tasks/non-functional/`
> using 2–4 terms derived from the requirement topic (domain nouns, action
> verbs, component names). Read hits to identify semantic overlaps even when
> folder names or IDs differ. This grep is the primary overlap-detection
> mechanism."

The mechanism exists in skill instructions but has no requirement-level
definition. REQ-PROC-058 `blocks: [REQ-PROC-045]` was set to track this
needed addition.

The mechanism:
- Derives 2–4 search terms from a requirement's topic (domain nouns, action
  verbs, component names)
- Greps `requirements_tasks/functional/`, `non-functional/`, and `process/`
- Surfaces semantic matches NOT already cross-referenced in the target
  requirement's `after:`, `blocks:`, or `## Related Requirements` section
- Implementation may be a script (preferred per deterministic-first
  principle from REQ-PROC-058 Developer Guidelines) or inline skill
  instructions — to be decided by impl tasks

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-24_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 0ea59bdb:requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

This is an alignment task — the mechanism is well-defined in REQ-PROC-058
AC-17 and in `requ-explore` Phase 1.4. Use `requ-explore` to add the new AC
(likely AC-11) to REQ-PROC-045, ensure `trackable_items.acceptance_criteria`
in YAML lists it, and keep AC-01 through AC-10 intact.

## Seeds

1. **AC scope boundary**: The AC must define the detection mechanism (the
   "what") without prescribing implementation (the "how" — script vs.
   inline skill). REQ-PROC-058 Developer Guidelines prefer scripts; that
   preference belongs in REQ-PROC-058, not in REQ-PROC-045's AC. What is
   the right granularity?

2. **Search scope**: `requ-explore` Phase 1.4 says functional + non-functional;
   REQ-PROC-058 AC-17 says `requirements_tasks/` (all categories including
   process). The new AC should be explicit and consistent. Which scope is
   correct?

3. **Three reference channels**: The mechanism checks three places —
   `after:`, `blocks:`, and `## Related Requirements`. Are there other
   YAML channels (e.g. `parent_epic:`, `implements_flows:`) that should
   count as "already cross-referenced"?

4. **Term derivation**: "2–4 terms derived from domain nouns, action verbs,
   component names" — is this prescriptive enough to verify, or does it
   require examples in the AC body?

5. **Output contract**: What does the mechanism return? A list of
   `(REQ-ID, matching-file, snippet)` tuples? A structured artifact for
   later classification? The downstream consumers (requ-explore prose,
   task-derive-from-requ classification gate) imply slightly different
   contracts — should the AC pin one?

## Execution Model

Well-scoped alignment task. Read REQ-PROC-058 AC-17 and `requ-explore`
Phase 1.4 to confirm the mechanism contract, then invoke `requ-explore` on
REQ-PROC-045 to add the new AC.

## Output

REQ-PROC-045 has a new AC (likely AC-11) defining the keyword-grep
cross-reference detection mechanism. The AC describes WHAT the mechanism
does — input (requirement topic), scope (which folders are searched),
output (semantic matches not already cross-referenced in `after:`, `blocks:`,
or `## Related Requirements`) — without dictating HOW (script vs. inline
instructions; that decision belongs to the impl tasks). YAML
`trackable_items.acceptance_criteria` lists the new AC. AC-01 through AC-10
remain intact.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-058 | active | AC-17 references REQ-PROC-045 as detection-mechanism owner |
