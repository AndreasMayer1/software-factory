---
task_id: TASK-PROC-068-14
type: explore
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-07-01
completed: 2026-07-01
session_completed_at: 2026-07-01T18:38:56Z
effort: XS
created: 2026-07-01
expected_tool_calls: 12
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add one intent-level AC to REQ-PROC-068: a deploy places the WHOLE factory into the harness such that a contained child session can invoke any factory skill end-to-end. No file/artifact enumeration in the requirement. Authored via requ-explore."
release_description: ""
opus_recommended: false
writes_requirements: true
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: 30f7f03d-0bc4-4e51-8333-de76597ead1f
session_account: web
---
# Goal: Whole-factory-deploy acceptance criterion for the harness

## Objective

The existing deploy (`scripts/playground/deploy.py`) copies only `.claude/skills/` into the harness.
REQ-PROC-068 AC-07 (deploy→run→**reset cycle**, EGP F) and AC-09 (containment, EGP S — test-proven) are
both legitimately met for what they assert, and **neither mandates copying the whole factory.** So the
requirement that "a deployed candidate must contain everything its skills transitively need, so a
*contained* child can actually run them" is **not yet expressed** by any AC.

This task adds exactly one **intent-level** AC to REQ-PROC-068 to close that gap. What must be discovered
is only the precise, checkable wording — not any file list.

## Background

Verified root cause (see the plan referenced below): the anchor/authoring skills shell out to helper
scripts (e.g. `generate_id_registry.py`) that anchor on `script_dir.parent.parent`, so a skills-only
deploy leaves a *contained* child unable to run them — it cannot reach the host `scripts/` (correctly
blocked by `containment.py`, AC-09) and does not have them locally. Hence the new AC.

**Developer principle that constrains the wording (critical):** the AC must say *"the whole factory"* and
must **NOT** enumerate which files/artifacts are the factory. What the factory is will be defined only by
the factory project itself once it is extracted (REQ-PROC-066) — "everything it provides." Defining the
boundary in an AC outside the factory would create an authoritative definition in the wrong place that
drifts at extraction. The pre-extraction *implementation* carries a temporary code-level exclude rule;
that is out of scope for this requirement task.

Authoritative seed/spec (read it):
`../2026-06-11_explore_llm-verifiable-open-ended-skill-tests (completed)/plans_and_protocols/2026-06-26_11_plan_orchestration-chain-buildout.md`
(§ "Continuation (2026-07-01)" + "Revision (2026-07-01, developer)").

The user's unedited initial thinking is preserved in:
`plans_and_protocols/2026-07-01_00_user_initial_input.md` — read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

The design is nearly decided; the work is to author *checkable* AC text (EGP archetype I — checkable
against plain-language intent) and get developer approval. Screen the wording so it cannot be satisfied by
a skills-only deploy, yet does not smuggle in a file enumeration.

## Seeds

- Candidate wording: *"A deploy places the whole factory into the harness such that a contained child
  session can invoke any factory skill end-to-end, with no reach-back to the host tree."* Is "whole
  factory" checkable without a file list? (Yes — via a functional probe: run a script-calling skill inside
  the jail.)
- EGP disposition for the new AC: archetype **F** (functional fidelity) with referent "a contained child
  running a script-calling skill end-to-end"? Confirm during authoring.
- Relationship to REQ-PROC-066 AC-02 (no-manual-copy consumer install): note the cross-reference; this
  harness AC is a precursor the extracted factory later generalizes. Do NOT bind this AC to 066.

## Execution Model

Read the requirement + the deploy code + the plan, then author the single AC via `requ-explore` with the
approval gate. Detailed how is owned by the routed skill.

## Output

One new, developer-approved, intent-level AC on REQ-PROC-068 (no file enumeration) that a skills-only
deploy fails and a whole-factory deploy passes. Its implementation (T-B) is a separate downstream task
(created by TASK-PROC-068-15).

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] The user has approved the final synthesis and stated what to do next
- [x] The action stated by the user as the next step was performed successfully

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies (root of Track A) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-15](../2026-07-01_impl_orchestrate-deploy-and-resolution-chain/goal.md) | Orchestration task — creates the deploy impl (T-B) that covers this AC once it exists |

## Notes

**Standing rule (developer, 2026-07-01):** every task that creates other tasks MUST add the tasks it
creates to `.claude/task_ordering_priority_override.txt`, and each created task must carry this same
instruction (the rule propagates recursively). If executing this task spawns any downstream task, register
it there.
