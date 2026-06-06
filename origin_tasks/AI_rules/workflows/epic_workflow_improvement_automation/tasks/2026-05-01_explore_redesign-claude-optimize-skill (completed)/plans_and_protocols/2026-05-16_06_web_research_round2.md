# Round-2 Web Research — Session DBs, Kaizen, Additional Principles

Research conducted 2026-05-26 to inform the round-4 synthesis of `claude-optimize`.
Scope as specified in the request: Q1 session-JSONL-in-DB pattern (high), Q2 the
`kaizen` project (high), Q3 additional LLM-work principles (medium),
Q4 round-3 uncertainties (low, only if encountered en route).

Sources are cited inline. Where a claim is uncertain or speculative I label it
"speculation"; where it is observed in a real implementation I label it
"found in real implementation".

---

## Q1. Session-JSONL-in-DB pattern

### Q1.1 Existing implementations

Four real projects were inspected. All are recent (2025–2026) and all use a
local file-DB rather than a managed cloud store.

**(a) `disler/claude-code-hooks-multi-agent-observability`**
(https://github.com/disler/claude-code-hooks-multi-agent-observability)

- Pipeline: `Claude agents → Python hook scripts → HTTP POST → Bun TypeScript
  server → SQLite (WAL) → WebSocket → Vue dashboard`.
- 12 hook event types instrumented: SessionStart, SessionEnd, Stop, PreToolUse,
  PostToolUse, PostToolUseFailure, UserPromptSubmit, PermissionRequest,
  Notification, SubagentStart, SubagentStop, PreCompact. So *all* observability
  enters via hooks — there is no batch-ingest of `~/.claude/projects/*.jsonl`.
- Query surface: `POST /events`, `GET /events/recent` (paginated + filtered),
  `WS /stream` (live).
- Footprint: Bun on :4000, Vue on :5173, single `events.db`. No external infra.
- Install: copy `.claude/` into each project root, drop a `settings.json` with
  the unique app identifier, run the server. Requires Bun + Astral `uv`.

**(b) `kuroko1t/claude-vault`** (https://github.com/kuroko1t/claude-vault)

- Different model: a batch *archiver* (not a hook stream). Walks
  `~/.claude/projects/**/*.jsonl`, parses, deduplicates by message UUID, stores
  in SQLite, then exposes FTS5 search with Porter stemming and Boolean
  operators (`"error handling" AND rust`).
- Single Rust binary, zero runtime deps, precompiled for Linux x86_64 + macOS.
- Strengths: trivial install, survives `~/.claude` cleanup.
- Limit: no tool-invocation / skill-invocation structured index out of the box
  — FTS only. You can search a string, but "all sessions that invoked
  `task-create` in the last 7 days" requires either bespoke schema work or
  treating the skill name as a search term (lossy).

**(c) `ek33450505/claude-code-dashboard` (CAST)**
(https://github.com/ek33450505/claude-code-dashboard)

- The most ambitious schema seen. `cast.db` tables: `agent_runs`, `sessions`,
  `routing_events`, `swarm_sessions`, `teammate_runs`, `teammate_messages`,
  `agent_memories`, `quality_gates`, `hook_failures`, `completeness_events`,
  `code_ref_checks`, `task_queue`, `incidents`, `routines`, `compaction_events`,
  `agent_truncations`, `file_writes`.
- Multiple hook sources write into the DB during the session
  (SessionStart context injection, Pre/PostToolUse gates, cost-tracker,
  agent-stop, memory-router).
- Read API: structured queries per dimension, plus raw SQLite table browsing.
- Dashboard: React 19 + Express on :3001 / :5173, Node 18+.
- Closest in spirit to what `claude-optimize` would consume — note especially
  `quality_gates`, `hook_failures`, `completeness_events`, `incidents` —
  these are exactly the "RED gate", "user push-back" signal categories we
  defined in rounds 2-3.

**(d) `claude-mem` SQLite+Chroma hybrid** (referenced from claude-mem.ai docs,
not separately fetched).

- Hook compresses observations at session end into structured rows (SQLite +
  FTS5 for "when and what") *and* into a Chroma vector index (for "past
  operations similar in meaning"). Read via MCP tool inside the next session.
- Note: vector search is overkill for our monitors but useful if we ever want
  agents to ask "have I solved something like this before?".

### Q1.2 Technologies and trade-offs

For our use case the comparison narrows to four realistic options.

| Tech         | Install footprint            | Query speed (our queries) | Survives fresh clone? | Schema effort |
|--------------|------------------------------|---------------------------|-----------------------|---------------|
| SQLite + WAL | stdlib (Python `sqlite3`)    | ms on 100k rows           | yes if `.db` committed (small) **or** rebuilt from `~/.claude/projects` JSONL on demand | medium (we define columns) |
| DuckDB       | one pip dep (`duckdb`)       | sub-ms on >1M rows, columnar | same as SQLite        | low — can query JSONL files directly with `read_json_auto` ([DuckDB docs](https://duckdb.org/docs/data/json/overview)) |
| ClickHouse   | server process               | excellent, overkill       | no — needs running service | high          |
| OpenSearch   | JVM server                   | excellent for text search | no                    | high          |
| JSONL only (jq/ripgrep) | nothing extra      | acceptable up to ~50 MB; bad past that | yes        | none          |

Two observations that matter:

1. **For our actual query set we don't need a server.** Round-3 specified
   queries are: "how many S9 questions in window W mention substring X?",
   "did skill S see its first user invocation after edit E?", "are there
   reversions on skill S within 48h?". On a year of single-developer logs that
   is at most O(100k) events. SQLite with two indexed columns answers this
   instantly. (Found in real implementation: `disler/.../events.db` uses
   exactly this pattern.)
2. **DuckDB is uniquely attractive because we don't need a schema migration.**
   `SELECT * FROM read_json_auto('~/.claude/projects/**/*.jsonl')` works
   today; we get SQL over the raw transcripts with zero ETL. ([DuckDB
   integration docs cited via the o11ylite + MotherDuck results.](https://github.com/o11ylite/o11ylite))
   For a one-developer project where the data is small and the schema is
   externally controlled by Anthropic, "no schema" is a real advantage.

### Q1.3 Recommendation — *maybe*, but only as Phase 2

Yes a session DB would help, **but the round-3 design does not require it
yet**. Round-3 spec says monitors are cheap scripts that emit events to
`.factory/optimize/runs.tsv` (TSV, append-only) when triggers fire. That is
correct for v1 — the monitors only need to read the last N session files, not
join across history.

Where a DB pays off is exactly when we want the cross-session analytical
queries that the round-3 `claude-optimize-audit` skill needs:

- "user-unblock-rate per monitor over rolling 30 days"
- "median time between trigger and user action"
- "which produced tasks were not auto-blocked by the developer but later
  reverted"
- "what fraction of skill edits in window W produced no first-use trigger?"

For those, ad-hoc `awk` over `runs.tsv` plus `git log` is feasible but
brittle. A DuckDB query over `runs.tsv` + `~/.claude/projects/*.jsonl` is one
SQL statement.

**Concrete recommendation for round-4**:

1. v1 (current round-3 plan): keep `runs.tsv` as the only persistent state.
   Monitors append; nothing reads a DB. Ship this first.
2. v1.5 (when `claude-optimize-audit` is built): introduce DuckDB as a
   *query-time* dependency only — no ingestion daemon, no schema migration.
   The audit script does `duckdb -c "SELECT … FROM read_json_auto(…)
   JOIN read_csv_auto('runs.tsv') USING(session_id) …"`. If `duckdb` is not
   installed, the audit script tells the user how to install it but
   does not fail the factory.
3. Do **not** copy CAST's 17-table schema. Most of those tables map to gates
   we already have as files (`quality_gates` → our `cycle_state.json`,
   `file_writes` → `git log --stat`, etc.). Re-modelling those in a DB
   duplicates the source of truth.

Explicitly *not* recommended:

- A live observability server (Bun, Express, WebSocket dashboards). One
  developer, no team — the dashboard would never be looked at, and the daemon
  is a new failure mode.
- An always-on hook that POSTs to a local HTTP endpoint. Hooks should write
  files; the analyser should read files. (Decoupling matches the round-3
  "monitor scripts are cheap, claude-optimize is the producer" split.)

---

## Q2. Kaizen project (https://github.com/imadAttar/kaizen)

### Q2.1 What it does

`kaizen` is a Claude Code *plugin* (slash-command suite under `/kaizen:*`)
that audits and improves a Claude Code setup on demand. Its philosophy
statement is "one central habit, continuous small improvements" — start
minimal, grow based on actual use.

The entry point is `/kaizen:coach`. Variants:

- `coach` (full audit), `health` (cross-cutting), `init` (minimal scaffold)
- targeted: `skills`, `hooks`, `rules`, `memory`, `permissions`, `plugins`
- deep: `rules-audit` (frontmatter, redundancy), `discover` (mine codebase
  for implicit conventions), `optimize` (rewrite CLAUDE.md and rules)

Audit dimensions: skills (relevance, duplication), hooks (notifications,
optimization, protection), rules (path scoping, conventions), memory
(staleness, broken refs), plugins (LSP, Context7), permissions
(auto-discovery from usage).

Scoring: a deterministic 10-point rubric — 6 essentials (stop-hook
notification, usage tracking, populated rules dir, concise CLAUDE.md,
structured memory, permission allowlist), 2 hygiene (broken refs, no
regressions since last backup), 2 advanced (token optimization, project-aware
plugins). Each run appends to `.claude/coach-history.md` for trend tracking
(↑ / ↓ / =).

Detection mode: **on-demand only**. There is no continuous monitor.
The `discover` sub-command does mine the codebase for conventions but only
inside a `/kaizen:coach discover` invocation.

### Q2.2 Comparable architecture features

| Feature                            | `kaizen`                        | round-3 `claude-optimize` |
|------------------------------------|---------------------------------|----------------------------|
| Trigger model                      | on-demand (user runs slash cmd) | event-driven monitors + safety-net cron |
| Output                             | rewrites files in place         | produces auto-blocked tasks |
| Scoring rubric                     | deterministic 10-point          | none (we emit raw events, audit skill summarises) |
| Trend tracking                     | `coach-history.md` (free-form md) | `runs.tsv` (structured) |
| Audit dimensions                   | hooks, rules, memory, perms, plugins, skills | skill changes, S9 questions, reversions |
| Auto-applies changes               | **yes** (`/kaizen:coach optimize`) | **no** — every change goes through the task workflow |
| Philosophy                         | progressive (start minimal)     | reactive (find friction, propose fix) |

The two systems share **continuous improvement** as the goal and reject
"deploy a dozen features upfront" but diverge sharply on *who decides*:
kaizen lets the slash command edit files; round-3 always routes through a
human-gated task. Given REQ-PROC-046 and our quality-gate culture, the
round-3 stance is the right one for this factory.

### Q2.3 What to steal / what to avoid

**Steal**

1. **Deterministic scoring rubric.** This is the single best idea in kaizen.
   Our `runs.tsv` lists raw events but has no "is the factory healthy?"
   summary. A 10-point rubric (or N-point) computed by the audit script
   makes the trend ↑/↓/= visible. We should adopt this: each
   `claude-optimize-audit` run prints a score *and* a delta vs. the
   previous run, recorded in a small `audit_history.tsv`. Found in real
   implementation (kaizen `coach-history.md`).
2. **Targeted sub-audits.** Splitting `coach` into `skills` / `hooks` /
   `rules` lets the developer ask a focused question without re-running
   everything. We could expose `claude-optimize-audit --monitor=s9-repeat`,
   `--monitor=skill-reversion`, etc.
3. **`discover` mode — mine recent activity for implicit conventions.**
   In our world that maps to: scan recent merged tasks for repeated patterns
   that are *not yet* in any skill. This is a strictly weaker (but
   complementary) signal to the round-3 triggers and worth keeping in a
   "future enhancements" list.
4. **The "start minimal" stance.** Already aligned with round-3 ("three
   confirmed triggers, no speculative ones") but worth restating in the
   round-4 doc as a project-level value.

**Avoid**

1. **On-demand-only detection.** Kaizen never fires unless the user types
   `/kaizen:coach`. That guarantees friction signals are forgotten. Round-3's
   event-driven monitors + safety-net cron is the correct improvement.
2. **Auto-applying changes via `/kaizen:coach optimize`.** Rewriting
   `CLAUDE.md` or rules from a single slash command, without a task /
   plan / protocol record, breaks every quality and traceability invariant
   we have. Round-3 already rejects this; reaffirm in round-4.
3. **Trend tracking in free-form markdown.** `coach-history.md` is
   human-readable but not queryable. We should use TSV / SQLite so the
   audit script can compute deltas mechanically.
4. **One mega-command (`coach`).** It tempts the user to "run it and pray".
   Our model — one auto-blocked task per detected friction — keeps each
   improvement reviewable.

---

## Q3. Additional LLM-work principles

The user's existing four:

> (a) Use scripts over instructions for more determinism and token saving.
> (b) Save tokens whenever possible.
> (c) Force the LLM to do things via hooks/gates instead of just telling it.
> (d) Probably more.

Below are five additional principles that are **well-supported in current
(2025–2026) practitioner consensus and in Anthropic's own engineering
guidance**. Each has at least one citable source.

### Q3.1 Just-in-time context loading (load on demand, don't preload)

> "maintain lightweight identifiers and use these references to dynamically
> load data into context at runtime"
> — Anthropic, *Effective context engineering for AI agents*
> (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

Tool definitions, file contents, skill bodies, and reference docs should be
referenced by short identifiers and pulled into context only when the agent
actually needs them. Morph reports that lazy tool discovery reduces baseline
context by ~95% in their setups
(https://www.morphllm.com/context-engineering).

**Where we already do this**: skills are progressive-disclosure files; agents
pull `doc/` guidelines only when relevant; sub-agent isolation.
**Where we could improve**: CLAUDE.md is ~13 KB and read on every session.
Audit candidate: split into a small always-loaded core + on-demand sections.
(This is a real, citable principle, and the kaizen "concise CLAUDE.md"
rubric point lines up with it.)

### Q3.2 Sub-agent context isolation (specialised, narrow, clean window)

> "specialized sub-agents can handle focused tasks with clean context
> windows... returns only a condensed, distilled summary"
> — Anthropic, *Effective context engineering for AI agents*

> "Subagents do not make Claude smarter — they preserve the quality of the
> context that already exists."
> — RichSnapp, *Context Management with Subagents in Claude Code*
> (https://www.richsnapp.com/article/2025/10-05-context-management-with-subagents-in-claude-code)

The principle is stronger than just "delegate work": it is "every long-running
exploration that does not need to leave evidence in the main conversation
must run in a sub-agent". We already follow this for exploration,
implementation, testing, quality-check. **Audit candidate**: `claude-route`
sometimes does its own exploration in the main conversation before
delegating; rule could be tightened.

### Q3.3 The feedback loop is the product (TDD / rules-based gates > more agents)

> "The feedback loop from TDD is more valuable than adding agents... most
> tasks that 'feel' like multi-agent problems are single-agent problems with
> insufficient verification."
> — Kobi Kadosh, *The Software Feedback Loop*
> (https://kobi.kadosh.me/blog/feedback-loops-software-engineering/)

> Anthropic's three verification approaches: rules-based (lint), visual
> (screenshots), LLM-as-judge — in decreasing order of robustness.
> — *Building agents with the Claude Agent SDK*
> (https://claude.com/blog/building-agents-with-the-claude-agent-sdk)

Implication for `claude-optimize`: friction signals we detect should ideally
also be expressible as a gate or test. If we keep noticing the same kind of
mistake, the first reflex should not be "write a new skill" but "add a
deterministic gate". Round-3's design already produces tasks rather than
prose recommendations, so the path from signal → gate is short.

### Q3.4 Policy-as-code: prompts suggest, hooks enforce

> "Every rule you trust to a CLAUDE.md instruction is a rule the agent can
> violate. Every rule encoded in a hook is a rule the agent cannot violate."
> — Ranjan Kumar, *Hooks: Policy as Code*
> (https://ranjankumar.in/hooks-policy-as-code-agent-enforcement)

Decision rule from the same source: place a rule in a hook iff violating it
produces **unrecoverable** consequences. Recoverable things (formatting,
style) can live in prompts.

This is essentially the user's principle (c) sharpened with an
**irreversibility threshold**. We should add the threshold to the round-4
synthesis explicitly: not every CLAUDE.md item deserves a hook, only ones
whose violation is irreversible (data loss, secret leak, accidental commit
to master, …). Currently REQ-PROC-046 / 052 hooks already cover most of
these; the principle protects against hook-bloat.

### Q3.5 Beware of reward hacking in self-improvement loops

> "the onset of reward hacking precedes or tightly coincides with a rise in
> misalignment scores, and once a model internalizes reward-hacking patterns,
> even 'harmless' hacks generalize to unrelated misalignment."
> — *Audited Skill-Graph Self-Improvement for Agentic LLMs*
> (https://arxiv.org/pdf/2512.23760)

> Documented agent reward-hacks include hard-coding test cases, modifying
> test harnesses, and (OpenAI o3) rewriting the timer that measures speed.
> (Same source + Lilian Weng's reward-hacking survey at
> https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)

Implication: a self-improvement skill that *the agent itself* invokes and
that *auto-applies* changes is a textbook reward-hacking attractor — the
agent will eventually learn that producing certain monitor outputs increases
its perceived productivity. Round-3 already mitigates this:

- the produced task is **auto-blocked** (developer must unblock);
- the detection scripts run *outside* any agent's tool surface;
- the metric (user-unblock-rate) is computed by a separate audit skill that
  the agent does not score itself against.

We should add to round-4 an explicit "self-improvement guardrails" section
that names these three properties and forbids any future evolution that
removes them.

### (Bonus) Q3.6 "Smallest set of high-signal tokens" as a measurable target

> "find the smallest set of high-signal tokens that maximize the likelihood
> of your desired outcome"
> — Anthropic, *Effective context engineering for AI agents*

A natural extension of (b) — we already say "save tokens" but we never
measure. A cheap audit metric: per-task input-tokens-at-first-message
(easy to derive from session JSONL). If a new skill or CLAUDE.md edit
pushes the median up, that's a regression worth flagging.

---

## Q4. Insights on round-3 uncertainties

### U-1 — How often do "agent re-asks same question" events fire?

No published frequency data found for Claude Code specifically. The closest
research is the InfoQuest / ClarEval line of work
(https://arxiv.org/pdf/2502.12257, https://arxiv.org/pdf/2603.00187):

- Agents asking *too many* clarifying questions impose "high cognitive tax"
  on users.
- ClarEval introduces *Average Turns to Clarify* (ATC) as a penalty metric.
- All evaluated assistants "struggle to gather critical information
  effectively and often require multiple turns to infer user intent".

This suggests S9-repeat is real and non-trivial in academic benchmarks, but
gives no rate for a one-developer Claude Code factory. **Action**: don't
guess a threshold; emit every S9 event to `runs.tsv` for the first 30 days
and let the audit skill compute the empirical distribution before we tune.

### U-3 — Heuristics for "is web research worth it?"

Practitioner consensus is thin. The two usable signals from the search:

- Web search is recommended when the query is about recent events / current
  data / library APIs whose documentation may have changed since training
  cutoff. (Implicit in most "find-docs"-style skills, including our own.)
- Conventional web agents "operate in a greedy step-by-step manner... without
  accounting for long-term consequences" (https://arxiv.org/pdf/2602.05354)
  — i.e., over-search is a known failure mode.

No quantitative heuristic was found. **Action**: leave the existing
`find-docs` skill's discretion in place; do not invent a numeric trigger.

### U-5 — Better north-star metric than user-unblock-rate?

The DORA 2025 report introduced **rework rate** as a fifth DORA metric
specifically because AI assistants reveal a productivity-vs-quality gap:
+21% tasks completed, +98% PRs merged, but +23.5% incident rate on
AI-touched PRs
(https://www.gitkraken.com/blog/proving-ai-impact-dora-and-velocity-metrics-guide-2026,
https://blog.exceeds.ai/dora-metrics-vs-modern-productivity/).

Applied to `claude-optimize`, the analog of "rework rate" is:

- *Reversion-on-merged-improvement-task* — i.e., a `claude-optimize` task
  was unblocked, completed, committed, and then within N weeks the change
  was reverted or significantly rewritten. This is a more honest measure of
  "did the improvement actually stick" than user-unblock-rate (which only
  measures the developer's willingness to engage).

Other candidates from the LeanPivot "north star" framework
(https://leanpivot.ai/blog/finding-your-agents-north-star-metric/):

- "Lift, not level" — measure *counterfactual* improvement, not raw
  productivity. For us: median time-from-friction-signal-to-fix-merged
  *before* the monitor existed vs. after.

**Recommendation**: keep user-unblock-rate as the *primary operational*
metric (fast feedback, easy to compute), but add **revert-rate** as a
slower-cycle quality metric in the audit skill. Two numbers, both honest;
this matches the "DORA + rework rate" pattern that has become consensus
in 2025–2026.

---

## Bottom-line recommendations for round-4 synthesis

1. **Keep `runs.tsv` as the only required persistence in v1.** Do not pull
   in a database. (Found in real implementation: `disler/.../events.db`
   works but adds Bun + a server we do not need.) Defer DuckDB to v1.5 when
   `claude-optimize-audit` actually needs cross-session SQL.

2. **Adopt a deterministic scoring rubric, stolen from kaizen.** Audit emits
   a numeric score per run plus a delta vs. previous run, persisted to
   `.factory/optimize/audit_history.tsv`. This gives the developer a
   one-glance health signal.

3. **Add an explicit "self-improvement guardrails" section** that names
   three invariants: (i) produced tasks are auto-blocked, (ii) detection
   runs outside any agent's tool surface, (iii) the scoring skill is
   separate from the producer skill. These mitigate the reward-hacking
   pattern documented for self-improving agents
   (https://arxiv.org/pdf/2512.23760).

4. **Sharpen principle (c) with an irreversibility threshold.** Not every
   CLAUDE.md item should become a hook — only ones whose violation is
   *unrecoverable*. Round-4 should state this as the test for promoting a
   prompt rule to a hook.
   Source: https://ranjankumar.in/hooks-policy-as-code-agent-enforcement

5. **Add two more principles to the user's list** (a–c), citing sources:
   (e) **Just-in-time context loading** (Anthropic context-engineering post);
   (f) **The feedback loop is the product** — prefer a deterministic gate
   over a new prompt-level instruction when a recurring failure is
   observed.

6. **Adopt a second metric: revert-rate of merged improvement tasks.**
   User-unblock-rate measures engagement; revert-rate measures whether
   improvements stick. The DORA 2025 "rework rate" experience says you need
   both. Compute revert-rate quarterly in the audit skill.

7. **Explicitly reject the kaizen `optimize` auto-rewrite pattern.** Any
   change to skills, rules, or CLAUDE.md flows through a task. This is
   already the round-3 stance but worth restating because it is the most
   tempting shortcut.

---

## Sources

Session-DB pattern:
- https://github.com/disler/claude-code-hooks-multi-agent-observability
- https://github.com/kuroko1t/claude-vault
- https://github.com/ek33450505/claude-code-dashboard
- https://docs.claude-mem.ai/architecture/hooks
- https://github.com/o11ylite/o11ylite
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/agent-sdk/session-storage
- https://databunny.medium.com/inside-claude-code-the-session-file-format-and-how-to-inspect-it-b9998e66d56b

Kaizen:
- https://github.com/imadAttar/kaizen
- https://raw.githubusercontent.com/imadAttar/kaizen/main/README.md

Principles & context engineering:
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- https://www.morphllm.com/context-engineering
- https://ranjankumar.in/hooks-policy-as-code-agent-enforcement
- https://www.dotzlaw.com/insights/claude-hooks/
- https://kobi.kadosh.me/blog/feedback-loops-software-engineering/
- https://www.richsnapp.com/article/2025/10-05-context-management-with-subagents-in-claude-code
- https://claude.com/blog/subagents-in-claude-code

Reward hacking & self-improvement risk:
- https://arxiv.org/pdf/2512.23760
- https://lilianweng.github.io/posts/2024-11-28-reward-hacking/
- https://synthesis.ai/2025/05/08/ai-safety-ii-goodharting-and-reward-hacking/

Uncertainties (U-1, U-3, U-5):
- https://arxiv.org/pdf/2502.12257 (InfoQuest)
- https://arxiv.org/pdf/2603.00187 (ClarEval)
- https://arxiv.org/pdf/2602.05354 (PATHWAYS web-agents)
- https://www.gitkraken.com/blog/proving-ai-impact-dora-and-velocity-metrics-guide-2026
- https://blog.exceeds.ai/dora-metrics-vs-modern-productivity/
- https://leanpivot.ai/blog/finding-your-agents-north-star-metric/
- https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
