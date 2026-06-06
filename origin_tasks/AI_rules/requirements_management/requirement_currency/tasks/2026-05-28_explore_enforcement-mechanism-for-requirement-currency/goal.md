---
task_id: TASK-PROC-064-01
type: explore
parent_requirement: REQ-PROC-064
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
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05]
  sections: []
scope_description: "Design the enforcement mechanism for REQ-PROC-064 requirement currency — how agents detect stale ACs and where/how the check is triggered across all artifact types"
release_description: ""
opus_recommended: true   # reason: cross-cutting scope (≥2 architectural layers — skill layer, quality gate layer, all artifact types); explicit trade-off analysis required; goal text contains "evaluate options", "decide approach"
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ""
  file: ../requirements.md
---

# Goal: Design Enforcement Mechanism for Requirement Currency

## Objective

Design how REQ-PROC-064 is enforced in practice. The requirement defines WHAT must be true: when a behavioral change is made to any artifact, stale requirement ACs must be found and updated before the task closes. This exploration defines HOW — the detection mechanism, trigger point, tooling, and the path to uniform coverage across all artifact types.

## Background

REQ-PROC-064 (Requirement Currency) was introduced because behavioral changes to scripts, skills, hooks, and Dart code can silently make requirement ACs false. The factory already enforces the top-down direction (product-intake prevents user-visible changes without a requirements chain). The bottom-up direction — implementation changes making requirements stale — has no enforcement today.

The problem is harder than it looks. A naïve "check all ACs on every file write" approach would be expensive and noisy. A "search ACs for the changed filename" approach would produce false positives and miss ACs that describe behavior without naming the file. The enforcement must be accurate enough to be trusted and cheap enough not to slow every task to a crawl.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-28_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show HEAD:requirements_tasks/process/AI_rules/requirements_management/requirement_currency/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **Detection signal**: An AC is stale when the behavior it describes no longer matches the artifact — not merely when the artifact's file was touched. What does "behavior described by AC" look like in practice? Is it always expressed as natural language, or can it be made machine-checkable? What's the minimum signal needed to distinguish "this AC may be stale" from "this AC is fine"?

2. **Trigger point tension**: If the check runs at task-complete (late), it's a hard block but easy to implement uniformly. If it runs inside each skill (early), it's easier to make contextual but requires changes to many skills. If it runs at verify-quality (middle), it fits the existing gate pattern. Which trigger point minimises both false positives and maintenance overhead?

3. **The indexing question**: Does a script that indexes "which requirement ACs mention which file paths / artifact names" buy enough precision to be worth the maintenance? What happens when ACs describe behavior in terms of outcomes rather than file names? What is the failure mode of an index-based approach?

4. **Uniform coverage without duplication**: claude-write-script already has a behavioral-change concept. code-simple/code-complex do too, implicitly. But skills, hooks, doc/, and devcontainer have no such concept in their workflows. How do you add the check uniformly without copy-pasting the same logic into 8 different skills?

5. **Automation-friendliness**: In automated mode, the detection step must not require interactive confirmation. The remediation step (requ-explore) may surface a pending-feedback question. What does the handoff between detection and remediation look like in automated mode? What is the right pending-feedback format?

6. **The exemption declaration problem**: AC-04 requires the agent to state which exemption applies when skipping. In practice, agents will forget or produce vague statements ("non-behavioral change"). How is this made enforceable — and how is it kept lightweight enough that agents don't resent it?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus, per `opus_recommended: true`).

**Web research**: For seeds requiring external knowledge — best practices for requirement traceability tooling, prior art in AI-assisted change impact analysis, what others have tried — delegate to a spawned `general-purpose` agent with a focused question. Never run WebSearch inline. The subagent returns only a distilled summary.

Key artifacts to read before synthesizing:
- `.claude/skills/verify-quality/SKILL.md` — existing gate structure
- `.claude/skills/task-complete/SKILL.md` — existing completion flow
- `.claude/skills/claude-write-script/SKILL.md` — existing behavioral-change definition
- `.claude/skills/code-simple/SKILL.md`, `code-complex/SKILL.md` — existing impl workflows
- `requirements_tasks/process/AI_rules/requirements_management/requirement_currency/requirements.md` — the WHAT

## Output

A concrete design proposal, not a menu of options. The output should be specific enough that implementation tasks can be written directly from it. It should answer:
- What is the detection mechanism (the algorithm/heuristic/script)?
- Where exactly does the check run (which skill, which step, what hook)?
- How is uniform coverage achieved across all artifact types?
- What does the agent say/write when it applies an exemption?
- What does the automated-mode flow look like end-to-end?
- What are the known limitations and acceptable false-negative rate?

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-064 | active | Defines the WHAT; this task designs the HOW |
