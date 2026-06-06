# Session/Token Efficiency Analysis — sub-skill split + agent delegation

**Task:** TASK-PROC-032-10 · **Date:** 2026-05-29 · **Model:** Opus 4.7
**Purpose:** Per user instruction in `2026-05-29_11_feedback.md` and the real-time hint "remember to delegate to agents if a fresh session saves tokens" — analyze what information is needed at which stage of the scribble pipeline, and which session splits minimize total token consumption.

> Method: estimate per-stage information needs against current pipeline. Identify duplications. Compare against split options (one session vs many tasks vs many agents). Conclude with a recommendation that the NEW-EXPLORATION task can validate via prototype.

> Caveat: token estimates here are coarse — actual numbers depend on model, prompt-cache state, and per-stage agent behavior. Treat numbers as relative magnitudes for trade-off reasoning, not absolutes.

---

## 1. The two-axis cost model

Token cost has two axes that move in opposite directions when we split work:

- **Context-bloat cost**: a session that accumulates unrelated context pays cache misses on subsequent reads and pays full re-input cost when the cache expires. Each KB of irrelevant context in the working window is *taxed every turn*.
- **Re-loading cost**: a fresh session pays full input cost for every artifact it needs to read, because it starts cold. Each artifact read is *paid once per session start*.

**Implication**: splits help when the avoided context-bloat cost > the added re-loading cost. They hurt when the opposite is true.

Two heuristics:

1. **The 5-minute cache window** (per CLAUDE.md §Cache Protection): any pause >5 min in a session expires the prompt cache; the next message pays full input cost again. Long-running work inside one session that doesn't speak frequently to the LLM is functionally equivalent to a fresh session — without the bloat benefit.

2. **Artifact reuse density**: if a phase reads artifacts that a sibling phase also needs to read, keeping them in one session amortizes the read. If sibling phases read disjoint artifacts, splitting saves the bloat cost without paying re-read.

---

## 2. The current scribble pipeline — per-phase information needs

Sampling from `ui-create-scribble/SKILL.md` and SKETCHES_README:

| Phase | What it reads | What it writes | Approx context size |
|---|---|---|---|
| Phase 0 (multimodal seed) | `inputs/sketch.{png,jpg,pdf}`, `inputs/reference.{png,jpg}` | Vision context for Phase 1 | Small (≤5 images) |
| Phase 0.5 (proposed pre-brief, PREBRIEF bundle) | `requirements.md`, persona list, T1/T2 rules summary, parent flow.md, prior version metadata (if v(n>1)) | `pre_brief.md` (≤300 words) | M — full requirement + flow context |
| Phase 1 (generate scribble) | `requirements.md`, ALL personas in personas_applied, ALL T1/T2 rules from `doc/presentation/`, parent flow.md (full), parent flow's `implementation_notes.md` (if exists), domain class info from `lib/features/`, concept_canon.yaml, optional `inputs/inspiration.yaml`, optional Stitch/Claude-Design draft | per-screen HTML files + index.html + metadata.yaml + feedback.md | **L — heaviest read in the pipeline** |
| Phase 2 (auto-review odd→even) | Phase 1's output + the same inputs Phase 1 used + the auto-review rubric (8 checks + YAGNI gate) | Regenerated scribble v{n+1} + auto_review_report.md + (proposed) auto-review brief + inter-version diff | L — repeats most Phase 1 reads |
| Phase 2.5 (proposed persona-embodiment) | persona.md + 1 scenario per materially-affected persona + flow Domain Concepts (already in context if continuous) + the scribble | Per-persona findings | M — adds 1–N scenarios |
| Phase 2b (proposed UX-protocol reviewer) | The scribble + Nielsen/Universal-Design/Affordance/Dark-Patterns reference (could be inline in agent prompt) | UX-protocol findings | S — minimal new reads if reference baked into agent prompt |
| Phase 3 (user review) | Waits for user feedback | feedback.md (user-authored) | None LLM-side |
| Phase 4 (feedback-classify + rule-update) | feedback.md + ALL T1/T2 rules + `doc/presentation/design/` directory + impact-check artifacts | classifications.yaml + optional `requ-explore` / `doc-update-guidelines` invocations | M-L — depends on impact-check scope |
| Phase 5 (approve + handoff emit) | The approved scribble (already in context if continuous) + flow.md (for flow_navigation.yaml) + screen HTML files for handoff yaml | `flutter_handoff.yaml` (with new `contract:` + `verification_seeds:` blocks per redundancy R3) + `metadata.yaml.status=approved` + flow `scribble_index.html` regen | M |

