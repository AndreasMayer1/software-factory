---
id: REQ-PROC-004
status: active
urgency: 3
urgency_reason: U3-QUALITY
impact: 4
impact_reason: I4-QUAL
effort: M
stakeholder: developer
created: 2025-10-09
updated: 2026-05-28
after: []
blocks:
  - REQ-PROC-008  # Orchestrator workflow depends on this (symmetric)
market_research_refs: [] # No relevant findings — internal process tooling, not app-domain
target_package: unassigned  # internal process requirement; no versioned package applies
trackable_items:
  acceptance_criteria:
    - id: AC-01
      target_package: unassigned
      text: "A five-phase structured ideation process (information gathering, analysis, ideation, synthesis, report) is documented as a standalone invocable workflow applicable regardless of calling context"
    - id: AC-02
      target_package: unassigned
      text: "The ideation phase produces a dedicated report document listing all generated ideas including unconventional and impractical ones, with no ideas withheld from the user"
    - id: AC-03
      target_package: unassigned
      text: "A user participation gate between ideation and synthesis is specified: synthesis does not begin until the user has reviewed the ideation report and provided an explicit approval signal"
    - id: AC-04
      target_package: unassigned
      text: "The workflow defines at least five cross-domain and associative thinking techniques mandated for the ideation phase"
    - id: AC-05
      target_package: unassigned
      text: "An effort calibration mechanism with at least three levels (Quick, Standard, Deep) and selection heuristics is specified"
    - id: AC-06
      target_package: unassigned
      text: "The workflow specifies a file-watch pause mechanism enabling agent-based execution to pause for user feedback and resume without full context reload"
    - id: AC-07
      target_package: unassigned
      text: "The workflow specifies how to elicit creative divergent output given Claude Code's lack of direct temperature control, including the recommended API parameter and its prompt-based workaround"
---

# Structured Ideation Workflow

## Overview

A five-phase creative exploration process for the Software Factory. Generic and reusable — invocable from any skill, agent, or task regardless of domain or calling context. Inspired by design thinking's double-diamond model (diverge → converge → diverge → converge) but generalized beyond UX problems. Any exploration task, architectural decision, skill design problem, or user flow creation can use it.

## Purpose

Exploration tasks and ad-hoc problem-solving in the factory currently converge too quickly: the default behavior is one gathering pass followed by the first plausible solution. This misses ideas that only emerge through sustained divergent thinking — especially cross-domain ideas the model has the knowledge to produce but does not generate under convergence pressure.

The user is currently excluded from the ideation phase. They see only the final proposal, not the creative space that produced it. This prevents contributions that most often improve outcomes: user ideas that combine with the model's ideas in ways neither would reach alone. Wild ideas the model produces but discards internally may be exactly what the user wanted to see and build on.

This requirement also addresses effort mismatch: all explorations currently receive the same depth of treatment regardless of whether the problem warrants it, making simple decisions expensive and complex ones shallow.

The trigger was a direct developer observation (2026-05-28) that the factory's exploration mode produces adequate but not creative outputs, and the desire to give the developer a window into — and a voice in — the divergent thinking phase.

## Phases

### Phase 1: Information Gathering

Collect all relevant context before beginning analysis or ideation. The caller defines what "relevant context" means for the specific invocation; the workflow does not prescribe sources.

Typical sources: goal documents, parent requirements, related requirements, `doc/` guidelines, existing code, user flows, market research findings, prior exploration outputs, web research.

**Output**: `plans_and_protocols/[date]_NN_context_summary.md` — explicitly states what is known and what is unknown. Unknown items are inputs to Phase 2 scope definition and Phase 3 ideation.

### Phase 2: Analysis

Synthesize gathered context into a precise problem framing. Define:

- **Scope**: what is in and out of scope for this ideation
- **Goal**: what does a successful outcome look like, stated as observable properties of the result
- **Constraints**: what cannot change
- **Tensions**: what competing goals or trade-offs must the ideation navigate
- **Key unknowns**: what must this exploration resolve (not answer, but clarify enough to decide)

**Output**: `plans_and_protocols/[date]_NN_analysis.md`

### Phase 3: Ideation

Open-ended creative exploration. This phase is explicitly divergent — the goal is a large, diverse set of ideas including unconventional and seemingly impractical ones. Ideas that are not immediately applicable often inspire combinations with other ideas that are. Ideas at the edge of feasibility define where the space could go and frequently contain smaller, immediately usable sub-ideas.

**Mandatory techniques** (apply all in every ideation pass):

