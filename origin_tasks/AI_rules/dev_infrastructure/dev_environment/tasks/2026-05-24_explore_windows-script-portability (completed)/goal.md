---
task_id: TASK-PROC-054-05
type: explore
parent_requirement: REQ-PROC-054
urgency: 3
urgency_reason: U3-DEBT
impact: 3
impact_reason: I3-INCR
status: completed
effort: S
created: 2026-05-24
completed: 2026-05-24
after: [TASK-PROC-043-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Add REQ-PROC-054 ACs for Windows-host script location-independence: a shared project-path resolution mechanism driven by a co-located config file, a configurable copy/install tool, and the requirement that all current/future windows scripts use the mechanism."
release_description: ""
opus_recommended: false
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: c620543c
  file: ../../requirements.md
---

# Goal: Define Windows-host script portability mechanism on REQ-PROC-054

## Objective

AC-13 established that Windows-host scripts (sleep watcher) install **outside**
the repository. The manual procedure currently requires per-invocation
`-ProjectPath` wiring. Generalize this into a documented mechanism so that
**every** Windows-host script — current (sleep watcher trio, smoke_test_windows,
smoke_test_llm) and future — runs correctly from any out-of-repo location
without per-script edits.

Define the end state in REQ-PROC-054 (the actual scripts/tool are built in
follow-up impl tasks D/E/F):
1. A **shared project-path resolution mechanism**: scripts resolve the project
   tree they operate on (the synced NTFS mirror containing `automation/`, build
   outputs, …) via precedence: explicit param → config file co-located with the
   installed scripts → auto-derivation from own location (in-repo).
2. A **copy/install tool** that copies all `scripts/windows/` scripts to a
   configurable target outside the repo and writes the resolution config there
   (recording the mirror path). Default target:
   `<Windows-user-home>/projects/<project-name>/windows-scripts/`.
3. **Enforcement**: any new `scripts/windows/` script uses the mechanism rather
   than hardcoding/own-location-deriving paths (enforced by the script-authoring
   workflow).

## Requirements Summary

REQ-PROC-054 (`status: active`). AC-13 already permits the out-of-repo install
of host-side watchers with a narrow action surface. This task adds the
portability mechanism that makes the out-of-repo install ergonomic and uniform.

For complete requirements at task creation time:
```
git show c620543c:requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- New AC(s) for the resolution mechanism, the copy/install tool (configurable
  target + default path), and the new-script enforcement.
- Reconcile AC-13 wording (manual copy → tool) and the §13 setup-guide
  reference where needed.
- Developer Guideline capturing the "windows scripts must use the mechanism"
  rule.

### Out of Scope
- Implementing the mechanism, the helper, the tool, or migrating the scripts
  (Tasks D/E).
- The `claude-write-script` skill change that enforces it (Task F).
- Config-file format / helper naming — implementation details for Task D, not
  the requirement.

## Acceptance Criteria

- [x] REQ-PROC-054 has an AC defining the shared project-path resolution
      mechanism (AC-14: precedence explicit param → co-located config →
      auto-derive; config readable by both PowerShell and Python) and the
      resulting location-independence of windows scripts.
- [x] REQ-PROC-054 has an AC defining the copy/install tool (AC-15): copies all
      `scripts/windows/` scripts out of the repo, writes the config recording
      the mirror path, target configurable with the documented default.
- [x] REQ-PROC-054 states (AC-16 + Key Decision + Common Pitfall) that any new
      `scripts/windows/` script uses the mechanism; enforcement via the
      `claude-write-script` authoring workflow.
- [x] AC-13 reconciled (now references the AC-15 install tool); §13 setup-guide
      rewrite deferred to the Task E impl (no contradiction introduced).
- [x] Requirement stays `status: active`; AC-14/15/16 in YAML `trackable_items`.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-043-05 | completed | scripts/windows/ now holds only host-only scripts |
