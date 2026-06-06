# Synthesis — Operationalizing REQ-PROC-053 Documentation-Lookup Policy

Date: 2026-05-26
Task: TASK-PROC-053-02
Status: FINAL

## Reading order

This document is the design synthesis the goal.md asked for. It is *not*
implementation — every per-skill amendment and the `context7` wiring land
in follow-up impl tasks named in §11.

It composes inputs from:
- the requirement itself (`requirements.md` @ commit `db92ca63`),
- the user's initial input (`2026-05-21_00_user_initial_input.md`),
- the codebase reconnaissance of every code-producing skill / agent
  (§3 below names them with file:line evidence),
- the prior-art research report
  (`2026-05-26_01_prior_art_research.md`),
- the `context7` integration research report
  (`2026-05-26_02_context7_integration_research.md`),
- and the sibling-requirement reading of REQ-PROC-046 / REQ-PROC-001.

The cache rule from goal.md (§"Cache rule for THIS task itself")
applies: every upstream documentation read this synthesis performed is
recorded in §12 so the same source is not re-fetched mid-task.

---

## 1. What this design must answer

The goal.md enumerated seven design questions. The contract this
synthesis must satisfy:

| Q | Question (paraphrased) | Section |
|---|---|---|
| Q1 | Which skills / agents carry the AC-07 checkpoint, at which step? | §3 + §4 |
| Q2 | Per-technology trigger calibration (Flutter / Dart core / Python / native / GHA / config)? | §6 |
| Q3 | How is `context7` integrated mechanically given devcontainer + WSL2 + Windows-host? | §5 |
| Q4 | What is the task-scope lookup log — location, format, fields, dedup, cache invalidation, concurrent-write safety? | §4 |
| Q5 | How does the gate-failure → lookup edge plug into `verify-quality` / `quality-checker`? How does it move cycle counts toward the floor? | §7 |
| Q6 | What's the per-task lookup budget under REQ-PROC-001? When does the budget cap force escalation? | §8 |
| Q7 | How do existing LLM coding tools handle the same problem — what to steal, what to avoid? | §2 |

Plus from the AC enumeration:

| Source | Item | Section |
|---|---|---|
| AC-06 + Seed 9 | Per-test-framework call-pattern risk classification | §6.6 |
| AC-02 (a) | Toolchain-clean verification mechanism | §4.5 |
| Seed 10 | Dependency-upgrade interface seam | §10 |

§9 lists decisions deferred to the user. §11 lists the follow-up impl
tasks the design implies. §12 is the dogfood lookup log.

---

## 2. Prior art

Full report: `2026-05-26_01_prior_art_research.md`. This section
distills what reshapes the design below.

### 2.1 The trigger-rule gap

No surveyed tool has solved the "look it up only when external evidence
is absent" problem that REQ-PROC-053 AC-02 specifies. The two dominant
patterns are:

- **"Always ask context7"** (Cline, Cursor-with-rule, Claude Code with
  MCP) — cheap to specify, costly to run, and lossy on dedup across the
  session.
- **"Agent decides"** (Aider, Replit Agent, Codex, OpenHands) — collapses
  to "rarely looks it up" because LLMs do not know what they do not know.

Our AC-02 external-evidence-based trigger is therefore **novel** — no
prior art to copy directly. The closest precursor is Devin's "Trigger
Description" field (free-text phrases that control when Knowledge is
injected), but Devin's mechanism is opaque and unauditable.

### 2.2 The dedup gap

No surveyed tool prevents both the orchestrator skill AND the spawned
subagent from hitting the doc service on the same call. Aider escapes
this only because its architect/editor pair shares the chat transcript.
Claude Code's progressive-disclosure model (Skills L1→L2→L3) gives us
the filesystem seam that makes a task-scope lookup log viable — but the
log protocol itself is novel.

### 2.3 Patterns we adopt

| Pattern | Source | How it reshapes this design |
|---|---|---|
| Two-tool split (`resolve-library-id` → `get-library-docs`) | context7 | The resolve step is cheap and dedup-friendly; §4.1's `technology` field stores the resolved slug. |
| Question-bound `WebFetch` (returns answer, not raw markdown) | Claude Code | The `doc-lookup` skill returns a result summary, not raw page content — mirrors this cost-control shape. |
| Progressive disclosure (skill metadata → on-demand files) | Claude Code Skills | The orchestrator declares the log path; the subagent reads it on demand. §4.7 adopts this directly. |
| Versioned slugs in the lookup identifier | context7 | §4.1's dedup key encodes `pinned_version` so lookups are version-anchored by construction, not by convention. |
| `WebSearch` + `WebFetch` split (probe is cheap, body is expensive) | Claude Code | §4.6's channel chain reuses this: resolve → query is cheap; full-page WebFetch is the expensive fallback. |
| `alwaysApply: true` rule frontmatter | context7/Cline | Per-skill checkpoint declarations adopt a similar unconditional-trigger marker. |

### 2.4 Patterns we explicitly reject

| Anti-pattern | Exhibited by | Failure mode this design avoids |
|---|---|---|
| "Always look it up" with no dedup | Cline/Cursor default context7 rule | 5–10× redundant lookups per task; §4.2's dedup key prevents this. |
| Model-judged trigger ("agent decides") | Replit Agent, Aider implicit, Codex | LLMs don't know what they don't know — our AC-02 external-evidence check externalizes the trigger. |
| User-initiated only (`@Docs`, paste URL) | Cursor, Continue, Aider | Breaks in autonomous/automated sessions; our trigger is declarative in the skill, not interactive. |
| Opaque server-side cache | context7 internal caching | Client-side dedup in our `lookup_log.jsonl` is the authority; server caching is a bonus, not a guarantee. |
| No version-pinning | Every surveyed tool | All put the burden on the user; our design derives the version from `pubspec.lock` automatically. |
| No gate-failure → lookup edge | Every surveyed tool | None wires "analyzer error → lookup first"; our §7 fills this. |
| No skill→subagent dedup | Every surveyed tool | Nothing prevents duplicate lookups across the boundary; our lookup log is the novel mechanism. |

### 2.5 context7 ecosystem signals

context7 is the de-facto standard for "agent reads up-to-date library
docs." Confirmed integrations span 30+ clients including Claude Code,
Cursor, Cline, Roo Code, Windsurf, Copilot CLI, and JetBrains AI
Assistant. The canonical activation is either the `"use context7"`
prompt sentinel or MCP tool availability in the agent's tool surface.
All clients use the same two-tool contract. See `2026-05-26_02_context7_integration_research.md` for full
ecosystem inventory.

---

## 3. The authoring chains (codebase reconnaissance)

REQ-PROC-053 AC-07 names six code-producing chains and adds "any future
skill or agent that produces or modifies code." From file-level reading
of `.claude/skills/code-*/SKILL.md` and `.claude/agents/*.md`, the
*current* chain set is:

### 3.1 Chain map

| # | Skill (orchestrator) | Spawned agent(s) that write code | Skill writes code directly? | Reference |
|---|---|---|---|---|
| C1 | `code-simple` | `implementation-engineer` (primary), `test-engineer` (per-file test runs, may fix impl on RED) | No — orchestrates only | `.claude/skills/code-simple/SKILL.md:44–58` |
| C2 | `code-complex` | `implementation-engineer` (per batch, ≤3 files), `test-engineer` (per test file) | No — orchestrates only | `.claude/skills/code-complex/SKILL.md:48–69` |
| C3 | `code-test` | `test-engineer` (planning + impl + reporting) | No — orchestrates only | `.claude/skills/code-test/SKILL.md:16–33` |
| C4 | `code-bugfix` (slim mode) | None | **Yes** — direct edits, no subagent | `.claude/skills/code-bugfix/SKILL.md:25–37` |
| C5 | `code-bugfix` (worktree mode) | None | **Yes** — direct edits in a worktree | `.claude/skills/code-bugfix/SKILL.md:41–112` |

