---
task_id: TASK-PROC-061-21
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: pending
effort: M
created: 2026-06-03
expected_tool_calls: 30
skill_chain_depth: 1
after: [TASK-PROC-061-19, TASK-PROC-061-20]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-10, AC-13, AC-14, AC-15]
  sections: []
scope_description: "Document the new evidence classes, retention registry, and trial-removal model in doc/process/dependency_lifecycle.md (AC-10), and verify the hardened usage-check end-to-end against AC-13/14/15."
release_description: ""
opus_recommended: false
requirements_version:
  commit: bbc9d0a5
  file: ../requirements.md
---

# Goal: Document AC-13/14/15 and verify usage-check end-to-end

## Objective

Two merged concerns (developer combined the doc-sync and verification tasks):
1. **AC-10 (single authoritative location)** — update `doc/process/dependency_lifecycle.md`
   so it documents the new evidence classes (config-referenced, native-declared), the tiered
   output, the retention registry, and the trial-removal recovery model, consistent with
   REQ-PROC-061.
2. **Verification** — confirm the hardened usage-check (TASK-PROC-061-19) and trial-removal
   model (TASK-PROC-061-20) actually satisfy AC-13/14/15.

This is the closing task of the REQ-PROC-061 hardening chain.

## Requirements Summary

REQ-PROC-061 AC-10 requires the trigger model, cadence, classification, and recovery
behaviors to be documented in a single authoritative location consistent with the
requirement. The new AC-13/14/15 behaviors must be reflected there.

For complete requirements at task creation time:
```
git show bbc9d0a5:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- Update `doc/process/dependency_lifecycle.md`: evidence classes, tiered output, retention
  registry (`kept.yaml`), trial-removal recovery model + per-platform CI gating +
  allow-with-residual-risk + config/codegen exemption. If the non-obvious workflow warrants
  it, invoke `doc-update-guidelines`.
- End-to-end verification (see Verification below).

### Out of Scope
- The classifier/registry implementation (AC-13/14 → TASK-PROC-061-19).
- The trial-removal implementation (AC-15 → TASK-PROC-061-20).

## Verification

Run `scripts/release/check_dependency_usage.py` and confirm:
- (a) `very_good_analysis` / `custom_lint` / `clean_architecture_kit` are classified
  config-referenced — **not** plain removal candidates;
- (b) native-declared packages appear in the needs-manual-review tier;
- (c) a keep written to the retention registry suppresses that package from the active
  removal-candidate list on the next run, and a stale entry (package gone) is reported;
- (d) the trial-removal procedure with per-platform CI-coverage gating is documented and was
  exercised (TASK-PROC-061-20's `local_notifier` demonstration).
Any AC not demonstrably met is a blocking error — do not complete until resolved.

## Acceptance Criteria

- [ ] `doc/process/dependency_lifecycle.md` documents the new evidence classes, tiered output, retention registry, and trial-removal model consistent with REQ-PROC-061 (AC-10)
- [ ] Verification (a)–(d) above all pass; AC-13, AC-14, AC-15 demonstrably met
- [ ] Any doc-only or script changes pass their respective gates

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-061-19 | pending | Classifier + registry must exist to document and verify |
| TASK-PROC-061-20 | pending | Trial-removal model must exist to document and verify |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-061-19](../2026-06-03_impl_harden-usage-check-classifier-and-registry/goal.md) | Predecessor — provides AC-13/14 behavior to document + verify |
| [TASK-PROC-061-20](../2026-06-03_impl_trial-removal-recovery-model/goal.md) | Predecessor — provides AC-15 behavior to document + verify |

## Notes

Process category — no `target_package`. This task merges the planned doc-sync (#10) and
verification tasks per developer direction; the Verification section satisfies the AC-02
verification-coverage requirement for the decomposition.
