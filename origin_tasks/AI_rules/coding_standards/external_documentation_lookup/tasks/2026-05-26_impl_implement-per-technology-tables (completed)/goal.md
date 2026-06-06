---
task_id: TASK-PROC-053-05
type: impl
parent_requirement: REQ-PROC-053
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-26
completed: 2026-05-26
session_completed_at: 2026-05-26T21:51:38Z
effort: S
created: 2026-05-26
after: [TASK-PROC-053-03]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-06]
  sections: [SEC-04]
scope_description: "Create per-technology trigger threshold tables in doc/"
release_description: ""
opus_recommended: false
writes_requirements: false
requirements_version:
  commit: db92ca63
  file: ../requirements.md
session_id: 9bb4d948-7647-4f09-ac2e-34de774761ae
session_account: gmail
---
# Goal — Tier 3: Per-technology trigger threshold tables

## Objective

Publish the per-technology lookup trigger tables from the synthesis into `doc/`,
so skills and agents can reference them as the authoritative calibration.

## Scope

### In Scope

Per synthesis §6 and §6.7:

- `doc/architecture/dart_lookup_thresholds.md` — Dart/Flutter stack (§6.2)
- `doc/testing/test_framework_lookup_risk.md` — test-framework call-pattern risk (§6.6)
- `doc/python/lookup_thresholds.md` — Python scripts/ stack (§6.3)
- `doc/general/native_and_ci_lookup.md` — native build files + CI/config/shell (§6.4, §6.5)

**Naming fix**: The synthesis uses "Stability" to mean "churn rate" (low = rarely changes).
This naming is confusing. Use "Churn rate" as the column name instead
(low = API rarely changes = stable).

### Out of Scope

- The actual lookup logic (Tier 1).
- Skill checkpoint wire-in (Tier 2).

## Design Reference

Synthesis §6 (all subsections) in TASK-PROC-053-02 plans_and_protocols.

## Acceptance Criteria

- [x] Four doc files created with tables from synthesis §6
- [x] Column name "Churn rate" used (not "Stability")
- [x] Security-critical package allowlist codified (D5: flutter_secure_storage, sqlite3, cryptography, argon2)
- [x] `doc/cross_cutting_standards/documentation_lookup.md` updated with pointers to the new files

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-053-03 | pending | cross-cutting doc created there; add pointers here |
