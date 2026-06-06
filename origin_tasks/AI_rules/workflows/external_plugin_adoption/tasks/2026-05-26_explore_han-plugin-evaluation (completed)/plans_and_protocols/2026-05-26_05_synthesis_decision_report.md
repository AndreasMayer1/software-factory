# han Plugin Adoption — Decision-Ready Synthesis Report

**Task:** TASK-PROC-055-01 · **Date:** 2026-05-26 · **Model:** Opus
**Inputs:** files 01 (han skills), 02 (han agents), 03 (web research), 04 (framework + our inventory)
**Subject:** github.com/testdouble/han (MIT, Test Double) — 20 skills, 22 agents

> This report is self-contained. A future implementer can act on it without re-reading
> the source material. It applies the reusable evaluation framework in file 04 Part B.

---

## 1. Bottom Line (recommendation first)

**Adopt han as inspiration, not as a dependency.** Port a small set of han's
*mechanics and ideas* into our own stable skills/agents; pilot at most one or two
self-contained specialist *agents* as frozen copies. **Do not** install the plugin,
**do not** track upstream, and **do not** replace any part of our pipeline/governance spine.

Three reasons drive this:

1. **The two systems are nearly orthogonal, not competing.** Our factory is a *vertical
   product pipeline + governance machine* (Persona→Scenario→Flow→Requirement→Task→Code,
   quality gates, stateful task lifecycle, release management, self-modification). Han
   is a *horizontal engineering-rigor toolkit* (planning, review, investigation, research,
   specialist analysis lenses). Han has essentially nothing on our spine; we are thin
   exactly where han is strong. The value is *complementary enrichment*, not replacement.

2. **Han is 15 days old with zero adoption track record.** 63 stars, no blog post, no HN/
   Reddit/X discussion, 8 releases in 15 days — one of which (v2.6.1) silently broke all
   20 skills. Copying/tracking ties us to a churning, unproven upstream and forces
   re-testing of established workflows. Inspirational porting carries none of that risk.

3. **Inspirational adoption has the lowest blast radius and zero attribution burden.**
   Re-authoring an idea inside our own gate-integrated skills means no upstream coupling,
   no skill→agent dependency drag, no name-collision risk, and no MIT obligation (MIT
   attaches to *copied text*, not to ideas).

---

## 2. Problem-Space Definition (what we now know that we didn't at task creation)

At task creation we framed this as "60 skills + 6 agents vs 20 skills + 22 agents — what
overlaps?" That framing was wrong in two ways:

**Surprise 1 — "22 agents" is a pool, not a team.** Han never runs 22 agents. Its skills
classify each job as small/medium/large and dispatch a *sized subset* (2–6), capped at 5
per team, gated by a "45%-of-optimal-quality" threshold before adding any agent. So the
real contrast is not "6 vs 22 agents" but "**6 broad always-individually-invoked agents**"
vs "**a 22-role pool governed by sizing economics**." Our economics live in CLAUDE.md prose
(cache rules, "don't over-spawn"); han's live in executable skill logic.

**Surprise 2 — the comparison is not skill-vs-skill; it is layer-vs-layer.** Mapping both
sides onto a capability taxonomy (file 04 B.2) shows the overlap is small and sits in one
band:

| Capability band | Our factory | Han | Verdict |
|---|---|---|---|
| **A. Planning** | architecture-advisor (single-pass plan), code-complex | plan-a-feature, plan-implementation, plan-a-phased-build, plan-work-items, iterative-plan-review | **Han far deeper** (multi-round, adversarial, rejected-alternatives logs) |
| **B. Review & critique** | quality-checker (doc-compliance), verify-quality (gates) | code-review, iterative-plan-review, adversarial-validator | **Gap**: we have no *correctness/adversarial* review, only conformance |
| **C. Investigation & research** | opus-advisor, Explore, code-bugfix | investigate, research, gap-analysis, evidence-based-investigator | **Han deeper** (evidence standard, adversarial validation step) |
| **D. Implementation** | implementation-engineer, code-simple/complex, code-test | tdd | **Overlap**; ours is stack-tuned (Flutter/doc-LAW) and superior for us |
| **E. Documentation & comms** | doc-update-guidelines, doc-split | project-documentation, stakeholder-summary, ADR, update-pr-description | **Partial**; ours is doc/-LAW-specific, theirs is generic |
| **F. Specialist analysis lenses** | *(none — 6 agents are broad)* | concurrency, edge-case, risk, security, data, devops, UX, structural, behavioral analysts | **Clear gap** — most selectively adoptable band |
| **G. Governance / quality gates** | 18+ blocking gates, verify-quality, back-pressure | coding-standard (advisory) | **We far deeper** — han has no enforcement |
| **H. Process orchestration** | requ-*, task-*, release-*, claude-autorun, dep graph | *(none)* | **We only** — han is stateless |
| **I. Product / user-needs modeling** | ux-*, personas, scenarios, flows, VCD | *(none)* | **We only** |

