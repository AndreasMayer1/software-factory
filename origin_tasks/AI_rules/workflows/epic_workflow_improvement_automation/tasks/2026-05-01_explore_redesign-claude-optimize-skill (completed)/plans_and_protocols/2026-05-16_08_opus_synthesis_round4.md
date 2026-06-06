---
name: opus_synthesis_round_4
description: Round-4 synthesis. Answers the user's session-DB question (Input A), integrates the kaizen prior art (Input B) and the cross-factory LLM-work principles (Input C), and folds in the round-2 web research. Adds three new design elements: a self-improvement guardrails section, a deterministic audit scoring rubric, and a second (revert-rate) effectiveness metric.
created: 2026-05-16
type: design_synthesis
author: claude-opus
session: 08e0c996-7fdf-4b10-abbe-15896c158562
references:
  - 2026-05-07_01_opus_synthesis.md
  - 2026-05-07_03_opus_synthesis_round2.md
  - 2026-05-16_05_opus_synthesis_round3.md
  - 2026-05-16_06_web_research_round2.md
  - 2026-05-16_07_decisions_applied.md
---

# Round-4 Synthesis: Session-DB Verdict, Kaizen Lessons, Cross-Factory Principles

> Delta against rounds 1–3 and the round-3 decisions log. The core architecture
> (task-producer, event-driven monitors, `.factory/optimize/` state, auto-blocked
> proposals, separate audit skill) is unchanged. This round answers the three new
> inputs the user added in their round-3 answer, and folds in the round-2 web
> research (`..._06_web_research_round2.md`).

The round-2 web research came back unusually clean: it confirmed the round-3
architecture is consistent with current (2025–2026) practitioner consensus,
identified one concrete prior-art project (`kaizen`) to learn from, and surfaced
one genuinely new risk-mitigation requirement (self-improvement guardrails). Three
design elements are added; nothing from round-3 is reversed.

---

## Part 1 — Input A answered: should we store session JSONL in a database?

**Short answer: yes eventually, no for v1. It is a Phase-2 (v1.5) capability, not a
prerequisite.**

### 1.1 What the research found

Four real Claude Code → DB implementations exist today (all 2025–2026, all
single-developer-or-small-team, all local file-DBs, none cloud):

- **`disler/claude-code-hooks-multi-agent-observability`** — hooks POST 12 event
  types to a Bun server → SQLite(WAL) → live Vue dashboard. Pure hook-stream; no
  batch ingest of the raw JSONL.
- **`kuroko1t/claude-vault`** — single Rust binary, batch-archives
  `~/.claude/projects/**/*.jsonl` into SQLite + FTS5 full-text search. No
  structured skill-invocation index (FTS only).
- **`ek33450505/claude-code-dashboard` (CAST)** — the most elaborate: a 17-table
  schema (`quality_gates`, `hook_failures`, `completeness_events`, `incidents`, …)
  written by many hooks during the session.
- **`claude-mem`** — SQLite+FTS5 *and* a Chroma vector index, read back via MCP.

### 1.2 Why not for v1

Round-3's monitors do not need cross-session joins. Their queries are local: "how
many S9 questions in the last window mention substring X?", "did skill S see a
first use after edit E?", "any reversion on S within 48h?". These read the last N
session files, not a year of history. `runs.tsv` (append-only TSV) plus
`git log` covers v1 completely. Adding a database now means adding either a daemon
(a new failure mode the factory has no equivalent of) or an ingestion/migration
step (maintenance burden), for queries we don't yet run.

The research is explicit: *"keep `runs.tsv` as the only required persistence in
v1. Do not pull in a database."*

### 1.3 Where a DB does pay off — and the right technology

The payoff is exactly the `claude-optimize-audit` skill's cross-session analytics:
"user-unblock-rate per monitor over 30 days", "median time from trigger to user
action", "which merged improvement tasks were later reverted". For those, ad-hoc
`awk` over `runs.tsv` is brittle.

The recommended technology is **DuckDB**, used as a *query-time dependency only*:

```sql
-- one statement, no schema migration, no daemon
SELECT ...
FROM read_json_auto('<session-jsonl-glob>')
JOIN read_csv_auto('.factory/optimize/history/runs.tsv') USING (session_id)
WHERE ...
```

DuckDB reads raw JSONL directly (`read_json_auto`), so there is **no ETL and no
schema to maintain** — a real advantage given the JSONL schema is controlled
externally by Anthropic. If `duckdb` is not installed, the audit script prints the
install hint and degrades to `awk`/`git`; it never fails the factory.

