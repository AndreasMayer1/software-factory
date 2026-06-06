---
task_id: TASK-PROC-027-01
type: impl
parent_requirement: REQ-PROC-027
urgency: 4
urgency_reason: U4-IMPL
impact: 4
impact_reason: I4-QUAL
status: pending
effort: L
created: 2026-02-07
after: []
awaiting: []
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Continue batch scenario generation for remaining personas and categories to reach ~15-20 total scenarios"
requirements_version:
  commit: a210650
  file: ../requirements.md
---

# Goal: Continue Scenario Generation (Batch 4 onwards)

## Objective

Continue batch scenario generation for remaining personas and categories to reach ~15-20 total scenarios, building on the work completed in TASK-PROC-010-10.

## Current Progress (as of 2026-02-07)

**Completed**: 8 scenarios across 4 personas (40% of ~20 target)

**By persona**:
- Jana: 2 scenarios (prepare_for_session, transfer)
- Sophie: 2 scenarios (prepare_for_session, transfer)
- Prof. Dr. Weber: 2 scenarios (prepare_protocol, review_collaboratively)
- Dr. med. Turan: 2 scenarios (prepare_protocol, review_collaboratively)

**Completed batches**:
- ✅ Batch 1: Therapist prepare_protocol (2 scenarios)
- ✅ Batch 2: Therapist review_collaboratively (2 scenarios)
- ✅ Batch 3: Client prepare_for_session (2 scenarios)
- ✅ Batch 5: Client transfer (1 scenario - Jana only)

## Scope

### In Scope

**Batch 4: `capture.spontaneous` - Client Spontaneous Capture** (HIGH PRIORITY)
- Generate for: Jana (BPD crisis capture), Sophie (ADHD spontaneous capture)
- Gold standard: SCEN-002-01 (Max brain_dump) - verify gold status first
- Expected: 2 scenarios

**Additional scenarios to reach ~5 per persona** (~8-12 more scenarios):
- Each persona needs ~3 more scenarios to reach target
- Categories to consider:
  - capture.routine (needs gold standard first)
  - analysis.self_reflect (for self_user personas if added)
  - Additional outcome variants of existing categories
  - Edge cases or failure modes

### Out of Scope

- Creating new personas (that would be a separate task)
- Modifying the scenario structure or templates (that's REQ-PROC-010)
- Creating user flows (separate task)

## Acceptance Criteria

- [ ] Batch 4 completed: Jana and Sophie each have a spontaneous capture scenario
- [ ] Quality review completed for all new scenarios
- [ ] SCENARIO_INDEX.md updated with all new scenarios
- [ ] All scenarios follow three-act structure and guidelines
- [ ] User reviews and approves each batch before continuing
- [ ] Target of ~15-20 total scenarios reached (or documented stopping point)

## How to Resume

1. Read resumption plan: `requirements_tasks/process/AI_rules/requirements_management/user_needs_structure/tasks/2026-02-02_impl_scenario_generation_strategy/plans_and_protocols/2026-02-07_03_resumption_plan.md`
2. Check SCENARIO_INDEX.md for coverage gaps
3. Start with Batch 4 (capture.spontaneous)
4. Use create-scenario skill with --use-opus for quality
5. Update SCENARIO_INDEX.md after each scenario
6. Present to user for review before continuing to next batch

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-010-10 | paused | Previous scenario generation work (8 scenarios created) |
| REQ-PROC-010 | implemented | User needs structure and guidelines |

## References

- Previous task: TASK-PROC-010-10
- Resumption plan: requirements_tasks/.../2026-02-07_03_resumption_plan.md
- Scenario index: requirements_user_needs/SCENARIO_INDEX.md
- Gold standards: Check SCENARIO_INDEX.md instances with gold_status: true

## Notes

This task picks up where TASK-PROC-010-10 left off. The previous task completed 8 scenarios (Batches 1, 2, 3, 5), and this task continues with Batch 4 and beyond to reach the ~20 scenario target.



# Pending Question

this task was started, but raised a question. i answered it. see below

## Task Context

**TASK-PROC-027-01** ("Continue Scenario Generation Batch 4") has `status: pending` (never started).

It was created on 2026-02-07 with this objective:
- Complete **Batch 4**: write `capture.spontaneous` scenarios for **Jana** and **Sophie**
- Add additional scenarios to reach **~15-20 total**

## Current State (as of 2026-04-19)

- **Total scenario files**: 86 (far exceeding the ~15-20 target)
- **Jana capture.spontaneous**: ✅ Done — 2 scenarios exist (`capture_data_spontaneously__black_book`, `capture_data_spontaneously__harm_reduction`)
- **Sophie capture.spontaneous**: ❌ Missing — `sophie_structure_seeker` has 6 scenarios but none in `capture.spontaneous` category

Sophie's ADHD profile differs from David's (SCEN-008-02 "The 3-Second Window"): Sophie is a **client with a therapist** (not a self-user), her core failure mode is **shame-driven streak-breaking and object permanence failure** (the app goes "out of sight = doesn't exist"), and her ADHD presents more as forgetting the tool exists vs. David's pure working-memory overwrite.

## Question

The overall target (15-20 scenarios) is massively exceeded. But Batch 4 AC-1 ("Jana and Sophie each have a spontaneous capture scenario") is only half-done.

**What should happen next?**

**Option A — Mark task complete as-is**
The 15-20 target is vastly exceeded. Sophie's spontaneous capture gap can be tracked as a separate idea in SCENARIO_INDEX.md rather than blocking this task. Mark TASK-PROC-027-01 as `completed`.

**Option B — Write Sophie's scenario first, then complete**
Generate a Sophie `capture_data_spontaneously` scenario (draft: ADHD app-forgetting + shame-after-gap mechanic, possibly titled something like "The App That Stopped Existing"), present it for your review, then complete the task. This scenario would focus on: Sophie opens a new tracker, uses it for 3 days, misses one morning, and never opens it again — the spontaneous-capture variant would be the moment she *tries* to record an emotional event and discovers she forgot the app exists entirely.

Please write your choice (A or B) in `answer.md`. If Option B, any notes on the scenario angle are welcome.




# ANSWER:

i lean towards Option B, but only if that scenario offers something new the other existing scenarios not already cover.. please verify. if it is redundant, close the task