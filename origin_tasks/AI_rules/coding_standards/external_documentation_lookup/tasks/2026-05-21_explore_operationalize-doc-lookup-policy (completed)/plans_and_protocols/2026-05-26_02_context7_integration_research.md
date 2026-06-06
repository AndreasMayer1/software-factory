# context7 Integration Research

Date: 2026-05-26
Agent: general-purpose (research)

## Summary

context7 (built and operated by Upstash) is a hosted, LLM-indexed documentation service that ships **five distinct integration paths**: (1) a first-party MCP server distributed as the npm package `@upstash/context7-mcp` for stdio transport, (2) a fully-hosted **remote MCP endpoint at `https://mcp.context7.com/mcp`** that any MCP-aware agent can talk to over HTTP (no local Node process), (3) a public REST API rooted at `https://context7.com/api/v1` and `/api/v2` (Bearer-token authenticated), (4) a CLI named `ctx7` (also distributed via npm — `npm install -g ctx7` or `npx ctx7 …`) that doubles as an interactive setup wizard for the MCP server across most popular agents, and (5) a TypeScript SDK plus an AI-SDK-compatible tool wrapper (`Context7Agent`, `resolveLibraryId`, `queryDocs`). All four runtime paths converge on the same two-step retrieval contract — `resolve-library-id` → `get-library-docs` (a.k.a. `query-docs`) — and all are gated by the same `ctx7sk-`-prefixed API key.[^overview][^api-guide][^all-clients][^cli-docs][^llms-txt]

The service exists because LLMs hallucinate APIs from stale training data; context7 grounds them with version-specific, recently-crawled snippets. The standard activation pattern is the **"use context7" sentinel** appended to a prompt — the MCP client sees the phrase, resolves the library mentioned in the same prompt, and injects a few thousand tokens of authoritative docs before the model answers. Free-tier accounts get 1,000 API calls/month (anonymous callers share a 60-req/hour pool); Pro is $10/seat/month for 5,000 calls; queries are anonymized and retained 30 days but are forwarded to OpenAI, Anthropic, and Gemini for reranking — a material privacy fact for any project that handles sensitive prompts.[^plans][^data-privacy][^auth-keys]

For a Linux-devcontainer Claude Code workflow with subagent spawning, the most attractive option is the **remote HTTP MCP endpoint** wired into the project's `.mcp.json`: it has zero local install footprint, survives container rebuilds, propagates to every subagent that inherits the project's MCP config, and removes Node-version drift. The stdio `npx @upstash/context7-mcp` variant is a viable fallback if outbound access to `mcp.context7.com` is ever blocked. WebFetch against the REST API remains useful as a last-resort retrieval path that doesn't need MCP at all.[^claude-code-docs][^all-clients][^decodesfuture]

## Integration paths

### MCP server

**Distribution.** Two simultaneous shapes:

1. **Local stdio** — npm package `@upstash/context7-mcp` (published by Upstash), run on demand with `npx -y @upstash/context7-mcp`. Requires Node ≥ 18 on the host that launches the agent (Claude Code documentation guides assume `npx` is on `$PATH`).[^npm-page][^decodesfuture]
2. **Hosted remote** — the URL `https://mcp.context7.com/mcp` accepts the standard streamable-HTTP MCP transport. No local process; auth is via the `CONTEXT7_API_KEY` header.[^all-clients]
3. There is also an unofficial **Docker image** `mcp/context7` in the Docker Hub MCP catalog, though all upstream docs steer users toward `npx` or the remote URL.[^docker-hub]

**Installation (Claude Code, project scope).** The verbatim `.mcp.json` snippets from `https://context7.com/docs/resources/all-clients`:

```jsonc
// Local (stdio via npx)
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"]
    }
  }
}
```

