# Web Research: han Plugin Evaluation
Date: 2026-05-26
Researcher: implementation-engineer agent

---

## Q1: What is han / Test Double's stated intent and philosophy?

**Primary sources consulted**: GitHub repo README (`github.com/testdouble/han`), `/blob/main/README.md`, `/blob/main/docs/concepts.md`.

### Findings

Han is a Claude Code plugin created and maintained by **River Lynn Bailey** at Test Double (MIT license, Copyright 2026 Test Double, Inc.). It was extracted from a private repo and made public in May 2026 (first public release v2.1.0 on May 11, 2026).

**Stated purpose**: "Combines evidence-based planning, test-driven implementation, full documentation maintenance, deep code review, and architectural analysis into a team of specialists" — designed for solo product engineers and small teams.

**Four pillars confirmed by the docs**:

1. **Evidence-based planning / YAGNI**: Applied as a hard gate across all planning, review, and architecture skills. The exact wording from `docs/concepts.md`: *"Items without evidence get deferred, recorded for later, not silently dropped."* Deferred items are listed under a "Deferred (YAGNI)" section with triggers for reopening. This is enforced mechanically in skill prompts, not just advisory.

2. **Adversarial review**: Multiple skills systematically dispatch skeptical specialist agents. `adversarial-security-analyst` joins code reviews; `adversarial-validator` provides second opinions on plans. The design treats adversarial challenge as a *core* quality mechanism rather than optional polish.

3. **Sized agent rosters (small/medium/large dispatch)**: Seven skills use this scaling model: `/architectural-analysis`, `/code-review`, `/gap-analysis`, `/iterative-plan-review`, `/plan-a-feature`, `/plan-implementation`, `/research`. The system starts at "small" and only escalates on concrete signals: file count, subsystems touched, and security/data/infrastructure surface area. Users can override with a `$size` parameter.

4. **Deterministic skills + contextual agents**: Skills are described as "deterministic workflows" (flowchart-like); agents provide "contextual judgment." The architecture is explicitly layered — routine steps are scripted, judgment-heavy decisions are delegated to specialist agents. The `/code-review` skill always dispatches `junior-developer` and `security-analyst`, then conditionally adds `test-engineer`, `data-engineer`, or `devops-engineer` based on changed file types.

**Scale**: 20 skills, 22 agents as of v2.6.x.

**No Test Double blog post or announcement article was found** for han. The project appears to have launched quietly via GitHub without a public marketing push.

**Confidence**: HIGH for philosophy (direct primary-source quotes from README and concepts.md). LOW for any blog/announcement context — no such content found.

**Sources**:
- https://github.com/testdouble/han (README, repo metadata)
- https://github.com/testdouble/han/blob/main/README.md
- https://github.com/testdouble/han/blob/main/docs/concepts.md

---

## Q2: How has han been received or adopted in the wild?

**Primary sources consulted**: Web searches for Reddit, HackerNews, X/Twitter, blog mentions; plugin roundup articles.

### Findings

**No secondary commentary found.** Multiple search strategies were tried:
- `"testdouble han" Claude Code review adoption 2025 2026`
- `"han" "testdouble" Claude Code skills agents YAGNI "adversarial review"`
- `testdouble han plugin Claude Code Reddit HackerNews discussion user experience`

None returned blog posts, HN threads, Reddit discussions, or user write-ups specifically about han. The plugin roundup article by Camille Roux ("Top 13 skills et plugins Claude Code en 2026") does not mention han at all.

**Context**: The Claude Code plugin marketplace is large (33+ official plugins, hundreds of community ones per search results). Han is a small-star project (63 stars as of research date) in a crowded space. Its quiet launch (no blog post, no announcement found) likely explains the absence of secondary commentary.

**No specific skills or agents from han were praised or cited** in any community content found.

**Confidence**: HIGH that no significant public adoption signal exists as of 2026-05-26. LOW on completeness — closed communities (private Slack/Discord channels, paid newsletters) may discuss it without leaving public traces.

