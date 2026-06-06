# Han Plugin Agent Inventory

**Source**: github.com/testdouble/han (MIT, by Test Double)
**Fetched**: 2026-05-26
**Purpose**: Distilled inventory for synthesis comparison against our 6-agent model

---

## Agents

| Name | Role / Purpose | Distinctive Lens | Model | Stack-Agnostic? |
|---|---|---|---|---|
| adversarial-security-analyst | Prove real, exploitable vulnerabilities exist in first-party code and dependencies | Adversarial posture: assumes all code is insecure; requires file path + line + exploit path or CVE before reporting anything | opus | Yes — reads any dependency manifest format |
| adversarial-validator | Actively disprove investigation findings and planned fixes before they ship | Pessimistic by default; searches for counter-evidence, unhandled edge cases, and flawed assumptions in upstream output | sonnet | Yes |
| behavioral-analyst | Analyze runtime behavior — data flow, error propagation, state management, integration boundaries | Produces numbered findings with file paths and verbatim code; focused on how data moves and where it is lost, not structure | sonnet | Yes |
| codebase-explorer | Discover implementation details for a specific feature or system across multiple angles | Adapts exploration strategy to feature type (auth, API, UI, etc.); finds entry points, models, config, and tests | haiku | Yes |
| concurrency-analyst | Identify race conditions, shared-resource contention, deadlock potential, async error handling | Examines patterns invisible in sequential analysis; specialized vocabulary (TOCTOU, lock ordering, retry storm) | sonnet | Yes |
| content-auditor | Validate documentation updates preserve all facts that are still true in the codebase | Suspicious posture: assumes content was lost; classifies each fact as present / correctly removed / missing | haiku | Yes |
| data-engineer | Prove real data-modeling, schema, access-pattern, migration, and governance problems | Adversarial: assumes schema is over/under-normalized and indexed for the wrong workload; covers ORM, migrations, pipelines | opus | Yes — language-agnostic schema review |
| devops-engineer | Prove operational risks exist before a change reaches production | Adversarial; audits against DORA metrics, Twelve-Factor App, Four Golden Signals, SLO/error-budget discipline | opus | Yes |
| edge-case-explorer | Systematically discover edge cases that should be covered by tests | Traces every input source, call chain, and integration boundary; focused mode by default (crashes/corruption only, not exhaustive) | sonnet | Yes |
| evidence-based-investigator | Gather concrete, verifiable evidence about a codebase issue | Every claim must have file path + line number + code snippet or error message; no speculation | sonnet | Yes |
| gap-analyzer | Find every place current state fails to satisfy desired state | Four-category taxonomy: Missing / Partial / Divergent / Implicit; can compare code against specs, PRDs, requirements, or design docs; accepts URLs | sonnet | Yes — accepts any artifact format |
| information-architect | Prove findability, orientation, and comprehension problems exist in documentation | Adversarial; audits against Rosenfeld & Morville IA systems; covers README, API docs, ADR collections, tutorials | opus | Yes |
| junior-developer | Surface hidden assumptions, muddied scope, and claims made without evidence | Two operating modes: artifact-review (8 analysis protocols, writes to file) and conversational (live discussion, 2-5 clarifying questions); asks what experts assume away | opus | Yes |
| project-manager | Facilitate team discussions and synthesize cross-specialist input into a committed plan | Two modes: facilitation (round-robin, evidence audit, open-item log) and synthesis (reconcile specialists, write final plan with rejected alternatives) | opus | Yes |
| project-scanner | Discover project-level attributes: languages, frameworks, tooling, config, infrastructure | Reads config files and directory structure rather than tracing code; optimized for fast project characterization | haiku | Yes |
| research-analyst | Answer open-ended questions with sourced web evidence and a recommendation | Uses WebSearch + WebFetch; treats fetched content as claims to evaluate, not instructions; produces options landscape with recommendation | sonnet | Yes — web-first |
| risk-analyst | Assess risk of inaction for architectural findings produced by upstream analysts | Does not discover problems; receives pre-digested structural/behavioral/concurrency output and evaluates likelihood, severity, blast radius, reversibility | sonnet | Yes |
| software-architect | Prove intra-codebase structural problems (coupling, cohesion, abstraction boundaries) | Adversarial: assumes structure is wrong until evidence says otherwise; distinct from system-architect in that scope is within one codebase | opus | Yes |
| structural-analyst | Analyze static structure — module boundaries, coupling, dependency direction, duplication | Produces numbered findings with file paths and verbatim code; pure static view, no runtime inference | sonnet | Yes |
| system-architect | Prove cross-service/cross-context topology problems (bounded context leakage, event vs. sync, data ownership) | Adversarial; scope is between services/contexts, not within a single codebase (complements software-architect) | opus | Yes |
| test-engineer | Identify untested behaviors and produce a prioritized test plan | Focuses on observable behavior (inputs/outputs/collaborator interactions), not internal code paths; recommends test doubles (stubs for queries, mocks for commands) | sonnet | Yes |
| user-experience-designer | Prove real usability problems exist in an interface or flow | Adversarial; grounds findings in Nielsen's 10 heuristics, WCAG 2.2, Universal Design, affordance/signifier clarity (Norman); reports only grounded violations | opus | Yes |

