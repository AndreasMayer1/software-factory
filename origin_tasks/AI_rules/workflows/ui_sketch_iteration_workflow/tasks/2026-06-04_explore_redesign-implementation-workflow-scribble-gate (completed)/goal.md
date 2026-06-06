---
task_id: TASK-PROC-032-29
type: explore
parent_requirement: REQ-PROC-032
urgency: 4
urgency_reason: U4-BLOCKING
impact: 5
impact_reason: I5-ENAB
status: completed
started: 2026-06-04
completed: 2026-06-05
session_completed_at: 2026-06-04T14:10:05Z
effort: XL
created: 2026-06-04
expected_tool_calls: 70
skill_chain_depth: 4
synthesis_dependent: true
synthesis_justification: "Must hold the whole top-down skill chain (requ-derive-from-flow → task-derive-from-requ → release-begin-impl/-finalize → scribble skills → coding tasks) and six coupled sub-problems (P-A..P-F) simultaneously to design a coherent skill topology and task-lifecycle; splitting would lose the cross-skill synthesis that is the point."
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: []
  sections: []
scope_description: "Re-think the end-to-end implementation workflow (all participating skills) so the scribble layer becomes a hard gate between requirement-derivation and coding-task creation; design the skill topology, task-lifecycle, loopback/cascade handling, and session/token cut points."
release_description: ""
opus_recommended: true   # reason: explicit decision/architecture task — cross-skill synthesis across the whole workflow chain; trade-offs (session boundaries, loopback ordering, cascade resolution) must be reasoned with all context held at once
writes_requirements: false
requirements_version:
  commit: d29b49c9
  file: ../requirements.md
session_id: eb2dae87-6afe-4175-b584-d87e047302f4
session_account: web
---
# Goal: Redesign the End-to-End Implementation Workflow Around a Scribble Gate

## Objective

Today coding/implementation tasks are created up front (in `release-begin-impl` Phase 2c, via
`task-derive-from-requ`) — *before* any scribble exists or is approved. The developer wants the opposite: the
**scribble layer must be a hard gate** between requirement-derivation and coding-task creation. Reviewing the
UI may reveal changes at the requirement or even the user-flow level; if coding tasks already exist they are
invalidated.

The unknowns this exploration must enter:
- **Where do the cuts go?** How should the monolithic "Begin Implementation" be decomposed (2 skills? 3?) so
  that no single skill carries all the complexity, the scribble gate sits between phases, and the *names*
  convey call-order and relationships?
- **How are loopbacks modeled?** When the scribble gate sends work back (flow re-adjust, requirement edit,
  "entry missing in another requirement"), are *new* tasks created or are existing un-approved scribbles
  updated in place? Which skill owns each loopback?
- **How is consistency maintained over time?** A requirement edited mid-release leaves its scribble stale
  (the discrepancy window). Other readers of requirements (notably coding tasks) depend on correct scribbles.
  What governs that window — transparency flags, blocking `after` edges, something else?
- **How does a UI cascade across requirement boundaries resolve?** A dashboard change can force scribble-level
  (not requirement-level) changes in unrelated features whose entry points moved — possibly multi-step.
- **What is the token/session shape?** The whole chain must minimise total tokens (read information twice as
  rarely as possible) while keeping each session holding only what it needs — forcing session boundaries via
  agents or new tasks. Where exactly?

This is NOT a request to patch the scribble skills. The developer's explicit instruction: *do not press the new
functions into the existing workflow — completely rethink the complete workflow, all skills involved.*

The output is a **design**, not an implementation. Skill/agent usage during the exploration is left open
(the developer framed this as an exploration).

## Background

