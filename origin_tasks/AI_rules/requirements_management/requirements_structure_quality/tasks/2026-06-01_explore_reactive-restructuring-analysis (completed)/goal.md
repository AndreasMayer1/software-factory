---
task_id: TASK-PROC-045-11
type: explore
parent_requirement: REQ-PROC-045
urgency: 3
urgency_reason: U3-TECH-DEBT
impact: 4
impact_reason: I4-ENAB
status: completed
completed: 2026-06-01
effort: M
created: 2026-06-01
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Design the reactive restructuring analysis: detect when adding new information (requirements, ACs) should trigger reorganization of neighboring requirements, and specify it as a new AC in REQ-PROC-045"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore — touches requ-explore skill, REQ-PROC-045 authoring rules, and the placement algorithm; trade-off analysis between automation and user control
writes_requirements: true
requirements_version:
  commit: 6ece1dc7
  file: ../requirements.md
---

# Goal: Explore Reactive Restructuring Analysis for requ-explore

## Objective

`requ-explore` currently evaluates structural placement for the requirement being authored. It does NOT detect when that authoring action reveals that neighboring requirements have become incorrectly grouped. This exploration defines what that backward-looking analysis should look like: when it should run, what cases it should detect, how findings are surfaced to the user, and what shape the resulting new AC in REQ-PROC-045 should take.

What we do NOT yet know: the full taxonomy of trigger cases beyond the user's three examples, the threshold conditions (how many ACs make a feature "too large"?), whether detection can be automated or requires LLM judgment, and how this interacts with the existing placement-walk governance (Path A/B/C in REQ-PROC-045 SEC-06).

## Background

REQ-PROC-045 governs requirements folder structure and placement. Its existing ACs cover:
- Forward placement: where a NEW requirement goes (SEC-05, AC-15/16)
- Governance when the placement walk halts (SEC-06, Path A/B/C)
- Script-checkable invariants: epic must have feat_* children, feat_* must have requirements.md, etc. (AC-01–AC-08, AC-10–AC-17)

What is absent: a mechanism that runs when `requ-explore` adds information and asks "does this new information make the existing neighboring structure incorrect or suboptimal?" The placement algorithm walks forward; the restructuring analysis looks sideways and backward at already-placed requirements.

The user explicitly said this should land "after or together with the restructuring" (TASK-PROC-045-09, which defines the migration roadmap for process/ and non-functional/ folders). The downstream impl task that wires this mechanism into `requ-explore` should have `after: [TASK-PROC-045-09, TASK-PROC-045-11]`.

The user's unedited initial thinking is preserved in:
`plans_and_protocols/2026-06-01_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 6ece1dc7:requirements_tasks/process/AI_rules/requirements_management/requirements_structure_quality/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

## Seeds

1. **The user's three cases — are they a complete taxonomy?** The user named: (a) two sibling features that should become an epic, (b) a feature that has grown too large and should split, (c) a new requirement that makes an existing one obsolete. What other cases exist? What about a new epic that absorbs a standalone feature? A requirement that was split but the split turned out wrong? Frame the full case taxonomy before designing the detection mechanism.

2. **Threshold problem**: What makes a feature "too large"? Is it AC count? Line count in requirements.md (the epic already has a 90-line limit)? Number of distinct domain entities addressed? Is there a principled, machine-checkable threshold — or is this inherently an LLM-judgment call? The answer affects whether the mechanism can be a script gate or must be a Phase 2.1 reasoning step.

3. **Automation vs. user control tension**: REQ-PROC-045 SEC-06 (Path C) already requires explicit user authorization for taxonomy changes. Does reactive restructuring always require the same gate, or are some cases (e.g., marking a superseded requirement) safe to do automatically? Map each case to its authorization level.

4. **Interaction with the existing placement algorithm**: REQ-PROC-045 SEC-05 already defines what happens when a new placement "halts with no match." Is reactive restructuring a natural extension of that halt, or a separate analysis? Could the placement walk's output trigger restructuring suggestions as a byproduct?

5. **Scope relative to TASK-PROC-045-09 (migration)**: The migration roadmap moves existing requirements to a new structure. The reactive mechanism prevents future drift. Are there cases where the mechanism design needs to account for the transitional state (half-migrated tree)? Or is the mechanism only correct after migration is complete?

6. **Superseded status**: REQ-PROC-045 does not currently define what "superseded" means for a requirement's lifecycle — status values, what happens to covering tasks, whether the requirement stays in the folder tree or is moved. This gap needs to be surfaced; it may belong in REQ-PROC-045 or in a separate lifecycle requirement.

## Execution Model

Gather raw material — read REQ-PROC-045 fully, read the existing placement algorithm steps, read the SEC-06 governance model, read the epic size gate in `requ-explore`. Synthesize iteratively; multiple passes are needed before the design is well-formed.

The session's model is fixed at launch (Opus when `opus_recommended: true`, Sonnet otherwise).

**Web research**: For seeds requiring external knowledge (e.g., "how do other structured authoring systems detect scope drift in existing documents?"), delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline.

## Output

A clear specification, in `plans_and_protocols/`, of:
1. The full case taxonomy (what triggers a restructuring suggestion)
2. For each case: trigger condition (machine-checkable vs. LLM judgment), user gate required (y/n), proposed mechanism
3. The draft new AC text for REQ-PROC-045 (end-state language, verifiable)
4. Any gaps discovered (e.g., "superseded" lifecycle, missing status values) that require separate requirements work
5. Sequencing recommendation: what must be in place before the impl task can write the mechanism into `requ-explore`

A future implementer reading the output should be able to write the mechanism into `requ-explore` without returning to this exploration.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies; explore can run before TASK-PROC-045-09. The downstream impl task must wait for both. |
