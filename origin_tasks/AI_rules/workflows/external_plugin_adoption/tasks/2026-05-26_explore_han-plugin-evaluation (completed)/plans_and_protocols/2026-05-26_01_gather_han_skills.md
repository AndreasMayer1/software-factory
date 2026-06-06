# Han Plugin — Distilled Skills and Philosophy Inventory

**Date gathered:** 2026-05-26
**Source:** github.com/testdouble/han (MIT license, by Test Double)
**Purpose:** Raw material for synthesis comparison against the Software Factory's skill set.

---

## Skills

Han has 20 skills grouped by purpose. Each skill is a `SKILL.md` file in `plugin/skills/<name>/`. Skills are project-agnostic by design — they discover project structure at runtime via `CLAUDE.md` or `project-discovery.md` rather than hardcoding paths or languages. None of the 20 skills hard-require a specific language; they adapt to whatever the codebase contains.

**Named agents referenced across skills (not an exhaustive agent list):**
`project-manager`, `junior-developer`, `adversarial-validator`, `evidence-based-investigator`, `adversarial-security-analyst`, `structural-analyst`, `behavioral-analyst`, `risk-analyst`, `software-architect`, `system-architect`, `concurrency-analyst`, `data-engineer`, `devops-engineer`, `test-engineer`, `edge-case-explorer`, `user-experience-designer`, `gap-analyzer`, `codebase-explorer`, `information-architect`, `content-auditor`, `project-scanner`, `research-analyst`.

---

### architectural-analysis

| Attribute | Detail |
|---|---|
| **Purpose** | Deep structural analysis of a specific module, directory, or feature area — coupling, data flow, concurrency, SOLID alignment, risk. |
| **Key workflow** | Size-classified fan-out: always dispatches a spine of `structural-analyst` + `behavioral-analyst` + `risk-analyst` + `software-architect`; adds signal-selected specialists in parallel (concurrency, security, data, devops, `system-architect`). Single pass, no iteration. Report rendered from a fixed template. Negative results ("this dimension is clean") are explicitly valuable and expected. |
| **Project-agnostic?** | Yes. Reads `CLAUDE.md` / `project-discovery.md` for context; adapts to any language. |
| **Agents spawned** | `structural-analyst`, `behavioral-analyst`, `risk-analyst`, `software-architect`, `system-architect` (signal-selected), `concurrency-analyst`, `adversarial-security-analyst`, `data-engineer`, `devops-engineer`, `codebase-explorer`. |

---

### architectural-decision-record

| Attribute | Detail |
|---|---|
| **Purpose** | Create, extract, or convert ADRs; update status of existing ADRs. |
| **Key workflow** | YAGNI gate is first-class: an ADR is only written when a concrete *forcing function* exists today (active decision, locked code path, regulation, customer commitment, incident). Without a forcing function the skill recommends deferral. When creating, launches `codebase-explorer` agents, then runs `software-architect` (or `system-architect`), `risk-analyst`, and `junior-developer` in parallel to stress-test the decision before writing. Discovers filename hierarchy taxonomy dynamically from existing ADR filenames rather than hardcoding it. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | `codebase-explorer`, `software-architect` or `system-architect`, `risk-analyst`, `junior-developer`. |

---

### code-review

| Attribute | Detail |
|---|---|
| **Purpose** | Comprehensive code review of a git branch, specified files, or directories. Local only — does not post to GitHub (that is `gh-pr-review`). |
| **Key workflow** | Size-classified (small/medium/large) roster of specialist agents; finding caps (30 manual + 30 agent findings). Severity calibrated to size band. YAGNI findings are a *separate non-correcting class* — listed in their own `### 🟡 YAGNI` section, never under CRIT/WARN/SUGG, and explicitly advisory ("will not be corrected unless explicitly requested"). Project-pattern deference: a pattern consistent within the project is not a finding. Automated tool boundary: if a linter/formatter covers it, the review skips it. |
| **Project-agnostic?** | Yes. Uses `detect-review-context.sh` script for git detection. Adapts to any tech stack. |
| **Agents spawned** | `junior-developer`, `adversarial-security-analyst`, `test-engineer`, `edge-case-explorer`, `structural-analyst`, `behavioral-analyst`, `concurrency-analyst`, `data-engineer`, `devops-engineer` (all conditional on signal + size). |

---

### coding-standard