### Standout Agent Notes

**adversarial-security-analyst**: The non-negotiable evidence standard is the key design choice — no finding is reported unless the exploit path can be fully demonstrated. This eliminates false-positive noise and makes findings actionable. Reads all dependency manifests automatically.

**gap-analyzer**: Unusually versatile — the "desired state" can be a spec, PRD, requirements doc, or URL. The four-category gap taxonomy (Missing / Partial / Divergent / Implicit) is a concise, reusable framework that could be adopted independently of the rest of han.

**junior-developer**: The dual-mode design (artifact-review vs. conversational) is distinctive. The agent explicitly models the "3-5 year generalist asking the questions experts no longer ask" perspective — a structured implementation of adversarial-collaboration that is separate from any single domain specialty.

**risk-analyst**: Deliberately receives pre-digested output from other agents rather than discovering problems itself. This is a pure downstream/synthesis role — it exists to answer "what happens if we do nothing about this finding?" across four dimensions. The anti-pattern list (Severity Inflation, Reversibility Optimism) is particularly concrete.

**project-manager**: The facilitation/synthesis split mirrors how real project managers work. The synthesis mode explicitly records rejected alternatives with reasons, which creates a lightweight ADR-style artifact as a byproduct.

---

## Agent Design Philosophy

### 1. Multi-Agent Economics (`docs/guidance/agent-building-guidelines/multi-agent-economics.md`)

**Core thesis**: Start with the simplest architecture that could work and add agents only when measured quality justifies the cost.

**The escalation cascade** (three levels):
- Level 0 — Single agent handles ~70% of tasks when well-prompted with domain vocabulary and tool access
- Level 1 — Add a second (reviewer) agent when the worker cannot reliably self-validate due to self-evaluation bias (generator biases replicate in evaluation)
- Level 2 — Team of 3-5 agents only when the review problem is genuinely multi-dimensional and combining reviewers into one degrades each domain's vocabulary activation

**Hard cap**: Teams must not exceed 5 agents. Beyond this, coordination costs consistently exceed production benefits.

**The 45% threshold**: Before adding an agent, verify the current architecture achieves less than 45% of optimal quality on the dimension being improved. If above 45%, improve the existing agent's instructions first.

**Scaling data** (DeepMind 2025 cited):
- 3 agents: ~4x tokens, ~2x quality, efficiency 0.5
- 5 agents: ~7x tokens, ~3.1x quality, efficiency 0.44
- 7+ agents: ~12x+ tokens, quality often less than 4-agent, efficiency < 0.3

Sequential reasoning tasks (each step depends on prior full context) can degrade 39–70% in multi-agent setups due to context loss at handoffs.

**Key implication**: Having 22 agents in the roster does not mean 22 agents are dispatched per task. The roster is the maximum available pool; skills choose a sized subset per invocation.

### 2. Domain Focus (`docs/guidance/agent-building-guidelines/agent-domain-focus.md`)

**Core thesis**: Focused domain vocabulary activates deep expert-level knowledge; generalist language activates shallow averaged knowledge.

**Vocabulary routing**: LLMs organize knowledge in embedding clusters activated by precise terminology. The "15-year practitioner test" — would a senior domain expert use this exact term with a peer? If not, the term is too generic.

**50-token role identity budget**: The "You are a..." opening paragraph should be under 50 tokens. Longer persona descriptions degrade accuracy by consuming attention on self-description rather than task performance. The frontmatter `description` field is separate and not subject to this budget (it serves as triggering metadata).

**Self-evaluation bias**: Agents cannot reliably evaluate their own work because generator biases replicate in evaluation. An agent should have a single role: generate or evaluate, not both. This is the primary justification for multi-agent review patterns.

**Domain vocabulary section**: Each agent definition includes a vocabulary section with the precise terms a practitioner would use — this is a documented design convention, not incidental.

### 3. Agent Model Selection (`docs/guidance/agent-building-guidelines/agent-model-selection.md`)

**Core thesis**: Choose model based on what the task demands; cost is explicitly not a factor.

**Decision criteria** (in order):
1. Use `inherit` only when the task is generic enough that the user's session model should carry through (rare)
2. Use `opus` when: synthesizing across many files, auditing for subtle omissions, exploring large codebases with judgment-driven direction, qualitative assessment weighing competing factors
3. Use `sonnet` when: following defined protocols, gathering evidence along well-defined paths, validating against known criteria, structured investigation
4. Use `haiku` when: quick file searches, simple pattern matching, high-volume repetitive operations, latency matters more than depth