**Observation**: Phase 1, Phase 2, and Phase 4 share the heaviest reads (T1/T2 rules, personas, flow, requirements). Phase 2.5 and Phase 2b add small extras. Phase 5 mostly re-uses already-loaded context.

---

## 3. Duplications and overlap

If the pipeline runs in a single session continuously:
- Phase 1 + Phase 2 reuse most of the same reads (~80% overlap)
- Phase 2.5 + Phase 2b are small additions to Phase 2's context
- Phase 4 may need a *different* corpus (the impact-check artifacts) but reuses T1/T2 rules

If split into separate sessions:
- Each session re-reads its full context from cold
- Phase 1 and Phase 2 effectively double the heavy read

This is the central trade-off.

---

## 4. Split candidates — where a fresh session beats reusing

### 4.1 Cuts that DO save tokens

**Cut A: Phase 4 (feedback-classify) as a separate session/agent.**

Rationale: Phase 4 fires only when the user provides feedback. By the time feedback arrives:
- The previous session's cache has likely expired (user reviewing scribble + writing feedback = >5 minutes)
- Phase 4's primary context (T1/T2 rules + impact-check) overlaps with Phase 1/2 reads but the impact-check artifacts are distinct
- Phase 4 may invoke other skills (`requ-explore`, `doc-update-guidelines`) — these are heavier than a single-phase agent's needs

**Verdict**: Phase 4 is a *natural* session boundary. The cache expiry has already happened; a fresh session pays the same cold-start cost as a re-warmed one. Splitting wins because the bloat-cost during the wait is wasted.

**Cut B: Phase 5 (approval handoff emit) as a separate brief agent.**

Rationale: Phase 5 fires only on approval. The work is mechanical (read approved scribble, emit YAMLs, update metadata). Doesn't need the full Phase 1 personas/rules corpus.

**Verdict**: Cheap fresh-agent invocation. Saves the bloat of carrying Phase 5 inside the iterating orchestrator.

**Cut C: Phase 2.5 persona-embodiment as a dedicated agent (already planned, D18).**

Rationale: The agent reads 1 scenario per affected persona + flow Domain Concepts — distinct context the auto-reviewer doesn't need. Persona-embodiment-reviewer is invoked from within the same Phase-2 boundary but with its own context window. Saves bloat in the parent.

**Verdict**: Already planned. Confirms the dedicated-agent decision.

**Cut D: Phase 2b UX-protocol reviewer as a dedicated agent (D16).**

Rationale: The agent's vocabulary corpus (Nielsen 10 + Universal Design 7 + Saffer microinteractions + dark patterns) lives in the agent prompt itself, NOT in shared context. The agent receives only the scribble + scope; produces findings. Minimal additional context.

**Verdict**: Already planned. Confirms.

### 4.2 Cuts that DON'T save tokens (resist these)

**Anti-cut E: Splitting Phase 1 generator from Phase 2 auto-reviewer into separate sessions.**

Rationale: ~80% read overlap. The auto-reviewer needs essentially the same context as the generator. A fresh-session split doubles the heavy reads.

**Verdict**: Keep Phase 1 and Phase 2 in the SAME session (single iteration cycle). However, both invoke dedicated AGENTS (per Q1-AGENTS) with their own context — the agents are split per LLM-activation, not per token-cost.