| Attribute | Detail |
|---|---|
| **Purpose** | Create, convert, or update coding standard documents. |
| **Key workflow** | Three modes: creating new (status=`proposed`), converting existing doc (status=`accepted`), updating existing. Before writing, evaluates whether the standard should be automated tooling instead (linters, formatters). YAGNI check: a standard is only worth writing when the project *already uses* the pattern and inconsistency is causing real friction. Creates per-file-type index files under `.claude/rules/coding-standards/` so standards are loaded on-demand via path-scoped rules rather than always in context. Runs an Adoption-Bias Audit (6 checks) and adversarial review (junior-developer + information-architect) before finalizing. |
| **Project-agnostic?** | Yes. Discovers filename taxonomy and file-type globs dynamically. |
| **Agents spawned** | Two parallel `codebase-explorer` agents (implementation patterns; existing standards/ADRs), `junior-developer` (adversarial review), `information-architect` (findability audit). |

---

### gap-analysis

| Attribute | Detail |
|---|---|
| **Purpose** | Compare two artifacts (current state vs. desired state) and produce a plain-language report with stable `G-NNN` gap IDs. |
| **Key workflow** | Delegates primary analysis to the `gap-analyzer` agent, which writes its output to a file. Then runs a validator-and-augmenter swarm by default (opt-out with `no swarm`). Distinctive: `junior-developer` runs an *actor-perspective sweep* — for every gap it checks whether the gap holds for every actor type (human users, API callers, AI agents, batch processes, etc.), not just the obvious one. Conditional second round if swarm surfaces ≥3 new gaps or contradicts ≥20% of analyzer gaps. Plain language in Sections 1–2 (no file paths, no identifiers); technical details quarantined to optional Section 3. |
| **Project-agnostic?** | Yes. Works on any pair of artifacts (docs, code, specs, PRDs). |
| **Agents spawned** | `gap-analyzer`, `adversarial-validator`, `junior-developer` (actor sweep), `evidence-based-investigator`, `project-manager` (medium/large only), domain specialists by signal. |

---

### gh-pr-review

| Attribute | Detail |
|---|---|
| **Purpose** | Run a full code review and post findings as PR comments to GitHub. Requires `gh` CLI. |
| **Key workflow** | Invokes the `code-review` skill first, then offers to post to GitHub. Before posting, runs `junior-developer` as a "clarity pass" on the draft review body itself — checking wording, severity assignments, and evidence-basis before the text is publicly visible. Handles self-authored PRs (posts as PR comment, not formal review, since GitHub rejects formal reviews from the PR author). |
| **Project-agnostic?** | No — requires `gh` CLI and GitHub PRs. |
| **Agents spawned** | (via `code-review`) + `junior-developer` for clarity pass. |

---

### investigate

| Attribute | Detail |
|---|---|
| **Purpose** | Evidence-based root cause investigation of bugs, failures, and integration issues. |
| **Key workflow** | Always dispatches ≥2 `evidence-based-investigator` agents in parallel from different angles (error path, data flow). Conditionally adds specialist agents (`concurrency-analyst`, `behavioral-analyst`, `data-engineer`) based on symptom classification. Evidence compiles into an E-series numbered list. Then `adversarial-validator` challenges evidence, proposed fix, and assumptions before the fix is accepted. Produces a plan file (problem statement → evidence summary → root cause → planned fix) for user approval before implementation. "Trace backward from symptoms — don't guess, follow the code." |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | ≥2 `evidence-based-investigator`, `concurrency-analyst`, `behavioral-analyst`, `data-engineer` (conditional), `adversarial-validator`. |

---

### issue-triage

| Attribute | Detail |
|---|---|
| **Purpose** | Convert a vague or incomplete bug/issue report into a structured triage document that names what is known, what is missing, and what to do next. |
| **Key workflow** | Strictly evidence-bounded: "Work only from what the reporter wrote. Do not infer facts that are not stated." Classifies issue type (Bug/Regression/Performance/Security/Feature Request/Question/Other), extracts known facts, lists missing information, assesses severity and reproducibility (marks Unknown when not inferable), identifies suspected system areas using `project-discovery.md` only to sharpen areas the report already points to. Recommends exactly one next han skill or "clarify with reporter." No agents spawned — this is a lightweight, deterministic skill. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | None. |

---

### iterative-plan-review