### 3.2 Agent inventory (code-relevant)

| Agent | Spawned by chains | Writes code? | Tool surface | Reference |
|---|---|---|---|---|
| `implementation-engineer` | C1, C2 | Yes (primary) | Read, Edit, Write, Bash, Skill — **no WebSearch / WebFetch** | `.claude/agents/implementation-engineer.md:5` |
| `test-engineer` | C1, C2, C3 | Yes (tests + may fix impl on RED) | Read, Edit, Write, Bash, Grep, Skill — **no WebSearch / WebFetch** | `.claude/agents/test-engineer.md:5` |
| `architecture-advisor` | C2 (plan only) | No — plan markdown only | Read, Grep, Glob, Write, Skill, **WebSearch, WebFetch** | `.claude/agents/architecture-advisor.md:5` |
| `quality-checker` | C1, C2, C3 (via `verify-quality`) | No — review only | Read, Grep, Glob, Bash, Skill — **no WebSearch / WebFetch** | `.claude/agents/quality-checker.md:5` |

Two structural facts shape the checkpoint design (§4):

- **MCP tools propagate to subagents automatically.** Claude Code's
  `.mcp.json` is inherited by every spawned subagent
  (`implementation-engineer`, `test-engineer`, etc.) regardless of
  the agent's `tools:` field. This means context7's MCP tools
  (`resolve-library-id`, `get-library-docs`) are available to
  code-writing agents even though they lack `WebSearch` / `WebFetch`.
  However, direct MCP invocation bypasses the dedup / budget logic —
  the `doc-lookup` skill (§4.6) wraps MCP calls with the log and
  budget protocol, so agents invoke the skill via their `Skill` tool
  rather than calling context7 directly.
- **`code-bugfix` has no `Skill` tool today** (`tools: Bash, Read, Edit,
  Write` — SKILL.md:5). The skill writes code directly and cannot
  invoke other skills. The bugfix checkpoint must therefore either be
  inlined into the skill's instructions (no skill invocation) or
  `code-bugfix` must grow the `Skill` tool. Surfaced in §9 as a
  decision.

### 3.3 Future-proofing AC-07

AC-07's "any future code-producing skill or agent" clause means new
authoring surfaces inherit the policy automatically. The design must
therefore make the checkpoint **easy to add** in a new skill — i.e. one
documented procedure callers invoke, not a per-skill bespoke
implementation. This drives §4's single-`doc-lookup` skill design over
per-chain duplication.

### 3.4 Out of scope (NOT a code-producing chain)

- `task-resolve` — by its own definition ("deliverables are *non-code*
  artifacts"; `.claude/skills/task-resolve/SKILL.md:8`). If a
  task-resolve run produces code, the user is misusing it — they should
  invoke `code-simple` or `code-complex`. No checkpoint added.
- `architecture-advisor`, `quality-checker`, `opus-advisor`,
  `setup-optimizer` — review / planning agents, no code emission.
- `task-create`, `task-complete`, `claude-route`, `claude-log` and the
  rest of the meta-skills — no code authoring.

The five chains in §3.1 are the closed set this design covers today.

---

## 4. The checkpoint and the task-scope lookup log

### 4.1 The lookup log

**Location**: `<task-folder>/plans_and_protocols/lookup_log.jsonl`

**Format**: JSONL (one JSON record per line), append-only.

**Why JSONL, not Markdown or YAML or `lookup_log.md`**:

1. *Concurrent-write safety.* Multiple agents in the same chain (e.g.
   `implementation-engineer` for batch 1 then batch 2 in `code-complex`)
   may write while another reads. POSIX `O_APPEND` guarantees atomic
   small-write semantics up to `PIPE_BUF` (4 KiB on Linux); JSONL
   records below that bound never interleave. Markdown / YAML are
   structural — a partial write corrupts the file.
2. *Programmatic dedup.* The dedup key (§4.3) is a tuple lookup over a
   line-stream — a 10-line `jq` or Python script over the file.
   Markdown requires parsing.
3. *Human readability is not lost.* `jq -r '.' lookup_log.jsonl` renders
   a readable summary; an inline "Lookup notes" section in the
   task's main protocol markdown can summarize counts and gap-flags.

**Record schema** (every field required unless marked optional):

```json
{
  "ts": "2026-05-26T14:32:11Z",
  "agent": "implementation-engineer",
  "agent_id": "abc123def456789a",
  "chain": "code-complex",
  "step": "batch-2/3",
  "technology": "package:flutter",
  "pinned_version": "3.24.0",
  "api_surface": "ListView.builder.itemBuilder",
  "decision": "looked_up",
  "channel": "context7",
  "source_ref": "context7:flutter/ListView.builder@3.24.0",
  "result_summary": "itemBuilder takes (BuildContext, int) → Widget; returns null for no-more-items; itemCount must be set when using nullable returns.",
  "trigger": "default",
  "cycle": 1
}
```

Field semantics:

| Field | Values / format | Why |
|---|---|---|
| `ts` | ISO-8601 UTC | Ordering only; not used for cache TTL (cache is anchored to pinned version, not wall clock — see §4.4) |
| `agent` | role name | Survives session restarts; matches `.claude/agents/<name>.md` |
| `agent_id` | session/agent ID | Per CLAUDE.md "find via `.jsonl` mtime"; lets a resume read which agent did what |
| `chain` | one of `code-simple` / `code-complex` / `code-test` / `code-bugfix-slim` / `code-bugfix-worktree` | Future code-producing skills register here |
| `step` | free-form label (e.g. `batch-2/3`, `test-fix-cycle-2`, `bugfix-attempt-1`) | Auditability; not parsed |
| `technology` | canonical identifier — `package:<name>` for pub deps, `dart:<lib>` for Dart core, `python:<module>`, `gha:<action>`, `gradle:<plugin>`, `shell:<bin>`, `flutter` for the framework itself | Dedup key component (§4.3) |
| `pinned_version` | string read from `pubspec.lock` / `requirements.txt` / equivalent at lookup time | Per AC-05 the reading frame |
| `api_surface` | a dotted-path identifier for the API location, granular enough to dedupe similar-but-different calls (e.g. `ListView.builder.itemBuilder` is distinct from `ListView.separated.itemBuilder`) | Dedup key component (§4.3) |
| `decision` | `looked_up`, `skipped_evidence_a`, `skipped_evidence_b`, `skipped_evidence_c`, `fallback_websearch`, `budget_capped` | Auditable — see §8 for `budget_capped` |
| `channel` | `context7`, `official`, `websearch`, `in_repo_call_site`, `prior_in_task_lookup`, `toolchain_run` (the last three are AC-02 evidence skips, not lookups) | The "channel" of `looked_up` is the AC-03 chain; skips record their evidence channel |
| `source_ref` | URL, `context7:` reference, or `lib/file.dart:42` for evidence (a), or `lookup_log.jsonl:line-N` for evidence (b), or `flutter test scripts/...` for evidence (c) | Traceability — closes the AC-03 "feedback loop that makes the chain itself improvable" |
| `result_summary` | 1–3 lines | Lets a later agent skip re-fetching even the same source |
| `trigger` | `default` (AC-02), `deprecation` (active signal), `gate_failure_api_mismatch` (REQ-PROC-046 edge), `version_bump` (AC-05 deprecation seam), `test_framework_subtle` (AC-06), `unknown_symbol` | Powers §7 |
| `cycle` | integer — current REQ-PROC-046 cycle count when entry was written | Enables §7's "lookup ratio per cycle" diagnostic |
| `note` *(optional)* | free-form | For `fallback_websearch` records the AC-03 "why the fallback was needed" requirement |

### 4.2 The dedup key

`dedup_key = sha256(technology + "@" + pinned_version + "::" + api_surface)`

A new authoring decision is a "cache hit" when a record with the same
`dedup_key` and `decision in {looked_up, skipped_evidence_a, skipped_evidence_c}`
already exists in the task's `lookup_log.jsonl`. (Evidence (b) records
are themselves cache references — they don't become cache themselves;
this prevents transitive caching that loses the original evidence trail.)

