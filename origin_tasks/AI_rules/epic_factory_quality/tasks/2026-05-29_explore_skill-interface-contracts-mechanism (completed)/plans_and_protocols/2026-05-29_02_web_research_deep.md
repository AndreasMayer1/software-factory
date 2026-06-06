# Deep Web Research — Skill Interface Contracts Mechanism

Date: 2026-05-29
Task: TASK-PROC-044-02
Round: 2 (deep dive after round-1 inventory was acknowledged incomplete)
Scope: 7 framed questions, ~18 web fetches, depth over breadth

This round does not re-do the survey from file 08 (`2026-05-28_08_skill_interface_exploration.md`). It goes deeper on the specific design tensions the developer flagged. Where a finding contradicts file 08, it is flagged inline.

---

## Q1 — When do mature multi-agent systems detect interface-contract mismatch, and what fails when contracts drift?

**Headline finding: detection happens overwhelmingly at runtime, not at lint or build time.** No surveyed framework ships a static "contract.yaml lint" the way a typed-protocol IDL toolchain (gRPC, OpenAPI) would. The mature systems pay for this with documented production-failure modes.

LangGraph's contract enforcement is the most concrete example: state-schema mismatch surfaces as `InvalidUpdateError` at the moment a node tries to write a key that doesn't fit the declared `TypedDict` or `Pydantic` schema, *or* when two nodes write the same un-`Annotated` key in the same super-step ([LangGraph troubleshooting](https://sumanmichael.github.io/langgraph-cheatsheet/cheatsheet/troubleshooting-debugging/), [issue #2644](https://github.com/langchain-ai/langgraph/issues/2644)). Documented failure mode: when Pydantic validation fails inside a subgraph, the traceback "is not useful" — the error surfaces several layers up from the actual node that produced bad data ([issue #1978](https://github.com/langchain-ai/langgraph/issues/1978)). A second documented mode: validation only fires on the *first node's* input, not on subsequent node outputs ([Substack: TypedDict vs Pydantic](https://shazaali.substack.com/p/type-safety-in-langgraph-when-to)). So even the framework's lauded type system is a runtime, partial check.

The Berkeley MAST paper ([arxiv 2503.13657](https://arxiv.org/abs/2503.13657)) analyzed 150+ execution traces across five MAS frameworks and produced a 14-mode taxonomy (FC1 Specification & Design, FC2 Inter-Agent Misalignment, FC3 Task Verification). A follow-up substack ([Future AGI](https://futureagi.substack.com/p/why-do-multi-agent-llm-systems-fail)) cites MAST's 1,600+ trace expansion: overall failure rate 41–86.7% across benchmarks; **41.8% specification/design**, **36.9% inter-agent misalignment**, **21.3% verification/termination**. Within Category 1 the directly contract-relevant modes are **FM-1.1 disobey task specification** and **FM-1.2 disobey role specification** — these are exactly what a declared contract would attempt to prevent. The taxonomy implies that even with strong contracts, an LLM agent can simply refuse to obey them, so a runtime guard (not just a lint) is necessary.

The Maxim AI write-up ([getmaxim.ai](https://www.getmaxim.ai/articles/multi-agent-system-reliability-failure-patterns-root-causes-and-production-validation-strategies/)) describes the canonical drift scenario: "a routing agent deploys with enhanced routing metadata while downstream execution agents run the previous version. Messages include new fields that old agents ignore, losing routing intent and degrading system functionality." This is the multi-agent version of a Protobuf schema-evolution bug — but with no static tool to catch it, because there is no compiler step. Detection is "parsing failures, dropped messages, or incorrect data interpretation" at runtime. A second concrete failure mode they describe: handoffs that "silently fail" leaving "no obvious error traces in individual agent logs" because each agent thinks the other completed the work.

The Future AGI / MAST source also cites an industry-specific number: **PwC reported 7× accuracy improvement (10% → 70%) after adding structured validation loops with judge agents to their CrewAI code-generation pipeline.** This is not a contract-format finding per se, but it argues the *verification* leg of the contract (FC3) carries the largest measurable win, more than the *declaration* leg (FC1). For our project: prioritize a runtime guard / post-condition check over an elaborate input-schema declaration.

**Mapping to our project**: we have no daemon; we have markdown skills invoked by Claude. The only available enforcement points are (a) a pre-commit lint over `SKILL.md` + sidecar contract files, (b) a check at the start of a skill body that grep-asserts preconditions, (c) the orchestrator's own scan of `pending_feedback/`. Anything else (rolling deploys, version skew between agents) doesn't apply. We get the LangGraph-style "runtime guard at the producer→consumer seam" essentially for free if every consumer skill begins with a `pre_check.sh` that asserts the input artifact exists and matches a schema. **What we should NOT promise**: a static lint that catches FM-1.1 / FM-1.2. The LLM may still disobey a perfectly well-declared contract — that's why MAST keeps verification as its third category.

**Contradiction with file 08**: file 08 §3.1 lists `contract.yaml` as RECOMMENDED for the "first migration wave" but is ambiguous about when violations are caught. The deep-research evidence says: the lint is necessary but cheap; the load-bearing enforcement is the runtime pre-condition check. File 08 should be amended to require both, not just the sidecar declaration.

---

## Q2 — How do mature systems structure bidirectional (consumer→producer) feedback channels?

The strongest reference design here is **Microsoft Magentic** (the AutoGen-derived orchestration in Microsoft Agent Framework, [docs](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/magentic)). It exposes a typed request/response pair: `MagenticPlanReviewRequest` and `MagenticPlanReviewResponse`. The request carries `plan` (proposed work), `current_progress` (the progress ledger), and `is_stalled` (whether stall-detection triggered the replan). The reviewer responds by calling either `approve()` or `revise(feedback)`. Critical detail: the same channel handles both "the planner asked the human to confirm" and "stall detection triggered a replan" — there is no second channel for the latter. One typed message, one routing path, one `event_type` enum distinguishing `PLAN_CREATED`, `REPLANNED`, `PROGRESS_LEDGER_UPDATED`.

AutoGen's `HandoffMessage` ([Handoffs docs](https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/design-patterns/handoffs.html)) is the lower-level primitive: fields `source`, `target`, `content`, `type='HandoffMessage'`. A `HandoffTermination` event stops the team and waits for a human. When the human replies, the reply is also a `HandoffMessage` (with target set to the agent that requested input). So the human-channel and the agent-channel are *the same typed message* differing only by `target`. This is structurally identical to "revision_requests as a subfolder of pending_feedback" in our project — one queue, target field distinguishes routing.

CrewAI's pattern is weaker and more conventional: feedback flows through Task.context — Critic's task takes Producer's task output as `context`, and the Critic's "decision" is just parsed prose ([CrewAI hierarchical reflection](https://teetracker.medium.com/crewai-hierarchical-manager-build-reflection-enabled-agentic-flow-8255c8c414ec), [CrewAI agents](https://docs.crewai.com/en/concepts/agents)). The hierarchical-manager pattern adds a Manager agent that *decides* whether to re-dispatch to Producer. There is no schematized "revision request" — it is free-form text. The cost of this is plainly visible in MAST data: this is where FM-2.5 (Ignored other agent's input) and FM-2.6 (Reasoning-action mismatch) live. CrewAI's pattern would not satisfy our developer's transparency goal.

The Magentic pattern's HITL mode is the cleanest reference for *escalation* (autonomous → human-required): every plan-review pause is the same `MagenticPlanReviewRequest`, the workflow runtime parks on it via a checkpoint, and the same machinery resumes whether the human approved or revised. There is no separate "developer question" channel — the request *is* the channel, and the human is one valid responder among others. Translated to our file-based system: a single `pending_feedback/{TASK_ID}/` queue with a discriminator field `responder_required: human | skill | either` would mirror Magentic.

**Mapping to our project**: I recommend Magentic's pattern as the closest analog. The developer's round-6 reframing (revision_requests as a subfolder of pending_feedback, scanned by the same orchestrator) is structurally correct — the failure mode of two separate channels (orchestrator scans only one) is exactly the "silent handoff" failure documented by Maxim AI. A single queue with a target/responder discriminator is the proven pattern.

**Contradiction with file 08**: file 08 §3.4 ("bidirectional feedback as one channel or many") asked the question but did not settle it. Round-2 evidence: one channel, typed, with a responder discriminator.

Sources: [Magentic docs](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/magentic), [AutoGen Human-in-the-Loop](https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html), [AutoGen Handoffs](https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/design-patterns/handoffs.html), [CrewAI Reflection](https://teetracker.medium.com/crewai-hierarchical-manager-build-reflection-enabled-agentic-flow-8255c8c414ec).

---

## Q3 — Split into sub-modules vs keep as one with internal phases: what's the actual rubric?

**LangGraph** ([Subgraphs docs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs), [Scaling LangGraph](https://aipractitioner.substack.com/p/scaling-langgraph-agents-parallelization)) does not publish a hard rubric, but the design notes converge on three signals: (1) **shared state** — if parent and subgraph share state keys, the subgraph "reads from and writes to the same channels as the parent" and the integration is automatic; this argues for *keep together* because the split adds no isolation benefit; (2) **isolated state** — if the candidate subgraph needs its own private state (e.g. per-agent message history) the split *is* meaningful; (3) **independent development** — "as long as the subgraph interface (input/output schemas) is respected, the parent graph can be built without knowing any details" — this is purely an organizational driver, not a correctness one. A documented failure mode of premature splitting: parallel subgraphs that share state keys throw `InvalidUpdateError: Can receive only one value per step` even when the subgraph never touches the conflicting key ([issue #6446](https://github.com/langchain-ai/langgraph/issues/6446)). So a careless split actively breaks the system.

**CrewAI's "crew vs single agent"** rubric is cleaner ([Hermify blog](https://www.hermify.io/en/blog/hermes-agent-vs-crewai), [CrewAI Crews](https://docs.crewai.com/en/concepts/crews)). The decision is task-shape, not size: **discrete, task-shaped work with explicit role specialization → crew**; **relationship-shaped, ongoing work with shared memory → single agent**. The Hermify article warns *both* directions of over-decomposition: "If you find yourself splitting a single agent's skills into a fixed sequence of 'planner skill' and 'critic skill' that always call each other in the same order... you are rebuilding CrewAI inside an agent." The reverse warning: "If you find yourself bolting a 'user profile agent' and a 'memory agent' onto your CrewAI setup, you are reimplementing what an agent ships out of the box." Mismatching tool to problem creates expensive rework.

The unifying signal across both: **split when phases plausibly run independently, in different orders, or with different state**. Do NOT split when phases share intermediate state, always run in the same fixed sequence, or pass implicit (un-serializable) context between each other. This validates the developer's round-6 question about SCRIBBLE-SPLIT: a sub-skill that *only* spawns one agent has zero orchestration value — it's a wrapper, and the wrapper itself becomes a contract surface to maintain. The Hermify framing makes the answer explicit: if there is no fan-out (one agent, fixed sequence, shared state with the caller) the sub-skill is a "fake split."

**Concrete rubric synthesized for our project** (4 binary signals; split if 2+ are YES):

1. **Independent invocation?** Could this phase be invoked outside the parent flow without manufacturing context? (e.g. `ux-write-canon-concept` can be invoked alone — YES; a phase named "compute and store scribble version number" cannot — NO.)
2. **Fan-out to multiple agents?** Does the phase coordinate ≥2 agents that the parent doesn't already see? (Fan-out is real orchestration value; spawning one agent and waiting is not.)
3. **Natural human review point?** Is the boundary a place where a human would plausibly want to stop, approve, or hand off? (Phase 4→5 of scribble = YES; tokenizing a path = NO.)
4. **File-based artifact crossing the boundary?** Does the producer write a file and the consumer read it? Then the split is cheap — the file IS the contract. (In-memory state passing makes split expensive.)

Applying to the SCRIBBLE-SPLIT proposal from file 09 §7.1: `ui-scribble-generate` (1 agent, no fan-out, no natural review point, file-based) — 1/4 → **stay bundled or replace with an agent**. `ui-scribble-auto-review` (3 agents, fan-out, natural review point, file-based) — 3/4 → **split**. `ui-scribble-feedback-classify` (multi-agent classification, fan-out, file-based) — 3/4 → **split**. `ui-scribble-approve-handoff` (1 agent, no fan-out, but IS a natural review point, file-based) — 2/4 → **borderline; lean split because the handoff is itself the contract**.

**Contradiction with file 08**: file 08 §3.5 proposed the rubric live in `claude-create-skill`. Round-2 evidence (Hermify's bidirectional warning) suggests the rubric belongs in *both* `claude-create-skill` (when authoring) AND `claude-modify-skill` (when an existing skill grows past it). It's a recurring check, not a one-shot.

Sources: [LangGraph Subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs), [Scaling LangGraph](https://aipractitioner.substack.com/p/scaling-langgraph-agents-parallelization), [LangGraph issue #6446](https://github.com/langchain-ai/langgraph/issues/6446), [Hermes Agent vs CrewAI](https://www.hermify.io/en/blog/hermes-agent-vs-crewai), [CrewAI Crews docs](https://docs.crewai.com/en/concepts/crews).

---

## Q4 — PRINCE2 Product Description: actual fields, format of "quality criteria" and "derived from"

PRINCE2's Product Description is the closest project-management analog to a "skill output contract" — it predates software interface descriptions and was designed for non-technical reviewers. The canonical field set, confirmed across [PRINCE2 Wiki](https://prince2.wiki/management-products/baselines/product-description/), [Aspire Europe](https://www.aspireeurope.com/prince2-product-description.php), [Projex Academy](https://www.projex.com/prince2-7-product-description-template/), and [BlackScrum](https://blackscrum.com.au/index.php/pm-blog/a-prince2-project-product-description-template-and-explanation/):

| Field | Content |
|---|---|
| Identifier | Product name or unique ID |
| Title | Human-readable name |
| Purpose | How the product is used and by whom |
| Composition | List of components/parts |
| Derivation ("Derived from") | Source products this one depends on (design, existing system, prior product, statement of expected benefits) |
| Format and presentation | Output medium (PDF, document, spreadsheet, software module) |
| Development skills required | Skills needed to produce it |
| Quality criteria | Measurable acceptance tests |
| Quality tolerance | Acceptable variance bands |
| Quality method | How verification is performed (review, test, inspection) |
| Quality skills required | Skills needed to verify it |
| Quality responsibilities | Producer, reviewer, acceptance authority |

**Format of "Quality criteria"**: the sources are unanimous that quality criteria must be *measurable* — PRINCE2 explicitly rejects "easy to use" in favor of "task X completable in N steps by user with role Y." In practice, the criteria appear as **a list of measurable acceptance bullets**, sometimes with a paired tolerance column. The PRINCE2 Wiki frames the check: "You will need to be able to measure quality criteria or you cannot determine whether the product meets them." This is structurally identical to our `Acceptance Criteria` block in `goal.md` — and our existing AC-XX format already satisfies the PRINCE2 measurable-criteria rule. We are not inventing anything; we are aligning with a 30-year-old project-management standard.

**Format of "Derived from"**: this field is a *list of upstream products*, not free-form prose. Examples given: "the design from stage N", "the existing CRM system", "the benefits statement from the Business Case." Translated to our system: this is the `inputs.required` and `inputs.optional` block from file 08 §3.1's `contract.yaml` proposal. The PRINCE2 vocabulary suggests a small structural improvement: rename `inputs:` to `derived_from:` and the meaning lands closer to what reviewers actually look for. (Bikeshedding — `inputs:` is fine too.)

**Difference between Composition and Derivation**: Composition is the *parts of the product itself* (its own internal structure); Derivation is the *upstream products it depends on*. For a skill, Composition = the files/sections inside the skill output (e.g. for `ui-create-scribble`: index.html, NN_*.html, metadata.yaml, feedback.md, flutter_handoff.yaml). Derivation = upstream files the skill reads (requirements.md, flow.md, optional sketches).

**Verdict on whether PRINCE2 is realistic for our project**: yes, but only as *vocabulary*. The full 12-field PRINCE2 form is overkill — most fields collapse for a software skill (Quality skills required, Quality responsibilities, Development skills required all default to "Claude with this skill loaded"). The fields that survive translation and add real value: Purpose, Composition (outputs), Derivation (inputs), Quality criteria (acceptance tests). That is exactly 4 fields, matching the minimum contract surface in file 08 §3.1. File 08 had the right structure; PRINCE2 confirms it from an independent tradition.

**No contradiction with file 08**, but a clarification: file-12 §1 hesitated on PRINCE2 as "too heavy." Round-2 evidence: the 4-field subset *is* light, and the existing AC-XX block already covers Quality criteria. PRINCE2 is best read as a sanity check that we are not over-engineering, not as a template to import wholesale.

Sources: [PRINCE2 Wiki](https://prince2.wiki/management-products/baselines/product-description/), [Aspire Europe](https://www.aspireeurope.com/prince2-product-description.php), [Projex Academy Part 1](https://www.projex.com/prince2-7-product-description-template/), [Projex Academy Part 2](https://www.projex.com/prince2-7-product-description-template-part-2/), [BlackScrum](https://blackscrum.com.au/index.php/pm-blog/a-prince2-project-product-description-template-and-explanation/).

---

## Q5 — Anthropic Agent Skills: progressive-disclosure tensions with a heavy contract format

The canonical Anthropic source is the [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) and the [Best practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). The most load-bearing facts for our design:

**Limits** (these are hard from Anthropic):
- `name` ≤ 64 chars, lowercase letters/numbers/hyphens only, no XML, no reserved words ("anthropic", "claude")
- `description` ≤ 1024 chars, non-empty, no XML — *this is the only thing always in the system prompt*
- **SKILL.md body recommended under 500 lines** for performance
- Three-level loading model: L1 metadata (always, ~100 tokens), L2 SKILL.md body (when triggered, under 5k tokens recommended), L3 referenced files (on demand, effectively unlimited)
- **Avoid nested references deeper than one level** — Claude partial-reads files when reached transitively, using `head -100` previews; nested-link chains lose information

**Anti-patterns Anthropic explicitly warns about** (Best practices §"Anti-patterns to avoid" and adjacent sections):
1. Windows-style paths
2. **Offering too many options** (gives concrete bad example: "you can use pypdf, or pdfplumber, or PyMuPDF...")
3. Verbose prose explaining what Claude already knows ("default assumption: Claude is already very smart")
4. Time-sensitive information that goes stale
5. Inconsistent terminology
6. Magic-number constants ("voodoo constants" — Ousterhout)
7. Punting to Claude in scripts (handle errors explicitly, don't `return open(path).read()` and let the model figure out the FileNotFoundError)

**Tension with a heavy contract format**: Anthropic does NOT discuss skill-to-skill contracts. The doc treats skills as standalone capabilities, not as nodes in a graph. The composability claim ("Compose capabilities: Combine Skills to build complex workflows") is asserted but not specified — there is no Anthropic-blessed format for how skills declare what they invoke or expect. **This is a gap, not a prohibition.** Our `contract.yaml` sidecar lives in level 3 (loaded on demand, zero startup cost) and respects all three levels of progressive disclosure. The relevant Anthropic rule it has to respect: contract.yaml must not be required reading for the skill to function — it's metadata for the lint, not for Claude at runtime. If Claude needs the contract at runtime, that content has to migrate up to SKILL.md body and contend with the 500-line ceiling.

**The Anthropic anti-pattern that contracts could trigger**: "Offering too many options." A bloated contract with 20 optional fields, multiple alternative schemas, conditional outputs — this is exactly the kind of cognitive load Anthropic warns against. The mitigation is to keep contract.yaml's *visible-to-Claude* surface (anything imported into SKILL.md) flat and short — say, just a `derived_from:` and `produces:` table. Everything else (full input schema, conditional outputs, side-effects) lives in the sidecar where the lint reads it and Claude never does.

**The Anthropic guidance that actively SUPPORTS contracts**: the "plan-validate-execute" pattern in Best practices §"Create verifiable intermediate outputs." Anthropic recommends having Claude write a plan in a structured format, validate it with a script, then execute. This is structurally identical to "skill emits handoff.yaml; downstream lint validates it; consumer skill reads it." Anthropic's own example validates `changes.json` before applying — a contract artifact between phases. So the contract.yaml + lint pattern is congruent with Anthropic's recommended pattern, just generalized one level up (across skills rather than within a skill).

**Mapping to our project**: keep contract.yaml as a sidecar (L3), do not surface it in SKILL.md body unless the skill body genuinely needs it. The lint reads it; Claude does not. This makes contracts a *zero-token* feature for routine skill invocations — they only cost tokens at lint time, never at runtime. This is the strongest argument for the sidecar approach over inline frontmatter.

**No contradiction with file 08**, but a sharpening: file 08 §3.1 said contract.yaml's "token cost is zero at skill-load time (Claude only loads SKILL.md)" — round 2 confirms this is exactly aligned with Anthropic's progressive-disclosure architecture and not a happy accident.

Sources: [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

---

## Q6 — OpenAI strict-mode: what does strictness actually cost?

OpenAI structured outputs in `strict: true` mode imposes a specific, hard set of constraints ([Digital Applied guide](https://www.digitalapplied.com/blog/openai-structured-outputs-complete-guide), [Daniel Saiz analysis](https://dsaiztc.com/blog/posts/navigating-openai-json-structured-outputs.html), [Firecrawl guide](https://www.firecrawl.dev/blog/using-structured-output-and-json-strict-mode-openai), [community discussion](https://community.openai.com/t/strict-true-and-required-fields/1131075)):

**Required**:
- `additionalProperties: false` on every object — model cannot return extra fields
- **Every property must appear in `required`** — no truly optional fields
- Cannot use `oneOf` at the root
- Cannot use `default:` values (API call fails)
- Cannot use `pattern`, `format`, `minLength`, `maxLength` and similar string constraints (silently ignored or rejected depending on version)
- Recursion depth bounded (~5–10 levels recommended)
- Max output ~16k tokens

**Workaround for "optional" fields**: use a union with `null` — `type: ["string", "null"]`. The field is always present in the response, just possibly null. This doubles down on rigidity: there is no concept of "field may be omitted"; only "field is present and may be null."

**Failure modes when misconfigured**:
1. Missing `additionalProperties: false` → explicit `400 BadRequestError` ("field is required to be supplied and to be false")
2. Missing `strict: true` (but using a schema) → **silent failure**: 200 OK with valid JSON but `parsed` attribute is `None`. The schema is ignored.

**Cost of strictness**: none of the sources reviewed quantify schema-compilation latency or token overhead. The community guide mentions schema is JIT-compiled on first request and cached, so subsequent calls don't pay the compile cost. The "cost" is mainly *authoring* and *expressiveness*: you give up `default`, `pattern`, `format`, optional fields, and root-level `oneOf`. You gain a guarantee that the response satisfies the structure.

**Mapping to our project**: full OpenAI strict-mode rigor is NOT what our contracts need. Our consumer is a Python lint and a human author, not a model that must generate JSON conforming to a schema. We benefit from:
- `additionalProperties: false`-style discipline (don't allow consumers to invent fields) — adopt
- Required field listing (every field a skill produces should be enumerated) — adopt
- Avoiding `pattern`/`format` exotica — irrelevant for us, our lint is simple regex/YAML-key checks
- The `null`-instead-of-optional workaround — actively REJECT. Our skills genuinely have optional outputs (e.g. `flutter_handoff.yaml` only on approval). A schema that forces "always present, may be null" forces every consumer to special-case nulls.

The right import from strict mode: **discipline (no extra fields, every produced field declared), but not the literal mechanism**. JSON Schema with `additionalProperties: false` is the right *shape*; strict-mode's required-everywhere rule is too rigid for file-based optional outputs.

**Contradiction with file 08**: file 08 §2 listed OpenAI strict mode as a pattern to import. Round 2 says: import its discipline, reject its "everything required" rule. Our schema dialect needs explicit `required: [...]` and `optional: [...]` blocks — strict-mode-style "required = the universe" doesn't fit file-based artifacts where presence/absence is itself a signal.

Sources: [Digital Applied](https://www.digitalapplied.com/blog/openai-structured-outputs-complete-guide), [Daniel Saiz](https://dsaiztc.com/blog/posts/navigating-openai-json-structured-outputs.html), [Firecrawl](https://www.firecrawl.dev/blog/using-structured-output-and-json-strict-mode-openai), [Community](https://community.openai.com/t/strict-true-and-required-fields/1131075).

---

## Q7 — Published failure stories where missing/loose contracts caused production bugs

The strongest empirical anchor is the **MAST paper** ([arxiv 2503.13657](https://arxiv.org/abs/2503.13657)). Methodology: 150+ multi-agent execution traces averaging 15,000 lines each, six expert annotators, three with full inter-annotator agreement at κ=0.88 on 15 traces; an LLM annotator validated agreement on the rest. The 14 failure modes are not "production incidents at named companies" — they are systematic patterns observed across five open-source MAS frameworks. The Future AGI extension cites the larger 1,600+ trace expansion: overall failure rates 41–86.7% across benchmarks, with FC1 (specification) at 41.8%, FC2 (inter-agent) at 36.9%, FC3 (verification) at 21.3%. Within FC3: premature termination 6.2%, incomplete verification 8.2%, incorrect verification 9.1%.

The MAST modes most directly tied to "missing/loose contracts":
- **FM-1.1 Disobey task specification** — agent ignored stated requirements (this is what well-declared contracts try to make harder to ignore, but cannot prevent)
- **FM-1.2 Disobey role specification** — agent acted outside its declared role
- **FM-1.4 Loss of conversation history** — context dropped between handoffs (no contract on what context the handoff carries)
- **FM-2.4 Information withholding** — producer agent didn't pass information the consumer needed (a contract on outputs catches this)
- **FM-2.5 Ignored other agent's input** — consumer didn't read what producer wrote
- **FM-3.2 No or incomplete verification** — no post-condition check

**Named production case study** ([Future AGI](https://futureagi.substack.com/p/why-do-multi-agent-llm-systems-fail)): **PwC reported a 7× accuracy improvement (10% → 70%)** after adding structured validation loops with judge agents to their CrewAI-based code-generation pipeline. This is the only company-named, numerically-supported, production-deployed case found in this research round. The improvement is attributed to *verification* (FC3 failures fixed), not to declared input contracts (FC1).

**The Maxim AI scenario** ([source](https://www.getmaxim.ai/articles/multi-agent-system-reliability-failure-patterns-root-causes-and-production-validation-strategies/)): the schema-evolution failure in a rolling enterprise deployment — "a routing agent deploys with enhanced routing metadata while downstream execution agents run the previous version." This is a real production-ops failure mode but is presented as a representative scenario, not a specific named incident.

**The "38% parsing failure" stat I expected to verify**: I could not find a primary source for this number in the search results. The Future AGI substack mentions parsing failures qualitatively but I did not corroborate the specific 38% figure that appeared in the first WebSearch summary. **Flag as unverified.**

**Bottom line for Q7**: there is no equivalent of the "Knight Capital $440M loss" postmortem for multi-agent contract failures. The empirical evidence is the MAST taxonomy (rigorous, systematic, not company-named) plus one named industry result (PwC, validation-loop driven, not contract-declaration driven). For our project: **the strongest case for contracts is the FC3-verification side (post-conditions, validation loops), not the FC1-declaration side**. PwC's 7× number argues for putting our heaviest investment in `verify-quality`-style post-condition checks at skill boundaries.

Sources: [MAST paper](https://arxiv.org/abs/2503.13657), [MAST HTML](https://arxiv.org/html/2503.13657v1), [Future AGI MAST analysis](https://futureagi.substack.com/p/why-do-multi-agent-llm-systems-fail), [Maxim AI failure patterns](https://www.getmaxim.ai/articles/multi-agent-system-reliability-failure-patterns-root-causes-and-production-validation-strategies/), [Redis multi-agent failures](https://redis.io/blog/why-multi-agent-llm-systems-fail/).

---

## Synthesis for our project

Distilled into concrete recommendations that respect our constraints (token budget, solo developer, file-based skills, no daemon):

1. **Adopt the sidecar `contract.yaml` (file 08 §3.1) — it's congruent with Anthropic's progressive-disclosure architecture.** L3 loading means zero startup cost. SKILL.md stays under 500 lines. The lint reads contract.yaml; Claude does not. This is the only mechanism that respects the developer's "transparency without token cost" requirement.

2. **Minimum contract surface: 4 fields, PRINCE2-aligned.** `derived_from:` (inputs), `produces:` (outputs/composition), `purpose:` (one-liner, already in SKILL.md description), `quality_criteria:` (the lint's pass conditions, structurally identical to the AC-XX block we already use). Resist the 12-field PRINCE2 form. Resist OpenAI's "every field required" — keep explicit `required:` and `optional:` sub-blocks because file presence/absence is itself a meaningful signal in our system.

3. **Enforce at two seams, not one. Lint at commit, runtime pre-check at skill entry.** The MAST data (41.8% FC1 + 21.3% FC3) shows that declaration alone leaves the verification gap untouched. A 5-line bash pre-check at the top of every consumer skill (`test -f $artifact || exit 1`) is the cheap-and-effective version of "runtime guard." PwC's 7× number is the strongest empirical argument for the verification leg.

4. **Bidirectional feedback: one queue, typed, responder discriminator.** Mirror Magentic's `MagenticPlanReviewRequest` — `pending_feedback/{TASK_ID}/question.md` already exists; add a `responder_required: human | skill | either` field and a `revision_target:` field. Do NOT create a second `revision_requests/` channel — the orchestrator's "scan only pending_feedback" rule is the documented antidote to silent-handoff failure.

5. **Skill-vs-agent rubric (4 binary signals; split if 2+):**
   1. Independent invocation possible? 2. Fan-out to multiple agents? 3. Natural human review point? 4. File-based artifact crossing the boundary?
   Applied: `ui-scribble-generate` 1/4 → don't split. `ui-scribble-auto-review` 3/4 → split. `ui-scribble-feedback-classify` 3/4 → split. `ui-scribble-approve-handoff` 2/4 → borderline; lean split because the handoff IS the contract.

6. **Migration: opt-in by `contract_version`.** `contract_version: 0` = unmanaged (no lint enforcement). Skills migrate when touched. This is exactly LangGraph's "respect the subgraph interface" pattern translated to file-based skills. The lint enforces only what the contract declares — silence is permissive.

7. **What we should NOT promise.** The contract will NOT catch FM-1.1 / FM-1.2 (an LLM agent disobeying a perfectly-declared contract). The contract WILL NOT replace `doc/` guidelines for non-obvious code decisions. The lint catches drift, not disobedience. Be honest in the rollout doc about this asymmetry — overselling will erode the developer's trust in the mechanism.

8. **Two anti-patterns Anthropic specifically warns against, applied to contracts:** (a) "Offering too many options" — keep the contract surface flat; if you find yourself authoring conditional schemas or multiple alternative shapes, the skill probably needs splitting (see rubric #5). (b) "Punting" — the lint should report specific, actionable errors ("ui-create-scribble's `produces:` lists `flutter_handoff.yaml` but `ui-verify-flutter`'s `derived_from:` doesn't reference it"), not "contract mismatch detected somewhere." Vague errors lose the developer.

---

## What I couldn't find / What remains uncertain

- **Latency cost of OpenAI strict mode**: no source quantified the schema-compilation overhead or first-token latency penalty. The "JIT then cached" claim is plausible but unverified at the numerical level. For our use case this doesn't matter (we're not calling strict-mode APIs), but the project's heuristic of "quantify before adopting" warrants the caveat.

- **The "38% parsing failures in production agentic systems" stat** surfaced in the initial WebSearch result summary, but I could not corroborate it against a primary source in this research round. Treat as unverified industry color, not as evidence.

- **No company-named contract-failure postmortem analogous to financial-industry "Knight Capital" stories.** The closest are MAST's framework-level statistics and PwC's improvement-after-fix number. We are designing in a space where the rigorous evidence is taxonomic, not incident-based. This argues for *modest* contracts (don't over-engineer based on hypothetical failures) and for *iteration* (revise the contract format after observing real factory failures, like Anthropic's own "evaluation-driven development" recommendation).

- **PRINCE2 actual filled-out examples**: four of the six sources I fetched described the fields but did not show a literal completed Product Description in full. I had to triangulate the format. Anyone implementing this should grab a PRINCE2 7 practitioner manual for one concrete worked example.

- **AutoGen-Magentic's checkpoint serialization format for plan-review pauses** — I did not fetch this. The pattern (typed request, approve/revise responder, checkpoint-and-resume) is clear; the on-disk format may suggest a better serialization for our `pending_feedback/{TASK_ID}/question.md` than what we use today, but that is a refinement question for the prototype phase, not a blocker.

- **The LangGraph "InvalidUpdateError when subgraphs share state keys but don't write them"** ([issue #6446](https://github.com/langchain-ai/langgraph/issues/6446)) is open and unresolved as of the search date. This is a cautionary tale: even when you DO declare schemas, parallel decomposition can break in subtle ways. If we ever add parallel skill execution (which we don't today), we will hit the same class of bug. Note for future work.

- **Whether the developer's "improvement suggestions live in `factory/` folder" channel should merge or stay separate** (Seed 3 in the goal): the Magentic precedent suggests merge. I did not verify this against our actual `factory/` folder contents. Defer to the in-repo inventory in the prototype phase.

---

Agent ID: a1a8dd1bcf62ff115