| Attribute | Detail |
|---|---|
| **Purpose** | Sharpen and stress-test an existing plan file through multiple codebase-grounded review passes, editing the plan in place. |
| **Key workflow** | Produces three cross-referenced files: the plan (edited in place), `artifacts/review-findings.md`, and `artifacts/review-iteration-history.md`. YAGNI is "a first-class review pillar" alongside correctness, completeness, and risk — every plan item is checked against the evidence test. All challenges must be grounded in codebase evidence ("The API handler at src/api/handler.go:47 returns XML, not JSON" is actionable; "This assumes the API returns JSON" is not). Round cap scales with size. No inline `(F#)` markers in plan sentences — forward traceability lives in the findings file. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | Specialist reviewers by signal (structural, behavioral, security, data, devops, test, edge-case, concurrency) + `project-manager` at medium/large. |

---

### plan-a-feature

| Attribute | Detail |
|---|---|
| **Purpose** | Produce a behavioral feature specification through a facilitated multi-agent team conversation. |
| **Key workflow** | Dispatches `project-manager` + `junior-developer` + 2–5 domain specialists sized to the feature. PM coordinates rounds of discussion; junior-developer stress-tests and reframes. Escalation to user only after evidence and reframing have both failed. YAGNI sweep runs before the spec is committed — speculative behaviors land in `## Deferred (YAGNI)`. Produces three cross-referenced files: `feature-specification.md`, `artifacts/decision-log.md`, `artifacts/team-findings.md`. Optionally a `feature-technical-notes.md` for committed T# mechanics. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | `project-manager`, `junior-developer`, and a signal-selected specialist roster (UX, security, devops, structural, behavioral, concurrency, architect, test, edge-case, data). |

---

### plan-a-phased-build

| Attribute | Detail |
|---|---|
| **Purpose** | Split any source of context (gap analysis, PRD, spec, conversation) into a sequence of independently demonstrable vertical-slice build phases. |
| **Key workflow** | Every phase must be *demonstrable to a real person* (something end-to-end the user can see), never a horizontal layer. Foundational phases come first only when truly required — and even then must be independently demoable. Plain language only: no file paths, function names, or library names in the output (only the "Source citations" section may reference heading names from source artifacts). Incrementally writes the file after each phase rather than buffering. IA agent reviews the rendered document for findability, scannability, and YAGNI compliance before presenting. |
| **Project-agnostic?** | Yes. Accepts any source context. |
| **Agents spawned** | `information-architect` (review pass). All sub-agents run on sonnet model. |

---

### plan-implementation

| Attribute | Detail |
|---|---|
| **Purpose** | Build a feature implementation plan from an existing spec through a `project-manager`-led team conversation. |
| **Key workflow** | Reads feature spec, runs parallel specialist agents (domain-scoped briefs), aggregates findings *deterministically* per-round (not via PM per round — PM is reserved for final synthesis and gate-trip facilitation). A spec-maturity gate checks for ≥5 spec-level findings by ≥3 specialists or ≥2 T#-contradictions by ≥2 specialists — triggers a pause to sharpen the spec before implementing. YAGNI sweep (Step 7.5) runs before synthesis. PM writes three cross-referenced files: `feature-implementation-plan.md`, `artifacts/implementation-decision-log.md`, `artifacts/implementation-iteration-history.md`. Full/trivial decision classification — trivial decisions get one-line bullets, full decisions get structured entries with rejected alternatives. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | `project-manager` (synthesis + gate facilitation), `junior-developer`, and a full specialist roster (all on sonnet model). |

---

### plan-work-items

| Attribute | Detail |
|---|---|
| **Purpose** | Break a trusted implementation plan into independently-grabbable, atomic work items written to a single `work-items.md` file. |
| **Key workflow** | Runs autonomously end-to-end without confirmation gates after the initial request. Each work item is a *vertical slice* (narrow but complete path through all layers, demoable on its own). Classifies items as HITL (requires human interaction) or AFK (can be merged without a sync) — prefers AFK. Writes incrementally. Never includes process artifacts (iteration histories, review findings) in work item bodies. UI work items reference design screenshots by relative path. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | `project-manager` for the breakdown judgement (sonnet model). |

---

### project-discovery