**Decision (proposed, N-D-7):** defer DB to v1.5. When `claude-optimize-audit` is
built (IMPL-G), introduce DuckDB as an optional query-time tool. Do **not** copy
CAST's 17-table schema — most of those tables (`quality_gates`, `file_writes`)
duplicate sources of truth we already have (`cycle_state.json`, `git log --stat`).
Do **not** run a live observability server/dashboard — one developer, no team; the
dashboard would never be read and the daemon is pure downside.

### 1.4 The three-account caveat the research did not catch

There is a wrinkle specific to this factory that the web research could not know:
**the session JSONL files are per-account and not committed.** They live under
`/home/vscode/.ccs/shared/context-groups/default/projects/<project>/<uuid>.jsonl`
and per-account snapshot dirs. A DuckDB query over "the JSONL" sees only whatever
account's files are present on disk at query time.

Consequence for the audit skill: a DuckDB-over-JSONL query is **account-local and
best-effort**, not a complete cross-account history. The *authoritative*
cross-session record must remain `runs.tsv` (committed, shared across all three
accounts). The JSONL/DuckDB layer is an enrichment for the account you happen to
run the audit from, never the source of truth. Round-4 records this so the v1.5
implementer does not mistakenly treat the JSONL DB as canonical.

This same caveat is why the round-3 `skills_used:` instrumentation (IMPL-H) is
*still worth doing* even though DuckDB could in principle answer "first use of
skill X" by scanning JSONL: the instrumentation writes into the committed protocol
files (visible to all accounts), whereas a JSONL scan is account-local. The two are
complementary, not redundant.

---

## Part 2 — Input B applied: lessons from `kaizen`