REQ-PROC-032 (the scribble / UI-sketch iteration workflow) was substantially rebuilt and then put through a
live pilot (TASK-FUNC-007-01-05) and evaluated in TASK-PROC-032-28. That evaluation produced two synthesis
rounds whose proposals (PROP-1…PROP-14, PROP-R1/R2) are the technical substrate for this redesign. Round 2
surfaced that the needed changes are not scribble-skill-local — they span the whole top-down chain
(`requ-derive-from-flow` → `task-derive-from-requ` → `release-begin-impl` / `release-begin-impl-finalize` →
scribble skills → coding tasks) — and the developer mandated a full rethink.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-06-04_00_user_initial_input.md`

Read it as a seed bed, not a spec.

**Primary substrate (read first)** — the evaluation task's two synthesis records (self-contained, no session
replay needed):
- `../2026-06-04_explore_eval-scribble-workflow-live-iteration/plans_and_protocols/2026-06-04_04_round_2_evaluation.md`
  — §4 is the problem statement (P-A…P-F); §1 is the comment-nesting render-leak finding folded into this task;
  §2 records developer-resolved design inputs (task-start wraps claude-route; sequential reviewers; gate-on-
  convergence default; container-dimension visibility); §3 is PROP-14 (script-driven flow sidebar).
- `../2026-06-04_explore_eval-scribble-workflow-live-iteration/plans_and_protocols/2026-06-04_02_round_1_evaluation.md`
  — PROP-8/9/10/11/12 (entry-context spine, coverage/ordering/basis, staleness, integrity) and PROP-R1/R2.

For complete requirements at task creation time:
```
git show d29b49c9:requirements_tasks/process/AI_rules/workflows/ui_sketch_iteration_workflow/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking — empathize with the current pipeline before redrawing it, diverge before converging, let
the cut-point questions lead, iterate. A single pass will not be enough. Surface surprises: the most valuable
discoveries will be coupling between sub-problems that the framing did not anticipate (P-A…P-F are stated as
six but are deeply entangled — e.g. the scribble hard-gate of P-A is in direct tension with mid-release
requirement edits of P-E).

Ground every design choice in what the current skills actually do — read the participating SKILL.md files
before proposing how to split them. Do not design in the abstract.

## Seeds

1. **The hard gate vs. mid-release edits tension.** P-A says coding tasks may not exist until scribbles are
   approved; P-E says requirements (hence scribbles) get edited *during* implementation. These cannot both be
   absolute. Where is the reconciling mechanism — and is the "gate" really a gate or a continuously-enforced
   invariant?

2. **The decomposition of "Begin Implementation."** Read `release-begin-impl` and `release-begin-impl-finalize`
   end to end. What are the natural seams? Is the scribble layer a third skill between them, or a re-shaping of
   Phase 2c? What naming makes the call-order self-evident (cf. `task-create → task-start → … → task-complete`)?

3. **Loopback taxonomy.** Enumerate every point where the workflow sends work backwards (flow re-adjust at the
   scribble gate; requirement edit; "entry missing in another requirement" per PROP-8; auto-review non-
   convergence per PROP-13B; cross-requirement cascade per P-F). For each: what triggers it, who owns it, does
   it create a task or stay in-session, and how does it avoid infinite loops?

4. **The discrepancy-window governance model (P-E).** When a requirement edit auto-creates a scribble-
   adjustment task, what stops a stale scribble from being consumed in the interim? Map the full set of
   requirement-readers that depend on scribble currency; decide transparency-flag vs. blocking-`after`-edge per
   reader.

5. **Cross-requirement UI cascade (P-F).** The dashboard example: a requirement change that is requirement-
   neutral for dependents but scribble-breaking for them. What dependency model detects this (shared flow /
   shared entry surface, not shared requirement)? How are multi-step cascades ordered without a global graph
   that itself rots (PROP-10)?

6. **Session/token cut points (P-D).** For the redrawn chain, which work belongs in the orchestrator context,
   which in spawned agents, which in fresh tasks? Re-validate the Round-1 changes proposed to
   `requ-derive-from-flow` (PROP-11 R4 / F13–F14) under the redesign — do they still make sense, or is a
   different split better?