**Sources**:
- Search results: https://aitoolanalysis.com/claude-code-plugins/ (does not mention han)
- https://www.camilleroux.com/top-skills-plugins-claude-code-2026-v3/ (does not mention han)
- https://github.com/quemsah/awesome-claude-plugins (han not in top results)

---

## Q3: Community guidance on selectively adopting parts of a Claude Code plugin

**Primary sources consulted**: Official Claude Code docs (`code.claude.com/docs/en/skills`), GitHub issues on `anthropics/claude-code`, community guides.

### Findings

**Selective adoption is well-supported and straightforward.**

The official Claude Code skill system works at three independent layers:
1. **Plugin-installed skills**: Live under `<plugin>/skills/<name>/SKILL.md`, invoked as `/plugin-name:skill-name`. Fully namespaced — cannot conflict with personal or project skills.
2. **Personal skills**: `~/.claude/skills/<name>/SKILL.md`, invoked as `/<name>`.
3. **Project skills**: `.claude/skills/<name>/SKILL.md`, invoked as `/<name>`.

**Cherry-picking individual skill files** (without installing the whole plugin) is explicitly supported: copy the skill directory (not the whole repo) into `~/.claude/skills/` or `.claude/skills/`. The skill becomes available immediately — Claude Code watches for changes and hot-reloads. No manifest or registry entry is needed.

**Key gotchas identified**:

