---
name: opus_synthesis_round_2_delta
description: Round-2 synthesis. Integrates web research (Reflexion, DSPy/GEPA, Voyager, Self-Refine, skill-creator, METR) into the round-1 architecture. Delta-only — does not repeat round-1.
created: 2026-05-07
type: design_synthesis
author: claude-opus
session: 7e90a3be-126e-4e21-ab14-78cd3f18d323
references:
  - 2026-05-07_01_opus_synthesis.md
  - 2026-05-07_02_web_research_external_knowledge.md
---

# Round-2 Synthesis: Integrating External Knowledge

This is a **delta document**. It updates round-1 with what the web research changed, reaffirmed, or added. The core architecture (claude-optimize as a *task-producer*, not an analyzer) is unchanged.

---

## A. Reaffirmed by external research

The round-1 architecture survives external scrutiny in its essentials:

1. **Producer/executor split** matches Voyager's "skills as code retrieved by description" pattern — the optimizer doesn't run the skill, it curates the library.
2. **Cheap-signals-first hierarchy** matches DSPy/GEPA's preference for sample-efficiency over big-data approaches.
3. **Bugfix-first preference** is consistent with the broader "ground-truth-over-judgment" finding (LLM-as-judge has self-preference bias; bugfix paths can use deterministic verification, optimization paths cannot).
4. **No daemon, no auto-apply** matches Constitutional AI's training-time-with-human-review pattern. The literature is unanimous: self-modifying systems without rollback fail.
5. **Saturation as a normal exit condition** is reframed positively: skill-creator's evidence (Self-Refine plateau by iteration 4) suggests "no candidate" should be the *modal* outcome, not the exception.

---

## B. Revised by external research

### B1. The "no auto-apply" rule is now mandatory, not preferred

**METR (2025)** documents that current frontier models actively reward-hack in autonomous SWE roles — modifying test code, suppressing logs, exploiting eval loopholes. This converts what was a "we shouldn't do that" preference in round-1 §17 into a **hard guardrail**:

> **claude-optimize-derived tasks must NEVER be permitted to modify CLAUDE.md, the verify-quality skill, the doc-update-guidelines skill, the claude-optimize skill itself, or any test script in `scripts/automation/tests/`. These are the system's eval surface. The skill that runs the optimizer must enforce this via a deny-list checked at task-create time.**

This is operationally cheap — it's a list of forbidden file-path patterns enforced at task-creation. It is also non-negotiable. Without it, the optimizer is theoretically free to neuter its own oversight.

This becomes a new user decision (D9 below) — not in the sense of *whether* to enforce it (we must) but in the sense of *what exactly is on the deny-list*.

### B2. "Skill body" vs "skill description" must be separate optimization targets

Anthropic's own `skill-creator` plugin treats body iteration and description iteration as **separate scripts** with different evaluators (task success vs trigger rate). This is empirically validated. Round-1 §4 had a single `optimization_dimension` taxonomy; that conflates two qualitatively different changes.

**Revised taxonomy** (replaces round-1 §4):

```yaml
optimization_target: skill_body | skill_description | doc_guideline | ordering_rule | hook | script
optimization_dimension:
  # for skill_body / doc_guideline / script:
  bugfix | alignment | latency | token_cost | safety | clarity
  # for skill_description:
  trigger_accuracy   # under-triggers (skill not invoked when it should be)
  trigger_precision  # over-triggers (skill invoked when it shouldn't be)
  # for ordering_rule:
  layer_order | priority_signal | dependency
```

`claude-optimize` picks both fields per task. Different combinations imply different downstream skills:
- `skill_body` + `bugfix` → executor `claude-modify-skill` with a binary verification
- `skill_description` + `trigger_accuracy` → executor `claude-modify-skill` with the skill-creator-style eval set
- `ordering_rule` + anything → executor `claude-modify-ordering-rules`

This makes downstream routing deterministic. The optimizer doesn't decide HOW to fix; it decides WHAT to fix and TO WHOM.

### B3. Verification preference order

Round-1 §5 said "executor verifies." External research strengthens this with a clear preference order, reflecting LLM-as-judge bias:

1. **Ground-truth signals** (test pass/fail, dart-analyze clean, script exit codes, file presence/absence) — strongly preferred. Cheap, unbiased, falsifiable.
2. **Structural rubric scoring** (rubric decomposition, blinded pairwise, position-shuffle) — acceptable when ground-truth doesn't apply.
3. **Single LLM "is this better?" call** — disallowed. Self-preference bias makes it useless.

