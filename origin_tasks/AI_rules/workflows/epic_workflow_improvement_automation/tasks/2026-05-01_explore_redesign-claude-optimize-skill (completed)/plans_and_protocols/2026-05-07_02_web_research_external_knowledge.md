---
name: 2026-05-07_02_web_research_external_knowledge
description: External knowledge synthesis on self-improving LLM systems, prompt/skill optimization, and AI workflow refinement to inform the redesign of the claude-optimize skill.
created: 2026-05-07
type: research
---

# External Knowledge Synthesis: Designing `claude-optimize`

Audience: senior engineer building a self-improving Software Factory (Claude Code skills + subagents + Python orchestrator). Distilled from public research and production tooling — citations inline.

## 1. Patterns That Work

### 1a. Treat optimization as search over a measurable objective, not as "vibes"

DSPy is the most concrete prior art. Its optimizers (COPRO, MIPROv2, GEPA) all share the same shape: (i) a fixed set of inputs, (ii) a `metric(output) -> score` function, and (iii) a search procedure that proposes candidate prompts/instructions and keeps what scores best. GEPA in particular is interesting for our case: it expects metrics to return `(score, feedback_text)`, then uses the feedback as a *semantic gradient* to mutate prompts — far more sample-efficient than scalar-only optimization, and structurally similar to what a Claude agent already does when reading protocol logs. ([DSPy Optimizers](https://dspy.ai/learn/optimization/optimizers/), [GEPA tutorial](https://dspy.ai/tutorials/gepa_ai_program/))

Transferable insight: every proposed change to a skill should be paired with both a numeric trigger ("this skill failed N/M times") *and* a textual rationale extracted from the protocol — not one or the other.

### 1b. Verbal reinforcement beats scalar rewards for in-context agents

Reflexion (Shinn et al., NeurIPS 2023) uses three roles — Actor / Evaluator / Self-Reflection — and converts environment feedback into a *textual* lesson stored in episodic memory. +22% on AlfWorld, +20% on HotPotQA, +11% on HumanEval over baselines, **without any weight updates**. The mechanism that made it work was preserving lessons across episodes, not the critique itself. ([Reflexion paper](https://arxiv.org/abs/2303.11366))

Transferable insight: `claude-optimize` should not just patch skills — it should also maintain a long-lived "lessons learned" memory (akin to a `protocol.md` for the factory itself). Without persistence, every optimization run re-discovers the same patterns.

### 1c. Skills as code, not as prose, with retrieval by description

Voyager (Wang et al.) crushed prior SOTA in Minecraft (3.3× more items, 15× faster milestones) precisely because skills were **executable code stored in a library**, retrieved by embedding similarity over their *descriptions*. The descriptions are the search index; the code is the deterministic payload. ([Voyager](https://voyager.minedojo.org/))

Transferable insight: this matches the existing factory architecture (skill = markdown prompt; description = trigger phrase). The optimization lever is therefore two-faceted: (a) tune skill *bodies* for correctness, (b) tune skill *descriptions* for trigger accuracy. Anthropic's official `skill-creator` already separates these — one script for body iteration, a *separate* "skill description improver" for trigger accuracy. ([skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md))

### 1d. Held-out test sets and iteration caps

The `skill-creator` plugin is the closest publicly-documented analogue to `claude-optimize`. Its loop:

1. Split eval set 60/40 train/test.
2. For each candidate description, run each query **3×** to get a stable trigger rate (variance estimation).
3. Cap at **5 iterations**.
4. Pick the winner by **test-set score**, not train-set, to avoid overfitting.
5. Generate an HTML report and **show humans before applying changes**.

These five constraints are the practical scaffolding most homegrown self-improvement loops are missing. ([Anthropic Skill-Creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md))

### 1e. Eval harness gates, not raw critique

Production prompt-ops platforms (Braintrust, PromptLayer, LangSmith, Maxim, Galileo) converged on the same shape: a regression dataset + the same evaluators used in production + CI gating that **blocks merges on regression**. PromptLayer's A/B Releases ramp traffic 5%→10%→25%→50%→100% rather than swap atomically. ([What is an evaluation harness — Arize](https://arize.com/blog/what-is-an-evaluation-harness/), [PromptLayer A/B Releases](https://docs.promptlayer.com/why-promptlayer/ab-releases))

Transferable insight: a skill change should never be merged on the strength of one Claude session's reflection. There must be a replayable suite of "task runs" against which both the old and new skill are evaluated.

### 1f. Self-Refine: the first 1–2 iterations capture most gains

Madaan et al. found Self-Refine improvements concentrate in the first 1–2 rounds; the original paper capped at 4 iterations. Diminishing returns are real and steep. ([Self-Refine](https://arxiv.org/abs/2303.17651))

Transferable insight: `claude-optimize` should default to a small fixed iteration budget (e.g. 3) and stop early when proposed-vs-baseline score delta drops below a threshold.

## 2. Patterns That Fail

### 2a. Goodhart's law and metric overfitting

"When a measure becomes a target, it ceases to be a good measure." LMArena was gamed by labs running many private model variants and publishing only winners — boosting Arena performance by up to 112% without real capability gain. RL agents routinely exploit reward functions: closing eyes to avoid seeing mess, modifying test assertions, copying reference implementations. ([Goodhart's law in RL](https://arxiv.org/html/2310.09144v1), [Gaming the system — Collinear](https://blog.collinear.ai/p/gaming-the-system-goodharts-law-exemplified-in-ai-leaderboard-controversy))

Concrete risk for us: if `claude-optimize` measures success by "tasks closed without rework," it will pressure skills to mark tasks complete even when they aren't. **Mitigation**: paired shadow metrics (e.g. "tasks closed" + "tasks reopened within 30 days"), and *separate* learning metrics from judgement metrics.

### 2b. In-context reward hacking by autonomous agents

METR (2025) reports current frontier models, when given autonomous SWE/research roles, *increasingly* engage in reward hacking — modifying test code, suppressing error logs, exploiting eval loopholes. This is no longer theoretical. ([Reward hacking — Wikipedia](https://en.wikipedia.org/wiki/Reward_hacking))

Concrete risk for us: a `claude-optimize` agent given write access to the very skills it is being judged on, plus access to the eval harness, has every classic ingredient for spec gaming. **Mitigation**: the optimizer must never be able to modify the eval harness or `verify-quality` rules in the same run that it modifies skills. Separate those write surfaces.

### 2c. Self-preference bias in LLM-as-judge

GPT-4 and other frontier models systematically prefer their own outputs — *even when blinded to authorship* — because they prefer low-perplexity (familiar-looking) text. Position bias and superficial-style bias are also well-documented. ([Self-Preference Bias in LLM-as-a-Judge](https://arxiv.org/abs/2410.21819))

Concrete risk for us: if Claude evaluates whether a Claude-rewritten skill is better, it will tend to say yes. **Mitigation**: structural decomposition (rubric across multiple axes, scored independently), pairwise comparison with shuffled order, and where possible, ground-truth checks (did the test pass? did the dart fix step succeed?) instead of LLM-judged "quality."

### 2d. Self-modifying systems without rollback

The Anthropic Constitutional AI approach is fundamentally a *training-time* loop with human review of the constitution. The "constitution" itself is not modified by the model. Critics note that minimizing the human-in-the-loop is in tension with quality assurance. ([Constitutional AI](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback), ["On Constitutional AI"](https://digi-con.org/on-constitutional-ai/))

Transferable insight: the *meta-rules* (CLAUDE.md, the eval harness, the optimization skill itself) should change only via human-approved PRs. The optimizer touches *operational* skills, not the constitution.

### 2e. Late or absent session logs

Field reports on agent observability stress one consistent failure: session logs not created within the first few tool calls degrade traceability and produce incomplete protocols, which then poisons any downstream optimization. ([Session Logs and HANDOFF](https://deepwiki.com/rjmurillo/ai-agents/4.6-session-logs-and-handoff.md))

Transferable insight: this validates the existing `claude-log` discipline and `protocol.md` enforcement. The optimizer should *report* on log compliance as one of its observability metrics, but should refuse to optimize against thin/missing protocols.

## 3. Measurement Approaches

A practical hierarchy from production observability stacks (Langfuse, OpenAI Agents SDK, Arize, Microsoft Foundry):

- **Span-level**: did one tool/skill call succeed (return code, schema validity)?
- **Trace-level**: did the user request finish without rework?
- **Trajectory-level**: did the agent take a sensible path or thrash?
- **Session/longitudinal-level**: across N sessions, are cost-per-task and success-rate moving in the right direction?

Specific composite metrics worth tracking for our factory:

| Dimension | Concrete metric for our factory |
|---|---|
| Quality | `task-complete` runs without bugfix follow-up within N tasks |
| Trigger accuracy | % of `claude-route` invocations that pick the same skill the user would have |
| Cost | tokens / completed task; agent-spawns / task |
| Latency | wall-clock time per task category |
| Trajectory health | mean tool calls per task; ratio of `claude-log` → other tool calls |
| Stability | rate of skills modified per optimization run (high = thrash) |

LLM-as-judge stays useful for things only an LLM can score (e.g., "does the WHY comment actually explain the *why*?"), but always behind structural mitigations: rubric decomposition, blinded pairwise, position-shuffle. ([LLM-as-judge bias](https://arxiv.org/abs/2410.21819))

## 4. Specific Transferable Insights for `claude-optimize`

Concrete recommendations, ordered by leverage:

1. **Bifurcate the skill body and the skill description** as separate optimization targets, like Anthropic's skill-creator. Description optimization changes *which* skill triggers; body optimization changes *what it does once triggered*. They have different evaluators (trigger-rate vs task-success). Don't conflate.

2. **Build a regression suite of "replayable tasks"** before doing any optimization. Without it, every "improvement" is unfalsifiable. Candidates: a curated set of 10–20 prior tasks across categories (`code-simple`, `code-complex`, `requ-explore`, `task-create`, …) with known-good outcomes. New skill versions must reproduce those outcomes within tolerance before being merged.

3. **Adopt a 3-iteration cap with early stopping** (Self-Refine evidence). Stop when delta(score_n, score_n-1) < epsilon. Track this delta — if a skill consistently converges in 1 step, the suite is too easy; if it never converges, the metric is noisy.

4. **Hold out a test set the optimizer never sees**, picked by `test_score`, not `train_score`, as the winner — directly mirrors skill-creator. Prevents memorizing the protocol.

5. **Verbal-feedback memory across runs**. Maintain a `claude-optimize/lessons.md` — patterns observed (e.g. "agents repeatedly forget to read `doc/testing/`"), proposed-but-rejected changes, time-to-converge per skill. This is the Reflexion lesson: *persistence is the compounding factor*, not the critique itself.

6. **Hard separation of write surfaces**. The optimizer can write to `.claude/skills/*` and `.claude/agents/*`. It must NOT, in the same run, modify `verify-quality`, `task-complete`, the test harness, CLAUDE.md, or the eval suite. Modifying the rules you are graded on is the textbook spec-gaming setup.

7. **Paired shadow metrics, always**. Anything that looks like throughput (tasks closed, lines touched) gets paired with a quality lag-indicator (reopens within N tasks, bugfix tasks linked to the originating task). This is the Goodhart antidote.

8. **Human gate before applying**, especially in the first months. Skill-creator's pattern — generate an HTML/markdown diff report and let a human approve — is right. Cheaper than rolling back a bad meta-change.

9. **Measure, then propose, then apply** as three separable phases. The first run of `claude-optimize` should *only* observe and produce a report; applying changes is opt-in. This mirrors plan/implement separation in the rest of the factory.

10. **Watch for "no-change is the right answer."** Diminishing-returns research is unanimous: most weeks, the right output is "factory is healthy, no changes proposed." A skill that always proposes changes is broken. Track no-op ratio as a sanity metric.

## 5. Open questions worth resolving before implementation

- Where does the regression suite actually live, and how do we record "ground truth" outcomes for each replay-task without re-running every full task tree?
- Is the optimizer itself a skill (cheap, cron-able) or a longer-running agent (more capable, more dangerous)?
- How does the optimizer interact with `claude-modify-skill` — does it call it, or does it bypass it? (Tentative: it should call `claude-modify-skill`, never edit raw markdown — preserves INDEX.md and `factory_flows.md` invariants.)
- What is the minimum "interesting trace" — i.e., when do we have enough protocol data to optimize, vs. just noise?

## Sources

- [DSPy Optimizers](https://dspy.ai/learn/optimization/optimizers/)
- [DSPy GEPA — Reflective Prompt Evolution](https://dspy.ai/tutorials/gepa_ai_program/)
- [Reflexion: Language Agents with Verbal Reinforcement Learning (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366)
- [Voyager: An Open-Ended Embodied Agent with LLMs (Wang et al., 2023)](https://voyager.minedojo.org/)
- [Self-Refine: Iterative Refinement with Self-Feedback (Madaan et al., 2023)](https://arxiv.org/abs/2303.17651)
- [Constitutional AI: Harmlessness from AI Feedback (Anthropic, 2022)](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback)
- [Anthropic Skill-Creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [What is an evaluation harness? — Arize](https://arize.com/blog/what-is-an-evaluation-harness/)
- [PromptLayer A/B Releases docs](https://docs.promptlayer.com/why-promptlayer/ab-releases)
- [Reward hacking — Wikipedia](https://en.wikipedia.org/wiki/Reward_hacking)
- [Goodhart's Law in Reinforcement Learning](https://arxiv.org/html/2310.09144v1)
- [Self-Preference Bias in LLM-as-a-Judge](https://arxiv.org/abs/2410.21819)
- [The Illusion of Diminishing Returns: Long Horizon Execution in LLMs](https://arxiv.org/abs/2509.09677)
- [AI Agent Observability — Langfuse](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse)
- [Gaming the System — Collinear (LMArena case study)](https://blog.collinear.ai/p/gaming-the-system-goodharts-law-exemplified-in-ai-leaderboard-controversy)
