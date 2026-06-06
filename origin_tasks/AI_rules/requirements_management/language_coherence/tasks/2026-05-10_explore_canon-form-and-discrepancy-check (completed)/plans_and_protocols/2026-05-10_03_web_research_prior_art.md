# Web Research: External Prior Art on Concept Canons, Ubiquitous Language Registries, and Terminology Linting

**Task**: TASK-PROC-049-01 — Designing a canonical concept canon for a Flutter mood-tracker app (solo developer, longevity > velocity).
**Date**: 2026-05-10
**Method**: WebSearch + WebFetch, framed as questions per six research axes.
**Audience**: Same task; informs canon form-and-shape decisions in step 03 of the explore plan.

---

## 1. Ubiquitous Language in DDD: How is it actually maintained in real OSS projects?

### What the literature says (the prescriptive picture)
Eric Evans / Vaughn Vernon write that the ubiquitous language must be a "single shared glossary used by all stakeholders" and should "live where everyone can edit it." The canonical guidance is *medium-agnostic*: wiki, GitBook, shared spreadsheet, or markdown — what matters is that it's the same vocabulary used in conversations, requirements, and code.

- DDD Community glossary (the genre-defining reference): [dddcommunity.org/resources/ddd_terms/](https://www.dddcommunity.org/resources/ddd_terms/)
- DDD Reference (Evans): [domainlanguage.com/ddd/reference/](https://www.domainlanguage.com/ddd/reference/)
- Practitioner's Guide glossary: [ddd-practitioners.com/home/glossary/](https://ddd-practitioners.com/home/glossary/)

These are *example* glossaries — flat markdown lists of term → definition with occasional cross-links. They are read-only artifacts, not registries consumed by tooling.

### What actually happens in OSS projects (the descriptive picture)
Looking at real DDD reference repos, the dominant pattern is **"no separate glossary file" — the ubiquitous language lives in code identifiers**.

**Example A — `ddd-by-examples/library`** ([github.com/ddd-by-examples/library](https://github.com/ddd-by-examples/library))
- Comprehensive DDD reference project.
- Does **not** maintain `GLOSSARY.md` or `UBIQUITOUS_LANGUAGE.md`.
- Domain terms are encoded as class names, method names, value-object types, and Event Storming artifacts (sticky-note photos / diagrams).
- Their stated philosophy: "equal attention to model and code, keep them consistent" — i.e., the glossary *is* the source tree.

**Example B — `niquola/ubiquitous-language`** ([github.com/niquola/ubiquitous-language](https://github.com/niquola/ubiquitous-language))
- A Ruby DSL that lets domain sentences ("user as Author creates new_post for_category notifying_followers") be executable code.
- Goes one step further: the glossary is not just *reflected* in code, it's *expressed as* code via a sentence-DSL.
- "Very very alpha" — proves the idea is interesting but is not a maintainable solo-dev pattern.

**Example C — `igor-lirussi/Concurrent-DDD-Ubiquitous-Language-Verifier`** ([github.com/igor-lirussi/Concurrent-DDD-Ubiquitous-Language-Verifier](https://github.com/igor-lirussi/Concurrent-DDD-Ubiquitous-Language-Verifier))
- Student project: a multithreaded program that counts most-common words in a codebase to *verify* correspondence between dev vocabulary and a stated domain model.
- This is closer to what TASK-PROC-049-01 calls "discrepancy check": harvest terms from artifacts, compare against a stated canon, flag deltas.
- Crude (word frequency only), but the *concept* — automated harvesting + comparison — is what's transferable.

**Example D — `about-code/glossarify-md`** ([github.com/about-code/glossarify-md](https://github.com/about-code/glossarify-md))
- A working markdown-glossary tool (npm).
- Glossary = markdown file where each `## Term` heading is a definition; YAML attribute comments (`<!-- aliases: foo, bar -->`) declare synonyms.
- Tool auto-links every occurrence of `Term` (or its aliases) across other markdown files to the glossary entry.
- Indirectly produces a "term used somewhere but not in the glossary" report (via its index generation).
- Glossary doc: [glossary.md](https://github.com/about-code/glossarify-md/blob/master/doc/glossary.md)

### What's transferable to a solo Flutter app
- **The "glossary lives in code" pattern fails for this project**: requirements_tasks/ and requirements_user_needs/ are markdown documents authored *before* Flutter classes exist. Code-only canon would leave the upstream artifacts (the bulk of this repo) un-canonized.
- **The `glossarify-md` shape (markdown headings + YAML alias comments) is the strongest match**: human-editable, version-controllable, machine-parseable, no daemon, no DSL.
- **The "word frequency vs. stated canon" idea from `Concurrent-DDD-Verifier`** is the right shape for an automatable discrepancy check. A solo dev can run it on demand; it doesn't need to be a CI gate.

### What's not transferable
- DSL-as-glossary (Ruby/Java sentence chains) — too much framework lock-in and too much code that exists *only* to encode vocabulary.
- "Wiki + spreadsheet" patterns from enterprise DDD — assume multiple stakeholders and an ops team to keep the link alive.

---

## 2. Layers of Product Design / OOUX: what does `/layers-conceptual-model` produce?

### Source
- Project site: [layers.jamiemill.com](https://layers.jamiemill.com/) — "AI skills for product designers"
- Skills index: [layers.jamiemill.com/skills](https://layers.jamiemill.com/skills)
- Repo: [github.com/jamiemill/layers-skills](https://github.com/jamiemill/layers-skills)
- Author background: [jamiemill.com/blog/2021-07-10-elements-of-product-design](https://jamiemill.com/blog/2021-07-10-elements-of-product-design/) — "Elements of Product Design" — origin of the 7-layer model

### The framework
Nine skills, one per layer plus an orient/intro skill. Layer 5 (out of 7) is the **Conceptual Model** — described as "the most load-bearing layer." Skill names use the `/layers-<name>` slash-command convention.

### What `/layers-conceptual-model` produces (from the SKILL.md)
Five deliverables, all combined into a single document:

1. **Object definitions** — each object has attributes, relationships, actions; uses a consistent schema.
2. **Object map** — **Mermaid `erDiagram`** with cardinality notation (`||`, `o{`, `|{`).
3. **State diagrams** — **Mermaid `stateDiagram-v2`** for objects with non-trivial lifecycles.
4. **Ubiquitous language section** — nouns and verbs, **with rejected alternatives and rationale**. Format: `term / rejected alternatives / decision`.
5. **Open questions** — deferred decisions, thin areas.

The skill explicitly addresses temporal/state concerns: deletion semantics, relationship temporality, history, and verb precision ("correct address" vs. "register change of address").

### Format and maintenance
- **Format**: a single markdown file mixing prose, Mermaid blocks, and structured object templates. No YAML registry, no separate machine-readable file.
- **Maintenance model**: re-invoke the skill when the model changes; the AI agent regenerates / updates the doc. No linter, no cross-reference checker. The skill is a *generator*, not a *guardian*.
- **License**: MIT.

### What's transferable
- **Capture rejected alternatives, not just chosen terms.** The `term / rejected / decision` triple is high-leverage: it stops the next AI session from "fixing" a deliberate choice. This matches the WHY-comment philosophy already in this codebase's CLAUDE.md.
- **Mermaid as the relationship-diagram format** — human-readable in raw markdown, renders on GitHub, no toolchain.
- **One document, multiple sections** rather than a fan-out of small files. Solo devs lose track of fanned-out files; one canonical canon.md is easier to keep mentally indexed.

### What's not transferable
- The framework assumes a *design* phase before code. The mood-tracker is past that; many concepts are already named in `lib/` and in requirements_user_needs/. The canon must start as an *audit* of what exists, not a green-field design exercise.
- "Re-run the skill to refresh" implies regenerating from conversation. For a long-lived repo, the canon must be *edited*, not regenerated, or VTRs and rejected-alternative history get lost.

---

## 3. Terminology linting across heterogeneous artifacts (markdown + code + UI strings)

### Survey of candidates
| Tool | Scope | Cross-format detect? | Use as discrepancy checker? |
|---|---|---|---|
| **Vale** ([vale.sh](https://vale.sh/), [vale.sh/docs/keys/vocab](https://vale.sh/docs/keys/vocab)) | Prose linter; markdown + some code formats | **No** — operates per-file; vocab is allow/reject only | Partial: can enforce spelling/capitalization of canonical terms wherever they appear, but cannot say "term X used in artifact A but never defined in canon." |
| **textlint** ([textlint/textlint](https://github.com/textlint/textlint)) | Pluggable prose linter, markdown | **No** — per-file rules | Same limitation as Vale. |
| **alex / write-good / RetextJS** | Sensitivity/quality prose linters | No | Not for terminology consistency at all. |
| **glossarify-md** | Markdown only | **Partial** — generates an index of where each term appears; can be inverted to detect terms in spec that lack a glossary entry | Closest off-the-shelf match for "concept used somewhere but not defined." |
| **markdownlint / pymarkdownlnt** | Markdown syntax | No | Out of scope. |

### Detailed findings

**Vale vocabularies** ([vale.sh/docs/keys/vocab](https://vale.sh/docs/keys/vocab)):
- A vocab folder = `accept.txt` + `reject.txt`, one regex per line.
- `accept.txt` enforces casing/spelling (e.g., `JavaScript`, not `Javascript`).
- `reject.txt` flags banned terms.
- **Critical limitation**: both detect *presence*. There is no "term absent" rule. The Vale model is "the words that appear must match the canon," not "the concepts in the canon must appear consistently across artifacts."

**Vale on Dart source**: Vale lists a generic "Code" format; Dart is not explicitly listed. Custom comment-extraction would be required.

**textlint**: similar shape — terminology rule flags incorrect terms, no built-in concept-coverage check.

### What's transferable
- **Vale's vocabulary model — accept.txt of canonical names — is exactly the right primitive** for one half of the canon: "if this term appears, it must be spelled and capitalized this way." This is cheap and high-value. Solo dev cost: ≈ 1 file, edit when adding a concept.
- **The discrepancy-check tooling described in this task does not exist off the shelf.** No existing tool does "concept X is named in canon.md but missing/different in artifact Y." This must be built — and it should be built as a **small Python script** in `scripts/`, not as a Vale plugin (Vale's model is wrong-shaped). The script would: parse canon.md, harvest term occurrences from all artifacts, report deltas.
- **Use Vale for the "consistent capitalization/spelling" subproblem; build a custom checker for the "concept coverage" subproblem.** Two tools, two narrow jobs.

### What's not transferable
- Trying to bend Vale into a coverage checker. It will fight back.
- Cross-artifact linting at write-time. The cost-benefit only works as an on-demand audit, not as a save-time hook.

---

## 4. i18n/translation context patterns — what duplication is accepted, what is factored out?

### Mozilla Fluent (FTL)
- Spec: [projectfluent.org](https://projectfluent.org/)
- Reviewer guide: [firefox-source-docs.mozilla.org/l10n/fluent/review.html](https://firefox-source-docs.mozilla.org/l10n/fluent/review.html)
- Brand names: [mozilla-l10n.github.io/localizer-documentation/tools/fluent/brand_names.html](https://mozilla-l10n.github.io/localizer-documentation/tools/fluent/brand_names.html)

**The factored-out concept: Terms.** Fluent `Terms` are identifiers prefixed with `-` (e.g., `-brand-short-name`). They cannot be called from source code, only referenced from other Fluent messages. **Their entire purpose is to be the single definition of a vocabulary item**, with consistent inflection per language. Brand names live in dedicated `*.ftl` files and are referenced everywhere.

This is **the strongest external prior art** for the canon idea: a registry of named definitions that other artifacts reference rather than restate.

### Crowdin
- In-context translation: [support.crowdin.com/developer/in-context-localization/](https://support.crowdin.com/developer/in-context-localization/)
- Context enrichment with AI: [crowdin.github.io/crowdin-cli/blog/2026/02/23/context-enrichment](https://crowdin.github.io/crowdin-cli/blog/2026/02/23/context-enrichment)
- Translation accuracy: [crowdin.com/blog/translation-accuracy](https://crowdin.com/blog/translation-accuracy)

Crowdin accepts **per-string context** as a first-class field (string description + screenshot + AI-generated 1–3-sentence descriptions). They explicitly target "ambiguous short words, plurals, UI labels with inline formatting."

### Lokalise
- Onboarding for translators: [docs.lokalise.com/en/articles/2967175-onboarding-guide-for-translators](https://docs.lokalise.com/en/articles/2967175-onboarding-guide-for-translators)
- AI translations: [docs.lokalise.com/en/articles/8011393-ai-translations](https://docs.lokalise.com/en/articles/8011393-ai-translations)

Lokalise enriches each AI translation task with **glossary + translation memory + style guide** — the same triad. They also accept key-level comments and screenshots.

### Apple HIG / Android string resources
- Apple HIG Writing: [developer.apple.com/design/human-interface-guidelines/writing](https://developer.apple.com/design/human-interface-guidelines/writing)
- Android string resources: [developer.android.com/guide/topics/resources/string-resource](https://developer.android.com/guide/topics/resources/string-resource)
- Localazy on Android comments: [localazy.com/docs/android/how-to-provide-comments-for-strings](https://localazy.com/docs/android/how-to-provide-comments-for-strings)

Both platforms accept **inline comments above each translatable string** as the context channel. Android: `<!-- This is the login button, max 10 chars -->`. Apple: `NSLocalizedString(..., comment: "...")`. Both treat the comment as *the* context payload — not a separate registry.

### What duplication is accepted vs. factored out
| Accepted duplication | Factored out |
|---|---|
| Per-string context comments (each call site annotated) | Brand names / product names (Fluent Terms — one definition) |
| Screenshots per key | Glossary terms (Lokalise glossary, one definition reused across translations) |
| Translation memory entries (multiple identical short strings) | Reusable Fluent message references |

**Pattern**: duplicate the *context* (because it's local and cheap), centralize the *definition* (because changing a brand name everywhere is expensive).

### What's transferable
- **The "Fluent Term" mental model is the single most useful import**: a registry of canonical *definitions* that downstream artifacts *reference by name*. The canon should be the Fluent-Term layer of this repo.
- **Accept that context lives at the use-site, not in the canon.** A canon entry should hold: canonical name, definition, rejected alternatives, scope (which bounded context). It should *not* try to hold every nuance of how the concept is rendered in every screen — that stays at the use-site, like an Android `<!-- -->` comment.
- **Glossary + translation-memory + style guide is a standard triad.** For this repo: canon + requirements/code identifiers + WHY-comments map onto the same triad.

### What's not transferable
- Crowdin/Lokalise screenshots — overkill for a solo dev.
- Per-language inflection logic in Fluent — single-language project.

---

## 5. Single-developer maintenance — low-maintenance canonical artifacts

### Comparison to machine-checkable contracts (OpenAPI / JSON Schema)
- Pactflow on OpenAPI contracts: [pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-2/](https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-2/)
- Speakeasy on OpenAPI testing: [speakeasy.com/blog/contract-testing-with-openapi](https://www.speakeasy.com/blog/contract-testing-with-openapi)

OpenAPI/JSON Schema work for low-maintenance because:
1. **One file, one source of truth** — every client, mock, validator reads the same YAML/JSON.
2. **Generated artifacts** (clients, docs, mocks) — humans never re-author downstream consumers.
3. **Validation is at runtime** — drift is caught by tests, not by manual audit.

Reported result: "40% reduction in API-related bugs" when teams adopt schema-first contract testing. Quoted maintenance cost: "super quick, quite low maintenance."

### Why a glossary is harder than OpenAPI
- OpenAPI describes a *machine boundary* — every request crosses it, so drift is automatically observable.
- A concept canon describes a *human-and-AI boundary* — drift only shows up when someone reads two artifacts and notices they disagree. There is no runtime that fails.
- Therefore a canon needs an **explicit on-demand audit step** (a script) to substitute for the missing runtime.

### Lessons from successful long-lived single-maintainer glossaries
- **Flutter docs glossary** ([docs.flutter.dev/resources/glossary](https://docs.flutter.dev/resources/glossary)) and **Dart glossary** ([dart.dev/resources/glossary](https://dart.dev/resources/glossary)) — both are flat markdown lists, alphabetical, with cross-links. Maintained by a team but the *shape* is solo-able.
- **OpenProject** ([openproject.org/blog/glossary/](https://www.openproject.org/blog/glossary/)) — single passion-project glossary, lives in their docs site, grows organically.
- Common pattern: **alphabetical markdown, no metadata beyond term/definition/cross-link**, low ceiling for ceremony.

### What's transferable
- **One file, alphabetical, markdown headings** — the lowest-maintenance shape known. Resist the urge to fan out.
- **Make audit explicit, on-demand, scripted.** OpenAPI gets drift-detection "for free" via runtime; a canon must script-substitute for it. A solo dev runs `./scripts/check_canon.py` before a release, not on every save.
- **Generated artifacts are gold; manual sync is poison.** If anything can be generated *from* the canon (e.g., a Vale `accept.txt`, or a list of allowed bounded-context names for `task-create`), generate it. Manual mirroring of the canon into N other files is the death of a solo glossary.

### What's not transferable
- Schema-validated runtime contracts. The canon doesn't have a runtime. Don't try to fake one.
- Auto-generated SDK clients. Too much machinery for the value.

---

## 6. Concept canons consumed by LLMs (newer angle, 2024–2026)

### Skills / SKILL.md as the de-facto canon-loading mechanism
- Anthropic Skills overview: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
- Skill authoring patterns: [generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics](https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics)
- Anthropic skills repo: [github.com/anthropics/skills](https://github.com/anthropics/skills)
- Complete Guide PDF: [resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

Key Anthropic guidance:
> "Reference skills are passive knowledge (style guides, domain vocabulary) that Claude applies inline whenever a relevant request matches."

This is exactly the canon's role: **passive domain vocabulary, loaded on demand, applied inline**. The SKILL.md mechanism is built for this case.

**Loading model**: SKILL.md is read into context on trigger; referenced files (FORMS.md, schema.md, GLOSSARY.md) are read **only if the task needs them**. Unused reference files cost zero tokens.

### CLAUDE.md / AGENTS.md / Copilot instructions as project-level prompt prelude
- AGENTS.md spec: [agents.md](https://agents.md/) — Linux Foundation–stewarded, "README for agents," 60k+ projects adopting.
- Writing CLAUDE.md (HumanLayer): [humanlayer.dev/blog/writing-a-good-claude-md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- Configure every AI assistant: [deployhq.com/blog/ai-coding-config-files-guide](https://www.deployhq.com/blog/ai-coding-config-files-guide)
- "You don't need a CLAUDE.md": [dev.to/byme8/you-dont-need-a-claudemd-jgf](https://dev.to/byme8/you-dont-need-a-claudemd-jgf)

**Both AGENTS.md and CLAUDE.md are deliberately section-free** — no schema, no required headings. AGENTS.md explicit: *"It's just standard Markdown. Use any headings you like."* The cost-benefit is: low ceremony → high adoption.

**Anti-pattern (from "You don't need a CLAUDE.md")**: bloated CLAUDE.md files that try to encode everything fail because LLMs can't absorb the whole prelude on every turn. Lean files referenced *by need* outperform comprehensive prefixes.

### LLM grounding / RAG / canonical-name resolution
- LLM grounding overview: [iguazio.com/glossary/llm-grounding/](https://www.iguazio.com/glossary/llm-grounding/)
- RAG in 2026: [techment.com/blogs/rag-in-2026/](https://www.techment.com/blogs/rag-in-2026/)
- Roadie context engineering glossary: [roadie.io/blog/context-engineering-glossary/](https://roadie.io/blog/context-engineering-glossary/)
- RAG year-end 2025 review (RAGFlow): [ragflow.io/blog/rag-review-2025-from-rag-to-context](https://ragflow.io/blog/rag-review-2025-from-rag-to-context)

**Key 2025–2026 shift**: from "RAG = vector retrieval" to "context engineering" — the framing has broadened to *all* mechanisms by which an agent's context window gets populated with authoritative facts. A concept canon is a flavor of context engineering: a small, hand-curated, high-precision context source, **not retrieved by embedding similarity but loaded by name reference**.

**Embedding-based canonical-name resolution** is mentioned (e.g., handling "developers describe what they're looking for in plain English; embeddings bridge to internal names"). For this project, **embeddings are overkill** — the canon is small (~50–200 terms) and an LLM can do exact name resolution by reading the canon directly.

### What's transferable
- **Skill-style "load when relevant" beats prefix-style "include in every prompt"** — the canon should be a referenced artifact (e.g., `canon.md` linked from CLAUDE.md), not inlined into the prompt prelude. This matches the current `doc/` pattern.
- **A frontmatter-tagged markdown canon is LLM-native.** YAML frontmatter per section + alphabetical headings is exactly the shape SKILL.md uses and is parseable by every LLM agent without custom tooling.
- **Keep the canon small.** "Lean reference files referenced by name" is repeatedly cited as outperforming "comprehensive context dumps." Aim for terms an outside reader could not infer from class names, not every concept in the app.
- **Don't index the canon for embeddings yet.** At this scale, exact-name lookup is sufficient and avoids RAG infra entirely.

### What's not transferable
- Vector indexing / embedding-based name resolution — premature optimization at this scale.
- Multi-document agentic retrieval (the "MCP server for glossary" pattern) — overkill for solo maintenance.

---

## Synthesis: 5 lessons that should shape the canon's form

1. **Fluent-Term model is the conceptual centerpiece.** The canon should be a registry of *definitions referenced by name from elsewhere*, not a glossary that duplicates context. Downstream artifacts (requirements, scenarios, code, WHY-comments) hold their own local context but **reference the canon by canonical name**. This is the single most replicated pattern across Mozilla Fluent, Lokalise glossaries, and Anthropic skill references.

2. **One file, markdown, alphabetical, YAML frontmatter per term.** Borrow `glossarify-md`'s shape (headings = terms, YAML attributes for aliases/rejected/scope) and Layers' `term / rejected alternatives / decision` triple. Resist fan-out. Solo-dev failure mode is N files, not too-large one file. Flutter docs and Dart docs glossaries prove the alphabetical-flat pattern scales for years.

3. **Two tools, two narrow jobs: Vale-style for spelling/casing, a custom Python script for concept-coverage.** Off-the-shelf terminology linters (Vale, textlint) solve only the "if a canon name appears, it must be spelled correctly" half. The "concept X is defined in canon but missing/diverging in artifact Y" half does not exist as a product and **must be built** — as a small on-demand script in `scripts/requirements/`, not as a CI gate, not as a save-time hook. This matches how OpenAPI substitutes runtime validation for the missing manual audit; a canon must script-substitute for the missing runtime.

4. **Generate downstream artifacts from the canon; never mirror manually.** OpenAPI's lesson is decisive: any artifact that can be generated *from* the canon (e.g., a Vale `accept.txt`, a list of allowed bounded-context names for `task-create`, a `--list-concepts` flag for skills) must be generated. Manual mirroring of vocabulary into multiple places is the proven death of solo-maintained glossaries.

5. **Capture rejected alternatives and rationale, not just chosen names.** This is the Layers-skills lesson and matches this codebase's existing WHY-comments and VTR culture. Without it, future AI sessions "fix" deliberate choices and rebuild every six months. A `rejected:` YAML field per term is a one-line addition with outsized longevity payoff. Pair with cross-links to VTRs when the rejection encodes a value trade-off.

### Honorable mentions (lessons that almost made the top 5)

- **Skill-style on-demand loading beats prefix inlining.** The canon should be referenced from CLAUDE.md, not inlined.
- **Audit is on-demand, not continuous.** A solo dev runs `./scripts/check_canon.py` before a release or before a refactor, not on every commit. The cost-benefit of a save-time hook is wrong-shaped for this project.
- **Per-bounded-context scope tag per term.** From DDD: a name only means one thing within one bounded context. The canon must record scope so that `Mood` in the entry context and `Mood` in the export context don't conflict accidentally.

---

## Source index

### Question 1 — DDD ubiquitous language in OSS
- [Martin Fowler — UbiquitousLanguage](https://martinfowler.com/bliki/UbiquitousLanguage.html)
- [DDD Community glossary](https://www.dddcommunity.org/resources/ddd_terms/)
- [DDD Reference (Evans)](https://www.domainlanguage.com/ddd/reference/)
- [ddd-by-examples/library](https://github.com/ddd-by-examples/library)
- [niquola/ubiquitous-language](https://github.com/niquola/ubiquitous-language)
- [igor-lirussi/Concurrent-DDD-Ubiquitous-Language-Verifier](https://github.com/igor-lirussi/Concurrent-DDD-Ubiquitous-Language-Verifier)
- [about-code/glossarify-md](https://github.com/about-code/glossarify-md)
- [Practitioner's Guide glossary](https://ddd-practitioners.com/home/glossary/)

### Question 2 — Layers / OOUX
- [layers.jamiemill.com](https://layers.jamiemill.com/)
- [layers.jamiemill.com/skills](https://layers.jamiemill.com/skills)
- [github.com/jamiemill/layers-skills](https://github.com/jamiemill/layers-skills)
- [Elements of Product Design (Jamie Mill blog)](https://jamiemill.com/blog/2021-07-10-elements-of-product-design/)

### Question 3 — terminology linting
- [Vale documentation — vocab keys](https://vale.sh/docs/keys/vocab)
- [Vale custom vocabularies guide](https://hetfs.github.io/documentation/docs/Vale_Linter/Create%20vocab%20txt%20File)
- [Vale on LWN](https://lwn.net/Articles/964075/)
- [textlint](https://github.com/textlint/textlint)
- [Datadog on Vale](https://www.datadoghq.com/blog/engineering/how-we-use-vale-to-improve-our-documentation-editing-process/)

### Question 4 — i18n context patterns
- [Project Fluent](https://projectfluent.org/)
- [Fluent reviewers guide](https://firefox-source-docs.mozilla.org/l10n/fluent/review.html)
- [Fluent brand names](https://mozilla-l10n.github.io/localizer-documentation/tools/fluent/brand_names.html)
- [Crowdin in-context localization](https://support.crowdin.com/developer/in-context-localization/)
- [Crowdin AI context enrichment (2026)](https://crowdin.github.io/crowdin-cli/blog/2026/02/23/context-enrichment)
- [Lokalise translator onboarding](https://docs.lokalise.com/en/articles/2967175-onboarding-guide-for-translators)
- [Lokalise AI translations](https://docs.lokalise.com/en/articles/8011393-ai-translations)
- [Apple HIG — Writing](https://developer.apple.com/design/human-interface-guidelines/writing)
- [Android string resources](https://developer.android.com/guide/topics/resources/string-resource)
- [Localazy — Android string comments](https://localazy.com/docs/android/how-to-provide-comments-for-strings)

### Question 5 — solo-developer low-maintenance contracts
- [Pactflow — JSON Schema + OpenAPI contract testing](https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-2/)
- [Speakeasy — contract testing with OpenAPI](https://www.speakeasy.com/blog/contract-testing-with-openapi)
- [Treblle — Contract Definition with OpenAPI](https://treblle.com/knowledgebase/design-phase/contract-definition-using-openapi-specification)
- [Flutter docs glossary](https://docs.flutter.dev/resources/glossary)
- [Dart glossary](https://dart.dev/resources/glossary)
- [OpenProject glossary as passion project](https://www.openproject.org/blog/glossary/)

### Question 6 — LLM-consumable canons
- [Anthropic Skills overview (Claude Code)](https://code.claude.com/docs/en/skills)
- [Anthropic Skills repo](https://github.com/anthropics/skills)
- [Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Skill authoring patterns from Anthropic](https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics)
- [AGENTS.md](https://agents.md/)
- [Writing a good CLAUDE.md (HumanLayer)](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [Configure every AI coding assistant](https://www.deployhq.com/blog/ai-coding-config-files-guide)
- ["You don't need a CLAUDE.md"](https://dev.to/byme8/you-dont-need-a-claudemd-jgf)
- [LLM grounding (Iguazio glossary)](https://www.iguazio.com/glossary/llm-grounding/)
- [RAG in 2026 (Techment)](https://www.techment.com/blogs/rag-in-2026/)
- [Roadie — Context Engineering Glossary](https://roadie.io/blog/context-engineering-glossary/)
- [RAGFlow — From RAG to Context 2025 review](https://ragflow.io/blog/rag-review-2025-from-rag-to-context)
