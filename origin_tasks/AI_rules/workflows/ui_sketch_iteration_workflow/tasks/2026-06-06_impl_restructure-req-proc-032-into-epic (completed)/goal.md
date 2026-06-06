---
task_id: TASK-PROC-032-34
type: impl
parent_requirement: REQ-PROC-032
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
completed: 2026-06-06
effort: XL
created: 2026-06-06
expected_tool_calls: 80
skill_chain_depth: 2
synthesis_dependent: true
synthesis_justification: "Seam map must hold all 70 ACs + 21 sections + downstream reference graph simultaneously to partition without breaking fidelity."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Restructure oversized REQ-PROC-032 into an epic + child feature requirements, distributing ACs/sections byte-exact (no spec change), with full crosswalk, diff-verification, reference rewrite, and in-flight-task retargeting."
release_description: ""
opus_recommended: true   # reason: cross-cutting fidelity-critical refactor — 70 ACs + 21 sections + 22 referencing files must move with zero specification drift
writes_requirements: true
requirements_version:
  commit: 9a73678c
  file: ../requirements.md
---

# Goal: Restructure REQ-PROC-032 into an Epic + Feature Requirements

## Objective

REQ-PROC-032 ("UI Scribble Iteration Workflow") has grown to **70 acceptance
criteria (AC-01…AC-70)** and **~21 body sections (SEC-…)** across 958 lines /
100 KB — far past a single implementable requirement. Restructure it into:

- an **epic** (folder `epic_<name>`) that **keeps the ID `REQ-PROC-032`**, and
- a set of **child feature requirements** `REQ-PROC-032-01 … REQ-PROC-032-0N`
  (folders `feat_<name>`), each owning a coherent subset of the ACs and sections.

**HARD CONSTRAINT — zero specification drift.** No AC description text and no
body-section prose may change in wording. Content is moved **byte-exact via a
migration script (no LLM in the copy path)** and verified by a
**normalizing-diff harness** against the git-golden version
(commit `9a73678c`, blob `cf51a2ba`) until the diff is empty modulo the three
explicitly-allowed transforms (AC renumbering, new epic/feature frontmatter,
section relocation).

## Requirements Summary

REQ-PROC-032 is the canonical definition of the scribble iteration workflow.
It is referenced by **106 files**; **22 of those (plus the redesign
implementation-task-manifest) cite specific AC numbers** and form the AC-level
blast radius. Four sibling tasks are mid-flight and paused
(TASK-PROC-032-30/31/32/33).

For complete requirements at task creation time:
```
git show 9a73678c:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## Developer Decisions (locked before execution)

1. **AC numbering: renumber per feature.** Each feature restarts AC-01…; a full
   `old (REQ-PROC-032 / AC-xx) → new (REQ-PROC-032-0N / AC-yy)` crosswalk is the
   load-bearing artifact. Every AC-level reference across the 22 files + the
   manifest is rewritten from it.
2. **Migration: scripted byte-exact + empty-diff gate.** A script slices exact
   AC/section ranges from the golden file and writes them verbatim into feature
   files. No requ-explore agent authors content (would paraphrase). The
   normalizing-diff harness is the pass condition; rerun "as many times as it
   takes" until empty.

## Scope

### In Scope
- Define the feature seam map (which ACs/sections → which feature) — **developer
  approval gate before any file is written**.
- Allocate epic + feature REQ-IDs via `allocate_req_id.py`.
- Scripted byte-exact content migration into feature files.
- Crosswalk authoring + reference rewrite across the 22 files + manifest.
- Regenerate generated artifacts (requirements.md merge, id_registry, STATUS).
- Retarget the 4 in-flight tasks (30/31/32/33) via their `pending_feedback`
  `answer.md` to resume against the new feature structure.
- Verification: empty normalizing-diff + green coverage/cross-ref scripts.

### Out of Scope
- Any change to specification wording, AC intent, or section meaning.
- Implementing the ACs themselves (derivation/impl happens after, per the
  retargeted in-flight tasks).
- Restarting the paused orchestrator (developer controls that; it stays stopped
  until this task's verification is green and the answer files are retargeted).

## Acceptance Criteria

- [x] Feature seam map (AC/section → feature) authored and **developer-approved**.
- [x] Epic `REQ-PROC-032` + child features `REQ-PROC-032-0N` created with valid frontmatter.
- [x] All ACs + sections migrated byte-exact via script (no manual retyping).
- [x] `old → new` AC crosswalk complete and covers all 70 ACs (bijective).
- [x] Normalizing-diff harness reports **empty diff** vs golden `9a73678c` (verified 3×, incl. orchestrator-independent check).
- [x] Live AC-citing references rewritten per crosswalk (7 feature bodies, 20 completed-task `covers`, 2 docs). Historical/narrative prose + the implementation-task-manifest left as snapshots per developer decision (2026-06-06).
- [x] Generated files regenerated; `coverage_report.py` + `check_cross_refs.py` run (coverage residue accepted per developer decision).
- [x] The 4 in-flight tasks' `answer.md` retargeted to the owning features; their `parent_requirement` updated (`covers` were empty — authoring tasks). New `derive-F06` task created for the fused feature.
- [x] Developer approved the final structure (each phase gated); orchestrator left stopped for the developer to resume.

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Orchestrator stopped | done | Developer confirmed; must stay stopped until verification green |
| Clean golden baseline | done | requirements.md == HEAD (blob cf51a2ba) |

## Notes

- **3c redirect override**: this is a structural refactor of the requirement, NOT
  AC implementation — task-create's standalone redirect to `task-derive-from-requ`
  is intentionally overridden. `covers` is empty by design.
- Epics are non-implementable: the in-flight tasks' future `task-derive-from-requ`
  step must retarget to the owning **feature**, never the epic.
- All migration/crosswalk/verification scripts live under this task's
  `plans_and_protocols/` (or `scripts/` via `claude-write-script` if reusable).