**1. Cross-domain mapping**
For the problem at hand, ask *"What would this look like in [domain]?"* Apply at least three unrelated domains per pass (e.g. biology, architecture, games, logistics, music, supply chains, civil engineering). Extract mechanisms and principles; do not require a direct mapping — analogical distance is where the value is.

**2. Association chains**
Start with a core element of the problem. Follow each association three to five levels deep without evaluating usefulness. Write down everything the chain produces. Useful ideas often emerge at level four or five; cutting the chain at level two produces only the obvious.

**3. Inversion**
"What would make this fail spectacularly?" List failure modes without restraint. Then invert each: the inverse of a failure mode is a design principle. Some of the best constraints come from this technique.

**4. Analogical reasoning**
Find a structurally similar problem in another domain that is already solved. How was it solved? What can be adapted? The similarity does not need to be superficial — look for shared structure (same constraints, same trade-offs, same flow) even when the surface looks nothing alike.

**5. SCAMPER pass**
For each existing solution, component, or pattern in scope: Substitute, Combine, Adapt, Modify/Magnify, Put to other uses, Eliminate, Rearrange/Reverse. Generate at least one idea from each operation.

**6. Random stimulus**
Introduce a random word, object, or concept entirely unrelated to the problem. Find three or more connections between it and the problem space. Connections do not need to be direct — remote connections are more valuable than obvious ones.

**7. Feasibility spectrum**
For each major direction, generate ideas at three levels: (a) incrementally doable now, (b) possible with significant effort, (c) would require a breakthrough or external change. Level-(c) ideas are not wastes — they define the direction of the space and often hide level-(a) ideas inside them.

**Self-censorship is forbidden during ideation.** No idea is too unusual, too expensive, or too speculative to include in the ideation report. Filtering happens in synthesis, not here.

**Output**: `plans_and_protocols/[date]_NN_ideation_report.md` — all ideas, categorized by approach type and feasibility level, with a brief rationale for each.

### User Participation Gate (between Phase 3 and Phase 4)

After the ideation report is written, the workflow pauses for user input before synthesis begins. This gate is mandatory at all effort levels including Quick.

**File-watch pause mechanism**:
1. Agent writes the ideation report to `plans_and_protocols/[date]_NN_ideation_report.md`
2. Agent writes `plans_and_protocols/awaiting_user_review.md` containing:
   - A brief highlight of the most interesting and most unusual ideas from the report
   - An explicit invitation for the user to add their own ideas by appending to this file or to the ideation report
   - Clear instructions: append `APPROVED` to advance to synthesis; append `ITERATE: [feedback]` to request another ideation pass with that feedback incorporated
3. Agent monitors `awaiting_user_review.md` for either signal

On `APPROVED`: proceed to Phase 4 Synthesis. The agent reads the complete ideation report (including any user additions) as synthesis input.

On `ITERATE: [feedback]`: perform another ideation pass incorporating the feedback and any new ideas the user added. Then rewrite `awaiting_user_review.md` with the updated report summary and repeat the gate.

User additions to the ideation report are treated as equal-status ideas in synthesis — not as overrides or preferences. The synthesis phase evaluates all ideas on the same criteria.

This mechanism enables asynchronous user participation without requiring a synchronous chat message and without the context-reload cost of re-spawning a fresh agent.

### Phase 4: Synthesis

Evaluate all ideas from Phase 3 (including user additions). Apply the following operations in order:

1. **Cluster**: Group ideas by underlying mechanism or approach type
2. **Evaluate**: For each cluster, assess feasibility, impact, and fit with the constraints from Analysis
3. **Merge**: Combine compatible ideas from different clusters into hybrid approaches
4. **Rate**: Score each approach on three dimensions (feasibility, impact, fit) using a 1–3 scale
5. **Prioritize**: Rank approaches by combined score; document the top three to five

The synthesis document must explain WHY the top-ranked approaches score higher — not just that they do. Discarded approaches must include a brief reason (so the user can see what was considered and why it was set aside).

**Output**: `plans_and_protocols/[date]_NN_synthesis.md`

### Phase 5: Final Report

A human-readable report summarizing the full exploration for the user:
- Problem framing (condensed from Analysis)
- Ideation highlights: the most interesting ideas, and at least the single most unusual one
- Recommended approach(es) with rationale
- Discarded approaches and why
- Open questions the exploration did not resolve
- Suggested next steps (implementation task, deeper exploration task, decision needed by user)

**Output**: `plans_and_protocols/[date]_NN_final_report.md`

## Effort Calibration

The depth of each phase scales with the declared effort level. The caller (skill, agent, or user) declares the effort level before Phase 1 begins, using the heuristics below.

