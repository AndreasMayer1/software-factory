---
task_id: TASK-PROC-068-25
type: impl
parent_requirement: REQ-PROC-068
urgency: 3
urgency_reason: U3-MEASUREMENT-CORRECTNESS
impact: 4
impact_reason: I4-CORE-PLAYGROUND-PURPOSE
status: completed
effort: M
created: 2026-07-10
started: 2026-07-10
completed: 2026-07-14
session_completed_at: 2026-07-14T18:53:02Z
expected_tool_calls: 40
skill_chain_depth: 3
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-18, AC-19]
  sections: []
egp:
  - { ac: AC-18, archetype: F, referent: "a real build/maintain run's observed termination mode + acceptance-oracle result + presence/absence of a recorded blocker artifact, checked against the outcome the playground classifies and reports for it" }
  - { ac: AC-19, archetype: F, referent: "a real build/maintain run observed with no injected acceptance oracle (must not harvest, must not report success) and a real run whose child holds an in-flight background agent at -p return (must not be observed as a clean complete exit)" }
consequence: HIGH
scope_description: "Implement the build/maintain run-outcome taxonomy (complete/interrupted/blocked/abandoned) + fail-safe completion gate + clean-exit attribution in the playground (REQ-PROC-068 AC-18/AC-19)."
release_description: ""
opus_recommended: true  # reason: HIGH-consequence measurement-correctness mechanism — subtle errors in outcome classification / non-resume-of-skill-fail corrupt the playground's core purpose
writes_requirements: false
requirements_version:
  commit: e0f9d317
  file: ../../requirements.md
session_id: 54478fa2-8a57-4e13-ae50-de13ee3e5cb7
session_account: gmail2
---
# Goal: Implement the build/maintain run-outcome taxonomy (REQ-PROC-068 AC-18/AC-19)

## Objective

Realize the run-outcome classification that AC-18 and AC-19 (added to REQ-PROC-068 this session)
specify. Today the playground's harvest gate (`build.py` `_gate_harvest`) collapses two very different
situations into "success": a genuinely-complete run AND a run whose child merely *exited cleanly*. With
no injected completion predicate the gate defaults `is_complete = True`, so a premature clean exit
(a session that silently believes it is done, or a still-working background agent that lets `-p` return
0) is harvested as success. That destroys the playground's most important measurement — detecting that
the **skill under test** did not equip the session with a clear enough definition-of-done — and, if the
run were instead routed to resume, would loop forever (resume cannot fix a skill that stops early).

Make the four outcomes real and give each its correct disposition, with a fail-safe gate and a
trustworthy "clean exit" signal.

## Requirements Summary

- **AC-18** (EGP F, HIGH): every run resolves to exactly one classified outcome — **complete**
  (clean exit + acceptance oracle confirms → harvest), **interrupted** (non-clean termination →
  preserve + resume, the AC-14/15/16 path), **blocked** (clean exit + explicit blocker/escalation
  artifact → developer-facing pause, not a skill failure), **abandoned** (clean exit, oracle says
  not-finished, no blocker → reported as a skill-under-test completion-guidance FAILURE; neither
  harvested nor auto-resumed).
- **AC-19** (EGP F, HIGH): the completion gate never certifies complete without a positive
  acceptance-oracle result (absent oracle → "cannot certify"; no silent harvest, no silent pass); a
  clean child process-exit reflects the child's own completion decision (a still-working background
  agent cannot produce a false clean exit).

For complete requirements at task creation time:
```
git show e0f9d317:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../../requirements.md

## Scope

### In Scope
1. **Outcome classifier (AC-18):** in `build.py` `_gate_harvest` (and the resume tail in
   `build_resume.py`), replace the binary complete/preserve decision with a four-way classification:
   - `complete` = `result.succeeded && reason==exited && acceptance_oracle==done` → harvest + discard.
   - `interrupted` = non-clean termination (rc!=0 / reason!=exited / hung / timeout) → preserve + mark
     resumable (existing AC-14/15/16 path).
   - `blocked` = clean exit + an explicit blocker/escalation artifact recorded in the copy (e.g. a
     `pending_feedback` question) → preserve as a developer-facing pause; NOT harvested, NOT reported as
     a skill failure.
   - `abandoned` = clean exit + oracle reports not-finished + no blocker artifact → reported as a
     run **failure attributable to the skill-under-test's completion guidance**; NOT harvested, NOT
     auto-resumed. Record the outcome on the run-registry record so a resume path never re-launches it.
2. **Fail-safe completion gate (AC-19, part 1 — fixes finding #1a):** an **absent** completion predicate
   must mean "cannot certify complete" (→ preserve/inconclusive, never harvest, never report success).
   Wire the real **ChainState-complete** acceptance oracle into the layer-derivation build-mode
   invocation (AC-17's injected-predicate seam already exists; the production caller must actually pass
   it). ChainState-complete is one instance of the oracle, not the gate itself.
3. **Clean-exit attribution (AC-19, part 2):** set `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` in the
   build-mode child env (`build.py` `child_env`, currently bare `dict(os.environ)`) so a still-working
   background agent inside the child cannot cause `-p` to return 0 prematurely and be observed as a
   clean, complete exit. (Same defense the orchestrator's `build_env` applies.)
4. **Tests:** unit tests for each of the four classifications (incl. abandoned = clean-exit-but-oracle-
   not-done → reported failure, not harvested, not resumable), the absent-oracle fail-safe (no harvest,
   no success), and a test that the bg-wait ceiling is set on the child env.

### Out of Scope
- The harvest-atomicity / crash-recovery hardening (finding #3) — separate task **TASK-PROC-068-24**.
- The single-runner-liveness / concurrent-run lease (AC-15 clarification only documents the assumption;
  no lease mechanism is built here).
- Any change to the orchestrator (`scripts/automation/orchestrate.py`).

## Acceptance Criteria

- [x] AC-18 — EGP: F (a real build/maintain run's observed termination mode + acceptance-oracle result + presence/absence of a recorded blocker artifact, checked against the outcome the playground classifies and reports for it); consequence: HIGH
- [x] AC-19 — EGP: F (a real build/maintain run observed with no injected acceptance oracle (must not harvest, must not report success) and a real run whose child holds an in-flight background agent at -p return (must not be observed as a clean complete exit)); consequence: HIGH

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Independent of TASK-PROC-068-24 (harvest atomicity) — different mechanism area |

## Notes

- **Standalone-override**: created as a single focused impl task rather than routing to
  `task-derive-from-requ`. REQ-PROC-068 is a large, mostly-built requirement (AC-01..AC-17 implemented);
  AC-18/AC-19 are the only new uncovered ACs and form one coherent deliverable, so a full requirement
  re-decomposition is unwarranted.
- Governance: scripts/ Python change → MUST go through `claude-write-script` + the Python quality gates
  (REQ-PROC-051), and `verify-quality` before `task-complete`.
- HIGH-consequence EGP note: AC-18/AC-19 carry EGP archetype F / consequence HIGH. The two
  HIGH-consequence dispositions were **approved by the developer on 2026-07-10** at the §2.2b authoring
  gate (auto-accepted during Direct-Edit authoring while away, then confirmed on return). Per the gate,
  a developer sign-off is still required at EGP-verification time.
- Mechanism files: `scripts/playground/build.py` (`_gate_harvest`, `launch_and_gate`, `_build_claude_cmd`,
  `child_env`), `scripts/playground/build_resume.py`, the layer-derivation build-mode caller that must
  inject the ChainState oracle, tests under `scripts/tests/`.