A cache hit means the agent emits the call against the cached
`result_summary` and APPENDS a new record with
`decision: skipped_evidence_b`, `channel: prior_in_task_lookup`,
`source_ref: lookup_log.jsonl:<line-N>` — so the chain is still
auditable (you see who depended on whose lookup) without re-fetching.

### 4.3 Cache invalidation within a task

**Never within a task.** Per AC-05, the pinned version is the reading
frame. The pinned version cannot change inside a task without violating
the dependency-upgrade-mechanism boundary (the user's separate task,
acknowledged in §10). If somehow the pinned version DID change
mid-task — e.g. a task that bumps `pubspec.yaml` then continues coding —
the bump is itself an AC-05 trigger, and the agent must re-lookup
against the new pinned version. Records keyed at the old version remain
on file (auditable history) but no longer match the dedup key.

This is the **simplest possible cache discipline**: pinned-version
identity. No TTL, no wall-clock decay, no manual invalidation.

### 4.4 Concurrent-write safety across chain steps

The five chains in §3.1 are all *sequential* — `code-complex`'s batches
run one after another (SKILL.md:62), `code-test`'s test-engineer is a
single agent, `code-bugfix` is one orchestrator. No two agents write
the same `lookup_log.jsonl` at the same instant.

Where concurrency could surface in future:
- A task that spawns *parallel* agents for independent file batches
  (theoretical — no current chain does this).
- A user manually running two skills against the same task folder.

Both are protected by JSONL + `O_APPEND` atomicity for records under
4 KiB. The record schema in §4.1 budgets ~500 bytes typical, 2 KiB
worst case — well within the bound. Skills writing the log MUST use
`open(path, 'a')` semantics (Python) or `>>` (shell), never read-modify-write.

### 4.5 AC-02 (a) toolchain-clean verification

This is the cost question Seed 6 raised: when the checkpoint sees an
existing in-repo call site at the same `api_surface`, how does it
verify the "toolchain currently passes clean at the pinned version"
claim that AC-02 (a) requires?

**Recommended design — tiered, with hard cost cap**:

1. **Fast path — `verify-quality` cache.** When `.git/quality_green_hash`
   exists AND matches the current `git stash create -u` hash, the entire
   tree (including the candidate evidence file) passed gates GREEN
   recently. The cache hash is a content identity (see
   `.claude/skills/verify-quality/SKILL.md:34–44`), so a match guarantees
   the analyzer reported no signal at the moment the cache was written.
   Evidence (a) is granted; record `decision: skipped_evidence_a`,
   `channel: in_repo_call_site`, `source_ref: lib/.../file.dart:NN`,
   `note: "verify-quality cache <SHA>"`.
2. **Slow path — targeted analyzer run.** When no cache hit, run
   `dart analyze --no-fatal-warnings --no-fatal-infos <file>` for the
   specific evidence file. Budget cap: 5 seconds (per-call, not
   cumulative). A clean exit grants evidence (a). A non-clean exit
   denies evidence and the default lookup fires.
3. **Fallback path — deny on timeout.** If the targeted analyzer
   exceeds the 5-second cap, the checkpoint denies evidence (a) and
   the default lookup fires. This biases toward correctness over
   speed when the toolchain is slow.

The 5-second cap is calibrated from typical `dart analyze` per-file
latency on this codebase (~1–3s for a feature file, ~2–5s for a
core/data-layer file with many imports). It is a per-call cost, not a
per-task budget — a task with many evidence checks pays linearly but
each is bounded.

For Python files in `scripts/`, the equivalent is `ruff check <file>`
(near-instant) + `mypy <file> --no-error-summary` (~1–3s per module).

Per-language toolchain probes:

| Technology | Probe | Latency | Failure mode |
|---|---|---|---|
| Dart / Flutter | `dart analyze --no-fatal-* <file>` | 1–5s | Treat exit ≠ 0 as deprecation/symbol signal |
| Python (scripts/) | `ruff check <file>` + `mypy <file>` | <1s + 1–3s | Treat any error as denial |
| Shell | `shellcheck <file>` (when present) | <1s | Treat warnings as soft signal; errors as denial |
| YAML / JSON | none reliable; deny by default | n/a | Default lookup fires |
| Native build files (Gradle, Podfile) | none in-container | n/a | Default lookup fires |

### 4.6 The single `doc-lookup` skill

Rather than implementing the checkpoint in five places, the design
proposes **one new skill** — `doc-lookup` — invoked from every
checkpoint site (§3.3 future-proofing). API sketch:

```
doc-lookup --technology <tech> --api-surface <surface> \
           --pinned-version <ver> [--trigger <reason>]
```

The skill:
1. Computes the dedup key (§4.2) and scans `lookup_log.jsonl`.
2. On cache hit: appends a `skipped_evidence_b` record, returns the
   cached `result_summary`.
3. On miss: checks AC-02 (a) evidence path via §4.5 — if granted,
   appends `skipped_evidence_a`, returns null (caller proceeds without
   a result summary; the in-repo call site IS the summary).
4. On all skips failing: dispatches the AC-03 channel chain
   (context7 → official → websearch), appends `looked_up`, returns the
   result.
5. On `budget_capped` (§8): appends `budget_capped`, returns a
   designated "escalate" sentinel; the caller routes to
   `pending_feedback`.

The skill is the ONE place AC-07's "exactly one checkpoint per chain"
is mechanically enforced — if two chain steps both invoke `doc-lookup`
on the same `dedup_key`, only the first runs the lookup; the second
records the dependency on the first.

This single-skill design also future-proofs AC-07: a new code-producing
skill adds one `doc-lookup` invocation at its authoring step; no chain
rewrite needed.

### 4.7 Where in each chain does the checkpoint fire?