```jsonc
// Remote (HTTP)
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "CONTEXT7_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

The CLI shortcut `claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key YOUR_API_KEY` writes the stdio form into `~/.claude.json` (user scope) or `.mcp.json` at the project root (`--scope project`). The interactive wizard `npx ctx7 setup --claude` will do this for you and also install the Anthropic plugin marketplace bundle `/plugin install context7-plugin@context7-marketplace`, which adds a `docs-researcher` subagent and a `/context7:docs` slash command.[^claude-code-docs][^decodesfuture]

**Tool surface (the only two tools the model sees):**

| Tool | Parameters | Purpose |
| --- | --- | --- |
| `resolve-library-id` | `libraryName` (string, required), `query` (string, required — used for relevance ranking) | Translate a free-form library name (`"flutter"`, `"riverpod"`, `"next.js"`) into a Context7 ID such as `/flutter/flutter` or `/vercel/next.js`. Must be called first unless the user already supplied the slash-form ID. |
| `get-library-docs` (alias `query-docs` in newer builds) | `context7CompatibleLibraryID` (required, e.g. `/mongodb/docs`), `topic` (optional, e.g. `"routing"`), `tokens` (optional, default 5000; values < 1000 are bumped to 1000) | Return ranked documentation snippets and code samples for that library. Versions are addressed inline in the ID: `/owner/repo/v15.1.8` or `/owner/repo@v15.1.8`. |

These two tools cover 100% of retrieval; everything else (library submission, refresh, policies) is REST-only.[^deepwiki-resolve][^api-guide]

**Configuration schema.** Required: `CONTEXT7_API_KEY` (env var or `--api-key` flag or `CONTEXT7_API_KEY` HTTP header). All keys begin with `ctx7sk-`. Optional CLI flags on `@upstash/context7-mcp` include `--transport` (`stdio` default, `http`/`sse` for hosted-mode parity), `--port`, and `--api-key`.[^auth-keys][^decodesfuture]

**Authentication model.** OAuth 2.0 in the browser (via `ctx7 login`) or API-key Bearer auth. Keys are shown once at creation, can be named for traceability, and revoked irreversibly from the dashboard. There is no documented per-key scope mechanism (key = full account access within rate limits).[^auth-keys]

**Offline behavior / failure modes.** The MCP server is a thin RPC client over the public API; without internet it cannot answer. On 429 (rate limit) responses propagate `Retry-After`, `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` headers. On 301 the response carries `redirectUrl` (e.g. when a library ID has been renamed). When no key is configured, the server still works but every request shares an anonymous 60-req/hour bucket — easy to exhaust during a long agent run.[^api-guide][^auth-keys]

**Cost model.** Per-API-call. Free: 1,000 calls/month + 20 daily bonus calls if blocked. Pro: $10/seat/month → 5,000 included → $10 per additional 1,000. Private-repo parsing is metered separately at $25/M tokens. A "call" appears to correspond to one tool invocation (one `resolve-library-id` + one `get-library-docs` = two calls).[^plans]

**Devcontainer compatibility.** Both transports work from inside a Linux container as long as outbound HTTPS to `mcp.context7.com` (remote) or to the npm registry (stdio cold-start downloads the package) is allowed. The remote variant is preferable in containerized environments where security policies restrict child-process execution.[^decodesfuture]

**Latency.** No published SLO. Anecdotally (multiple integration guides) cold-start of the stdio variant is dominated by the first `npx` download (a few seconds). Warm calls — including the remote HTTP form — typically resolve in well under a second for popular libraries because Context7 reranks against precomputed embeddings before forwarding the top results to an LLM reranker (OpenAI/Anthropic/Gemini) for final ordering.[^data-privacy]

### HTTP / REST API

Yes, fully exposed and documented at `https://context7.com/docs/api-guide`. Authentication header: `Authorization: Bearer ctx7sk-…`. Twelve+ endpoints across `/api/v1` and `/api/v2`:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v2/libs/search` | Find libraries by name |
| GET | `/api/v2/context` | Retrieve documentation snippets for a library (the REST equivalent of `get-library-docs`) |
| POST | `/api/v1/refresh` | Trigger reindex of a library |
| GET/PATCH | `/api/v2/policies` | Teamspace policy CRUD |
| POST | `/api/v2/add/repo/{provider}` | Submit a GitHub/GitLab/Bitbucket repo |
| POST | `/api/v2/add/openapi`, `/add/openapi-upload` | Submit an OpenAPI spec by URL or upload |
| POST | `/api/v2/add/llmstxt` | Submit an `llms.txt` file |
| POST | `/api/v2/add/website` | Crawl an arbitrary website |
| POST | `/api/v2/add/confluence` | Index a Confluence space |