1. **Namespace collision when copying without plugin prefix**: When you manually copy a han skill into `.claude/skills/`, it gets the bare `/<name>` command (e.g., `/code-review`). If Claude Code has a built-in bundled skill also named `/code-review`, the manually copied skill takes precedence over project-level skills but there is documented ambiguity. A confirmed silent-failure bug (Issue #13586): a command named `/skill` silently prevented ALL custom commands from loading. The resolution was to rename. Takeaway: avoid names that collide with built-in bundled skill names (`/debug`, `/code-review`, `/batch`, `/loop`, `/claude-api`, etc.).

2. **Agent file dependencies**: Han skills reference agents by name (e.g., `adversarial-security-analyst`, `research-analyst`). When a skill is cherry-picked without its companion agents, the skill's prompt instructions will reference agents that do not exist in the session. Claude will likely degrade gracefully (treating the agent reference as a subagent prompt instruction), but the multi-agent dispatch model won't work as designed. This is a structural dependency the han README does not explicitly warn about.

3. **Hook conflicts**: Plugin hooks are scoped to the plugin. Manually copied skill files that include `hooks:` frontmatter could conflict with existing project hooks if the same lifecycle event is covered twice. Recommendation: strip `hooks:` frontmatter when cherry-picking individual skills into a repo that already manages its own hooks.

4. **Feature request for per-skill install** (Issue #138 on `mattpocock/skills`): Community members have asked for this, confirming the use case is real and somewhat friction-prone but technically viable.

**Confidence**: HIGH for the mechanical process (official docs are authoritative). MEDIUM for the agent-dependency gotcha (inferred from architecture, not a documented warning). HIGH for the naming-collision issue (confirmed via filed GitHub issue).

**Sources**:
- https://code.claude.com/docs/en/skills (official docs, namespacing table)
- https://github.com/anthropics/claude-code/issues/13586 (naming collision bug)
- https://github.com/mattpocock/skills/issues/138 (feature request for selective install)
- https://dev.to/samuel_rose_b30991db2b25b/how-to-install-skills-in-claude-code-3-methods-2ofl

---

## Q4: MIT license requirements when copying or adapting markdown files

**Primary sources consulted**: MIT license text (OSI), choosealicense.com, sbomify.com guide, GitHub community discussion #23453.

### Findings

**The MIT license text imposes one condition**: "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."

**For purely internal, non-distributed use** (your situation): The MIT license technically triggers on "copies." Whether running han's skill files inside your private repo constitutes a "copy" in the legal sense is a fine point — most legal practitioners read MIT's trigger as applying when you distribute to third parties, not when you copy internally. However, **the conservative and commonly-recommended practice is to retain attribution regardless**, because:
- It costs nothing.
- It is good practice if the repo ever becomes less private.
- It satisfies the condition beyond any ambiguity.

**For adapted (modified) files**: MIT does NOT require you to:
- State that you modified the file (unlike Apache 2.0, which explicitly requires this).
- Publish your modifications.
- License your adaptations under MIT.

You DO need to retain the original copyright notice even on adapted files, per the "copies or substantial portions" language.

**Per-file header vs. centralized NOTICE/THIRD_PARTY file**: MIT does not specify placement. The commonly recommended approach (confirmed by sbomify guide and GitHub community discussion):

- A single `THIRD_PARTY_NOTICES.md` or `NOTICE` file at the repo root that lists: "Portions adapted from han (https://github.com/testdouble/han), Copyright 2026 Test Double, Inc., MIT License" plus the full MIT permission text.
- Per-file headers are NOT required by MIT and are considered overkill for adapted files (they would be confusing if 90% of the file is your own work).

**Practical recommendation for this project**:
1. Create `/workspaces/private_mood_tracker/flutter_app/THIRD_PARTY_NOTICES.md` with one entry per adopted han component.
2. Include: original file path, adapted file path, copyright line, and the MIT permission text block.
3. No per-file header needed on the adapted `.claude/` skill or agent files.
4. No obligation to open-source your adaptations.

**Confidence**: HIGH on the practical recommendation (well-established community practice). MEDIUM on the "internal use does not trigger MIT" interpretation — this is a legal nuance and the conservative approach (include attribution) is strongly preferred regardless.

**Sources**:
- https://opensource.org/license/mit (canonical MIT text)
- https://choosealicense.com/licenses/mit/
- https://sbomify.com/2026/01/22/mit-license-guide/
- https://github.com/orgs/community/discussions/23453

---

## Q5: Maintenance signals for han

**Primary sources consulted**: GitHub releases page, commits page, issues page for `testdouble/han`.

### Findings

**Han is extremely actively maintained as of 2026-05-26**, but it is very new.

| Signal | Data |
|---|---|
| First public release | v2.1.0, May 11, 2026 |
| Latest release | v2.6.2, May 26, 2026 (same day as this research) |
| Total releases | 8 (v2.1.0 through v2.6.2) in 15 days |
| Commit frequency | 20+ commits in the last 4 days alone |
| Open issues | 0 |
| Closed issues | 0 |
| Stars | 63 |
| Forks | 5 |

**Release cadence summary** (v2.1.0 → v2.6.2, May 11–26):
- v2.1.0: Initial public release, extraction from private repo
- v2.2.0: Enhanced gap analysis with full agent swarm
- v2.3.0: Recalibrated `/code-review` with guardrails
- v2.4.0: Added `/issue-triage`, `/tdd`, `/plan-work-items`; rebuilt `/architectural-analysis`
- v2.5.0: Added `/research` skill and `research-analyst` agent
- v2.6.0: Added `/stakeholder-summary`; internal `han-update-documentation` tool
- v2.6.1: Fixed skill loader (20 skills not registering correctly)
- v2.6.2: Token optimization for `/tdd`; per-file-type index files for `/coding-standard`

**Breaking changes**: None explicitly documented. All changes are additive (new skills/agents) or refinements (token optimization, guardrails). The v2.6.1 bugfix note ("Fixed skill loader issue; 20 skills register correctly again") is a concern for anyone who installed v2.6.0 — it shows that the plugin infrastructure itself can break silently.

**Stability risk**: The rapid iteration is a double-edged signal. Active development means improvements land quickly, but it also means that anyone cherry-picking a skill today could find the upstream has changed substantially within weeks. The v2.6.1 patch fixing a skill-loader bug within days of launch suggests the project is still shaking out foundational issues.

**Maintenance SLA**: Explicitly "best-effort, no SLA, approximately 2 weeks for issues." This is a one-maintainer personal project with Test Double's organizational backing, not a commercially supported product.

**Confidence**: HIGH (direct observation of repo metadata, releases page, and commit history).

**Sources**:
- https://github.com/testdouble/han/releases
- https://github.com/testdouble/han/commits/main
- https://github.com/testdouble/han/issues
