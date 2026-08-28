---
task_id: TASK-PROC-068-24
type: bugfix
parent_requirement: REQ-PROC-068
urgency: 2
urgency_reason: U2-LATENT
impact: 3
impact_reason: I3-CORRECTNESS-HIGH-AC
status: completed
started: 2026-07-10
completed: 2026-07-10
session_completed_at: 2026-07-10T16:41:38Z
effort: S
created: 2026-07-10
expected_tool_calls: 25
skill_chain_depth: 2
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-14]
  sections: []
egp:
  - { ac: AC-14, archetype: F, referent: "a real interrupted build/maintain run observed to preserve the isolated copy and perform no harvest, and a real completed run observed to harvest then discard" }
consequence: HIGH
scope_description: "Harden the build-mode harvest so a mid-run crash cannot leave a partial/incoherent deposit in test_harness_app/ (AC-14)."
release_description: ""
opus_recommended: false
writes_requirements: false
worktree_path: ""
requirements_version:
  commit: 7b56c6ef
  file: ../../requirements.md
session_id: d44af56f-aaea-4767-a444-64fa8ee09d50
session_account: gmail
---
# Goal: Ensure that AC-14 of REQ-PROC-068 works correctly

## Objective

AC-14 (consequence: **HIGH**) guarantees that "a partial or incoherent deposit into
`test_harness_app/` **cannot happen**" — on any non-complete termination the isolated copy is
preserved and no harvest occurs. The current harvest implementation does not fully uphold this under
one termination class the AC explicitly names: **crash**.

`build.py`'s `harvest_authored` is a plain `shutil.copy2` loop, and `_gate_harvest` runs
harvest → flip registry `complete` → discard copy with **no atomicity**. A rare mid-run crash of the
`build.py` process (OOM, `kill -9`, devcontainer death, disk-full, unhandled exception, or the
orchestrator's session-timeout killing the process tree) can leave a **partial deposit** in
`test_harness_app/`. (Usage-limit is explicitly NOT a trigger: the harvest is host-side Python that
makes no model API call, so the usage limit cannot interrupt it — the harvest only runs after the LLM
child has cleanly exited.)

Close this gap **proportionately to its rarity**, without an in-script git-commit transaction.

## Bug Report

**Steps to reproduce:**
1. Start a build-mode run whose child cleanly completes the derivation chain.
2. Kill the `build.py` process during `harvest_authored` — after some product-definition files have
   been copied into `test_harness_app/` but before all of them are (e.g. `kill -9`, or simulate by
   injecting an exception between file copies).

**Expected behavior (AC-14):**
No partial or incoherent deposit is ever observable/consumable in `test_harness_app/`; the run remains
resumable and, once resumed, `test_harness_app/` holds exactly the full coherent deposit.

**Actual behavior:**
`test_harness_app/` is left with a subset of the authored files (and possibly a torn/truncated file).
The registry record stays `running` and the durable copy survives, so the state is *recoverable* — but
the partial deposit is present and, absent a fence, could be consumed/committed before resume repairs it.

**Environment:** devcontainer (host-side Python; no LLM in the harvest loop).

## Requirements Summary

AC-14 (HIGH, EGP archetype F): deposit into `test_harness_app/` and discard the copy only once an
explicit completion signal confirms the derivation finished; on any non-complete termination
(usage-limit, timeout, hung session, or **crash**) preserve the copy and skip harvest —
"preserve-by-default, discard-only-on-verified-complete, skip-harvest-on-incomplete."

For complete requirements at task creation time:
```
git show 7b56c6ef:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../../requirements.md

## Design (decided with developer — do not re-litigate)

- **Recovery = the existing idempotent re-harvest that the resume path already runs.**
  `harvest_authored` is copy-only (never deletes/renames), so a partial deposit is always a *subset* of
  the full deposit; re-running reproduces the complete, coherent set and overwrites any torn file. No
  LLM-driven git surgery.
- **The load-bearing safeguard is ONE fencing invariant:** nothing may consume/commit the
  `test_harness_app/` deposit while the run's registry record is `running` or `preserved` — only after
  `complete`. With the fence + idempotent re-harvest, no coherent-state consumer ever observes a partial
  deposit, which is exactly AC-14's guarantee.

## Scope

### In Scope
1. **FENCE (primary):** audit every path that commits or consumes harvested `test_harness_app/` content
   after a build-mode run (the outer-session / `task-complete` commit flow) and gate it on run-registry
   status == `complete`. Add the gate where missing.
2. **IDEMPOTENT RE-HARVEST (verify + test):** add a crash-injection test simulating a partial deposit
   (a subset of files pre-present, including a torn/truncated file) and assert that resume re-harvest
   yields the full coherent set (overwrite semantics). Handle the orphan-copy edge: registry already
   `complete` but the workspace copy not yet destroyed → discard the copy, do NOT re-harvest.
3. **DEFENSIVE CLEANUP (optional):** a path-scoped, HEAD-relative pre-harvest
   `git restore --source=HEAD --staged --worktree -- <product-def paths>` + scoped
   `git clean -fd -- <paths>` in `build_resume`, for torn-file tidiness. MUST be path-scoped to the
   product-definition globs and HEAD-relative — build mode ACCUMULATES (AC-11), so **never** a blanket
   `git reset --hard`, which would wipe prior committed harvests or the task's in-flight working-tree
   changes.

### Out of Scope
- The in-harvest git-commit-as-atomic-boundary transaction (rejected as heavier than a rare crash
  warrants).
- The completion-predicate / outcome-classification gap (finding #1 — a separate spec-gap task under
  the outcome-taxonomy requirement change).

## Acceptance Criteria

- [x] AC-14 — EGP: F (a real interrupted build/maintain run observed to preserve the isolated copy and perform no harvest, and a real completed run observed to harvest then discard); consequence: HIGH

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies |

## Notes

- Governance: scripts/ Python change → MUST go through `claude-write-script` + the Python quality gates
  (REQ-PROC-051). Hardening bugfix restoring already-documented AC-14 behavior — no `product-intake`.
- Related mechanism files: `scripts/playground/build.py` (`harvest_authored`, `_gate_harvest`,
  `launch_and_gate`), `scripts/playground/build_resume.py` (`resume_run`, `find_resumable_run`),
  tests `scripts/tests/test_playground_build.py`, `scripts/tests/test_playground_build_resume.py`.
- Priority is developer-defaulted (parent requirement is pre-migration on urgency/impact): U2 (latent,
  rare trigger) / I3 (correctness of a HIGH-consequence AC). Adjust if the developer prefers.
