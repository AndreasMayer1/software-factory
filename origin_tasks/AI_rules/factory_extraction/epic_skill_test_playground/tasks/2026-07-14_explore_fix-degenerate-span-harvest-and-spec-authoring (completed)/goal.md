---
task_id: TASK-PROC-068-27
type: explore
parent_requirement: REQ-PROC-068
urgency: 4
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-07-15
completed: 2026-07-17
session_completed_at: 2026-07-17T19:09:40Z
effort: M
created: 2026-07-14
expected_tool_calls: 55
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold the layer-derivation span/completion mechanism, the HIGH-consequence build-mode harvest oracle/taxonomy (AC-18/19), and the spec-authoring surface together to choose one coherent design without regressing any."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Design (via ideation) the fix for the degenerate zero-authoring-pair span vs harvest-oracle conflation, modify the governing requirements (clarify AC-18/19 + add ACs for a plan-time harvestability pre-flight and spec-authoring guidance), then emit the impl chain."
release_description: ""
opus_recommended: true   # reason: high-stakes open design at the gate/harvest seam (HIGH-consequence AC-18) + skill/requirement authoring
writes_requirements: true
requirements_version:
  commit: e0f9d317
  file: ../requirements.md
session_id: de9647b5-61b2-4b75-9729-0bf119b96ce6
session_account: gmail2
---
# Goal: Design + Ground the Degenerate-Span Harvest Fix (ideation → requirements → impl)

## Objective

Decide, by structured design rather than reflex, **how** the layer-derivation build-mode pipeline
should treat a **degenerate zero-authoring-pair span** so a legitimately-complete chain harvests — and
**where** that decision lives (mechanism disposition vs. harvest oracle), **what** guardrail catches the
class before a run is spent, and **how** the LLM that authors these specs is taught the model. Then
modify the governing requirements to capture it, and emit the implementation.

This is NOT yet known and must be worked out here:
- Should the fix change the **mechanism** (a degenerate span completes vacuously DONE) or the **harvest
  oracle** (tolerate a degenerate/no-op unit)? Each has different blast radius and truthfulness.
- AC-18 (HIGH, EGP-F) currently classifies exactly this case as **abandoned** — *"a run failure
  attributable to the completion guidance of the skill under test."* That mis-blames the skill. How
  should AC-18/AC-19 be clarified so a degenerate no-op unit is **not** an abandonment/blame signal,
  without weakening their real guarantees?
- Where does a **harvestability pre-flight** belong, and what is its contract?
- Do we need a **dedicated spec-authoring skill**, or is extending `layer-derivation-start` + a governed
  spec template enough?

## Background

TASK-PROC-068-26 hit this defect (`../2026-07-14_impl_harness-materialization-layer-derive/plans_and_protocols/2026-07-14_02_blocker_oracle-vs-degenerate-unit.md`).
`fixed_layers=[persona, scenario]` resolves to 2 spans; span-0 (persona↔scenario) has zero authoring
pairs, `plan_chain` forces one unit per span, its default disposition is ESCALATED, and the strict
all-DONE harvest oracle (`scripts/playground/acceptance_oracles.py`, wired by TASK-PROC-068-25) then
refuses to harvest — so a chain that plans fine can never harvest. A per-task Option-A workaround
(certify the approved boundary to DONE) was applied to 068-26 and 068-12 (`_03`), but the root cause,
the missing guardrail, and the missing authoring guidance should be fixed once, properly.

Why this is a design task, not a bare impl: the disposition change collides with a **HIGH-consequence
EGP-F** acceptance criterion (AC-18), the fix locus is a genuine trade-off, and two net-new capabilities
(pre-flight, spec-authoring surface) are not grounded in any current AC. New/changed behaviour must be
grounded in requirements first (factory rule) — so this task ideates the design, edits the requirements,
and only then emits the impl.