Responses are JSON (the GET-context endpoint accepts a `type=json` parameter; markdown is the default body of the snippet field). Rate limits surface via `Retry-After` + `RateLimit-*` headers and 429 on overflow; redirects return 301 with a `redirectUrl` field. Full OpenAPI spec is published at `https://context7.com/docs/openapi.json`, making this directly consumable by `WebFetch`, `curl`, or any HTTP client.[^api-guide][^llms-txt]

### CLI tool

Yes — `ctx7`, distributed as npm package `ctx7` (separate from the MCP package). Install with `npm install -g ctx7` or invoke ad-hoc via `npx ctx7 …`. Authentication via `ctx7 login` (browser OAuth) or `CONTEXT7_API_KEY` env var.[^cli-docs]

Subcommand surface:

- `ctx7 library <query>` — search the index by name.
- `ctx7 docs <libraryId> <query>` — fetch documentation by ID.
- `ctx7 setup [--claude|--cursor|--opencode|--antigravity|--universal] [--mcp|--cli] [--api-key …] [--global|--project] [--yes] [--no-browser]` — interactive wizard that registers either the MCP server or the CLI-+-Skills mode in the chosen agent. `--claude` writes the right snippet to `.claude/` for Claude Code.
- `ctx7 remove` — uninstall.
- `ctx7 skills install|search|suggest|generate|list|info|remove` — manage Upstash-style skills.
- `ctx7 login`, `ctx7 whoami`, `ctx7 logout`.

Output is human text by default; `--json` switches to structured output and TTY detection auto-disables colors when piped. Useful as a Bash-callable retrieval shim for skills that don't want to go through MCP.[^cli-docs]

### Library SDKs

