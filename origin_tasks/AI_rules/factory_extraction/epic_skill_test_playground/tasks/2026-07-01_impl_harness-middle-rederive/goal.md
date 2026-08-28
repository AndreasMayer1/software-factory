---
task_id: TASK-PROC-068-12
type: impl
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: blocked
effort: M
created: 2026-07-01
started: 2026-07-08
expected_tool_calls: 45
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold the approved anchor layers and the fixed layer-derivation mechanism together to derive a conformant, coverage-closed, natural middle layer as one unit."
after: [TASK-PROC-071-05-05, TASK-PROC-068-11, TASK-PROC-071-06-06, TASK-PROC-041-01-12, TASK-PROC-068-18, TASK-PROC-071-06-07, TASK-PROC-068-21, TASK-PROC-068-22, TASK-PROC-068-23, TASK-PROC-071-06-08, TASK-PROC-071-06-09, TASK-PROC-068-26]
awaiting: ["user-unblock"]
awaiting_note: "Phase 1 (flow layer) complete + harvested. Phase 2 (requirement layer) needs a developer decision — requ-derive-from-flow hard-blocks unless FLOW-001/FLOW-002 are review_status: approved (they are draft), and reaching approved requires the human-rated Fit-Score walk. Question: automation/pending_feedback/TASK-PROC-068-12/question.md (options A–D + target bucket/budget); analysis: plans_and_protocols/2026-07-19_07_blocker_phase2-flow-approval-gate.md. Parked via awaiting[] rather than the pending_feedback channel because is_awaiting_answer.py currently mis-reports every parked task as answered (see 2026-08-01_09 protocol) — clear this field once the question is answered."
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Re-derive the harness MIDDLE layers (flows + requirements) from the approved conformant anchors using the FIXED layer-derivation mechanism (content gates wired), replacing the non-conformant TASK-PROC-068-07 output."
release_description: ""
opus_recommended: true   # reason: synthesis — holds approved anchors + fixed mechanism; corrected re-run of the terminal derivation
writes_requirements: false
requirements_version:
  commit: 9b25bde0
  file: ../requirements.md
session_id: 05cae057-2ee1-4806-b1e2-b877d7295fc5
session_account: gmail
session_last_run: 2026-08-01T03:44:22.501952+00:00
---
# Goal: Re-derive the Harness Middle Layers (Flows + Requirements) via the Fixed Mechanism

## Objective

Derive the harness's **middle** product-definition layers — flows and requirements — from the
**approved conformant anchors** (TASK-PROC-068-11) using the **fixed** layer-derivation mechanism
(TASK-PROC-071-05-05, with the content gates wired in). This replaces the non-conformant output of
TASK-PROC-068-07 with type-conformant, coverage-closed, natural artifacts.

## Background

TASK-PROC-068-07's middle-layer "derivation" ran a hand-rolled ID-coverage driver + freehand markdown,
bypassing the authoring skills and the content gates, producing non-conformant stub flows/requirements.
The root cause (the orphaned content gates) is fixed by TASK-PROC-071-05-05; the conformant anchors are
authored by TASK-PROC-068-11. This task runs the corrected end-to-end derivation.

For complete requirements at task creation time:
```
git show 9b25bde0:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

This derivation runs as a **deployed build-mode run** against the harness — inside an isolated deployed
copy of the factory, harvesting the derived middle layers back into `test_harness_app/`. It uses the
build-mode **resumability** mechanism built by the predecessors (068-21 wrapper, 068-22 registry/resume,
071-06-08 validated), so a mid-chain session termination or usage-limit does not lose committed work.

1. Confirm predecessors landed: the mechanism fix (071-05-05) is complete and its gates are wired; the
   anchors (068-11) are authored and **developer-approved**; the build-mode resumable wrapper
   (068-21), the run registry + `playground-build-resume` skill (068-22), and the deployed-resumability
   validation (071-06-08) are complete.
2. Launch the derivation as a **deployed build-mode run** via `scripts/playground/build.py` (the resumable
   wrapper): it deploys the factory into a durable out-of-project git-backed copy, seeds it from
   `test_harness_app/`, and runs the inner derivation there. Inside the copy the derivation is driven by
   the real `layer-derivation-start` chain — each unit dispatched through the correct authoring skill
   (`ux-create-flow` for scenario→flow, `requ-derive-from-flow`/`requ-explore` for flow→requirement) with
   the wired AC-02 density + AC-03 naturalness gates active, and a commit per unit.
3. On any mid-run interruption (session termination, usage-limit), the copy is **preserved** and no partial
   harvest occurs; a later session re-attaches from the run registry (via `playground-build-resume`) and
   resumes the chain from its committed units. Only on **verified completion** are the derived middle layers
   harvested into `test_harness_app/` and the copy discarded (preserve-by-default, discard-only-on-verified-complete).
4. Honour the two-tree split: all product content authored under `test_harness_app/requirements_*`.

## Scope

### In Scope
- Derive the flow layer (from approved scenarios) and the requirement layer (from flows) via the fixed
  mechanism + real authoring skills, README_5-conformant flows and conformant requirements.
- Carry the ADVISORY authority caveats on any consumed oracle verdict.

### Out of Scope
- Personas/scenarios (anchors — TASK-PROC-068-11).
- Any change to the mechanism itself (TASK-PROC-071-05-05).
- Tasks/code layers below requirements.

## Acceptance Criteria

- [ ] AC-1: Flow layer derived via `layer-derivation-start` + `ux-create-flow`, fully README_5-conformant
      (six required sections, correct frontmatter, happy-path table + exceptions).
- [ ] AC-2: Requirement layer derived from the flows via the factory requirement skills, conformant.
- [ ] AC-3: Every derived node passed the wired AC-02 density + AC-03 naturalness gates (no unit completed
      on a hollow/unnatural body); coverage closed against the anchors, minimal.
- [ ] AC-4: All product content lives under `test_harness_app/requirements_*` (two-tree split honoured).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-071-05-05 | pending | Mechanism fix — content gates must be wired first |
| TASK-PROC-068-11 | pending | Approved conformant anchors (personas + scenarios) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-071-05-05](../../../epic_layer_derivation/feat_minimality_naturalness/tasks/2026-07-01_impl_fix-layer-derivation-content-gate-seam/goal.md) | Predecessor — supplies the fixed, gate-wired mechanism |
| [TASK-PROC-068-11](../2026-07-01_impl_harness-anchors-reauthor/goal.md) | Predecessor — supplies the approved conformant anchors |

## Notes

- Coordinator-derived, covers-empty process task (no `target_package`) — surfaces only via the override.
- Corrected replacement for TASK-PROC-068-07's deliverable.