**Anti-cut F: Splitting iteration cycles (v1 / v3 / v5 …) into separate tasks.**

Rationale: Each iteration cycle has its own version of the scribble. Splitting tasks adds task-creation overhead + re-reads. Today the iterating orchestrator handles all versions in one task with phase cycling.

**Verdict**: Keep iteration cycles in ONE task. The proposed sub-skill split (SCRIBBLE-SPLIT) preserves this — the orchestrator (`ui-scribble-iterate`) owns the loop; sub-skills are invoked per phase, not per version.

---

## 5. Agent vs session distinction (clarifying)

This was implicit above; making it explicit:

- **Session split** = the main conversation thread ends; a new conversation thread starts cold. Cache expires; context starts empty. Triggered by: user pause >5 min, new `task-create` invocation (typically), explicit fresh-claude launch in automated mode.
- **Agent invocation within a session** = the main session spawns a sub-agent (background or foreground). The sub-agent has its own cold context. The main session continues with its existing cache. Triggered by: `Task` tool / `Agent` tool call.

**Agent invocation costs**:
- Sub-agent input tokens (full cold read for the agent's prompt)
- Sub-agent output tokens
- Main session input tokens for the agent's return message (small if the agent writes to a file and returns only a path)

**Session-only costs**:
- Main session input tokens (cached if recent; cold if expired)
- Main session output tokens

**When agent invocation wins**:
- The main session has accumulated significant unrelated context (bloat)
- The agent's task has a self-contained context window (reads ≤10 artifacts)
- The agent's output is small (a path + a summary), so it doesn't bloat the main session on return
- The work is parallel-able (foreground main session can do other things while background agent runs)

**When agent invocation loses**:
- The main session already has the context the agent would need
- The agent's task is small (a few file reads); the spawn overhead > the saved bloat
- The work must serialize with the next main-session step (foreground blocks the session anyway)

### 5.1 Mapping to the recommended cuts

| Cut | Mechanism | Why |
|---|---|---|
| Cut A (Phase 4 as session) | Session split (next `task-create`) | Cache already expired during user review |
| Cut B (Phase 5 as brief agent) | Agent invocation | Self-contained read; small output; saves bloat in iterator |
| Cut C (persona-embodiment as agent) | Agent invocation | Distinct context (1 scenario per persona); reusable elsewhere |
| Cut D (UX-protocol-reviewer as agent) | Agent invocation | Vocabulary corpus in agent prompt, not session context |

---

## 6. The "delegate to agent" heuristic (in plain English)

When work in the main session would:

1. Require loading artifacts the main session doesn't already have → **delegate to agent** (the agent loads fresh; the main session stays light)
2. Be self-contained (clear input list, defined output, no need to interact with the user during the work) → **delegate to agent** (background-able; main session keeps cache warm)
3. Produce a large output (a long analysis, a many-file fan-out) where the main session only needs a summary → **delegate to agent** (the agent writes to a file; returns the path + summary)
4. Be expensive and parallel-able (web research, multi-file investigation, broad codebase scans) → **delegate to agent** (foreground while main session does other things)

When work would:

1. Use only artifacts already in main session context, and produce small output → **stay in main session** (no point paying spawn overhead)
2. Need iterative user interaction → **stay in main session** (agents can't sustain a conversation with the user)
3. Be a single quick read or edit → **stay in main session** (delegation overhead > the saved bloat)

### 6.1 Applied to this very session

Today's work in TASK-PROC-032-10 used delegation correctly:
- **Spawned `general-purpose` agent** for web research on Han + wireframe-to-code contracts (iteration 1) → correct (web research is bloat-heavy, distinct context)
- **Spawned `general-purpose` agent** for the meta-exploration on skill-interface contracts (iteration 4) → correct (10+ web fetches + skill inventory pass = bloat-heavy, distinct context)
- **Wrote iteration 1–5 documents in the main session** → correct (each document builds on previous iterations already in context; an agent would re-read everything cold)
- **Wrote this efficiency analysis in the main session** → correct (same reason as above)

The user's real-time hint reinforces this principle for future work (NEW-EXPLORATION's execution especially).

---

## 7. Recommendation for the sub-skill split (SCRIBBLE-SPLIT)

The meta-exploration agent proposed 4 sub-skills + 1 thin orchestrator. The token-efficiency lens informs *whether each sub-skill should be its own session or an agent within the orchestrator's session*:

| Sub-skill | Session or agent? | Reason |
|---|---|---|
| **ui-scribble-iterate** (orchestrator) | Session (one per scribble cycle) | Owns the iteration loop; manages user-interaction points |
| **ui-scribble-generate** (Phase 1) | Agent invoked by orchestrator | Reads heavy context; produces files; output is paths, not full HTML in main context |
| **ui-scribble-auto-review** (Phase 2) | Agent invoked by orchestrator | Same as generate; needs ~80% overlap with generate's reads but ITS OWN agent so the orchestrator's session doesn't double-load |
| **ui-scribble-feedback-classify** (Phase 4) | Session — fresh `task-create` after user feedback | Cache expired during user review; classify-then-invoke-other-skills is its own work unit |
| **ui-scribble-approve-handoff** (Phase 5) | Agent invoked by orchestrator | Small mechanical task; returns paths |

Plus the reviewer agents that the auto-review sub-skill spawns in turn:
| Reviewer | Where |
|---|---|
| persona-embodiment-reviewer | Agent invoked by ui-scribble-auto-review |
| scribble-ux-protocol-reviewer | Agent invoked by ui-scribble-auto-review |

**Implication for SCRIBBLE-SPLIT**: the 4-sub-skill split is fine AT THE SKILL LEVEL but the runtime model is "orchestrator session + 3-4 agents per cycle + 1 fresh session for feedback classification." This is a HYBRID — sessions split at user-interaction boundaries; agents split at LLM-activation boundaries.

---

## 8. Per-stage token-cost estimate (rough order-of-magnitude)

Using a hypothetical mid-complexity scribble (5 screens, 3 personas, 2 T1 + 4 T2 rules, 1 parent flow, 0 inspiration files):

| Stage | Input tokens (cold) | Cached input cost | Output tokens | Notes |
|---|---|---|---|---|
| Phase 0.5 pre-brief | ~25k | N/A (first read) | ~500 | Writes pre-brief.md; minimal |
| Phase 1 generate (agent) | ~40k | N/A | ~15k | Big input; per-screen HTML output substantial |
| Phase 2 auto-review (agent) | ~42k | N/A (fresh agent) | ~15k | Same heavy read as Phase 1 + scribble itself |
| Phase 2.5 persona-embodiment (agent) | ~12k | N/A | ~3k | 1 scenario × 3 personas + scribble |
| Phase 2b UX-protocol-reviewer (agent) | ~6k | N/A | ~3k | Vocab in agent prompt; reads only scribble |
| Phase 4 feedback-classify (new session) | ~30k | N/A | ~5k | Cache expired; full read |
| Phase 5 approve-handoff (agent) | ~10k | N/A | ~2k | Mechanical |

**Per iteration cycle total** (Phase 1 → 2.5 → 2b → 2 → 3 → 4 → 5, assuming feedback received once): roughly ~165k input + ~43k output = ~210k tokens per cycle.

**Cycles per scribble**: typically 2-4 (v1 → v2 → optional v3 → approval). Mid-case: ~600-800k tokens per scribble end-to-end.

These numbers are coarse; NEW-EXPLORATION should validate via instrumented prototype.

### 8.1 What this is NOT measuring

- Vision-input cost (Phase 0 multimodal seed; visual-validation Opus calls) — these add substantially when present but are excluded for the baseline
- Cache reuse savings if Phase 2 follows Phase 1 closely enough to share warm cache (today rare because the user interaction triggers cache expiry)
- The downstream coding session (which reads the scribble + handoff yaml during implementation)

---

## 9. The "split too much vs split too little" trade-off

| Direction | Risk |
|---|---|
| Over-split (every phase its own session/skill) | Each session pays cold-start; aggregate re-reads dominate; orchestration overhead grows |
| Under-split (everything in one session/skill) | Context bloat; cache thrashing; the SKILL.md grows unmaintainable |

**The recommended cuts (§4.1) sit at natural boundaries**:
- Phase 4 split = at user-interaction boundary (cache already gone)
- Agent invocations = at LLM-activation boundary (specialized vocabulary worth its own prompt)
- Sub-skill split = at maintainability boundary (per-phase files for human readers)

These are *different* boundary criteria, and they align — the natural split points serve multiple purposes simultaneously. That alignment is the signal we have the right cuts.

---

## 10. Recommendations for NEW-EXPLORATION

Items NEW-EXPLORATION should validate via prototype:

1. **Measure the actual token cost** of one scribble end-to-end on a real feature (instrument a Phase-1→5 run). Compare against the §8 estimate.
2. **Test cache-hit rates** for the Phase 1 → Phase 2 transition. If the auto-reviewer fires soon enough after generate that the cache is warm, the savings could be larger than §8 assumes; if not, the cost is closer to the agent-per-phase model.
3. **Validate Cut A** (Phase 4 as fresh session) by checking whether classify-then-invoke patterns benefit from cold context (no Phase 1 noise) or hurt (re-reading the rule corpus).
4. **Validate the 1-scenario-per-persona cap** by running persona-embodiment-reviewer on 2-3 representative scribbles and measuring whether 1 scenario suffices for finding quality.
5. **Document a "delegation decision tree"** the orchestrator skills use to choose session-vs-agent at runtime, codifying §6.

---

## 11. Honest gaps in this analysis

- **Numbers are coarse.** Real token counts depend on model, prompt-cache state, image vs text input, and per-agent behavior. The relative trade-offs are robust; the absolutes are not.
- **No instrumentation today.** We're not measuring scribble-cycle tokens — the §8 estimates are derived from skill-prompt lengths + typical artifact sizes. NEW-EXPLORATION should instrument before locking-in cut decisions.
- **Cache modeling assumes Anthropic's 5-min TTL** (per CLAUDE.md). If automation mode changes this (e.g. long-lived agents with different cache behavior), the cut decisions shift.
- **Sub-skill split's runtime impact** depends on how `task-create` invocations are bundled. If every sub-skill produces its own task, that's many cold-start sessions; if sub-skills are invoked within one orchestrating task's session, the analysis above holds.
- **Multi-feature scribble runs** (when one scribble cycle is part of a larger 0.0.1 release impl session) inherit the same patterns but compound across features. The infrastructure-first decision (iteration 5 §7) is partly motivated by amortizing this.
- **Web-research and exploration tasks** (like NEW-EXPLORATION itself) follow different patterns — their token cost is dominated by web fetches and broad codebase reads. The agent-delegation principle is the right answer there; the session-vs-agent cut decisions are simpler.

---

## 12. Summary table — actionable cuts

| Cut | Action | Owns |
|---|---|---|
| A | Phase 4 (feedback-classify) → fresh `task-create` session | NEW-EXPLORATION ratifies; SCRIBBLE-SPLIT implements |
| B | Phase 5 (approve-handoff) → agent invoked by orchestrator | SCRIBBLE-SPLIT |
| C | persona-embodiment-reviewer → dedicated agent (D18) | Q1-AGENTS |
| D | scribble-ux-protocol-reviewer → dedicated agent (D16) | Q1-AGENTS |
| E (don't split) | Phase 1 + Phase 2 stay in ONE session (different agents, same task) | SCRIBBLE-SPLIT |
| F (don't split) | Iteration cycles (v1 / v3 / v5 …) stay in ONE task | SCRIBBLE-SPLIT |

The split decisions reinforce, not change, the bundles already in iteration-4 §9. NEW-EXPLORATION validates and may refine.