### Levels

| Level | Ideation passes | Min ideas | Web research | Synthesis rounds | User gate iterations |
|-------|----------------|-----------|--------------|-----------------|---------------------|
| **Quick** | 1 | 10 | No | 1 | 1 (approve or single iterate) |
| **Standard** | 2 | 25 | Optional | 2 | Up to 2 |
| **Deep** | 3+ | 50+ | Yes | 3+ | Unlimited |

### Selection Heuristics

Use **Quick** when ALL hold:
- Fewer than three significant unknowns
- Scope is contained within a single system layer or skill
- A decision is needed quickly and a good-enough answer is acceptable
- The caller has strong prior knowledge of the domain

Use **Deep** when ANY holds:
- The problem spans two or more architectural layers, epics, or factory skills
- The decision has high reversal cost (architectural, cross-cutting, or user-facing once implemented)
- The problem is genuinely novel with no prior art in the codebase
- The user explicitly requests deep exploration

Use **Standard** in all other cases.

If no effort level is declared by the caller, default to **Standard**.

## Creative Output and Temperature

The Claude API supports a `temperature` parameter (0–1) that controls output randomness. Higher values (0.8–1.0) measurably increase ideation diversity and reduce repetitive convergence on obvious solutions. Temperature 0 produces deterministic, identical outputs unsuitable for brainstorming.

**Constraint**: Claude Code CLI does not expose temperature as a command-line parameter. The temperature is set by the Claude Code harness and is not configurable per-session or per-phase.

**Mitigation**: Ideation-phase prompts must include explicit creativity-eliciting instructions that counteract the model's default convergence tendency. Any skill or agent implementing this workflow must include the following language (verbatim or equivalently strong) in the prompt for the ideation phase:

> *For this ideation phase: prioritize diversity over quality. Generate ideas across the full feasibility spectrum. Do not self-censor — include ideas that seem impractical, expensive, or unusual. Filtering happens in synthesis, not here. Apply cross-domain thinking actively: look for applicable mechanisms in unrelated fields. Follow association chains. Introduce surprising connections. The most valuable ideas are often the ones that seem wrong at first.*

Skills that later gain the ability to call the Claude API directly with configurable parameters may remove this language and set `temperature: 0.9` instead.

## Developer Guidelines

### Key Decisions

- The user participation gate is mandatory at all effort levels including Quick. Even a single-pass ideation produces a report the user should see. The effort level controls how many passes happen, not whether the gate exists.
- The file-watch pause mechanism uses plain files in `plans_and_protocols/` — not chat messages, tool calls, or external services. This requires no infrastructure, works in any agent context, and survives context reloads.
- SCAMPER and cross-domain mapping are mandatory (not optional techniques) because they are the methods most likely to surface ideas the model would not generate under convergence pressure.
- Temperature is documented as a limitation with a mitigation, not a solved problem. If Claude Code adds temperature control, the prompt-language requirement may be relaxed; the rest of the workflow remains.
- Self-censorship is explicitly named and forbidden in the ideation phase because the default model behavior is to suppress unusual ideas before writing them. The prohibition must appear in the prompt, not just in this requirement.

### Common Pitfalls

- Filtering ideas during ideation (wrong end state: a small set of reasonable ideas; correct end state: a large diverse set including unusual ones with no filtering applied until synthesis)
- Skipping the user gate because the exploration already feels well-understood (the gate exists precisely for cases where the exploration surprises its author)
- Merging ideation with analysis in the same pass (the phases are deliberately separate to prevent premature convergence)
- Using identical prompting for all phases (ideation requires creativity-eliciting language; analysis and synthesis require convergent, evaluative language — mixing them produces neither well)
- Treating user additions as directional preferences rather than equal-status ideas (the user's ideas enter synthesis on equal footing and must be evaluated against the same criteria)

## Related Requirements

- REQ-PROC-008: Orchestrator Workflow — the orchestrator and its skills are the primary callers; complex planning decisions qualify for this workflow
- REQ-PROC-059: Cross-Factory LLM Work Principles — principle (g) (sub-agent context isolation) applies to agents implementing this workflow; ideation agents should run isolated and return a distilled summary

## References

- Original developer request: `tasks/2026-05-28_explore_implement-ideation-workflow/plans_and_protocols/2026-05-28_00_user_initial_input.md`
- Web research summary: LLM-based multi-agent design thinking (Springer 2025); AI ideation with LLMs (arXiv:2512.00010); temperature and creativity (carilu.com, anablock.com)
- Double diamond model: https://www.designcouncil.org.uk/our-resources/the-double-diamond/
