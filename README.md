# Software Factory

The **Software Factory** is a set of skills, agents, hooks, scripts, and process
rules that govern *how* software is built with AI coding agents (Claude Code):
top-down from persona → scenario → flow → requirement → task → code, with
quality gates and file-based memory holding it together.

It grew inside a real project (an offline Flutter app) and is being extracted
into its own, independently versioned repository so any project can consume it.

> **Status: pre-extraction snapshot.** This repo is a flat copy of the factory as
> it currently lives inside its host project — it is **not yet** packaged, wired
> up, or usable standalone. A proper README and a real consumption mechanism come
> after the extraction itself. The vision and methodology for that extraction are
> in `origin_tasks/AI_rules/factory_extraction/` and
> `origin_tasks/requirement_draft.md`.

## Layout

| Path | What it is |
|---|---|
| `product/` | The factory itself — the runtime that Claude Code loads. |
| `product/.claude/` | Skills, agents, hooks, schemas, settings. |
| `product/scripts/` | Factory tooling (tasks, requirements, releases, quality gates). |
| `origin_tasks/` | Source material: the process requirements and the extraction vision. |
| `origin_tasks/AI_rules/` | The `process/AI_rules` requirement & task corpus that specifies the factory. |
| `origin_tasks/requirement_draft.md` | The extraction vision / methodology draft. |

## License

Licensed under the **Elastic License 2.0** — see [`LICENSE`](LICENSE). The scope
of "the software" (it covers prompts, agent/skill definitions, schemas, configs,
not just code) is set out in [`NOTICE`](NOTICE). Third-party components and their
own licenses are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