| Chain | Checkpoint location | Justification |
|---|---|---|
| C1 `code-simple` | Inside `implementation-engineer` step 2 (after reading goal.md + doc/, before producing each file's first call into a new API surface). | Step 2 is when the agent first commits to a call shape. The skill orchestrator (`code-simple` SKILL.md:44) records the initial `lookup_log.jsonl` (empty); the agent invokes `doc-lookup` per new API surface. Test-engineer (step 4) reads the log; cache hits skip the lookup; new fix-time API surfaces trigger their own `doc-lookup`. |
| C2 `code-complex` | Inside `implementation-engineer` per batch (step 5b). Architecture-advisor's plan (step 2) MAY pre-warm the log via `doc-lookup --trigger plan` for APIs the plan names, reducing per-batch lookups. | Same logic as C1; the plan-time pre-warm is an optimization, not a requirement. |
| C3 `code-test` | Inside `test-engineer` Phase 2 (TDD impl). | Test-engineer is the sole code writer; no orchestrator code edits. |
| C4 `code-bugfix` slim | Inside the skill itself, in step 2 ("Apply fix") — but the skill lacks the `Skill` tool today (see §3.3); §9 D2 surfaces this as a decision. | The skill writes code directly; the checkpoint must inline here. |
| C5 `code-bugfix` worktree | Same as C4; in worktree-resume mode (step 6 "Execute plan"), the prior run's `lookup_log.jsonl` is read (it survives — worktree shares the task folder). | Bugfix sessions can be long; log survives session boundaries. |

The "step closest to where the code is written" rule (AC-07) is satisfied
in all five cases.

### 4.8 Visible artifacts

After a task with N lookups completes:
- `<task>/plans_and_protocols/lookup_log.jsonl` exists with N+M
  records (N lookups, M evidence skips).
- The task's final protocol or commit message MAY reference the log
  count (e.g. "8 lookups, 14 evidence skips, 0 fallbacks"). This is
  the lightweight observability surface.
- Fallback (`decision: fallback_websearch`) records are the
  gap-tracking signal AC-03 cares about — a follow-up task can grep
  for them across all closed tasks to identify recurring uncovered
  technologies for `context7` reporting / submission.

---

## 5. The `context7` integration mechanism

Full report: `2026-05-26_02_context7_integration_research.md`. This
section locks the design decision and the rationale.

### 5.1 Available integration paths

context7 (Upstash) exposes five paths:

| # | Path | Mechanism | Local process? |
|---|---|---|---|
| 1 | Remote HTTP MCP | `https://mcp.context7.com/mcp` via `.mcp.json` `type: http` | No |
| 2 | Local stdio MCP | `npx -y @upstash/context7-mcp` via `.mcp.json` `command` | Yes (Node) |
| 3 | REST API | `https://context7.com/api/v2/*` via `curl` / `WebFetch` | No |
| 4 | CLI | `ctx7 docs <id> <query>` via `npx ctx7` | Yes (Node) |
| 5 | TypeScript SDK | `@upstash/context7` npm package | Yes (Node) |

### 5.2 Recommended path: remote HTTP MCP

**Decision**: wire context7 via the remote HTTP MCP endpoint declared
in `.mcp.json` at project root. Authentication via `CONTEXT7_API_KEY`
environment variable.

```jsonc
// .mcp.json (project root)
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" }
    }
  }
}
```

**Rationale vs alternatives**:

| Criterion | Remote HTTP MCP | Local stdio MCP | REST API | CLI |
|---|---|---|---|---|
| Container footprint | Zero | Node child process | Zero | Node |
| Survives container rebuild | Yes (env var only) | Needs npm cache | Yes | Needs npm |
| Subagent propagation | Automatic via `.mcp.json` | Automatic | Manual (Bash) | Manual (Bash) |
| Latency (warm) | Sub-second | Sub-second | Sub-second | ~2s (npx) |
| Cold start | None | npm download (~5s first time) | None | npm download |
| Version pinning | Via slug `/owner/repo/vX.Y.Z` | Same | Same | Same |
| Offline fallback | Fails; need secondary path | Same | Same | Same |

The remote path wins on zero container footprint, no Node-version
coupling, automatic subagent propagation, and no cold-start latency.

### 5.3 The MCP tool surface

Two tools, matching the context7 research report verbatim:

| Tool | Parameters | Purpose |
|---|---|---|
| `resolve-library-id` | `libraryName` (string), `query` (string) | Free-form library name → context7 slug (e.g. `/flutter/flutter`) |
| `get-library-docs` | `context7CompatibleLibraryID` (required), `topic` (optional), `tokens` (optional, default 5000, min 1000) | Slug + topic → ranked doc snippets + code samples |

The `doc-lookup` skill (§4.6) wraps these two calls:
1. Derive the slug from the technology identifier + pinned version
   (e.g. `flutter` + `3.24.0` → `/flutter/flutter/v3.24.0`).
2. Call `resolve-library-id` if the slug isn't cached.
3. Call `get-library-docs` with the resolved slug and a focused topic.
4. Return a summary + source reference; append to `lookup_log.jsonl`.

### 5.4 The "use context7" prompt convention

The research confirms that `"use context7"` is a **prompt sentinel** —
the MCP client sees it and biases toward calling context7 tools. With
the MCP tools directly available via `.mcp.json`, the sentinel is NOT
required — the `doc-lookup` skill calls the MCP tools programmatically.
Skills SHOULD NOT embed the sentinel in user-facing prompts or agent
instructions. The tool invocation is the trigger, not a magic phrase.

### 5.5 Fallback chain when context7 is unavailable

| Failure mode | Detection | Fallback |
|---|---|---|
| Service down / unreachable | MCP tool call returns error | Fall through to AC-03 step 2: `WebFetch` against official docs URL (e.g. `api.flutter.dev`, `pub.dev/<pkg>/versions/<ver>`) |
| Library not indexed | `resolve-library-id` returns no match | Same fallback; record gap as `note: "context7 does not index <tech>"` in lookup log |
| Rate-limited (429) | `Retry-After` header in response | Wait per header; if > 10s, fall through to official docs |
| API key missing | 401 or anonymous 60-req/hr throttle | **Fail loud at skill start** — do NOT proceed with degraded anonymous access; prompt the user to set `CONTEXT7_API_KEY` |

The fallback always records the reason in the lookup log's `note` field
so coverage gaps accumulate and are reportable (§4.8).

### 5.6 Devcontainer / WSL2 environment

- The container has outbound HTTPS (required for `mcp.context7.com`).
- The Windows host is NOT in scope — context7 is container-side only.
  Windows-target operations (per REQ-PROC-054) do not need it.
- `CONTEXT7_API_KEY` lives in `.devcontainer/devcontainer.env` or
  a user-level `.env` file. Per project convention it MUST NOT be
  committed (`.gitignore` already covers `*.env`, `.env*`).
- The `.mcp.json` file at project root IS committed (it carries
  no secrets — the key is read from the env var at runtime).

### 5.7 Cost model

| Tier | Monthly calls | Cost | Notes |
|---|---|---|---|
| Free | 1,000 + 20/day bonus | $0 | May suffice for manual sessions; will exhaust under automation |
| Pro | 5,000 included | $10/seat/month | $10 per additional 1,000 |
| Anonymous (no key) | 60/hour shared pool | $0 | Unusable for a factory pipeline |

A `resolve-library-id` + `get-library-docs` pair likely counts as 2
calls (research notes this is unconfirmed — §9 D9). At the §8.2
budget bands (≤5 lookups/simple task, ≤25/complex), a month of moderate
activity (~20 sessions × ~10 lookups) costs ~200 context7 calls — within
Free tier. Heavy automation may push to Pro.

### 5.8 Privacy constraint (IMPORTANT)

context7 forwards queries to OpenAI, Anthropic, and Google Gemini for
reranking. Queries are stored anonymized for 30 days.

For a private mood tracker app, this means:
- **Do NOT embed file paths, identifiers, or user data in context7
  queries.** Queries should contain only the library name and the
  public API topic (e.g. "flutter ListView.builder itemBuilder signature").
- This is an explicit privacy constraint on the `doc-lookup` skill:
  sanitize queries before forwarding to context7.
- Whether this is acceptable at all is surfaced as a user decision in
  §9 D8.

---

## 6. Per-technology trigger calibration

The policy (AC-01, AC-04) is technology-agnostic; the *heuristics* live
here and in `doc/`. The trigger thresholds below are ranges, not exact
numbers, calibrated against churn rate and per-technology stability.

### 6.1 Reading the table

For each technology row:
- **Stability**: how often the public API surface changes per year.
  `low` = bedrock APIs (`dart:core`); `high` = active rewrite churn.
- **Default trigger**: when AC-02's default rule fires absent cache. A
  tighter trigger means more lookups for that technology.
- **Skip-friendliness**: how readily AC-02 (a) evidence skips apply.
  `loose` = trust an in-repo call site freely; `tight` = require a
  recent toolchain pass.
- **Active signal sensitivity**: how aggressively the agent treats a
  toolchain warning as a re-lookup trigger.

### 6.2 Dart-stack technologies

| Technology | Stability | Default trigger | Skip-friendliness | Active signal sensitivity |
|---|---|---|---|---|
| `dart:core` / `dart:async` / `dart:collection` | very low | Lookup only on new-to-task API surface AND no evidence (a) | loose — evidence (a) freely accepted | low — only on explicit deprecation signal |
| `dart:io` / `dart:isolate` / `dart:typed_data` | low | Same as above | loose | low |
| Flutter framework (`package:flutter/*`) — stable surfaces (Text, Container, Padding, basic gestures) | medium | Lookup on new-to-task non-trivial config | normal — evidence (a) accepted with toolchain-clean check | medium |
| Flutter framework — high-churn surfaces (animation, gesture deep customization, sliver, custom painters, `RenderObject`) | high | Lookup on *every* new authoring decision; evidence (b) caches; evidence (a) requires fresh toolchain pass | tight | high |
| `package:flutter_bloc` / `package:provider` / `package:get_it` / `package:injectable` / `package:go_router` (project's heavy dependencies) | medium | Lookup on new pattern; trust established patterns | normal | medium |
| `package:freezed` / `package:built_value` / `package:built_collection` (codegen-related) | medium | Lookup on annotation changes or new generator usage | normal | medium |
| `package:flutter_secure_storage` / `package:sqlite3` / `package:cryptography` / `package:argon2` (security-critical) | medium | **Lookup on EVERY new authoring decision**; cache aggressively within task | tight — toolchain-clean required, plus SP-gate clean | high — any analyzer hint forces lookup |
| `package:test` / `package:flutter_test` matchers / finders | low | Lookup on subtle behaviors (see §6.6); trust vanilla `expect`, `find.byType`, basic taps | normal | medium |
| `package:integration_test` | medium | Lookup on driver behavior, screenshot APIs, channel mocking | normal | medium |
| `package:glados` (property-test combinators) | medium-niche | Lookup on every `Generator.combine` / shrink customization (high subtlety) | tight | high |
| `package:mutation_test` | medium-niche | Lookup on every operator selection or threshold-tuning decision | tight | high |
| Long-stable 1.x packages with steady releases | low | Lookup on new-to-task API surface | loose | low |
| Newly-added or aggressively-developed pub packages | high | Lookup per AC-02 default; cache freely within task | tight | high |

### 6.3 Python technologies (in `scripts/`)

| Technology | Stability | Default trigger | Skip-friendliness | Active signal sensitivity |
|---|---|---|---|---|
| `pathlib` / `subprocess` / `dataclasses` / `typing` / `enum` / `os` / `sys` (stdlib bedrock) | very low | Lookup only on new-to-task uncommon APIs | loose | low |
| `ruff` / `mypy` / `pytest` / `uv` (project's pinned tooling, evolving) | medium | Lookup on configuration changes or new feature use | normal | medium |
| `pyyaml` (Note: project policy is "no hand-rolled YAML" per REQ-PROC-051 G4 — lookup only confirms ruamel.yaml usage) | low | Lookup only on novel YAML structure handling | loose | low |
| Third-party scripts deps (per `pyproject.toml`) | varies | Lookup per AC-02 default | depends on stability | medium |

### 6.4 Native build files

| Technology | Stability | Default trigger | Skip-friendliness | Active signal sensitivity |
|---|---|---|---|---|
| Android Gradle plugins / AGP / Kotlin DSL | medium-high | Lookup on every modification (rare — must be high-friction) | tight | high |
| iOS Podfile / Xcode project | medium | Lookup on every modification | tight | high |
| Windows MSIX manifest / runner CMake | medium | Lookup on every modification | tight | high |

Native build files change rarely in this project; when they do, the
lookup cost is rounded up — these files have failure modes that the
analyzer doesn't catch in-container.

### 6.5 CI / config / shell

| Technology | Stability | Default trigger | Skip-friendliness | Active signal sensitivity |
|---|---|---|---|---|
| GitHub Actions workflows / actions / expressions | medium | Lookup on new action / version-bumped action / new condition syntax | normal | medium |
| `pubspec.yaml` keys | low | Lookup on novel keys / constraints | loose | low |
| `analysis_options.yaml` rules | medium | **Forbidden** to edit per REQ-PROC-046 K.10 — out of LLM scope; lookup not applicable | n/a | n/a |
| `.arb` localization files | low | Lookup on new ICU plural / select / placeholder | loose | low |
| Shell (POSIX `sh` / `bash`) | very low | Lookup only on niche features (process substitution, here-strings, traps) | loose | low |
| PowerShell | low-medium | Lookup on cmdlet behavior, native-command interop | normal | medium |

### 6.6 Per-test-framework call-pattern risk (AC-06 operationalization)

Per goal.md Seed 9, this is the test-framework-specific risk classification.

| Framework | Low-risk (skip-friendly) | Medium-risk (default trigger) | High-risk (lookup required even on first sight) |
|---|---|---|---|
| `package:test` | `test`, `group`, `setUp`, `tearDown`, basic `expect` with built-in matchers | Custom matchers, async with `Future` returns, `tags` filtering | `setUpAll`/`tearDownAll` with shared mutable state, `expectAsync`, custom `Reporter` |
| `package:flutter_test` | `find.byType` / `find.text` / `find.byKey`, basic `tester.tap` / `tester.enterText`, `await tester.pump()` | `pumpAndSettle` with explicit duration, `runAsync`, mocking platform channels via `setMockMessageHandler` | Golden tests (font / pixel ratio gotchas), `TestWidgetsFlutterBinding.ensureInitialized` ordering, semantics tests interacting with `AccessibilityGuideline` |
| `package:integration_test` | `IntegrationTestWidgetsFlutterBinding.ensureInitialized()`, basic widget interaction in `testWidgets` | `traceAction` for frame-budget assertions, screenshot comparison | Driver-handler bidirectional channels, native screenshot under flutter-tester vs. real device |
| `package:glados` | trivial generators (int, string), `glados<int>()` with simple body | Generator chaining, `glados2`/`glados3` | `Generator.combine` shrink-order issues, custom `Generator` subclasses, `null`-safety in shrink |
| `package:mutation_test` | reading a mutation report | Operator-selection tuning, threshold setting | Custom rule definitions, integrating with CI gating |
| `pytest` (Python) | `def test_*`, `assert`, simple `parametrize` with literals | `fixture` (function scope), `monkeypatch`, `tmp_path` | `fixture` scope=`session`/`module` composition, conftest.py inheritance, `parametrize` × `fixture` combinations, `pytest_plugins`, async-pytest |

The "always look up" cell (rightmost column) means evidence (a) — even
a working in-repo call site — does NOT skip the lookup. The framework's
subtlety is itself the trigger; in-repo precedent without a recent
toolchain pass is too weak a signal at this granularity.

### 6.7 The "where these tables live" question

These tables move into `doc/` once the design lands as implementation:

- `doc/cross_cutting_standards/documentation_lookup.md` — the
  cross-cutting policy operationalization, including §4 (the lookup
  log format), §5 (the context7 integration mechanism), and a per-language
  pointer table.
- `doc/architecture/dart_lookup_thresholds.md` (or fold into
  cross-cutting if small) — the Dart-stack table (§6.2).
- `doc/testing/test_framework_lookup_risk.md` — the per-test-framework
  table (§6.6).
- `doc/python/lookup_thresholds.md` — the Python-stack table (§6.3).
- `doc/general/native_and_ci_lookup.md` — §6.4 + §6.5.

REQ-PROC-053 itself remains technology-agnostic; the per-tech tables
sit in the language-specific docs per `doc/README.md`'s ownership model.

---

## 7. Interaction with REQ-PROC-046 (gate failure → lookup)

The "Gate-failure context is itself a lookup trigger" Key Decision in
REQ-PROC-053's Developer Guidelines makes this interaction the
preventive lever on cycle counts.

### 7.1 Today's loop

`verify-quality` returns RED → orchestrator (e.g. `code-simple` step 5
or `code-complex` step 6) reads the failure → spawns
`implementation-engineer` (or runs the fix inline) → re-runs gates →
cycle count incremented → up to 5, then escalate.

The orchestrator currently has no formal "documentation lookup first"
step on the re-spawn path. The agent reads the failure text and tries
to fix; if the failure is an API-contract mismatch, the fix often
guesses again and burns a cycle.

### 7.2 Proposed wire-in

`quality-checker` already tags failures by type
(`STATUS: RED — <one-line reason>` per
`.claude/agents/quality-checker.md:24`). The synthesis extends this:
when the reason matches one of these failure categories, the
orchestrator MUST prepend a `doc-lookup` step to the fix re-spawn:

| Failure category | Detection | Pre-fix step |
|---|---|---|
| Deprecation warning | analyzer message contains "deprecated" / "deprecated_member_use" | `doc-lookup --technology <package> --api-surface <symbol> --pinned-version <pin> --trigger deprecation` |
| Unknown symbol | analyzer "Undefined name", "isn't defined for the type", `non_existent_method` | Same with `--trigger unknown_symbol` |
| Signature mismatch | analyzer "argument type", "isn't a subtype", `extra_positional_arguments` | Same with `--trigger gate_failure_api_mismatch` |
| Test framework subtle behavior | test runner stack-trace + matcher mismatch on async/golden/sem | Same with `--trigger test_framework_subtle` |
| SP gate violation (REQ-PROC-052) | SP1–SP6 violation on a security-relevant package | Same with `--trigger gate_failure_api_mismatch` (SP gates are AC-relevant) |

The pre-fix `doc-lookup` runs BEFORE the agent reads the failure text
for fixing — it injects fresh upstream context that the failure text
alone doesn't carry. The agent then fixes with both the failure text
AND the fresh API doc.

### 7.3 Cycle floor vs ceiling

The empirical claim from REQ-PROC-046 (LLMLOOP, ICSME 2025) is that
LLM feedback loops plateau at 3–5 cycles. The hypothesis this design
acts on: **the plateau is partly driven by stale API knowledge in the
agent's training data**. When cycle 2's fix guesses against the same
stale shape that caused cycle 1's failure, the loop is stuck.
Injecting a doc-lookup before cycle 2's fix breaks that pattern.

Expected effect (TO BE MEASURED post-implementation, not a design claim):
- The mean cycle count for API-contract-mismatch failures drops toward 1–2.
- The cycle-5 escalations for those failures drop sharply.
- The mean cycle count for *non-API* failures (logic bugs, missing
  edge cases) is unchanged — the lookup edge is API-specific.

A follow-up measurement task (named in §11) instruments the cycle
log against the `lookup_log.jsonl` to validate or falsify this.

### 7.4 What `verify-quality` itself does NOT do

`verify-quality` is the gate runner; it does NOT call `doc-lookup`. The
edge is owned by the orchestrating skill (the chain) on the fix
re-spawn, not by the gate. This keeps `verify-quality` focused on its
single responsibility — measure, report — and concentrates the lookup
discipline in §4.6's single skill.

---

## 8. Interaction with REQ-PROC-001 (per-task lookup budget)

Lookups consume both tool calls (S1) and context tokens. The budget
follows REQ-PROC-001's signal model.

### 8.1 Per-lookup cost model

| Mode | Tool calls | Token cost |
|---|---|---|
| Cache hit (evidence (b)) | 1 (Read of log + jq scan) | ~0 — record summary already in context once |
| Evidence (a) — cache hash hit | 1 (Read of `.git/quality_green_hash`) | ~0 |
| Evidence (a) — targeted analyzer | 1 Bash call, 1–5s wall time | ~100 tokens (analyzer output) |
| Lookup via context7 (MCP) | 1 tool call | ~500–2000 tokens (result summary) |
| Lookup via official docs (`WebFetch`) | 1 tool call | ~1000–5000 tokens (page content) |
| Lookup via `WebSearch` (fallback) | 1–3 calls | ~2000–8000 tokens |

### 8.2 Per-task budget bands

Aligned with REQ-PROC-001's S1 bands (CLAUDE.md §7):

| Task class | Expected lookups | Token budget for lookups | Action when capped |
|---|---|---|---|
| Simple (S1 < 30 calls; closed scope; non-iterative) | ≤ 5 | ~10K tokens | None — within band. |
| Standard (S1 30–60; closed scope) | ≤ 10 | ~20K tokens | Escalation candidate via S1 — but lookups themselves are not the driver. |
| Complex (S1 > 60 OR open scope OR iterative) | ≤ 25 | ~50K tokens | When approached, the chain MAY split: a checkpoint that would exceed the budget routes the *finding* into a follow-up task ("This change requires lookups against N high-churn surfaces — recommend splitting"). |
| Synthesis-dependent | additive — synthesis lookups don't replace impl lookups | adds ~30K | Escalation via `opus_recommended: true`; budget remains lookup-side. |

### 8.3 Cap-driven escalation

When a `doc-lookup` invocation would push the task over its allowed
lookup count (counted by reading `lookup_log.jsonl` line count of
`decision: looked_up` records), the skill MUST:

1. Append a `budget_capped` record.
2. Return the "escalate" sentinel to the caller.
3. The caller (orchestrator) routes to `pending_feedback` per
   automated-mode rules — a question like *"Lookup budget capped at N
   for TASK-X — would you like to (a) raise the budget, (b) split the
   task, or (c) accept the remaining authoring decisions without
   upstream verification?"*.

This is the explicit **back-pressure on lookup volume itself** — a
mirror of the REQ-PROC-046 five-cycle bound, scoped to lookups
specifically. Without it, a chain with degraded `context7` coverage
could ratchet up cost indefinitely.

### 8.4 Interaction with model-escalation

Opus sessions (per REQ-PROC-001 AC-03 / AC-07) have more headroom but
also more capable judgment about when to skip vs. lookup. The budget
bands above assume Sonnet-default chains; Opus sessions can scale the
budget proportionally (~1.5×) — but no hard rule mandates it. Surfaced
as a deferred decision in §9 D6.

---

## 9. Decisions deferred to the user

The synthesis surfaces these for explicit user resolution before
follow-up impl tasks are created. None of them can be silently decided
inside this exploration without overstepping the goal.md constraints.

### D1 — `context7` integration path

§5 recommends the remote HTTP MCP endpoint at
`https://mcp.context7.com/mcp` via `.mcp.json`. Alternatives:

- *Option A (recommended)*: Remote HTTP MCP. Zero container footprint,
  automatic subagent propagation, no cold-start. Requires outbound HTTPS.
- *Option B*: Local stdio MCP via `npx @upstash/context7-mcp`. Works
  offline if the npm package is pre-cached; but adds Node child process,
  npm-cache dependency, and cold-start latency.
- *Option C*: REST API via `curl` / `WebFetch` from `doc-lookup` skill.
  No MCP dependency; but breaks subagent propagation (each agent would
  need its own Bash-based retrieval), and loses the two-tool contract.

The user decides. Option A is recommended unless outbound HTTPS is
restricted in the devcontainer (it currently isn't).

### D2 — `code-bugfix` skill-tool access

`code-bugfix` currently lists `tools: Bash, Read, Edit, Write` (no
`Skill`, no `Agent`). To invoke `doc-lookup` from inside the skill, it
must grow the `Skill` tool — OR the checkpoint logic is inlined into
the skill's instructions (no skill invocation, no log writing).

- *Option A*: Grow `Skill` on `code-bugfix`. Smallest surface change;
  the bugfix skill gains the same single-source checkpoint as the
  other chains.
- *Option B*: Inline the checkpoint logic in `code-bugfix` SKILL.md.
  Avoids the tool grant but duplicates logic and bypasses the
  `lookup_log.jsonl` write (Bash can append-write JSONL directly,
  but the dedup-key logic re-implements §4.2).
- *Recommended*: Option A — smaller code surface and consistent
  semantics across chains. The user decides.

### D3 — Lookup-log retention across release boundaries

`lookup_log.jsonl` lives in `<task>/plans_and_protocols/`. After
`task-complete`, the file is committed (per AC-08 of the automated-mode
escalation rule, and per the general "commit task artifacts" rule).
The question: do we *index* lookup logs across all closed tasks for
fallback-analysis purposes (gap reporting to `context7`, recurring
deprecation patterns), or do we leave them as per-task evidence and
rely on `grep` for cross-task analytics?

- *Recommended*: leave as per-task; a follow-up analytics task can
  surface trends. No central index needed in v1.

### D4 — Trigger thresholds (§6 tables) — open to user calibration

The trigger calibrations in §6 are this synthesis's best-effort
defaults. They will need empirical adjustment after 2–4 weeks of
real-world use. The user owns the calibration loop. No design
decision needed now; surfacing for awareness.

### D5 — Per-package allowlist for the "high-churn" classification

§6.2 names `flutter_secure_storage`, `sqlite3`, `cryptography`,
`argon2` as security-critical (every-call lookup). Should this list be
codified somewhere (`doc/cross_cutting_standards/documentation_lookup.md`?)
or left to skill heuristics?

- *Recommended*: codify in the cross-cutting doc; the SP-relevant
  package list is closed and small enough.

### D6 — Lookup budget scaling on Opus

§8.4 — does an Opus session get a 1.5× lookup budget multiplier
automatically, or stays at the Sonnet defaults?

- *Recommended*: no automatic multiplier; the user adjusts the goal.md
  `budget` field when needed. This keeps the gate visible.

### D7 — `lookup_log.jsonl` commit-message inclusion

Should the task's commit (created by `task-complete`) summarize the
lookup-log counts in its body (e.g. "8 lookups, 14 evidence skips, 0
fallbacks")?

- *Recommended*: yes. Cheap observability; helps the user spot
  regressions in lookup discipline over time.

### D8 — context7 privacy acceptability

context7 forwards every query to OpenAI, Anthropic, and Google Gemini
for reranking. Queries are stored anonymized for 30 days. For a private
mood tracker app:

- *Option A (recommended)*: Accept context7 with a query-sanitization
  constraint — `doc-lookup` strips file paths, domain identifiers, and
  anything project-specific from queries before forwarding. Queries
  contain only library names and public API topics.
- *Option B*: Reject context7 entirely and use only `WebFetch` against
  official doc sites. Loses the structured, version-indexed retrieval
  that context7 offers.
- *Option C*: Accept for public-API queries only; use a separate
  `WebFetch` path for security-critical packages (REQ-PROC-052 scope)
  where even the topic name could reveal architectural intent.

The user decides. Option A is recommended — the query surface is
inherently public (library names + public API topics), and
sanitization makes the risk negligible.

### D9 — context7 call-counting confirmation

Does one `resolve-library-id` + one `get-library-docs` count as 1
or 2 API calls against the monthly quota? The context7 docs are
ambiguous. This affects the §8.2 budget bands and the Free vs Pro
tier decision.

- *Action*: confirm with a test call once the API key is provisioned.
  If 2-per-lookup, the budget bands in §8.2 should halve (or the
  `doc-lookup` skill should cache resolved slugs per-task to avoid
  re-resolving).

---

## 10. Dependency-upgrade interface seam

The user is creating a separate task in a separate session for the
dependency-update mechanism. This exploration MAY identify the
interface — what REQ-PROC-053 operationalization needs to *assume*
about dependency-update behavior so the two designs compose cleanly.

### 10.1 What REQ-PROC-053 needs from the upgrade mechanism

| Assumption | Why this design depends on it | Failure mode if violated |
|---|---|---|
| The pinned version is readable from a single source per technology (`pubspec.lock` for Dart, `requirements.txt` / `pyproject.toml` / `uv.lock` for Python, build files for native, etc.) | §4.1's `pinned_version` field and §4.5's targeted-analyzer call both read this. | `doc-lookup` cannot anchor the lookup; AC-05 fails. |
| Pinned versions DO NOT change inside a task that isn't the dedicated upgrade task. The upgrade task IS a discrete unit of work that has the upgrade as its goal. | §4.4's cache invalidation discipline ("never within a task") assumes this. | Cached records become stale; agents act on outdated `result_summary`. |
| When AC-05 directs "replacement available at pinned version — use it directly", no upgrade-mechanism action is needed. The pinned version already contains the replacement. | §5 / §6.2's "high-churn" lookup discipline catches this in the lookup result. | None — fully contained inside REQ-PROC-053. |
| When AC-05 directs "TODO future version", the TODO comment is the only artifact written. The upgrade mechanism owns the TODO-discovery path on its own schedule. | Decouples this design from the upgrade flow. | If the upgrade mechanism does NOT scan for `TODO(<tech> <ver>)` comments, drift accumulates — but that's the upgrade mechanism's problem, not this design's. |
| The upgrade mechanism emits a discrete bump (a single commit / PR per version change) with an entry the next code-task can pick up. | §4.4's per-task cache discipline assumes "no bumps mid-task." | Same as above — would require mid-task invalidation, which this design explicitly excludes. |

### 10.2 What the upgrade mechanism needs from REQ-PROC-053 operationalization

| Provision | Form |
|---|---|
| Cross-task fallback log (the `WebSearch` fallback records — §4.8) is a signal that `context7` coverage is missing for that technology. The upgrade mechanism can use this signal when deciding which technologies to track for upgrades. | Read-only — grep for `decision: fallback_websearch` in past `lookup_log.jsonl` files. |
| TODO comments of the form `TODO(<technology> <version>): <one-line>` are written adjacent to call sites whose replacement API is not yet at the pinned version (AC-05). | Read-only — grep for `TODO(<technology>` across `lib/`. |
| Deprecation records (`trigger: deprecation` entries in `lookup_log.jsonl`) — a deprecation seen in a task is a candidate for an upgrade task. | Read-only — same grep target. |

### 10.3 What is explicitly NOT this design's problem

- *How* the upgrade mechanism decides to bump `pubspec.yaml`.
- *When* it runs (manual / scheduled / triggered-by-TODO-grep).
- *Who* it consults (other than re-using REQ-PROC-053's `doc-lookup`
  skill if it wants channel-consistent lookups during the bump).
- *How* the gate-set responds to a successful upgrade.

The interaction is one-directional: REQ-PROC-053 emits signals
(fallback records, TODOs, deprecation records); the upgrade mechanism
reads them. No coordination protocol, no shared state, no message bus.

---

## 11. Follow-up impl tasks the design implies

These are PROPOSED — not pre-created. The user reviews this synthesis
and decides which to spawn. Task IDs are reserved-but-not-allocated
(use `scripts/requirements/allocate_req_id.py` patterns at the
task-creation step).

### Tier 1 — Foundation (must land first; everything depends on these)

**TASK-PROC-053-03 — Create the `doc-lookup` skill**
- Type: impl
- Output: `.claude/skills/doc-lookup/SKILL.md`
- Implements: §4.1 (log record schema), §4.2 (dedup key), §4.3 (cache invalidation), §4.5 (toolchain-clean probe), §4.6 (skill API), §8.3 (budget cap)
- Effort: M
- Touches: `.claude/`, possibly small Python helper in `scripts/util/` for jsonl parsing

**TASK-PROC-053-04 — Wire `context7` integration**
- Type: impl
- Output: integration artifact per §5 (MCP `.mcp.json` entry OR CLI proxy script OR HTTP client in `scripts/util/`)
- Implements: §5 (channel chain), and feeds `doc-lookup`'s "lookup" branch
- Effort: S–M depending on D1
- Touches: `.mcp.json` OR `scripts/util/` OR `.claude/skills/doc-lookup/`

**TASK-PROC-053-05 — Cross-cutting `doc/` documentation**
- Type: impl
- Output: `doc/cross_cutting_standards/documentation_lookup.md` (the policy operationalization, including the log schema and channel chain reference)
- Effort: S
- Touches: `doc/`

### Tier 2 — Per-skill checkpoint wire-in (depends on Tier 1)

**TASK-PROC-053-06 — Amend `code-simple` with the `doc-lookup` checkpoint**
- Type: impl
- Implements: §4.7 row C1
- Effort: S
- Touches: `.claude/skills/code-simple/SKILL.md`

**TASK-PROC-053-07 — Amend `code-complex` with checkpoints (plan + per-batch)**
- Type: impl
- Implements: §4.7 row C2
- Effort: S
- Touches: `.claude/skills/code-complex/SKILL.md`

**TASK-PROC-053-08 — Amend `code-test` with the test-engineer checkpoint**
- Type: impl
- Implements: §4.7 row C3
- Effort: S
- Touches: `.claude/skills/code-test/SKILL.md`

**TASK-PROC-053-09 — Amend `code-bugfix` (slim + worktree) with the checkpoint**
- Type: impl
- Implements: §4.7 rows C4, C5 — RESOLVES D2 (Skill-tool grant)
- Effort: S
- Touches: `.claude/skills/code-bugfix/SKILL.md`
- Dependency: D2 must be answered before this task starts.

**TASK-PROC-053-10 — Update `implementation-engineer` agent**
- Type: impl
- Implements: per-agent invocation pattern of `doc-lookup`
- Effort: S
- Touches: `.claude/agents/implementation-engineer.md`

**TASK-PROC-053-11 — Update `test-engineer` agent**
- Type: impl
- Implements: per-agent invocation pattern of `doc-lookup`
- Effort: S
- Touches: `.claude/agents/test-engineer.md`

### Tier 3 — Per-technology tables (depends on Tier 1; parallel-safe with Tier 2)

**TASK-PROC-053-12 — Dart per-technology thresholds**
- Type: impl
- Implements: §6.2 + §6.7
- Effort: S
- Touches: `doc/architecture/` or `doc/cross_cutting_standards/`

**TASK-PROC-053-13 — Test-framework risk table**
- Type: impl
- Implements: §6.6
- Effort: S
- Touches: `doc/testing/test_framework_lookup_risk.md`

**TASK-PROC-053-14 — Python thresholds**
- Type: impl
- Implements: §6.3
- Effort: XS
- Touches: `doc/python/lookup_thresholds.md`

**TASK-PROC-053-15 — Native + CI + shell thresholds**
- Type: impl
- Implements: §6.4 + §6.5
- Effort: XS
- Touches: `doc/general/native_and_ci_lookup.md`

### Tier 4 — Cross-cutting wire-in (depends on Tier 2)

**TASK-PROC-053-16 — Wire gate-failure → lookup edge into orchestrator skills**
- Type: impl
- Implements: §7.2 — orchestrators (`code-simple` step 5, `code-complex` step 6, `code-test` step 5) read `quality-checker`'s STATUS line, classify the failure, prepend `doc-lookup` on the fix re-spawn
- Effort: M
- Touches: `.claude/skills/code-*/SKILL.md` (potentially `verify-quality` for richer failure-category reporting)

**TASK-PROC-053-17 — Update CLAUDE.md §7 / §8 with the lookup-budget framework**
- Type: impl
- Implements: §8.2 + §8.3
- Effort: XS
- Touches: `CLAUDE.md`

### Tier 5 — Measurement / observability (optional; depends on everything else)

**TASK-PROC-053-18 — Lookup analytics script**
- Type: impl
- Implements: §7.3 measurement (cycle-count × lookup count correlation), §4.8 fallback gap reporting
- Effort: M
- Touches: `scripts/util/` or new `scripts/lookup_analytics/`

**TASK-PROC-053-19 — Add lookup-log summary to commit messages**
- Type: impl
- Implements: D7 if accepted
- Effort: XS
- Touches: `.claude/skills/task-complete/SKILL.md` or `claude-commit`

---

## 12. Lookup notes (this task's own dogfooding)

Per goal.md §"Cache rule for THIS task itself", every upstream
documentation read this synthesis performed is recorded here.

(Note: this task itself authored a *design* — no in-line API call
emissions. The dogfooding scope is the synthesis's external reading,
not its design output. The synthesis writes about lookup mechanics
without itself emitting many lookups because the codebase reconnaissance
is what dominated the work.)

| Source | Reason | Channel |
|---|---|---|
| `requirements.md` @ commit `db92ca63` | AC text source of truth | git-only |
| `.claude/skills/code-*/SKILL.md` | chain mapping (§3) | repo-local |
| `.claude/agents/*.md` | agent inventory (§3.2) | repo-local |
| `.claude/skills/verify-quality/SKILL.md` | §4.5 cache-hash mechanism | repo-local |
| `requirements_tasks/.../code_quality/requirements.md` (REQ-PROC-046) | §7 interaction | repo-local |
| `requirements_tasks/.../context_window/requirements.md` (REQ-PROC-001) | §8 budget framework | repo-local |
| `doc/README.md`, `doc/cross_cutting_standards/`, `doc/general/` listings | §6.7 file-placement decisions | repo-local |
| `pubspec.lock` first lines | §4.5 version-string format | repo-local |
| `2026-05-26_01_prior_art_research.md` (subagent output) | §2 | research-agent delegated |
| `2026-05-26_02_context7_integration_research.md` (subagent output) | §5 + D1 | research-agent delegated |

No `WebFetch` or `WebSearch` was performed inline by this synthesis;
all external reading was delegated to subagents (§2 and §5).