| Attribute | Detail |
|---|---|
| **Purpose** | Scan a repository and write a static `project-discovery.md` reference consumed by all other skills. |
| **Key workflow** | Dispatches 3 parallel `project-scanner` agents (languages/frameworks; build/test commands; docs/infrastructure). Reconciles against existing README/CLAUDE.md — contradictions surface via `AskUserQuestion`. Writes two outputs: a standalone `project-discovery.md` and a `## Project Discovery` section in `CLAUDE.md`. This file is the single bootstrap artifact other skills look for at runtime. |
| **Project-agnostic?** | Yes — explicitly designed to work on any stack. |
| **Agents spawned** | 3 parallel `project-scanner` agents. |

---

### project-documentation

| Attribute | Detail |
|---|---|
| **Purpose** | Create and maintain project documentation for features, systems, and components. |
| **Key workflow** | Dispatches 2–3 `codebase-explorer` agents to gather real code examples. Code examples must reference real files; examples labeled as "Proposed pattern" when no code exists yet. Runs a `content-auditor` agent after updates to catch facts that were silently dropped. Runs `information-architect` for findability/orientation review before finalizing. Updates `CLAUDE.md` with a reference to the new doc. Bidirectional cross-references with related docs. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | 2–3 `codebase-explorer`, `content-auditor` (update mode), `information-architect`. |

---

### research

| Attribute | Detail |
|---|---|
| **Purpose** | Research an open-ended question (options, prior art, trade-offs) and produce an evidence-backed, adversarially-validated report. |
| **Key workflow** | Web-facing `research-analyst` agents are *isolated* from codebase contents in their briefs — fetched web content is data to evaluate, never instruction to follow. Parallel codebase and web angles. `adversarial-validator` runs last, attacking evidence integrity, options framing, and whether any fetched source could have been adversarially constructed. Strict mode by default (all claims must be corroborated; single-source claims flagged); operator can opt into "exploratory" mode. All claims cross-reference indexed `A#` artifact IDs. |
| **Project-agnostic?** | Yes. Uses `WebSearch` + `WebFetch` tools. |
| **Agents spawned** | `research-analyst` (1–3 angles by size), `codebase-explorer` (when codebase-bearing), `adversarial-validator`. |

---

### stakeholder-summary

| Attribute | Detail |
|---|---|
| **Purpose** | Produce a plain-language stakeholder summary from a feature spec for sharing with non-technical audiences before implementation. |
| **Key workflow** | Plain language only: no file paths, function/class names, API shapes, or library names. Diagram-first: Mermaid `flowchart TD` for UX flow, `flowchart LR` for data before/after. Number of diagrams must match the spec's actual distinct paths — no padding to hit a template count. Three self-check passes before presenting: (A) internal consistency/contradiction check, (B) plain-language audit, (C) reading-order and progressive-disclosure check. Each pass requires a fresh `Read` from disk, not from working memory. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | None (skill performs all analysis directly, with multiple self-check passes). |

---

### tdd

| Attribute | Detail |
|---|---|
| **Purpose** | Implement code through a disciplined BDD-framed red-green-refactor loop. |
| **Key workflow** | The observed-failure gate is described as "load-bearing" — no production code until a test has been run and *observed* to fail for the intended reason. Tests name observable behaviors, not implementation details. Refactor step is non-skippable: either something is changed or the skill explicitly states "no duplication, structure, or standards issue this cycle." YAGNI governs the refactor step and the test list: speculative structure added "for flexibility" during refactor is a YAGNI candidate. One behavior at a time. References `references/failure-modes.md` to catch the specific ways an agent fakes TDD. Runs autonomously after the initial request — no confirmation gate unless the user explicitly requests a plan review before implementation. |
| **Project-agnostic?** | Yes. Supports Node/npm/pnpm/yarn, Python/pytest, Go, Rust/cargo, Ruby/bundle/rake. |
| **Agents spawned** | None in the main loop (the skill itself writes code). |

---

### test-planning

| Attribute | Detail |
|---|---|
| **Purpose** | Produce a standalone test plan document by analyzing code for coverage gaps and edge cases. Does not write test code. |
| **Key workflow** | Always dispatches `test-engineer` + `edge-case-explorer`. Conditionally adds `concurrency-analyst` (when code touches async/threads) and `adversarial-security-analyst` (when code touches auth/input validation). YAGNI sweep in Step 3 demotes speculative tests to a `Deferred Tests` section: tests for non-existent code paths, hypothetical adversaries, symmetry-driven coverage, or where one behavioral test replaces several low-level tests. 40-item cap (security items exempt). Items get cross-referenced IDs (`TP-001 (from T3)`, etc.) for traceability. |
| **Project-agnostic?** | Yes. |
| **Agents spawned** | `test-engineer`, `edge-case-explorer`, `concurrency-analyst` (conditional), `adversarial-security-analyst` (conditional). |

