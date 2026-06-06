---
task_id: TASK-PROC-054-06
type: explore
parent_requirement: REQ-PROC-054
urgency: 3
urgency_reason: U3-DEBT
impact: 4
impact_reason: I4-RISK
status: completed
effort: S
created: 2026-05-24
completed: 2026-05-24
after: [TASK-PROC-054-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Ground the Windows-host script review-before-execute safety control set (install-tool diff+hash gate, deterministic denylist checker, advisory-only LLM, Sandbox containment) and the windows test location + runner in REQ-PROC-054."
release_description: ""
opus_recommended: false
writes_requirements: true
worktree_path: ""
requirements_version:
  commit: 4e24851f
  file: ../../requirements.md
---

# Goal: Ground Windows-host script safety + test-location rules in REQ-PROC-054

## Objective

The Windows-host scripts (sleep watcher, smoke tests, the AC-15 install tool,
the AC-14 helper) are LLM-authored and run on the host, some elevated. The
developer cannot realistically review every script on every run. Define the
control set that bounds per-run review to what changed and never substitutes an
LLM verdict for human judgment.

Add two ACs to REQ-PROC-054:
1. **AC-17 — review-before-execute control set**: (a) the AC-15 install tool is
   the single choke point and surfaces the `git diff` of `scripts/windows/`
   since the last install plus a per-file SHA-256 manifest, requiring explicit
   confirmation before copying out-of-repo; (b) a small, deterministic,
   denylist-based safety checker (NO LLM) scans the windows scripts for a fixed
   set of dangerous constructs and is itself small enough to review once and pin
   by hash; (c) any LLM-assisted review is advisory only — it may summarize or
   flag but never auto-approves or replaces the human verdict; (d) a disposable
   Windows Sandbox is a supported containment environment for first/unreviewed
   runs and for developing/testing the pure-logic PowerShell.
2. **AC-18 — test location + runner**: Windows-host script tests live under
   `scripts/windows/tests/` (not co-located beside the scripts); a single test
   runner there discovers and runs all of them; the AC-15 install tool excludes
   `scripts/windows/tests/` from out-of-repo deployment.

## Background (why LLM-as-gate was rejected)

An earlier idea — a PowerShell script that launches Claude on the host to judge
script safety — was evaluated and rejected as a *gate*: it is circular (the
checker/launcher is itself unreviewed LLM-authored code that runs first), an LLM
is not a sound boundary against adversarial code, it is vulnerable to prompt
injection from the very files under review, it is non-deterministic, and a
"Claude said safe" verdict creates false assurance that erodes review. The
sound controls are deterministic (denylist + diff/hash) plus bounded human
review of the diff; LLM review is retained only as an advisory accelerator.

For complete requirements at task creation time:
```
git show 4e24851f:requirements_tasks/process/AI_rules/dev_infrastructure/dev_environment/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
- AC-17 (control set) and AC-18 (test location + runner) on REQ-PROC-054.
- Developer Guideline + Common Pitfall (LLM-as-gate is not a control;
  review the diff, not everything).
- Reconcile AC-15 wording to reference the review gate.

### Out of Scope
- Implementing the install tool, checker, runner, helper, migration, Sandbox
  config (Tasks D/E).
- The claude-write-script enforcement change (Task F).

## Acceptance Criteria

- [x] AC-17 added: install-tool diff+hash review gate, deterministic denylist
      checker (no LLM, hash-pinned), advisory-only LLM framing, Sandbox
      containment.
- [x] AC-18 added: windows tests in `scripts/windows/tests/`, a test runner,
      install tool excludes the tests folder.
- [x] A Developer Guideline + Common Pitfall capture "LLM is not the gate;
      review the diff, not the whole tree".
- [x] AC-15 reconciled to reference the review gate.
- [x] Requirement stays `status: active`; AC-17/AC-18 in YAML `trackable_items`.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-054-05 | completed | Defines the mechanism + install tool these controls wrap |
