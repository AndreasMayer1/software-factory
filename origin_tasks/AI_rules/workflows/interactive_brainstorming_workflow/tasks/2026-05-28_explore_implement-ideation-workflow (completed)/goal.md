---
task_id: TASK-PROC-004-02
type: explore
parent_requirement: REQ-PROC-004
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
status: completed
effort: L
created: 2026-05-28
started: 2026-06-05
completed: 2026-06-05
session_completed_at: 2026-06-05T21:35:37Z
after: []
awaiting: []
awaiting_note: ""
covers:
  acceptance_criteria: [AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07]
  sections: []
scope_description: "Explore concrete implementation of the structured ideation workflow as defined in REQ-PROC-004 — skill vs agent design, file-watch pause mechanism, ideation prompts, effort calibration, multi-run iteration until gap-closure (breadth + depth) under finite per-run thinking/output budgets, and integration with existing factory skills"
release_description: ""
opus_recommended: true   # reason: cross-cutting explore — spans multiple architectural layers (skills, agents, task execution model, prompt engineering); novel problem with genuine trade-off analysis needed
writes_requirements: false
requirements_version:
  commit: ""  # requirements.md not yet committed at task creation time
  file: ../requirements.md
session_id: 1dab745b-ec08-4988-90f9-48d0a9469d44
session_account: gmail
---
# Goal: Implement Structured Ideation Workflow as Factory Mechanism

## Objective

REQ-PROC-067 defines WHAT the structured ideation workflow must achieve. This exploration answers the HOW: what concrete factory mechanism implements it, how the user participation gate works in practice, how effort calibration is operationalized, and how existing skills (task-create, requ-explore, code-complex, ux-create-flow, etc.) invoke it.

What is not yet known: whether a dedicated skill, a reusable agent template, a modified explore task protocol, or a combination is the right implementation vehicle; how the file-watch pause works without polling overhead; whether the ideation phase is better served by a separate agent invocation (context isolation) or inline execution (context continuity); and how the brainstorming techniques in the requirement translate into concrete prompt language that reliably produces divergent output.

Also not yet known — and added to this task on 2026-06-05: how the workflow guarantees a *complete* result when a single LLM request cannot produce one. The binding constraint here is **not** the session context window and **not** the cost of re-loading context — it is the **amount of output a model can produce in a single request**: each response has a finite output budget (and a finite per-request thinking budget). A large research question's full answer simply does not fit in one response, so the model is forced to wrap up and converge to a synthesis that still carries open questions and under-explored areas — even though it still holds all the relevant context. The workflow therefore cannot assume "one request = one finished synthesis." It must support **multiple follow-up iterations** (additional requests/runs) that each continue producing output where the previous one left off, progressively closing gaps in both **breadth** (sub-questions never opened) and **depth** (sub-questions opened but answered shallowly), with a **gap-driven terminal condition** — "iterate until no gaps remain" — rather than a fixed pass count. This raises its own design questions: how the unfinished work is tracked and handed to the next request, how gaps are detected and represented, how the loop avoids non-termination and diminishing returns, and who certifies "no gaps remain" (the model, the user gate, or both).

## Background

The factory's exploration tasks currently converge too quickly. The `requ-explore` skill, the `code-complex` skill, and the `task-create` explore template all have a single-pass information-gathering phase that leads directly to synthesis. There is no structured divergent phase and no mechanism for the user to see and contribute to the ideation before the model converges.

REQ-PROC-067 was written in session 2026-05-28 in response to a developer observation that the factory produces adequate but not creative exploration outputs. The requirement specifies a five-phase process (gather → analyze → ideate → [user gate] → synthesize → report) with user participation, effort calibration, file-watch pause, and explicit brainstorming techniques.

A second developer observation (2026-06-05, verbatim in `plans_and_protocols/2026-06-05_01_user_followup_input.md`) added a related but distinct failure mode: even when the process runs, the synthesis document it produces frequently still contains open questions. The diagnosis is that the research question is sometimes simply too large to answer in one model run — each run is capped by a maximum thinking budget and a maximum output budget, so the model is forced to converge before the space is fully covered. The fix is not "think harder in one pass" (the budget makes that impossible) but a loop: spawn follow-up iterations that continue covering the space until no gaps remain in breadth or depth. This makes completeness an explicit, tracked property of the workflow rather than an implicit hope. Note this concern is orthogonal to ideation quality — a perfectly divergent ideation phase can still feed an incomplete synthesis — so the implementation must address both.

