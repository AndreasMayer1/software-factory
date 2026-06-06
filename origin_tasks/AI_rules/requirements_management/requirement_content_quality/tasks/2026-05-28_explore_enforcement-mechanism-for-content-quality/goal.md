---
task_id: TASK-PROC-062-01
type: explore
parent_requirement: REQ-PROC-062
urgency: 3
urgency_reason: U3-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-05-28
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07]
  sections: []
scope_description: "Design how to enforce REQ-PROC-062 content quality properties — prospectively for new requirements and retrospectively for existing ones"
release_description: ""
opus_recommended: true   # reason: cross-cutting scope (affects requ-explore, verify-quality, and potentially a new script); explicit trade-off analysis; decide approach for retrospective remediation strategy
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Design Enforcement Mechanism for Requirement Content Quality

## Objective

Design how REQ-PROC-062 (Requirement Content Quality) is enforced in practice. The requirement defines WHAT must be true: seven content properties that every requirement must satisfy. This exploration defines HOW — which properties can be checked mechanically, which require judgment, where checks run, and how existing requirements that pre-date the contract are remediated.

## Background

REQ-PROC-062 formalizes content properties that previously existed only as a skill-internal checklist in `requ-explore` Phase 2.5. The Phase 2.5 checklist already enforces several of these properties prospectively (for requirements written through the skill). The gap is:

1. **No formal contract** — the checklist is an implementation detail, not a specification. It can change without violating any requirement.
2. **No retrospective coverage** — requirements written before the checklist (or written outside requ-explore) are not subject to it.
3. **No mechanical check** — all seven properties are currently evaluated by LLM judgment during requ-explore. Some of them (AC-07 forbidden sections, AC-02 transition verbs, AC-01 threshold-free adjectives) could be checked by a script.
4. **No gate integration** — content quality is not a blocking gate in verify-quality or task-complete.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-28_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show HEAD:requirements_tasks/process/AI_rules/requirements_management/requirement_content_quality/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises.

## Seeds

1. **Mechanical vs. judgment split**: Which of the seven properties (AC-01 through AC-07) can be checked by a script reliably? AC-07 (forbidden sections) and AC-02 (transition verbs) are plausible candidates. AC-01 (threshold-free adjectives) is harder — the word list would have false positives. AC-03 (atomicity) and AC-04 (evidence grounding) likely require LLM judgment. What is the right split, and what false-positive rate is acceptable before a mechanical check becomes counterproductive noise?

2. **Integration point**: Should content quality checks run inside requ-explore (Phase 2.5 strengthened), inside verify-quality as a new gate, or as a standalone script invoked by task-complete? Each option has different blast radius and different noise characteristics. The right answer probably differs per-property.

3. **Retrospective remediation scope**: There are O(100) existing requirements that pre-date REQ-PROC-062. Remediating all of them at once is a large task; ignoring them means the contract only applies to new work. What is the right trigger for retrospective checks — "when next opened via requ-explore", "per-release audit", "on-demand script", or "continuous background task"?

4. **requ-explore Phase 2.5 as the primary gate**: Phase 2.5 already has a checklist. The question is whether strengthening it (making each item a hard block rather than a soft check) is sufficient for prospective enforcement, or whether a separate gate is needed for requirements modified outside requ-explore (e.g., direct edits, automated requirement generation from flows).

5. **The evidence-grounding problem (AC-04)**: This is the hardest property to check mechanically. Evidence grounding requires knowing WHY an AC was written, which may not be in the file. Can the requ-explore workflow be modified to capture evidence inline in the requirement (e.g., a `source:` comment on each AC in the YAML)? Would that make AC-04 checkable?

6. **Deferred (YAGNI) section hygiene**: AC-04 requires failing ACs to go to ## Deferred (YAGNI) with a reopen condition. Over time, deferred sections accumulate. Is there a cleanup mechanism — expiry, per-release review, automatic flag when reopen condition is met?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively.

The session's model is fixed at launch (Opus, per `opus_recommended: true`).

**Web research**: For seeds requiring external knowledge — requirement quality frameworks (IEEE 29148, INVEST, SMART), tooling for automated AC analysis — delegate to a spawned `general-purpose` agent with a focused question. Never run WebSearch inline.

Key artifacts to read before synthesizing:
- `.claude/skills/requ-explore/SKILL.md` Phase 2.2 (YAGNI gate) and Phase 2.5 (quality checklist) — the existing enforcement
- `.claude/skills/verify-quality/SKILL.md` — existing gate structure and how new gates are added
- `.claude/skills/task-complete/SKILL.md` — completion flow
- `requirements_tasks/process/AI_rules/requirements_management/requirement_content_quality/requirements.md` — the seven properties to enforce
- `requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md` — how REQ-PROC-045 is enforced (mechanical checks in requ-explore and release-begin-impl) — useful pattern to follow

## Output

A concrete design proposal covering:
- Which properties are checked mechanically vs. by LLM judgment, and where each check runs
- How Phase 2.5 is strengthened (or whether a separate gate is preferable)
- Retrospective remediation strategy — trigger, scope, and mechanism
- Whether inline evidence capture in YAML (to support AC-04 mechanical checking) is worth the cost
- Deferred (YAGNI) section lifecycle management
- Known limitations and acceptable false-negative/false-positive trade-offs

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-062 | active | Defines the seven properties to enforce |
| TASK-PROC-064-01 | pending | Related enforcement exploration for requirement currency — may share design patterns |