- **TypeScript SDK** — official, published by Upstash. Exposes `getContext(libraryId, …)` and `searchLibrary(name)` commands; ships an AI-SDK-compatible tool bundle (`Context7Agent`, `resolveLibraryId`, `queryDocs`). Documented under `/docs/sdks/ts/` and `/docs/agentic-tools/ai-sdk/`.[^llms-txt]
- **Python / Dart SDKs** — none discovered in the official sitemap or on npm/PyPI. Python users go through the REST API or MCP. There is no pub.dev `context7` client package (and `context7` itself is not a pub.dev package — it's a service).

### Prompt convention

The **`use context7`** sentinel is the canonical trigger. Mechanism:

- The MCP client (Claude Code, Cursor, etc.) sees the literal phrase anywhere in the user message.
- Without the sentinel, MCP clients still expose the tools, but most agents only invoke them on explicit cue or when a library is asked about by name in conjunction with the sentinel.
- Variants accepted by the upstream docs include `"use context7"`, `"get the docs using context7"`, and explicit `"use library /supabase/supabase"` to skip resolution.
- The new Claude Code **plugin/skill** bundle (`/plugin install context7-plugin@context7-marketplace`) installs an Anthropic-style skill that triggers automatically on library-related queries, removing the need to type the sentinel.[^claude-code-docs]
- Equivalent Cursor / Cline / Continue setups recommend adding an "agent rule" or system-prompt line saying "always call context7 for code questions about external libraries."[^upstash-blog]

For this project, the cleanest enforcement is a **skill instruction** ("when answering a question about an external library, prepend `use context7` to the synthesized query") rather than relying on the user to remember.

## Coverage assessment

**Indexing model.** context7 ingests from GitHub / GitLab / Bitbucket repos, arbitrary websites (crawl), `llms.txt` files, OpenAPI specs, Confluence, and Notion. Library owners can claim their library for higher refresh rates; anyone can submit a URL via `POST /api/v2/add/*`.[^api-guide][^llms-txt]

**Languages / ecosystems known to be covered well.** The platform is language-agnostic — anything with a GitHub repo or a website can be indexed. Public guides repeatedly cite Next.js, Supabase, MongoDB, Cloudflare Workers, React, FastAPI, LangChain, and the major JS frameworks as canonical examples. The example IDs in the docs (`/vercel/next.js`, `/mongodb/docs`, `/supabase/supabase`) confirm a JS-heavy bias.[^github-readme][^upstash-blog]

**Flutter / Dart specifically.** Neither the official README nor the marketing pages call out Flutter or Dart by name. The library page `https://context7.com/flutter` exists structurally but our fetch returned only the navigation chrome (no snippet count was renderable to WebFetch — the search index likely populates client-side). Empirically, library IDs of the shape `/flutter/flutter` (for the SDK), `/flutter/website`, `/dart-lang/sdk`, and per-package `/<owner>/<repo>` slugs (e.g., `/rrousselGit/riverpod`, `/felangel/bloc`) are the expected pattern given the GitHub-source convention. **Verification action for the project**: hit `GET https://context7.com/api/v2/libs/search?query=flutter` once with a real API key to enumerate.

**Other ecosystems the project might touch:**

- **pub.dev packages**: not directly ingested. Coverage depends on whether the package's GitHub repo is indexed (most popular ones are).
- **GitHub Actions**: covered insofar as action repos are indexable as GitHub repos; no dedicated marketplace ingestion is documented.
- **Android Gradle / AGP**: same — depends on whether `android/gradle` repos are individually indexed.
- **Python stdlib**: not in scope; context7 indexes third-party libraries, not language stdlibs (the Python stdlib docs would need to be submitted as a website or `llms.txt` to appear).

**Known gaps.** Anything not on a public Git host or a crawlable website needs explicit submission. Private repos require Pro + extra parsing fees ($25/M tokens). Documentation that lives only in PDFs or Discord channels is invisible.

## Freshness, versioning, pricing, privacy

**Freshness.** Popularity-tiered automatic refresh thresholds: Top-100 libraries every 1 day, Top-1,000 every 15 days, Top-5,000 every 30 days, everything else every 45 days. Refresh only fires when a library has been queried recently AND its docs are older than the threshold. Manual refresh available via `POST /api/v1/refresh` or the library page (claimed-library owners get higher refresh limits). Private libraries are manual-only.[^library-updates]

**Versioning.** Inline in the library ID: `/owner/repo/v15.1.8` or `@v15.1.8`. The model can ask for a specific version directly, and context7 will match it if that version's docs were captured. Prompts like `"Next.js 14 middleware"` are parsed to select the correct version automatically.[^api-guide][^deepwiki-resolve]

**Pricing.** Already enumerated above. Headline: Free = 1k calls/month, Pro = $10/seat → 5k calls then $10/k, Enterprise scales down per-seat with volume; private-repo parsing at $25/M tokens; **anonymous (no key) = 60 req/hour shared globally** — fine for personal experimentation, hopeless for an automated factory pipeline.[^plans]

**Privacy.** Material findings from `https://context7.com/docs/security/data-privacy`:

- **Queries are stored anonymized for 30 days** (API logs) and used to benchmark retrieval quality.
- Queries are **forwarded to OpenAI, Anthropic, and Google Gemini for reranking** — i.e., a third-party LLM sees every prompt that triggers context7. For a "private mood tracker" project, this is the single most important constraint to surface: even though the local prompt may concern Flutter widgets, anything the agent appends (file names, error traces, identifiers) leaves the project boundary.
- Storage in Upstash's SOC-2 Type II infrastructure (US and EU regions).
- HTTP-transport client IPs are AES-256-CBC-encrypted for rate-limit accounting (no raw-IP retention).
- GDPR: access, deletion, portability rights advertised.
- TLS 1.2+ in transit; encryption at rest.[^data-privacy]

## Failure modes & offline behavior

| Scenario | Behavior | Mitigation |
| --- | --- | --- |
| Service down (`mcp.context7.com` unreachable) | MCP tool calls fail; the model receives an error and (in our experience) typically falls back to its own training data without an audible warning | Skill should explicitly tell agents "if context7 returns an error, state that fact in the protocol and proceed with caution" |
| API key missing | Stdio variant: works but pooled into the 60 req/hour anonymous bucket — likely throttled mid-task. Remote variant: depends on header presence; usually 401. | Always set `CONTEXT7_API_KEY` in `.devcontainer/devcontainer.env` (or via `direnv`); fail loud at session start |
| Library not indexed | `resolve-library-id` returns no high-confidence match; `get-library-docs` then 404s on a fabricated ID | Skill must handle the empty-result case — fall back to `WebFetch` against the upstream docs URL |
| Rate-limited (429) | `Retry-After` header set; the call is wasted | For long automated runs, batch retrievals at task start rather than per-question; cache results in `plans_and_protocols/` |
| Outdated docs (top-1000+ slow tier) | Returned content is up to 45 days stale | Trigger a manual `POST /api/v1/refresh` from the skill when the user explicitly asks for "latest" |
| Container has no outbound HTTPS | Both transports fail | Document the outbound-allow requirement in `dev_environment/setup_guides/` |

## Reference integrations

- **Cline** — first-class Marketplace entry. Install via Cline's MCP Server Marketplace UI; uses the standard streamable-HTTP transport with `Authorization: Bearer …`. Multiple guides treat context7 as Cline's flagship doc-lookup server.[^cline-guide]
- **Cursor** — `Settings → Cursor Settings → MCP → Add Server` with `https://mcp.context7.com/mcp`. The Upstash blog post that introduced context7 used Cursor as the canonical demo.[^upstash-blog]
- **Continue.dev** — Continue accepts standard MCP-JSON configs in `.continue/mcpServers/`; the project doesn't ship a context7-specific recipe but explicitly tells users to copy Claude Desktop / Cursor JSON snippets verbatim.[^continue-docs]
- **Claude Code (this project's harness)** — official `/docs/clients/claude-code.md` page; supports both `.mcp.json` schemes, the `claude mcp add` CLI, and a plugin marketplace install (`/plugin marketplace add upstash/context7` → `/plugin install context7-plugin@context7-marketplace`) that bundles a docs-researcher subagent and a `/context7:docs` slash command.[^claude-code-docs]
- **OpenCode, Antigravity** — first-class `--opencode` / `--antigravity` setup wizard flags.[^cli-docs]
- **VS Code, Windsurf, Zed, Roo Code** — covered with verbatim snippets on `/docs/resources/all-clients`.[^all-clients]
- **GitHub Actions** — official integration page exists at `/docs/integrations/github-actions.md`, enabling doc-lookup in CI workflows.[^llms-txt]
- **CodeRabbit, Factory AI, Mastra, Tembo** — dedicated integration pages for each.[^llms-txt]
- **Smithery registry** — `@upstash/context7-mcp` is listed for cross-agent install.

(No GitHub-config snippets from the major coding-agent repos were extracted in-line in this research session; the canonical examples live on the context7 docs themselves rather than in third-party repos.)

## Recommendation for this project

**Wire context7 in via the remote HTTP MCP endpoint declared in the project-root `.mcp.json`, behind a `CONTEXT7_API_KEY` read from `.devcontainer/devcontainer.env`.** Concretely:

```jsonc
// /workspaces/private_mood_tracker/flutter_app/.mcp.json
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

Rationale:

1. **Zero container footprint** — no `npx` cold start, no Node version coupling, no extra `pub get`-style noise inside the devcontainer.
2. **Subagent propagation works for free** — Claude Code's `.mcp.json` is inherited by every spawned subagent (general-purpose, implementation-engineer, test-engineer), so the existing skill model doesn't need any per-agent rewiring.
3. **Survives container rebuilds** — only the env-var needs persisting (1Password / devcontainer secrets / WSL `.env`).
4. **Version-pinned retrieval is supported** — the agent can always pass `/flutter/flutter/v3.27.0` etc.; no infrastructure work needed on our side.
5. **Falls back gracefully** — when context7 is unreachable, skills should detect the MCP error and fall through to the existing `WebFetch` path against the upstream docs URL. This is already the pattern in `external_documentation_lookup` thinking.

**Adopt the "use context7" sentinel inside skills**, not as a user-facing convention. The `code-simple` / `code-complex` / `test-engineer` skills should be amended to prepend `use context7` when synthesizing a library-research query, plus an instruction to call `resolve-library-id` first. This keeps the trigger explicit and auditable in the protocol log.

**Operationalize the privacy constraint**: tell skills not to embed file paths, identifiers from this private codebase, or user data in context7 queries — only the library/topic. This blunts the OpenAI/Anthropic/Gemini reranking exposure documented above.

**Skip the CLI and SDK** for the main loop — both are duplicative of MCP and add a second installation surface. Keep `ctx7` available as a one-off Bash troubleshooting tool only.

## Open questions surfaced by the research

- **Flutter coverage depth.** We could not enumerate Flutter / Dart library IDs from the public web. A single authenticated call to `GET /api/v2/libs/search?query=flutter` (and `…?query=dart`, `…?query=riverpod`, `…?query=bloc`) at first key-provisioning time should be run and the IDs cached in `doc/` for the project's hot dependencies.
- **Per-call accounting.** Does one `resolve-library-id` + one `get-library-docs` count as one API call or two? The "API call" definition is not explicit in `/plans`. Worth confirming before estimating monthly budget against an automated factory that may issue dozens of lookups per session.
- **Header name casing.** The official remote-MCP example uses `CONTEXT7_API_KEY` as the HTTP header name (not `Authorization: Bearer …` as in the REST API). Worth confirming both work — some MCP-aware proxies normalize header casing aggressively.
- **What happens when the Top-1000 cadence is too slow for a fast-moving Flutter package?** Should the skill auto-fire `POST /api/v1/refresh` when the user prompt contains "latest", or wait for the user to ask? Either choice is a policy decision that belongs in the `external_documentation_lookup` requirement.
- **Privacy carve-out.** Is the OpenAI/Anthropic/Gemini reranking forwarding acceptable for this project's threat model, or do we need to gate context7 usage to public-information queries only? This needs an explicit decision in the requirements doc, not a tacit assumption.
- **Plugin-marketplace bundle vs. raw MCP.** The `/plugin install context7-plugin@context7-marketplace` bundle ships a `docs-researcher` subagent and a `/context7:docs` slash command. These could overlap or conflict with this project's existing subagent vocabulary — a small audit is needed before turning the bundle on.
- **Cost ceiling.** Free tier (1k/month) is plausibly enough for one developer; an unattended automation loop will exhaust it quickly. We should set up usage alerts at the dashboard and budget either the Pro $10/seat or a hard local cap (e.g., a skill-level circuit breaker after N calls per session).

---

### Footnotes (sources)

[^overview]: Context7 docs — Overview. https://context7.com/docs/overview
[^api-guide]: Context7 docs — API Guide. https://context7.com/docs/api-guide
[^all-clients]: Context7 docs — All Clients. https://context7.com/docs/resources/all-clients
[^cli-docs]: Context7 docs — CLI client. https://context7.com/docs/clients/cli
[^llms-txt]: Context7 docs — `llms.txt` sitemap. https://context7.com/docs/llms.txt
[^claude-code-docs]: Context7 docs — Claude Code. https://context7.com/docs/clients/claude-code
[^auth-keys]: Context7 docs — API Keys. https://context7.com/docs/howto/api-keys ; DeepWiki — Authentication. https://deepwiki.com/upstash/context7/18.1-authentication-and-api-keys
[^plans]: Context7 — Plans & Pricing. https://context7.com/plans
[^data-privacy]: Context7 docs — Data Privacy. https://context7.com/docs/security/data-privacy
[^library-updates]: Context7 docs — Keeping Libraries Fresh. https://context7.com/docs/library-updates
[^npm-page]: npm — `@upstash/context7-mcp`. https://www.npmjs.com/package/@upstash/context7-mcp
[^decodesfuture]: "Context7 MCP Setup for Claude Code: Commands, Config & Security (2026)." https://www.decodesfuture.com/articles/context7-mcp-claude-code-guide
[^deepwiki-resolve]: DeepWiki — resolve-library-id Tool. https://deepwiki.com/upstash/context7/4.1-resolve-library-id-tool
[^github-readme]: GitHub — upstash/context7 README. https://github.com/upstash/context7
[^docker-hub]: Docker Hub — mcp/context7. https://hub.docker.com/r/mcp/context7
[^upstash-blog]: Upstash blog — "Context7 MCP: Up-to-Date Docs for Any Cursor Prompt." https://upstash.com/blog/context7-mcp
[^cline-guide]: "Cline MCP Servers: Setup Guide & Best Extensions (2026)." https://evomap.ai/blog/cline-mcp-servers-setup-guide-2026
[^continue-docs]: Continue docs — MCP setup. https://docs.continue.dev/customize/deep-dives/mcp