The user's unedited initial thinking that prompted this task is preserved in:
`plans_and_protocols/2026-05-28_00_user_initial_input.md`

Read it as a seed bed, not a spec.

For complete requirements at task creation time:
```
git show HEAD:requirements_tasks/process/AI_rules/workflows/structured_ideation_process/requirements.md
```

Current requirements: ../requirements.md

## How to Approach This

Use design thinking as the guiding process — empathize before defining, diverge before converging, let questions lead, iterate. A single pass through the material will not be enough. Surface surprises — the most valuable discoveries are the ones that were not anticipated.

The key tension: context continuity (inline in calling session) vs. context isolation (separate agent). Both have real costs. The file-watch pause mechanism the user proposed suggests they have already thought about the agent approach and its context-reload cost — honor this by treating it seriously rather than dismissing it.

Existing prior art to read before ideating: `requirements_tasks/process/AI_rules/workflows/interactive_brainstorming_workflow/requirements.md` (REQ-PROC-004, the predecessor). Also: `requirements_tasks/process/AI_rules/llm_work_principles/requirements.md` (REQ-PROC-059, especially principle g on sub-agent context isolation).

## Seeds

1. **Skill vs. agent vs. protocol — what is the right vehicle?** A skill is loaded as context into the calling session (token cost, context continuity). An agent starts cold (token-free context, but context-reload cost on each iteration). A protocol embedded in existing explore task templates adds no new skill but has no enforcement mechanism. Which trade-off does this factory prefer — and does the answer depend on effort level?

2. **The file-watch pause in practice.** The user proposed an agent that monitors a file for approval. In Claude Code, the mechanism for watching a file and resuming is the `Monitor` tool + a loop, or an agent that polls. What does a concrete, low-overhead implementation look like? Does it block the main session? What happens if the user never responds — does the agent time out? How does the resumed agent re-acquire context without a full reload?

3. **Temperature control in Claude Code.** The API supports temperature; the CLI does not expose it. Is there any configuration path (model settings, API override, custom wrapper) that would allow setting temperature per-phase in Claude Code? If not, what is the maximum creative divergence achievable through prompt engineering alone — and is there evidence that specific prompt patterns reliably produce more novel software-domain ideas?

4. **Brainstorming techniques for software problems specifically.** The requirement specifies seven techniques (cross-domain mapping, association chains, inversion, analogical reasoning, SCAMPER, random stimulus, feasibility spectrum). Are these the right seven? Are there software-domain-specific adaptations that produce better results? What do practitioner reports and research say about which techniques surface the most novel architectural ideas vs. which are more useful for UX problems?

5. **The gap between current explorations and this workflow's ideal output.** Pick two or three completed exploration tasks from the task history and trace them through REQ-PROC-067's five phases. Where would the current output diverge most from the ideal? Would the user participation gate have changed the outcome in any of them? Use this as a test against over-engineering — if the gap is small, the implementation should be minimal.

6. **Integration surface with existing skills.** Which existing skills should invoke this workflow, and how? `requ-explore` phases 1–3 already resemble information gathering + analysis; can the ideation phase be inserted without rewriting the skill? `code-complex` has a planning phase that might benefit from ideation for architectural decisions. Does the workflow need a dedicated `ideation` skill, or is it better expressed as a modular protocol section that skills can opt into?

