# Context Summary (Phase 1: Gathering) — TASK-PROC-004-02

Date: 2026-06-05 · Session 1dab745b (Opus, automated)
Gathered via 3 background agents: web-ideation (a613c2fe…), web-completeness (a89dd30d…), codebase-map (abbf79ec…).

## What is KNOWN

### Spec (REQ-PROC-004, "Structured Ideation Workflow")
Five phases (gather → analyze → ideate → **user gate** → synthesize → report), 7 mandatory ideation techniques, effort tiers (Quick/Standard/Deep) with selection heuristics, a file-watch pause user gate, and a temperature limitation+mitigation. This task = the HOW. (Goal body mislabels the spec "REQ-PROC-067"; that ID is actually *Claude Code Usability* — recorded for final report.)

### Web findings — ideation / creativity (agent a613c2fe)
- **Temperature is a dead end.** Claude Code CLI cannot set temperature (only the Anthropic API can; >1.0 → HTTP 400). Empirically temperature is weak anyway: novelty β≈0.31, *hurts* coherence, "a randomness dial, not a creativity control." → **Do not design around a temperature knob.** ([arXiv 2405.00492])
- **CoT is the #1 diversity lever** — lowest pairwise similarity (0.255) of 35 strategies on GPT-4, nearly matching human-group diversity. ([arXiv 2402.01727])
- **Personas = diverse sampling cues** ("knowledge partitioning"); CoT+personas beat humans. **Multilingual prompting** out-diversifies temperature/personas (cheap surprise lever). ([arXiv 2602.20408], [2505.15229])
- **ADHD — Parallel Divergent Ideation for Coding Agents** (uditakhourii.github.io/adhd): coding agents converge prematurely as a *structural* failure. Fix = **N≈5 context-isolated branches** (no shared context → anchoring eliminated "by construction"), each under a **cognitive-frame distortion** ("re-ask this as a [hardware engineer / biologist / regulator / $0-budget operator] problem"), then a **separate critic pass** that scores novelty/viability/fit, flags "traps" (attractive-but-flawed), **clusters by underlying angle** (3–6 groups), and deepens only top-K survivors. Strongest evidence that for *architecture*, branch isolation + frame reframing + strict generator/critic separation beat sequential SCAMPER (which yields nearby UX-flavored tweaks).
- **Gate between divergence and convergence**, after clustering, before deepening. **Observability gap** (arXiv 2603.26942): output-only human review fails for coding agents — reviewers must see *reasoning/clusters*, not a flat idea list. Maps onto this project's file-based `pending_feedback` model.
- **Mode separation must be mechanical**: divergence prompt forbids evaluation/ranking/hedging; convergence prompt forbids generation. One call doing both collapses divergence.

### Web findings — completeness / multi-run iteration (agent a89dd30d)
- **Output-budget ceiling is real**: base LLMs reliably fail past ~2,000 words single-shot (LongWriter, arXiv 2408.07055) → structural forcing of multi-call decomposition.
- **Two deep-research architectures**: (a) parameterized tree (GPT Researcher: explicit breadth/depth params, structural termination); (b) **gap-driven loop** (qx-labs IterativeResearcher, Magentic, Langflow Reviewer): a **Knowledge-Gap Agent runs FIRST each cycle**, names what's missing, fills it, repeats; breadth/depth emerge from gaps. → **Adopt (b).**
- **Separate critic >> self-assessment.** Self-refinement *amplifies* self-bias ("Pride and Prejudice" arXiv 2402.11436); external/ensemble critics (CRITIC 2305.11738, N-Critics 2310.18679) materially better. Best completeness check = **coverage-against-outline** (decompose into claims, check each).
- **Diminishing returns quantified**: round 1 ≈ 50% of gain, rounds 1–2 ≈ 75%. → cap iterations LOW; spend budget on breadth not deep polish.
- **Termination**: `gaps_empty OR max_iter OR gap_closure_rate < ε`; track per-iteration open-gap delta as convergence meter; graceful degradation = emit partial + open-gaps appendix.
- **Failure modes**: over-aggressive critic *oscillation* (rewrites correct→incorrect) → critic should only **ADD gaps, never rewrite settled content**; premature convergence from self-judged completeness.
- **Ledger schema** (Magentic task-ledger + Reviewer-adds-subquestions): `id, parent_id, question, gap_type(breadth|depth), status(open→in_progress→answered|partial|dropped), depth_score/confidence, iteration_opened/closed, evidence, priority`. Ledger doubles as termination meter AND cache-saver (agents read small ledger, not full prior synthesis).

### Factory mechanisms (agent abbf79ec)
- **File-watch pause already exists**: `automation/pending_feedback/<TASK_ID>/{question.md, answer.md}` + `TEMPLATE_answer.md`. `scripts/tasks/is_awaiting_answer.py` = the answered-sentinel (Exit 1 while question exists AND answer absent/empty/template-only). `scripts/automation/orchestrate.py` (`find_resumable_in_progress_task`, `run_resume_session`) resumes `--resume <session_id>` with archived Q+A preamble. **This IS the requirement's file-watch gate** — file-only, survives context loss, generic.
- **ScheduleWakeup is PROHIBITED for session self-scheduling** (CLAUDE.md responsibility boundary) — the orchestrator owns resume timing. So the gate's "resume" must be orchestrator-driven (automated) or a live chat turn (interactive), NOT an agent that polls/sleeps.
- **Effort precedents**: `goal.md effort: XS|S|M|L|XL`; `scripts/util/should_use_agents.py` (30KB / 5-file thresholds); `doc-lookup-dependencies` budget bands (XS/S→5, M→10, L/XL→25, returns `BUDGET_CAPPED`); task-create sizing gate (expected_tool_calls>60 OR skill_chain_depth≥4 → opus/split/fan-out).
- **Integration points**: requ-explore §1.2–1.6 (gather) before §2.0 (synthesis); code-complex Step 2 planning (architecture-advisor) + §2.0 YAGNI gate + §2b optional han-adversarial-validator (a critic precedent!); task-resolve Step 2 assess&plan; task-create explore template (Seeds + "≥1 synthesis round"); ux-create-flow.
- **Agent infra**: `claude-create-agent` → `.claude/agents/{expertise}-{role}.md` + `.contract.yaml` (role ∈ writer/transformer/reviewer/classifier). Existing reviewer-role precedent: `han-adversarial-validator`, `quality-checker`. Skills spawn agents sequentially (code-complex) or background+heartbeat (task-derive-from-requ).
- **Gap-tracking precedents**: `coverage_report.py` (covered_by cross-ref); `requ-verify-flow-coverage` Phase-1 per-gap extraction files + Phase-2 synthesis (CONFIRMED GAPS / NEEDS USER DECISION); `cycle_state.json` (back-pressure counter); `monitor_repeated_question.py`; protocol.md / fresh-agent-per-batch tracker.

## What is UNKNOWN (inputs to analysis/ideation)
1. Vehicle: skill vs agent vs protocol-section vs combination — and does it depend on effort?
2. Does the divergence phase need true context-isolated branches (ADHD) given Claude Code's agent model, or is single-session multi-frame CoT enough?
3. How the user gate composes with the *completeness* loop without two competing approval points.
4. Gap-ledger concrete schema + who runs the gap-detector (separate critic agent vs self) given factory's agent economics.
5. Continuation vehicle: same-session (context still present, only output budget exhausted) vs cold restart — when each applies.
6. Termination certification + runaway backstop bounded by effort.
7. Minimal integration: can ideation insert into requ-explore/code-complex without rewriting them?
