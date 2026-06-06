# Prior-Art Research — Documentation-Lookup Triggers in LLM Coding Tools

Date: 2026-05-26
Agent: general-purpose (research)

## Summary

Across the leading LLM coding tools, the documentation-lookup-trigger problem
is solved at three quite different levels of explicitness. **Cursor**,
**Continue.dev**, and **JetBrains AI Assistant** treat docs as an
indexed corpus the user (mostly) selects via `@Docs` / `@-mention`; retrieval
is RAG-style and silent — the agent rarely decides on its own to consult
upstream docs unless a context provider is wired and a rule says so.
**Aider** is at the opposite pole: it does *nothing* automatic, and exposes
two explicit primitives (`/web` for URL→markdown scrape, `/read-only` for
local files) plus an opportunistic "URL in chat → scrape" heuristic the user
controls. **Cline**, **Roo Code**, **Windsurf**, **Claude Code**, **Claude
Desktop**, **OpenAI Codex**, **VS Code Copilot**, **Gemini CLI** and ~30
other clients delegate the decision to whatever MCP server is configured —
the de-facto standard for "live upstream docs" is **context7**, whose
recommended client-side rule is *"Always use Context7 when I need library/API
documentation, code generation, setup or configuration steps without me
having to explicitly ask"*. **Replit Agent**, **Devin** and **Copilot
Workspace** lean on free-form web search with model-judged triggers.