7. **Budget-bounded completeness — iterating until no gaps remain.** The binding constraint is the **per-request output budget** (plus the per-request thinking budget): a single response can only emit so much, so for a large enough research question the full answer does not fit and the model converges to a synthesis that still has open questions — *not* because it ran out of context or lost track of the material, but because it ran out of room to write it all down in one request. (Distinguish sharply from Seeds 1/2, which are about input-context cost; this is about output-production capacity.) The workflow must therefore be able to run again — follow-up requests/iterations that continue producing output where the last left off and progressively close gaps until a gap-driven terminal condition is met ("until no gaps exist anymore"), not a fixed number of passes. Open questions to resolve:
   - **Gap representation.** What is the artifact that carries the unfinished work between iterations so the next request knows exactly where to continue? A "gap ledger" / open-questions register that each iteration reads, advances, and rewrites is the obvious candidate — what is its schema? It likely needs to distinguish **breadth gaps** (sub-questions identified but never explored) from **depth gaps** (explored but shallow / unresolved / contingent on a decision), because they call for different next moves.
   - **Gap detection.** How does an iteration decide what is still missing — model self-assessment at end of pass, an explicit "what did I not get to?" prompt step, a separate reviewer/critic agent that audits the synthesis for holes, or coverage checked against the analyze-phase scope map? How reliable is LLM self-assessment of its own completeness, and does an adversarial critic pass materially improve it?
   - **Continuation vehicle (same session vs. fresh request/agent).** Because the constraint is output budget rather than context, a follow-up iteration does *not* inherently need to re-acquire context — if it continues in the same session the context is still there; the only thing it strictly needs is the gap ledger plus the prior output to know what remains. The input-context-reload cost (Seeds 1/2, REQ-PROC-059 principle g, the §"Agent Delegation Economics" / fresh-agent-per-batch pattern) becomes relevant *only* if the chosen vehicle restarts cold (e.g. a new agent per iteration) — so it is a consequence of a vehicle decision, not the root problem. Determine when each vehicle is appropriate and what the carrier must contain in each case.
   - **Termination and runaway control.** "No gaps remain" must be operationalized so the loop actually halts: who certifies it (model self-certification, the existing user gate, or a critic agent), how is diminishing-returns / gap-closure-rate detected, and what backstop bounds the loop (a max-iteration cap, effort-calibrated per Seed/effort level) to prevent non-termination or infinite churn on inherently open questions?
   - **Relationship to effort calibration and the user gate.** Effort level (Seed via REQ-PROC-067) should bound the iteration budget — XS/S may legitimately be one pass, L/XL may need several. Does the user see and approve intermediate iteration reports, or only the final gap-closed synthesis? How does this loop compose with the ideation user-participation gate without creating two competing approval points?

## Execution Model

Gather raw material — read artifacts, follow threads, surface facts and anomalies. Synthesize iteratively; multiple gathering rounds may be needed before the problem space is well understood.

The session's model is fixed at launch (Opus — `opus_recommended: true`). No mid-session model switching.

**Web research**: For seeds requiring external knowledge — best practices, prior art, tool capabilities, what others have tried — use web search. Always delegate web research to a spawned `general-purpose` agent with a focused question; never run WebSearch inline. Raw web content inflates the gathering agent's context window fast with irrelevant results; the subagent returns only a distilled summary while the raw content stays in its own context.

Frame search queries as questions rather than keyword bags — this produces more useful results. Suggested research directions:
- *"How do LLM-based brainstorming agents handle context continuity across user feedback iterations?"*
- *"What prompt patterns produce the most divergent, non-obvious ideas in LLM systems?"*
- *"Claude API temperature parameter: effect on output diversity vs. coherence in extended reasoning tasks"*
- *"SCAMPER and cross-domain analogical reasoning adapted for software architecture problems"*

## Output

The output is a synthesis document (`plans_and_protocols/[date]_NN_synthesis.md`) and a final report (`plans_and_protocols/[date]_NN_final_report.md`) that together give the next implementer:
- A clear decision on implementation vehicle (skill / agent / protocol / combination) with rationale
- A concrete design for the file-watch pause mechanism
- Draft prompt language for the ideation phase (ready to paste into a skill file)
- A concrete design for effort calibration (the heuristic logic an implementing skill would execute)
- A concrete design for the **multi-run iteration loop** that exists because a single request's output budget cannot emit the full result at once: the gap-ledger artifact (schema + how breadth vs. depth gaps are recorded), how an iteration detects remaining gaps, what the next request needs to continue producing output (and the same-session vs. cold-restart vehicle trade-off), the operational terminal condition for "no gaps remain", and the runaway backstop — including how the loop is bounded by effort level and how it composes with the user gate
- A prioritized integration plan: which existing skills to modify first, and in what order

The output should be honest about what remains uncertain and what decisions require the developer's input before implementation can begin.

## Acceptance Criteria

- [x] Exploration produced at least one synthesis round
- [x] The synthesis defines the problem space in terms that were not fully known at task creation
- [x] Decisions requiring user input are identified and framed clearly enough for the user to decide
- [x] The output is honest about what remains uncertain
- [x] The output specifies how the workflow handles a research question too large for one run: a multi-run iteration design with a gap-ledger (breadth + depth), a gap-driven terminal condition ("until no gaps remain"), and a runaway backstop

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| REQ-PROC-067 | active | Requirement document defines the WHAT; this task defines the HOW |
