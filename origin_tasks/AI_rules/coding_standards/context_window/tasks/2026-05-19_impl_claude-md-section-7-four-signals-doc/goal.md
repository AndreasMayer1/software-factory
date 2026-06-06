---
task_id: TASK-PROC-001-03
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
  acceptance_criteria: [AC-08]
  sections: []
scope_description: "Replace CLAUDE.md §7 Context-Window Rule with the four-signal framework (S1 tool-call volume, S2 scope openness, S3 synthesis dependency, S4 iterative-fix loop) and the composition rule from REQ-PROC-001."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: ba1e025f
  file: ../../requirements.md
---
# Goal: Document the four-signal framework in CLAUDE.md §7

## Objective

CLAUDE.md §7 today contains a single Context-Window Rule pinned to the 30 KB / 5 files threshold used by `scripts/util/should_use_agents.py`. The synthesis from TASK-PROC-001-02 introduced four signals (S1–S4) that together drive sizing decisions across creation-time and runtime — but those signals only exist in REQ-PROC-001 and the synthesis draft. Skills that should compose them when judging a task do not see them in the constitution. This task brings CLAUDE.md §7 in line with REQ-PROC-001 AC-08.

## Scope

- Replace the current Context-Window Rule text in CLAUDE.md §7 with a section documenting S1 (expected tool-call volume), S2 (scope openness), S3 (synthesis dependency), S4 (iterative-fix loop).
- Add the composition rule explaining how the signals combine into a sizing decision (monolithic vs split vs Opus vs agent fan-out).
- Preserve the existing 30 KB / 5 files release-level rule for `should_use_agents.py` — that threshold continues to govern release-scope scans only; mark this scope explicitly.
- Keep token footprint of CLAUDE.md §7 reasonable — the four signals recap in REQ-PROC-001 is the authoritative form, CLAUDE.md mirrors it.

## Acceptance Criteria

- [ ] **AC-08** — CLAUDE.md §7 ("Context-Window Rule") documents the four signals — S1 expected tool-call volume, S2 scope openness, S3 synthesis dependency, S4 iterative-fix loop — and their composition into a sizing decision, so every skill applies them consistently.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-001-02 | completed-after-this-runs | Synthesis from explore task |
