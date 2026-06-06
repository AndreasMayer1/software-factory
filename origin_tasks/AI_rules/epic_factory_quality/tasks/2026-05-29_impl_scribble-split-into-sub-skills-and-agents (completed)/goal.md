---
task_id: TASK-PROC-044-07
type: impl
parent_requirement: REQ-PROC-044
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-05-30
completed: 2026-05-30
effort: L
created: 2026-05-29
after: [TASK-PROC-044-05]
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-03]
  sections: []
scope_description: "Refactor ui-create-scribble into: thin orchestrator ui-scribble-iterate (owns iteration loop + version tracking); 3 sub-skills (ui-scribble-auto-review, ui-scribble-feedback-classify, ui-scribble-approve-handoff); 6 agents (ui-scribble-generator, ui-scribble-rule-reviewer, ui-scribble-heuristics-reviewer, ui-scribble-persona-walker, ui-scribble-feedback-classifier, ui-scribble-handoff-emitter). Each sub-skill carries contract.yaml per the format from FU-1. Apply the sub-skill-vs-agent rubric to confirm the 3/4 + 2/4 split holds in production. Existing consumers (ui-verify-flutter, ui-improve-flutter, code-simple, code-complex) gain one-line edits to point at new producer names."
release_description: ""
opus_recommended: true   # reason: large refactor of a 285-line skill into 4 skill files + 6 agent files; cross-skill consumer edits
writes_requirements: false
requirements_version:
  commit: b10665f5
  file: ../../requirements.md
source_exploration: TASK-PROC-044-02
bundle_id: FU-5
---
# Goal: SCRIBBLE-SPLIT — Refactor ui-create-scribble Per the Mechanism

## Objective

Validate the contract mechanism by applying it to a real refactor. Split the current `ui-create-scribble` (285 lines, 5 phases, 3+ spawned agents) into:

- 1 thin orchestrator: `ui-scribble-iterate`
- 3 sub-skills: `ui-scribble-auto-review`, `ui-scribble-feedback-classify`, `ui-scribble-approve-handoff`
- 6 agents: `ui-scribble-generator`, `ui-scribble-rule-reviewer`, `ui-scribble-heuristics-reviewer`, `ui-scribble-persona-walker`, `ui-scribble-feedback-classifier`, `ui-scribble-handoff-emitter`

This shape was derived in the exploration via the 4-signal sub-skill-vs-agent rubric (see `05_round_3_synthesis.md` §D-1 and `09_amendments.md` §A-2 for naming).

## Background

Naming rationale (per `09_amendments.md` §A-2):
- All agents use `ui-` prefix for family alignment with the skills they belong to
- "auto" dropped (every agent is auto)
- "UX protocol" → "heuristics" (matches the actual corpus: Nielsen, Universal Design, Saffer, dark patterns)
- "persona-embodiment-reviewer" → "ui-scribble-persona-walker" (scribble-scoped per YAGNI; if Wave 2 surfaces a flutter-implementation need, add sibling `ui-flutter-persona-walker`)

Skill-vs-agent rubric scores (applied in the exploration):
- ui-scribble-generator (was sub-skill `ui-scribble-generate`): 1/4 → agent, not sub-skill
- ui-scribble-auto-review: 3/4 → sub-skill (fan-out to 3 reviewer agents + natural review point)
- ui-scribble-feedback-classify: 3/4 → sub-skill (multi-agent classification + natural decision point)
- ui-scribble-approve-handoff: 2/4 → sub-skill (borderline; handoff IS the contract artifact)

## How to Approach This

1. Read `05_round_3_synthesis.md` §D-1 §3.3 + `09_amendments.md` §A-2 + the prototype `prototypes/contract_ui-create-scribble.yaml`.
2. Use `claude-create-skill` to create the 3 new sub-skills (ui-scribble-auto-review, ui-scribble-feedback-classify, ui-scribble-approve-handoff). Each gets a `contract.yaml` per the Wave-1-established format.
3. Use `claude-modify-skill` to convert the existing `ui-create-scribble` into `ui-scribble-iterate` (thin orchestrator). Update its `contract.yaml` to declare it as the orchestrator + name the 3 sub-skills in `may_invoke:` + the 6 agents in a new `may_spawn:` section (or factor into may_invoke if agents are tracked there).
4. Create the 6 agents using `claude-create-agent` skill (if it exists — if not, create them manually following the agent file convention in `.claude/agents/`). Use the `claude-modify-agent` skill (if it exists from NEW-SKILL bundle) to refine.
5. Re-apply the rubric to the FINAL configuration; document scores in `plans_and_protocols/`; if the production shape differs from the exploration's prediction (e.g. `ui-scribble-approve-handoff` ends up clearly 1/4 once concrete), propose refinement via revision_target.yaml to FU-6.
6. Update consumer skills (ui-verify-flutter, ui-improve-flutter, code-simple, code-complex) to reference the new producer names. Each gets a one-line edit pointing at `ui-scribble-iterate` (or the appropriate sub-skill) instead of `ui-create-scribble`.
7. Verify with the lint (productionized in FU-1): cross-references between the new sub-skills + agents + consumers should all resolve cleanly.

## Acceptance Criteria

- [x] 4 new SKILL.md files exist (ui-scribble-iterate, ui-scribble-auto-review, ui-scribble-feedback-classify, ui-scribble-approve-handoff)
- [x] 6 agent definition files exist (or 6 agent prompts inline in the sub-skills if `.claude/agents/` is not the convention) with the names listed above
- [x] Each new SKILL.md has a contract.yaml passing the FU-1 lint
- [x] Old `ui-create-scribble/SKILL.md` is renamed to `ui-scribble-iterate/SKILL.md` (or equivalent migration) — no orphan
- [x] 4 consumer skills updated to reference new names
- [x] Lint passes on full producer-consumer graph
- [x] Rubric scores documented in `plans_and_protocols/` per final skill; any refinement proposal logged
- [x] One end-to-end smoke test: invoke `ui-scribble-iterate` on a tiny test requirement; verify each phase fires the right sub-skill / agent

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| TASK-PROC-044-05 (Wave 3) | pending | Contract mechanism fully migrated first |

## Notes

This task is in `flutter_app/.claude/task_ordering_priority_override.txt`. Completion of this task unblocks the 0.0.1 release implementation chain.

Reconciliation note: this task SUPERSEDES the SCRIBBLE-SPLIT bundle from TASK-PROC-032-10's file 09 §11 (which proposed 4 sub-skills; we revised to 3 sub-skills + 1 agent based on rubric). TASK-PROC-032-10 iteration-6 will note this supersession.