---

### update-pr-description

| Attribute | Detail |
|---|---|
| **Purpose** | Generate a PR description for the current branch and optionally update it on GitHub via `gh` CLI. |
| **Key workflow** | Uses `junior-developer`'s "fresh-reviewer perspective" to write the description — the rationale being that writing as someone without full context naturally produces what a reviewer needs to see. Fixed section order: Summary (with bolded TL;DR sentence `**This PR <verb> <behavior>, so that <why>.**`) → What to look at first → How this was tested → Files of interest (max 5 entries) → Test scenario changes. Three passes of self-verification before displaying. Omits "How this was tested" for documentation-only PRs. Handles self-authored PR edge case same as `gh-pr-review`. |
| **Project-agnostic?** | Requires `gh` CLI for the update step; review generation works without it. |
| **Agents spawned** | `junior-developer`. |

---

### Plugin-maintenance skills (not deep-dived)

Two skills in `.claude/skills/` are for maintaining the han plugin itself:
- **han-release** — releases a new version of the han plugin.
- **han-update-documentation** — updates han's own documentation.

Neither is relevant to adopting han patterns in another project.

---

## Philosophy

Han's design is governed by five interlocking principles. The most important two are called out as "foundational mechanics."

---

### Concepts (docs/concepts.md)

**Core thesis:** Han is composed of exactly two kinds of things: *skills* (deterministic processes, like flowcharts) and *agents* (specialist personas with judgment, like teammates). The test: "could you draw the whole thing as a flowchart? If yes, it is a skill." / "does this require reasoning about context rather than following a script? If yes, it is an agent."

**Concrete rules/heuristics:**
- Skills dispatch agents for judgment-heavy subtasks; the skill orchestrates and folds findings back in.
- The two foundational mechanics are *Sizing* (how much review an artifact gets) and *YAGNI* (what survives the review).
- All sizing-aware skills classify work as small/medium/large *before* dispatching — default is always small.
- All artifact-producing skills and artifact-reviewing agents apply the YAGNI rule before committing items.
- Skills are always invocable directly by the user via a slash command; agents are typically dispatched by skills, though direct invocation is possible for narrow judgment requests.
- 20 skills, 22 agents in the plugin.

---

### YAGNI (docs/yagni.md + plugin/references/yagni-rule.md)

**Core thesis:** "Every line of code, every section of a spec, every runbook, every abstraction, every configuration knob, every observability hook is ongoing maintenance cost. It is also a pattern future agents will treat as load-bearing and copy." YAGNI is evidence-based, not absolute.

**Two gates:**
1. **Evidence test (Gate 1 — inclusion):** Any committed item must cite at least one piece of acceptable evidence: (a) user-described need, (b) named direct dependency, (c) existing production code path that breaks without it, (d) regulatory rule demonstrably in effect today, or (e) documented incident / real fired alert / measured metric. Hypotheticals do not qualify.
2. **Simpler-version test (Gate 2 — shape):** When evidence justifies inclusion, ask whether a strictly simpler version satisfies the same evidence. "A single function beats a class. A class beats a class hierarchy." If yes, the simpler version replaces the larger one.

**Default is defer, never drop:** Items failing the evidence test go to `## Deferred (YAGNI)` in the artifact with a named *reopen-when* trigger. They are never silently omitted.

**Named auto-flag anti-patterns (partial list):** "for future flexibility", "when we scale", "best practice says…", symmetry/completeness ("we have create, so we should have delete"), single-implementation interfaces, speculative config knobs, defensive code at trusted internal boundaries, observability for telemetry not yet flowing, runbooks for alerts that have never fired, SLOs for absent traffic, indexes for queries that don't run, tests for code paths that don't exist, ADRs without a forcing function, coding standards for patterns the project doesn't use yet, build phases justified only by roadmap completeness.

**User always wins:** YAGNI makes cost visible; the user can override any single item. The override is recorded with rationale.

**Applies across the plugin in two postures:** producing artifacts (spec, plan, code) and reviewing artifacts (code review, plan review, standard creation). Code review treats YAGNI findings as *advisory-only* — a separate section, not a blocker.

---

### Sizing (docs/sizing.md)