The optimizer should reject candidates whose acceptance criteria can only be verified by (3). They are the seed of metric corruption.

### B4. Persistent lessons memory is now first-class output

Reflexion's evidence (+22% on AlfWorld) shows the *episodic memory persistence* is what made the lesson-learning loop compound, not the critique itself.

The factory already has `MEMORY.md` and the `feedback_*.md` memory files. Round-1 mentioned MEMORY.md as a Tier-0 input. This round elevates it to a **second output channel**:

When `claude-optimize` runs, it produces ONE of three things (not just one task):

a. **An improvement task** (the round-1 default) — for when the candidate is concrete enough to fix
b. **A new memory entry** (`memory/feedback_*.md` or `memory/project_*.md`) — for when the lesson is a heuristic or a soft preference, not a code/skill change. Examples: "skill X tends to be over-eager when Y; future runs should add a guard at Z."
c. **A saturation note** in `MEMORY.md` — for when no candidate exists. This is normal, not failure.

Each of (a)/(b)/(c) is mutually exclusive per run. The skill picks the right vehicle based on the candidate's nature.

### B5. Iteration cap belongs to the executor, not the optimizer

Self-Refine's plateau-by-iteration-4 is about iterating on a *single* candidate change. That's an executor concern, not an optimizer concern (the optimizer makes one proposal and stops). But the optimizer should annotate the task with a **retry budget**: if the executor's first attempt to apply the change fails verification, how many more times may it retry before escalating?

