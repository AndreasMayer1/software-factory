---
name: round_3_decisions_applied
description: Captures the user's answers to the round-3 question (R1–R6 confirmed; N-D-1 through N-D-6 answered) and records new directions opened by the same answer: .factory/ refactoring, web-search logging, and a round-4 trigger for additional inspirations.
created: 2026-05-16
type: decisions_log
author: claude-opus
session: 08e0c996-7fdf-4b10-abbe-15896c158562
references:
  - 2026-05-16_05_opus_synthesis_round3.md
  - automation/pending_feedback/TASK-PROC-006-02/question.md (answered inline)
---

# Round-3 Decisions Applied & New Inputs

## 1 — Confirmed reversals (R1–R6)

All six reversals from round-3 §1 are **confirmed** by the user inline in the
question file:

| ID | Decision | Status |
|---|---|---|
| R1 | OS memory abandoned; project-local state | **confirmed** |
| R2 | Blocked-task trigger removed | **confirmed** |
| R3 | Auto-block produced tasks — permanent default | **confirmed** |
| R4 | Bugfix-first is strict; no fairness rule | **confirmed** |
| R5 | Two-stage skill-change-first-use detection | **confirmed** |
| R6 | No memory entries for saturation; runs.tsv only | **confirmed** |

## 2 — New decisions resolved (N-D-1 through N-D-6)

### N-D-1 — Project-local state folder location

**Answer:** `.factory/optimize/` (NOT `automation/optimize/` as proposed in round-3).

**Additional direction from the user:**

> "our folder structure is a little mess... we would need a `.factory` folder and
> then also move the automation folder (and maybe also other folders and files to
> the `.factory` folder). that's a refactoring task (goal: move all files and
> folders that are only part of the software factory below `.factory`, but skip
> files/folders that need a specific location dictated by an external dependency
> (e.g. `.claude/CLAUDE.md`)). For this task you are working on: use
> `.factory/optimize/` — let's start to do it right."

**Consequences:**
- Every path in round-3 reading `automation/optimize/...` now reads `.factory/optimize/...`.
- A new refactoring task must be created (see §5 below): move factory-only files to `.factory/`, leave externally-dictated paths alone (`.claude/CLAUDE.md`, `.git/`, etc.).
- The claude-optimize implementation is **not blocked** by this refactor — it goes directly to `.factory/optimize/` from day one.

### N-D-2 — Audit skill name

**Answer:** `claude-optimize-audit`. Confirmed as proposed in round-3 §2.5.

### N-D-3 — Stage 1 vs Stage 2 timing

**Answer:** Ship Stage 1 immediately; queue Stage 2 as a separate task. Confirmed.

### N-D-4 — Web-research heuristics table

**Answer:** Keep the round-3 §2.3 table as-is. **Additional requirement:**

> "we should log somewhere if a web search was performed so that we can later
> analyze it."

This is a small but real new requirement. The web-search log lives at
`.factory/optimize/history/web_searches.tsv` (parallel to `runs.tsv`):

```
2026-05-20T10:32Z  TASK-PROC-NNN-XX  skill_body  bugfix  query="how do anthropic skills handle XYZ" hits=3 used=2
```

This file is appended by **the executor** of the task (e.g. `claude-modify-skill`), not by claude-optimize itself. The audit skill (§2.5) reads it to compute: per-dimension web-search frequency, and (after correlation with task outcomes) whether tasks-with-search outperform tasks-without — refining the round-3 §2.3 heuristics empirically over time.

This adds **IMPL-J** to the round-3 §7 impl backlog: instrument the executor skills (or `claude-log`) to write `web_searches.tsv` whenever a web search is performed.

### N-D-5 — Auto-block awaiting tag string

**Answer (from research, not user):** `awaiting: ["user-unblock"]`.

User wrote: *"well: research :D We have conventions, i think... if not: choose something that fits well without asking for approval."*

Research findings (grep across `requirements_tasks/`):