7. **Carry the resolved design inputs (Round-2 §2).** `task-start` wraps `claude-route`; reviewers run
   sequentially not in parallel; the default gate cadence is "gate only on auto-review convergence"; container
   entry-context must include size/dimension. These are settled — fold them in rather than re-deciding them.

8. **The comment-nesting render-leak (Round-2 §1, folded in).** The generator nests `<!-- … -->` comments,
   which leak reviewer text into the rendered page (HTML comments can't nest). The redesign of how reviewer
   detail is carried in the artifact (PROP-1 human-facing review layer) must also fix this concrete defect —
   they share a locus.

## Execution Model

Gather raw material — read the participating SKILL.md files and the two substrate synthesis records — then
synthesize iteratively. Expect several gathering rounds before the skill topology stabilizes. The exploration
may legitimately conclude that the redesign should itself be split into staged design sub-tasks; if so, say so
and propose the staging.

The session's model is fixed at launch (Opus — `opus_recommended: true`). No mid-session model switching.

**Web research**: if a seed needs external prior art (e.g. how other pipeline/agent systems gate design before
implementation, or model staged-approval workflows), delegate to a spawned `general-purpose` agent with a
focused question framed as a question; never run WebSearch inline.

This task is a heavy synthesis (expected_tool_calls ~70, skill_chain_depth 4). If executed by a spawned agent
it MUST run with `run_in_background: true` and a heartbeat (CLAUDE.md long-running-agent cache rule).

## Output

A future implementer (or a set of impl tasks) must be able to read the output and execute the redesign without
replaying this session. "Done" looks like:
- A proposed **skill topology** for the implementation workflow: which skills exist, what each owns, their
  call-order, and the names that make the order self-evident — with the scribble layer as the gate.
- A **task-lifecycle model**: when scribble tasks are created, when coding tasks are created, how loopbacks
  create/refresh tasks, and the `after`/blocking edges that enforce ordering.
- A **consistency model** for the discrepancy window (P-E) and the cross-requirement cascade (P-F), naming the
  detector and recovery for each rot path.
- A **session/token map**: the cut points (orchestrator vs agent vs new task) across the chain.
- A clear statement of which existing skills change and how, anchored to REQ-PROC-032 ACs (and flagging where
  new ACs / `requ-explore` are needed), so the redesign can be decomposed into impl tasks.
- Honest identification of the unresolved tensions (especially Seed 1) and the decisions that still need the
  developer.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round — files 02 + 04–16
- [x] The synthesis defines the problem space in terms that were not fully known at task creation (e.g. names
      the actual reconciling mechanism for the hard-gate-vs-mid-release-edit tension, not just "there is a
      tension") — SCI invariant, the 5-edge staleness rot-graph, AC facet-tagging, lazy-wavefront cascade + two-stage width-breaker (file 11)
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide — file 10 §4 + file 11 §E
- [x] The output is honest about what remains uncertain — file 11 §D (narrowed) + file 12 (contingency branches + abort line)
- [x] The user has approved the final synthesis and stated what to do next — developer ratified fixture-first + web fixture; approved the plan; directed task creation
- [x] The action stated by the user as the next step was performed successfully — created TASK-PROC-066-03, TASK-PROC-035-21, TASK-PROC-035-22, TASK-PROC-032-30/31/32/33, TASK-PROC-066-04 and registered them in `.claude/task_ordering_priority_override.txt`

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| — | — | No blocking dependencies. The evaluation task TASK-PROC-032-28 is the source of the substrate but does not block (its synthesis records are already written and self-contained). |

## Related Tasks

| Task | Reason |
|------|--------|
| [TASK-PROC-032-28](../2026-06-04_explore_eval-scribble-workflow-live-iteration/goal.md) | Predecessor/extension — its Round-1 & Round-2 synthesis records are the problem statement (§4 P-A…P-F) and technical substrate (PROP-1…14) for this redesign; read them first. |
