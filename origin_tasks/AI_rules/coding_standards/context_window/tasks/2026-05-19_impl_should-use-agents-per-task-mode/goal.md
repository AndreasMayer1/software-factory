---
task_id: TASK-PROC-001-04
type: impl
parent_requirement: REQ-PROC-001
urgency: 4
urgency_reason: U4-PROC
impact: 4
impact_reason: I4-ENAB
status: pending
effort: S
created: 2026-05-19
after: [TASK-PROC-001-02]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-05]
  sections: []
scope_description: "Extend scripts/util/should_use_agents.py with a per-task input mode (--paths or --goal) so skills can evaluate the read-budget for a specific file set, distinct from the existing release-scope mode."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ba1e025f
  file: ../../requirements.md
---
# Goal: Add per-task mode to should_use_agents.py

## Objective

The current `scripts/util/should_use_agents.py` script governs release-level fan-out decisions with its 30 KB / 5 files threshold. Heavy multi-read skills like `requ-explore`, `task-resolve`, and `task-create` need an equivalent check scoped to a specific file set (a goal.md scope list, an explicit `--paths` argument). This task adds that mode so per-task read-budget enforcement (REQ-PROC-001 AC-05) becomes mechanical instead of judgment-based.

## Scope

- Add `--paths f1,f2,...` or `--goal PATH` input modes to `scripts/util/should_use_agents.py`. The release-scope mode stays as-is.
- Calibrate the per-task threshold based on the synthesis from TASK-PROC-001-02 (note: per-task threshold may differ from the release 30 KB / 5 files cap).
- Add pytest coverage for the new mode under `scripts/tests/` covering: closed file set under budget → no agent; over budget → agent recommended; non-existent path → clear error.
- Update the script's docstring / `--help` to distinguish the two modes.

## Acceptance Criteria

- [ ] **AC-05** — Heavy skills that perform multi-file read passes (currently `requ-explore`, `task-resolve`, `task-create`, `release-begin-impl`) defer to agents for read-set scans when the per-task read budget is exceeded. This budget is distinct from the release-level threshold in `scripts/util/should_use_agents.py`, which governs release-scope scans only.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed-after-this-runs | Synthesis from explore task |
