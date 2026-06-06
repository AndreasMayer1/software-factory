# Web Research — External Prior Art

Date: 2026-05-14
Delegated to: general-purpose agent
Question framing: forms, linting patterns, LLM consumption, longitudinal practice, bootstrap strategies

## 1. Forms of real-world concept canons / ubiquitous language artifacts

- **ammit-php/ammit** maintains a single [`UBIQUITOUS_LANGUAGE_DICTIONARY.md`](https://github.com/ammit-php/ammit/blob/master/UBIQUITOUS_LANGUAGE_DICTIONARY.md) at repo root — flat markdown table of terms with definitions and "aliases to avoid." Simple, no linting integration.
- **IFRCGo/cbs** keeps a [wiki "Ubiquitous language" page](https://github.com/IFRCGo/cbs/wiki/Glossary:-Ubiquitous-language) — narrative-prose style grouped by lifecycle ("Order," "People," "Relationships"), includes cardinality phrasing ("an Order belongs to exactly one Customer").
- **ddd-crew/eventstorming-glossary-cheat-sheet** publishes the [DDD vocabulary as a static site](https://ddd-crew.github.io/eventstorming-glossary-cheat-sheet/) generated from markdown — cards per term with relationships.

Generalizes: single-file markdown with a small typed schema (term, definition, aliases-to-avoid, related-terms) is the dominant choice — per-concept files are rare.
Does not generalize: none of these enforce consistency against code or i18n; they are read-only references.

## 2. Cross-artifact terminology consistency linting

- **Vale** (`vale.sh/docs/keys/vocab`) — closest established pattern. `accept.txt` / `reject.txt` per Vocab folder, case-sensitive regex. Datadog and Elastic ship published rulesets. Lints prose only — not Dart identifiers or YAML keys.
- **Stoplight Spectral** (`stoplight.io/open-source/spectral`) — generic JSON/YAML rules engine with custom functions; can cross-check `$ref` identifiers exist. Rules are YAML, targets are JSONPath expressions. Could be repurposed to assert "every term used in `*.arb` exists in `canon.yaml`."
- **igor-lirussi/Concurrent-DDD-Ubiquitous-Language-Verifier** — academic prototype that counts word frequency in source code and compares to glossary. Demonstrates the harvest-from-code pattern.

Gap: no off-the-shelf tool checks the markdown↔YAML↔Dart triple. Standard pattern is a small custom CI script that walks each artifact type and looks up against one canon — Netlify uses textlint for this on docs.

## 3. LLM-consumed concept canons

- **dbreunig's Jekyll glossary generator** (gist) — DSPy script emits `glossary.yaml` to `_data/`. YAML chosen because Jekyll consumes it AND it fits LLM prompt context cleanly. Concrete model: YAML-as-canon, markdown-as-render.
- **Roadie's "context engineering" pattern** — argues for `catalog-info.yaml`-style structured metadata as LLM context primitive: machine-readable fields (owner, lifecycle, tags) the LLM can reason over.
- **arXiv 2411.10541** measured up to 40% variance by prompt format — GPT-3.5 prefers JSON, GPT-4 prefers Markdown. Store as YAML/JSON and render markdown views on demand.

Generalizes: structured (YAML/JSON) source, markdown render for humans.
Does not generalize: no published Flutter/Dart precedent.

## 4. OOUX / DDD ubiquitous language in long-term practice

Honest gap: no longitudinal retrospectives found. OOUX literature (Prater A List Apart article, InfoQ podcast) is all delivery-phase. ddd-crew curates artifacts but no post-mortems on what survived. Anecdotal pattern in DDD community: object maps die after launch; only the glossary file (if checked into the repo) survives, and only when it has a linter enforcing it.

**Signal: durability correlates with executable enforcement, not artifact richness.**

## 5. Bootstrap strategies

No prior art specifically on glossary retrofitting was found. Adjacent patterns:

- **Harvest-from-code**: the DDD verifier above ranks code-frequency words as glossary candidates — useful seed list.
- **i18n key naming guides** (Locize, Lokalise) treat keys as a "contract between three stakeholders" — same shape as our four-artifact problem; their recommendation is structured-semantic keys mirroring app structure, introduced top-down per feature, never retroactively renamed (history loss).
- **Strangler-style incremental adoption** is the dominant legacy refactor pattern — applied to canon, this means: lint warns only on new/changed files initially, hard-fail later.

## Signal on gaps

The four-way (md + YAML + Dart + requirements) discrepancy check is genuinely novel territory — expect to build the linter ourselves, modeled on Spectral's JSONPath-rule architecture and Vale's accept/reject vocab files.
