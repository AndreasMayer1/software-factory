---
task_id: TASK-PROC-044-08
type: impl
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 4
impact_reason: I4-QUAL
status: completed
started: 2026-05-30
completed: 2026-05-30
session_completed_at: 2026-05-29T23:25:17Z
effort: S
created: 2026-05-29
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-03]
  sections: []
scope_description: "Codify the 4-signal sub-skill-vs-agent rubric in claude-create-skill (Phase split decision sub-section) AND claude-modify-skill (Re-evaluate phase split sub-section). The rubric: (S1) independent invocation possible? (S2) fan-out to ≥2 agents? (S3) natural human review point? (S4) file-based artifact crossing boundary? Split if 2+ signals YES. Include the SCRIBBLE-SPLIT worked example. Track Wave-2/3 refinements via revision_target.yaml landed by FU-2 and FU-3."
release_description: ""
opus_recommended: false   # reason: small, scoped documentation work in 2 existing skills
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-6
session_id: d1fe4225-fdd1-425e-adc1-76ccdf3e0663
session_account: web

---
# Goal: Codify the Sub-Skill-vs-Agent Rubric in claude-create-skill + claude-modify-skill

## Objective

Make the sub-skill-vs-agent rubric a permanent part of skill authoring discipline. Without it, skills tend to grow organically and Hermify's "rebuilding CrewAI inside an agent" anti-pattern returns (file 02 §Q3).

## Background

The rubric was synthesized from LangGraph + CrewAI + Hermify evidence (web research file 02 §Q3) and validated on SCRIBBLE-SPLIT in the exploration (Round 1 §3.2).

Both claude-create-skill (authoring time) AND claude-modify-skill (modification time) need the rubric because — per Hermify — adding a phase to an existing skill might tip a previously-correct 2/4 to a clearer 3/4 (now split) or drop a 2/4 to 1/4 (now collapse into the parent).

## How to Approach This

1. Read `05_round_3_synthesis.md` §D-1 §3.1-3.4 + Round-1 §3 + web research file 02 §Q3.
2. Use `claude-modify-skill` to add a "Phase split decision" sub-section to `claude-create-skill/SKILL.md`. The sub-section includes:
   - The 4 binary signals (definitions + why each matters)
   - The split-if-2+ rule
   - The SCRIBBLE-SPLIT worked example (showing 1/4, 3/4, 3/4, 2/4 scores and verdicts)
3. Use `claude-modify-skill` to add a "Re-evaluate phase split" sub-section to `claude-modify-skill/SKILL.md`. The sub-section says: when a skill modification adds or splits a phase, re-run the rubric; document the new score in the modify-skill protocol.
4. Add a tracking subsection to this task's `plans_and_protocols/` that will receive revision_target.yaml entries from FU-2 (Wave 2) and FU-3 (Wave 3) if rubric refinements are proposed during those rollouts.
5. After all 3 waves complete: synthesize the refinement notes into a final rubric v2 (or confirm v1 holds). This synthesis can be deferred to a follow-up task if v1 holds; capture it inline here if any refinement is needed.

## Acceptance Criteria

- [x] `claude-create-skill/SKILL.md` has a "Phase split decision" sub-section with the 4 signals + decision rule + worked example
- [x] `claude-modify-skill/SKILL.md` has a "Re-evaluate phase split" sub-section with the trigger condition + re-run instructions
- [x] Both modifications use `claude-modify-skill` skill (per CLAUDE.md MANDATORY rule for skill modifications)
- [x] This task's `plans_and_protocols/` has a tracking entry ready to receive Wave-2/3 refinement proposals
- [ ] After Wave 3 completes: synthesis note recording v1 (no refinement) or v2 (with refinements)

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | Parallel-eligible; codification can happen any time; refinement synthesis is gated by FU-3 completion |

## Notes

This task is in `flutter_app/.claude/task_ordering_priority_override.txt`. The refinement-synthesis sub-task can be deferred or folded into FU-3's completion criteria — choose based on real-world evidence emerging from FU-2.
