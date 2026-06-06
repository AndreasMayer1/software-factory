---
task_id: TASK-PROC-061-06
type: impl
parent_requirement: REQ-PROC-061
urgency: 2
urgency_reason: U2-PROC-IMPROVEMENT
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-06-03
completed: 2026-06-03
session_completed_at: 2026-06-03T15:09:08Z
effort: S
created: 2026-06-02
expected_tool_calls: 30
skill_chain_depth: 2
after: []
covers:
  acceptance_criteria: [AC-11]
  sections: []
scope_description: "Add usage-check pass to the monthly dependency review runner so unused packages are flagged as removal candidates before version-bump evaluation"
release_description: ""
opus_recommended: false
requirements_version:
  commit: 3cbd51ab
  file: ../requirements.md
session_id: e94f3c46-fc95-4e91-8fda-31cd98b93c06
session_account: web

---
# Goal: Add Usage-Check Pass to Monthly Dependency Review Runner

## Objective

The monthly dependency review script (`scripts/release/check_dependency_sweep.py`) currently only scans for security advisories. The automation session that produces the review proposal (`automation/dependency_reviews/<month>/proposal.md`) evaluates version bumps without first checking whether each package is actually used. Add a usage-check pass that classifies every direct `pubspec.yaml` dependency before upgrade evaluation, so that unused packages are flagged as removal candidates rather than proposed for upgrades.

## Requirements Summary

REQ-PROC-061 AC-11 requires the monthly review to classify each direct dependency as: (a) directly imported, (b) indirectly required (with named dependency chain), or (c) no evidence of use. Class (c) packages go to the removal-candidates section of the proposal, not the upgrade section. The pass runs before version-bump evaluation.

For complete requirements at task creation time:
```
git show 3cbd51ab:requirements_tasks/process/AI_rules/ai_tool_management/dependency_lifecycle/requirements.md
```

Current requirements: ../requirements.md

## Scope

### In Scope
- New Python script (or module) under `scripts/` that scans `pubspec.yaml` direct dependencies and classifies each against Dart source imports in `lib/`, `test/`, `integration_test/`
- Handle the "indirectly required" case: a package is indirectly required if it is a known platform-binary companion, code-gen tool, or runtime support library for another direct dependency. The known indirect relationships must be discoverable (e.g. a configurable allow-list or convention)
- Output: structured classification result (directly imported / indirectly required / no evidence of use) per package
- Update the LLM prompt or automation instructions that produce `proposal.md` so the usage-check pass runs first and removal candidates are separated from upgrade candidates
- Python quality gates must pass (`scripts/quality/check_python_gates.sh`)

### Out of Scope
- Changing how `check_dependency_sweep.py` handles security advisory scanning
- Checking Python `scripts/` dependencies or npm manifests (Dart/pub only for this task)
- Automated removal of unused packages (flagging only; removal is a separate human-authorized step)

## Acceptance Criteria

- [x] A script or module exists that classifies all direct `pubspec.yaml` dependencies into (a) directly imported, (b) indirectly required, or (c) no evidence of use
- [x] The script scans `lib/`, `test/`, and `integration_test/` for import statements
- [x] Indirect requirements can be documented (e.g. `sqlite3_flutter_libs` → required by `drift` NativeDatabase)
- [x] Output distinguishes removal candidates from upgrade candidates
- [x] The monthly review automation instructions reference the usage-check step before DG1–DG4 evaluation
- [x] Python quality gates pass

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |
