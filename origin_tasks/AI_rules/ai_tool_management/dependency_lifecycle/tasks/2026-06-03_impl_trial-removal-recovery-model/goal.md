---
task_id: TASK-PROC-061-20
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 40
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Must hold the usage-check script, the retention registry, per-platform CI coverage, and the decision-task workflow together to wire the recovery procedure coherently."
after: [TASK-PROC-061-19]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-15]
  sections: []
scope_description: "Implement the empirical trial-removal recovery model: branch -> analyzer+tests+CI lanes -> revert-on-red, per-platform CI gating, residual-risk recording, failure->registry; demonstrate on local_notifier."
release_description: ""
opus_recommended: true  # reason: developer-directed; cross-cutting synthesis across script, CI coverage, decision-task workflow, and residual-risk policy
requirements_version:
  commit: bbc9d0a5
  file: ../requirements.md
---

# Goal: Implement empirical trial-removal recovery model

## Objective

Implement REQ-PROC-061 **AC-15**: confirm an authorized dependency removal *empirically*
(remove on an isolated branch → run analyzer + tests + every CI-covered platform's
build-plus-smoke lane → revert on red and record the failing signal as keep-justification)
rather than by manual code search. Gate confirmation on per-target-platform CI coverage with
the **allow-with-residual-risk** policy chosen for this requirement. Demonstrate the model
end-to-end on the concrete `local_notifier` removal candidate.

This is the recovery path that lets a "remove" decision be safe-by-experiment, and turns a
failed experiment into the durable keep-justification the retention registry (AC-14) records.

## Requirements Summary

REQ-PROC-061 AC-15: removal confirmed by experiment, not code archaeology. With the package
removed on an isolated branch, analyzer + tests + every CI-covered platform build-plus-smoke
must pass; red reverts and writes the failure into the AC-14 registry. Platforms with no CI
lane (per `.flutter-plugins-dependencies`) are recorded as accepted residual risk in the
proposal and decision task — they do not block. Config-referenced and code-generation packages
are exempt (their removal produces no test/build failure).

For complete requirements at task creation time:
```
git show bbc9d0a5:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

Design + ADR: `../../decisions/2026-06-03_trial-removal-recovery-model.md`;
`../2026-06-03_explore_harden-dependency-usage-check (completed)/plans_and_protocols/2026-06-03_01_design.md` (§5).

## Scope

### In Scope
- The trial-removal procedure: isolated branch/worktree → `flutter analyze` + `flutter test` + every CI-covered platform's build-plus-smoke lane → revert on red.
- Per-target-platform CI-coverage gating: derive a package's target platforms from `.flutter-plugins-dependencies`, compare against the CI lanes that exist; **allow-with-residual-risk** for uncovered platforms (record acceptance in the proposal + decision task).
- On red: write the failing signal (compile/link/test error) into the AC-14 retention registry as that package's keep-justification.
- Exempt config-referenced and code-generation packages from trial-removal.
- Demonstrate the model on the `local_notifier` removal candidate (#9): run the procedure, record the outcome (remove or keep-with-evidence).

### Out of Scope
- The classifier/registry implementation itself (AC-13/14 → TASK-PROC-061-19, predecessor).
- `doc/process/dependency_lifecycle.md` documentation (AC-10 → TASK-PROC-061-21).

## Acceptance Criteria

- [ ] Trial-removal runs on an isolated branch/worktree (never develop) and reverts cleanly on red
- [ ] Confirmation runs analyzer + tests + every CI-covered platform's build-plus-smoke lane
- [ ] Per-target-platform coverage is derived from `.flutter-plugins-dependencies`; uncovered platforms are recorded as accepted residual risk (allow-with-residual-risk), not silently assumed safe
- [ ] A red result reverts and writes the failing signal into the AC-14 retention registry as keep-justification
- [ ] Config-referenced and code-generation packages are exempt from trial-removal
- [ ] The model is demonstrated on `local_notifier` with a recorded outcome
- [ ] Python quality gates pass for any script work (via claude-write-script)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-061-19 | pending | Predecessor — the AC-14 retention registry must exist to receive failure-derived keep-justifications |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-061-19](../2026-06-03_impl_harden-usage-check-classifier-and-registry/goal.md) | Predecessor — provides the retention registry this model writes failure-justifications into |

## Notes

Process category — no `target_package`. opus_recommended per developer direction: the procedure
spans the usage-check script, CI platform coverage, the decision-task workflow, and the
residual-risk policy, which must be reasoned about together. Allow-with-residual-risk gating was
chosen over a strict CI-coverage gate (see ADR "Alternatives considered").
