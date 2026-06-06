---
name: codegraph
description: Semantic code intelligence for any codebase. Use this skill whenever you need to search for symbols, understand code structure, find related code for a task, explore unfamiliar code, or build context before making changes — anytime semantic search over code would be helpful.
---

# CodeGraph

CodeGraph builds a semantic knowledge graph of your codebase using tree-sitter parsing and local SQLite storage. It gives you instant symbol search, task-aware context building, and code structure analysis — all locally, no API keys needed.

## When to Use

Use codegraph **anytime semantic search over code would be helpful**:

- Understanding code related to a task or bug before making changes
- Searching for functions, classes, types, or methods by name or meaning
- Exploring an unfamiliar codebase or module
- Building context before spawning exploration agents
- Finding where a symbol is defined or used

## Primary Workflow

### 1. Build context for a task (most useful command)

Before exploring code manually with grep/find/read, try building context first:

```bash
codegraph context "fix the checkout validation bug" --max-nodes 20
```

This performs semantic search, graph traversal, and code extraction in one call — often enough to understand the relevant code without additional exploration.

```bash
# More nodes for complex tasks
codegraph context "add user authentication to the API" --max-nodes 50

# JSON output when you need structured data
codegraph context "refactor payment service" --format json
```

### 2. Search for symbols by name

Use instead of grep when looking for functions, classes, types, or methods:

```bash
codegraph query "UserService"
codegraph query "authenticate" --kind function --limit 20
codegraph query "validate" --json
```

Available kinds: `function`, `method`, `class`, `interface`, `type`, `variable`, `route`, `component`.

### 3. Check index status

```bash
codegraph status
```

Shows: files indexed, nodes/edges count, languages detected, pending changes, git hook status.

### 4. Sync after changes

If you've modified files and need fresh results:

```bash
codegraph sync
```

This incrementally updates the index (only changed files).

## Decision Guide

| Task | Command |
|------|---------|
| Understand code for a task/bug | `codegraph context "<description>"` |
| Find a symbol by name | `codegraph query "<name>"` |
| Check what's indexed | `codegraph status` |
| Update index after changes | `codegraph sync` |
| Full re-index | `codegraph index --force` |

## Tips

- **Prefer `codegraph context` over `codegraph query`** — context gives you related code, not just locations
- **Use `codegraph context` before spawning exploration agents** — it often provides enough context in one call
- **Run `codegraph sync`** if results seem stale after editing files
- CodeGraph supports 15+ languages: TypeScript, JavaScript, Python, Go, Rust, Java, C#, PHP, Ruby, C, C++, Swift, Kotlin, and more
