---
task_id: TASK-PROC-061-11
type: explore
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 25
skill_chain_depth: 2
after: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Re-evaluate the clean_architecture_kit / bloc_lint analyzer ceiling that blocks the latest drift, drift_dev, freezed, json_serializable, and mockito"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 804bcfc0
  file: ../requirements.md
---

# Goal: Re-evaluate the analyzer ceiling blocking code-gen dependency bumps

## Objective

The project's `pubspec.lock` pins `analyzer 8.4.0` and `_fe_analyzer_shared 91`
(latest are 13.x / 100). This ceiling is imposed by `clean_architecture_kit
^2.0.1` and the intentionally-pinned `bloc_lint ^0.3.7` (rationale in
`pubspec.yaml`: `bloc_lint` 0.4.x pulls `_fe_analyzer_shared >=93`, incompatible
with `clean_architecture_kit`'s transitive `analyzer ^8.0.0`). The ceiling
blocks the latest versions of five code-gen / test tools, each of which requires
`analyzer > 8.4.0`:

- drift 2.31.0 → 2.33.0
- drift_dev 2.31.0 → 2.33.0
- freezed 3.2.3 → 3.2.5
- json_serializable 6.11.2 → 6.14.0
- mockito 5.6.4 → 5.7.0

What is not yet known: whether a coherent dependency set exists that lifts the
ceiling (newer `clean_architecture_kit` / `bloc_lint` / `custom_lint` /
`analyzer`) without breaking the custom-lint tooling — and whether the value of
those five bumps justifies the churn. This exploration should produce a clear
go/no-go with a concrete upgrade path or a documented "stay pinned" decision.

## Background

Deferred from **TASK-PROC-061-05** (apply 2026-06 autonomous bumps). That task
discovered — when running a real `pub solve` in the devcontainer — that 7 of the
16 proposed bumps were not solver-reachable. Five of those seven are blocked by
this analyzer ceiling. The source monthly review proposed pub.dev `Latest`
versions without a real solve, so the ceiling was invisible at review time.

This is a **major dependency decision requiring human authorization** — bumping
`clean_architecture_kit` and/or `bloc_lint` can change lint behavior and may
cascade through `custom_lint` / `analyzer`. It is explicitly out of scope for
the autonomous-bump cadence.

Evidence: `automation/dependency_reviews/2026-06/proposal.md` (Deferred targets
section) and the apply-bumps protocol at
`../2026-06-02_impl_apply-2026-06-autonomous-bumps/plans_and_protocols/2026-06-02_01_protocol_apply-bumps.md`.

For complete requirements at task creation time:
```
git show 804bcfc0:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Empathize with the constraint before trying to remove it: the `bloc_lint` pin
exists for a documented reason. Diverge on possible coherent dependency sets,
then converge on the one (if any) that lifts the ceiling without breaking the
custom-lint pipeline. Verify every candidate with an actual `flutter pub
upgrade --dry-run` / `pub solve` in the devcontainer — do not trust pub.dev
`Latest` columns.

## Seeds

- Is there a `clean_architecture_kit` version (or successor) that depends on
  `analyzer >=13` / `_fe_analyzer_shared >=100`, and does it still satisfy the
  project's custom-lint rules?
- Can `bloc_lint` move to 0.4.x once `clean_architecture_kit` is updated, or is
  the conflict structural? (This intersects TASK-PROC-061-07's bloc_lint line.)
- How much real value do the five blocked bumps deliver? Are any of them
  security-relevant or unblocking a feature, or are they pure hygiene?
- What is the blast radius of an `analyzer` 8→13 jump on the existing
  `custom_lint` / `very_good_analysis` setup?
- Is "stay pinned and document" the honest answer for this cycle, deferring
  until `clean_architecture_kit` ships an analyzer-13-compatible release?

## Execution Model

Gather raw material — read `pubspec.yaml`/`pubspec.lock`, the `bloc_lint` pin
rationale, and run real solves in the devcontainer. Delegate any web research
(e.g. "has clean_architecture_kit released an analyzer-13-compatible version?")
to a spawned `general-purpose` agent with a focused question; never run
WebSearch inline.

The session's model is fixed at launch (Sonnet — `opus_recommended: false`).

## Output

A future implementer should understand: whether the ceiling can be lifted now,
the exact dependency set that does it (verified by a real solve), the blast
radius on lint tooling, and a go/no-go recommendation per blocked package. If
the answer is "stay pinned", the output should say so plainly with the date/
condition to re-check.

## Acceptance Criteria

- [ ] Exploration produced at least one synthesis round
- [ ] The synthesis defines the problem space in terms that were not fully known at task creation
- [ ] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [ ] The output is honest about what remains uncertain

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No hard blockers; can begin independently |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-061-07](../2026-06-02_explore_decide-2026-06-major-bumps/goal.md) | Scope boundary — that task decides the `bloc_lint`/`clean_architecture_kit` bump go/no-go; this task analyzes the analyzer-ceiling cascade those packages impose on drift/drift_dev/freezed/json_serializable/mockito and the path to lift it |
| [TASK-PROC-061-05](../2026-06-02_impl_apply-2026-06-autonomous-bumps/goal.md) | Predecessor — deferred these five bumps here after the real solve revealed the ceiling |

## Notes

Deferred from TASK-PROC-061-05 per the developer's Option-A decision (2026-06-03).