| Existing tag | Where used | Semantics |
|---|---|---|
| `[TASK-XXX]` / `[REQ-XXX]` | Most common | Blocked on a specific artifact in the system |
| `["user-decision"]` | `factory_quality/.../2026-04-22_explore_factory-quality-improvements` | A question has been asked; awaiting the answer |
| `["time"]` | `branding/app_naming/.../2026-02-08_explore_app_naming` | Blocked on natural time-passing |
| `["green-test-suite"]` | blocker file | Blocked on a system state |
| `["release 0.0.1 shipped"]` | calibration task | Blocked on a milestone |
| `["physical A40 attached on Windows host"]` | A40 baseline task | Blocked on an external condition |
| `["factory_stability_confirmation"]` | new-project skill | Blocked on a vague human-judgment milestone |

**Pattern**: descriptive lowercase-with-hyphens strings inside quotes are normal for human-gated blocks. `"user-decision"` already exists with the meaning "we asked, awaiting answer". To disambiguate from claude-optimize's case (the proposal IS the question; user must accept by unblocking), the cleanest tag is **`"user-unblock"`** — semantically distinct, follows the existing naming style, doesn't collide with any existing string.

**Decision:** Auto-blocked optimize-produced tasks use `awaiting: ["user-unblock"]`.

### N-D-6 — Commit audit reports

**Answer:** Yes, commit at `.factory/optimize/reports/<date>_audit.md`.

(Path adjusted from round-3's `automation/optimize/reports/` to `.factory/optimize/reports/` per N-D-1.)

## 3 — New user inputs requiring further synthesis

The user's answer file added three substantial inputs beyond confirming N-D-1
through N-D-6:

### Input A — Session-JSONL-in-database pattern

> "I additionally point to something I've read on reddit: there are people who
> store the complete session json files in databases for fast access and easy
> query. That can for example be done with hooks. not sure if that would help
> us. what do you think? formulate what exactly we would need and if yes: dig
> deeper, perform a web search for technologies."

**Why this matters:** Round-3 §3.2.2 / §1.4 / N-D-3 currently rest on a
chicken-and-egg around skill-change-first-use detection. The reason JSONL was
"forbidden" in rounds 1–3 was cost: each file is 100KB–1MB, reading even one
consumes context. **If those files were streamed into a queryable store**, the
"first use of skill X after commit Y" question becomes a sub-second indexed
query. The entire Stage 1 / Stage 2 split (R5) could collapse into a single
Stage 1 that's actually correct.

**Web research agent has been spawned to investigate** — see §4 below. The
findings will feed a round-4 synthesis.

### Input B — Kaizen GitHub project as prior art

> "Additionally I stumbled upon https://github.com/imadAttar/kaizen/tree/main not
> sure if it's good. but maybe it helps us for inspiration?"

Listed for the web research agent to investigate.

### Input C — Four general LLM-work principles (incorporate into design)

> "the work with llms should follow the principle a) use scripts over instructions
> for more determinism and token saving whenever possible b) save tokens whenever
> possible (short instructions, efficient work with as little rereading as
> possible, as little in claude.md as possible that means instructions just in
> time) c) force the llm to do things instead of just telling it to to it: use
> hooks to implement gates d) I'm sure there are many other things worth
> mentioning as general improvement advice (the web will probably reveal more)"

These are **factory-wide principles, not specific to claude-optimize.** They
will likely affect the round-4 design in concrete ways:

- **Principle (a) — scripts over instructions:** Reinforces round-3's
  monitor-script-based detection architecture (§2.2). The LLM step in
  claude-optimize is already minimal (consume events → pick one → produce one
  task). Round-4 should consider whether *more* of the skill body can be
  promoted to a script (e.g. tier-0 read aggregation, candidate scoring).
- **Principle (b) — token economy:** The claude-optimize skill body itself must
  be short. Tier-1 reads must be lazy. CLAUDE.md changes triggered by
  claude-optimize should be small and just-in-time.
- **Principle (c) — hooks as gates:** The monitor invocation is already piggybacked
  on `task-complete`. The auto-block default could be enforced by a pre-commit
  hook (refuse to commit a goal.md created by claude-optimize without
  `awaiting: ["user-unblock"]`). This is defense-in-depth on R3.