The most important finding for our designer is the **trigger-rule gap**: no
public tool has solved the "look it up only when external evidence is
absent" problem the way REQ-PROC-053 wants. The two dominant patterns are
either (a) "always ask context7 for library questions" — cheap to specify,
costly to run, and lossy on dedup — or (b) "the agent decides" — which
collapses to "rarely look it up" because LLMs do not know what they do not
know (cf. Aider's docs and our own user notes). **context7 itself is a pure
channel; it owns neither the trigger nor the dedup; both have to be
implemented in the host skill.**

The second important finding is the **dedup gap across the skill→subagent
boundary**: none of the surveyed tools has a documented mechanism for
preventing the orchestrator skill *and* the spawned subagent from both
hitting the doc service. Claude Code's progressive-disclosure Skills model
(Level 1 metadata always loaded, Level 2 instructions only when triggered,
Level 3 resources on-demand) is the closest thing to a usable primitive —
the orchestrator-side SKILL.md can carry a "lookup-done sentinel" the
subagent reads before deciding. Devin's "Trigger Description"-based
just-in-time knowledge retrieval (`"Devin retrieves Knowledge when
relevant, not all at once or all at the beginning"`) is the closest thing
to a budgeting primitive but is opaque and not auditable. We will likely
have to invent the task-scope lookup log ourselves; nothing off the shelf
implements it.

## Tool-by-tool

### Aider

- **Channel:** explicit user commands only — `/web <url>` ("Scrape a
  webpage, convert to markdown and send in a message") and
  `/read-only <path>` for local docs / conventions files. Tips page
  explicitly invites the inline pattern: *"Include a URL to docs in your
  chat message and aider will scrape and read it. For example: `Add a
  submit button like this https://ui.shadcn.com/docs/components/button`."*
- **Trigger:** **never automatic.** The model is expected to ask the user
  for missing docs, and the user pastes a URL or runs `/web`. The Tips
  page acknowledges the underlying problem: *"LLMs know about a lot of
  standard tools and libraries, but may get some of the fine details
  wrong about API versions and function arguments"* — and pushes the burden
  to the user.
- **Cost-control:** none beyond "user only asks when they need it";
  scraped pages count as ordinary chat tokens; no per-task budget.
- **Cache / dedup:** none. A re-scraped URL is re-tokenised.
- **Skill→subagent boundary:** Architect/Editor mode does split work
  between two models (architect proposes, editor renders edits) but they
  share the chat history, so a URL scraped by the architect is visible to
  the editor. No explicit dedup logic — the shared transcript *is* the
  dedup mechanism.
- **Version-pinning:** none. Whatever URL the user passes is what the
  model sees. Users are expected to point at version-specific doc URLs by
  hand.
- **Test-code:** identical treatment — no distinction between code and
  tests for `/web` / `/read-only`.
- **Gate-failure → lookup:** does not exist as a built-in. Aider runs
  lint/test commands after edits and feeds output back to the model, but
  there is no rule "on AttributeError, web-search the symbol first";
  the model decides whether to guess or ask the user.
- **Sources:**
  - https://aider.chat/docs/usage/commands.html
  - https://aider.chat/docs/usage/tips.html
  - https://aider.chat/docs/usage/modes.html
  - https://aider.chat/docs/repomap.html

### Cursor

- **Channel:** built-in `@Docs` index over a curated set of third-party
  docs, plus user-added URLs (the URL is crawled and indexed locally on
  add). MCP servers (including context7) extend this.
- **Trigger:** primarily **user-initiated via `@Docs`** in the prompt.
  Agent mode can include docs via configured rules, but the default
  posture is "the user mentions it." From the community guide:
  *"@Docs extends the AI's knowledge beyond the local codebase by
  referencing official documentation for libraries and frameworks."*
- **Cost-control:** RAG with `nRetrieve` / `nFinal` reranking caps applied
  at the chunk level; codebase index re-syncs every 5 minutes; not a
  per-task budget but a per-query chunk cap.
- **Cache / dedup:** indexed once on add; re-indexed on demand; the user
  must explicitly re-trigger crawl to pick up upstream changes (this is
  a known pain point in the forum threads).
- **Skill→subagent boundary:** Cursor's agent mode is single-agent; the
  doc retrieval happens in the one process, so the boundary doesn't
  arise.
- **Version-pinning:** **none built-in.** The user is responsible for
  pointing `@Docs` at a versioned URL (e.g. the `v3.x` subtree of a doc
  site). If the upstream site is `latest`-only, Cursor will show
  `latest`. Recommended workaround in community guides is to use a
  `.cursorrules` file naming the pinned versions.
- **Test-code:** same retrieval pipeline; no special handling.
- **Gate-failure → lookup:** no explicit edge. The agent's retry loop
  feeds error output back, but the doc retrieval only re-fires if the
  follow-up prompt happens to contain `@Docs` or matches a configured
  rule.
- **Sources:**
  - https://cursor.com/docs/context/codebase-indexing
  - https://docs.cursor.com (`Cursor Settings > Features > Docs`)
  - https://forum.cursor.com/t/best-practices-for-private-documentation-indexing/26709
  - https://rudrank.com/exploring-cursor-accessing-external-documentation-using-doc

### Cline

- **Channel:** MCP-first. context7 is the recommended doc channel;
  any other MCP server (e.g. `arabold/docs-mcp-server`,
  `sammcj/mcp-package-docs`) also plugs in.
- **Trigger:** governed by the `Cline rules` / `.clinerules` file. The
  community-standard rule, copied from context7's own README, is
  *"Always use Context7 MCP when I need library/API documentation, code
  generation, setup or configuration steps without me having to explicitly
  ask"*. Without that rule the model decides; with it, the model is
  primed to call `resolve-library-id` + `query-docs` for any
  library-shaped question. Plan/Act modes do *not* themselves split doc
  retrieval — both can call MCP tools.
- **Cost-control:** none beyond the model's own restraint and the MCP
  server's response-size limits (context7 caps per-doc-chunk size on its
  side). No per-task cap surfaced in the system prompt.
- **Cache / dedup:** none in Cline; context7 caches *server-side*; the
  client re-asks each call. A repeat call within the same conversation
  *will* pay the full token cost again.
- **Skill→subagent boundary:** Cline does not currently spawn typed
  subagents; the rule applies to the one agent. The MCP tool listing in
  the system prompt is shared. If a plugin/subagent path were added, it
  would share the same MCP config but not the same conversation.
- **Version-pinning:** depends entirely on the MCP server. context7
  supports `/org/lib/<version>` slugs (e.g. `/supabase/supabase`), which
  the agent can encode in the call. Cline itself does not auto-derive
  the version from `package.json` / `pubspec.lock`.
- **Test-code:** no distinction.
- **Gate-failure → lookup:** no explicit edge. On lint/test failure the
  default is "the model retries"; whether it calls context7 next is up
  to the model.
- **Sources:**
  - https://github.com/cline/cline/tree/main/src/core/prompts/system-prompt
  - https://deepwiki.com/cline/cline/3.4-plan-and-act-modes
  - https://cline.ghost.io/5-tool-mcp-starter-pack-for-cline/
  - https://github.com/upstash/context7
  - https://www.augmentcode.com/mcp/context7

### Continue.dev

- **Channel:** the `@Docs` context provider is the first-class mechanism;
  documentation sites are added via URL and indexed using the configured
  embeddings provider. MCP servers (including context7) are an
  alternative second channel.
- **Trigger:** **user-initiated by typing `@Docs`** in the chat. There is
  *no* automatic per-request firing — the explicit context provider
  pattern is the design. Agent mode follows configured rules (e.g.
  "for `react-query` questions always include the `tanstack` docs"),
  but again, the rule has to be authored.
- **Cost-control:** `nRetrieve` (docs fetched from embedding query),
  `nFinal` (returned after rerank), `useReranking` flag — explicit
  per-query chunk-cap parameters. GitHub indexer is rate-limited to 60
  req/hr unless a token is provided.
- **Cache / dedup:** doc index is persistent; *switching embeddings
  provider triggers a full re-index*. Same-session repeated `@Docs`
  retrieval is not deduplicated — each `@Docs` mention runs the
  retrieval pipeline again.
- **Skill→subagent boundary:** Continue's "Agent mode" is single-process;
  no subagent boundary today. Slash commands and tools all share the
  same context window.
- **Version-pinning:** none structural; the user pins by choosing the
  versioned URL when adding the doc site.
- **Test-code:** same handling.
- **Gate-failure → lookup:** no explicit edge.
- **Sources:**
  - https://docs.continue.dev/customize/context/documentation
  - https://docs.continue.dev/customize/deep-dives/docs
  - https://docs.continue.dev/guides/codebase-documentation-awareness
  - https://docs.continue.dev/reference

### GitHub Copilot Workspace (and Copilot agent / Copilot CLI)

- **Channel:** in Workspace's plan/implement/test loop, doc lookup is
  *not a first-class step* — the spec/plan/diff artefacts are the focus.
  In Copilot CLI and Copilot Coding Agent, MCP (including context7) is
  available via `~/.copilot/mcp-config.json` (CLI) or repo-level config
  (Coding Agent).
- **Trigger:** in Workspace, the agent uses the integrated terminal to
  *execute* (which implicitly tests against the real library), but does
  not explicitly fetch upstream docs. In MCP-equipped Copilot, the same
  context7-style rule applies: model decides, optionally primed by a
  rule.
- **Cost-control:** none specific to docs.
- **Cache / dedup:** none documented.
- **Skill→subagent boundary:** Workspace's plan→implement→test is a
  three-phase single-agent loop; specs and plans persist as editable
  artefacts in the UI, so a doc fact discovered at "plan" is visible to
  "implement" via the spec text.
- **Version-pinning:** none.
- **Test-code:** identical handling (the "test" phase is just running
  the model-generated tests).
- **Gate-failure → lookup:** Workspace's test step can fail and the user
  edits the plan; no automatic "go look it up" rule.
- **Sources:**
  - https://github.com/githubnext/copilot-workspace-user-manual
  - https://github.com/githubnext/copilot-workspace-user-manual/blob/main/overview.md
  - https://docs.github.com/en/copilot/tutorials/plan-a-project
  - https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices

### Claude Code (this project's host)

- **Channel:** `WebFetch` (URL → answered question) and `WebSearch`
  (query → list of `{title, url}`) are the built-in primitives. MCP
  servers extend this (context7 is a first-class supported client per
  the context7 client list). Skills carry their own SKILL.md
  instructions and can reference URLs.
- **Trigger:** model-decided. `WebFetch` *requires* a URL the user
  supplied earlier in the conversation or that came from an earlier
  `WebSearch` / `WebFetch`: *"Claude can only fetch URLs that have been
  explicitly provided by the user or that come from previous web search
  or web fetch results."* — this is a hard injection-resistance bound,
  not a doc-policy rule. There is no built-in "consult docs by default"
  rule; that has to come from CLAUDE.md, a Skill, or an MCP rule.
- **Cost-control:** `WebFetch` is summarised by Claude 3.5 Haiku and
  returns just an answer + metadata (cap ~125-char verbatim quote),
  truncated to 100KB of source markdown; **15-minute TTL cache per URL**.
  `WebSearch` returns title+URL only (page bodies discarded), forcing
  an explicit second `WebFetch` if the body is needed. This split is
  itself a cost-control pattern.
- **Cache / dedup:** the 15-min URL TTL is the only built-in cache; it
  is opaque to skills. No cross-skill / cross-subagent dedup.
- **Skill→subagent boundary:** Skills load progressively (Level 1
  metadata always; Level 2 SKILL.md only when triggered; Level 3
  files on-demand via bash). A skill can write to the filesystem,
  which is the only durable channel the subagent can see — *this is
  the seam where our task-scope lookup log can live*. The subagent
  inherits no `WebFetch` cache from the parent; only files on disk
  cross the boundary.
- **Version-pinning:** none built-in. CLAUDE.md and Skills can prescribe
  it; nothing enforces it.
- **Test-code:** identical handling.
- **Gate-failure → lookup:** the `verify-quality` skill in this project
  already turns gate failures into a back-pressure loop, but does not
  today flip the next attempt to "lookup-first". This is an
  intervention point REQ-PROC-053 should claim.
- **Sources:**
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
  - https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool
  - https://mikhail.io/2025/10/claude-code-web-tools/
  - https://code.claude.com/docs/en/skills
  - https://context7.com/docs/resources/all-clients
  - https://websearchapi.ai/blog/claude-code-web-search-agent-skills

### Tier-2 (compact form)

**Devin** — Knowledge tab with **Trigger Descriptions**: free-text
phrases the agent matches against current work to decide whether to
load a knowledge item. *"Devin retrieves Knowledge when relevant, not
all at once or all at the beginning."* No deduplication or budget
documented. Macros (`!my-knowledge`) let humans pin a knowledge item
into a prompt. Devin also has general web-browsing for documentation
("look up documentation, install packages, run shell commands, read
error logs"). Source: https://docs.devin.ai/product-guides/knowledge ;
https://cognition.ai/blog/devin-2 .

**Sourcegraph Cody** — `@-mentions` for repo/file/symbol; keyword
search + Sourcegraph Search API + Code Graph; "smart context-fetching"
for built-in commands. Custom Commands can include CLI tool calls and
prompt templates. No explicit doc-lookup heuristics for upstream APIs;
relies on indexed repo content. Source:
https://sourcegraph.com/docs/cody/capabilities/commands ;
https://sourcegraph.com/docs/cody/core-concepts/context .

**Replit Agent** — `Web Search` is on by default; *"Agent automatically
determines when to use Web Search based on your requests"* — fully
model-judged. Trigger keywords like "search" / "research" force-fire.
Citations are returned. No version-pinning. Source:
https://docs.replit.com/core-concepts/agent/web-search ;
https://blog.replit.com/web-search .

**Tabnine** — completion-time context retrieval over local workspace +
optional "Enterprise Context Engine"; documentation lookup is a
keyboard-shortcut feature on a suggestion (LSP-hover-like). No
agentic upstream doc fetch in the standard product. Source:
https://docs.tabnine.com/main/welcome/readme/ai-models ;
https://docs.tabnine.com/main/getting-started/getting-the-most-from-tabnine-chat/chat-context/context-scoping .

**Codeium Windsurf / Cascade** — Cascade tool palette includes Web
Search, MCP, and "parse and chunk web pages and documentation"; the
`.windsurfrules` file is the recommended place to declare stack
versions (manual pinning). Trigger is model-judged. Source:
https://docs.codeium.com/windsurf/cascade ;
https://deepwiki.com/jujumilk3/leaked-system-prompts/2.2-codeium-cascade-and-windsurf-ide .

**Roo Code** — system prompt is assembled dynamically; MCP server tools
are inlined into the prompt with descriptions + parameter schemas;
`use_mcp_tool` is the actual call. Modes (Architect, Code, Debug,
Ask…) toggle which tool subsets are included. Trigger is model-judged,
guided by mode + rules + MCP descriptions. Source:
https://docs.roocode.com/features/mcp/using-mcp-in-roo ;
https://deepwiki.com/jasonkneen/Roo-Code/4.1-system-prompt-generation .

**OpenHands / OpenDevin** — agent loop with browse + execute + write;
the agent can "browse documentation" as one of its action types,
purely model-judged when to do so; no doc-specific budget or cache.
Source: https://arxiv.org/abs/2407.16741 ;
https://www.openhands.dev/ .

**JetBrains AI Assistant** — `/docs` slash-command restricts retrieval
to the IDE's own documentation via RAG (as of 2024.3). External
library docs are reached via MCP (Streamable HTTP transport). No
auto-trigger; user invokes. Source:
https://www.jetbrains.com/help/ai-assistant/about-ai-assistant.html ;
https://blog.jetbrains.com/ai/2025/02/doc-powered-ai-assistant/ ;
https://www.jetbrains.com/help/ai-assistant/mcp.html .

## context7 ecosystem

context7 (Upstash) is the present-day standard for "agent reads
up-to-date version-specific library docs." Its design:

- Two MCP tools: `resolve-library-id` (free-text → `/org/lib` slug)
  and `query-docs` (slug + optional version + topic → markdown
  excerpt). CLI equivalents: `ctx7 library`, `ctx7 docs`.
- Versioning by slug: `/supabase/supabase`, optional version
  suffix; the agent must encode the version it wants.
- Trigger: **client-side rule** is the only mechanism. Recommended
  rule (carried in setup skills installed by `ctx7 setup`):
  *"Always use Context7 MCP when I need library/API documentation,
  code generation, setup or configuration steps without me having
  to explicitly ask."* — `alwaysApply: true` in the rule frontmatter
  evaluates against every prompt.
- Server-side caching/freshness: opaque to clients; clients re-call
  every time.

Confirmed integrations (per https://context7.com/docs/resources/all-clients):
Claude Code, Cursor, Opencode, OpenAI Codex, Google Antigravity, VS
Code, Kiro, Kilo Code, Roo Code, Windsurf, Claude Desktop, ChatGPT
(via Developer Mode connectors), Trae, Cline, Augment Code, Gemini
CLI, Hermes, Copilot Coding Agent, Copilot CLI, Amazon Q Developer
CLI, Warp, Amp, Zed, Smithery, JetBrains AI Assistant, Qwen Code,
Docker, LM Studio, Visual Studio 2022, Crush, BoltAI, Rovo Dev CLI,
Zencoder, Qodo Gen, Perplexity Desktop, Factory, Emdash. Auth via
`CONTEXT7_API_KEY` header or OAuth.

Open-source alternatives worth knowing about for fallback / private-doc
indexing: `arabold/docs-mcp-server` (positions as "open-source
alternative to Context7, Nia, Ref.Tools" — supports version-pinned
indexing and local content), `sammcj/mcp-package-docs` (multi-language
package docs MCP). Sources:
https://github.com/arabold/docs-mcp-server ;
https://github.com/sammcj/mcp-package-docs .

## Patterns worth stealing

- **Two-tool split (resolve-id → fetch-doc), context7**: the
  resolve-id step is cheap and dedup-friendly; once a task has resolved
  `/dart-lang/sdk@3.5.0`, every later lookup in the same task can reuse
  the slug without re-resolving. Our task-scope lookup log should store
  the resolved slug as its primary key.
- **Question-bound `WebFetch`, Claude Code**: requiring a *question* with
  the URL and returning only the answer (Haiku-summarised, ≤125-char
  verbatim quotes, 100KB hard cap) is the single best cost-control
  pattern surveyed. Steal the shape: a doc-lookup call returns "answer +
  source URL + answered question," not raw markdown.
- **15-minute URL cache, Claude Code**: short TTL is correct for live
  docs; per-task log can rely on it for the "exact same URL within the
  task" case and worry only about semantic dedup.
- **Progressive disclosure, Claude Skills**: SKILL.md → on-demand files
  → on-demand bash output is the architecture that makes a single
  checkpoint per chain feasible. The orchestrator-side skill can
  *describe* the checkpoint in metadata (Level 1); the subagent only
  reads the lookup log when it actually needs to (Level 3 from the
  subagent's POV).
- **Trigger Description, Devin**: free-text trigger phrases — *"Devin
  retrieves Knowledge when its current work is related to the specified
  triggers"* — are a usable spec language for "fire the lookup when the
  task touches X." Worth borrowing the *form* (a triggers field on each
  skill) even if the *mechanism* (semantic match against current work)
  needs an explicit list of API-surface symbols in our case.
- **Rule-as-data, context7/cline**: `alwaysApply: true` rule frontmatter
  is a clean way to declare "this rule fires unconditionally," and it
  composes with mode/skill-scoped rules. Worth borrowing for our
  per-skill checkpoint declarations.
- **Versioned slugs, context7**: encode the version *in the lookup
  identifier* rather than as a side parameter. Makes pubspec.lock-driven
  pinning straightforward: derive the slug from the lockfile and the
  dedup key naturally includes the version.
- **WebSearch + WebFetch split, Claude Code**: WebSearch returns
  `{title, url}` only; force a second WebFetch to commit to a page.
  This pattern is itself a cost gate. Apply to our flow: a "is there
  a doc page for X?" probe is cheap; a "what does the doc say about
  X" call is expensive and gets logged.

## Anti-patterns to avoid

- **"Always look it up" rule with no dedup, context7-default-rule on
  Cline/Cursor**: the recommended rule fires on *every* library-shaped
  question. Without a task-scope log this causes 5-10× redundant
  lookups per task; users in the community threads complain about
  token spend. Avoid by making the rule "look it up *unless* the log
  has an unexpired entry."
- **Model-judged trigger, Replit Agent / Aider implicit / Codex**: "the
  agent decides when to fetch docs" collapses to "the agent rarely
  fetches docs," precisely because LLMs do not know what they do not
  know — the same hallucination-confidence problem our user flagged.
  Avoid by externalising the trigger (in-repo evidence check, lockfile
  pin check, gate-failure trip) rather than asking the model.
- **User-initiated only, Cursor / Continue / Aider**: relying on the
  user to type `@Docs` or paste a URL means the lookup happens for
  *interactive* sessions and never for *autonomous* sessions (our
  automated orchestrator). Avoid by making the trigger declarative in
  the skill, not interactive.
- **Opaque cache, context7 server-side**: server-side caching is
  invisible to the client, so the same call from skill *and* subagent
  pays full token cost twice. Avoid by keeping the dedup decision in
  *our* task-scope log, not delegating it to the server.
- **No version-pinning, every surveyed tool**: every tool puts the
  burden of version-pinning on the user (Cursor's `.cursorrules`,
  Windsurf's `.windsurfrules`, Continue's user-added URL, context7's
  slug). Avoid by *deriving* the version from `pubspec.lock` and
  passing it in the lookup ID — make it impossible to forget.
- **No gate-failure edge, all surveyed tools**: not one tool wires
  "lint/test failed because of an unknown symbol" → "next attempt
  reads docs first." The default is retry-and-guess. Avoid by making
  REQ-PROC-046's back-pressure loop set a "lookup-required" flag on
  the next attempt when the failure mode is API-shaped.
- **No skill→subagent dedup, all surveyed tools**: nothing in prior art
  prevents both the orchestrator and the spawned subagent from looking
  up the same symbol. Aider's architect/editor split escapes this only
  because they share the chat. We have to design this — the
  task-scope log file is the obvious mechanism, but the *protocol*
  (read-before-call, append-after-call, cache key = `{slug, version,
  symbol}`) is novel.

## Open questions surfaced by the research

- **What is the cache key?** Options: `{library-id}`, `{library-id,
  version}`, `{library-id, version, symbol}`, `{library-id, version,
  symbol, question-hash}`. context7's slug + version is the natural
  resolve-id key; the symbol/question grain is the one we have to pick.
  The right answer probably differs between "I want the migration
  guide" (coarse) and "I want the signature of `X.foo`" (fine).
- **What invalidates the cache within a task?** TTL (mirror Claude
  Code's 15-min)? Pubspec.lock mtime? Explicit user `/refresh`? A
  task-scope log without invalidation is fine because the task is
  short-lived, but the *cross-task* layer needs a policy.
- **Where does the log file live?** Inside the task folder
  (`plans_and_protocols/lookup_log.jsonl`) — natural fit with our
  existing memory model, survives subagent boundary via filesystem,
  visible to verify-quality. Alternative: `~/.cache/...` per-user, but
  that loses the per-task scope.
- **How does the gate-failure edge encode "API-shaped"?** Heuristic on
  the analyzer output (`uri_does_not_exist`, `argument_type_not_assignable`,
  `undefined_method`, `deprecated_member_use`) → set the flag. This is
  language-specific; needs a per-toolchain mapping table.
- **Subagent contract:** does the subagent's SKILL.md instruct it to
  read the log unconditionally, or only when about to call an external
  doc tool? The cheaper option is the latter, with the orchestrator
  guaranteeing the log is fresh before spawning.
- **context7 absence handling:** if context7 is unreachable (network,
  rate-limit, library not indexed), do we fall back to `WebFetch`
  against the upstream doc site, or block the task? The orchestrator's
  back-pressure protocol already has a five-cycle bound; the doc
  lookup should plug into that, not invent its own.
- **Test code special-case (or not):** REQ-PROC-053 says the rule
  applies to tests too. Prior art unanimously gives tests no special
  treatment. Open question: do we add an exemption for *test
  scaffolding* calls (the test framework's own API) so we don't
  duplicate-lookup `expect`/`group`/`test` on every TDD step? Probably
  yes, via an allowlist of "framework-of-record" symbols in the log
  bootstrap.
- **One-checkpoint-per-chain placement:** the user's AC-07 says one
  checkpoint per authoring chain. The natural placements per skill
  type: for `code-simple` / `code-complex` / `code-test` it is the
  *plan* step (before the implementer subagent runs). For
  `code-bugfix` it is the *diagnosis* step. For `task-resolve` it is
  the *first impl step*. Synthesis needs to enumerate these
  placements and the corresponding log-key convention.
- **Interaction with REQ-PROC-001 per-task lookup budget:** how do we
  count? Per `query-docs` call? Per unique resolved slug? A budget
  measured in *unique slugs* is more robust than one measured in
  *calls* because the log naturally bounds the call count.