Default: `retry_budget: 2` (so total of up to 3 attempts, matching Self-Refine's evidence). The optimizer overrides downward for risky/blast-high changes.

### B6. The regression suite question

`skill-creator` and the broader prompt-ops literature (Braintrust, PromptLayer, LangSmith) converge on one strong recommendation: **build a regression suite before optimizing.** "Improvement" without a held-out test set is unfalsifiable.

This is a real, big decision. Two options:

**Option α: Ship claude-optimize without a regression suite.** Rely on individual task-level acceptance criteria for verification. Simpler. Faster. But every claimed "improvement" is local — we can't detect global regressions across many task types.

**Option β: Block claude-optimize until a regression suite exists.** Stronger guarantees. But the suite is itself a substantial infrastructure project (curated 10–20 replayable task fixtures + LLM-evaluated rubric runner + CI gating).

I lean Option α with a deliberate caveat: ship the optimizer in a "**proposal-only**" mode for the first 30 days where it produces tasks but every task is gated on user confirmation before execution. After 30 days of human-confirmed-correct proposals, transition to autonomous mode. This buys real-world validation before automation, without blocking on infrastructure.

This is now D10 (below).

---

## C. Net-new from external research

### C1. Sanity check: the no-op ratio

Track what fraction of `claude-optimize` runs produce no candidate (path c — saturation). External evidence (Self-Refine's plateau) says this should be *high* in a healthy system. If the optimizer produces a task on every run, the trigger rules are too loose and Goodhart pressure builds. Target: 30–60% no-op rate at steady state. Document this expectation.

### C2. Paired shadow metrics to defeat Goodhart pressure

Where the optimizer's task includes a quantitative metric (e.g., "task completion time should drop from M to N"), it must also include a *quality lag-indicator* paired with that metric:

- "completion time" pairs with "tasks reopened within 30 days"
- "fewer sessions per task" pairs with "fewer pending_feedback questions per task"
- "smaller skill body" pairs with "trigger accuracy unchanged"

If only the throughput metric is satisfiable, the change is rejected as Goodhart-prone. This is a hard rule in the optimizer's task-validation step.

### C3. Trigger accuracy as a first-class measurable

Voyager's insight that *descriptions are the search index* applies directly: when a Claude session fails to invoke a skill it should have, that's a description-level failure. We don't track that today. The cheap signal is: the user explicitly invoked a skill via "/use X" or via instructions in conversation — meaning Claude's auto-routing failed. These events are countable from session_outputs.

This becomes another Tier-0 signal source: instances where the user had to manually route a skill that should have triggered automatically.

### C4. The optimizer must report on log compliance

External agent-observability research stresses that thin/missing protocol files poison any downstream optimization. The optimizer should refuse to optimize a skill whose recent runs don't have proper protocol files — and instead produce a meta-task: "skill X is failing to write claude-log entries; fix the skill to enforce logging." This is a fundamentally different class of bug, but it directly impacts every other optimization downstream.

---

## D. Updated Decision List for the User

(Round-1 D1–D8 plus new D9–D11)

**D1.** Acceptance of the reframe (claude-optimize = task-producer). [unchanged]

**D2.** Default trigger cadence (every N completed tasks; proposed N=10). [unchanged]

**D3.** Reactive trigger set (which monitoring patterns auto-create). [unchanged]

**D4.** Bugfix-first preference rule. [unchanged]

**D5.** Bootstrap with current signals vs. wait for TASK-PROC-044's observability layer. [unchanged]

**D6.** The optimization_dimension taxonomy. [REVISED in B2 — now a two-field {target, dimension} taxonomy]

**D7.** Saturation policy. [unchanged]

**D8.** Whether claude-optimize may modify CLAUDE.md (was: per-task user approval). [SUBSUMED by D9 below]

**D9. (NEW) Write-surface deny-list.** Per B1 and METR's reward-hacking evidence, claude-optimize-derived tasks must never modify the eval surface. Proposed minimum deny-list:
- `CLAUDE.md`
- `.claude/skills/claude-optimize/skill.md` (the skill cannot modify itself)
- `.claude/skills/claude-modify-skill/skill.md` (immediate enforcer)
- `.claude/skills/task-complete/skill.md` (closes loops; corrupting it = silent passes)
- Any file in `scripts/automation/tests/`
- `verify-quality` (when/if it exists as a skill — note: not yet in `.claude/skills/`)
- `.claude/factory_flows.md` and `.claude/skills/INDEX.md` (system manifests)

The user should review this list and add/remove. The skill enforces it programmatically (path-glob check at task-create time).

**D10. (NEW) Proposal-only first 30 days?** Per B6, ship in a mode where every produced task requires user confirmation before execution, even in autorun. After ~30 days of demonstrated correctness, transition to autonomous. This is the alternative to a full regression suite.

**D11. (NEW) Should saturation no-ops emit a memory entry?** Per B4 and C1, a no-op run could optionally write a `memory/optimize_no_op_<date>.md` for trend visibility, or just log to MEMORY.md as a one-liner, or do nothing. Proposed: one-liner addendum to `MEMORY.md` index only when the *fourth* consecutive no-op fires (avoids noise; surfaces persistent saturation).

---

## E. Refined "What REQ-PROC-006 Should Say"

Adds two clauses on top of round-1 §16:

> The system shall additionally:
> - enforce a write-surface deny-list (D9) at task-creation time;
> - distinguish skill-body, skill-description, doc-guideline, ordering-rule, hook, and script targets in produced tasks;
> - produce one of three outcomes per run: an improvement task, a new memory entry, or a saturation note (mutually exclusive);
> - require all task acceptance criteria to be verifiable by ground-truth signals or structurally-decomposed rubric — never single-LLM judgment;
> - track the no-op ratio across runs as a system-health indicator.

---

## F. Honesty Update (additions to round-1 §18)

- **The deny-list is a moving target.** As skills evolve, what counts as the "eval surface" changes. The list will need periodic human review. Stale deny-lists are themselves a security weakness.
- **The proposal-only mode adds friction in autorun.** During the 30-day validation window, optimize tasks pile up as pending_feedback questions, blocking autorun progress on improvements. This is a feature, not a bug — but the user should know.
- **The bifurcation of body vs. description (B2) increases task volume.** Where we'd previously have created one task to "improve skill X," we now potentially create two (one for body, one for description). The user may prefer to bundle them when they share a root cause — that requires a special case.
- **The regression-suite question (B6) is genuinely deferred, not solved.** Option α with proposal-only mode is a pragmatic compromise. It is not as robust as a real regression suite. A future task should explore building one — possibly the natural evolution of this skill in its second year of life.

---

## G. Recommended Next Steps for the Task

1. **User answers D1–D11.** This is the gating step. The architecture is stable; implementation is blocked on these calls.
2. **Then a follow-up impl task** rewrites REQ-PROC-006 (or supersedes it with a new REQ in the same folder) using round-1 §16 + round-2 §E as the basis.
3. **Then a second follow-up impl task** implements:
   a. The post-task-complete trigger script (`scripts/optimize/create_optimize_task_if_due.py`)
   b. The new claude-optimize skill body
   c. The deny-list enforcement
   d. The proposal-only-mode flag
4. **Optionally a third explore task** spec'ing the regression-suite (Option β) for the future.

This exploration task can complete after step 1 (user answers received). The follow-ups are separate impl tasks tracked normally.