**Core thesis:** Every skill that dispatches a swarm classifies work as small/medium/large first, uses that classification to cap team size, iteration depth, and finding severity calibration. "Fewer agents producing higher-signal findings is the goal; quantity is not the metric."

**Concrete rules:**
- **Default is small.** Every sizing-aware skill starts at small and escalates only when a signal clearly requires it. Borderline signals stay at the smaller band.
- **Auto-classified with a `$size` override:** skills announce the chosen size and justification before dispatching ("Medium: 6 files touched, adds one index and a query for it"). The user can pass `small`/`medium`/`large` as the first argument.
- **Conservative by design:** under-dispatching is recoverable (re-run larger); over-dispatching is not.
- **Sizing is transparent:** always announced before agents are dispatched.
- Seven sizing-aware skills: `architectural-analysis`, `code-review`, `gap-analysis`, `iterative-plan-review`, `plan-a-feature`, `plan-implementation`, `research`.
- Small: minimum roster, round cap 1. Medium: modest team, round cap 2. Large: full signal-selected roster, round cap 3.

---

### Writing Voice (docs/writing-voice.md)

**Core thesis:** Han documents and skill outputs should match the project author's established voice: a "generous mentor, not lecturer" — plainspoken, direct second-person, physical-world analogies, non-hedging confidence. This applies to how skills format their output, not just blog posts.

**Concrete rules (most relevant to AI output):**
- Never use: "It's worth noting", "Importantly", "Let's dive in", "In today's fast-paced world", "leverage", "utilize", "empower", "robust", "showcase", "deep dive", "synergy", "pivotal", "paradigm shift", "spoiler alert", "Full stop.", the "Question? Answer." header pattern, "This isn't about X. It's about Y."
- Never use "actually" (implies the reader was wrong) or "just" (implies something is easy and can make readers feel insulted).
- No em-dash anywhere.
- Never replace direct "you" with generic third-person.
- Never invent a benefits list or marketing-flavored closing.
- Enthusiasm through concrete demonstration, not assertion.

---

### YAGNI Rule (plugin/references/yagni-rule.md)

**Core thesis:** The canonical runtime reference loaded by every YAGNI-aware skill and agent. Content is structurally identical to `docs/yagni.md` but framed as an operational directive rather than a concept explanation.

**Key additional framing:**
- "The bar for inclusion is 'we need this now and have evidence to prove it,' not 'we might want this someday.'"
- How to apply when *producing* artifacts: state evidence before committing, defer without evidence, apply simpler-version test.
- How to apply when *reviewing* artifacts: run evidence test per item, cite resolution path (missing evidence cited → keep; replace with simpler → replace; no evidence → defer).
- YAGNI candidates are "never silently dropped" — escalate to user with deferred trigger named.
- The `## Deferred (YAGNI)` section format is standardized: `### {item name}` / `**Why deferred:**` / `**Reopen when:**` / `**Source:**`. Section is omitted entirely when no items are deferred.

---

## Summary Observations for Synthesis

1. **Strict skill/agent separation:** han's taxonomy (skill = flowchart, agent = judgment) is more explicit and architecturally enforced than is typical in custom Claude Code setups. Each agent has a narrow domain and an explicit posture.

2. **YAGNI is a cross-cutting framework rule, not a suggestion:** It applies to specs, plans, code, ADRs, tests, coding standards, observability, and operational machinery — with the same two-gate evidence test in every context. The Software Factory has no equivalent systematic gate.

3. **Sizing is the dispatch lever:** The small/medium/large classification controls token cost, agent roster size, and finding calibration simultaneously. It is announced transparently before every dispatch and always defaults to the smallest band.

4. **Three-file cross-referenced output pattern:** Multiple planning skills produce three mutually cross-linked files (primary artifact + decision log + iteration history) with inline `([D-N](artifacts/...))` links. This creates a durable, auditable chain from decisions to plan claims to round history.

5. **Adversarial validation is structural, not optional:** The `adversarial-validator` agent runs as a required final step in `investigate`, `research`, and `gap-analysis`. In `plan-implementation` the spec-maturity gate automatically surfaces contradictions before they become implementation assumptions.

6. **Plain-language output layers:** `plan-a-phased-build`, `gap-analysis`, and `stakeholder-summary` all enforce a strict plain-language surface (no file paths, identifiers, or library names in the primary output sections), with technical detail quarantined to explicitly opt-in secondary sections. This is a deliberate design for multi-audience artifacts.