The developer's directive that prompted this framing is preserved in:
`plans_and_protocols/2026-07-14_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show e0f9d317:requirements_tasks/process/AI_rules/factory_extraction/epic_skill_test_playground/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Design thinking, then grounding, then emission. Do not jump to code.

## Seeds

- The word **ESCALATED** is doing two jobs — "blocked" and "skip this no-op". Untangle them: is the
  right primitive a distinct *degenerate/vacuous* disposition, or does the oracle simply not count it?
- AC-18's blame clause is load-bearing (EGP-F, HIGH). A clarification must keep "abandoned = the
  skill-under-test silently under-finished" true while excluding "the chain had a mandatory no-op span".
- `plan_chain`'s "one unit per resolved span" rule is what *forces* the degenerate unit. Is the cleanest
  fix upstream (don't emit a unit for a zero-pair span) rather than downstream (tolerate it)?
- "plan-success ≠ harvestable" is the trap that bit the spec author (an LLM). A pre-flight that
  simulates completion+oracle turns it into a loud plan-time failure — but where, and how much should it
  simulate?
- The developer never hand-writes the spec. What is the smallest artifact that reliably teaches an LLM
  the span↔unit mapping and the degenerate-span rule — a template, a contract, a skill? (Not `doc/`.)

## Execution Model

Routed execution (`requ-explore`, and `task-resolve` → `ideation-start`) owns the phase mechanics.
Expected shape: **(1)** structured **ideation** on the four open questions above → synthesis with a
recommended design; **(2)** developer approval of the synthesis; **(3)** **`requ-explore`** to modify
REQ-PROC-068 (clarify AC-18/19; add a harvestability-pre-flight AC) and REQ-PROC-071 /
`layer-derivation-start` (spec-authoring guidance AC); **(4)** **`task-derive-from-requ`** to emit the
impl task(s), each appended to the priority override per the recursive override rule.

## Output

A recorded design decision (fix locus + degenerate-span semantics + pre-flight contract +
spec-authoring surface), the corresponding requirement edits (AC-18/19 clarified, new ACs added), and
the emitted impl task(s) that realize them. A future implementer should be able to read the requirements
alone and build the fix, with the Option-A per-task workaround no longer needed.

## Acceptance Criteria

- [x] Ideation produced at least one synthesis round covering the fix-locus trade-off, the AC-18/19
      clarification, the pre-flight contract, and the spec-authoring surface. (IDEATION-023; `2026-07-15_004_synthesis.md`)
- [x] The synthesis defines the design in terms not fully known at task creation, and is honest about
      residual uncertainty. (the VACUOUS structural-proof-gated primitive; Residual R1–R5 section)
- [x] The developer approved the synthesis and the intended requirement changes. (APPROVE — `2026-07-17_05_feedback-checkpoint.md`; R1/R2 taken as recommended)
- [x] Requirements modified via `requ-explore`: AC-18/AC-19 clarified so a degenerate no-op unit is not
      an abandonment/blame signal; new ACs added for the harvestability pre-flight (REQ-PROC-068 AC-22) and
      the spec-authoring guidance/skill (REQ-PROC-071-06 AC-10, + the mechanism disposition AC-09).
- [x] Impl task(s) emitted via `task-derive-from-requ` and appended to the priority override
      (TASK-PROC-071-06-10, TASK-PROC-068-30); the Option-A workaround in 068-26/068-12 is documented as
      retire-able once they land (both task goals + override comment).

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-068-25 | completed | Wired the chainstate acceptance oracle / AC-18/19 taxonomy this task revises |
| TASK-PROC-068-26 | pending | Discovery source (`_02` blocker, `_03` Option-A workaround) |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-068-26](../2026-07-14_impl_harness-materialization-layer-derive/goal.md) | Discovered this defect; carries the Option-A workaround this task makes retire-able |
| [TASK-PROC-068-25](../2026-07-10_impl_build-run-outcome-classification/goal.md) | Built the harvest oracle / AC-18/19 taxonomy this task revises |

## Notes

- Coordinator/mechanism design task, covers-empty process task (no `target_package`) — surfaces via the
  priority override. `writes_requirements: true`.
- Recursive override rule: every impl task this task emits (and their children) MUST be appended to
  `.claude/task_ordering_priority_override.txt` on creation.
- Gate/mechanism discipline: do NOT hand-edit gates; route `scripts/**` via `claude-write-script`, skill
  edits via `claude-modify-skill`, requirement edits via `requ-explore`.
