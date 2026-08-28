---
task_id: TASK-PROC-068-13
type: verify
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: pending
effort: S
created: 2026-07-01
expected_tool_calls: 25
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Must judge the full regenerated product-definition stack (personas→scenarios→flows→requirements) as one coherent, type-conformant unit against the README artifact-type definitions."
after: [TASK-PROC-068-12]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
consequence: MEDIUM
scope_description: "Independently verify the regenerated harness product-definition stack conforms to the artifact-type definitions (README_3/4/5), closes coverage, and is natural — the new live frontier the finalize + captest tasks re-point to. Replaces the failed TASK-PROC-068-09 gate."
release_description: ""
opus_recommended: true   # reason: synthesis verification — holds the whole stack + the type definitions at once
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
---

# Goal: Verify Harness Re-derivation Conformance (New Live Frontier)

## Objective

Independently confirm the **regenerated** harness product-definition stack (personas → scenarios →
flows → requirements) is **type-conformant, coverage-closed, and natural** — the gate that the failed
TASK-PROC-068-09 was supposed to be, now applied to the corrected artifacts. This is the **new live
frontier**: TASK-PROC-068-03 (finalize) and TASK-PROC-068-10 (captest run) re-point their `after:` here.

## Background

TASK-PROC-068-09 was closed **FAILED**: the terminal batch's artifacts were non-conformant stubs
produced by a mechanism whose content gates were orphaned. The remediation chain — TASK-PROC-071-05-05
(mechanism fix), TASK-PROC-068-11 (approved anchors), TASK-PROC-068-12 (re-derivation) — produces the
corrected artifacts this task verifies. Unlike 068-09, this gate checks **type-validity of each node**,
not merely ID coverage.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Verify each artifact conforms to its type definition:
  - personas → README_3, scenarios → README_4 (incl. the status-quo CRITICAL RULE + folder layout),
    flows → README_5 (the six required sections, frontmatter, happy-path table + exceptions),
    requirements → the requirements schema (trackable_items where applicable).
- Verify coverage closes across layer boundaries and the layers are minimal.
- Verify the content gates actually fired during derivation (AC-02 density + AC-03 naturalness),
  consuming any oracle verdict under the five ADVISORY caveats.
- Confirm the two-tree split (all product content under `test_harness_app/requirements_*`).

### Out of Scope
- Re-authoring or re-deriving (that is 068-11 / 068-12).
- Finalization (TASK-PROC-068-03).

## Acceptance Criteria

- [ ] AC-1: Personas, scenarios, flows, requirements each pass their README_3/4/5 / schema conformance.
- [ ] AC-2: Coverage closes across all layer boundaries; layers are minimal (nothing invented).
- [ ] AC-3: Evidence the AC-02 density + AC-03 naturalness gates fired during the re-derivation.
- [ ] AC-4: Two-tree split honoured; ADVISORY caveats carried on any consumed oracle verdict.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-12 | pending | The re-derivation whose output this gate verifies |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-12](../2026-07-01_impl_harness-middle-rederive/goal.md) | Predecessor — supplies the regenerated stack under verification |

## Notes

- Coordinator-derived, covers-empty process verify task (no `target_package`) — surfaces only via the
  override. New live frontier: TASK-PROC-068-03 and TASK-PROC-068-10 re-pointed to this task.