**Observed distribution across 22 han agents**: 8 opus (adversarial specialists, synthesizers), 10 sonnet (structured investigators, validators), 4 haiku (fast scanners/auditors).

**Cost optimization is explicitly rejected** as a selection criterion: "A false economy that wastes developer time reviewing bad output and re-running tasks."

### 4. Graceful Degradation (`docs/guidance/agent-building-guidelines/graceful-degradation.md`)

**Core thesis**: Agents must check tool availability inline and skip gracefully rather than failing silently when tools (git, CLIs, external APIs) are absent.

**The pattern**: For any step depending on a tool, check availability before attempting. If unavailable, skip and note the limitation explicitly in output. This makes agents self-adapting and eliminates the need for calling skills to add defensive guards around every dispatch.

**Explicit notation requirement**: The agent must include a line like "Note: git was not available. Recency analysis was skipped." — not silently omit results.

### 5. Specialization and Model Selection (`docs/guidance/specialization-and-model-selection.md`)

**Core thesis**: A well-specified agent definition shifts work from inference-time compute (model tier, thinking budget) to prompt-time design, allowing smaller models to match larger ones on narrow tasks.

**Mechanism**: Specialization stops the model from wasting capability on disambiguation and planning — it does not raise the capability ceiling. For genuinely novel reasoning, no prompt fixes the limitation.

**Literature cited**:
- Up to ~4x performance improvement from prompt optimization on classification tasks (Orq.ai)
- 10–40 percentage-point gains from complexity-guided decomposition (arXiv 2510.07772)
- Smaller models match larger ones on narrow tasks once prompts encode the task tightly (arXiv 2301.12726)

**Brittleness trade-off acknowledged**: Specialized prompts perform worse on out-of-distribution inputs. General Opus + high-effort is more robust; a tight agent definition is more efficient on the path it was built for.

**Three signals for model choice**: (1) prompt specificity — named heuristics, fixed output shape, narrow domain → lower tier viable; (2) reasoning novelty — synthesis across unbounded inputs → higher tier required; (3) brittleness tolerance — agents that anchor downstream work need robustness.

### 6. Sizing (`docs/sizing.md`)

**Core thesis**: Every sizing-aware skill classifies work as small/medium/large before dispatching agents, and scales the roster and iteration depth accordingly. Default is small; escalate only on concrete signals.

**Three bands**:
- Small: single subsystem, handful of files, no cross-cutting concerns → minimum roster, 1 iteration round
- Medium: 2-3 adjacent subsystems, up to ~12 files, one cross-cutting concern (schema migration, new permission) → required roles + 2-3 domain specialists
- Large: cross-service, security-sensitive, architectural changes, >12 files → required roles + 4-6 domain specialists

**Auto-classification process**: Start at small. Map signals (file count, subsystem count, security/PII/auth/data surface, integration concerns). Escalate only when a signal clearly requires it — borderline signals stay at the smaller band. Announce the chosen size and justification before dispatching.

**Always overridable**: Pass size as the first positional argument (`/code-review medium`, `/plan-a-feature large`).

**Conservative design philosophy**: "Fewer agents producing higher-signal findings is the goal; quantity is not the metric. The skill prefers under-dispatching that you can re-run at a larger size to over-dispatching that drowns you in low-signal findings."

**Why this matters**: Without sizing, a two-line README fix would dispatch the full security/structural/behavioral/concurrency/data/devops/test/edge-case roster. A cross-service change would get the same default roster as a single-file rename. Findings would not calibrate to scope, mixing Suggestions with Criticals.

---

## Summary: Key Design Contrasts vs. a 6-Agent Model

Our factory uses 6 broad roles (architecture-advisor, implementation-engineer, test-engineer, quality-checker, setup-optimizer, general). Han uses 22 narrow specialists dispatched selectively by size-aware skills. The critical differences:

1. **Roster vs. team**: Han's 22 agents are a pool, not a team. Per-invocation, 2-6 are selected based on sizing. The factory should read "22 specialists" as "up to 22 available roles" rather than "22 always-active agents."

2. **Adversarial posture as a first-class design pattern**: 9 of 22 agents are explicitly adversarial (assume the thing being reviewed is wrong/insecure/incomplete). Our 6 broad agents do not encode this posture as a named design choice.

3. **Self-evaluation bias is the primary justification for specialist reviewers**: Han names the anti-pattern explicitly — a generator agent must not evaluate its own output. This is the structural reason specialist review agents exist as separate entities.

4. **Model assignment per cognitive profile, not cost**: Han uses opus for judgment/synthesis, sonnet for structured investigation, haiku for fast scanning. The 6-broad-agent model tends to inherit the session model uniformly.

5. **Sizing is the economics enforcement mechanism**: Rather than a fixed agent count, skill-level sizing logic determines how many and which agents run. This is the mechanism that makes a large roster economically defensible.
