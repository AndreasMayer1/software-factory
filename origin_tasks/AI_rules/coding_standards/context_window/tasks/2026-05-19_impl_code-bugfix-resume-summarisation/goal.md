---
task_id: TASK-PROC-001-09
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
scope_description: "Update the code-bugfix skill resume path: when plans_and_protocols/ exceeds N files or M KB, spawn a summarisation agent that returns a distilled session-history summary instead of reading every protocol inline."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ba1e025f
  file: ../../requirements.md
---
# Goal: code-bugfix resume-path summarisation

## Objective

`.claude/skills/code-bugfix/skill.md` currently re-reads every file under `plans_and_protocols/` when resuming a bugfix task. For long-running bugfix tasks the protocol set grows to tens of files and quickly consumes the per-task read budget — exactly the failure mode REQ-PROC-001 AC-05 targets. This task adds a threshold (N files or M KB) above which the resume path spawns a summarisation agent that reads the protocol set and returns a distilled session-history summary, instead of reading every protocol inline.

## Scope

- Edit `.claude/skills/code-bugfix/skill.md` resume section to add a size check on `plans_and_protocols/` (file count and total bytes).
- Above the threshold, spawn a summarisation agent (general-purpose, focused prompt) that returns the distilled history; below it, read inline as today.
- Calibrate N and M against the per-task budget defined in TASK-PROC-001-04's calibration work; cite the values inline.
- No changes to non-resume code-bugfix paths.

## Acceptance Criteria

- [ ] **AC-05** — Heavy skills that perform multi-file read passes (currently `requ-explore`, `task-resolve`, `task-create`, `release-begin-impl`) defer to agents for read-set scans when the per-task read budget is exceeded. This budget is distinct from the release-level threshold in `scripts/util/should_use_agents.py`, which governs release-scope scans only.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed-after-this-runs | Synthesis from explore task |