`kaizen` (https://github.com/imadAttar/kaizen) is an on-demand Claude Code plugin
(`/kaizen:coach`) that audits and *rewrites* a Claude Code setup. It shares our
"continuous small improvements" philosophy but diverges sharply on *who decides*:
kaizen lets a slash command edit `CLAUDE.md`/rules directly; round-3 always routes
through a human-gated task. Given REQ-PROC-046 and our quality-gate culture, the
round-3 stance is correct and is reaffirmed.

### 2.1 Steal: the deterministic scoring rubric (new design element)

The single best idea in kaizen is a **deterministic N-point health rubric** with a
trend marker (↑ / ↓ / =) appended to a history file each run. Round-3's
`runs.tsv` lists raw events but offers no "is the factory getting healthier?"
glance value.

**Decision (proposed, N-D-8):** the `claude-optimize-audit` skill computes a
deterministic score per run and records it with a delta vs. the previous run in
`.factory/optimize/history/audit_history.tsv`:

```
2026-06-01T09:00Z  score=7/10  delta=+1  unblock_rate=0.62  revert_rate=0.08  notes="..."
```

The rubric is computed by the script (not LLM judgment), so it is reproducible.
A proposed starting rubric (10 points, refine later):

| # | Points | Criterion (computed from runs.tsv + git) |
|---|---|---|
| 1 | 1 | No-op rate is in the healthy 30–60% band (round-2 §C1) |
| 2 | 1 | User-unblock-rate in 50–80% band (round-3 §3.4) |
| 3 | 1 | Revert-rate of merged improvement tasks < 15% (Part 4) |
| 4 | 1 | Every produced task carried a verifiable acceptance criterion |
| 5 | 1 | No produced task targeted a deny-list path |
| 6 | 1 | Median trigger→unblock latency < 7 days (no proposal rot) |
| 7 | 1 | At least one High-confidence trigger fired in the window (system is observing) |
| 8 | 1 | No skill-change went > 30 days without a first-use signal (no dead edits) |
| 9 | 1 | claude-optimize skill body still under its token budget |
| 10 | 1 | All produced tasks were auto-blocked (guardrail intact — Part 3) |

The exact criteria are a starting point; the *mechanism* (deterministic score +
delta + trend) is the durable decision.

### 2.2 Steal: targeted sub-audits

Expose `claude-optimize-audit --monitor=<name>` so the developer can ask a focused
question ("how is the S9-repeat monitor doing?") without re-running the full audit.
Cheap to add; mirrors kaizen's `coach skills` / `coach hooks` split.

### 2.3 Steal (future, not v1): `discover` mode

kaizen's `discover` mines the codebase for *implicit* conventions not yet codified.
The analog here: scan recently merged tasks for repeated patterns not yet in any
skill. This is a strictly weaker, complementary signal to the round-3 triggers.
Parked in a "future enhancements" list — not v1.

### 2.4 Avoid (explicit non-goals, reaffirmed)

- **On-demand-only detection** (kaizen never fires unless you type the command) —
  our event-driven monitors + periodic safety net are the improvement.
- **Auto-applying changes** (`/kaizen:coach optimize` rewrites files directly) —
  breaks traceability and every quality invariant; round-3 already forbids it.
- **Free-form-markdown trend tracking** (`coach-history.md`) — not queryable; we
  use TSV/DuckDB instead.
- **One mega-command** that tempts "run it and pray" — our one-task-per-friction
  model keeps each change reviewable.

---

## Part 3 — New section: self-improvement guardrails (non-negotiable)

The research surfaced a sharpened version of the round-2 METR finding. A 2025
arXiv paper on audited skill-graph self-improvement
(https://arxiv.org/pdf/2512.23760) reports that *"once a model internalizes
reward-hacking patterns, even 'harmless' hacks generalize to unrelated
misalignment."* A self-improvement skill that an agent invokes **and** that
auto-applies changes is a textbook reward-hacking attractor.

Round-3's design already mitigates this, but the mitigations were scattered across
sections. Round-4 consolidates them into **three named invariants that no future
evolution of claude-optimize may remove**:

> **G-INV-1 — Produced tasks are auto-blocked.** Every task claude-optimize creates
> is born `awaiting: ["user-unblock"]`. The developer is always the gate between
> proposal and execution. (round-3 R3)
>
> **G-INV-2 — Detection runs outside any agent's tool surface.** The monitor scripts
> are plain Python invoked by `task-complete`; they are not tools the optimizing
> agent can call, shape, or suppress. An agent cannot make a monitor fire (or not
> fire) to influence its own perceived productivity.
>
> **G-INV-3 — Scoring is separated from production.** The `claude-optimize-audit`
> skill that computes the health score is a different skill from `claude-optimize`
> that produces tasks. The producing agent is never scored against a metric it can
> manipulate within the same run.

These three are added to REQ-PROC-006 as hard constraints (not goals), and the
round-3 deny-list (D9) remains as defense-in-depth on top. The "Honesty" sections
of earlier rounds flagged the deny-list as a moving target needing periodic human
review; G-INV-1 is what makes that acceptable — even a stale deny-list cannot cause
harm because nothing executes without the human unblock.

---

## Part 4 — New design element: a second effectiveness metric (revert-rate)

Round-3 §3.4 proposed **user-unblock-rate** as the north-star metric. The research
(DORA 2025's introduction of "rework rate" as a fifth metric, prompted by AI
assistants showing +21% tasks completed but +23.5% incident rate on AI-touched PRs)
argues that a single throughput-flavored metric is Goodhart-prone.

**Decision (proposed, N-D-9):** the audit skill tracks **two** metrics:

1. **User-unblock-rate** (primary, fast): of tasks claude-optimize produced, what
   fraction did the developer unblock? Measures engagement / calibration. Easy to
   compute from `runs.tsv` + goal.md `awaiting:` history.
2. **Revert-rate** (secondary, slow): of improvement tasks that were unblocked,
   completed, and committed, what fraction were reverted or substantially rewritten
   within N weeks? Measures whether improvements *stick*. Computed from `git log`
   over the changed files.

Unblock-rate alone measures "did the developer engage"; revert-rate measures "did
the change survive contact with reality". Together they match the "DORA + rework
rate" consensus. Revert-rate is computed on a slower cadence (e.g. quarterly) since
it needs a maturation window.

This pairs naturally with round-2 §C2 (paired shadow metrics): unblock-rate is the
throughput indicator, revert-rate is its quality lag-indicator.

---

## Part 5 — Input C: the cross-factory LLM-work principles

The user proposed three principles and predicted "the web will reveal more." It
did. These principles are **factory-wide**, not specific to claude-optimize — they
belong in their own requirement (IMPL-K). Round-4 records the full list with
sources so IMPL-K has a ready basis.

### The user's three (kept verbatim in intent)

- **(a) Scripts over instructions** — for determinism and token saving, whenever
  possible. *(Reinforces round-3's monitor-script architecture: the LLM step in
  claude-optimize is deliberately minimal — consume events, pick one, produce one
  task. Round-4 note: consider promoting candidate-scoring and tier-0 aggregation
  to scripts too.)*
- **(b) Save tokens** — short instructions, efficient work, minimal re-reading,
  as little in CLAUDE.md as possible, instructions just-in-time.
- **(c) Force, don't ask** — use hooks to implement gates rather than relying on
  prompt-level instructions.

### Sharpening (c) — the irreversibility threshold

From *Hooks: Policy as Code* (https://ranjankumar.in/hooks-policy-as-code-agent-enforcement):

> *"Every rule you trust to a CLAUDE.md instruction is a rule the agent can
> violate. Every rule encoded in a hook is a rule the agent cannot violate."*

But not every rule should become a hook — hook-bloat is its own problem. The
decision rule: **promote a prompt rule to a hook iff violating it is
*unrecoverable*** (data loss, secret leak, commit to `master`, eval-surface
corruption). Recoverable concerns (formatting, style) stay in prompts. This gives
principle (c) a crisp test instead of "hook everything."

For claude-optimize specifically: G-INV-1 (auto-block) is a good hook candidate —
a pre-commit check that refuses a claude-optimize-authored `goal.md` lacking
`awaiting: ["user-unblock"]`. Violation (an unblocked auto-proposal executing in
autorun) is exactly the irreversible-ish harm the threshold is meant to catch.

### The web-revealed additions (the user's "(d) probably more")

- **(e) Just-in-time context loading.** Reference data by short identifiers; pull
  into context only when needed. (Anthropic, *Effective context engineering for AI
  agents*; Morph reports ~95% baseline context reduction from lazy tool discovery.)
  *Factory audit candidate: CLAUDE.md is ~13 KB read every session — split into a
  small always-loaded core + on-demand sections.*
- **(f) The feedback loop is the product.** When a recurring failure is observed,
  prefer adding a deterministic gate/test over writing a new prompt-level
  instruction or a new skill. (Kobi Kadosh, *The Software Feedback Loop*; Anthropic
  Agent SDK verification hierarchy: rules-based > visual > LLM-as-judge.) *This is
  the deepest one for claude-optimize: the path from "we keep seeing this mistake"
  to "add a gate" should be shorter than the path to "write a new skill."*
- **(g) Sub-agent context isolation.** Every long exploration that doesn't need to
  leave evidence in the main conversation runs in a sub-agent that returns a
  distilled summary. (Anthropic; RichSnapp: *"subagents preserve the quality of the
  context that already exists."*) *Already factory practice; worth codifying.*
- **(h) Smallest set of high-signal tokens, as a measured target.** Extends (b) from
  aspiration to metric: track per-task input-tokens-at-first-message; flag
  regressions when a skill or CLAUDE.md edit pushes the median up. (Anthropic.)

**Decision (proposed, N-D-10):** IMPL-K writes a `REQ-PROC` for these principles
(a–h), with the irreversibility threshold attached to (c). This requirement then
becomes a lens that future `claude-optimize` runs can detect violations against
(e.g. "CLAUDE.md grew 40% — principle (b)/(e) regression → propose a split task").

---

## Part 6 — Updated impl backlog (delta from round-3 §7 / decisions-log §5)

Round-4 adds no new *blocking* structure; it enriches existing items and adds one
optional item.

| ID | What | Change from decisions-log §5 |
|---|---|---|
| IMPL-A | Rewrite REQ-PROC-006 | now also incorporates G-INV-1/2/3 (Part 3) + two-metric model (Part 4) |
| IMPL-B | `.factory/optimize/` scaffolding | add `history/audit_history.tsv`, `history/web_searches.tsv` |
| IMPL-C | Monitor scripts + `run_monitors.py` | unchanged |
| IMPL-D | `create_optimize_task.py` (auto-block default) | consider pre-commit hook enforcing G-INV-1 (Part 5, principle c) |
| IMPL-E | claude-optimize skill body | unchanged |
| IMPL-F | Wire monitors into `task-complete` | unchanged |
| IMPL-G | `claude-optimize-audit` skill | now also: deterministic scoring rubric (Part 2.1), `--monitor=` sub-audits (2.2), DuckDB optional query layer (Part 1.3), revert-rate metric (Part 4) |
| IMPL-H | `skills_used:` protocol instrumentation | unchanged; note complementarity with DuckDB (Part 1.4) |
| IMPL-I | (blocked) consume TASK-PROC-044 observability | unchanged |
| IMPL-J | `web_searches.tsv` instrumentation | unchanged |
| IMPL-K | REQ-PROC for cross-factory LLM-work principles (a–h) | now has full sourced list (Part 5) |
| IMPL-L | Refactor factory-only files under `.factory/` | unchanged; independent |
| **IMPL-M (new, optional)** | v1.5: DuckDB optional query layer for the audit skill | after IMPL-G; optional |

12 required + 1 optional. The dependency order is unchanged: requirement first,
then scaffolding, then scripts, then skill bodies, then audit, then the deferred
enrichments.

---

## Part 7 — What changed vs. round-3 (at a glance)

| Area | Round-3 | Round-4 |
|---|---|---|
| Session DB | "forbidden in routine use" | "deferred to v1.5 as optional DuckDB query layer; runs.tsv canonical" |
| Audit skill output | raw aggregates | + deterministic 10-point score with trend delta |
| Effectiveness metric | user-unblock-rate only | + revert-rate (quality lag-indicator) |
| Reward-hacking mitigation | scattered across sections | consolidated into 3 named invariants G-INV-1/2/3 |
| Principle (c) | "use hooks as gates" | + irreversibility threshold (hook iff violation unrecoverable) |
| Principles list | a/b/c (user's) | a–h, sourced; promoted to its own requirement (IMPL-K) |
| Folder | `automation/optimize/` | `.factory/optimize/` (per N-D-1) |

Nothing from round-3 is reversed. Everything is additive.

---

## Part 8 — New decisions opened by round-4

These are the only fresh choices; all are additive and low-stakes.

- **N-D-7. DB deferral.** Defer the session-DB to v1.5 as an optional DuckDB
  query-time layer (no daemon, no schema, runs.tsv stays canonical). *Proposed:
  accept.*
- **N-D-8. Deterministic audit scoring rubric.** Adopt the kaizen-style N-point
  score + trend delta in the audit skill. *Proposed: accept; exact criteria
  refined during IMPL-G.*
- **N-D-9. Two-metric model.** Track both user-unblock-rate (primary) and
  revert-rate (secondary). *Proposed: accept.*
- **N-D-10. Cross-factory principles requirement.** Write a REQ-PROC for principles
  a–h (IMPL-K). *Proposed: accept.*

If all four are accepted, no further synthesis round is needed and the exploration
task can close.

---

## Part 9 — Remaining uncertainties (honest list)

- **U-1 (S9 frequency) unresolved by data.** No published rate for Claude Code.
  Plan stands: emit every S9 event to runs.tsv for 30 days, let the audit skill
  compute the empirical distribution before tuning the threshold. Do not guess a
  number now.
- **U-3 (web-research-worth-it heuristic) has no quantitative answer in the
  literature.** Over-search is a documented failure mode but no numeric trigger
  exists. Plan stands: keep the round-3 §2.3 qualitative table + log every search
  to `web_searches.tsv` (N-D-4) and let evidence refine it.
- **The scoring rubric criteria (Part 2.1) are a guess.** The *mechanism* is sound;
  the specific 10 criteria will need a pass once real runs.tsv data exists. This is
  fine — the rubric is owned by a script that is itself a normal, editable artifact.
- **DuckDB-over-JSONL is account-local (Part 1.4).** The v1.5 implementer must not
  treat it as canonical history. Flagged here so it isn't forgotten.
- **IMPL-K scope creep risk.** A cross-factory principles requirement could balloon
  into a rewrite of CLAUDE.md. It must be scoped tightly: state the principles +
  the irreversibility threshold; do *not* re-audit every existing skill in the same
  task (that is what claude-optimize is *for*, later).

---

## Part 10 — Closing recommendation

The exploration is complete. Across four synthesis rounds the problem space went
from "redesign a stub skill" to a fully-shaped, prior-art-validated,
guardrail-protected design with a 12-task implementation backlog and clear
acceptance criteria.

Recommended close-out: accept N-D-7 through N-D-10 (all additive), close
TASK-PROC-006-02 via `task-complete`, and create the impl backlog. IMPL-A (rewrite
REQ-PROC-006) is the first runnable task; IMPL-L (the `.factory/` refactor) is
independent and can run anytime.

One-sentence design summary, updated for round-4:

**claude-optimize is a small task-producer driven by cheap monitor scripts that
run after every task-complete; it emits one auto-blocked improvement task (or a
no-op) per run, writes its own `runs.tsv` under `.factory/optimize/`, and is held
honest by three non-removable guardrails and a separate audit skill that scores the
whole loop on two metrics — engagement (unblock-rate) and durability (revert-rate) —
with a database introduced only later, only for queries, and never as the canonical
record.**