The headline: **han can only meaningfully enrich bands A, B, C, and F** — the
"engineering-rigor inside the task-execution stage" — and even there, mostly as ideas.
Bands G/H/I are our moat and han is empty there.

**Surprise 3 — han's two "foundational mechanics" are things we lack systematically.**
- **YAGNI two-gate evidence test** (Gate 1 inclusion: cite real evidence; Gate 2 shape:
  simpler version that satisfies the same evidence; default = *defer with a named
  reopen-trigger*, never silently drop). We have the *ethos* (CLAUDE.md "don't add features
  beyond the task") but no *gate* and no defer-with-trigger discipline.
- **Sizing announced before dispatch** controlling roster + iteration depth + finding
  severity together. We split code-simple/complex by file count informally; we never
  announce a size or calibrate iteration/severity to it.

---

## 3. Component-by-Component Map (han item → our equivalent → recommended level)

Adoption levels: **Full** (replace ours), **Selective** (copy+adapt+freeze), **Inspirational**
(port the idea into ours), **None**. Effort S/M/L. Re-test risk per file 04 B.3.

### 3.1 Han skills

| Han skill | Our nearest equivalent | Overlap | Recommended | Why |
|---|---|---|---|---|
| plan-a-feature | architecture-advisor + code-complex plan | partial | **Inspirational** | Port multi-round + rejected-alternatives; full copy drags PM/junior-dev agents |
| plan-implementation | code-complex planning | partial | **Inspirational** | Spec-maturity gate idea is valuable; copy would conflict with task lifecycle |
| iterative-plan-review | *(none)* | none | **Inspirational** (high value) | Add an adversarial plan-review pass to code-complex; biggest planning gap |
| plan-a-phased-build | release-plan + task-derive-from-requ | partial | **None** | Our release/package decomposition already owns this, pipeline-integrated |
| plan-work-items | task-derive-from-requ, task-create-code | partial | **None** | Our task derivation is deeper and dependency-graph aware |
| code-review | quality-checker + built-in /code-review | partial | **None** (copy) / **Inspirational** (ideas) | Copying risks silent collision with built-in `/code-review`; port YAGNI-as-advisory-section idea only |
| gap-analysis | requ-verify-flow-coverage (narrow) | partial | **Inspirational** | Port the 4-category gap taxonomy + actor-perspective sweep |
| investigate | code-bugfix, opus-advisor | partial | **Inspirational** | Port evidence-numbering + mandatory adversarial-validation step into code-bugfix |
| research | opus-advisor, claude-ask | partial | **Inspirational** | Port web-content-isolation + adversarial-validation-last into opus-advisor brief |
| architectural-analysis | architecture-advisor | partial | **Inspirational** | Port signal-selected specialist fan-out idea |
| architectural-decision-record | *(decisions/ ADRs ad-hoc)* | partial | **Inspirational** (low pri) | Port the "forcing-function" YAGNI gate for ADRs |
| coding-standard | doc-update-guidelines, doc/ | partial | **Inspirational** (low pri) | Port the Adoption-Bias Audit idea (prevents AI over-applying a standard) |
| tdd | code-test | full | **None** | Ours is Flutter/doc-testing-LAW specific and superior for us |
| test-planning | code-test planning | partial | **Inspirational** (low pri) | Port YAGNI "Deferred Tests" demotion |
| project-discovery / project-documentation | CLAUDE.md + doc/ | partial | **None** | We already have a richer bootstrap (CLAUDE.md is LAW) |
| stakeholder-summary | *(none)* | none | **None** (now) | No current audience need; revisit if we add non-technical stakeholders |
| issue-triage | code-bugfix intake | partial | **None** | Lightweight; our bugfix flow covers it |
| gh-pr-review / update-pr-description | *(none — we commit to develop)* | none | **None** | We have no PR workflow; built-in /review covers ad-hoc needs |
| han-release / han-update-documentation | *(plugin self-maintenance)* | n/a | **None** | Irrelevant outside han itself |

### 3.2 Han agents (band F is the selective-pilot zone)

| Han agent | Self-contained? | Fills a real gap? | Recommended |
|---|---|---|---|
| **adversarial-validator** (sonnet) | High (no skill dep) | Yes — we have no "disprove the plan/finding" role | **Selective pilot (top candidate)** or Inspirational |
| **gap-analyzer** (sonnet) | High (artifact-vs-artifact, accepts URLs) | Yes — generalizes requ-verify-flow-coverage | **Selective pilot** or Inspirational |
| **edge-case-explorer** (sonnet) | High | Partial — test-engineer could absorb the lens | **Inspirational** (fold into test-engineer) |
| **risk-analyst** (sonnet) | High (pure downstream synthesis) | Partial | **Inspirational** |
| concurrency / data / devops / system-architect analysts | High but niche | Low for a single-user Flutter app | **None** (now) |
| adversarial-security-analyst | High | Overlaps SP1–SP6 gates + /security-review | **Inspirational** (informs gates) |
| user-experience-designer | High | Overlaps ux-* + personas | **None** (ours is persona-grounded) |
| codebase-explorer / project-scanner | High | Overlaps Explore + CLAUDE.md | **None** |
| junior-developer | High (dual-mode) | Yes — "actor-perspective / hidden-assumptions" sweep | **Inspirational** (a powerful idea; fold into review) |
| project-manager / information-architect / content-auditor / behavioral / structural analyst | Medium | Low standalone | **None** (now) |

---

## 4. Adoption-Level Analysis (effort / risk per level)

### Full — REJECT categorically
Replacing our skills/agents with han's would discard bands G/H/I (our entire value), adopt
a stateless model incompatible with protocol.md/task-lifecycle, and depend on a 15-day-old
project. **Effort: XL. Re-test risk: catastrophic (every workflow). Recommendation: never.**

### Selective (copy + adapt + freeze specific files)
Viable only for self-contained, project-agnostic, high-value *agents* in band F. Rules if
chosen: (a) copy the agent file(s) **and freeze** — do not track upstream; (b) since some
skills reference agents by name, only copy items with **no han-skill dependency** (pure
agents qualify; skills do not); (c) **rename** to avoid collision with our/built-in names;
(d) add `THIRD_PARTY_NOTICES.md` at repo root with "Copyright 2026 Test Double, Inc." + MIT
text; (e) wire as an *optional* step in code-complex, behind explicit invocation.
**Best 1–2 candidates: adversarial-validator, gap-analyzer.**
**Effort: S–M per agent. Re-test risk: low-medium** (only the skills that call it).

### Inspirational (port ideas into our own skills) — PRIMARY RECOMMENDATION
Re-author the *mechanics* inside our stable, gate-integrated skills. Zero upstream coupling,
zero attribution burden, reversible via normal skill edits (claude-modify-skill).
**Effort: S–M per idea. Re-test risk: low** (text/skill changes; medium only where agent
dispatch behavior changes). Targets ranked in §5.

### None
GitHub-PR skills, plugin-maintenance skills, project-discovery (we have CLAUDE.md), tdd
(ours is better for us), niche analysts. **Effort: 0.**

---

## 5. Straightforward, Low-Risk Wins (ranked)

1. **YAGNI two-gate evidence test + defer-with-reopen-trigger** → port into `requ-explore`
   (AC inclusion), `task-derive-from-requ`, and `code-complex` planning. Pure skill-text
   change; complements our existing end-state-AC discipline. *Effort S, risk low.*
2. **Adversarial plan-review pass** → add a "challenge the plan against codebase evidence"
   step to `code-complex` (and optionally `requ-explore`), executed by a separate agent
   from the planner (honors self-evaluation-bias). *Effort M, risk low-medium* (changes
   code-complex flow → re-run 1–2 representative tasks).
3. **Explicit sizing announcement** → have multi-agent skills classify small/medium/large,
   announce it, and calibrate roster/iteration to it. Aligns with our CLAUDE.md cache
   economics. *Effort S–M, risk low.*
4. **Model-per-cognitive-profile** → audit our 6 agents + our subagent dispatch defaults
   (haiku=scan, sonnet=structured, opus=judgment). We already applied this here (gathering
   on sonnet). *Effort S, risk low.*
5. **Pilot ONE band-F agent** (adversarial-validator, frozen copy, renamed, optional in
   code-complex) to test whether an adversarial lens measurably improves our outputs.
   *Effort S, risk low, fully reversible.*

Lower priority: gap-taxonomy + actor-sweep into requ-verify-flow-coverage; three-file
decision-log/rejected-alternatives pattern in plans_and_protocols/; ADR forcing-function
gate; coding-standard Adoption-Bias Audit; writing-voice anti-slop list for doc/ authoring.

---

## 6. Re-Test Risk Flags

- **Any change to how `code-*` or `task-*` skills dispatch agents** touches the automation
  orchestrator (`claude-autorun`) and the quality-gate flow → re-run representative impl +
  bugfix tasks before trusting in automated mode. (Sizing change, added adversarial pass.)
- **Copying a han *skill*** that references built-in skill names (han `code-review` vs
  Claude Code's bundled `/code-review`) risks a confirmed silent-failure collision →
  avoid copying skills; prefer agents or inspirational ports.
- **Copying a han *agent*** referenced by a han skill without copying the skill is safe; the
  reverse (skill without its agents) silently degrades → always copy the full bundle or
  neither.

---

## 7. Licensing Practicalities (MIT)

- **Inspirational ports:** no obligation. MIT covers copied text, not ideas/mechanics.
- **Selective copies:** retain the copyright + permission notice. Practical approach:
  a single `THIRD_PARTY_NOTICES.md` at repo root ("Copyright 2026 Test Double, Inc." + the
  MIT permission text + list of adapted files). **No per-file headers required** for adapted
  files. **No obligation to publish** our modifications (internal, non-distributed use).
- Record the snapshot commit SHA of han we copied from, so a future audit can diff.

---

## 8. Honest Uncertainties

- **Zero external adoption signal** means we cannot lean on anyone's experience. Han's agent
  quality is asserted by its prompts, not proven in our context. Whether an adversarial
  lens or sizing actually improves *our* outputs (vs. adding ceremony) is **unknown until
  piloted** — "we don't know until we try" is the honest answer, which is exactly why the
  recommendation leads with a small reversible pilot rather than a broad rollout.
- **Upstream churn** (8 releases/15 days, a release that broke all skills) means any copied
  file is a point-in-time snapshot we own thereafter; we are not buying ongoing maintenance.
- We did **not** functionally execute any han skill/agent in our repo; this report is a
  document-level analysis. A pilot is required to convert assertions into evidence.

---

## 9. Decisions Requiring User Input (framed for a confident call)

1. **Adoption posture.** Confirm the recommended posture — *inspirational-first; pilot 1–2
   band-F agents as frozen copies; never full/never-track-upstream* — or choose a more
   aggressive selective-copy path despite the maturity risk.
2. **Author REQ-PROC-055 now?** `writes_requirements: true` and a `.reserve-REQ-PROC-055`
   marker exists. Proposed content: a **living process requirement** ("External Tooling /
   Plugin Adoption") whose body IS the reusable evaluation framework (file 04 Part B) plus
   the standing policy (inspirational-first, freeze-on-copy, THIRD_PARTY_NOTICES rule,
   built-in-name-collision avoidance, re-test gate). Write it this task, or keep this task
   report-only and author the requirement separately?
3. **Which ports to schedule, and priority.** From §5: (1) YAGNI gate, (2) adversarial
   plan-review, (3) sizing, (4) model-per-profile, (5) agent pilot. Which become follow-up
   impl tasks now?
4. **Pilot agent choice.** If piloting: adversarial-validator (challenge plans/findings) vs
   gap-analyzer (artifact-vs-artifact). Confirm the frozen-copy + rename + THIRD_PARTY_NOTICES
   approach is acceptable.