- **Principle (d) — more from the web:** Web research agent is gathering this.

These principles likely deserve their own requirement document (REQ-PROC-???),
since they apply across the factory, not just to claude-optimize. **A new task
to write that requirement is added to the impl backlog (IMPL-K below).**

## 4 — Web research agent status

A round-2 web research agent is running in the background, tasked with:

- **Q1.** Session-JSONL-in-DB pattern, technologies, real implementations
- **Q2.** Kaizen project review (architecture, what to steal/avoid)
- **Q3.** Additional general LLM-work principles beyond (a)/(b)/(c)
- **Q4.** Insights on round-3 §6 uncertainties (if time permits)

Output target:
`plans_and_protocols/2026-05-16_06_web_research_round2.md`

When it completes, a round-4 synthesis will integrate findings — this is the
appropriate next document.

## 5 — Refined impl backlog (delta from round-3 §7)

The user's answers re-shape the impl backlog. Here is the updated list:

| ID | What | Blocks on |
|---|---|---|
| IMPL-A | Rewrite REQ-PROC-006 per round-1 §16 + round-2 §E + round-3 §1.3/§2.1/§2.3 + round-4 (when produced) + the Input A finding (DB-or-not) | round-4 complete |
| IMPL-B | Build `.factory/optimize/` scaffolding (state.json schema, events/, README.md, history/runs.tsv, reports/, web_searches.tsv) | IMPL-A |
| IMPL-C | Build the monitor scripts (`scripts/optimize/monitor_*.py`) + orchestrator `scripts/optimize/run_monitors.py` | IMPL-B |
| IMPL-D | Build `scripts/optimize/create_optimize_task.py` with the auto-block `awaiting: ["user-unblock"]` default | IMPL-B |
| IMPL-E | Rewrite the `claude-optimize` skill body (event consumer + Tier 0/1 reads + task-create + commit) | IMPL-C, IMPL-D |
| IMPL-F | Wire `scripts/optimize/run_monitors.py` into `task-complete`'s tail end | IMPL-C |
| IMPL-G | Build the `claude-optimize-audit` skill (reads runs.tsv + web_searches.tsv + git, computes aggregates, writes report) | IMPL-E |
| IMPL-H | Instrument protocol logging with `skills_used:` — enables Stage 2 of `monitor_skill_change_first_use` | IMPL-C |
| IMPL-I | (Blocked) extend claude-optimize tier-0 sources to consume TASK-PROC-044's observability data | TASK-PROC-044-NN done |
| **IMPL-J (new)** | Instrument executor skills (or `claude-log`) to write `web_searches.tsv` when web search performed | IMPL-B |
| **IMPL-K (new)** | Write a REQ-PROC for cross-factory LLM-work principles (a/b/c + round-4 additions) | round-4 complete |
| **IMPL-L (new)** | Refactoring task: move factory-only files to `.factory/`; preserve externally-dictated paths | independent — can run anytime |

12 distinct tasks. Most have small concrete scopes.

## 6 — Status of TASK-PROC-006-02

This task **does not close yet.** The user's additional inputs (Input A, B, C)
require a round-4 synthesis after the web research returns. Once round-4 is in
place, the user's expected action is:

- Quick read of round-4
- Either: confirm with "ship the impl backlog as-is" → task closes via
  `task-complete`
- Or: another small clarification round if the JSONL-DB finding changes the
  architecture materially

The user explicitly authorized this: *"If there's something we can improve:
create an iteration 4 synthesis, I mean you also have other topics open from
iteration 3, so it's maybe worth it anyways."*

## 7 — What does NOT need to wait for round-4

The following work could begin immediately without round-4, but the impl
backlog (§5) keeps them blocked on REQ-PROC-006 anyway. Listing for clarity:

- IMPL-L (refactor to `.factory/`) is independent of everything else and could
  start now.
- IMPL-K (the cross-factory principles requirement) is loosely independent —
  round-4 may add to the principles list but the requirement skeleton could be
  drafted now.

Recommendation: leave both as tasks-to-be-created and let the standard
prioritization handle them.
